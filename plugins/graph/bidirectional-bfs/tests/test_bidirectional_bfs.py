"""Tests for Bidirectional BFS plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "bidir_bfs_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BidirectionalBFSSimulation = mod.BidirectionalBFSSimulation
_NODES = mod._NODES
_EDGES = mod._EDGES
_SOURCE = mod._SOURCE
_TARGET = mod._TARGET


def _make_plugin(seed=0):
    plugin = BidirectionalBFSSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def _collect(plugin, params):
    state = plugin.initialize(params)
    states = [state]
    gen = plugin.steps(state)
    try:
        while True:
            states.append(next(gen))
    except StopIteration as e:
        states.append(e.value)
    return states


def _bfs_reference(adj, source, target):
    """Standard BFS to verify path length."""
    from collections import deque
    dist = {source: 0}
    q = deque([source])
    while q:
        u = q.popleft()
        if u == target:
            return dist[u]
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return None


def test_metadata_slug():
    p = BidirectionalBFSSimulation()
    assert p.metadata().slug == "bidirectional-bfs"


def test_metadata_category():
    p = BidirectionalBFSSimulation()
    assert p.metadata().category == "graph"


def test_initial_node_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.nodes) == len(_NODES)


def test_initial_edge_count():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.edges) == len(_EDGES)


def test_path_found():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    # Final path should include source and target
    assert str(_SOURCE) in final.path
    assert str(_TARGET) in final.path


def test_path_length_correct():
    # Verify via standard BFS
    adj = {i: [] for i in range(len(_NODES))}
    for u, v in _EDGES:
        adj[u].append(v)
        adj[v].append(u)
    expected_len = _bfs_reference(adj, _SOURCE, _TARGET)

    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    actual_len = len(final.path) - 1  # edges = nodes - 1
    assert actual_len == expected_len


def test_final_description_has_path():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert "Path found" in final.description or "→" in final.description


def test_final_description_has_source_target():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert _NODES[_SOURCE][0] in final.description
    assert _NODES[_TARGET][0] in final.description


def test_steps_produced():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    assert len(states) >= 5


def test_forward_and_backward_steps():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    forward_steps = [s for s in states if "Forward" in s.description]
    backward_steps = [s for s in states if "Backward" in s.description]
    assert len(forward_steps) > 0
    assert len(backward_steps) > 0


def test_path_is_connected():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    path = [int(n) for n in final.path]
    adj_set = set()
    for u, v in _EDGES:
        adj_set.add((u, v))
        adj_set.add((v, u))
    for i in range(len(path) - 1):
        assert (path[i], path[i + 1]) in adj_set, f"Edge ({path[i]},{path[i+1]}) not in graph"
