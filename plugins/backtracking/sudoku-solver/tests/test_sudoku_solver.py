"""Tests for Sudoku Solver plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "sudoku_solver",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SudokuSolverSimulation = _mod.SudokuSolverSimulation

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = SudokuSolverSimulation()
    params = SimulationParams(seed=seed, inputs={}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def _is_valid_board(board) -> bool:
    """Check if completed board is a valid sudoku solution."""
    for r in range(9):
        row = [board[r][c] for c in range(9)]
        if sorted(row) != list(range(1, 10)):
            return False
    for c in range(9):
        col = [board[r][c] for r in range(9)]
        if sorted(col) != list(range(1, 10)):
            return False
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = [board[br + dr][bc + dc] for dr in range(3) for dc in range(3)]
            if sorted(box) != list(range(1, 10)):
                return False
    return True


class TestSudokuMetadata:
    def test_slug(self):
        assert SudokuSolverSimulation().metadata().slug == "sudoku-solver"

    def test_category(self):
        assert SudokuSolverSimulation().metadata().category == "backtracking"

    def test_visualization_type(self):
        assert SudokuSolverSimulation().metadata().visualization_type == "MATRIX"


class TestSudokuCorrectness:
    @pytest.mark.parametrize("seed", range(4))
    def test_solved(self, seed: int):
        _, _, final = run(seed=seed)
        assert "Solved" in final.description

    @pytest.mark.parametrize("seed", range(4))
    def test_valid_solution(self, seed: int):
        _, _, final = run(seed=seed)
        board = final.table
        assert _is_valid_board(board)

    @pytest.mark.parametrize("seed", range(4))
    def test_preserves_given_clues(self, seed: int):
        initial, _, final = run(seed=seed)
        for r in range(9):
            for c in range(9):
                if initial.table[r][c] != 0:
                    assert final.table[r][c] == initial.table[r][c]

    def test_table_is_9x9(self):
        initial, _, _ = run()
        assert len(initial.table) == 9
        for row in initial.table:
            assert len(row) == 9


class TestSudokuFrames:
    def test_has_frames(self):
        _, frames, _ = run()
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run()
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_computed_cells_only_empty(self):
        initial, _, final = run()
        prefilled = {(r, c) for r in range(9) for c in range(9) if initial.table[r][c] != 0}
        for cell in final.computed_cells:
            assert cell not in prefilled
