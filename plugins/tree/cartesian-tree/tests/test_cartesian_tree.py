"""Tests for Cartesian Tree plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "cartesian_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CartesianTreeSimulation = mod.CartesianTreeSimulation
_ARRAY = mod._ARRAY


def _build_cartesian(arr):
    """Reference: build cartesian tree, return parent array and root."""
    n = len(arr)
    parent = [None] * n
    left_child = [None] * n
    right_child = [None] * n
    stack = []
    for i in range(n):
        last_popped = None
        while stack and arr[stack[-1]] > arr[i]:
            last_popped = stack.pop()
        if last_popped is not None:
            left_child[i] = last_popped
            parent[last_popped] = i
        if stack:
            right_child[stack[-1]] = i
            parent[i] = stack[-1]
        stack.append(i)
    root = next(i for i in range(n) if parent[i] is None)
    return parent, left_child, right_child, root


def _make_plugin(seed=0):
    plugin = CartesianTreeSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def _collect(plugin, params):
    state = plugin.initialize(params)
    states = [state]
    gen = plugin.steps(state)
    try:
        while True:
            states.append(next(gen))
    except StopIteration as e:
        states.append(e.value)
    return states


def test_metadata_slug():
    p = CartesianTreeSimulation()
    assert p.metadata().slug == "cartesian-tree"


def test_metadata_category():
    p = CartesianTreeSimulation()
    assert p.metadata().category == "tree"


def test_initial_node_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.nodes) == len(_ARRAY)


def test_initial_no_edges():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.edges) == 0


def test_root_is_minimum():
    parent, lc, rc, root = _build_cartesian(_ARRAY)
    assert _ARRAY[root] == min(_ARRAY)


def test_n_minus_1_edges_in_final():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    # A tree with n nodes has n-1 edges
    assert len(final.edges) == len(_ARRAY) - 1


def test_min_heap_property():
    parent, lc, rc, root = _build_cartesian(_ARRAY)
    n = len(_ARRAY)
    for i in range(n):
        if lc[i] is not None:
            assert _ARRAY[i] <= _ARRAY[lc[i]]
        if rc[i] is not None:
            assert _ARRAY[i] <= _ARRAY[rc[i]]


def test_bst_index_property():
    """In-order traversal of cartesian tree should give sorted indices."""
    parent, lc, rc, root = _build_cartesian(_ARRAY)

    def inorder(node):
        if node is None:
            return []
        return inorder(lc[node]) + [node] + inorder(rc[node])

    result = inorder(root)
    assert result == list(range(len(_ARRAY)))


def test_final_state_all_visited():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert len(final.visited) == len(_ARRAY)


def test_step_count():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    # initial + n steps + final = n + 2
    assert len(states) == len(_ARRAY) + 2


def test_final_description_mentions_root():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert "Root" in final.description or "root" in final.description
    assert str(min(_ARRAY)) in final.description


def test_all_nodes_have_unique_ids():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    ids = [n.node_id for n in final.nodes]
    assert len(ids) == len(set(ids))
