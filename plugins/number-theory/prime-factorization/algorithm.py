"""Prime Factorization plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_NUMBERS = [12, 30, 60, 84, 90, 100, 120, 210, 360, 420,
            504, 630, 720, 840, 900, 1260, 2310, 30030]


class PrimeFactorizationSimulation(AlgorithmPlugin):
    """
    Prime Factorization — trial division O(√n).

    DPState table rows:
      row 0: divisors tried [p1, p2, p3, ...] (padded)
      row 1: exponents [e1, e2, e3, ...] corresponding to each prime
      row 2: running quotient after dividing by each prime
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="prime-factorization",
            name="Prime Factorization",
            category="number-theory",
            visualization_type="MATRIX",
            description=(
                "Decompose n into prime factors using trial division: "
                "divide by 2, then odd numbers up to √n."
            ),
            intuition=(
                "Divide n repeatedly by 2, then by odd numbers starting at 3. "
                "Each time p | n, record it (with exponent). "
                "If n > 1 after the loop, n itself is prime."
            ),
            complexity_time_best="O(√n)",
            complexity_time_average="O(√n)",
            complexity_time_worst="O(√n)",
            complexity_space="O(log n)",
            tags=("number-theory", "factorization", "primes", "trial-division"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        n = _NUMBERS[params.seed % len(_NUMBERS)]
        # Precompute factors to size table
        temp = n
        factors_list = []
        p = 2
        while p * p <= temp:
            if temp % p == 0:
                exp = 0
                while temp % p == 0:
                    exp += 1
                    temp //= p
                factors_list.append((p, exp))
            p += 1 if p == 2 else 2
        if temp > 1:
            factors_list.append((temp, 1))

        w = max(len(factors_list), 1)
        table = (
            tuple(f[0] for f in factors_list) + (0,) * (w - len(factors_list)),
            tuple(f[1] for f in factors_list) + (0,) * (w - len(factors_list)),
            tuple(n for _ in range(w)),
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Factor({n}): begin trial division",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        n = int(initial_state.description.split("(")[1].split(")")[0])
        primes = [x for x in initial_state.table[0] if x > 0]
        exponents = [x for x in initial_state.table[1] if x > 0]
        w = len(primes)
        quotients = [n] * w
        computed: set = set()

        running = n
        for i, (p, e) in enumerate(zip(primes, exponents)):
            running //= p ** e
            quotients[i] = running
            computed.add((1, i))
            computed.add((2, i))
            yield DPState(
                table=(
                    tuple(primes),
                    tuple(exponents),
                    tuple(quotients),
                ),
                current_cell=(2, i),
                computed_cells=frozenset(computed),
                description=f"Factor {p}^{e}: {n if i==0 else 'quotient'} ÷ {p}^{e} = {running}",
            )

        factorization = " × ".join(
            f"{p}^{e}" if e > 1 else str(p) for p, e in zip(primes, exponents)
        )
        return DPState(
            table=initial_state.table,
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"{n} = {factorization}",
        )
