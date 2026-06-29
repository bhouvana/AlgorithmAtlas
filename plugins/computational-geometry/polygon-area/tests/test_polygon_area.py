"""Tests for Polygon Area Shoelace plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "polygon_area", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PolygonAreaSimulation = _mod.PolygonAreaSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n=6, seed=0):
    sim = PolygonAreaSimulation()
    params = SimulationParams(seed=seed, inputs={"vertex_count": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestPolygonAreaMetadata:
    def test_slug(self):
        assert PolygonAreaSimulation().metadata().slug == "polygon-area"

    def test_category(self):
        assert PolygonAreaSimulation().metadata().category == "computational-geometry"


class TestPolygonAreaCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_area_positive(self, seed: int):
        _, _, final = run(6, seed)
        area = float(final.description.split("= ")[-1].split(" ")[0])
        assert area > 0

    def test_frame_count_equals_vertex_count(self):
        initial, frames, _ = run(6, 0)
        pts = list(initial.path)
        assert len(frames) == len(pts)

    def test_final_description_contains_area(self):
        _, _, final = run(6)
        assert "Area" in final.description

    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0


class TestPolygonAreaFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
