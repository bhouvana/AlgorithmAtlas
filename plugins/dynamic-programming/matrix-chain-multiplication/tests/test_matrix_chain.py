"""Tests for Matrix Chain Multiplication plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "matrix_chain",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MatrixChainSimulation = _mod.MatrixChainSimulation

from algorithm_atlas_sdk import SimulationParams

_INF = 999999


def run(n: int = 4, seed: int = 42):
    sim = MatrixChainSimulation()
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


def brute_force_mcm(dims):
    n = len(dims) - 1
    dp = [[0 if i == j else _INF for j in range(n)] for i in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if cost < dp[i][j]:
                    dp[i][j] = cost
    return dp[0][n - 1]


class TestMatrixChainMetadata:
    def test_slug(self):
        assert MatrixChainSimulation().metadata().slug == "matrix-chain-multiplication"

    def test_category(self):
        assert MatrixChainSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert MatrixChainSimulation().metadata().visualization_type == "MATRIX"


class TestMatrixChainCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_optimal_cost_correct(self, seed: int):
        initial, _, final = run(4, seed=seed)
        dims_str = initial.description.split("dims=")[1]
        dims = [int(x) for x in dims_str.split(",")]
        expected = brute_force_mcm(dims)
        # Extract cost from final description
        cost = int(final.description.split("Optimal cost = ")[1].split(" ")[0])
        assert cost == expected

    def test_table_shape(self):
        initial, _, final = run(4)
        n = len(initial.table)
        assert len(final.table) == n
        assert all(len(row) == n for row in final.table)

    def test_diagonal_is_zero(self):
        _, _, final = run(4)
        for i in range(len(final.table)):
            assert final.table[i][i] == 0

    def test_has_frames(self):
        _, frames, _ = run(4)
        assert len(frames) > 0

    def test_all_upper_triangle_computed(self):
        initial, _, final = run(4)
        n = len(initial.table)
        for i in range(n):
            for j in range(i + 1, n):
                assert (i, j) in final.computed_cells


class TestMatrixChainFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(4)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
