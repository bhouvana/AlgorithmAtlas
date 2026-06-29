"""BST Search plugin for Algorithm Atlas."""
from __future__ import annotations

import math
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


def _build_bst(
    rng: random.Random, n: int
) -> Tuple[str, Dict[str, int], Dict[str, List[Optional[str]]], Tuple[NodeState, ...], Tuple[EdgeState, ...]]:
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
                curr = children[curr][0]
            else:
                if children[curr][1] is None:
                    children[curr][1] = nid
                    break
                curr = children[curr][1]

    depths: Dict[str, int] = {root: 0}
    queue = [root]
    max_depth = 0
    while queue:
        node = queue.pop(0)
        d = depths[node]
        if d > max_depth:
            max_depth = d
        for child in filter(None, children[node]):
            depths[child] = d + 1
            queue.append(child)

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
        NodeState(node_id=nid, label=str(values[nid]), x=nx(x_pos[nid]), y=ny(depths[nid]))
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


class BSTSearchSimulation(AlgorithmPlugin):
    """
    BST Search — O(h) where h is tree height.

    visited: nodes already compared (and eliminated).
    frontier: (target,) — the value being searched.
    current: node being compared.
    distances: comparisons count as float.
    path: (found_nid,) if found, () if not found.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bst-search",
            name="BST Search",
            category="tree",
            visualization_type="TREE",
            description="Search for a key in a Binary Search Tree by traversing left or right based on comparisons.",
            intuition=(
                "At each node compare the target with the node's value. "
                "If equal, found. If smaller, go left. If larger, go right. "
                "Each step eliminates half the remaining tree (on balanced trees)."
            ),
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(n)",
            complexity_space="O(h)",
            tags=("tree", "bst", "search", "binary-search-tree"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("node_count", 10), 15))
        root, values, children, nodes, edges = _build_bst(rng, n)

        # Search for a value that may or may not be in the tree
        all_vals = sorted(values.values())
        # 50% chance search for existing value, 50% for missing
        if rng.random() < 0.5:
            target_val = rng.choice(all_vals)
        else:
            # Pick a value not in the tree
            lo, hi = all_vals[0] - 5, all_vals[-1] + 5
            candidates = [v for v in range(lo, hi + 1) if v not in all_vals]
            target_val = rng.choice(candidates) if candidates else all_vals[0] + 1

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(root,),
            current=None,
            distances={"target": float(target_val)},
            path=(),
            description=f"BST Search: looking for {target_val} in {n}-node tree",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges

        node_val: Dict[str, int] = {n.node_id: int(n.label) for n in nodes}
        children: Dict[str, List[Optional[str]]] = {n.node_id: [None, None] for n in nodes}
        parents: set = set()
        for e in edges:
            parents.add(e.target)
            pv = node_val[e.source]
            cv = node_val[e.target]
            if cv < pv:
                children[e.source][0] = e.target
            else:
                children[e.source][1] = e.target

        root = next(n.node_id for n in nodes if n.node_id not in parents)
        target_val = int(initial_state.distances["target"])

        visited: set = set()
        comparisons = 0
        curr: Optional[str] = root

        while curr is not None:
            cv = node_val[curr]
            comparisons += 1

            if target_val == cv:
                yield GraphTraversalState(
                    nodes=nodes, edges=edges,
                    visited=frozenset(visited),
                    frontier=(),
                    current=curr,
                    distances={"target": float(target_val), "comparisons": float(comparisons)},
                    path=(curr,),
                    description=f"Found {target_val} at node {curr}! ({comparisons} comparisons)",
                )
                return GraphTraversalState(
                    nodes=nodes, edges=edges,
                    visited=frozenset(visited | {curr}),
                    frontier=(),
                    current=None,
                    distances={"target": float(target_val), "comparisons": float(comparisons)},
                    path=(curr,),
                    description=f"Done: {target_val} found at {curr} in {comparisons} step(s)",
                )
            elif target_val < cv:
                visited.add(curr)
                next_node = children[curr][0]
                yield GraphTraversalState(
                    nodes=nodes, edges=edges,
                    visited=frozenset(visited),
                    frontier=(next_node,) if next_node else (),
                    current=curr,
                    distances={"target": float(target_val), "comparisons": float(comparisons)},
                    path=(),
                    description=f"{target_val} < {cv}: go LEFT from {curr}",
                )
                curr = next_node
            else:
                visited.add(curr)
                next_node = children[curr][1]
                yield GraphTraversalState(
                    nodes=nodes, edges=edges,
                    visited=frozenset(visited),
                    frontier=(next_node,) if next_node else (),
                    current=curr,
                    distances={"target": float(target_val), "comparisons": float(comparisons)},
                    path=(),
                    description=f"{target_val} > {cv}: go RIGHT from {curr}",
                )
                curr = next_node

        return GraphTraversalState(
            nodes=nodes, edges=edges,
            visited=frozenset(visited),
            frontier=(),
            current=None,
            distances={"target": float(target_val), "comparisons": float(comparisons)},
            path=(),
            description=f"Done: {target_val} NOT found ({comparisons} comparison(s))",
        )
