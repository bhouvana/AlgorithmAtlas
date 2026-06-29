"""Rotating Calipers plugin for Algorithm Atlas."""
from __future__ import annotations

import math
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Fixed convex polygon (already in CCW order)
_HULL = [
    (1, 4), (3, 7), (6, 8), (9, 6), (10, 3), (8, 1), (4, 1),
]


def _dist2(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def _dist(p1, p2):
    return math.sqrt(_dist2(p1, p2))


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _edge_cross(hull, i, j):
    """Cross product of edge vectors at hull[i] and hull[j]."""
    n = len(hull)
    ni = (i + 1) % n
    nj = (j + 1) % n
    ei = (hull[ni][0] - hull[i][0], hull[ni][1] - hull[i][1])
    ej = (hull[nj][0] - hull[j][0], hull[nj][1] - hull[j][1])
    return ei[0] * ej[1] - ei[1] * ej[0]


def _rotating_calipers_steps(hull):
    """Return antipodal pairs (i, j, dist). Correctly initialized."""
    n = len(hull)
    steps = []
    # Find initial antipodal: farthest from hull[0]
    j = 1
    while _dist2(hull[0], hull[(j + 1) % n]) > _dist2(hull[0], hull[j]):
        j += 1

    for i in range(n):
        steps.append((i, j, _dist(hull[i], hull[j])))
        c = _edge_cross(hull, i, j)
        if c > 0:
            j = (j + 1) % n
        elif c == 0:
            # Flush both
            ni = (i + 1) % n
            nj = (j + 1) % n
            steps.append((ni, j, _dist(hull[ni], hull[j])))
            steps.append((i, nj, _dist(hull[i], hull[nj])))
            j = nj

    return steps


class RotatingCaliperSimulation(AlgorithmPlugin):
    """Rotating calipers diameter computation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="rotating-calipers",
            name="Rotating Calipers",
            category="computational-geometry",
            visualization_type="ARRAY_BARS",
            description="Find convex polygon diameter using rotating calipers.",
            intuition=(
                "Two antipodal supporting lines rotate around the convex hull. "
                "At each step, advance whichever caliper has the smaller cross product. "
                "Track maximum distance between caliper contact points."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("computational-geometry", "convex-hull", "rotating-calipers", "diameter", "antipodal"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        hull = _HULL
        n = len(hull)
        # Show pairwise distances as initial array
        steps = _rotating_calipers_steps(hull)
        arr = tuple(1 for _ in steps)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"RotCalipers hull_size={n}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        hull = _HULL
        steps = _rotating_calipers_steps(hull)
        all_dists = [s[2] for s in steps]
        max_dist = max(all_dists)

        for idx, (i, j, d) in enumerate(steps):
            distances_so_far = all_dists[:idx + 1]
            mx = max(distances_so_far) or 1.0
            arr = tuple(
                max(1, min(99, int(v * 99 / mx)))
                for v in distances_so_far
            ) + tuple(1 for _ in range(len(steps) - idx - 1))

            is_max = abs(d - max_dist) < 1e-9
            yield SortState(
                array=arr,
                comparing=(idx, idx),
                last_swap=(idx, idx) if is_max else None,
                sorted_indices=frozenset(k for k in range(idx + 1) if abs(all_dists[k] - max_dist) < 1e-9),
                comparisons=idx + 1,
                swaps=int(d * 100),  # distance * 100 for integer storage
                description=(
                    f"Pair ({i},{j}): dist={d:.2f}"
                    + (" ← MAX" if is_max else "")
                ),
            )

        arr_final = tuple(
            max(1, min(99, int(d * 99 / max_dist)))
            for d in all_dists
        )
        return SortState(
            array=arr_final,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(steps))),
            comparisons=len(steps),
            swaps=int(max_dist * 100),
            description=f"Diameter = {max_dist:.2f} (in {len(steps)} caliper positions)",
        )
