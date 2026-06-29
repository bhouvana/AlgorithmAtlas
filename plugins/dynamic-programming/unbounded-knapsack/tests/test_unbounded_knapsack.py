"""Tests for Unbounded Knapsack."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("ubk_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

UnboundedKnapsackSimulation = _mod.UnboundedKnapsackSimulation
_ITEMS = _mod._ITEMS


def _make_params(size=15, seed=0):
    class P:
        inputs = {"size": size}
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


def _brute_force(W):
    dp = [0] * (W + 1)
    for w in range(1, W + 1):
        for wi, vi in _ITEMS:
            if wi <= w:
                dp[w] = max(dp[w], dp[w - wi] + vi)
    return dp[W]


# --- metadata ---

def test_metadata_slug():
    alg = UnboundedKnapsackSimulation()
    assert alg.metadata().slug == "unbounded-knapsack"


def test_metadata_category():
    alg = UnboundedKnapsackSimulation()
    assert alg.metadata().category == "dynamic-programming"


def test_metadata_visualization():
    alg = UnboundedKnapsackSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = UnboundedKnapsackSimulation()
    state = alg.initialize(_make_params(15))
    assert len(state.array) == 16  # W+1


# --- steps ---

def test_step_count_equals_num_items():
    alg = UnboundedKnapsackSimulation()
    params = _make_params(15)
    states, _ = _collect(alg, params)
    assert len(states) == len(_ITEMS)


def test_final_value_correct():
    alg = UnboundedKnapsackSimulation()
    for W in [10, 15, 20]:
        expected = _brute_force(W)
        params = _make_params(W)
        _, final = _collect(alg, params)
        assert final.swaps == expected, f"W={W}: expected {expected}, got {final.swaps}"


def test_values_non_decreasing():
    alg = UnboundedKnapsackSimulation()
    params = _make_params(15)
    states, _ = _collect(alg, params)
    prev_val = 0
    for s in states:
        assert s.swaps >= prev_val
        prev_val = s.swaps


def test_array_values_in_range():
    alg = UnboundedKnapsackSimulation()
    params = _make_params(15)
    states, final = _collect(alg, params)
    for s in states + [final]:
        for v in s.array:
            assert 1 <= v <= 99


def test_final_description():
    alg = UnboundedKnapsackSimulation()
    params = _make_params(15)
    _, final = _collect(alg, params)
    assert "Max value" in final.description


def test_larger_capacity_better_value():
    alg = UnboundedKnapsackSimulation()
    results = {}
    for W in [10, 15, 20]:
        params = _make_params(W)
        _, final = _collect(alg, params)
        results[W] = final.swaps
    assert results[20] >= results[15] >= results[10]
