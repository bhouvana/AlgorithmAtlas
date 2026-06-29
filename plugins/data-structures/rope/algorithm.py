"""
Rope Data Structure — Algorithm Atlas Plugin

Rope is a binary tree where leaves hold string segments; interior nodes
store the weight (total length of left subtree). Demonstrates:
  1. Build rope from string "Hello, World!"
  2. Concatenate with " Goodbye."
  3. Index lookup O(log n)
  4. Split at position 7

GraphTraversalState:
  - nodes: each rope node; label=segment (leaf) or weight (internal);
    weight = depth in tree
  - edges: parent → child
  - current: node_id being accessed
  - frontier: access path
  - visited: all leaves (where strings live)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Generator, List, Optional, Tuple

from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, SimulationParams
from algorithm_atlas_sdk import GraphTraversalState
from algorithm_atlas_sdk.types import NodeState, EdgeState

_id = [0]


def _nid() -> str:
    _id[0] += 1
    return f"r{_id[0]}"


@dataclass
class _RNode:
    node_id: str
    segment: str = ""   # only for leaves
    weight: int = 0     # total chars in left subtree for internal nodes
    left: Optional[str] = None
    right: Optional[str] = None

    @property
    def is_leaf(self):
        return self.left is None and self.right is None


class Rope(AlgorithmPlugin):

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="rope",
            name="Rope",
            category="data-structures",
            visualization_type="TREE",
            description=(
                "Rope: binary tree for efficient string operations. "
                "Leaves store string segments; internal nodes store left-subtree length. "
                "Concat O(1), Index O(log n), Split O(log n)."
            ),
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(n)",
            tags=("data-structures", "rope", "string", "binary-tree"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        return GraphTraversalState(
            nodes=(), edges=(), visited=frozenset(), frontier=(),
            current=None, distances={}, path=(),
            description='Rope demo. Building rope for "Hello, World!" then concatenating and splitting.')

    def _mk(self, nodes: Dict[str, _RNode], root: Optional[str],
            current: Optional[str], path: List[str], desc: str) -> GraphTraversalState:
        if not nodes or root is None:
            return GraphTraversalState(nodes=(), edges=(), visited=frozenset(), frontier=(),
                                       current=current, distances={}, path=(), description=desc)

        # BFS layout
        from collections import deque
        pos: Dict[str, Tuple[float, float]] = {}
        x_by_d: Dict[int, int] = {}
        q: deque = deque([(root, 0)])
        while q:
            nid, d = q.popleft()
            if nid not in nodes:
                continue
            lvl = x_by_d.get(d, 0)
            pos[nid] = (float(lvl), float(d))
            x_by_d[d] = lvl + 1
            n = nodes[nid]
            if n.left and n.left in nodes:
                q.append((n.left, d + 1))
            if n.right and n.right in nodes:
                q.append((n.right, d + 1))

        mx = max((p[0] for p in pos.values()), default=0)
        my = max((p[1] for p in pos.values()), default=0)

        ns = []
        for nid, n in nodes.items():
            label = repr(n.segment) if n.is_leaf else f"w={n.weight}"
            ns.append(NodeState(
                node_id=nid, label=label,
                x=pos.get(nid, (0, 0))[0] / max(mx, 1),
                y=pos.get(nid, (0, 0))[1] / max(my, 1),
                weight=pos.get(nid, (0, 0))[1],
            ))

        es = []
        for nid, n in nodes.items():
            if n.left and n.left in nodes:
                es.append(EdgeState(f"e-{nid}-L", nid, n.left, directed=True))
            if n.right and n.right in nodes:
                es.append(EdgeState(f"e-{nid}-R", nid, n.right, directed=True))

        leaves = frozenset(nid for nid, n in nodes.items() if n.is_leaf)
        return GraphTraversalState(
            nodes=tuple(ns), edges=tuple(es),
            visited=leaves, frontier=tuple(path[-5:]),
            current=current, distances={nid: pos.get(nid, (0, 0))[1] for nid in nodes},
            path=tuple(path), description=desc)

    def steps(self, initial_state: GraphTraversalState) -> Generator:
        _id[0] = 0
        nodes: Dict[str, _RNode] = {}

        def leaf(s: str) -> str:
            nid = _nid()
            n = _RNode(node_id=nid, segment=s, weight=len(s))
            nodes[nid] = n
            return nid

        def internal(left: str, right: str) -> str:
            nid = _nid()
            lw = _total_weight(left)
            n = _RNode(node_id=nid, weight=lw, left=left, right=right)
            nodes[nid] = n
            return nid

        def _total_weight(nid: str) -> int:
            n = nodes[nid]
            if n.is_leaf:
                return len(n.segment)
            return _total_weight(n.left) + _total_weight(n.right) if n.left and n.right else n.weight

        def concat(r1: str, r2: str) -> str:
            return internal(r1, r2)

        def index(root: str, i: int, path_acc: list) -> Tuple[str, str]:
            """Return (node_id, char) at index i."""
            n = nodes[root]
            path_acc.append(root)
            if n.is_leaf:
                return root, n.segment[i] if i < len(n.segment) else '?'
            if i < n.weight:
                return index(n.left, i, path_acc)
            else:
                return index(n.right, i - n.weight, path_acc)

        path: List[str] = []

        # Step 1: Build rope for "Hello, World!"
        yield self._mk(nodes, None, None, path, 'Building rope for "Hello, World!"...')

        l1 = leaf("Hello, ")
        l2 = leaf("World!")
        root = internal(l1, l2)
        path = [root]

        yield self._mk(nodes, root, root, path,
                       'Rope built: root.weight=7 (len("Hello, ")). '
                       'Left leaf="Hello, ", Right leaf="World!"')

        # Step 2: Concatenate with " Goodbye."
        yield self._mk(nodes, root, root, path,
                       'Concatenating with " Goodbye." — O(1) operation: just create new root.')
        l3 = leaf(" Goodbye.")
        root2 = concat(root, l3)
        path.append(root2)
        full_str = "Hello, World! Goodbye."

        yield self._mk(nodes, root2, root2, path,
                       f'Concatenated. New root weight={nodes[root2].weight}. '
                       f'Full string: "{full_str[:20]}..." ({_total_weight(root2)} chars)')

        # Step 3: Index lookup at position 7 ('W')
        idx_path: List[str] = []
        target_i = 7
        node_found, char = index(root2, target_i, idx_path)
        yield self._mk(nodes, root2, node_found, idx_path,
                       f'Index({target_i}): traversed {len(idx_path)} nodes. '
                       f'Found char="{char}" at leaf. '
                       f'O(log n) path: {" → ".join(n for n in idx_path)}')

        # Step 4: Show split concept
        split_pos = 7
        yield self._mk(nodes, root2, root2, path,
                       f'Split at position {split_pos}: divide into "Hello, " | "World! Goodbye.". '
                       f'O(log n) — follow the index path, rebalancing as needed.')

        final = self._mk(nodes, root2, None, path,
                         f'Rope demo complete. {len(nodes)} nodes ({sum(1 for n in nodes.values() if n.is_leaf)} leaves). '
                         f'Concat O(1), Index O(log n), Split O(log n) vs O(n) for plain strings.')
        yield final
        return final
