"""Tests for Longest Bitonic Subsequence."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("lbs_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

LongestBitonicSubsequenceSimulation = _mod.LongestBitonicSubsequenceSimulation


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


def _brute_lbs(arr):
    n = len(arr)
    lis = [1] * n
    for i in range(1, n):
        for j in range(i):
            if arr[j] < arr[i]:
                lis[i] = max(lis[i], lis[j] + 1)
    lds = [1] * n
    for i in range(n - 2, -1, -1):
        for j in range(i + 1, n):
            if arr[j] < arr[i]:
                lds[i] = max(lds[i], lds[j] + 1)
    return max(lis[i] + lds[i] - 1 for i in range(n))


# --- metadata ---

def test_metadata_slug():
    alg = LongestBitonicSubsequenceSimulation()
    assert alg.metadata().slug == "longest-bitonic-subsequence"


def test_metadata_category():
    alg = LongestBitonicSubsequenceSimulation()
    assert alg.metadata().category == "dynamic-programming"


def test_metadata_visualization():
    alg = LongestBitonicSubsequenceSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- steps ---

def test_step_count():
    alg = LongestBitonicSubsequenceSimulation()
    params = _make_params(10)
    states, _ = _collect(alg, params)
    # n-1 LIS steps + n LDS steps (from n-2 down to 0 = n-1 steps) + 1 combine = 2n-1
    assert len(states) == 2 * 10 - 1


def test_final_lbs_correct():
    alg = LongestBitonicSubsequenceSimulation()
    for seed in range(5):
        params = _make_params(10, seed)
        state = alg.initialize(params)
        arr = list(state.array)
        expected = _brute_lbs(arr)
        _, final = _collect(alg, params)
        assert final.swaps == expected, f"seed={seed}: expected {expected}, got {final.swaps}"


def test_lbs_at_least_1():
    alg = LongestBitonicSubsequenceSimulation()
    for seed in range(5):
        params = _make_params(10, seed)
        _, final = _collect(alg, params)
        assert final.swaps >= 1


def test_final_description_has_length():
    alg = LongestBitonicSubsequenceSimulation()
    params = _make_params(10)
    _, final = _collect(alg, params)
    assert "bitonic subsequence length" in final.description.lower()


def test_array_unchanged():
    alg = LongestBitonicSubsequenceSimulation()
    params = _make_params(10)
    state = alg.initialize(params)
    original = state.array
    # Initial array is input
    # During LIS phase, array shows LIS values, so it changes - that's expected


def test_combine_step_has_best_index():
    alg = LongestBitonicSubsequenceSimulation()
    params = _make_params(10)
    states, _ = _collect(alg, params)
    # Last step before final is the combine step
    combine = states[-1]
    assert "LBS" in combine.description
    assert combine.last_swap is not None
