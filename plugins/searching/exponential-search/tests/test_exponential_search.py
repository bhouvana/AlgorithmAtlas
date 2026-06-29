"""Tests for Exponential Search plugin."""
import importlib.util
import math
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "exponential_search_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ExponentialSearchSimulation = _mod.ExponentialSearchSimulation

from algorithm_atlas_sdk import SearchState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def make_params(**kwargs) -> SimulationParams:
    defaults = {"seed": 42, "inputs": {"array_size": 20, "target_position": "middle"}}
    defaults.update(kwargs)
    if "inputs" in kwargs:
        defaults["inputs"] = kwargs["inputs"]
    return SimulationParams(**defaults)


def test_metadata():
    sim = ExponentialSearchSimulation()
    meta = sim.metadata()
    assert meta.slug == "exponential-search"
    assert meta.category == "searching"
    assert meta.visualization_type == "ARRAY_BARS_SEARCH"


def test_found_middle():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_found_first():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "first"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target
    # Finding first element takes only 1 comparison (index 0 check)
    assert final.comparisons == 1


def test_found_last():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "last"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_not_found():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "missing"})
    final = harness.get_terminal_state(params)
    assert final.found_at is None


def test_log_n_comparisons():
    """Exponential search is O(log n) total."""
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    for size in (16, 32, 64):
        params = make_params(
            inputs={"array_size": size, "target_position": "middle"}
        )
        final = harness.get_terminal_state(params)
        # Very generous: 2 * log2(n) + 5 covers both phases
        max_cmp = int(2 * math.log2(size)) + 10
        assert final.comparisons <= max_cmp, (
            f"size={size}: expected <= {max_cmp}, got {final.comparisons}"
        )


def test_array_sorted():
    sim = ExponentialSearchSimulation()
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    initial = sim.initialize(params)
    arr = list(initial.array)
    assert arr == sorted(arr)


def test_array_unchanged_throughout():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "last"})
    frames: List[SearchState] = harness.run_to_completion(params)
    first_arr = frames[0].array
    for f in frames:
        assert f.array == first_arr


def test_deterministic():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    harness.assert_deterministic(params)


def test_json_serializable():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "last"})
    harness.assert_json_serializable(params)


def test_comparisons_monotone_increasing():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "missing"})
    frames: List[SearchState] = harness.run_to_completion(params)
    cmp_values = [f.comparisons for f in frames]
    for a, b in zip(cmp_values, cmp_values[1:]):
        assert b >= a


def test_eliminated_grows_monotonically():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "missing"})
    frames: List[SearchState] = harness.run_to_completion(params)
    prev = frozenset()
    for f in frames:
        assert f.eliminated >= prev
        prev = f.eliminated


def test_two_phase_structure():
    """Descriptions should show both exponential probing and binary search."""
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 32, "target_position": "last"})
    frames: List[SearchState] = harness.run_to_completion(params)
    descriptions = " ".join(f.description for f in frames)
    assert "Exponential" in descriptions or "exponential" in descriptions.lower()
    assert "binary" in descriptions.lower() or "Binary" in descriptions


def test_terminal_no_current():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.current is None


def test_descriptions_nonempty():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 10, "target_position": "middle"})
    frames: List[SearchState] = harness.run_to_completion(params)
    for f in frames:
        assert isinstance(f.description, str) and len(f.description) > 0


def test_all_positions_found():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    for pos in ("first", "middle", "last"):
        params = make_params(inputs={"array_size": 20, "target_position": pos})
        final = harness.get_terminal_state(params)
        assert final.found_at is not None, f"Expected found for '{pos}'"
        assert final.array[final.found_at] == final.target


def test_larger_array():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 80, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None


def test_small_array():
    harness = AlgorithmTestHarness(ExponentialSearchSimulation())
    params = make_params(inputs={"array_size": 4, "target_position": "first"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
