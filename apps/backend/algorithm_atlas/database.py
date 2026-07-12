"""
Async SQLAlchemy engine + session factory for Algorithm Atlas.

SQLite via aiosqlite for zero-config development; swap DATABASE_URL
in .env to PostgreSQL (asyncpg) for production.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncConnection,
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
    url = settings.resolved_sqlite_url()
    kwargs: dict = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    # Loud by design (Phase 1's DB-path resolver requirement): this is the one
    # line that would have made the apps/backend/atlas.db decoy-DB footgun
    # immediately obvious the first time it happened instead of silently
    # returning 0 rows.
    print(f"[database] resolved DB URL: {url}")
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

# Columns added to existing tables after their first release. `create_all`
# only creates whole tables that don't exist yet — it never ALTERs an
# existing table to add a new column — so a lightweight, additive-only,
# idempotent migration runs alongside it. Never drops or renames a column;
# safe to run against a database with real existing data.
_NEW_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "problems": [
        ("test_suite_version", "VARCHAR(20) DEFAULT '1.0'"),
        # Dual-mode Run architecture (Function Mode). NULL = Function Mode
        # not supported for this problem; Program Mode is unaffected either way.
        ("function_contract", "JSON"),
        ("starter_code_function", "JSON"),
    ],
    "submissions": [
        ("memory_kb", "FLOAT"),
        ("compile_output", "TEXT"),
        ("judge_version", "VARCHAR(20)"),
        ("test_suite_version", "VARCHAR(20)"),
        ("test_results_json", "JSON"),
    ],
    "test_cases": [
        # Canonical typed arguments/expected-return for Function Mode, captured
        # at the exact same generation step as input_data/expected_output
        # (see testgen.build_forty) -- never re-derived by parsing stdin.
        #
        # Declared TEXT, not JSON: SQLite assigns NUMERIC affinity to any
        # declared type that doesn't contain CHAR/CLOB/TEXT (JSON matches
        # none of those), and NUMERIC affinity silently coerces an inserted
        # TEXT value that "looks like a bare number" into INTEGER/REAL
        # storage -- for a big-integer return value (e.g. catalan-number's
        # 70-digit answers) that exceeds a 64-bit int, SQLite falls back to
        # REAL, corrupting the exact integer into a lossy float on write.
        # Reproduced directly: `sqlite3` on a JSON-typed column stores the
        # 70-digit string as `3.0867482673729235e+66`. function_args is
        # unaffected in practice (always a JSON OBJECT, never a bare
        # scalar), but function_expected can be a bare integer/float for
        # scalar-return contracts, so it must have TEXT affinity to store
        # the JSON text byte-for-byte with no silent type coercion.
        ("function_args", "TEXT"),
        ("function_expected", "TEXT"),
    ],
}


async def _add_missing_columns(conn: AsyncConnection) -> None:
    dialect = conn.engine.dialect.name
    if dialect != "sqlite":
        # Only SQLite's ALTER TABLE ADD COLUMN is handled here (this project's
        # dev database). A Postgres deployment should use a real migration
        # tool (alembic is already a declared dependency) instead of this.
        return
    for table, columns in _NEW_COLUMNS.items():
        existing = await conn.execute(text(f'PRAGMA table_info("{table}")'))
        existing_names = {row[1] for row in existing.fetchall()}
        for name, ddl_type in columns:
            if name not in existing_names:
                await conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN {name} {ddl_type}'))


# `atlascode_matrix_ledger` is NOT a mapped SQLAlchemy model (it's written by
# standalone verification scripts via scripts/atlascode_ledger.py's own raw
# sqlite3 connection -- see that module's docstring), so Base.metadata.create_all
# above never creates it. On a real dev machine with a populated atlas.db this
# is invisible (the table already exists from those scripts having run), but
# on a genuinely fresh database (a first Render deploy, or anyone cloning the
# repo) the table is simply absent -- and apps/backend/algorithm_atlas/api/v1/
# problems.py's _language_coverage() queries it on every /problems request,
# so a missing table 500s the entire AtlasCode catalog page. Schema kept in
# sync by hand with scripts/atlascode_ledger.py's _SCHEMA constant.
_LEDGER_SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS atlascode_matrix_ledger (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id          TEXT NOT NULL,
        language            TEXT NOT NULL,
        mode                TEXT NOT NULL,
        adapter_version     TEXT,
        contract_version    TEXT,
        test_suite_version  TEXT,
        toolchain_version   TEXT,
        verification_level  INTEGER NOT NULL,
        status              TEXT NOT NULL,
        failure_class       TEXT,
        failure_message      TEXT,
        duration_ms         REAL,
        timestamp           REAL NOT NULL,
        UNIQUE(problem_id, language, mode)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_ledger_lang_mode ON atlascode_matrix_ledger(language, mode)",
    "CREATE INDEX IF NOT EXISTS idx_ledger_level ON atlascode_matrix_ledger(verification_level)",
]


async def _ensure_ledger_table(conn: AsyncConnection) -> None:
    if conn.engine.dialect.name != "sqlite":
        return
    for statement in _LEDGER_SCHEMA_STATEMENTS:
        await conn.execute(text(statement))


async def init_db() -> None:
    """Create all tables that don't already exist (idempotent), then apply
    any additive column migrations to tables that already exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _add_missing_columns(conn)
        await _ensure_ledger_table(conn)
