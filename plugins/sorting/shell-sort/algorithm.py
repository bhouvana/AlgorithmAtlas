"""Shell Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    SimulationParams,
    SortState,
)

_CIURA_GAPS = [701, 301, 132, 57, 23, 10, 4, 1]


class ShellSortSimulation(AlgorithmPlugin):
    """
    Shell Sort with Ciura gap sequence — O(n log² n) practical performance.

    At each gap, performs a gapped insertion sort. The two elements being
    compared across the gap are shown in 'comparing' (amber).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="shell-sort",
            name="Shell Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Gapped insertion sort with decreasing gap sizes (Ciura sequence).",
            intuition=(
                "First sort elements far apart with a large step, then progressively "
                "smaller steps — until a regular insertion sort finishes the job."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log² n)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("comparison", "in-place", "unstable", "gap-sequence"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 20)
        arr: List[int] = [rng.randint(1, size * 2) for _ in range(size)]
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            auxiliary_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description="Ready to sort",
        )

    def steps(
        self,
        initial_state: SortState,
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        comparisons = 0
        swaps = 0

        gaps = [g for g in _CIURA_GAPS if g < n]
        if not gaps:
            gaps = [1]

        for gap in gaps:
            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(),
                auxiliary_indices=frozenset(),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Gap = {gap}: starting gapped insertion sort",
            )

            for i in range(gap, n):
                temp = arr[i]
                j = i

                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=None,
                    sorted_indices=frozenset(),
                    auxiliary_indices=frozenset({i}),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Gap {gap}: inserting arr[{i}]={temp}",
                )

                while j >= gap:
                    comparisons += 1
                    yield SortState(
                        array=tuple(arr),
                        comparing=(j - gap, j),
                        last_swap=None,
                        sorted_indices=frozenset(),
                        auxiliary_indices=frozenset({j}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Gap {gap}: arr[{j - gap}]={arr[j - gap]} > {temp}?",
                    )
                    if arr[j - gap] <= temp:
                        break
                    arr[j] = arr[j - gap]
                    swaps += 1
                    yield SortState(
                        array=tuple(arr),
                        comparing=None,
                        last_swap=(j - gap, j),
                        sorted_indices=frozenset(),
                        auxiliary_indices=frozenset({j - gap}),
                        comparisons=comparisons,
                        swaps=swaps,
                        description=f"Gap {gap}: shifting arr[{j - gap}]={arr[j]} right",
                    )
                    j -= gap

                arr[j] = temp

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            auxiliary_indices=frozenset(),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted! {comparisons} comparisons, {swaps} shifts",
        )
