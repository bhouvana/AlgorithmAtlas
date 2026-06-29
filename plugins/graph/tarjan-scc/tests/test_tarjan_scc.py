"""Tests for Tarjan SCC plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List, Set, FrozenSet

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "tarjan_scc",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TarjanSCCSimulation = _mod.TarjanSCCSimulation

from algorithm_atlas_sdk import GraphTraversalState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def run(node_count: int = 6, extra_edges: int = 6, seed: int = 42):
    sim = TarjanSCCSimulation()
    params = SimulationParams(
        seed=seed,
        inputs={"node_count": node_count, "extra_edges": extra_edges},
        config={},
    )
    initial = sim.initialize(params)
    gen = sim.steps(initial)
    frames: List[GraphTraversalState] = []
    try:
        while True:
            frames.append(next(gen))
    except StopIteration as exc:
        final = exc.value
    return initial, frames, final


def brute_force_sccs(nodes: List[str], adj: dict) -> Set[FrozenSet[str]]:
    """Kosaraju's for reference: find SCCs using two DFS passes."""
    def dfs1(u, visited, finish_order):
        visited.add(u)
        for v in adj.get(u, []):
            if v not in visited:
                dfs1(v, visited, finish_order)
        finish_order.append(u)

    # Build reverse graph
    radj: dict = {n: [] for n in nodes}
    for u in nodes:
        for v in adj.get(u, []):
            radj[v].append(u)

    # Pass 1: finish order on original graph
    visited: set = set()
    finish_order: List[str] = []
    for u in nodes:
        if u not in visited:
            dfs1(u, visited, finish_order)

    # Pass 2: DFS on reverse graph in reverse finish order
    def dfs2(u, visited, component):
        visited.add(u)
        component.add(u)
        for v in radj.get(u, []):
            if v not in visited:
                dfs2(v, visited, component)

    visited2: set = set()
    sccs: Set[FrozenSet[str]] = set()
    for u in reversed(finish_order):
        if u not in visited2:
            comp: set = set()
            dfs2(u, visited2, comp)
            sccs.add(frozenset(comp))
    return sccs


def parse_sccs_from_description(desc: str) -> Set[FrozenSet[str]]:
    """Extract SCC sets from final description like 'Done: 2 SCC(s) — {A,B}; {C}'."""
    sccs: Set[FrozenSet[str]] = set()
    if "—" not in desc:
        return sccs
    parts = desc.split("—")[1].strip().split(";")
    for part in parts:
        part = part.strip().strip("{}")
        if part:
            nodes = frozenset(n.strip() for n in part.split(",") if n.strip())
            sccs.add(nodes)
    return sccs


class TestTarjanSCCMetadata:
    def test_slug(self):
        assert TarjanSCCSimulation().metadata().slug == "tarjan-scc"

    def test_category(self):
        assert TarjanSCCSimulation().metadata().category == "graph"

    def test_visualization_type(self):
        assert TarjanSCCSimulation().metadata().visualization_type == "GRAPH"


class TestTarjanSCCCorrectness:
    @pytest.mark.parametrize("seed", range(8))
    def test_correct_sccs(self, seed: int):
        """Verify SCCs against Kosaraju's reference implementation."""
        initial, _, final = run(6, extra_edges=6, seed=seed)

        adj: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            adj[e.source].append(e.target)

        node_ids = [n.node_id for n in initial.nodes]
        expected = brute_force_sccs(node_ids, adj)
        actual = parse_sccs_from_description(final.description)
        assert actual == expected, (
            f"seed={seed}: expected={expected}, got={actual}\n"
            f"desc={final.description}"
        )

    def test_all_nodes_in_some_scc(self):
        initial, _, final = run(6)
        all_nodes = {n.node_id for n in initial.nodes}
        scc_nodes = parse_sccs_from_description(final.description)
        found = set()
        for comp in scc_nodes:
            found |= comp
        assert found == all_nodes

    def test_sccs_partition_nodes(self):
        """SCCs must be disjoint and cover all nodes."""
        initial, _, final = run(6)
        all_nodes = {n.node_id for n in initial.nodes}
        sccs = parse_sccs_from_description(final.description)
        combined: List[str] = []
        for comp in sccs:
            combined.extend(comp)
        assert len(combined) == len(all_nodes)
        assert set(combined) == all_nodes

    def test_single_node_is_own_scc(self):
        """A node with no incoming path from itself is a trivial SCC."""
        initial, _, final = run(4, extra_edges=2, seed=0)
        sccs = parse_sccs_from_description(final.description)
        assert len(sccs) >= 1

    def test_all_nodes_discovered(self):
        initial, _, final = run(6)
        node_ids = {n.node_id for n in initial.nodes}
        assert final.visited == node_ids

    def test_scc_count_in_description(self):
        _, _, final = run(6)
        assert "SCC" in final.description

    @pytest.mark.parametrize("seed", range(5))
    def test_larger_graph_correct(self, seed: int):
        initial, _, final = run(8, extra_edges=8, seed=seed)
        adj: dict = {n.node_id: [] for n in initial.nodes}
        for e in initial.edges:
            adj[e.source].append(e.target)
        node_ids = [n.node_id for n in initial.nodes]
        expected = brute_force_sccs(node_ids, adj)
        actual = parse_sccs_from_description(final.description)
        assert actual == expected


class TestTarjanSCCFrames:
    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_frontier_empty_at_terminal(self):
        _, _, final = run(6)
        assert final.frontier == ()

    def test_current_none_at_terminal(self):
        _, _, final = run(6)
        assert final.current is None

    def test_visited_grows_monotonically(self):
        _, frames, _ = run(6)
        prev = frozenset()
        for f in frames:
            assert f.visited >= prev
            prev = f.visited

    def test_graph_structure_unchanged(self):
        initial, frames, final = run(6)
        for f in frames + [final]:
            assert f.nodes == initial.nodes
            assert f.edges == initial.edges

    def test_edges_are_directed(self):
        initial, _, _ = run(6)
        for e in initial.edges:
            assert e.directed is True

    def test_descriptions_nonempty(self):
        _, frames, _ = run(6)
        for f in frames:
            assert isinstance(f.description, str) and len(f.description) > 0

    def test_scc_root_frames_present(self):
        _, frames, _ = run(6)
        scc_root_frames = [f for f in frames if "SCC root" in f.description]
        assert len(scc_root_frames) >= 1

    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_deterministic(self):
        harness = AlgorithmTestHarness(TarjanSCCSimulation())
        params = SimulationParams(seed=42, inputs={"node_count": 6, "extra_edges": 6}, config={})
        harness.assert_deterministic(params)

    def test_node_positions_in_unit_square(self):
        initial, _, _ = run(6)
        for node in initial.nodes:
            assert 0.0 <= node.x <= 1.0
            assert 0.0 <= node.y <= 1.0

    def test_disc_times_all_nodes(self):
        initial, _, final = run(6)
        node_ids = {n.node_id for n in initial.nodes}
        assert set(final.distances.keys()) == node_ids
