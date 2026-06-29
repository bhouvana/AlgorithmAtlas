"""Stooge Sort plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class StoogeSortSimulation(AlgorithmPlugin):
    """Stooge Sort."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="stooge-sort",
            name="Stooge Sort",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Recursive sort with O(n^2.7): sort first 2/3, last 2/3, first 2/3 again.",
            intuition=(
                "Recursively: if only 2 elements, compare-and-swap if needed. "
                "Otherwise, sort first 2/3, then last 2/3, then first 2/3 again."
            ),
            complexity_time_best="O(n^2.7)",
            complexity_time_average="O(n^2.7)",
            complexity_time_worst="O(n^2.7)",
            complexity_space="O(log n)",
            tags=("sorting", "stooge-sort", "recursive", "theoretical"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 5))
        arr = rng.sample(range(1, n * 3 + 1), n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Stooge sort {arr}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        frames: list = []
        comparisons = [0]
        swaps = [0]

        def stooge(lo: int, hi: int):
            if lo >= hi:
                return
            comparisons[0] += 1
            frames.append(("compare", lo, hi, list(arr)))
            if arr[lo] > arr[hi]:
                arr[lo], arr[hi] = arr[hi], arr[lo]
                swaps[0] += 1
                frames.append(("swap", lo, hi, list(arr)))
            if hi - lo + 1 > 2:
                t = (hi - lo + 1) // 3
                stooge(lo, hi - t)
                stooge(lo + t, hi)
                stooge(lo, hi - t)

        stooge(0, n - 1)

        for action, i, j, snapshot in frames:
            yield SortState(
                array=tuple(snapshot),
                comparing=(i, j) if action == "compare" else None,
                last_swap=(i, j) if action == "swap" else None,
                sorted_indices=frozenset(),
                comparisons=comparisons[0],
                swaps=swaps[0],
                description=f"{action.capitalize()} [{i}] and [{j}]",
            )

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=comparisons[0],
            swaps=swaps[0],
            description=f"Sorted in {swaps[0]} swaps",
        )
