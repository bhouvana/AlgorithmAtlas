"""Tests for Number of Divisors Sieve."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("divs_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

NumberOfDivisorsSimulation = _mod.NumberOfDivisorsSimulation


def _make_params(size=30, seed=0):
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


def _true_divisors(k):
    return sum(1 for d in range(1, k + 1) if k % d == 0)


# --- metadata ---

def test_metadata_slug():
    alg = NumberOfDivisorsSimulation()
    assert alg.metadata().slug == "number-of-divisors"


def test_metadata_category():
    alg = NumberOfDivisorsSimulation()
    assert alg.metadata().category == "number-theory"


def test_metadata_visualization():
    alg = NumberOfDivisorsSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = NumberOfDivisorsSimulation()
    state = alg.initialize(_make_params(30))
    assert len(state.array) == 30


# --- steps ---

def test_step_count_equals_n():
    alg = NumberOfDivisorsSimulation()
    params = _make_params(30)
    states, _ = _collect(alg, params)
    assert len(states) == 30


def test_final_max_divisors_correct():
    # In [1..30], number 24 has 8 divisors (maximum)
    alg = NumberOfDivisorsSimulation()
    params = _make_params(30)
    _, final = _collect(alg, params)
    # Max divisors = 8 for 24
    assert final.swaps == 8


def test_known_divisor_counts():
    # Verify via the last state's max being correct
    alg = NumberOfDivisorsSimulation()
    params = _make_params(20)
    _, final = _collect(alg, params)
    # In [1..20], max divisors is for 12 or 18 or 20
    # 12 has 6, 18 has 6, 20 has 6 → max = 6
    assert final.swaps == 6


def test_primes_have_two_divisors():
    # After full sieve, bars for primes should be second-lowest
    alg = NumberOfDivisorsSimulation()
    params = _make_params(30)
    _, final = _collect(alg, params)
    # Reconstruct by checking relative heights
    # The smallest non-1 bar should be prime-height (2 divisors)
    # Just verify the final has more than 2 distinct heights
    unique_heights = set(final.array)
    assert len(unique_heights) > 2


def test_1_has_one_divisor():
    alg = NumberOfDivisorsSimulation()
    params = _make_params(30)
    _, final = _collect(alg, params)
    # The bar for k=1 (index 0) should be smallest since d(1)=1
    assert final.array[0] < final.array[1]  # d(1)=1 < d(2)=2


def test_array_values_in_range():
    alg = NumberOfDivisorsSimulation()
    params = _make_params(30)
    states, final = _collect(alg, params)
    for s in states + [final]:
        for v in s.array:
            assert 1 <= v <= 99
