"""Aho-Corasick pattern count plugin for Algorithm Atlas."""
from __future__ import annotations

from collections import deque
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

_PATTERNS = ["he", "she", "his", "hers"]
_TEXT = "ushers"


def _build_automaton(patterns):
    goto = [{}]
    fail = [0]
    output = [[]]
    state = 1

    # Build trie
    for pid, pat in enumerate(patterns):
        cur = 0
        for ch in pat:
            if ch not in goto[cur]:
                goto[cur][ch] = state
                goto.append({})
                fail.append(0)
                output.append([])
                state += 1
            cur = goto[cur][ch]
        output[cur].append(pid)

    # Build failure links via BFS
    q = deque()
    for ch, s in goto[0].items():
        fail[s] = 0
        q.append(s)
    while q:
        r = q.popleft()
        for ch, s in goto[r].items():
            q.append(s)
            state_f = fail[r]
            while state_f and ch not in goto[state_f]:
                state_f = fail[state_f]
            fail[s] = goto[state_f].get(ch, 0)
            if fail[s] == s:
                fail[s] = 0
            output[s] = output[s] + output[fail[s]]
    return goto, fail, output, state


# Pre-build for use in visualization
_GOTO, _FAIL, _OUTPUT, _NUM_STATES = _build_automaton(_PATTERNS)

_STATE_LABELS = ["root"] + [""] * (_NUM_STATES - 1)
for pid, pat in enumerate(_PATTERNS):
    cur = 0
    prefix = ""
    for ch in pat:
        cur = _GOTO[cur][ch]
        prefix += ch
        if not _STATE_LABELS[cur]:
            _STATE_LABELS[cur] = prefix

# Positions: root at left, then trie nodes arranged by BFS depth
_POS = [(0.05, 0.50)]
_BFS_DEPTH = [0] * _NUM_STATES
_Q2 = deque([0])
_SEEN = {0}
while _Q2:
    u = _Q2.popleft()
    children = sorted(_GOTO[u].items())
    depth = _BFS_DEPTH[u]
    n_ch = len(children)
    for k, (ch, v) in enumerate(children):
        if v not in _SEEN:
            _SEEN.add(v)
            _BFS_DEPTH[v] = depth + 1
            _Q2.append(v)

# Simple grid layout
_DEPTH_COUNTS = {}
for s in range(_NUM_STATES):
    d = _BFS_DEPTH[s]
    _DEPTH_COUNTS[d] = _DEPTH_COUNTS.get(d, 0) + 1

_DEPTH_IDX = {}
for s in range(_NUM_STATES):
    d = _BFS_DEPTH[s]
    _DEPTH_IDX[s] = _DEPTH_IDX.get(d, -1) + 1
    _DEPTH_IDX[d] = _DEPTH_IDX[s]

_NODE_X = {s: 0.05 + _BFS_DEPTH[s] * 0.22 for s in range(_NUM_STATES)}
_cnt_at_depth: dict = {}
_OFFSET_IDX: dict = {}
for s in range(_NUM_STATES):
    d = _BFS_DEPTH[s]
    _cnt_at_depth[d] = _cnt_at_depth.get(d, 0)
    _OFFSET_IDX[s] = _cnt_at_depth[d]
    _cnt_at_depth[d] += 1

_NODE_Y = {}
for s in range(_NUM_STATES):
    d = _BFS_DEPTH[s]
    total = _DEPTH_COUNTS.get(d, 1)
    idx = _OFFSET_IDX[s]
    _NODE_Y[s] = 0.1 + idx * (0.8 / max(total, 1))

_POS_FINAL = {s: (_NODE_X[s], _NODE_Y[s]) for s in range(_NUM_STATES)}


class AhoCorasickCountSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="aho-corasick-count",
            name="Aho-Corasick Pattern Count",
            category="string",
            visualization_type="GRAPH",
            description="Count all occurrences of multiple patterns in a text using the Aho-Corasick automaton.",
            intuition=(
                "Build a trie of all patterns and connect nodes with failure links (like KMP). "
                "Process the text in one pass: follow trie edges, use failure links on mismatch. "
                "Count all pattern matches including overlapping ones."
            ),
            complexity_time_best="O(n+m+z)",
            complexity_time_average="O(n+m+z)",
            complexity_time_worst="O(n+m+z)",
            complexity_space="O(m)",
            tags=("string", "aho-corasick", "pattern-matching", "multi-pattern", "automaton"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        nodes = tuple(
            NodeState(
                node_id=str(s),
                label=_STATE_LABELS[s] or str(s),
                x=_POS_FINAL[s][0],
                y=_POS_FINAL[s][1],
                weight=0.0,
            )
            for s in range(_NUM_STATES)
        )
        edges = []
        for u in range(_NUM_STATES):
            for ch, v in sorted(_GOTO[u].items()):
                edges.append(
                    EdgeState(
                        edge_id=f"t{u}_{v}",
                        source=str(u),
                        target=str(v),
                        weight=1.0,
                        directed=True,
                    )
                )
        for s in range(1, _NUM_STATES):
            if _FAIL[s]:
                edges.append(
                    EdgeState(
                        edge_id=f"f{s}_{_FAIL[s]}",
                        source=str(s),
                        target=str(_FAIL[s]),
                        weight=0.0,   # 0 = failure link (drawn differently)
                        directed=True,
                    )
                )
        return GraphTraversalState(
            nodes=nodes,
            edges=tuple(edges),
            visited=frozenset(),
            frontier=(),
            current="0",
            distances={},
            path=(),
            description=f"Automaton built: {_NUM_STATES} states, patterns={_PATTERNS}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        goto, fail, output = _GOTO, _FAIL, _OUTPUT

        def make_state(cur_state, visited_set, matches, desc):
            nodes = [
                NodeState(
                    node_id=str(s),
                    label=_STATE_LABELS[s] or str(s),
                    x=_POS_FINAL[s][0],
                    y=_POS_FINAL[s][1],
                    weight=2.0 if s == cur_state else 1.0 if str(s) in visited_set else 0.0,
                )
                for s in range(_NUM_STATES)
            ]
            return GraphTraversalState(
                nodes=tuple(nodes),
                edges=initial_state.edges,
                visited=frozenset(visited_set),
                frontier=(),
                current=str(cur_state),
                distances={"matches": float(matches)},
                path=(),
                description=desc,
            )

        cur = 0
        total_matches = 0
        visited = set()

        for i, ch in enumerate(_TEXT):
            while cur and ch not in goto[cur]:
                cur = fail[cur]
            cur = goto[cur].get(ch, 0)
            visited.add(str(cur))
            matched = output[cur]
            total_matches += len(matched)
            match_info = (
                " matches: " + ",".join(f'"{_PATTERNS[p]}"' for p in matched)
                if matched else ""
            )
            yield make_state(
                cur,
                visited.copy(),
                total_matches,
                f"text[{i}]='{ch}' → state {cur}{match_info} (total={total_matches})",
            )

        final = make_state(
            cur, visited, total_matches,
            f"Done: {total_matches} total matches in text \"{_TEXT}\"",
        )
        yield final
        return final
