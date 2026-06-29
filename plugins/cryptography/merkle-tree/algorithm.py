"""
Merkle Tree — Algorithm Atlas Plugin

Builds a binary Merkle tree over 8 leaf data items ("TX0".."TX7").
Uses a truncated SHA-256 hex digest (first 8 chars) as the "hash" function
so values are readable in the visualiser.

Frame sequence (~12 frames):
  1 init frame showing the 8 leaves
  7 frames: compute L2 hashes (TX0+TX1, TX2+TX3, TX4+TX5, TX6+TX7)
  3 frames: compute L1 hashes (pairs of L2)
  1 frame:  compute root
  1 final frame: tree complete
"""
from __future__ import annotations

import hashlib
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CryptoState,
    SimulationParams,
)

_LEAVES = ["TX0", "TX1", "TX2", "TX3", "TX4", "TX5", "TX6", "TX7"]


def _fake_hash(data: str) -> str:
    """Return first 8 hex chars of SHA-256 of data — readable in the visualiser."""
    return hashlib.sha256(data.encode()).hexdigest()[:8]


def _hash_pair(left: str, right: str) -> str:
    return _fake_hash(left + right)


class MerkleTree:
    """Merkle Tree build simulation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="merkle-tree",
            name="Merkle Tree",
            category="cryptography",
            visualization_type="STATE_MACHINE",
            description=(
                "Builds a binary Merkle tree over 8 leaf data items by repeatedly "
                "hashing pairs of nodes upward until a single root hash is produced."
            ),
            intuition=(
                "Like a chain of receipts — each parent proves both children are unchanged. "
                "Tampering with any leaf invalidates every ancestor up to the root, "
                "making fraud detectable in O(log n) checks."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("cryptography", "merkle", "hash", "blockchain", "intermediate"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CryptoState:
        leaf_hashes = [_fake_hash(tx) for tx in _LEAVES]
        return CryptoState(
            variables=tuple(
                (f"leaf_{i}", f"{_LEAVES[i]}→{leaf_hashes[i]}") for i in range(8)
            ),
            operation="Hash each leaf: h(TX_i) = SHA256(TX_i)[:8]",
            step_name="Leaf hashing",
            highlighted=tuple(f"leaf_{i}" for i in range(8)),
            bits=format(ord(_LEAVES[0][0]), "08b"),
            result=None,
            description=(
                "Level 0 (leaves): hash each transaction string to produce the 8 leaf hashes."
            ),
        )

    def steps(
        self, initial_state: AlgorithmState
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CryptoState)

        # Level 0: leaf hashes
        level: List[str] = [_fake_hash(tx) for tx in _LEAVES]

        # Show initial leaves
        yield CryptoState(
            variables=tuple(
                (f"L0_{i}", f"{_LEAVES[i]}→{level[i]}") for i in range(8)
            ),
            operation="Level 0: compute leaf hashes",
            step_name="Level 0 — Leaf hashes",
            highlighted=tuple(f"L0_{i}" for i in range(8)),
            bits=format(int(level[0][:2], 16), "08b"),
            result=None,
            description=(
                "Level 0: 8 leaf hashes computed. Each is the first 8 hex characters "
                "of SHA-256(TX_i)."
            ),
        )

        tree_levels: List[List[str]] = [level[:]]

        lvl_num = 1
        while len(level) > 1:
            next_level: List[str] = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i + 1] if i + 1 < len(level) else level[i]
                parent = _hash_pair(left, right)
                next_level.append(parent)

                yield CryptoState(
                    variables=(
                        ("level", str(lvl_num)),
                        ("left_child", left),
                        ("right_child", right),
                        ("parent_hash", parent),
                        ("node_index", str(i // 2)),
                        ("current_nodes", str(len(next_level))),
                    ),
                    operation=(
                        f"L{lvl_num}[{i // 2}] = hash(L{lvl_num - 1}[{i}] + L{lvl_num - 1}[{i + 1 if i + 1 < len(level) else i}])\n"
                        f"= hash({left} + {right})\n"
                        f"= {parent}"
                    ),
                    step_name=f"Level {lvl_num} — Node {i // 2}",
                    highlighted=("parent_hash", "left_child", "right_child"),
                    bits=format(int(left[:2], 16), "08b"),
                    result=None,
                    description=(
                        f"Level {lvl_num}, node {i // 2}: "
                        f"hash({left} || {right}) = {parent}"
                    ),
                )

            level = next_level
            tree_levels.append(level[:])
            lvl_num += 1

        root = level[0]

        yield CryptoState(
            variables=(
                ("root", root),
                ("level", str(lvl_num - 1)),
                ("total_levels", str(lvl_num)),
                ("leaf_count", "8"),
            ),
            operation=f"Merkle root = {root}",
            step_name="Root computed",
            highlighted=("root",),
            bits=format(int(root[:2], 16), "08b"),
            result=root,
            description=(
                f"Merkle tree complete. Root hash = {root}. "
                "Any change to any leaf will cascade and change the root."
            ),
        )

        return CryptoState(
            variables=(
                ("root", root),
                ("level_0", " ".join(tree_levels[0])),
                ("level_1", " ".join(tree_levels[1])),
                ("level_2", " ".join(tree_levels[2])),
            ),
            operation=f"Merkle root = {root}",
            step_name="Tree complete",
            highlighted=("root",),
            bits=None,
            result=root,
            description=(
                f"Merkle Tree over {len(_LEAVES)} transactions. "
                f"Root = {root}. "
                f"Height = 3 levels."
            ),
        )
