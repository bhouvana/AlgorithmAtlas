"""Selection Sort plugin for Algorithm Atlas."""
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


class SelectionSortSimulation(AlgorithmPlugin):
    """
    Selection Sort — O(n²) comparisons always, O(n) swaps always.

    Each pass through the unsorted region finds the minimum element and
    swaps it into its final position. auxiliary_indices tracks the running
    minimum index so the renderer shows the current tracked minimum (yellow).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="selection-sort",
            name="Selection Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Repeatedly selects the minimum from the unsorted portion.",
            intuition=(
                "Scan the rest of the pile, find the smallest card, "
                "pull it to the front — repeat."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("comparison", "in-place", "unstable", "quadratic"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 20)
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
        sorted_indices: set[int] = set()

        for i in range(n - 1):
            min_idx = i

            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(sorted_indices),
                auxiliary_indices=frozenset({min_idx}),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Pass {i + 1}: scanning for minimum starting at index {i}",
            )

            for j in range(i + 1, n):
                comparisons += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=(min_idx, j),
                    last_swap=None,
                    sorted_indices=frozenset(sorted_indices),
                    auxiliary_indices=frozenset({min_idx}),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Comparing arr[{j}]={arr[j]} with current min arr[{min_idx}]={arr[min_idx]}",
                )
                if arr[j] < arr[min_idx]:
                    min_idx = j
                    yield SortState(
                        array=tuple(arr),
                        comparing=None,
                        last_swap=None,
                        sorted_indices=frozenset(sorted_indices),
                        auxiliary_indices=frozenset({min_idx}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"New minimum found: arr[{min_idx}]={arr[min_idx]}",
                    )

            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                swaps += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=(i, min_idx),
                    sorted_indices=frozenset(sorted_indices),
                    auxiliary_indices=frozenset(),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Swapping minimum {arr[i]} into position {i}",
                )
            else:
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=None,
                    sorted_indices=frozenset(sorted_indices),
                    auxiliary_indices=frozenset(),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Element {arr[i]} already in correct position {i}",
                )

            sorted_indices.add(i)

        sorted_indices.add(n - 1)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(sorted_indices),
            auxiliary_indices=frozenset(),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted! {comparisons} comparisons, {swaps} swaps",
        )
