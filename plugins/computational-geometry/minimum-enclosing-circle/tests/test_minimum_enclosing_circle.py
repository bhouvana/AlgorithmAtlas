"""Tests for Minimum Enclosing Circle (Welzl)."""
import importlib.util
import math
import sys
from pathlib import Path

import pytest

_ALG_PATH = Path(__file__).parent.parent / "algorithm.py"
spec = importlib.util.spec_from_file_location("mec_alg", _ALG_PATH)
_mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
spec.loader.exec_module(_mod)

MinimumEnclosingCircleSimulation = _mod.MinimumEnclosingCircleSimulation
_in_circle = _mod._in_circle
_circle_2 = _mod._circle_2
_circle_3 = _mod._circle_3


def _make_params(size=10, seed=0):
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


# --- helper tests ---

def test_circle_2_midpoint():
    c = _circle_2((0, 0), (4, 0))
    assert abs(c[0] - 2.0) < 1e-6
    assert abs(c[1] - 0.0) < 1e-6
    assert abs(c[2] - 2.0) < 1e-6


def test_in_circle_inside():
    c = (5.0, 5.0, 3.0)
    assert _in_circle(c, (5, 5))
    assert _in_circle(c, (6, 5))


def test_in_circle_outside():
    c = (5.0, 5.0, 3.0)
    assert not _in_circle(c, (0, 0))


# --- metadata ---

def test_metadata_slug():
    alg = MinimumEnclosingCircleSimulation()
    assert alg.metadata().slug == "minimum-enclosing-circle"


def test_metadata_category():
    alg = MinimumEnclosingCircleSimulation()
    assert alg.metadata().category == "computational-geometry"


def test_metadata_visualization():
    alg = MinimumEnclosingCircleSimulation()
    assert alg.metadata().visualization_type == "ARRAY_BARS"


# --- initialize ---

def test_initialize_array_length():
    alg = MinimumEnclosingCircleSimulation()
    state = alg.initialize(_make_params(10))
    assert len(state.array) == 10


def test_initialize_description_has_pts():
    alg = MinimumEnclosingCircleSimulation()
    state = alg.initialize(_make_params(10))
    assert "pts=" in state.description
    assert "n=10" in state.description


def test_initialize_sorted_empty():
    alg = MinimumEnclosingCircleSimulation()
    state = alg.initialize(_make_params(10))
    assert state.sorted_indices == frozenset()


# --- steps ---

def test_step_count():
    alg = MinimumEnclosingCircleSimulation()
    params = _make_params(10)
    states, _ = _collect(alg, params)
    # n-1 steps (one per point after the first)
    assert len(states) == 9


def test_all_points_enclosed_at_end():
    # The final circle should enclose all n points
    alg = MinimumEnclosingCircleSimulation()
    for seed in range(5):
        params = _make_params(10, seed)
        _, final = _collect(alg, params)
        # All n points should be in sorted_indices (inside circle)
        assert len(final.sorted_indices) == 10, f"seed={seed} failed"


def test_final_radius_positive():
    alg = MinimumEnclosingCircleSimulation()
    _, final = _collect(alg, _make_params(10))
    assert final.swaps > 0


def test_final_description_contains_center():
    alg = MinimumEnclosingCircleSimulation()
    _, final = _collect(alg, _make_params(10))
    assert "center=" in final.description
    assert "r=" in final.description


def test_different_seeds_different_radii():
    alg = MinimumEnclosingCircleSimulation()
    radii = set()
    for seed in range(5):
        _, final = _collect(alg, _make_params(10, seed))
        radii.add(final.swaps)
    assert len(radii) > 1


def test_outside_point_updates_circle():
    # When a point is outside, last_swap should be set (non-None)
    alg = MinimumEnclosingCircleSimulation()
    params = _make_params(15, seed=42)
    states, _ = _collect(alg, params)
    # At least one step should have last_swap set (point was outside)
    assert any(s.last_swap is not None for s in states)


def test_array_values_in_range():
    alg = MinimumEnclosingCircleSimulation()
    params = _make_params(10)
    states, final = _collect(alg, params)
    for s in states + [final]:
        for v in s.array:
            assert 1 <= v <= 99


def test_different_sizes():
    alg = MinimumEnclosingCircleSimulation()
    for n in [5, 10, 15]:
        params = _make_params(n)
        state = alg.initialize(params)
        assert len(state.array) == n
