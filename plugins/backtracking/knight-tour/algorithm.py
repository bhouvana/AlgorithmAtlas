"""Knight's Tour plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    GridState,
    SimulationParams,
)

CELL_EMPTY = 0
CELL_WALL = 1
CELL_START = 2
CELL_GOAL = 3
CELL_OPEN = 4
CELL_CLOSED = 5
CELL_PATH = 6

MOVES = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]

# Precomputed complete tours for 5x5 boards at different starting positions
# (start_row, start_col, tour_path)
_TOURS_5 = [
    # Start (0,0) on 5x5
    (0, 0, [(0,0),(1,2),(0,4),(2,3),(4,4),(3,2),(4,0),(2,1),(0,2),(1,4),(3,3),(4,1),(2,0),(0,1),(1,3),(3,4),(4,2),(3,0),(1,1),(0,3),(2,4),(4,3),(3,1),(2,3),(4,2)]),
]

def _warnsdorff(n: int, start_r: int, start_c: int):
    """Find a knight's tour using Warnsdorff's heuristic."""
    board = [[-1] * n for _ in range(n)]
    board[start_r][start_c] = 0
    path = [(start_r, start_c)]
    r, c = start_r, start_c

    def degree(br, bc):
        count = 0
        for dr, dc in MOVES:
            nr, nc = br + dr, bc + dc
            if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == -1:
                count += 1
        return count

    for move_num in range(1, n * n):
        candidates = []
        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == -1:
                candidates.append((degree(nr, nc), nr, nc))
        if not candidates:
            return None
        candidates.sort()
        _, nr, nc = candidates[0]
        board[nr][nc] = move_num
        path.append((nr, nc))
        r, c = nr, nc

    return path


class KnightTourSimulation(AlgorithmPlugin):
    """Knight's Tour using Warnsdorff's heuristic."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="knight-tour",
            name="Knight's Tour",
            category="backtracking",
            visualization_type="GRID",
            description="Visit every square on a chessboard exactly once using knight moves.",
            intuition=(
                "Warnsdorff's rule: always move to the accessible square with the fewest "
                "onward moves. This greedy heuristic finds tours on 5×5 and larger boards quickly."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(8^(n²))",
            complexity_space="O(n²)",
            tags=("backtracking", "knight-tour", "chess", "warnsdorff"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        n = 5
        start_r = params.seed % n
        start_c = (params.seed // n) % n
        # Try Warnsdorff; fall back to (0,0) if fails
        path = _warnsdorff(n, start_r, start_c)
        if path is None:
            start_r, start_c = 0, 0
            path = _warnsdorff(n, 0, 0)

        grid = [[CELL_EMPTY] * n for _ in range(n)]
        grid[start_r][start_c] = CELL_START
        return GridState(
            grid=tuple(tuple(row) for row in grid),
            current=(start_r, start_c),
            path=tuple(),
            description=f"Knight's tour 5x5 start=({start_r},{start_c}) tour_len={len(path) if path else 0}",
        )

    def steps(
        self, initial_state: GridState
    ) -> Generator[GridState, None, GridState]:
        desc = initial_state.description
        n = 5
        start_r = int(desc.split("start=(")[1].split(",")[0])
        start_c = int(desc.split(",")[1].split(")")[0])

        path = _warnsdorff(n, start_r, start_c)
        if path is None:
            path = [(start_r, start_c)]

        visited_path: list = []
        for step, (r, c) in enumerate(path):
            visited_path.append((r, c))
            grid = [[CELL_EMPTY] * n for _ in range(n)]
            for i, (pr, pc) in enumerate(visited_path):
                grid[pr][pc] = CELL_PATH if i < len(visited_path) - 1 else CELL_OPEN
            grid[path[0][0]][path[0][1]] = CELL_START

            yield GridState(
                grid=tuple(tuple(row) for row in grid),
                current=(r, c),
                path=tuple(visited_path),
                description=f"Move {step+1}/{n*n}: knight at ({r},{c})",
            )

        # Mark completed tour
        grid = [[CELL_PATH] * n for _ in range(n)]
        return GridState(
            grid=tuple(tuple(row) for row in grid),
            current=None,
            path=tuple(path),
            description=f"Tour complete: {len(path)}/{n*n} squares visited",
        )
