"""House Robber DP plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class HouseRobberSimulation(AlgorithmPlugin):
    """House Robber — max non-adjacent sum."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="house-robber",
            name="House Robber",
            category="dynamic-programming",
            visualization_type="ARRAY_BARS",
            description="Find max money from non-adjacent houses: dp[i] = max(dp[i-1], dp[i-2]+nums[i]).",
            intuition=(
                "At each house, decide to rob it (prev_prev + current value) "
                "or skip it (prev). Track two running values to avoid O(n) space."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("dynamic-programming", "house-robber", "linear-dp"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 8))
        nums = [rng.randint(1, 20) for _ in range(n)]

        # Compute optimal
        prev2, prev1 = 0, 0
        for v in nums:
            prev2, prev1 = prev1, max(prev1, prev2 + v)

        return SortState(
            array=tuple(nums),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=prev1,
            description=f"Rob houses {nums}: max={prev1}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        nums = list(initial_state.array)
        n = len(nums)
        prev2, prev1 = 0, 0
        robbed: set[int] = set()

        for i, v in enumerate(nums):
            new_val = max(prev1, prev2 + v)
            if prev2 + v > prev1:
                # Would rob this house
                action = f"rob house {i} (+{v}) → {new_val}"
            else:
                action = f"skip house {i} → {new_val}"
            prev2, prev1 = prev1, new_val

            yield SortState(
                array=tuple(nums),
                comparing=(i, max(0, i - 1)),
                last_swap=None,
                sorted_indices=frozenset(),
                comparisons=i + 1,
                swaps=prev1,
                description=f"i={i} val={v} dp={prev1} ({action})",
            )

        return SortState(
            array=tuple(nums),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=n,
            swaps=prev1,
            description=f"Max robbery = {prev1}",
        )
