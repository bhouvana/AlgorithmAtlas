"""Miller-Rabin Primality Test plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# Primes and composites to test
_CANDIDATES = [
    # (n, is_prime)
    (2, True), (3, True), (5, True), (7, True), (11, True), (13, True),
    (17, True), (19, True), (23, True), (29, True), (31, True), (37, True),
    (41, True), (43, True), (53, True), (97, True), (101, True),
    (997, True), (7919, True), (104729, True),
    (4, False), (9, False), (15, False), (21, False), (25, False),
    (49, False), (77, False), (91, False), (121, False), (341, False),
    (561, False),  # Carmichael number (fools Fermat but not Miller-Rabin)
]

_DETERMINISTIC_WITNESSES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]


def _decompose(n: int) -> Tuple[int, int]:
    """Return (r, d) such that n-1 = 2^r * d with d odd."""
    r, d = 0, n - 1
    while d % 2 == 0:
        d //= 2
        r += 1
    return r, d


def _miller_rabin_witness(n: int, a: int, r: int, d: int) -> bool:
    """Return True if a is a witness for n being COMPOSITE."""
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return False  # Not a witness (n might be prime)
    for _ in range(r - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return False
    return True  # a IS a witness — n is definitely composite


class MillerRabinSimulation(AlgorithmPlugin):
    """
    Miller-Rabin Primality Test.

    DPState table rows:
      row 0: witness values [a1, a2, ...]
      row 1: pow(a, d, n) for each witness
      row 2: result for each witness (0=passed, 1=composite_witness)

    Encodes "MillerRabin(n)" in description.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="miller-rabin",
            name="Miller-Rabin Primality Test",
            category="number-theory",
            visualization_type="MATRIX",
            description=(
                "Probabilistic primality test: decompose n-1 = 2^r*d "
                "and verify that no witness exposes n as composite."
            ),
            intuition=(
                "Write n-1 = 2^r * d (d odd). For each witness a, "
                "compute a^d mod n. If it's 1 or n-1, skip. Otherwise square r-1 times; "
                "if we never hit n-1, a proves n is composite."
            ),
            complexity_time_best="O(k log² n)",
            complexity_time_average="O(k log² n)",
            complexity_time_worst="O(k log² n)",
            complexity_space="O(1)",
            tags=("number-theory", "primality", "miller-rabin", "probabilistic"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n, is_prime = _CANDIDATES[params.seed % len(_CANDIDATES)]
        # Skip trivially small primes — start witnesses from safe values
        if n < 4:
            # n=2 or 3 — trivially prime, use dummy witness row
            table = (
                (2, 0, 0, 0, 0, 0),
                (1, 0, 0, 0, 0, 0),  # a^d mod n = 1 => passes
                (0, 0, 0, 0, 0, 0),
            )
            return DPState(
                table=table,
                current_cell=None,
                computed_cells=frozenset(),
                description=f"MillerRabin({n}): trivially PRIME (n < 4)",
            )
        r, d = _decompose(n)
        # Use up to 6 witnesses from the deterministic set (excluding n itself)
        witnesses = [a for a in _DETERMINISTIC_WITNESSES if 1 < a < n][:6]
        w = len(witnesses)
        pad = max(0, 6 - w)
        table = (
            tuple(witnesses) + (0,) * pad,
            tuple(pow(a, d, n) for a in witnesses) + (0,) * pad,
            tuple(0 for _ in range(6)),
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"MillerRabin({n}): n-1 = 2^{r} * {d}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        n = int(desc.split("(")[1].split(")")[0])
        # Handle trivial small primes
        if "trivially" in desc:
            yield DPState(
                table=initial_state.table,
                current_cell=(2, 0),
                computed_cells=frozenset([(2, 0)]),
                description=f"MillerRabin({n}) = PRIME (trivial)",
            )
            return DPState(
                table=initial_state.table,
                current_cell=None,
                computed_cells=frozenset([(2, 0)]),
                description=f"MillerRabin({n}) = PRIME (probable)",
            )
        r, d = _decompose(n)
        witnesses_row = initial_state.table[0]
        witnesses = [a for a in witnesses_row if a > 0]
        w = len(witnesses)

        table = [list(initial_state.table[0]), list(initial_state.table[1]), list(initial_state.table[2])]
        computed: set = set()
        is_composite = False

        for i, a in enumerate(witnesses):
            x = pow(a, d, n)
            table[1][i] = x
            is_witness = _miller_rabin_witness(n, a, r, d)
            table[2][i] = 1 if is_witness else 0
            computed.add((1, i))
            computed.add((2, i))

            if is_witness:
                is_composite = True
                yield DPState(
                    table=tuple(tuple(row) for row in table),
                    current_cell=(2, i),
                    computed_cells=frozenset(computed),
                    description=f"Witness a={a}: a^d mod n={x}, COMPOSITE confirmed",
                )
                break
            else:
                yield DPState(
                    table=tuple(tuple(row) for row in table),
                    current_cell=(2, i),
                    computed_cells=frozenset(computed),
                    description=f"Witness a={a}: a^d mod n={x}, passed",
                )

        verdict = "COMPOSITE" if is_composite else "PRIME (probable)"
        return DPState(
            table=tuple(tuple(row) for row in table),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"MillerRabin({n}) = {verdict}",
        )
