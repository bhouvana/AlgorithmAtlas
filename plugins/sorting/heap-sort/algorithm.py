"""Heap Sort plugin for Algorithm Atlas."""
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


class HeapSortSimulation(AlgorithmPlugin):
    """
    Heap Sort — O(n log n) always, O(1) space.

    Phase 1: Build a max-heap (Floyd's algorithm, O(n)).
    Phase 2: Repeatedly extract the max (root) to the sorted tail.

    The current heap root being sifted down is shown in auxiliary_indices.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="heap-sort",
            name="Heap Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Build a max-heap, then repeatedly extract the maximum to sort.",
            intuition=(
                "Build a tournament bracket, extract the champion to the end, "
                "rebuild, repeat."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(1)",
            tags=("comparison", "in-place", "unstable", "heap"),
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

        def sift_down(root: int, end: int) -> Generator[SortState, None, None]:
            nonlocal comparisons, swaps
            while True:
                largest = root
                left = 2 * root + 1
                right = 2 * root + 2

                if left < end:
                    comparisons += 1
                    yield SortState(
                        array=tuple(arr),
                        comparing=(largest, left),
                        last_swap=None,
                        sorted_indices=frozenset(sorted_indices),
                        auxiliary_indices=frozenset({root}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=(
                            f"Sift down: comparing root arr[{largest}]={arr[largest]} "
                            f"with left child arr[{left}]={arr[left]}"
                        ),
                    )
                    if arr[left] > arr[largest]:
                        largest = left

                if right < end:
                    comparisons += 1
                    yield SortState(
                        array=tuple(arr),
                        comparing=(largest, right),
                        last_swap=None,
                        sorted_indices=frozenset(sorted_indices),
                        auxiliary_indices=frozenset({root}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=(
                            f"Sift down: comparing arr[{largest}]={arr[largest]} "
                            f"with right child arr[{right}]={arr[right]}"
                        ),
                    )
                    if arr[right] > arr[largest]:
                        largest = right

                if largest == root:
                    break

                arr[root], arr[largest] = arr[largest], arr[root]
                swaps += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=(root, largest),
                    sorted_indices=frozenset(sorted_indices),
                    auxiliary_indices=frozenset({largest}),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Swapping arr[{root}]={arr[root]} down to arr[{largest}]",
                )
                root = largest

        yield SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            auxiliary_indices=frozenset(),
            comparisons=comparisons,
            swaps=swaps,
            description="Phase 1: Building max-heap",
        )

        for start in range((n - 2) // 2, -1, -1):
            yield from sift_down(start, n)

        yield SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            auxiliary_indices=frozenset(),
            comparisons=comparisons,
            swaps=swaps,
            description="Max-heap built — Phase 2: extracting elements",
        )

        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]
            swaps += 1
            sorted_indices.add(end)
            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=(0, end),
                sorted_indices=frozenset(sorted_indices),
                auxiliary_indices=frozenset(),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Moved max {arr[end]} to final position {end}",
            )
            yield from sift_down(0, end)

        sorted_indices.add(0)
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
