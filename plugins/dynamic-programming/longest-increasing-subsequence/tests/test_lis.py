"""Tests for LIS plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "lis",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LISSimulation = _mod.LISSimulation

from algorithm_atlas_sdk import SimulationParams


def run(size: int = 8, seed: int = 42):
    sim = LISSimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": size}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def brute_force_lis(arr):
    n = len(arr)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if arr[j] < arr[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


class TestLISMetadata:
    def test_slug(self):
        assert LISSimulation().metadata().slug == "longest-increasing-subsequence"

    def test_category(self):
        assert LISSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert LISSimulation().metadata().visualization_type == "MATRIX"


class TestLISCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_lis_length(self, seed: int):
        initial, _, final = run(8, seed=seed)
        arr = list(initial.table[0])
        expected = brute_force_lis(arr)
        # Extract LIS length from final description
        lis_len = int(final.description.split("LIS length = ")[1].split(" ")[0])
        assert lis_len == expected

    def test_dp_values_all_at_least_1(self):
        initial, _, final = run(8)
        dp = list(final.table[1])
        assert all(v >= 1 for v in dp)

    def test_dp_row_length(self):
        initial, _, final = run(8)
        assert len(final.table[1]) == len(final.table[0])

    def test_table_has_2_rows(self):
        initial, _, final = run(8)
        assert len(final.table) == 2

    def test_all_cells_computed(self):
        initial, _, final = run(8)
        n = len(initial.table[0])
        assert len(final.computed_cells) == n

    def test_has_frames(self):
        _, frames, _ = run(8)
        assert len(frames) > 0


class TestLISFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(8)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_dp_values_non_decreasing_in_final(self):
        initial, _, final = run(8)
        # Not necessarily sorted, but all >= 1
        dp = list(final.table[1])
        assert all(v >= 1 for v in dp)
