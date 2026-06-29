"""Tests for Burrows-Wheeler Transform algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "burrows_wheeler", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

BurrowsWheelerSimulation = _mod.BurrowsWheelerSimulation
_INPUT = _mod._INPUT
_BWT_OUT = _mod._BWT_OUT
_ORIG_IDX = _mod._ORIG_IDX
_ibwt = _mod._ibwt
_bwt = _mod._bwt


def _make_plugin(seed=0):
    plugin = BurrowsWheelerSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "burrows-wheeler"


def test_metadata_category():
    plugin, _ = _make_plugin()
    assert plugin.metadata().category == "string"


def test_metadata_visualization():
    plugin, _ = _make_plugin()
    assert plugin.metadata().visualization_type == "MATRIX"


def test_initialize_returns_dp_state():
    from algorithm_atlas_sdk import DPState
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert isinstance(state, DPState)


def test_initialize_n_rows():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.table) == len(_INPUT)


def test_bwt_banana():
    """BWT of 'banana$' is 'annb$aa'."""
    bwt_out, _, _ = _bwt("banana$")
    assert bwt_out == "annb$aa"


def test_orig_idx_banana():
    """'banana$' is the 5th rotation (index 4) in sorted order."""
    _, _, orig_idx = _bwt("banana$")
    assert orig_idx == 4


def test_ibwt_recovers_original():
    """Inverse BWT of 'annb$aa' with index 4 → 'banana$'."""
    assert _ibwt("annb$aa", 4) == "banana$"


def test_bwt_roundtrip():
    bwt_out, _, orig_idx = _bwt(_INPUT)
    recovered = _ibwt(bwt_out, orig_idx)
    assert recovered == _INPUT


def test_steps_yields_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) >= len(_INPUT)


def test_steps_final_contains_bwt():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert _BWT_OUT in steps[-1].description


def test_steps_final_recovers_input():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert _INPUT in steps[-1].description


def test_steps_sorted_table_in_final():
    """Final table should have rotations_sorted as rows."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    # Check it's n rows
    assert len(final.table) == len(_INPUT)


def test_steps_rotation_step_present():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    # Individual rotation steps: "Rotation 0: ..." etc. (singular, not "Rotations sorted")
    rot_steps = [s for s in steps if s.description.startswith("Rotation ")]
    assert len(rot_steps) == len(_INPUT)


def test_steps_inverse_bwt_steps_present():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    inv_steps = [s for s in steps if "InvBWT" in s.description]
    assert len(inv_steps) == len(_INPUT)
