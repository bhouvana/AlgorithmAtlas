"""Sudoku Solver backtracking plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# A set of known valid Sudoku puzzles (17-clue minimal puzzles)
_PUZZLES = [
    # Each row is a 9-element list, 0 = empty
    [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
    [
        [0, 0, 0, 2, 6, 0, 7, 0, 1],
        [6, 8, 0, 0, 7, 0, 0, 9, 0],
        [1, 9, 0, 0, 0, 4, 5, 0, 0],
        [8, 2, 0, 1, 0, 0, 0, 4, 0],
        [0, 0, 4, 6, 0, 2, 9, 0, 0],
        [0, 5, 0, 0, 0, 3, 0, 2, 8],
        [0, 0, 9, 3, 0, 0, 0, 7, 4],
        [0, 4, 0, 0, 5, 0, 0, 3, 6],
        [7, 0, 3, 0, 1, 8, 0, 0, 0],
    ],
    [
        [0, 0, 0, 0, 0, 0, 2, 0, 0],
        [0, 8, 0, 0, 0, 7, 0, 9, 0],
        [6, 0, 2, 0, 0, 0, 5, 0, 0],
        [0, 7, 0, 0, 6, 0, 0, 0, 0],
        [0, 0, 0, 9, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 2, 0, 0, 4, 0],
        [0, 0, 5, 0, 0, 0, 6, 0, 3],
        [0, 9, 0, 4, 0, 0, 0, 7, 0],
        [0, 0, 6, 0, 0, 0, 0, 0, 0],
    ],
    [
        [1, 0, 0, 4, 8, 9, 0, 0, 6],
        [7, 3, 0, 0, 0, 0, 0, 4, 0],
        [0, 0, 0, 0, 0, 1, 2, 9, 5],
        [0, 0, 7, 1, 2, 0, 6, 0, 0],
        [5, 0, 0, 7, 0, 3, 0, 0, 8],
        [0, 0, 6, 0, 9, 5, 7, 0, 0],
        [9, 1, 4, 6, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0, 0, 3, 7],
        [8, 0, 0, 5, 1, 2, 0, 0, 4],
    ],
]


def _is_valid(board: List[List[int]], row: int, col: int, num: int) -> bool:
    if num in board[row]:
        return False
    if num in (board[r][col] for r in range(9)):
        return False
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num:
                return False
    return True


def _find_empty(board: List[List[int]]) -> Optional[Tuple[int, int]]:
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def _board_tuple(board: List[List[int]]) -> Tuple[Tuple[int, ...], ...]:
    return tuple(tuple(row) for row in board)


class SudokuSolverSimulation(AlgorithmPlugin):
    """
    Sudoku Solver — iterative backtracking with explicit stack.

    DPState encoding:
      table:          9×9 board (0 = empty)
      current_cell:   (row, col) being tried now
      computed_cells: cells filled by the solver (not pre-filled)
      description:    step label
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="sudoku-solver",
            name="Sudoku Solver",
            category="backtracking",
            visualization_type="MATRIX",
            description=(
                "Solve a 9×9 Sudoku using backtracking — place digits 1–9 "
                "in empty cells, checking row/column/box constraints."
            ),
            intuition=(
                "Find the first empty cell. Try digits 1–9 one by one. "
                "If a digit is valid (no clash in row, column, or 3×3 box), place it "
                "and recurse. If no digit works, erase and backtrack."
            ),
            complexity_time_best="O(9^m) where m = empty cells",
            complexity_time_average="O(9^m)",
            complexity_time_worst="O(9^m)",
            complexity_space="O(m)",
            tags=("backtracking", "sudoku", "constraint-satisfaction", "puzzle"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        puzzle = [list(row) for row in _PUZZLES[params.seed % len(_PUZZLES)]]
        prefilled: frozenset = frozenset(
            (r, c) for r in range(9) for c in range(9) if puzzle[r][c] != 0
        )
        empty_count = 81 - len(prefilled)
        return DPState(
            table=_board_tuple(puzzle),
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Sudoku puzzle: {empty_count} empty cells to fill.",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        board = [list(row) for row in initial_state.table]
        prefilled: frozenset = frozenset(
            (r, c) for r in range(9) for c in range(9) if board[r][c] != 0
        )
        solved: set = set()

        # Iterative backtracking: stack of (row, col, next_digit_to_try)
        # Find initial empty cell
        first = _find_empty(board)
        if first is None:
            return DPState(
                table=_board_tuple(board),
                current_cell=None,
                computed_cells=frozenset(),
                description="Already solved.",
            )

        stack: list = [(*first, 1)]  # (row, col, digit)
        # Limit frames yielded to keep it manageable
        step_count = 0
        max_yields = 200

        while stack:
            r, c, d = stack[-1]

            if d > 9:
                # Backtrack
                stack.pop()
                if board[r][c] != 0:
                    board[r][c] = 0
                    solved.discard((r, c))
                continue

            stack[-1] = (r, c, d + 1)

            if _is_valid(board, r, c, d):
                board[r][c] = d
                solved.add((r, c))

                if step_count < max_yields:
                    step_count += 1
                    yield DPState(
                        table=_board_tuple(board),
                        current_cell=(r, c),
                        computed_cells=frozenset(solved),
                        description=f"Place {d} at ({r},{c})",
                    )

                nxt = _find_empty(board)
                if nxt is None:
                    # Solved
                    break
                stack.append((*nxt, 1))

        # Verify solved
        empty = _find_empty(board)
        if empty is None:
            filled = sum(1 for r in range(9) for c in range(9) if (r, c) not in prefilled)
            return DPState(
                table=_board_tuple(board),
                current_cell=None,
                computed_cells=frozenset(solved),
                description=f"Solved! Filled {filled} cells.",
            )
        else:
            return DPState(
                table=_board_tuple(board),
                current_cell=None,
                computed_cells=frozenset(solved),
                description="No solution found.",
            )
