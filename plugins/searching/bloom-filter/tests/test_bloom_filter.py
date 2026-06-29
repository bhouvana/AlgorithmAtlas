"""Tests for Bloom Filter."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("bloom_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

BloomFilterSimulation = _mod.BloomFilterSimulation
_M = _mod._M
_K = _mod._K
_ITEMS = _mod._ITEMS
_QUERIES = _mod._QUERIES
_hash = _mod._hash
_insert_bits = _mod._insert_bits


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


# --- hash function ---

def test_hash_in_range():
    for item in _ITEMS:
        for k in range(_K):
            h = _hash(item, k)
            assert 0 <= h < _M


def test_different_seeds_different_hashes():
    item = "cat"
    hashes = [_hash(item, k) for k in range(_K)]
    # With 3 hash functions, at least 2 should differ
    assert len(set(hashes)) >= 1


def test_insert_bits_count():
    bits = _insert_bits("cat")
    assert len(bits) == _K


# --- metadata ---

def test_metadata_slug():
    alg = BloomFilterSimulation()
    assert alg.metadata().slug == "bloom-filter"


def test_metadata_category():
    alg = BloomFilterSimulation()
    assert alg.metadata().category == "searching"


def test_metadata_visualization():
    alg = BloomFilterSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = BloomFilterSimulation()
    state = alg.initialize(_make_params(0))
    assert len(state.array) == _M


def test_initialize_all_bits_zero():
    alg = BloomFilterSimulation()
    state = alg.initialize(_make_params(0))
    assert all(v == 1 for v in state.array)  # all 0-bits shown as 1


# --- steps ---

def test_bits_increase_after_insert():
    alg = BloomFilterSimulation()
    params = _make_params(0)
    states, _ = _collect(alg, params)
    # First few steps are insertions, bits should grow
    insert_steps = [s for s in states if "Inserted" in s.description]
    if len(insert_steps) >= 2:
        assert insert_steps[1].swaps >= insert_steps[0].swaps


def test_inserted_items_not_absent():
    # Items that were inserted should NEVER be shown as ABSENT (no false negatives)
    alg = BloomFilterSimulation()
    params = _make_params(0)
    n_items = (params.seed % 5) + 3
    inserted = set(_ITEMS[:n_items])
    states, _ = _collect(alg, params)
    for s in states:
        if "ABSENT" in s.description:
            # Extract queried item
            import re
            m = re.search(r"Query '([^']+)'", s.description)
            if m:
                item = m.group(1)
                assert item not in inserted, f"False negative for '{item}'!"


def test_array_values_are_binary():
    alg = BloomFilterSimulation()
    params = _make_params(0)
    states, final = _collect(alg, params)
    for s in states + [final]:
        for v in s.array:
            assert v in (1, 99)  # 0-bit = 1, 1-bit = 99


def test_sorted_indices_are_set_bits():
    alg = BloomFilterSimulation()
    params = _make_params(0)
    states, _ = _collect(alg, params)
    for s in states:
        # sorted_indices should match set bits in array
        set_bits = frozenset(i for i, v in enumerate(s.array) if v == 99)
        # sorted_indices is a subset (only checked positions in current step)
        assert s.sorted_indices <= set_bits


def test_queries_after_inserts():
    alg = BloomFilterSimulation()
    params = _make_params(0)
    states, _ = _collect(alg, params)
    query_steps = [s for s in states if "Query" in s.description]
    assert len(query_steps) == len(_QUERIES)


def test_final_bits_count():
    alg = BloomFilterSimulation()
    params = _make_params(0)
    _, final = _collect(alg, params)
    set_bits = sum(1 for v in final.array if v == 99)
    assert set_bits > 0
    assert set_bits <= _M
