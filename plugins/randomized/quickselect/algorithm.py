"""Quickselect (Randomized) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class QuickselectSimulation(AlgorithmPlugin):
    """Randomized Quickselect — find the k-th smallest element."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="quickselect",
            name="Quickselect (Randomized)",
            category="randomized",
            visualization_type="ARRAY_BARS",
            description=(
                "Find the k-th smallest element in O(n) expected time "
                "using randomized partitioning."
            ),
            intuition=(
                "Like quicksort: pick a random pivot and partition. "
                "But only recurse into the side that contains position k. "
                "Expected O(n) since we halve the problem on average."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("randomized", "quickselect", "order-statistics", "selection"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 12))
        arr = [rng.randint(1, 99) for _ in range(n)]
        k = n // 2  # find the median (0-indexed)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=k,
            description=f"Quickselect: find {k}-th smallest (0-indexed), n={n}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        k = initial_state.swaps
        n = len(arr)
        rng = random.Random(hash(tuple(arr)) % (2 ** 31))
        comparisons = 0

        lo, hi = 0, n - 1

        while lo < hi:
            # Choose random pivot, swap to end
            pivot_idx = rng.randint(lo, hi)
            arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
            pivot_val = arr[hi]

            yield SortState(
                array=tuple(arr),
                comparing=(pivot_idx, hi),
                last_swap=(pivot_idx, hi),
                sorted_indices=frozenset(),
                comparisons=comparisons,
                swaps=k,
                description=f"Range [{lo},{hi}]: pivot={pivot_val} moved to end",
            )

            # Lomuto partition
            i = lo - 1
            for j in range(lo, hi):
                comparisons += 1
                if arr[j] <= pivot_val:
                    i += 1
                    if i != j:
                        arr[i], arr[j] = arr[j], arr[i]
            i += 1
            arr[i], arr[hi] = arr[hi], arr[i]
            pivot_pos = i

            direction = (
                "found!"
                if pivot_pos == k
                else ("recurse right" if k > pivot_pos else "recurse left")
            )
            yield SortState(
                array=tuple(arr),
                comparing=(lo, hi),
                last_swap=(pivot_pos, pivot_pos),
                sorted_indices=frozenset([pivot_pos]),
                comparisons=comparisons,
                swaps=k,
                description=(
                    f"Pivot {pivot_val} landed at {pivot_pos} — "
                    f"k={k}: {direction}"
                ),
            )

            if pivot_pos == k:
                break
            elif pivot_pos < k:
                lo = pivot_pos + 1
            else:
                hi = pivot_pos - 1

        found_val = arr[k]
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([k]),
            comparisons=comparisons,
            swaps=found_val,
            description=f"Done: {k}-th smallest = {found_val}",
        )
