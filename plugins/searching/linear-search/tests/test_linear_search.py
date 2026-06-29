"""Tests for Linear Search plugin."""
import importlib.util
import sys
from pathlib import Path
from typing import List

# Resolve SDK and load algorithm module in isolation
sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "linear_search_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LinearSearchSimulation = _mod.LinearSearchSimulation

from algorithm_atlas_sdk import SearchState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def make_params(**kwargs) -> SimulationParams:
    defaults = {"seed": 42, "inputs": {"array_size": 15, "target_position": "middle"}}
    defaults.update(kwargs)
    if "inputs" in kwargs:
        defaults["inputs"] = kwargs["inputs"]
    return SimulationParams(**defaults)


def test_metadata():
    sim = LinearSearchSimulation()
    meta = sim.metadata()
    assert meta.slug == "linear-search"
    assert meta.category == "searching"
    assert meta.visualization_type == "ARRAY_BARS_SEARCH"


def test_found_middle():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert isinstance(final, SearchState)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_found_first():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 15, "target_position": "first"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target
    # Finding the first element takes only 1 comparison
    assert final.comparisons == 1


def test_found_last():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 15, "target_position": "last"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
    assert final.array[final.found_at] == final.target


def test_not_found():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 20, "target_position": "missing"})
    final = harness.get_terminal_state(params)
    assert final.found_at is None
    # Must examine all elements
    assert final.comparisons == len(final.array)


def test_comparisons_monotone_increasing():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 10, "target_position": "last"})
    frames: List[SearchState] = harness.run_to_completion(params)
    cmp_values = [f.comparisons for f in frames]
    for a, b in zip(cmp_values, cmp_values[1:]):
        assert b >= a, "comparisons should never decrease"


def test_eliminated_grows_monotonically():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 12, "target_position": "missing"})
    frames: List[SearchState] = harness.run_to_completion(params)
    prev_elim = frozenset()
    for f in frames:
        assert f.eliminated >= prev_elim
        prev_elim = f.eliminated


def test_array_unchanged_throughout():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 10, "target_position": "middle"})
    frames: List[SearchState] = harness.run_to_completion(params)
    first_arr = frames[0].array
    for f in frames:
        assert f.array == first_arr, "linear search must not modify the array"


def test_target_consistent_throughout():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 10, "target_position": "first"})
    frames: List[SearchState] = harness.run_to_completion(params)
    target = frames[0].target
    for f in frames:
        assert f.target == target


def test_deterministic():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 15, "target_position": "middle"})
    harness.assert_deterministic(params)


def test_json_serializable():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 12, "target_position": "last"})
    harness.assert_json_serializable(params)


def test_no_low_high_for_linear():
    """Linear search doesn't use low/high bounds."""
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 10, "target_position": "middle"})
    frames: List[SearchState] = harness.run_to_completion(params)
    for f in frames:
        assert f.low is None
        assert f.high is None


def test_small_array():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 3, "target_position": "first"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None


def test_found_at_correct_value():
    """found_at index must point to target value in the array."""
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    for pos in ("first", "middle", "last"):
        params = make_params(inputs={"array_size": 20, "target_position": pos})
        final = harness.get_terminal_state(params)
        assert final.found_at is not None
        assert final.array[final.found_at] == final.target


def test_missing_all_eliminated():
    """When target not found, all indices should be in eliminated set at end."""
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 10, "target_position": "missing"})
    final = harness.get_terminal_state(params)
    assert final.found_at is None
    assert final.eliminated == frozenset(range(len(final.array)))


def test_terminal_state_no_current():
    """Terminal state should have current=None (not actively examining)."""
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 10, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.current is None


def test_different_seeds_produce_different_arrays():
    sim = LinearSearchSimulation()
    p1 = make_params(seed=1, inputs={"array_size": 20, "target_position": "middle"})
    p2 = make_params(seed=99, inputs={"array_size": 20, "target_position": "middle"})
    s1 = sim.initialize(p1)
    s2 = sim.initialize(p2)
    # Different seeds should (with overwhelming probability) produce different arrays
    assert s1.array != s2.array


def test_minimum_frames():
    """Should produce at least 2 frames (at least one probe + terminal)."""
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 5, "target_position": "middle"})
    frames: List[SearchState] = harness.run_to_completion(params)
    assert len(frames) >= 2


def test_descriptions_nonempty():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 8, "target_position": "last"})
    frames: List[SearchState] = harness.run_to_completion(params)
    for f in frames:
        assert isinstance(f.description, str) and len(f.description) > 0


def test_larger_array():
    harness = AlgorithmTestHarness(LinearSearchSimulation())
    params = make_params(inputs={"array_size": 50, "target_position": "middle"})
    final = harness.get_terminal_state(params)
    assert final.found_at is not None
