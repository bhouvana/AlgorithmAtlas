"""Interpolation Search plugin for Algorithm Atlas."""
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


class InterpolationSearchSimulation(AlgorithmPlugin):
    """
    Interpolation Search — O(log log n) average on uniformly distributed data.

    Probe position is estimated as:
        pos = low + ((target - arr[low]) * (high - low)) // (arr[high] - arr[low])

    This places the probe proportionally based on where the target's value
    falls within the current range's value range. Falls back to midpoint when
    arr[high] == arr[low] to avoid division by zero.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="interpolation-search",
            name="Interpolation Search",
            category="searching",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Probes at an interpolated position based on value distribution.",
            intuition="If looking for 'Zebra', skip to near the end of the dictionary — you know roughly where Z lives.",
            complexity_time_best="O(1)",
            complexity_time_average="O(log log n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("searching", "sorted", "interpolation", "uniform-distribution"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 20)
        target_pos: str = params.inputs.get("target_position", "middle")
        # Use uniformly distributed values for best-case O(log log n) behavior
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
            description=f"Interpolation searching for {target} in {size} elements",
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

        while (
            low <= high
            and arr[low] <= target <= arr[high]
        ):
            if arr[high] == arr[low]:
                # Avoid division by zero — fall back to midpoint
                pos = (low + high) // 2
            else:
                pos = low + ((target - arr[low]) * (high - low)) // (arr[high] - arr[low])
                pos = max(low, min(pos, high))

            comparisons += 1
            yield SearchState(
                array=tuple(arr),
                target=target,
                current=pos,
                low=low,
                high=high,
                eliminated=frozenset(eliminated),
                found_at=None,
                comparisons=comparisons,
                description=(
                    f"Probe at pos={pos} (interpolated), arr[{pos}]={arr[pos]}"
                ),
            )

            if arr[pos] == target:
                return SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=None,
                    high=None,
                    eliminated=frozenset(eliminated),
                    found_at=pos,
                    comparisons=comparisons,
                    description=f"Found {target} at index {pos}! {comparisons} comparisons",
                )
            elif arr[pos] < target:
                eliminated.update(range(low, pos + 1))
                low = pos + 1
                yield SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=low,
                    high=high,
                    eliminated=frozenset(eliminated),
                    found_at=None,
                    comparisons=comparisons,
                    description=f"arr[{pos}]={arr[pos]} < {target}: new range [{low}, {high}]",
                )
            else:
                eliminated.update(range(pos, high + 1))
                high = pos - 1
                yield SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=low,
                    high=high,
                    eliminated=frozenset(eliminated),
                    found_at=None,
                    comparisons=comparisons,
                    description=f"arr[{pos}]={arr[pos]} > {target}: new range [{low}, {high}]",
                )

        # Check remaining single element (target out of range means not found)
        if low <= high and arr[low] == target:
            comparisons += 1
            return SearchState(
                array=tuple(arr),
                target=target,
                current=None,
                low=None,
                high=None,
                eliminated=frozenset(eliminated),
                found_at=low,
                comparisons=comparisons,
                description=f"Found {target} at index {low}! {comparisons} comparisons",
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
