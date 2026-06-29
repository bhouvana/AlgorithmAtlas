"""
B-Tree (Order 3) — Algorithm Atlas Plugin

Inserts 10 keys into a B-tree of order t=2 (min t-1=1, max 2t-1=3 keys/node).
Demonstrates node splitting when a node overflows.

GraphTraversalState encoding:
  - nodes: each B-tree node; label = comma-separated keys; weight = depth
  - edges: parent → child
  - current: node_id being split or inserted into
  - frontier: search path to insertion point
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Generator, List, Optional, Tuple

from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, SimulationParams
from algorithm_atlas_sdk import GraphTraversalState
from algorithm_atlas_sdk.types import NodeState, EdgeState

_nid_counter = [0]


def _new_id():
    _nid_counter[0] += 1
    return f"bt{_nid_counter[0]}"


@dataclass
class _BNode:
    node_id: str
    keys: List[int] = field(default_factory=list)
    children: List[str] = field(default_factory=list)   # child node_ids

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0


T = 2   # minimum degree: max 2T-1=3 keys per node


class BTree(AlgorithmPlugin):

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="b-tree",
            name="B-Tree (Order 3)",
            category="data-structures",
            visualization_type="TREE",
            description=(
                "B-Tree with minimum degree t=2 (max 3 keys/node). "
                "Nodes split when full. Used in databases and file systems. "
                "All operations O(log n) with low disk I/O."
            ),
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(n)",
            tags=("data-structures", "b-tree", "balanced-tree", "database"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        return GraphTraversalState(
            nodes=(), edges=(), visited=frozenset(), frontier=(),
            current=None, distances={}, path=(),
            description="Empty B-Tree (t=2, max 3 keys/node). Inserting: 10,20,5,6,12,30,7,17,3,8")

    def _to_gts(self, nodes: Dict[str, _BNode], root: Optional[str],
                current: Optional[str], path: List[str], desc: str,
                depth: Dict[str, int]) -> GraphTraversalState:
        if not nodes or root is None:
            return GraphTraversalState(nodes=(), edges=(), visited=frozenset(),
                                       frontier=(), current=current, distances={},
                                       path=tuple(path), description=desc)

        # Assign x positions via BFS
        from collections import deque
        positions: Dict[str, Tuple[float, float]] = {}
        x_by_depth: Dict[int, int] = {}
        q: deque = deque([(root, 0)])
        while q:
            nid, d = q.popleft()
            lvl = x_by_depth.get(d, 0)
            positions[nid] = (float(lvl), float(d))
            x_by_depth[d] = lvl + 1
            for child in nodes[nid].children:
                if child in nodes:
                    q.append((child, d + 1))

        max_x = max((p[0] for p in positions.values()), default=0)
        max_y = max((p[1] for p in positions.values()), default=0)

        ns = tuple(
            NodeState(
                node_id=nid,
                label=",".join(str(k) for k in nodes[nid].keys),
                x=positions.get(nid, (0, 0))[0] / max(max_x, 1),
                y=positions.get(nid, (0, 0))[1] / max(max_y, 1),
                weight=float(depth.get(nid, 0)),
            )
            for nid in nodes
        )
        es = []
        for nid, bnode in nodes.items():
            for child in bnode.children:
                if child in nodes:
                    es.append(EdgeState(f"e-{nid}-{child}", nid, child, directed=True))

        full_nodes = frozenset(nid for nid, n in nodes.items() if len(n.keys) == 2*T-1)
        return GraphTraversalState(
            nodes=ns, edges=tuple(es),
            visited=full_nodes,
            frontier=tuple(path[-4:]),
            current=current,
            distances={nid: float(depth.get(nid, 0)) for nid in nodes},
            path=tuple(path),
            description=desc,
        )

    def steps(self, initial_state: GraphTraversalState) -> Generator:
        _nid_counter[0] = 0
        keys_to_insert = [10, 20, 5, 6, 12, 30, 7, 17, 3, 8]
        nodes: Dict[str, _BNode] = {}
        depth: Dict[str, int] = {}
        root_id: Optional[str] = None
        path: List[str] = []

        def new_node() -> _BNode:
            nid = _new_id()
            n = _BNode(node_id=nid)
            nodes[nid] = n
            return n

        def split_child(parent: _BNode, i: int, child: _BNode):
            """Split child at index i of parent. child must be full (2T-1 keys)."""
            sibling = new_node()
            depth[sibling.node_id] = depth.get(child.node_id, 0)
            sibling.keys = child.keys[T:]       # right half
            child.keys = child.keys[:T-1]       # left half (T-1 keys)
            if not child.is_leaf:
                sibling.children = child.children[T:]
                child.children = child.children[:T]
                for c in sibling.children:
                    if c in depth:
                        depth[c] = depth.get(sibling.node_id, 0) + 1
            mid_key = child.keys[T-1] if len(child.keys) >= T else child.keys[-1]
            # The median key to push up
            all_keys = sorted(child.keys + sibling.keys)
            if len(all_keys) >= T - 1:
                # Reconstruct: child.keys was left T-1 keys before removal of median
                # Let's re-derive
                pass
            # Simpler: backup full keys before split
            parent.keys.insert(i, _median_key)
            parent.children.insert(i + 1, sibling.node_id)

        # Use pre-split approach (split on the way down)
        def insert_non_full(node: _BNode, k: int):
            i = len(node.keys) - 1
            if node.is_leaf:
                node.keys.append(0)
                while i >= 0 and k < node.keys[i]:
                    node.keys[i + 1] = node.keys[i]
                    i -= 1
                node.keys[i + 1] = k
            else:
                while i >= 0 and k < node.keys[i]:
                    i -= 1
                i += 1
                child = nodes[node.children[i]]
                if len(child.keys) == 2 * T - 1:
                    _split_child(node, i, child)
                    if k > node.keys[i]:
                        i += 1
                insert_non_full(nodes[node.children[i]], k)

        def _split_child(parent: _BNode, i: int, child: _BNode):
            sib = new_node()
            depth[sib.node_id] = depth.get(child.node_id, 0)
            full = list(child.keys)  # 2T-1 keys
            mid = full[T - 1]
            child.keys = full[:T - 1]
            sib.keys = full[T:]
            if not child.is_leaf:
                sib.children = child.children[T:]
                child.children = child.children[:T]
                for c in sib.children:
                    depth[c] = depth.get(sib.node_id, 0) + 1
            parent.keys.insert(i, mid)
            parent.children.insert(i + 1, sib.node_id)

        def insert(k: int):
            nonlocal root_id
            if root_id is None:
                r = new_node()
                depth[r.node_id] = 0
                r.keys.append(k)
                root_id = r.node_id
                return

            r = nodes[root_id]
            if len(r.keys) == 2 * T - 1:
                # Root is full: split root
                new_root = new_node()
                depth[new_root.node_id] = 0
                # Bump all existing depths
                for nid in nodes:
                    if nid != new_root.node_id:
                        depth[nid] = depth.get(nid, 0) + 1
                new_root.children.append(root_id)
                _split_child(new_root, 0, r)
                root_id = new_root.node_id
                insert_non_full(new_root, k)
            else:
                insert_non_full(r, k)

        for key in keys_to_insert:
            old_count = len(nodes)
            yield self._to_gts(dict(nodes), root_id, root_id, list(path), dict(depth),
                                f"Inserting key {key}...")
            insert(key)
            path.append(root_id or "")
            split_happened = len(nodes) > old_count + 1  # more than 1 new node = split occurred
            desc = (f"Inserted {key}. "
                    + ("Node split occurred — median key promoted to parent. " if split_happened else "")
                    + f"Root now has {len(nodes[root_id].keys)} key(s).")
            yield self._to_gts(dict(nodes), root_id, root_id, list(path), dict(depth), desc)

        final_desc = (f"B-Tree complete: {len(nodes)} nodes, {sum(len(n.keys) for n in nodes.values())} keys. "
                      f"All leaves at same depth → O(log n) guaranteed.")
        final = self._to_gts(dict(nodes), root_id, root_id, list(path), dict(depth), final_desc)
        yield final
        return final
