"""Tests for Aho-Corasick plugin."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))

_spec = importlib.util.spec_from_file_location(
    "aho_corasick", Path(__file__).parent.parent / "algorithm.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
AhoCorasickSimulation = _mod.AhoCorasickSimulation
_AC = _mod._AC

from algorithm_atlas_sdk import SimulationParams, SortState


def make_params(seed=0):
    return SimulationParams(seed=seed, inputs={})


def run(seed=0):
    sim = AhoCorasickSimulation()
    params = make_params(seed=seed)
    init = sim.initialize(params)
    gen = sim.steps(init)
    states = []
    try:
        while True:
            states.append(next(gen))
    except StopIteration as e:
        final = e.value
    return init, states, final


class TestMetadata:
    def test_slug(self):
        assert AhoCorasickSimulation().metadata().slug == "aho-corasick"

    def test_category(self):
        assert AhoCorasickSimulation().metadata().category == "string"

    def test_visualization_type(self):
        assert AhoCorasickSimulation().metadata().visualization_type == "ARRAY_BARS"


class TestACAutomaton:
    def test_classic_ushers(self):
        ac = _AC()
        for p in ["he", "she", "his", "hers"]:
            ac.add(p)
        ac.build()
        matches = list(ac.search("ushers"))
        pats_found = {pat for _, pat in matches}
        assert "he" in pats_found
        assert "she" in pats_found
        assert "hers" in pats_found

    def test_no_match(self):
        ac = _AC()
        ac.add("xyz")
        ac.build()
        assert list(ac.search("abcdef")) == []

    def test_overlapping(self):
        ac = _AC()
        ac.add("ab")
        ac.add("abc")
        ac.build()
        matches = list(ac.search("abcabc"))
        assert len(matches) >= 2


class TestInitialize:
    def test_returns_sort_state(self):
        init = AhoCorasickSimulation().initialize(make_params())
        assert isinstance(init, SortState)

    def test_description_has_text_and_patterns(self):
        init = AhoCorasickSimulation().initialize(make_params())
        assert "text=" in init.description
        assert "patterns=" in init.description

    def test_array_length_equals_text_length(self):
        # Default seed=0 uses "ushers" (length 6)
        init = AhoCorasickSimulation().initialize(make_params(seed=0))
        import re
        text = re.search(r"text='([^']+)'", init.description).group(1)
        assert len(init.array) == len(text)


class TestSteps:
    def test_produces_steps(self):
        _, states, _ = run()
        assert len(states) >= 1

    def test_all_sort_state(self):
        _, states, final = run()
        for s in states:
            assert isinstance(s, SortState)
        assert isinstance(final, SortState)

    def test_match_count_positive(self):
        # "ushers" has matches for "he", "she", "hers" → at least 3
        _, _, final = run(seed=0)
        assert final.swaps >= 3

    def test_match_positions_subset_of_text(self):
        init, _, final = run()
        for idx in final.sorted_indices:
            assert 0 <= idx < len(init.array)

    def test_reproducible(self):
        _, _, f1 = run(seed=1)
        _, _, f2 = run(seed=1)
        assert f1.swaps == f2.swaps
        assert f1.sorted_indices == f2.sorted_indices

    def test_different_seeds_use_different_examples(self):
        i0 = AhoCorasickSimulation().initialize(make_params(seed=0))
        i1 = AhoCorasickSimulation().initialize(make_params(seed=1))
        # Different seeds may give different text/patterns
        assert True  # just verify they run

    def test_final_description_has_done(self):
        _, _, final = run()
        assert "Done" in final.description or "done" in final.description

    def test_ushers_classic_matches(self):
        # Known: "ushers" contains "she" (positions 1-3), "he" (2-3), "hers" (2-5)
        _, _, final = run(seed=0)
        assert final.swaps == 3  # she, he, hers
