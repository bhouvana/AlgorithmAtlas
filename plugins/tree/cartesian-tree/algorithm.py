"""Cartesian Tree plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator, Optional

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)

_ARRAY = [3, 2, 6, 1, 9, 4, 8, 7, 5]


def _build_positions(parent, children, root, n):
    """Assign x,y coordinates via BFS-based level layout."""
    from collections import deque
    pos = {}
    level_width = {}
    level_order = {}

    def _height(node):
        if node is None:
            return 0
        c = children.get(node, [])
        return 1 + max((_height(ch) for ch in c), default=0)

    def _assign(node, lo, hi, depth):
        if node is None:
            return
        mid = (lo + hi) / 2.0
        pos[node] = (0.1 + mid * 0.8, 0.1 + depth * 0.12)
        c = children.get(node, [])
        if len(c) == 2:
            _assign(c[0], lo, mid, depth + 1)
            _assign(c[1], mid, hi, depth + 1)
        elif len(c) == 1:
            _assign(c[0], lo, hi, depth + 1)

    _assign(root, 0.0, 1.0, 0)
    return pos


class CartesianTreeSimulation(AlgorithmPlugin):
    """Cartesian tree construction via monotone stack."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="cartesian-tree",
            name="Cartesian Tree",
            category="tree",
            visualization_type="GRAPH",
            description="Build Cartesian tree: min-heap on values, BST on indices.",
            intuition=(
                "Process array left to right. "
                "Pop stack while stack top > current value (heap property). "
                "Popped node becomes current's left child; "
                "current becomes right child of new stack top."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("tree", "cartesian-tree", "heap", "bst", "stack", "data-structure"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        # Just show the array as isolated nodes initially
        n = len(_ARRAY)
        nodes = tuple(
            NodeState(
                node_id=str(i),
                label=str(_ARRAY[i]),
                x=0.05 + i * 0.9 / (n - 1),
                y=0.5,
            )
            for i in range(n)
        )
        return GraphTraversalState(
            nodes=nodes,
            edges=(),
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={str(i): _ARRAY[i] for i in range(n)},
            path=(),
            description="Cartesian Tree: ready (min-heap + BST)",
        )

    def steps(self, initial_state: GraphTraversalState) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        n = len(_ARRAY)
        parent = [None] * n
        left_child = [None] * n
        right_child = [None] * n
        stack = []  # stack of indices

        steps_log = []

        for i in range(n):
            last_popped = None
            while stack and _ARRAY[stack[-1]] > _ARRAY[i]:
                last_popped = stack.pop()

            if last_popped is not None:
                left_child[i] = last_popped
                parent[last_popped] = i

            if stack:
                right_child[stack[-1]] = i
                parent[i] = stack[-1]

            stack.append(i)
            steps_log.append((i, list(stack), dict(enumerate(parent)), dict(enumerate(left_child)), dict(enumerate(right_child))))

        # Find root
        root = next(i for i in range(n) if parent[i] is None)

        # Build positions
        children_map = {}
        for i in range(n):
            kids = []
            if left_child[i] is not None:
                kids.append(left_child[i])
            if right_child[i] is not None:
                kids.append(right_child[i])
            children_map[i] = kids

        pos = _build_positions(parent, children_map, root, n)

        def _make_state(step_i, current_i, stack_now, par, lc, rc, desc):
            nodes = []
            for j in range(n):
                x, y = pos.get(j, (0.05 + j * 0.9 / (n - 1), 0.5))
                in_stack = j in stack_now
                # weight: 2=current, 1=in_stack, 0=visited
                nodes.append(NodeState(
                    node_id=str(j),
                    label=str(_ARRAY[j]),
                    x=x,
                    y=y,
                    weight=2.0 if j == current_i else (1.0 if in_stack else 0.0),
                ))
            edges = []
            for j in range(n):
                if lc.get(j) is not None:
                    edges.append(EdgeState(
                        edge_id=f"L{j}_{lc[j]}",
                        source=str(j),
                        target=str(lc[j]),
                        weight=1.0,
                        directed=False,
                    ))
                if rc.get(j) is not None:
                    edges.append(EdgeState(
                        edge_id=f"R{j}_{rc[j]}",
                        source=str(j),
                        target=str(rc[j]),
                        weight=1.0,
                        directed=False,
                    ))
            return GraphTraversalState(
                nodes=tuple(nodes),
                edges=tuple(edges),
                visited=frozenset(str(k) for k in range(step_i + 1)),
                frontier=tuple(str(k) for k in stack_now),
                current=str(current_i),
                distances={},
                path=(),
                description=desc,
            )

        for step_i, (cur, stk, par, lc, rc) in enumerate(steps_log):
            yield _make_state(
                step_i, cur, stk, lc, rc, lc,
                f"Insert {_ARRAY[cur]} at idx {cur}. Stack: {[_ARRAY[s] for s in stk]}",
            )

        # Final state
        nodes_final = []
        for j in range(n):
            x, y = pos.get(j, (0.05 + j * 0.9 / (n - 1), 0.5))
            nodes_final.append(NodeState(
                node_id=str(j),
                label=str(_ARRAY[j]),
                x=x,
                y=y,
                weight=3.0 if j == root else 1.0,
            ))
        edges_final = []
        for j in range(n):
            if left_child[j] is not None:
                edges_final.append(EdgeState(
                    edge_id=f"L{j}_{left_child[j]}",
                    source=str(j), target=str(left_child[j]),
                    weight=1.0, directed=False,
                ))
            if right_child[j] is not None:
                edges_final.append(EdgeState(
                    edge_id=f"R{j}_{right_child[j]}",
                    source=str(j), target=str(right_child[j]),
                    weight=1.0, directed=False,
                ))
        return GraphTraversalState(
            nodes=tuple(nodes_final),
            edges=tuple(edges_final),
            visited=frozenset(str(i) for i in range(n)),
            frontier=(),
            current=str(root),
            distances={},
            path=(),
            description=f"Cartesian tree built. Root={_ARRAY[root]} (min value)",
        )
