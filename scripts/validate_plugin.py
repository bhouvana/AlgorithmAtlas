#!/usr/bin/env python3
"""
validate_plugin.py — Validate a community algorithm plugin before submission.

Usage:
    python scripts/validate_plugin.py <plugin-directory> [--run-tests]

Exit codes:
    0  All checks passed
    1  One or more checks failed

Checks performed:
    1. Directory structure (manifest.json, algorithm.py, tests/ present)
    2. manifest.json validates against the manifest schema
    3. category in manifest matches the parent directory name
    4. No forbidden imports in algorithm.py (AST scan)
    5. Plugin class can be imported and instantiates without error
    6. (with --run-tests) pytest tests/ passes
"""
from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
import types
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Schema (mirrors apps/backend/algorithm_atlas/plugins/loader.py)
# ──────────────────────────────────────────────────────────────────────────────

MANIFEST_SCHEMA = {
    "type": "object",
    "required": [
        "schema_version", "id", "name", "version",
        "category", "visualization_type", "entry_point",
        "description", "complexity",
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
        },
        "description": {"type": "string", "minLength": 20},
        "complexity": {
            "type": "object",
            "required": ["time_best", "time_average", "time_worst", "space"],
            "properties": {
                "time_best":    {"type": "string"},
                "time_average": {"type": "string"},
                "time_worst":   {"type": "string"},
                "space":        {"type": "string"},
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
                    "url":   {"type": "string"},
                    "type":  {"type": "string", "enum": ["paper", "book", "video", "article"]},
                },
            },
        },
        "benchmark_enabled": {"type": "boolean"},
    },
    "additionalProperties": True,
}

ALLOWED_STDLIB = {
    "math", "random", "heapq", "bisect", "collections", "itertools",
    "functools", "enum", "dataclasses", "typing", "typing_extensions",
    "abc", "copy", "operator", "string", "re", "sys", "os", "io",
    "pathlib", "json", "struct", "array",
}

ALLOWED_THIRD_PARTY = {
    "algorithm_atlas_sdk", "numpy", "scipy", "networkx",
    "sympy", "pandas", "polars",
}

FORBIDDEN_PREFIXES = {
    "algorithm_atlas", "fastapi", "sqlalchemy", "alembic",
    "uvicorn", "starlette", "pydantic",
}

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

PASS = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"
WARN = "\033[33m⚠\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"

failures: list[str] = []
warnings: list[str] = []


def ok(msg: str) -> None:
    print(f"  {PASS} {msg}")


def fail(msg: str) -> None:
    print(f"  {FAIL} {msg}")
    failures.append(msg)


def warn(msg: str) -> None:
    print(f"  {WARN} {msg}")
    warnings.append(msg)


def section(title: str) -> None:
    print(f"\n{BOLD}{title}{RESET}")


# ──────────────────────────────────────────────────────────────────────────────
# Checks
# ──────────────────────────────────────────────────────────────────────────────

def check_structure(plugin_dir: Path) -> bool:
    section("1. Directory structure")
    all_ok = True
    for name in ("manifest.json", "algorithm.py"):
        p = plugin_dir / name
        if p.exists():
            ok(f"{name} present")
        else:
            fail(f"{name} missing")
            all_ok = False
    tests_dir = plugin_dir / "tests"
    if tests_dir.is_dir():
        test_files = list(tests_dir.glob("test_*.py"))
        if test_files:
            ok(f"tests/ directory with {len(test_files)} test file(s)")
        else:
            warn("tests/ directory exists but contains no test_*.py files")
    else:
        warn("tests/ directory missing — tests required before PR merge")
    return all_ok


def check_manifest(plugin_dir: Path) -> dict | None:
    section("2. manifest.json validation")
    manifest_path = plugin_dir / "manifest.json"
    if not manifest_path.exists():
        fail("manifest.json not found — skipping validation")
        return None

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON: {e}")
        return None

    try:
        from jsonschema import validate, ValidationError
        validate(instance=manifest, schema=MANIFEST_SCHEMA)
        ok("Schema valid")
    except ImportError:
        warn("jsonschema not installed — skipping schema check (pip install jsonschema)")
    except ValidationError as e:
        fail(f"Schema error: {e.message}")
        return None

    # ID must match directory name
    expected_id = plugin_dir.name
    if manifest.get("id") == expected_id:
        ok(f"id matches directory name: {expected_id!r}")
    else:
        fail(f"id {manifest.get('id')!r} does not match directory name {expected_id!r}")

    # category must match parent directory name
    parent_name = plugin_dir.parent.name
    if manifest.get("category") == parent_name:
        ok(f"category matches parent directory: {parent_name!r}")
    else:
        fail(
            f"category {manifest.get('category')!r} does not match "
            f"parent directory {parent_name!r}"
        )

    return manifest


def check_imports(plugin_dir: Path) -> None:
    section("3. Import safety scan (AST)")
    alg_path = plugin_dir / "algorithm.py"
    if not alg_path.exists():
        fail("algorithm.py not found — skipping import scan")
        return

    source = alg_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        fail(f"Syntax error in algorithm.py: {e}")
        return

    bad: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            else:
                names = [node.module or ""]
            for name in names:
                root = name.split(".")[0]
                if root in FORBIDDEN_PREFIXES or any(
                    name.startswith(p) for p in FORBIDDEN_PREFIXES
                ):
                    bad.append(name)

    if bad:
        for b in bad:
            fail(f"Forbidden import: {b!r}")
    else:
        ok("No forbidden imports detected")


def check_plugin_class(plugin_dir: Path) -> None:
    section("4. Plugin class import and instantiation")
    alg_path = plugin_dir / "algorithm.py"
    if not alg_path.exists():
        fail("algorithm.py not found — skipping class check")
        return

    # Ensure SDK is importable
    repo_root = Path(__file__).parents[1]
    sdk_path = repo_root / "packages" / "plugin-sdk" / "python"
    if sdk_path.exists() and str(sdk_path) not in sys.path:
        sys.path.insert(0, str(sdk_path))

    spec = importlib.util.spec_from_file_location(
        f"_atlas_plugin_{plugin_dir.name}", alg_path
    )
    if spec is None or spec.loader is None:
        fail("Could not create module spec from algorithm.py")
        return

    mod = types.ModuleType(spec.name)
    try:
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        ok("algorithm.py imported without errors")
    except Exception as e:
        fail(f"Import error: {e}")
        return

    # Find AlgorithmPlugin subclass
    try:
        from algorithm_atlas_sdk.protocols import AlgorithmPlugin
        plugin_classes = [
            cls for cls in vars(mod).values()
            if isinstance(cls, type) and issubclass(cls, AlgorithmPlugin) and cls is not AlgorithmPlugin
        ]
    except ImportError:
        warn("algorithm_atlas_sdk not installed — skipping protocol check (pip install -e packages/plugin-sdk/python)")
        return

    if not plugin_classes:
        fail("No AlgorithmPlugin subclass found in algorithm.py")
        return

    for cls in plugin_classes:
        try:
            instance = cls()
            ok(f"Instantiated {cls.__name__}")
            # Try metadata()
            try:
                meta = instance.metadata()
                ok(f"metadata() returned: {type(meta).__name__}")
            except Exception as e:
                warn(f"metadata() raised: {e}")
        except Exception as e:
            fail(f"Could not instantiate {cls.__name__}: {e}")


def run_tests(plugin_dir: Path) -> None:
    section("5. Running tests")
    tests_dir = plugin_dir / "tests"
    if not tests_dir.is_dir():
        warn("tests/ directory not found — skipping")
        return

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(tests_dir), "-v", "--tb=short"],
        cwd=plugin_dir.parents[2],  # repo root equivalent
    )
    if result.returncode == 0:
        ok("All tests passed")
    else:
        fail(f"pytest exited with code {result.returncode}")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate an Algorithm Atlas community plugin."
    )
    parser.add_argument("plugin_dir", help="Path to the plugin directory")
    parser.add_argument(
        "--run-tests", action="store_true",
        help="Run pytest on the tests/ subdirectory",
    )
    args = parser.parse_args()

    plugin_dir = Path(args.plugin_dir).resolve()
    if not plugin_dir.is_dir():
        print(f"Error: {plugin_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"\n{BOLD}Validating plugin: {plugin_dir.name}{RESET}")
    print(f"Path: {plugin_dir}")

    structure_ok = check_structure(plugin_dir)
    if structure_ok:
        check_manifest(plugin_dir)
        check_imports(plugin_dir)
        check_plugin_class(plugin_dir)
        if args.run_tests:
            run_tests(plugin_dir)

    print()
    if failures:
        print(f"{FAIL} {BOLD}{len(failures)} check(s) failed:{RESET}")
        for f in failures:
            print(f"    • {f}")
        if warnings:
            print(f"{WARN} {len(warnings)} warning(s):")
            for w in warnings:
                print(f"    • {w}")
        sys.exit(1)
    else:
        if warnings:
            print(f"{WARN} {BOLD}Passed with {len(warnings)} warning(s):{RESET}")
            for w in warnings:
                print(f"    • {w}")
        else:
            print(f"{PASS} {BOLD}All checks passed!{RESET}")
        print("\nPlugin is ready for PR submission.")
        sys.exit(0)


if __name__ == "__main__":
    main()
