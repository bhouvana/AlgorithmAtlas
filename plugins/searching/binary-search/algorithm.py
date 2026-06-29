"""Binary Search plugin for Algorithm Atlas."""
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


class BinarySearchSimulation(AlgorithmPlugin):
    """
    Binary Search — O(log n), requires sorted array.

    Maintains [low, high] active range. At each step:
    1. Compute mid = (low + high) // 2
    2. Compare arr[mid] with target
    3. Eliminate the half that cannot contain target

    Elements outside [low, high] are marked eliminated (gray in renderer).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="binary-search",
            name="Binary Search",
            category="searching",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Halves the search range each step by comparing target to the middle element.",
            intuition="Open a dictionary to the middle — if before, go left; if after, go right.",
            complexity_time_best="O(1)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(1)",
            tags=("searching", "sorted", "divide-and-conquer", "logarithmic"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 20)
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
            description=f"Binary searching for {target} in sorted array of {size} elements",
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
        low = 0
        high = n - 1

        while low <= high:
            mid = (low + high) // 2
            comparisons += 1

            yield SearchState(
                array=tuple(arr),
                target=target,
                current=mid,
                low=low,
                high=high,
                eliminated=frozenset(eliminated),
                found_at=None,
                comparisons=comparisons,
                description=f"mid={mid}, arr[{mid}]={arr[mid]} — comparing with {target}",
            )

            if arr[mid] == target:
                return SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=None,
                    high=None,
                    eliminated=frozenset(eliminated),
                    found_at=mid,
                    comparisons=comparisons,
                    description=f"Found {target} at index {mid}! {comparisons} comparisons",
                )
            elif arr[mid] < target:
                eliminated.update(range(low, mid + 1))
                low = mid + 1
                yield SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=low,
                    high=high,
                    eliminated=frozenset(eliminated),
                    found_at=None,
                    comparisons=comparisons,
                    description=f"arr[{mid}]={arr[mid]} < {target}: eliminated left half, new range [{low}, {high}]",
                )
            else:
                eliminated.update(range(mid, high + 1))
                high = mid - 1
                yield SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=low,
                    high=high,
                    eliminated=frozenset(eliminated),
                    found_at=None,
                    comparisons=comparisons,
                    description=f"arr[{mid}]={arr[mid]} > {target}: eliminated right half, new range [{low}, {high}]",
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
