"""Inorder Tree Traversal (left-root-right) plugin for Algorithm Atlas."""
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
) -> Tuple[str, Dict[str, int], Dict[str, List[Optional[str]]], Tuple[NodeState, ...], Tuple[EdgeState, ...]]:
    """Build a random BST with n nodes. Returns (root, values, children, nodes, edges)."""
    values: Dict[str, int] = {}
    children: Dict[str, List[Optional[str]]] = {}

    pool = rng.sample(range(10, 99), n)
    root = "n0"

    for i, val in enumerate(pool):
        nid = f"n{i}"
        values[nid] = val
        children[nid] = [None, None]

    # BST insertion
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

    # Compute depths via BFS
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

    # X positions via inorder traversal
    x_pos: Dict[str, int] = {}
    counter = [0]

    def _inorder_assign(nid: Optional[str]) -> None:
        if nid is None:
            return
        _inorder_assign(children[nid][0])
        x_pos[nid] = counter[0]
        counter[0] += 1
        _inorder_assign(children[nid][1])

    _inorder_assign(root)
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

    return root, values, children, tuple(node_list), tuple(edge_list)


# ── Plugin ─────────────────────────────────────────────────────────────────────

class InorderTraversalSimulation(AlgorithmPlugin):
    """
    Inorder Traversal — visit left subtree, then root, then right subtree.
    For a BST, this produces nodes in ascending sorted order.
    Uses an explicit stack to simulate the call stack iteratively.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="inorder-traversal",
            name="Inorder Traversal",
            category="tree",
            visualization_type="TREE",
            description="Visits binary tree nodes in left-root-right order.",
            intuition="Read a BST left-to-right: always finishes the left branch before visiting the root, then moves to the right. Produces sorted output for any BST.",
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(h)",
            tags=("tree", "traversal", "inorder", "dfs", "bst"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("node_count", 9), 15))
        root, values, children, nodes, edges = _build_tree(rng, n)

        self._root = root
        self._values = values
        self._children = children

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(root,),
            current=None,
            distances={},
            path=(),
            description="Inorder traversal: start at root",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges

        # Reconstruct left/right using BST property: left child value < parent value
        node_val: Dict[str, int] = {n.node_id: int(n.label) for n in nodes}
        children: Dict[str, List[str]] = {n.node_id: [] for n in nodes}
        parents: set = set()
        for e in edges:
            children[e.source].append(e.target)
            parents.add(e.target)

        root = next(n.node_id for n in nodes if n.node_id not in parents)

        def left(nid: str) -> Optional[str]:
            pv = node_val[nid]
            for c in children[nid]:
                if node_val[c] < pv:
                    return c
            return None

        def right(nid: str) -> Optional[str]:
            pv = node_val[nid]
            for c in children[nid]:
                if node_val[c] >= pv:
                    return c
            return None

        # Iterative inorder using a stack
        stack: List[str] = []
        current: Optional[str] = root
        result: List[str] = []
        visited: set = set()

        while current is not None or stack:
            # Push left spine
            while current is not None:
                stack.append(current)
                yield GraphTraversalState(
                    nodes=nodes, edges=edges,
                    visited=frozenset(visited),
                    frontier=tuple(reversed(stack)),
                    current=current,
                    distances={},
                    path=tuple(result),
                    description=f"Push {current} (val={_label(nodes, current)}) onto stack, go left",
                )
                current = left(current)

            # Pop and visit
            current = stack.pop()
            result.append(current)
            visited.add(current)

            yield GraphTraversalState(
                nodes=nodes, edges=edges,
                visited=frozenset(visited),
                frontier=tuple(reversed(stack)),
                current=current,
                distances={},
                path=tuple(result),
                description=f"Visit {current} (val={_label(nodes, current)}) → result: [{', '.join(_label(nodes, r) for r in result)}]",
            )

            current = right(current)

        return GraphTraversalState(
            nodes=nodes, edges=edges,
            visited=frozenset(visited),
            frontier=(),
            current=None,
            distances={},
            path=tuple(result),
            description=f"Inorder complete: [{', '.join(_label(nodes, r) for r in result)}]",
        )


def _label(nodes: Tuple[NodeState, ...], nid: str) -> str:
    for n in nodes:
        if n.node_id == nid:
            return n.label
    return nid
