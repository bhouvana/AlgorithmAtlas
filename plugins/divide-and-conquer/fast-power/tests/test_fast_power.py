"""Tests for Fast Power (Exponentiation by Squaring)."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("fast_power_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

FastPowerSimulation = _mod.FastPowerSimulation


def _make_params(exponent=27, seed=0):
    class P:
        inputs = {"exponent": exponent}
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
    alg = FastPowerSimulation()
    assert alg.metadata().slug == "fast-power"


def test_metadata_category():
    alg = FastPowerSimulation()
    assert alg.metadata().category == "divide-and-conquer"


def test_metadata_visualization():
    alg = FastPowerSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_bits_for_27():
    # 27 = 0b11011 → bits [1,1,0,1,1]
    alg = FastPowerSimulation()
    state = alg.initialize(_make_params(27))
    assert list(state.array) == [1, 1, 0, 1, 1]


def test_initialize_bits_for_8():
    # 8 = 0b1000 → bits [1,0,0,0]
    alg = FastPowerSimulation()
    state = alg.initialize(_make_params(8))
    assert list(state.array) == [1, 0, 0, 0]


def test_initialize_swaps_zero():
    alg = FastPowerSimulation()
    state = alg.initialize(_make_params(27))
    assert state.swaps == 0


def test_initialize_description_contains_exp():
    alg = FastPowerSimulation()
    state = alg.initialize(_make_params(27))
    assert "exp=27" in state.description


# --- steps ---

def test_step_count_equals_bit_length():
    alg = FastPowerSimulation()
    params = _make_params(27)
    states, final = _collect(alg, params)
    # 27 has 5 bits → 5 yielded states
    assert len(states) == 5


def test_final_result_correct_27():
    # 2^27 mod 1000 = 134217728 mod 1000 = 728
    alg = FastPowerSimulation()
    params = _make_params(27)
    _, final = _collect(alg, params)
    assert final.swaps == 728


def test_final_result_correct_8():
    # 2^8 mod 1000 = 256
    alg = FastPowerSimulation()
    params = _make_params(8)
    _, final = _collect(alg, params)
    assert final.swaps == 256


def test_final_result_correct_4():
    # 2^4 mod 1000 = 16
    alg = FastPowerSimulation()
    params = _make_params(4)
    _, final = _collect(alg, params)
    assert final.swaps == 16


def test_final_result_correct_63():
    # 2^63 mod 1000
    expected = pow(2, 63, 1000)
    alg = FastPowerSimulation()
    params = _make_params(63)
    _, final = _collect(alg, params)
    assert final.swaps == expected


def test_final_sorted_indices_all_bits():
    alg = FastPowerSimulation()
    params = _make_params(27)
    _, final = _collect(alg, params)
    assert final.sorted_indices == frozenset(range(5))


def test_step_sorted_indices_grow():
    alg = FastPowerSimulation()
    params = _make_params(27)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert i in s.sorted_indices


def test_each_step_comparing_is_current_bit():
    alg = FastPowerSimulation()
    params = _make_params(27)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert s.comparing == (i, i)


def test_final_swaps_in_description():
    alg = FastPowerSimulation()
    params = _make_params(27)
    _, final = _collect(alg, params)
    assert "728" in final.description


def test_different_exponents_give_different_results():
    alg = FastPowerSimulation()
    results = set()
    for exp in [4, 8, 16, 27, 32, 63]:
        _, final = _collect(alg, _make_params(exp))
        results.add(final.swaps)
    assert len(results) > 3


def test_step_count_for_power_of_2():
    # 32 = 0b100000 → 6 bits
    alg = FastPowerSimulation()
    params = _make_params(32)
    states, _ = _collect(alg, params)
    assert len(states) == 6


def test_last_swap_set_for_1_bits():
    # bit=1 → last_swap set; bit=0 → last_swap None
    alg = FastPowerSimulation()
    params = _make_params(8)  # bits = [1,0,0,0]
    states, _ = _collect(alg, params)
    assert states[0].last_swap is not None  # bit=1
    assert states[1].last_swap is None      # bit=0
    assert states[2].last_swap is None      # bit=0
    assert states[3].last_swap is None      # bit=0
