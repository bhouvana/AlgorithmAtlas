"""Goldbach's Conjecture plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


def _sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return is_prime


def _goldbach_pairs(n, is_prime):
    pairs = []
    for p in range(2, n // 2 + 1):
        if is_prime[p] and is_prime[n - p]:
            pairs.append((p, n - p))
    return pairs


class GoldbachSimulation(AlgorithmPlugin):
    """Goldbach conjecture verification visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="goldbach",
            name="Goldbach's Conjecture",
            category="number-theory",
            visualization_type="ARRAY_BARS",
            description="Verify every even n > 2 is the sum of two primes.",
            intuition=(
                "Sieve primes up to N. For each even 4, 6, ..., N, "
                "count prime pairs (p, q) with p+q=n. "
                "The bar height shows number of decompositions."
            ),
            complexity_time_best="O(n log log n)",
            complexity_time_average="O(n log log n)",
            complexity_time_worst="O(n log log n)",
            complexity_space="O(n)",
            tags=("number-theory", "goldbach", "primes", "conjecture", "sieve"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = int(params.inputs.get("size", 40))
        # Round down to even
        if n % 2 != 0:
            n -= 1
        evens = list(range(4, n + 1, 2))
        arr = tuple(1 for _ in evens)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Goldbach n={n}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))
        is_prime = _sieve(n)
        evens = list(range(4, n + 1, 2))
        pair_counts = []

        for idx, even in enumerate(evens):
            pairs = _goldbach_pairs(even, is_prime)
            pair_counts.append(len(pairs))
            mx = max(pair_counts) or 1
            arr = tuple(max(1, min(99, c * 99 // mx)) for c in pair_counts) + \
                  tuple(1 for _ in range(len(evens) - idx - 1))
            p, q = pairs[0]
            yield SortState(
                array=arr,
                comparing=(idx, idx),
                last_swap=(idx, idx) if len(pairs) > 1 else None,
                sorted_indices=frozenset(range(idx + 1)),
                comparisons=idx + 1,
                swaps=len(pairs),
                description=f"{even} = {p}+{q} ({len(pairs)} pair{'s' if len(pairs)>1 else ''})",
            )

        mx = max(pair_counts) or 1
        arr = tuple(max(1, min(99, c * 99 // mx)) for c in pair_counts)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(evens))),
            comparisons=len(evens),
            swaps=sum(pair_counts),
            description=f"All {len(evens)} even numbers verified. Max pairs: {mx}",
        )
