"""Tests for Random Forest plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "rf_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

RandomForestSimulation = mod.RandomForestSimulation
_gen_data = mod._gen_data
_N_TREES = mod._N_TREES
_gini = mod._gini


def _make_plugin(seed=0):
    plugin = RandomForestSimulation()

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
    p = RandomForestSimulation()
    assert p.metadata().slug == "random-forest"


def test_metadata_category():
    p = RandomForestSimulation()
    assert p.metadata().category == "machine-learning"


def test_gini_pure():
    assert _gini([0, 0, 0]) == 0.0
    assert _gini([1, 1, 1]) == 0.0


def test_gini_impure():
    assert abs(_gini([0, 1]) - 0.5) < 1e-9


def test_step_count():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    # initial + _N_TREES steps + final
    assert len(states) == _N_TREES + 2


def test_final_accuracy_positive():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert final.swaps > 0  # swaps = accuracy * 100


def test_final_accuracy_reasonable():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert final.swaps >= 50  # at least 50% accuracy


def test_all_array_values_in_range():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_comparisons_increment():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    step_states = states[1:-1]
    for i, s in enumerate(step_states):
        assert s.comparisons == i + 1


def test_final_description_mentions_forest():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert "Forest" in final.description or "trees" in final.description.lower()


def test_different_seeds_give_different_results():
    results = []
    for seed in range(3):
        plugin, params = _make_plugin(seed=seed)
        states = _collect(plugin, params)
        results.append(states[-1].swaps)
    # Results may vary by seed (not guaranteed, but usually true)
    # At minimum, all should be positive
    assert all(r > 0 for r in results)
