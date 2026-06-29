"""Convex Hull Trick DP optimization plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator, List, Optional

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# Problem: dp[j] = min over i<j of (dp[i] + slope[i] * query[j])
# Slopes are decreasing, queries are increasing → monotone CHT → O(n)
# Concrete: divide n tasks into groups; cost of adding task j to group
# ending at i is slope[i] * j.
_N = 6
_SLOPES = [10, 8, 6, 4, 2, 0]    # b[i]: cost multiplier for line from state i
_QUERIES = [1, 2, 3, 4, 5, 6]    # x[j]: query values (increasing)
# dp[0] = 0 (base case)
# dp[j] = min_{0<=i<j}( dp[i] + _SLOPES[i] * _QUERIES[j] )


class _Line:
    __slots__ = ("m", "b")

    def __init__(self, m: int, b: int):
        self.m = m   # slope
        self.b = b   # intercept (= dp[i])

    def eval(self, x: int) -> int:
        return self.m * x + self.b


def _bad(l1: _Line, l2: _Line, l3: _Line) -> bool:
    """True if l2 is never optimal given l1 and l3 (l1.m >= l2.m >= l3.m)."""
    # Intersection of l1,l3 is <= intersection of l1,l2 ⟹ l2 useless
    return (l3.b - l1.b) * (l1.m - l2.m) <= (l2.b - l1.b) * (l1.m - l3.m)


class ConvexHullTrickSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="convex-hull-trick",
            name="Convex Hull Trick (DP Optimization)",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Optimize dp[j]=min_i(dp[i]+b[i]·x[j]) from O(n²) to O(n) using a convex hull of lines.",
            intuition=(
                "Each state i defines a line y = b[i]·x + dp[i]. "
                "For query x[j] we want the minimum y. "
                "Maintain these lines as a lower convex hull. "
                "With monotone slopes and queries the hull pointer moves forward only."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "convex-hull-trick", "cht", "optimization", "lines"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        dp = [0] + [10 ** 9] * (_N - 1)
        opt = [-1] * _N
        return DPState(
            table=(tuple(dp), tuple(opt)),
            current_cell=None,
            computed_cells=frozenset({(0, 0)}),
            description=f"slopes={_SLOPES}  queries={_QUERIES}  dp[0]=0",
        )

    def steps(self, initial_state: DPState) -> Generator[DPState, None, DPState]:
        dp: List[int] = [0] + [10 ** 9] * (_N - 1)
        opt: List[int] = [-1] * _N
        computed: set = {(0, 0)}
        hull: List[_Line] = []
        ptr = 0   # monotone pointer

        def add_line(line: _Line):
            while len(hull) >= 2 and _bad(hull[-2], hull[-1], line):
                hull.pop()
            hull.append(line)

        def query(x: int) -> tuple:
            nonlocal ptr
            while ptr + 1 < len(hull) and hull[ptr + 1].eval(x) <= hull[ptr].eval(x):
                ptr += 1
            return hull[ptr].eval(x), ptr

        # Add line for dp[0]
        add_line(_Line(_SLOPES[0], dp[0]))
        yield DPState(
            table=(tuple(dp), tuple(opt)),
            current_cell=(0, 0),
            computed_cells=frozenset(computed),
            description=f"Add line: y = {_SLOPES[0]}x + {dp[0]} (from state 0)",
        )

        for j in range(1, _N):
            val, best_i = query(_QUERIES[j])
            dp[j] = val
            opt[j] = best_i
            computed.add((0, j))
            computed.add((1, j))
            yield DPState(
                table=(tuple(dp), tuple(opt)),
                current_cell=(0, j),
                computed_cells=frozenset(computed),
                description=(
                    f"dp[{j}]: query x={_QUERIES[j]} → best line {best_i} "
                    f"gives {val} (dp[{j}]={dp[j]})"
                ),
            )
            # Add new line for state j
            if j < _N - 1:
                add_line(_Line(_SLOPES[j], dp[j]))
                yield DPState(
                    table=(tuple(dp), tuple(opt)),
                    current_cell=(1, j),
                    computed_cells=frozenset(computed),
                    description=(
                        f"Add line: y = {_SLOPES[j]}x + {dp[j]} (hull size={len(hull)})"
                    ),
                )

        final = DPState(
            table=(tuple(dp), tuple(opt)),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"CHT done: dp={dp}  optimal previous indices={opt}",
        )
        yield final
        return final
