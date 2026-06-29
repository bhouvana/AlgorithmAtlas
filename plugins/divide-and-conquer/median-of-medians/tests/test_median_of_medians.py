"""Tests for Median of Medians."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("mom_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

MedianOfMediansSimulation = _mod.MedianOfMediansSimulation
_GROUP = _mod._GROUP


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


# --- metadata ---

def test_metadata_slug():
    alg = MedianOfMediansSimulation()
    assert alg.metadata().slug == "median-of-medians"


def test_metadata_category():
    alg = MedianOfMediansSimulation()
    assert alg.metadata().category == "divide-and-conquer"


def test_metadata_visualization():
    alg = MedianOfMediansSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = MedianOfMediansSimulation()
    state = alg.initialize(_make_params(15))
    assert len(state.array) == 15


def test_initialize_distinct_values():
    alg = MedianOfMediansSimulation()
    state = alg.initialize(_make_params(15))
    assert len(set(state.array)) == 15  # sample without replacement


def test_initialize_description():
    alg = MedianOfMediansSimulation()
    state = alg.initialize(_make_params(15))
    assert "n=15" in state.description


# --- steps ---

def test_steps_exist():
    alg = MedianOfMediansSimulation()
    params = _make_params(15)
    states, _ = _collect(alg, params)
    assert len(states) > 0


def test_final_finds_median():
    # For n elements, median = element at index n//2 in sorted order
    alg = MedianOfMediansSimulation()
    for seed in range(5):
        params = _make_params(15, seed)
        state = alg.initialize(params)
        arr = sorted(state.array)
        _, final = _collect(alg, params)
        found_val = final.swaps
        true_median = arr[15 // 2]
        assert found_val == true_median, f"seed={seed}: found {found_val}, expected {true_median}"


def test_final_sorted_indices_has_result():
    alg = MedianOfMediansSimulation()
    params = _make_params(15)
    _, final = _collect(alg, params)
    assert len(final.sorted_indices) >= 1


def test_array_unchanged():
    alg = MedianOfMediansSimulation()
    params = _make_params(15)
    state = alg.initialize(params)
    original = state.array
    states, final = _collect(alg, params)
    for s in states + [final]:
        assert s.array == original


def test_different_sizes():
    alg = MedianOfMediansSimulation()
    for n in [10, 15, 20, 25]:
        params = _make_params(n)
        state = alg.initialize(params)
        arr = sorted(state.array)
        _, final = _collect(alg, params)
        assert final.swaps == arr[n // 2], f"n={n} failed"


def test_group_size():
    assert _GROUP == 5


def test_final_description_has_median():
    alg = MedianOfMediansSimulation()
    params = _make_params(15)
    _, final = _collect(alg, params)
    assert "Median" in final.description or "median" in final.description
