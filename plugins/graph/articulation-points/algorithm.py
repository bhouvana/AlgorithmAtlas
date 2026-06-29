"""Articulation Points (Cut Vertices) plugin for Algorithm Atlas."""
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


def _build_adj(
    nodes: Tuple[NodeState, ...], edges: Tuple[EdgeState, ...]
) -> Dict[str, List[str]]:
    adj: Dict[str, List[str]] = {n.node_id: [] for n in nodes}
    for e in edges:
        adj[e.source].append(e.target)
        adj[e.target].append(e.source)
    return adj


def _make_graph(
    rng: random.Random, n: int, extra: int
) -> Tuple[Tuple[NodeState, ...], Tuple[EdgeState, ...]]:
    """Generate a random connected undirected graph with n nodes."""
    labels = [chr(ord("A") + i) for i in range(n)]

    edge_set: set = set()
    edge_list: List[Tuple[str, str]] = []

    shuffled = labels[:]
    rng.shuffle(shuffled)
    for i in range(1, n):
        j = rng.randint(0, i - 1)
        u, v = shuffled[i], shuffled[j]
        key = (min(u, v), max(u, v))
        edge_set.add(key)
        edge_list.append((u, v))

    attempts = 0
    added = 0
    while added < extra and attempts < 200:
        attempts += 1
        u = rng.choice(labels)
        v = rng.choice(labels)
        if u != v:
            key = (min(u, v), max(u, v))
            if key not in edge_set:
                edge_set.add(key)
                edge_list.append((u, v))
                added += 1

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


class ArticulationPointsSimulation(AlgorithmPlugin):
    """
    Articulation Points — Tarjan's DFS-based algorithm, O(V + E).

    Uses DFS discovery time and low values. A vertex u is an articulation point if:
      1. u is the DFS root and has ≥ 2 children in the DFS tree, OR
      2. u is not the root and has a child v where low[v] ≥ disc[u]
         (no back edge from v's subtree reaches above u).

    State encoding:
      distances: disc[] — discovery timestamps (float for type compatibility)
      path:      sorted list of confirmed articulation points found so far
      visited:   set of all discovered nodes
      frontier:  current DFS call stack (top of stack is innermost frame)
      current:   node whose DFS frame is active
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="articulation-points",
            name="Articulation Points",
            category="graph",
            visualization_type="GRAPH",
            description=(
                "Find all cut vertices whose removal disconnects the graph "
                "using Tarjan's DFS algorithm."
            ),
            intuition=(
                "Run DFS and track two values per node: disc (when it was found) "
                "and low (the earliest disc reachable via back edges in its subtree). "
                "A node is a cut vertex if no back edge lets its subtree bypass it."
            ),
            complexity_time_best="O(V + E)",
            complexity_time_average="O(V + E)",
            complexity_time_worst="O(V + E)",
            complexity_space="O(V)",
            tags=("graph", "articulation-points", "cut-vertices", "dfs", "tarjan"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("node_count", 7), 10))
        # Few extra edges → more likely to have articulation points
        extra: int = params.inputs.get("extra_edges", max(1, n // 4))

        nodes, edges = _make_graph(rng, n, extra)

        labels = sorted(nd.node_id for nd in nodes)
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=(
                f"Find articulation points: {n} nodes, {len(edges)} edges. "
                "Starting DFS from A."
            ),
        )

    def steps(
        self,
        initial_state: GraphTraversalState,
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        nodes = initial_state.nodes
        edges = initial_state.edges
        adj = _build_adj(nodes, edges)

        disc: Dict[str, int] = {}
        low: Dict[str, int] = {}
        timer = [0]
        ap_confirmed: Set[str] = set()

        all_nodes = sorted(nd.node_id for nd in nodes)

        for start in all_nodes:
            if start in disc:
                continue

            disc[start] = low[start] = timer[0]
            timer[0] += 1

            # Frame: [u, parent_u, nbr_iter, children_count]
            # Use list so children_count (index 3) is mutable
            stack_frames: List[List] = [
                [start, None, iter(sorted(adj[start])), [0]]
            ]

            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset(disc.keys()),
                frontier=tuple(f[0] for f in stack_frames),
                current=start,
                distances={k: float(v) for k, v in disc.items()},
                path=tuple(sorted(ap_confirmed)),
                description=f"Discover {start}: disc[{start}]={disc[start]}, low[{start}]={low[start]}",
            )

            while stack_frames:
                u = stack_frames[-1][0]
                par_u = stack_frames[-1][1]
                nbr_iter = stack_frames[-1][2]
                children = stack_frames[-1][3]

                try:
                    v = next(nbr_iter)
                except StopIteration:
                    # Finished processing u — pop and propagate low value
                    stack_frames.pop()

                    if stack_frames:
                        p_node = stack_frames[-1][0]
                        p_parent = stack_frames[-1][1]

                        old_low_p = low[p_node]
                        low[p_node] = min(low[p_node], low[u])
                        newly_ap = False

                        # Non-root AP condition: low[u] >= disc[p_node]
                        if p_parent is not None and low[u] >= disc[p_node]:
                            if p_node not in ap_confirmed:
                                ap_confirmed.add(p_node)
                                newly_ap = True

                        msg = (
                            f"Return {u}→{p_node}: low[{p_node}]="
                            f"min({old_low_p},{low[u]})={low[p_node]}"
                        )
                        if newly_ap:
                            msg += (
                                f" → {p_node} is AP "
                                f"(low[{u}]={low[u]} ≥ disc[{p_node}]={disc[p_node]})"
                            )

                        yield GraphTraversalState(
                            nodes=nodes,
                            edges=edges,
                            visited=frozenset(disc.keys()),
                            frontier=tuple(f[0] for f in stack_frames),
                            current=p_node,
                            distances={k: float(v) for k, v in disc.items()},
                            path=tuple(sorted(ap_confirmed)),
                            description=msg,
                        )
                    else:
                        # u was the root of this DFS tree
                        if children[0] > 1 and u not in ap_confirmed:
                            ap_confirmed.add(u)

                        yield GraphTraversalState(
                            nodes=nodes,
                            edges=edges,
                            visited=frozenset(disc.keys()),
                            frontier=(),
                            current=None,
                            distances={k: float(v) for k, v in disc.items()},
                            path=tuple(sorted(ap_confirmed)),
                            description=(
                                f"Root {u}: {children[0]} DFS child(ren)"
                                + (f" → {u} is AP" if u in ap_confirmed else "")
                            ),
                        )
                    continue

                # Skip the edge back to the tree-parent (undirected graph)
                if v == par_u:
                    continue

                if v not in disc:
                    # Tree edge: discover v
                    children[0] += 1
                    disc[v] = low[v] = timer[0]
                    timer[0] += 1
                    stack_frames.append([v, u, iter(sorted(adj[v])), [0]])

                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(disc.keys()),
                        frontier=tuple(f[0] for f in stack_frames),
                        current=v,
                        distances={k: float(v_) for k, v_ in disc.items()},
                        path=tuple(sorted(ap_confirmed)),
                        description=(
                            f"Tree edge {u}→{v}: "
                            f"disc[{v}]={disc[v]}, low[{v}]={low[v]}"
                        ),
                    )
                else:
                    # Back edge: update low[u]
                    old_low = low[u]
                    low[u] = min(low[u], disc[v])
                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(disc.keys()),
                        frontier=tuple(f[0] for f in stack_frames),
                        current=u,
                        distances={k: float(v_) for k, v_ in disc.items()},
                        path=tuple(sorted(ap_confirmed)),
                        description=(
                            f"Back edge {u}→{v}: "
                            f"low[{u}]=min({old_low},{disc[v]})={low[u]}"
                        ),
                    )

        ap_list = sorted(ap_confirmed)
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(disc.keys()),
            frontier=(),
            current=None,
            distances={k: float(v) for k, v in disc.items()},
            path=tuple(ap_list),
            description=(
                f"Done: {len(ap_list)} articulation point(s) → "
                + (", ".join(ap_list) if ap_list else "none")
            ),
        )
