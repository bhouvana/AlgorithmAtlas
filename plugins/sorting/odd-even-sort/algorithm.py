"""Odd-Even Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class OddEvenSortSimulation(AlgorithmPlugin):
    """Odd-Even (Brick) Sort."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="odd-even-sort",
            name="Odd-Even Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description=(
                "Alternates between comparing odd-indexed and even-indexed adjacent pairs. "
                "Parallelizable variant of bubble sort."
            ),
            intuition=(
                "Phase 1 (odd): compare (0,1),(2,3),(4,5)… "
                "Phase 2 (even): compare (1,2),(3,4),(5,6)… "
                "Repeat until no swaps in either phase."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("sorting", "odd-even", "parallel", "bubble-variant"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 8))
        arr = random.Random(params.seed).sample(range(1, n * 3 + 1), n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Odd-even sort {arr}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        comparisons = 0
        swaps = 0
        sorted_indices: set[int] = set()

        sorted_flag = False
        while not sorted_flag:
            sorted_flag = True

            # Odd phase: pairs (0,1),(2,3),...
            for i in range(0, n - 1, 2):
                comparisons += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=(i, i + 1),
                    last_swap=None,
                    sorted_indices=frozenset(sorted_indices),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Odd phase: compare [{i}]={arr[i]} vs [{i+1}]={arr[i+1]}",
                )
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swaps += 1
                    sorted_flag = False
                    yield SortState(
                        array=tuple(arr),
                        comparing=None,
                        last_swap=(i, i + 1),
                        sorted_indices=frozenset(sorted_indices),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Odd phase: swap [{i}] and [{i+1}]",
                    )

            # Even phase: pairs (1,2),(3,4),...
            for i in range(1, n - 1, 2):
                comparisons += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=(i, i + 1),
                    last_swap=None,
                    sorted_indices=frozenset(sorted_indices),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Even phase: compare [{i}]={arr[i]} vs [{i+1}]={arr[i+1]}",
                )
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swaps += 1
                    sorted_flag = False
                    yield SortState(
                        array=tuple(arr),
                        comparing=None,
                        last_swap=(i, i + 1),
                        sorted_indices=frozenset(sorted_indices),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Even phase: swap [{i}] and [{i+1}]",
                    )

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted in {swaps} swaps and {comparisons} comparisons",
        )
