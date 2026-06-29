"""Graph Coloring plugin for Algorithm Atlas."""
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

_COLORS = ["red", "blue", "green", "yellow", "purple"]

# Hardcoded small graphs with known chromatic numbers
_GRAPHS = [
    # (nodes, edges, chromatic_number)
    (["A","B","C","D"], [("A","B"),("B","C"),("C","D"),("D","A"),("A","C")], 3),
    (["A","B","C"], [("A","B"),("B","C"),("A","C")], 3),  # triangle = K3
    (["A","B","C","D","E"], [("A","B"),("B","C"),("C","D"),("D","E"),("E","A"),("A","C")], 3),
    (["A","B","C","D"], [("A","B"),("C","D"),("A","C"),("B","D")], 2),  # bipartite
    (["A","B","C","D","E"], [("A","B"),("A","C"),("A","D"),("A","E"),("B","C"),("C","D")], 3),
]


def _make_layout(nodes: list) -> dict:
    import math
    n = len(nodes)
    return {
        nd: (0.5 + 0.4 * math.cos(2 * math.pi * i / n),
             0.5 + 0.4 * math.sin(2 * math.pi * i / n))
        for i, nd in enumerate(nodes)
    }


def _color_graph(nodes: list, adj: dict, k: int):
    """Backtracking graph coloring. Returns color assignment or None."""
    color = {nd: 0 for nd in nodes}
    frames = []

    def bt(idx: int) -> bool:
        if idx == len(nodes):
            return True
        nd = nodes[idx]
        for c in range(1, k + 1):
            # Check if any neighbor has color c
            ok = all(color[nb] != c for nb in adj[nd])
            frames.append((nd, c, ok, dict(color)))
            if ok:
                color[nd] = c
                if bt(idx + 1):
                    return True
                color[nd] = 0
        return False

    success = bt(0)
    return (color if success else None), frames


class GraphColoringSimulation(AlgorithmPlugin):
    """Graph Coloring via Backtracking."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="graph-coloring",
            name="Graph Coloring (Backtracking)",
            category="graph",
            visualization_type="GRAPH",
            description="Assign minimum colors to vertices so no two adjacent vertices share a color.",
            intuition=(
                "Try each color at each vertex. If assignment is consistent, recurse. "
                "Backtrack when no color works. The minimum k that succeeds is the chromatic number."
            ),
            complexity_time_best="O(k^V)",
            complexity_time_average="O(k^V)",
            complexity_time_worst="O(k^V)",
            complexity_space="O(V)",
            tags=("graph", "coloring", "backtracking", "chromatic-number"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        idx = params.seed % len(_GRAPHS)
        nodes_list, edges_list, chi = _GRAPHS[idx]
        pos = _make_layout(nodes_list)
        nodes = [NodeState(node_id=nd, label=nd, x=pos[nd][0], y=pos[nd][1]) for nd in nodes_list]
        edges = [
            EdgeState(edge_id=f"{u}-{v}", source=u, target=v, weight=1.0, directed=False)
            for u, v in edges_list
        ]
        distances = {nd: 0.0 for nd in nodes_list}
        return GraphTraversalState(
            nodes=tuple(nodes),
            edges=tuple(edges),
            visited=frozenset(),
            frontier=tuple(),
            current=None,
            distances=distances,
            path=tuple(),
            description=f"Color graph idx={idx} chromatic={chi}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        desc = initial_state.description
        idx = int(desc.split("idx=")[1].split(" ")[0])
        chi = int(desc.split("chromatic=")[1])
        nodes_list, edges_list, _ = _GRAPHS[idx]

        adj: dict[str, list[str]] = {nd: [] for nd in nodes_list}
        for u, v in edges_list:
            adj[u].append(v)
            adj[v].append(u)

        coloring, frames = _color_graph(nodes_list, adj, chi)

        current_colors: dict[str, float] = {nd: 0.0 for nd in nodes_list}
        for nd, c, ok, snapshot in frames[:50]:  # cap at 50 frames
            current_colors = {n: float(snapshot[n]) for n in nodes_list}
            yield GraphTraversalState(
                nodes=initial_state.nodes,
                edges=initial_state.edges,
                visited=frozenset(n for n in nodes_list if snapshot[n] > 0),
                frontier=tuple([nd]),
                current=nd,
                distances=dict(current_colors),
                path=tuple(),
                description=f"Try color {c} for {nd}: {'ok' if ok else 'conflict'}",
            )

        if coloring:
            final_colors = {nd: float(coloring[nd]) for nd in nodes_list}
        else:
            final_colors = {nd: 0.0 for nd in nodes_list}

        return GraphTraversalState(
            nodes=initial_state.nodes,
            edges=initial_state.edges,
            visited=frozenset(nodes_list),
            frontier=tuple(),
            current=None,
            distances=final_colors,
            path=tuple(),
            description=f"Colored with {chi} colors: {coloring}",
        )
