"""Depth-First Search plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
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

    shuffled = labels[:]
    rng.shuffle(shuffled)
    for i in range(1, n):
        j = rng.randint(0, i - 1)
        u, v = shuffled[i], shuffled[j]
        key = (min(u, v), max(u, v))
        edge_set.add(key)
        edge_list.append((u, v))

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


class DFSSimulation(AlgorithmPlugin):
    """
    Depth-First Search — iterative, O(V + E).

    Uses an explicit LIFO stack. Neighbors are pushed in reverse-sorted order
    so that alphabetically-first neighbor is explored first (consistent, deterministic).

    frontier: current DFS stack (next-to-process is frontier[-1]).
    visited:  nodes already processed (green in renderer).
    current:  node currently being expanded (amber).
    distances: discovery order index (0-based counter, not hop count).
    path:     DFS traversal order — sequence of nodes as they were popped/visited.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="dfs",
            name="Depth-First Search",
            category="graph",
            visualization_type="GRAPH",
            description="Explores a graph as deep as possible along each branch before backtracking.",
            intuition=(
                "Navigate a maze by always taking the first unexplored passage — "
                "backtrack only when you reach a dead end."
            ),
            complexity_time_best="O(V + E)",
            complexity_time_average="O(V + E)",
            complexity_time_worst="O(V + E)",
            complexity_space="O(V)",
            tags=("graph", "traversal", "stack", "backtracking", "depth"),
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
            distances={},
            path=(),
            description=f"DFS from {start}: push {start} onto stack",
        )

    def steps(
        self,
        initial_state: GraphTraversalState,
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges
        adj = _build_adj(nodes, edges)

        start = initial_state.frontier[0]
        stack: List[str] = [start]
        visited: Set[str] = set()
        distances: Dict[str, float] = {}
        path: List[str] = []
        discovery_counter = 0

        while stack:
            current = stack.pop()

            if current in visited:
                # Already visited via another path — skip
                yield GraphTraversalState(
                    nodes=nodes,
                    edges=edges,
                    visited=frozenset(visited),
                    frontier=tuple(stack),
                    current=current,
                    distances=dict(distances),
                    path=tuple(path),
                    description=f"Pop {current}: already visited, skip",
                )
                continue

            visited.add(current)
            path.append(current)
            distances[current] = float(discovery_counter)
            discovery_counter += 1

            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset(visited),
                frontier=tuple(stack),
                current=current,
                distances=dict(distances),
                path=tuple(path),
                description=(
                    f"Visit {current} (discovery #{discovery_counter - 1}): "
                    f"neighbors = {sorted(adj[current])}"
                ),
            )

            # Push unvisited neighbors in reverse-sorted order so
            # alphabetically-first is popped next (consistent ordering).
            for neighbor in sorted(adj[current], reverse=True):
                if neighbor not in visited:
                    stack.append(neighbor)

                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(visited),
                        frontier=tuple(stack),
                        current=current,
                        distances=dict(distances),
                        path=tuple(path),
                        description=f"Push {neighbor} (unvisited neighbor of {current})",
                    )

        node_ids = [nd.node_id for nd in nodes]
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(visited),
            frontier=(),
            current=None,
            distances=dict(distances),
            path=tuple(path),
            description=(
                f"DFS complete: visited {len(visited)}/{len(node_ids)} nodes — "
                + " → ".join(path)
            ),
        )
