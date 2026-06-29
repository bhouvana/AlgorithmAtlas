"""Tarjan's Strongly Connected Components plugin for Algorithm Atlas."""
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
    return adj


def _make_directed_graph(
    rng: random.Random, n: int, extra: int
) -> Tuple[Tuple[NodeState, ...], Tuple[EdgeState, ...]]:
    """Generate a random directed graph with n nodes and back-edges to create SCCs."""
    labels = [chr(ord("A") + i) for i in range(n)]

    edge_set: set = set()
    edge_list: List[Tuple[str, str]] = []

    # Build a random directed spanning tree (each node except root gets one parent edge)
    shuffled = labels[:]
    rng.shuffle(shuffled)
    for i in range(1, n):
        j = rng.randint(0, i - 1)
        u, v = shuffled[i], shuffled[j]
        key = (u, v)
        if key not in edge_set:
            edge_set.add(key)
            edge_list.append((u, v))

    # Add random directed edges (including some back-edges to form SCCs)
    attempts = 0
    added = 0
    while added < extra and attempts < 300:
        attempts += 1
        u = rng.choice(labels)
        v = rng.choice(labels)
        if u != v:
            key = (u, v)
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
        EdgeState(edge_id=f"e{idx}", source=u, target=v, directed=True)
        for idx, (u, v) in enumerate(edge_list)
    ]

    return tuple(nodes_list), tuple(edges_list)


class TarjanSCCSimulation(AlgorithmPlugin):
    """
    Tarjan's SCC algorithm — O(V + E).

    Single DFS pass. Each node maintains:
      disc[u]  — DFS discovery time
      low[u]   — lowest disc reachable from u's subtree via back/cross edges
      on_stack — whether u is currently on the SCC candidate stack

    When DFS finishes u and low[u] == disc[u], u is the root of an SCC.
    Pop the SCC stack down to u to collect the component.

    State encoding:
      distances: disc[] values (float for compatibility)
      path:      flat sequence of SCC root labels, one per component found so far
                 (format: "SCC1_root SCC2_root ..." where each root is the node
                  with the minimum disc in that component)
      visited:   all discovered nodes
      frontier:  current DFS call stack || current SCC candidate stack
                 (DFS stack is the primary indicator; SCC stack carried in description)
      current:   active node
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="tarjan-scc",
            name="Tarjan's SCC",
            category="graph",
            visualization_type="GRAPH",
            description=(
                "Find all strongly connected components (SCCs) in a directed graph "
                "in a single DFS pass using Tarjan's algorithm."
            ),
            intuition=(
                "Track discovery time and low-link for each node. "
                "A node with low[u] == disc[u] is the root of an SCC — "
                "pop the stack to collect every node in that component."
            ),
            complexity_time_best="O(V + E)",
            complexity_time_average="O(V + E)",
            complexity_time_worst="O(V + E)",
            complexity_space="O(V)",
            tags=("graph", "scc", "strongly-connected", "dfs", "tarjan"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(4, min(params.inputs.get("node_count", 6), 9))
        extra: int = params.inputs.get("extra_edges", n)

        nodes, edges = _make_directed_graph(rng, n, extra)

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=(
                f"Tarjan SCC: {n} nodes, {len(edges)} directed edges. "
                "DFS from first unvisited node."
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
        on_stack: Set[str] = set()
        scc_stack: List[str] = []
        timer = [0]

        # sccs: list of sorted node lists, one per SCC
        sccs: List[List[str]] = []

        def scc_path_repr() -> Tuple[str, ...]:
            # Each SCC represented by its sorted-first node
            return tuple(comp[0] for comp in sccs)

        all_nodes = sorted(nd.node_id for nd in nodes)

        for start in all_nodes:
            if start in disc:
                continue

            disc[start] = low[start] = timer[0]
            timer[0] += 1
            scc_stack.append(start)
            on_stack.add(start)

            # Frame: [u, nbr_iter]
            stack_frames: List[List] = [
                [start, iter(sorted(adj[start]))]
            ]

            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset(disc.keys()),
                frontier=tuple(f[0] for f in stack_frames),
                current=start,
                distances={k: float(v) for k, v in disc.items()},
                path=scc_path_repr(),
                description=(
                    f"Discover {start}: disc={disc[start]}, low={low[start]}; "
                    f"SCC-stack=[{','.join(scc_stack)}]"
                ),
            )

            while stack_frames:
                u = stack_frames[-1][0]
                nbr_iter = stack_frames[-1][1]

                try:
                    v = next(nbr_iter)
                except StopIteration:
                    # Finished u — check if u is SCC root
                    stack_frames.pop()

                    is_root = low[u] == disc[u]
                    if is_root:
                        # Pop SCC from scc_stack
                        component: List[str] = []
                        while True:
                            w = scc_stack.pop()
                            on_stack.discard(w)
                            component.append(w)
                            if w == u:
                                break
                        component.sort()
                        sccs.append(component)

                        yield GraphTraversalState(
                            nodes=nodes,
                            edges=edges,
                            visited=frozenset(disc.keys()),
                            frontier=tuple(f[0] for f in stack_frames),
                            current=u,
                            distances={k: float(v) for k, v in disc.items()},
                            path=scc_path_repr(),
                            description=(
                                f"SCC root {u}: low[{u}]={low[u]}=disc[{u}] → "
                                f"SCC={{{','.join(component)}}}"
                            ),
                        )
                    else:
                        # Propagate low to parent
                        if stack_frames:
                            p = stack_frames[-1][0]
                            old_low_p = low[p]
                            low[p] = min(low[p], low[u])

                            yield GraphTraversalState(
                                nodes=nodes,
                                edges=edges,
                                visited=frozenset(disc.keys()),
                                frontier=tuple(f[0] for f in stack_frames),
                                current=p,
                                distances={k: float(v) for k, v in disc.items()},
                                path=scc_path_repr(),
                                description=(
                                    f"Return {u}→{p}: low[{p}]="
                                    f"min({old_low_p},{low[u]})={low[p]}; "
                                    f"SCC-stack=[{','.join(scc_stack)}]"
                                ),
                            )
                    continue

                if v not in disc:
                    # Tree edge
                    disc[v] = low[v] = timer[0]
                    timer[0] += 1
                    scc_stack.append(v)
                    on_stack.add(v)
                    stack_frames.append([v, iter(sorted(adj[v]))])

                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(disc.keys()),
                        frontier=tuple(f[0] for f in stack_frames),
                        current=v,
                        distances={k: float(v_) for k, v_ in disc.items()},
                        path=scc_path_repr(),
                        description=(
                            f"Tree edge {u}→{v}: disc[{v}]={disc[v]}, low[{v}]={low[v]}; "
                            f"SCC-stack=[{','.join(scc_stack)}]"
                        ),
                    )
                elif v in on_stack:
                    # Back edge to node on SCC stack — update low
                    old_low = low[u]
                    low[u] = min(low[u], disc[v])
                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset(disc.keys()),
                        frontier=tuple(f[0] for f in stack_frames),
                        current=u,
                        distances={k: float(v_) for k, v_ in disc.items()},
                        path=scc_path_repr(),
                        description=(
                            f"Back edge {u}→{v} (on stack): "
                            f"low[{u}]=min({old_low},{disc[v]})={low[u]}"
                        ),
                    )
                # else: cross edge to already-finished SCC — no low update needed

        scc_count = len(sccs)
        all_in_sccs = sorted(n for comp in sccs for n in comp)
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(disc.keys()),
            frontier=(),
            current=None,
            distances={k: float(v) for k, v in disc.items()},
            path=scc_path_repr(),
            description=(
                f"Done: {scc_count} SCC(s) — "
                + "; ".join(f"{{{','.join(c)}}}" for c in sccs)
            ),
        )
