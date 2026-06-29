"""Tests for Convex Hull Graham Scan plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "convex_hull_graham",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ConvexHullGrahamSimulation = _mod.ConvexHullGrahamSimulation
_cross = _mod._cross

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 10, seed: int = 0):
    sim = ConvexHullGrahamSimulation()
    params = SimulationParams(seed=seed, inputs={"point_count": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestConvexHullGrahamMetadata:
    def test_slug(self):
        assert ConvexHullGrahamSimulation().metadata().slug == "convex-hull-graham"

    def test_category(self):
        assert ConvexHullGrahamSimulation().metadata().category == "computational-geometry"

    def test_visualization_type(self):
        assert ConvexHullGrahamSimulation().metadata().visualization_type == "GRID"


class TestConvexHullGrahamCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_hull_is_convex(self, seed: int):
        """All consecutive triplets on hull must be CCW (non-negative cross product)."""
        _, _, final = run(10, seed)
        hull = list(final.path)
        n = len(hull)
        if n < 3:
            return
        for i in range(n):
            o, a, b = hull[i], hull[(i + 1) % n], hull[(i + 2) % n]
            assert _cross(o, a, b) >= 0, f"Non-CCW turn at {o}, {a}, {b}"

    def test_has_frames(self):
        _, frames, _ = run(10)
        assert len(frames) > 0

    def test_final_description_contains_hull(self):
        _, _, final = run(10)
        assert "hull" in final.description.lower()

    @pytest.mark.parametrize("seed", range(5))
    def test_hull_cells_marked(self, seed: int):
        _, _, final = run(10, seed)
        hull_pts = set(map(tuple, final.path))
        for r, c in hull_pts:
            assert final.grid[r][c] == _mod.CELL_HULL


class TestConvexHullGrahamFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(10)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
