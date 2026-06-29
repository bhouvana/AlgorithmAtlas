"""Tests for Interpolation Search plugin."""
import importlib.util
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "interpolation_search_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
InterpolationSearchSimulation = _mod.InterpolationSearchSimulation

from algorithm_atlas_sdk import SearchState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def make_params(**kwargs) -> SimulationParams:
    defaults = {"seed": 42, "inputs": {"array_size": 20, "target_position": "middle"}}
    defaults.update(kwargs)
    if "inputs" in kwargs:
        defaults["inputs"] = kwargs["inputs"]
    return SimulationParams(**defaults)


def test_metadata():
    sim = InterpolationSearchSimulation()
    meta = sim.metadata()
    assert meta.slug == "interpolation-search"
    assert meta.category == "searching"
    assert meta.visualization_type == "ARRAY_BARS_SEARCH"


def test_found_middle():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_found_first():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "first"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_found_last():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "last"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_not_found():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "missing"})
    final = harness.get_terminal_state(params)
    assert final.found_at is None


def test_array_sorted():
    sim = InterpolationSearchSimulation()
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    initial = sim.initialize(params)
    arr = list(initial.array)
    assert arr == sorted(arr)


def test_array_unchanged_throughout():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "first"})
    frames: List[SearchState] = harness.run_to_completion(params)
    first_arr = frames[0].array
    for f in frames:
        assert f.array == first_arr


def test_deterministic():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    harness.assert_deterministic(params)


def test_json_serializable():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "last"})
    harness.assert_json_serializable(params)


def test_comparisons_monotone_increasing():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "missing"})
    frames: List[SearchState] = harness.run_to_completion(params)
    cmp_values = [f.comparisons for f in frames]
    for a, b in zip(cmp_values, cmp_values[1:]):
        assert b >= a


def test_eliminated_grows_monotonically():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "missing"})
    frames: List[SearchState] = harness.run_to_completion(params)
    prev = frozenset()
    for f in frames:
        assert f.eliminated >= prev
        prev = f.eliminated


def test_probe_within_active_range():
    """Every probe (current != None) must be within [low, high] when those are set."""
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    frames: List[SearchState] = harness.run_to_completion(params)
    for f in frames:
        if f.current is not None and f.low is not None and f.high is not None:
            assert f.low <= f.current <= f.high


def test_terminal_no_current():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.current is None


def test_descriptions_nonempty():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 8, "target_position": "middle"})
    frames: List[SearchState] = harness.run_to_completion(params)
    for f in frames:
        assert isinstance(f.description, str) and len(f.description) > 0


def test_all_positions_found():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    for pos in ("first", "middle", "last"):
        params = make_params(inputs={"array_size": 20, "target_position": pos})
        final = harness.get_terminal_state(params)
        assert final.found_at is not None, f"Expected found for '{pos}'"
        assert final.array[final.found_at] == final.target


def test_interpolation_probe_description():
    """Probe frames should mention 'interpolated' in description."""
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    frames: List[SearchState] = harness.run_to_completion(params)
    probe_frames = [f for f in frames if f.current is not None]
    assert len(probe_frames) >= 1
    # At least one probe should mention interpolated
    assert any("interpolated" in f.description.lower() for f in probe_frames)


def test_larger_array():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 60, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None


def test_small_array():
    harness = AlgorithmTestHarness(InterpolationSearchSimulation())
    params = make_params(inputs={"array_size": 3, "target_position": "first"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
