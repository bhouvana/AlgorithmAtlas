"""Tests for Min-Cost Max-Flow algorithm."""
import importlib.util
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "min_cost_max_flow", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

MinCostMaxFlowSimulation = _mod.MinCostMaxFlowSimulation
_EDGE_DATA = _mod._EDGE_DATA
_SOURCE = _mod._SOURCE
_SINK = _mod._SINK
_NODES = _mod._NODES


def _make_plugin(seed=0):
    plugin = MinCostMaxFlowSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "min-cost-max-flow"


def test_metadata_category():
    plugin, _ = _make_plugin()
    assert plugin.metadata().category == "graph"


def test_metadata_visualization():
    plugin, _ = _make_plugin()
    assert plugin.metadata().visualization_type == "GRAPH"


def test_initialize_returns_graph_state():
    from algorithm_atlas_sdk import GraphTraversalState
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert isinstance(state, GraphTraversalState)


def test_initialize_node_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.nodes) == len(_NODES)


def test_initialize_edge_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.edges) == len(_EDGE_DATA)


def test_initialize_edges_directed():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert all(e.directed for e in state.edges)


def test_steps_yields_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) >= 1


def test_steps_final_has_done():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert "Done" in steps[-1].description


def test_steps_max_flow_positive():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    last = steps[-1]
    m = re.search(r"max flow=(\d+)", last.description)
    assert m is not None
    assert int(m.group(1)) > 0


def test_steps_min_cost_positive():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    last = steps[-1]
    m = re.search(r"min cost=(\d+)", last.description)
    assert m is not None
    assert int(m.group(1)) > 0


def test_steps_total_flow_bounded_by_source():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    last = steps[-1]
    m = re.search(r"max flow=(\d+)", last.description)
    src_cap = sum(c for u, v, c, _ in _EDGE_DATA if u == _SOURCE)
    assert int(m.group(1)) <= src_cap


def test_steps_edges_non_negative_capacity():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    for step in plugin.steps(state):
        for edge in step.edges:
            assert edge.weight >= 0


def test_steps_distances_have_flow_and_cost():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    for step in steps[:-1]:
        if step.distances:
            assert "flow" in step.distances
            assert "cost" in step.distances


def test_steps_node_count_constant():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    for step in plugin.steps(state):
        assert len(step.nodes) == len(_NODES)
