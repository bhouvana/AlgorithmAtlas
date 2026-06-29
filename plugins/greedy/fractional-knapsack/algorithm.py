"""Fractional Knapsack greedy plugin for Algorithm Atlas.

Array holds item values (sorted by value/weight ratio descending).
Bar heights = value. sorted_indices = fully taken items.
comparing = item currently being considered.
swaps = total value accumulated (stored as int * 10 for display).
"""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class FractionalKnapsackSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="fractional-knapsack",
            name="Fractional Knapsack",
            category="greedy",
            visualization_type="ARRAY_BARS",
            description="Maximize value in a knapsack by taking fractions of items sorted by value/weight ratio.",
            intuition="Sort items by value-per-unit-weight descending. Greedily take as much of the best-ratio item as the remaining capacity allows.",
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(1)",
            tags=("greedy", "fractional-knapsack", "optimization", "ratio"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 6), 10))
        weights = [rng.randint(2, 10) for _ in range(n)]
        values = [rng.randint(5, 30) for _ in range(n)]
        capacity = sum(weights) * 2 // 3  # take about 2/3 of total weight

        # Sort by ratio descending
        items = sorted(zip(weights, values), key=lambda x: x[1] / x[0], reverse=True)
        weights_s = [w for w, _ in items]
        values_s = [v for _, v in items]

        w_str = ",".join(str(w) for w in weights_s)
        cap_str = str(capacity)
        return SortState(
            array=tuple(values_s),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"weights={w_str} capacity={cap_str}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        values = list(initial_state.array)
        n = len(values)
        desc = initial_state.description
        w_part, cap_part = desc.split(" capacity=")
        weights = [int(x) for x in w_part.split("weights=")[1].split(",")]
        capacity = int(cap_part)

        remaining = float(capacity)
        total_value = 0.0
        fully_taken: List[int] = []
        comparisons = 0

        yield SortState(
            array=tuple(values),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Capacity={capacity}, items sorted by v/w ratio descending",
        )

        for i in range(n):
            if remaining <= 0:
                break
            comparisons += 1
            w = weights[i]
            v = values[i]
            ratio = v / w

            yield SortState(
                array=tuple(values),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(fully_taken),
                comparisons=comparisons,
                swaps=int(total_value * 10),
                description=f"Item {i}: v={v}, w={w}, ratio={ratio:.2f}, remaining={remaining:.1f}",
            )

            if w <= remaining:
                # Take whole item
                remaining -= w
                total_value += v
                fully_taken.append(i)
                yield SortState(
                    array=tuple(values),
                    comparing=None,
                    last_swap=(i, i),
                    sorted_indices=frozenset(fully_taken),
                    comparisons=comparisons,
                    swaps=int(total_value * 10),
                    description=f"Take all of item {i} (w={w}): total_value={total_value:.1f}, remaining={remaining:.1f}",
                )
            else:
                # Take fraction
                fraction = remaining / w
                partial_value = v * fraction
                total_value += partial_value
                yield SortState(
                    array=tuple(values),
                    comparing=None,
                    last_swap=(i, i),
                    sorted_indices=frozenset(fully_taken),
                    comparisons=comparisons,
                    swaps=int(total_value * 10),
                    description=f"Take {fraction:.2f} of item {i}: +{partial_value:.1f} value — knapsack full",
                )
                remaining = 0

        return SortState(
            array=tuple(values),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(fully_taken))),
            comparisons=comparisons,
            swaps=int(total_value * 10),
            description=f"Done — max value={total_value:.2f} with capacity={capacity}",
        )
