"""Tests for Convex Hull Trick DP optimization."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "convex_hull_trick", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

ConvexHullTrickSimulation = _mod.ConvexHullTrickSimulation
_N = _mod._N
_SLOPES = _mod._SLOPES
_QUERIES = _mod._QUERIES


def _make_plugin(seed=0):
    plugin = ConvexHullTrickSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "convex-hull-trick"


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


def test_initialize_two_rows():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.table) == 2


def test_initialize_dp_zero_base():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert state.table[0][0] == 0


def test_steps_yields_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) >= _N


def test_steps_dp_values_non_negative():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    for val in final.table[0]:
        assert val >= 0


def test_steps_dp_base_case_preserved():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    for step in steps:
        assert step.table[0][0] == 0


def test_steps_final_has_cht():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert "CHT" in steps[-1].description or "dp=" in steps[-1].description


def test_steps_dp_values_match_brute_force():
    """CHT must give same result as O(n²) brute force."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    cht_dp = list(final.table[0])

    # Brute-force O(n²)
    dp = [0] + [10 ** 9] * (_N - 1)
    for j in range(1, _N):
        for i in range(j):
            dp[j] = min(dp[j], dp[i] + _SLOPES[i] * _QUERIES[j])

    assert cht_dp == dp


def test_steps_optimal_indices_valid():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    opt = list(final.table[1])
    for j in range(1, _N):
        if opt[j] != -1:
            assert 0 <= opt[j] < j


def test_steps_add_line_steps():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    add_steps = [s for s in steps if "Add line" in s.description]
    assert len(add_steps) >= 1
