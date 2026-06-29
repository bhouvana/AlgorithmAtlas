"""Strand Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class StrandSortSimulation(AlgorithmPlugin):
    """Strand Sort."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="strand-sort",
            name="Strand Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Repeatedly extract sorted strands from input and merge them into the output.",
            intuition=(
                "Scan input; greedily pull elements larger than the strand's tail. "
                "Merge the extracted strand into the sorted result. Best on nearly-sorted data."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n)",
            tags=("sorting", "strand-sort", "merge-based", "natural-sort"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 8))
        arr = rng.sample(range(1, n * 3 + 1), n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Strand sort {arr}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        input_arr = list(initial_state.array)
        n = len(input_arr)
        result: list = []
        comparisons = 0
        swaps = 0

        pass_num = 0
        while input_arr:
            pass_num += 1
            # Extract strand
            strand = [input_arr[0]]
            remaining = []
            for i in range(1, len(input_arr)):
                comparisons += 1
                if input_arr[i] >= strand[-1]:
                    strand.append(input_arr[i])
                else:
                    remaining.append(input_arr[i])

            yield SortState(
                array=tuple(input_arr),
                comparing=(0, len(input_arr) - 1),
                last_swap=None,
                sorted_indices=frozenset(range(n - len(input_arr))),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Pass {pass_num}: extracted strand={strand}, remaining={remaining}",
            )

            # Merge strand with result
            merged = []
            i = j = 0
            while i < len(result) and j < len(strand):
                comparisons += 1
                if result[i] <= strand[j]:
                    merged.append(result[i])
                    i += 1
                else:
                    merged.append(strand[j])
                    j += 1
                swaps += 1
            merged.extend(result[i:])
            merged.extend(strand[j:])
            result = merged
            input_arr = remaining

            yield SortState(
                array=tuple(result + input_arr),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(range(len(result))),
                comparisons=comparisons,
                swaps=swaps,
                description=f"After merge: result={result}",
            )

        return SortState(
            array=tuple(result),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Strand sort complete: {pass_num} passes",
        )
