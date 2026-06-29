"""Point-in-Polygon (Ray Casting) plugin for Algorithm Atlas."""
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
CELL_WALL = 1    # polygon edge
CELL_START = 2   # polygon vertex
CELL_QUERY = 3   # query point (CELL_GOAL)
CELL_OPEN = 4    # ray outside polygon / crossing point
CELL_PATH = 6    # ray inside polygon


def _bresenham(r0, c0, r1, c1):
    """Yield integer (row, col) pairs along the line from (r0,c0) to (r1,c1)."""
    dr = abs(r1 - r0)
    dc = abs(c1 - c0)
    sr = 1 if r1 > r0 else -1
    sc = 1 if c1 > c0 else -1
    err = dr - dc
    r, c = r0, c0
    while True:
        yield r, c
        if r == r1 and c == c1:
            break
        e2 = 2 * err
        if e2 > -dc:
            err -= dc
            r += sr
        if e2 < dr:
            err += dr
            c += sc


def _make_convex_polygon(rng: random.Random, n_verts: int):
    """Generate n_verts vertices of a convex polygon scaled to the grid."""
    import math
    cx, cy = GRID_SIZE // 2, GRID_SIZE // 2
    r = GRID_SIZE // 2 - 3
    angles = sorted(rng.uniform(0, 2 * math.pi) for _ in range(n_verts))
    return [
        (int(cy + r * math.sin(a)), int(cx + r * math.cos(a)))
        for a in angles
    ]


def _ray_crosses_edge(qr, qc, r1, c1, r2, c2) -> bool:
    """Does horizontal ray from (qr, qc) rightward cross edge (r1,c1)-(r2,c2)?"""
    if r1 == r2:
        return False  # horizontal edge — skip to avoid ambiguity
    # Check if edge straddles query row
    if min(r1, r2) < qr <= max(r1, r2):
        # x-coordinate of crossing
        t = (qr - r1) / (r2 - r1)
        cross_c = c1 + t * (c2 - c1)
        return cross_c >= qc
    return False


def _draw_polygon(verts):
    """Return set of (row, col) on all polygon edges."""
    cells = set()
    n = len(verts)
    for i in range(n):
        r0, c0 = verts[i]
        r1, c1 = verts[(i + 1) % n]
        for r, c in _bresenham(r0, c0, r1, c1):
            cells.add((r, c))
    return cells


def _make_grid(poly_cells, verts, query, ray_inside_cells, ray_outside_cells, crossing_cells):
    g = [[CELL_EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]
    for r, c in poly_cells:
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            g[r][c] = CELL_WALL
    for r, c in ray_outside_cells:
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and g[r][c] == CELL_EMPTY:
            g[r][c] = CELL_OPEN
    for r, c in ray_inside_cells:
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and g[r][c] == CELL_EMPTY:
            g[r][c] = CELL_PATH
    for r, c in crossing_cells:
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            g[r][c] = CELL_START
    qr, qc = query
    if 0 <= qr < GRID_SIZE and 0 <= qc < GRID_SIZE:
        g[qr][qc] = CELL_QUERY
    return tuple(tuple(row) for row in g)


class PointInPolygonSimulation(AlgorithmPlugin):
    """Point-in-Polygon via ray casting."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="point-in-polygon",
            name="Point in Polygon (Ray Casting)",
            category="computational-geometry",
            visualization_type="GRID",
            description=(
                "Determine whether a point is inside a polygon "
                "using the ray-casting algorithm."
            ),
            intuition=(
                "Cast a horizontal ray rightward from the query point. "
                "Count polygon edge crossings. Odd → inside; even → outside."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("computational-geometry", "ray-casting", "polygon", "point-location"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        rng = random.Random(params.seed)
        verts = _make_convex_polygon(rng, 6)
        # Query point: either clearly inside or outside
        qr = rng.randint(3, GRID_SIZE - 4)
        qc = rng.randint(3, GRID_SIZE - 4)

        poly_cells = _draw_polygon(verts)
        grid = _make_grid(poly_cells, verts, (qr, qc), [], [], [])
        vert_str = ";".join(f"{r},{c}" for r, c in verts)
        return GridState(
            grid=grid,
            current=(qr, qc),
            path=tuple(),
            description=f"PIP query=({qr},{qc}) verts={vert_str} seed={params.seed}",
        )

    def steps(self, initial_state: GridState) -> Generator[GridState, None, GridState]:
        import re
        desc = initial_state.description
        qr, qc = map(int, re.search(r"query=\((\d+),(\d+)\)", desc).groups())
        vert_str = re.search(r"verts=([^s]+) seed", desc).group(1)
        verts = [
            tuple(map(int, pair.split(",")))
            for pair in vert_str.split(";")
        ]

        poly_cells = _draw_polygon(verts)
        n = len(verts)
        crossings = 0
        crossing_cells: list = []

        for i in range(n):
            r1, c1 = verts[i]
            r2, c2 = verts[(i + 1) % n]

            crossed = _ray_crosses_edge(qr, qc, r1, c1, r2, c2)
            if crossed:
                crossings += 1
                # Approximate crossing cell
                t = (qr - r1) / (r2 - r1)
                cross_c = int(c1 + t * (c2 - c1))
                crossing_cells.append((qr, cross_c))

            # Colour the ray: alternate inside/outside as crossings accumulate
            ray_cells = [(qr, col) for col in range(qc + 1, GRID_SIZE)]
            inside_cells = []
            outside_cells = []
            # Simple colouring: cells right of an odd number of crossings = inside
            for _, col in ray_cells:
                cx_count = sum(1 for _, xc in crossing_cells if xc < col)
                if cx_count % 2 == 1:
                    inside_cells.append((qr, col))
                else:
                    outside_cells.append((qr, col))

            yield GridState(
                grid=_make_grid(
                    poly_cells, verts, (qr, qc),
                    inside_cells, outside_cells, crossing_cells
                ),
                current=(qr, qc),
                path=tuple(crossing_cells),
                description=(
                    f"Edge {i+1}/{n} ({r1},{c1})→({r2},{c2}): "
                    f"{'CROSSED' if crossed else 'no cross'}, "
                    f"crossings so far={crossings}"
                ),
            )

        inside = crossings % 2 == 1
        ray_cells = [(qr, col) for col in range(qc + 1, GRID_SIZE)]
        inside_cells_final = []
        outside_cells_final = []
        for _, col in ray_cells:
            cx_count = sum(1 for _, xc in crossing_cells if xc < col)
            if cx_count % 2 == 1:
                inside_cells_final.append((qr, col))
            else:
                outside_cells_final.append((qr, col))

        return GridState(
            grid=_make_grid(
                poly_cells, verts, (qr, qc),
                inside_cells_final, outside_cells_final, crossing_cells
            ),
            current=None,
            path=tuple(crossing_cells),
            description=(
                f"Result: query ({qr},{qc}) is "
                f"{'INSIDE' if inside else 'OUTSIDE'} polygon "
                f"({crossings} crossings)"
            ),
        )
