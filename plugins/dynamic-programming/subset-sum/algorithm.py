"""Subset Sum DP plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class SubsetSumSimulation(AlgorithmPlugin):
    """
    Subset Sum — O(n * W) DP.

    (n+1) × (W+1) boolean table where:
      row 0:   dp[0][j] = 1 if j==0 else 0  (empty set)
      row i:   dp[i][j] = can subset of first i elements sum to j?

    Column indices 0..W are packed in description as:
      "SubsetSum(arr) target=T"
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="subset-sum",
            name="Subset Sum",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description=(
                "Check if any subset of the input sums exactly to the target "
                "using a 2D boolean DP table."
            ),
            intuition=(
                "dp[i][j] = 1 if some subset of elements [0..i-1] sums to j. "
                "Transition: skip element i (take dp[i-1][j]) or include it "
                "(take dp[i-1][j - arr[i-1]] if j >= arr[i-1])."
            ),
            complexity_time_best="O(n×W)",
            complexity_time_average="O(n×W)",
            complexity_time_worst="O(n×W)",
            complexity_space="O(n×W)",
            tags=("dynamic-programming", "subset-sum", "knapsack"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(3, min(params.inputs.get("array_size", 5), 7))
        arr = [rng.randint(1, 8) for _ in range(n)]
        # Target: roughly half the total sum
        total = sum(arr)
        target = max(1, total // 2 + rng.randint(-2, 2))
        target = min(target, total)  # must not exceed total

        W = target
        # Build initial table: all zeros, then set dp[0][0] = 1
        table = []
        row0 = [0] * (W + 1)
        row0[0] = 1  # empty set sums to 0
        table.append(tuple(row0))
        for _ in range(n):
            table.append(tuple(0 for _ in range(W + 1)))

        nums_str = ",".join(str(x) for x in arr)
        return DPState(
            table=tuple(table),
            current_cell=None,
            computed_cells=frozenset({(0, j) for j in range(W + 1)}),
            description=f"SubsetSum([{nums_str}]) target={target}",
        )

    def steps(
        self,
        initial_state: DPState,
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        nums_str = desc[desc.index("[") + 1 : desc.index("]")]
        arr = [int(x) for x in nums_str.split(",")]
        target = int(desc.split("target=")[1])
        n = len(arr)
        W = target

        dp: List[List[int]] = [[0] * (W + 1) for _ in range(n + 1)]
        dp[0][0] = 1

        computed: set = {(0, j) for j in range(W + 1)}

        for i in range(1, n + 1):
            val = arr[i - 1]
            for j in range(W + 1):
                skip = dp[i - 1][j]
                include = dp[i - 1][j - val] if j >= val else 0
                dp[i][j] = 1 if (skip or include) else 0
                computed.add((i, j))

                table = tuple(tuple(row) for row in dp)
                yield DPState(
                    table=table,
                    current_cell=(i, j),
                    computed_cells=frozenset(computed),
                    description=(
                        f"dp[{i}][{j}]: skip={skip}"
                        + (f", include=dp[{i-1}][{j-val}]={include}" if j >= val else "")
                        + f" → {dp[i][j]}"
                    ),
                )

        answer = dp[n][W]
        table = tuple(tuple(row) for row in dp)
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(computed),
            description=(
                f"Done: subset summing to {target} "
                + ("EXISTS" if answer else "does NOT exist")
            ),
        )
