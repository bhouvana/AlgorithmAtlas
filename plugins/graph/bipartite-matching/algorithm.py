"""Bipartite Matching (Augmenting Paths) plugin for Algorithm Atlas."""
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

# Fixed bipartite graph: 5 left + 5 right nodes
# Adjacency: adj[l] = list of right-node indices reachable from l
_L = 5  # number of left nodes
_R = 5  # number of right nodes
_ADJ = [
    [0, 1],       # L0 → R0, R1
    [1, 2],       # L1 → R1, R2
    [0, 3],       # L2 → R0, R3
    [2, 4],       # L3 → R2, R4
    [3, 4],       # L4 → R3, R4
]

# Layout: left nodes on left column, right nodes on right column
def _node_pos(i: int, side: str):
    """Return (x, y) for node i on the given side."""
    if side == "L":
        return 0.15, (i + 1) / (_L + 1)
    else:
        return 0.85, (i + 1) / (_R + 1)


def _make_state(
    match_l: dict,
    match_r: dict,
    aug_path: list,
    current: str | None,
    desc: str,
) -> GraphTraversalState:
    nodes = []
    for i in range(_L):
        x, y = _node_pos(i, "L")
        label = f"L{i}" + (f"→R{match_l[i]}" if i in match_l else "")
        nodes.append(NodeState(node_id=f"L{i}", label=label, x=x, y=y))
    for j in range(_R):
        x, y = _node_pos(j, "R")
        label = f"R{j}" + (f"←L{match_r[j]}" if j in match_r else "")
        nodes.append(NodeState(node_id=f"R{j}", label=label, x=x, y=y))

    edges = []
    matched_edges = {(l, match_l[l]) for l in match_l}
    for l, nbrs in enumerate(_ADJ):
        for r in nbrs:
            matched = (l, r) in matched_edges
            edges.append(EdgeState(
                edge_id=f"L{l}-R{r}",
                source=f"L{l}",
                target=f"R{r}",
                weight=1.0 if matched else 0.0,
                directed=False,
            ))

    visited = frozenset(f"L{l}" for l in match_l) | frozenset(f"R{r}" for r in match_r)
    path = tuple(aug_path)

    return GraphTraversalState(
        nodes=tuple(nodes),
        edges=tuple(edges),
        visited=visited,
        frontier=tuple(),
        current=current,
        distances={f"L{l}": float(r) for l, r in match_l.items()},
        path=path,
        description=desc,
    )


def _augment(u: int, match_l: dict, match_r: dict, seen: set) -> list | None:
    """DFS from left node u. Returns augmenting path as list of node-ids, or None."""
    for v in _ADJ[u]:
        if v not in seen:
            seen.add(v)
            if v not in match_r or _augment(match_r[v], match_l, match_r, seen) is not None:
                # Augment
                match_l[u] = v
                match_r[v] = u
                return [f"L{u}", f"R{v}"]
    return None


class BipartiteMatchingSimulation(AlgorithmPlugin):
    """Maximum bipartite matching via augmenting paths."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bipartite-matching",
            name="Bipartite Matching (Augmenting Paths)",
            category="graph",
            visualization_type="GRAPH",
            description=(
                "Find a maximum matching in a bipartite graph by "
                "repeatedly augmenting along free paths."
            ),
            intuition=(
                "From each unmatched left node, try to find an alternating path "
                "to an unmatched right node. Flip matched/unmatched edges along "
                "the path to increase the matching by 1."
            ),
            complexity_time_best="O(V × E)",
            complexity_time_average="O(V × E)",
            complexity_time_worst="O(V × E)",
            complexity_space="O(V + E)",
            tags=("graph", "bipartite", "matching", "augmenting-path"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        return _make_state(
            match_l={},
            match_r={},
            aug_path=[],
            current=None,
            desc=f"Bipartite matching: {_L}L + {_R}R nodes. Starting.",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        match_l: dict = {}
        match_r: dict = {}
        total = 0

        for u in range(_L):
            seen: set = set()
            path = _augment(u, match_l, match_r, seen)

            yield _make_state(
                match_l=dict(match_l),
                match_r=dict(match_r),
                aug_path=[f"L{u}"] + (path or []),
                current=f"L{u}",
                desc=(
                    f"L{u}: "
                    + (f"augmenting path found → matched with R{match_l[u]}"
                       if u in match_l
                       else "no augmenting path")
                ),
            )

            if u in match_l:
                total += 1

        return _make_state(
            match_l=dict(match_l),
            match_r=dict(match_r),
            aug_path=[],
            current=None,
            desc=(
                f"Maximum matching = {total}: "
                + ", ".join(f"L{l}↔R{r}" for l, r in sorted(match_l.items()))
            ),
        )
