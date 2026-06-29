"""Tests for Subsets (Power Set) plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "subsets",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SubsetsSimulation = _mod.SubsetsSimulation

from algorithm_atlas_sdk import SimulationParams


def run(size: int = 4, seed: int = 42):
    sim = SubsetsSimulation()
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


class TestSubsetsMetadata:
    def test_slug(self):
        assert SubsetsSimulation().metadata().slug == "subsets"

    def test_category(self):
        assert SubsetsSimulation().metadata().category == "backtracking"

    def test_visualization_type(self):
        assert SubsetsSimulation().metadata().visualization_type == "ARRAY_BARS_SEARCH"


class TestSubsetsCorrectness:
    @pytest.mark.parametrize("size", [3, 4, 5])
    def test_correct_count(self, size: int):
        _, _, final = run(size)
        # target field stores subset count at end
        assert final.target == 2 ** size

    def test_array_unchanged(self):
        initial, _, final = run(4)
        assert initial.array == final.array

    def test_has_frames(self):
        _, frames, _ = run(4)
        assert len(frames) > 0

    @pytest.mark.parametrize("seed", range(5))
    def test_count_stable_across_seeds(self, seed: int):
        _, _, final = run(4, seed=seed)
        assert final.target == 16  # 2^4


class TestSubsetsFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(4)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_descriptions_mention_subset(self):
        _, frames, _ = run(3)
        subset_frames = [f for f in frames if "subset" in f.description.lower() or "[" in f.description]
        assert len(subset_frames) > 0
