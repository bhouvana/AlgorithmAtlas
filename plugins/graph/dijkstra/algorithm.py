"""Dijkstra's shortest-path plugin for Algorithm Atlas."""
from __future__ import annotations

import heapq
import math
import random
from typing import Dict, Generator, List, Optional, Set, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

_INF = float("inf")


def _build_weighted_graph(
    rng: random.Random, n: int
) -> Tuple[Tuple[NodeState, ...], Tuple[EdgeState, ...]]:
    """Random connected weighted undirected graph with positive integer weights."""
    labels = [chr(ord("A") + i) for i in range(n)]
    edge_set: set = set()
    edge_list: List[Tuple[str, str, int]] = []

    # Random spanning tree
    shuffled = labels[:]
    rng.shuffle(shuffled)
    for i in range(1, n):
        j = rng.randint(0, i - 1)
        u, v = shuffled[i], shuffled[j]
        key = (min(u, v), max(u, v))
        edge_set.add(key)
        edge_list.append((u, v, rng.randint(1, 9)))

    # A few extra edges for variety
    extra = max(1, n // 3)
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
                edge_list.append((u, v, rng.randint(1, 9)))
                added += 1

    # Circular layout
    nodes = []
    for i, label in enumerate(labels):
        angle = 2 * math.pi * i / n - math.pi / 2
        x = round(0.5 + 0.42 * math.cos(angle), 4)
        y = round(0.5 + 0.42 * math.sin(angle), 4)
        nodes.append(NodeState(node_id=label, label=label, x=x, y=y))

    edges = [
        EdgeState(edge_id=f"e{idx}", source=u, target=v, weight=float(w), directed=False)
        for idx, (u, v, w) in enumerate(edge_list)
    ]
    return tuple(nodes), tuple(edges)


def _build_adj(
    edges: Tuple[EdgeState, ...]
) -> Dict[str, List[Tuple[str, float]]]:
    adj: Dict[str, List[Tuple[str, float]]] = {}
    for e in edges:
        adj.setdefault(e.source, []).append((e.target, e.weight or 1.0))
        adj.setdefault(e.target, []).append((e.source, e.weight or 1.0))
    return adj


class DijkstraSimulation(AlgorithmPlugin):
    """
    Dijkstra's algorithm — O((V+E) log V) using a min-heap.

    distances[v]: shortest known distance from source.
    visited:      settled nodes (distance is final).
    frontier:     nodes currently in the heap (discovered, not yet settled).
    current:      node being settled at this step.
    path:         settlement order (ordered by distance from source).
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="dijkstra",
            name="Dijkstra's Shortest Path",
            category="graph",
            visualization_type="GRAPH",
            description="Finds shortest paths from a source node using a greedy priority queue.",
            intuition="Greedily settle the nearest unsettled node. Each settlement is final — no shorter path can later be found through unvisited nodes with higher distance.",
            complexity_time_best="O((V + E) log V)",
            complexity_time_average="O((V + E) log V)",
            complexity_time_worst="O((V + E) log V)",
            complexity_space="O(V)",
            tags=("graph", "shortest-path", "greedy", "priority-queue", "weighted"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("node_count", 7), 10))
        nodes, edges = _build_weighted_graph(rng, n)
        start = nodes[0].node_id
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(start,),
            current=None,
            distances={start: 0.0},
            path=(),
            description=f"Dijkstra from {start}: dist[{start}]=0, all others=∞",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges
        adj = _build_adj(edges)

        start = initial_state.frontier[0]
        dist: Dict[str, float] = {n.node_id: _INF for n in nodes}
        dist[start] = 0.0
        heap: List[Tuple[float, str]] = [(0.0, start)]
        settled: Set[str] = set()
        settlement_order: List[str] = []

        while heap:
            d, u = heapq.heappop(heap)
            if u in settled:
                continue
            settled.add(u)
            settlement_order.append(u)

            # Show the settlement step
            frontier_nodes = [v for v, _ in heap if v not in settled]
            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset(settlement_order[:-1]),
                frontier=tuple(sorted(set(frontier_nodes))),
                current=u,
                distances={k: v for k, v in dist.items() if v != _INF},
                path=tuple(settlement_order),
                description=f"Settle {u} (dist={d:.0f}): examining neighbors",
            )

            for v, w in sorted(adj.get(u, []), key=lambda x: x[0]):
                if v in settled:
                    continue
                new_dist = d + w
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    heapq.heappush(heap, (new_dist, v))

                    frontier_after = [x for _, x in heap if x not in settled]
                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(settlement_order),
                        frontier=tuple(sorted(set(frontier_after))),
                        current=u,
                        distances={k: v for k, v in dist.items() if v != _INF},
                        path=tuple(settlement_order),
                        description=f"Relax {u}→{v}: dist[{v}] updated to {new_dist:.0f}",
                    )

        reachable = {k: v for k, v in dist.items() if v != _INF}
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(settlement_order),
            frontier=(),
            current=None,
            distances=reachable,
            path=tuple(settlement_order),
            description=(
                f"Done: settled {len(settled)}/{len(nodes)} nodes. "
                + ", ".join(f"{k}={v:.0f}" for k, v in sorted(reachable.items()))
            ),
        )
