"""Tests for Karger's Min-Cut plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "karger_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

KargerMincutSimulation = mod.KargerMincutSimulation
_ORIG_EDGES = mod._ORIG_EDGES
_N_NODES = mod._N_NODES
_TRUE_MINCUT = mod._TRUE_MINCUT
_karger_run = mod._karger_run
_karger_multi = mod._karger_multi


def _make_plugin(seed=0):
    plugin = KargerMincutSimulation()

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
    p = KargerMincutSimulation()
    assert p.metadata().slug == "karger-mincut"


def test_metadata_category():
    p = KargerMincutSimulation()
    assert p.metadata().category == "randomized"


def test_true_mincut_value():
    assert _TRUE_MINCUT == 2


def test_karger_finds_mincut():
    min_cut, _ = _karger_multi(_ORIG_EDGES, _N_NODES, 20, 42)
    assert min_cut == _TRUE_MINCUT


def test_final_swaps_is_mincut():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert final.swaps == _TRUE_MINCUT


def test_step_count():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    # initial + 8 trial steps + final = 10
    assert len(states) == 10


def test_all_array_values_in_range():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_final_description_mentions_mincut():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert "Min-cut" in final.description or "min" in final.description.lower()


def test_some_trial_found_optimal():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    # At least one step state should show optimal cut
    optimal_steps = [s for s in states[1:-1] if s.swaps == _TRUE_MINCUT]
    assert len(optimal_steps) > 0


def test_cut_values_positive():
    for seed in [42, 100, 200]:
        cut, _ = _karger_run(_ORIG_EDGES, _N_NODES, seed)
        assert cut >= _TRUE_MINCUT  # can't be less than true min cut
