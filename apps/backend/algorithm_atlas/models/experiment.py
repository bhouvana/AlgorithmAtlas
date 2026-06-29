"""
Persistence models for saved experiments and notebook cells.

Experiment   — a named snapshot of an algorithm run (slug + params + seed + frames).
NotebookCell — a code cell inside a Notebook that can be re-executed via /notebook/run.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    algorithm_slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    params: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    seed: Mapped[int] = mapped_column(Integer, nullable=False, default=42)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    cells: Mapped[list[NotebookCell]] = relationship(
        "NotebookCell",
        back_populates="experiment",
        cascade="all, delete-orphan",
        order_by="NotebookCell.order",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "algorithm_slug": self.algorithm_slug,
            "params": self.params,
            "seed": self.seed,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "cell_count": len(self.cells),
        }


class NotebookCell(Base):
    __tablename__ = "notebook_cells"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    experiment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    language: Mapped[str] = mapped_column(String(32), nullable=False, default="python")
    source: Mapped[str] = mapped_column(Text, nullable=False, default="")
    output: Mapped[str] = mapped_column(Text, nullable=False, default="")
    error: Mapped[str] = mapped_column(Text, nullable=False, default="")
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    experiment: Mapped[Experiment] = relationship("Experiment", back_populates="cells")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "order": self.order,
            "language": self.language,
            "source": self.source,
            "output": self.output,
            "error": self.error,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }
