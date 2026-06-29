"""
Experiments CRUD — save, list, get, update, delete algorithm run snapshots.

POST   /api/v1/experiments            — create
GET    /api/v1/experiments            — list (paginated)
GET    /api/v1/experiments/{id}       — detail (with cells)
PATCH  /api/v1/experiments/{id}       — update name/notes
DELETE /api/v1/experiments/{id}       — delete

POST   /api/v1/experiments/{id}/cells          — add cell
PATCH  /api/v1/experiments/{id}/cells/{cid}    — update cell source / output
DELETE /api/v1/experiments/{id}/cells/{cid}    — remove cell
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...database import get_db
from ...models.experiment import Experiment, NotebookCell

router = APIRouter(prefix="/experiments", tags=["experiments"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class ExperimentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    algorithm_slug: str
    params: dict[str, Any] = Field(default_factory=dict)
    seed: int = 42
    notes: str = ""


class ExperimentUpdate(BaseModel):
    name: str | None = None
    notes: str | None = None


class CellCreate(BaseModel):
    language: str = "python"
    source: str = ""
    order: int = 0


class CellUpdate(BaseModel):
    source: str | None = None
    output: str | None = None
    error: str | None = None


# ── Experiment endpoints ────────────────────────────────────────────────────────

@router.post("", status_code=201)
async def create_experiment(
    body: ExperimentCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    exp = Experiment(
        name=body.name,
        algorithm_slug=body.algorithm_slug,
        params=body.params,
        seed=body.seed,
        notes=body.notes,
    )
    db.add(exp)
    await db.flush()
    await db.refresh(exp)
    return exp.to_dict()


@router.get("")
async def list_experiments(
    algorithm_slug: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    q = select(Experiment).order_by(Experiment.created_at.desc())
    if algorithm_slug:
        q = q.where(Experiment.algorithm_slug == algorithm_slug)
    total_q = q
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    experiments = result.scalars().all()
    total_result = await db.execute(total_q)
    total = len(total_result.scalars().all())
    return {
        "items": [e.to_dict() for e in experiments],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{experiment_id}")
async def get_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Experiment)
        .options(selectinload(Experiment.cells))
        .where(Experiment.id == experiment_id)
    )
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    data = exp.to_dict()
    data["cells"] = [c.to_dict() for c in sorted(exp.cells, key=lambda c: c.order)]
    return data


@router.patch("/{experiment_id}")
async def update_experiment(
    experiment_id: str,
    body: ExperimentUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(Experiment).where(Experiment.id == experiment_id))
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if body.name is not None:
        exp.name = body.name
    if body.notes is not None:
        exp.notes = body.notes
    exp.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return exp.to_dict()


@router.delete("/{experiment_id}", status_code=200)
async def delete_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Experiment).where(Experiment.id == experiment_id))
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    await db.delete(exp)
    return {"deleted": experiment_id}


# ── Cell endpoints ─────────────────────────────────────────────────────────────

@router.post("/{experiment_id}/cells", status_code=201)
async def add_cell(
    experiment_id: str,
    body: CellCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(Experiment).where(Experiment.id == experiment_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Experiment not found")
    cell = NotebookCell(
        experiment_id=experiment_id,
        language=body.language,
        source=body.source,
        order=body.order,
    )
    db.add(cell)
    await db.flush()
    await db.refresh(cell)
    return cell.to_dict()


@router.patch("/{experiment_id}/cells/{cell_id}")
async def update_cell(
    experiment_id: str,
    cell_id: str,
    body: CellUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(NotebookCell)
        .where(NotebookCell.id == cell_id, NotebookCell.experiment_id == experiment_id)
    )
    cell = result.scalar_one_or_none()
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    if body.source is not None:
        cell.source = body.source
    if body.output is not None:
        cell.output = body.output
    if body.error is not None:
        cell.error = body.error
    await db.flush()
    return cell.to_dict()


@router.delete("/{experiment_id}/cells/{cell_id}", status_code=200)
async def delete_cell(
    experiment_id: str,
    cell_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotebookCell)
        .where(NotebookCell.id == cell_id, NotebookCell.experiment_id == experiment_id)
    )
    cell = result.scalar_one_or_none()
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    await db.delete(cell)
    return {"deleted": cell_id}
