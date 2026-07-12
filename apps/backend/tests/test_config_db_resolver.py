"""Regression tests for the canonical DB path resolver (Phase 1 of the
dual-mode completion pass). The core bug this guards against: a relative
sqlite URL resolves differently depending on the process's cwd at startup,
which is exactly how `apps/backend/atlas.db` (a stale, 0-row decoy) came to
exist alongside the real 216-problem `atlas.db` at repo root.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from algorithm_atlas.config import Settings


def test_relative_sqlite_url_resolves_to_absolute_repo_root_path():
    s = Settings()
    resolved = s.resolved_sqlite_url()
    assert resolved.startswith("sqlite+aiosqlite:///")
    path = Path(resolved[len("sqlite+aiosqlite:///"):])
    assert path.is_absolute()
    assert path.name == "atlas.db"
    assert path.parent == s.REPO_ROOT.resolve()


def test_resolution_is_independent_of_process_cwd(tmp_path, monkeypatch):
    s = Settings()
    expected = s.resolved_sqlite_url()
    monkeypatch.chdir(tmp_path)
    # A fresh Settings() instantiated with cwd pointed somewhere else entirely
    # must still resolve to the exact same absolute path -- REPO_ROOT is
    # anchored on config.py's own file location, never on cwd.
    s2 = Settings()
    assert s2.resolved_sqlite_url() == expected


def test_never_silently_resolves_to_the_known_decoy_db():
    s = Settings()
    resolved_path = s.resolved_sqlite_path()
    decoy = s.REPO_ROOT / "apps" / "backend" / "atlas.db"
    assert resolved_path is not None
    assert resolved_path.resolve() != decoy.resolve()


def test_explicit_database_url_always_wins():
    s = Settings(DATABASE_URL="postgresql+asyncpg://user:pass@host/db")
    assert s.resolved_sqlite_url() == "postgresql+asyncpg://user:pass@host/db"


def test_absolute_sqlite_url_passes_through_unchanged():
    abs_path = (Path(__file__).parent / "somewhere.db").as_posix()
    s = Settings(SQLITE_URL=f"sqlite+aiosqlite:///{abs_path}")
    assert s.resolved_sqlite_url() == f"sqlite+aiosqlite:///{abs_path}"
