"""Tests for Suffix Automaton plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "sam_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SuffixAutomatonSimulation = mod.SuffixAutomatonSimulation
_STRINGS = mod._STRINGS
_build_sam = mod._build_sam


def _make_plugin(seed=0):
    plugin = SuffixAutomatonSimulation()

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


def _count_distinct_substrings(s):
    """Brute force count of distinct substrings."""
    subs = set()
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n + 1):
            subs.add(s[i:j])
    return len(subs)


def test_metadata_slug():
    p = SuffixAutomatonSimulation()
    assert p.metadata().slug == "suffix-automaton"


def test_metadata_category():
    p = SuffixAutomatonSimulation()
    assert p.metadata().category == "string"


def test_state_count_bound():
    # States should be ≤ 2n - 1
    for s in _STRINGS[:4]:
        sam, _ = _build_sam(s)
        n = len(s)
        assert len(sam) <= 2 * n, f"Too many states for '{s}': {len(sam)} > {2*n}"


def test_sam_accepts_all_substrings():
    """Check that all substrings are recognized by the SAM."""
    s = "abcbc"
    sam, _ = _build_sam(s)
    n = len(s)

    def accepts(t):
        cur = 0
        for ch in t:
            if ch not in sam[cur].next:
                return False
            cur = sam[cur].next[ch]
        return True

    for i in range(n):
        for j in range(i + 1, n + 1):
            sub = s[i:j]
            assert accepts(sub), f"SAM does not accept substring '{sub}'"


def test_step_count():
    plugin, params = _make_plugin(seed=0)
    s = _STRINGS[0]
    states = _collect(plugin, params)
    assert len(states) == len(s) + 2  # initial + n steps + final


def test_final_state_count_in_range():
    for seed in range(5):
        plugin, params = _make_plugin(seed=seed)
        states = _collect(plugin, params)
        final = states[-1]
        s = _STRINGS[seed]
        n = len(s)
        assert 1 < final.swaps <= 2 * n


def test_all_array_values_in_range():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_final_description_mentions_states():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert "states" in final.description.lower() or "SAM" in final.description


def test_states_grow_monotonically():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    step_states = states[1:-1]
    counts = [s.swaps for s in step_states]
    for i in range(1, len(counts)):
        assert counts[i] >= counts[i - 1], "State count should be non-decreasing"
