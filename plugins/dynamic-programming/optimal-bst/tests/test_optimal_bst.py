"""Tests for Optimal BST (Knuth's Algorithm)."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "optimal_bst", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

OptimalBSTSimulation = _mod.OptimalBSTSimulation
_KEYS = _mod._KEYS
_FREQ = _mod._FREQ
_N = _mod._N


def _make_plugin(seed=0):
    plugin = OptimalBSTSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "optimal-bst"


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


def test_initialize_table_square():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.table) == _N
    assert all(len(row) == _N for row in state.table)


def test_initialize_diagonal_matches_freq():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    for i in range(_N):
        assert state.table[i][i] == _FREQ[i]


def test_initialize_computed_diagonal():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    for i in range(_N):
        assert (i, i) in state.computed_cells


def test_steps_yields_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) >= _N


def test_steps_final_has_optimal_cost():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert "Optimal BST cost" in steps[-1].description


def test_steps_final_cost_positive():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    import re
    m = re.search(r"Optimal BST cost = (\d+)", steps[-1].description)
    assert m is not None
    assert int(m.group(1)) > 0


def test_steps_final_cost_at_least_sum_freq():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    import re
    m = re.search(r"Optimal BST cost = (\d+)", steps[-1].description)
    cost = int(m.group(1))
    # Minimum possible cost >= sum of frequencies (each key accessed at least once)
    assert cost >= sum(_FREQ)


def test_steps_all_cells_computed():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    for i in range(_N):
        for j in range(i, _N):
            assert (i, j) in final.computed_cells


def test_steps_top_right_cell_optimal():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    # dp[0][N-1] should be set and > 0
    assert final.table[0][_N - 1] > 0


def test_steps_dp_values_non_decreasing_with_range():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    # dp[i][j] >= max(dp[i][j-1], dp[i+1][j]) for valid indices
    for i in range(_N):
        for j in range(i, _N - 1):
            assert final.table[i][j + 1] >= final.table[i][j]
