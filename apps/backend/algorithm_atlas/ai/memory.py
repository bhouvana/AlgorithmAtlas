"""Async helpers for reading and writing Atlas AI user memory."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.atlas_memory import AtlasMemory, _utcnow


async def get_user_memories(db: AsyncSession, user_id: str) -> dict[str, str]:
    result = await db.execute(
        select(AtlasMemory).where(AtlasMemory.user_id == user_id)
    )
    return {row.key: row.value for row in result.scalars().all()}


async def upsert_memory(db: AsyncSession, user_id: str, key: str, value: str) -> None:
    result = await db.execute(
        select(AtlasMemory).where(
            AtlasMemory.user_id == user_id,
            AtlasMemory.key == key,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.value = value
        existing.updated_at = _utcnow()
    else:
        db.add(AtlasMemory(user_id=user_id, key=key, value=value))
    await db.flush()


async def delete_memory(db: AsyncSession, user_id: str, key: str) -> bool:
    result = await db.execute(
        select(AtlasMemory).where(
            AtlasMemory.user_id == user_id,
            AtlasMemory.key == key,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()
        return True
    return False
