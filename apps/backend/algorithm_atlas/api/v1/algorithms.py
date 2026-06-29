"""
Algorithm catalog endpoints.

GET /api/v1/algorithms              — paginated list with filtering
GET /api/v1/algorithms/categories   — category tree
GET /api/v1/algorithms/{slug}       — full algorithm detail
GET /api/v1/algorithms/{slug}/source — algorithm Python source code
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from algorithm_atlas.plugins.registry import AlgorithmNotFound, get_registry

router = APIRouter(prefix="/algorithms", tags=["algorithms"])


# ──────────────────────────────────────────────────────────────────────────────
# Response models
# ──────────────────────────────────────────────────────────────────────────────

class ComplexityResponse(BaseModel):
    time_best: str
    time_average: str
    time_worst: str
    space: str


class ReferenceResponse(BaseModel):
    title: str
    type: str
    url: Optional[str] = None


class AlgorithmSummary(BaseModel):
    slug: str
    name: str
    category: str
    visualization_type: str
    execution_target: str
    complexity: ComplexityResponse
    tags: List[str]
    description: str


class AlgorithmSourceResponse(BaseModel):
    slug: str
    filename: str
    source: str
    language: str = "python"
    line_count: int


class AlgorithmDetail(AlgorithmSummary):
    intuition: str
    references: List[ReferenceResponse]
    default_params: dict
    version: str
    benchmark_enabled: bool


class CategoryResponse(BaseModel):
    slug: str
    name: str
    algorithm_count: int


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get("", response_model=List[AlgorithmSummary])
async def list_algorithms(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    search: Optional[str] = Query(None, description="Fuzzy search on name and tags"),
    execution_target: Optional[str] = Query(None, description="Filter by execution_target"),
):
    registry = get_registry()
    algorithms = registry.list_all()

    if category:
        algorithms = [a for a in algorithms if a.category == category]

    if execution_target:
        algorithms = [a for a in algorithms if a.execution_target == execution_target]

    if search:
        q = search.lower()
        algorithms = [
            a for a in algorithms
            if q in a.name.lower()
            or q in a.category.lower()
            or any(q in t.lower() for t in a.manifest.get("tags", []))
        ]

    return [_to_summary(a.manifest) for a in algorithms]


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories():
    registry = get_registry()
    categories: dict[str, int] = {}
    for alg in registry.list_all():
        categories[alg.category] = categories.get(alg.category, 0) + 1
    return [
        CategoryResponse(slug=cat, name=cat.replace("-", " ").title(), algorithm_count=count)
        for cat, count in sorted(categories.items())
    ]


@router.get("/{slug}/source", response_model=AlgorithmSourceResponse)
async def get_algorithm_source(slug: str):
    registry = get_registry()
    try:
        alg = registry.get(slug)
    except AlgorithmNotFound:
        raise HTTPException(status_code=404, detail=f"Algorithm '{slug}' not found")

    entry_point = alg.manifest.get("entry_point", "algorithm.py")
    source_path = alg.plugin_dir / entry_point

    if not source_path.exists():
        raise HTTPException(status_code=404, detail="Source file not found")

    source = source_path.read_text(encoding="utf-8")
    return AlgorithmSourceResponse(
        slug=slug,
        filename=entry_point,
        source=source,
        language="python",
        line_count=source.count("\n") + 1,
    )


@router.get("/{slug}", response_model=AlgorithmDetail)
async def get_algorithm(slug: str):
    registry = get_registry()
    try:
        alg = registry.get(slug)
    except AlgorithmNotFound:
        raise HTTPException(status_code=404, detail=f"Algorithm '{slug}' not found")
    return _to_detail(alg.manifest)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _normalize_param(spec: dict) -> dict:
    """
    Convert a JSON Schema property entry to our ParameterPanel format.

    JSON Schema uses:  type="integer" + minimum/maximum, or type="string" + enum
    ParameterPanel expects: type="integer" + min/max, or type="choice" + choices
    """
    out = dict(spec)
    raw_type = spec.get("type", "")

    if raw_type == "integer":
        out["type"] = "integer"
        if "minimum" in spec and "min" not in out:
            out["min"] = spec["minimum"]
        if "maximum" in spec and "max" not in out:
            out["max"] = spec["maximum"]

    elif raw_type == "string" and "enum" in spec:
        out["type"] = "choice"
        if "choices" not in out:
            out["choices"] = spec["enum"]

    elif raw_type == "boolean":
        out["type"] = "boolean"

    return out


def _normalize_params(raw: dict) -> dict:
    return {key: _normalize_param(val) if isinstance(val, dict) else val
            for key, val in raw.items()}


def _to_summary(m: dict) -> AlgorithmSummary:
    return AlgorithmSummary(
        slug=m["id"],
        name=m["name"],
        category=m["category"],
        visualization_type=m["visualization_type"],
        execution_target=m.get("execution_target", "server"),
        complexity=ComplexityResponse(**m["complexity"]),
        tags=m.get("tags", []),
        description=m.get("description", ""),
    )


def _to_detail(m: dict) -> AlgorithmDetail:
    raw_params = (
        m.get("parameters")
        or m.get("params_schema", {}).get("properties", {})
    )
    return AlgorithmDetail(
        slug=m["id"],
        name=m["name"],
        category=m["category"],
        visualization_type=m["visualization_type"],
        execution_target=m.get("execution_target", "server"),
        complexity=ComplexityResponse(**m["complexity"]),
        tags=m.get("tags", []),
        description=m.get("description", ""),
        intuition=m.get("intuition", ""),
        references=[ReferenceResponse(**r) for r in m.get("references", [])],
        default_params=_normalize_params(raw_params),
        version=m.get("version", "1.0.0"),
        benchmark_enabled=m.get("benchmark_enabled", True),
    )
