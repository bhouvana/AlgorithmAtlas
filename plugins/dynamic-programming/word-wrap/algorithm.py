"""Word Wrap DP plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_LINE_WIDTH = 16
_WORDS = ["the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
_INF = 10 ** 9


def _extra(words, i, j, W):
    """Extra space if words[i..j] are on one line."""
    total = sum(len(words[k]) for k in range(i, j + 1)) + (j - i)
    return W - total


def _cost(words, i, j, W):
    e = _extra(words, i, j, W)
    if e < 0:
        return _INF
    if j == len(words) - 1:
        return 0  # last line has no penalty
    return e ** 3


class WordWrapSimulation(AlgorithmPlugin):
    """Word wrap optimization via DP."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="word-wrap",
            name="Word Wrap DP",
            category="dynamic-programming",
            visualization_type="ARRAY_BARS",
            description="Minimize total overflow penalty when wrapping words to fixed line width.",
            intuition=(
                "dp[i] = min total cost to wrap words[0..i-1]. "
                f"Line width = {_LINE_WIDTH}. "
                "Cost of a line = (extra spaces)^3. Last line has zero cost."
            ),
            complexity_time_best="O(n^2)",
            complexity_time_average="O(n^2)",
            complexity_time_worst="O(n^2)",
            complexity_space="O(n)",
            tags=("dynamic-programming", "word-wrap", "text-formatting", "optimization"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        n = len(_WORDS)
        return SortState(
            array=tuple([0] * (n + 1)),
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset([0]),
            comparisons=0,
            swaps=0,
            description=f"WordWrap W={_LINE_WIDTH} n={n}",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        n = len(_WORDS)
        dp = [_INF] * (n + 1)
        dp[0] = 0

        for i in range(1, n + 1):
            for j in range(i - 1, -1, -1):
                c = _cost(_WORDS, j, i - 1, _LINE_WIDTH)
                if c == _INF:
                    continue
                if dp[j] + c < dp[i]:
                    dp[i] = dp[j] + c

            # Normalize dp for display
            finite_vals = [v for v in dp if v < _INF]
            mx = max(finite_vals) if finite_vals else 1
            arr = tuple(
                max(1, min(99, v * 99 // max(mx, 1))) if v < _INF else 0
                for v in dp
            )
            yield SortState(
                array=arr,
                comparing=(i, i),
                last_swap=(i, i) if dp[i] < _INF else None,
                sorted_indices=frozenset(k for k in range(i + 1) if dp[k] < _INF),
                comparisons=i,
                swaps=dp[i] if dp[i] < _INF else 0,
                description=f"dp[{i}] = {dp[i]} (word '{_WORDS[i-1]}')",
            )

        finite_vals = [v for v in dp if v < _INF]
        mx = max(finite_vals) if finite_vals else 1
        arr = tuple(
            max(1, min(99, v * 99 // max(mx, 1))) if v < _INF else 0
            for v in dp
        )
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n + 1)),
            comparisons=n,
            swaps=dp[n],
            description=f"Min cost to wrap {n} words = {dp[n]}",
        )
