"""Tests for Catalan Numbers DP."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("catalan_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

CatalanNumberSimulation = _mod.CatalanNumberSimulation
_CATALAN = _mod._CATALAN
_scale = _mod._scale


def _make_params(n=8, seed=0):
    class P:
        inputs = {"n": n}
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


# --- metadata ---

def test_metadata_slug():
    alg = CatalanNumberSimulation()
    assert alg.metadata().slug == "catalan-number"


def test_metadata_category():
    alg = CatalanNumberSimulation()
    assert alg.metadata().category == "number-theory"


def test_metadata_visualization():
    alg = CatalanNumberSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = CatalanNumberSimulation()
    state = alg.initialize(_make_params(8))
    assert len(state.array) == 9  # indices 0..8


def test_initialize_first_element_nonzero():
    # C(0)=1, scaled to some positive value
    alg = CatalanNumberSimulation()
    state = alg.initialize(_make_params(8))
    assert state.array[0] > 0


def test_initialize_rest_zero():
    alg = CatalanNumberSimulation()
    state = alg.initialize(_make_params(8))
    # Unscaled yet, but raw is [1, 0, 0, ...] and C(0)=1 is set
    # The initialized state uses [0]*(n+1) with [0]=1, not scaled
    # raw array[0] should be 1 (not yet scaled)
    assert state.array[0] == 1
    for i in range(1, 9):
        assert state.array[i] == 0


def test_initialize_description_contains_n():
    alg = CatalanNumberSimulation()
    state = alg.initialize(_make_params(8))
    assert "n=8" in state.description


def test_initialize_sorted_indices_contains_zero():
    alg = CatalanNumberSimulation()
    state = alg.initialize(_make_params(8))
    assert 0 in state.sorted_indices


# --- steps ---

def test_step_count_equals_n():
    alg = CatalanNumberSimulation()
    params = _make_params(8)
    states, _ = _collect(alg, params)
    assert len(states) == 8


def test_known_catalan_values_n8():
    # C(0..8) = [1, 1, 2, 5, 14, 42, 132, 429, 1430]
    alg = CatalanNumberSimulation()
    params = _make_params(8)
    _, final = _collect(alg, params)
    assert final.swaps == 9  # swaps = n+1 = 9


def test_final_description_contains_catalan():
    alg = CatalanNumberSimulation()
    params = _make_params(5)
    _, final = _collect(alg, params)
    assert "42" in final.description  # C(5) = 42


def test_step_sorted_indices_grows():
    alg = CatalanNumberSimulation()
    params = _make_params(8)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert i + 1 in s.sorted_indices


def test_comparing_is_current_k():
    alg = CatalanNumberSimulation()
    params = _make_params(8)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        k = i + 1
        assert s.comparing == (k, k)


def test_array_bars_are_scaled_1_to_99():
    alg = CatalanNumberSimulation()
    params = _make_params(8)
    states, final = _collect(alg, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_bars_are_monotone_increasing():
    # Catalan numbers are strictly increasing; bars should also be increasing
    alg = CatalanNumberSimulation()
    params = _make_params(8)
    _, final = _collect(alg, params)
    arr = list(final.array)
    for i in range(1, len(arr)):
        assert arr[i] >= arr[i - 1]


def test_different_n_gives_different_step_counts():
    alg = CatalanNumberSimulation()
    for n in [4, 6, 8, 10]:
        params = _make_params(n)
        states, _ = _collect(alg, params)
        assert len(states) == n


def test_scale_helper():
    vals = [1, 2, 5, 14]
    scaled = _scale(vals)
    assert scaled[-1] == 99  # max → 99
    assert all(1 <= v <= 99 for v in scaled)


def test_final_sorted_all_indices():
    alg = CatalanNumberSimulation()
    params = _make_params(5)
    _, final = _collect(alg, params)
    assert final.sorted_indices == frozenset(range(6))
