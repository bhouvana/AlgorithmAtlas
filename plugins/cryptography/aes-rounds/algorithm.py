"""
AES Rounds (Simplified) — Algorithm Atlas Plugin

Pedagogical AES-128 demonstration showing the four round operations:
  1. SubBytes  — non-linear S-box byte substitution
  2. ShiftRows — cyclic row rotation
  3. MixColumns — matrix multiplication in GF(2^8)
  4. AddRoundKey — XOR with round key

Shows the first 3 rounds (initial AddRoundKey + 3 main rounds).
State is a 4×4 byte matrix displayed as 32 hex chars in `bits`.
~15 frames total.

The AES S-box, key schedule, and GF arithmetic are implemented
from scratch using only the stdlib.
"""
from __future__ import annotations

from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CryptoState,
    SimulationParams,
)

# ─── AES S-box ──────────────────────────────────────────────────────────────
_SBOX: Tuple[int, ...] = (
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
)

_RCON: Tuple[int, ...] = (
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36,
)


def _xtime(b: int) -> int:
    """Multiply b by 2 in GF(2^8)."""
    if b & 0x80:
        return ((b << 1) ^ 0x1b) & 0xFF
    return (b << 1) & 0xFF


def _gmul(a: int, b: int) -> int:
    """Multiply a and b in GF(2^8)."""
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1b
        b >>= 1
    return p


State = List[List[int]]  # 4x4 byte matrix


def _bytes_to_state(data: bytes) -> State:
    return [[data[r + 4 * c] for c in range(4)] for r in range(4)]


def _state_to_hex(state: State) -> str:
    return "".join(f"{state[r][c]:02x}" for c in range(4) for r in range(4))


def _sub_bytes(state: State) -> State:
    return [[_SBOX[state[r][c]] for c in range(4)] for r in range(4)]


def _shift_rows(state: State) -> State:
    return [
        [state[r][(c + r) % 4] for c in range(4)]
        for r in range(4)
    ]


def _mix_col(col: List[int]) -> List[int]:
    s0, s1, s2, s3 = col
    return [
        _gmul(s0, 2) ^ _gmul(s1, 3) ^ s2 ^ s3,
        s0 ^ _gmul(s1, 2) ^ _gmul(s2, 3) ^ s3,
        s0 ^ s1 ^ _gmul(s2, 2) ^ _gmul(s3, 3),
        _gmul(s0, 3) ^ s1 ^ s2 ^ _gmul(s3, 2),
    ]


def _mix_columns(state: State) -> State:
    result = [[0] * 4 for _ in range(4)]
    for c in range(4):
        col = [state[r][c] for r in range(4)]
        mixed = _mix_col(col)
        for r in range(4):
            result[r][c] = mixed[r]
    return result


def _add_round_key(state: State, key: State) -> State:
    return [[state[r][c] ^ key[r][c] for c in range(4)] for r in range(4)]


def _key_expansion(key: bytes) -> List[State]:
    """Return list of 11 round keys as State matrices."""
    w: List[int] = list(key)
    for i in range(4, 44):
        temp = w[(i - 1) * 4: i * 4]
        if i % 4 == 0:
            temp = [_SBOX[temp[1]], _SBOX[temp[2]], _SBOX[temp[3]], _SBOX[temp[0]]]
            temp[0] ^= _RCON[i // 4]
        for k in range(4):
            w.append(w[(i - 4) * 4 + k] ^ temp[k])

    round_keys = []
    for r in range(11):
        flat = w[r * 16: (r + 1) * 16]
        round_keys.append(_bytes_to_state(bytes(flat)))
    return round_keys


# Fixed 128-bit key and plaintext for pedagogy
_PLAINTEXT = bytes([
    0x32, 0x43, 0xf6, 0xa8, 0x88, 0x5a, 0x30, 0x8d,
    0x31, 0x31, 0x98, 0xa2, 0xe0, 0x37, 0x07, 0x34,
])
_KEY = bytes([
    0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
    0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c,
])


class AesRounds:
    """Simplified AES-128 round visualiser — first 3 rounds."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="aes-rounds",
            name="AES Rounds (Simplified)",
            category="cryptography",
            visualization_type="STATE_MACHINE",
            description=(
                "Pedagogical AES-128 demonstration showing SubBytes, ShiftRows, "
                "MixColumns, and AddRoundKey as distinct steps for the first 3 rounds."
            ),
            intuition=(
                "AES builds security through layers: SubBytes adds non-linearity, "
                "ShiftRows diffuses bytes across rows, MixColumns mixes columns, "
                "and AddRoundKey injects the secret."
            ),
            complexity_time_best="O(1)",
            complexity_time_average="O(1)",
            complexity_time_worst="O(1)",
            complexity_space="O(1)",
            tags=("cryptography", "aes", "symmetric", "block-cipher", "advanced"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CryptoState:
        state_hex = _PLAINTEXT.hex()
        return CryptoState(
            variables=(
                ("plaintext", _PLAINTEXT.hex()),
                ("key", _KEY.hex()),
                ("state", state_hex),
                ("round", "0"),
                ("operation", "init"),
            ),
            operation="state ← plaintext",
            step_name="Initial state",
            highlighted=("state", "plaintext"),
            bits=format(_PLAINTEXT[0], "08b"),
            result=None,
            description=(
                f"AES-128 initial state loaded from plaintext.\n"
                f"Plaintext: {_PLAINTEXT.hex()}\n"
                f"Key:       {_KEY.hex()}"
            ),
        )

    def steps(
        self, initial_state: AlgorithmState
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CryptoState)

        round_keys = _key_expansion(_KEY)
        state = _bytes_to_state(_PLAINTEXT)

        # Initial AddRoundKey (round 0)
        before = _state_to_hex(state)
        state = _add_round_key(state, round_keys[0])
        after = _state_to_hex(state)

        yield CryptoState(
            variables=(
                ("round", "0"),
                ("operation", "AddRoundKey"),
                ("state_before", before),
                ("round_key", _state_to_hex(round_keys[0])),
                ("state_after", after),
            ),
            operation=f"state XOR round_key[0]",
            step_name="Round 0 — AddRoundKey",
            highlighted=("state_after", "round_key"),
            bits=format(state[0][0], "08b"),
            result=None,
            description=(
                f"Round 0 — AddRoundKey: XOR each byte of the state with the "
                f"initial round key.\nBefore: {before}\nAfter:  {after}"
            ),
        )

        # Main rounds 1..3
        for rnd in range(1, 4):
            # SubBytes
            before = _state_to_hex(state)
            state = _sub_bytes(state)
            after = _state_to_hex(state)
            yield CryptoState(
                variables=(
                    ("round", str(rnd)),
                    ("operation", "SubBytes"),
                    ("state_before", before),
                    ("state_after", after),
                ),
                operation=f"state[r][c] ← SBOX[state[r][c]]",
                step_name=f"Round {rnd} — SubBytes",
                highlighted=("state_after",),
                bits=format(state[0][0], "08b"),
                result=None,
                description=(
                    f"Round {rnd} SubBytes: non-linear S-box substitution on each byte. "
                    f"\nBefore: {before}\nAfter:  {after}"
                ),
            )

            # ShiftRows
            before = _state_to_hex(state)
            state = _shift_rows(state)
            after = _state_to_hex(state)
            yield CryptoState(
                variables=(
                    ("round", str(rnd)),
                    ("operation", "ShiftRows"),
                    ("state_before", before),
                    ("state_after", after),
                ),
                operation="row i is cyclically shifted left by i positions",
                step_name=f"Round {rnd} — ShiftRows",
                highlighted=("state_after",),
                bits=format(state[0][0], "08b"),
                result=None,
                description=(
                    f"Round {rnd} ShiftRows: row 0 unchanged, row 1 shifted left 1, "
                    f"row 2 left 2, row 3 left 3.\nBefore: {before}\nAfter:  {after}"
                ),
            )

            # MixColumns (skip in final round)
            if rnd < 10:
                before = _state_to_hex(state)
                state = _mix_columns(state)
                after = _state_to_hex(state)
                yield CryptoState(
                    variables=(
                        ("round", str(rnd)),
                        ("operation", "MixColumns"),
                        ("state_before", before),
                        ("state_after", after),
                    ),
                    operation="each column multiplied by fixed matrix in GF(2^8)",
                    step_name=f"Round {rnd} — MixColumns",
                    highlighted=("state_after",),
                    bits=format(state[0][0], "08b"),
                    result=None,
                    description=(
                        f"Round {rnd} MixColumns: each 4-byte column is treated as a "
                        f"polynomial in GF(2^8) and multiplied by a fixed matrix.\n"
                        f"Before: {before}\nAfter:  {after}"
                    ),
                )

            # AddRoundKey
            before = _state_to_hex(state)
            rk = round_keys[rnd]
            state = _add_round_key(state, rk)
            after = _state_to_hex(state)
            yield CryptoState(
                variables=(
                    ("round", str(rnd)),
                    ("operation", "AddRoundKey"),
                    ("state_before", before),
                    ("round_key", _state_to_hex(rk)),
                    ("state_after", after),
                ),
                operation=f"state XOR round_key[{rnd}]",
                step_name=f"Round {rnd} — AddRoundKey",
                highlighted=("state_after", "round_key"),
                bits=format(state[0][0], "08b"),
                result=None,
                description=(
                    f"Round {rnd} AddRoundKey: XOR state with round key {rnd}.\n"
                    f"Before: {before}\nAfter:  {after}"
                ),
            )

        final_hex = _state_to_hex(state)
        return CryptoState(
            variables=(
                ("round", "3"),
                ("operation", "done"),
                ("state", final_hex),
                ("note", "3 of 10 rounds shown"),
            ),
            operation=f"State after 3 rounds = {final_hex}",
            step_name="3 rounds complete",
            highlighted=("state",),
            bits=format(state[0][0], "08b"),
            result=final_hex,
            description=(
                f"First 3 of 10 AES-128 rounds complete. "
                f"State: {final_hex}. "
                "(Full AES runs 10 rounds — last round omits MixColumns.)"
            ),
        )
