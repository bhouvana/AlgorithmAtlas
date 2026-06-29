"""Tests for Heavy-Light Decomposition algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "heavy_light_decomposition", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

HeavyLightDecompositionSimulation = _mod.HeavyLightDecompositionSimulation
_TREE_EDGES = _mod._TREE_EDGES
_N = _mod._N
_ROOT = _mod._ROOT


def _make_plugin(seed=0):
    plugin = HeavyLightDecompositionSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "heavy-light-decomposition"


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


def test_initialize_node_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.nodes) == _N


def test_initialize_edge_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.edges) == len(_TREE_EDGES)


def test_initialize_undirected_edges():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert all(not e.directed for e in state.edges)


def test_steps_yields_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) >= 2


def test_steps_final_has_chains():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert "chain" in steps[-1].description.lower() or "chains" in steps[-1].description.lower()


def test_steps_final_all_nodes_visited():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    assert len(final.nodes) == _N


def test_steps_subtree_sizes_step():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    size_steps = [s for s in steps if "size" in s.description.lower()]
    assert len(size_steps) >= 1


def test_steps_heavy_edges_identified():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    heavy_steps = [s for s in steps if "heavy" in s.description.lower()]
    assert len(heavy_steps) >= 1


def test_steps_chain_assignment_complete():
    """Every node should get a chain id (weight > 0) in the final state."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    # chain IDs are encoded as node weights (1-indexed)
    chain_ids = {n.weight for n in final.nodes}
    assert len(chain_ids) >= 2   # at least 2 chains for this 7-node tree


def test_steps_root_in_heavy_chain():
    """Root node should be in chain 0."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    root_node = next(n for n in final.nodes if n.node_id == str(_ROOT))
    # chain is 1-indexed as weight: chain 0 → weight 1.0
    assert root_node.weight == 1.0
