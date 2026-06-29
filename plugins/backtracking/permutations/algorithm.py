"""Permutations backtracking plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_MAX_PERMS = 80  # cap frames for large arrays


class PermutationsSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="permutations",
            name="Permutations (Backtracking)",
            category="backtracking",
            visualization_type="ARRAY_BARS",
            description="Generate all permutations of an array using backtracking with in-place swapping.",
            intuition="Fix each element at each position by swapping it with the start index, recurse for the remaining subarray, then swap back. Generates all n! orderings.",
            complexity_time_best="O(n·n!)",
            complexity_time_average="O(n·n!)",
            complexity_time_worst="O(n·n!)",
            complexity_space="O(n)",
            tags=("backtracking", "permutations", "combinatorics", "recursion"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = max(3, min(params.inputs.get("array_size", 4), 7))
        arr = list(range(1, size + 1))
        rng.shuffle(arr)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Generate all {size}! = {_factorial(size)} permutations",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        # Use mutable containers to mutate from nested functions
        stats = [0, 0]  # [comparisons, swaps]
        perm_count = [0]
        max_perms = min(_factorial(n), _MAX_PERMS)

        def permute(start: int):
            if perm_count[0] >= max_perms:
                return
            if start == n:
                perm_count[0] += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=None,
                    sorted_indices=frozenset(range(n)),
                    comparisons=stats[0],
                    swaps=stats[1],
                    description=f"Permutation #{perm_count[0]}: {list(arr)}",
                )
                return

            for i in range(start, n):
                if perm_count[0] >= max_perms:
                    return
                stats[0] += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=(start, i),
                    last_swap=None,
                    sorted_indices=frozenset(range(start)),
                    comparisons=stats[0],
                    swaps=stats[1],
                    description=f"depth={start}: swap arr[{start}]={arr[start]} ↔ arr[{i}]={arr[i]}",
                )
                arr[start], arr[i] = arr[i], arr[start]
                stats[1] += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=(start, i),
                    sorted_indices=frozenset(range(start + 1)),
                    comparisons=stats[0],
                    swaps=stats[1],
                    description=f"depth={start}: fixed {arr[start]} at pos {start}, recurse",
                )
                yield from permute(start + 1)
                # Backtrack
                arr[start], arr[i] = arr[i], arr[start]
                stats[1] += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=(start, i),
                    sorted_indices=frozenset(range(start)),
                    comparisons=stats[0],
                    swaps=stats[1],
                    description=f"depth={start}: backtrack — restore arr[{start}]={arr[start]}",
                )

        yield from permute(0)

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=stats[0],
            swaps=stats[1],
            description=f"Done — generated {perm_count[0]} permutation(s), {stats[1]} swaps",
        )


def _factorial(n: int) -> int:
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r
