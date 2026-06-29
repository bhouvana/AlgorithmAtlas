"""Ternary Search plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SearchState,
    SimulationParams,
)


class TernarySearchSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="ternary-search",
            name="Ternary Search",
            category="searching",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Eliminates one-third of the search range per step by dividing into three parts.",
            intuition="Split range [low, high] at 1/3 and 2/3 points. Compare target with both mid points to determine which third to keep.",
            complexity_time_best="O(1)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(1)",
            tags=("searching", "sorted", "divide-and-conquer"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        size: int = max(10, min(params.inputs.get("array_size", 20), 40))
        target_pos: str = params.inputs.get("target_position", "middle")
        arr = sorted(set([rng.randint(1, size * 3) for _ in range(size * 2)]))[:size]

        if target_pos == "first":
            target = arr[0]
        elif target_pos == "last":
            target = arr[-1]
        elif target_pos == "missing":
            target = max(arr) + 1
        else:
            target = arr[len(arr) // 2]

        return SearchState(
            array=tuple(arr),
            target=target,
            current=None,
            low=0,
            high=len(arr) - 1,
            eliminated=frozenset(),
            found_at=None,
            comparisons=0,
            description=f"Ternary search for {target} in array of {size} elements",
        )

    def steps(
        self, initial_state: SearchState
    ) -> Generator[SearchState, None, SearchState]:
        arr = list(initial_state.array)
        target = initial_state.target
        n = len(arr)
        eliminated: set = set()
        low, high = 0, n - 1
        comparisons = 0

        while low <= high:
            m1 = low + (high - low) // 3
            m2 = high - (high - low) // 3
            comparisons += 2

            yield SearchState(
                array=tuple(arr),
                target=target,
                current=m1,
                low=low,
                high=high,
                eliminated=frozenset(eliminated),
                found_at=None,
                comparisons=comparisons,
                description=f"m1={m1}({arr[m1]}), m2={m2}({arr[m2]}), comparing with {target}",
            )

            if arr[m1] == target:
                return SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=None,
                    high=None,
                    eliminated=frozenset(eliminated),
                    found_at=m1,
                    comparisons=comparisons,
                    description=f"Found {target} at m1={m1}! {comparisons} comparisons",
                )
            if arr[m2] == target:
                return SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=None,
                    high=None,
                    eliminated=frozenset(eliminated),
                    found_at=m2,
                    comparisons=comparisons,
                    description=f"Found {target} at m2={m2}! {comparisons} comparisons",
                )

            if target < arr[m1]:
                eliminated.update(range(m1, n))
                high = m1 - 1
                yield SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=low,
                    high=high,
                    eliminated=frozenset(eliminated),
                    found_at=None,
                    comparisons=comparisons,
                    description=f"{target} < arr[m1]={arr[m1]}: search [{low}, {high}]",
                )
            elif target > arr[m2]:
                eliminated.update(range(0, m2 + 1))
                low = m2 + 1
                yield SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=low,
                    high=high,
                    eliminated=frozenset(eliminated),
                    found_at=None,
                    comparisons=comparisons,
                    description=f"{target} > arr[m2]={arr[m2]}: search [{low}, {high}]",
                )
            else:
                new_elim = list(range(0, m1)) + list(range(m2 + 1, n))
                eliminated.update(new_elim)
                low, high = m1 + 1, m2 - 1
                yield SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=low,
                    high=high,
                    eliminated=frozenset(eliminated),
                    found_at=None,
                    comparisons=comparisons,
                    description=f"arr[m1] < {target} < arr[m2]: search middle [{low}, {high}]",
                )

        eliminated.update(range(n))
        return SearchState(
            array=tuple(arr),
            target=target,
            current=None,
            low=None,
            high=None,
            eliminated=frozenset(eliminated),
            found_at=None,
            comparisons=comparisons,
            description=f"{target} not found after {comparisons} comparisons",
        )
