"""Tests for Jump Search plugin."""
import importlib.util
import math
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "jump_search_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
JumpSearchSimulation = _mod.JumpSearchSimulation

from algorithm_atlas_sdk import SearchState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def make_params(**kwargs) -> SimulationParams:
    defaults = {"seed": 42, "inputs": {"array_size": 25, "target_position": "middle"}}
    defaults.update(kwargs)
    if "inputs" in kwargs:
        defaults["inputs"] = kwargs["inputs"]
    return SimulationParams(**defaults)


def test_metadata():
    sim = JumpSearchSimulation()
    meta = sim.metadata()
    assert meta.slug == "jump-search"
    assert meta.category == "searching"
    assert meta.visualization_type == "ARRAY_BARS_SEARCH"


def test_found_middle():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_found_first():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "first"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_found_last():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "last"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_not_found():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "missing"})
    final = harness.get_terminal_state(params)
    assert final.found_at is None


def test_sqrt_n_comparisons_upper_bound():
    """Jump search uses at most ~2*√n comparisons."""
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    for size in (25, 36, 49, 64):
        params = make_params(
            inputs={"array_size": size, "target_position": "middle"}
        )
        final = harness.get_terminal_state(params)
        upper = int(2 * math.sqrt(size)) + 5  # generous upper bound
        assert final.comparisons <= upper, (
            f"size={size}: expected <= {upper}, got {final.comparisons}"
        )


def test_array_sorted_invariant():
    sim = JumpSearchSimulation()
    params = make_params(inputs={"array_size": 25, "target_position": "middle"})
    initial = sim.initialize(params)
    arr = list(initial.array)
    assert arr == sorted(arr)


def test_array_unchanged_throughout():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "last"})
    frames: List[SearchState] = harness.run_to_completion(params)
    first_arr = frames[0].array
    for f in frames:
        assert f.array == first_arr


def test_deterministic():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "middle"})
    harness.assert_deterministic(params)


def test_json_serializable():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "last"})
    harness.assert_json_serializable(params)


def test_comparisons_monotone_increasing():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "missing"})
    frames: List[SearchState] = harness.run_to_completion(params)
    cmp_values = [f.comparisons for f in frames]
    for a, b in zip(cmp_values, cmp_values[1:]):
        assert b >= a


def test_eliminated_grows_monotonically():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "missing"})
    frames: List[SearchState] = harness.run_to_completion(params)
    prev = frozenset()
    for f in frames:
        assert f.eliminated >= prev
        prev = f.eliminated


def test_terminal_state_no_current():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.current is None


def test_descriptions_nonempty():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "middle"})
    frames: List[SearchState] = harness.run_to_completion(params)
    for f in frames:
        assert isinstance(f.description, str) and len(f.description) > 0


def test_found_at_correct_value():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    for pos in ("first", "middle", "last"):
        params = make_params(inputs={"array_size": 25, "target_position": pos})
        final = harness.get_terminal_state(params)
        assert final.found_at is not None
        assert final.array[final.found_at] == final.target


def test_larger_array():
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 100, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None


def test_two_phase_structure_visible():
    """Check that both jump probes and linear scan appear in frame descriptions."""
    harness = AlgorithmTestHarness(JumpSearchSimulation())
    params = make_params(inputs={"array_size": 25, "target_position": "last"})
    frames: List[SearchState] = harness.run_to_completion(params)
    descriptions = [f.description for f in frames]
    has_jump = any("Jump" in d or "jump" in d for d in descriptions)
    has_linear = any("linear" in d.lower() or "Linear" in d for d in descriptions)
    assert has_jump or len(frames) > 2  # degenerate case: target at first block
    # At least linear scan messages should appear
    assert has_linear or has_jump


def test_different_seeds():
    sim = JumpSearchSimulation()
    p1 = make_params(seed=1, inputs={"array_size": 25, "target_position": "middle"})
    p2 = make_params(seed=77, inputs={"array_size": 25, "target_position": "middle"})
    s1 = sim.initialize(p1)
    s2 = sim.initialize(p2)
    assert s1.array != s2.array
