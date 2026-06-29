"""Tests for Level-Order Traversal plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "level_order",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LevelOrderSimulation = _mod.LevelOrderSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 7, seed: int = 42):
    sim = LevelOrderSimulation()
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


class TestLevelOrderMetadata:
    def test_slug(self):
        assert LevelOrderSimulation().metadata().slug == "level-order"

    def test_category(self):
        assert LevelOrderSimulation().metadata().category == "tree"

    def test_visualization_type(self):
        assert LevelOrderSimulation().metadata().visualization_type == "TREE"


class TestLevelOrderCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_all_nodes_visited(self, seed: int):
        initial, _, final = run(7, seed=seed)
        assert len(final.visited) == len(initial.nodes)

    @pytest.mark.parametrize("seed", range(8))
    def test_root_visited_first(self, seed: int):
        initial, frames, _ = run(7, seed=seed)
        root = initial.frontier[0]
        assert frames[0].current == root

    def test_frame_count_equals_node_count(self):
        initial, frames, _ = run(7)
        assert len(frames) == len(initial.nodes)

    def test_path_length_equals_node_count(self):
        initial, _, final = run(7)
        assert len(final.path) == len(initial.nodes)

    def test_root_in_path(self):
        initial, _, final = run(7)
        assert initial.frontier[0] in final.path


class TestLevelOrderFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_visited_grows_monotonically(self):
        _, frames, _ = run(7)
        for i in range(len(frames) - 1):
            assert len(frames[i].visited) <= len(frames[i + 1].visited)
