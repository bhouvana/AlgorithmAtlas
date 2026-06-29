"""Morris Inorder Traversal plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from collections import deque
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)


def _build_bst(rng: random.Random, n: int):
    """Build BST, return (children dict, root, NodeState list, EdgeState list, positions)."""
    values = sorted(rng.sample(range(1, 99), n))
    rng.shuffle(values)

    left: dict[int, int | None] = {}
    right: dict[int, int | None] = {}
    root_val = values[0]
    left[root_val] = None
    right[root_val] = None

    for v in values[1:]:
        cur = root_val
        while True:
            if v < cur:
                if left[cur] is None:
                    left[cur] = v
                    left[v] = None
                    right[v] = None
                    break
                else:
                    cur = left[cur]
            else:
                if right[cur] is None:
                    right[cur] = v
                    left[v] = None
                    right[v] = None
                    break
                else:
                    cur = right[cur]

    # BFS layout
    pos: dict[int, tuple[float, float]] = {}
    queue: deque = deque([(root_val, 0, 0.5, 0.25)])
    while queue:
        node, depth, cx, spread = queue.popleft()
        pos[node] = (cx, depth * 0.18)
        if left[node] is not None:
            queue.append((left[node], depth + 1, cx - spread, spread / 2))
        if right[node] is not None:
            queue.append((right[node], depth + 1, cx + spread, spread / 2))

    all_nodes = list(left.keys())
    nodes = [NodeState(node_id=str(v), label=str(v), x=pos[v][0], y=pos[v][1]) for v in all_nodes]
    edges = []
    for v in all_nodes:
        if left[v] is not None:
            edges.append(EdgeState(edge_id=f"{v}-{left[v]}", source=str(v), target=str(left[v]), weight=0.0, directed=True))
        if right[v] is not None:
            edges.append(EdgeState(edge_id=f"{v}-{right[v]}", source=str(v), target=str(right[v]), weight=1.0, directed=True))

    return left, right, root_val, nodes, edges


def _inorder_sorted(left: dict, right: dict, root: int) -> list[int]:
    """Standard recursive inorder for verification."""
    result = []
    def dfs(node):
        if node is None: return
        dfs(left[node])
        result.append(node)
        dfs(right[node])
    dfs(root)
    return result


class MorrisTraversalSimulation(AlgorithmPlugin):
    """Morris Inorder Traversal."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="morris-traversal",
            name="Morris Inorder Traversal",
            category="tree",
            visualization_type="TREE",
            description="Inorder traversal using O(1) space by temporarily threading predecessor links.",
            intuition=(
                "For each node: if no left child, visit it and go right. "
                "Otherwise find inorder predecessor; if it has no right, link it to current node "
                "and go left; else unlink and visit current node."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("tree", "morris", "inorder", "threaded-tree"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 7))
        left, right, root, nodes, edges = _build_bst(rng, n)
        sorted_order = _inorder_sorted(left, right, root)
        return GraphTraversalState(
            nodes=tuple(nodes),
            edges=tuple(edges),
            visited=frozenset(),
            frontier=tuple(),
            current=None,
            distances={nd.node_id: 0.0 for nd in nodes},
            path=tuple(),
            description=f"Morris inorder root={root} expected={sorted_order}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        desc = initial_state.description
        root = int(desc.split("root=")[1].split(" ")[0])

        # Rebuild BST from edges
        left: dict[int, int | None] = {}
        right: dict[int, int | None] = {}
        for nd in initial_state.nodes:
            left[int(nd.node_id)] = None
            right[int(nd.node_id)] = None
        for ed in initial_state.edges:
            src, tgt = int(ed.source), int(ed.target)
            if ed.weight == 0.0:
                left[src] = tgt
            else:
                right[src] = tgt

        result = []
        cur = root

        while cur is not None:
            if left[cur] is None:
                result.append(cur)
                yield GraphTraversalState(
                    nodes=initial_state.nodes,
                    edges=initial_state.edges,
                    visited=frozenset(str(v) for v in result),
                    frontier=tuple(),
                    current=str(cur),
                    distances={nd.node_id: float(i+1) if nd.node_id in [str(v) for v in result] else 0.0
                               for i, nd in enumerate(initial_state.nodes)},
                    path=tuple(str(v) for v in result),
                    description=f"Visit {cur} (no left child), result={result}",
                )
                cur = right[cur]
            else:
                # Find inorder predecessor
                pred = left[cur]
                while right[pred] is not None and right[pred] != cur:
                    pred = right[pred]

                if right[pred] is None:
                    # Make thread
                    right[pred] = cur
                    cur = left[cur]
                else:
                    # Remove thread and visit
                    right[pred] = None
                    result.append(cur)
                    yield GraphTraversalState(
                        nodes=initial_state.nodes,
                        edges=initial_state.edges,
                        visited=frozenset(str(v) for v in result),
                        frontier=tuple([str(pred)]),
                        current=str(cur),
                        distances={nd.node_id: 0.0 for nd in initial_state.nodes},
                        path=tuple(str(v) for v in result),
                        description=f"Visit {cur} (unthreaded from {pred}), result={result}",
                    )
                    cur = right[cur]

        return GraphTraversalState(
            nodes=initial_state.nodes,
            edges=initial_state.edges,
            visited=frozenset(str(v) for v in result),
            frontier=tuple(),
            current=None,
            distances={nd.node_id: 0.0 for nd in initial_state.nodes},
            path=tuple(str(v) for v in result),
            description=f"Inorder = {result}",
        )
