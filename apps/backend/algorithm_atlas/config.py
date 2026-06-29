"""
Application configuration via environment variables.
All settings have sensible development defaults.
"""
from __future__ import annotations

from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Algorithm Atlas"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS — in production, restrict to your frontend origin
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Plugin discovery root — 4 levels up from config.py reaches algorithm-atlas/
    PLUGIN_ROOT: Path = Path(__file__).parent.parent.parent.parent / "plugins"

    # Logging
    LOG_LEVEL: str = "DEBUG"

    # SQLite (default — zero-config for dev). Set DATABASE_URL in .env to switch.
    SQLITE_URL: str = "sqlite+aiosqlite:///./atlas.db"

    # Redis (Phase 1+)
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
