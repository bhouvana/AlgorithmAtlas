"""
Plugin Registry — single source of truth for all registered algorithms.

After discovery, every algorithm (built-in and community) is indistinguishable
from the registry's perspective. The registry maps slug → RegisteredAlgorithm.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Type

from loguru import logger

from algorithm_atlas_sdk.protocols import AlgorithmPlugin


@dataclass
class RegisteredAlgorithm:
    """Metadata + class reference for a loaded plugin."""
    manifest: dict
    algorithm_class: Type[AlgorithmPlugin]
    plugin_dir: Path

    @property
    def slug(self) -> str:
        return self.manifest["id"]

    @property
    def name(self) -> str:
        return self.manifest["name"]

    @property
    def category(self) -> str:
        return self.manifest["category"]

    @property
    def visualization_type(self) -> str:
        return self.manifest["visualization_type"]

    @property
    def execution_target(self) -> str:
        return self.manifest.get("execution_target", "server")

    def instantiate(self) -> AlgorithmPlugin:
        """Return a fresh algorithm instance. Instances are stateless."""
        return self.algorithm_class()


class AlgorithmNotFound(KeyError):
    pass


class PluginRegistry:
    """
    Holds all RegisteredAlgorithm entries.
    Thread-safe for reads. Writes happen only at startup during discovery.
    """

    def __init__(self) -> None:
        self._algorithms: Dict[str, RegisteredAlgorithm] = {}

    def register(self, algorithm: RegisteredAlgorithm) -> None:
        slug = algorithm.slug
        if slug in self._algorithms:
            logger.warning(
                f"Overwriting existing algorithm '{slug}' — "
                "check for duplicate plugin IDs"
            )
        self._algorithms[slug] = algorithm
        logger.info(f"Registered algorithm: {slug} ({algorithm.name})")

    def get(self, slug: str) -> RegisteredAlgorithm:
        if slug not in self._algorithms:
            raise AlgorithmNotFound(
                f"Algorithm '{slug}' is not registered. "
                f"Available: {list(self._algorithms.keys())}"
            )
        return self._algorithms[slug]

    def list_all(self) -> List[RegisteredAlgorithm]:
        return sorted(self._algorithms.values(), key=lambda a: (a.category, a.name))

    def list_by_category(self, category: str) -> List[RegisteredAlgorithm]:
        return [a for a in self.list_all() if a.category == category]

    def categories(self) -> List[str]:
        return sorted({a.category for a in self._algorithms.values()})

    def __len__(self) -> int:
        return len(self._algorithms)

    def __iter__(self) -> Iterator[RegisteredAlgorithm]:
        return iter(self.list_all())

    def __contains__(self, slug: str) -> bool:
        return slug in self._algorithms


# Module-level singleton
_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    return _registry
