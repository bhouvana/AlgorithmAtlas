"""Karatsuba Multiplication plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)

_PAIRS = [
    (12, 34), (56, 78), (123, 456), (789, 321),
    (1234, 5678), (9999, 8888), (1111, 9999),
    (999, 1001), (12345, 67890), (31415, 92653),
]


def _karatsuba_trace(x: int, y: int, frames: list, depth: int = 0) -> int:
    """Karatsuba with trace recording. Returns x*y."""
    if x < 10 or y < 10:
        result = x * y
        frames.append((depth, x, y, result, "base"))
        return result

    # Split
    n = max(len(str(x)), len(str(y)))
    m = n // 2
    B = 10 ** m

    x_H, x_L = x // B, x % B
    y_H, y_L = y // B, y % B

    z0 = _karatsuba_trace(x_L, y_L, frames, depth + 1)
    z2 = _karatsuba_trace(x_H, y_H, frames, depth + 1)
    z1 = _karatsuba_trace(x_L + x_H, y_L + y_H, frames, depth + 1) - z0 - z2

    result = z2 * (B ** 2) + z1 * B + z0
    frames.append((depth, x, y, result, f"z0={z0} z1={z1} z2={z2}"))
    return result


class KaratsubaSimulation(AlgorithmPlugin):
    """
    Karatsuba Multiplication.

    DPState table rows (up to 5 recursive levels, each level a row):
      row i: [x, y, result] for each call at depth i
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="karatsuba",
            name="Karatsuba Multiplication",
            category="divide-and-conquer",
            visualization_type="MATRIX",
            description=(
                "Multiply two integers faster than O(n²) by splitting each number "
                "and using 3 recursive multiplications instead of 4."
            ),
            intuition=(
                "Split x = x_H·B^m + x_L. Compute z0=x_L·y_L, z2=x_H·y_H, "
                "z1=(x_L+x_H)(y_L+y_H)-z0-z2. Result = z2·B^2m + z1·B^m + z0."
            ),
            complexity_time_best="O(n^1.585)",
            complexity_time_average="O(n^1.585)",
            complexity_time_worst="O(n^1.585)",
            complexity_space="O(n)",
            tags=("divide-and-conquer", "multiplication", "karatsuba", "arithmetic"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        x, y = _PAIRS[params.seed % len(_PAIRS)]
        # Precompute trace
        frames: list = []
        result = _karatsuba_trace(x, y, frames)
        # Build table: max 4 rows, each with [x, y, result] for up to 3 calls per depth
        max_depth = max(f[0] for f in frames) if frames else 0
        W = 3
        rows = []
        for d in range(max_depth + 1):
            level_frames = [(f[1], f[2], f[3]) for f in frames if f[0] == d][:W]
            row = []
            for lx, ly, lr in level_frames:
                row.extend([lx, ly, lr])
            # Pad to width W*3
            row.extend([0] * (W * 3 - len(row)))
            rows.append(tuple(row))
        if not rows:
            rows = [(x, y, result, 0, 0, 0, 0, 0, 0)]
        return DPState(
            table=tuple(rows),
            current_cell=None,
            computed_cells=frozenset(),
            description=f"Karatsuba({x} × {y}): expect {result}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        desc = initial_state.description
        x = int(desc.split("(")[1].split(" ×")[0])
        y = int(desc.split("× ")[1].split(")")[0])
        expected = int(desc.split("expect ")[1])

        frames: list = []
        _karatsuba_trace(x, y, frames)
        computed: set = set()

        for i, (depth, fx, fy, fresult, note) in enumerate(frames):
            computed.add((depth, i % 3))
            yield DPState(
                table=initial_state.table,
                current_cell=(depth, i % 3),
                computed_cells=frozenset(computed),
                description=f"depth={depth}: {fx}×{fy}={fresult} ({note})",
            )

        return DPState(
            table=initial_state.table,
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Karatsuba({x}×{y}) = {x*y}",
        )
