"""Staircase (Climbing Stairs) DP plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class StaircaseSimulation(AlgorithmPlugin):
    """
    Staircase problem — count ways to reach the top taking 1 or 2 steps.

    2-row DPState table:
      row 0: stair index [0, 1, 2, ..., n]
      row 1: dp[i] = number of ways to reach stair i

    Base: dp[0] = 1 (one way to stand at ground), dp[1] = 1
    Recurrence: dp[i] = dp[i-1] + dp[i-2]
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="staircase",
            name="Staircase",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description=(
                "Count distinct ways to climb n stairs taking 1 or 2 steps at a time. "
                "Answer equals the (n+1)th Fibonacci number."
            ),
            intuition=(
                "Each stair i is reachable from stair i-1 (one step) or i-2 (two steps). "
                "So dp[i] = dp[i-1] + dp[i-2], giving Fibonacci-like growth."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "fibonacci", "staircase", "combinatorics"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        n: int = max(4, min(params.inputs.get("array_size", 10), 15))
        table = (
            tuple(range(n + 1)),  # row 0: stair indices
            tuple(0 for _ in range(n + 1)),  # row 1: dp values (all 0 initially)
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Staircase: n={n} stairs. dp[0]=1, dp[1]=1, dp[i]=dp[i-1]+dp[i-2]",
        )

    def steps(
        self,
        initial_state: DPState,
    ) -> Generator[DPState, None, DPState]:
        n = len(initial_state.table[0]) - 1
        dp = [0] * (n + 1)
        dp[0] = 1
        dp[1] = 1 if n >= 1 else 0

        computed: set = set()

        # Base cases
        table = (tuple(range(n + 1)), tuple(dp))
        computed.add((1, 0))
        if n >= 1:
            computed.add((1, 1))

        yield DPState(
            table=table,
            current_cell=(1, 1) if n >= 1 else (1, 0),
            computed_cells=frozenset(computed),
            description=f"Base: dp[0]=1 (empty staircase), dp[1]=1 (one way to reach stair 1)",
        )

        for i in range(2, n + 1):
            dp[i] = dp[i - 1] + dp[i - 2]
            computed.add((1, i))
            table = (tuple(range(n + 1)), tuple(dp))

            yield DPState(
                table=table,
                current_cell=(1, i),
                computed_cells=frozenset(computed),
                    description=(
                    f"dp[{i}] = dp[{i-1}] + dp[{i-2}] = {dp[i-1]} + {dp[i-2]} = {dp[i]}"
                ),
            )

        final_table = (tuple(range(n + 1)), tuple(dp))
        return DPState(
            table=final_table,
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Done: {dp[n]} ways to climb {n} stairs",
        )
