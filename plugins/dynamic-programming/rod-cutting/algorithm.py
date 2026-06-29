"""Rod Cutting DP plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class RodCuttingSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="rod-cutting",
            name="Rod Cutting",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Find the maximum revenue from cutting a rod into pieces using DP.",
            intuition="dp[i] = max revenue for rod length i. For each i, try every cut j: dp[i] = max(price[j] + dp[i-j]). Build bottom-up.",
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "rod-cutting", "optimization", "classic"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 7), 10))
        # Prices for lengths 1..n (index 0 = length 1)
        prices = [rng.randint(1, n * 2) for _ in range(n)]
        dp = [0] * (n + 1)

        prices_str = ",".join(str(p) for p in prices)
        # 2-row table: row 0 = prices (index 0 unused, prices[j-1] for length j)
        # row 1 = dp values dp[0..n]
        row0 = tuple([0] + prices)   # row0[j] = price of length j
        row1 = tuple(dp)
        return DPState(
            table=(row0, row1),
            current_cell=None,
            computed_cells=frozenset({(1, 0)}),
            description=f"prices={prices_str}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        prices_str = initial_state.description.split("prices=")[1]
        prices = [int(x) for x in prices_str.split(",")]
        n = len(prices)

        dp = [0] * (n + 1)
        row0 = initial_state.table[0]
        computed: set = {(1, 0)}

        def make_table():
            return (row0, tuple(dp))

        for i in range(1, n + 1):
            for j in range(1, i + 1):
                candidate = prices[j - 1] + dp[i - j]
                yield DPState(
                    table=make_table(),
                    current_cell=(1, i),
                    computed_cells=frozenset(computed),
                    description=f"dp[{i}]: try cut j={j}, price[{j}]={prices[j-1]}+dp[{i-j}]={dp[i-j]}={candidate}",
                )
                if candidate > dp[i]:
                    dp[i] = candidate
            computed.add((1, i))
            yield DPState(
                table=make_table(),
                current_cell=(1, i),
                computed_cells=frozenset(computed),
                description=f"dp[{i}] = {dp[i]} (best revenue for length {i})",
            )

        return DPState(
            table=make_table(),
            current_cell=None,
            computed_cells=frozenset((1, i) for i in range(n + 1)),
            description=f"Max revenue for rod length {n} = {dp[n]}",
        )
