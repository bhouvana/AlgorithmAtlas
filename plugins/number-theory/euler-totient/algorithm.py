"""Euler's Totient Function plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_NUMBERS = [12, 15, 18, 20, 24, 28, 30, 36, 42, 45, 48, 50, 60, 72, 84, 90, 100]


class EulerTotientSimulation(AlgorithmPlugin):
    """
    Euler's Totient Function φ(n).

    DPState table rows (columns = prime factors found):
      row 0: prime factors p_i (padded with 0)
      row 1: n after dividing by p_i (running value)
      row 2: φ(n) after applying factor p_i (running value)
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="euler-totient",
            name="Euler's Totient Function",
            category="number-theory",
            visualization_type="MATRIX",
            description=(
                "Compute φ(n) — count of integers 1..n coprime to n — "
                "by factorizing n and applying φ(n) = n × ∏(1 - 1/p)."
            ),
            intuition=(
                "Trial-divide n by 2, then odd numbers. "
                "Each time p | n, multiply result by (p-1)/p. "
                "If a remainder > 1 remains, it's a prime factor."
            ),
            complexity_time_best="O(√n)",
            complexity_time_average="O(√n)",
            complexity_time_worst="O(√n)",
            complexity_space="O(1)",
            tags=("number-theory", "euler-totient", "phi", "coprime"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        n = _NUMBERS[params.seed % len(_NUMBERS)]
        # Precompute prime factors for table width
        temp = n
        factors = []
        p = 2
        while p * p <= temp:
            if temp % p == 0:
                factors.append(p)
                while temp % p == 0:
                    temp //= p
            p += 1
        if temp > 1:
            factors.append(temp)

        w = max(len(factors), 1)
        table = (
            tuple(factors) + (0,) * (w - len(factors)),
            tuple(n for _ in range(w)),
            tuple(n for _ in range(w)),
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"EulerTotient({n}): find φ({n})",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        n = int(initial_state.description.split("(")[1].split(")")[0])
        factors = [x for x in initial_state.table[0] if x > 0]
        w = len(factors)

        # Recompute step-by-step
        result = n
        temp = n
        running_n = [n] * w
        running_phi = [n] * w
        computed: set = set()

        for i, p in enumerate(factors):
            # Apply φ(n) = result * (p-1) / p
            result = result // p * (p - 1)
            while temp % p == 0:
                temp //= p
            running_n[i] = temp
            running_phi[i] = result
            computed.add((1, i))
            computed.add((2, i))

            yield DPState(
                table=(
                    tuple(factors) + (0,) * (w - len(factors)),
                    tuple(running_n),
                    tuple(running_phi),
                ),
                current_cell=(2, i),
                computed_cells=frozenset(computed),
                description=f"Factor p={p}: φ so far = {result}",
            )

        return DPState(
            table=(
                tuple(factors) + (0,) * (w - len(factors)),
                tuple(running_n),
                tuple(running_phi),
            ),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"φ({n}) = {result}",
        )
