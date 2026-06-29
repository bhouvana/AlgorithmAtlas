"""Bucket Sort plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _gen_array(seed, n):
    rng = seed * 1103515245 + 12345
    arr = []
    for _ in range(n):
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        arr.append((rng % 97) + 1)  # values 1..97
    return arr


def _insertion_sort(lst):
    for i in range(1, len(lst)):
        key = lst[i]
        j = i - 1
        while j >= 0 and lst[j] > key:
            lst[j + 1] = lst[j]
            j -= 1
        lst[j + 1] = key
    return lst


class BucketSortSimulation(AlgorithmPlugin):
    """Bucket sort visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bucket-sort",
            name="Bucket Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Distribute into buckets, sort each, then concatenate.",
            intuition=(
                "Divide value range into k buckets. "
                "Place each element in its bucket (O(n)). "
                "Sort each bucket with insertion sort. "
                "Concatenate buckets. O(n) average for uniform input."
            ),
            complexity_time_best="O(n+k)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n+k)",
            tags=("sorting", "bucket-sort", "distribution-sort", "linear-time"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = int(params.inputs.get("size", 12))
        arr = _gen_array(params.seed, n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"BucketSort n={n} seed={params.seed}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))
        seed = int(re.search(r"seed=(\d+)", initial_state.description).group(1))
        arr = list(_gen_array(seed, n))

        k = n  # number of buckets = array size
        max_val = 99  # values are 1..97

        # Phase 1: distribute into buckets
        buckets = [[] for _ in range(k)]
        for i, v in enumerate(arr):
            bucket_idx = min(k - 1, int(v * k / (max_val + 1)))
            buckets[bucket_idx].append(v)
            # Show distribution: array with current position
            display = list(arr)
            yield SortState(
                array=tuple(display),
                comparing=(i, bucket_idx),
                last_swap=None,
                sorted_indices=frozenset(),
                comparisons=i + 1,
                swaps=i,
                description=f"Distribute arr[{i}]={v} → bucket {bucket_idx}",
            )

        # Phase 2: sort each bucket and collect
        sorted_arr = []
        for b_idx, bucket in enumerate(buckets):
            if bucket:
                _insertion_sort(bucket)
                sorted_arr.extend(bucket)
                # Show sorted prefix + remaining
                remaining = sum(len(buckets[j]) for j in range(b_idx + 1, k))
                display = sorted_arr + [1] * remaining
                display = display[:n] if len(display) >= n else display + [1] * (n - len(display))
                yield SortState(
                    array=tuple(display[:n]),
                    comparing=None,
                    last_swap=(len(sorted_arr) - 1, len(sorted_arr) - 1),
                    sorted_indices=frozenset(range(len(sorted_arr))),
                    comparisons=n + b_idx,
                    swaps=b_idx + 1,
                    description=f"Sorted bucket {b_idx}: {sorted(bucket)} → output",
                )

        return SortState(
            array=tuple(sorted_arr[:n]),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=n + k,
            swaps=n,
            description=f"Bucket sort complete. {n} elements sorted.",
        )
