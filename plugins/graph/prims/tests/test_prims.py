"""Tests for Prim's MST plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "prims",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PrimsSimulation = _mod.PrimsSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 0):
    sim = PrimsSimulation()
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


class TestPrimsMetadata:
    def test_slug(self):
        assert PrimsSimulation().metadata().slug == "prims"

    def test_category(self):
        assert PrimsSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert PrimsSimulation().metadata().visualization_type == "GRAPH"


class TestPrimsCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_correct_mst_weight(self, seed: int):
        initial, _, final = run(6, seed)
        expected = float(initial.description.split("expected_weight=")[1])
        result = float(final.description.split("total weight=")[1])
        assert abs(result - expected) < 1e-9, f"seed={seed}: expected {expected}, got {result}"

    @pytest.mark.parametrize("seed", range(8))
    def test_all_nodes_in_mst(self, seed: int):
        initial, _, final = run(6, seed)
        n = len(initial.nodes)
        assert len(final.visited) == n

    def test_has_n_minus_1_frames(self):
        initial, frames, _ = run(6)
        n = len(initial.nodes)
        assert len(frames) == n - 1


class TestPrimsFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
