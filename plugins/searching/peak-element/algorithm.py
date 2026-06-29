"""Find Peak Element plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _make_array(rng: random.Random, n: int) -> list[int]:
    """Generate array with at least one peak."""
    arr = [rng.randint(1, 50) for _ in range(n)]
    # Ensure not monotone
    arr[n // 2] = max(arr) + 5
    return arr


class PeakElementSimulation(AlgorithmPlugin):
    """Find Peak Element via Binary Search."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="peak-element",
            name="Find Peak Element",
            category="searching",
            visualization_type="ARRAY_BARS",
            description="Find any peak element (larger than neighbors) in O(log n) with binary search.",
            intuition=(
                "If arr[mid] < arr[mid+1], right half must have a peak. "
                "If arr[mid] < arr[mid-1], left half must. Otherwise arr[mid] is peak."
            ),
            complexity_time_best="O(1)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(1)",
            tags=("searching", "peak-element", "binary-search"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 8))
        arr = _make_array(rng, n)
        return SortState(
            array=tuple(arr),
            comparing=(0, n - 1),
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=-1,
            description=f"Find peak in {arr}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        lo, hi = 0, n - 1
        found_idx = -1

        while lo <= hi:
            mid = (lo + hi) // 2
            is_left_larger = mid > 0 and arr[mid - 1] > arr[mid]
            is_right_larger = mid < n - 1 and arr[mid + 1] > arr[mid]

            yield SortState(
                array=tuple(arr),
                comparing=(lo, hi),
                last_swap=(mid, mid),
                sorted_indices=frozenset(),
                comparisons=mid,
                swaps=-1,
                description=(
                    f"lo={lo} hi={hi} mid={mid} arr[mid]={arr[mid]} "
                    f"{'→right' if is_right_larger else '←left' if is_left_larger else 'PEAK!'}"
                ),
            )

            if is_right_larger:
                lo = mid + 1
            elif is_left_larger:
                hi = mid - 1
            else:
                found_idx = mid
                break

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([found_idx]),
            comparisons=found_idx,
            swaps=found_idx,
            description=f"Peak found at index {found_idx} value={arr[found_idx]}",
        )
