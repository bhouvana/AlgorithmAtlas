"""AVL Tree (Self-Balancing BST) plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)


class _N:
    """Minimal AVL tree node."""
    __slots__ = ("val", "left", "right", "h")

    def __init__(self, val: int):
        self.val = val
        self.left: _N | None = None
        self.right: _N | None = None
        self.h = 1


def _h(n: _N | None) -> int:
    return n.h if n else 0


def _bf(n: _N | None) -> int:
    return (_h(n.left) - _h(n.right)) if n else 0


def _upd(n: _N) -> None:
    n.h = 1 + max(_h(n.left), _h(n.right))


def _rr(z: _N) -> _N:
    y = z.left
    z.left = y.right
    y.right = z
    _upd(z)
    _upd(y)
    return y


def _lr(z: _N) -> _N:
    y = z.right
    z.right = y.left
    y.left = z
    _upd(z)
    _upd(y)
    return y


def _insert(root: _N | None, val: int):
    """Returns (new_root, rotation_description)."""
    if root is None:
        return _N(val), ""

    rot = ""
    if val < root.val:
        root.left, rot = _insert(root.left, val)
    elif val > root.val:
        root.right, rot = _insert(root.right, val)
    else:
        return root, ""

    _upd(root)
    bf = _bf(root)

    if bf > 1 and val < root.left.val:
        rot = f"LL-rotation at {root.val}"
        return _rr(root), rot
    if bf < -1 and val > root.right.val:
        rot = f"RR-rotation at {root.val}"
        return _lr(root), rot
    if bf > 1 and val > root.left.val:
        root.left = _lr(root.left)
        rot = f"LR-rotation at {root.val}"
        return _rr(root), rot
    if bf < -1 and val < root.right.val:
        root.right = _rr(root.right)
        rot = f"RL-rotation at {root.val}"
        return _lr(root), rot

    return root, rot


def _inorder(root: _N | None) -> list:
    if root is None:
        return []
    return _inorder(root.left) + [root] + _inorder(root.right)


def _tree_to_graph(root: _N | None, new_val: int | None, rotated: str):
    if root is None:
        return tuple(), tuple()

    ordered = _inorder(root)
    n = len(ordered)
    pos = {node.val: i for i, node in enumerate(ordered)}

    nodes: list = []
    edges: list = []

    def _build(node: _N, depth: int):
        x = (pos[node.val] + 0.5) / n
        y = depth * 0.18
        label = f"{node.val}(b{_bf(node)})"
        nodes.append(NodeState(node_id=str(node.val), label=label, x=x, y=y))
        if node.left:
            edges.append(EdgeState(
                edge_id=f"{node.val}L{node.left.val}",
                source=str(node.val),
                target=str(node.left.val),
                weight=float(_h(node.left)),
                directed=True,
            ))
            _build(node.left, depth + 1)
        if node.right:
            edges.append(EdgeState(
                edge_id=f"{node.val}R{node.right.val}",
                source=str(node.val),
                target=str(node.right.val),
                weight=float(_h(node.right)),
                directed=True,
            ))
            _build(node.right, depth + 1)

    _build(root, 0)
    return tuple(nodes), tuple(edges)


class AVLTreeSimulation(AlgorithmPlugin):
    """AVL self-balancing BST — insert with rotations."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="avl-tree",
            name="AVL Tree (Self-Balancing BST)",
            category="tree",
            visualization_type="TREE",
            description="Insert keys into an AVL tree, maintaining balance via rotations.",
            intuition=(
                "After each BST insert, fix any node with |balance| > 1 "
                "via LL/RR/LR/RL rotation. Height stays ≤ 1.44 log₂ n."
            ),
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(n)",
            tags=("tree", "avl", "balanced-bst", "rotation"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 7))
        vals = rng.sample(range(1, n * 6 + 1), n)
        # Build single-node tree with first value
        root = _N(vals[0])
        nodes, edges = _tree_to_graph(root, vals[0], "")
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=tuple(str(v) for v in vals[1:]),
            current=str(vals[0]),
            distances={"height": float(_h(root))},
            path=tuple(),
            description=f"AVL insert sequence: {vals}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        desc = initial_state.description
        vals_str = desc.split("[")[1].rstrip("]")
        vals = list(map(int, vals_str.split(", ")))

        root: _N | None = _N(vals[0])

        for val in vals[1:]:
            root, rot_desc = _insert(root, val)
            nodes, edges = _tree_to_graph(root, val, rot_desc)

            step_desc = (
                f"Inserted {val}" + (f", {rot_desc}" if rot_desc else "")
                + f". h={_h(root)}"
            )
            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset([str(val)]),
                frontier=tuple(),
                current=str(val),
                distances={"height": float(_h(root))},
                path=tuple(),
                description=step_desc,
            )

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(str(n.val) for n in _inorder(root)),
            frontier=tuple(),
            current=str(root.val),
            distances={"height": float(_h(root)), "size": float(len(vals))},
            path=tuple(),
            description=(
                f"AVL complete: {len(vals)} nodes, height={_h(root)}, "
                f"root={root.val}"
            ),
        )
