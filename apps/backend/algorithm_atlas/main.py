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
# otherwise boot with a completely empty AtlasCode catalog. This runs the
# same idempotent logic as `python scripts/seed_atlas_code.py` (skips rows
# that already exist), so it's always safe to call on every boot, not just
# the first one — the emptiness check below just avoids the catalog-assembly
# cost on every restart once it's already seeded.
#
# Measured locally: a genuinely fresh database takes ~8 MINUTES to fully
# seed (250-plugin discovery/import + 216 problems' worth of family builders,
# some of which do real adversarial-test generation, e.g. bfs-graph-variants
# alone took ~60s). That is why the caller below fires this as a background
# task via asyncio.create_task() instead of awaiting it directly inside
# lifespan(): anything awaited before `yield` blocks the ASGI server from
# ever opening its port, so an 8-minute await here would fail Render's
# deploy health check (which expects the port to open within a much shorter
# window) and likely crash-loop the service — worse, seed()'s DB writes are
# one single transaction that only commits at the very end, so a kill
# mid-seed loses ALL progress and the next boot starts over from zero.
# Running this in the background lets the server start accepting requests
# immediately (with an empty AtlasCode catalog for a few minutes) while
# seeding finishes asynchronously — the same tradeoff Render itself expects
# from long-running startup work.
async def _auto_seed_atlascode_if_empty() -> None:
    from sqlalchemy import func, select

    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(func.count()).select_from(Problem))).scalar_one()

    if existing > 0:
        logger.info(f"AtlasCode already seeded ({existing} problems) — skipping auto-seed")
        return

    logger.info("AtlasCode problems table is empty — auto-seeding on boot (first deploy or fresh volume, ~1-2 minutes)")
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
