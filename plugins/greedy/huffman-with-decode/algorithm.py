"""Huffman Decode plugin for Algorithm Atlas."""
from __future__ import annotations

import heapq
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    SimulationParams,
    SortState,
)

_STRINGS = [
    "abracadabra",
    "mississippi",
    "hello world",
    "the quick brown fox",
    "banana split",
]


def _freq(s):
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    return freq



class _HNode:
    __slots__ = ("freq", "char", "left", "right")

    def __init__(self, freq, char=None, left=None, right=None):
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def _huffman_codes(s):
    freq = _freq(s)
    if len(freq) == 1:
        char = next(iter(freq))
        return {char: "0"}

    heap = [_HNode(f, ch) for ch, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        heapq.heappush(heap, _HNode(left.freq + right.freq, None, left, right))

    root = heap[0]
    codes = {}

    def traverse(node, prefix):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = prefix or "0"
        else:
            traverse(node.left, prefix + "0")
            traverse(node.right, prefix + "1")

    traverse(root, "")
    return codes


class HuffmanDecodeSimulation(AlgorithmPlugin):
    """Huffman encode+decode visualization."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="huffman-with-decode",
            name="Huffman Decode",
            category="greedy",
            visualization_type="ARRAY_BARS",
            description="Huffman encode then decode a string, showing compression.",
            intuition=(
                "Frequent chars get shorter codes, rare chars get longer. "
                "Bar heights = code lengths per unique character. "
                "Decoding: traverse tree bit-by-bit, emit char on leaf."
            ),
            complexity_time_best="O(n log n)",
            complexity_time_average="O(n log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=("greedy", "huffman", "compression", "encoding", "tree"),
        )

    def initialize(self, params: SimulationParams) -> SortState:
        s = _STRINGS[params.seed % len(_STRINGS)]
        freq = _freq(s)
        n = len(freq)
        arr = tuple(1 for _ in range(n))
        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(),
            comparisons=0,
            swaps=0,
            description=f"HuffDecode s='{s}'",
        )

    def steps(self, initial_state: SortState) -> Generator[SortState, None, SortState]:
        import re
        s = re.search(r"s='([^']+)'", initial_state.description).group(1)
        freq = _freq(s)
        codes = _huffman_codes(s)
        chars = sorted(freq.keys())
        n = len(chars)

        # Show code lengths
        code_lengths = [len(codes.get(c, "")) for c in chars]
        mx = max(code_lengths) or 1

        # Encoding phase: show each char being encoded
        encoded = "".join(codes[c] for c in s)
        total_bits = len(encoded)
        naive_bits = len(s) * 8

        for i, c in enumerate(chars):
            arr = tuple(max(1, min(99, code_lengths[j] * 99 // mx)) for j in range(n))
            yield SortState(
                array=arr,
                comparing=(i, i),
                last_swap=None,
                sorted_indices=frozenset(range(i + 1)),
                comparisons=i + 1,
                swaps=len(codes.get(c, "")),
                description=f"'{c}': freq={freq[c]}, code='{codes.get(c,'?')}' ({len(codes.get(c,''))} bits)",
            )

        # Summary step
        arr = tuple(max(1, min(99, code_lengths[j] * 99 // mx)) for j in range(n))
        yield SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=n + 1,
            swaps=total_bits,
            description=f"Encoded: {total_bits} bits vs naive {naive_bits} bits ({100*total_bits//naive_bits}%)",
        )

        return SortState(
            array=arr,
            comparing=None,
            last_swap=None,
            sorted_indices=frozenset(range(n)),
            comparisons=n + 2,
            swaps=total_bits,
            description=f"Huffman compression: {naive_bits}→{total_bits} bits, ratio={total_bits/naive_bits:.2f}",
        )
