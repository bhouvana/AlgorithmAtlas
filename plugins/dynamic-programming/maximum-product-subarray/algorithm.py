"""Maximum Product Subarray plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _make_array(rng: random.Random, n: int) -> list[int]:
    """Generate array with some negatives and zeros."""
    arr = []
    for _ in range(n):
        r = rng.random()
        if r < 0.2:
            arr.append(0)
        elif r < 0.5:
            arr.append(-rng.randint(1, 5))
        else:
            arr.append(rng.randint(1, 5))
    return arr


def _max_product(nums: list) -> int:
    max_p = min_p = best = nums[0]
    for v in nums[1:]:
        candidates = (v, max_p * v, min_p * v)
        max_p = max(candidates)
        min_p = min(candidates)
        best = max(best, max_p)
    return best


class MaxProductSubarraySimulation(AlgorithmPlugin):
    """Maximum Product Subarray."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="maximum-product-subarray",
            name="Maximum Product Subarray",
            category="dynamic-programming",
            visualization_type="ARRAY_BARS",
            description="Find max product contiguous subarray by tracking max and min at each position.",
            intuition=(
                "Two negatives make a positive, so track min_product too. "
                "max[i] = max(num, max[i-1]·num, min[i-1]·num). "
                "Answer = max over all positions."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("dynamic-programming", "product-subarray", "linear-dp"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 8))
        nums = _make_array(rng, n)
        best = _max_product(nums)
        return SortState(
            array=tuple(nums),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=best,
            description=f"Max product subarray of {nums}: expected={best}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        nums = list(initial_state.array)
        max_p = min_p = best = nums[0]
        best_end = 0

        yield SortState(
            array=tuple(nums),
            comparing=(0, 0),
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=1,
            swaps=best,
            description=f"i=0 val={nums[0]} max_p={max_p} min_p={min_p} best={best}",
        )

        for i in range(1, len(nums)):
            v = nums[i]
            candidates = (v, max_p * v, min_p * v)
            max_p = max(candidates)
            min_p = min(candidates)
            if max_p > best:
                best = max_p
                best_end = i

            yield SortState(
                array=tuple(nums),
                comparing=(i, best_end),
                last_swap=None,
                sorted_indices=frozenset(),
                comparisons=i + 1,
                swaps=best,
                description=f"i={i} val={v} max_p={max_p} min_p={min_p} best={best}",
            )

        return SortState(
            array=tuple(nums),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(nums))),
            comparisons=len(nums),
            swaps=best,
            description=f"Max product = {best}",
        )
