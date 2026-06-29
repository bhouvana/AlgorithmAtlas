"""Line Segment Intersection Test plugin for Algorithm Atlas."""
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
CELL_ENDPT = 1   # CELL_WALL — segment endpoint
CELL_INTER = 6   # CELL_PATH — intersection point
CELL_AB    = 4   # CELL_OPEN — segment AB points
CELL_CD    = 5   # CELL_CLOSED — segment CD points


_SEGMENT_PAIRS = [
    # (A, B, C, D, intersects)
    ((3, 3), (17, 17), (3, 17), (17, 3), True),
    ((2, 2), (8, 2),  (5, 1), (5, 10), True),
    ((1, 1), (5, 5),  (6, 6), (10, 10), False),
    ((2, 5), (10, 5), (6, 3), (6, 12), True),
    ((1, 1), (3, 3),  (4, 4), (8, 8),  False),
    ((5, 1), (5, 18), (1, 9), (18, 9), True),
    ((1, 1), (10, 1), (1, 5), (10, 5), False),
    ((3, 8), (15, 8), (9, 3), (9, 14), True),
    ((2, 2), (2, 15), (1, 15), (5, 15), True),
    ((1, 1), (8, 8),  (9, 9), (15, 15), False),
]


def _cross(o, a, b):
    return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])


def _on_segment(p, q, r):
    return (min(p[0],r[0]) <= q[0] <= max(p[0],r[0]) and
            min(p[1],r[1]) <= q[1] <= max(p[1],r[1]))


def _intersects(a, b, c, d) -> bool:
    d1 = _cross(c, d, a)
    d2 = _cross(c, d, b)
    d3 = _cross(a, b, c)
    d4 = _cross(a, b, d)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    if d1 == 0 and _on_segment(c, a, d): return True
    if d2 == 0 and _on_segment(c, b, d): return True
    if d3 == 0 and _on_segment(a, c, b): return True
    if d4 == 0 and _on_segment(a, d, b): return True
    return False


def _draw_line(r0, c0, r1, c1) -> List[Tuple[int, int]]:
    """Bresenham line rasterization."""
    pts = []
    dr = abs(r1 - r0)
    dc = abs(c1 - c0)
    sr = 1 if r0 < r1 else -1
    sc = 1 if c0 < c1 else -1
    err = dr - dc
    r, c = r0, c0
    while True:
        pts.append((r, c))
        if r == r1 and c == c1:
            break
        e2 = 2 * err
        if e2 > -dc: err -= dc; r += sr
        if e2 < dr:  err += dr; c += sc
    return pts


def _make_grid(a, b, c, d, phase: str) -> Tuple:
    g = [[CELL_EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]
    for r, col in _draw_line(a[0], a[1], b[0], b[1]):
        if 0 <= r < GRID_SIZE and 0 <= col < GRID_SIZE:
            g[r][col] = CELL_AB
    for r, col in _draw_line(c[0], c[1], d[0], d[1]):
        if 0 <= r < GRID_SIZE and 0 <= col < GRID_SIZE:
            g[r][col] = CELL_CD
    for pt in [a, b, c, d]:
        r, col = pt
        if 0 <= r < GRID_SIZE and 0 <= col < GRID_SIZE:
            g[r][col] = CELL_ENDPT
    if phase == "intersect":
        # Mark approximate intersection zone
        for r in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if g[r][col] == CELL_AB:
                    # Check neighbors for CD
                    for nr, nc in [(r-1,col),(r+1,col),(r,col-1),(r,col+1)]:
                        if 0<=nr<GRID_SIZE and 0<=nc<GRID_SIZE and g[nr][nc]==CELL_CD:
                            g[r][col] = CELL_INTER
                            g[nr][nc] = CELL_INTER
    return tuple(tuple(row) for row in g)


class LineSegmentIntersectionSimulation(AlgorithmPlugin):
    """Line segment intersection test using cross-product orientations."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="line-segment-intersection",
            name="Line Segment Intersection Test",
            category="computational-geometry",
            visualization_type="GRID",
            description="Determine if two line segments intersect using cross-product orientation.",
            intuition=(
                "Segment AB intersects CD if and only if A and B straddle line CD "
                "AND C and D straddle line AB. Cross products encode which side each point is on."
            ),
            complexity_time_best="O(1)",
            complexity_time_average="O(1)",
            complexity_time_worst="O(1)",
            complexity_space="O(1)",
            tags=("computational-geometry", "line-segment", "intersection"),
        )

    def initialize(self, params: SimulationParams) -> GridState:
        rng = random.Random(params.seed)
        idx = rng.randint(0, len(_SEGMENT_PAIRS) - 1)
        a, b, c, d, expected = _SEGMENT_PAIRS[idx]
        grid = _make_grid(a, b, c, d, "initial")
        return GridState(
            grid=grid,
            current=a,
            path=(a, b, c, d),
            description=f"Test AB∩CD? expected={'YES' if expected else 'NO'} case={idx}",
        )

    def steps(self, initial_state: GridState) -> Generator[GridState, None, GridState]:
        a, b, c, d = initial_state.path[:4]

        # Step 1: Compute d1 = cross(C, D, A)
        d1 = _cross(c, d, a)
        yield GridState(
            grid=_make_grid(a, b, c, d, "initial"),
            current=a,
            path=(a, b, c, d),
            description=f"d1 = cross(C,D,A) = {d1} ({'left' if d1>0 else 'right' if d1<0 else 'on'})",
        )

        # Step 2: Compute d2 = cross(C, D, B)
        d2 = _cross(c, d, b)
        yield GridState(
            grid=_make_grid(a, b, c, d, "initial"),
            current=b,
            path=(a, b, c, d),
            description=f"d2 = cross(C,D,B) = {d2} ({'left' if d2>0 else 'right' if d2<0 else 'on'})",
        )

        # Step 3: Compute d3 = cross(A, B, C)
        d3 = _cross(a, b, c)
        yield GridState(
            grid=_make_grid(a, b, c, d, "initial"),
            current=c,
            path=(a, b, c, d),
            description=f"d3 = cross(A,B,C) = {d3} ({'left' if d3>0 else 'right' if d3<0 else 'on'})",
        )

        # Step 4: Compute d4 = cross(A, B, D)
        d4 = _cross(a, b, d)
        straddle = ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
                   ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0))
        yield GridState(
            grid=_make_grid(a, b, c, d, "initial"),
            current=d,
            path=(a, b, c, d),
            description=f"d4 = cross(A,B,D) = {d4}. Straddle check: {'YES' if straddle else 'NO'}",
        )

        result = _intersects(a, b, c, d)
        phase = "intersect" if result else "initial"
        return GridState(
            grid=_make_grid(a, b, c, d, phase),
            current=None,
            path=(a, b, c, d),
            description=f"Segments {'DO' if result else 'do NOT'} intersect",
        )
