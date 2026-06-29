"""Tests for Word Search plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "word_search",
    Path(__file__).parent.parent / "algorithm.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
WordSearchSimulation = _mod.WordSearchSimulation
_PUZZLES = _mod._PUZZLES
_search_word = _mod._search_word

from algorithm_atlas_sdk import SimulationParams


def run(seed: int = 0):
    sim = WordSearchSimulation()
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


class TestWordSearchMetadata:
    def test_slug(self):
        assert WordSearchSimulation().metadata().slug == "word-search"

    def test_category(self):
        assert WordSearchSimulation().metadata().category == "backtracking"

    def test_visualization_type(self):
        assert WordSearchSimulation().metadata().visualization_type == "GRID"


class TestWordSearchCorrectness:
    @pytest.mark.parametrize("seed", range(len(_PUZZLES)))
    def test_correct_found_status(self, seed: int):
        grid_chars, word, expected_found = _PUZZLES[seed]
        _, _, final = run(seed)
        if expected_found:
            assert "FOUND" in final.description and "NOT FOUND" not in final.description
        else:
            assert "NOT FOUND" in final.description

    @pytest.mark.parametrize("seed", [0, 1, 3, 4])
    def test_found_path_spells_word(self, seed: int):
        grid_chars, word, _ = _PUZZLES[seed]
        _, _, final = run(seed)
        path = final.path
        assert len(path) == len(word)
        for i, (r, c) in enumerate(path):
            assert grid_chars[r][c] == word[i]

    def test_has_frames(self):
        _, frames, _ = run(0)
        assert len(frames) > 0


class TestWordSearchFrames:
    def test_serializable(self):
        import json
        initial, frames, final = run(0)
        for state in [initial, frames[0], final]:
            json.dumps(state.to_dict())
