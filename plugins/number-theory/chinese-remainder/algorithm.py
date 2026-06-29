"""Chinese Remainder Theorem plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# (remainders, moduli, solution)
_INSTANCES = [
    ([2, 3, 2], [3, 5, 7], 23),
    ([1, 4, 6], [2, 5, 7], 69),
    ([0, 3, 4], [3, 7, 5], 24),
    ([2, 0], [3, 5], 5),
    ([1, 2, 3], [5, 7, 9], 156),
    ([3, 2, 1], [5, 7, 11], 23),
    ([0, 0, 1], [2, 3, 5], 6),
    ([1, 1, 1], [2, 3, 5], 1),
    ([2, 2], [3, 5], 2),
    ([4, 3, 2], [5, 7, 9], 164),
]


def _ext_gcd(a: int, b: int):
    """Extended Euclidean: returns (g, x, y) s.t. a*x + b*y = g."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = _ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def _mod_inverse(a: int, m: int) -> int:
    """Modular inverse of a mod m."""
    _, x, _ = _ext_gcd(a % m, m)
    return x % m


def _crt(remainders: list, moduli: list) -> int:
    M = 1
    for m in moduli:
        M *= m
    x = 0
    for r, m in zip(remainders, moduli):
        Mi = M // m
        yi = _mod_inverse(Mi, m)
        x += r * Mi * yi
    return x % M


class ChineseRemainderSimulation(AlgorithmPlugin):
    """Chinese Remainder Theorem."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="chinese-remainder",
            name="Chinese Remainder Theorem",
            category="number-theory",
            visualization_type="MATRIX",
            description="Solve a system of modular congruences: x ≡ r_i (mod m_i).",
            intuition=(
                "Compute M = ∏m_i. For each (r_i, m_i): M_i = M/m_i, y_i = M_i⁻¹ mod m_i. "
                "Solution x = (∑ r_i·M_i·y_i) mod M."
            ),
            complexity_time_best="O(n log max_m)",
            complexity_time_average="O(n log max_m)",
            complexity_time_worst="O(n log max_m)",
            complexity_space="O(n)",
            tags=("number-theory", "chinese-remainder", "modular-arithmetic"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        remainders, moduli, expected = _INSTANCES[params.seed % len(_INSTANCES)]
        n = len(moduli)
        # Rows: remainders row, moduli row, Mi row, yi row (4 rows × n cols)
        M = 1
        for m in moduli:
            M *= m
        Mi_vals = [M // m for m in moduli]
        yi_vals = [_mod_inverse(Mi, m) for Mi, m in zip(Mi_vals, moduli)]
        table = (
            tuple(remainders),
            tuple(moduli),
            tuple(Mi_vals),
            tuple(yi_vals),
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"CRT: r={remainders} m={moduli} M={M} expected={expected}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        expected_val = int(desc.split("expected=")[1])
        idx = next((i for i, inst in enumerate(_INSTANCES) if inst[2] == expected_val), 0)
        remainders, moduli, expected = _INSTANCES[idx]
        n = len(moduli)

        M = 1
        for m in moduli:
            M *= m

        Mi_vals = [M // m for m in moduli]
        yi_vals = [_mod_inverse(Mi, m) for Mi, m in zip(Mi_vals, moduli)]
        contributions = [r * Mi * yi for r, Mi, yi in zip(remainders, Mi_vals, yi_vals)]
        computed: set = set()
        x = 0

        for i in range(n):
            computed.add((0, i))
            computed.add((1, i))
            computed.add((2, i))
            computed.add((3, i))
            x += contributions[i]
            yield DPState(
                table=initial_state.table,
                current_cell=(0, i),
                computed_cells=frozenset(computed),
                description=(
                    f"i={i}: r={remainders[i]} m={moduli[i]} "
                    f"M_i={Mi_vals[i]} y_i={yi_vals[i]} "
                    f"contribution={contributions[i]} running_x={x}"
                ),
            )

        result = x % M
        return DPState(
            table=initial_state.table,
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"x = {x} mod {M} = {result}",
        )
