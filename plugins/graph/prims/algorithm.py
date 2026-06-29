"""Prim's Minimum Spanning Tree plugin for Algorithm Atlas."""
from __future__ import annotations

import heapq
import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

_INF = 999999.0


def _make_graph(rng: random.Random, n: int):
    """Generate connected weighted undirected graph."""
    labels = [chr(65 + i) for i in range(n)]  # A, B, C, ...

    # Positions in a rough circle
    import math
    positions = {}
    for i, lbl in enumerate(labels):
        angle = 2 * math.pi * i / n
        positions[lbl] = (0.5 + 0.38 * math.cos(angle), 0.5 + 0.38 * math.sin(angle))

    # Ensure connectivity: random spanning tree first
    adj: dict[str, dict[str, float]] = {lbl: {} for lbl in labels}
    perm = labels[:]
    rng.shuffle(perm)
    for i in range(1, n):
        u = perm[i]
        v = perm[rng.randint(0, i - 1)]
        w = float(rng.randint(1, 9))
        adj[u][v] = w
        adj[v][u] = w

    # Add extra edges
    for _ in range(n):
        u, v = rng.sample(labels, 2)
        if v not in adj[u]:
            w = float(rng.randint(1, 9))
            adj[u][v] = w
            adj[v][u] = w

    nodes = [
        NodeState(node_id=lbl, label=lbl, x=positions[lbl][0], y=positions[lbl][1])
        for lbl in labels
    ]
    edges = []
    seen = set()
    for u in labels:
        for v, w in adj[u].items():
            key = tuple(sorted([u, v]))
            if key not in seen:
                seen.add(key)
                edges.append(EdgeState(edge_id=f"{u}-{v}", source=u, target=v, weight=w, directed=False))

    return nodes, edges, adj, labels[0]


def _prim_mst_weight(adj: dict, start: str) -> float:
    """Compute total MST weight."""
    in_mst = {start}
    heap = [(w, start, v) for v, w in adj[start].items()]
    heapq.heapify(heap)
    total = 0.0
    while heap and len(in_mst) < len(adj):
        w, u, v = heapq.heappop(heap)
        if v in in_mst:
            continue
        in_mst.add(v)
        total += w
        for nxt, nw in adj[v].items():
            if nxt not in in_mst:
                heapq.heappush(heap, (nw, v, nxt))
    return total


class PrimsSimulation(AlgorithmPlugin):
    """Prim's MST."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="prims",
            name="Prim's Minimum Spanning Tree",
            category="graph",
            visualization_type="GRAPH",
            description="Grow a minimum spanning tree by greedily adding the cheapest outgoing edge.",
            intuition=(
                "Maintain a set of MST nodes. At each step, add the edge with minimum weight "
                "that crosses the cut between MST and non-MST nodes."
            ),
            complexity_time_best="O((V+E) log V)",
            complexity_time_average="O((V+E) log V)",
            complexity_time_worst="O(E log V)",
            complexity_space="O(V+E)",
            tags=("graph", "mst", "prims", "greedy"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 6))
        nodes, edges, adj, start = _make_graph(rng, n)
        mst_weight = _prim_mst_weight(adj, start)
        distances = {nd.node_id: _INF for nd in nodes}
        distances[start] = 0.0
        return GraphTraversalState(
            nodes=tuple(nodes),
            edges=tuple(edges),
            visited=frozenset(),
            frontier=(start,),
            current=None,
            distances=distances,
            path=tuple(),
            description=f"Prim's MST start={start} expected_weight={mst_weight:.0f}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        desc = initial_state.description
        start = desc.split("start=")[1].split(" ")[0]

        # Rebuild adj from edges
        adj: dict[str, dict[str, float]] = {nd.node_id: {} for nd in initial_state.nodes}
        for ed in initial_state.edges:
            u, v, w = ed.source, ed.target, ed.weight
            adj[u][v] = w
            adj[v][u] = w

        in_mst: set[str] = {start}
        heap: list = [(w, start, v) for v, w in adj[start].items()]
        heapq.heapify(heap)
        mst_edges: list = []
        total_weight = 0.0
        distances = {nd.node_id: _INF for nd in initial_state.nodes}
        distances[start] = 0.0

        while heap and len(in_mst) < len(adj):
            w, u, v = heapq.heappop(heap)
            if v in in_mst:
                continue
            in_mst.add(v)
            total_weight += w
            mst_edges.append((u, v))
            distances[v] = w

            yield GraphTraversalState(
                nodes=initial_state.nodes,
                edges=initial_state.edges,
                visited=frozenset(in_mst),
                frontier=tuple(adj[v].keys() - in_mst),
                current=v,
                distances=dict(distances),
                path=tuple(v for _, v in mst_edges),
                description=f"Added edge {u}-{v} (w={w:.0f}), MST weight so far={total_weight:.0f}",
            )

            for nxt, nw in adj[v].items():
                if nxt not in in_mst:
                    heapq.heappush(heap, (nw, v, nxt))

        return GraphTraversalState(
            nodes=initial_state.nodes,
            edges=initial_state.edges,
            visited=frozenset(in_mst),
            frontier=tuple(),
            current=None,
            distances=dict(distances),
            path=tuple(v for _, v in mst_edges),
            description=f"MST complete, total weight={total_weight:.0f}",
        )
