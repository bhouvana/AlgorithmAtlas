"""Interval Tree plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Intervals to insert: [lo, hi]
_INTERVALS = [
    (15, 20), (10, 30), (17, 19), (5, 20), (12, 15), (30, 40), (6, 10), (25, 35),
]
# Query interval
_QUERY = (14, 18)


class _INode:
    __slots__ = ("lo", "hi", "max_hi", "left", "right")

    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi
        self.max_hi = hi
        self.left: Optional[_INode] = None
        self.right: Optional[_INode] = None


def _insert(root: Optional[_INode], lo: int, hi: int) -> _INode:
    if root is None:
        return _INode(lo, hi)
    if lo < root.lo:
        root.left = _insert(root.left, lo, hi)
    else:
        root.right = _insert(root.right, lo, hi)
    root.max_hi = max(root.hi, _max_hi(root.left), _max_hi(root.right))
    return root


def _max_hi(node: Optional[_INode]) -> int:
    return node.max_hi if node else -1


def _query(root: Optional[_INode], ql: int, qr: int, result: List):
    if root is None:
        return
    if root.left and root.left.max_hi >= ql:
        _query(root.left, ql, qr, result)
    if root.lo <= qr and root.hi >= ql:
        result.append((root.lo, root.hi))
    if root.lo <= qr:
        _query(root.right, ql, qr, result)


def _flatten(root: Optional[_INode], out: List):
    if root is None:
        return
    _flatten(root.left, out)
    out.append((root.lo, root.hi, root.max_hi))
    _flatten(root.right, out)


class IntervalTreeSimulation(AlgorithmPlugin):
    """Interval tree build + query visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="interval-tree",
            name="Interval Tree",
            category="tree",
            visualization_type="ARRAY_BARS",
            description="Build interval tree and query overlapping intervals.",
            intuition=(
                "Augmented BST on interval start. "
                "Each subtree stores max_hi for early pruning. "
                f"Query {_QUERY}: find all intervals overlapping this range."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(log n + k)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("tree", "interval-tree", "augmented-bst", "range-query", "data-structure"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = len(_INTERVALS)
        # Array = interval lengths as bars
        arr = tuple(hi - lo for lo, hi in _INTERVALS)
        mx = max(arr)
        arr = tuple(max(1, min(99, v * 99 // mx)) for v in arr)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"IntervalTree n={n} query={_QUERY}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        root = None
        ql, qr = _QUERY

        # Build phase
        for idx, (lo, hi) in enumerate(_INTERVALS):
            root = _insert(root, lo, hi)
            flat: List[Tuple] = []
            _flatten(root, flat)
            # Array = max_hi values after each insertion
            if flat:
                mx = max(f[2] for f in flat)
                arr = tuple(max(1, min(99, f[2] * 99 // max(mx, 1))) for f in flat)
                arr = arr + tuple(1 for _ in range(len(_INTERVALS) - len(arr)))
            else:
                arr = tuple(1 for _ in _INTERVALS)
            yield SortState(
                array=arr,
                comparing=(idx, idx),
                last_swap=None,
                sorted_indices=frozenset(range(idx + 1)),
                comparisons=idx + 1,
                swaps=hi,
                description=f"Insert [{lo},{hi}]: tree has {idx+1} nodes",
            )

        # Query phase
        overlaps: List[Tuple[int, int]] = []
        _query(root, ql, qr, overlaps)
        flat = []
        _flatten(root, flat)

        # Highlight overlapping intervals
        overlap_set = set(overlaps)
        mx_hi = max(f[2] for f in flat) if flat else 1
        arr = tuple(max(1, min(99, f[2] * 99 // max(mx_hi, 1))) for f in flat)

        yield SortState(
            array=arr,
            comparing=(0, len(flat) - 1),
            last_swap=None,
            sorted_indices=frozenset(
                k for k, (lo, hi, _) in enumerate(flat) if (lo, hi) in overlap_set
            ),
            comparisons=len(_INTERVALS) + 1,
            swaps=len(overlaps),
            description=f"Query {_QUERY}: {len(overlaps)} overlap(s): {sorted(overlaps)}",
        )

        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(
                k for k, (lo, hi, _) in enumerate(flat) if (lo, hi) in overlap_set
            ),
            comparisons=len(_INTERVALS) + 1,
            swaps=len(overlaps),
            description=f"Done. {len(overlaps)} intervals overlap {_QUERY}: {sorted(overlaps)}",
        )
