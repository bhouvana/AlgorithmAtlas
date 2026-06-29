"""Tests for BFS plugin."""
import importlib.util
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parents[4] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "bfs_algorithm",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BFSSimulation = _mod.BFSSimulation

from algorithm_atlas_sdk import GraphTraversalState, SimulationParams
from algorithm_atlas_sdk.testing import AlgorithmTestHarness


def make_params(**kwargs) -> SimulationParams:
    defaults = {"seed": 42, "inputs": {"node_count": 8, "extra_edges": 3, "start_node": "A"}}
    defaults.update(kwargs)
    if "inputs" in kwargs:
        defaults["inputs"] = kwargs["inputs"]
    return SimulationParams(**defaults)


def test_metadata():
    sim = BFSSimulation()
    meta = sim.metadata()
    assert meta.slug == "bfs"
    assert meta.category == "graph"
    assert meta.visualization_type == "GRAPH"


def test_produces_states():
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    frames: List[GraphTraversalState] = harness.run_to_completion(params)
    assert len(frames) >= 2


def test_terminal_state_has_visited_nodes():
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    final: GraphTraversalState = harness.get_terminal_state(params)
    assert len(final.visited) > 0


def test_all_nodes_visited_connected_graph():
    """BFS must visit all nodes in a connected graph."""
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params(inputs={"node_count": 8, "extra_edges": 3, "start_node": "A"})
    final: GraphTraversalState = harness.get_terminal_state(params)
    node_ids = {n.node_id for n in final.nodes}
    assert final.visited == node_ids, (
        f"BFS missed nodes: {node_ids - final.visited}"
    )


def test_start_node_distance_zero():
    """Start node must have BFS level 0."""
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params(inputs={"node_count": 8, "extra_edges": 3, "start_node": "A"})
    final: GraphTraversalState = harness.get_terminal_state(params)
    assert final.distances.get("A") == 0.0


def test_distances_non_negative():
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    final: GraphTraversalState = harness.get_terminal_state(params)
    for node_id, dist in final.distances.items():
        assert dist >= 0.0, f"Node {node_id} has negative distance {dist}"


def test_distances_respect_bfs_levels():
    """Adjacent nodes' BFS levels must differ by at most 1."""
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params(inputs={"node_count": 8, "extra_edges": 3, "start_node": "A"})
    final: GraphTraversalState = harness.get_terminal_state(params)

    # Build adjacency from edges
    adj = {}
    for n in final.nodes:
        adj[n.node_id] = []
    for e in final.edges:
        adj[e.source].append(e.target)
        adj[e.target].append(e.source)

    for u, neighbors in adj.items():
        if u not in final.distances:
            continue
        for v in neighbors:
            if v not in final.distances:
                continue
            diff = abs(final.distances[u] - final.distances[v])
            assert diff <= 1.0, (
                f"BFS level gap > 1 between adjacent nodes {u}(level {final.distances[u]}) "
                f"and {v}(level {final.distances[v]})"
            )


def test_frontier_empty_at_terminal():
    """BFS queue must be empty when algorithm completes."""
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    final: GraphTraversalState = harness.get_terminal_state(params)
    assert final.frontier == ()


def test_current_none_at_terminal():
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    final: GraphTraversalState = harness.get_terminal_state(params)
    assert final.current is None


def test_path_length_equals_visited():
    """path tuple should contain exactly the visited nodes (no duplicates)."""
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    final: GraphTraversalState = harness.get_terminal_state(params)
    assert len(final.path) == len(final.visited)
    assert set(final.path) == final.visited


def test_path_starts_with_start_node():
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params(inputs={"node_count": 8, "extra_edges": 3, "start_node": "A"})
    final: GraphTraversalState = harness.get_terminal_state(params)
    assert final.path[0] == "A"


def test_graph_structure_unchanged():
    """Nodes and edges must not change during traversal."""
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    frames: List[GraphTraversalState] = harness.run_to_completion(params)
    initial_nodes = frames[0].nodes
    initial_edges = frames[0].edges
    for f in frames:
        assert f.nodes == initial_nodes
        assert f.edges == initial_edges


def test_visited_grows_monotonically():
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    frames: List[GraphTraversalState] = harness.run_to_completion(params)
    prev = frozenset()
    for f in frames:
        assert f.visited >= prev
        prev = f.visited


def test_deterministic():
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    harness.assert_deterministic(params)


def test_json_serializable():
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    harness.assert_json_serializable(params)


def test_node_positions_in_unit_square():
    """All node positions must be within [0, 1]."""
    sim = BFSSimulation()
    params = make_params()
    initial = sim.initialize(params)
    for node in initial.nodes:
        assert 0.0 <= node.x <= 1.0, f"Node {node.node_id} x={node.x} out of range"
        assert 0.0 <= node.y <= 1.0, f"Node {node.node_id} y={node.y} out of range"


def test_graph_is_connected():
    """BFS from any node must reach all nodes (graph is connected by construction)."""
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params(inputs={"node_count": 6, "extra_edges": 2, "start_node": "A"})
    final: GraphTraversalState = harness.get_terminal_state(params)
    assert len(final.visited) == 6


def test_different_seeds_produce_different_graphs():
    sim = BFSSimulation()
    p1 = make_params(seed=1)
    p2 = make_params(seed=99)
    s1 = sim.initialize(p1)
    s2 = sim.initialize(p2)
    assert s1.nodes != s2.nodes or s1.edges != s2.edges


def test_small_graph():
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params(inputs={"node_count": 3, "extra_edges": 0, "start_node": "A"})
    final: GraphTraversalState = harness.get_terminal_state(params)
    assert len(final.visited) == 3


def test_descriptions_nonempty():
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params()
    frames: List[GraphTraversalState] = harness.run_to_completion(params)
    for f in frames:
        assert isinstance(f.description, str) and len(f.description) > 0


def test_bfs_level_order_property():
    """Nodes with lower BFS level must appear earlier in path than higher-level nodes."""
    harness = AlgorithmTestHarness(BFSSimulation())
    params = make_params(inputs={"node_count": 8, "extra_edges": 2, "start_node": "A"})
    final: GraphTraversalState = harness.get_terminal_state(params)

    path_position = {node: i for i, node in enumerate(final.path)}
    for u, pos_u in path_position.items():
        dist_u = final.distances.get(u, float("inf"))
        for v, pos_v in path_position.items():
            dist_v = final.distances.get(v, float("inf"))
            # If u has strictly lower level, it must appear before v in path
            if dist_u < dist_v:
                assert pos_u < pos_v, (
                    f"BFS level order violated: {u}(level {dist_u}, pos {pos_u}) "
                    f"appears after {v}(level {dist_v}, pos {pos_v})"
                )
