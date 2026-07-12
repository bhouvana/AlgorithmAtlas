"""
Canonical algorithm discovery.

This is the ONLY place AtlasCode should learn what algorithms exist. It loads
the same plugin manifests (plugins/<category>/<slug>/manifest.json) that power
the Catalog, visualizations, and benchmarks — never a hand-maintained list.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..config import get_settings
from ..plugins.loader import PluginLoader
from ..plugins.registry import PluginRegistry, RegisteredAlgorithm


@dataclass(frozen=True)
class CanonicalAlgorithm:
    slug: str
    name: str
    category: str
    visualization_type: str
    tags: tuple[str, ...]
    complexity: dict = field(default_factory=dict)
    intuition: str = ""
    description: str = ""

    @classmethod
    def from_registered(cls, reg: RegisteredAlgorithm) -> "CanonicalAlgorithm":
        m = reg.manifest
        return cls(
            slug=reg.slug,
            name=reg.name,
            category=reg.category,
            visualization_type=reg.visualization_type,
            tags=tuple(m.get("tags", [])),
            complexity=m.get("complexity", {}),
            intuition=m.get("intuition", ""),
            description=m.get("description", ""),
        )


def discover_canonical_algorithms() -> list[CanonicalAlgorithm]:
    """
    Load every plugin under settings.PLUGIN_ROOT into a fresh, throwaway
    registry and return the full canonical algorithm list.

    Uses its own PluginRegistry instance (not the FastAPI app-wide singleton)
    so this can be called from scripts/tests without depending on app startup
    having already run, and without mutating global state.
    """
    registry = PluginRegistry()
    loader = PluginLoader(registry)
    loader.discover(get_settings().PLUGIN_ROOT)
    return [CanonicalAlgorithm.from_registered(r) for r in registry.list_all()]


def discover_registered_algorithms() -> list[RegisteredAlgorithm]:
    """Same discovery, but returns the raw RegisteredAlgorithm (with .instantiate())."""
    registry = PluginRegistry()
    loader = PluginLoader(registry)
    loader.discover(get_settings().PLUGIN_ROOT)
    return registry.list_all()
