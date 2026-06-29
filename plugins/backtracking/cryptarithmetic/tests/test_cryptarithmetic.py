"""Tests for Cryptarithmetic plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "cryptarith_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CryptarithmeticSimulation = mod.CryptarithmeticSimulation
_SOLUTION = mod._SOLUTION
_LETTERS = mod._LETTERS
_check = mod._check


def _make_plugin(seed=0):
    plugin = CryptarithmeticSimulation()

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
    p = CryptarithmeticSimulation()
    assert p.metadata().slug == "cryptarithmetic"


def test_metadata_category():
    p = CryptarithmeticSimulation()
    assert p.metadata().category == "backtracking"


def test_solution_correct():
    assert _check(_SOLUTION)


def test_solution_values():
    S, E, N, D = _SOLUTION["S"], _SOLUTION["E"], _SOLUTION["N"], _SOLUTION["D"]
    M, O, R, Y = _SOLUTION["M"], _SOLUTION["O"], _SOLUTION["R"], _SOLUTION["Y"]
    SEND = 1000*S + 100*E + 10*N + D
    MORE = 1000*M + 100*O + 10*R + E
    MONEY = 10000*M + 1000*O + 100*N + 10*E + Y
    assert SEND == 9567
    assert MORE == 1085
    assert MONEY == 10652


def test_solution_digits_unique():
    digits = list(_SOLUTION.values())
    assert len(digits) == len(set(digits))


def test_initial_array_length():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.array) == len(_LETTERS)


def test_steps_produced():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    assert len(states) > 3


def test_final_description_has_numbers():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert "9567" in final.description


def test_solution_step_found():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    # At least one step should mention SOLUTION
    solution_steps = [s for s in states if "SOLUTION" in s.description]
    assert len(solution_steps) >= 1


def test_all_array_values_in_range():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 0 <= v <= 99


def test_no_leading_zero():
    assert _SOLUTION["S"] != 0
    assert _SOLUTION["M"] != 0
