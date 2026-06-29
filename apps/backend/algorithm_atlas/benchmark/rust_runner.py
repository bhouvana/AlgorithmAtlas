"""
Optional Rust acceleration for Algorithm Atlas benchmarks.

Tries to import the compiled `algorithm_atlas_rs` native extension.
If the wheel is not present (maturin hasn't been run yet), falls back
gracefully — the server keeps running on pure Python with no change in
API behaviour.

Build:
    cd packages/rust-engine
    maturin develop                # editable install (dev)
    maturin build --release        # wheel (production)

The Rust engine gives ~10× throughput for sort algorithms and supports
true parallel benchmark runs via Rayon's thread pool.
"""
from __future__ import annotations

import json
from typing import Optional

try:
    import algorithm_atlas_rs as _rust  # type: ignore[import-not-found]
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

# Slugs supported by the Rust simulation engine (mirrors wasm-engine's sort set).
RUST_SORT_SLUGS: frozenset[str] = frozenset([
    "bubble-sort",
    "insertion-sort",
    "selection-sort",
    "merge-sort",
    "quick-sort",
])


def is_available() -> bool:
    """Return True when the compiled Rust extension is importable."""
    return _AVAILABLE


def benchmark_slug(
    slug: str,
    seed: int,
    array_size: int,
    input_order: str = "random",
    trials: int = 3,
) -> Optional[float]:
    """
    Benchmark a single sort algorithm.

    Returns median milliseconds, or None when:
    - Rust extension is not compiled
    - slug is not in RUST_SORT_SLUGS
    """
    if not _AVAILABLE or slug not in RUST_SORT_SLUGS:
        return None
    try:
        return _rust.benchmark_sort_rs(slug, seed, array_size, input_order, trials)
    except Exception:
        return None


def benchmark_parallel(
    requests: list[dict],
) -> list[dict]:
    """
    Run multiple benchmark requests in parallel using Rayon.

    Args:
        requests: List of dicts with keys:
            slug (str), seed (int), array_size (int),
            input_order (str, default "random"), trials (int, default 3)

    Returns:
        List of dicts: [{"slug": str, "array_size": int, "ms": float}, ...]
        Empty list when Rust extension is unavailable.
    """
    if not _AVAILABLE:
        return []
    # Filter to only slugs the Rust engine handles
    rust_requests = [r for r in requests if r.get("slug") in RUST_SORT_SLUGS]
    if not rust_requests:
        return []
    try:
        result_json: str = _rust.benchmark_parallel_rs(json.dumps(rust_requests))
        return json.loads(result_json)
    except Exception:
        return []


def run_sort_frames(
    slug: str,
    seed: int,
    array_size: int,
    input_order: str = "random",
) -> Optional[list[dict]]:
    """
    Return all simulation frames for a sort algorithm as a list of dicts.

    Equivalent to the Python plugin's `steps()` generator, but ~10× faster.
    Returns None when the Rust extension is unavailable or slug unsupported.
    """
    if not _AVAILABLE or slug not in RUST_SORT_SLUGS:
        return None
    try:
        frames_json: str = _rust.run_sort_rs(slug, seed, array_size, input_order)
        return json.loads(frames_json)
    except Exception:
        return None
