"""Quick Sort test suite — ≥20 tests required by correctness gate."""
import importlib.util
import sys
from pathlib import Path
import math

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "quick_sort_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
QuickSortSimulation = _mod.QuickSortSimulation

from algorithm_atlas_sdk import AlgorithmTestHarness, SimulationParams, SortState


def params(size: int = 8, seed: int = 42, pivot: str = "median_of_three") -> SimulationParams:
    return SimulationParams(
        seed=seed,
        inputs={"array_size": size, "pivot_strategy": pivot},
        config={},
    )


@pytest.fixture
def harness():
    return AlgorithmTestHarness(QuickSortSimulation())


def test_random_array_sorted(harness):
    final = harness.get_terminal_state(params(8, seed=1))
    assert list(final.array) == sorted(final.array)

def test_multiple_seeds(harness):
    for seed in range(15):
        final = harness.get_terminal_state(params(10, seed=seed))
        assert list(final.array) == sorted(final.array)

def test_all_pivot_strategies(harness):
    for strategy in ["last", "first", "median_of_three"]:
        final = harness.get_terminal_state(params(10, seed=5, pivot=strategy))
        assert list(final.array) == sorted(final.array), f"Failed with pivot={strategy}"

def test_two_elements(harness):
    final = harness.get_terminal_state(params(2))
    assert final.array[0] <= final.array[1]

def test_single_element(harness):
    final = harness.get_terminal_state(params(1))
    assert len(final.array) == 1

def test_large_array(harness):
    final = harness.get_terminal_state(params(50, seed=9))
    assert list(final.array) == sorted(final.array)

def test_average_comparisons_reasonable(harness):
    n = 16
    final = harness.get_terminal_state(params(n, seed=42))
    assert final.comparisons <= 3 * n * math.ceil(math.log2(n))

def test_terminal_all_sorted(harness):
    final = harness.get_terminal_state(params(8))
    assert final.sorted_indices == frozenset(range(len(final.array)))

def test_deterministic(harness):
    harness.assert_deterministic(params(8))

def test_json_serializable(harness):
    harness.assert_json_serializable(params(8))

def test_terminal_state_fully_sorted(harness):
    harness.assert_terminal_state(
        params(8),
        lambda s: isinstance(s, SortState) and s.sorted_indices == frozenset(range(len(s.array)))
    )

def test_no_comparing_in_terminal(harness):
    final = harness.get_terminal_state(params(8))
    assert final.comparing is None

def test_array_length_constant(harness):
    states = harness.run_to_completion(params(8))
    for s in states:
        assert len(s.array) == 8

def test_auxiliary_indices_contains_pivot(harness):
    states = harness.run_to_completion(params(8))
    has_pivot = any(
        isinstance(s, SortState) and len(s.auxiliary_indices) > 0
        for s in states
    )
    assert has_pivot

def test_metadata_correctness(harness):
    meta = QuickSortSimulation().metadata()
    assert meta.slug == "quick-sort"
    assert meta.complexity_time_worst == "O(n²)"

def test_frame_count_grows_with_size(harness):
    c4 = harness.get_frame_count(params(4))
    c8 = harness.get_frame_count(params(8))
    assert c8 > c4

def test_comparisons_non_negative(harness):
    final = harness.get_terminal_state(params(8))
    assert final.comparisons >= 0

def test_swaps_non_negative(harness):
    final = harness.get_terminal_state(params(8))
    assert final.swaps >= 0

def test_correct_for_size_1_each_strategy(harness):
    for strategy in ["last", "first", "median_of_three"]:
        final = harness.get_terminal_state(params(1, pivot=strategy))
        assert len(final.array) == 1
