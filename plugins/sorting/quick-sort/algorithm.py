"""Quick Sort plugin for Algorithm Atlas."""
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


class QuickSortSimulation(AlgorithmPlugin):
    """
    Quick Sort — iterative Lomuto partition scheme with configurable pivot strategy.

    Uses an explicit stack to simulate recursion. The pivot is tracked in
    auxiliary_indices (yellow). Pivot strategy is stored from initialize().
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="quick-sort",
            name="Quick Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Partition around a pivot, recurse on each side.",
            intuition=(
                "Choose a dividing line, push everything smaller left "
                "and larger right, then repeat for each side."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n²)",
            complexity_space="O(log n)",
            tags=("comparison", "divide-and-conquer", "in-place", "unstable"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 16)
        arr: List[int] = [rng.randint(1, size * 2) for _ in range(size)]
        self._pivot_strategy: str = params.inputs.get("pivot_strategy", "median_of_three")
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
        pivot_strategy = getattr(self, "_pivot_strategy", "median_of_three")

        def choose_pivot(lo: int, hi: int) -> int:
            if pivot_strategy == "first":
                return lo
            if pivot_strategy == "median_of_three":
                mid = (lo + hi) // 2
                triple = [(arr[lo], lo), (arr[mid], mid), (arr[hi], hi)]
                triple.sort()
                return triple[1][1]
            return hi  # "last"

        stack: List[tuple[int, int]] = [(0, n - 1)]

        while stack:
            lo, hi = stack.pop()
            if lo >= hi:
                if lo == hi:
                    sorted_indices.add(lo)
                continue

            pivot_idx = choose_pivot(lo, hi)
            if pivot_idx != hi:
                arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
                swaps += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=(pivot_idx, hi),
                    sorted_indices=frozenset(sorted_indices),
                    auxiliary_indices=frozenset({hi}),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Moving pivot {arr[hi]} to end (index {hi})",
                )

            pivot_val = arr[hi]
            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(sorted_indices),
                auxiliary_indices=frozenset({hi}),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Pivot = {pivot_val} at index {hi}; partitioning [{lo}..{hi - 1}]",
            )

            store = lo
            for j in range(lo, hi):
                comparisons += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=(j, hi),
                    last_swap=None,
                    sorted_indices=frozenset(sorted_indices),
                    auxiliary_indices=frozenset({hi, store}),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"arr[{j}]={arr[j]} ≤ pivot {pivot_val}?",
                )
                if arr[j] <= pivot_val:
                    if store != j:
                        arr[store], arr[j] = arr[j], arr[store]
                        swaps += 1
                        yield SortState(
                            array=tuple(arr),
                            comparing=None,
                            last_swap=(store, j),
                            sorted_indices=frozenset(sorted_indices),
                            auxiliary_indices=frozenset({hi, store}),
                            comparisons=comparisons,
                            swaps=swaps,
                            description=f"Swap arr[{store}] and arr[{j}]",
                        )
                    store += 1

            arr[store], arr[hi] = arr[hi], arr[store]
            swaps += 1
            sorted_indices.add(store)
            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=(store, hi),
                sorted_indices=frozenset(sorted_indices),
                auxiliary_indices=frozenset(),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Pivot {pivot_val} is in its final position at index {store}",
            )

            stack.append((lo, store - 1))
            stack.append((store + 1, hi))

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            auxiliary_indices=frozenset(),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted! {comparisons} comparisons, {swaps} swaps",
        )
