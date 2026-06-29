"""Strassen Matrix Multiplication plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Fixed 2x2 matrices for clear visualization (Strassen's 7 products)
# Using small values so results stay in 1-99 after scaling


def _mat_add(A, B):
    return [[A[i][j] + B[i][j] for j in range(2)] for i in range(2)]


def _mat_sub(A, B):
    return [[A[i][j] - B[i][j] for j in range(2)] for i in range(2)]


def _mat_mul_naive(A, B):
    return [
        [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
        [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]],
    ]


def _flat(mat):
    return [mat[0][0], mat[0][1], mat[1][0], mat[1][1]]


def _scale(vals):
    mx = max(abs(v) for v in vals) or 1
    return tuple(max(1, min(99, int(abs(v) * 99 // mx))) for v in vals)


class StrassenSimulation(AlgorithmPlugin):
    """Strassen 2×2 matrix multiplication with 7 products."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="strassen",
            name="Strassen Matrix Multiplication",
            category="divide-and-conquer",
            visualization_type="ARRAY_BARS",
            description="Multiply 2×2 matrices using Strassen's 7-product algorithm.",
            intuition=(
                "Naive 2×2 multiply uses 8 multiplications. "
                "Strassen's M1..M7 use only 7 multiplications (more additions). "
                "Recursively applied to n×n: O(n^2.807) instead of O(n^3)."
            ),
            complexity_time_best="O(n^2.807)",
            complexity_time_average="O(n^2.807)",
            complexity_time_worst="O(n^2.807)",
            complexity_space="O(n^2)",
            tags=("divide-and-conquer", "strassen", "matrix-multiplication", "fast-multiplication"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        import random
        rng = random.Random(params.seed)
        A = [[rng.randint(1, 9) for _ in range(2)] for _ in range(2)]
        B = [[rng.randint(1, 9) for _ in range(2)] for _ in range(2)]
        # Encode as flat array: [a00,a01,a10,a11, b00,b01,b10,b11]
        combined = _flat(A) + _flat(B)
        # Scale to 1-99
        mx = max(combined)
        arr = tuple(max(1, min(99, v * 99 // mx)) for v in combined)
        a_str = f"[{A[0]},{A[1]}]"
        b_str = f"[{B[0]},{B[1]}]"
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"Strassen seed={params.seed} A={a_str} B={b_str}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        import ast
        desc = initial_state.description
        a_str = re.search(r"A=(\[\[.*?\]\])", desc).group(1)
        b_str = re.search(r"B=(\[\[.*?\]\])", desc).group(1)
        A = ast.literal_eval(a_str)
        B = ast.literal_eval(b_str)

        a, b, c, d = A[0][0], A[0][1], A[1][0], A[1][1]
        e, f, g, h = B[0][0], B[0][1], B[1][0], B[1][1]

        # Strassen's 7 products
        products = [
            ("M1", (a + d) * (e + h), "(a+d)(e+h)"),
            ("M2", (c + d) * e,        "(c+d)e"),
            ("M3", a * (f - h),         "a(f-h)"),
            ("M4", d * (g - e),         "d(g-e)"),
            ("M5", (a + b) * h,         "(a+b)h"),
            ("M6", (c - a) * (e + f),   "(c-a)(e+f)"),
            ("M7", (b - d) * (g + h),   "(b-d)(g+h)"),
        ]

        M = {}
        for i, (name, val, expr) in enumerate(products):
            M[name] = val
            current_vals = [M.get(f"M{j+1}", 0) for j in range(7)]
            mx = max(abs(v) for v in current_vals) or 1
            arr = tuple(max(1, min(99, int(abs(v) * 99 // mx))) for v in current_vals)
            yield SortState(
                array=arr,
                comparing=(i, i),
                last_swap=(i, i),
                sorted_indices=frozenset(range(i + 1)),
                comparisons=i + 1,
                swaps=abs(val),
                description=f"{name} = {expr} = {val}",
            )

        # Compute result C = A×B
        C = [
            [M["M1"] + M["M4"] - M["M5"] + M["M7"], M["M3"] + M["M5"]],
            [M["M2"] + M["M4"],                       M["M1"] - M["M2"] + M["M3"] + M["M6"]],
        ]
        # Verify
        C_naive = _mat_mul_naive(A, B)
        c_flat = _flat(C)
        c_naive_flat = _flat(C_naive)
        correct = c_flat == c_naive_flat

        mx = max(abs(v) for v in c_flat) or 1
        arr_c = tuple(max(1, min(99, int(abs(v) * 99 // mx))) for v in c_flat)

        # Pad to 7 (show result + verification)
        arr_out = arr_c + tuple([99 if correct else 1] * 3)

        return SortState(
            array=arr_out[:7],
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(7)),
            comparisons=7,
            swaps=sum(abs(v) for v in c_flat),
            description=(
                f"C = A×B = [{C[0]}, {C[1]}] "
                f"(naive={C_naive}, correct={correct})"
            ),
        )
