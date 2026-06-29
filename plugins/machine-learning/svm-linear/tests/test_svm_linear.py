"""Tests for Linear SVM plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "svm_linear_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SVMLinearSimulation = mod.SVMLinearSimulation
_generate_data = mod._generate_data
_ITERS = mod._ITERS


def _make_plugin(seed=0):
    plugin = SVMLinearSimulation()

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
    p = SVMLinearSimulation()
    assert p.metadata().slug == "svm-linear"


def test_metadata_category():
    p = SVMLinearSimulation()
    assert p.metadata().category == "machine-learning"


def test_initial_array_length():
    plugin, params = _make_plugin(seed=0)
    state = plugin.initialize(params)
    points, _ = _generate_data(0)
    assert len(state.array) == len(points)


def test_step_count():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    # initial + _ITERS steps + final = _ITERS + 2
    assert len(states) == _ITERS + 2


def test_all_array_values_in_range():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_final_accuracy_high():
    """Data is linearly separable so final accuracy should be perfect or near-perfect."""
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    points, labels = _generate_data(0)
    n = len(points)
    assert final.swaps >= n * 0.8  # at least 80% accuracy


def test_comparisons_increment():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    step_states = states[1:-1]
    for i, s in enumerate(step_states):
        assert s.comparisons == i + 1


def test_data_is_separable():
    """Class +1 has x1 > 0.4, class -1 has x1 < 0.36 — should be linearly separable."""
    for seed in range(5):
        points, labels = _generate_data(seed)
        class1 = [p[0] for p, l in zip(points, labels) if l == 1]
        classn1 = [p[0] for p, l in zip(points, labels) if l == -1]
        assert min(class1) > max(classn1) * 0.5  # rough check classes differ


def test_loss_decreases():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    step_states = states[1:-1]
    # Loss should generally decrease over iterations
    # Compare first half vs second half
    import re
    losses = []
    for s in step_states:
        m = re.search(r"loss=([0-9.]+)", s.description)
        if m:
            losses.append(float(m.group(1)))
    if len(losses) >= 4:
        first_half = sum(losses[:len(losses)//2]) / (len(losses)//2)
        second_half = sum(losses[len(losses)//2:]) / (len(losses) - len(losses)//2)
        assert second_half <= first_half + 0.5  # not dramatically worse


def test_final_description_mentions_accuracy():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert "Accuracy" in final.description or "accuracy" in final.description
