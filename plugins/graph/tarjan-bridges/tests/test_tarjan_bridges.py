"""Tests for Tarjan's Bridge Finding algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "tarjan_bridges", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TarjanBridgesSimulation = _mod.TarjanBridgesSimulation
_NODES = _mod._NODES
_EDGES = _mod._EDGES
_BRIDGES = _mod._BRIDGES
_find_bridges = _mod._find_bridges


def _make_plugin(seed=0):
    plugin = TarjanBridgesSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "tarjan-bridges"


def test_metadata_category():
    plugin, _ = _make_plugin()
    assert plugin.metadata().category == "graph"


def test_metadata_visualization():
    plugin, _ = _make_plugin()
    assert plugin.metadata().visualization_type == "GRAPH"


def test_find_bridges_correct_count():
    n = len(_NODES)
    adj = [[] for _ in range(n)]
    for u, v in _EDGES:
        adj[u].append(v)
        adj[v].append(u)
    bridges, disc, low = _find_bridges(n, adj)
    assert len(bridges) == 3


def test_find_bridges_correct_edges():
    n = len(_NODES)
    adj = [[] for _ in range(n)]
    for u, v in _EDGES:
        adj[u].append(v)
        adj[v].append(u)
    bridges, _, _ = _find_bridges(n, adj)
    assert bridges == _BRIDGES


def test_find_bridges_non_bridges():
    n = len(_NODES)
    adj = [[] for _ in range(n)]
    for u, v in _EDGES:
        adj[u].append(v)
        adj[v].append(u)
    bridges, _, _ = _find_bridges(n, adj)
    # Cycle edges should NOT be bridges
    assert frozenset({2, 3}) not in bridges
    assert frozenset({3, 4}) not in bridges
    assert frozenset({2, 4}) not in bridges
    assert frozenset({5, 6}) not in bridges
    assert frozenset({6, 7}) not in bridges
    assert frozenset({5, 7}) not in bridges


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
    assert len(state.edges) == len(_EDGES)


def test_steps_visits_all_nodes():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    assert len(all_steps) == len(_NODES)


def test_steps_final_has_bridges_description():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    last = all_steps[-1]
    assert "bridge" in last.description.lower()


def test_steps_bridge_edges_marked():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    # In the final step, bridge edges should have weight 3.0
    last = all_steps[-1]
    bridge_weights = []
    non_bridge_weights = []
    for edge in last.edges:
        u, v = int(edge.source), int(edge.target)
        if frozenset({u, v}) in _BRIDGES:
            bridge_weights.append(edge.weight)
        else:
            non_bridge_weights.append(edge.weight)
    assert all(w == 3.0 for w in bridge_weights), f"Expected 3.0 for bridges, got {bridge_weights}"
    assert all(w == 1.0 for w in non_bridge_weights), f"Expected 1.0 for non-bridges, got {non_bridge_weights}"
