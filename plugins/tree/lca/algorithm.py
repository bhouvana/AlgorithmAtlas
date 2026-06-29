"""Lowest Common Ancestor (LCA) plugin for Algorithm Atlas."""
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


def _build_bst(rng: random.Random, n: int):
    values: Dict[str, int] = {}
    children: Dict[str, List[Optional[str]]] = {}
    pool = rng.sample(range(10, 99), n)
    root = "n0"
    for i, val in enumerate(pool):
        nid = f"n{i}"
        values[nid] = val
        children[nid] = [None, None]
    for i in range(1, n):
        nid = f"n{i}"
        val = values[nid]
        curr = root
        while True:
            if val < values[curr]:
                if children[curr][0] is None:
                    children[curr][0] = nid
                    break
                curr = children[curr][0]
            else:
                if children[curr][1] is None:
                    children[curr][1] = nid
                    break
                curr = children[curr][1]

    depths: Dict[str, int] = {root: 0}
    q = [root]
    all_nodes = []
    max_depth = 0
    while q:
        node = q.pop(0)
        all_nodes.append(node)
        d = depths[node]
        max_depth = max(max_depth, d)
        for child in filter(None, children[node]):
            depths[child] = d + 1
            q.append(child)

    x_pos: Dict[str, int] = {}
    counter = [0]

    def _inorder_assign(nid):
        if nid is None:
            return
        _inorder_assign(children[nid][0])
        x_pos[nid] = counter[0]
        counter[0] += 1
        _inorder_assign(children[nid][1])

    _inorder_assign(root)
    max_x = max(x_pos.values()) if x_pos else 0

    node_list = [
        NodeState(
            node_id=nid,
            label=str(values[nid]),
            x=0.05 + 0.9 * x_pos[nid] / max_x if max_x else 0.5,
            y=0.06 + 0.82 * depths[nid] / max_depth if max_depth else 0.1,
        )
        for nid in sorted(values, key=lambda k: int(k[1:]))
    ]
    edges = []
    eid = 0
    for nid, (left, right) in children.items():
        if left:
            edges.append(EdgeState(edge_id=f"e{eid}", source=nid, target=left, directed=True))
            eid += 1
        if right:
            edges.append(EdgeState(edge_id=f"e{eid}", source=nid, target=right, directed=True))
            eid += 1

    return root, values, children, depths, all_nodes, tuple(node_list), tuple(edges)


class LCASimulation(AlgorithmPlugin):
    """
    Lowest Common Ancestor — iterative DFS.

    GraphTraversalState:
      distances: {"p": node_id of p, "q": node_id of q (as float via hash)}
      path: path to the LCA
      current: the LCA node (in final state)
    """

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="lca",
            name="Lowest Common Ancestor",
            category="tree",
            visualization_type="TREE",
            description=(
                "Find the deepest node that is an ancestor of both query nodes "
                "in a binary tree."
            ),
            intuition=(
                "Post-order DFS: a node is LCA if it equals p or q, "
                "or if one of p/q is found in its left subtree and the other in its right. "
                "Return the node upward when found."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(h)",
            tags=("tree", "lca", "ancestor", "dfs", "binary-tree"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n: int = max(5, min(params.inputs.get("array_size", 7), 12))
        root, values, children, depths, all_nodes, node_states, edge_states = _build_bst(rng, n)

        # Pick two distinct leaf-ish nodes as p and q
        leaves = [v for v in all_nodes if children[v][0] is None and children[v][1] is None]
        if len(leaves) >= 2:
            p, q = rng.sample(leaves, 2)
        else:
            candidates = all_nodes[1:]  # exclude root
            p = candidates[0]
            q = candidates[-1] if len(candidates) > 1 else all_nodes[0]

        return GraphTraversalState(
            nodes=node_states,
            edges=edge_states,
            visited=frozenset(),
            frontier=(root, p, q),
            current=None,
            distances={
                "p_value": float(values[p]),
                "q_value": float(values[q]),
            },
            path=(),
            description=f"Find LCA of {values[p]} and {values[q]} in BST",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        root = initial_state.frontier[0]
        p_str = initial_state.frontier[1]
        q_str = initial_state.frontier[2]
        p_val = initial_state.distances["p_value"]
        q_val = initial_state.distances["q_value"]

        children: Dict[str, List[str]] = {n.node_id: [] for n in initial_state.nodes}
        values: Dict[str, str] = {n.node_id: n.label for n in initial_state.nodes}
        for e in initial_state.edges:
            children[e.source].append(e.target)

        # Iterative post-order DFS with parent tracking
        parent: Dict[str, Optional[str]] = {root: None}
        stack = [root]
        visited_in_dfs: set = set()
        dfs_order: list = []
        lca_result = [None]

        # BFS to find all nodes and build parent map
        from collections import deque
        bfs_q = deque([root])
        while bfs_q:
            node = bfs_q.popleft()
            for child in sorted(children[node]):
                parent[child] = node
                bfs_q.append(child)

        # Path to root for both p and q
        def path_to_root(node: str) -> list:
            path = []
            cur = node
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return path

        path_p = path_to_root(p_str)
        path_q = path_to_root(q_str)
        set_q = set(path_q)

        # Find LCA (first common ancestor)
        lca_node = None
        for node in path_p:
            if node in set_q:
                lca_node = node
                break

        visited: set = set()
        # Yield frames showing DFS traversal
        dfs_stack = [root]
        frames_path: list = []

        while dfs_stack:
            node = dfs_stack.pop()
            if node in visited:
                continue
            visited.add(node)
            frames_path.append(node)

            is_target = node in (p_str, q_str)
            is_lca = node == lca_node
            desc = f"Visit {values[node]}"
            if is_target:
                desc += f" ← {'p' if node == p_str else 'q'}={values[node]}"
            if is_lca:
                desc += " ← LCA!"

            yield GraphTraversalState(
                nodes=initial_state.nodes,
                edges=initial_state.edges,
                visited=frozenset(visited),
                frontier=tuple(dfs_stack),
                current=node,
                distances={"p_value": p_val, "q_value": q_val},
                path=tuple(frames_path),
                description=desc,
            )

            for child in sorted(children[node], reverse=True):
                if child not in visited:
                    dfs_stack.append(child)

        return GraphTraversalState(
            nodes=initial_state.nodes,
            edges=initial_state.edges,
            visited=frozenset(visited),
            frontier=(),
            current=lca_node,
            distances={"p_value": p_val, "q_value": q_val, "lca_value": float(int(values[lca_node]))},
            path=tuple(frames_path),
            description=f"LCA({int(p_val)}, {int(q_val)}) = {values[lca_node]}",
        )
