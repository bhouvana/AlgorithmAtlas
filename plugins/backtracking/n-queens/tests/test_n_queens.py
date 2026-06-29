"""Tests for N-Queens plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "n_queens",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
NQueensSimulation = _mod.NQueensSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 42):
    sim = NQueensSimulation()
    params = SimulationParams(seed=seed, inputs={"board_size": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestNQueensMetadata:
    def test_slug(self):
        assert NQueensSimulation().metadata().slug == "n-queens"

    def test_category(self):
        assert NQueensSimulation().metadata().category == "backtracking"

    def test_visualization_type(self):
        assert NQueensSimulation().metadata().visualization_type == "GRID"


class TestNQueensInitialize:
    def test_grid_is_n_by_n(self):
        initial, _, _ = run(6)
        assert len(initial.grid) == 6
        assert all(len(row) == 6 for row in initial.grid)

    def test_initial_grid_empty(self):
        initial, _, _ = run(6)
        for row in initial.grid:
            for cell in row:
                assert cell == 0

    @pytest.mark.parametrize("n", [4, 5, 6, 7, 8])
    def test_board_sizes(self, n: int):
        initial, _, _ = run(n)
        assert len(initial.grid) == n


class TestNQueensCorrectness:
    @pytest.mark.parametrize("n", [4, 5, 6, 7, 8])
    def test_solution_has_n_queens(self, n: int):
        _, _, final = run(n)
        # Count placed queens (CELL_PATH = 6)
        queen_count = sum(1 for row in final.grid for cell in row if cell == 6)
        assert queen_count == n, f"Expected {n} queens, got {queen_count}"

    @pytest.mark.parametrize("n", [4, 5, 6])
    def test_solution_path_length(self, n: int):
        _, _, final = run(n)
        assert len(final.path) == n

    @pytest.mark.parametrize("n", [4, 5, 6])
    def test_solution_one_queen_per_row(self, n: int):
        _, _, final = run(n)
        rows = [r for r, _ in final.path]
        assert sorted(rows) == list(range(n))

    @pytest.mark.parametrize("n", [4, 5, 6])
    def test_solution_no_column_conflict(self, n: int):
        _, _, final = run(n)
        cols = [c for _, c in final.path]
        assert len(cols) == len(set(cols)), "Duplicate column"

    @pytest.mark.parametrize("n", [4, 5, 6])
    def test_solution_no_diagonal_conflict(self, n: int):
        _, _, final = run(n)
        queens = sorted(final.path)
        for i in range(n):
            for j in range(i + 1, n):
                r1, c1 = queens[i]
                r2, c2 = queens[j]
                assert abs(r1 - r2) != abs(c1 - c2), "Diagonal conflict"


class TestNQueensFrames:
    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_frames_have_grid(self):
        _, frames, _ = run(6)
        for f in frames[:5]:
            assert f.grid is not None

    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
