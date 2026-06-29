"""
Public API for Algorithm Atlas notebook usage.

    from algorithm_atlas_notebook import run, compare

    # Run a single algorithm
    display = run("bubble-sort", seed=42, array_size=30)
    display                           # renders animated player in Jupyter
    display.save_html("demo.html")    # export to standalone HTML file

    # Compare two algorithms side-by-side
    compare("bubble-sort", "quick-sort", array_size=30, seed=42)
"""
from __future__ import annotations

import sys
import pathlib
from typing import Any

from algorithm_atlas_sdk.types import SimulationParams

from .display import AtlasDisplay

# ── Plugin registry ───────────────────────────────────────────────────────────

def _find_plugin_dir() -> pathlib.Path | None:
    """Walk up from this file to find the algorithm-atlas project root."""
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "apps" / "backend" / "algorithm_atlas" / "plugins"
        if candidate.exists():
            return candidate
    return None


def _get_registry():
    """Import and return the plugin registry, running discovery if needed."""
    plugin_dir = _find_plugin_dir()
    if plugin_dir is None:
        raise ImportError(
            "Cannot locate the algorithm-atlas project root. "
            "Make sure you're running from inside the repository."
        )
    backend_dir = plugin_dir.parent.parent
    sdk_dir = plugin_dir.parents[3] / "packages" / "plugin-sdk" / "python"

    for d in (str(backend_dir), str(sdk_dir)):
        if d not in sys.path:
            sys.path.insert(0, d)

    from algorithm_atlas.plugins.registry import get_registry  # type: ignore[import]
    registry = get_registry()

    if len(registry) == 0:
        # Registry is empty (not yet populated by a running server).
        # Run plugin discovery directly so the notebook kernel can work standalone.
        from algorithm_atlas.plugins.loader import PluginLoader  # type: ignore[import]
        loader = PluginLoader(registry)
        # plugin_dir points to apps/backend/algorithm_atlas/plugins — the plugins
        # folder we need is the project-root-level "plugins/" directory.
        project_root = plugin_dir.parents[3]
        plugins_root = project_root / "plugins"
        loader.discover(plugins_root)

    return registry


# ── Core run function ─────────────────────────────────────────────────────────

def run(
    slug: str,
    seed: int = 42,
    **params: Any,
) -> AtlasDisplay:
    """
    Run an algorithm and return an interactive visualization.

    Args:
        slug:   Algorithm identifier, e.g. "bubble-sort", "merge-sort".
        seed:   PRNG seed for deterministic input generation.
        **params: Algorithm-specific parameters (e.g. array_size=50,
                  input_order="random").

    Returns:
        AtlasDisplay — renders as an animated bar chart in Jupyter.
        Call .save_html("out.html") to export as a static file.

    Examples:
        run("bubble-sort")
        run("quick-sort", seed=7, array_size=40, input_order="reverse")
        run("merge-sort", array_size=64).save_html("merge_demo.html")

    Raises:
        KeyError:   When the slug is not found in the plugin registry.
        RuntimeError: When the algorithm fails to initialize or step.
    """
    # Set sensible defaults
    if "array_size" not in params:
        params["array_size"] = 20
    if "input_order" not in params:
        params["input_order"] = "random"

    registry = _get_registry()
    registered = registry.get(slug)
    algorithm = registered.instantiate()

    sim_params = SimulationParams(seed=seed, inputs=dict(params))

    # Collect all frames
    initial_state = algorithm.initialize(sim_params)
    gen = algorithm.steps(initial_state)

    raw_frames: list[dict[str, Any]] = [_state_to_frame(initial_state, 0)]
    idx = 1
    try:
        while True:
            state = next(gen)
            raw_frames.append(_state_to_frame(state, idx))
            idx += 1
    except StopIteration as exc:
        if exc.value is not None:
            raw_frames.append(_state_to_frame(exc.value, idx))

    return AtlasDisplay(frames=raw_frames, slug=slug, seed=seed, params=params)


# ── Side-by-side comparison ───────────────────────────────────────────────────

def compare(*slugs: str, seed: int = 42, **params: Any) -> None:
    """
    Display multiple algorithm simulations side-by-side.

    Renders each as a separate cell output using IPython.display.
    Requires IPython to be available (i.e., must run inside Jupyter).

    Args:
        *slugs: Two or more algorithm slugs to compare.
        seed:   Shared seed (same input array for fair comparison).
        **params: Shared parameters applied to all algorithms.

    Example:
        compare("bubble-sort", "insertion-sort", "quick-sort", array_size=30)
    """
    try:
        from IPython.display import display as ipy_display  # type: ignore[import]
    except ImportError as e:
        raise ImportError("compare() requires IPython. Install with: pip install ipython") from e

    for slug in slugs:
        ipy_display(run(slug, seed=seed, **params))


# ── Helpers ───────────────────────────────────────────────────────────────────

def _state_to_frame(state: Any, idx: int) -> dict[str, Any]:
    """Convert an AlgorithmState (Python SDK type) to a plain frame dict."""
    if hasattr(state, "to_dict"):
        raw = state.to_dict()
    elif hasattr(state, "__dict__"):
        raw = _deep_serialize(state)
    else:
        raw = {}

    return {
        "frame_index": idx,
        "state":       raw,
        "timestamp_ms": idx * 100.0,
        "event_label": getattr(state, "description", None),
    }


def _deep_serialize(obj: Any) -> Any:
    """Recursively convert SDK types to plain dicts/lists for JSON serialization."""
    if hasattr(obj, "__dict__"):
        return {k: _deep_serialize(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    if isinstance(obj, (list, tuple)):
        return [_deep_serialize(x) for x in obj]
    return obj
