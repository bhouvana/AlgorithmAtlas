"""Pancake Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _flip(arr: list, k: int) -> list:
    """Reverse arr[0..k] in place. Returns arr."""
    arr[:k+1] = arr[:k+1][::-1]
    return arr


class PancakeSortSimulation(AlgorithmPlugin):
    """Pancake Sort."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="pancake-sort",
            name="Pancake Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Sort by flipping prefixes. Each element placed by at most 2 flips.",
            intuition=(
                "For size n down to 2: find max in arr[0..size-1], "
                "flip it to index 0 (if not already there), "
                "then flip it to index size-1."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("sorting", "pancake", "prefix-reversal"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 7))
        arr = rng.sample(range(1, n * 3 + 1), n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Pancake sort {arr}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        comparisons = 0
        swaps = 0
        sorted_indices: set[int] = set()

        for size in range(n, 1, -1):
            # Find max index in arr[0..size-1]
            max_idx = 0
            for i in range(1, size):
                comparisons += 1
                if arr[i] > arr[max_idx]:
                    max_idx = i

            if max_idx == size - 1:
                # Already in place
                sorted_indices.add(size - 1)
                yield SortState(
                    array=tuple(arr),
                    comparing=(max_idx, size - 1),
                    last_swap=None,
                    sorted_indices=frozenset(sorted_indices),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Max {arr[max_idx]} already at position {size-1}",
                )
                continue

            if max_idx != 0:
                # Flip max to front
                _flip(arr, max_idx)
                swaps += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=(0, max_idx),
                    sorted_indices=frozenset(sorted_indices),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Flip [0..{max_idx}] to bring max {arr[0]} to front",
                )

            # Flip max from front to position size-1
            _flip(arr, size - 1)
            swaps += 1
            sorted_indices.add(size - 1)
            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=(0, size - 1),
                sorted_indices=frozenset(sorted_indices),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Flip [0..{size-1}] to place max {arr[size-1]} at position {size-1}",
            )

        sorted_indices.add(0)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted in {swaps} flips",
        )
