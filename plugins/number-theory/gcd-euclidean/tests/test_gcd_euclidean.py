"""Tests for Euclidean GCD plugin."""
from __future__ import annotations

import importlib.util
import sys
from math import gcd
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "gcd_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
EuclideanGCDSimulation = _mod.EuclideanGCDSimulation

from algorithm_atlas_sdk import SimulationParams


def run(a: int = 48, b: int = 18):
    sim = EuclideanGCDSimulation()
    params = SimulationParams(seed=0, inputs={"a": a, "b": b}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestGCDMetadata:
    def test_slug(self):
        assert EuclideanGCDSimulation().metadata().slug == "gcd-euclidean"

    def test_category(self):
        assert EuclideanGCDSimulation().metadata().category == "number-theory"

    def test_visualization_type(self):
        assert EuclideanGCDSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestGCDCorrectness:
    @pytest.mark.parametrize("a,b", [
        (48, 18), (100, 75), (17, 13), (120, 45), (56, 98),
        (10, 10), (10, 20), (14, 10), (36, 24), (100, 37),
    ])
    def test_gcd_matches_stdlib(self, a: int, b: int):
        _, _, final = run(a, b)
        expected = gcd(a, b)
        # final.array[0] should be the GCD
        assert final.array[0] == expected, (
            f"gcd({a},{b}): got {final.array[0]}, expected {expected}"
        )

    def test_final_second_element_is_zero(self):
        _, _, final = run(48, 18)
        assert final.array[1] == 0

    def test_gcd_divides_both(self):
        for a, b in [(48, 18), (100, 75), (17, 13)]:
            _, _, final = run(a, b)
            g = final.array[0]
            assert a % g == 0
            assert b % g == 0

    def test_equal_inputs(self):
        _, _, final = run(42, 42)
        assert final.array[0] == 42


class TestGCDFrames:
    def test_has_frames(self):
        _, frames, _ = run(48, 18)
        assert len(frames) > 0

    def test_initial_array_is_inputs(self):
        initial, _, _ = run(48, 18)
        assert initial.array == (48, 18)

    def test_sorted_indices_at_end(self):
        _, _, final = run(48, 18)
        assert 0 in final.sorted_indices
        assert 1 in final.sorted_indices

    def test_serializable(self):
        import json
        initial, frames, final = run(48, 18)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = EuclideanGCDSimulation()
        p = SimulationParams(seed=0, inputs={"a": 1, "b": 1}, config={})
        s = sim.initialize(p)
        assert s.array == (10, 10)

    def test_clamp_max(self):
        sim = EuclideanGCDSimulation()
        p = SimulationParams(seed=0, inputs={"a": 999, "b": 999}, config={})
        s = sim.initialize(p)
        assert s.array == (200, 200)
