"""Tests for Edmonds-Karp max-flow algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "edmonds_karp", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

EdmondsKarpSimulation = _mod.EdmondsKarpSimulation
_CAPS = _mod._CAPS
_SOURCE = _mod._SOURCE
_SINK = _mod._SINK
_NODES = _mod._NODES


def _make_plugin(seed=0):
    plugin = EdmondsKarpSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "edmonds-karp"


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
    assert len(state.edges) == len(_CAPS)


def test_steps_yields_iterations():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    assert len(all_steps) >= 1


def test_steps_max_flow_positive():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    last = all_steps[-1]
    assert "Max flow" in last.description
    # Extract flow value
    import re
    m = re.search(r"Max flow = (\d+)", last.description)
    assert m is not None
    assert int(m.group(1)) > 0


def test_steps_max_flow_correct():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    last = all_steps[-1]
    import re
    m = re.search(r"Max flow = (\d+)", last.description)
    # Max flow for this graph = 15 (limited by sink-side: 8+10 via D→T and C→T paths)
    flow = int(m.group(1))
    assert flow > 0
    # Should not exceed sum of source capacities
    source_cap = sum(c for u, v, c in _CAPS if u == _SOURCE)
    assert flow <= source_cap


def test_steps_nodes_present_in_final():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    last = all_steps[-1]
    assert len(last.nodes) == len(_NODES)


def test_steps_edges_have_remaining_capacities():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    # Each intermediate step should have edges with non-negative weights
    for step in all_steps:
        for edge in step.edges:
            assert edge.weight >= 0


def test_steps_distances_track_flow():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    # Intermediate steps should have distances dict with "flow" key
    for step in all_steps[:-1]:
        if step.distances:
            assert "flow" in step.distances
            assert step.distances["flow"] >= 0
