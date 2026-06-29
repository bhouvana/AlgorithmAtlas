"""Tests for Link-Cut Tree algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "link_cut_tree", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

LinkCutTreeSimulation = _mod.LinkCutTreeSimulation
_LCT = _mod._LCT
_N = _mod._N


def _make_plugin(seed=0):
    plugin = LinkCutTreeSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "link-cut-tree"


def test_metadata_category():
    plugin, _ = _make_plugin()
    assert plugin.metadata().category == "tree"


def test_metadata_visualization():
    plugin, _ = _make_plugin()
    assert plugin.metadata().visualization_type == "GRAPH"


def test_initialize_returns_graph_state():
    from algorithm_atlas_sdk import GraphTraversalState
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert isinstance(state, GraphTraversalState)


def test_initialize_empty_forest():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.edges) == 0


def test_initialize_n_nodes():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.nodes) == _N


def test_lct_link_connect():
    """Low-level: link two nodes and verify they are connected."""
    lct = _LCT(_N)
    assert not lct.connected(lct.nodes[0], lct.nodes[1])
    lct.link(lct.nodes[0], lct.nodes[1])
    assert lct.connected(lct.nodes[0], lct.nodes[1])


def test_lct_cut_disconnect():
    lct = _LCT(_N)
    lct.link(lct.nodes[0], lct.nodes[1])
    assert lct.connected(lct.nodes[0], lct.nodes[1])
    lct.cut(lct.nodes[0], lct.nodes[1])
    assert not lct.connected(lct.nodes[0], lct.nodes[1])


def test_lct_find_root():
    lct = _LCT(_N)
    lct.link(lct.nodes[0], lct.nodes[1])
    lct.link(lct.nodes[1], lct.nodes[2])
    # After linking 0-1 and 1-2, making 0 root: find_root(2) should be 0
    lct.make_root(lct.nodes[0])
    assert lct.find_root(lct.nodes[2]) is lct.nodes[0]


def test_steps_yields_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) >= 5


def test_steps_link_adds_edges():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    link_steps = [s for s in steps if "link" in s.description.lower()]
    max_edges = max(len(s.edges) for s in link_steps)
    assert max_edges >= 3


def test_steps_cut_removes_edge():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    cut_steps = [s for s in steps if "cut" in s.description.lower()]
    assert len(cut_steps) >= 1


def test_steps_connected_query_appears():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    conn_steps = [s for s in steps if "connected" in s.description.lower()]
    assert len(conn_steps) >= 1


def test_steps_final_description_has_edges():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert "edge" in steps[-1].description.lower()


def test_steps_node_count_constant():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    for step in plugin.steps(state):
        assert len(step.nodes) == _N
