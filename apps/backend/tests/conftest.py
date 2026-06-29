"""
Backend test fixtures.

Sets PLUGIN_ROOT before any algorithm_atlas imports so pydantic-settings
picks it up correctly. The registry singleton is reset between test sessions
by clearing the cached settings.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Point to algorithm-atlas/plugins/ — must be set before importing settings
_ROOT = Path(__file__).parent.parent.parent.parent  # algorithm-atlas/
os.environ.setdefault("PLUGIN_ROOT", str(_ROOT / "plugins"))

# Ensure the backend package is importable when pytest runs from repo root
_BACKEND_DIR = Path(__file__).parent.parent  # apps/backend/
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# Reset the settings singleton so it re-reads the env var above
import algorithm_atlas.config as _cfg
_cfg._settings = None

# Reset the registry singleton so lifespan gets a clean state
from algorithm_atlas.plugins.registry import PluginRegistry
import algorithm_atlas.plugins.registry as _reg_mod
_reg_mod._registry = PluginRegistry()

from algorithm_atlas.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c
