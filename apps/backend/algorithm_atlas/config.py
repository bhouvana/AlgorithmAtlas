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
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
        "http://localhost:5176", "http://127.0.0.1:5176",
    ]

    # Plugin discovery root — 4 levels up from config.py reaches algorithm-atlas/
    PLUGIN_ROOT: Path = Path(__file__).parent.parent.parent.parent / "plugins"

    # Repo root — same 4-levels-up anchor as PLUGIN_ROOT, reused so every
    # cwd-sensitive default (DB path, etc.) resolves identically regardless of
    # the process's working directory at startup.
    REPO_ROOT: Path = Path(__file__).parent.parent.parent.parent

    # Logging
    LOG_LEVEL: str = "DEBUG"

    # SQLite (default — zero-config for dev). Relative "./atlas.db" is kept
    # only as the literal default value for backwards compatibility with any
    # existing .env; the value actually used at runtime always goes through
    # `resolved_sqlite_url()` below, which rewrites a relative sqlite path to
    # an ABSOLUTE one anchored at REPO_ROOT. A relative URL resolves
    # differently depending on the process's cwd at startup, which is
    # exactly how `apps/backend/atlas.db` (a stale, 0-row decoy DB) came to
    # exist alongside the real 216-problem `atlas.db` at repo root. Set
    # DATABASE_URL in .env to point at a different DB entirely (e.g. Postgres
    # in production) — that always wins and is never rewritten.
    SQLITE_URL: str = "sqlite+aiosqlite:///./atlas.db"
    DATABASE_URL: str = ""

    def resolved_sqlite_url(self) -> str:
        """The URL `database.py` must actually use. Rewrites a cwd-relative
        sqlite path (`sqlite+aiosqlite:///./atlas.db` or any `///.`-prefixed
        relative variant) to an absolute path under REPO_ROOT so the DB
        resolved is always the same file regardless of the process's cwd.
        Absolute sqlite URLs and non-sqlite URLs pass through unchanged."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        url = self.SQLITE_URL
        prefix = "sqlite+aiosqlite:///"
        if url.startswith(prefix):
            rel = url[len(prefix):]
            if not Path(rel).is_absolute():
                abs_path = (self.REPO_ROOT / rel.lstrip("./")).resolve()
                return f"{prefix}{abs_path.as_posix()}"
        return url

    def resolved_sqlite_path(self) -> Path | None:
        """The bare filesystem path behind `resolved_sqlite_url()`, or None
        for a non-sqlite DATABASE_URL. Used by migration/backfill scripts
        that need to print or open the file directly rather than through
        SQLAlchemy."""
        url = self.resolved_sqlite_url()
        prefix = "sqlite+aiosqlite:///"
        if not url.startswith(prefix):
            return None
        return Path(url[len(prefix):])

    # Redis (Phase 1+)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Atlas AI — Groq LLM provider
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Atlas AI — Ollama Cloud (ollama.com), OpenAI-compatible endpoint.
    # Two keys are supported so the provider pool can round-robin between them
    # (plus Groq) instead of hammering a single key's rate limit.
    OLLAMA_API_KEY_1: str = ""
    OLLAMA_API_KEY_2: str = ""
    OLLAMA_MODEL: str = "gpt-oss:120b"
    OLLAMA_BASE_URL: str = "https://ollama.com/v1"

    class Config:
        # Walk up to find .env at the repo root (algorithm-atlas/) regardless of CWD
        env_file = str(Path(__file__).parent.parent.parent.parent / ".env")
        env_file_encoding = "utf-8"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
