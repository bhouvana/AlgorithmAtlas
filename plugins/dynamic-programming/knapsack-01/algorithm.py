"""0/1 Knapsack DP plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


def _random_items(rng: random.Random, n: int, capacity: int):
    """Generate n items as (weight, value) pairs."""
    items = []
    for _ in range(n):
        w = rng.randint(1, max(2, capacity // 2))
        v = rng.randint(1, 10)
        items.append((w, v))
    return items


class Knapsack01Simulation(AlgorithmPlugin):
    """
    0/1 Knapsack — O(n·W).

    dp[i][w] = max value using items 0..i-1 with capacity w.
    Row labels: [ε, item1, item2, ...]
    Col labels: [0, 1, 2, ..., W]
    Table: (n+1) × (W+1), rows = items (0 = no items), cols = capacity.
    description encodes items as "w1:v1,w2:v2,..."
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="knapsack-01",
            name="0/1 Knapsack",
            category="dynamic-programming",
            visualization_type="MATRIX",
            description="Maximize value of selected items without exceeding weight capacity.",
            intuition="dp[i][w] = max value with first i items, capacity w. Either skip item i (same as dp[i-1][w]) or include it (dp[i-1][w-wi] + vi) if it fits.",
            complexity_time_best="O(n·W)",
            complexity_time_average="O(n·W)",
            complexity_time_worst="O(n·W)",
            complexity_space="O(n·W)",
            tags=("dynamic-programming", "optimization", "knapsack", "combinatorics"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(3, min(params.inputs.get("item_count", 4), 6))
        W: int = max(6, min(params.inputs.get("capacity", 8), 12))
        items = _random_items(rng, n, W)
        table = tuple(tuple(0 for _ in range(W + 1)) for _ in range(n + 1))
        items_str = ",".join(f"{w}:{v}" for w, v in items)
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset((0, w) for w in range(W + 1)),
            description=f"Knapsack: n={n} W={W} items={items_str}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        n = len(initial_state.table) - 1
        W = len(initial_state.table[0]) - 1
        # Parse items from description
        items_str = initial_state.description.split("items=")[1]
        items: List[Tuple[int, int]] = []
        for pair in items_str.split(","):
            wi, vi = pair.split(":")
            items.append((int(wi), int(vi)))

        dp: List[List[int]] = [[0] * (W + 1) for _ in range(n + 1)]
        computed: set = set((0, w) for w in range(W + 1))

        for i in range(1, n + 1):
            wi, vi = items[i - 1]
            for w in range(W + 1):
                if wi <= w and dp[i - 1][w - wi] + vi > dp[i - 1][w]:
                    dp[i][w] = dp[i - 1][w - wi] + vi
                    action = f"include item {i}(w={wi},v={vi}): {dp[i-1][w-wi]}+{vi}={dp[i][w]}"
                else:
                    dp[i][w] = dp[i - 1][w]
                    action = f"skip item {i}(w={wi},v={vi}): keep {dp[i][w]}"
                computed.add((i, w))
                yield DPState(
                    table=tuple(tuple(r) for r in dp),
                    current_cell=(i, w),
                    computed_cells=frozenset(computed),
                    description=f"dp[{i}][{w}]: {action}",
                )

        max_val = dp[n][W]
        return DPState(
            table=tuple(tuple(r) for r in dp),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Max value = {max_val} (capacity {W}, {n} items)",
        )
