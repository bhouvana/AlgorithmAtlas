"""Extended Euclidean Algorithm plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class ExtendedEuclideanSimulation(AlgorithmPlugin):
    """
    Extended Euclidean Algorithm — O(log min(a,b)).

    4-row table showing each step of the algorithm:
      row 0: r (remainder)
      row 1: q (quotient at this step)
      row 2: s (Bézout coefficient for a)
      row 3: t (Bézout coefficient for b)

    Invariant: r[i] = s[i]*a + t[i]*b at every step.
    Encodes inputs in description: "ExtGCD(a,b)"
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="extended-euclidean",
            name="Extended Euclidean",
            category="number-theory",
            visualization_type="MATRIX",
            description=(
                "Compute GCD(a, b) and Bézout coefficients x, y "
                "such that ax + by = GCD(a, b)."
            ),
            intuition=(
                "Track how each remainder is a linear combination of a and b. "
                "When the remainder reaches 0, back-substitute to get coefficients. "
                "Used in modular inverse computation for RSA."
            ),
            complexity_time_best="O(log min(a,b))",
            complexity_time_average="O(log min(a,b))",
            complexity_time_worst="O(log min(a,b))",
            complexity_space="O(log min(a,b))",
            tags=("number-theory", "gcd", "bezout", "extended-euclidean"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        mag: int = max(3, min(params.inputs.get("array_size", 5), 8))
        # Pick two numbers in a range determined by mag
        hi = 10 ** mag
        lo = hi // 10
        a = rng.randint(lo, hi)
        b = rng.randint(lo // 2, a - 1)
        if b == 0:
            b = rng.randint(1, a - 1)
        # Ensure a >= b
        if a < b:
            a, b = b, a

        table = (
            (a, b) + (0,) * 10,   # row 0: remainders (padded)
            (0, 0) + (0,) * 10,   # row 1: quotients
            (1, 0) + (0,) * 10,   # row 2: s coefficients
            (0, 1) + (0,) * 10,   # row 3: t coefficients
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"ExtGCD({a},{b})",
        )

    def steps(
        self,
        initial_state: DPState,
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description  # "ExtGCD(a,b)"
        inner = desc[7:-1]
        a_orig, b_orig = [int(x) for x in inner.split(",")]

        # Extended Euclidean: iterative
        # r[i] = s[i]*a + t[i]*b
        r = [a_orig, b_orig]
        s = [1, 0]
        t = [0, 1]
        q_list = [0, 0]  # quotients (q_list[0] unused, q_list[i] = r[i-2] // r[i-1])

        computed: set = set()
        step = 1

        def make_table(r_, q_, s_, t_, width):
            pad = max(0, width - len(r_))
            return (
                tuple(r_) + (0,) * pad,
                tuple(q_) + (0,) * pad,
                tuple(s_) + (0,) * pad,
                tuple(t_) + (0,) * pad,
            )

        while r[-1] != 0:
            qi = r[-2] // r[-1]
            ri = r[-2] % r[-1]
            si = s[-2] - qi * s[-1]
            ti = t[-2] - qi * t[-1]

            r.append(ri)
            q_list.append(qi)
            s.append(si)
            t.append(ti)

            step += 1
            for row_idx in range(4):
                computed.add((row_idx, step - 1))

            width = max(len(r), 4)
            table = make_table(r, q_list, s, t, width)

            yield DPState(
                table=table,
                current_cell=(0, step - 1),
                computed_cells=frozenset(computed),
                description=(
                    f"Step {step-1}: {r[-3]} = {qi}×{r[-2] + qi * ri} + {ri}; "
                    f"s={si}, t={ti}"
                ),
            )

        gcd = r[-2]
        x = s[-2]
        y = t[-2]

        width = max(len(r), 4)
        table = make_table(r, q_list, s, t, width)
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(computed),
            description=(
                f"Done: GCD({a_orig},{b_orig})={gcd}; "
                f"{a_orig}×({x}) + {b_orig}×({y}) = {gcd}"
            ),
        )
