"""Counting Sort plugin for Algorithm Atlas."""
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


class CountingSortSimulation(AlgorithmPlugin):
    """
    Counting Sort — O(n + k) time and space, stable, integer keys only.

    Phase 1: Count occurrences of each value.
    Phase 2: Reconstruct sorted output from counts.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="counting-sort",
            name="Counting Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Count occurrences of each value, reconstruct sorted array — no comparisons.",
            intuition=(
                "Count how many 1s, 2s, 3s are in the pile, then place that many "
                "of each value back in order."
            ),
            complexity_time_best="O(n + k)",
            complexity_time_average="O(n + k)",
            complexity_time_worst="O(n + k)",
            complexity_space="O(k)",
            tags=("non-comparison", "stable", "integer", "linear"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 20)
        max_val: int = params.inputs.get("max_value", 20)
        arr: List[int] = [rng.randint(1, max_val) for _ in range(size)]
        self._max_val: int = max_val
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
        max_val = getattr(self, "_max_val", 20)
        swaps = 0

        yield SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            auxiliary_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Phase 1: counting occurrences (range 1..{max_val})",
        )

        counts: List[int] = [0] * (max_val + 1)
        for idx, val in enumerate(arr):
            counts[val] += 1
            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(),
                auxiliary_indices=frozenset({idx}),
                comparisons=0,
                swaps=swaps,
                description=f"Counting: arr[{idx}]={val} → count[{val}]={counts[val]}",
            )

        yield SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            auxiliary_indices=frozenset(),
            comparisons=0,
            swaps=swaps,
            description="Phase 2: reconstructing sorted array from counts",
        )

        output = [0] * n
        write_pos = 0

        for val in range(1, max_val + 1):
            for _ in range(counts[val]):
                output[write_pos] = val
                swaps += 1
                yield SortState(
                    array=tuple(output),
                    comparing=None,
                    last_swap=(write_pos, write_pos),
                    sorted_indices=frozenset(range(write_pos)),
                    auxiliary_indices=frozenset({write_pos}),
                    comparisons=0,
                    swaps=swaps,
                    description=f"Writing value {val} to position {write_pos}",
                )
                write_pos += 1

        return SortState(
            array=tuple(output),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            auxiliary_indices=frozenset(),
            comparisons=0,
            swaps=swaps,
            description=f"Sorted! 0 comparisons, {swaps} writes",
        )
