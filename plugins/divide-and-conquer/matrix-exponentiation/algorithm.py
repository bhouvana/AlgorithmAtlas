"""Matrix Exponentiation plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_MOD = 10 ** 9 + 7


def _mat_mul(A, B):
    return [
        [(A[0][0]*B[0][0] + A[0][1]*B[1][0]) % _MOD,
         (A[0][0]*B[0][1] + A[0][1]*B[1][1]) % _MOD],
        [(A[1][0]*B[0][0] + A[1][1]*B[1][0]) % _MOD,
         (A[1][0]*B[0][1] + A[1][1]*B[1][1]) % _MOD],
    ]


def _identity():
    return [[1, 0], [0, 1]]


def _fib_matrix():
    return [[1, 1], [1, 0]]


def _fib_naive(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


class MatrixExponentiationSimulation(AlgorithmPlugin):
    """Fibonacci via matrix fast power in O(log n)."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="matrix-exponentiation",
            name="Matrix Exponentiation (Fibonacci)",
            category="divide-and-conquer",
            visualization_type="ARRAY_BARS",
            description="Compute F(n) via [[1,1],[1,0]]^n in O(log n) matrix multiplications.",
            intuition=(
                "M = [[1,1],[1,0]]. M^n[0][1] = F(n). "
                "Use binary exponentiation: square M at each bit, multiply if bit=1. "
                "O(log n) matrix multiplications total."
            ),
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(log n)",
            tags=("divide-and-conquer", "matrix-exponentiation", "fibonacci", "fast-power"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = int(params.inputs.get("exponent", 15))
        M = _fib_matrix()
        # Show initial matrix as 4 bars
        arr = tuple([M[0][0], M[0][1], M[1][0], M[1][1]])
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"MatrixExp n={n}: compute F({n}) via M^{n}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))
        bits = [(n >> i) & 1 for i in range(n.bit_length() - 1, -1, -1)]
        nbits = len(bits)

        result = _identity()
        base = _fib_matrix()
        mults = 0

        for i, bit in enumerate(bits):
            # Square result
            result = _mat_mul(result, result)
            if bit == 1:
                result = _mat_mul(result, base)
                mults += 1

            # Display as 4-bar array (scale to 1-99)
            flat = [result[0][0], result[0][1], result[1][0], result[1][1]]
            mx = max(flat) or 1
            arr = tuple(max(1, min(99, v * 99 // mx)) for v in flat)
            fib_n = result[0][1]  # M^n[0][1] = F(n)
            yield SortState(
                array=arr,
                comparing=(i, i),
                last_swap=(i, i) if bit == 1 else None,
                sorted_indices=frozenset(range(i + 1)),
                comparisons=i + 1,
                swaps=fib_n % 10000,  # last 4 digits
                description=(
                    f"bit[{i}]={bit}: "
                    f"M^? = [[{result[0][0]},{result[0][1]}],[{result[1][0]},{result[1][1]}]]"
                ),
            )

        fib_n = result[0][1]
        expected = _fib_naive(n)
        flat = [result[0][0], result[0][1], result[1][0], result[1][1]]
        mx = max(flat) or 1
        arr = tuple(max(1, min(99, v * 99 // mx)) for v in flat)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(nbits)),
            comparisons=nbits,
            swaps=fib_n % 10000,
            description=(
                f"F({n}) = {fib_n} "
                f"(verified: {expected % _MOD}) "
                f"in {nbits} steps"
            ),
        )
