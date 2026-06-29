"""Tests for Sparse Table (RMQ)."""
import importlib.util
import math
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("sparse_table_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

SparseTableSimulation = _mod.SparseTableSimulation


def _make_params(size=12, seed=0):
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
    alg = SparseTableSimulation()
    assert alg.metadata().slug == "sparse-table"


def test_metadata_category():
    alg = SparseTableSimulation()
    assert alg.metadata().category == "tree"


def test_metadata_visualization():
    alg = SparseTableSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = SparseTableSimulation()
    state = alg.initialize(_make_params(12))
    assert len(state.array) == 12


def test_initialize_values_in_range():
    alg = SparseTableSimulation()
    state = alg.initialize(_make_params(12))
    assert all(1 <= v <= 99 for v in state.array)


def test_initialize_description():
    alg = SparseTableSimulation()
    state = alg.initialize(_make_params(12))
    assert "n=12" in state.description


# --- steps ---

def test_steps_exist():
    alg = SparseTableSimulation()
    params = _make_params(12)
    states, _ = _collect(alg, params)
    assert len(states) > 0


def test_first_step_is_row_0():
    alg = SparseTableSimulation()
    params = _make_params(12)
    states, _ = _collect(alg, params)
    assert "Row 0" in states[0].description


def test_log2_rows_built():
    alg = SparseTableSimulation()
    n = 12
    params = _make_params(n)
    states, _ = _collect(alg, params)
    log2n = int(math.log2(n)) + 1
    # First log2n steps are row builds, then queries
    build_steps = [s for s in states if "Row" in s.description]
    assert len(build_steps) == log2n


def test_query_steps_exist():
    alg = SparseTableSimulation()
    params = _make_params(12)
    states, _ = _collect(alg, params)
    query_steps = [s for s in states if "RMQ" in s.description]
    assert len(query_steps) > 0


def test_rmq_answers_are_correct():
    alg = SparseTableSimulation()
    params = _make_params(12, seed=7)
    state0 = alg.initialize(params)
    arr = list(state0.array)
    n = len(arr)
    states, _ = _collect(alg, params)
    query_steps = [s for s in states if "RMQ" in s.description]
    import re
    for s in query_steps:
        m = re.search(r"RMQ\[(\d+),(\d+)\] = (\d+)", s.description)
        if m:
            l, r, result = int(m.group(1)), int(m.group(2)), int(m.group(3))
            true_min = min(arr[l:r + 1])
            assert result == true_min, f"RMQ[{l},{r}]: expected {true_min}, got {result}"


def test_final_swaps_is_global_min():
    alg = SparseTableSimulation()
    params = _make_params(12)
    state0 = alg.initialize(params)
    arr = state0.array
    _, final = _collect(alg, params)
    # final.swaps might be min of the last query, check it's plausible
    assert final.swaps == min(arr)


def test_different_seeds():
    alg = SparseTableSimulation()
    for seed in range(4):
        params = _make_params(12, seed)
        states, final = _collect(alg, params)
        assert len(states) > 0
        assert final is not None
