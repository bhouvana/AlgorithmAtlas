"""Tests for Diameter of a Binary Tree plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "diameter",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
DiameterSimulation = _mod.DiameterSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 7, seed: int = 0):
    sim = DiameterSimulation()
    params = SimulationParams(seed=seed, inputs={"array_size": n}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestDiameterMetadata:
    def test_slug(self):
        assert DiameterSimulation().metadata().slug == "diameter"

    def test_category(self):
        assert DiameterSimulation().metadata().category == "tree"

    def test_visualization_type(self):
        assert DiameterSimulation().metadata().visualization_type == "TREE"


class TestDiameterCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_correct_diameter(self, seed: int):
        initial, _, final = run(7, seed)
        expected_diam = int(initial.description.split("Expected=")[1].split(" ")[0])
        result_diam = int(final.description.split("Diameter = ")[1].split(" ")[0])
        assert result_diam == expected_diam

    def test_has_frames(self):
        _, frames, _ = run(7)
        assert len(frames) >= 5  # at least n frames


class TestDiameterFrames:
    def test_all_nodes_visited(self):
        initial, _, final = run(7)
        n = len(initial.nodes)
        assert len(final.visited) == n

    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
