"""Bellman-Ford shortest-path plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from typing import Dict, Generator, List, Optional, Tuple

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
    """Random connected weighted undirected graph (positive weights only — no negative cycles)."""
    labels = [chr(ord("A") + i) for i in range(n)]
    edge_set: set = set()
    edge_list: List[Tuple[str, str, int]] = []

    shuffled = labels[:]
    rng.shuffle(shuffled)
    for i in range(1, n):
        j = rng.randint(0, i - 1)
        u, v = shuffled[i], shuffled[j]
        key = (min(u, v), max(u, v))
        edge_set.add(key)
        edge_list.append((u, v, rng.randint(1, 9)))

    extra = max(1, n // 3)
    attempts, added = 0, 0
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

    nodes = []
    for i, label in enumerate(labels):
        angle = 2 * math.pi * i / n - math.pi / 2
        x = round(0.5 + 0.42 * math.cos(angle), 4)
        y = round(0.5 + 0.42 * math.sin(angle), 4)
        nodes.append(NodeState(node_id=label, label=label, x=x, y=y))

    # Undirected edges represented as directed pairs for relaxation
    edges = [
        EdgeState(edge_id=f"e{idx}", source=u, target=v, weight=float(w), directed=False)
        for idx, (u, v, w) in enumerate(edge_list)
    ]
    return tuple(nodes), tuple(edges)


def _all_directed_pairs(
    edges: Tuple[EdgeState, ...]
) -> List[Tuple[str, str, float]]:
    """For undirected graph: each edge becomes two directed relaxation pairs."""
    pairs = []
    for e in edges:
        w = e.weight or 1.0
        pairs.append((e.source, e.target, w))
        pairs.append((e.target, e.source, w))
    return sorted(pairs)


class BellmanFordSimulation(AlgorithmPlugin):
    """
    Bellman-Ford — O(V·E).

    Relaxes all edges V-1 times.
    distances[v]: shortest known distance from source.
    visited:      nodes with finalized distances (updated this round).
    frontier:     nodes updated in the current iteration (show activity).
    current:      most recently relaxed-to node.
    path:         order in which nodes got their first finite distance.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bellman-ford",
            name="Bellman-Ford Shortest Path",
            category="graph",
            visualization_type="GRAPH",
            description="Finds shortest paths from a source, handles negative weights, detects negative cycles.",
            intuition="Relax all edges V-1 times. Each round can only improve distances by at most one edge hop. After V-1 rounds, all shortest paths are found (if no negative cycle exists).",
            complexity_time_best="O(V · E)",
            complexity_time_average="O(V · E)",
            complexity_time_worst="O(V · E)",
            complexity_space="O(V)",
            tags=("graph", "shortest-path", "dynamic-programming", "negative-weights", "weighted"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("node_count", 6), 8))
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
            description=f"Bellman-Ford from {start}: {n-1} relaxation rounds needed",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges
        pairs = _all_directed_pairs(edges)
        node_ids = [n.node_id for n in nodes]
        start = initial_state.frontier[0]
        V = len(node_ids)

        dist: Dict[str, float] = {nid: _INF for nid in node_ids}
        dist[start] = 0.0
        first_found_order: List[str] = [start]

        for iteration in range(1, V):
            updated_this_round: List[str] = []

            for u, v, w in pairs:
                if dist[u] == _INF:
                    continue
                new_d = dist[u] + w
                if new_d < dist[v]:
                    old = dist[v]
                    dist[v] = new_d
                    updated_this_round.append(v)
                    if v not in first_found_order:
                        first_found_order.append(v)

                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(first_found_order[:-1]) if len(first_found_order) > 1 else frozenset(),
                        frontier=tuple(sorted(set(updated_this_round))),
                        current=v,
                        distances={k: val for k, val in dist.items() if val != _INF},
                        path=tuple(first_found_order),
                        description=(
                            f"Round {iteration}: relax {u}→{v} "
                            f"({dist[u]:.0f}+{w:.0f}={new_d:.0f} < "
                            f"{'∞' if old == _INF else f'{old:.0f}'})"
                        ),
                    )

            if not updated_this_round:
                yield GraphTraversalState(
                    nodes=nodes,
                    edges=edges,
                    visited=frozenset(first_found_order),
                    frontier=(),
                    current=None,
                    distances={k: val for k, val in dist.items() if val != _INF},
                    path=tuple(first_found_order),
                    description=f"Round {iteration}: no relaxations — converged early",
                )
                break

        reachable = {k: val for k, val in dist.items() if val != _INF}
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(first_found_order),
            frontier=(),
            current=None,
            distances=reachable,
            path=tuple(first_found_order),
            description=(
                f"Done: {len(reachable)}/{V} nodes reachable. "
                + ", ".join(f"{k}={v:.0f}" for k, v in sorted(reachable.items()))
            ),
        )
