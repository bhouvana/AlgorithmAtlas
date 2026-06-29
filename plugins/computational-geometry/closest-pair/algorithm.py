"""Closest Pair of Points plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    GridState,
    SimulationParams,
)

GRID_SIZE = 20
CELL_EMPTY  = 0
CELL_POINT  = 1   # CELL_WALL
CELL_BEST   = 6   # CELL_PATH — current best pair
CELL_ACTIVE = 4   # CELL_OPEN — current pair being compared


def _make_grid(
    pts: List[Tuple[int, int]],
    active: Tuple[int, int],
    best: Tuple[int, int],
) -> Tuple:
    a_i, a_j = active
    b_i, b_j = best
    g = [[CELL_EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]
    for i, (r, c) in enumerate(pts):
        if i == b_i or i == b_j:
            g[r][c] = CELL_BEST
        elif i == a_i or i == a_j:
            g[r][c] = CELL_ACTIVE
        else:
            g[r][c] = CELL_POINT
    return tuple(tuple(row) for row in g)


def _dist(p, q):
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)


class ClosestPairSimulation(AlgorithmPlugin):
    """Closest Pair of Points — brute force O(n²)."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="closest-pair",
            name="Closest Pair of Points",
            category="computational-geometry",
            visualization_type="GRID",
            description="Find the two closest points in 2D by checking all pairs.",
            intuition=(
                "Check all n(n-1)/2 pairs. Track the running minimum. "
                "Divide-and-conquer achieves O(n log n) but brute force is clearest."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("computational-geometry", "closest-pair", "brute-force"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("point_count", 8))
        pts: List[Tuple[int, int]] = []
        while len(pts) < n:
            r = rng.randint(1, GRID_SIZE - 2)
            c = rng.randint(1, GRID_SIZE - 2)
            if (r, c) not in pts:
                pts.append((r, c))

        grid = _make_grid(pts, (-1, -1), (-1, -1))
        return GridState(
            grid=grid,
            current=None,
            path=tuple(pts),
            description=f"Closest pair in {n} points",
        )

    def steps(self, initial_state: GridState) -> Generator[GridState, None, GridState]:
        pts = list(initial_state.path)
        n = len(pts)
        best_i, best_j = 0, 1
        best_d = _dist(pts[0], pts[1])

        for i in range(n):
            for j in range(i + 1, n):
                d = _dist(pts[i], pts[j])
                changed = d < best_d
                if changed:
                    best_i, best_j = i, j
                    best_d = d

                yield GridState(
                    grid=_make_grid(pts, (i, j), (best_i, best_j)),
                    current=pts[i],
                    path=tuple(pts),
                    description=(
                        f"Pair ({i},{j}): d={d:.2f}"
                        + (f" ← new best!" if changed else f", best={best_d:.2f}")
                    ),
                )

        return GridState(
            grid=_make_grid(pts, (-1, -1), (best_i, best_j)),
            current=None,
            path=(pts[best_i], pts[best_j]),
            description=(
                f"Closest: ({pts[best_i][0]},{pts[best_i][1]}) ↔ "
                f"({pts[best_j][0]},{pts[best_j][1]}) dist={best_d:.2f}"
            ),
        )
