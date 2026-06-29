"""Tests for Berlekamp-Massey LFSR algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "berlekamp_massey", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

BerlekampMasseySimulation = _mod.BerlekampMasseySimulation
_SEQ = _mod._SEQ


def _make_plugin(seed=0):
    plugin = BerlekampMasseySimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "berlekamp-massey"


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


def test_initialize_has_two_rows():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.table) == 2


def test_initialize_first_row_is_sequence():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert list(state.table[0]) == list(_SEQ)


def test_initialize_second_row_starts_with_one():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert state.table[1][0] == 1


def test_steps_yields_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) >= len(_SEQ)


def test_steps_final_has_lfsr_length():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert "length=" in steps[-1].description


def test_steps_lfsr_length_is_3():
    """The m-sequence [1,1,0,1,0,0,1] requires an LFSR of length 3."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    import re
    m = re.search(r"length=(\d+)", steps[-1].description)
    assert m is not None
    assert int(m.group(1)) == 3


def test_steps_polynomial_row_length():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    # Second row (polynomial) should have length == len(_SEQ)
    assert len(steps[-1].table[1]) == len(_SEQ)


def test_steps_lfsr_generates_sequence():
    """Verify the final LFSR polynomial actually generates the input sequence."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    C = list(final.table[1])
    # Trim trailing zeros
    while len(C) > 1 and C[-1] == 0:
        C.pop()
    L = len(C) - 1   # degree = LFSR length
    # Regenerate: s[n] = sum(C[i]*s[n-i] for i=1..L) mod 2
    init = list(_SEQ[:L])
    generated = init[:]
    for n_idx in range(L, len(_SEQ)):
        val = 0
        for j in range(1, L + 1):
            val ^= C[j] * generated[n_idx - j]
        val &= 1
        generated.append(val)
    assert generated == list(_SEQ)


def test_steps_sequence_row_unchanged():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    for step in steps:
        assert list(step.table[0]) == list(_SEQ)
