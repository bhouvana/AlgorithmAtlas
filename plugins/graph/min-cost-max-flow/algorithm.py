"""Min-Cost Max-Flow (SPFA successive-shortest-paths) plugin for Algorithm Atlas."""
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
    ("S", 0.05, 0.50),
    ("A", 0.35, 0.20),
    ("B", 0.35, 0.80),
    ("C", 0.65, 0.20),
    ("D", 0.65, 0.80),
    ("T", 0.95, 0.50),
]
# (u, v, capacity, cost)
_EDGE_DATA = [
    (0, 1, 3, 1),
    (0, 2, 2, 2),
    (1, 3, 2, 2),
    (1, 4, 1, 4),
    (2, 3, 1, 1),
    (2, 4, 2, 1),
    (3, 5, 3, 3),
    (4, 5, 3, 2),
]
_SOURCE = 0
_SINK = 5


def _build_graph(n, edge_data):
    graph = [[] for _ in range(n)]
    fwd_indices = []
    for u, v, cap, cost in edge_data:
        fwd_indices.append((u, len(graph[u])))
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])
    return graph, fwd_indices


def _spfa(graph, n, source, sink):
    INF = float("inf")
    dist = [INF] * n
    in_queue = [False] * n
    prev = [-1] * n
    prev_edge = [-1] * n
    dist[source] = 0
    q = deque([source])
    in_queue[source] = True
    while q:
        u = q.popleft()
        in_queue[u] = False
        for idx, (v, cap, cost, _) in enumerate(graph[u]):
            if cap > 0 and dist[u] + cost < dist[v]:
                dist[v] = dist[u] + cost
                prev[v] = u
                prev_edge[v] = idx
                if not in_queue[v]:
                    q.append(v)
                    in_queue[v] = True
    if dist[sink] == INF:
        return None, None, None
    path = []
    v = sink
    while v != -1:
        path.append(v)
        v = prev[v]
    path.reverse()
    flow = min(graph[path[i]][prev_edge[path[i + 1]]][1] for i in range(len(path) - 1))
    return path, flow, prev_edge


class MinCostMaxFlowSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="min-cost-max-flow",
            name="Min-Cost Max-Flow",
            category="graph",
            visualization_type="GRAPH",
            description="Find maximum flow with minimum cost using SPFA to find cheapest augmenting paths.",
            intuition=(
                "Repeatedly find the minimum-cost augmenting path via SPFA "
                "(Bellman-Ford BFS on the residual graph). Augment along it. "
                "The total flow is maximised while total cost is minimised."
            ),
            complexity_time_best="O(VE² log V)",
            complexity_time_average="O(VE² log V)",
            complexity_time_worst="O(VE² log V)",
            complexity_space="O(V+E)",
            tags=("graph", "min-cost-max-flow", "network-flow", "spfa", "shortest-path"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        nodes = tuple(
            NodeState(node_id=str(i), label=lbl, x=x, y=y)
            for i, (lbl, x, y) in enumerate(_NODES)
        )
        edges = tuple(
            EdgeState(
                edge_id=f"e{u}_{v}",
                source=str(u),
                target=str(v),
                weight=float(cap),
                directed=True,
            )
            for u, v, cap, cost in _EDGE_DATA
        )
        src_cap = sum(c for u, _, c, __ in _EDGE_DATA if u == _SOURCE)
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=f"Min-Cost Max-Flow: source cap={src_cap}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        n = len(_NODES)
        graph, fwd_indices = _build_graph(n, _EDGE_DATA)
        total_flow = 0
        total_cost = 0
        iteration = 0

        def make_state(path_nodes, desc):
            path_set = {str(v) for v in path_nodes}
            nodes = [
                NodeState(
                    node_id=str(i),
                    label=lbl,
                    x=x,
                    y=y,
                    weight=2.0 if str(i) in path_set else 1.0 if i in {_SOURCE, _SINK} else 0.0,
                )
                for i, (lbl, x, y) in enumerate(_NODES)
            ]
            edges = []
            for (u_fi, eidx), (u, v, orig_cap, cost) in zip(fwd_indices, _EDGE_DATA):
                rem = graph[u_fi][eidx][1]
                edges.append(
                    EdgeState(
                        edge_id=f"e{u}_{v}",
                        source=str(u),
                        target=str(v),
                        weight=float(rem),
                        directed=True,
                    )
                )
            return GraphTraversalState(
                nodes=tuple(nodes),
                edges=tuple(edges),
                visited=frozenset(str(v) for v in path_nodes),
                frontier=(),
                current=str(path_nodes[-1]) if path_nodes else None,
                distances={"flow": float(total_flow), "cost": float(total_cost)},
                path=tuple(str(v) for v in path_nodes),
                description=desc,
            )

        while True:
            path, flow, prev_edge = _spfa(graph, n, _SOURCE, _SINK)
            if path is None:
                break
            path_cost = sum(
                graph[path[i]][prev_edge[path[i + 1]]][2] for i in range(len(path) - 1)
            )
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                eidx = prev_edge[v]
                rev = graph[u][eidx][3]
                graph[u][eidx][1] -= flow
                graph[v][rev][1] += flow
            total_flow += flow
            total_cost += flow * path_cost
            iteration += 1
            path_labels = [_NODES[p][0] for p in path]
            yield make_state(
                path,
                f"Iter {iteration}: {'→'.join(path_labels)} "
                f"flow={flow} path_cost={path_cost} "
                f"(total_flow={total_flow} total_cost={total_cost})",
            )

        final = make_state(
            [],
            f"Done: max flow={total_flow} min cost={total_cost} ({iteration} iterations)",
        )
        yield final
        return final
