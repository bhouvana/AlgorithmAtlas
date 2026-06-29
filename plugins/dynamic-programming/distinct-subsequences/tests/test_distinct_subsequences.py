"""Tests for Distinct Subsequences Count plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "dist_subseq_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

DistinctSubsequencesSimulation = mod.DistinctSubsequencesSimulation
_EXAMPLES = mod._EXAMPLES


def _brute_count(s, t):
    """Brute-force: count subsequences recursively."""
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def dp(i, j):
        if j == len(t):
            return 1
        if i == len(s):
            return 0
        result = dp(i + 1, j)
        if s[i] == t[j]:
            result += dp(i + 1, j + 1)
        return result

    return dp(0, 0)


def _make_plugin(seed=0):
    plugin = DistinctSubsequencesSimulation()

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
    p = DistinctSubsequencesSimulation()
    assert p.metadata().slug == "distinct-subsequences"


def test_metadata_category():
    p = DistinctSubsequencesSimulation()
    assert p.metadata().category == "dynamic-programming"


def test_initial_array_length_t_plus_1():
    plugin, params = _make_plugin(seed=0)
    state = plugin.initialize(params)
    s, t = _EXAMPLES[0]
    assert len(state.array) == len(t) + 1


def test_initial_swaps_zero():
    plugin, params = _make_plugin(seed=0)
    state = plugin.initialize(params)
    assert state.swaps == 0


def test_rabbbit_rabbit():
    # "rabbbit" contains "rabbit" in 3 ways
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert final.swaps == 3


def test_babgbag_bag():
    # "babgbag" contains "bag" in 5 ways
    plugin, params = _make_plugin(seed=1)
    states = _collect(plugin, params)
    final = states[-1]
    assert final.swaps == 5


def test_seed2_matches_brute_force():
    plugin, params = _make_plugin(seed=2)
    states = _collect(plugin, params)
    s, t = _EXAMPLES[2]
    expected = _brute_count(s, t)
    assert states[-1].swaps == expected


def test_seed3_matches_brute_force():
    plugin, params = _make_plugin(seed=3)
    states = _collect(plugin, params)
    s, t = _EXAMPLES[3]
    expected = _brute_count(s, t)
    assert states[-1].swaps == expected


def test_seed4_aaaaaa_aaa():
    plugin, params = _make_plugin(seed=4)
    states = _collect(plugin, params)
    s, t = _EXAMPLES[4]
    expected = _brute_count(s, t)
    assert states[-1].swaps == expected


def test_step_count_equals_s_length():
    plugin, params = _make_plugin(seed=0)
    s, t = _EXAMPLES[0]
    states = _collect(plugin, params)
    # initial + len(s) step states + final = len(s) + 2
    assert len(states) == len(s) + 2


def test_all_array_values_in_range():
    for seed in range(5):
        plugin, params = _make_plugin(seed=seed)
        states = _collect(plugin, params)
        for s in states:
            for v in s.array:
                assert 0 <= v <= 99


def test_final_description_contains_count():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    assert "3" in states[-1].description


def test_comparisons_equal_s_length_at_end():
    plugin, params = _make_plugin(seed=0)
    s, _ = _EXAMPLES[0]
    states = _collect(plugin, params)
    assert states[-1].comparisons == len(s)
