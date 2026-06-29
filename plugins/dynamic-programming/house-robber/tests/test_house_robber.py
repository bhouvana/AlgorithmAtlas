"""Tests for House Robber plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "house_robber",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
HouseRobberSimulation = _mod.HouseRobberSimulation

from algorithm_atlas_sdk import SimulationParams


def brute(nums):
    n = len(nums)
    if n == 0: return 0
    if n == 1: return nums[0]
    dp = [0] * n
    dp[0] = nums[0]
    dp[1] = max(nums[0], nums[1])
    for i in range(2, n):
        dp[i] = max(dp[i-1], dp[i-2] + nums[i])
    return dp[-1]


def run(n: int = 8, seed: int = 0):
    sim = HouseRobberSimulation()
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


class TestHouseRobberMetadata:
    def test_slug(self):
        assert HouseRobberSimulation().metadata().slug == "house-robber"

    def test_category(self):
        assert HouseRobberSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert HouseRobberSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestHouseRobberCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_max(self, seed: int):
        initial, _, final = run(8, seed)
        expected = brute(list(initial.array))
        result = int(final.description.split("= ")[1])
        assert result == expected

    def test_has_n_frames(self):
        initial, frames, _ = run(8)
        assert len(frames) == len(initial.array)


class TestHouseRobberFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
