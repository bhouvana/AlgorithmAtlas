"""Jump Search plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    SearchState,
    SimulationParams,
)


class JumpSearchSimulation(AlgorithmPlugin):
    """
    Jump Search — O(√n), requires sorted array.

    Phase 1 (jumping): jump ahead by step=√n until arr[pos] >= target.
    Phase 2 (linear): scan backwards from the current block start.

    The jump step boundary is shown in auxiliary positions implied by current.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="jump-search",
            name="Jump Search",
            category="searching",
            visualization_type="ARRAY_BARS_SEARCH",
            description="Jump ahead by √n steps to find the target's block, then linear search within it.",
            intuition="Flip through a book √n pages at a time, then backtrack page by page.",
            complexity_time_best="O(1)",
            complexity_time_average="O(√n)",
            complexity_time_worst="O(√n)",
            complexity_space="O(1)",
            tags=("searching", "sorted", "block", "sqrt-decomposition"),
        )

    def initialize(self, params: SimulationParams) -> SearchState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 25)
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
            low=None,
            high=None,
            eliminated=frozenset(),
            found_at=None,
            comparisons=0,
            description=f"Jump searching for {target} (step size = √{size} ≈ {int(math.sqrt(size))})",
        )

    def steps(
        self,
        initial_state: SearchState,
    ) -> Generator[SearchState, None, SearchState]:
        arr = list(initial_state.array)
        target = initial_state.target
        n = len(arr)
        step = int(math.sqrt(n))
        comparisons = 0
        eliminated: set[int] = set()

        # Phase 1: Jump ahead
        prev = 0
        current = step

        while current < n and arr[min(current, n - 1) - 1] < target:
            comparisons += 1
            probe = min(current, n - 1)
            yield SearchState(
                array=tuple(arr),
                target=target,
                current=probe,
                low=prev,
                high=current,
                eliminated=frozenset(eliminated),
                found_at=None,
                comparisons=comparisons,
                description=f"Jump: arr[{probe}]={arr[probe]} < {target}, jumping to {current + step}",
            )
            eliminated.update(range(prev, probe))
            prev = current
            current += step

        # Phase 2: Linear search in [prev, min(current, n)-1]
        high = min(current, n) - 1
        yield SearchState(
            array=tuple(arr),
            target=target,
            current=None,
            low=prev,
            high=high,
            eliminated=frozenset(eliminated),
            found_at=None,
            comparisons=comparisons,
            description=f"Phase 2: linear search in block [{prev}, {high}]",
        )

        for i in range(prev, high + 1):
            comparisons += 1
            yield SearchState(
                array=tuple(arr),
                target=target,
                current=i,
                low=prev,
                high=high,
                eliminated=frozenset(eliminated),
                found_at=None,
                comparisons=comparisons,
                description=f"Linear: arr[{i}]={arr[i]} — is it {target}?",
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

        eliminated.update(range(high + 1, n))
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
