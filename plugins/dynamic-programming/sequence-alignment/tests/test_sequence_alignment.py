"""Tests for Sequence Alignment (Needleman-Wunsch) plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "seq_align_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SequenceAlignmentSimulation = mod.SequenceAlignmentSimulation
_PAIRS = mod._PAIRS
_nw = mod._nw
_traceback = mod._traceback
_MATCH = mod._MATCH
_MISMATCH = mod._MISMATCH
_GAP = mod._GAP


def _make_plugin(seed=0):
    plugin = SequenceAlignmentSimulation()

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
    p = SequenceAlignmentSimulation()
    assert p.metadata().slug == "sequence-alignment"


def test_metadata_category():
    p = SequenceAlignmentSimulation()
    assert p.metadata().category == "dynamic-programming"


def test_nw_base_cases():
    # Empty string alignment
    s1, s2 = "ACGT", ""
    dp = _nw(s1, s2)
    assert dp[4][0] == 4 * _GAP
    assert dp[0][0] == 0


def test_nw_all_match():
    dp = _nw("ACGT", "ACGT")
    assert dp[4][4] == 4 * _MATCH


def test_nw_all_mismatch():
    dp = _nw("AAAA", "TTTT")
    assert dp[4][4] == 4 * _MISMATCH


def test_step_count():
    plugin, params = _make_plugin(seed=0)
    s1, s2 = _PAIRS[0]
    states = _collect(plugin, params)
    # initial + len(s1) steps + final = len(s1) + 2
    assert len(states) == len(s1) + 2


def test_final_score_matches_nw():
    for seed in range(5):
        plugin, params = _make_plugin(seed=seed)
        states = _collect(plugin, params)
        s1, s2 = _PAIRS[seed]
        dp = _nw(s1, s2)
        expected = dp[len(s1)][len(s2)]
        assert states[-1].swaps == expected


def test_final_description_has_score():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert "Score=" in final.description


def test_traceback_alignment_correct():
    s1, s2 = "ACGT", "AGCT"
    dp = _nw(s1, s2)
    a1, a2 = _traceback(dp, s1, s2)
    # Alignment should have same length
    assert len(a1) == len(a2)
    # Verify score from alignment
    score = sum(
        _MATCH if a1[i] != '-' and a2[i] != '-' and a1[i] == a2[i] else
        _MISMATCH if a1[i] != '-' and a2[i] != '-' else
        _GAP
        for i in range(len(a1))
    )
    assert score == dp[4][4]


def test_comparisons_increment():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    step_states = states[1:-1]
    for i, s in enumerate(step_states):
        assert s.comparisons == i + 1


def test_all_array_values_in_range():
    for seed in range(5):
        plugin, params = _make_plugin(seed=seed)
        states = _collect(plugin, params)
        for s in states:
            for v in s.array:
                assert 0 <= v <= 99
