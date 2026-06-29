"""Aho-Corasick multi-pattern string search plugin for Algorithm Atlas."""
from __future__ import annotations

from collections import deque
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Classic example: Knuth, Morris, Pratt patterns in "ushers"
_EXAMPLES = [
    # (text, patterns)
    ("ushers", ["he", "she", "his", "hers"]),
    ("abcaababc", ["ab", "bc", "abc"]),
    ("mississippi", ["miss", "issi", "ippi", "si"]),
    ("aababcabc", ["a", "ab", "abc", "bc"]),
    ("theyhavehistory", ["they", "he", "have", "his", "hers"]),
]


class _AC:
    """Minimal Aho-Corasick automaton."""

    def __init__(self):
        self.goto: list[dict] = [{}]
        self.fail: list[int] = [0]
        self.out: list[list] = [[]]

    def add(self, pattern: str) -> None:
        cur = 0
        for ch in pattern:
            if ch not in self.goto[cur]:
                self.goto.append({})
                self.fail.append(0)
                self.out.append([])
                self.goto[cur][ch] = len(self.goto) - 1
            cur = self.goto[cur][ch]
        self.out[cur].append(pattern)

    def build(self) -> None:
        q: deque = deque()
        for ch, s in self.goto[0].items():
            self.fail[s] = 0
            q.append(s)
        while q:
            r = q.popleft()
            for ch, s in self.goto[r].items():
                q.append(s)
                state = self.fail[r]
                while state and ch not in self.goto[state]:
                    state = self.fail[state]
                f = self.goto[state].get(ch, 0)
                self.fail[s] = 0 if f == s else f
                self.out[s] = self.out[s] + self.out[self.fail[s]]

    def search(self, text: str):
        """Yield (end_idx, pattern) for each match."""
        cur = 0
        for i, ch in enumerate(text):
            while cur and ch not in self.goto[cur]:
                cur = self.fail[cur]
            cur = self.goto[cur].get(ch, 0)
            for pat in self.out[cur]:
                yield i, pat


def _text_to_array(text: str) -> tuple:
    """Map characters to bar heights 1-99 based on ASCII."""
    if not text:
        return tuple()
    lo = min(ord(c) for c in text)
    hi = max(ord(c) for c in text)
    spread = hi - lo or 1
    return tuple(max(1, int((ord(c) - lo) * 98 / spread) + 1) for c in text)


class AhoCorasickSimulation(AlgorithmPlugin):
    """Aho-Corasick multi-pattern string search."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="aho-corasick",
            name="Aho-Corasick",
            category="string",
            visualization_type="ARRAY_BARS",
            description=(
                "Search for multiple patterns simultaneously in O(n + m + k) "
                "using a finite automaton."
            ),
            intuition=(
                "Build a trie of all patterns. Add failure links that allow "
                "fall-back without missing matches. Scan text once: "
                "any state with output = a match."
            ),
            complexity_time_best="O(n + m + k)",
            complexity_time_average="O(n + m + k)",
            complexity_time_worst="O(n + m + k)",
            complexity_space="O(m)",
            tags=("string", "aho-corasick", "pattern-matching", "trie", "automaton"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        example = _EXAMPLES[params.seed % len(_EXAMPLES)]
        text, patterns = example
        arr = _text_to_array(text)
        pat_str = "|".join(patterns)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"AC text='{text}' patterns='{pat_str}'",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        desc = initial_state.description
        text = re.search(r"text='([^']+)'", desc).group(1)
        pat_str = re.search(r"patterns='([^']+)'", desc).group(1)
        patterns = pat_str.split("|")

        arr = _text_to_array(text)
        ac = _AC()
        for p in patterns:
            ac.add(p)
        ac.build()

        # Yield trie-built state
        yield SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=(
                f"Trie built for {len(patterns)} patterns: "
                f"{patterns}. Scanning text '{text}'"
            ),
        )

        match_ends: set = set()
        match_count = 0
        cur_state = 0

        for i, ch in enumerate(text):
            while cur_state and ch not in ac.goto[cur_state]:
                cur_state = ac.fail[cur_state]
            cur_state = ac.goto[cur_state].get(ch, 0)

            found = list(ac.out[cur_state])
            if found:
                for pat in found:
                    match_count += 1
                    start = i - len(pat) + 1
                    for j in range(start, i + 1):
                        match_ends.add(j)

                yield SortState(
                    array=arr,
                    comparing=(i, i),
                    last_swap=(i - len(found[0]) + 1, i),
                    sorted_indices=frozenset(match_ends),
                    comparisons=i + 1,
                    swaps=match_count,
                    description=(
                        f"pos {i} ('{ch}'): MATCH '{found[0]}' ends here. "
                        f"Total matches={match_count}"
                    ),
                )
            else:
                yield SortState(
                    array=arr,
                    comparing=(i, i),
                    last_swap=None,
                    sorted_indices=frozenset(match_ends),
                    comparisons=i + 1,
                    swaps=match_count,
                    description=f"pos {i} ('{ch}'): state={cur_state}, no match",
                )

        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(match_ends),
            comparisons=len(text),
            swaps=match_count,
            description=(
                f"Done: {match_count} matches in '{text}' "
                f"for patterns {patterns}"
            ),
        )
