"""Topological Sort (Kahn's algorithm) plugin for Algorithm Atlas."""
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


def _build_dag(
    rng: random.Random, n: int
) -> Tuple[Tuple[NodeState, ...], Tuple[EdgeState, ...]]:
    """Build a random DAG with n nodes. Edges always go from lower to higher label index."""
    labels = [chr(ord("A") + i) for i in range(n)]
    edge_set: set = set()
    edge_list: List[Tuple[str, str]] = []

    # Random spanning DAG edges (i→j where i < j)
    for j in range(1, n):
        i = rng.randint(0, j - 1)
        key = (labels[i], labels[j])
        if key not in edge_set:
            edge_set.add(key)
            edge_list.append(key)

    # Extra edges (also i→j, i < j)
    extra = max(1, n // 3)
    attempts, added = 0, 0
    while added < extra and attempts < 200:
        attempts += 1
        i = rng.randint(0, n - 2)
        j = rng.randint(i + 1, n - 1)
        key = (labels[i], labels[j])
        if key not in edge_set:
            edge_set.add(key)
            edge_list.append(key)
            added += 1

    # Layered layout: nodes arranged by longest path from source
    nodes = []
    for k, label in enumerate(labels):
        angle = 2 * math.pi * k / n - math.pi / 2
        x = round(0.5 + 0.42 * math.cos(angle), 4)
        y = round(0.5 + 0.42 * math.sin(angle), 4)
        nodes.append(NodeState(node_id=label, label=label, x=x, y=y))

    edges = [
        EdgeState(edge_id=f"e{idx}", source=u, target=v, directed=True)
        for idx, (u, v) in enumerate(edge_list)
    ]
    return tuple(nodes), tuple(edges)


class TopologicalSortSimulation(AlgorithmPlugin):
    """
    Kahn's topological sort — O(V + E).

    visited: nodes already placed in topological order.
    frontier: nodes with in-degree 0 (ready to process).
    current: node being dequeued.
    distances: current in-degree of each node (shrinks as predecessors are removed).
    path: topological order so far.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="topological-sort",
            name="Topological Sort (Kahn's)",
            category="graph",
            visualization_type="GRAPH",
            description="Orders a DAG's nodes so every edge u→v has u before v.",
            intuition="Repeatedly remove nodes with no remaining prerequisites. Each removed node gets the next position in the ordering.",
            complexity_time_best="O(V + E)",
            complexity_time_average="O(V + E)",
            complexity_time_worst="O(V + E)",
            complexity_space="O(V)",
            tags=("graph", "dag", "topological-sort", "kahn", "scheduling"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("node_count", 7), 10))
        nodes, edges = _build_dag(rng, n)

        # Compute in-degrees
        in_deg: Dict[str, float] = {nd.node_id: 0.0 for nd in nodes}
        for e in edges:
            in_deg[e.target] = in_deg.get(e.target, 0.0) + 1.0

        zero_in = tuple(sorted(nd.node_id for nd in nodes if in_deg[nd.node_id] == 0.0))
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=zero_in,
            current=None,
            distances=dict(in_deg),
            path=(),
            description=f"Kahn's: {len(zero_in)} nodes with in-degree 0 → {zero_in}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges

        # Build adjacency and in-degree
        adj: Dict[str, List[str]] = {nd.node_id: [] for nd in nodes}
        in_deg: Dict[str, int] = {nd.node_id: 0 for nd in nodes}
        for e in edges:
            adj[e.source].append(e.target)
            in_deg[e.target] += 1

        queue: deque[str] = deque(sorted(nd.node_id for nd in nodes if in_deg[nd.node_id] == 0))
        order: List[str] = []

        while queue:
            u = queue.popleft()
            order.append(u)

            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset(order[:-1]),
                frontier=tuple(queue),
                current=u,
                distances={k: float(v) for k, v in in_deg.items()},
                path=tuple(order),
                description=f"Remove {u} (in-deg 0): append to order, decrement neighbors",
            )

            for v in sorted(adj[u]):
                in_deg[v] -= 1
                if in_deg[v] == 0:
                    queue.append(v)

                yield GraphTraversalState(
                    nodes=nodes,
                    edges=edges,
                    visited=frozenset(order),
                    frontier=tuple(queue),
                    current=u,
                    distances={k: float(v) for k, v in in_deg.items()},
                    path=tuple(order),
                    description=f"Decrement in-deg[{v}] to {in_deg[v]}"
                    + (" → add to queue" if in_deg[v] == 0 else ""),
                )

        has_cycle = len(order) < len(nodes)
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(order),
            frontier=(),
            current=None,
            distances={k: float(v) for k, v in in_deg.items()},
            path=tuple(order),
            description=(
                "Cycle detected — not a DAG!"
                if has_cycle
                else "Order: " + " → ".join(order)
            ),
        )
