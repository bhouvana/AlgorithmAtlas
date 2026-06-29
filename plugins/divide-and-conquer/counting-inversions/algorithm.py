"""Counting Inversions (modified merge sort) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class CountingInversionsSimulation(AlgorithmPlugin):
    """
    Counting Inversions via modified merge sort — O(n log n).

    SortState encoding:
      array:        current array state
      comparisons:  inversions counted so far
      swaps:        merge operations completed
      sorted_indices: indices that are in their final sorted position
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="counting-inversions",
            name="Counting Inversions",
            category="divide-and-conquer",
            visualization_type="ARRAY_BARS",
            description=(
                "Count pairs (i,j) with i<j but arr[i]>arr[j] — the measure "
                "of how 'unsorted' an array is — using modified merge sort."
            ),
            intuition=(
                "During merge, when right[j] < left[i], all remaining left elements "
                "form inversions with right[j]. Count these and add to total. "
                "Total inversions = sum across all merges."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("divide-and-conquer", "merge-sort", "inversions", "counting"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("array_size", 8), 12))
        arr = rng.sample(range(1, n + 1), n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Count inversions in {list(arr)}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        frames = []
        total_inversions = [0]
        sorted_indices: set = set()

        def merge_sort(sub: List[int], offset: int) -> List[int]:
            if len(sub) <= 1:
                sorted_indices.add(offset)
                return sub
            mid = len(sub) // 2
            left = merge_sort(sub[:mid], offset)
            right = merge_sort(sub[mid:], offset + mid)
            # Merge and count
            merged = []
            i = j = 0
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    merged.append(left[i])
                    i += 1
                else:
                    # All remaining left elements are inversions with right[j]
                    total_inversions[0] += len(left) - i
                    merged.append(right[j])
                    j += 1
            merged.extend(left[i:])
            merged.extend(right[j:])
            # Update arr at this offset
            for k, val in enumerate(merged):
                arr[offset + k] = val
                sorted_indices.add(offset + k)
            frames.append((list(arr), total_inversions[0], offset, offset + len(sub) - 1))
            return merged

        merge_sort(arr, 0)

        for arr_snap, inv_count, lo, hi in frames:
            yield SortState(
                array=tuple(arr_snap),
                comparing=(lo, hi),
                last_swap=None,
                sorted_indices=frozenset(sorted_indices),
                comparisons=inv_count,
                swaps=1,
                description=f"Merge [{lo},{hi}]: inversions so far = {inv_count}",
            )

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=total_inversions[0],
            swaps=n,
            description=f"Total inversions = {total_inversions[0]}",
        )
