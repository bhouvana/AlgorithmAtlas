"""Number of Divisors Sieve plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class NumberOfDivisorsSimulation(AlgorithmPlugin):
    """Count divisors for 1..n using a sieve."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="number-of-divisors",
            name="Number of Divisors (Sieve)",
            category="number-theory",
            visualization_type="ARRAY_BARS",
            description="Compute d(k) = number of divisors of k for all k ≤ n.",
            intuition=(
                "For each d from 1 to n, add 1 to divisor count of d, 2d, 3d, ... "
                "After all d processed: divs[k] = total number of divisors of k. "
                "Highly composite numbers (12, 24, 36...) will have the tallest bars."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("number-theory", "divisors", "sieve", "arithmetic-functions"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = int(params.inputs.get("size", 30))
        return SortState(
            array=tuple([1] * n),  # all 0 divisors shown as 1
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"DivisorSieve n={n}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))
        divs = [0] * (n + 1)  # divs[1..n]

        for d in range(1, n + 1):
            for multiple in range(d, n + 1, d):
                divs[multiple] += 1

            # Show current state (1-indexed, skip index 0)
            arr_raw = divs[1:n + 1]
            mx = max(arr_raw) or 1
            arr = tuple(max(1, min(99, v * 99 // mx)) for v in arr_raw)
            max_divs_idx = arr_raw.index(max(arr_raw)) if arr_raw else 0

            yield SortState(
                array=arr,
                comparing=(d - 1, d - 1),  # highlight current d
                last_swap=None,
                sorted_indices=frozenset(range(d)),  # d processed so far
                comparisons=d,
                swaps=max(arr_raw),
                description=(
                    f"d={d}: marked {n // d} multiples. "
                    f"Max divisors so far: {max(arr_raw)} (at {max_divs_idx + 1})"
                ),
            )

        arr_raw = divs[1:n + 1]
        mx = max(arr_raw) or 1
        arr = tuple(max(1, min(99, v * 99 // mx)) for v in arr_raw)
        most_idx = arr_raw.index(max(arr_raw))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=n,
            swaps=max(arr_raw),
            description=(
                f"Done: d({most_idx + 1}) = {arr_raw[most_idx]} divisors (max in [1,{n}])"
            ),
        )
