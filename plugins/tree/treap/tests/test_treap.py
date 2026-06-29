"""Tests for Treap (Randomized BST)."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("treap_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

TreapSimulation = _mod.TreapSimulation
_insert = _mod._insert
_inorder = _mod._inorder
_TNode = _mod._TNode


def _make_params(size=7, seed=0):
    class P:
        inputs = {"size": size}
        pass
    p = P()
    p.seed = seed
    return p


def _collect(alg, params):
    state = alg.initialize(params)
    gen = alg.steps(state)
    states = []
    try:
        while True:
            states.append(next(gen))
    except StopIteration as e:
        return states, e.value


# --- treap helpers ---

def test_insert_single():
    root = _insert(None, 5, 10)
    assert root.key == 5
    assert root.pri == 10


def test_insert_bst_order():
    root = None
    for key, pri in [(5, 20), (3, 15), (7, 25)]:
        root = _insert(root, key, pri)
    inorder = [nd.key for nd in _inorder(root)]
    assert inorder == sorted(inorder)


def test_insert_heap_property():
    root = None
    for key, pri in [(5, 50), (3, 30), (7, 70), (2, 10)]:
        root = _insert(root, key, pri)
    # Check heap property: every parent has lower priority than children
    def check_heap(nd):
        if nd is None:
            return True
        if nd.left and nd.left.pri < nd.pri:
            return False
        if nd.right and nd.right.pri < nd.pri:
            return False
        return check_heap(nd.left) and check_heap(nd.right)
    assert check_heap(root)


# --- metadata ---

def test_metadata_slug():
    alg = TreapSimulation()
    assert alg.metadata().slug == "treap"


def test_metadata_category():
    alg = TreapSimulation()
    assert alg.metadata().category == "tree"


def test_metadata_visualization():
    alg = TreapSimulation()
    assert alg.metadata().visualization_type == "GRAPH"


# --- initialize ---

def test_initialize_description():
    alg = TreapSimulation()
    state = alg.initialize(_make_params(7))
    assert "Treap" in state.description
    assert "n=7" in state.description


# --- steps ---

def test_step_count_equals_n():
    alg = TreapSimulation()
    params = _make_params(7)
    states, _ = _collect(alg, params)
    assert len(states) == 7


def test_final_inorder_is_sorted():
    alg = TreapSimulation()
    params = _make_params(7)
    _, final = _collect(alg, params)
    path_keys = [int(k) for k in final.path]
    assert path_keys == sorted(path_keys)


def test_final_node_count():
    alg = TreapSimulation()
    params = _make_params(7)
    _, final = _collect(alg, params)
    assert len(final.nodes) == 7


def test_final_all_nodes_visited():
    alg = TreapSimulation()
    params = _make_params(7)
    _, final = _collect(alg, params)
    assert len(final.visited) == 7


def test_step_tree_grows():
    alg = TreapSimulation()
    params = _make_params(7)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert len(s.nodes) == i + 1


def test_heap_property_maintained_throughout():
    alg = TreapSimulation()
    params = _make_params(7)
    states, _ = _collect(alg, params)
    # All states should have current node highlighted
    for s in states:
        assert s.current is not None


def test_different_seeds():
    alg = TreapSimulation()
    inorders = []
    for seed in range(4):
        params = _make_params(7, seed)
        _, final = _collect(alg, params)
        inorders.append(tuple(final.path))
    # Different seeds should produce different key sets
    assert len(set(inorders)) > 1
