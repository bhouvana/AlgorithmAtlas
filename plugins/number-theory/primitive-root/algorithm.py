"""Primitive Root Finder plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_PRIMES = [7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def _prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def _is_primitive_root(g, p):
    phi = p - 1
    for q in _prime_factors(phi):
        if pow(g, phi // q, p) == 1:
            return False
    return True


def _find_primitive_root(p):
    for g in range(2, p):
        if _is_primitive_root(g, p):
            return g
    return -1


class PrimitiveRootSimulation(AlgorithmPlugin):
    """Primitive root search visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="primitive-root",
            name="Primitive Root Finder",
            category="number-theory",
            visualization_type="ARRAY_BARS",
            description="Find smallest primitive root mod prime p.",
            intuition=(
                "g is a primitive root if {g^1, g^2, ..., g^(p-1)} = {1..p-1}. "
                "Equivalently: g^((p-1)/q) ≢ 1 mod p for all prime q | (p-1). "
                "Bar = g^k mod p for k=1..p-1, showing cycle length."
            ),
            complexity_time_best="O(√p)",
            complexity_time_average="O(p^0.25 log p)",
            complexity_time_worst="O(p)",
            complexity_space="O(log p)",
            tags=("number-theory", "primitive-root", "modular-arithmetic", "group-theory"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        p = int(params.inputs.get("size", 41))
        if p not in _PRIMES:
            p = _PRIMES[params.seed % len(_PRIMES)]
        arr = tuple(1 for _ in range(p - 1))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"PrimRoot p={p}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        p = int(re.search(r"p=(\d+)", initial_state.description).group(1))
        phi = p - 1
        factors = _prime_factors(phi)

        # Try each candidate g
        for g in range(2, p):
            powers = [pow(g, k, p) for k in range(1, p)]
            mx = max(powers) or 1
            arr = tuple(max(1, min(99, v * 99 // mx)) for v in powers)

            is_prim = _is_primitive_root(g, p)
            yield SortState(
                array=arr,
                comparing=(g - 2, g - 2),
                last_swap=(0, len(powers) - 1) if is_prim else None,
                sorted_indices=frozenset(range(phi)) if is_prim else frozenset(),
                comparisons=g - 1,
                swaps=g if is_prim else 0,
                description=(
                    f"g={g}: {'PRIMITIVE ROOT!' if is_prim else f'order={len(set(powers))}'}"
                ),
            )
            if is_prim:
                break

        root = _find_primitive_root(p)
        powers = [pow(root, k, p) for k in range(1, p)]
        mx = max(powers)
        arr = tuple(max(1, min(99, v * 99 // mx)) for v in powers)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(phi)),
            comparisons=root - 1,
            swaps=root,
            description=f"Smallest primitive root of {p} is g={root}. Generates all {phi} residues.",
        )
