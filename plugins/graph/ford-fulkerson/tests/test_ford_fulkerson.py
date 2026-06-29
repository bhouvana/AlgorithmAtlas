"""Tests for Ford-Fulkerson Max Flow plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "ford_fulkerson",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
FordFulkersonSimulation = _mod.FordFulkersonSimulation
_NETWORKS = _mod._NETWORKS

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = FordFulkersonSimulation()
    params = SimulationParams(seed=seed, inputs={}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


class TestFFMetadata:
    def test_slug(self):
        assert FordFulkersonSimulation().metadata().slug == "ford-fulkerson"

    def test_category(self):
        assert FordFulkersonSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert FordFulkersonSimulation().metadata().visualization_type == "GRAPH"


class TestFFCorrectness:
    @pytest.mark.parametrize("seed", range(len(_NETWORKS)))
    def test_correct_max_flow(self, seed: int):
        initial, _, final = run(seed)
        expected = int(initial.description.split("expected=")[1])
        result = int(final.description.split("Max flow = ")[1])
        assert result == expected, f"seed={seed}: expected {expected}, got {result}"

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) >= 1

    @pytest.mark.parametrize("seed", range(len(_NETWORKS)))
    def test_flow_is_positive(self, seed: int):
        _, _, final = run(seed)
        flow = int(final.description.split("Max flow = ")[1])
        assert flow > 0


class TestFFFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_frame_paths_are_valid(self):
        initial, frames, final = run(0)
        node_ids = {nd.node_id for nd in initial.nodes}
        for f in frames:
            for nd in f.path:
                assert nd in node_ids
