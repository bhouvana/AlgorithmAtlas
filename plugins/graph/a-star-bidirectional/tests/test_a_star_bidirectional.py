"""Tests for Bidirectional A* plugin."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

spec = importlib.util.spec_from_file_location(
    "bidir_astar_alg", Path(__file__).parent.parent / "algorithm.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BidirectionalAStarSimulation = mod.BidirectionalAStarSimulation
_NODES = mod._NODES
_EDGES = mod._EDGES
_SOURCE = mod._SOURCE
_TARGET = mod._TARGET
_heuristic = mod._heuristic


def _make_plugin(seed=0):
    plugin = BidirectionalAStarSimulation()

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


def _dijkstra_reference():
    """Dijkstra's to get true shortest path cost."""
    import heapq
    INF = float('inf')
    dist = [INF] * len(_NODES)
    dist[_SOURCE] = 0.0
    pq = [(0.0, _SOURCE)]
    adj = {i: [] for i in range(len(_NODES))}
    for u, v, w in _EDGES:
        adj[u].append((v, w))
        adj[v].append((u, w))
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    return dist[_TARGET]


def test_metadata_slug():
    p = BidirectionalAStarSimulation()
    assert p.metadata().slug == "a-star-bidirectional"


def test_metadata_category():
    p = BidirectionalAStarSimulation()
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
    assert len(final.path) >= 2
    assert str(_SOURCE) in final.path
    assert str(_TARGET) in final.path


def test_path_cost_correct():
    expected = _dijkstra_reference()
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    # Extract cost from description
    import re
    m = re.search(r"cost=([\d.]+)", final.description)
    if m:
        actual_cost = float(m.group(1))
        assert abs(actual_cost - expected) < 0.5


def test_heuristic_admissible():
    for i in range(len(_NODES)):
        h = _heuristic(i, _TARGET)
        assert h >= 0


def test_steps_produced():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    assert len(states) >= 5


def test_forward_and_backward_in_steps():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    fwd = [s for s in states if "Forward" in s.description]
    bwd = [s for s in states if "Backward" in s.description]
    assert len(fwd) > 0
    assert len(bwd) > 0


def test_final_description_has_cost():
    plugin, params = _make_plugin()
    states = _collect(plugin, params)
    final = states[-1]
    assert "cost=" in final.description or "Path" in final.description
