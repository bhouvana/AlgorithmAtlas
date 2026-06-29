"""Tarjan's Bridge Finding plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

# Graph with clear bridges:
# 0-1-2 form a chain (0-1 and 1-2 are bridges)
# 2-3-4-2 form a cycle (no bridges)
# 4-5 is a bridge
# 5-6-7-5 form a cycle (no bridges)
_NODES = [
    ("0", 0.05, 0.5),
    ("1", 0.2, 0.5),
    ("2", 0.4, 0.5),
    ("3", 0.55, 0.3),
    ("4", 0.55, 0.7),
    ("5", 0.75, 0.5),
    ("6", 0.9, 0.3),
    ("7", 0.9, 0.7),
]
_EDGES = [
    (0, 1),  # bridge
    (1, 2),  # bridge
    (2, 3),
    (3, 4),
    (4, 2),  # cycle: 2-3-4
    (4, 5),  # bridge
    (5, 6),
    (6, 7),
    (7, 5),  # cycle: 5-6-7
]
_BRIDGES = {frozenset({0, 1}), frozenset({1, 2}), frozenset({4, 5})}


def _find_bridges(n, adj):
    disc = [-1] * n
    low = [-1] * n
    bridges = set()
    timer = [0]

    def dfs(u, parent):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        for v in adj[u]:
            if disc[v] == -1:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.add(frozenset({u, v}))
            elif v != parent:
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if disc[i] == -1:
            dfs(i, -1)
    return bridges, disc, low


class TarjanBridgesSimulation(AlgorithmPlugin):
    """Tarjan's bridge-finding visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="tarjan-bridges",
            name="Tarjan's Bridge Finding",
            category="graph",
            visualization_type="GRAPH",
            description="Find all bridges in an undirected graph.",
            intuition=(
                "DFS assigns disc[] and low[]. "
                "low[v] = min discovery time reachable from v's subtree via back-edges. "
                "Edge (u,v) is a bridge iff low[v] > disc[u]."
            ),
            complexity_time_best="O(V+E)",
            complexity_time_average="O(V+E)",
            complexity_time_worst="O(V+E)",
            complexity_space="O(V)",
            tags=("graph", "tarjan", "bridge", "dfs", "connectivity"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        nodes = tuple(
            NodeState(node_id=str(i), label=lbl, x=x, y=y)
            for i, (lbl, x, y) in enumerate(_NODES)
        )
        edges = tuple(
            EdgeState(edge_id=f"e{u}_{v}", source=str(u), target=str(v), directed=False)
            for u, v in _EDGES
        )
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description="Tarjan bridges: find all bridge edges",
        )

    def steps(self, initial_state: GraphTraversalState) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        n = len(_NODES)
        adj = [[] for _ in range(n)]
        for u, v in _EDGES:
            adj[u].append(v)
            adj[v].append(u)

        disc = [-1] * n
        low = [-1] * n
        found_bridges = set()
        timer = [0]
        dfs_order = []

        def dfs(u, parent):
            disc[u] = low[u] = timer[0]
            timer[0] += 1
            dfs_order.append(u)
            for v in adj[u]:
                if disc[v] == -1:
                    dfs(v, u)
                    low[u] = min(low[u], low[v])
                    if low[v] > disc[u]:
                        found_bridges.add(frozenset({u, v}))
                elif v != parent:
                    low[u] = min(low[u], disc[v])

        dfs(0, -1)

        # Emit one step per discovered node
        for idx, u in enumerate(dfs_order):
            def make_state(visited_so_far, bridges_so_far, current_node, desc):
                nodes = []
                for i, (lbl, x, y) in enumerate(_NODES):
                    if i == current_node:
                        w = 2.0
                    elif i in visited_so_far:
                        w = 1.0
                    else:
                        w = 0.0
                    nodes.append(NodeState(node_id=str(i), label=lbl, x=x, y=y, weight=w))
                edges = []
                for eu, ev in _EDGES:
                    is_bridge = frozenset({eu, ev}) in bridges_so_far
                    edges.append(EdgeState(
                        edge_id=f"e{eu}_{ev}",
                        source=str(eu), target=str(ev),
                        weight=3.0 if is_bridge else 1.0,
                        directed=False,
                    ))
                return GraphTraversalState(
                    nodes=tuple(nodes),
                    edges=tuple(edges),
                    visited=frozenset(str(i) for i in visited_so_far),
                    frontier=(),
                    current=str(current_node),
                    distances={str(i): float(disc[i]) for i in visited_so_far if disc[i] >= 0},
                    path=tuple(str(x) for x in dfs_order[:idx + 1]),
                    description=desc,
                )

            visited_so_far = set(dfs_order[:idx + 1])
            bridges_so_far = {b for b in found_bridges if b <= visited_so_far}
            yield make_state(
                visited_so_far, bridges_so_far, u,
                f"Visit {_NODES[u][0]}: disc={disc[u]}, low={low[u]}, bridges={len(bridges_so_far)}",
            )

        # Final state showing all bridges
        def final_state():
            nodes = []
            for i, (lbl, x, y) in enumerate(_NODES):
                nodes.append(NodeState(node_id=str(i), label=lbl, x=x, y=y, weight=1.0))
            edges = []
            for eu, ev in _EDGES:
                is_bridge = frozenset({eu, ev}) in found_bridges
                edges.append(EdgeState(
                    edge_id=f"e{eu}_{ev}",
                    source=str(eu), target=str(ev),
                    weight=3.0 if is_bridge else 1.0,
                    directed=False,
                ))
            bridge_names = [f"{min(b)}-{max(b)}" for b in found_bridges]
            return GraphTraversalState(
                nodes=tuple(nodes),
                edges=tuple(edges),
                visited=frozenset(str(i) for i in range(n)),
                frontier=(),
                current=None,
                distances={str(i): float(disc[i]) for i in range(n)},
                path=(),
                description=f"Done: {len(found_bridges)} bridges found: {bridge_names}",
            )

        return final_state()
