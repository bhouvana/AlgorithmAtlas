"""Preorder Tree Traversal (root-left-right) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Dict, Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)


# ── BST builder + hierarchical layout ─────────────────────────────────────────

def _build_tree(
    rng: random.Random, n: int
) -> Tuple[str, Tuple[NodeState, ...], Tuple[EdgeState, ...]]:
    values: Dict[str, int] = {}
    children: Dict[str, List[Optional[str]]] = {}

    pool = rng.sample(range(10, 99), n)
    root = "n0"

    for i, val in enumerate(pool):
        nid = f"n{i}"
        values[nid] = val
        children[nid] = [None, None]

    for i in range(1, n):
        nid = f"n{i}"
        val = values[nid]
        curr = root
        while True:
            if val < values[curr]:
                if children[curr][0] is None:
                    children[curr][0] = nid
                    break
                curr = children[curr][0]  # type: ignore[assignment]
            else:
                if children[curr][1] is None:
                    children[curr][1] = nid
                    break
                curr = children[curr][1]  # type: ignore[assignment]

    depths: Dict[str, int] = {root: 0}
    queue = [root]
    max_depth = 0
    while queue:
        node = queue.pop(0)
        d = depths[node]
        if d > max_depth:
            max_depth = d
        for child in filter(None, children[node]):
            depths[child] = d + 1  # type: ignore[index]
            queue.append(child)  # type: ignore[arg-type]

    x_pos: Dict[str, int] = {}
    counter = [0]

    def _inorder(nid: Optional[str]) -> None:
        if nid is None:
            return
        _inorder(children[nid][0])
        x_pos[nid] = counter[0]
        counter[0] += 1
        _inorder(children[nid][1])

    _inorder(root)
    max_x = max(x_pos.values()) if x_pos else 0

    def nx(pos: int) -> float:
        return 0.05 + 0.9 * pos / max_x if max_x else 0.5

    def ny(depth: int) -> float:
        return 0.06 + 0.82 * depth / max_depth if max_depth else 0.1

    node_list = [
        NodeState(
            node_id=nid,
            label=str(values[nid]),
            x=nx(x_pos[nid]),
            y=ny(depths[nid]),
        )
        for nid in sorted(values, key=lambda k: int(k[1:]))
    ]

    edge_list = []
    eid = 0
    for nid, (left, right) in children.items():
        if left:
            edge_list.append(EdgeState(edge_id=f"e{eid}", source=nid, target=left, directed=True))
            eid += 1
        if right:
            edge_list.append(EdgeState(edge_id=f"e{eid}", source=nid, target=right, directed=True))
            eid += 1

    return root, tuple(node_list), tuple(edge_list)


# ── Plugin ─────────────────────────────────────────────────────────────────────

class PreorderTraversalSimulation(AlgorithmPlugin):
    """
    Preorder Traversal — visit root, then recurse into left, then right.
    Iterative implementation using an explicit stack (push right then left
    so left is processed first).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="preorder-traversal",
            name="Preorder Traversal",
            category="tree",
            visualization_type="TREE",
            description="Visits the root before its subtrees: root → left → right.",
            intuition="Process the node as soon as you arrive, before descending. Used to serialize/copy a tree — you can rebuild it from its preorder sequence.",
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(h)",
            tags=("tree", "traversal", "preorder", "dfs", "serialization"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("node_count", 9), 15))
        root, nodes, edges = _build_tree(rng, n)

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(root,),
            current=None,
            distances={},
            path=(),
            description="Preorder traversal: push root onto stack",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges

        node_val: Dict[str, int] = {n.node_id: int(n.label) for n in nodes}
        children: Dict[str, List[str]] = {n.node_id: [] for n in nodes}
        parents: set = set()
        for e in edges:
            children[e.source].append(e.target)
            parents.add(e.target)

        root = next(n.node_id for n in nodes if n.node_id not in parents)

        # Sort each child list so index 0 = left child (value < parent), index 1 = right
        for nid in children:
            pv = node_val[nid]
            children[nid].sort(key=lambda c: 0 if node_val[c] < pv else 1)

        stack: List[str] = [root]
        result: List[str] = []
        visited: set = set()

        while stack:
            # Show the state before popping
            yield GraphTraversalState(
                nodes=nodes, edges=edges,
                visited=frozenset(visited),
                frontier=tuple(reversed(stack)),
                current=stack[-1],
                distances={},
                path=tuple(result),
                description=f"Pop {stack[-1]} (val={_label(nodes, stack[-1])}) from stack",
            )

            node = stack.pop()
            result.append(node)
            visited.add(node)

            yield GraphTraversalState(
                nodes=nodes, edges=edges,
                visited=frozenset(visited),
                frontier=tuple(reversed(stack)),
                current=node,
                distances={},
                path=tuple(result),
                description=f"Visit {node} (val={_label(nodes, node)}) → push right then left",
            )

            # Push right first so left is processed first
            right = children[node][1] if len(children[node]) > 1 else None
            left = children[node][0] if children[node] else None

            if right:
                stack.append(right)
            if left:
                stack.append(left)

        return GraphTraversalState(
            nodes=nodes, edges=edges,
            visited=frozenset(visited),
            frontier=(),
            current=None,
            distances={},
            path=tuple(result),
            description=f"Preorder complete: [{', '.join(_label(nodes, r) for r in result)}]",
        )


def _label(nodes: Tuple[NodeState, ...], nid: str) -> str:
    for n in nodes:
        if n.node_id == nid:
            return n.label
    return nid
