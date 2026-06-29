"""Tests for Eulerian Path plugin."""
from __future__ import annotations

import importlib.util
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "euler_path",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
EulerPathSimulation = _mod.EulerPathSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 5, seed: int = 42):
    sim = EulerPathSimulation()
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


def edges_from_path(path: tuple) -> List[tuple]:
    return [(path[i], path[i + 1]) for i in range(len(path) - 1)]


class TestEulerPathMetadata:
    def test_slug(self):
        assert EulerPathSimulation().metadata().slug == "euler-path"

    def test_category(self):
        assert EulerPathSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert EulerPathSimulation().metadata().visualization_type == "GRAPH"


class TestEulerPathCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_all_edges_traversed(self, seed: int):
        initial, _, final = run(5, seed=seed)
        total_edges = int(initial.distances["total_edges"])
        traversed = int(final.distances["edge_count"])
        assert traversed == total_edges, (
            f"seed={seed}: traversed {traversed}/{total_edges}"
        )

    @pytest.mark.parametrize("seed", range(8))
    def test_path_uses_valid_edges(self, seed: int):
        initial, _, final = run(5, seed=seed)
        # Build adjacency from original edges
        edge_multi: Dict = defaultdict(int)
        for e in initial.edges:
            key = (min(e.source, e.target), max(e.source, e.target))
            edge_multi[key] += 1

        # Count usage in path
        path = final.path
        used: Dict = defaultdict(int)
        for a, b in edges_from_path(path):
            key = (min(a, b), max(a, b))
            used[key] += 1

        for key, count in used.items():
            assert count <= edge_multi[key], f"Edge {key} used {count} times but only has multiplicity {edge_multi[key]}"

    @pytest.mark.parametrize("seed", range(8))
    def test_path_is_contiguous(self, seed: int):
        initial, _, final = run(5, seed=seed)
        # Build adjacency
        adj = defaultdict(set)
        for e in initial.edges:
            adj[e.source].add(e.target)
            adj[e.target].add(e.source)
        # Each consecutive pair in path must be adjacent
        path = final.path
        for i in range(len(path) - 1):
            assert path[i + 1] in adj[path[i]], (
                f"Non-adjacent step {path[i]}→{path[i+1]} in path"
            )

    def test_has_frames(self):
        _, frames, _ = run(5)
        assert len(frames) > 0


class TestEulerPathFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(5)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
