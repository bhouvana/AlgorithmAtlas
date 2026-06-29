"""Diameter of a Binary Tree plugin for Algorithm Atlas."""
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
    """Build a BST and return (nodes, edges, positions)."""
    values = sorted(rng.sample(range(1, 99), n))
    rng.shuffle(values)

    # Build BST
    children: dict[int, list[int]] = {}
    parent: dict[int, int | None] = {}
    root_val = values[0]
    children[root_val] = []
    parent[root_val] = None

    for v in values[1:]:
        cur = root_val
        while True:
            if v < cur:
                left_child = children[cur][0] if len(children[cur]) > 0 and children[cur][0] < cur else None
                if left_child is None:
                    # check if first child is less
                    lefts = [c for c in children[cur] if c < cur]
                    if lefts:
                        cur = lefts[0]
                    else:
                        children[cur].append(v)
                        children[v] = []
                        parent[v] = cur
                        break
                else:
                    cur = left_child
            else:
                rights = [c for c in children[cur] if c > cur]
                if rights:
                    cur = rights[0]
                else:
                    children[cur].append(v)
                    children[v] = []
                    parent[v] = cur
                    break

    # BFS layout
    pos: dict[int, tuple[float, float]] = {}
    queue: deque = deque([(root_val, 0, 0.5, 0.25)])
    while queue:
        node, depth, cx, spread = queue.popleft()
        pos[node] = (cx, depth * 0.18)
        kids = sorted(children[node])
        lefts = [k for k in kids if k < node]
        rights = [k for k in kids if k > node]
        if lefts:
            queue.append((lefts[0], depth + 1, cx - spread, spread / 2))
        if rights:
            queue.append((rights[0], depth + 1, cx + spread, spread / 2))

    nodes = [
        NodeState(node_id=str(v), label=str(v), x=pos[v][0], y=pos[v][1])
        for v in children
    ]
    edges = [
        EdgeState(edge_id=f"{p}-{v}", source=str(p), target=str(v), weight=1.0, directed=False)
        for v, p in parent.items()
        if p is not None
    ]
    return nodes, edges, children, root_val


def _dfs_diameter(children: dict, node: int):
    """Post-order DFS, returns (height, diameter, path_pair, order)."""
    # Iterative post-order with (node, phase) stack
    stack = [(node, False)]
    height: dict[int, int] = {}
    diam = [0]
    best_pair = [None, None]
    visit_order = []

    while stack:
        cur, processed = stack.pop()
        if processed:
            visit_order.append(cur)
            kids = sorted(children[cur])
            h_kids = sorted([height[k] for k in kids], reverse=True)
            if len(h_kids) == 0:
                height[cur] = 0
            elif len(h_kids) == 1:
                height[cur] = h_kids[0] + 1
            else:
                height[cur] = h_kids[0] + 1
                through = h_kids[0] + h_kids[1] + 2
                if through > diam[0]:
                    diam[0] = through
                    best_pair[0] = kids[0]
                    best_pair[1] = kids[1]
        else:
            stack.append((cur, True))
            for k in sorted(children[cur]):
                stack.append((k, False))

    return height[node], diam[0], best_pair, visit_order


class DiameterSimulation(AlgorithmPlugin):
    """Diameter of a Binary Tree."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="diameter",
            name="Diameter of a Tree",
            category="tree",
            visualization_type="TREE",
            description="Find the longest path between any two nodes in a binary tree.",
            intuition=(
                "Post-order DFS: at each node, the diameter through it is "
                "left_height + right_height + 2. Track the global maximum."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(h)",
            tags=("tree", "diameter", "dfs", "binary-tree"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 7))
        nodes, edges, children, root = _build_bst(rng, n)
        _, diam, _, _ = _dfs_diameter(children, root)
        return GraphTraversalState(
            nodes=tuple(nodes),
            edges=tuple(edges),
            visited=frozenset(),
            frontier=tuple(),
            current=None,
            distances={nd.node_id: -1.0 for nd in nodes},
            path=tuple(),
            description=f"Find diameter of BST (root={root}). Expected={diam} edges",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        rng = random.Random(0)
        desc = initial_state.description
        n = len(initial_state.nodes)
        # Rebuild tree from edges
        children: dict[int, list[int]] = {}
        for nd in initial_state.nodes:
            children[int(nd.node_id)] = []
        for ed in initial_state.edges:
            src, tgt = int(ed.source), int(ed.target)
            children[src].append(tgt)

        root = int(desc.split("root=")[1].split(")")[0])
        _, diam, _, visit_order = _dfs_diameter(children, root)

        heights: dict[str, float] = {}
        visited: set[str] = set()

        for node in visit_order:
            visited.add(str(node))
            kids = children[node]
            h_kids = [heights.get(str(k), 0.0) for k in kids]
            h_kids.sort(reverse=True)
            if not h_kids:
                heights[str(node)] = 0.0
            else:
                heights[str(node)] = h_kids[0] + 1

            yield GraphTraversalState(
                nodes=initial_state.nodes,
                edges=initial_state.edges,
                visited=frozenset(visited),
                frontier=tuple(),
                current=str(node),
                distances=dict(heights),
                path=tuple(),
                description=f"DFS post-order at node {node}, height={heights[str(node)]:.0f}",
            )

        return GraphTraversalState(
            nodes=initial_state.nodes,
            edges=initial_state.edges,
            visited=frozenset(nd.node_id for nd in initial_state.nodes),
            frontier=tuple(),
            current=None,
            distances=dict(heights),
            path=tuple(),
            description=f"Diameter = {diam} edges",
        )
