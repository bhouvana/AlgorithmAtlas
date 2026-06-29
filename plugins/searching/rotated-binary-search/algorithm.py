"""Search in Rotated Sorted Array plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _make_rotated(rng: random.Random, n: int):
    """Return a rotated sorted array and a target that may or may not exist."""
    vals = sorted(rng.sample(range(1, n * 5 + 1), n))
    pivot = rng.randint(1, n - 1)
    rotated = vals[pivot:] + vals[:pivot]
    # 70% chance target exists in array
    if rng.random() < 0.7:
        target = rng.choice(rotated)
    else:
        target = rng.randint(1, n * 5 + 1)
        while target in rotated:
            target = rng.randint(1, n * 5 + 1)
    return rotated, target


class RotatedBinarySearchSimulation(AlgorithmPlugin):
    """Binary search in a rotated sorted array."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="rotated-binary-search",
            name="Search in Rotated Sorted Array",
            category="searching",
            visualization_type="ARRAY_BARS",
            description="Binary search on a sorted array that has been rotated at an unknown pivot.",
            intuition=(
                "At each mid, one half is always sorted. Check which half is sorted "
                "and if target lies in that half; narrow search accordingly."
            ),
            complexity_time_best="O(1)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(1)",
            tags=("searching", "binary-search", "rotated-array"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 10))
        arr, target = _make_rotated(rng, n)
        return SortState(
            array=tuple(arr),
            comparing=(0, len(arr) - 1),
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=target,
            description=f"Search {target} in rotated array {arr}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        target = initial_state.swaps
        lo, hi = 0, n - 1
        found_idx = -1
        cmps = 0

        while lo <= hi:
            mid = (lo + hi) // 2
            cmps += 1

            if arr[mid] == target:
                found_idx = mid
                yield SortState(
                    array=tuple(arr),
                    comparing=(lo, hi),
                    last_swap=(mid, mid),
                    sorted_indices=frozenset([mid]),
                    comparisons=cmps,
                    swaps=target,
                    description=f"Found {target} at index {mid}",
                )
                break

            # Determine which half is sorted
            if arr[lo] <= arr[mid]:
                # Left half [lo..mid] is sorted
                if arr[lo] <= target < arr[mid]:
                    yield SortState(
                        array=tuple(arr),
                        comparing=(lo, mid - 1),
                        last_swap=(lo, mid),
                        sorted_indices=frozenset(),
                        comparisons=cmps,
                        swaps=target,
                        description=(
                            f"lo={lo} mid={mid} hi={hi}: left sorted, {target} in [{arr[lo]},{arr[mid]}), search left"
                        ),
                    )
                    hi = mid - 1
                else:
                    yield SortState(
                        array=tuple(arr),
                        comparing=(mid + 1, hi),
                        last_swap=(lo, mid),
                        sorted_indices=frozenset(),
                        comparisons=cmps,
                        swaps=target,
                        description=(
                            f"lo={lo} mid={mid} hi={hi}: left sorted, {target} not in left, search right"
                        ),
                    )
                    lo = mid + 1
            else:
                # Right half [mid..hi] is sorted
                if arr[mid] < target <= arr[hi]:
                    yield SortState(
                        array=tuple(arr),
                        comparing=(mid + 1, hi),
                        last_swap=(mid, hi),
                        sorted_indices=frozenset(),
                        comparisons=cmps,
                        swaps=target,
                        description=(
                            f"lo={lo} mid={mid} hi={hi}: right sorted, {target} in ({arr[mid]},{arr[hi]}], search right"
                        ),
                    )
                    lo = mid + 1
                else:
                    yield SortState(
                        array=tuple(arr),
                        comparing=(lo, mid - 1),
                        last_swap=(mid, hi),
                        sorted_indices=frozenset(),
                        comparisons=cmps,
                        swaps=target,
                        description=(
                            f"lo={lo} mid={mid} hi={hi}: right sorted, {target} not in right, search left"
                        ),
                    )
                    hi = mid - 1

        if found_idx == -1:
            return SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(),
                comparisons=cmps,
                swaps=-1,
                description=f"{target} not found in array",
            )

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([found_idx]),
            comparisons=cmps,
            swaps=found_idx,
            description=f"Found {target} at index {found_idx} in {cmps} comparisons",
        )
