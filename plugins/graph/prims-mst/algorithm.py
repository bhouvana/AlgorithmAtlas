"""Prim's Minimum Spanning Tree plugin for Algorithm Atlas."""
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

    edges = [
        EdgeState(edge_id=f"e{idx}", source=u, target=v, weight=float(w), directed=False)
        for idx, (u, v, w) in enumerate(edge_list)
    ]
    return tuple(nodes), tuple(edges)


class PrimsMSTSimulation(AlgorithmPlugin):
    """
    Prim's MST — O((V+E) log V).

    visited: nodes in MST so far.
    frontier: candidate nodes reachable from MST.
    current: node being added to MST.
    distances: cheapest edge cost connecting each node to MST.
    path: MST addition order.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="prims-mst",
            name="Prim's Minimum Spanning Tree",
            category="graph",
            visualization_type="GRAPH",
            description="Builds a minimum spanning tree by greedily adding the cheapest edge to a new node.",
            intuition="Grow the MST greedily: at each step, add the cheapest edge that connects the MST to a node not yet in it.",
            complexity_time_best="O((V + E) log V)",
            complexity_time_average="O((V + E) log V)",
            complexity_time_worst="O((V + E) log V)",
            complexity_space="O(V)",
            tags=("graph", "mst", "greedy", "spanning-tree", "weighted"),
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
            description=f"Prim's MST from {start}: key[{start}]=0, all others=∞",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges

        adj: Dict[str, List[Tuple[str, float]]] = {nd.node_id: [] for nd in nodes}
        for e in edges:
            w = e.weight or 1.0
            adj[e.source].append((e.target, w))
            adj[e.target].append((e.source, w))

        start = initial_state.frontier[0]
        key: Dict[str, float] = {nd.node_id: _INF for nd in nodes}
        key[start] = 0.0
        in_mst: Set[str] = set()
        mst_order: List[str] = []
        heap: List[Tuple[float, str]] = [(0.0, start)]
        total_cost = 0.0

        while heap:
            cost, u = heapq.heappop(heap)
            if u in in_mst:
                continue
            in_mst.add(u)
            mst_order.append(u)
            total_cost += cost

            candidate_fringe = [v for v in adj if v not in in_mst and key[v] != _INF]
            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset(mst_order[:-1]),
                frontier=tuple(sorted(set(candidate_fringe))),
                current=u,
                distances={k: v for k, v in key.items() if v != _INF},
                path=tuple(mst_order),
                description=f"Add {u} to MST (edge cost {cost:.0f}), total={total_cost:.0f}",
            )

            for v, w in sorted(adj.get(u, []), key=lambda x: x[0]):
                if v not in in_mst and w < key[v]:
                    key[v] = w
                    heapq.heappush(heap, (w, v))

                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(in_mst),
                        frontier=tuple(sorted(vv for vv in key if vv not in in_mst and key[vv] != _INF)),
                        current=u,
                        distances={k: val for k, val in key.items() if val != _INF},
                        path=tuple(mst_order),
                        description=f"Update key[{v}] = {w:.0f} (via {u})",
                    )

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(mst_order),
            frontier=(),
            current=None,
            distances={k: v for k, v in key.items() if v != _INF},
            path=tuple(mst_order),
            description=f"MST complete: total cost = {total_cost:.0f}, nodes: {' → '.join(mst_order)}",
        )
