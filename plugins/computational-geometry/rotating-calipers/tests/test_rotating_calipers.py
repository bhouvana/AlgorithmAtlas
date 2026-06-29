"""Tests for Rotating Calipers plugin."""
import importlib.util
import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "rot_cal_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

RotatingCaliperSimulation = mod.RotatingCaliperSimulation
_HULL = mod._HULL
_dist = mod._dist
_dist2 = mod._dist2
_rotating_calipers_steps = mod._rotating_calipers_steps


def _brute_force_diameter(hull):
    """O(n^2) brute force diameter."""
    n = len(hull)
    return max(_dist(hull[i], hull[j]) for i in range(n) for j in range(i + 1, n))


def _make_plugin(seed=0):
    plugin = RotatingCaliperSimulation()

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
    p = RotatingCaliperSimulation()
    assert p.metadata().slug == "rotating-calipers"


def test_metadata_category():
    p = RotatingCaliperSimulation()
    assert p.metadata().category == "computational-geometry"


def test_brute_force_diameter():
    d = _brute_force_diameter(_HULL)
    assert d > 0


def test_rotating_calipers_matches_brute_force():
    steps = _rotating_calipers_steps(_HULL)
    rc_diameter = max(s[2] for s in steps)
    bf_diameter = _brute_force_diameter(_HULL)
    assert abs(rc_diameter - bf_diameter) < 1e-6


def test_final_swaps_encodes_diameter():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    bf_diameter = _brute_force_diameter(_HULL)
    # swaps = int(diameter * 100)
    assert abs(final.swaps / 100.0 - bf_diameter) < 0.01


def test_steps_produced():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    steps = _rotating_calipers_steps(_HULL)
    # initial + len(steps) step states + final = len(steps) + 2
    assert len(states) == len(steps) + 2


def test_all_array_values_in_range():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    for s in states:
        for v in s.array:
            assert 1 <= v <= 99


def test_final_description_mentions_diameter():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert "Diameter" in final.description or "diameter" in final.description


def test_max_step_marked_as_max():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    step_states = states[1:-1]
    max_step = max(step_states, key=lambda s: s.swaps)
    assert "MAX" in max_step.description


def test_hull_is_valid_polygon():
    assert len(_HULL) >= 3
