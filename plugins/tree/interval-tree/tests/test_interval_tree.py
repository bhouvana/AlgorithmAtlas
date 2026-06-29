"""Tests for Interval Tree plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "interval_tree_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

IntervalTreeSimulation = mod.IntervalTreeSimulation
_INTERVALS = mod._INTERVALS
_QUERY = mod._QUERY
_insert = mod._insert
_query = mod._query


def _brute_overlap(intervals, ql, qr):
    return sorted([(lo, hi) for lo, hi in intervals if lo <= qr and hi >= ql])


def _make_plugin(seed=0):
    plugin = IntervalTreeSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def _collect(plugin, params):
    state = plugin.initialize(params)
    states = [state]
    gen = plugin.steps(state)
    try:
        while True:
            states.append(next(gen))
    except StopIteration as e:
        states.append(e.value)
    return states


def test_metadata_slug():
    p = IntervalTreeSimulation()
    assert p.metadata().slug == "interval-tree"


def test_metadata_category():
    p = IntervalTreeSimulation()
    assert p.metadata().category == "tree"


def test_brute_force_overlaps():
    ql, qr = _QUERY
    overlaps = _brute_overlap(_INTERVALS, ql, qr)
    assert len(overlaps) > 0


def test_tree_query_matches_brute_force():
    root = None
    for lo, hi in _INTERVALS:
        root = _insert(root, lo, hi)
    ql, qr = _QUERY
    result = []
    _query(root, ql, qr, result)
    brute = _brute_overlap(_INTERVALS, ql, qr)
    assert sorted(result) == brute


def test_final_swaps_is_overlap_count():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    ql, qr = _QUERY
    expected = len(_brute_overlap(_INTERVALS, ql, qr))
    assert final.swaps == expected


def test_step_count():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    # initial + n build steps + 1 query step + final = n + 3
    assert len(states) == len(_INTERVALS) + 3


def test_all_array_values_in_range():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_final_description_mentions_overlap():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert "overlap" in final.description.lower() or "Done" in final.description


def test_query_step_mentions_query():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    query_step = states[-2]  # second-to-last is the query step
    assert "Query" in query_step.description or "overlap" in query_step.description.lower()


def test_initial_comparisons_zero():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert state.comparisons == 0
