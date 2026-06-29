"""Tests for String Hashing (Polynomial Rolling Hash)."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("strhash_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

StringHashingSimulation = _mod.StringHashingSimulation
_EXAMPLES = _mod._EXAMPLES
_BASE = _mod._BASE
_MOD = _mod._MOD
_char_val = _mod._char_val


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


# --- helper ---

def test_char_val_a():
    assert _char_val('a') == 1


def test_char_val_z():
    assert _char_val('z') == 26


def test_char_val_case_insensitive():
    assert _char_val('A') == _char_val('a')


# --- metadata ---

def test_metadata_slug():
    alg = StringHashingSimulation()
    assert alg.metadata().slug == "string-hashing"


def test_metadata_category():
    alg = StringHashingSimulation()
    assert alg.metadata().category == "string"


def test_metadata_visualization():
    alg = StringHashingSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = StringHashingSimulation()
    state = alg.initialize(_make_params(0))
    s = _EXAMPLES[0]
    assert len(state.array) == len(s)


def test_initialize_description_has_input():
    alg = StringHashingSimulation()
    state = alg.initialize(_make_params(0))
    assert "input='" in state.description


# --- steps ---

def test_step_count_equals_string_length():
    alg = StringHashingSimulation()
    for seed in range(len(_EXAMPLES)):
        s = _EXAMPLES[seed % len(_EXAMPLES)]
        params = _make_params(seed)
        states, _ = _collect(alg, params)
        assert len(states) == len(s)


def test_sorted_indices_grow():
    alg = StringHashingSimulation()
    params = _make_params(0)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert i in s.sorted_indices


def test_comparing_is_current_index():
    alg = StringHashingSimulation()
    params = _make_params(0)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert s.comparing == (i, i)


def test_final_all_indices_sorted():
    alg = StringHashingSimulation()
    s = _EXAMPLES[0]
    params = _make_params(0)
    _, final = _collect(alg, params)
    assert final.sorted_indices == frozenset(range(len(s)))


def test_hash_values_differ_per_char():
    # Each character should contribute differently to the hash
    alg = StringHashingSimulation()
    params = _make_params(2)  # "algorithm"
    states, _ = _collect(alg, params)
    swaps_set = {s.swaps for s in states}
    assert len(swaps_set) > 1


def test_array_values_in_range():
    alg = StringHashingSimulation()
    params = _make_params(0)
    states, final = _collect(alg, params)
    for s in states + [final]:
        for v in s.array:
            assert 1 <= v <= 99


def test_final_description_has_hash():
    alg = StringHashingSimulation()
    params = _make_params(0)
    _, final = _collect(alg, params)
    assert "H[" in final.description


def test_different_strings_different_hashes():
    alg = StringHashingSimulation()
    finals = []
    for seed in range(len(_EXAMPLES)):
        params = _make_params(seed)
        _, final = _collect(alg, params)
        finals.append(final.swaps)
    assert len(set(finals)) > 1
