"""Tests for Floyd-Warshall all-pairs shortest paths plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "floyd_warshall_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
FloydWarshallSimulation = _mod.FloydWarshallSimulation
_INF = _mod._INF

from algorithm_atlas_sdk import SimulationParams


def run(node_count: int = 5, seed: int = 42):
    sim = FloydWarshallSimulation()
    params = SimulationParams(seed=seed, inputs={"node_count": node_count}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def naive_floyd(mat):
    n = len(mat)
    d = [list(row) for row in mat]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] < _INF and d[k][j] < _INF:
                    d[i][j] = min(d[i][j], d[i][k] + d[k][j])
    return d


class TestFloydWarshallMetadata:
    def test_slug(self):
        assert FloydWarshallSimulation().metadata().slug == "floyd-warshall"

    def test_category(self):
        assert FloydWarshallSimulation().metadata().category == "dynamic-programming"

    def test_visualization_type(self):
        assert FloydWarshallSimulation().metadata().visualization_type == "MATRIX"


class TestFloydWarshallCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_matches_naive(self, seed: int):
        initial, _, final = run(5, seed=seed)
        expected = naive_floyd(initial.table)
        for i, row in enumerate(final.table):
            for j, val in enumerate(row):
                assert val == expected[i][j], f"seed={seed} [{i}][{j}]: got {val}, expected {expected[i][j]}"

    def test_diagonal_is_zero(self):
        _, _, final = run(5)
        n = len(final.table)
        for i in range(n):
            assert final.table[i][i] == 0

    def test_triangle_inequality(self):
        _, _, final = run(5)
        n = len(final.table)
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if final.table[i][k] < _INF and final.table[k][j] < _INF:
                        assert final.table[i][j] <= final.table[i][k] + final.table[k][j]

    def test_non_negative_distances(self):
        _, _, final = run(5)
        for row in final.table:
            for v in row:
                assert v >= 0


class TestFloydWarshallFrames:
    def test_has_frames(self):
        _, frames, _ = run(5)
        assert len(frames) > 0

    def test_all_cells_computed_at_end(self):
        initial, _, final = run(5)
        n = len(initial.table)
        assert len(final.computed_cells) == n * n

    def test_no_current_cell_at_end(self):
        _, _, final = run(5)
        assert final.current_cell is None

    def test_serializable(self):
        import json
        initial, frames, final = run(5)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = FloydWarshallSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 1}, config={})
        s = sim.initialize(p)
        assert len(s.table) == 4

    def test_clamp_max(self):
        sim = FloydWarshallSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 99}, config={})
        s = sim.initialize(p)
        assert len(s.table) == 6
