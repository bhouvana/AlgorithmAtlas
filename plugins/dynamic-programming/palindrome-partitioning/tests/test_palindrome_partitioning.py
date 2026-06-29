"""Tests for Palindrome Partitioning (min cuts) algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "palindrome_partitioning", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

PalindromePartitioningSimulation = _mod.PalindromePartitioningSimulation
_STRINGS = _mod._STRINGS
_min_cuts = _mod._min_cuts


def _make_plugin(seed=0):
    plugin = PalindromePartitioningSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def _brute_min_cuts(s):
    """Reference: brute force min cuts via recursion."""
    from functools import lru_cache

    n = len(s)

    def is_pal(i, j):
        while i < j:
            if s[i] != s[j]:
                return False
            i += 1
            j -= 1
        return True

    @lru_cache(maxsize=None)
    def dp(i):
        if is_pal(0, i):
            return 0
        best = i
        for j in range(1, i + 1):
            if is_pal(j, i):
                best = min(best, dp(j - 1) + 1)
        return best

    return dp(n - 1)


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "palindrome-partitioning"


def test_metadata_category():
    plugin, _ = _make_plugin()
    assert plugin.metadata().category == "dynamic-programming"


def test_metadata_visualization():
    plugin, _ = _make_plugin()
    assert plugin.metadata().visualization_type == "ARRAY_BARS"


def test_min_cuts_aab():
    dp, _ = _min_cuts("aab")
    assert dp[-1] == 1  # "aa|b"


def test_min_cuts_abacaba():
    dp, _ = _min_cuts("abacaba")
    assert dp[-1] == 0  # "abacaba" is itself a palindrome


def test_min_cuts_abcde():
    dp, _ = _min_cuts("abcde")
    assert dp[-1] == 4  # each char is its own palindrome


def test_min_cuts_matches_brute_force():
    for s in _STRINGS:
        dp, _ = _min_cuts(s)
        brute = _brute_min_cuts(s)
        assert dp[-1] == brute, f"'{s}': dp={dp[-1]}, brute={brute}"


def test_min_cuts_palindrome_has_zero():
    dp, _ = _min_cuts("racecar")
    assert dp[-1] == 0


def test_initialize_array_length():
    plugin, params = _make_plugin(0)
    state = plugin.initialize(params)
    assert len(state.array) == len(_STRINGS[0])


def test_initialize_description():
    plugin, params = _make_plugin(0)
    state = plugin.initialize(params)
    assert "PalPart s='" in state.description


def test_steps_yields_n_steps():
    plugin, params = _make_plugin(0)
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    s = _STRINGS[0]
    assert len(all_steps) == len(s)


def test_steps_array_values_in_range():
    for seed in range(len(_STRINGS)):
        plugin, _ = _make_plugin()

        class P:
            pass

        P.seed = seed
        P.inputs = {}
        state = plugin.initialize(P())
        for step in plugin.steps(state):
            for v in step.array:
                assert 1 <= v <= 99


def test_steps_swaps_track_dp_value():
    plugin, params = _make_plugin(0)
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    s = _STRINGS[0]
    dp, _ = _min_cuts(s)
    for i, step in enumerate(all_steps):
        assert step.swaps == dp[i]
