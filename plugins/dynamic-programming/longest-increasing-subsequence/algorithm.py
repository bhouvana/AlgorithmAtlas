"""Longest Increasing Subsequence DP plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class LISSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="longest-increasing-subsequence",
            name="Longest Increasing Subsequence",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Find the length of the longest strictly increasing subsequence using O(n²) DP.",
            intuition="For each element i, dp[i] = 1 + max(dp[j]) for all j < i where arr[j] < arr[i]. The answer is the maximum dp value.",
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "lis", "subsequence", "classic"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("array_size", 8), 12))
        arr = [rng.randint(1, n * 2) for _ in range(n)]
        dp = [1] * n  # each element alone is a subsequence of length 1

        # DPState: 2-row table — row 0 = input array, row 1 = dp values
        table = (tuple(arr), tuple(dp))
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"LIS: arr={arr}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        arr = list(initial_state.table[0])
        n = len(arr)
        dp = [1] * n
        computed: set = set()

        for i in range(1, n):
            for j in range(i):
                if arr[j] < arr[i]:
                    yield DPState(
                        table=(tuple(arr), tuple(dp)),
                        current_cell=(1, i),
                        computed_cells=frozenset(computed),
                        description=f"arr[{j}]={arr[j]} < arr[{i}]={arr[i]}: try dp[{i}] = max({dp[i]}, dp[{j}]+1={dp[j]+1})",
                    )
                    if dp[j] + 1 > dp[i]:
                        dp[i] = dp[j] + 1
                else:
                    yield DPState(
                        table=(tuple(arr), tuple(dp)),
                        current_cell=(1, i),
                        computed_cells=frozenset(computed),
                        description=f"arr[{j}]={arr[j]} >= arr[{i}]={arr[i]}: skip",
                    )

            computed.add((1, i))
            yield DPState(
                table=(tuple(arr), tuple(dp)),
                current_cell=(1, i),
                computed_cells=frozenset(computed),
                description=f"dp[{i}] = {dp[i]} (LIS ending at index {i})",
            )

        lis_len = max(dp)
        lis_end = dp.index(lis_len)
        return DPState(
            table=(tuple(arr), tuple(dp)),
            current_cell=None,
            computed_cells=frozenset((1, j) for j in range(n)),
            description=f"LIS length = {lis_len} (ending at index {lis_end})",
        )
