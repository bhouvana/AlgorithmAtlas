"""Sieve of Eratosthenes plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class SieveSimulation(AlgorithmPlugin):
    """
    Sieve of Eratosthenes — O(n log log n).

    Uses SortState where array = [2, 3, ..., N].
    sorted_indices: confirmed prime positions (green).
    auxiliary_indices: positions being marked composite (yellow).
    comparing: (prime_idx, multiple_idx) during sieving.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="sieve-of-eratosthenes",
            name="Sieve of Eratosthenes",
            category="number-theory",
            visualization_type="ARRAY_BARS",
            description="Finds all primes up to N by striking out multiples of each discovered prime.",
            intuition="The first unmarked number is always prime. Mark all its multiples composite. Repeat from p².",
            complexity_time_best="O(n log log n)",
            complexity_time_average="O(n log log n)",
            complexity_time_worst="O(n log log n)",
            complexity_space="O(n)",
            tags=("number-theory", "prime", "sieve", "math"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n: int = max(20, min(params.inputs.get("limit", 30), 50))
        # array[i] = i+2 (values 2..n), length = n-1
        array = tuple(range(2, n + 1))
        return SortState(
            array=array,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            auxiliary_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Sieve: find all primes ≤ {n}",
        )

    def steps(
        self, initial_state: SortState
    ) -> Generator[SortState, None, SortState]:
        array = list(initial_state.array)
        n = len(array)  # length = limit - 1; array[i] = i + 2
        composite: List[bool] = [False] * n  # composite[i] → array[i] is not prime
        primes: set = set()
        comparisons = 0

        def idx(val: int) -> int:
            return val - 2  # value v → index v-2

        i = 0
        while i < n:
            if composite[i]:
                i += 1
                continue
            # array[i] is prime
            p = array[i]
            primes.add(i)

            yield SortState(
                array=tuple(array),
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(primes),
                auxiliary_indices=frozenset(),
                comparisons=comparisons,
                swaps=0,
                description=f"{p} is prime — mark multiples from {p*p}",
            )

            # Mark multiples starting from p²
            multiple_indices: set = set()
            for j in range(p * p, array[-1] + 1, p):
                jidx = idx(j)
                if jidx < n and not composite[jidx]:
                    composite[jidx] = True
                    multiple_indices.add(jidx)
                    comparisons += 1

                    yield SortState(
                        array=tuple(array),
                        comparing=(i, jidx),
                        last_swap=None,
                        sorted_indices=frozenset(primes),
                        auxiliary_indices=frozenset(multiple_indices),
                        comparisons=comparisons,
                        swaps=0,
                        description=f"Mark {j} = {p}×{j//p} as composite",
                    )

            i += 1

        # Final state: all primes confirmed
        prime_indices = frozenset(k for k in range(n) if not composite[k])
        return SortState(
            array=tuple(array),
            comparing=None,
            last_swap=None,
            sorted_indices=prime_indices,
            auxiliary_indices=frozenset(),
            comparisons=comparisons,
            swaps=0,
            description=(
                f"Sieve complete: {len(prime_indices)} primes ≤ {array[-1]}: "
                + ", ".join(str(array[k]) for k in sorted(prime_indices))
            ),
        )
