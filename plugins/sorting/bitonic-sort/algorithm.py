"""Bitonic Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from math import log2
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _next_power_of_2(n: int) -> int:
    p = 1
    while p < n:
        p <<= 1
    return p


class BitonicSortSimulation(AlgorithmPlugin):
    """Bitonic Sort."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bitonic-sort",
            name="Bitonic Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Sort by building bitonic sequences and merging them, suitable for parallel hardware.",
            intuition=(
                "Divide array into pairs. Compare-and-swap each pair to make half ascending, "
                "half descending. Recursively build larger bitonic sequences until fully sorted."
            ),
            complexity_time_best="O(n log²n)",
            complexity_time_average="O(n log²n)",
            complexity_time_worst="O(n log²n)",
            complexity_space="O(n log n)",
            tags=("sorting", "bitonic", "parallel", "network-sort"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n_req = int(params.inputs.get("array_size", 8))
        n = _next_power_of_2(n_req)
        arr = rng.sample(range(1, n * 3 + 1), n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Bitonic sort n={n} {arr}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        comparisons = 0
        swaps = 0

        def compare_and_swap(i: int, j: int, ascending: bool):
            nonlocal comparisons, swaps
            comparisons += 1
            if (arr[i] > arr[j]) == ascending:
                arr[i], arr[j] = arr[j], arr[i]
                swaps += 1

        k = 2
        while k <= n:
            j = k >> 1
            while j > 0:
                for i in range(n):
                    l = i ^ j
                    if l > i:
                        ascending = ((i & k) == 0)
                        yield SortState(
                            array=tuple(arr),
                            comparing=(i, l),
                            last_swap=None,
                            sorted_indices=frozenset(),
                            comparisons=comparisons,
                            swaps=swaps,
                            description=f"k={k} j={j}: compare [{i}] and [{l}] (ascending={ascending})",
                        )
                        compare_and_swap(i, l, ascending)
                j >>= 1
            k <<= 1

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Bitonic sort complete: {swaps} swaps",
        )
