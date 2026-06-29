"""Tests for Tonelli-Shanks modular square root algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "tonelli_shanks", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TonelliShanksSimulation = _mod.TonelliShanksSimulation
_N_VAL = _mod._N_VAL
_P_VAL = _mod._P_VAL


def _make_plugin(seed=0):
    plugin = TonelliShanksSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "tonelli-shanks"


def test_metadata_category():
    plugin, _ = _make_plugin()
    assert plugin.metadata().category == "number-theory"


def test_metadata_visualization():
    plugin, _ = _make_plugin()
    assert plugin.metadata().visualization_type == "MATRIX"


def test_initialize_returns_dp_state():
    from algorithm_atlas_sdk import DPState
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert isinstance(state, DPState)


def test_initialize_single_row():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.table) == 1
    assert len(state.table[0]) == 9


def test_steps_yields_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) >= 3


def test_steps_final_has_sqrt():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    desc = steps[-1].description
    assert "≡" in desc or "mod" in desc.lower()


def test_steps_result_is_correct_sqrt():
    """R^2 ≡ N_VAL (mod P_VAL)."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final_row = steps[-1].table[0]
    R = final_row[8]
    assert (R * R) % _P_VAL == _N_VAL


def test_steps_both_roots():
    """Both R and P-R are valid square roots."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    R = steps[-1].table[0][8]
    assert (R * R) % _P_VAL == _N_VAL
    assert (((_P_VAL - R) * (_P_VAL - R)) % _P_VAL) == _N_VAL


def test_steps_p_is_prime():
    """The prime P should be odd and > 2."""
    assert _P_VAL > 2
    # Quick primality check
    for i in range(2, int(_P_VAL ** 0.5) + 1):
        assert _P_VAL % i != 0


def test_steps_euler_criterion_step():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    euler_steps = [s for s in steps if "Euler" in s.description]
    assert len(euler_steps) >= 1


def test_steps_factoring_step():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    factor_steps = [s for s in steps if "Q=" in s.description]
    assert len(factor_steps) >= 1


def test_steps_qnr_found():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    qnr_steps = [s for s in steps if "QNR" in s.description]
    assert len(qnr_steps) >= 1
