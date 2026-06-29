"""Tests for Trie plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "trie",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TrieSimulation = _mod.TrieSimulation
_WORDS = _mod._WORDS

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = TrieSimulation()
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


class TestTrieMetadata:
    def test_slug(self):
        assert TrieSimulation().metadata().slug == "trie"

    def test_category(self):
        assert TrieSimulation().metadata().category == "tree"

    def test_visualization_type(self):
        assert TrieSimulation().metadata().visualization_type == "TREE"


class TestTrieStructure:
    @pytest.mark.parametrize("seed", range(len(_WORDS)))
    def test_correct_node_count(self, seed: int):
        from algorithm_atlas_sdk import SimulationParams
        sim = TrieSimulation()
        params = SimulationParams(seed=seed, inputs={}, config={})
        initial = sim.initialize(params)
        words = _WORDS[seed]
        # Verify all words have nodes (shared prefixes reduce count)
        unique_chars = set()
        for w in words:
            for i in range(len(w)):
                unique_chars.add(w[:i+1])  # unique prefixes
        # Node count = unique prefixes + 1 (root)
        assert len(initial.nodes) == len(unique_chars) + 1

    def test_root_node_label(self):
        initial, _, _ = run(0)
        root = next(n for n in initial.nodes if n.node_id == "0")
        assert "*" in root.label

    def test_has_edges(self):
        initial, _, _ = run(0)
        assert len(initial.edges) > 0

    @pytest.mark.parametrize("seed", range(len(_WORDS)))
    def test_edge_count_equals_nodes_minus_1(self, seed: int):
        sim = TrieSimulation()
        params = SimulationParams(seed=seed, inputs={}, config={})
        initial = sim.initialize(params)
        assert len(initial.edges) == len(initial.nodes) - 1


class TestTrieSearch:
    @pytest.mark.parametrize("seed", range(len(_WORDS)))
    def test_last_word_found(self, seed: int):
        _, _, final = run(seed=seed)
        assert "FOUND" in final.description

    def test_search_frames_equal_word_length(self):
        seed = 0
        _, frames, _ = run(seed=seed)
        query = _WORDS[seed][-1]
        assert len(frames) == len(query)

    def test_path_includes_root(self):
        _, _, final = run(0)
        assert final.path[0] == "0"


class TestTrieFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
