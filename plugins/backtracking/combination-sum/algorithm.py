"""Combination Sum backtracking plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_MAX_SOLUTIONS = 20
_CANDIDATES = [2, 3, 5, 7, 11]


class CombinationSumSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="combination-sum",
            name="Combination Sum",
            category="backtracking",
            visualization_type="ARRAY_BARS",
            description="Find all combinations of candidates that sum to a target, with each candidate reusable.",
            intuition="Try each candidate starting from the current index. Subtract it from the remaining target and recurse. Backtrack when the remainder goes negative. Reuse is allowed.",
            complexity_time_best="O(n^(t/m))",
            complexity_time_average="O(n^(t/m))",
            complexity_time_worst="O(n^(t/m))",
            complexity_space="O(t/m)",
            tags=("backtracking", "combination", "sum", "recursion"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = max(3, min(params.inputs.get("array_size", 4), 6))
        candidates = sorted(_CANDIDATES[:size])
        # Pick a target achievable by 2-3 candidates
        target = candidates[0] * 2 + candidates[1]
        return SortState(
            array=tuple(candidates),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Combination Sum: candidates={candidates}, target={target}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        candidates = list(initial_state.array)
        n = len(candidates)
        # Decode target from the description
        desc = initial_state.description
        target = int(desc.split("target=")[1])

        current_combo: List[int] = []
        solutions: List[List[int]] = []
        comparisons = [0]
        swaps = [0]  # reused as solution counter display

        def backtrack(start: int, remaining: int):
            if len(solutions) >= _MAX_SOLUTIONS:
                return
            if remaining == 0:
                solutions.append(list(current_combo))
                swaps[0] = len(solutions)
                yield SortState(
                    array=tuple(candidates),
                    comparing=None,
                    last_swap=None,
                    sorted_indices=frozenset(
                        i for i, c in enumerate(candidates) if c in current_combo
                    ),
                    comparisons=comparisons[0],
                    swaps=swaps[0],
                    description=f"Solution #{swaps[0]}: {sorted(current_combo)}",
                )
                return
            for i in range(start, n):
                if len(solutions) >= _MAX_SOLUTIONS:
                    return
                c = candidates[i]
                comparisons[0] += 1
                if c > remaining:
                    yield SortState(
                        array=tuple(candidates),
                        comparing=(i, i),
                        last_swap=None,
                        sorted_indices=frozenset(
                            j for j, cv in enumerate(candidates) if cv in current_combo
                        ),
                        comparisons=comparisons[0],
                        swaps=swaps[0],
                        description=f"candidates[{i}]={c} > remaining={remaining}: prune",
                    )
                    break  # candidates are sorted, larger ones won't work either
                yield SortState(
                    array=tuple(candidates),
                    comparing=(i, i),
                    last_swap=None,
                    sorted_indices=frozenset(
                        j for j, cv in enumerate(candidates) if cv in current_combo
                    ),
                    comparisons=comparisons[0],
                    swaps=swaps[0],
                    description=f"Try adding {c}, remaining={remaining - c}, combo so far: {sorted(current_combo + [c])}",
                )
                current_combo.append(c)
                yield from backtrack(i, remaining - c)
                current_combo.pop()

        yield from backtrack(0, target)

        return SortState(
            array=tuple(candidates),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=comparisons[0],
            swaps=len(solutions),
            description=f"Done — {len(solutions)} combination(s) sum to {target}",
        )
