"""Tests for Morris Inorder Traversal plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "morris_traversal",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MorrisTraversalSimulation = _mod.MorrisTraversalSimulation
_inorder_sorted = _mod._inorder_sorted
_build_bst = _mod._build_bst

from algorithm_atlas_sdk import SimulationParams
import random


def run(n: int = 7, seed: int = 0):
    sim = MorrisTraversalSimulation()
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


class TestMorrisMetadata:
    def test_slug(self):
        assert MorrisTraversalSimulation().metadata().slug == "morris-traversal"

    def test_category(self):
        assert MorrisTraversalSimulation().metadata().category == "tree"

    def test_visualization_type(self):
        assert MorrisTraversalSimulation().metadata().visualization_type == "TREE"


class TestMorrisCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_inorder_sorted(self, seed: int):
        _, _, final = run(7, seed)
        path = [int(v) for v in final.path]
        assert path == sorted(path), f"seed={seed}: {path} is not sorted"

    @pytest.mark.parametrize("seed", range(10))
    def test_visits_all_nodes(self, seed: int):
        initial, _, final = run(7, seed)
        n = len(initial.nodes)
        assert len(final.path) == n

    def test_has_frames(self):
        _, frames, _ = run(7)
        assert len(frames) > 0


class TestMorrisFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
