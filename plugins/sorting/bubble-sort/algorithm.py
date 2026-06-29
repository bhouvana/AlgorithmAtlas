"""
Bubble Sort — Algorithm Atlas Plugin

Implementation notes:
- Uses the optimized variant: tracks whether any swap occurred in a pass.
  If no swap happens, the array is already sorted → early termination.
  This gives O(n) best-case on already-sorted input.
- Every comparison and every swap produces a new frame.
- The sorted_indices set grows by one after each complete pass.
- The generator yields the state AFTER each comparison (not after each swap),
  so the educational value of seeing both comparisons and swaps is preserved.
"""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    SimulationParams,
    SortState,
)


class BubbleSortSimulation:
    """
    Instrumented Bubble Sort simulation.

    Generates one SimulationFrame per comparison.
    For swapping comparisons, an additional frame shows the post-swap state.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bubble-sort",
            name="Bubble Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description=(
                "A simple comparison-based sorting algorithm that repeatedly steps through "
                "the list, compares adjacent elements, and swaps them if they are in the "
                "wrong order."
            ),
            intuition=(
                "After each full pass, the largest unsorted element 'bubbles up' to its "
                "final position. The sorted region grows from right to left with each pass."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("sorting", "comparison", "in-place", "stable", "beginner"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> SortState:
        array_size = int(params.inputs.get("array_size", 20))
        input_order = params.inputs.get("input_order", "random")

        rng = random.Random(params.seed)

        if input_order == "random":
            arr = rng.sample(range(1, array_size + 1), array_size)
        elif input_order == "sorted":
            arr = list(range(1, array_size + 1))
        elif input_order == "reverse":
            arr = list(range(array_size, 0, -1))
        elif input_order == "nearly_sorted":
            arr = list(range(1, array_size + 1))
            swaps = max(1, array_size // 10)
            for _ in range(swaps):
                i, j = rng.sample(range(array_size), 2)
                arr[i], arr[j] = arr[j], arr[i]
        else:
            raise ValueError(f"Unknown input_order: '{input_order}'")

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Initial array ({input_order}, size {array_size})",
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

        for pass_num in range(n):
            swapped_this_pass = False
            boundary = n - pass_num - 1  # Last unsorted index in this pass

            for j in range(boundary):
                comparisons += 1
                comparing = (j, j + 1)

                if arr[j] > arr[j + 1]:
                    # Show the comparison highlight before swapping
                    yield SortState(
                        array=tuple(arr),
                        comparing=comparing,
                        last_swap=None,
                        sorted_indices=frozenset(sorted_indices),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Comparing index {j} ({arr[j]}) and {j + 1} ({arr[j + 1]}) — will swap",
                    )

                    # Perform the swap
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swaps += 1
                    swapped_this_pass = True

                    # Show post-swap state
                    yield SortState(
                        array=tuple(arr),
                        comparing=comparing,
                        last_swap=comparing,
                        sorted_indices=frozenset(sorted_indices),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Swapped index {j} and {j + 1} — swap #{swaps}",
                    )
                else:
                    # No swap needed — just show the comparison
                    yield SortState(
                        array=tuple(arr),
                        comparing=comparing,
                        last_swap=None,
                        sorted_indices=frozenset(sorted_indices),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Comparing index {j} ({arr[j]}) and {j + 1} ({arr[j + 1]}) — no swap needed",
                    )

            # After each pass, the element at boundary is in its final position
            sorted_indices.add(boundary)

            if not swapped_this_pass:
                # Early termination: array is sorted
                for k in range(boundary):
                    sorted_indices.add(k)
                break

        # Add any remaining unsorted indices to sorted set
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
