"""Cocktail Shaker Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class CocktailSortSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="cocktail-sort",
            name="Cocktail Shaker Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description=(
                "Bidirectional bubble sort: alternating forward and backward passes "
                "to move large elements right and small elements left."
            ),
            intuition=(
                "Forward pass: bubble the maximum to the right end. "
                "Backward pass: bubble the minimum to the left end. "
                "The sorted region shrinks from both ends simultaneously."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("sorting", "comparison", "in-place", "cocktail", "bidirectional"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 10))
        arr = rng.sample(range(1, n + 1), n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Initial array, size {n}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        comparisons = swaps = 0
        sorted_indices: set = set()
        lo, hi = 0, n - 1

        while lo < hi:
            swapped = False
            # Forward pass
            for i in range(lo, hi):
                comparisons += 1
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swaps += 1
                    swapped = True
                    yield SortState(
                        array=tuple(arr),
                        comparing=(i, i + 1),
                        last_swap=(i, i + 1),
                        sorted_indices=frozenset(sorted_indices),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Forward: swap arr[{i}]↔arr[{i+1}]",
                    )
                else:
                    yield SortState(
                        array=tuple(arr),
                        comparing=(i, i + 1),
                        last_swap=None,
                        sorted_indices=frozenset(sorted_indices),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Forward: arr[{i}]≤arr[{i+1}], no swap",
                    )
            sorted_indices.add(hi)
            hi -= 1
            if not swapped:
                break

            # Backward pass
            for i in range(hi, lo, -1):
                comparisons += 1
                if arr[i] < arr[i - 1]:
                    arr[i], arr[i - 1] = arr[i - 1], arr[i]
                    swaps += 1
                    swapped = True
                    yield SortState(
                        array=tuple(arr),
                        comparing=(i - 1, i),
                        last_swap=(i - 1, i),
                        sorted_indices=frozenset(sorted_indices),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Backward: swap arr[{i-1}]↔arr[{i}]",
                    )
                else:
                    yield SortState(
                        array=tuple(arr),
                        comparing=(i - 1, i),
                        last_swap=None,
                        sorted_indices=frozenset(sorted_indices),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Backward: arr[{i-1}]≤arr[{i}], no swap",
                    )
            sorted_indices.add(lo)
            lo += 1
            if not swapped:
                break

        for i in range(n):
            sorted_indices.add(i)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(sorted_indices),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted — {comparisons} comparisons, {swaps} swaps",
        )
