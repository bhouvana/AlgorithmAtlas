"""Tests for Kosaraju SCC plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "kosaraju_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

KosarajuSCCSimulation = mod.KosarajuSCCSimulation
_NODES = mod._NODES
_EDGES = mod._EDGES


def _make_plugin(seed=0):
    plugin = KosarajuSCCSimulation()

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
    p = KosarajuSCCSimulation()
    assert p.metadata().slug == "kosaraju-scc"


def test_metadata_category():
    p = KosarajuSCCSimulation()
    assert p.metadata().category == "graph"


def test_initial_state_no_visited():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.visited) == 0


def test_initial_state_edge_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.edges) == len(_EDGES)


def test_final_state_all_visited():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert len(final.visited) == len(_NODES)


def test_final_state_mentions_sccs():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert "SCC" in final.description or "Found" in final.description


def test_correct_number_of_sccs():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    # Should find 4 SCCs: {A,B,C}, {D,E}, {F}, {G}
    assert "4" in final.description


def test_scc_abc_exists():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    desc = final.description
    # A, B, C should be in the same SCC
    assert "A" in desc and "B" in desc and "C" in desc


def test_steps_produced():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    assert len(states) > 3


def test_all_edges_directed():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    for edge in state.edges:
        assert edge.directed is True


def test_node_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.nodes) == len(_NODES)
