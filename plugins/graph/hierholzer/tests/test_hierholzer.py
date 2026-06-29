"""Tests for Hierholzer's Euler Circuit algorithm."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("hierholzer_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

HierholzerSimulation = _mod.HierholzerSimulation
_NODES_POS = _mod._NODES_POS
_EDGE_LIST = _mod._EDGE_LIST
_N = _mod._N


def _make_params(seed=0):
    class P:
        inputs = {}
        size = 16
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


# --- graph properties ---

def test_all_nodes_even_degree():
    from collections import Counter
    degree = Counter()
    for u, v in _EDGE_LIST:
        degree[u] += 1
        degree[v] += 1
    for node, deg in degree.items():
        assert deg % 2 == 0, f"Node {node} has odd degree {deg}"


def test_edge_count():
    assert len(_EDGE_LIST) == 12


def test_node_count():
    assert _N == 6


# --- metadata ---

def test_metadata_slug():
    alg = HierholzerSimulation()
    assert alg.metadata().slug == "hierholzer"


def test_metadata_category():
    alg = HierholzerSimulation()
    assert alg.metadata().category == "graph"


def test_metadata_visualization():
    alg = HierholzerSimulation()
    assert alg.metadata().visualization_type == "GRAPH"


# --- initialize ---

def test_initialize_node_count():
    alg = HierholzerSimulation()
    state = alg.initialize(_make_params())
    assert len(state.nodes) == _N


def test_initialize_edge_count():
    alg = HierholzerSimulation()
    state = alg.initialize(_make_params())
    assert len(state.edges) == len(_EDGE_LIST)


def test_initialize_current_is_zero():
    alg = HierholzerSimulation()
    state = alg.initialize(_make_params())
    assert state.current == "0"


def test_initialize_no_used_edges():
    alg = HierholzerSimulation()
    state = alg.initialize(_make_params())
    # All edge weights should be 0 (unused)
    assert all(e.weight == 0.0 for e in state.edges)


# --- steps ---

def test_circuit_length():
    # An Euler circuit visits every edge exactly once → length = E + 1
    alg = HierholzerSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    assert len(final.path) == len(_EDGE_LIST) + 1


def test_circuit_starts_and_ends_at_zero():
    alg = HierholzerSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    assert final.path[0] == "0"
    assert final.path[-1] == "0"


def test_all_edges_used_at_end():
    alg = HierholzerSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    # All edge weights should be 1.0 (used)
    assert all(e.weight == 1.0 for e in final.edges)


def test_circuit_uses_each_edge_exactly_once():
    alg = HierholzerSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    path = [int(n) for n in final.path]
    edge_uses = {}
    for a, b in zip(path, path[1:]):
        eid = f"{min(a,b)}-{max(a,b)}"
        edge_uses[eid] = edge_uses.get(eid, 0) + 1
    expected_eids = {f"{min(u,v)}-{max(u,v)}" for u, v in _EDGE_LIST}
    assert set(edge_uses.keys()) == expected_eids
    assert all(v == 1 for v in edge_uses.values())


def test_steps_yield_progress():
    alg = HierholzerSimulation()
    params = _make_params()
    states, _ = _collect(alg, params)
    assert len(states) > 0


def test_distances_track_circuit_length():
    alg = HierholzerSimulation()
    params = _make_params()
    states, final = _collect(alg, params)
    # circuit_len in distances should grow
    assert final.distances.get("circuit_len", 0) == len(_EDGE_LIST) + 1


def test_all_nodes_appear_in_circuit():
    alg = HierholzerSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    visited_nodes = set(final.path)
    expected = {str(i) for i in range(_N)}
    assert visited_nodes == expected


def test_final_description_contains_circuit():
    alg = HierholzerSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    assert "circuit" in final.description.lower() or "→" in final.description
