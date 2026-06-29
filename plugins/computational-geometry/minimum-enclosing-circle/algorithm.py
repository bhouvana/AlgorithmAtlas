"""Minimum Enclosing Circle (Welzl) plugin for Algorithm Atlas."""
from __future__ import annotations

import math
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _circle_2(p1, p2):
    cx = (p1[0] + p2[0]) / 2
    cy = (p1[1] + p2[1]) / 2
    r = math.hypot(p1[0] - cx, p1[1] - cy)
    return (cx, cy, r)


def _circle_3(p1, p2, p3):
    ax, ay = p1
    bx, by = p2
    cx, cy = p3
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-9:
        # Collinear: return circle from widest pair
        c12 = _circle_2(p1, p2)
        c13 = _circle_2(p1, p3)
        c23 = _circle_2(p2, p3)
        return max(c12, c13, c23, key=lambda c: c[2])
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) +
          (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) +
          (cx**2 + cy**2) * (bx - ax)) / d
    r = math.hypot(ax - ux, ay - uy)
    return (ux, uy, r)


def _in_circle(c, p, eps=1e-7):
    return math.hypot(p[0] - c[0], p[1] - c[1]) <= c[2] + eps


def _mec_with_boundary(pts, R):
    """Smallest enclosing circle with points R on boundary (|R| <= 2)."""
    if not pts or len(R) == 3:
        if len(R) == 0:
            return (0.0, 0.0, 0.0)
        if len(R) == 1:
            return (R[0][0], R[0][1], 0.0)
        if len(R) == 2:
            return _circle_2(R[0], R[1])
        return _circle_3(R[0], R[1], R[2])
    p = pts[0]
    D = _mec_with_boundary(pts[1:], R)
    if _in_circle(D, p):
        return D
    return _mec_with_boundary(pts[1:], R + [p])


def _scale_dist(dist, max_r):
    if max_r < 1e-9:
        return 1
    return max(1, min(99, int(dist * 99 / max_r)))


class MinimumEnclosingCircleSimulation(AlgorithmPlugin):
    """Welzl's randomized incremental MEC algorithm."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="minimum-enclosing-circle",
            name="Minimum Enclosing Circle (Welzl)",
            category="computational-geometry",
            visualization_type="ARRAY_BARS",
            description="Find the smallest circle enclosing n random points.",
            intuition=(
                "Process points one by one. If a new point is inside the current "
                "circle, continue. Otherwise it must be on the boundary — recompute "
                "the MEC of previous points with this constraint."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n³)",
            complexity_space="O(1)",
            tags=("computational-geometry", "welzl", "enclosing-circle", "randomized"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        import random
        n = int(params.inputs.get("size", 10))
        rng = random.Random(params.seed)
        pts = [(rng.randint(5, 95), rng.randint(5, 95)) for _ in range(n)]
        # Encode points in description
        pts_str = ";".join(f"{x},{y}" for x, y in pts)
        return SortState(
            array=tuple([50] * n),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"MEC n={n} seed={params.seed} pts={pts_str}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        import random
        desc = initial_state.description
        n = int(re.search(r"n=(\d+)", desc).group(1))
        seed = int(re.search(r"seed=(\d+)", desc).group(1))
        pts_str = re.search(r"pts=(.+)$", desc).group(1)
        pts = [tuple(map(int, p.split(","))) for p in pts_str.split(";")]

        # Shuffle for Welzl's expected linear time
        rng = random.Random(seed * 7 + 13)
        order = list(range(n))
        rng.shuffle(order)
        pts_shuffled = [pts[i] for i in order]

        circle = (pts_shuffled[0][0], pts_shuffled[0][1], 0.0)

        def dists_array(c, pts_list):
            max_r = max(c[2], 1.0)
            return tuple(_scale_dist(math.hypot(p[0] - c[0], p[1] - c[1]), max_r)
                         for p in pts_list)

        inside = frozenset()
        for i in range(1, n):
            p = pts_shuffled[i]
            if _in_circle(circle, p):
                inside = frozenset(j for j in range(i + 1)
                                   if _in_circle(circle, pts_shuffled[j]))
                yield SortState(
                    array=dists_array(circle, pts_shuffled),
                    comparing=(i, i),
                    last_swap=None,
                    sorted_indices=inside,
                    comparisons=i,
                    swaps=int(circle[2]),
                    description=(
                        f"Point {i} inside circle (r={circle[2]:.1f})"
                    ),
                )
            else:
                # Must be on boundary — recompute
                new_circle = _mec_with_boundary(pts_shuffled[:i], [p])
                circle = new_circle
                inside = frozenset(j for j in range(i + 1)
                                   if _in_circle(circle, pts_shuffled[j]))
                yield SortState(
                    array=dists_array(circle, pts_shuffled),
                    comparing=(i, i),
                    last_swap=(i, i),
                    sorted_indices=inside,
                    comparisons=i,
                    swaps=int(circle[2]),
                    description=(
                        f"Point {i} outside! Recompute: center=({circle[0]:.1f},{circle[1]:.1f}) r={circle[2]:.1f}"
                    ),
                )

        inside_final = frozenset(j for j in range(n) if _in_circle(circle, pts_shuffled[j]))
        return SortState(
            array=dists_array(circle, pts_shuffled),
            comparing=None,
            last_swap=None,
            sorted_indices=inside_final,
            comparisons=n,
            swaps=int(circle[2]),
            description=(
                f"MEC done: center=({circle[0]:.1f},{circle[1]:.1f}) r={circle[2]:.1f} "
                f"enclosing {len(inside_final)}/{n} pts"
            ),
        )
