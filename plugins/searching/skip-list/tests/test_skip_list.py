"""Tests for Skip List."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("skip_list_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

SkipListSimulation = _mod.SkipListSimulation
_MAX_LEVEL = _mod._MAX_LEVEL


def _make_params(size=10, seed=0):
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
    alg = SkipListSimulation()
    assert alg.metadata().slug == "skip-list"


def test_metadata_category():
    alg = SkipListSimulation()
    assert alg.metadata().category == "searching"


def test_metadata_visualization():
    alg = SkipListSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_is_sorted():
    alg = SkipListSimulation()
    state = alg.initialize(_make_params(10))
    arr = list(state.array)
    assert arr == sorted(arr)


def test_initialize_array_length():
    alg = SkipListSimulation()
    state = alg.initialize(_make_params(10))
    assert len(state.array) == 10


def test_initialize_description():
    alg = SkipListSimulation()
    state = alg.initialize(_make_params(10))
    assert "n=10" in state.description
    assert "values=" in state.description


# --- steps ---

def test_steps_exist():
    alg = SkipListSimulation()
    params = _make_params(10)
    states, _ = _collect(alg, params)
    assert len(states) > 0


def test_insert_steps():
    alg = SkipListSimulation()
    params = _make_params(10)
    states, _ = _collect(alg, params)
    insert_steps = [s for s in states if "Insert" in s.description]
    assert len(insert_steps) == 10


def test_levels_in_range():
    alg = SkipListSimulation()
    params = _make_params(10)
    states, _ = _collect(alg, params)
    insert_steps = [s for s in states if "Insert" in s.description]
    for s in insert_steps:
        assert 1 <= s.swaps <= _MAX_LEVEL


def test_final_all_indices_sorted():
    alg = SkipListSimulation()
    params = _make_params(10)
    _, final = _collect(alg, params)
    assert final.sorted_indices == frozenset(range(10))


def test_search_step_exists():
    alg = SkipListSimulation()
    params = _make_params(10)
    states, _ = _collect(alg, params)
    search_steps = [s for s in states if "Search" in s.description or "Found" in s.description]
    assert len(search_steps) > 0


def test_array_values_in_range():
    alg = SkipListSimulation()
    params = _make_params(10)
    states, final = _collect(alg, params)
    for s in states + [final]:
        for v in s.array:
            assert 1 <= v <= 99


def test_different_seeds():
    alg = SkipListSimulation()
    arrays = set()
    for seed in range(4):
        params = _make_params(10, seed)
        state = alg.initialize(params)
        arrays.add(state.array)
    assert len(arrays) > 1
