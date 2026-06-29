"""Tests for Closest Pair of Points plugin."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from typing import List, Tuple

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "closest_pair",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ClosestPairSimulation = _mod.ClosestPairSimulation
_SCALE = _mod._SCALE

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 42):
    sim = ClosestPairSimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def brute_force_closest(xs: list, ys: list) -> float:
    n = len(xs)
    best = math.inf
    for i in range(n):
        for j in range(i + 1, n):
            dx = (xs[i] - xs[j]) / _SCALE
            dy = (ys[i] - ys[j]) / _SCALE
            d = math.sqrt(dx * dx + dy * dy)
            best = min(best, d)
    return best


class TestClosestPairMetadata:
    def test_slug(self):
        assert ClosestPairSimulation().metadata().slug == "closest-pair"

    def test_category(self):
        assert ClosestPairSimulation().metadata().category == "divide-and-conquer"

    def test_visualization_type(self):
        assert ClosestPairSimulation().metadata().visualization_type == "MATRIX"


class TestClosestPairCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_distance(self, seed: int):
        initial, _, final = run(6, seed=seed)
        xs = list(initial.table[0])
        ys = list(initial.table[1])
        expected = brute_force_closest(xs, ys)
        # Parse distance from description: "dist=D.DDD"
        actual = float(final.description.split("dist=")[1])
        assert abs(actual - expected) < 0.001, (
            f"seed={seed}: expected={expected:.3f}, got={actual:.3f}"
        )

    def test_table_has_2_rows(self):
        initial, _, _ = run(6)
        assert len(initial.table) == 2

    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_points_sorted_by_x(self):
        initial, _, _ = run(6)
        xs = initial.table[0]
        assert xs == tuple(sorted(xs))


class TestClosestPairFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_final_has_two_points(self):
        _, _, final = run(6)
        desc = final.description
        assert "Closest:" in desc
        assert "dist=" in desc
