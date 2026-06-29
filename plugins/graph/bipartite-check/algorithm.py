"""Bipartite Check plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from collections import deque
from typing import Dict, Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

_COLOR_A = 1.0  # Group A label
_COLOR_B = 2.0  # Group B label


def _build_adj(
    nodes: Tuple[NodeState, ...], edges: Tuple[EdgeState, ...]
) -> Dict[str, List[str]]:
    adj: Dict[str, List[str]] = {n.node_id: [] for n in nodes}
    for e in edges:
        adj[e.source].append(e.target)
        adj[e.target].append(e.source)
    return adj


def _make_graph(
    rng: random.Random, n: int, bipartite: bool
) -> Tuple[Tuple[NodeState, ...], Tuple[EdgeState, ...]]:
    """Build either a bipartite or non-bipartite graph."""
    labels = [chr(ord("A") + i) for i in range(n)]

    edge_set: set = set()
    edge_list: List[Tuple[str, str]] = []

    if bipartite:
        # Build a random bipartite graph: split into two halves
        half = n // 2
        left = labels[:half]
        right = labels[half:]
        # Connect each left node to 1-2 right nodes
        for u in left:
            for v in rng.sample(right, min(2, len(right))):
                key = (min(u, v), max(u, v))
                if key not in edge_set:
                    edge_set.add(key)
                    edge_list.append((u, v))
        # Add a spanning connection so graph is connected
        shuffled_right = right[:]
        rng.shuffle(shuffled_right)
        for i in range(1, len(shuffled_right)):
            u = rng.choice(left)
            v = shuffled_right[i]
            key = (min(u, v), max(u, v))
            if key not in edge_set:
                edge_set.add(key)
                edge_list.append((u, v))
    else:
        # Build a random spanning tree, then add an odd cycle
        shuffled = labels[:]
        rng.shuffle(shuffled)
        for i in range(1, n):
            j = rng.randint(0, i - 1)
            u, v = shuffled[i], shuffled[j]
            key = (min(u, v), max(u, v))
            edge_set.add(key)
            edge_list.append((u, v))
        # Add one extra edge to create an odd cycle (e.g., triangle)
        for _ in range(50):
            u = rng.choice(labels)
            v = rng.choice(labels)
            if u != v:
                key = (min(u, v), max(u, v))
                if key not in edge_set:
                    edge_set.add(key)
                    edge_list.append((u, v))
                    break

    nodes_list = []
    for i, label in enumerate(labels):
        angle = 2 * math.pi * i / n - math.pi / 2
        x = round(0.5 + 0.42 * math.cos(angle), 4)
        y = round(0.5 + 0.42 * math.sin(angle), 4)
        nodes_list.append(NodeState(node_id=label, label=label, x=x, y=y))

    edges_list = [
        EdgeState(edge_id=f"e{idx}", source=u, target=v, directed=False)
        for idx, (u, v) in enumerate(edge_list)
    ]

    return tuple(nodes_list), tuple(edges_list)


class BipartiteCheckSimulation(AlgorithmPlugin):
    """
    Bipartite Check — BFS 2-coloring, O(V + E).

    Uses BFS. Assign color 1 to source, color 2 to neighbors, alternate.
    If a neighbor already has the same color as current node → not bipartite.

    State encoding:
      distances: color[node] — 1.0 (Group A) or 2.0 (Group B), 0 = uncolored
      visited:   colored nodes
      frontier:  current BFS queue
      current:   node currently being colored
      path:      ("BIPARTITE",) or ("NOT_BIPARTITE",) when result is known
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bipartite-check",
            name="Bipartite Check",
            category="graph",
            visualization_type="GRAPH",
            description=(
                "Determine if an undirected graph is 2-colorable (bipartite) "
                "using BFS alternating coloring."
            ),
            intuition=(
                "Assign alternating colors to nodes via BFS. "
                "If any edge connects two same-color nodes, the graph is not bipartite "
                "(it contains an odd-length cycle)."
            ),
            complexity_time_best="O(V + E)",
            complexity_time_average="O(V + E)",
            complexity_time_worst="O(V + E)",
            complexity_space="O(V)",
            tags=("graph", "bipartite", "bfs", "coloring"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("node_count", 6), 10))
        # Alternate between bipartite and non-bipartite based on seed parity
        bipartite = (params.seed % 2 == 0)

        nodes, edges = _make_graph(rng, n, bipartite)
        labels = sorted(nd.node_id for nd in nodes)

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=f"Bipartite check: {n} nodes, {len(edges)} edges. BFS 2-coloring.",
        )

    def steps(
        self,
        initial_state: GraphTraversalState,
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges
        adj = _build_adj(nodes, edges)

        color: Dict[str, int] = {}  # 1 = Group A, 2 = Group B
        all_nodes = sorted(nd.node_id for nd in nodes)

        is_bipartite = True

        for start in all_nodes:
            if start in color:
                continue

            color[start] = 1
            queue: deque = deque([start])

            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset(color.keys()),
                frontier=tuple(queue),
                current=start,
                distances={k: float(v) for k, v in color.items()},
                path=(),
                description=f"Color {start}=A (Group 1), enqueue",
            )

            while queue and is_bipartite:
                u = queue.popleft()
                c_u = color[u]
                c_neighbor = 3 - c_u  # flip: 1→2, 2→1

                for v in sorted(adj[u]):
                    if v not in color:
                        color[v] = c_neighbor
                        queue.append(v)
                        group = "A" if c_neighbor == 1 else "B"
                        yield GraphTraversalState(
                            nodes=nodes,
                            edges=edges,
                            visited=frozenset(color.keys()),
                            frontier=tuple(queue),
                            current=v,
                            distances={k: float(v_) for k, v_ in color.items()},
                            path=(),
                            description=f"Color {v}=Group {group} (neighbor of {u})",
                        )
                    elif color[v] == c_u:
                        is_bipartite = False
                        yield GraphTraversalState(
                            nodes=nodes,
                            edges=edges,
                            visited=frozenset(color.keys()),
                            frontier=(),
                            current=u,
                            distances={k: float(v_) for k, v_ in color.items()},
                            path=("NOT_BIPARTITE",),
                            description=(
                                f"Conflict: {u} and {v} same color! "
                                f"Edge ({u},{v}) violates 2-coloring → NOT bipartite"
                            ),
                        )
                        break

        result = "BIPARTITE" if is_bipartite else "NOT_BIPARTITE"
        group_a = sorted(k for k, v in color.items() if v == 1)
        group_b = sorted(k for k, v in color.items() if v == 2)
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(color.keys()),
            frontier=(),
            current=None,
            distances={k: float(v) for k, v in color.items()},
            path=(result,),
            description=(
                f"Done: graph is {result}. "
                + (f"A={{{','.join(group_a)}}}, B={{{','.join(group_b)}}}" if is_bipartite else "Odd cycle detected.")
            ),
        )
