"""0-1 BFS (Deque BFS) plugin for Algorithm Atlas."""
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

# Fixed 7-node graph designed to showcase 0-1 BFS behaviour.
# 0-weight edges allow "free" teleports; 1-weight edges cost one step.
# Source=0, Target=6.
#
#   0 --0-- 1 --0-- 3
#   |       |       |
#   1       1       0
#   |       |       |
#   2 --0-- 4 --1-- 5 --0-- 6
#
# Optimal: 0→1→3→5... wait, let me verify:
# 0→1 (0), 1→3 (0), 3→5 (0), 5→6 (0) = cost 0
# All 0-weight path exists!
#
# Actually let me use a better graph where not everything is 0:
# Nodes: 0-6
# Edges (undirected):
#   0-1: 0, 0-2: 1, 1-3: 0, 1-4: 1, 2-4: 0, 3-5: 1, 4-5: 0, 5-6: 0
# Optimal 0→6: 0→1→3... 3-5 costs 1, then 5→6 costs 0 = 0+0+1+0=1
# or 0→1→4→5→6: 0+1+0+0=1, or 0→2→4→5→6: 1+0+0+0=1
# or can we do it with cost 0? 0→1→3... 3 only connects to 1 and 5 (cost 1). No 0-cost path to 6.

_NODES_POS = [
    (0.1, 0.35),  # 0 - source
    (0.35, 0.15),  # 1
    (0.35, 0.55),  # 2
    (0.60, 0.15),  # 3
    (0.60, 0.55),  # 4
    (0.82, 0.35),  # 5
    (0.97, 0.35),  # 6 - target
]

# (u, v, weight)
_EDGES = [
    (0, 1, 0),
    (0, 2, 1),
    (1, 3, 0),
    (1, 4, 1),
    (2, 4, 0),
    (3, 5, 1),
    (4, 5, 0),
    (5, 6, 0),
]

_SOURCE = 0
_TARGET = 6
_N = len(_NODES_POS)


def _build_adj():
    adj = {i: [] for i in range(_N)}
    for u, v, w in _EDGES:
        adj[u].append((v, w))
        adj[v].append((u, w))
    return adj


def _make_graph_state(
    dist: dict,
    visited: frozenset,
    frontier: tuple,
    current: str | None,
    desc: str,
) -> GraphTraversalState:
    nodes = []
    for i, (x, y) in enumerate(_NODES_POS):
        d = dist.get(i, float("inf"))
        label = f"{i}({'∞' if d == float('inf') else d})"
        nodes.append(NodeState(node_id=str(i), label=label, x=x, y=y))

    edges = []
    for u, v, w in _EDGES:
        edges.append(EdgeState(
            edge_id=f"{u}-{v}",
            source=str(u),
            target=str(v),
            weight=float(w),
            directed=False,
        ))

    return GraphTraversalState(
        nodes=tuple(nodes),
        edges=tuple(edges),
        visited=visited,
        frontier=frontier,
        current=current,
        distances={str(i): float(d) for i, d in dist.items()},
        path=tuple(),
        description=desc,
    )


class ZeroOneBFSSimulation(AlgorithmPlugin):
    """0-1 BFS for shortest paths with 0/1 edge weights."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="0-1-bfs",
            name="0-1 BFS (Deque BFS)",
            category="graph",
            visualization_type="GRAPH",
            description="Shortest paths in a graph with 0/1 edge weights via deque BFS.",
            intuition=(
                "Use a deque. 0-weight edges push neighbour to front (free move). "
                "1-weight edges push to back (one step). "
                "Nodes at front always have minimum known distance."
            ),
            complexity_time_best="O(V + E)",
            complexity_time_average="O(V + E)",
            complexity_time_worst="O(V + E)",
            complexity_space="O(V)",
            tags=("graph", "bfs", "shortest-path", "deque"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        dist = {_SOURCE: 0}
        return _make_graph_state(
            dist,
            visited=frozenset(),
            frontier=(str(_SOURCE),),
            current=str(_SOURCE),
            desc=f"0-1 BFS from {_SOURCE} to {_TARGET}. Deque: [{_SOURCE}]",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        adj = _build_adj()
        dist = {i: float("inf") for i in range(_N)}
        dist[_SOURCE] = 0
        dq = deque([_SOURCE])
        visited: set = set()

        while dq:
            u = dq.popleft()
            if u in visited:
                continue
            visited.add(u)

            for v, w in adj[u]:
                new_d = dist[u] + w
                if new_d < dist[v]:
                    dist[v] = new_d
                    if w == 0:
                        dq.appendleft(v)
                    else:
                        dq.append(v)

            yield _make_graph_state(
                dist,
                visited=frozenset(str(n) for n in visited),
                frontier=tuple(str(n) for n in dq),
                current=str(u),
                desc=(
                    f"Processed node {u} (dist={dist[u]}). "
                    f"Deque: {list(dq)}"
                ),
            )

        # Reconstruct shortest path
        path = []
        cur = _TARGET
        prev = {i: None for i in range(_N)}
        # Re-run to capture predecessors
        dist2 = {i: float("inf") for i in range(_N)}
        dist2[_SOURCE] = 0
        dq2 = deque([_SOURCE])
        vis2: set = set()
        while dq2:
            u = dq2.popleft()
            if u in vis2:
                continue
            vis2.add(u)
            for v, w in adj[u]:
                nd = dist2[u] + w
                if nd < dist2[v]:
                    dist2[v] = nd
                    prev[v] = u
                    if w == 0:
                        dq2.appendleft(v)
                    else:
                        dq2.append(v)

        cur = _TARGET
        while cur is not None:
            path.append(str(cur))
            cur = prev[cur]
        path.reverse()

        return _make_graph_state(
            dist2,
            visited=frozenset(str(n) for n in range(_N)),
            frontier=tuple(),
            current=str(_TARGET),
            desc=(
                f"Done: dist({_SOURCE}→{_TARGET})={dist2[_TARGET]}, "
                f"path={' → '.join(path)}"
            ),
        )
