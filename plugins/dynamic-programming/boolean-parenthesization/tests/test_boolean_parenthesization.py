"""Tests for Boolean Parenthesization DP."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "boolean_parenthesization", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

BooleanParenthesizationSimulation = _mod.BooleanParenthesizationSimulation
_SYMS = _mod._SYMS
_OPS = _mod._OPS
_N = _mod._N


def _make_plugin(seed=0):
    plugin = BooleanParenthesizationSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "boolean-parenthesization"


def test_metadata_category():
    plugin, _ = _make_plugin()
    assert plugin.metadata().category == "dynamic-programming"


def test_metadata_visualization():
    plugin, _ = _make_plugin()
    assert plugin.metadata().visualization_type == "MATRIX"


def test_initialize_returns_dp_state():
    from algorithm_atlas_sdk import DPState
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert isinstance(state, DPState)


def test_initialize_table_n_by_n():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.table) == _N
    assert all(len(row) == _N for row in state.table)


def test_initialize_base_cases_correct():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    for i in range(_N):
        expected = 1 if _SYMS[i] else 0
        assert state.table[i][i] == expected, f"Base case {i}: expected {expected}"


def test_steps_yields_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) >= _N


def test_steps_final_has_total():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert "Total ways" in steps[-1].description


def test_steps_total_ways_non_negative():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    import re
    m = re.search(r"Total ways to evaluate True = (\d+)", steps[-1].description)
    assert m is not None
    assert int(m.group(1)) >= 0


def test_steps_true_ways_bounded_by_catalan():
    from math import comb
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    # Total parenthesizations = Catalan(N-1)
    n = _N - 1
    catalan = comb(2 * n, n) // (n + 1)
    assert final.table[0][_N - 1] <= catalan


def test_steps_expression_T_and_F_or_T_xor_F_result():
    # Expression: T & F | T ^ F
    # All 5 parenthesizations evaluate to True (computed manually)
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    # True ways for T&F|T^F should be 5 (all Catalan(3) = 5 ways are True)
    assert final.table[0][_N - 1] == 5


def test_steps_all_diagonal_cells_computed():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    for i in range(_N):
        assert (i, i) in final.computed_cells


def test_steps_dp_table_non_negative():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    for row in final.table:
        for val in row:
            assert val >= 0


def test_steps_description_contains_operator():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    op_steps = [s for s in steps if "op=" in s.description]
    assert len(op_steps) >= 1
