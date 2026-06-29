"""Tests for Logistic Regression."""
import importlib.util
import math
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("logreg_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

LogisticRegressionSimulation = _mod.LogisticRegressionSimulation
_sigmoid = _mod._sigmoid
_generate_data = _mod._generate_data
_ITERS = _mod._ITERS


def _make_params(size=20, seed=0):
    class P:
        inputs = {"size": size}
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


# --- sigmoid helper ---

def test_sigmoid_zero():
    assert abs(_sigmoid(0.0) - 0.5) < 1e-9


def test_sigmoid_positive():
    assert _sigmoid(10.0) > 0.99


def test_sigmoid_negative():
    assert _sigmoid(-10.0) < 0.01


def test_sigmoid_symmetric():
    assert abs(_sigmoid(2.0) + _sigmoid(-2.0) - 1.0) < 1e-9


# --- metadata ---

def test_metadata_slug():
    alg = LogisticRegressionSimulation()
    assert alg.metadata().slug == "logistic-regression"


def test_metadata_category():
    alg = LogisticRegressionSimulation()
    assert alg.metadata().category == "machine-learning"


def test_metadata_visualization():
    alg = LogisticRegressionSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = LogisticRegressionSimulation()
    state = alg.initialize(_make_params(20))
    assert len(state.array) == 20


def test_initialize_predictions_at_50():
    alg = LogisticRegressionSimulation()
    state = alg.initialize(_make_params(20))
    assert all(v == 50 for v in state.array)


def test_initialize_description_contains_data():
    alg = LogisticRegressionSimulation()
    state = alg.initialize(_make_params(20))
    assert "xs=" in state.description
    assert "ys=" in state.description


# --- steps ---

def test_step_count_equals_iters():
    alg = LogisticRegressionSimulation()
    params = _make_params(20)
    states, _ = _collect(alg, params)
    assert len(states) == _ITERS


def test_accuracy_improves():
    alg = LogisticRegressionSimulation()
    params = _make_params(20)
    states, final = _collect(alg, params)
    first_acc = states[0].swaps
    last_acc = final.swaps
    assert last_acc >= first_acc


def test_final_high_accuracy():
    # With clearly separable data (class 0: [10,45], class 1: [55,90])
    # should achieve >80% accuracy after normalization
    alg = LogisticRegressionSimulation()
    params = _make_params(20)
    _, final = _collect(alg, params)
    acc = final.swaps / 20.0
    assert acc >= 0.8, f"Expected >= 80% accuracy, got {acc:.0%}"


def test_predictions_in_range():
    alg = LogisticRegressionSimulation()
    params = _make_params(20)
    states, final = _collect(alg, params)
    for s in states + [final]:
        for v in s.array:
            assert 1 <= v <= 99


def test_comparisons_increment():
    alg = LogisticRegressionSimulation()
    params = _make_params(20)
    states, _ = _collect(alg, params)
    for i, s in enumerate(states):
        assert s.comparisons == i + 1


def test_description_contains_weights():
    alg = LogisticRegressionSimulation()
    params = _make_params(20)
    states, _ = _collect(alg, params)
    for s in states:
        assert "w=" in s.description
        assert "loss=" in s.description


def test_class_1_predictions_higher_than_class_0():
    # After training, class-1 points should have higher probability bars
    import random
    alg = LogisticRegressionSimulation()
    params = _make_params(20)
    state = alg.initialize(params)
    import re
    xs_str = re.search(r"xs=([0-9,]+)", state.description).group(1)
    ys_str = re.search(r"ys=([0-9,]+)", state.description).group(1)
    xs = list(map(int, xs_str.split(",")))
    ys = list(map(int, ys_str.split(",")))
    _, final = _collect(alg, params)
    # Average prediction for class 1 should be > average for class 0
    avg_0 = sum(final.array[i] for i, y in enumerate(ys) if y == 0) / max(ys.count(0), 1)
    avg_1 = sum(final.array[i] for i, y in enumerate(ys) if y == 1) / max(ys.count(1), 1)
    assert avg_1 > avg_0


def test_different_seeds_converge():
    alg = LogisticRegressionSimulation()
    for seed in range(3):
        params = _make_params(20, seed)
        _, final = _collect(alg, params)
        acc = final.swaps / 20.0
        assert acc >= 0.75, f"seed={seed}: accuracy {acc:.0%} too low"
