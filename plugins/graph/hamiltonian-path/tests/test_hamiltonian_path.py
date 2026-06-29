"""Tests for Hamiltonian Path plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "hamiltonian_path",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
HamiltonianPathSimulation = _mod.HamiltonianPathSimulation
_GRAPHS = _mod._GRAPHS

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = HamiltonianPathSimulation()
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


class TestHamiltonianMetadata:
    def test_slug(self):
        assert HamiltonianPathSimulation().metadata().slug == "hamiltonian-path"

    def test_category(self):
        assert HamiltonianPathSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert HamiltonianPathSimulation().metadata().visualization_type == "GRAPH"


class TestHamiltonianCorrectness:
    @pytest.mark.parametrize("seed", range(len(_GRAPHS)))
    def test_visits_all_nodes(self, seed: int):
        initial, _, final = run(seed)
        n = len(initial.nodes)
        assert len(final.path) == n, f"seed={seed}: only {len(final.path)}/{n} nodes visited"

    @pytest.mark.parametrize("seed", range(len(_GRAPHS)))
    def test_no_repeated_nodes(self, seed: int):
        _, _, final = run(seed)
        assert len(set(final.path)) == len(final.path)

    @pytest.mark.parametrize("seed", range(len(_GRAPHS)))
    def test_path_uses_valid_edges(self, seed: int):
        initial, _, final = run(seed)
        edge_set = {(ed.source, ed.target) for ed in initial.edges}
        edge_set |= {(ed.target, ed.source) for ed in initial.edges}
        path = final.path
        for i in range(1, len(path)):
            assert (path[i-1], path[i]) in edge_set, f"Invalid edge {path[i-1]}-{path[i]}"

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) > 0


class TestHamiltonianFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
