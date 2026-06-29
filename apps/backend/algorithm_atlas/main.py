"""
Algorithm Atlas — FastAPI application entry point.

Startup sequence:
1. Configure logging
2. Discover and register all plugins
3. Mount API router
4. Serve
"""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .api.v1.router import api_router
from .config import get_settings
from .database import init_db
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

    yield

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
