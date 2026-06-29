"""Subsets (Power Set) backtracking plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SearchState,
    SimulationParams,
)

_MAX_SUBSETS = 64


class SubsetsSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="subsets",
            name="Subsets (Power Set)",
            category="backtracking",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Generate all 2^n subsets of an array using backtracking (include/exclude each element).",
            intuition="At each index, branch twice: include the current element or exclude it. Recursing through all indices generates all 2^n subsets.",
            complexity_time_best="O(2^n)",
            complexity_time_average="O(2^n)",
            complexity_time_worst="O(2^n)",
            complexity_space="O(n)",
            tags=("backtracking", "subsets", "power-set", "combinatorics"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        size: int = max(3, min(params.inputs.get("array_size", 4), 6))
        arr = sorted(random.Random(params.seed).sample(range(1, size * 3), size))
        return SearchState(
            array=tuple(arr),
            target=0,  # current subset size (display only)
            current=0,  # current index being considered
            low=0,
            high=size - 1,
            eliminated=frozenset(),
            found_at=None,
            comparisons=0,
            description=f"subsets=[]  Generate all 2^{size}={2**size} subsets",
        )

    def steps(
        self, initial_state: SearchState
    ) -> Generator[SearchState, None, SearchState]:
        arr = list(initial_state.array)
        n = len(arr)
        current_subset: List[int] = []
        subset_count = [0]
        comparisons = [0]

        def backtrack(index: int):
            if subset_count[0] >= _MAX_SUBSETS:
                return
            # Record this subset
            subset_count[0] += 1
            subset_repr = str(sorted(current_subset))
            yield SearchState(
                array=tuple(arr),
                target=len(current_subset),
                current=index if index < n else n - 1,
                low=0,
                high=n - 1,
                eliminated=frozenset(
                    i for i in range(n) if arr[i] not in current_subset
                ),
                found_at=None,
                comparisons=comparisons[0],
                description=f"subsets #{subset_count[0]}: {subset_repr}",
            )
            for i in range(index, n):
                if subset_count[0] >= _MAX_SUBSETS:
                    return
                comparisons[0] += 1
                # Include arr[i]
                current_subset.append(arr[i])
                yield SearchState(
                    array=tuple(arr),
                    target=len(current_subset),
                    current=i,
                    low=index,
                    high=n - 1,
                    eliminated=frozenset(
                        j for j in range(n) if arr[j] not in current_subset
                    ),
                    found_at=None,
                    comparisons=comparisons[0],
                    description=f"include {arr[i]} → subset so far: {sorted(current_subset)}",
                )
                yield from backtrack(i + 1)
                # Exclude arr[i] (backtrack)
                current_subset.pop()

        yield from backtrack(0)

        return SearchState(
            array=tuple(arr),
            target=subset_count[0],
            current=None,
            low=0,
            high=n - 1,
            eliminated=frozenset(),
            found_at=None,
            comparisons=comparisons[0],
            description=f"Done — {subset_count[0]} subsets generated",
        )
