"""Majority Element (Boyer-Moore Vote) plugin for Algorithm Atlas."""
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
    """Generate array with a clear majority element (>n/2 occurrences)."""
    majority_val = rng.randint(1, 9)
    majority_count = n // 2 + 1
    arr = [majority_val] * majority_count
    other_vals = [v for v in range(1, 10) if v != majority_val]
    for _ in range(n - majority_count):
        arr.append(rng.choice(other_vals))
    rng.shuffle(arr)
    return arr


class MajorityElementSimulation(AlgorithmPlugin):
    """Boyer-Moore Majority Vote Algorithm."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="majority-element",
            name="Majority Element (Boyer-Moore Vote)",
            category="divide-and-conquer",
            visualization_type="ARRAY_BARS",
            description="Find the element appearing more than n/2 times in O(n) time and O(1) space.",
            intuition=(
                "Keep a candidate and count. Each mismatch 'cancels' one prior vote. "
                "The majority element always has more votes than all others combined."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("divide-and-conquer", "majority-vote", "boyer-moore", "linear"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 9))
        arr = _make_array(rng, n)
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Boyer-Moore vote: find majority in {arr}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        candidate = arr[0]
        count = 1
        comparisons = 0

        # Phase 1: Find candidate
        for i in range(1, n):
            comparisons += 1
            if arr[i] == candidate:
                count += 1
                action = f"match: count={count}"
            else:
                count -= 1
                action = f"cancel: count={count}"
                if count == 0:
                    candidate = arr[i]
                    count = 1
                    action = f"new candidate={candidate}"

            yield SortState(
                array=tuple(arr),
                comparing=(0, i),  # i vs current candidate position
                last_swap=None,
                sorted_indices=frozenset(),
                comparisons=comparisons,
                swaps=candidate,  # reuse swaps as candidate value
                description=f"i={i} arr[i]={arr[i]} candidate={candidate} count={count} ({action})",
            )

        # Phase 2: Verify (count occurrences)
        actual_count = arr.count(candidate)

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(i for i, v in enumerate(arr) if v == candidate),
            comparisons=comparisons,
            swaps=actual_count,
            description=f"Majority element = {candidate} (appears {actual_count} times)",
        )
