"""Level-Order (BFS) Tree Traversal plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from collections import deque
from typing import Dict, Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)


def _build_bst(rng: random.Random, n: int):
    """Build a random BST. Returns (root, values, children, nodes, edges)."""
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
    q = [root]
    max_depth = 0
    while q:
        node = q.pop(0)
        d = depths[node]
        max_depth = max(max_depth, d)
        for child in filter(None, children[node]):
            depths[child] = d + 1
            q.append(child)

    x_pos: Dict[str, int] = {}
    counter = [0]

    def _inorder_assign(nid):
        if nid is None:
            return
        _inorder_assign(children[nid][0])
        x_pos[nid] = counter[0]
        counter[0] += 1
        _inorder_assign(children[nid][1])

    _inorder_assign(root)
    max_x = max(x_pos.values()) if x_pos else 0

    node_list = [
        NodeState(
            node_id=nid,
            label=str(values[nid]),
            x=0.05 + 0.9 * x_pos[nid] / max_x if max_x else 0.5,
            y=0.06 + 0.82 * depths[nid] / max_depth if max_depth else 0.1,
        )
        for nid in sorted(values, key=lambda k: int(k[1:]))
    ]
    edges = []
    eid = 0
    for nid, (left, right) in children.items():
        if left:
            edges.append(EdgeState(edge_id=f"e{eid}", source=nid, target=left, directed=True))
            eid += 1
        if right:
            edges.append(EdgeState(edge_id=f"e{eid}", source=nid, target=right, directed=True))
            eid += 1

    return root, values, children, tuple(node_list), tuple(edges)


class LevelOrderSimulation(AlgorithmPlugin):
    """
    Level-Order (BFS) Traversal — visit all nodes level by level.

    GraphTraversalState:
      visited: nodes already processed
      frontier: current BFS queue (nodes to visit next)
      path: nodes in level-order visit sequence
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="level-order",
            name="Level-Order Traversal (BFS)",
            category="tree",
            visualization_type="TREE",
            description=(
                "Visit binary tree nodes level by level, "
                "from root to leaves, left to right within each level."
            ),
            intuition=(
                "Use a queue. Dequeue a node, visit it, enqueue its children. "
                "All level-d nodes are processed before any level-(d+1) node."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("tree", "bfs", "level-order", "traversal", "queue"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("array_size", 7), 15))
        root, values, children, node_states, edge_states = _build_bst(rng, n)
        return GraphTraversalState(
            nodes=node_states,
            edges=edge_states,
            visited=frozenset(),
            frontier=(root,),
            current=None,
            distances={"depth": 0.0},
            path=(),
            description=f"Start BFS from root {root} (value={values[root]})",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        # Rebuild tree structure from edges
        children: Dict[str, List[str]] = {n.node_id: [] for n in initial_state.nodes}
        values: Dict[str, str] = {n.node_id: n.label for n in initial_state.nodes}
        for e in initial_state.edges:
            children[e.source].append(e.target)

        root = initial_state.frontier[0]
        queue: deque = deque([root])
        visited: set = set()
        path: list = []
        depth: Dict[str, int] = {root: 0}

        while queue:
            node = queue.popleft()
            visited.add(node)
            path.append(node)

            for child in sorted(children[node]):
                if child not in visited and child not in set(queue):
                    depth[child] = depth[node] + 1
                    queue.append(child)

            yield GraphTraversalState(
                nodes=initial_state.nodes,
                edges=initial_state.edges,
                visited=frozenset(visited),
                frontier=tuple(queue),
                current=node,
                distances={"depth": float(depth[node])},
                path=tuple(path),
                description=f"Visit {node} (value={values[node]}, depth={depth[node]})",
            )

        return GraphTraversalState(
            nodes=initial_state.nodes,
            edges=initial_state.edges,
            visited=frozenset(visited),
            frontier=(),
            current=None,
            distances={"total_nodes": float(len(visited))},
            path=tuple(path),
            description=f"Level-order: {' → '.join(values[n] for n in path)}",
        )
