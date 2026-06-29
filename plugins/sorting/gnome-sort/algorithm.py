"""Gnome Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class GnomeSortSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="gnome-sort",
            name="Gnome Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description=(
                "Like insertion sort but moves elements one step backward at a time, "
                "similar to a gnome sorting flower pots."
            ),
            intuition=(
                "At each position: if element is ≥ previous, step forward. "
                "Otherwise, swap backward and step back. If at start, step forward again."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(1)",
            tags=("sorting", "comparison", "in-place", "gnome"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 10))
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
        pos = 1

        while pos < n:
            if pos == 0 or arr[pos] >= arr[pos - 1]:
                comparisons += 1
                if pos > 0:
                    sorted_indices.add(pos - 1)
                yield SortState(
                    array=tuple(arr),
                    comparing=(pos - 1, pos) if pos > 0 else None,
                    last_swap=None,
                    sorted_indices=frozenset(sorted_indices),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"pos={pos}: arr[{pos}]={arr[pos]} ≥ arr[{pos-1}]={arr[pos-1] if pos>0 else '?'} → advance",
                )
                pos += 1
            else:
                comparisons += 1
                arr[pos], arr[pos - 1] = arr[pos - 1], arr[pos]
                swaps += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=(pos - 1, pos),
                    last_swap=(pos - 1, pos),
                    sorted_indices=frozenset(sorted_indices),
                    comparisons=comparisons,
                    swaps=swaps,
                    description=f"pos={pos}: swap arr[{pos}] and arr[{pos-1}] → retreat",
                )
                pos -= 1

        for i in range(n):
            sorted_indices.add(i)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(sorted_indices),
            comparisons=comparisons,
            swaps=swaps,
            description=f"Sorted — {comparisons} comparisons, {swaps} swaps",
        )
