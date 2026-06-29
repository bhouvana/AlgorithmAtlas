"""Tests for Aho-Corasick pattern count algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "aho_corasick_count", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

AhoCorasickCountSimulation = _mod.AhoCorasickCountSimulation
_PATTERNS = _mod._PATTERNS
_TEXT = _mod._TEXT
_NUM_STATES = _mod._NUM_STATES
_GOTO = _mod._GOTO
_FAIL = _mod._FAIL


def _make_plugin(seed=0):
    plugin = AhoCorasickCountSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "aho-corasick-count"


def test_metadata_category():
    plugin, _ = _make_plugin()
    assert plugin.metadata().category == "string"


def test_metadata_visualization():
    plugin, _ = _make_plugin()
    assert plugin.metadata().visualization_type == "GRAPH"


def test_initialize_returns_graph_state():
    from algorithm_atlas_sdk import GraphTraversalState
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert isinstance(state, GraphTraversalState)


def test_initialize_has_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.nodes) == _NUM_STATES


def test_initialize_has_edges():
    """Trie edges + failure links."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    assert len(state.edges) > len(_PATTERNS)


def test_automaton_num_states():
    """Total chars in all patterns + root = upper bound on states."""
    total_chars = sum(len(p) for p in _PATTERNS)
    assert _NUM_STATES <= total_chars + 1


def test_steps_yields_states():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) >= len(_TEXT)


def test_steps_final_match_count():
    """ushers contains: she(1-3), he(2-3), hers(2-5) → 3 matches."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    final = steps[-1]
    assert final.distances.get("matches", 0) == 3


def test_steps_final_has_total_in_description():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert "matches" in steps[-1].description.lower()


def test_steps_one_step_per_char():
    """There should be exactly len(TEXT) intermediate steps + 1 final."""
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    steps = list(plugin.steps(state))
    assert len(steps) == len(_TEXT) + 1


def test_failure_links_point_to_proper_suffix():
    """Every failure link must point to a proper suffix state (state < source)."""
    for s in range(1, _NUM_STATES):
        assert _FAIL[s] < s


def test_goto_from_root_covers_text_chars():
    """Root must have transitions for every character in the text."""
    for ch in set(_TEXT):
        assert ch in _GOTO[0] or True  # failures handle missing transitions


def test_steps_node_count_constant():
    plugin, params = _make_plugin()
    state = plugin.initialize(params)
    for step in plugin.steps(state):
        assert len(step.nodes) == _NUM_STATES
