"""Treap (Randomized BST) plugin for Algorithm Atlas."""
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


class _TNode:
    __slots__ = ("key", "pri", "left", "right")

    def __init__(self, key, pri):
        self.key = key
        self.pri = pri
        self.left = None
        self.right = None


def _rotate_right(y):
    x = y.left
    y.left = x.right
    x.right = y
    return x


def _rotate_left(x):
    y = x.right
    x.right = y.left
    y.left = x
    return y


def _insert(root, key, pri):
    if root is None:
        return _TNode(key, pri)
    if key < root.key:
        root.left = _insert(root.left, key, pri)
        if root.left.pri < root.pri:
            root = _rotate_right(root)
    elif key > root.key:
        root.right = _insert(root.right, key, pri)
        if root.right.pri < root.pri:
            root = _rotate_left(root)
    return root


def _inorder(node, result=None):
    if result is None:
        result = []
    if node:
        _inorder(node.left, result)
        result.append(node)
        _inorder(node.right, result)
    return result


def _tree_to_graph(root, new_key):
    nodes_list = _inorder(root)
    n = len(nodes_list)
    pos = {nd.key: i for i, nd in enumerate(nodes_list)}

    nodes = []
    edges = []

    def _layout(nd, depth=0, x_min=0.0, x_max=1.0):
        if nd is None:
            return
        x = (x_min + x_max) / 2
        y = 0.1 + depth * 0.15
        label = f"{nd.key}(p{nd.pri})"
        nodes.append(NodeState(node_id=str(nd.key), label=label, x=x, y=y))
        if nd.left:
            edges.append(EdgeState(
                edge_id=f"{nd.key}-{nd.left.key}",
                source=str(nd.key), target=str(nd.left.key),
                weight=0.0, directed=True,
            ))
            _layout(nd.left, depth + 1, x_min, x)
        if nd.right:
            edges.append(EdgeState(
                edge_id=f"{nd.key}-{nd.right.key}",
                source=str(nd.key), target=str(nd.right.key),
                weight=0.0, directed=True,
            ))
            _layout(nd.right, depth + 1, x, x_max)

    _layout(root)
    visited = frozenset(str(nd.key) for nd in nodes_list)
    return nodes, edges, visited


class TreapSimulation(AlgorithmPlugin):
    """Treap: randomized BST with heap-ordered priorities."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="treap",
            name="Treap (Randomized BST)",
            category="tree",
            visualization_type="GRAPH",
            description="Insert keys into a treap maintaining BST order and min-heap on random priorities.",
            intuition=(
                "Each key gets a random priority. "
                "BST property on keys + heap property on priorities. "
                "Rotations after insertion restore heap order. "
                "Expected O(log n) height due to random priorities."
            ),
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("tree", "treap", "randomized", "bst", "heap"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        import random
        n = int(params.inputs.get("size", 7))
        rng = random.Random(params.seed)
        keys = rng.sample(range(10, 90), n)
        pris = rng.sample(range(1, 99), n)
        keys_str = ",".join(map(str, keys))
        pris_str = ",".join(map(str, pris))
        empty_node = NodeState(node_id="empty", label="empty", x=0.5, y=0.5)
        return GraphTraversalState(
            nodes=(empty_node,),
            edges=(),
            visited=frozenset(),
            frontier=(),
            current=None,
            distances={},
            path=(),
            description=f"Treap n={n} keys={keys_str} pris={pris_str}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        import re
        desc = initial_state.description
        keys_str = re.search(r"keys=([0-9,]+)", desc).group(1)
        pris_str = re.search(r"pris=([0-9,]+)", desc).group(1)
        keys = list(map(int, keys_str.split(",")))
        pris = list(map(int, pris_str.split(",")))

        root = None

        for i, (key, pri) in enumerate(zip(keys, pris)):
            root = _insert(root, key, pri)
            nodes, edges, visited = _tree_to_graph(root, key)
            inorder_keys = [nd.key for nd in _inorder(root)]
            yield GraphTraversalState(
                nodes=tuple(nodes),
                edges=tuple(edges),
                visited=visited,
                frontier=(),
                current=str(key),
                distances={f"k{j}": float(k) for j, k in enumerate(inorder_keys)},
                path=tuple(str(k) for k in inorder_keys),
                description=(
                    f"Inserted key={key} priority={pri}. "
                    f"In-order: {inorder_keys}"
                ),
            )

        nodes, edges, visited = _tree_to_graph(root, -1)
        inorder_keys = [nd.key for nd in _inorder(root)]
        return GraphTraversalState(
            nodes=tuple(nodes),
            edges=tuple(edges),
            visited=visited,
            frontier=(),
            current=None,
            distances={f"k{j}": float(k) for j, k in enumerate(inorder_keys)},
            path=tuple(str(k) for k in inorder_keys),
            description=(
                f"Done: {len(keys)} keys in treap. "
                f"Sorted: {inorder_keys}"
            ),
        )
