"""Kruskal's Minimum Spanning Tree plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from typing import Dict, Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)


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


class UnionFind:
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.rank = {n: 0 for n in nodes}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


class KruskalsMSTSimulation(AlgorithmPlugin):
    """
    Kruskal's MST — O(E log E).

    visited: nodes in the MST with at least one edge.
    frontier: nodes being considered in current edge check.
    current: most recently added node (one endpoint of added edge).
    distances: number of MST edges each node participates in.
    path: MST nodes in order they gained their first MST edge.
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="kruskals-mst",
            name="Kruskal's Minimum Spanning Tree",
            category="graph",
            visualization_type="GRAPH",
            description="Builds an MST by processing edges in weight order, adding each that doesn't create a cycle.",
            intuition="Sort all edges by weight. Add the lightest edge that connects two different components. Use Union-Find to detect cycles in O(α(n)) ≈ O(1) per edge.",
            complexity_time_best="O(E log E)",
            complexity_time_average="O(E log E)",
            complexity_time_worst="O(E log E)",
            complexity_space="O(V)",
            tags=("graph", "mst", "greedy", "union-find", "spanning-tree", "weighted"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("node_count", 7), 10))
        nodes, edges = _build_weighted_graph(rng, n)
        sorted_edges = sorted(edges, key=lambda e: e.weight or 0)
        min_w = sorted_edges[0].weight if sorted_edges else 0
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={nd.node_id: 0.0 for nd in nodes},
            path=(),
            description=f"Kruskal's: {len(edges)} edges sorted by weight. Lightest={min_w:.0f}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges
        node_ids = [nd.node_id for nd in nodes]

        sorted_edges = sorted(edges, key=lambda e: e.weight or 0)
        uf = UnionFind(node_ids)
        mst_nodes: set = set()
        mst_first: List[str] = []
        mst_edge_count: Dict[str, int] = {nid: 0 for nid in node_ids}
        total_cost = 0.0
        mst_edges_added = 0

        for edge in sorted_edges:
            u, v = edge.source, edge.target
            w = edge.weight or 0.0

            # Show: considering this edge
            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset(mst_nodes),
                frontier=(u, v),
                current=None,
                distances={k: float(cnt) for k, cnt in mst_edge_count.items()},
                path=tuple(mst_first),
                description=f"Consider edge {u}-{v} (weight {w:.0f}): same component? {uf.find(u) == uf.find(v)}",
            )

            if uf.union(u, v):
                mst_edges_added += 1
                total_cost += w
                for node in (u, v):
                    mst_edge_count[node] += 1
                    if node not in mst_nodes:
                        mst_nodes.add(node)
                        mst_first.append(node)

                yield GraphTraversalState(
                    nodes=nodes,
                    edges=edges,
                    visited=frozenset(mst_nodes),
                    frontier=(),
                    current=v,
                    distances={k: float(cnt) for k, cnt in mst_edge_count.items()},
                    path=tuple(mst_first),
                    description=f"Add {u}-{v} (w={w:.0f}) to MST. Total={total_cost:.0f}, edges={mst_edges_added}/{len(node_ids)-1}",
                )

                if mst_edges_added == len(node_ids) - 1:
                    break
            else:
                yield GraphTraversalState(
                    nodes=nodes,
                    edges=edges,
                    visited=frozenset(mst_nodes),
                    frontier=(),
                    current=None,
                    distances={k: float(cnt) for k, cnt in mst_edge_count.items()},
                    path=tuple(mst_first),
                    description=f"Skip {u}-{v}: would create a cycle",
                )

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(mst_nodes),
            frontier=(),
            current=None,
            distances={k: float(cnt) for k, cnt in mst_edge_count.items()},
            path=tuple(mst_first),
            description=f"MST complete: {mst_edges_added} edges, total weight={total_cost:.0f}",
        )
