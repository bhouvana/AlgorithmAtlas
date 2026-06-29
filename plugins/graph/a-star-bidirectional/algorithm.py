"""Bidirectional A* plugin for Algorithm Atlas."""
from __future__ import annotations

import heapq
import math
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
    ("A", 0.2, 0.15),
    ("B", 0.2, 0.85),
    ("C", 0.4, 0.3),
    ("D", 0.4, 0.7),
    ("E", 0.6, 0.15),
    ("F", 0.6, 0.5),
    ("G", 0.6, 0.85),
    ("T", 0.9, 0.5),
]
_EDGES = [
    (0, 1, 2.0), (0, 2, 3.0),
    (1, 3, 2.5), (1, 5, 5.0),
    (2, 4, 2.0), (2, 7, 6.0),
    (3, 5, 2.0), (3, 6, 3.5),
    (4, 6, 3.0), (4, 7, 2.5),
    (5, 8, 3.0),
    (6, 8, 2.0),
    (7, 8, 4.0),
]
_SOURCE = 0
_TARGET = 8


def _heuristic(i, j):
    x1, y1 = _NODES[i][1], _NODES[i][2]
    x2, y2 = _NODES[j][1], _NODES[j][2]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * 6.0  # scale to match edge weights


def _build_adj():
    adj = {i: [] for i in range(len(_NODES))}
    for u, v, w in _EDGES:
        adj[u].append((v, w))
        adj[v].append((u, w))
    return adj


def _make_state(fwd_closed, bwd_closed, fwd_front, bwd_front, cur, path, edges, desc):
    nodes = []
    for i, (lbl, x, y) in enumerate(_NODES):
        in_fwd = i in fwd_closed
        in_bwd = i in bwd_closed
        in_path = i in path
        if in_path:
            w = 3.0
        elif in_fwd and in_bwd:
            w = 2.0
        elif i in fwd_front:
            w = 1.5
        elif i in bwd_front:
            w = -1.5
        elif in_fwd:
            w = 1.0
        elif in_bwd:
            w = -1.0
        else:
            w = 0.0
        nodes.append(NodeState(node_id=str(i), label=lbl, x=x, y=y, weight=w))
    return GraphTraversalState(
        nodes=tuple(nodes),
        edges=edges,
        visited=frozenset(str(i) for i in (fwd_closed | bwd_closed)),
        frontier=tuple(str(i) for i in (fwd_front | bwd_front)),
        current=str(cur) if cur is not None else None,
        distances={},
        path=tuple(str(i) for i in path),
        description=desc,
    )


class BidirectionalAStarSimulation(AlgorithmPlugin):
    """Bidirectional A* pathfinding."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="a-star-bidirectional",
            name="Bidirectional A*",
            category="graph",
            visualization_type="GRAPH",
            description="A* search from both source and target simultaneously.",
            intuition=(
                "Forward A* uses h(n) = dist to T. Backward uses h(n) = dist to S. "
                "Always expand the node with lowest f=g+h in either frontier. "
                "Stop when a node is settled in both frontiers."
            ),
            complexity_time_best="O(b^(d/2))",
            complexity_time_average="O(b^(d/2))",
            complexity_time_worst="O(V+E)",
            complexity_space="O(b^(d/2))",
            tags=("graph", "a-star", "shortest-path", "bidirectional", "heuristic"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        nodes = tuple(
            NodeState(node_id=str(i), label=lbl, x=x, y=y)
            for i, (lbl, x, y) in enumerate(_NODES)
        )
        edges = tuple(
            EdgeState(edge_id=f"e{u}_{v}", source=str(u), target=str(v), weight=w, directed=False)
            for u, v, w in _EDGES
        )
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(str(_SOURCE), str(_TARGET)),
            current=None,
            distances={},
            path=(),
            description="Bidirectional A*: S→T",
        )

    def steps(self, initial_state: GraphTraversalState) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        adj = _build_adj()
        edges = initial_state.edges

        INF = float('inf')
        fwd_g = [INF] * len(_NODES)
        bwd_g = [INF] * len(_NODES)
        fwd_g[_SOURCE] = 0.0
        bwd_g[_TARGET] = 0.0
        fwd_parent = {_SOURCE: None}
        bwd_parent = {_TARGET: None}
        fwd_closed = set()
        bwd_closed = set()

        fwd_pq = [(0 + _heuristic(_SOURCE, _TARGET), 0.0, _SOURCE)]
        bwd_pq = [(0 + _heuristic(_TARGET, _SOURCE), 0.0, _TARGET)]

        best = INF
        best_meet = None

        def _reconstruct(meet):
            fwd_path = []
            n = meet
            while n is not None:
                fwd_path.append(n)
                n = fwd_parent.get(n)
            fwd_path.reverse()
            bwd_path = []
            n = bwd_parent.get(meet)
            while n is not None:
                bwd_path.append(n)
                n = bwd_parent.get(n)
            return fwd_path + bwd_path

        MAX_STEPS = 30
        step_count = 0

        while (fwd_pq or bwd_pq) and step_count < MAX_STEPS:
            # Choose which frontier to expand
            expand_fwd = True
            if fwd_pq and bwd_pq:
                expand_fwd = fwd_pq[0][0] <= bwd_pq[0][0]
            elif bwd_pq:
                expand_fwd = False

            if expand_fwd and fwd_pq:
                f, g, u = heapq.heappop(fwd_pq)
                if u in fwd_closed:
                    continue
                fwd_closed.add(u)
                step_count += 1

                if u in bwd_closed:
                    d = fwd_g[u] + bwd_g[u]
                    if d < best:
                        best = d
                        best_meet = u

                fwd_front = {n for _, _, n in fwd_pq if n not in fwd_closed}
                bwd_front = {n for _, _, n in bwd_pq if n not in bwd_closed}
                yield _make_state(
                    fwd_closed, bwd_closed, fwd_front, bwd_front, u, [], edges,
                    f"Forward: expand {_NODES[u][0]} (g={g:.1f}, f={f:.1f})",
                )

                for v, w in adj[u]:
                    ng = fwd_g[u] + w
                    if ng < fwd_g[v]:
                        fwd_g[v] = ng
                        fwd_parent[v] = u
                        h = _heuristic(v, _TARGET)
                        heapq.heappush(fwd_pq, (ng + h, ng, v))

            elif bwd_pq:
                f, g, u = heapq.heappop(bwd_pq)
                if u in bwd_closed:
                    continue
                bwd_closed.add(u)
                step_count += 1

                if u in fwd_closed:
                    d = fwd_g[u] + bwd_g[u]
                    if d < best:
                        best = d
                        best_meet = u

                fwd_front = {n for _, _, n in fwd_pq if n not in fwd_closed}
                bwd_front = {n for _, _, n in bwd_pq if n not in bwd_closed}
                yield _make_state(
                    fwd_closed, bwd_closed, fwd_front, bwd_front, u, [], edges,
                    f"Backward: expand {_NODES[u][0]} (g={g:.1f}, f={f:.1f})",
                )

                for v, w in adj[u]:
                    ng = bwd_g[u] + w
                    if ng < bwd_g[v]:
                        bwd_g[v] = ng
                        bwd_parent[v] = u
                        h = _heuristic(v, _SOURCE)
                        heapq.heappush(bwd_pq, (ng + h, ng, v))

            # Check termination
            fwd_min = fwd_pq[0][0] if fwd_pq else INF
            bwd_min = bwd_pq[0][0] if bwd_pq else INF
            if best <= fwd_min and best <= bwd_min:
                break

        path = _reconstruct(best_meet) if best_meet is not None else []
        path_names = [_NODES[n][0] for n in path]
        return _make_state(
            fwd_closed, bwd_closed, set(), set(),
            best_meet, path, edges,
            f"Path (cost={best:.1f}): {' → '.join(path_names)}",
        )
