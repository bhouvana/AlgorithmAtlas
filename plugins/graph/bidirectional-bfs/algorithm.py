"""Bidirectional BFS plugin for Algorithm Atlas."""
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
    ("S", 0.05, 0.5),   # 0: source
    ("A", 0.25, 0.2),   # 1
    ("B", 0.25, 0.8),   # 2
    ("C", 0.45, 0.2),   # 3
    ("D", 0.45, 0.5),   # 4
    ("E", 0.45, 0.8),   # 5
    ("F", 0.65, 0.2),   # 6
    ("G", 0.65, 0.8),   # 7
    ("T", 0.85, 0.5),   # 8: target
]
_EDGES = [
    (0, 1), (0, 2),
    (1, 3), (1, 4),
    (2, 4), (2, 5),
    (3, 6), (4, 6), (4, 7),
    (5, 7),
    (6, 8), (7, 8),
]
_SOURCE = 0
_TARGET = 8


def _bfs_build_adj():
    adj = {i: [] for i in range(len(_NODES))}
    for u, v in _EDGES:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def _reconstruct(fwd_parent, bwd_parent, meet):
    path = []
    # Forward path from source to meet
    node = meet
    while node is not None:
        path.append(node)
        node = fwd_parent.get(node)
    path.reverse()
    # Backward path from meet+1 to target
    node = bwd_parent.get(meet)
    while node is not None:
        path.append(node)
        node = bwd_parent.get(node)
    return path


class BidirectionalBFSSimulation(AlgorithmPlugin):
    """Bidirectional BFS from source to target."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bidirectional-bfs",
            name="Bidirectional BFS",
            category="graph",
            visualization_type="GRAPH",
            description="Shortest path via simultaneous BFS from source and target.",
            intuition=(
                "Forward BFS from S, backward BFS from T. "
                "Alternate expanding the smaller frontier. "
                "Stop when a node appears in both visited sets. "
                "Complexity: O(b^(d/2)) vs O(b^d) for one-way BFS."
            ),
            complexity_time_best="O(b^(d/2))",
            complexity_time_average="O(b^(d/2))",
            complexity_time_worst="O(V+E)",
            complexity_space="O(b^(d/2))",
            tags=("graph", "bfs", "shortest-path", "bidirectional", "search"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        nodes = tuple(
            NodeState(node_id=str(i), label=lbl, x=x, y=y)
            for i, (lbl, x, y) in enumerate(_NODES)
        )
        edges = tuple(
            EdgeState(edge_id=f"e{u}_{v}", source=str(u), target=str(v), weight=1.0, directed=False)
            for u, v in _EDGES
        )
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset([str(_SOURCE), str(_TARGET)]),
            frontier=(str(_SOURCE), str(_TARGET)),
            current=None,
            distances={str(_SOURCE): 0.0, str(_TARGET): 0.0},
            path=(),
            description="Bidirectional BFS: S→T",
        )

    def steps(self, initial_state: GraphTraversalState) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        adj = _bfs_build_adj()
        edges = initial_state.edges
        nodes_meta = _NODES

        fwd_visited = {_SOURCE: None}  # node → parent
        bwd_visited = {_TARGET: None}

        fwd_queue = deque([_SOURCE])
        bwd_queue = deque([_TARGET])

        meet = None
        path = []

        def make_state(fwd_vis, bwd_vis, fwd_front, bwd_front, cur, desc, final_path=()):
            colored_nodes = []
            for i, (lbl, x, y) in enumerate(nodes_meta):
                in_fwd = i in fwd_vis
                in_bwd = i in bwd_vis
                in_path = i in final_path
                # weight encodes role: 3=path, 2=both frontiers, 1=fwd, -1=bwd, 0=unvisited
                if in_path:
                    w = 3.0
                elif in_fwd and in_bwd:
                    w = 2.0
                elif in_fwd:
                    w = 1.0
                elif in_bwd:
                    w = -1.0
                else:
                    w = 0.0
                colored_nodes.append(NodeState(node_id=str(i), label=lbl, x=x, y=y, weight=w))
            return GraphTraversalState(
                nodes=tuple(colored_nodes),
                edges=edges,
                visited=frozenset(str(n) for n in (set(fwd_vis) | set(bwd_vis))),
                frontier=tuple(str(n) for n in (fwd_front + bwd_front)),
                current=str(cur) if cur is not None else None,
                distances={str(n): float(d) for n, d in {**{k: 0 for k in fwd_vis}, **{k: 0 for k in bwd_vis}}.items()},
                path=tuple(str(n) for n in final_path),
                description=desc,
            )

        while fwd_queue or bwd_queue:
            # Expand forward frontier
            if fwd_queue:
                node = fwd_queue.popleft()
                for nb in adj[node]:
                    if nb not in fwd_visited:
                        fwd_visited[nb] = node
                        fwd_queue.append(nb)
                        if nb in bwd_visited:
                            meet = nb
                            break
                yield make_state(
                    fwd_visited, bwd_visited,
                    list(fwd_queue), list(bwd_queue),
                    node,
                    f"Forward: expand {nodes_meta[node][0]} → frontier={[nodes_meta[n][0] for n in fwd_queue]}",
                )
                if meet is not None:
                    break

            # Expand backward frontier
            if bwd_queue:
                node = bwd_queue.popleft()
                for nb in adj[node]:
                    if nb not in bwd_visited:
                        bwd_visited[nb] = node
                        bwd_queue.append(nb)
                        if nb in fwd_visited:
                            meet = nb
                            break
                yield make_state(
                    fwd_visited, bwd_visited,
                    list(fwd_queue), list(bwd_queue),
                    node,
                    f"Backward: expand {nodes_meta[node][0]} → frontier={[nodes_meta[n][0] for n in bwd_queue]}",
                )
                if meet is not None:
                    break

        # Reconstruct path
        if meet is not None:
            # Build forward path
            fwd_path = []
            n = meet
            while n is not None:
                fwd_path.append(n)
                n = fwd_visited.get(n)
            fwd_path.reverse()
            # Build backward path
            bwd_path = []
            n = bwd_visited.get(meet)
            while n is not None:
                bwd_path.append(n)
                n = bwd_visited.get(n)
            path = fwd_path + bwd_path

        path_names = [nodes_meta[n][0] for n in path]
        return make_state(
            fwd_visited, bwd_visited, [], [],
            meet,
            f"Path found (len={len(path)-1}): {' → '.join(path_names)}",
            path,
        )
