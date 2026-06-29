"""Collatz Sequence plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_MAX_STEPS = 40  # cap sequence for display


def _collatz_seq(n):
    seq = [n]
    while n != 1 and len(seq) < _MAX_STEPS:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        seq.append(n)
    return seq


class CollatzSimulation(AlgorithmPlugin):
    """Collatz sequence visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="collatz",
            name="Collatz Sequence",
            category="number-theory",
            visualization_type="ARRAY_BARS",
            description="Compute Collatz sequence from n until reaching 1.",
            intuition=(
                "Even: halve. Odd: triple and add one. "
                "Always reaches 1 (experimentally proven for all tested values). "
                "Stopping time varies wildly — n=27 takes 111 steps!"
            ),
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(unknown)",
            complexity_space="O(steps)",
            tags=("number-theory", "collatz", "sequence", "conjecture"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = int(params.inputs.get("size", 27))
        seq = _collatz_seq(n)
        mx = max(seq)
        arr = tuple(max(1, min(99, v * 99 // mx)) for v in seq)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=n,
            description=f"Collatz n={n} steps={len(seq)-1}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))
        seq = _collatz_seq(n)
        mx = max(seq)

        for i in range(1, len(seq)):
            val = seq[i]
            arr = tuple(max(1, min(99, v * 99 // mx)) for v in seq)
            is_even = seq[i - 1] % 2 == 0
            yield SortState(
                array=arr,
                comparing=(i, i),
                last_swap=(i - 1, i) if not is_even else None,  # odd step is dramatic
                sorted_indices=frozenset(range(i + 1)),
                comparisons=i,
                swaps=val,
                description=(
                    f"Step {i}: {seq[i-1]}→{val} "
                    f"({'÷2' if is_even else '×3+1'})"
                ),
            )

        return SortState(
            array=initial_state.array,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(seq))),
            comparisons=len(seq) - 1,
            swaps=len(seq) - 1,
            description=(
                f"Collatz({n}) reached 1 in {len(seq)-1} steps. "
                f"Max value: {mx}"
            ),
        )
