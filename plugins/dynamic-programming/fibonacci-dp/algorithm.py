"""Fibonacci DP (bottom-up) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class FibonacciDPSimulation(AlgorithmPlugin):
    """
    Fibonacci via bottom-up dynamic programming.

    Builds a 1×(n+1) table left to right:
      dp[0] = 0,  dp[1] = 1
      dp[i] = dp[i-1] + dp[i-2]  for i >= 2

    Visualization: 1-D row of cells, filled amber-then-green as the
    algorithm steps through.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="fibonacci-dp",
            name="Fibonacci (DP)",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Computes Fibonacci numbers via bottom-up DP table.",
            intuition="Store each fib(i) once. dp[i] = dp[i-1] + dp[i-2] in O(1) per cell.",
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "fibonacci", "memoization", "bottom-up"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        n: int = max(5, min(params.inputs.get("n", 10), 20))
        # 1-row table: size n+1, all None initially
        table: Tuple[Tuple[Optional[int], ...], ...] = (tuple(None for _ in range(n + 1)),)
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Build fib[0..{n}] bottom-up",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        n = len(initial_state.table[0]) - 1
        row: List[Optional[int]] = [None] * (n + 1)
        computed: set = set()

        # Base cases
        for base_i, base_val in [(0, 0), (1, 1)]:
            if base_i > n:
                break
            row[base_i] = base_val
            computed.add((0, base_i))
            yield DPState(
                table=(tuple(row),),
                current_cell=(0, base_i),
                computed_cells=frozenset(computed),
                description=f"Base case: dp[{base_i}] = {base_val}",
            )

        # Fill
        for i in range(2, n + 1):
            val = row[i - 1] + row[i - 2]  # type: ignore[operator]
            row[i] = val
            computed.add((0, i))
            yield DPState(
                table=(tuple(row),),
                current_cell=(0, i),
                computed_cells=frozenset(computed),
                description=f"dp[{i}] = dp[{i-1}]({row[i-1]}) + dp[{i-2}]({row[i-2]}) = {val}",
            )

        return DPState(
            table=(tuple(row),),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Done — fib({n}) = {row[n]}",
        )
