"""Merge Sort plugin for Algorithm Atlas."""
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


class MergeSortSimulation(AlgorithmPlugin):
    """
    Merge Sort — iterative bottom-up, O(n log n) guaranteed, stable.

    The merge step highlights the two source pointers as 'comparing' and
    the write position as 'auxiliary'.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="merge-sort",
            name="Merge Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Divide-and-conquer: split, sort each half, merge back together.",
            intuition="Split a deck into two sorted halves, then carefully interleave them into one.",
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("comparison", "divide-and-conquer", "stable", "iterative"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 16)
        arr: List[int] = [rng.randint(1, size * 2) for _ in range(size)]
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
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

        width = 1
        while width < n:
            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(),
                auxiliary_indices=frozenset(),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Merging runs of width {width}",
            )

            for left in range(0, n, width * 2):
                mid = min(left + width, n)
                right = min(left + width * 2, n)
                if mid >= right:
                    continue

                left_half = arr[left:mid]
                right_half = arr[mid:right]
                i = j = 0
                k = left

                while i < len(left_half) and j < len(right_half):
                    li = left + i
                    rj = mid + j
                    comparisons += 1
                    yield SortState(
                        array=tuple(arr),
                        comparing=(li, rj),
                        last_swap=None,
                        sorted_indices=frozenset(),
                        auxiliary_indices=frozenset({k}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=(
                            f"Comparing left[{i}]={left_half[i]} "
                            f"vs right[{j}]={right_half[j]}"
                        ),
                    )
                    if left_half[i] <= right_half[j]:
                        arr[k] = left_half[i]
                        i += 1
                    else:
                        arr[k] = right_half[j]
                        j += 1
                    swaps += 1
                    yield SortState(
                        array=tuple(arr),
                        comparing=None,
                        last_swap=(k, k),
                        sorted_indices=frozenset(),
                        auxiliary_indices=frozenset({k}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Placed {arr[k]} at position {k}",
                    )
                    k += 1

                while i < len(left_half):
                    arr[k] = left_half[i]
                    swaps += 1
                    yield SortState(
                        array=tuple(arr),
                        comparing=None,
                        last_swap=(k, k),
                        sorted_indices=frozenset(),
                        auxiliary_indices=frozenset({k}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Copying remaining left {left_half[i]} to position {k}",
                    )
                    i += 1
                    k += 1

                while j < len(right_half):
                    arr[k] = right_half[j]
                    swaps += 1
                    yield SortState(
                        array=tuple(arr),
                        comparing=None,
                        last_swap=(k, k),
                        sorted_indices=frozenset(),
                        auxiliary_indices=frozenset({k}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Copying remaining right {right_half[j]} to position {k}",
                    )
                    j += 1
                    k += 1

            width *= 2

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            auxiliary_indices=frozenset(),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted! {comparisons} comparisons, {swaps} writes",
        )
