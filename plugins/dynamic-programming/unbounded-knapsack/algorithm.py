"""Unbounded Knapsack plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Fixed items: (weight, value)
_ITEMS = [(2, 3), (3, 4), (4, 5), (5, 8), (6, 9)]


class UnboundedKnapsackSimulation(AlgorithmPlugin):
    """Unbounded knapsack with unlimited item copies."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="unbounded-knapsack",
            name="Unbounded Knapsack",
            category="dynamic-programming",
            visualization_type="ARRAY_BARS",
            description="Maximize value with unlimited copies of each item using 1D DP.",
            intuition=(
                "dp[w] = best value using exactly w capacity. "
                "For each item: for each capacity, try adding this item again. "
                "Scan forward (not backward) — allows multiple copies."
            ),
            complexity_time_best="O(n·W)",
            complexity_time_average="O(n·W)",
            complexity_time_worst="O(n·W)",
            complexity_space="O(W)",
            tags=("dynamic-programming", "knapsack", "unbounded", "optimization"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        W = int(params.inputs.get("size", 15))
        return SortState(
            array=tuple([1] * (W + 1)),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([0]),
            comparisons=0,
            swaps=0,
            description=f"UbKnapsack W={W} items={_ITEMS}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        W = int(re.search(r"W=(\d+)", initial_state.description).group(1))
        dp = [0] * (W + 1)

        for item_idx, (w_i, v_i) in enumerate(_ITEMS):
            for w in range(w_i, W + 1):
                if dp[w - w_i] + v_i > dp[w]:
                    dp[w] = dp[w - w_i] + v_i

            mx = max(dp) or 1
            arr = tuple(max(1, min(99, dp[w] * 99 // mx)) for w in range(W + 1))
            improved = frozenset(w for w in range(W + 1) if dp[w] > 0)
            yield SortState(
                array=arr,
                comparing=(item_idx, item_idx),
                last_swap=None,
                sorted_indices=improved,
                comparisons=(item_idx + 1) * W,
                swaps=dp[W],
                description=(
                    f"Item {item_idx + 1}/{len(_ITEMS)} (w={w_i}, v={v_i}): "
                    f"dp[{W}]={dp[W]}"
                ),
            )

        mx = max(dp) or 1
        arr = tuple(max(1, min(99, dp[w] * 99 // mx)) for w in range(W + 1))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(W + 1)),
            comparisons=len(_ITEMS) * W,
            swaps=dp[W],
            description=f"Max value for W={W}: {dp[W]}",
        )
