"""Hierholzer's Euler Circuit algorithm plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

# Fixed Eulerian graph: all vertices have even degree.
# Nodes 0-5, edges form an Eulerian circuit.
_NODES_POS = [
    (0.15, 0.50),  # 0
    (0.40, 0.15),  # 1
    (0.65, 0.15),  # 2
    (0.90, 0.50),  # 3
    (0.65, 0.85),  # 4
    (0.40, 0.85),  # 5
]

# Each edge listed once; undirected. All vertices have degree 4 → Eulerian.
_EDGE_LIST = [
    (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0),  # outer hexagon
    (0, 2), (2, 4), (4, 0),                             # inner triangle 0-2-4
    (1, 3), (3, 5), (5, 1),                             # inner triangle 1-3-5
]
_N = len(_NODES_POS)


def _make_state(circuit: list, used_edges: frozenset, current: str | None, desc: str):
    nodes = [
        NodeState(node_id=str(i), label=str(i), x=x, y=y)
        for i, (x, y) in enumerate(_NODES_POS)
    ]
    edges = []
    for u, v in _EDGE_LIST:
        eid = f"{min(u,v)}-{max(u,v)}"
        edges.append(EdgeState(
            edge_id=eid,
            source=str(u),
            target=str(v),
            weight=1.0 if eid in used_edges else 0.0,
            directed=False,
        ))
    visited = frozenset(str(n) for n in circuit)
    return GraphTraversalState(
        nodes=tuple(nodes),
        edges=tuple(edges),
        visited=visited,
        frontier=tuple(),
        current=current,
        distances={"circuit_len": float(len(circuit))},
        path=tuple(str(n) for n in circuit),
        description=desc,
    )


class HierholzerSimulation(AlgorithmPlugin):
    """Hierholzer's algorithm for finding Euler circuits."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="hierholzer",
            name="Hierholzer's Algorithm (Euler Circuit)",
            category="graph",
            visualization_type="GRAPH",
            description="Find an Euler circuit using Hierholzer's stack-based algorithm.",
            intuition=(
                "Push vertices onto a stack, following unused edges. "
                "When stuck, pop to circuit. "
                "Revisit any vertex with unused edges to splice in sub-circuits."
            ),
            complexity_time_best="O(V + E)",
            complexity_time_average="O(V + E)",
            complexity_time_worst="O(V + E)",
            complexity_space="O(E)",
            tags=("graph", "euler-circuit", "hierholzer", "traversal"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        return _make_state(
            circuit=[0],
            used_edges=frozenset(),
            current="0",
            desc=f"Hierholzer: Eulerian graph with {_N} nodes, {len(_EDGE_LIST)} edges.",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        # Build adjacency as sorted lists (deterministic order)
        adj: dict[int, list] = {i: [] for i in range(_N)}
        for u, v in _EDGE_LIST:
            adj[u].append(v)
            adj[v].append(u)
        for i in adj:
            adj[i].sort()

        # Hierholzer's algorithm
        stack = [0]
        circuit: list = []
        used_edges: set = set()

        while stack:
            v = stack[-1]
            # Find an unused edge from v
            next_v = None
            for u in adj[v]:
                eid = f"{min(v,u)}-{max(v,u)}"
                if eid not in used_edges:
                    next_v = u
                    break

            if next_v is not None:
                eid = f"{min(v,next_v)}-{max(v,next_v)}"
                used_edges.add(eid)
                stack.append(next_v)
                yield _make_state(
                    circuit=list(circuit) + list(stack),
                    used_edges=frozenset(used_edges),
                    current=str(next_v),
                    desc=f"Edge {v}→{next_v} used. Stack depth={len(stack)}",
                )
            else:
                circuit.append(stack.pop())
                yield _make_state(
                    circuit=list(circuit),
                    used_edges=frozenset(used_edges),
                    current=str(circuit[-1]) if circuit else None,
                    desc=f"Node {circuit[-1]} added to circuit. Circuit len={len(circuit)}",
                )

        circuit_str = " → ".join(str(n) for n in circuit)
        return _make_state(
            circuit=circuit,
            used_edges=frozenset(used_edges),
            current=None,
            desc=f"Euler circuit: {circuit_str}",
        )
