"""Fibonacci Search plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SearchState,
    SimulationParams,
)


class FibonacciSearchSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="fibonacci-search",
            name="Fibonacci Search",
            category="searching",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Uses Fibonacci numbers to split the array, avoiding division (only addition/subtraction).",
            intuition="Maintain three consecutive Fibonacci numbers fib-2, fib-1, fib. The split is at offset+fib-2. Discard one third at a time.",
            complexity_time_best="O(1)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(1)",
            tags=("searching", "sorted", "fibonacci", "divide-and-conquer"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        size: int = max(10, min(params.inputs.get("array_size", 20), 40))
        arr = sorted(set([rng.randint(1, size * 3) for _ in range(size * 2)]))[:size]
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
            description=f"Fibonacci search for {target} in array of {size} elements",
        )

    def steps(
        self, initial_state: SearchState
    ) -> Generator[SearchState, None, SearchState]:
        arr = list(initial_state.array)
        target = initial_state.target
        n = len(arr)
        eliminated: set = set()
        comparisons = 0

        # Find smallest Fibonacci >= n
        f2, f1, f = 0, 1, 1
        while f < n:
            f2, f1, f = f1, f, f1 + f

        offset = -1

        while f > 1:
            i = min(offset + f2, n - 1)
            comparisons += 1

            yield SearchState(
                array=tuple(arr),
                target=target,
                current=i,
                low=offset + 1,
                high=min(offset + f, n - 1),
                eliminated=frozenset(eliminated),
                found_at=None,
                comparisons=comparisons,
                description=f"Fibonacci ({f2},{f1},{f}): check arr[{i}]={arr[i]}",
            )

            if arr[i] < target:
                # Eliminate left portion
                eliminated.update(range(0, i + 1))
                f2, f1, f = f1 - f2, f2, f1
                offset = i
                yield SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=offset + 1,
                    high=min(offset + f, n - 1),
                    eliminated=frozenset(eliminated),
                    found_at=None,
                    comparisons=comparisons,
                    description=f"arr[{i}]={arr[i]} < {target}: move right, new range [{offset+1}, {min(offset+f, n-1)}]",
                )
            elif arr[i] > target:
                # Eliminate right portion: step back 2 Fibonacci positions
                eliminated.update(range(i, n))
                f2, f1, f = 2 * f2 - f1, f1 - f2, f2
                yield SearchState(
                    array=tuple(arr),
                    target=target,
                    current=None,
                    low=offset + 1,
                    high=min(offset + f, n - 1),
                    eliminated=frozenset(eliminated),
                    found_at=None,
                    comparisons=comparisons,
                    description=f"arr[{i}]={arr[i]} > {target}: move left, new range [{offset+1}, {min(offset+f, n-1)}]",
                )
            else:
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

        # Check last remaining element
        if f1 and offset + 1 < n and arr[offset + 1] == target:
            comparisons += 1
            return SearchState(
                array=tuple(arr),
                target=target,
                current=None,
                low=None,
                high=None,
                eliminated=frozenset(eliminated),
                found_at=offset + 1,
                comparisons=comparisons,
                description=f"Found {target} at index {offset+1}! {comparisons} comparisons",
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
