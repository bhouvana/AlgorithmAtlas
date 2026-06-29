"""Johnson's Algorithm (All-Pairs Shortest Paths) plugin for Algorithm Atlas."""
from __future__ import annotations

import heapq
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

_NODES = [
    ("A", 0.1, 0.5),
    ("B", 0.35, 0.15),
    ("C", 0.35, 0.85),
    ("D", 0.65, 0.5),
    ("E", 0.9, 0.5),
]
# Directed weighted edges — negative edges but NO negative cycles
_EDGES = [
    (0, 1, 1),    # A→B: 1
    (0, 2, 5),    # A→C: 5
    (1, 2, -3),   # B→C: -3 (so A→B→C = -2, better than 5)
    (1, 3, 4),    # B→D: 4
    (2, 3, 2),    # C→D: 2
    (2, 4, 6),    # C→E: 6
    (3, 4, -1),   # D→E: -1
    (4, 0, 10),   # E→A: 10 (positive, so cycle A→…→E→A > 0)
]
_N = len(_NODES)


def _bellman_ford(n, edges, source):
    """Returns potentials h[] or None if negative cycle."""
    INF = float('inf')
    dist = [INF] * n
    dist[source] = 0
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist


def _dijkstra(n, adj, source):
    INF = float('inf')
    dist = [INF] * n
    dist[source] = 0
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    return dist


def _make_nodes(visited, current, source_node):
    nodes = []
    for i, (lbl, x, y) in enumerate(_NODES):
        w = 2.0 if i == current else (1.0 if i in visited else 0.0)
        nodes.append(NodeState(node_id=str(i), label=lbl, x=x, y=y, weight=w))
    return tuple(nodes)


def _make_edges(dist_matrix=None):
    edges = []
    for u, v, w in _EDGES:
        edges.append(EdgeState(
            edge_id=f"e{u}_{v}",
            source=str(u),
            target=str(v),
            weight=float(w),
            directed=True,
        ))
    return tuple(edges)


class JohnsonAlgorithmSimulation(AlgorithmPlugin):
    """Johnson's algorithm visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="johnson-algorithm",
            name="Johnson's Algorithm",
            category="graph",
            visualization_type="GRAPH",
            description="All-pairs shortest paths using Bellman-Ford + Dijkstra.",
            intuition=(
                "Step 1: Bellman-Ford from virtual node to compute potentials h[v]. "
                "Step 2: Reweight edges so all weights ≥ 0. "
                "Step 3: Dijkstra from each node on reweighted graph."
            ),
            complexity_time_best="O(V² log V + VE)",
            complexity_time_average="O(V² log V + VE)",
            complexity_time_worst="O(V² log V + VE)",
            complexity_space="O(V²)",
            tags=("graph", "shortest-path", "all-pairs", "johnson", "dijkstra", "bellman-ford"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        nodes = tuple(
            NodeState(node_id=str(i), label=lbl, x=x, y=y)
            for i, (lbl, x, y) in enumerate(_NODES)
        )
        return GraphTraversalState(
            nodes=nodes,
            edges=_make_edges(),
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description="Johnson's: ready (has negative edges)",
        )

    def steps(self, initial_state: GraphTraversalState) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        edges = _make_edges()
        n = _N

        # Step 1: Bellman-Ford with virtual node
        # Add virtual node n connecting to all others with weight 0
        aug_edges = list(_EDGES) + [(n, i, 0) for i in range(n)]
        h = _bellman_ford(n + 1, aug_edges, n)

        yield GraphTraversalState(
            nodes=_make_nodes(set(range(n)), None, -1),
            edges=edges,
            visited=frozenset(str(i) for i in range(n)),
            frontier=(),
            current=None,
            distances={str(i): round(h[i], 2) for i in range(n)},
            path=(),
            description=f"Bellman-Ford done. Potentials: {[round(h[i],1) for i in range(n)]}",
        )

        # Step 2: Reweight edges
        reweighted = {(u, v): w + h[u] - h[v] for u, v, w in _EDGES}
        adj = {i: [] for i in range(n)}
        for u, v, w in _EDGES:
            adj[u].append((v, reweighted[(u, v)]))

        yield GraphTraversalState(
            nodes=_make_nodes(set(range(n)), None, -1),
            edges=tuple(
                EdgeState(
                    edge_id=f"rw{u}_{v}",
                    source=str(u),
                    target=str(v),
                    weight=round(reweighted[(u, v)], 2),
                    directed=True,
                )
                for u, v, w in _EDGES
            ),
            visited=frozenset(str(i) for i in range(n)),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description="Reweighted edges — all non-negative now",
        )

        # Step 3: Dijkstra from each node
        dist_matrix = []
        for src in range(n):
            d = _dijkstra(n, adj, src)
            # Recover true distances: D[u][v] = d[v] + h[v] - h[u]
            true_d = [d[v] + h[v] - h[src] if d[v] < float('inf') else float('inf') for v in range(n)]
            dist_matrix.append(true_d)
            yield GraphTraversalState(
                nodes=_make_nodes(set(range(n)), src, src),
                edges=edges,
                visited=frozenset(str(i) for i in range(n)),
                frontier=(),
                current=str(src),
                distances={str(v): round(true_d[v], 1) if true_d[v] < 1e8 else None for v in range(n)},
                path=(),
                description=f"Dijkstra from {_NODES[src][0]}: {[round(x,1) if x<1e8 else '∞' for x in true_d]}",
            )

        # Find min non-trivial distance
        min_d = min(
            dist_matrix[u][v]
            for u in range(n) for v in range(n)
            if u != v and dist_matrix[u][v] < float('inf')
        )
        return GraphTraversalState(
            nodes=_make_nodes(set(range(n)), None, -1),
            edges=edges,
            visited=frozenset(str(i) for i in range(n)),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=f"All-pairs done. Min dist={round(min_d,1)}",
        )
