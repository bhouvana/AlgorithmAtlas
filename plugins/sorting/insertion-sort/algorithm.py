"""Insertion Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    SimulationParams,
    SortState,
)


class InsertionSortSimulation(AlgorithmPlugin):
    """
    Insertion Sort — O(n²) worst, O(n) best (already sorted).

    Builds the sorted prefix one element at a time. Each new element is
    shifted leftward until it reaches its correct position. The element
    being inserted is tracked in auxiliary_indices (yellow).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="insertion-sort",
            name="Insertion Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Builds the sorted array by inserting each element into its correct position.",
            intuition="Pick up each card, slide it into the right spot among your already-sorted hand.",
            complexity_time_best="O(n)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("comparison", "in-place", "stable", "adaptive", "online"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 20)
        arr: List[int] = [rng.randint(1, size * 2) for _ in range(size)]
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset({0}),
            auxiliary_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description="Ready to sort",
        )

    def steps(
        self,
        initial_state: SortState,
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        comparisons = 0
        swaps = 0
        sorted_prefix: set[int] = {0}

        for i in range(1, n):
            key = arr[i]
            j = i

            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(sorted_prefix),
                auxiliary_indices=frozenset({i}),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Inserting arr[{i}]={key} into sorted prefix",
            )

            while j > 0:
                comparisons += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=(j - 1, j),
                    last_swap=None,
                    sorted_indices=frozenset(sorted_prefix),
                    auxiliary_indices=frozenset({j}),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Comparing arr[{j - 1}]={arr[j - 1]} > {key}?",
                )
                if arr[j - 1] <= key:
                    break
                arr[j] = arr[j - 1]
                swaps += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=(j - 1, j),
                    sorted_indices=frozenset(sorted_prefix),
                    auxiliary_indices=frozenset({j - 1}),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Shifting arr[{j - 1}]={arr[j]} right",
                )
                j -= 1

            arr[j] = key
            sorted_prefix = set(range(i + 1))
            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(sorted_prefix),
                auxiliary_indices=frozenset(),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Placed {key} at index {j}; sorted prefix is now [0..{i}]",
            )

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            auxiliary_indices=frozenset(),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted! {comparisons} comparisons, {swaps} shifts",
        )
