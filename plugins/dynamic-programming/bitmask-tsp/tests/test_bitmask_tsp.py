"""Tests for Bitmask DP TSP."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("bitmask_tsp_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

BitmaskTSPSimulation = _mod.BitmaskTSPSimulation
_N = _mod._N
_DIST = _mod._DIST


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


def _brute_force_tsp():
    from itertools import permutations
    best = float('inf')
    for perm in permutations(range(1, _N)):
        path = [0] + list(perm) + [0]
        cost = sum(_DIST[path[i]][path[i+1]] for i in range(len(path)-1))
        best = min(best, cost)
    return best


# --- metadata ---

def test_metadata_slug():
    alg = BitmaskTSPSimulation()
    assert alg.metadata().slug == "bitmask-tsp"


def test_metadata_category():
    alg = BitmaskTSPSimulation()
    assert alg.metadata().category == "dynamic-programming"


def test_metadata_visualization():
    alg = BitmaskTSPSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- distance matrix ---

def test_dist_symmetric():
    for i in range(_N):
        for j in range(_N):
            assert _DIST[i][j] == _DIST[j][i]


def test_dist_diagonal_zero():
    for i in range(_N):
        assert _DIST[i][i] == 0


# --- initialize ---

def test_initialize_array_length():
    alg = BitmaskTSPSimulation()
    state = alg.initialize(_make_params())
    assert len(state.array) == _N


# --- steps ---

def test_steps_exist():
    alg = BitmaskTSPSimulation()
    params = _make_params()
    states, _ = _collect(alg, params)
    assert len(states) > 0


def test_final_optimal_cost():
    # Optimal TSP cost should match brute force
    expected = _brute_force_tsp()
    alg = BitmaskTSPSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    assert final.swaps == expected, f"Expected {expected}, got {final.swaps}"


def test_final_path_visits_all_cities():
    alg = BitmaskTSPSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    import re
    path_m = re.search(r"tour: ([\d → ]+) cost", final.description)
    if path_m:
        cities = [int(x) for x in path_m.group(1).split(" → ")]
        assert sorted(cities[:-1]) == list(range(_N))  # all cities, returns to 0


def test_final_path_starts_and_ends_at_0():
    alg = BitmaskTSPSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    import re
    path_m = re.search(r"tour: ([\d → ]+) cost", final.description)
    if path_m:
        cities = [int(x) for x in path_m.group(1).split(" → ")]
        assert cities[0] == 0
        assert cities[-1] == 0


def test_final_all_cities_in_sorted_indices():
    alg = BitmaskTSPSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    assert final.sorted_indices == frozenset(range(_N))


def test_step_costs_decrease_sometimes():
    # Some step costs should be less than max distance
    alg = BitmaskTSPSimulation()
    params = _make_params()
    states, _ = _collect(alg, params)
    costs = [s.swaps for s in states]
    assert min(costs) < max(costs)


def test_final_description_has_optimal():
    alg = BitmaskTSPSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    assert "Optimal" in final.description
    assert "cost=" in final.description
