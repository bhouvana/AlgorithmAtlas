"""Tests for Gift Wrapping convex hull plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "gift_wrapping", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
GiftWrappingSimulation = _mod.GiftWrappingSimulation
_cross = _mod._cross

from algorithm_atlas_sdk import SimulationParams


def run(n=10, seed=0):
    sim = GiftWrappingSimulation()
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


class TestGiftWrappingMetadata:
    def test_slug(self):
        assert GiftWrappingSimulation().metadata().slug == "gift-wrapping"

    def test_category(self):
        assert GiftWrappingSimulation().metadata().category == "computational-geometry"

    def test_visualization_type(self):
        assert GiftWrappingSimulation().metadata().visualization_type == "GRID"


class TestGiftWrappingCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_hull_is_convex(self, seed: int):
        _, _, final = run(10, seed)
        hull = list(final.path)
        n = len(hull)
        if n < 3:
            return
        for i in range(n):
            o, a, b = hull[i], hull[(i+1)%n], hull[(i+2)%n]
            assert _cross(o, a, b) >= 0, f"CW turn at {o}"

    def test_final_description(self):
        _, _, final = run(10)
        assert "hull" in final.description.lower()

    def test_has_frames(self):
        _, frames, _ = run(10)
        assert len(frames) > 0


class TestGiftWrappingFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(10)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
