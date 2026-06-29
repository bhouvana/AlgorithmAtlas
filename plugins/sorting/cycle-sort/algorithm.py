"""Cycle Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class CycleSortSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="cycle-sort",
            name="Cycle Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description=(
                "In-place sort minimizing writes: each element is moved directly "
                "to its sorted position by rotating cycles."
            ),
            intuition=(
                "For each starting element, count elements smaller to find its position. "
                "Place it there, then continue placing the displaced element — "
                "forming a cycle until we return to the start."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("sorting", "comparison", "in-place", "cycle", "writes"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 8))
        arr = rng.sample(range(1, n + 1), n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Initial array, size {n}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        comparisons = swaps = 0
        sorted_indices: set = set()

        for cycle_start in range(n - 1):
            item = arr[cycle_start]
            # Find position for item
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                comparisons += 1
                if arr[i] < item:
                    pos += 1

            if pos == cycle_start:
                sorted_indices.add(cycle_start)
                continue  # Already in correct position

            # Skip duplicates
            while item == arr[pos]:
                pos += 1

            # Place item
            arr[pos], item = item, arr[pos]
            swaps += 1
            yield SortState(
                array=tuple(arr),
                comparing=(cycle_start, pos),
                last_swap=(cycle_start, pos),
                sorted_indices=frozenset(sorted_indices),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Cycle from {cycle_start}: place {item} at {pos}",
            )

            # Rotate rest of cycle
            while pos != cycle_start:
                pos = cycle_start
                for i in range(cycle_start + 1, n):
                    comparisons += 1
                    if arr[i] < item:
                        pos += 1
                while item == arr[pos]:
                    pos += 1
                arr[pos], item = item, arr[pos]
                swaps += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=(cycle_start, pos),
                    last_swap=(cycle_start, pos),
                    sorted_indices=frozenset(sorted_indices),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"Cycle continues: place {item} at {pos}",
                )

            sorted_indices.add(cycle_start)

        for i in range(n):
            sorted_indices.add(i)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(sorted_indices),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted — {comparisons} comparisons, {swaps} writes",
        )
