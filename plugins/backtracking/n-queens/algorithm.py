"""N-Queens backtracking plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    GridState,
    SimulationParams,
)
from algorithm_atlas_sdk import (
    CELL_EMPTY,
    CELL_WALL,    # reused as queen
    CELL_GOAL,    # reused as "safe to try"
    CELL_CLOSED,  # reused as "attacking/rejected"
    CELL_PATH,    # reused as "placed queen"
)

# Cell semantics for N-Queens:
_QUEEN = CELL_WALL      # 1 — a placed queen
_TRYING = CELL_GOAL     # 3 — cell being attempted
_ATTACK = CELL_CLOSED   # 5 — cell under attack / rejected
_PLACED = CELL_PATH     # 6 — confirmed queen position


class NQueensSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="n-queens",
            name="N-Queens",
            category="backtracking",
            visualization_type="GRID",
            description="Place N queens on an N×N chessboard so no two queens threaten each other.",
            intuition="Try placing a queen in each row one at a time. At each step, check if the placement is safe. If not, backtrack and try the next column.",
            complexity_time_best="O(N!)",
            complexity_time_average="O(N!)",
            complexity_time_worst="O(N!)",
            complexity_space="O(N)",
            tags=("backtracking", "constraint-satisfaction", "n-queens", "chess"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        n: int = max(4, min(params.inputs.get("board_size", 6), 8))
        grid = tuple(tuple(CELL_EMPTY for _ in range(n)) for _ in range(n))
        return GridState(
            grid=grid,
            current=None,
            path=(),
            description=f"N-Queens on {n}×{n} board — starting backtracking",
        )

    def steps(
        self, initial_state: GridState
    ) -> Generator[GridState, None, GridState]:
        grid_list = initial_state.grid
        n = len(grid_list)
        board: List[int] = [-1] * n  # board[row] = col of queen in that row

        def make_grid(
            current_row: Optional[int] = None,
            current_col: Optional[int] = None,
            highlight_attack: bool = False,
        ) -> Tuple[Tuple[int, ...], ...]:
            g: List[List[int]] = [[CELL_EMPTY] * n for _ in range(n)]
            for r in range(n):
                if board[r] != -1:
                    g[r][board[r]] = _PLACED
            if current_row is not None and current_col is not None:
                if highlight_attack:
                    g[current_row][current_col] = _ATTACK
                else:
                    g[current_row][current_col] = _TRYING
            return tuple(tuple(row) for row in g)

        def is_safe(row: int, col: int) -> bool:
            for r in range(row):
                c = board[r]
                if c == col or abs(c - col) == abs(r - row):
                    return False
            return True

        def solve(row: int) -> Generator:
            if row == n:
                return  # solution found — generator exhausted normally
            for col in range(n):
                yield GridState(
                    grid=make_grid(row, col, False),
                    current=(row, col),
                    path=tuple((r, board[r]) for r in range(row) if board[r] != -1),
                    description=f"Row {row}: trying col {col}",
                )
                if is_safe(row, col):
                    board[row] = col
                    yield from solve(row + 1)
                    if board[row] == col and _placed_through(row):
                        return  # found first solution
                    board[row] = -1
                else:
                    yield GridState(
                        grid=make_grid(row, col, True),
                        current=(row, col),
                        path=tuple((r, board[r]) for r in range(row) if board[r] != -1),
                        description=f"Row {row}, col {col}: conflict — backtrack",
                    )

        def _placed_through(stop_row: int) -> bool:
            return all(board[r] != -1 for r in range(stop_row + 1))

        # Iterative wrapper that stops after finding the first solution
        found = [False]

        def solve_iter(row: int):
            if found[0]:
                return
            if row == n:
                found[0] = True
                return
            for col in range(n):
                if found[0]:
                    return
                g = make_grid(row, col, False)
                yield GridState(
                    grid=g,
                    current=(row, col),
                    path=tuple((r, board[r]) for r in range(row) if board[r] != -1),
                    description=f"Row {row}: trying col {col}",
                )
                if is_safe(row, col):
                    board[row] = col
                    yield from solve_iter(row + 1)
                    if not found[0]:
                        board[row] = -1
                        yield GridState(
                            grid=make_grid(row, None),
                            current=None,
                            path=tuple((r, board[r]) for r in range(row) if board[r] != -1),
                            description=f"Backtrack to row {row}, try next col",
                        )
                else:
                    yield GridState(
                        grid=make_grid(row, col, True),
                        current=(row, col),
                        path=tuple((r, board[r]) for r in range(row) if board[r] != -1),
                        description=f"Row {row}, col {col}: conflict — skip",
                    )

        yield from solve_iter(0)

        if found[0]:
            final_path = tuple((r, board[r]) for r in range(n))
            final_grid = make_grid()
            return GridState(
                grid=final_grid,
                current=None,
                path=final_path,
                description=f"Solution found! Queens at cols: {[board[r] for r in range(n)]}",
            )

        return GridState(
            grid=initial_state.grid,
            current=None,
            path=(),
            description="No solution found",
        )
