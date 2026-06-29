"""Tests for Stable Matching (Gale-Shapley)."""
import importlib.util
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("sm_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

StableMatchingSimulation = _mod.StableMatchingSimulation
_N = _mod._N
_MEN_PREF = _mod._MEN_PREF
_WOMEN_PREF = _mod._WOMEN_PREF


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


# --- preference validation ---

def test_men_prefs_complete():
    for pref in _MEN_PREF:
        assert sorted(pref) == list(range(_N))


def test_women_prefs_valid_ranks():
    for prefs in _WOMEN_PREF:
        assert len(prefs) == _N


# --- metadata ---

def test_metadata_slug():
    alg = StableMatchingSimulation()
    assert alg.metadata().slug == "stable-matching"


def test_metadata_category():
    alg = StableMatchingSimulation()
    assert alg.metadata().category == "greedy"


def test_metadata_visualization():
    alg = StableMatchingSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = StableMatchingSimulation()
    state = alg.initialize(_make_params())
    assert len(state.array) == _N


def test_initialize_all_free():
    alg = StableMatchingSimulation()
    state = alg.initialize(_make_params())
    assert all(v == 1 for v in state.array)
    assert state.sorted_indices == frozenset()


# --- steps ---

def test_steps_exist():
    alg = StableMatchingSimulation()
    params = _make_params()
    states, _ = _collect(alg, params)
    assert len(states) > 0


def test_final_all_matched():
    alg = StableMatchingSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    assert final.swaps == _N
    assert final.sorted_indices == frozenset(range(_N))


def test_final_matching_is_bijection():
    alg = StableMatchingSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    # Extract matching from description
    import re
    matches = re.findall(r"M(\d+)↔W(\d+)", final.description)
    assert len(matches) == _N
    men_matched = [int(m) for m, w in matches]
    women_matched = [int(w) for m, w in matches]
    assert sorted(men_matched) == list(range(_N))
    assert sorted(women_matched) == list(range(_N))


def test_final_matching_stable():
    # Verify no blocking pair exists
    alg = StableMatchingSimulation()
    params = _make_params()
    _, final = _collect(alg, params)
    import re
    matches = re.findall(r"M(\d+)↔W(\d+)", final.description)
    match = {int(m): int(w) for m, w in matches}
    woman_match = {w: m for m, w in match.items()}

    for m in range(_N):
        for w in range(_N):
            if match[m] == w:
                continue
            # Is (m, w) a blocking pair?
            m_prefers_w = _MEN_PREF[m].index(w) < _MEN_PREF[m].index(match[m])
            w_prefers_m = _WOMEN_PREF[w][m] < _WOMEN_PREF[w][woman_match[w]]
            assert not (m_prefers_w and w_prefers_m), f"Blocking pair: M{m}↔W{w}"


def test_matched_count_increases():
    alg = StableMatchingSimulation()
    params = _make_params()
    states, _ = _collect(alg, params)
    max_matched = 0
    for s in states:
        if s.swaps > max_matched:
            max_matched = s.swaps
    assert max_matched == _N


def test_proposals_finite():
    alg = StableMatchingSimulation()
    params = _make_params()
    states, final = _collect(alg, params)
    assert final.comparisons <= _N * _N  # at most n² proposals
