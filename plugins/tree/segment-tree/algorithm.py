"""Segment Tree plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class SegmentTreeSimulation(AlgorithmPlugin):
    """
    Segment Tree — O(n) build, O(log n) query/update.

    2-row table:
      row 0: original array (leaves)
      row 1: segment tree nodes 0..2n-1 (1-indexed, tree[1] is root)
              padded to len(arr) + 1 slots for alignment

    Phase 1: build (leaf assignment + parent aggregation)
    Phase 2: range sum query [ql, qr]
    Phase 3: point update arr[i] += delta
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="segment-tree",
            name="Segment Tree",
            category="tree",
            visualization_type="MATRIX",
            description=(
                "Build a segment tree for range-sum queries, "
                "then answer a query and perform a point update in O(log n)."
            ),
            intuition=(
                "Store partial sums in a complete binary tree. "
                "Leaves hold array values; each internal node holds the sum of its children. "
                "Queries decompose into O(log n) disjoint ranges."
            ),
            complexity_time_best="O(n) build, O(log n) per query/update",
            complexity_time_average="O(n) build, O(log n) per query/update",
            complexity_time_worst="O(n) build, O(log n) per query/update",
            complexity_space="O(n)",
            tags=("tree", "segment-tree", "range-query", "data-structure"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 6), 8))
        arr = [rng.randint(1, 15) for _ in range(n)]
        tree = [0] * (2 * n)  # 0-indexed, tree[n..2n-1] = leaves

        table = (
            tuple(arr),
            tuple(tree),
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"SegTree: arr={arr}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        arr = list(initial_state.table[0])
        n = len(arr)
        tree = [0] * (2 * n)
        computed: set = set()

        # Phase 1: Build — assign leaves
        for i in range(n):
            tree[n + i] = arr[i]
            computed.add((1, n + i))
            yield DPState(
                table=(tuple(arr), tuple(tree)),
                current_cell=(1, n + i),
                computed_cells=frozenset(computed),
                description=f"Leaf tree[{n+i}] = arr[{i}] = {arr[i]}",
            )

        # Build internal nodes bottom-up
        for i in range(n - 1, 0, -1):
            tree[i] = tree[2 * i] + tree[2 * i + 1]
            computed.add((1, i))
            yield DPState(
                table=(tuple(arr), tuple(tree)),
                current_cell=(1, i),
                computed_cells=frozenset(computed),
                description=(
                    f"tree[{i}] = tree[{2*i}] + tree[{2*i+1}] = "
                    f"{tree[2*i]} + {tree[2*i+1]} = {tree[i]}"
                ),
            )

        # Phase 2: Range query [ql, qr]
        ql = 1
        qr = n - 2
        if ql > qr:
            ql, qr = 0, n - 1

        result = 0
        lo, hi = ql + n, qr + n
        query_nodes: List[int] = []
        _lo, _hi = lo, hi
        while _lo <= _hi:
            if _lo % 2 == 1:
                query_nodes.append(_lo)
                result += tree[_lo]
                _lo += 1
            if _hi % 2 == 0:
                query_nodes.append(_hi)
                result += tree[_hi]
                _hi -= 1
            _lo //= 2
            _hi //= 2

        yield DPState(
            table=(tuple(arr), tuple(tree)),
            current_cell=(1, ql + n),
            computed_cells=frozenset(computed),
            description=(
                f"Query sum[{ql}..{qr}] = {result} "
                f"(nodes: {query_nodes})"
            ),
        )

        # Phase 3: Point update arr[0] += 5
        upd_idx = 0
        delta = 5
        i = upd_idx + n
        arr[upd_idx] += delta
        tree[i] += delta
        computed.add((0, upd_idx))
        yield DPState(
            table=(tuple(arr), tuple(tree)),
            current_cell=(0, upd_idx),
            computed_cells=frozenset(computed),
            description=f"Update arr[{upd_idx}] += {delta} → {arr[upd_idx]}",
        )
        i //= 2
        while i >= 1:
            tree[i] = tree[2 * i] + tree[2 * i + 1]
            computed.add((1, i))
            yield DPState(
                table=(tuple(arr), tuple(tree)),
                current_cell=(1, i),
                computed_cells=frozenset(computed),
                description=f"Propagate: tree[{i}] = {tree[2*i]} + {tree[2*i+1]} = {tree[i]}",
            )
            i //= 2

        return DPState(
            table=(tuple(arr), tuple(tree)),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Done: tree[1] (total sum) = {tree[1]}",
        )
