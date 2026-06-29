"""Trie (Prefix Tree) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Dict, Generator, List, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

_WORDS = [
    ["cat", "car", "card", "care", "cart"],
    ["app", "apple", "apt", "ape"],
    ["bat", "ball", "ban", "band", "bar"],
    ["dog", "dot", "do", "door", "dock"],
    ["hot", "hop", "horn", "horse", "home"],
    ["sun", "sum", "sub", "sup", "sue"],
    ["ten", "tea", "team", "teal", "tear"],
    ["fly", "flaw", "flag", "flat", "flab"],
]


def _build_trie(words: List[str]):
    """Build trie node dict. Returns (children, is_end) for each node id."""
    node_id = [0]
    children: Dict[int, Dict[str, int]] = {0: {}}
    is_end: Dict[int, bool] = {0: False}
    label: Dict[int, str] = {0: "*"}  # root

    def insert(word: str):
        cur = 0
        for ch in word:
            if ch not in children[cur]:
                node_id[0] += 1
                nid = node_id[0]
                children[cur][ch] = nid
                children[nid] = {}
                is_end[nid] = False
                label[nid] = ch
            cur = children[cur][ch]
        is_end[cur] = True

    for w in words:
        insert(w)

    return children, is_end, label, node_id[0]


def _layout(children: Dict, n_nodes: int) -> Dict[int, Tuple[float, float]]:
    """Simple BFS layout for tree visualization."""
    pos: Dict[int, Tuple[float, float]] = {}
    depth: Dict[int, int] = {0: 0}
    order: List[int] = [0]
    q = [0]
    max_depth = 0
    while q:
        node = q.pop(0)
        for ch_node in sorted(children[node].values()):
            depth[ch_node] = depth[node] + 1
            max_depth = max(max_depth, depth[ch_node])
            order.append(ch_node)
            q.append(ch_node)
    # Assign x positions per depth level
    by_depth: Dict[int, List[int]] = {}
    for nid in order:
        d = depth[nid]
        by_depth.setdefault(d, []).append(nid)
    for d, nodes in by_depth.items():
        for i, nid in enumerate(nodes):
            pos[nid] = (i / max(1, len(nodes) - 1) * 8.0, d * 2.0)
    return pos


class TrieSimulation(AlgorithmPlugin):
    """
    Trie (Prefix Tree) — insert words then search.

    GraphTraversalState with visualization_type=TREE:
      nodes: trie nodes (id = node_id, label = char or '*' for root)
      visited: nodes confirmed to be on the search path
      current: current node being visited
      path: sequence of node ids traversed during current insert/search
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="trie",
            name="Trie (Prefix Tree)",
            category="tree",
            visualization_type="TREE",
            description=(
                "Build a trie from words. "
                "Each node stores one character. Mark terminal nodes as end-of-word."
            ),
            intuition=(
                "Insert: walk the trie character by character, creating nodes when needed. "
                "Search: same walk — if all chars found, prefix exists. "
                "End-of-word flag distinguishes full words from prefixes."
            ),
            complexity_time_best="O(L) per operation",
            complexity_time_average="O(L) per operation",
            complexity_time_worst="O(L) per operation",
            complexity_space="O(n × L)",
            tags=("tree", "trie", "prefix-tree", "string", "search"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        word_set = _WORDS[params.seed % len(_WORDS)]
        children, is_end, label, max_id = _build_trie(word_set)
        pos = _layout(children, max_id + 1)

        nodes = tuple(
            NodeState(
                node_id=str(nid),
                label=("●" if is_end[nid] else "") + label[nid],
                x=pos.get(nid, (0.0, 0.0))[0],
                y=pos.get(nid, (0.0, 0.0))[1],
            )
            for nid in range(max_id + 1)
        )
        edges = []
        for parent, cmap in children.items():
            for ch, child in cmap.items():
                edges.append(EdgeState(
                    edge_id=f"{parent}-{child}",
                    source=str(parent),
                    target=str(child),
                    weight=None,
                    directed=True,
                ))
        return GraphTraversalState(
            nodes=nodes,
            edges=tuple(edges),
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=f"Trie built with {len(word_set)} words: {', '.join(word_set)}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        # Rebuild trie
        words_str = initial_state.description.split(": ")[1]
        words = [w.strip() for w in words_str.split(",")]
        children, is_end, label, max_id = _build_trie(words)

        # Search for the longest word's prefix
        query = words[-1]  # search for the last word
        query_prefix = query[:-1]  # also search for prefix (without last char)

        def node_from_char_path(path_chars: str):
            """Follow path_chars from root, return (node_id, success)."""
            cur = 0
            for ch in path_chars:
                if ch not in children[cur]:
                    return cur, False
                cur = children[cur][ch]
            return cur, True

        visited: set = {"0"}
        cur = 0
        path = ["0"]

        # Step through each character of the search word
        for i, ch in enumerate(query):
            if ch in children[cur]:
                cur = children[cur][ch]
                visited.add(str(cur))
                path.append(str(cur))
                found = is_end[cur] and i == len(query) - 1
                yield GraphTraversalState(
                    nodes=initial_state.nodes,
                    edges=initial_state.edges,
                    visited=frozenset(visited),
                    frontier=tuple(str(c) for c in children[cur].values()),
                    current=str(cur),
                    distances={"depth": float(i + 1)},
                    path=tuple(path),
                    description=(
                        f"Search '{query[:i+1]}': node '{ch}' found"
                        + (" (end-of-word)" if found else "")
                    ),
                )
            else:
                yield GraphTraversalState(
                    nodes=initial_state.nodes,
                    edges=initial_state.edges,
                    visited=frozenset(visited),
                    frontier=(),
                    current=str(cur),
                    distances={"depth": float(i)},
                    path=tuple(path),
                    description=f"Search '{query[:i+1]}': '{ch}' not found — MISS",
                )
                return GraphTraversalState(
                    nodes=initial_state.nodes,
                    edges=initial_state.edges,
                    visited=frozenset(visited),
                    frontier=(),
                    current=None,
                    distances={},
                    path=tuple(path),
                    description=f"'{query}' NOT FOUND in trie",
                )

        found_word = is_end[cur]
        return GraphTraversalState(
            nodes=initial_state.nodes,
            edges=initial_state.edges,
            visited=frozenset(visited),
            frontier=(),
            current=None,
            distances={"depth": float(len(query))},
            path=tuple(path),
            description=(
                f"Search complete: '{query}' "
                + ("FOUND (end-of-word)" if found_word else "PREFIX ONLY")
            ),
        )
