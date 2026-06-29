"""Fast Power (Exponentiation by Squaring) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_BASE = 2
_MOD = 1000


class FastPowerSimulation(AlgorithmPlugin):
    """Exponentiation by squaring: compute BASE^n mod MOD."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="fast-power",
            name="Fast Power (Exponentiation by Squaring)",
            category="divide-and-conquer",
            visualization_type="ARRAY_BARS",
            description=f"Compute {_BASE}^n mod {_MOD} in O(log n) multiplications.",
            intuition=(
                "Write n in binary. For each bit (MSB→LSB): square result. "
                "If bit=1, also multiply by base. "
                "Each step halves the remaining exponent."
            ),
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(log n)",
            tags=("divide-and-conquer", "fast-power", "modular-arithmetic", "binary"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = int(params.inputs.get("exponent", 27))
        bits = [(n >> i) & 1 for i in range(n.bit_length() - 1, -1, -1)]
        return SortState(
            array=tuple(bits),  # bit representation of n
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"FastPow: base={_BASE} exp={n} mod={_MOD} bits={bits}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        desc = initial_state.description
        n = int(re.search(r"exp=(\d+)", desc).group(1))
        bits = list(initial_state.array)
        nbits = len(bits)

        result = 1
        base = _BASE

        for i, bit in enumerate(bits):
            # Square
            result = (result * result) % _MOD

            mul_str = "sq"
            if bit == 1:
                result = (result * base) % _MOD
                mul_str += f"×{base}"

            yield SortState(
                array=tuple(bits),
                comparing=(i, i),
                last_swap=(i, i) if bit == 1 else None,
                sorted_indices=frozenset(range(i + 1)),
                comparisons=i + 1,
                swaps=result,
                description=(
                    f"bit[{i}]={bit} ({mul_str}): "
                    f"result={result}"
                ),
            )

        expected = pow(_BASE, n, _MOD)
        return SortState(
            array=tuple(bits),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(nbits)),
            comparisons=nbits,
            swaps=result,
            description=(
                f"{_BASE}^{n} mod {_MOD} = {result} "
                f"(verified: {expected}) in {nbits} steps"
            ),
        )
