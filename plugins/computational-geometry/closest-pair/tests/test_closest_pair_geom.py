"""Tests for Closest Pair of Points plugin."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "closest_pair", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ClosestPairSimulation = _mod.ClosestPairSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n=8, seed=0):
    sim = ClosestPairSimulation()
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


class TestClosestPairMetadata:
    def test_slug(self):
        assert ClosestPairSimulation().metadata().slug == "closest-pair"

    def test_category(self):
        assert ClosestPairSimulation().metadata().category == "computational-geometry"


class TestClosestPairCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_result_is_actual_closest(self, seed: int):
        """Brute-force verify the answer."""
        initial, _, final = run(8, seed)
        all_pts = list(initial.path)
        n = len(all_pts)
        best_d = math.inf
        for i in range(n):
            for j in range(i + 1, n):
                d = math.sqrt((all_pts[i][0]-all_pts[j][0])**2 + (all_pts[i][1]-all_pts[j][1])**2)
                if d < best_d:
                    best_d = d
        p1, p2 = final.path[0], final.path[1]
        reported_d = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
        assert abs(reported_d - best_d) < 1e-6

    def test_has_frames(self):
        _, frames, _ = run(8)
        n = 8
        # n*(n-1)/2 comparisons
        assert len(frames) == n * (n - 1) // 2

    def test_final_has_two_points(self):
        _, _, final = run(8)
        assert len(final.path) == 2


class TestClosestPairFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
