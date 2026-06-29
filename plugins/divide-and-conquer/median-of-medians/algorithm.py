"""Median of Medians (Introselect) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_GROUP = 5  # group size


def _insertion_sort_indices(arr, indices):
    """Sort indices by arr[idx] value."""
    idx = list(indices)
    for i in range(1, len(idx)):
        key = idx[i]
        j = i - 1
        while j >= 0 and arr[idx[j]] > arr[key]:
            idx[j + 1] = idx[j]
            j -= 1
        idx[j + 1] = key
    return idx


def _median_index(arr, indices):
    sorted_idx = _insertion_sort_indices(arr, indices)
    return sorted_idx[len(sorted_idx) // 2]


class MedianOfMediansSimulation(AlgorithmPlugin):
    """Deterministic linear-time selection via median of medians."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="median-of-medians",
            name="Median of Medians (Introselect)",
            category="divide-and-conquer",
            visualization_type="ARRAY_BARS",
            description="Select median of array in O(n) worst-case with pivot from group medians.",
            intuition=(
                "Divide array into groups of 5, sort each group (O(1) per group). "
                "Median of group medians guarantees partition balance. "
                "Recurse into correct half — O(7n/10) each time → O(n) total."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(log n)",
            tags=("divide-and-conquer", "selection", "median-of-medians", "order-statistics"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        import random
        n = int(params.inputs.get("size", 15))
        rng = random.Random(params.seed)
        arr = tuple(rng.sample(range(1, 100), n))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"MoM n={n} seed={params.seed} target=median",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))
        arr = list(initial_state.array)
        target_k = n // 2  # find median

        steps_log = []

        def mom_select(indices, k):
            """Recursively select k-th smallest (0-indexed) from arr[indices]."""
            if len(indices) <= _GROUP:
                sorted_i = _insertion_sort_indices(arr, indices)
                steps_log.append(("base", list(indices), sorted_i[k]))
                return sorted_i[k]

            # Step 1: Divide into groups of 5, find each group's median
            group_medians = []
            for g in range(0, len(indices), _GROUP):
                group = indices[g:g + _GROUP]
                med_i = _median_index(arr, group)
                group_medians.append(med_i)
                steps_log.append(("group_median", list(group), med_i))

            # Step 2: Recursively find median of medians
            pivot_i = mom_select(group_medians, len(group_medians) // 2)
            steps_log.append(("pivot", list(indices), pivot_i))

            # Step 3: Partition around pivot
            pivot_val = arr[pivot_i]
            low = [i for i in indices if arr[i] < pivot_val]
            eq = [i for i in indices if arr[i] == pivot_val]
            high = [i for i in indices if arr[i] > pivot_val]

            steps_log.append(("partition", list(indices), pivot_i))

            if k < len(low):
                return mom_select(low, k)
            elif k < len(low) + len(eq):
                return eq[0]
            else:
                return mom_select(high, k - len(low) - len(eq))

        result_i = mom_select(list(range(n)), target_k)

        # Replay steps as visualization states
        visited = set()
        for step_type, idxs, highlight in steps_log:
            visited.update(idxs)
            sorted_so_far = frozenset(i for i in range(n) if i in visited)
            yield SortState(
                array=tuple(arr),
                comparing=(highlight, highlight),
                last_swap=(highlight, highlight) if step_type in ("pivot", "base") else None,
                sorted_indices=sorted_so_far,
                comparisons=len(steps_log),
                swaps=arr[highlight],
                description=(
                    f"{step_type}: idx={highlight} val={arr[highlight]} "
                    f"group_size={len(idxs)}"
                ),
            )

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([result_i]),
            comparisons=len(steps_log),
            swaps=arr[result_i],
            description=(
                f"Median found: arr[{result_i}]={arr[result_i]} "
                f"(true median of {n} elements)"
            ),
        )
