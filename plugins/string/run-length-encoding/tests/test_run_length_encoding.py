"""Tests for Run-Length Encoding."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("rle_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

RunLengthEncodingSimulation = _mod.RunLengthEncodingSimulation
_EXAMPLES = _mod._EXAMPLES
_str_to_array = _mod._str_to_array


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


def _count_runs(s):
    if not s:
        return 0
    runs = 1
    for i in range(1, len(s)):
        if s[i] != s[i - 1]:
            runs += 1
    return runs


# --- metadata ---

def test_metadata_slug():
    alg = RunLengthEncodingSimulation()
    assert alg.metadata().slug == "run-length-encoding"


def test_metadata_category():
    alg = RunLengthEncodingSimulation()
    assert alg.metadata().category == "string"


def test_metadata_visualization():
    alg = RunLengthEncodingSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_matches_example_0():
    alg = RunLengthEncodingSimulation()
    state = alg.initialize(_make_params(0))
    expected = _str_to_array(_EXAMPLES[0])
    assert state.array == expected


def test_initialize_description_contains_input():
    alg = RunLengthEncodingSimulation()
    state = alg.initialize(_make_params(0))
    assert "input='" in state.description
    assert _EXAMPLES[0] in state.description


def test_initialize_sorted_indices_empty():
    alg = RunLengthEncodingSimulation()
    state = alg.initialize(_make_params(0))
    assert state.sorted_indices == frozenset()


# --- steps ---

def test_step_count_equals_run_count():
    alg = RunLengthEncodingSimulation()
    for seed in range(len(_EXAMPLES)):
        s = _EXAMPLES[seed % len(_EXAMPLES)]
        params = _make_params(seed)
        states, _ = _collect(alg, params)
        assert len(states) == _count_runs(s), f"failed for '{s}'"


def test_swaps_track_run_index():
    alg = RunLengthEncodingSimulation()
    params = _make_params(0)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert s.swaps == i + 1


def test_comparing_spans_current_run():
    # AABBBCCDDDDEE: runs A(2), B(3), C(2), D(4), E(2)
    alg = RunLengthEncodingSimulation()
    params = _make_params(0)  # AABBBCCDDDDEE
    states, _ = _collect(alg, params)
    run_start, run_end = states[0].comparing
    assert run_end - run_start + 1 == 2  # "AA"


def test_run_start_in_sorted_indices():
    alg = RunLengthEncodingSimulation()
    params = _make_params(0)
    states, _ = _collect(alg, params)
    # Each run_start should accumulate in sorted_indices
    run_starts = set()
    for s in states:
        if s.sorted_indices:
            for idx in s.sorted_indices:
                run_starts.add(idx)
    assert 0 in run_starts  # first run starts at 0


def test_final_description_contains_encoded():
    alg = RunLengthEncodingSimulation()
    params = _make_params(0)  # AABBBCCDDDDEE
    _, final = _collect(alg, params)
    # Encoded should be "2A3B2C4D2E"
    assert "2A" in final.description or "2A" in final.description


def test_final_swaps_equals_run_count():
    alg = RunLengthEncodingSimulation()
    for seed in range(len(_EXAMPLES)):
        s = _EXAMPLES[seed % len(_EXAMPLES)]
        params = _make_params(seed)
        _, final = _collect(alg, params)
        assert final.swaps == _count_runs(s)


def test_all_seeds_run_without_error():
    alg = RunLengthEncodingSimulation()
    for seed in range(len(_EXAMPLES)):
        params = _make_params(seed)
        states, final = _collect(alg, params)
        assert len(states) > 0
        assert final is not None


def test_str_to_array_basic():
    arr = _str_to_array("ABC")
    assert arr[0] < arr[1] < arr[2]  # A < B < C in height


def test_single_char_run_has_no_last_swap():
    # Find an example with a single-char run or check first run of AABBBCCDDDDEE
    # 'C' in seed 0 = "AABBBCCDDDDEE" → 'C' run has len 2, not 1
    # seed=3: "AABBCCDDEE" → all runs of length 2
    alg = RunLengthEncodingSimulation()
    # Use seed 2: XYYYYZZZZ → X run length=1
    params = _make_params(2)
    states, _ = _collect(alg, params)
    # First run is 'X' with count=1
    assert states[0].last_swap is None  # count=1, no last_swap


def test_multi_char_run_has_last_swap():
    # seed=2: XYYYYZZZZ → Y run length=4
    alg = RunLengthEncodingSimulation()
    params = _make_params(2)
    states, _ = _collect(alg, params)
    # Second run is 'Y' with count=4
    assert states[1].last_swap is not None
