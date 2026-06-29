"""A* pathfinding plugin for Algorithm Atlas."""
from __future__ import annotations

import heapq
import random
from typing import Dict, Generator, List, Optional, Tuple

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


def _manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _build_grid(
    rng: random.Random, rows: int, cols: int, wall_pct: int
) -> Tuple[List[List[int]], Tuple[int, int], Tuple[int, int]]:
    """Generate a random passable grid with start at top-left and goal at bottom-right."""
    grid = [[CELL_EMPTY] * cols for _ in range(rows)]
    start = (0, 0)
    goal = (rows - 1, cols - 1)

    # Place walls randomly, never on start/goal
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in (start, goal):
                if rng.randint(1, 100) <= wall_pct:
                    grid[r][c] = CELL_WALL

    # Ensure start/goal are clear
    grid[start[0]][start[1]] = CELL_START
    grid[goal[0]][goal[1]] = CELL_GOAL
    return grid, start, goal


def _neighbors(r: int, c: int, rows: int, cols: int):
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc


class AStarSimulation(AlgorithmPlugin):
    """
    A* pathfinding — O(E log V) with Manhattan distance heuristic.

    GridState.grid cell codes:
      CELL_EMPTY=0, CELL_WALL=1, CELL_START=2, CELL_GOAL=3,
      CELL_OPEN=4 (frontier), CELL_CLOSED=5 (visited), CELL_PATH=6.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="a-star",
            name="A* Pathfinding",
            category="graph",
            visualization_type="GRID",
            description="Shortest-path algorithm on a grid using f = g + h (cost + Manhattan distance heuristic).",
            intuition="Explore cells in order of f = g + h. The heuristic guides search toward the goal, visiting far fewer cells than Dijkstra on average.",
            complexity_time_best="O(E)",
            complexity_time_average="O(E log V)",
            complexity_time_worst="O(E log V)",
            complexity_space="O(V)",
            tags=("graph", "pathfinding", "heuristic", "grid", "a-star"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        rng = random.Random(params.seed)
        size: int = max(6, min(params.inputs.get("grid_size", 9), 12))
        wall_pct: int = max(10, min(params.inputs.get("wall_density", 20), 35))
        grid, start, goal = _build_grid(rng, size, size, wall_pct)
        return GridState(
            grid=tuple(tuple(row) for row in grid),
            current=None,
            path=(),
            description=f"A*: {size}×{size} grid, start={start}, goal={goal}, walls={wall_pct}%",
        )

    def steps(
        self, initial_state: GridState
    ) -> Generator[GridState, None, GridState]:
        grid_orig = [list(row) for row in initial_state.grid]
        rows = len(grid_orig)
        cols = len(grid_orig[0])

        # Find start and goal
        start: Optional[Tuple[int, int]] = None
        goal: Optional[Tuple[int, int]] = None
        for r in range(rows):
            for c in range(cols):
                if grid_orig[r][c] == CELL_START:
                    start = (r, c)
                elif grid_orig[r][c] == CELL_GOAL:
                    goal = (r, c)

        if start is None or goal is None:
            return initial_state

        g: Dict[Tuple[int, int], int] = {start: 0}
        parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        heap: List[Tuple[int, Tuple[int, int]]] = [(0 + _manhattan(start, goal), start)]
        closed: set = set()
        open_set: set = {start}

        def make_grid(current_node, highlight_path=()):
            g2 = [list(row) for row in grid_orig]
            for r, c in closed:
                if g2[r][c] == CELL_EMPTY:
                    g2[r][c] = CELL_CLOSED
            for r, c in open_set:
                if g2[r][c] == CELL_EMPTY:
                    g2[r][c] = CELL_OPEN
            for r, c in highlight_path:
                if g2[r][c] not in (CELL_START, CELL_GOAL):
                    g2[r][c] = CELL_PATH
            return tuple(tuple(row) for row in g2)

        while heap:
            f, current = heapq.heappop(heap)
            if current in closed:
                continue
            closed.add(current)
            open_set.discard(current)

            yield GridState(
                grid=make_grid(current),
                current=current,
                path=(),
                description=f"Expand ({current[0]},{current[1]}): g={g[current]}, h={_manhattan(current, goal)}, f={g[current]+_manhattan(current,goal)}",
            )

            if current == goal:
                # Reconstruct path
                path = []
                node = goal
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return GridState(
                    grid=make_grid(None, path),
                    current=None,
                    path=tuple(path),
                    description=f"Path found! Length={len(path)-1} steps",
                )

            r, c = current
            for nr, nc in _neighbors(r, c, rows, cols):
                if grid_orig[nr][nc] == CELL_WALL or (nr, nc) in closed:
                    continue
                ng = g[current] + 1
                if (nr, nc) not in g or ng < g[(nr, nc)]:
                    g[(nr, nc)] = ng
                    parent[(nr, nc)] = current
                    f_new = ng + _manhattan((nr, nc), goal)
                    heapq.heappush(heap, (f_new, (nr, nc)))
                    open_set.add((nr, nc))

        return GridState(
            grid=make_grid(None),
            current=None,
            path=(),
            description="No path found — goal is unreachable",
        )
