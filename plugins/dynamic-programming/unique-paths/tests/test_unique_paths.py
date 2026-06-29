"""Tests for Unique Paths plugin."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "unique_paths",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
UniquePathsSimulation = _mod.UniquePathsSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 4, seed: int = 0):
    sim = UniquePathsSimulation()
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


def expected_unique_paths(n: int) -> int:
    # C(2(n-1), n-1)
    return math.comb(2 * (n - 1), n - 1)


class TestUniquePathsMetadata:
    def test_slug(self):
        assert UniquePathsSimulation().metadata().slug == "unique-paths"

    def test_category(self):
        assert UniquePathsSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert UniquePathsSimulation().metadata().visualization_type == "MATRIX"


class TestUniquePathsCorrectness:
    @pytest.mark.parametrize("n", [3, 4, 5, 6])
    def test_correct_count(self, n: int):
        _, _, final = run(n)
        actual = int(final.description.split("= ")[1])
        expected = expected_unique_paths(n)
        assert actual == expected, f"n={n}: expected {expected}, got {actual}"

    def test_base_row_all_ones(self):
        initial, _, _ = run(4)
        assert all(initial.table[0][j] == 1 for j in range(4))

    def test_base_col_all_ones(self):
        initial, _, _ = run(4)
        assert all(initial.table[i][0] == 1 for i in range(4))

    def test_frame_count(self):
        n = 4
        _, frames, _ = run(n)
        # (n-1)*(n-1) interior cells
        assert len(frames) == (n - 1) ** 2


class TestUniquePathsFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(4)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_values_increase_monotonically(self):
        _, _, final = run(4)
        # dp[n-1][n-1] >= dp[n-2][n-1] and dp[n-1][n-2]
        n = len(final.table)
        assert final.table[n-1][n-1] >= final.table[n-2][n-1]
        assert final.table[n-1][n-1] >= final.table[n-1][n-2]
