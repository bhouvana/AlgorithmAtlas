"""Tests for Word Wrap DP plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "word_wrap_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

WordWrapSimulation = mod.WordWrapSimulation
_LINE_WIDTH = mod._LINE_WIDTH
_WORDS = mod._WORDS
_cost = mod._cost
_extra = mod._extra
_INF = mod._INF


def _make_plugin(seed=0):
    plugin = WordWrapSimulation()

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
    p = WordWrapSimulation()
    assert p.metadata().slug == "word-wrap"


def test_metadata_category():
    p = WordWrapSimulation()
    assert p.metadata().category == "dynamic-programming"


def test_initial_array_length():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.array) == len(_WORDS) + 1


def test_step_count():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    # initial + n step states + final = n + 2
    assert len(states) == len(_WORDS) + 2


def test_final_cost_finite():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert final.swaps < _INF
    assert final.swaps >= 0


def test_final_cost_non_negative():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    assert states[-1].swaps >= 0


def test_brute_force_optimal():
    """Brute-force verify DP finds optimal cost via trying all line breaks."""
    words = _WORDS
    n = len(words)
    W = _LINE_WIDTH

    # DP reference
    dp = [_INF] * (n + 1)
    dp[0] = 0
    for i in range(1, n + 1):
        for j in range(i - 1, -1, -1):
            c = _cost(words, j, i - 1, W)
            if c < _INF and dp[j] + c < dp[i]:
                dp[i] = dp[j] + c

    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    assert states[-1].swaps == dp[n]


def test_all_array_values_in_range():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 0 <= v <= 99


def test_final_description_mentions_cost():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    assert "cost" in states[-1].description.lower()


def test_extra_function():
    # "the quick" = 9 chars, in line width 16 → extra = 16-9 = 7
    assert _extra(_WORDS, 0, 1, 16) == 7


def test_cost_last_line_zero():
    # Last word has zero cost regardless of extra space
    n = len(_WORDS)
    assert _cost(_WORDS, n - 1, n - 1, _LINE_WIDTH) == 0
