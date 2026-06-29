"""Sparse Table (RMQ) plugin for Algorithm Atlas."""
from __future__ import annotations

import math
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)


class SparseTableSimulation(AlgorithmPlugin):
    """Sparse table construction for O(1) range minimum queries."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="sparse-table",
            name="Sparse Table (Range Minimum Query)",
            category="tree",
            visualization_type="ARRAY_BARS",
            description="Preprocess array for O(1) RMQ using overlapping power-of-2 ranges.",
            intuition=(
                "Build table[j][i] = min(arr[i..i+2^j-1]). "
                "Row 0 = array itself. Each row doubles the covered range. "
                "Query [l,r]: take max of two overlapping ranges of length 2^k."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n log n)",
            tags=("tree", "sparse-table", "range-query", "rmq", "preprocessing"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        import random
        n = int(params.inputs.get("size", 12))
        rng = random.Random(params.seed)
        arr = tuple(rng.randint(1, 99) for _ in range(n))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"SparseTable n={n} seed={params.seed}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n = int(re.search(r"n=(\d+)", initial_state.description).group(1))
        arr = list(initial_state.array)
        log2n = max(1, int(math.log2(n)) + 1)

        # Build sparse table
        table = [[0] * n for _ in range(log2n)]
        table[0] = arr[:]

        yield SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=0,
            swaps=0,
            description=f"Row 0 (range=1): copied from array",
        )

        for j in range(1, log2n):
            length = 1 << j
            processed = set()
            for i in range(n - length + 1):
                prev_len = length >> 1
                a = table[j - 1][i]
                b = table[j - 1][min(i + prev_len, n - 1)]
                table[j][i] = min(a, b)
                processed.add(i)
                processed.add(min(i + prev_len, n - 1))

            # Show this row's minimums as current array state
            row_vals = [table[j][i] if i in range(n - length + 1) else arr[i]
                        for i in range(n)]
            yield SortState(
                array=tuple(row_vals),
                comparing=None,
                last_swap=None,
                sorted_indices=frozenset(range(n - length + 1)),
                comparisons=j * n,
                swaps=length,
                description=(
                    f"Row {j} (range={length}): computed {n - length + 1} entries"
                ),
            )

        # Demo queries: answer a few RMQ
        query_pairs = [(0, n // 2), (n // 3, 2 * n // 3), (0, n - 1)]
        for l, r in query_pairs:
            if l > r:
                continue
            length = r - l + 1
            k = int(math.log2(length))
            a = table[k][l]
            b = table[k][r - (1 << k) + 1]
            result = min(a, b)
            result_idx = arr.index(result) if result in arr else l

            yield SortState(
                array=tuple(arr),
                comparing=(l, r),
                last_swap=(result_idx, result_idx),
                sorted_indices=frozenset([result_idx]),
                comparisons=log2n * n,
                swaps=result,
                description=(
                    f"RMQ[{l},{r}] = {result} "
                    f"(overlap two ranges of len 2^{k}={1<<k})"
                ),
            )

        return SortState(
            array=tuple(arr),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=log2n * n,
            swaps=min(arr),
            description=(
                f"Done: {log2n} table rows built. "
                f"Any RMQ answered in O(1)."
            ),
        )
