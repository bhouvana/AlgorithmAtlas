"""Random Walk (2D) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    GridState,
    SimulationParams,
)

GRID_SIZE = 20
CELL_EMPTY = 0
CELL_PATH = 6    # visited cell
CELL_START = 2   # origin
CELL_CURRENT = 3 # current walker position

_DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def _make_grid(path: list, start: tuple) -> tuple:
    g = [[CELL_EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]
    for r, c in path[:-1]:
        g[r][c] = CELL_PATH
    sr, sc = start
    g[sr][sc] = CELL_START
    cr, cc = path[-1]
    g[cr][cc] = CELL_CURRENT
    return tuple(tuple(row) for row in g)


class RandomWalkSimulation(AlgorithmPlugin):
    """2D random walk on a bounded grid."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="random-walk",
            name="Random Walk (2D)",
            category="randomized",
            visualization_type="GRID",
            description="Simulate a 2D random walk: at each step, move to a random neighbour.",
            intuition=(
                "Starting from centre, choose up/down/left/right at random each step. "
                "After n steps the typical distance from start is ~√n (diffusion)."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("randomized", "random-walk", "simulation", "probability"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        n = int(params.inputs.get("steps", 50))
        start = (GRID_SIZE // 2, GRID_SIZE // 2)
        grid = _make_grid([start], start)
        return GridState(
            grid=grid,
            current=start,
            path=(start,),
            description=f"Random walk: steps={n} seed={params.seed}",
        )

    def steps(self, initial_state: GridState) -> Generator[GridState, None, GridState]:
        import re
        desc = initial_state.description
        n = int(re.search(r"steps=(\d+)", desc).group(1))
        seed_val = int(re.search(r"seed=(\d+)", desc).group(1))
        rng = random.Random(seed_val)

        start = (GRID_SIZE // 2, GRID_SIZE // 2)
        r, c = start
        path = [start]
        visited: set = {start}

        step_size = max(1, n // 30)

        for step in range(1, n + 1):
            dr, dc = rng.choice(_DIRS)
            r = max(0, min(GRID_SIZE - 1, r + dr))
            c = max(0, min(GRID_SIZE - 1, c + dc))
            path.append((r, c))
            visited.add((r, c))

            if step % step_size == 0 or step == n:
                sr, sc = start
                dist = abs(r - sr) + abs(c - sc)
                yield GridState(
                    grid=_make_grid(path, start),
                    current=(r, c),
                    path=tuple(path),
                    description=(
                        f"Step {step}/{n}: pos=({r},{c}) "
                        f"dist={dist} unique={len(visited)}"
                    ),
                )

        sr, sc = start
        dist = abs(r - sr) + abs(c - sc)
        return GridState(
            grid=_make_grid(path, start),
            current=None,
            path=tuple(path),
            description=(
                f"Done: {n} steps, final=({r},{c}), "
                f"dist={dist}, unique cells={len(visited)}"
            ),
        )
