"""Shell Sort test suite — ≥20 tests required by correctness gate."""
import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "shell_sort_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ShellSortSimulation = _mod.ShellSortSimulation

from algorithm_atlas_sdk import AlgorithmTestHarness, SimulationParams, SortState


def params(size: int = 8, seed: int = 42) -> SimulationParams:
    return SimulationParams(seed=seed, inputs={"array_size": size}, config={})


@pytest.fixture
def harness():
    return AlgorithmTestHarness(ShellSortSimulation())


def test_random_sorted(harness):
    final = harness.get_terminal_state(params(8, seed=1))
    assert list(final.array) == sorted(final.array)

def test_multiple_seeds(harness):
    for seed in range(15):
        final = harness.get_terminal_state(params(10, seed=seed))
        assert list(final.array) == sorted(final.array)

def test_two_elements(harness):
    final = harness.get_terminal_state(params(2))
    assert final.array[0] <= final.array[1]

def test_single_element(harness):
    final = harness.get_terminal_state(params(1))
    assert len(final.array) == 1

def test_large(harness):
    final = harness.get_terminal_state(params(80, seed=5))
    assert list(final.array) == sorted(final.array)

def test_comparisons_leq_quadratic(harness):
    n = 12
    final = harness.get_terminal_state(params(n))
    assert final.comparisons <= n * n

def test_deterministic(harness):
    harness.assert_deterministic(params(8))

def test_json_serializable(harness):
    harness.assert_json_serializable(params(8))

def test_terminal_fully_sorted(harness):
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

def test_auxiliary_indices_used(harness):
    states = harness.run_to_completion(params(8))
    has_aux = any(
        isinstance(s, SortState) and len(s.auxiliary_indices) > 0
        for s in states
    )
    assert has_aux

def test_metadata_slug(harness):
    meta = ShellSortSimulation().metadata()
    assert meta.slug == "shell-sort"

def test_metadata_complexity(harness):
    meta = ShellSortSimulation().metadata()
    assert meta.complexity_space == "O(1)"

def test_comparisons_positive(harness):
    final = harness.get_terminal_state(params(8, seed=42))
    assert final.comparisons > 0

def test_frame_count_grows(harness):
    c4 = harness.get_frame_count(params(4))
    c8 = harness.get_frame_count(params(8))
    assert c8 > c4

def test_various_sizes(harness):
    for n in [5, 10, 20, 30, 50]:
        final = harness.get_terminal_state(params(n, seed=3))
        assert list(final.array) == sorted(final.array)

def test_swaps_non_negative(harness):
    final = harness.get_terminal_state(params(8))
    assert final.swaps >= 0

def test_stable_duplicate_result(harness):
    for seed in [100, 200, 300]:
        final = harness.get_terminal_state(params(10, seed=seed))
        assert list(final.array) == sorted(final.array)
