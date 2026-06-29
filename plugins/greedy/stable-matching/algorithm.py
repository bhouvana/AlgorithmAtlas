"""Stable Matching (Gale-Shapley) plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Fixed 5x5 stable matching instance
_N = 5
# men_pref[i] = ordered list of women preferences (0-indexed)
_MEN_PREF = [
    [1, 0, 2, 3, 4],
    [0, 1, 3, 2, 4],
    [2, 1, 0, 3, 4],
    [0, 3, 1, 4, 2],
    [3, 2, 0, 1, 4],
]
# women_pref[j][i] = rank of man i in woman j's preference (lower=better)
_WOMEN_PREF = [
    [3, 0, 1, 2, 4],  # woman 0 prefers man 1 > 2 > 3 > 0 > 4
    [1, 0, 2, 3, 4],
    [0, 1, 2, 4, 3],
    [2, 1, 0, 3, 4],
    [0, 1, 2, 3, 4],
]


class StableMatchingSimulation(AlgorithmPlugin):
    """Gale-Shapley stable matching algorithm."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="stable-matching",
            name="Stable Matching (Gale-Shapley)",
            category="greedy",
            visualization_type="ARRAY_BARS",
            description=f"Find stable matching for {_N} men and {_N} women using Gale-Shapley.",
            intuition=(
                "Free men propose to women in preference order. "
                "Women keep their best offer and reject others. "
                "Rejected men move to next preference. "
                "Result: stable — no pair prefers each other over current matches."
            ),
            complexity_time_best="O(n²)",
            complexity_time_average="O(n²)",
            complexity_time_worst="O(n²)",
            complexity_space="O(n²)",
            tags=("greedy", "stable-matching", "gale-shapley", "bipartite"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        # array[i] = current engagement of man i: -1 (free) → 0-4 (engaged to woman i)
        # Visualize as bars: height = engaged_woman + 1 (1=free shown as 1)
        return SortState(
            array=tuple([1] * _N),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"GaleShapley n={_N}: all men free",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        # Gale-Shapley simulation
        man_match = [-1] * _N      # man_match[m] = woman m is engaged to, -1 if free
        woman_match = [-1] * _N   # woman_match[w] = man w is engaged to
        next_prop = [0] * _N      # next_prop[m] = next woman index to propose to
        free_men = list(range(_N))

        proposals = 0

        while free_men:
            m = free_men[0]
            w = _MEN_PREF[m][next_prop[m]]
            next_prop[m] += 1
            proposals += 1

            if woman_match[w] == -1:
                # w is free, accept
                man_match[m] = w
                woman_match[w] = m
                free_men.remove(m)
                arr = tuple(man_match[i] + 2 if man_match[i] >= 0 else 1 for i in range(_N))
                yield SortState(
                    array=arr,
                    comparing=(m, m),
                    last_swap=(m, m),
                    sorted_indices=frozenset(i for i in range(_N) if man_match[i] >= 0),
                    comparisons=proposals,
                    swaps=sum(1 for x in man_match if x >= 0),
                    description=(
                        f"M{m} proposes to W{w}: W{w} free → engaged! "
                        f"({sum(1 for x in man_match if x >= 0)}/{_N} matched)"
                    ),
                )
            else:
                m_current = woman_match[w]
                # w prefers m over current?
                if _WOMEN_PREF[w][m] < _WOMEN_PREF[w][m_current]:
                    # w dumps m_current for m
                    man_match[m] = w
                    woman_match[w] = m
                    man_match[m_current] = -1
                    free_men.remove(m)
                    free_men.append(m_current)
                    arr = tuple(man_match[i] + 2 if man_match[i] >= 0 else 1 for i in range(_N))
                    yield SortState(
                        array=arr,
                        comparing=(m, m_current),
                        last_swap=(m, m_current),
                        sorted_indices=frozenset(i for i in range(_N) if man_match[i] >= 0),
                        comparisons=proposals,
                        swaps=sum(1 for x in man_match if x >= 0),
                        description=(
                            f"M{m} proposes to W{w}: W{w} prefers M{m} over M{m_current} → swap!"
                        ),
                    )
                else:
                    arr = tuple(man_match[i] + 2 if man_match[i] >= 0 else 1 for i in range(_N))
                    yield SortState(
                        array=arr,
                        comparing=(m, m_current),
                        last_swap=None,
                        sorted_indices=frozenset(i for i in range(_N) if man_match[i] >= 0),
                        comparisons=proposals,
                        swaps=sum(1 for x in man_match if x >= 0),
                        description=(
                            f"M{m} proposes to W{w}: W{w} prefers M{m_current} → M{m} rejected"
                        ),
                    )

        arr = tuple(man_match[i] + 2 for i in range(_N))
        matching_str = ", ".join(f"M{m}↔W{w}" for m, w in enumerate(man_match))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(_N)),
            comparisons=proposals,
            swaps=_N,
            description=f"Stable matching: {matching_str}",
        )
