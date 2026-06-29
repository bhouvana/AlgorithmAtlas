"""Two Sum plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _make_array_with_target(rng: random.Random, n: int):
    """Make array and a target that has a solution."""
    arr = [rng.randint(1, 20) for _ in range(n)]
    i, j = rng.sample(range(n), 2)
    target = arr[i] + arr[j]
    return arr, target


class TwoSumSimulation(AlgorithmPlugin):
    """Two Sum with Hash Map."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="two-sum",
            name="Two Sum",
            category="searching",
            visualization_type="ARRAY_BARS",
            description="Find two indices summing to target using a complement hash map in O(n).",
            intuition=(
                "For each element x at index i, check if target-x is already seen. "
                "If yes, return (complement_index, i). Otherwise store {x: i} in the map."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("searching", "two-sum", "hash-map"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 8))
        arr, target = _make_array_with_target(rng, n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=target,
            description=f"Two sum in {arr} target={target}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        target = initial_state.swaps
        n = len(arr)
        seen: dict[int, int] = {}
        comparisons = 0
        result = (-1, -1)

        for i, v in enumerate(arr):
            complement = target - v
            comparisons += 1
            if complement in seen:
                result = (seen[complement], i)
                yield SortState(
                    array=tuple(arr),
                    comparing=(seen[complement], i),
                    last_swap=None,
                    sorted_indices=frozenset([seen[complement], i]),
                    comparisons=comparisons,
                    swaps=target,
                    description=f"Found! arr[{seen[complement]}]={complement} + arr[{i}]={v} = {target}",
                )
                break
            seen[v] = i
            yield SortState(
                array=tuple(arr),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(),
                comparisons=comparisons,
                swaps=target,
                description=f"i={i} val={v} complement={complement} not in map, store {v}→{i}",
            )

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(result) if result[0] >= 0 else frozenset(),
            comparisons=comparisons,
            swaps=target,
            description=f"Result: indices {result[0]},{result[1]}" if result[0] >= 0 else "No solution found",
        )
