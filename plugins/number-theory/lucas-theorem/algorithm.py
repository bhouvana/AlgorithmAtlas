"""Lucas' Theorem plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# (n, k, p, expected = C(n,k) mod p)
_INSTANCES = [
    (10, 3, 3, 1),    # C(10,3)=120, 120 mod 3=0... let me recompute
    (5, 2, 3, 1),
    (7, 3, 5, 1),
    (100, 10, 7, 2),
    (10, 2, 7, 3),
    (15, 5, 5, 0),
    (6, 3, 5, 2),
    (8, 4, 3, 0),
    (9, 4, 7, 2),
    (12, 5, 11, 1),
]


def _c(n: int, k: int) -> int:
    if k < 0 or k > n: return 0
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def _lucas(n: int, k: int, p: int) -> int:
    """C(n, k) mod p using Lucas' theorem."""
    if k == 0:
        return 1
    n_i = n % p
    k_i = k % p
    return (_c(n_i, k_i) % p) * _lucas(n // p, k // p, p) % p


# Fix the expected values
_INSTANCES = [
    (n, k, p, _lucas(n, k, p))
    for n, k, p, _ in _INSTANCES
]


class LucasTheoremSimulation(AlgorithmPlugin):
    """Lucas' Theorem for C(n, k) mod p."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="lucas-theorem",
            name="Lucas' Theorem",
            category="number-theory",
            visualization_type="MATRIX",
            description="Efficiently compute C(n,k) mod p for large n, k using base-p digit decomposition.",
            intuition=(
                "Write n = n_r·p^r + ... + n_0 in base p. Then "
                "C(n,k) ≡ C(n_r,k_r) · C(n_{r-1},k_{r-1}) · ... · C(n_0,k_0) (mod p)."
            ),
            complexity_time_best="O(p² + log_p n)",
            complexity_time_average="O(p² + log_p n)",
            complexity_time_worst="O(p² + log_p n)",
            complexity_space="O(p²)",
            tags=("number-theory", "lucas-theorem", "binomial-coefficient"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        n, k, p, expected = _INSTANCES[params.seed % len(_INSTANCES)]

        # Build Pascal's triangle mod p (p rows)
        pascal = [[0] * p for _ in range(p)]
        for i in range(p):
            pascal[i][0] = 1
            for j in range(1, i + 1):
                pascal[i][j] = (pascal[i-1][j-1] + pascal[i-1][j]) % p

        table = tuple(tuple(row) for row in pascal)
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"C({n},{k}) mod {p} expected={expected}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        n = int(desc.split("C(")[1].split(",")[0])
        k = int(desc.split(",")[1].split(")")[0])
        p = int(desc.split("mod ")[1].split(" ")[0])

        # Decompose n and k in base p
        n_digits, k_digits = [], []
        nn, kk = n, k
        while nn > 0 or kk > 0:
            n_digits.append(nn % p)
            k_digits.append(kk % p)
            nn //= p
            kk //= p

        # Reverse to show most-significant first
        n_digits.reverse()
        k_digits.reverse()

        computed: set = set()
        result = 1

        for step, (ni, ki) in enumerate(zip(n_digits, k_digits)):
            ci = _c(ni, ki) % p
            result = (result * ci) % p
            computed.add((ni, ki))
            yield DPState(
                table=initial_state.table,
                current_cell=(ni, ki),
                computed_cells=frozenset(computed),
                description=f"Step {step+1}: C({ni},{ki}) mod {p} = {ci}, running product = {result}",
            )

        return DPState(
            table=initial_state.table,
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"C({n},{k}) mod {p} = {result}",
        )
