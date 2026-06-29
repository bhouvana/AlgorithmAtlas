"""Maximum Subarray (Kadane's Algorithm) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class MaxSubarraySimulation(AlgorithmPlugin):
    """
    Kadane's algorithm — O(n).

    2-row DPState table:
      row 0: input array (may include negatives)
      row 1: dp[i] = maximum subarray sum ending at index i

    dp[i] = max(arr[i], dp[i-1] + arr[i])
    Answer = max(dp)
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="maximum-subarray",
            name="Maximum Subarray (Kadane's)",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description=(
                "Find the contiguous subarray with the largest sum "
                "in O(n) time using Kadane's algorithm."
            ),
            intuition=(
                "At each index, decide whether to extend the current subarray "
                "or start a new one. dp[i] = max(arr[i], dp[i-1] + arr[i])."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "kadane", "maximum-subarray", "greedy"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("array_size", 10), 15))
        # Mix of negatives and positives to make it interesting
        arr = [rng.randint(-5, 10) for _ in range(n)]
        # Ensure at least one positive
        if all(v <= 0 for v in arr):
            arr[rng.randint(0, n - 1)] = rng.randint(1, 8)

        table = (
            tuple(arr),
            tuple(0 for _ in range(n)),
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Kadane's: n={n}, find max contiguous subarray sum",
        )

    def steps(
        self,
        initial_state: DPState,
    ) -> Generator[DPState, None, DPState]:
        arr = list(initial_state.table[0])
        n = len(arr)
        dp = [0] * n
        dp[0] = arr[0]
        computed: set = {(1, 0)}
        best = dp[0]
        best_end = 0

        table = (tuple(arr), tuple(dp))
        yield DPState(
            table=table,
            current_cell=(1, 0),
            computed_cells=frozenset(computed),
            description=f"dp[0] = arr[0] = {arr[0]} (base case)",
        )

        for i in range(1, n):
            extend = dp[i - 1] + arr[i]
            restart = arr[i]
            dp[i] = max(extend, restart)
            computed.add((1, i))
            table = (tuple(arr), tuple(dp))

            if dp[i] > best:
                best = dp[i]
                best_end = i

            choice = "extend" if extend >= restart else "restart"
            yield DPState(
                table=table,
                current_cell=(1, i),
                computed_cells=frozenset(computed),
                description=(
                    f"dp[{i}] = max({dp[i-1]}+{arr[i]}, {arr[i]}) = max({extend},{restart}) = {dp[i]} ({choice})"
                ),
            )

        best_sum = max(dp)
        # Find best subarray bounds
        best_end_idx = dp.index(best_sum)
        cur = 0
        best_start_idx = best_end_idx
        for i in range(best_end_idx + 1):
            cur = max(arr[i], cur + arr[i])
            if cur == best_sum and i == best_end_idx:
                j = i
                total = 0
                while j >= 0 and total + arr[j] <= best_sum:
                    total += arr[j]
                    if total == best_sum:
                        best_start_idx = j
                        break
                    j -= 1
                break

        return DPState(
            table=(tuple(arr), tuple(dp)),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Done: max subarray sum = {best_sum}",
        )
