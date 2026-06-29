"""
Red-Black Tree — Algorithm Atlas Plugin

Inserts 7 keys into an RB-tree, demonstrating:
  - Case 1: Uncle is red → recolor parent, uncle, grandparent
  - Case 2: Node is inner child → rotate parent
  - Case 3: Node is outer child → rotate grandparent + recolor

GraphTraversalState encoding:
  - nodes: each RB node; weight=0 (black) / weight=1 (red)
  - current: node_id of most recently inserted/rotated node
  - visited: set of "settled" black-height-correct subtrees
  - path: insertion path
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Generator, List, Optional, Tuple

from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, SimulationParams
from algorithm_atlas_sdk import GraphTraversalState
from algorithm_atlas_sdk.types import NodeState, EdgeState

RED = 1.0
BLACK = 0.0


@dataclass
class _Node:
    key: int
    color: float = RED
    left: Optional[str] = None
    right: Optional[str] = None
    parent: Optional[str] = None
    node_id: str = ""

    def __post_init__(self):
        if not self.node_id:
            self.node_id = f"n{self.key}"


class RedBlackTree(AlgorithmPlugin):

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="red-black-tree",
            name="Red-Black Tree",
            category="data-structures",
            visualization_type="TREE",
            description=(
                "Self-balancing BST where every node is red or black. "
                "5 invariants ensure O(log n) height. "
                "Insert uses rotations and recoloring to restore balance."
            ),
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(n)",
            tags=("data-structures", "red-black-tree", "balanced-bst", "self-balancing"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        return GraphTraversalState(
            nodes=(), edges=(), visited=frozenset(), frontier=(),
            current=None, distances={}, path=(),
            description="Empty Red-Black Tree. Inserting keys: 10, 20, 30, 15, 25, 5, 1")

    # ── Internal RB-tree ──────────────────────────────────────────────

    def _to_gts(self, nodes: Dict[str, _Node], root: Optional[str],
                current: Optional[str], path: List[str],
                desc: str) -> GraphTraversalState:
        """Convert internal node dict to GraphTraversalState."""
        if not nodes:
            return GraphTraversalState(nodes=(), edges=(), visited=frozenset(),
                                       frontier=(), current=current, distances={},
                                       path=tuple(path), description=desc)

        # Assign (x, y) via level-order layout
        positions: Dict[str, Tuple[float, float]] = {}
        depth: Dict[str, int] = {}
        x_offset: Dict[int, int] = {}

        queue = [root] if root else []
        depth[root] = 0 if root else 0
        while queue:
            nid = queue.pop(0)
            if nid is None:
                continue
            d = depth.get(nid, 0)
            lvl = x_offset.get(d, 0)
            positions[nid] = (float(lvl), float(d))
            x_offset[d] = lvl + 1
            n = nodes[nid]
            if n.left and n.left in nodes:
                depth[n.left] = d + 1
                queue.append(n.left)
            if n.right and n.right in nodes:
                depth[n.right] = d + 1
                queue.append(n.right)

        # Normalise x to [0, 1]
        max_x = max((p[0] for p in positions.values()), default=0)
        max_y = max((p[1] for p in positions.values()), default=0)

        ns = tuple(
            NodeState(
                node_id=nid,
                label=str(nodes[nid].key),
                x=positions.get(nid, (0, 0))[0] / max(max_x, 1),
                y=positions.get(nid, (0, 0))[1] / max(max_y, 1),
                weight=nodes[nid].color,   # 1.0=RED, 0.0=BLACK
            )
            for nid in nodes
        )
        es = []
        for nid, node in nodes.items():
            if node.left and node.left in nodes:
                es.append(EdgeState(f"e-{nid}-{node.left}", nid, node.left, directed=True))
            if node.right and node.right in nodes:
                es.append(EdgeState(f"e-{nid}-{node.right}", nid, node.right, directed=True))

        black_nodes = frozenset(nid for nid, n in nodes.items() if n.color == BLACK)
        return GraphTraversalState(
            nodes=ns, edges=tuple(es),
            visited=black_nodes,
            frontier=tuple(path[-3:]),
            current=current,
            distances={nid: nodes[nid].color for nid in nodes},
            path=tuple(path),
            description=desc,
        )

    def steps(self, initial_state: GraphTraversalState) -> Generator:
        keys = [10, 20, 30, 15, 25, 5, 1]
        nodes: Dict[str, _Node] = {}
        root: Optional[str] = None
        path: List[str] = []

        def insert(key: int):
            nonlocal root
            nid = f"n{key}"
            new_node = _Node(key=key, node_id=nid)
            nodes[nid] = new_node

            if root is None:
                root = nid
                new_node.color = BLACK
                path.append(nid)
                return

            # BST insert
            cur = root
            while True:
                n = nodes[cur]
                if key < n.key:
                    if n.left is None:
                        n.left = nid
                        new_node.parent = cur
                        break
                    cur = n.left
                else:
                    if n.right is None:
                        n.right = nid
                        new_node.parent = cur
                        break
                    cur = n.right

            path.append(nid)
            fix_insert(nid)

        def fix_insert(z: str):
            nonlocal root
            while nodes[z].parent and nodes[nodes[z].parent].color == RED:
                p = nodes[z].parent   # parent (red)
                g = nodes[p].parent   # grandparent
                if g is None:
                    break

                if p == nodes[g].left:
                    # Uncle is right child
                    u = nodes[g].right
                    if u and nodes[u].color == RED:
                        # Case 1: uncle red → recolor
                        nodes[p].color = BLACK
                        nodes[u].color = BLACK
                        nodes[g].color = RED
                        z = g
                    else:
                        if z == nodes[p].right:
                            # Case 2: z is right child → left rotate parent
                            z = p
                            left_rotate(z)
                            p = nodes[z].parent
                            g = nodes[p].parent if p else None
                            if g is None:
                                break
                        # Case 3
                        nodes[p].color = BLACK
                        nodes[g].color = RED
                        right_rotate(g)
                else:
                    u = nodes[g].left
                    if u and nodes[u].color == RED:
                        nodes[p].color = BLACK
                        nodes[u].color = BLACK
                        nodes[g].color = RED
                        z = g
                    else:
                        if z == nodes[p].left:
                            z = p
                            right_rotate(z)
                            p = nodes[z].parent
                            g = nodes[p].parent if p else None
                            if g is None:
                                break
                        nodes[p].color = BLACK
                        nodes[g].color = RED
                        left_rotate(g)
            nodes[root].color = BLACK

        def left_rotate(x: str):
            nonlocal root
            n = nodes[x]
            y = n.right
            if y is None:
                return
            n.right = nodes[y].left
            if nodes[y].left:
                nodes[nodes[y].left].parent = x
            nodes[y].parent = n.parent
            if n.parent is None:
                root = y
            elif x == nodes[n.parent].left:
                nodes[n.parent].left = y
            else:
                nodes[n.parent].right = y
            nodes[y].left = x
            n.parent = y

        def right_rotate(x: str):
            nonlocal root
            n = nodes[x]
            y = n.left
            if y is None:
                return
            n.left = nodes[y].right
            if nodes[y].right:
                nodes[nodes[y].right].parent = x
            nodes[y].parent = n.parent
            if n.parent is None:
                root = y
            elif x == nodes[n.parent].right:
                nodes[n.parent].right = y
            else:
                nodes[n.parent].left = y
            nodes[y].right = x
            n.parent = y

        for key in keys:
            yield self._to_gts(dict(nodes), root, None, list(path),
                                f"Inserting key {key} into RB-tree...")
            insert(key)
            color_str = "BLACK" if nodes[f"n{key}"].color == BLACK else "RED"
            yield self._to_gts(dict(nodes), root, f"n{key}", list(path),
                                f"Inserted {key} ({color_str}). Root={root}, height balanced by RB invariants.")

        final = self._to_gts(dict(nodes), root, root, list(path),
                             f"RB-Tree complete: {len(nodes)} nodes. "
                             f"Root={nodes[root].key} (BLACK). "
                             f"All paths from root have equal black-height.")
        yield final
        return final
