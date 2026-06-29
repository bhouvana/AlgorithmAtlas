"""Kosaraju's Strongly Connected Components plugin for Algorithm Atlas."""
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

# Fixed directed graph: 7 nodes, has SCCs {0,1,2}, {3,4}, {5}, {6}
_NODES = [
    ("A", 0.15, 0.5),
    ("B", 0.35, 0.2),
    ("C", 0.35, 0.8),
    ("D", 0.55, 0.35),
    ("E", 0.55, 0.65),
    ("F", 0.75, 0.2),
    ("G", 0.75, 0.8),
]
# Edges (directed)
_EDGES = [
    (0, 1), (1, 2), (2, 0),   # SCC: 0→1→2→0
    (1, 3), (2, 4),            # bridges to other SCCs
    (3, 4), (4, 3),            # SCC: 3↔4
    (3, 5),                    # bridge
    (4, 6),                    # bridge
]  # SCC {5} and {6} are singletons


def _build_graph():
    adj = {i: [] for i in range(len(_NODES))}
    radj = {i: [] for i in range(len(_NODES))}
    for u, v in _EDGES:
        adj[u].append(v)
        radj[v].append(u)
    return adj, radj


def _dfs1(node, adj, visited, stack):
    visited.add(node)
    for nb in adj[node]:
        if nb not in visited:
            _dfs1(nb, adj, visited, stack)
    stack.append(node)


def _dfs2(node, radj, visited, component):
    visited.add(node)
    component.append(node)
    for nb in radj[node]:
        if nb not in visited:
            _dfs2(nb, radj, visited, component)


def _build_state(nodes_tuple, edges_tuple, visited, frontier, current, comp_map, phase, step_desc):
    colored_nodes = []
    for i, (label, x, y) in enumerate(_NODES):
        c = comp_map.get(i, -1)
        # Encode component in weight field (used by renderer for coloring)
        colored_nodes.append(NodeState(
            node_id=str(i),
            label=label,
            x=x,
            y=y,
            weight=float(c) if c >= 0 else (-1.0 if i not in visited else -2.0),
        ))
    return GraphTraversalState(
        nodes=tuple(colored_nodes),
        edges=edges_tuple,
        visited=frozenset(str(v) for v in visited),
        frontier=tuple(str(f) for f in frontier),
        current=str(current) if current is not None else None,
        distances={},
        path=(),
        description=f"[{phase}] {step_desc}",
    )


class KosarajuSCCSimulation(AlgorithmPlugin):
    """Kosaraju SCC visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="kosaraju-scc",
            name="Kosaraju's SCC",
            category="graph",
            visualization_type="GRAPH",
            description="Find strongly connected components using two-pass DFS.",
            intuition=(
                "Pass 1: DFS on original graph, push to stack on finish. "
                "Pass 2: DFS on reversed graph in stack order — each tree is one SCC."
            ),
            complexity_time_best="O(V+E)",
            complexity_time_average="O(V+E)",
            complexity_time_worst="O(V+E)",
            complexity_space="O(V+E)",
            tags=("graph", "scc", "dfs", "directed", "kosaraju"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        nodes = tuple(
            NodeState(node_id=str(i), label=lbl, x=x, y=y)
            for i, (lbl, x, y) in enumerate(_NODES)
        )
        edges = tuple(
            EdgeState(
                edge_id=f"e{u}_{v}",
                source=str(u),
                target=str(v),
                weight=1.0,
                directed=True,
            )
            for u, v in _EDGES
        )
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description="Kosaraju SCC: ready to start",
        )

    def steps(self, initial_state: GraphTraversalState) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        n = len(_NODES)
        adj, radj = _build_graph()
        edges = initial_state.edges

        # Pass 1: fill finish-order stack
        stack = []
        visited1 = set()
        for start in range(n):
            if start not in visited1:
                _dfs1(start, adj, visited1, stack)
                yield _build_state(
                    initial_state.nodes, edges, visited1,
                    [stack[-1]] if stack else [],
                    start, {}, "Pass 1 DFS",
                    f"Pass 1: finished node {_NODES[start][0]}, stack top={_NODES[stack[-1]][0]}",
                )

        yield _build_state(
            initial_state.nodes, edges, visited1, [],
            None, {}, "Pass 1 complete",
            f"Pass 1 done. Stack order: {[_NODES[s][0] for s in stack]}",
        )

        # Pass 2: DFS on reversed graph
        visited2 = set()
        comp_map = {}  # node → component_id
        comp_id = 0

        while stack:
            node = stack.pop()
            if node not in visited2:
                component = []
                _dfs2(node, radj, visited2, component)
                for c in component:
                    comp_map[c] = comp_id
                yield _build_state(
                    initial_state.nodes, edges, visited2,
                    component, node, comp_map, "Pass 2 DFS",
                    f"SCC {comp_id}: {{{', '.join(_NODES[c][0] for c in component)}}}",
                )
                comp_id += 1

        return _build_state(
            initial_state.nodes, edges, visited2, [], None,
            comp_map, "Done",
            f"Found {comp_id} SCCs: " + " | ".join(
                f"{{{', '.join(_NODES[c][0] for c in sorted(k for k in comp_map if comp_map[k] == cid))}}}"
                for cid in range(comp_id)
            ),
        )
