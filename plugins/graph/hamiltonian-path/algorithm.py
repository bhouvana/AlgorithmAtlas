"""Hamiltonian Path plugin for Algorithm Atlas."""
from __future__ import annotations

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

import math

# Hardcoded small graphs with known Hamiltonian paths
_GRAPHS = [
    # (nodes, edges, start_node)
    (["A","B","C","D","E"], [("A","B"),("B","C"),("C","D"),("D","E"),("A","C"),("B","D"),("C","E")], "A"),
    (["A","B","C","D"], [("A","B"),("B","C"),("C","D"),("D","A"),("A","C")], "A"),
    (["A","B","C","D","E"], [("A","B"),("B","E"),("E","D"),("D","C"),("C","A"),("A","D")], "A"),
    (["1","2","3","4","5"], [("1","2"),("2","3"),("3","4"),("4","5"),("5","1"),("1","3"),("2","4")], "1"),
    (["A","B","C","D","E","F"], [("A","B"),("B","C"),("C","D"),("D","E"),("E","F"),("F","A"),("A","C"),("B","D"),("C","E")], "A"),
]


def _find_hamiltonian(adj: dict, nodes: list, start: str):
    """Backtracking with frame recording. Returns (path, frames)."""
    path = [start]
    visited = {start}
    frames = []

    def bt():
        if len(path) == len(nodes):
            return True
        cur = path[-1]
        for nxt in sorted(adj[cur]):
            if nxt not in visited:
                frames.append(("visit", list(path), cur, nxt))
                visited.add(nxt)
                path.append(nxt)
                if bt():
                    return True
                frames.append(("backtrack", list(path), nxt, cur))
                path.pop()
                visited.remove(nxt)
        return False

    success = bt()
    return (list(path) if success else [start]), frames


def _layout(nodes: list) -> dict:
    n = len(nodes)
    return {
        nd: (0.5 + 0.4 * math.cos(2 * math.pi * i / n),
             0.5 + 0.4 * math.sin(2 * math.pi * i / n))
        for i, nd in enumerate(nodes)
    }


class HamiltonianPathSimulation(AlgorithmPlugin):
    """Hamiltonian Path via Backtracking."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="hamiltonian-path",
            name="Hamiltonian Path (Backtracking)",
            category="graph",
            visualization_type="GRAPH",
            description="Find a path visiting every vertex exactly once using backtracking DFS.",
            intuition=(
                "Extend the current path with any unvisited neighbor. "
                "When all vertices are visited, we have a Hamiltonian path. "
                "Backtrack when no extension is possible."
            ),
            complexity_time_best="O(V!)",
            complexity_time_average="O(V!)",
            complexity_time_worst="O(V!)",
            complexity_space="O(V)",
            tags=("graph", "hamiltonian-path", "backtracking", "np-complete"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        idx = params.seed % len(_GRAPHS)
        nodes_list, edges_list, start = _GRAPHS[idx]
        pos = _layout(nodes_list)
        nodes = [NodeState(node_id=nd, label=nd, x=pos[nd][0], y=pos[nd][1]) for nd in nodes_list]
        edges = [
            EdgeState(edge_id=f"{u}-{v}", source=u, target=v, weight=1.0, directed=False)
            for u, v in edges_list
        ]
        return GraphTraversalState(
            nodes=tuple(nodes),
            edges=tuple(edges),
            visited=frozenset(),
            frontier=tuple([start]),
            current=None,
            distances={nd: 0.0 for nd in nodes_list},
            path=tuple(),
            description=f"Hamiltonian path idx={idx} start={start} n={len(nodes_list)}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        desc = initial_state.description
        idx = int(desc.split("idx=")[1].split(" ")[0])
        start = desc.split("start=")[1].split(" ")[0]
        nodes_list, edges_list, _ = _GRAPHS[idx]

        adj: dict[str, list[str]] = {nd: [] for nd in nodes_list}
        for u, v in edges_list:
            adj[u].append(v)
            adj[v].append(u)

        ham_path, frames = _find_hamiltonian(adj, nodes_list, start)

        for action, path, frm, to in frames[:60]:
            yield GraphTraversalState(
                nodes=initial_state.nodes,
                edges=initial_state.edges,
                visited=frozenset(path),
                frontier=tuple([to]),
                current=frm,
                distances={nd: float(i) for i, nd in enumerate(path)},
                path=tuple(path),
                description=f"{'Try' if action=='visit' else 'Backtrack'}: {frm}→{to} path_len={len(path)}",
            )

        return GraphTraversalState(
            nodes=initial_state.nodes,
            edges=initial_state.edges,
            visited=frozenset(ham_path),
            frontier=tuple(),
            current=ham_path[-1] if ham_path else None,
            distances={nd: float(i) for i, nd in enumerate(ham_path)},
            path=tuple(ham_path),
            description=f"Hamiltonian path: {ham_path} length={len(ham_path)}",
        )
