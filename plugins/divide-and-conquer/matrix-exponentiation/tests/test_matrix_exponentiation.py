"""Tests for Matrix Exponentiation (Fibonacci)."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("matexp_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

MatrixExponentiationSimulation = _mod.MatrixExponentiationSimulation
_fib_naive = _mod._fib_naive
_mat_mul = _mod._mat_mul
_fib_matrix = _mod._fib_matrix
_MOD = _mod._MOD


def _make_params(exponent=15, seed=0):
    class P:
        inputs = {"exponent": exponent}
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


# --- helpers ---

def test_fib_naive_base():
    assert _fib_naive(0) == 0
    assert _fib_naive(1) == 1
    assert _fib_naive(2) == 1


def test_fib_naive_known():
    assert _fib_naive(10) == 55
    assert _fib_naive(15) == 610


def test_mat_mul_identity():
    I = [[1, 0], [0, 1]]
    M = _fib_matrix()
    assert _mat_mul(I, M) == M
    assert _mat_mul(M, I) == M


# --- metadata ---

def test_metadata_slug():
    alg = MatrixExponentiationSimulation()
    assert alg.metadata().slug == "matrix-exponentiation"


def test_metadata_category():
    alg = MatrixExponentiationSimulation()
    assert alg.metadata().category == "divide-and-conquer"


def test_metadata_visualization():
    alg = MatrixExponentiationSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = MatrixExponentiationSimulation()
    state = alg.initialize(_make_params(15))
    assert len(state.array) == 4  # 2x2 matrix


def test_initialize_description():
    alg = MatrixExponentiationSimulation()
    state = alg.initialize(_make_params(15))
    assert "n=15" in state.description


# --- steps ---

def test_step_count_equals_bit_length():
    # n=15 = 0b1111 → 4 bits
    alg = MatrixExponentiationSimulation()
    params = _make_params(15)
    states, _ = _collect(alg, params)
    assert len(states) == 4


def test_final_fibonacci_correct():
    alg = MatrixExponentiationSimulation()
    for n in [5, 10, 15, 20, 30]:
        params = _make_params(n)
        _, final = _collect(alg, params)
        expected = _fib_naive(n) % 10000
        assert final.swaps == expected, f"F({n}): expected {expected}, got {final.swaps}"


def test_final_description_verified():
    alg = MatrixExponentiationSimulation()
    params = _make_params(15)
    _, final = _collect(alg, params)
    assert "verified" in final.description


def test_sorted_indices_grow():
    alg = MatrixExponentiationSimulation()
    params = _make_params(15)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert i in s.sorted_indices


def test_different_exponents():
    alg = MatrixExponentiationSimulation()
    results = {}
    for n in [5, 10, 15, 20]:
        params = _make_params(n)
        _, final = _collect(alg, params)
        results[n] = final.swaps
    # Fibonacci is strictly increasing, so values should differ
    assert len(set(results.values())) == len(results)
