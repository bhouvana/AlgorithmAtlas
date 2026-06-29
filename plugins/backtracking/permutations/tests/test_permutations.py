"""Tests for Permutations plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "permutations",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PermutationsSimulation = _mod.PermutationsSimulation

from algorithm_atlas_sdk import SimulationParams


def run(size: int = 4, seed: int = 42):
    sim = PermutationsSimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": size}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestPermutationsMetadata:
    def test_slug(self):
        assert PermutationsSimulation().metadata().slug == "permutations"

    def test_category(self):
        assert PermutationsSimulation().metadata().category == "backtracking"

    def test_visualization_type(self):
        assert PermutationsSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestPermutationsCorrectness:
    def test_array_preserved_as_multiset(self):
        initial, _, final = run(4)
        assert sorted(initial.array) == sorted(final.array)

    def test_final_has_sorted_indices(self):
        _, _, final = run(4)
        assert len(final.sorted_indices) == 4

    @pytest.mark.parametrize("size", [3, 4, 5])
    def test_frame_count_positive(self, size: int):
        _, frames, _ = run(size)
        assert len(frames) > 0

    def test_size_3_has_6_solutions(self):
        _, frames, _ = run(3)
        solution_frames = [f for f in frames if f.description.startswith("Permutation #")]
        assert len(solution_frames) == 6  # 3! = 6

    def test_size_4_has_24_solutions(self):
        _, frames, _ = run(4)
        solution_frames = [f for f in frames if f.description.startswith("Permutation #")]
        assert len(solution_frames) == 24  # 4! = 24

    def test_swap_count_positive(self):
        _, _, final = run(4)
        assert final.swaps > 0

    @pytest.mark.parametrize("seed", range(5))
    def test_various_seeds(self, seed: int):
        initial, frames, final = run(4, seed=seed)
        assert sorted(initial.array) == sorted(final.array)


class TestPermutationsFrames:
    def test_has_frames(self):
        _, frames, _ = run(4)
        assert len(frames) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(4)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
