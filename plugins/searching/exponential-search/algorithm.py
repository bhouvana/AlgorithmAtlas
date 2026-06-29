"""Exponential Search plugin for Algorithm Atlas."""
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


class ExponentialSearchSimulation(AlgorithmPlugin):
    """
    Exponential Search — O(log n), useful when array size is unknown.

    Phase 1: Find a range [i//2, i] where target lies, by doubling i each step.
    Phase 2: Binary search within [i//2, min(i, n-1)].
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="exponential-search",
            name="Exponential Search",
            category="searching",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Double the search range until overshoot, then binary search within the last range.",
            intuition="Double your window size (1, 2, 4, 8, 16…) until you overshoot, then binary search that last window.",
            complexity_time_best="O(1)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(1)",
            tags=("searching", "sorted", "exponential", "unbounded"),
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
            description=f"Exponential searching for {target} in {size} elements",
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

        # Immediate match at index 0
        comparisons += 1
        yield SearchState(
            array=tuple(arr),
            target=target,
            current=0,
            low=0,
            high=n - 1,
            eliminated=frozenset(eliminated),
            found_at=None,
            comparisons=comparisons,
            description=f"Check arr[0]={arr[0]} — is it {target}?",
        )

        if arr[0] == target:
            return SearchState(
                array=tuple(arr),
                target=target,
                current=None,
                low=None,
                high=None,
                eliminated=frozenset(eliminated),
                found_at=0,
                comparisons=comparisons,
                description=f"Found {target} at index 0! {comparisons} comparison",
            )

        # Phase 1: Find range [i//2, i] by doubling
        i = 1
        eliminated.add(0)
        while i < n:
            comparisons += 1
            probe = min(i, n - 1)
            yield SearchState(
                array=tuple(arr),
                target=target,
                current=probe,
                low=i // 2,
                high=probe,
                eliminated=frozenset(eliminated),
                found_at=None,
                comparisons=comparisons,
                description=f"Exponential probe: arr[{probe}]={arr[probe]} — is it ≥ {target}?",
            )

            if arr[probe] >= target:
                break

            eliminated.update(range(i // 2, probe + 1))
            i *= 2

        # Phase 2: Binary search in [i//2, min(i, n-1)]
        low = i // 2
        high = min(i, n - 1)

        yield SearchState(
            array=tuple(arr),
            target=target,
            current=None,
            low=low,
            high=high,
            eliminated=frozenset(eliminated),
            found_at=None,
            comparisons=comparisons,
            description=f"Phase 2: binary search in [{low}, {high}]",
        )

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
                description=f"Binary mid={mid}, arr[{mid}]={arr[mid]} — comparing with {target}",
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
            else:
                eliminated.update(range(mid, high + 1))
                high = mid - 1

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
