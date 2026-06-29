"""Tests for Pollard's Rho plugin."""
import importlib.util
import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "pollard_rho_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PollardRhoSimulation = mod.PollardRhoSimulation
_pollard_steps = mod._pollard_steps
_gcd = mod._gcd
_COMPOSITES = mod._COMPOSITES


def _make_plugin(n=77, seed=0):
    plugin = PollardRhoSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {"size": n}
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
    p = PollardRhoSimulation()
    assert p.metadata().slug == "pollard-rho"


def test_metadata_category():
    p = PollardRhoSimulation()
    assert p.metadata().category == "number-theory"


def test_gcd():
    assert _gcd(12, 8) == 4
    assert _gcd(7, 13) == 1
    assert _gcd(77, 11) == 11


def test_pollard_finds_factor_77():
    steps, factor = _pollard_steps(77)
    assert factor in (7, 11)
    assert 77 % factor == 0


def test_pollard_finds_factor_91():
    steps, factor = _pollard_steps(91)
    assert factor in (7, 13)
    assert 91 % factor == 0


def test_final_swaps_is_factor():
    plugin, params = _make_plugin(n=77)
    states = _collect(plugin, params)
    final = states[-1]
    assert 77 % final.swaps == 0
    assert 1 < final.swaps < 77


def test_final_description_multiplication():
    plugin, params = _make_plugin(n=77)
    states = _collect(plugin, params)
    final = states[-1]
    assert "×" in final.description or "x" in final.description.lower() or "=" in final.description


def test_steps_produced():
    plugin, params = _make_plugin(n=77)
    states = _collect(plugin, params)
    assert len(states) >= 3


def test_all_composites_factorable():
    for n in _COMPOSITES:
        steps, factor = _pollard_steps(n)
        assert 1 < factor < n
        assert n % factor == 0


def test_comparisons_increment():
    plugin, params = _make_plugin(n=57)
    states = _collect(plugin, params)
    step_states = states[1:-1]
    for i, s in enumerate(step_states):
        assert s.comparisons == i + 1
