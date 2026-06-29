"""Link-Cut Tree plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator, List, Optional

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

# Demo: 6 nodes; show link / cut / find_root / connected operations
_N = 6
_NODE_POS = [
    (0.15, 0.50),  # 0
    (0.38, 0.20),  # 1
    (0.38, 0.80),  # 2
    (0.62, 0.20),  # 3
    (0.62, 0.80),  # 4
    (0.85, 0.50),  # 5
]


class _Node:
    __slots__ = ("ch", "p", "rev", "val", "path_agg")

    def __init__(self, val=0):
        self.ch: List[Optional[_Node]] = [None, None]
        self.p: Optional[_Node] = None
        self.rev: bool = False
        self.val: int = val
        self.path_agg: int = val


class _LCT:
    def __init__(self, n):
        self.nodes = [_Node(i) for i in range(n)]

    def _is_root(self, u):
        p = u.p
        return p is None or (p.ch[0] is not u and p.ch[1] is not u)

    def _push(self, u):
        if u.rev:
            u.ch[0], u.ch[1] = u.ch[1], u.ch[0]
            if u.ch[0]:
                u.ch[0].rev ^= True
            if u.ch[1]:
                u.ch[1].rev ^= True
            u.rev = False

    def _pull(self, u):
        agg = u.val
        if u.ch[0]:
            agg += u.ch[0].path_agg
        if u.ch[1]:
            agg += u.ch[1].path_agg
        u.path_agg = agg

    def _rotate(self, u):
        p, g = u.p, u.p.p if u.p else None
        d = 1 if p.ch[1] is u else 0
        c = u.ch[d ^ 1]
        if not self._is_root(p):
            if g.ch[0] is p:
                g.ch[0] = u
            else:
                g.ch[1] = u
        u.p = g
        if c:
            c.p = p
        p.ch[d] = c
        u.ch[d ^ 1] = p
        p.p = u
        self._pull(p)
        self._pull(u)

    def _splay(self, u):
        stk = []
        v = u
        stk.append(v)
        while not self._is_root(v):
            v = v.p
            stk.append(v)
        while stk:
            self._push(stk.pop())
        while not self._is_root(u):
            p = u.p
            if not self._is_root(p):
                gp = p.p
                if (gp.ch[0] is p) == (p.ch[0] is u):
                    self._rotate(p)
                else:
                    self._rotate(u)
            self._rotate(u)

    def access(self, u):
        last = None
        v = u
        while v:
            self._splay(v)
            v.ch[1] = last
            self._pull(v)
            last = v
            v = v.p
        self._splay(u)
        return last

    def make_root(self, u):
        self.access(u)
        u.rev ^= True
        self._push(u)

    def find_root(self, u):
        self.access(u)
        while u.ch[0]:
            self._push(u)
            u = u.ch[0]
        self._splay(u)
        return u

    def link(self, u, v):
        """Link trees rooted at u and v (make u child of v)."""
        self.make_root(u)
        if self.find_root(v) is not u:
            u.p = v
            return True
        return False  # already connected

    def cut(self, u, v):
        """Cut the edge between u and v."""
        self.make_root(u)
        self.access(v)
        if v.ch[0] is u and u.ch[1] is None:
            v.ch[0] = None
            u.p = None
            self._pull(v)
            return True
        return False  # edge does not exist

    def connected(self, u, v):
        return self.find_root(u) is self.find_root(v)


def _snapshot(lct, n, pos, active_edges, label, highlight=None):
    nodes = [
        NodeState(
            node_id=str(i),
            label=str(i),
            x=pos[i][0],
            y=pos[i][1],
            weight=2.0 if highlight and i in highlight else 0.0,
        )
        for i in range(n)
    ]
    edges = [
        EdgeState(
            edge_id=f"e{min(u,v)}_{max(u,v)}",
            source=str(u),
            target=str(v),
            weight=1.0,
            directed=False,
        )
        for u, v in active_edges
    ]
    return nodes, edges


class LinkCutTreeSimulation(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="link-cut-tree",
            name="Link-Cut Tree",
            category="tree",
            visualization_type="GRAPH",
            description="Dynamic forest with O(log n) link, cut, and path-query operations via splay trees.",
            intuition=(
                "Each preferred path is maintained as a splay tree (auxiliary). "
                "access(u) reassigns preferred paths from u to root. "
                "make_root reverses the path to make u the root. "
                "link/cut modify parent pointers in O(log n) amortised time."
            ),
            complexity_time_best="O(log n) amortized",
            complexity_time_average="O(log n) amortized",
            complexity_time_worst="O(log n) amortized",
            complexity_space="O(n)",
            tags=("tree", "link-cut-tree", "splay-tree", "dynamic-trees", "advanced"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        nodes = tuple(
            NodeState(node_id=str(i), label=str(i), x=x, y=y, weight=0.0)
            for i, (x, y) in enumerate(_NODE_POS)
        )
        return GraphTraversalState(
            nodes=nodes,
            edges=(),
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=f"LCT: {_N} isolated nodes",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        lct = _LCT(_N)
        pos = _NODE_POS
        active: set = set()   # set of (u,v) edges, u<v

        def make_state(desc, highlight=None):
            edge_set = sorted(active)
            ns = [
                NodeState(
                    node_id=str(i),
                    label=str(i),
                    x=pos[i][0],
                    y=pos[i][1],
                    weight=2.0 if highlight and i in highlight else 0.0,
                )
                for i in range(_N)
            ]
            es = [
                EdgeState(
                    edge_id=f"e{u}_{v}",
                    source=str(u),
                    target=str(v),
                    weight=1.0,
                    directed=False,
                )
                for u, v in edge_set
            ]
            return GraphTraversalState(
                nodes=tuple(ns),
                edges=tuple(es),
                visited=frozenset(),
                frontier=(),
                current=None,
                distances={},
                path=(),
                description=desc,
            )

        ops = [
            ("link", 0, 1),
            ("link", 1, 3),
            ("link", 0, 2),
            ("link", 2, 4),
            ("link", 3, 5),
            ("connected", 0, 5),
            ("cut", 1, 3),
            ("connected", 0, 5),
            ("link", 2, 5),
            ("connected", 0, 5),
        ]

        for op, u, v in ops:
            if op == "link":
                ok = lct.link(lct.nodes[u], lct.nodes[v])
                if ok:
                    active.add((min(u, v), max(u, v)))
                yield make_state(
                    f"link({u},{v}) {'✓ linked' if ok else '✗ already connected'}",
                    highlight={u, v},
                )
            elif op == "cut":
                ok = lct.cut(lct.nodes[u], lct.nodes[v])
                if ok:
                    active.discard((min(u, v), max(u, v)))
                yield make_state(
                    f"cut({u},{v}) {'✓ removed' if ok else '✗ edge not found'}",
                    highlight={u, v},
                )
            elif op == "connected":
                res = lct.connected(lct.nodes[u], lct.nodes[v])
                yield make_state(
                    f"connected({u},{v}) = {res}",
                    highlight={u, v},
                )

        final = make_state(
            f"Done: {len(active)} edges in forest",
            highlight=None,
        )
        yield final
        return final
