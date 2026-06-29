"""Edmonds-Karp (BFS-based max-flow) plugin for Algorithm Atlas."""
from __future__ import annotations

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

_NODES = [
    ("S", 0.05, 0.5),
    ("A", 0.3, 0.2),
    ("B", 0.3, 0.8),
    ("C", 0.6, 0.2),
    ("D", 0.6, 0.8),
    ("T", 0.9, 0.5),
]
# (u, v, capacity)
_CAPS = [
    (0, 1, 10),
    (0, 2, 8),
    (1, 2, 5),
    (1, 3, 7),
    (2, 4, 9),
    (3, 4, 3),
    (3, 5, 8),
    (4, 5, 10),
]
_SOURCE = 0
_SINK = 5


def _build_graph():
    n = len(_NODES)
    cap = [[0] * n for _ in range(n)]
    for u, v, c in _CAPS:
        cap[u][v] += c
    return cap


def _bfs(cap, source, sink, n):
    parent = [-1] * n
    visited = [False] * n
    visited[source] = True
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in range(n):
            if not visited[v] and cap[u][v] > 0:
                visited[v] = True
                parent[v] = u
                if v == sink:
                    return parent
                queue.append(v)
    return None


class EdmondsKarpSimulation(AlgorithmPlugin):
    """Edmonds-Karp max-flow visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="edmonds-karp",
            name="Edmonds-Karp Algorithm",
            category="graph",
            visualization_type="GRAPH",
            description="Max-flow via BFS augmenting paths.",
            intuition=(
                "BFS finds shortest augmenting path each iteration. "
                "Bottleneck flow is added, residual capacities updated. "
                "Max flow = sum of all augmenting path flows."
            ),
            complexity_time_best="O(VE²)",
            complexity_time_average="O(VE²)",
            complexity_time_worst="O(VE²)",
            complexity_space="O(V+E)",
            tags=("graph", "max-flow", "edmonds-karp", "ford-fulkerson", "bfs", "network-flow"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        nodes = tuple(
            NodeState(node_id=str(i), label=lbl, x=x, y=y)
            for i, (lbl, x, y) in enumerate(_NODES)
        )
        edges = tuple(
            EdgeState(edge_id=f"e{u}_{v}", source=str(u), target=str(v), weight=float(c), directed=True)
            for u, v, c in _CAPS
        )
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=f"Edmonds-Karp: S→T, total cap={sum(c for u,v,c in _CAPS if u==_SOURCE)}",
        )

    def steps(self, initial_state: GraphTraversalState) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        n = len(_NODES)
        cap = _build_graph()
        total_flow = 0
        iteration = 0

        def make_state(path_nodes, flow_added, desc):
            path_set = set(path_nodes)
            nodes = []
            for i, (lbl, x, y) in enumerate(_NODES):
                w = 2.0 if i in path_set else 1.0 if i in {_SOURCE, _SINK} else 0.0
                nodes.append(NodeState(node_id=str(i), label=lbl, x=x, y=y, weight=w))
            edges = []
            for u, v, orig_c in _CAPS:
                remaining = cap[u][v]
                used = orig_c - remaining
                edges.append(EdgeState(
                    edge_id=f"e{u}_{v}",
                    source=str(u), target=str(v),
                    weight=float(remaining),
                    directed=True,
                ))
            return GraphTraversalState(
                nodes=tuple(nodes),
                edges=tuple(edges),
                visited=frozenset(str(i) for i in path_set),
                frontier=(),
                current=str(path_nodes[-1]) if path_nodes else None,
                distances={"flow": float(total_flow + flow_added)},
                path=tuple(str(i) for i in path_nodes),
                description=desc,
            )

        while True:
            parent = _bfs(cap, _SOURCE, _SINK, n)
            if parent is None:
                break
            # Find bottleneck
            path = []
            v = _SINK
            while v != -1:
                path.append(v)
                v = parent[v]
            path.reverse()

            flow = min(cap[path[k]][path[k + 1]] for k in range(len(path) - 1))
            for k in range(len(path) - 1):
                cap[path[k]][path[k + 1]] -= flow
                cap[path[k + 1]][path[k]] += flow

            total_flow += flow
            iteration += 1
            path_names = [_NODES[p][0] for p in path]

            yield make_state(
                path, 0,
                f"Iter {iteration}: path={'→'.join(path_names)} flow={flow} (total={total_flow})",
            )

        final = make_state(
            [], 0,
            f"Max flow = {total_flow} (found in {iteration} iterations)",
        )
        yield final
        return final
