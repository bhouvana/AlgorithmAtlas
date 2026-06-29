"""Bridge Finding plugin for Algorithm Atlas."""
from __future__ import annotations

import math
import random
from typing import Dict, Generator, List, Set, Tuple

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


class BridgesSimulation(AlgorithmPlugin):
    """
    Bridge Finding — Tarjan's DFS-based algorithm, O(V + E).

    An edge (u, v) is a bridge if low[v] > disc[u]: no back edge in v's
    DFS subtree can reach u or an ancestor of u, so removing (u,v) disconnects
    the graph.

    State encoding:
      distances: disc[] values (float for type compatibility)
      path:      sorted edge strings "U-V" for each confirmed bridge so far
      visited:   all discovered nodes
      frontier:  current DFS call stack
      current:   active node
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bridges",
            name="Bridge Finding",
            category="graph",
            visualization_type="GRAPH",
            description=(
                "Find all bridge edges whose removal disconnects the graph "
                "using Tarjan's DFS low-value technique."
            ),
            intuition=(
                "Run DFS and track disc and low for each node. "
                "Edge (u→v) is a bridge when low[v] > disc[u], "
                "meaning v's entire subtree cannot reach u without this edge."
            ),
            complexity_time_best="O(V + E)",
            complexity_time_average="O(V + E)",
            complexity_time_worst="O(V + E)",
            complexity_space="O(V)",
            tags=("graph", "bridges", "cut-edges", "dfs", "tarjan"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("node_count", 7), 10))
        extra: int = params.inputs.get("extra_edges", max(1, n // 4))

        nodes, edges = _make_graph(rng, n, extra)

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=(
                f"Find bridges: {n} nodes, {len(edges)} edges. "
                "Bridges are edges whose removal disconnects the graph."
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
        bridges: List[Tuple[str, str]] = []  # confirmed bridges as (u, v) sorted pairs

        def bridge_path() -> Tuple[str, ...]:
            return tuple(f"{u}-{v}" for u, v in sorted(bridges))

        all_nodes = sorted(nd.node_id for nd in nodes)

        for start in all_nodes:
            if start in disc:
                continue

            disc[start] = low[start] = timer[0]
            timer[0] += 1

            # Frame: [u, parent_u, nbr_iter]
            stack_frames: List[List] = [
                [start, None, iter(sorted(adj[start]))]
            ]

            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset(disc.keys()),
                frontier=tuple(f[0] for f in stack_frames),
                current=start,
                distances={k: float(v) for k, v in disc.items()},
                path=bridge_path(),
                description=f"Discover {start}: disc[{start}]={disc[start]}, low[{start}]={low[start]}",
            )

            while stack_frames:
                u = stack_frames[-1][0]
                par_u = stack_frames[-1][1]
                nbr_iter = stack_frames[-1][2]

                try:
                    v = next(nbr_iter)
                except StopIteration:
                    # Finished u — propagate low and check bridge to parent
                    stack_frames.pop()

                    if stack_frames:
                        p_node = stack_frames[-1][0]
                        old_low_p = low[p_node]
                        low[p_node] = min(low[p_node], low[u])

                        is_bridge = low[u] > disc[p_node]
                        if is_bridge:
                            a, b = (min(p_node, u), max(p_node, u))
                            if (a, b) not in bridges:
                                bridges.append((a, b))

                        msg = (
                            f"Return {u}→{p_node}: low[{p_node}]="
                            f"min({old_low_p},{low[u]})={low[p_node]}"
                        )
                        if is_bridge:
                            msg += (
                                f" → ({p_node},{u}) is BRIDGE "
                                f"(low[{u}]={low[u]} > disc[{p_node}]={disc[p_node]})"
                            )

                        yield GraphTraversalState(
                            nodes=nodes,
                            edges=edges,
                            visited=frozenset(disc.keys()),
                            frontier=tuple(f[0] for f in stack_frames),
                            current=p_node,
                            distances={k: float(v) for k, v in disc.items()},
                            path=bridge_path(),
                            description=msg,
                        )
                    else:
                        # Root finished
                        yield GraphTraversalState(
                            nodes=nodes,
                            edges=edges,
                            visited=frozenset(disc.keys()),
                            frontier=(),
                            current=None,
                            distances={k: float(v) for k, v in disc.items()},
                            path=bridge_path(),
                            description=f"Root {u} finished.",
                        )
                    continue

                if v == par_u:
                    continue

                if v not in disc:
                    # Tree edge
                    disc[v] = low[v] = timer[0]
                    timer[0] += 1
                    stack_frames.append([v, u, iter(sorted(adj[v]))])

                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(disc.keys()),
                        frontier=tuple(f[0] for f in stack_frames),
                        current=v,
                        distances={k: float(v_) for k, v_ in disc.items()},
                        path=bridge_path(),
                        description=(
                            f"Tree edge {u}→{v}: "
                            f"disc[{v}]={disc[v]}, low[{v}]={low[v]}"
                        ),
                    )
                else:
                    # Back edge
                    old_low = low[u]
                    low[u] = min(low[u], disc[v])
                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(disc.keys()),
                        frontier=tuple(f[0] for f in stack_frames),
                        current=u,
                        distances={k: float(v_) for k, v_ in disc.items()},
                        path=bridge_path(),
                        description=(
                            f"Back edge {u}→{v}: "
                            f"low[{u}]=min({old_low},{disc[v]})={low[u]}"
                        ),
                    )

        bridge_list = sorted(bridges)
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(disc.keys()),
            frontier=(),
            current=None,
            distances={k: float(v) for k, v in disc.items()},
            path=bridge_path(),
            description=(
                f"Done: {len(bridge_list)} bridge(s) → "
                + (", ".join(f"({a},{b})" for a, b in bridge_list) if bridge_list else "none")
            ),
        )
