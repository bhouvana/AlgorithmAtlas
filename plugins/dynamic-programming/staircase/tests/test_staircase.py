"""Tests for Staircase DP plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "staircase",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
StaircaseSimulation = _mod.StaircaseSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 10, seed: int = 42):
    sim = StaircaseSimulation()
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


def brute_force_staircase(n: int) -> int:
    """Recursive reference with memoization."""
    memo = {}
    def f(k):
        if k <= 1:
            return 1
        if k in memo:
            return memo[k]
        memo[k] = f(k - 1) + f(k - 2)
        return memo[k]
    return f(n)


class TestStaircaseMetadata:
    def test_slug(self):
        assert StaircaseSimulation().metadata().slug == "staircase"

    def test_category(self):
        assert StaircaseSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert StaircaseSimulation().metadata().visualization_type == "MATRIX"


class TestStaircaseCorrectness:
    @pytest.mark.parametrize("n", [4, 5, 6, 7, 8, 9, 10, 12, 15])
    def test_correct_answer(self, n: int):
        _, _, final = run(n)
        result = int(final.description.split("ways")[0].split(": ")[1])
        assert result == brute_force_staircase(n)

    def test_table_has_2_rows(self):
        initial, _, _ = run(10)
        assert len(initial.table) == 2

    def test_row0_is_indices(self):
        initial, _, _ = run(10)
        n = 10
        assert list(initial.table[0]) == list(range(n + 1))

    def test_base_cases(self):
        _, _, final = run(10)
        dp = list(final.table[1])
        assert dp[0] == 1
        assert dp[1] == 1

    def test_dp_monotonically_increases(self):
        _, _, final = run(10)
        dp = list(final.table[1])
        for i in range(1, len(dp)):
            assert dp[i] >= dp[i - 1]

    def test_all_cells_computed(self):
        initial, _, final = run(10)
        n = len(initial.table[0]) - 1
        assert len(final.computed_cells) == n + 1


class TestStaircaseFrames:
    def test_has_frames(self):
        _, frames, _ = run(10)
        assert len(frames) > 0

    def test_frame_count_equals_n(self):
        n = 10
        _, frames, _ = run(n)
        assert len(frames) == n  # base case frame + n-1 recurrence frames

    def test_serializable(self):
        import json
        initial, frames, final = run(10)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_descriptions_have_dp_formula(self):
        _, frames, _ = run(10)
        recurrence_frames = [f for f in frames if "dp[" in f.description and "+" in f.description]
        assert len(recurrence_frames) >= 1
