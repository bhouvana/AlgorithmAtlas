"""Closest Pair of Points divide-and-conquer plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_SCALE = 100  # Fixed-point scale: store x*100, y*100 as integers


def _dist(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    dx = (a[0] - b[0]) / _SCALE
    dy = (a[1] - b[1]) / _SCALE
    return math.sqrt(dx * dx + dy * dy)


def _make_points(rng: random.Random, n: int) -> List[Tuple[int, int]]:
    """Generate n distinct 2D points with integer coordinates 0..9."""
    seen = set()
    pts = []
    while len(pts) < n:
        x, y = rng.randint(0, 9), rng.randint(0, 9)
        if (x, y) not in seen:
            seen.add((x, y))
            pts.append((x * _SCALE, y * _SCALE))
    return sorted(pts)


class ClosestPairSimulation(AlgorithmPlugin):
    """
    Closest Pair of Points — O(n log n).

    DPState table rows (columns = n points sorted by x):
      row 0: x-coordinates (scaled by 100)
      row 1: y-coordinates (scaled by 100)

    Steps yield frames for each divide/merge operation.
    description encodes point coords: "ClosestPair: p1=(x1,y1) p2=(x2,y2) d=D.DD"
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="closest-pair",
            name="Closest Pair of Points",
            category="divide-and-conquer",
            visualization_type="MATRIX",
            description=(
                "Find two points with minimum Euclidean distance "
                "using divide-and-conquer — O(n log n) vs O(n²) brute-force."
            ),
            intuition=(
                "Sort by x. Divide into left/right halves; recurse to find min distance d. "
                "Check 2d-wide strip around midline — any crossing pair is within this strip."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("divide-and-conquer", "geometry", "closest-pair", "recursion"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 6), 10))
        pts = _make_points(rng, n)
        xs = tuple(p[0] for p in pts)
        ys = tuple(p[1] for p in pts)
        return DPState(
            table=(xs, ys),
            current_cell=None,
            computed_cells=frozenset(),
            description=f"ClosestPair: {n} points sorted by x",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        xs = list(initial_state.table[0])
        ys = list(initial_state.table[1])
        n = len(xs)
        pts = list(zip(xs, ys))
        computed: set = set()
        frames: list = []

        best_d = [math.inf]
        best_pair = [None, None]

        def rec(lo: int, hi: int) -> float:
            """Recursive closest pair on pts[lo:hi+1] (sorted by x)."""
            if hi - lo < 1:
                return math.inf
            if hi - lo == 1:
                d = _dist(pts[lo], pts[hi])
                if d < best_d[0]:
                    best_d[0] = d
                    best_pair[0], best_pair[1] = lo, hi
                computed.add((0, lo))
                computed.add((0, hi))
                frames.append((lo, hi, d))
                return d

            mid = (lo + hi) // 2
            d_left = rec(lo, mid)
            d_right = rec(mid + 1, hi)
            d = min(d_left, d_right)

            # Check strip — d is real distance, pts coords are scaled
            mid_x = pts[mid][0]
            strip = [i for i in range(lo, hi + 1) if abs(pts[i][0] - mid_x) / _SCALE < d]
            strip.sort(key=lambda i: pts[i][1])

            for a in range(len(strip)):
                for b in range(a + 1, len(strip)):
                    if (pts[strip[b]][1] - pts[strip[a]][1]) / _SCALE >= d:
                        break
                    dc = _dist(pts[strip[a]], pts[strip[b]])
                    if dc < d:
                        d = dc
                        if dc < best_d[0]:
                            best_d[0] = dc
                            best_pair[0], best_pair[1] = strip[a], strip[b]

            for i in range(lo, hi + 1):
                computed.add((0, i))
                computed.add((1, i))
            frames.append((lo, hi, d))
            return d

        rec(0, n - 1)

        # Yield frames — d is already in real (unscaled) distance units
        for lo, hi, d in frames:
            yield DPState(
                table=(tuple(xs), tuple(ys)),
                current_cell=(0, (lo + hi) // 2),
                computed_cells=frozenset(computed),
                description=(
                    f"Subproblem [{lo},{hi}]: min dist = {d:.3f}"
                ),
            )

        p1, p2 = best_pair
        d_final = best_d[0]
        x1, y1 = xs[p1] // _SCALE, ys[p1] // _SCALE
        x2, y2 = xs[p2] // _SCALE, ys[p2] // _SCALE
        return DPState(
            table=(tuple(xs), tuple(ys)),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=(
                f"Closest: ({x1},{y1}) and ({x2},{y2}), dist={d_final:.3f}"
            ),
        )
