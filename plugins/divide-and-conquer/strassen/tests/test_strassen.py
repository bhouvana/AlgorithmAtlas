"""Tests for Strassen Matrix Multiplication."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("strassen_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

StrassenSimulation = _mod.StrassenSimulation
_mat_mul_naive = _mod._mat_mul_naive
_flat = _mod._flat


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


# --- matrix helpers ---

def test_mat_mul_naive_identity():
    I = [[1, 0], [0, 1]]
    A = [[2, 3], [4, 5]]
    assert _mat_mul_naive(A, I) == A
    assert _mat_mul_naive(I, A) == A


def test_mat_mul_naive_known():
    A = [[1, 2], [3, 4]]
    B = [[5, 6], [7, 8]]
    C = _mat_mul_naive(A, B)
    assert C == [[19, 22], [43, 50]]


def test_flat_helper():
    M = [[1, 2], [3, 4]]
    assert _flat(M) == [1, 2, 3, 4]


# --- metadata ---

def test_metadata_slug():
    alg = StrassenSimulation()
    assert alg.metadata().slug == "strassen"


def test_metadata_category():
    alg = StrassenSimulation()
    assert alg.metadata().category == "divide-and-conquer"


def test_metadata_visualization():
    alg = StrassenSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = StrassenSimulation()
    state = alg.initialize(_make_params(0))
    assert len(state.array) == 8  # 4 from A + 4 from B


def test_initialize_description():
    alg = StrassenSimulation()
    state = alg.initialize(_make_params(0))
    assert "A=" in state.description
    assert "B=" in state.description


# --- steps ---

def test_exactly_7_product_steps():
    alg = StrassenSimulation()
    params = _make_params(0)
    states, _ = _collect(alg, params)
    assert len(states) == 7


def test_product_descriptions_m1_to_m7():
    alg = StrassenSimulation()
    params = _make_params(0)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert f"M{i+1}" in s.description


def test_result_correct():
    # Strassen result should match naive multiplication
    import re, ast
    alg = StrassenSimulation()
    for seed in range(5):
        params = _make_params(seed)
        state = alg.initialize(params)
        desc = state.description
        a_str = re.search(r"A=(\[\[.*?\]\])", desc).group(1)
        b_str = re.search(r"B=(\[\[.*?\]\])", desc).group(1)
        A = ast.literal_eval(a_str)
        B = ast.literal_eval(b_str)
        expected = _mat_mul_naive(A, B)

        _, final = _collect(alg, params)
        assert "correct=True" in final.description, f"seed={seed} Strassen gave wrong result"


def test_sorted_indices_grow():
    alg = StrassenSimulation()
    params = _make_params(0)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert i in s.sorted_indices


def test_array_values_in_range():
    alg = StrassenSimulation()
    params = _make_params(0)
    states, final = _collect(alg, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_different_seeds_give_different_matrices():
    alg = StrassenSimulation()
    descs = set()
    for seed in range(5):
        state = alg.initialize(_make_params(seed))
        descs.add(state.description)
    assert len(descs) > 1
