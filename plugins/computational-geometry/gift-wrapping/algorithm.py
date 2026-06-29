"""Convex Hull — Gift Wrapping (Jarvis March) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    GridState,
    SimulationParams,
)

GRID_SIZE = 20
CELL_EMPTY = 0
CELL_POINT = 1
CELL_HULL  = 6
CELL_ACTIVE = 4


def _make_grid(points: List[Tuple[int, int]], hull_indices: List[int], active: int) -> Tuple:
    g = [[CELL_EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]
    for i, (r, c) in enumerate(points):
        if i in hull_indices:
            g[r][c] = CELL_HULL
        elif i == active:
            g[r][c] = CELL_ACTIVE
        else:
            g[r][c] = CELL_POINT
    return tuple(tuple(row) for row in g)


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


class GiftWrappingSimulation(AlgorithmPlugin):
    """Gift Wrapping (Jarvis March) convex hull."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="gift-wrapping",
            name="Convex Hull — Gift Wrapping (Jarvis March)",
            category="computational-geometry",
            visualization_type="GRID",
            description="Find the convex hull using gift-wrapping in O(nh), where h is hull size.",
            intuition=(
                "Start from the leftmost point. "
                "At each step, pick the most counter-clockwise point from the current. "
                "Repeat until back at the start."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(nh)",
            complexity_time_worst="O(n²)",
            complexity_space="O(h)",
            tags=("computational-geometry", "convex-hull", "jarvis-march"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("point_count", 10))
        pts: List[Tuple[int, int]] = []
        while len(pts) < n:
            r = rng.randint(1, GRID_SIZE - 2)
            c = rng.randint(1, GRID_SIZE - 2)
            if (r, c) not in pts:
                pts.append((r, c))

        grid = _make_grid(pts, [], -1)
        return GridState(
            grid=grid,
            current=None,
            path=tuple(),
            description=f"Gift Wrapping on {n} points",
        )

    def steps(self, initial_state: GridState) -> Generator[GridState, None, GridState]:
        pts: List[Tuple[int, int]] = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if initial_state.grid[r][c] != CELL_EMPTY:
                    pts.append((r, c))
        pts.sort()

        # Leftmost point as start
        start = min(pts, key=lambda p: (p[1], p[0]))
        current = start
        hull: List[Tuple[int, int]] = []

        while True:
            hull.append(current)
            cur_idx = pts.index(current)
            hull_indices = [pts.index(p) for p in hull]

            yield GridState(
                grid=_make_grid(pts, hull_indices, cur_idx),
                current=current,
                path=tuple(hull),
                description=f"Added ({current[0]},{current[1]}) to hull, size={len(hull)}",
            )

            # Find most CCW point
            candidate = pts[0]
            for pt in pts[1:]:
                c_cross = _cross(current, candidate, pt)
                if c_cross < 0:
                    candidate = pt
                elif c_cross == 0:
                    # Collinear: pick farther one
                    d_cand = (candidate[0]-current[0])**2 + (candidate[1]-current[1])**2
                    d_pt   = (pt[0]-current[0])**2 + (pt[1]-current[1])**2
                    if d_pt > d_cand:
                        candidate = pt

            if candidate == start:
                break
            current = candidate

        hull_indices = [pts.index(p) for p in hull]
        return GridState(
            grid=_make_grid(pts, hull_indices, -1),
            current=None,
            path=tuple(hull),
            description=f"Convex hull: {len(hull)} vertices",
        )
