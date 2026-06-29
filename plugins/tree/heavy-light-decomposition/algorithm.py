"""Heavy-Light Decomposition plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

# Tree as adjacency list (undirected). Root = 0.
# Structure:
#         0
#        / \
#       1   2
#      /|    \
#     3  4    5
#    /
#   6
_TREE_EDGES = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (3, 6)]
_N = 7
_ROOT = 0
_NODE_POS = [
    (0.50, 0.08),  # 0
    (0.25, 0.28),  # 1
    (0.75, 0.28),  # 2
    (0.15, 0.52),  # 3
    (0.38, 0.52),  # 4
    (0.75, 0.52),  # 5
    (0.08, 0.76),  # 6
]


def _build_adj(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def _compute_subtree_sizes(adj, root, n):
    size = [1] * n
    parent = [-1] * n
    order = []
    stack = [root]
    visited = [False] * n
    visited[root] = True
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                stack.append(v)
    for u in reversed(order):
        if parent[u] != -1:
            size[parent[u]] += size[u]
    return size, parent


def _hld(adj, root, n, size, parent):
    heavy = [-1] * n
    for u in range(n):
        max_sz, hchild = 0, -1
        for v in adj[u]:
            if v != parent[u] and size[v] > max_sz:
                max_sz = size[v]
                hchild = v
        heavy[u] = hchild
    # Assign chain IDs
    chain = [-1] * n
    cid = 0
    for u in range(n):
        if parent[u] == -1 or heavy[parent[u]] != u:
            # u is a chain head
            v = u
            while v != -1:
                chain[v] = cid
                v = heavy[v]
            cid += 1
    return heavy, chain, cid


class HeavyLightDecompositionSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="heavy-light-decomposition",
            name="Heavy-Light Decomposition",
            category="tree",
            visualization_type="GRAPH",
            description="Decompose a tree into heavy-edge chains enabling O(log² n) path queries.",
            intuition=(
                "Each node takes the edge to its largest-subtree child as its heavy edge. "
                "All other edges are light. Any root-to-leaf path crosses O(log n) chains. "
                "Nodes in each chain get contiguous positions in a segment tree."
            ),
            complexity_time_best="O(n) build, O(log² n) per query",
            complexity_time_average="O(n) build, O(log² n) per query",
            complexity_time_worst="O(n) build, O(log² n) per query",
            complexity_space="O(n)",
            tags=("tree", "heavy-light-decomposition", "hld", "path-query", "chains"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        nodes = tuple(
            NodeState(node_id=str(i), label=str(i), x=x, y=y)
            for i, (x, y) in enumerate(_NODE_POS)
        )
        edges = tuple(
            EdgeState(
                edge_id=f"e{u}_{v}",
                source=str(u),
                target=str(v),
                weight=0.0,
                directed=False,
            )
            for u, v in _TREE_EDGES
        )
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=f"Tree: {_N} nodes, root={_ROOT}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        adj = _build_adj(_N, _TREE_EDGES)
        size, parent = _compute_subtree_sizes(adj, _ROOT, _N)
        heavy, chain, num_chains = _hld(adj, _ROOT, _N, size, parent)
        computed: set = set()

        # Phase 1: Show subtree sizes
        yield GraphTraversalState(
            nodes=tuple(
                NodeState(node_id=str(i), label=f"{i}(sz={size[i]})",
                          x=_NODE_POS[i][0], y=_NODE_POS[i][1], weight=float(size[i]))
                for i in range(_N)
            ),
            edges=initial_state.edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={str(i): float(size[i]) for i in range(_N)},
            path=(),
            description=f"Subtree sizes computed: {size}",
        )

        # Phase 2: Show heavy edges one by one
        heavy_edge_set: set = set()
        for u in range(_N):
            if heavy[u] != -1:
                heavy_edge_set.add((u, heavy[u]))
                heavy_edge_set.add((heavy[u], u))
                yield GraphTraversalState(
                    nodes=tuple(
                        NodeState(
                            node_id=str(i),
                            label=str(i),
                            x=_NODE_POS[i][0],
                            y=_NODE_POS[i][1],
                            weight=2.0 if i in {u, heavy[u]} else 0.0,
                        )
                        for i in range(_N)
                    ),
                    edges=tuple(
                        EdgeState(
                            edge_id=f"e{min(a,b)}_{max(a,b)}",
                            source=str(a),
                            target=str(b),
                            weight=2.0 if (a, b) in heavy_edge_set or (b, a) in heavy_edge_set else 0.0,
                            directed=False,
                        )
                        for a, b in _TREE_EDGES
                    ),
                    visited=frozenset(str(n) for n in {u, heavy[u]}),
                    frontier=(),
                    current=str(u),
                    distances={},
                    path=(),
                    description=f"Heavy edge: {u} → {heavy[u]} (subtree size {size[heavy[u]]})",
                )

        # Phase 3: Show final chain assignment
        # Each chain gets a unique weight ID for colour coding
        chain_colors = {i: float(chain[i] + 1) for i in range(_N)}
        final = GraphTraversalState(
            nodes=tuple(
                NodeState(
                    node_id=str(i),
                    label=f"{i}(c{chain[i]})",
                    x=_NODE_POS[i][0],
                    y=_NODE_POS[i][1],
                    weight=chain_colors[i],
                )
                for i in range(_N)
            ),
            edges=tuple(
                EdgeState(
                    edge_id=f"e{min(u,v)}_{max(u,v)}",
                    source=str(u),
                    target=str(v),
                    weight=2.0 if (u, v) in heavy_edge_set or (v, u) in heavy_edge_set else 0.0,
                    directed=False,
                )
                for u, v in _TREE_EDGES
            ),
            visited=frozenset(str(i) for i in range(_N)),
            frontier=(),
            current=None,
            distances={str(i): float(chain[i]) for i in range(_N)},
            path=(),
            description=f"HLD complete: {num_chains} chains, heavy_children={heavy}",
        )
        yield final
        return final
