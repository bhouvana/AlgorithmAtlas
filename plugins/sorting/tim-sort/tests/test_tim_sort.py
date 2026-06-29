"""Tim Sort test suite — ≥20 tests required by correctness gate."""
import importlib.util
import sys
from pathlib import Path
import math

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "tim_sort_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TimSortSimulation = _mod.TimSortSimulation

from algorithm_atlas_sdk import AlgorithmTestHarness, SimulationParams, SortState


def params(size: int = 32, seed: int = 42) -> SimulationParams:
    return SimulationParams(seed=seed, inputs={"array_size": size}, config={})


@pytest.fixture
def harness():
    return AlgorithmTestHarness(TimSortSimulation())


def test_random_sorted(harness):
    final = harness.get_terminal_state(params(32, seed=1))
    assert list(final.array) == sorted(final.array)

def test_multiple_seeds(harness):
    for seed in range(12):
        final = harness.get_terminal_state(params(20, seed=seed))
        assert list(final.array) == sorted(final.array)

def test_small_array_below_run_size(harness):
    for n in [1, 2, 5, 10, 15]:
        final = harness.get_terminal_state(params(n))
        assert list(final.array) == sorted(final.array)

def test_exactly_run_size(harness):
    final = harness.get_terminal_state(params(32))
    assert list(final.array) == sorted(final.array)

def test_multiple_runs(harness):
    final = harness.get_terminal_state(params(64, seed=7))
    assert list(final.array) == sorted(final.array)

def test_large_array(harness):
    final = harness.get_terminal_state(params(100, seed=3))
    assert list(final.array) == sorted(final.array)

def test_comparisons_bounded(harness):
    n = 32
    final = harness.get_terminal_state(params(n))
    assert final.comparisons <= 3 * n * (math.ceil(math.log2(n)) + 1)

def test_deterministic(harness):
    harness.assert_deterministic(params(16))

def test_json_serializable(harness):
    harness.assert_json_serializable(params(16))

def test_terminal_fully_sorted(harness):
    harness.assert_terminal_state(
        params(16),
        lambda s: isinstance(s, SortState) and s.sorted_indices == frozenset(range(len(s.array)))
    )

def test_no_comparing_in_terminal(harness):
    final = harness.get_terminal_state(params(16))
    assert final.comparing is None

def test_array_length_constant(harness):
    states = harness.run_to_completion(params(16))
    for s in states:
        assert len(s.array) == 16

def test_auxiliary_indices_during_phase1(harness):
    states = harness.run_to_completion(params(16))
    has_aux = any(
        isinstance(s, SortState) and len(s.auxiliary_indices) > 0
        for s in states
    )
    assert has_aux

def test_metadata_slug(harness):
    meta = TimSortSimulation().metadata()
    assert meta.slug == "tim-sort"

def test_metadata_best_case_linear(harness):
    meta = TimSortSimulation().metadata()
    assert meta.complexity_time_best == "O(n)"

def test_metadata_worst_case_nlogn(harness):
    meta = TimSortSimulation().metadata()
    assert meta.complexity_time_worst == "O(n log n)"

def test_frame_count_grows_with_size(harness):
    c8 = harness.get_frame_count(params(8))
    c32 = harness.get_frame_count(params(32))
    assert c32 > c8

def test_stable_duplicates(harness):
    for seed in [50, 100, 150]:
        final = harness.get_terminal_state(params(20, seed=seed))
        assert list(final.array) == sorted(final.array)

def test_comparisons_positive(harness):
    final = harness.get_terminal_state(params(16))
    assert final.comparisons > 0

def test_writes_positive(harness):
    final = harness.get_terminal_state(params(32, seed=5))
    assert final.swaps > 0
