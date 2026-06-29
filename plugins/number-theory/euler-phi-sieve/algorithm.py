"""Euler's Totient Sieve plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class EulerPhiSieveSimulation(AlgorithmPlugin):
    """Compute φ(i) for all i from 1 to n using a sieve."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="euler-phi-sieve",
            name="Euler's Totient Sieve",
            category="number-theory",
            visualization_type="ARRAY_BARS",
            description="Compute Euler's totient φ(n) for all n from 1 to N using a linear sieve.",
            intuition=(
                "φ(n) counts integers ≤ n coprime to n. "
                "Start with φ[i]=i. For each prime p, divide every multiple "
                "by the prime factor: φ[kp] *= (p-1)/p."
            ),
            complexity_time_best="O(n log log n)",
            complexity_time_average="O(n log log n)",
            complexity_time_worst="O(n log log n)",
            complexity_space="O(n)",
            tags=("number-theory", "euler-totient", "sieve", "prime"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = int(params.inputs.get("n", 30))
        phi = list(range(n + 1))  # phi[i] = i initially (index 0 unused)
        return SortState(
            array=tuple(phi[1:]),  # phi[1..n] as the visible array
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Totient sieve n={n}: phi[i]=i initially",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))

        phi = list(range(n + 1))  # phi[0..n], 0-indexed; display phi[1..n]
        prime_count = 0

        for i in range(2, n + 1):
            if phi[i] == i:
                # i is prime
                prime_count += 1
                for j in range(i, n + 1, i):
                    phi[j] -= phi[j] // i

                yield SortState(
                    array=tuple(phi[1:]),
                    comparing=(i - 1, i - 1),  # 0-indexed into display array
                    last_swap=None,
                    sorted_indices=frozenset(
                        k - 1 for k in range(2, n + 1) if phi[k] == k - 1
                    ),
                    comparisons=i,
                    swaps=prime_count,
                    description=(
                        f"Prime p={i}: updated {n // i} multiples. "
                        f"φ[{i}]={phi[i]}, primes so far={prime_count}"
                    ),
                )

        # Mark all primes in sorted_indices (primes have phi[p] = p-1)
        primes_idx = frozenset(k - 1 for k in range(2, n + 1) if phi[k] == k - 1)
        return SortState(
            array=tuple(phi[1:]),
            comparing=None,
            last_swap=None,
            sorted_indices=primes_idx,
            comparisons=n,
            swaps=prime_count,
            description=f"Done: φ(1..{n}) computed, {prime_count} primes found",
        )
