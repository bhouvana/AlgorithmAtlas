"""Cycle Detection (Directed Graph) plugin for Algorithm Atlas."""
from __future__ import annotations

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

_WHITE = 0.0   # unvisited
_GRAY  = 1.0   # on current DFS stack
_BLACK = 2.0   # fully processed


def _build_adj(
    nodes: Tuple[NodeState, ...], edges: Tuple[EdgeState, ...]
) -> Dict[str, List[str]]:
    adj: Dict[str, List[str]] = {n.node_id: [] for n in nodes}
    for e in edges:
        adj[e.source].append(e.target)
    return adj


def _make_directed_graph(
    rng: random.Random, n: int, has_cycle: bool
) -> Tuple[Tuple[NodeState, ...], Tuple[EdgeState, ...]]:
    labels = [chr(ord("A") + i) for i in range(n)]
    edge_set: set = set()
    edge_list: List[Tuple[str, str]] = []

    # Build a random DAG (topological order)
    order = labels[:]
    rng.shuffle(order)
    for i in range(1, n):
        j = rng.randint(0, i - 1)
        u, v = order[j], order[i]  # only forward edges → DAG
        key = (u, v)
        if key not in edge_set:
            edge_set.add(key)
            edge_list.append((u, v))

    # Add a few extra DAG edges
    for _ in range(n // 2):
        idx_u = rng.randint(0, n - 2)
        idx_v = rng.randint(idx_u + 1, n - 1)
        u, v = order[idx_u], order[idx_v]
        key = (u, v)
        if key not in edge_set:
            edge_set.add(key)
            edge_list.append((u, v))

    if has_cycle:
        # Add a guaranteed back edge: last → first in topological order.
        # The spanning tree has a path from order[0] to order[n-1], so
        # adding order[n-1] → order[0] definitely creates a cycle.
        u, v = order[n - 1], order[0]
        key = (u, v)
        if key not in edge_set:
            edge_set.add(key)
            edge_list.append((u, v))
        else:
            # Fallback: try order[n-1] → order[1]
            u, v = order[n - 1], order[1] if n > 2 else order[0]
            key = (u, v)
            if key not in edge_set:
                edge_set.add(key)
                edge_list.append((u, v))

    nodes_list = []
    for i, label in enumerate(labels):
        angle = 2 * math.pi * i / n - math.pi / 2
        x = round(0.5 + 0.42 * math.cos(angle), 4)
        y = round(0.5 + 0.42 * math.sin(angle), 4)
        nodes_list.append(NodeState(node_id=label, label=label, x=x, y=y))

    edges_list = [
        EdgeState(edge_id=f"e{idx}", source=u, target=v, directed=True)
        for idx, (u, v) in enumerate(edge_list)
    ]

    return tuple(nodes_list), tuple(edges_list)


class CycleDetectionSimulation(AlgorithmPlugin):
    """
    Cycle Detection (Directed Graph) — DFS 3-color, O(V + E).

    distances[node]: 0=WHITE (unvisited), 1=GRAY (in stack), 2=BLACK (done)
    visited:  BLACK nodes (fully processed)
    frontier: GRAY nodes (current DFS stack path)
    path:     ("CYCLE",) or ("NO_CYCLE",) once determined
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="cycle-detection",
            name="Cycle Detection (Directed)",
            category="graph",
            visualization_type="GRAPH",
            description=(
                "Detect whether a directed graph contains a cycle "
                "using DFS with WHITE/GRAY/BLACK node coloring."
            ),
            intuition=(
                "DFS marks nodes GRAY when first visited. "
                "If we reach a GRAY node via a directed edge, "
                "we've found a back edge and thus a cycle. "
                "Mark BLACK when all descendants are processed."
            ),
            complexity_time_best="O(V + E)",
            complexity_time_average="O(V + E)",
            complexity_time_worst="O(V + E)",
            complexity_space="O(V)",
            tags=("graph", "cycle-detection", "dfs", "directed"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("node_count", 6), 9))
        has_cycle = (params.seed % 2 == 1)

        nodes, edges = _make_directed_graph(rng, n, has_cycle)

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={nd.node_id: _WHITE for nd in nodes},
            path=(),
            description=(
                f"Cycle detection: {n} nodes, {len(edges)} directed edges. "
                "WHITE=unvisited, GRAY=in stack, BLACK=done."
            ),
        )

    def steps(
        self,
        initial_state: GraphTraversalState,
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges
        adj = _build_adj(nodes, edges)

        color: Dict[str, float] = {nd.node_id: _WHITE for nd in nodes}
        all_nodes = sorted(nd.node_id for nd in nodes)
        cycle_found = False

        def black_nodes():
            return frozenset(k for k, v in color.items() if v == _BLACK)

        def gray_nodes():
            return tuple(k for k in all_nodes if color[k] == _GRAY)

        for start in all_nodes:
            if color[start] != _WHITE or cycle_found:
                continue

            color[start] = _GRAY
            # Frame: [u, nbr_iter]
            stack_frames: List[List] = [[start, iter(sorted(adj[start]))]]

            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=black_nodes(),
                frontier=gray_nodes(),
                current=start,
                distances=dict(color),
                path=(),
                description=f"Mark {start}=GRAY, push to DFS stack",
            )

            while stack_frames and not cycle_found:
                u = stack_frames[-1][0]
                nbr_iter = stack_frames[-1][1]

                try:
                    v = next(nbr_iter)
                except StopIteration:
                    stack_frames.pop()
                    color[u] = _BLACK

                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=black_nodes(),
                        frontier=gray_nodes(),
                        current=u,
                        distances=dict(color),
                        path=(),
                        description=f"Mark {u}=BLACK (all descendants processed)",
                    )
                    continue

                if color[v] == _GRAY:
                    cycle_found = True
                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=black_nodes(),
                        frontier=gray_nodes(),
                        current=u,
                        distances=dict(color),
                        path=("CYCLE",),
                        description=(
                            f"Back edge {u}→{v} ({v} is GRAY) → CYCLE DETECTED!"
                        ),
                    )
                elif color[v] == _WHITE:
                    color[v] = _GRAY
                    stack_frames.append([v, iter(sorted(adj[v]))])

                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=black_nodes(),
                        frontier=gray_nodes(),
                        current=v,
                        distances=dict(color),
                        path=(),
                        description=f"Tree edge {u}→{v}: mark {v}=GRAY",
                    )
                # BLACK node → cross/forward edge → no cycle concern

        result = "CYCLE" if cycle_found else "NO_CYCLE"
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=black_nodes(),
            frontier=(),
            current=None,
            distances=dict(color),
            path=(result,),
            description=(
                f"Done: graph has {'a cycle' if cycle_found else 'NO cycle'}"
            ),
        )
