"""Polynomial Multiplication (FFT) plugin for Algorithm Atlas."""
from __future__ import annotations

import cmath
import math
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Fixed polynomials: A * B
_POLY_PAIRS = [
    ([1, 2, 3], [4, 5]),            # (1+2x+3x²)(4+5x)
    ([1, 1], [1, 1]),                # (1+x)²
    ([1, 3, 2], [2, 1]),             # (1+3x+2x²)(2+x)
    ([1, 0, 1], [1, 0, 1]),          # (1+x²)²
    ([2, 3, 1, 4], [1, 2, 1]),       # degree 3 × degree 2
]


def _fft(a, invert=False):
    n = len(a)
    if n == 1:
        return a
    even = _fft(a[::2], invert)
    odd = _fft(a[1::2], invert)
    angle = 2 * math.pi / n * (-1 if invert else 1)
    w = complex(1)
    wn = cmath.exp(complex(0, angle))
    result = [0] * n
    for k in range(n // 2):
        result[k] = even[k] + w * odd[k]
        result[k + n // 2] = even[k] - w * odd[k]
        w *= wn
    if invert:
        result = [x / 2 for x in result]
    return result


def _poly_mul(a, b):
    n = 1
    while n < len(a) + len(b):
        n <<= 1
    fa = _fft(a + [0] * (n - len(a)))
    fb = _fft(b + [0] * (n - len(b)))
    fc = [fa[i] * fb[i] for i in range(n)]
    c = _fft(fc, invert=True)
    result = [int(round(x.real)) for x in c]
    # Trim trailing zeros
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def _naive_mul(a, b):
    n, m = len(a), len(b)
    c = [0] * (n + m - 1)
    for i in range(n):
        for j in range(m):
            c[i + j] += a[i] * b[j]
    return c


class PolynomialMultiplicationSimulation(AlgorithmPlugin):
    """Polynomial multiplication via FFT visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="polynomial-multiplication",
            name="Polynomial Multiplication (FFT)",
            category="divide-and-conquer",
            visualization_type="ARRAY_BARS",
            description="Multiply polynomials in O(n log n) with FFT.",
            intuition=(
                "Step 1: FFT evaluates both polynomials at n roots of unity. "
                "Step 2: Pointwise multiply O(n). "
                "Step 3: Inverse FFT recovers product coefficients."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("divide-and-conquer", "fft", "polynomial", "convolution", "number-theory"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        a, b = _POLY_PAIRS[params.seed % len(_POLY_PAIRS)]
        result = _poly_mul(a, b)
        arr = tuple(1 for _ in result)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"PolyMul A={a} B={b}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        a_str = re.search(r"A=\[([^\]]+)\]", initial_state.description).group(1)
        b_str = re.search(r"B=\[([^\]]+)\]", initial_state.description).group(1)
        a = list(map(int, a_str.split(",")))
        b = list(map(int, b_str.split(",")))

        n = 1
        while n < len(a) + len(b):
            n <<= 1

        # Step 1: FFT of A
        fa = _fft(a + [0] * (n - len(a)))
        fa_mags = [abs(v) for v in fa]
        mx = max(fa_mags) or 1
        arr = tuple(max(1, min(99, int(v * 99 / mx))) for v in fa_mags)
        yield SortState(
            array=arr,
            comparing=(0, len(a) - 1),
            last_swap=None,
            sorted_indices=frozenset(range(len(a))),
            comparisons=1,
            swaps=len(fa),
            description=f"FFT(A): {len(fa)} frequency components",
        )

        # Step 2: FFT of B
        fb = _fft(b + [0] * (n - len(b)))
        fb_mags = [abs(v) for v in fb]
        mx = max(fb_mags) or 1
        arr = tuple(max(1, min(99, int(v * 99 / mx))) for v in fb_mags)
        yield SortState(
            array=arr,
            comparing=(0, len(b) - 1),
            last_swap=None,
            sorted_indices=frozenset(range(len(b))),
            comparisons=2,
            swaps=len(fb),
            description=f"FFT(B): {len(fb)} frequency components",
        )

        # Step 3: Pointwise multiply
        fc = [fa[i] * fb[i] for i in range(n)]
        fc_mags = [abs(v) for v in fc]
        mx = max(fc_mags) or 1
        arr = tuple(max(1, min(99, int(v * 99 / mx))) for v in fc_mags)
        yield SortState(
            array=arr,
            comparing=(0, n - 1),
            last_swap=(0, n - 1),
            sorted_indices=frozenset(range(n)),
            comparisons=3,
            swaps=n,
            description=f"Pointwise multiply: {n} values",
        )

        # Step 4: Inverse FFT
        c = _fft(fc, invert=True)
        result = [int(round(x.real)) for x in c]
        while len(result) > 1 and result[-1] == 0:
            result.pop()

        mx = max(abs(v) for v in result) or 1
        arr = tuple(max(1, min(99, int(abs(v) * 99 / mx))) for v in result)
        yield SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(result))),
            comparisons=4,
            swaps=result[-1] if result else 0,
            description=f"Inverse FFT: coefficients = {result}",
        )

        naive = _naive_mul(a, b)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(len(result))),
            comparisons=4,
            swaps=result[-1] if result else 0,
            description=f"Product: {result} ✓ (verified vs naive: {result == naive})",
        )
