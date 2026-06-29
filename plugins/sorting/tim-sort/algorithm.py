"""Tim Sort plugin for Algorithm Atlas."""
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

MIN_MERGE = 32


class TimSortSimulation(AlgorithmPlugin):
    """
    Tim Sort — hybrid Insertion Sort + Merge Sort, O(n log n) worst, O(n) best.

    Phase 1: Divide array into runs of size MIN_MERGE; sort each with Insertion Sort.
    Phase 2: Merge adjacent runs with standard merge.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="tim-sort",
            name="Tim Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Hybrid Insertion Sort + Merge Sort as used in Python and Java standard libraries.",
            intuition=(
                "Find naturally-ordered runs, extend short ones with insertion sort, "
                "then merge all runs with merge sort."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("comparison", "stable", "hybrid", "adaptive", "real-world"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 32)
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

        run_size = min(MIN_MERGE, n)
        run_starts = list(range(0, n, run_size))

        run_boundary_set = frozenset(run_starts[1:])
        yield SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            auxiliary_indices=run_boundary_set,
            comparisons=comparisons,
            swaps=swaps,
            description=f"Phase 1: sorting {len(run_starts)} runs of size ≤{run_size}",
        )

        sorted_run_indices: set[int] = set()
        for run_idx, left in enumerate(run_starts):
            right = min(left + run_size, n)

            for i in range(left + 1, right):
                key = arr[i]
                j = i
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=None,
                    sorted_indices=frozenset(sorted_run_indices),
                    auxiliary_indices=frozenset({i}),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Run {run_idx + 1}: inserting arr[{i}]={key}",
                )
                while j > left:
                    comparisons += 1
                    yield SortState(
                        array=tuple(arr),
                        comparing=(j - 1, j),
                        last_swap=None,
                        sorted_indices=frozenset(sorted_run_indices),
                        auxiliary_indices=frozenset({j}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Run {run_idx + 1}: arr[{j - 1}]={arr[j - 1]} > {key}?",
                    )
                    if arr[j - 1] <= key:
                        break
                    arr[j] = arr[j - 1]
                    swaps += 1
                    yield SortState(
                        array=tuple(arr),
                        comparing=None,
                        last_swap=(j - 1, j),
                        sorted_indices=frozenset(sorted_run_indices),
                        auxiliary_indices=frozenset({j - 1}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Run {run_idx + 1}: shifting {arr[j]} right",
                    )
                    j -= 1
                arr[j] = key

            sorted_run_indices.update(range(left, right))

        yield SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(sorted_run_indices),
            auxiliary_indices=frozenset(),
            comparisons=comparisons,
            swaps=swaps,
            description="Phase 2: merging runs",
        )

        width = run_size
        while width < n:
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
                        description=f"Merge: left[{i}]={left_half[i]} vs right[{j}]={right_half[j]}",
                    )
                    if left_half[i] <= right_half[j]:
                        arr[k] = left_half[i]
                        i += 1
                    else:
                        arr[k] = right_half[j]
                        j += 1
                    swaps += 1
                    k += 1

                while i < len(left_half):
                    arr[k] = left_half[i]
                    swaps += 1
                    k += 1
                    i += 1

                while j < len(right_half):
                    arr[k] = right_half[j]
                    swaps += 1
                    k += 1
                    j += 1

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
