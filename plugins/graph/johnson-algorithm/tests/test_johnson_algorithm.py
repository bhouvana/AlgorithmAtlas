"""Tests for Johnson's Algorithm plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "johnson_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

JohnsonAlgorithmSimulation = mod.JohnsonAlgorithmSimulation
_NODES = mod._NODES
_EDGES = mod._EDGES
_bellman_ford = mod._bellman_ford
_dijkstra = mod._dijkstra
_N = mod._N


def _make_plugin(seed=0):
    plugin = JohnsonAlgorithmSimulation()

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
    p = JohnsonAlgorithmSimulation()
    assert p.metadata().slug == "johnson-algorithm"


def test_metadata_category():
    p = JohnsonAlgorithmSimulation()
    assert p.metadata().category == "graph"


def test_initial_node_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.nodes) == _N


def test_initial_edge_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.edges) == len(_EDGES)


def test_bellman_ford_computes_potentials():
    aug_edges = list(_EDGES) + [(_N, i, 0) for i in range(_N)]
    h = _bellman_ford(_N + 1, aug_edges, _N)
    assert len(h) == _N + 1
    # Virtual source potential = 0
    assert h[_N] == 0


def test_reweighted_edges_nonnegative():
    aug_edges = list(_EDGES) + [(_N, i, 0) for i in range(_N)]
    h = _bellman_ford(_N + 1, aug_edges, _N)
    for u, v, w in _EDGES:
        rw = w + h[u] - h[v]
        assert rw >= -1e-9, f"Negative reweighted edge ({u},{v}): {rw}"


def test_steps_produced():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    # Should have: initial + BF_done + reweight + N dijkstra steps + final = N + 4
    assert len(states) >= _N + 3


def test_final_description_all_pairs():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert "All-pairs" in final.description or "done" in final.description.lower()


def test_dijkstra_from_node():
    import heapq
    adj = {i: [] for i in range(_N)}
    for u, v, w in _EDGES:
        adj[u].append((v, float(w)))
    d = _dijkstra(_N, adj, 0)
    assert d[0] == 0
    assert len(d) == _N


def test_final_all_nodes_visited():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert len(final.visited) == _N
