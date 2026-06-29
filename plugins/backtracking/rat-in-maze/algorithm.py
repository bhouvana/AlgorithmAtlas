"""Rat in a Maze backtracking plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from collections import deque
from typing import Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    CELL_CLOSED,
    CELL_EMPTY,
    CELL_GOAL,
    CELL_OPEN,
    CELL_PATH,
    CELL_START,
    CELL_WALL,
    GridState,
    SimulationParams,
)

_DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up


def _make_maze(rng: random.Random, n: int) -> List[List[int]]:
    """Generate a random solvable maze by placing walls then guaranteeing a path."""
    start, goal = (0, 0), (n - 1, n - 1)
    grid = [[CELL_EMPTY] * n for _ in range(n)]

    # Place random walls (~25% density), never on start or goal
    for r in range(n):
        for c in range(n):
            if (r, c) not in (start, goal) and rng.random() < 0.25:
                grid[r][c] = CELL_WALL

    # BFS to check and fix connectivity
    def bfs_path() -> Optional[List[Tuple[int, int]]]:
        queue: deque = deque([(0, 0)])
        parent: dict = {(0, 0): None}
        while queue:
            r, c = queue.popleft()
            if (r, c) == goal:
                path: List[Tuple[int, int]] = []
                node: Optional[Tuple[int, int]] = goal
                while node is not None:
                    path.append(node)
                    node = parent[node]
                return path[::-1]
            for dr, dc in _DIRS:
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < n
                    and 0 <= nc < n
                    and (nr, nc) not in parent
                    and grid[nr][nc] != CELL_WALL
                ):
                    parent[(nr, nc)] = (r, c)
                    queue.append((nr, nc))
        return None

    if bfs_path() is None:
        # Carve a guaranteed path: right along row 0, then down to goal
        for c in range(1, n):
            grid[0][c] = CELL_EMPTY
        for r in range(1, n):
            grid[r][n - 1] = CELL_EMPTY

    grid[0][0] = CELL_START
    grid[n - 1][n - 1] = CELL_GOAL
    return grid


def _grid_tuple(grid: List[List[int]]) -> Tuple[Tuple[int, ...], ...]:
    return tuple(tuple(row) for row in grid)


class RatInMazeSimulation(AlgorithmPlugin):
    """
    Rat in a Maze — backtracking on a grid.

    GridState encoding:
      CELL_START=2  : starting cell (0,0)
      CELL_GOAL=3   : destination (n-1,n-1)
      CELL_OPEN=4   : currently on the active path
      CELL_CLOSED=5 : backtracked (dead end)
      CELL_WALL=1   : impassable
      CELL_PATH=6   : final solution path
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="rat-in-maze",
            name="Rat in a Maze",
            category="backtracking",
            visualization_type="GRID",
            description=(
                "Find a path from top-left to bottom-right of a maze "
                "using backtracking — try each direction and undo dead ends."
            ),
            intuition=(
                "From the current cell try right, down, left, up. "
                "Mark the cell as part of the current path. "
                "If all directions fail, backtrack (unmark) and try the next option."
            ),
            complexity_time_best="O(2^(n²))",
            complexity_time_average="O(2^(n²))",
            complexity_time_worst="O(2^(n²))",
            complexity_space="O(n²)",
            tags=("backtracking", "maze", "pathfinding", "grid"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 6), 8))
        grid = _make_maze(rng, n)
        return GridState(
            grid=_grid_tuple(grid),
            current=(0, 0),
            path=(),
            description=f"Start at (0,0). Find path to ({n-1},{n-1}).",
        )

    def steps(
        self, initial_state: GridState
    ) -> Generator[GridState, None, GridState]:
        grid = [list(row) for row in initial_state.grid]
        n = len(grid)
        goal = (n - 1, n - 1)

        # Iterative DFS with explicit backtracking
        # Stack entries: (row, col, next_direction_index)
        stack: list = [(0, 0, 0)]
        on_path: list = [(0, 0)]
        path_set: set = {(0, 0)}

        # Start cell is already CELL_START; mark as CELL_OPEN for traversal
        grid[0][0] = CELL_OPEN

        def snap(desc: str) -> GridState:
            return GridState(
                grid=_grid_tuple(grid),
                current=on_path[-1] if on_path else None,
                path=tuple(on_path),
                description=desc,
            )

        found = False
        while stack:
            r, c, d = stack[-1]

            if (r, c) == goal:
                found = True
                break

            if d < 4:
                dr, dc = _DIRS[d]
                stack[-1] = (r, c, d + 1)
                nr, nc = r + dr, c + dc

                if (
                    0 <= nr < n
                    and 0 <= nc < n
                    and grid[nr][nc] not in (CELL_WALL, CELL_OPEN, CELL_CLOSED)
                    and (nr, nc) not in path_set
                ):
                    grid[nr][nc] = CELL_OPEN
                    on_path.append((nr, nc))
                    path_set.add((nr, nc))
                    stack.append((nr, nc, 0))
                    yield snap(f"Move to ({nr},{nc})")
            else:
                # All 4 directions failed — backtrack
                stack.pop()
                if on_path:
                    br, bc = on_path.pop()
                    path_set.discard((br, bc))
                    if (br, bc) not in ((0, 0), goal):
                        grid[br][bc] = CELL_CLOSED
                if on_path:
                    yield snap(f"Backtrack to ({on_path[-1][0]},{on_path[-1][1]})")

        if found:
            # Mark final path (exclude start and goal which keep their codes)
            for pr, pc in on_path:
                if grid[pr][pc] not in (CELL_START, CELL_GOAL):
                    grid[pr][pc] = CELL_PATH
            # Restore start and goal markers
            grid[0][0] = CELL_START
            grid[goal[0]][goal[1]] = CELL_GOAL
            return GridState(
                grid=_grid_tuple(grid),
                current=goal,
                path=tuple(on_path),
                description=f"Path found! Length = {len(on_path)} cells.",
            )
        else:
            return GridState(
                grid=_grid_tuple(grid),
                current=None,
                path=(),
                description="No path exists.",
            )
