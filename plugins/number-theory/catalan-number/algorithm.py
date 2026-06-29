"""Catalan Numbers plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Known Catalan numbers: C(0)=1, C(1)=1, C(2)=2, C(3)=5, C(4)=14, ...
_CATALAN = [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796]


def _scale(vals: list) -> tuple:
    """Scale Catalan numbers to 1-99 bar heights."""
    mx = max(vals) if vals else 1
    return tuple(max(1, int(v * 99 // mx)) for v in vals)


class CatalanNumberSimulation(AlgorithmPlugin):
    """Compute the first n+1 Catalan numbers via DP recurrence."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="catalan-number",
            name="Catalan Numbers",
            category="number-theory",
            visualization_type="ARRAY_BARS",
            description="Compute the first n Catalan numbers using C(n) = Σ C(i)·C(n-1-i).",
            intuition=(
                "C(n) counts: valid bracket sequences, BSTs on n nodes, "
                "non-crossing partitions, polygon triangulations, and more. "
                "The recurrence splits at each possible middle position."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n)",
            tags=("number-theory", "catalan", "combinatorics", "dynamic-programming"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = int(params.inputs.get("n", 8))
        initial = [0] * (n + 1)
        initial[0] = 1
        return SortState(
            array=tuple(initial),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([0]),
            comparisons=0,
            swaps=1,
            description=f"Catalan n={n}: C(0)=1",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))
        cat = [0] * (n + 1)
        cat[0] = 1

        for k in range(1, n + 1):
            total = 0
            for i in range(k):
                total += cat[i] * cat[k - 1 - i]
            cat[k] = total

            scaled = _scale(cat)
            yield SortState(
                array=scaled,
                comparing=(k, k),
                last_swap=None,
                sorted_indices=frozenset(range(k + 1)),
                comparisons=k * k,
                swaps=k + 1,
                description=f"C({k}) = {total} (sum of {k} products)",
            )

        scaled = _scale(cat)
        return SortState(
            array=scaled,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n + 1)),
            comparisons=n * n,
            swaps=n + 1,
            description=(
                f"Done: C(0..{n}) = {cat[:n+1]}"
            ),
        )
