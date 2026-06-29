"""Tests for Graph Coloring plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "graph_coloring",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
GraphColoringSimulation = _mod.GraphColoringSimulation
_GRAPHS = _mod._GRAPHS

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = GraphColoringSimulation()
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


class TestGraphColoringMetadata:
    def test_slug(self):
        assert GraphColoringSimulation().metadata().slug == "graph-coloring"

    def test_category(self):
        assert GraphColoringSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert GraphColoringSimulation().metadata().visualization_type == "GRAPH"


class TestGraphColoringCorrectness:
    @pytest.mark.parametrize("seed", range(len(_GRAPHS)))
    def test_valid_coloring(self, seed: int):
        nodes_list, edges_list, chi = _GRAPHS[seed]
        _, _, final = run(seed)
        # Parse coloring from description
        coloring_str = final.description.split(": {")[1].rstrip("}")
        coloring = {}
        for pair in coloring_str.split(", "):
            k, v = pair.split(": ")
            coloring[k.strip("'")] = int(v)
        # Verify no adjacent vertices have same color
        for u, v in edges_list:
            assert coloring[u] != coloring[v], f"seed={seed}: {u} and {v} have same color {coloring[u]}"

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) > 0


class TestGraphColoringFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
