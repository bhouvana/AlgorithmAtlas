"""Fenwick Tree (Binary Indexed Tree) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    DPState,
    SimulationParams,
)


class FenwickTreeSimulation(AlgorithmPlugin):
    """
    Fenwick Tree (BIT) — O(n) build, O(log n) prefix-sum query and point update.

    2-row table:
      row 0: original array (1-indexed, index 0 unused → 0)
      row 1: BIT array (1-indexed)

    Phase 1: build by inserting elements one by one.
    Phase 2: demonstrate a prefix-sum query up to index k.
    Phase 3: demonstrate a point update.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="fenwick-tree",
            name="Fenwick Tree (BIT)",
            category="tree",
            visualization_type="MATRIX",
            description=(
                "Build a Binary Indexed Tree for O(log n) prefix-sum queries "
                "and point updates using the lowest-set-bit trick."
            ),
            intuition=(
                "BIT[i] stores the sum of arr[i - lsb(i) + 1 .. i]. "
                "To update index i, add to BIT[i] and propagate to BIT[i + lsb(i)]. "
                "Prefix query: accumulate BIT[i] then jump to BIT[i - lsb(i)]."
            ),
            complexity_time_best="O(n) build, O(log n) per query/update",
            complexity_time_average="O(n) build, O(log n) per query/update",
            complexity_time_worst="O(n) build, O(log n) per query/update",
            complexity_space="O(n)",
            tags=("tree", "fenwick-tree", "bit", "prefix-sum"),
        )

    def initialize(self, params: SimulationParams) -> DPState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 8), 10))
        arr = [0] + [rng.randint(1, 10) for _ in range(n)]  # 1-indexed

        table = (
            tuple(arr),
            tuple(0 for _ in range(n + 1)),
        )
        return DPState(
            table=table,
            current_cell=None,
            computed_cells=frozenset(),
            description=f"FenwickTree: n={n}, arr={arr[1:]}",
        )

    def steps(
        self, initial_state: DPState
    ) -> Generator[DPState, None, DPState]:
        arr = list(initial_state.table[0])  # 1-indexed
        n = len(arr) - 1
        bit = [0] * (n + 1)
        computed: set = set()

        def update(i: int, delta: int):
            while i <= n:
                bit[i] += delta
                i += i & (-i)

        def prefix_sum(i: int) -> int:
            s = 0
            while i > 0:
                s += bit[i]
                i -= i & (-i)
            return s

        # Phase 1: build
        for i in range(1, n + 1):
            # Track which BIT cells get updated
            j = i
            while j <= n:
                bit[j] += arr[i]
                computed.add((1, j))
                j += j & (-j)

            yield DPState(
                table=(tuple(arr), tuple(bit)),
                current_cell=(0, i),
                computed_cells=frozenset(computed),
                description=f"Insert arr[{i}]={arr[i]}: update BIT chain from {i}",
            )

        # Phase 2: prefix query up to n//2
        q = n // 2
        result = prefix_sum(q)
        yield DPState(
            table=(tuple(arr), tuple(bit)),
            current_cell=(1, q),
            computed_cells=frozenset(computed),
            description=f"Query prefix_sum(1..{q}) = {result}",
        )

        # Phase 3: point update arr[1] += 3
        upd_val = 3
        arr[1] += upd_val
        update(1, upd_val)
        j = 1
        while j <= n:
            computed.add((1, j))
            j += j & (-j)

        yield DPState(
            table=(tuple(arr), tuple(bit)),
            current_cell=(0, 1),
            computed_cells=frozenset(computed),
            description=f"Update arr[1] += {upd_val} → {arr[1]}; BIT updated",
        )

        new_total = prefix_sum(n)
        return DPState(
            table=(tuple(arr), tuple(bit)),
            current_cell=None,
            computed_cells=frozenset(computed),
            description=f"Done: total sum = {new_total} (BIT[1..{n}])",
        )
