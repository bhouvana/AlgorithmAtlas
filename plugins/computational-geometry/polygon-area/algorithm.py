"""Polygon Area — Shoelace Formula plugin for Algorithm Atlas."""
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
CELL_VERTEX = 6   # CELL_PATH — polygon vertex
CELL_ACTIVE = 4   # CELL_OPEN — currently processing edge


def _make_convex_polygon(rng: random.Random, n: int) -> List[Tuple[int, int]]:
    """Generate n vertices of a convex polygon on the grid."""
    cx, cy = GRID_SIZE // 2, GRID_SIZE // 2
    r = GRID_SIZE // 2 - 3
    angles = sorted(rng.uniform(0, 2 * math.pi) for _ in range(n))
    pts = []
    for angle in angles:
        row = int(cx + r * math.sin(angle))
        col = int(cy + r * math.cos(angle))
        row = max(1, min(GRID_SIZE - 2, row))
        col = max(1, min(GRID_SIZE - 2, col))
        pts.append((row, col))
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for p in pts:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    while len(unique) < 3:
        unique.append((rng.randint(1, GRID_SIZE-2), rng.randint(1, GRID_SIZE-2)))
    return unique


def _make_grid(pts: List[Tuple[int, int]], active_i: int, active_j: int) -> Tuple:
    g = [[CELL_EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]
    for i, (r, c) in enumerate(pts):
        if i == active_i or i == active_j:
            g[r][c] = CELL_ACTIVE
        else:
            g[r][c] = CELL_VERTEX
    return tuple(tuple(row) for row in g)


class PolygonAreaSimulation(AlgorithmPlugin):
    """Polygon area via Shoelace formula."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="polygon-area",
            name="Polygon Area — Shoelace Formula",
            category="computational-geometry",
            visualization_type="GRID",
            description="Compute polygon area using the Shoelace (Gauss) formula in O(n).",
            intuition=(
                "For each edge (xi,yi)→(xi+1,yi+1), add xi*yi+1 − xi+1*yi. "
                "Area = |sum| / 2. Signed area is positive for CCW, negative for CW."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("computational-geometry", "polygon", "shoelace"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("vertex_count", 6))
        pts = _make_convex_polygon(rng, n)
        grid = _make_grid(pts, -1, -1)
        return GridState(
            grid=grid,
            current=None,
            path=tuple(pts),
            description=f"Shoelace on {len(pts)}-gon",
        )

    def steps(self, initial_state: GridState) -> Generator[GridState, None, GridState]:
        pts = list(initial_state.path)
        n = len(pts)
        running_sum = 0

        for i in range(n):
            j = (i + 1) % n
            xi, yi = pts[i][0], pts[i][1]
            xj, yj = pts[j][0], pts[j][1]
            term = xi * yj - xj * yi
            running_sum += term

            yield GridState(
                grid=_make_grid(pts, i, j),
                current=pts[i],
                path=tuple(pts),
                description=(
                    f"Edge {i}→{j}: {xi}×{yj} − {xj}×{yi} = {term:+d}, "
                    f"running sum = {running_sum}"
                ),
            )

        area_times_2 = abs(running_sum)
        area = area_times_2 / 2
        return GridState(
            grid=_make_grid(pts, -1, -1),
            current=None,
            path=tuple(pts),
            description=f"Area = |{running_sum}| / 2 = {area:.1f} sq units",
        )
