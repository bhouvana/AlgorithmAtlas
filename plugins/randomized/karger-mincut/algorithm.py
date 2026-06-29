"""Karger's Min-Cut plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

# Fixed graph: 6 nodes, min cut = 2 (between {0,1,2} and {3,4,5})
_N_NODES = 6
_ORIG_EDGES = [
    (0, 1), (0, 2), (1, 2),   # dense triangle 0-1-2
    (3, 4), (3, 5), (4, 5),   # dense triangle 3-4-5
    (2, 3), (1, 4),             # two cross edges (min cut = 2)
]
_TRUE_MINCUT = 2


def _karger_run(edges, n, seed):
    """Run one instance of Karger's algorithm. Returns cut size."""
    # Build adjacency as list of (u, v) edges
    e = list(edges)
    # Union-find
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    rng = seed
    nodes_left = n
    steps = []

    while nodes_left > 2:
        # Pick random edge
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        idx = rng % len(e)
        u, v = e[idx]
        ru, rv = find(u), find(v)
        if ru == rv:
            # Self loop, remove
            e.pop(idx)
            continue
        union(ru, rv)
        nodes_left -= 1
        # Remove self-loops
        e = [(a, b) for a, b in e if find(a) != find(b)]
        steps.append((len(e), nodes_left))

    return len(e), steps


def _karger_multi(edges, n, trials, base_seed):
    """Run Karger's algorithm multiple times and return (min_cut, all_results)."""
    results = []
    for t in range(trials):
        cut, steps = _karger_run(edges, n, base_seed + t * 7919)
        results.append((cut, steps))
    min_cut = min(r[0] for r in results)
    return min_cut, results


class KargerMincutSimulation(AlgorithmPlugin):
    """Karger's randomized min-cut visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="karger-mincut",
            name="Karger's Min-Cut",
            category="randomized",
            visualization_type="ARRAY_BARS",
            description="Randomized min-cut via edge contraction.",
            intuition=(
                f"Graph has {_N_NODES} nodes, min cut = {_TRUE_MINCUT}. "
                "Each trial contracts random edges until 2 nodes remain. "
                "Bar heights = remaining edges after each contraction."
            ),
            complexity_time_best="O(V²)",
            complexity_time_average="O(V² log V)",
            complexity_time_worst="O(V² log V)",
            complexity_space="O(V + E)",
            tags=("randomized", "karger", "min-cut", "graph", "contraction"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n_trials = 8
        arr = tuple(len(_ORIG_EDGES) for _ in range(n_trials))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=len(_ORIG_EDGES),
            description=f"Karger n={_N_NODES} edges={len(_ORIG_EDGES)} trials=8",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        n_trials = 8
        min_cut, all_results = _karger_multi(_ORIG_EDGES, _N_NODES, n_trials, 42)

        trial_cuts = [r[0] for r in all_results]
        best_so_far = len(_ORIG_EDGES)

        for t, (cut, steps) in enumerate(all_results):
            best_so_far = min(best_so_far, cut)
            # Show remaining edges count per trial
            arr = tuple(
                max(1, min(99, trial_cuts[i] * 99 // max(max(trial_cuts), 1)))
                if i <= t else max(1, min(99, len(_ORIG_EDGES) * 99 // max(max(trial_cuts), 1)))
                for i in range(n_trials)
            )
            found_true = cut == _TRUE_MINCUT
            yield SortState(
                array=arr,
                comparing=(t, t),
                last_swap=(t, t) if found_true else None,
                sorted_indices=frozenset(i for i in range(t + 1) if trial_cuts[i] == _TRUE_MINCUT),
                comparisons=t + 1,
                swaps=best_so_far,
                description=f"Trial {t+1}: cut={cut} (best so far={best_so_far})"
                + (" ✓ optimal!" if found_true else ""),
            )

        return SortState(
            array=tuple(
                max(1, min(99, c * 99 // max(max(trial_cuts), 1))) for c in trial_cuts
            ),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(i for i in range(n_trials) if trial_cuts[i] == min_cut),
            comparisons=n_trials,
            swaps=min_cut,
            description=f"Min-cut = {min_cut} (true={_TRUE_MINCUT}). "
                        f"{sum(1 for c in trial_cuts if c == min_cut)}/{n_trials} trials found it.",
        )
