"""
Algorithm Atlas — FastAPI application entry point.

Startup sequence:
1. Configure logging
2. Discover and register all plugins
3. Mount API router
4. Serve
"""
from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .api.v1.router import api_router
from .config import get_settings
from .database import AsyncSessionLocal, engine, init_db
from .models import atlas_memory as _   # noqa: F401 — ensure table is registered
from .models import atlas_code as _ac  # noqa: F401 — register AtlasCode tables
from .models.atlas_code import Problem
from .plugins.loader import PluginLoader
from .plugins.registry import get_registry


# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────

def _configure_logging(level: str) -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# AtlasCode ledger snapshot
# ──────────────────────────────────────────────────────────────────────────────
# atlas.db (and its atlascode_matrix_ledger table) is gitignored and never
# travels with the repo, so a fresh database has ZERO verified-language
# history even when the real local ledger already has thousands of verified
# (problem_id, language, mode) cells across all 16 non-Python target
# languages. ledger_snapshot.json (apps/backend/algorithm_atlas/atlascode/,
# refreshed via `python scripts/export_ledger_snapshot.py`) is a small,
# committable export of exactly that data. Loading it here means a fresh
# boot reflects the SAME verified-language state as local development —
# not just Python — instead of starting from nothing. Idempotent
# (INSERT OR IGNORE) and fast (a few thousand rows), so it runs on every
# boot, not gated behind the "problems table empty" check below: if the
# ledger is ever partially reset, this self-heals it back to at least the
# snapshot's state.
async def _load_ledger_snapshot() -> None:
    from .atlascode.ledger_snapshot import load_ledger_snapshot

    try:
        async with engine.begin() as conn:
            inserted = await load_ledger_snapshot(conn)
        if inserted:
            logger.info(f"Ledger snapshot loaded — {inserted} verified language/mode cell(s) restored")
        else:
            logger.info("Ledger snapshot: nothing new to load (already up to date or snapshot missing)")
    except Exception:
        logger.exception(
            "Ledger snapshot load failed — the app will still start, but "
            "language-coverage badges may under-report until this is fixed."
        )


# ──────────────────────────────────────────────────────────────────────────────
# AtlasCode auto-seed
# ──────────────────────────────────────────────────────────────────────────────
# atlas.db is gitignored (231MB+, over GitHub's 100MB hard limit, and it also
# carries the multi-language verification ledger which is separately rebuilt
# over time — not something to fake at boot). init_db() above only creates
# empty tables, so a fresh deploy (Render, or any first-time clone) would
# otherwise boot with a completely empty AtlasCode catalog. The emptiness
# check below is what makes this safe to call on every boot, not just the
# first one — a non-empty problems table means it's already been seeded.
#
# Two-tier strategy, tried in order:
#  1. FAST PATH — load apps/backend/algorithm_atlas/atlascode/
#     problems_snapshot.db.gz (a committed, pre-built SQLite export; see
#     scripts/export_problems_snapshot.py). Row copy happens entirely
#     inside SQLite (ATTACH DATABASE + INSERT...SELECT) -- finishes in
#     seconds with minimal memory, since no row data is ever materialized
#     as Python objects. (An earlier JSON-based version of this snapshot
#     WAS Python-object-heavy at load time and still OOM-killed Render's
#     512MB container despite the DB insert itself being fast -- see
#     problems_snapshot.py's docstring.)
#  2. SLOW PATH (fallback if the snapshot is missing/empty) — regenerate
#     everything via seed_atlascode(), the same logic as
#     `python scripts/seed_atlas_code.py`. Measured locally: ~8 MINUTES on a
#     genuinely fresh database (250-plugin discovery/import + 216 problems'
#     worth of family builders doing real adversarial-test generation).
#     CONFIRMED to OOM-kill Render's free-tier 512MB container before
#     finishing, every single time, in an infinite crash-loop (no
#     persistent disk means every restart starts from an empty DB and
#     retries the same OOM) -- this is why the fast path exists and is
#     always tried first. The slow path remains for environments where the
#     snapshot is absent or stale relative to the family builders.
#
# Both tiers run as a background task via asyncio.create_task() rather than
# being awaited directly inside lifespan(): anything awaited before `yield`
# blocks the ASGI server from ever opening its port, so an 8-minute (slow
# path) or even a few-second (fast path, but still non-zero) await here
# risks failing Render's deploy health check. Running this in the
# background lets the server start accepting requests immediately (with an
# empty AtlasCode catalog until seeding finishes) — the same tradeoff
# Render itself expects from long-running startup work.
async def _auto_seed_atlascode_if_empty() -> None:
    from sqlalchemy import func, select

    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(func.count()).select_from(Problem))).scalar_one()

    if existing > 0:
        logger.info(f"AtlasCode already seeded ({existing} problems) — skipping auto-seed")
        return

    logger.info("AtlasCode problems table is empty — attempting fast snapshot load")
    try:
        db_path = get_settings().resolved_sqlite_path()
        if db_path is None:
            logger.info(
                "DATABASE_URL is non-sqlite — snapshot fast path only supports "
                "sqlite, falling back to full generation"
            )
        else:
            from .atlascode.problems_snapshot import load_problems_snapshot
            inserted = await load_problems_snapshot(db_path)
            if inserted:
                logger.info(f"AtlasCode snapshot load complete — {inserted} problem(s) inserted")
                return
            logger.info("Problems snapshot missing or empty — falling back to full generation")
    except Exception:
        logger.exception("Problems snapshot load failed — falling back to full generation")

    logger.info("AtlasCode auto-seeding via full generation on boot (memory-heavy, ~8 minutes)")
    try:
        from .atlascode.seed import seed as seed_atlascode
        await seed_atlascode()
        logger.info("AtlasCode auto-seed complete")
    except Exception:
        # Never let a seeding failure take the whole app down — algorithm
        # visualizations, the notebook, etc. are all independent of AtlasCode
        # and should still come up. Re-run `python scripts/seed_atlas_code.py`
        # manually (or just restart once the underlying issue is fixed; this
        # runs again on every boot until the table is non-empty).
        logger.exception(
            "AtlasCode auto-seed failed — the app will still start, but the "
            "AtlasCode catalog may be empty or partially seeded."
        )


# ──────────────────────────────────────────────────────────────────────────────
# Application lifecycle
# ──────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    _configure_logging(settings.LOG_LEVEL)

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Plugin root: {settings.PLUGIN_ROOT}")

    await init_db()
    logger.info("Database schema initialised")

    # Fast (a few thousand INSERT OR IGNORE rows) -- safe to await directly,
    # unlike the AtlasCode problem/test-case seed below.
    await _load_ledger_snapshot()

    registry = get_registry()
    loader = PluginLoader(registry)
    count = loader.discover(settings.PLUGIN_ROOT)

    if count == 0:
        logger.warning(
            "No plugins loaded. The algorithm catalog will be empty. "
            f"Verify PLUGIN_ROOT points to the correct directory: {settings.PLUGIN_ROOT}"
        )
    else:
        logger.info(f"Ready — {count} algorithm(s) available")

    # Fire-and-forget: see _auto_seed_atlascode_if_empty()'s docstring for why
    # this must NOT be awaited here (would block the server from ever opening
    # its port on a fresh deploy). Keep a reference so it isn't garbage-
    # collected mid-flight — asyncio only holds a weak reference to tasks.
    seed_task = asyncio.create_task(_auto_seed_atlascode_if_empty())

    yield

    if not seed_task.done():
        logger.info("Cancelling in-flight AtlasCode auto-seed for shutdown")
        seed_task.cancel()

    logger.info("Shutting down")


# ──────────────────────────────────────────────────────────────────────────────
# Application factory
# ──────────────────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Algorithm Atlas API — "
            "interactive computational encyclopedia for algorithms and simulations."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count"],
    )

    app.include_router(api_router)

    @app.get("/health", tags=["meta"])
    async def health():
        registry = get_registry()
        return {
            "status": "ok",
            "version": settings.APP_VERSION,
            "algorithms_loaded": len(registry),
        }

    return app


app = create_app()
