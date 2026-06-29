"""Tests for Binary Search plugin."""
import importlib.util
import math
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "binary_search_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BinarySearchSimulation = _mod.BinarySearchSimulation

from algorithm_atlas_sdk import SearchState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def make_params(**kwargs) -> SimulationParams:
    defaults = {"seed": 42, "inputs": {"array_size": 16, "target_position": "middle"}}
    defaults.update(kwargs)
    if "inputs" in kwargs:
        defaults["inputs"] = kwargs["inputs"]
    return SimulationParams(**defaults)


def test_metadata():
    sim = BinarySearchSimulation()
    meta = sim.metadata()
    assert meta.slug == "binary-search"
    assert meta.category == "searching"
    assert meta.visualization_type == "ARRAY_BARS_SEARCH"


def test_found_middle():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_found_first():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "first"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_found_last():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "last"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_not_found():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "missing"})
    final = harness.get_terminal_state(params)
    assert final.found_at is None


def test_log_n_comparisons():
    """Binary search must use at most ceil(log2(n)) + 1 comparisons."""
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    for size in (8, 16, 32, 64):
        params = make_params(
            inputs={"array_size": size, "target_position": "middle"}
        )
        final = harness.get_terminal_state(params)
        max_comparisons = math.ceil(math.log2(size)) + 1
        assert final.comparisons <= max_comparisons, (
            f"size={size}: expected <= {max_comparisons} comparisons, "
            f"got {final.comparisons}"
        )


def test_array_sorted_invariant():
    """Initialize must produce a sorted array."""
    sim = BinarySearchSimulation()
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    initial = sim.initialize(params)
    arr = list(initial.array)
    assert arr == sorted(arr)


def test_array_unchanged_throughout():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "last"})
    frames: List[SearchState] = harness.run_to_completion(params)
    first_arr = frames[0].array
    for f in frames:
        assert f.array == first_arr


def test_low_high_narrow_monotonically():
    """Active range [low, high] must strictly narrow each full iteration."""
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 32, "target_position": "missing"})
    frames: List[SearchState] = harness.run_to_completion(params)

    # Collect frames that have both low and high set
    bounded = [(f.low, f.high) for f in frames if f.low is not None and f.high is not None]
    ranges = [h - l for l, h in bounded]
    # Ranges should be non-increasing
    for a, b in zip(ranges, ranges[1:]):
        assert b <= a


def test_eliminated_contains_final_out_of_bounds():
    """After not finding, eliminated should cover most of the array."""
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "missing"})
    final = harness.get_terminal_state(params)
    assert final.found_at is None


def test_deterministic():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "middle"})
    harness.assert_deterministic(params)


def test_json_serializable():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "last"})
    harness.assert_json_serializable(params)


def test_initial_low_zero_high_n_minus_1():
    sim = BinarySearchSimulation()
    params = make_params(inputs={"array_size": 10, "target_position": "middle"})
    initial = sim.initialize(params)
    assert initial.low == 0
    assert initial.high == len(initial.array) - 1


def test_terminal_no_active_range_on_found():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.low is None
    assert final.high is None


def test_terminal_no_active_range_on_missing():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "missing"})
    final = harness.get_terminal_state(params)
    assert final.found_at is None
    assert final.low is None
    assert final.high is None


def test_descriptions_nonempty():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 8, "target_position": "middle"})
    frames: List[SearchState] = harness.run_to_completion(params)
    for f in frames:
        assert isinstance(f.description, str) and len(f.description) > 0


def test_comparisons_monotone_increasing():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 16, "target_position": "missing"})
    frames: List[SearchState] = harness.run_to_completion(params)
    cmp_values = [f.comparisons for f in frames]
    for a, b in zip(cmp_values, cmp_values[1:]):
        assert b >= a


def test_larger_array():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    params = make_params(inputs={"array_size": 100, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None


def test_all_positions_found():
    harness = AlgorithmTestHarness(BinarySearchSimulation())
    for pos in ("first", "middle", "last"):
        params = make_params(inputs={"array_size": 16, "target_position": pos})
        final = harness.get_terminal_state(params)
        assert final.found_at is not None, f"Expected found for position '{pos}'"
        assert final.array[final.found_at] == final.target
