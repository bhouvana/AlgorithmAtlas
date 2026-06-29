"""Ford-Fulkerson Max Flow plugin for Algorithm Atlas."""
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

# Hardcoded flow networks: list of (nodes, edges_with_capacity)
# edges: (src, dst, capacity)
_NETWORKS = [
    # Network 0: simple 4-node
    (["S", "A", "B", "T"],
     [("S","A",10), ("S","B",5), ("A","B",4), ("A","T",7), ("B","T",9)]),
    # Network 1: classic textbook 6-node
    (["S","A","B","C","D","T"],
     [("S","A",16),("S","C",13),("A","B",12),("C","A",4),("C","D",14),
      ("B","T",20),("D","B",7),("D","T",4),("B","C",9)]),
    # Network 2: linear
    (["S","A","B","T"],
     [("S","A",8),("A","B",6),("B","T",10),("S","B",3),("A","T",4)]),
    # Network 3: diamond
    (["S","A","B","T"],
     [("S","A",5),("S","B",3),("A","T",4),("B","T",6),("A","B",2)]),
    # Network 4: parallel paths
    (["S","A","B","C","T"],
     [("S","A",6),("S","B",4),("A","C",3),("B","C",5),("A","T",3),
      ("B","T",2),("C","T",8)]),
]


def _dfs_path(cap: dict, visited: set, source: str, sink: str, nodes: list):
    """DFS to find augmenting path. Returns path or None."""
    stack = [(source, [source])]
    while stack:
        node, path = stack.pop()
        if node == sink:
            return path
        for nxt in nodes:
            if nxt not in visited and cap.get((node, nxt), 0) > 0:
                visited.add(nxt)
                stack.append((nxt, path + [nxt]))
    return None


def _bottleneck(cap: dict, path: list) -> int:
    return min(cap.get((path[i], path[i+1]), 0) for i in range(len(path)-1))


def _layout(nodes: list) -> dict:
    """Linear left-to-right layout."""
    n = len(nodes)
    positions = {}
    for i, nd in enumerate(nodes):
        positions[nd] = (i / max(n - 1, 1) * 0.85 + 0.05, 0.4 + 0.15 * (i % 2))
    return positions


class FordFulkersonSimulation(AlgorithmPlugin):
    """Ford-Fulkerson Maximum Flow."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="ford-fulkerson",
            name="Ford-Fulkerson Max Flow",
            category="graph",
            visualization_type="GRAPH",
            description="Find the maximum flow from source to sink in a directed capacity graph.",
            intuition=(
                "Greedily find augmenting paths with DFS and push flow through them. "
                "Each iteration increases total flow by the path's bottleneck capacity."
            ),
            complexity_time_best="O(E·f)",
            complexity_time_average="O(E·f)",
            complexity_time_worst="O(E·f)",
            complexity_space="O(V+E)",
            tags=("graph", "max-flow", "ford-fulkerson", "network-flow"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        idx = params.seed % len(_NETWORKS)
        node_ids, edge_list = _NETWORKS[idx]
        pos = _layout(node_ids)

        # Compute true max flow for description
        cap = {}
        for s, d, c in edge_list:
            cap[(s, d)] = cap.get((s, d), 0) + c
            cap[(d, s)] = cap.get((d, s), 0)  # reverse edge

        cap_copy = dict(cap)
        source, sink = node_ids[0], node_ids[-1]
        total = 0
        while True:
            visited = {source}
            path = _dfs_path(cap_copy, visited, source, sink, node_ids)
            if not path:
                break
            flow = _bottleneck(cap_copy, path)
            for i in range(len(path) - 1):
                cap_copy[(path[i], path[i+1])] -= flow
                cap_copy[(path[i+1], path[i])] = cap_copy.get((path[i+1], path[i]), 0) + flow
            total += flow

        nodes = [
            NodeState(node_id=nd, label=nd, x=pos[nd][0], y=pos[nd][1])
            for nd in node_ids
        ]
        edges = [
            EdgeState(edge_id=f"{s}-{d}", source=s, target=d, weight=float(c), directed=True)
            for s, d, c in edge_list
        ]
        distances = {nd: 0.0 for nd in node_ids}
        return GraphTraversalState(
            nodes=tuple(nodes),
            edges=tuple(edges),
            visited=frozenset(),
            frontier=tuple(),
            current=None,
            distances=distances,
            path=tuple(),
            description=f"Max flow network idx={idx} source={source} sink={sink} expected={total}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        desc = initial_state.description
        idx = int(desc.split("idx=")[1].split(" ")[0])
        source = desc.split("source=")[1].split(" ")[0]
        sink = desc.split("sink=")[1].split(" ")[0]
        expected = int(desc.split("expected=")[1])

        node_ids, edge_list = _NETWORKS[idx]

        cap = {}
        for s, d, c in edge_list:
            cap[(s, d)] = cap.get((s, d), 0) + c
            cap[(d, s)] = cap.get((d, s), 0)

        total_flow = 0
        iteration = 0

        while True:
            visited_set = {source}
            path = _dfs_path(cap, visited_set, source, sink, node_ids)
            if not path:
                break

            flow = _bottleneck(cap, path)
            path_str = "→".join(path)

            yield GraphTraversalState(
                nodes=initial_state.nodes,
                edges=initial_state.edges,
                visited=frozenset(path),
                frontier=tuple(path),
                current=source,
                distances={nd: float(total_flow) for nd in node_ids},
                path=tuple(path),
                description=f"Iteration {iteration+1}: path={path_str} flow={flow}",
            )

            for i in range(len(path) - 1):
                cap[(path[i], path[i+1])] -= flow
                cap[(path[i+1], path[i])] = cap.get((path[i+1], path[i]), 0) + flow
            total_flow += flow
            iteration += 1

        return GraphTraversalState(
            nodes=initial_state.nodes,
            edges=initial_state.edges,
            visited=frozenset(node_ids),
            frontier=tuple(),
            current=sink,
            distances={nd: float(total_flow) for nd in node_ids},
            path=tuple(),
            description=f"Max flow = {total_flow}",
        )
