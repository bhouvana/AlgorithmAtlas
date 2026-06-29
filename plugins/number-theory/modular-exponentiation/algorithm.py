"""Modular Exponentiation plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class ModularExponentiationSimulation(AlgorithmPlugin):
    """
    Modular Exponentiation (fast power) — O(log exp).

    2-row table:
      row 0: bit index [k-1, k-2, ..., 1, 0]  (MSB to LSB of exponent)
      row 1: partial result at each bit position

    Encodes base, exp, mod in description: "ModExp(base,exp,mod)"
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="modular-exponentiation",
            name="Modular Exponentiation",
            category="number-theory",
            visualization_type="MATRIX",
            description=(
                "Compute (base^exp) mod m in O(log exp) multiplications "
                "using repeated squaring."
            ),
            intuition=(
                "Process bits of exp from MSB to LSB. "
                "Square the running result each step; multiply by base when the bit is 1."
            ),
            complexity_time_best="O(log exp)",
            complexity_time_average="O(log exp)",
            complexity_time_worst="O(log exp)",
            complexity_space="O(log exp)",
            tags=("number-theory", "modular-exponentiation", "fast-power"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        bits: int = max(4, min(params.inputs.get("array_size", 8), 12))
        base = rng.randint(2, 15)
        exp = rng.randint(1 << (bits - 1), (1 << bits) - 1)  # bits-bit number
        mod = rng.choice([97, 101, 103, 107, 109])  # small primes

        k = exp.bit_length()
        table = (
            tuple(range(k - 1, -1, -1)),   # bit positions MSB..LSB
            tuple(0 for _ in range(k)),     # partial results (filled in steps)
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"ModExp({base},{exp},{mod})",
        )

    def steps(
        self,
        initial_state: DPState,
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description  # "ModExp(base,exp,mod)"
        inner = desc[7:-1]
        parts = inner.split(",")
        base, exp, mod = int(parts[0]), int(parts[1]), int(parts[2])

        k = exp.bit_length()
        bits = [(exp >> i) & 1 for i in range(k - 1, -1, -1)]  # MSB to LSB

        result = 1
        partial: List[int] = []
        computed: set = set()

        for step, bit in enumerate(bits):
            result = (result * result) % mod
            if bit:
                result = (result * base) % mod
            partial.append(result)
            computed.add((1, step))

            table = (
                tuple(range(k - 1, -1, -1)),
                tuple(partial + [0] * (k - len(partial))),
            )
            action = f"square → {(partial[-1] * partial[-1] if step > 0 else 1) % mod}"
            if bit:
                action += f", bit=1: ×{base} → {result}"
            else:
                action += f", bit=0"

            yield DPState(
                table=table,
                current_cell=(1, step),
                computed_cells=frozenset(computed),
                description=f"bit[{k-1-step}]={bit}: {action} → result={result}",
            )

        final_table = (
            tuple(range(k - 1, -1, -1)),
            tuple(partial),
        )
        return DPState(
            table=final_table,
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Done: {base}^{exp} mod {mod} = {result}",
        )
