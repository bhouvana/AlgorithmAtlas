"""Eulerian Path (Hierholzer's Algorithm) plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Dict, Generator, List, Optional, Set, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

_NODE_LABELS = "ABCDEFGHIJ"


def _make_euler_graph(rng: random.Random, n: int) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Generate a connected undirected graph with exactly 0 or 2 odd-degree vertices
    (Eulerian circuit or path).
    """
    nodes = list(_NODE_LABELS[:n])
    # Start with a random spanning path (guarantees all-even except endpoints)
    order = list(nodes)
    rng.shuffle(order)
    adj: Dict[str, List[str]] = defaultdict(list)
    edges_added: Set[Tuple[str, str]] = set()

    def add_edge(u: str, v: str):
        key = (min(u, v), max(u, v))
        if key not in edges_added:
            edges_added.add(key)
            adj[u].append(v)
            adj[v].append(u)

    # Add a Hamiltonian path through all nodes — 2 odd-degree endpoints
    for i in range(n - 1):
        add_edge(order[i], order[i + 1])

    # Add some extra edges (even count) between random pairs to make graph denser
    node_list = list(nodes)
    for _ in range(n // 2):
        u, v = rng.sample(node_list, 2)
        add_edge(u, v)

    # Fix degree parity: if more than 2 odd-degree nodes, add edges to pair them up
    while True:
        odd = [v for v in nodes if len(adj[v]) % 2 == 1]
        if len(odd) <= 2:
            break
        u, v = odd[0], odd[1]
        add_edge(u, v)

    return nodes, dict(adj)


def _make_node_states(nodes: List[str], n: int) -> Tuple[NodeState, ...]:
    node_states = []
    for i, nid in enumerate(nodes):
        angle = 2 * math.pi * i / n
        x = round(4.0 + 3.5 * math.cos(angle), 3)
        y = round(4.0 + 3.5 * math.sin(angle), 3)
        node_states.append(NodeState(node_id=nid, label=nid, x=x, y=y))
    return tuple(node_states)


def _make_edge_states(adj: Dict[str, List[str]]) -> Tuple[EdgeState, ...]:
    seen: Set[Tuple[str, str]] = set()
    edges = []
    for u, neighbors in sorted(adj.items()):
        for v in sorted(neighbors):
            key = (min(u, v), max(u, v))
            if key not in seen:
                seen.add(key)
                edges.append(EdgeState(
                    edge_id=f"{min(u,v)}-{max(u,v)}",
                    source=min(u, v),
                    target=max(u, v),
                    weight=None,
                    directed=False,
                ))
    return tuple(edges)


class EulerPathSimulation(AlgorithmPlugin):
    """
    Eulerian Path via Hierholzer's algorithm — O(E).

    GraphTraversalState:
      visited: edges traversed so far (encoded as "A-B" strings in distances dict)
      path: Eulerian path nodes in order
      current: current node
      distances: {"edge_count": float, "total_edges": float}
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="euler-path",
            name="Eulerian Path (Hierholzer)",
            category="graph",
            visualization_type="GRAPH",
            description=(
                "Find an Eulerian path — a trail visiting every edge exactly once — "
                "using Hierholzer's O(E) algorithm."
            ),
            intuition=(
                "Start from the vertex with odd degree (or any if all even). "
                "Follow unvisited edges greedily, building a circuit. "
                "When stuck, splice in sub-circuits until all edges are used."
            ),
            complexity_time_best="O(E)",
            complexity_time_average="O(E)",
            complexity_time_worst="O(E)",
            complexity_space="O(E)",
            tags=("graph", "euler-path", "hierholzer", "edges"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("array_size", 5), 8))
        nodes, adj = _make_euler_graph(rng, n)
        node_states = _make_node_states(nodes, n)
        edge_states = _make_edge_states(adj)

        # Find start: prefer odd-degree node
        odd_nodes = [v for v in nodes if len(adj[v]) % 2 == 1]
        start = odd_nodes[0] if odd_nodes else nodes[0]
        total_edges = len(edge_states)

        return GraphTraversalState(
            nodes=node_states,
            edges=edge_states,
            visited=frozenset(),
            frontier=(start,),
            current=start,
            distances={"edge_count": 0.0, "total_edges": float(total_edges)},
            path=(),
            description=f"Start at {start}: {total_edges} edges to traverse",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = [n.node_id for n in initial_state.nodes]
        adj: Dict[str, List[str]] = defaultdict(list)
        for e in initial_state.edges:
            adj[e.source].append(e.target)
            adj[e.target].append(e.source)

        total_edges = int(initial_state.distances["total_edges"])
        start = initial_state.frontier[0]

        # Hierholzer's algorithm — iterative version
        adj_copy: Dict[str, List[str]] = {k: sorted(v) for k, v in adj.items()}
        stack = [start]
        euler_path: List[str] = []
        used_edges: set = set()

        while stack:
            v = stack[-1]
            if adj_copy[v]:
                u = adj_copy[v].pop(0)
                # Remove the reverse edge too
                adj_copy[u].remove(v)
                edge_key = (min(u, v), max(u, v), len(used_edges))
                used_edges.add((min(u, v), max(u, v)))
                stack.append(u)
                yield GraphTraversalState(
                    nodes=initial_state.nodes,
                    edges=initial_state.edges,
                    visited=frozenset(str(k) for k in used_edges),
                    frontier=tuple(stack),
                    current=u,
                    distances={
                        "edge_count": float(len(used_edges)),
                        "total_edges": float(total_edges),
                    },
                    path=tuple(euler_path),
                    description=f"Traverse edge {v}→{u} ({len(used_edges)}/{total_edges})",
                )
            else:
                euler_path.append(stack.pop())

        all_used = len(used_edges) == total_edges
        path_type = "Eulerian Circuit" if euler_path[0] == euler_path[-1] else "Eulerian Path"
        return GraphTraversalState(
            nodes=initial_state.nodes,
            edges=initial_state.edges,
            visited=frozenset(str(k) for k in used_edges),
            frontier=(),
            current=None,
            distances={
                "edge_count": float(len(used_edges)),
                "total_edges": float(total_edges),
            },
            path=tuple(euler_path),
            description=(
                f"{path_type}: {' → '.join(euler_path)}"
                if all_used
                else f"Incomplete: only {len(used_edges)}/{total_edges} edges"
            ),
        )
