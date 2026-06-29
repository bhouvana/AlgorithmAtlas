"""
Async SQLAlchemy engine + session factory for Algorithm Atlas.

SQLite via aiosqlite for zero-config development; swap DATABASE_URL
in .env to PostgreSQL (asyncpg) for production.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings

# ── Base ──────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ── Engine ─────────────────────────────────────────────────────────────────────

def _make_engine():
    settings = get_settings()
    url = settings.SQLITE_URL
    kwargs: dict = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_async_engine(url, echo=settings.DEBUG, **kwargs)


engine = _make_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Dependency ─────────────────────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Schema creation ────────────────────────────────────────────────────────────

async def init_db() -> None:
    """Create all tables that don't already exist (idempotent)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
