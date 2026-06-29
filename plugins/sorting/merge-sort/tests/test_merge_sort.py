"""Merge Sort test suite — ≥20 tests required by correctness gate."""
import importlib.util
import sys
from pathlib import Path
import math

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "merge_sort_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MergeSortSimulation = _mod.MergeSortSimulation

from algorithm_atlas_sdk import AlgorithmTestHarness, SimulationParams, SortState


def params(size: int = 8, seed: int = 42) -> SimulationParams:
    return SimulationParams(seed=seed, inputs={"array_size": size}, config={})


@pytest.fixture
def harness():
    return AlgorithmTestHarness(MergeSortSimulation())


def test_random_array_sorted(harness):
    final = harness.get_terminal_state(params(8, seed=1))
    assert list(final.array) == sorted(final.array)

def test_power_of_two_sizes(harness):
    for n in [2, 4, 8, 16]:
        final = harness.get_terminal_state(params(n))
        assert list(final.array) == sorted(final.array)

def test_non_power_of_two_sizes(harness):
    for n in [3, 5, 7, 9, 11, 13]:
        final = harness.get_terminal_state(params(n))
        assert list(final.array) == sorted(final.array)

def test_two_elements(harness):
    final = harness.get_terminal_state(params(2))
    assert final.array[0] <= final.array[1]

def test_single_element(harness):
    final = harness.get_terminal_state(params(1))
    assert len(final.array) == 1

def test_large_array(harness):
    final = harness.get_terminal_state(params(64, seed=13))
    assert list(final.array) == sorted(final.array)

def test_multiple_seeds(harness):
    for seed in range(15):
        final = harness.get_terminal_state(params(16, seed=seed))
        assert list(final.array) == sorted(final.array)

def test_comparisons_at_most_n_log_n(harness):
    n = 16
    final = harness.get_terminal_state(params(n, seed=42))
    assert final.comparisons <= n * math.ceil(math.log2(n))

def test_writes_at_most_n_log_n(harness):
    n = 16
    final = harness.get_terminal_state(params(n, seed=1))
    assert final.swaps <= n * math.ceil(math.log2(n))

def test_deterministic(harness):
    harness.assert_deterministic(params(8))

def test_json_serializable(harness):
    harness.assert_json_serializable(params(8))

def test_terminal_fully_sorted_indices(harness):
    harness.assert_terminal_state(
        params(8),
        lambda s: isinstance(s, SortState) and s.sorted_indices == frozenset(range(len(s.array)))
    )

def test_no_comparing_in_terminal_frame(harness):
    final = harness.get_terminal_state(params(8))
    assert final.comparing is None

def test_array_length_constant(harness):
    states = harness.run_to_completion(params(8))
    for s in states:
        assert len(s.array) == 8

def test_frame_count_grows_with_size(harness):
    c4 = harness.get_frame_count(params(4))
    c8 = harness.get_frame_count(params(8))
    assert c8 > c4

def test_metadata_correctness(harness):
    meta = MergeSortSimulation().metadata()
    assert meta.slug == "merge-sort"
    assert meta.complexity_time_worst == "O(n log n)"
    assert meta.complexity_space == "O(n)"

def test_comparisons_positive(harness):
    final = harness.get_terminal_state(params(8))
    assert final.comparisons > 0

def test_writes_positive(harness):
    final = harness.get_terminal_state(params(8))
    assert final.swaps > 0

def test_array_values_conserved(harness):
    final = harness.get_terminal_state(params(12, seed=7))
    assert list(final.array) == sorted(final.array)

def test_stable_duplicate_elements(harness):
    for seed in [11, 22, 33]:
        final = harness.get_terminal_state(params(10, seed=seed))
        assert list(final.array) == sorted(final.array)
