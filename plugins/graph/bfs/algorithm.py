"""Breadth-First Search plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from collections import deque
from typing import Dict, Generator, List, Set, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)


def _build_adj(
    nodes: Tuple[NodeState, ...], edges: Tuple[EdgeState, ...]
) -> Dict[str, List[str]]:
    adj: Dict[str, List[str]] = {n.node_id: [] for n in nodes}
    for e in edges:
        adj[e.source].append(e.target)
        adj[e.target].append(e.source)
    return adj


def _make_graph(
    rng: random.Random, n: int, extra: int
) -> Tuple[Tuple[NodeState, ...], Tuple[EdgeState, ...]]:
    """Generate a random connected undirected graph with n nodes."""
    labels = [chr(ord("A") + i) for i in range(n)]

    edge_set: set = set()
    edge_list: List[Tuple[str, str]] = []

    # Random spanning tree: connect each node to a random earlier node
    shuffled = labels[:]
    rng.shuffle(shuffled)
    for i in range(1, n):
        j = rng.randint(0, i - 1)
        u, v = shuffled[i], shuffled[j]
        key = (min(u, v), max(u, v))
        edge_set.add(key)
        edge_list.append((u, v))

    # Extra edges
    attempts = 0
    added = 0
    while added < extra and attempts < 200:
        attempts += 1
        u = rng.choice(labels)
        v = rng.choice(labels)
        if u != v:
            key = (min(u, v), max(u, v))
            if key not in edge_set:
                edge_set.add(key)
                edge_list.append((u, v))
                added += 1

    # Circular layout: nodes evenly spaced around a unit circle
    nodes = []
    for i, label in enumerate(labels):
        angle = 2 * math.pi * i / n - math.pi / 2
        x = round(0.5 + 0.42 * math.cos(angle), 4)
        y = round(0.5 + 0.42 * math.sin(angle), 4)
        nodes.append(NodeState(node_id=label, label=label, x=x, y=y))

    edges = [
        EdgeState(edge_id=f"e{idx}", source=u, target=v, directed=False)
        for idx, (u, v) in enumerate(edge_list)
    ]

    return tuple(nodes), tuple(edges)


class BFSSimulation(AlgorithmPlugin):
    """
    Breadth-First Search — O(V + E).

    Uses a FIFO queue. Explores nodes level by level, so the shortest-hop
    path from start to any reachable node is discovered first.

    frontier: current BFS queue (next-to-process is frontier[0]).
    visited:  nodes already dequeued and fully explored (green in renderer).
    current:  node currently being expanded (amber).
    distances: BFS level (hop count from start node).
    path:     traversal order — sequence of nodes as they were dequeued.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bfs",
            name="Breadth-First Search",
            category="graph",
            visualization_type="GRAPH",
            description="Explores a graph level by level using a FIFO queue.",
            intuition=(
                "Drop a stone in a pond — ripples spread one ring at a time, "
                "reaching every reachable point at the same distance simultaneously."
            ),
            complexity_time_best="O(V + E)",
            complexity_time_average="O(V + E)",
            complexity_time_worst="O(V + E)",
            complexity_space="O(V)",
            tags=("graph", "traversal", "queue", "shortest-path", "level-order"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(3, min(params.inputs.get("node_count", 8), 12))
        extra: int = params.inputs.get("extra_edges", n // 3)

        nodes, edges = _make_graph(rng, n, extra)

        labels = [nd.node_id for nd in nodes]
        start: str = params.inputs.get("start_node", labels[0])
        if start not in labels:
            start = labels[0]

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(start,),
            current=None,
            distances={start: 0.0},
            path=(),
            description=f"BFS from {start}: enqueue {start} (level 0)",
        )

    def steps(
        self,
        initial_state: GraphTraversalState,
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges
        adj = _build_adj(nodes, edges)

        start = initial_state.frontier[0]
        queue: deque[str] = deque([start])
        enqueued: Set[str] = {start}   # tracks nodes ever added to queue
        distances: Dict[str, float] = {start: 0.0}
        path: List[str] = []

        while queue:
            current = queue.popleft()
            path.append(current)

            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset(path[:-1]),      # nodes fully processed before this
                frontier=tuple(queue),
                current=current,
                distances=dict(distances),
                path=tuple(path),
                description=(
                    f"Dequeue {current} (level {int(distances[current])}): "
                    f"neighbors = {sorted(adj[current])}"
                ),
            )

            for neighbor in sorted(adj[current]):
                if neighbor not in enqueued:
                    enqueued.add(neighbor)
                    distances[neighbor] = distances[current] + 1.0
                    queue.append(neighbor)

                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(path),
                        frontier=tuple(queue),
                        current=current,
                        distances=dict(distances),
                        path=tuple(path),
                        description=(
                            f"Discover {neighbor} from {current} → level {int(distances[neighbor])}, "
                            f"enqueue {neighbor}"
                        ),
                    )

        node_ids = [nd.node_id for nd in nodes]
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(path),
            frontier=(),
            current=None,
            distances=dict(distances),
            path=tuple(path),
            description=(
                f"BFS complete: visited {len(path)}/{len(node_ids)} nodes — "
                + " → ".join(path)
            ),
        )
