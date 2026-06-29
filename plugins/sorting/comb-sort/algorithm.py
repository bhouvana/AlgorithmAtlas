"""Comb Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_SHRINK = 1.3


class CombSortSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="comb-sort",
            name="Comb Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Improved bubble sort that starts with large gaps to eliminate distant inversions early.",
            intuition="Large initial gap removes 'turtles' (small values near end) efficiently. The gap shrinks by factor 1.3 each pass until gap=1 (final bubble sort phase).",
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n²/2^p)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("sorting", "comparison-based", "comb-sort", "gap-sequence"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = max(5, min(params.inputs.get("array_size", 10), 20))
        arr = [rng.randint(1, size * 2) for _ in range(size)]
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Comb sort: {size} elements, gap starts at {int(size / _SHRINK)}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        gap = n
        sorted_flag = False
        comparisons = 0
        swaps = 0

        while not (gap == 1 and sorted_flag):
            gap = max(1, int(gap / _SHRINK))
            sorted_flag = True

            for i in range(n - gap):
                j = i + gap
                comparisons += 1

                yield SortState(
                    array=tuple(arr),
                    comparing=(i, j),
                    last_swap=None,
                    sorted_indices=frozenset(),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"gap={gap}: compare arr[{i}]={arr[i]} with arr[{j}]={arr[j]}",
                )

                if arr[i] > arr[j]:
                    arr[i], arr[j] = arr[j], arr[i]
                    swaps += 1
                    sorted_flag = False
                    yield SortState(
                        array=tuple(arr),
                        comparing=None,
                        last_swap=(i, j),
                        sorted_indices=frozenset(),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"gap={gap}: swap arr[{i}] ↔ arr[{j}]",
                    )

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted! {comparisons} comparisons, {swaps} swaps",
        )
