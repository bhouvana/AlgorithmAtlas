"""Euclidean GCD plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class EuclideanGCDSimulation(AlgorithmPlugin):
    """
    Euclidean GCD — O(log min(a,b)).

    Uses SortState with a 2-element array [a, b].
    comparing = (0, 1) while active.
    sorted_indices: {1} when swapping (showing b becomes the new a).
    sorted_indices: {0, 1} when GCD is found.
    description shows the step.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="gcd-euclidean",
            name="Euclidean GCD",
            category="number-theory",
            visualization_type="ARRAY_BARS",
            description="Finds the GCD of two numbers by repeatedly replacing the larger with (a mod b).",
            intuition="gcd(a, b) = gcd(b, a mod b). The remainder shrinks each step until zero. The two bars show a and b converging toward their GCD.",
            complexity_time_best="O(log min(a,b))",
            complexity_time_average="O(log min(a,b))",
            complexity_time_worst="O(log min(a,b))",
            complexity_space="O(1)",
            tags=("number-theory", "math", "gcd", "euclidean"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        a = max(10, min(params.inputs.get("a", 48), 200))
        b = max(10, min(params.inputs.get("b", 18), 200))
        return SortState(
            array=(a, b),
            comparing=(0, 1),
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"GCD({a}, {b}): start",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        a, b = initial_state.array
        comparisons = 0
        swaps = 0

        while b != 0:
            comparisons += 1
            remainder = a % b
            yield SortState(
                array=(a, b),
                comparing=(0, 1),
                last_swap=None,
                sorted_indices=frozenset(),
                comparisons=comparisons,
                swaps=swaps,
                description=f"GCD({a}, {b}): {a} mod {b} = {remainder}",
            )
            a, b = b, remainder
            swaps += 1
            yield SortState(
                array=(a, b),
                comparing=None,
                last_swap=(0, 1),
                sorted_indices=frozenset({1}) if b > 0 else frozenset(),
                comparisons=comparisons,
                swaps=swaps,
                description=f"Step → ({a}, {b})" + (f" — continue" if b > 0 else " — b=0, done"),
            )

        return SortState(
            array=(a, 0),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset({0, 1}),
            comparisons=comparisons,
            swaps=swaps,
            description=f"GCD = {a} (b reached 0 after {comparisons} steps)",
        )
