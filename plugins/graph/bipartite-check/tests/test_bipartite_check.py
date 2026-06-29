"""Tests for Bipartite Check plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "bipartite_check",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BipartiteCheckSimulation = _mod.BipartiteCheckSimulation

from algorithm_atlas_sdk import GraphTraversalState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def run(node_count: int = 6, seed: int = 42):
    sim = BipartiteCheckSimulation()
    params = SimulationParams(seed=seed, inputs={"node_count": node_count}, config={})
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames: List[GraphTraversalState] = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def brute_force_bipartite(nodes, adj) -> bool:
    """BFS 2-coloring reference."""
    color = {}
    from collections import deque
    for start in nodes:
        if start in color:
            continue
        color[start] = 0
        q = deque([start])
        while q:
            u = q.popleft()
            for v in adj.get(u, []):
                if v not in color:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True


class TestBipartiteCheckMetadata:
    def test_slug(self):
        assert BipartiteCheckSimulation().metadata().slug == "bipartite-check"

    def test_category(self):
        assert BipartiteCheckSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert BipartiteCheckSimulation().metadata().visualization_type == "GRAPH"


class TestBipartiteCheckCorrectness:
    @pytest.mark.parametrize("seed", range(10))
    def test_correct_result(self, seed: int):
        initial, _, final = run(6, seed=seed)

        adj: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            adj[e.source].append(e.target)
            adj[e.target].append(e.source)

        node_ids = [n.node_id for n in initial.nodes]
        expected = brute_force_bipartite(node_ids, adj)
        actual_bipartite = "BIPARTITE" in final.path and "NOT_BIPARTITE" not in final.path
        assert actual_bipartite == expected, (
            f"seed={seed}: expected bipartite={expected}, "
            f"got path={final.path}"
        )

    def test_even_seed_is_bipartite(self):
        """Even seeds generate bipartite graphs by construction."""
        initial, _, final = run(6, seed=0)
        adj: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            adj[e.source].append(e.target)
            adj[e.target].append(e.source)
        node_ids = [n.node_id for n in initial.nodes]
        assert brute_force_bipartite(node_ids, adj) is True

    def test_all_nodes_colored(self):
        initial, _, final = run(6, seed=0)
        node_ids = {n.node_id for n in initial.nodes}
        colored = set(final.distances.keys())
        assert colored == node_ids

    def test_colors_are_1_or_2(self):
        initial, _, final = run(6, seed=0)
        for v in final.distances.values():
            assert v in (1.0, 2.0)

    def test_bipartite_groups_are_disjoint(self):
        _, _, final = run(6, seed=0)
        if "BIPARTITE" in final.path and "NOT_BIPARTITE" not in final.path:
            group_a = {k for k, v in final.distances.items() if v == 1.0}
            group_b = {k for k, v in final.distances.items() if v == 2.0}
            assert group_a.isdisjoint(group_b)


class TestBipartiteCheckFrames:
    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_frontier_empty_at_terminal(self):
        _, _, final = run(6)
        assert final.frontier == ()

    def test_graph_structure_unchanged(self):
        initial, frames, final = run(6)
        for f in frames + [final]:
            assert f.nodes == initial.nodes
            assert f.edges == initial.edges

    def test_descriptions_nonempty(self):
        _, frames, _ = run(6)
        for f in frames:
            assert len(f.description) > 0

    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_deterministic(self):
        harness = AlgorithmTestHarness(BipartiteCheckSimulation())
        params = SimulationParams(seed=42, inputs={"node_count": 6}, config={})
        harness.assert_deterministic(params)

    def test_visited_grows_monotonically(self):
        _, frames, _ = run(6, seed=0)
        prev = frozenset()
        for f in frames:
            assert f.visited >= prev
            prev = f.visited
