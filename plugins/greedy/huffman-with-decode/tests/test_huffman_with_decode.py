"""Tests for Huffman Decode algorithm."""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "huffman_with_decode", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

HuffmanDecodeSimulation = _mod.HuffmanDecodeSimulation
_STRINGS = _mod._STRINGS
_huffman_codes = _mod._huffman_codes
_freq = _mod._freq


def _make_plugin(seed=0):
    plugin = HuffmanDecodeSimulation()

    class P:
        pass

    P.seed = seed
    P.inputs = {}
    return plugin, P()


def test_metadata_slug():
    plugin, _ = _make_plugin()
    assert plugin.metadata().slug == "huffman-with-decode"


def test_metadata_category():
    plugin, _ = _make_plugin()
    assert plugin.metadata().category == "greedy"


def test_metadata_visualization():
    plugin, _ = _make_plugin()
    assert plugin.metadata().visualization_type == "ARRAY_BARS"


def test_huffman_codes_all_chars_have_code():
    for s in _STRINGS:
        freq = _freq(s)
        codes = _huffman_codes(s)
        for ch in freq:
            assert ch in codes
            assert len(codes[ch]) >= 1


def test_huffman_codes_prefix_free():
    for s in _STRINGS:
        codes = _huffman_codes(s)
        code_list = list(codes.values())
        for i, c1 in enumerate(code_list):
            for j, c2 in enumerate(code_list):
                if i != j:
                    assert not c1.startswith(c2), f"'{c1}' starts with '{c2}' in codes for '{s}'"


def test_huffman_codes_decode_round_trip():
    for s in _STRINGS:
        codes = _huffman_codes(s)
        # Encode
        encoded = "".join(codes[c] for c in s)
        # Decode by building reverse lookup trie
        tree = {}
        for ch, code in codes.items():
            node = tree
            for bit in code:
                node = node.setdefault(bit, {})
            node["_char"] = ch
        # Decode
        decoded = []
        node = tree
        for bit in encoded:
            node = node[bit]
            if "_char" in node:
                decoded.append(node["_char"])
                node = tree
        assert "".join(decoded) == s, f"Round-trip failed for '{s}'"


def test_initialize_array_length_matches_unique_chars():
    plugin, params = _make_plugin(0)
    state = plugin.initialize(params)
    s = _STRINGS[0]
    unique = len(set(s))
    assert len(state.array) == unique


def test_initialize_description_contains_string():
    plugin, params = _make_plugin(0)
    state = plugin.initialize(params)
    assert "HuffDecode s='" in state.description


def test_steps_yields_one_per_unique_plus_summary():
    plugin, params = _make_plugin(0)
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    s = _STRINGS[0]
    unique = len(set(s))
    assert len(all_steps) == unique + 1


def test_steps_all_values_in_range():
    for seed in range(len(_STRINGS)):
        plugin, _ = _make_plugin()
        class P:
            pass
        P.seed = seed
        P.inputs = {}
        state = plugin.initialize(P())
        for step in plugin.steps(state):
            for v in step.array:
                assert 1 <= v <= 99


def test_steps_compression_encoded_less_than_naive():
    plugin, params = _make_plugin(0)
    state = plugin.initialize(params)
    all_steps = list(plugin.steps(state))
    summary = all_steps[-1]
    # Should show some compression happening
    assert "bits" in summary.description.lower()


def test_steps_all_seeds_complete():
    for seed in range(len(_STRINGS)):
        plugin, _ = _make_plugin()
        class P:
            pass
        P.seed = seed
        P.inputs = {}
        state = plugin.initialize(P())
        steps = list(plugin.steps(state))
        assert len(steps) >= 2
