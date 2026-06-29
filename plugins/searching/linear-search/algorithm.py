"""Linear Search plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    SearchState,
    SimulationParams,
)


class LinearSearchSimulation(AlgorithmPlugin):
    """
    Linear Search — O(n) worst, O(1) best, works on unsorted arrays.

    Examines each element in order. current tracks the probe index (amber).
    eliminated grows as each non-matching element is checked.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="linear-search",
            name="Linear Search",
            category="searching",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Scans every element one by one until the target is found.",
            intuition="Check each book on the shelf from left to right until you find the one you want.",
            complexity_time_best="O(1)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("searching", "unsorted", "sequential", "beginner"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 20)
        target_pos: str = params.inputs.get("target_position", "middle")
        arr = sorted([rng.randint(1, size * 2) for _ in range(size)])

        if target_pos == "first":
            target = arr[0]
        elif target_pos == "last":
            target = arr[-1]
        elif target_pos == "missing":
            target = max(arr) + 1
        else:  # middle
            target = arr[len(arr) // 2]

        self._arr: List[int] = arr
        self._target: int = target
        return SearchState(
            array=tuple(arr),
            target=target,
            current=None,
            low=None,
            high=None,
            eliminated=frozenset(),
            found_at=None,
            comparisons=0,
            description=f"Searching for {target} in array of {size} elements",
        )

    def steps(
        self,
        initial_state: SearchState,
    ) -> Generator[SearchState, None, SearchState]:
        arr = list(initial_state.array)
        target = initial_state.target
        n = len(arr)
        comparisons = 0
        eliminated: set[int] = set()

        for i in range(n):
            comparisons += 1
            yield SearchState(
                array=tuple(arr),
                target=target,
                current=i,
                low=None,
                high=None,
                eliminated=frozenset(eliminated),
                found_at=None,
                comparisons=comparisons,
                description=f"Examining arr[{i}]={arr[i]} — is it {target}?",
            )

            if arr[i] == target:
                return SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=None,
                    high=None,
                    eliminated=frozenset(eliminated),
                    found_at=i,
                    comparisons=comparisons,
                    description=f"Found {target} at index {i}! {comparisons} comparisons",
                )

            eliminated.add(i)
            yield SearchState(
                array=tuple(arr),
                target=target,
                current=None,
                low=None,
                high=None,
                eliminated=frozenset(eliminated),
                found_at=None,
                comparisons=comparisons,
                description=f"arr[{i}]={arr[i]} ≠ {target}, eliminated",
            )

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
