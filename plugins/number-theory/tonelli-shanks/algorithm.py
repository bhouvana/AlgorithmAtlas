"""Tonelli-Shanks (modular square root) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

# Find x such that x^2 ≡ N (mod P)
_N_VAL = 5
_P_VAL = 41   # prime; sqrt(5) mod 41 = 13 (13^2=169=4*41+5)


def _pow_mod(base, exp, mod):
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = result * base % mod
        base = base * base % mod
        exp >>= 1
    return result


class TonelliShanksSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="tonelli-shanks",
            name="Tonelli-Shanks Algorithm",
            category="number-theory",
            visualization_type="MATRIX",
            description="Compute the modular square root: find x with x² ≡ n (mod p).",
            intuition=(
                "Write p−1 = Q·2^S. Find quadratic non-residue z. "
                "Track (M, c, t, R) and halve the exponent M at each step "
                "until t=1, at which point R is the answer."
            ),
            complexity_time_best="O(log² p)",
            complexity_time_average="O(log² p)",
            complexity_time_worst="O(log² p)",
            complexity_space="O(1)",
            tags=("number-theory", "tonelli-shanks", "modular-arithmetic", "square-root", "prime"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        # Table: single row [n, p, Q, S, z, M, c, t, R]
        # Start with placeholder zeros for computed fields
        return DPState(
            table=((0, 0, 0, 0, 0, 0, 0, 0, 0),),
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Find x: x² ≡ {_N_VAL} (mod {_P_VAL})",
        )

    def steps(self, initial_state: DPState) -> Generator[DPState, None, DPState]:
        n, p = _N_VAL, _P_VAL
        computed: set = set()

        # Step 1: Euler's criterion — check n is a QR mod p
        euler = _pow_mod(n, (p - 1) // 2, p)
        computed.add((0, 0))
        yield DPState(
            table=((n, p, 0, 0, 0, 0, 0, 0, 0),),
            current_cell=(0, 0),
            computed_cells=frozenset(computed),
            description=f"Euler criterion: {n}^((p-1)/2) = {euler} mod {p} (1 = QR)",
        )

        # Step 2: Factor p-1 = Q * 2^S
        Q, S = p - 1, 0
        while Q % 2 == 0:
            Q //= 2
            S += 1
        computed.add((0, 1))
        computed.add((0, 2))
        yield DPState(
            table=((n, p, Q, S, 0, 0, 0, 0, 0),),
            current_cell=(0, 2),
            computed_cells=frozenset(computed),
            description=f"p-1 = {p-1} = {Q} × 2^{S}  (Q={Q}, S={S})",
        )

        # Step 3: Find quadratic non-residue z
        z = 2
        while _pow_mod(z, (p - 1) // 2, p) == 1:
            z += 1
        computed.add((0, 3))
        computed.add((0, 4))
        yield DPState(
            table=((n, p, Q, S, z, 0, 0, 0, 0),),
            current_cell=(0, 4),
            computed_cells=frozenset(computed),
            description=f"Smallest QNR z = {z}  ({z}^((p-1)/2) = {_pow_mod(z,(p-1)//2,p)} ≠ 1)",
        )

        # Step 4: Initialise M, c, t, R
        M = S
        c = _pow_mod(z, Q, p)
        t = _pow_mod(n, Q, p)
        R = _pow_mod(n, (Q + 1) // 2, p)
        computed.update({(0, 5), (0, 6), (0, 7), (0, 8)})
        yield DPState(
            table=((n, p, Q, S, z, M, c, t, R),),
            current_cell=(0, 5),
            computed_cells=frozenset(computed),
            description=f"Init: M={M} c={c} t={t} R={R}",
        )

        iteration = 0
        while t != 1:
            iteration += 1
            # Find least i > 0 such that t^(2^i) ≡ 1 (mod p)
            i, tmp = 1, t * t % p
            while tmp != 1:
                tmp = tmp * tmp % p
                i += 1
            b = _pow_mod(c, 1 << (M - i - 1), p)
            R = R * b % p
            t = t * b * b % p
            c = b * b % p
            M = i
            yield DPState(
                table=((n, p, Q, S, z, M, c, t, R),),
                current_cell=(0, 8),
                computed_cells=frozenset(computed),
                description=(
                    f"Iter {iteration}: i={i} b={b} → R={R} t={t} c={c} M={M}"
                ),
            )

        final = DPState(
            table=((n, p, Q, S, z, M, c, t, R),),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"√{n} mod {p} = {R}  (verify: {R}²={R*R%p} ≡ {n} mod {p})",
        )
        yield final
        return final
