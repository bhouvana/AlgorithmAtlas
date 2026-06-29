"""Tests for Baby-Step Giant-Step plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "bsgs_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BabyStepGiantStepSimulation = mod.BabyStepGiantStepSimulation
_bsgs = mod._bsgs
_PROBLEMS = mod._PROBLEMS


def _make_plugin(seed=0):
    plugin = BabyStepGiantStepSimulation()

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
    p = BabyStepGiantStepSimulation()
    assert p.metadata().slug == "baby-step-giant-step"


def test_metadata_category():
    p = BabyStepGiantStepSimulation()
    assert p.metadata().category == "number-theory"


def test_bsgs_solves_problem_0():
    h, g, p = _PROBLEMS[0]
    x, _, _, _ = _bsgs(h, g, p)
    assert x is not None
    assert pow(g, x, p) == h % p


def test_bsgs_solves_all_problems():
    for h, g, p in _PROBLEMS:
        x, _, _, _ = _bsgs(h, g, p)
        assert x is not None, f"Failed to solve {g}^x ≡ {h} (mod {p})"
        assert pow(g, x, p) == h % p


def test_final_swaps_is_solution():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    h, g, p = _PROBLEMS[0]
    assert pow(g, final.swaps, p) == h


def test_final_description_has_solution():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    final = states[-1]
    assert "Solution" in final.description or "Verify" in final.description


def test_steps_produced():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    assert len(states) >= 5


def test_baby_steps_phase_exists():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    baby_step_states = [s for s in states if "Baby step" in s.description]
    assert len(baby_step_states) > 0


def test_giant_steps_phase_exists():
    plugin, params = _make_plugin(seed=0)
    states = _collect(plugin, params)
    giant_step_states = [s for s in states if "Giant step" in s.description]
    assert len(giant_step_states) > 0


def test_different_seeds_different_problems():
    solutions = []
    for seed in range(5):
        plugin, params = _make_plugin(seed=seed)
        states = _collect(plugin, params)
        solutions.append(states[-1].swaps)
    # Different seeds should give different answers
    assert len(set(solutions)) > 1
