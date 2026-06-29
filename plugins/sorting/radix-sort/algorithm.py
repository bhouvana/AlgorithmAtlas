"""Radix Sort (LSD) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    SimulationParams,
    SortState,
)


class RadixSortSimulation(AlgorithmPlugin):
    """
    Radix Sort LSD (Least Significant Digit first) — O(nk) time, O(n+k) space.

    For each digit position, performs a stable counting sort on that digit.
    auxiliary_indices highlights the element being placed (yellow).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="radix-sort",
            name="Radix Sort (LSD)",
            category="sorting",
            visualization_type="ARRAY_BARS",
            description="Sort digit by digit, least significant first, using stable counting sort.",
            intuition=(
                "Sort by ones digit, then tens, then hundreds — each pass is stable, "
                "so the final order is correct."
            ),
            complexity_time_best="O(nk)",
            complexity_time_average="O(nk)",
            complexity_time_worst="O(nk)",
            complexity_space="O(n + k)",
            tags=("non-comparison", "stable", "integer", "linear", "lsd"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        rng = random.Random(params.seed)
        size: int = params.inputs.get("array_size", 20)
        max_val: int = params.inputs.get("max_value", 100)
        arr: List[int] = [rng.randint(1, max_val) for _ in range(size)]
        self._max_val: int = max_val
        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            auxiliary_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description="Ready to sort",
        )

    def steps(
        self,
        initial_state: SortState,
    ) -> Generator[SortState, None, SortState]:
        arr = list(initial_state.array)
        n = len(arr)
        max_val = getattr(self, "_max_val", 100)
        swaps = 0

        num_digits = len(str(max_val))
        digit_names = ["ones", "tens", "hundreds", "thousands"]

        for digit_pass in range(num_digits):
            digit_base = 10 ** digit_pass
            digit_name = digit_names[min(digit_pass, 3)]

            yield SortState(
                array=tuple(arr),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(),
                auxiliary_indices=frozenset(),
                comparisons=0,
                swaps=swaps,
                description=f"Pass {digit_pass + 1}/{num_digits}: sorting by {digit_name} digit",
            )

            counts: List[int] = [0] * 10
            for idx, val in enumerate(arr):
                d = (val // digit_base) % 10
                counts[d] += 1
                yield SortState(
                    array=tuple(arr),
                    comparing=None,
                    last_swap=None,
                    sorted_indices=frozenset(),
                    auxiliary_indices=frozenset({idx}),
                    comparisons=0,
                    swaps=swaps,
                    description=f"{digit_name} digit of {val} = {d} (bucket {d})",
                )

            for i in range(1, 10):
                counts[i] += counts[i - 1]

            output: List[int] = [0] * n
            for idx in range(n - 1, -1, -1):
                val = arr[idx]
                d = (val // digit_base) % 10
                counts[d] -= 1
                output[counts[d]] = val
                swaps += 1
                yield SortState(
                    array=tuple(output),
                    comparing=None,
                    last_swap=(counts[d], counts[d]),
                    sorted_indices=frozenset(),
                    auxiliary_indices=frozenset({counts[d]}),
                    comparisons=0,
                    swaps=swaps,
                    description=f"Placing {val} (digit {d}) at position {counts[d]}",
                )

            arr = output

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            auxiliary_indices=frozenset(),
            comparisons=0,
            swaps=swaps,
            description=f"Sorted! 0 comparisons, {swaps} writes across {num_digits} passes",
        )
