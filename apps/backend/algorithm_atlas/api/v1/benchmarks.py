"""
Benchmark endpoints.

POST /api/v1/benchmarks        — single algorithm across input sizes
POST /api/v1/benchmarks/batch  — multiple algorithms in parallel (Rust-accelerated)

Phase 4.2: Rust engine acceleration.
  When `algorithm_atlas_rs` is compiled and installed (`maturin develop`),
  sort benchmarks run ~10× faster via the native Rust+Rayon engine.
  Falls back to the Python BenchmarkRunner transparently.
"""
from __future__ import annotations

import asyncio
import json
from functools import partial
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from algorithm_atlas.benchmark.config import get_config
from algorithm_atlas.benchmark.runner import BenchmarkRunner, SizeResult
from algorithm_atlas.benchmark.rust_runner import (
    benchmark_parallel,
    benchmark_slug,
    is_available as rust_available,
)
from algorithm_atlas.plugins.registry import AlgorithmNotFound, get_registry

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])

# ── Request / Response models ─────────────────────────────────────────────────

class BenchmarkRequest(BaseModel):
    algorithm_slug: str
    sizes: List[int] = Field(
        default=[10, 25, 50, 100, 200],
        description="Input sizes to benchmark",
    )
    size_param: str = Field(
        default="array_size",
        description="The param key that controls input size",
    )
    param_overrides: Dict[str, Any] = Field(default_factory=dict)
    trials: int = Field(default=3, ge=1, le=10)
    seed: int = Field(default=42, ge=0)


class SizeResultResponse(BaseModel):
    input_size: int
    frame_count: int
    init_ms: float
    steps_ms: float
    total_ms: float


class BenchmarkResponse(BaseModel):
    slug: str
    size_param: str
    results: List[SizeResultResponse]
    engine: str = "python"  # "python" | "rust"


class BatchBenchmarkItem(BaseModel):
    slug: str
    seed: int = Field(default=42, ge=0)
    array_size: int = Field(ge=2, le=10_000)
    input_order: str = "random"
    trials: int = Field(default=3, ge=1, le=10)


class BatchBenchmarkRequest(BaseModel):
    items: List[BatchBenchmarkItem] = Field(
        min_length=1,
        max_length=100,
        description="Up to 100 (slug, size) benchmark requests run in parallel",
    )


class BatchBenchmarkResultItem(BaseModel):
    slug: str
    array_size: int
    ms: float


class BatchBenchmarkResponse(BaseModel):
    results: List[BatchBenchmarkResultItem]
    engine: str


# ── Benchmark config endpoint ─────────────────────────────────────────────────

class BenchmarkConfigResponse(BaseModel):
    slug: str
    category: str
    size_param: str
    default_sizes: List[int]
    label: str


@router.get("/config/{slug}", response_model=BenchmarkConfigResponse)
async def get_benchmark_config(slug: str):
    """Return the canonical size_param and default sizes for a given algorithm."""
    registry = get_registry()
    try:
        registered = registry.get(slug)
    except AlgorithmNotFound:
        raise HTTPException(status_code=404, detail=f"Algorithm '{slug}' not found")

    meta = registered.metadata
    category = meta.category
    cfg = get_config(category)

    return BenchmarkConfigResponse(
        slug=slug,
        category=category,
        size_param=cfg.size_param,
        default_sizes=list(cfg.default_sizes),
        label=cfg.label,
    )


# ── Single benchmark endpoint ─────────────────────────────────────────────────

MAX_SIZE = 10_000
MAX_SIZES_COUNT = 20

@router.post("", response_model=BenchmarkResponse)
async def run_benchmark(body: BenchmarkRequest):
    """
    Run the algorithm at each requested input size and return timing results.

    When the Rust engine is compiled and the algorithm is a supported sort,
    the Rust engine handles each size ~10× faster than pure Python.
    Falls back to Python BenchmarkRunner transparently.
    """
    registry = get_registry()
    try:
        registered = registry.get(body.algorithm_slug)
    except AlgorithmNotFound:
        raise HTTPException(status_code=404, detail=f"Algorithm '{body.algorithm_slug}' not found")

    sizes = [min(s, MAX_SIZE) for s in body.sizes[:MAX_SIZES_COUNT]]
    engine = "python"

    # ── Try Rust acceleration for supported sort algorithms ──────────────────
    if rust_available() and body.size_param == "array_size":
        rust_results: list[SizeResultResponse] = []
        all_rust = True
        for size in sizes:
            ms = benchmark_slug(
                body.algorithm_slug,
                seed=body.seed,
                array_size=size,
                input_order=body.param_overrides.get("input_order", "random"),
                trials=body.trials,
            )
            if ms is not None:
                # Rust returns only total_ms; frame_count via a quick run
                rust_results.append(SizeResultResponse(
                    input_size=size,
                    frame_count=0,   # not tracked by Rust engine (perf path)
                    init_ms=0.0,
                    steps_ms=ms,
                    total_ms=ms,
                ))
            else:
                all_rust = False
                break

        if all_rust and rust_results:
            return BenchmarkResponse(
                slug=body.algorithm_slug,
                size_param=body.size_param,
                results=rust_results,
                engine="rust",
            )

    # ── Python fallback ──────────────────────────────────────────────────────
    runner = BenchmarkRunner()
    algorithm = registered.instantiate()
    loop = asyncio.get_event_loop()
    raw_results: List[SizeResult] = await loop.run_in_executor(
        None,
        partial(
            runner.run,
            algorithm,
            sizes,
            body.size_param,
            body.param_overrides,
            body.trials,
            body.seed,
        ),
    )

    return BenchmarkResponse(
        slug=body.algorithm_slug,
        size_param=body.size_param,
        results=[
            SizeResultResponse(
                input_size=r.input_size,
                frame_count=r.frame_count,
                init_ms=r.init_ms,
                steps_ms=r.steps_ms,
                total_ms=r.total_ms,
            )
            for r in raw_results
        ],
        engine=engine,
    )


# ── Batch benchmark endpoint (Rust-parallel) ──────────────────────────────────

@router.post("/batch", response_model=BatchBenchmarkResponse)
async def run_benchmark_batch(body: BatchBenchmarkRequest):
    """
    Run up to 100 (slug, size) benchmark requests in parallel.

    When the Rust engine is compiled, all Rust-supported requests are
    dispatched to the Rayon thread pool simultaneously — on an 8-core machine
    this is ~8× faster than sequential Python benchmarks.

    Requests for unsupported slugs are silently omitted from the response.
    """
    if not rust_available():
        raise HTTPException(
            status_code=503,
            detail="Rust engine not available. Run: cd packages/rust-engine && maturin develop",
        )

    requests_payload = [
        {
            "slug":        item.slug,
            "seed":        item.seed,
            "array_size":  item.array_size,
            "input_order": item.input_order,
            "trials":      item.trials,
        }
        for item in body.items
    ]

    loop = asyncio.get_event_loop()
    raw: list[dict] = await loop.run_in_executor(
        None,
        partial(benchmark_parallel, requests_payload),
    )

    return BatchBenchmarkResponse(
        results=[
            BatchBenchmarkResultItem(
                slug=r["slug"],
                array_size=r["array_size"],
                ms=r["ms"],
            )
            for r in raw
        ],
        engine="rust",
    )
