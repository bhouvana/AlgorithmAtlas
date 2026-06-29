"""Tests for Topological Sort (Kahn's) plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "topo_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TopologicalSortSimulation = _mod.TopologicalSortSimulation

from algorithm_atlas_sdk import SimulationParams


def run(node_count: int = 7, seed: int = 42):
    sim = TopologicalSortSimulation()
    params = SimulationParams(seed=seed, inputs={"node_count": node_count}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def is_valid_topo_order(order, edges):
    """Check that no edge u→v has v before u."""
    pos = {n: i for i, n in enumerate(order)}
    for e in edges:
        if e.directed:
            if pos.get(e.source, -1) >= pos.get(e.target, len(order)):
                return False
    return True


class TestTopoSortMetadata:
    def test_slug(self):
        assert TopologicalSortSimulation().metadata().slug == "topological-sort"

    def test_category(self):
        assert TopologicalSortSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert TopologicalSortSimulation().metadata().visualization_type == "GRAPH"


class TestTopoSortCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_valid_topological_order(self, seed: int):
        initial, _, final = run(7, seed=seed)
        assert is_valid_topo_order(final.path, initial.edges), (
            f"seed={seed}: invalid topo order {final.path}"
        )

    def test_all_nodes_in_order(self):
        initial, _, final = run(7)
        assert len(final.path) == len(initial.nodes)
        assert set(final.path) == {nd.node_id for nd in initial.nodes}

    def test_edges_directed(self):
        initial, _, _ = run(7)
        for e in initial.edges:
            assert e.directed is True

    def test_in_degrees_start_non_negative(self):
        initial, _, _ = run(7)
        for v in initial.distances.values():
            assert v >= 0


class TestTopoSortFrames:
    def test_has_frames(self):
        _, frames, _ = run(7)
        assert len(frames) > 0

    def test_path_grows_monotonically(self):
        _, frames, _ = run(7)
        prev_len = 0
        for f in frames:
            assert len(f.path) >= prev_len
            prev_len = len(f.path)

    def test_no_current_at_end(self):
        _, _, final = run(7)
        assert final.current is None

    def test_frontier_empty_at_end(self):
        _, _, final = run(7)
        assert final.frontier == ()

    def test_serializable(self):
        import json
        initial, frames, final = run(7)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_clamp_min(self):
        sim = TopologicalSortSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 1}, config={})
        s = sim.initialize(p)
        assert len(s.nodes) == 4

    def test_clamp_max(self):
        sim = TopologicalSortSimulation()
        p = SimulationParams(seed=0, inputs={"node_count": 99}, config={})
        s = sim.initialize(p)
        assert len(s.nodes) == 10
