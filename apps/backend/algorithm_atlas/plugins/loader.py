"""
Plugin Loader — discovers and loads algorithm plugins from the filesystem.

Discovery is filesystem-based: any directory containing a valid manifest.json
is treated as a plugin candidate. Failed plugins are logged and skipped;
they never crash the application.

Security: import boundaries are statically validated before plugin code executes.
Plugins may only import from algorithm_atlas_sdk, the standard library, and
approved third-party packages (numpy, scipy, networkx).
"""
from __future__ import annotations

import ast
import importlib.util
import json
import types
from pathlib import Path
from typing import Set, Type

from jsonschema import ValidationError, validate
from loguru import logger

from algorithm_atlas_sdk.protocols import AlgorithmPlugin

from .registry import AlgorithmNotFound, PluginRegistry, RegisteredAlgorithm

# ──────────────────────────────────────────────────────────────────────────────
# Manifest schema
# ──────────────────────────────────────────────────────────────────────────────

MANIFEST_SCHEMA = {
    "type": "object",
    "required": [
        "schema_version", "id", "name", "version",
        "category", "visualization_type", "entry_point",
        "complexity",
    ],
    "properties": {
        "schema_version": {"type": "string"},
        "id": {"type": "string", "pattern": r"^[a-z0-9-]+$"},
        "name": {"type": "string", "minLength": 1},
        "version": {"type": "string"},
        "category": {"type": "string"},
        "visualization_type": {
            "type": "string",
            "enum": [
                "ARRAY_BARS", "ARRAY_BARS_SEARCH", "GRAPH", "TREE", "MATRIX", "GRID",
                "CURVE", "PARTICLE_FIELD", "NETWORK_TOPOLOGY",
                "GEOMETRIC", "STATE_MACHINE", "PROBABILITY_SPACE", "TIMELINE",
            ],
        },
        "entry_point": {"type": "string"},
        "execution_target": {
            "type": "string",
            "enum": ["server", "wasm", "both"],
            "default": "server",
        },
        "complexity": {
            "type": "object",
            "required": ["time_best", "time_average", "time_worst", "space"],
            "properties": {
                "time_best": {"type": "string"},
                "time_average": {"type": "string"},
                "time_worst": {"type": "string"},
                "space": {"type": "string"},
            },
        },
        "tags": {"type": "array", "items": {"type": "string"}},
        "references": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "type"],
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "type": {"type": "string", "enum": ["paper", "book", "video", "article"]},
                },
            },
        },
        "benchmark_enabled": {"type": "boolean"},
        "rust_accelerated": {"type": "boolean"},
    },
    "additionalProperties": True,
}

# Packages plugins are allowed to import from
ALLOWED_IMPORT_PREFIXES: Set[str] = {
    "algorithm_atlas_sdk",
    # Standard library (no prefix needed — handled separately)
    # Approved scientific packages
    "numpy",
    "scipy",
    "networkx",
    "sympy",
    "pandas",
    "polars",
    # Typing
    "typing",
    "typing_extensions",
    "collections",
    "dataclasses",
    "enum",
    "functools",
    "itertools",
    "math",
    "random",
    "heapq",
    "bisect",
}

FORBIDDEN_IMPORT_PREFIXES: Set[str] = {
    "algorithm_atlas",          # Internal — only SDK is allowed
    "fastapi",
    "sqlalchemy",
    "alembic",
}


class PluginLoadError(Exception):
    pass


# ──────────────────────────────────────────────────────────────────────────────
# Loader
# ──────────────────────────────────────────────────────────────────────────────

class PluginLoader:
    """Discovers and loads plugins into the provided PluginRegistry."""

    def __init__(self, registry: PluginRegistry) -> None:
        self._registry = registry

    def discover(self, plugin_root: Path) -> int:
        """
        Walk plugin_root recursively.
        Load every directory that contains a valid manifest.json.
        Returns the number of successfully loaded plugins.
        """
        if not plugin_root.exists():
            logger.warning(f"Plugin root does not exist: {plugin_root}")
            return 0

        loaded = 0
        for manifest_path in sorted(plugin_root.rglob("manifest.json")):
            try:
                self._load_one(manifest_path)
                loaded += 1
            except PluginLoadError as exc:
                logger.error(f"Plugin load failed at {manifest_path}: {exc}")
            except Exception as exc:
                logger.exception(f"Unexpected error loading plugin at {manifest_path}: {exc}")

        logger.info(f"Plugin discovery complete — {loaded} plugin(s) loaded from {plugin_root}")
        return loaded

    def _load_one(self, manifest_path: Path) -> None:
        plugin_dir = manifest_path.parent
        manifest = self._read_and_validate_manifest(manifest_path)

        entry_path = plugin_dir / manifest["entry_point"]
        if not entry_path.exists():
            raise PluginLoadError(
                f"entry_point '{manifest['entry_point']}' not found in {plugin_dir}"
            )

        self._check_import_boundaries(entry_path)

        module = self._load_module(manifest["id"], entry_path)
        algorithm_class = self._find_algorithm_class(module, manifest["id"])

        registered = RegisteredAlgorithm(
            manifest=manifest,
            algorithm_class=algorithm_class,
            plugin_dir=plugin_dir,
        )
        self._registry.register(registered)

    def _read_and_validate_manifest(self, path: Path) -> dict:
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PluginLoadError(f"Invalid JSON in manifest: {exc}") from exc

        try:
            validate(instance=manifest, schema=MANIFEST_SCHEMA)
        except ValidationError as exc:
            raise PluginLoadError(f"Manifest schema validation failed: {exc.message}") from exc

        return manifest

    def _check_import_boundaries(self, entry_path: Path) -> None:
        """
        Static AST analysis. Reject plugins that import from forbidden namespaces.
        This runs BEFORE any plugin code is executed.
        """
        try:
            tree = ast.parse(entry_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            raise PluginLoadError(f"Syntax error in {entry_path}: {exc}") from exc

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._assert_import_allowed(alias.name, entry_path)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._assert_import_allowed(node.module, entry_path)

    def _assert_import_allowed(self, module_name: str, source: Path) -> None:
        # Explicitly allowed imports take precedence over the forbidden prefix check.
        # This matters because algorithm_atlas_sdk shares the algorithm_atlas prefix.
        if any(module_name.startswith(p) for p in ALLOWED_IMPORT_PREFIXES):
            return
        if any(module_name.startswith(p) for p in FORBIDDEN_IMPORT_PREFIXES):
            raise PluginLoadError(
                f"Forbidden import '{module_name}' in {source.name}. "
                f"Plugins may only import from: {sorted(ALLOWED_IMPORT_PREFIXES)}"
            )

    def _load_module(self, plugin_id: str, entry_path: Path) -> types.ModuleType:
        module_name = f"algorithm_atlas_plugins.{plugin_id.replace('-', '_')}"
        spec = importlib.util.spec_from_file_location(module_name, entry_path)
        if spec is None or spec.loader is None:
            raise PluginLoadError(f"Cannot create module spec for {entry_path}")
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)  # type: ignore[union-attr]
        except Exception as exc:
            raise PluginLoadError(f"Error executing plugin module: {exc}") from exc
        return module

    def _find_algorithm_class(
        self, module: types.ModuleType, plugin_id: str
    ) -> Type[AlgorithmPlugin]:
        """
        Find the class in the module that implements AlgorithmPlugin.
        Raises PluginLoadError if none found or multiple found.
        """
        def _is_plugin_class(cls: type) -> bool:
            try:
                return isinstance(cls(), AlgorithmPlugin)
            except TypeError:
                # Helper classes that require constructor arguments are not plugins
                return False

        candidates = [
            obj
            for name in dir(module)
            if not name.startswith("_")
            for obj in [getattr(module, name)]
            if isinstance(obj, type)
            and obj.__module__ == module.__name__
            and _is_plugin_class(obj)
        ]

        if not candidates:
            raise PluginLoadError(
                f"No class implementing AlgorithmPlugin found in plugin '{plugin_id}'. "
                "Ensure your class implements metadata(), initialize(), and steps()."
            )
        if len(candidates) > 1:
            names = [c.__name__ for c in candidates]
            raise PluginLoadError(
                f"Multiple AlgorithmPlugin implementations found in '{plugin_id}': {names}. "
                "Each plugin must define exactly one algorithm class."
            )

        return candidates[0]
