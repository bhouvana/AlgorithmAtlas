"""Run-Length Encoding plugin for Algorithm Atlas."""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_EXAMPLES = [
    "AABBBCCDDDDEE",
    "AAABBBCCCCDDDDEEEE",
    "XYYYYZZZZ",
    "AABBCCDDEE",
    "WWWWWAAAABBCC",
]


def _str_to_array(s: str) -> tuple:
    """Map character to bar height: A=4, B=8, ..., Z=100."""
    return tuple(max(1, (ord(c) - ord('A') + 1) * 4) for c in s)


class RunLengthEncodingSimulation(AlgorithmPlugin):
    """Run-length encoding compression."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="run-length-encoding",
            name="Run-Length Encoding",
            category="string",
            visualization_type="ARRAY_BARS",
            description=(
                "Compress a string by replacing consecutive identical characters "
                "with (count, char)."
            ),
            intuition=(
                "Scan left-to-right, track run length. "
                "When character changes, emit (count, char). "
                "Effective for highly repetitive strings."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("string", "compression", "run-length", "encoding"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        s = _EXAMPLES[params.seed % len(_EXAMPLES)]
        arr = _str_to_array(s)
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"RLE input='{s}'",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        s = re.search(r"input='([^']+)'", initial_state.description).group(1)
        arr = _str_to_array(s)
        n = len(s)
        encoded: list[tuple] = []  # (count, char)
        run_starts: set = set()

        i = 0
        while i < n:
            run_start = i
            count = 1
            while i + count < n and s[i + count] == s[i]:
                count += 1

            encoded.append((count, s[i]))
            run_starts.add(run_start)

            # Highlight the current run and all run-starts found so far
            yield SortState(
                array=arr,
                comparing=(run_start, run_start + count - 1),
                last_swap=(run_start, run_start + count - 1) if count > 1 else None,
                sorted_indices=frozenset(run_starts),
                comparisons=run_start + count,
                swaps=len(encoded),
                description=(
                    f"Run at [{run_start}..{run_start+count-1}]: "
                    f"'{s[i]}' × {count} → '{count}{s[i]}'"
                ),
            )
            i += count

        encoded_str = "".join(f"{c}{ch}" for c, ch in encoded)
        ratio = len(s) / len(encoded_str) if encoded_str else 1.0

        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(run_starts),
            comparisons=n,
            swaps=len(encoded),
            description=(
                f"Encoded: '{encoded_str}' "
                f"({n}→{len(encoded_str)} chars, ratio={ratio:.2f}x)"
            ),
        )
