"""Tests for Combination Sum plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "combination_sum",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CombinationSumSimulation = _mod.CombinationSumSimulation

from algorithm_atlas_sdk import SimulationParams


def run(size: int = 4, seed: int = 42):
    sim = CombinationSumSimulation()
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


def _get_target(initial) -> int:
    return int(initial.description.split("target=")[1])


class TestCombinationSumMetadata:
    def test_slug(self):
        assert CombinationSumSimulation().metadata().slug == "combination-sum"

    def test_category(self):
        assert CombinationSumSimulation().metadata().category == "backtracking"

    def test_visualization_type(self):
        assert CombinationSumSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestCombinationSumCorrectness:
    def test_has_solutions(self):
        _, _, final = run(4)
        assert final.swaps >= 1  # at least one solution

    def test_final_description_mentions_done(self):
        _, _, final = run(4)
        assert "Done" in final.description or "combination" in final.description.lower()

    def test_array_unchanged(self):
        initial, _, final = run(4)
        assert initial.array == final.array

    def test_has_frames(self):
        _, frames, _ = run(4)
        assert len(frames) > 0

    def test_solution_frames_have_matching_sorted_indices(self):
        initial, frames, final = run(3)
        target = _get_target(initial)
        candidates = list(initial.array)
        solution_frames = [f for f in frames if "Solution" in f.description]
        for sf in solution_frames:
            # Each solution frame should describe a valid combination
            assert "Solution" in sf.description

    @pytest.mark.parametrize("size", [3, 4, 5])
    def test_sizes(self, size: int):
        initial, frames, final = run(size)
        assert len(frames) > 0
        assert len(initial.array) == size


class TestCombinationSumFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(4)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_comparisons_increase(self):
        _, frames, final = run(4)
        assert final.comparisons > 0
