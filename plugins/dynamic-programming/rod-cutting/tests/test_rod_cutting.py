"""Tests for Rod Cutting plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "rod_cutting",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
RodCuttingSimulation = _mod.RodCuttingSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 7, seed: int = 42):
    sim = RodCuttingSimulation()
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


def brute_force_rod(prices, n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        for j in range(1, i + 1):
            dp[i] = max(dp[i], prices[j - 1] + dp[i - j])
    return dp[n]


class TestRodCuttingMetadata:
    def test_slug(self):
        assert RodCuttingSimulation().metadata().slug == "rod-cutting"

    def test_category(self):
        assert RodCuttingSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert RodCuttingSimulation().metadata().visualization_type == "MATRIX"


class TestRodCuttingCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_optimal_revenue_correct(self, seed: int):
        initial, _, final = run(7, seed=seed)
        prices_str = initial.description.split("prices=")[1]
        prices = [int(x) for x in prices_str.split(",")]
        n = len(prices)
        expected = brute_force_rod(prices, n)
        actual = int(final.description.split("= ")[-1])
        assert actual == expected

    def test_dp_row_starts_with_0(self):
        initial, _, _ = run(7)
        dp = list(initial.table[1])
        assert dp[0] == 0

    def test_dp_non_negative(self):
        _, _, final = run(7)
        dp = list(final.table[1])
        assert all(v >= 0 for v in dp)

    def test_dp_non_decreasing(self):
        _, _, final = run(7)
        dp = list(final.table[1])
        for i in range(1, len(dp)):
            assert dp[i] >= dp[i - 1], "dp values should be non-decreasing"

    def test_table_has_2_rows(self):
        _, _, final = run(7)
        assert len(final.table) == 2

    def test_has_frames(self):
        _, frames, _ = run(7)
        assert len(frames) > 0


class TestRodCuttingFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_all_cells_computed_in_final(self):
        initial, _, final = run(7)
        n = len(initial.table[1])
        assert len(final.computed_cells) == n
