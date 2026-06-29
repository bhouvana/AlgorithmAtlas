"""Tests for Huffman Coding plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "huffman_coding",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
HuffmanCodingSimulation = _mod.HuffmanCodingSimulation

from algorithm_atlas_sdk import SimulationParams


def run(n: int = 6, seed: int = 42):
    sim = HuffmanCodingSimulation()
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


class TestHuffmanCodingMetadata:
    def test_slug(self):
        assert HuffmanCodingSimulation().metadata().slug == "huffman-coding"

    def test_category(self):
        assert HuffmanCodingSimulation().metadata().category == "greedy"

    def test_visualization_type(self):
        assert HuffmanCodingSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestHuffmanCodingInitialize:
    def test_array_size(self):
        initial, _, _ = run(6)
        assert len(initial.array) == 6

    def test_array_sorted(self):
        initial, _, _ = run(6)
        arr = list(initial.array)
        assert arr == sorted(arr), "Frequencies should be sorted"

    def test_description_has_symbols(self):
        initial, _, _ = run(6)
        assert "symbols=" in initial.description


class TestHuffmanCodingCorrectness:
    def test_merge_count(self):
        initial, _, final = run(6)
        n = len(initial.array)
        # n-1 merges needed to build a full Huffman tree
        assert final.swaps == n - 1

    def test_has_frames(self):
        _, frames, _ = run(6)
        assert len(frames) > 0

    def test_merge_frames_correct_count(self):
        initial, frames, _ = run(6)
        n = len(initial.array)
        # "Merge 'X'..." frames only (not "Merged ... placed" confirmation frames)
        merge_frames = [f for f in frames if f.description.startswith("Merge '")]
        assert len(merge_frames) == n - 1

    @pytest.mark.parametrize("n", [4, 5, 6, 7, 8])
    def test_n_minus_1_merges(self, n: int):
        _, _, final = run(n)
        assert final.swaps == n - 1

    def test_final_description_mentions_root(self):
        _, _, final = run(6)
        assert "root" in final.description.lower() or "built" in final.description.lower()

    @pytest.mark.parametrize("seed", range(5))
    def test_various_seeds(self, seed: int):
        initial, _, final = run(6, seed=seed)
        assert final.swaps == len(initial.array) - 1


class TestHuffmanCodingFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(6)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())

    def test_comparisons_increase(self):
        _, frames, final = run(6)
        assert final.comparisons == len(frames) // 2 or final.comparisons >= 1
