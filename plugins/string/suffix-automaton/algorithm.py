"""Suffix Automaton plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_STRINGS = ["abcbc", "aabab", "banana", "abcdef", "mississippi"]


class _State:
    __slots__ = ("len", "link", "next")

    def __init__(self, length=0, link=-1):
        self.len = length
        self.link = link
        self.next = {}


def _build_sam(s):
    """Build suffix automaton and return (states, steps_log)."""
    sa = [_State()]  # initial state
    last = 0
    steps = []

    for ch in s:
        cur = len(sa)
        sa.append(_State(sa[last].len + 1))
        p = last
        while p != -1 and ch not in sa[p].next:
            sa[p].next[ch] = cur
            p = sa[p].link
        if p == -1:
            sa[cur].link = 0
        else:
            q = sa[p].next[ch]
            if sa[p].len + 1 == sa[q].len:
                sa[cur].link = q
            else:
                clone = len(sa)
                sa.append(_State(sa[p].len + 1, sa[q].link))
                sa[-1].next = dict(sa[q].next)
                while p != -1 and sa[p].next.get(ch) == q:
                    sa[p].next[ch] = clone
                    p = sa[p].link
                sa[q].link = clone
                sa[cur].link = clone
        last = cur
        steps.append(len(sa))  # number of states after this char
    return sa, steps


class SuffixAutomatonSimulation(AlgorithmPlugin):
    """Suffix automaton construction visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="suffix-automaton",
            name="Suffix Automaton",
            category="string",
            visualization_type="ARRAY_BARS",
            description="Build DAWG representing all substrings in O(n) states.",
            intuition=(
                "Online construction: for each char, create new state with len=last.len+1. "
                "Walk suffix links to update transitions. "
                "Optionally clone a state if suffix link lengths don't match. "
                "States ≤ 2n, transitions ≤ 3n."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("string", "suffix-automaton", "dawg", "substring", "online-construction"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        s = _STRINGS[params.seed % len(_STRINGS)]
        n = len(s)
        arr = tuple(1 for _ in range(n))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"SuffixAutomaton s='{s}'",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        s = re.search(r"s='([^']+)'", initial_state.description).group(1)
        n = len(s)
        _, steps = _build_sam(s)

        # Expected: states ≤ 2n, transitions ≤ 3n
        max_states = max(steps) if steps else 1

        for i, state_count in enumerate(steps):
            # Bar = state count normalized
            arr = tuple(
                max(1, min(99, steps[k] * 99 // max_states)) if k <= i else 1
                for k in range(n)
            )
            yield SortState(
                array=arr,
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(range(i + 1)),
                comparisons=i + 1,
                swaps=state_count,
                description=f"Add '{s[i]}': {state_count} states (≤{2*(i+1)+1} bound)",
            )

        final_count = steps[-1] if steps else 1
        arr = tuple(max(1, min(99, c * 99 // max_states)) for c in steps)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=n,
            swaps=final_count,
            description=f"SAM built: {final_count} states (bound 2·{n}={2*n}) for '{s}'",
        )
