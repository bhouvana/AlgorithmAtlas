"""Convex Hull — Graham Scan plugin for Algorithm Atlas."""
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
CELL_EMPTY = 0
CELL_POINT = 1   # CELL_WALL — input point
CELL_HULL  = 6   # CELL_PATH — hull vertex
CELL_ACTIVE = 4  # CELL_OPEN — current candidate
CELL_INNER = 5   # CELL_CLOSED — eliminated/interior


def _make_grid(points: List[Tuple[int, int]], hull: List[int], active: int) -> Tuple:
    g = [[CELL_EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]
    for i, (r, c) in enumerate(points):
        if i in hull:
            g[r][c] = CELL_HULL
        elif i == active:
            g[r][c] = CELL_ACTIVE
        else:
            g[r][c] = CELL_POINT
    return tuple(tuple(row) for row in g)


def _cross(o, a, b):
    """Cross product of OA and OB. Positive = CCW, negative = CW, 0 = collinear."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


class ConvexHullGrahamSimulation(AlgorithmPlugin):
    """Graham Scan convex hull on a 2D integer grid."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="convex-hull-graham",
            name="Convex Hull — Graham Scan",
            category="computational-geometry",
            visualization_type="GRID",
            description="Find the convex hull of a 2D point set using Graham Scan in O(n log n).",
            intuition=(
                "Sort by polar angle from the lowest point. "
                "Maintain a CCW stack: pop while the last turn is clockwise, then push. "
                "The stack contains the hull at the end."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("computational-geometry", "convex-hull", "graham-scan"),
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
            description=f"Graham Scan on {n} points",
        )

    def steps(self, initial_state: GridState) -> Generator[GridState, None, GridState]:
        # Recover points from description
        n_str = initial_state.description.split(" on ")[1].split(" ")[0]
        n = int(n_str)

        seed_match = None
        # Re-generate identical point set using the grid as source of truth
        pts: List[Tuple[int, int]] = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if initial_state.grid[r][c] != CELL_EMPTY:
                    pts.append((r, c))
        # Sort by (row, col) to match original deterministic order
        pts.sort()

        # Step 1: Find bottom-most, then leftmost
        pivot = min(pts, key=lambda p: (p[0], p[1]))
        piv_idx = pts.index(pivot)

        yield GridState(
            grid=_make_grid(pts, [], piv_idx),
            current=pivot,
            path=tuple([pivot]),
            description=f"Pivot (lowest-leftmost): row={pivot[0]} col={pivot[1]}",
        )

        # Step 2: Sort by polar angle from pivot
        def polar_key(p):
            if p == pivot:
                return (-math.pi * 2, 0)
            dy = p[0] - pivot[0]
            dx = p[1] - pivot[1]
            angle = math.atan2(dy, dx)
            dist = dy * dy + dx * dx
            return (angle, dist)

        sorted_pts = sorted(pts, key=polar_key)

        # Step 3: Graham scan
        stack: List[Tuple[int, int]] = []
        for i, pt in enumerate(sorted_pts):
            pt_idx = pts.index(pt)
            while len(stack) >= 2 and _cross(stack[-2], stack[-1], pt) <= 0:
                popped = stack.pop()
                hull_set = set(pts.index(p) for p in stack)
                yield GridState(
                    grid=_make_grid(pts, list(hull_set), pt_idx),
                    current=pt,
                    path=tuple(stack + [pt]),
                    description=f"Pop ({popped[0]},{popped[1]}): clockwise turn",
                )
            stack.append(pt)
            hull_set = set(pts.index(p) for p in stack)
            yield GridState(
                grid=_make_grid(pts, list(hull_set), pt_idx),
                current=pt,
                path=tuple(stack),
                description=f"Push ({pt[0]},{pt[1]}), hull size={len(stack)}",
            )

        hull_indices = [pts.index(p) for p in stack]
        return GridState(
            grid=_make_grid(pts, hull_indices, -1),
            current=None,
            path=tuple(stack),
            description=f"Convex hull: {len(stack)} vertices",
        )
