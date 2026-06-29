"""
SHA-256 Steps — Algorithm Atlas Plugin

Pedagogical walk-through of SHA-256 on input "abc":
  Phase 1 — Pre-processing: padding and bit-length encoding
  Phase 2 — Message schedule: W[0]..W[63] expansion
  Phase 3 — Compression: 64 rounds updating (a,b,c,d,e,f,g,h)

Uses stdlib hashlib only to verify the final result.
All arithmetic is implemented from scratch using stdlib struct/binascii.

~80 frames (1 init + 1 padding + 16 schedule init + 48 schedule expand +
            1 init state + 64 compression rounds + 1 final)
"""
from __future__ import annotations

import hashlib
import struct
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CryptoState,
    SimulationParams,
)

# SHA-256 constants: first 32 bits of fractional parts of cube roots of primes
_K: Tuple[int, ...] = (
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
)

# Initial hash values: first 32 bits of fractional parts of square roots of primes
_H0: Tuple[int, ...] = (
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
)

_MASK32 = 0xFFFFFFFF

_INPUT = "abc"


def _rotr(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & _MASK32


def _sigma0(x: int) -> int:
    return _rotr(x, 7) ^ _rotr(x, 18) ^ (x >> 3)


def _sigma1(x: int) -> int:
    return _rotr(x, 17) ^ _rotr(x, 19) ^ (x >> 10)


def _SIGMA0(x: int) -> int:
    return _rotr(x, 2) ^ _rotr(x, 13) ^ _rotr(x, 22)


def _SIGMA1(x: int) -> int:
    return _rotr(x, 6) ^ _rotr(x, 11) ^ _rotr(x, 25)


def _Ch(e: int, f: int, g: int) -> int:
    return (e & f) ^ (~e & g) & _MASK32


def _Maj(a: int, b: int, c: int) -> int:
    return (a & b) ^ (a & c) ^ (b & c)


def _pad_message(msg: bytes) -> bytes:
    """SHA-256 padding: append 0x80, zeros, then 64-bit big-endian bit length."""
    bit_len = len(msg) * 8
    msg += b"\x80"
    while len(msg) % 64 != 56:
        msg += b"\x00"
    msg += struct.pack(">Q", bit_len)
    return msg


class Sha256Steps:
    """Pedagogical SHA-256 simulation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="sha256-steps",
            name="SHA-256 Hash Function",
            category="cryptography",
            visualization_type="STATE_MACHINE",
            description=(
                "Pedagogical walk-through of SHA-256: pre-processing (padding and length "
                "encoding), message schedule expansion (W[0]..W[63]), and the 64-round "
                "compression function updating the 8-word state (a,b,c,d,e,f,g,h)."
            ),
            intuition=(
                "SHA-256 scrambles data through 64 rounds of bitwise mixing. "
                "Each round feeds the output back in — a single bit change avalanches "
                "through the entire hash."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(1)",
            tags=("cryptography", "hash", "sha256", "one-way", "advanced"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CryptoState:
        msg_bytes = _INPUT.encode("ascii")
        bits_str = "".join(format(b, "08b") for b in msg_bytes)
        return CryptoState(
            variables=(
                ("input", _INPUT),
                ("input_hex", msg_bytes.hex()),
                ("input_bits", bits_str),
                ("padded_len", "?"),
                ("hash", "?"),
            ),
            operation="",
            step_name="Input",
            highlighted=("input",),
            bits=format(msg_bytes[0], "08b"),
            result=None,
            description=(
                f'Input: "{_INPUT}" ({len(msg_bytes)} bytes = {len(msg_bytes) * 8} bits). '
                "SHA-256 processes data in 512-bit (64-byte) blocks."
            ),
        )

    def steps(
        self, initial_state: AlgorithmState
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CryptoState)

        msg_bytes = _INPUT.encode("ascii")
        padded = _pad_message(msg_bytes)

        # Frame: Padding
        pad_hex = padded.hex()
        yield CryptoState(
            variables=(
                ("input", _INPUT),
                ("input_bytes", str(len(msg_bytes))),
                ("padded_bytes", str(len(padded))),
                ("padded_hex", pad_hex[:32] + "..."),
            ),
            operation=(
                f"Append 0x80, pad zeros, append length={len(msg_bytes) * 8} bits as 64-bit BE"
            ),
            step_name="Pre-processing: padding",
            highlighted=("padded_bytes", "padded_hex"),
            bits=format(padded[3], "08b"),
            result=None,
            description=(
                f"Pad message to 512 bits (64 bytes): append 0x80 byte, "
                f"then zeros, then 64-bit big-endian bit count ({len(msg_bytes) * 8}). "
                f"Padded length: {len(padded)} bytes."
            ),
        )

        # Unpack the single 512-bit block into 16 words
        W: List[int] = list(struct.unpack(">16I", padded[:64]))

        # Frames: W[0]..W[15] (initial schedule words)
        for i in range(16):
            yield CryptoState(
                variables=(
                    ("schedule_i", str(i)),
                    ("W_i", f"0x{W[i]:08x}"),
                    ("W_hex", " ".join(f"0x{W[j]:08x}" for j in range(min(i + 1, 8)))),
                ),
                operation=f"W[{i}] = padded_block[{i}] = 0x{W[i]:08x}",
                step_name=f"Message schedule W[{i}]",
                highlighted=("W_i", "schedule_i"),
                bits=format((W[i] >> 24) & 0xFF, "08b"),
                result=None,
                description=(
                    f"W[{i}] is loaded directly from the {i}th 32-bit word "
                    f"of the padded message block: 0x{W[i]:08x}."
                ),
            )

        # Extend schedule to W[16]..W[63]
        for i in range(16, 64):
            s0 = _sigma0(W[i - 15])
            s1 = _sigma1(W[i - 2])
            w_new = (W[i - 16] + s0 + W[i - 7] + s1) & _MASK32
            W.append(w_new)

            yield CryptoState(
                variables=(
                    ("schedule_i", str(i)),
                    ("W_i_minus_16", f"0x{W[i - 16]:08x}"),
                    ("sigma0_W_i_minus_15", f"0x{s0:08x}"),
                    ("W_i_minus_7", f"0x{W[i - 7]:08x}"),
                    ("sigma1_W_i_minus_2", f"0x{s1:08x}"),
                    ("W_i", f"0x{w_new:08x}"),
                ),
                operation=(
                    f"W[{i}] = W[{i-16}] + σ0(W[{i-15}]) + W[{i-7}] + σ1(W[{i-2}])\n"
                    f"      = 0x{W[i-16]:08x} + 0x{s0:08x} + 0x{W[i-7]:08x} + 0x{s1:08x}\n"
                    f"      = 0x{w_new:08x}"
                ),
                step_name=f"Expand schedule W[{i}]",
                highlighted=("W_i", "sigma0_W_i_minus_15", "sigma1_W_i_minus_2"),
                bits=format((w_new >> 24) & 0xFF, "08b"),
                result=None,
                description=(
                    f"W[{i}] expanded using σ0(W[{i-15}]) and σ1(W[{i-2}]). "
                    f"Result: 0x{w_new:08x}."
                ),
            )

        # Initialise working variables
        a, b, c, d, e, f, g, h = _H0

        yield CryptoState(
            variables=(
                ("a", f"0x{a:08x}"), ("b", f"0x{b:08x}"),
                ("c", f"0x{c:08x}"), ("d", f"0x{d:08x}"),
                ("e", f"0x{e:08x}"), ("f", f"0x{f:08x}"),
                ("g", f"0x{g:08x}"), ("h", f"0x{h:08x}"),
            ),
            operation="(a,b,c,d,e,f,g,h) ← initial hash values H0",
            step_name="Init compression state",
            highlighted=("a", "b", "c", "d", "e", "f", "g", "h"),
            bits=format(a & 0xFF, "08b"),
            result=None,
            description=(
                "Initialise working variables (a..h) to SHA-256 initial hash values "
                "(first 32 bits of fractional parts of sqrt of first 8 primes)."
            ),
        )

        # 64 compression rounds
        for i in range(64):
            T1 = (h + _SIGMA1(e) + _Ch(e, f, g) + _K[i] + W[i]) & _MASK32
            T2 = (_SIGMA0(a) + _Maj(a, b, c)) & _MASK32
            h = g
            g = f
            f = e
            e = (d + T1) & _MASK32
            d = c
            c = b
            b = a
            a = (T1 + T2) & _MASK32

            yield CryptoState(
                variables=(
                    ("round", str(i)),
                    ("a", f"0x{a:08x}"), ("b", f"0x{b:08x}"),
                    ("c", f"0x{c:08x}"), ("d", f"0x{d:08x}"),
                    ("e", f"0x{e:08x}"), ("f", f"0x{f:08x}"),
                    ("g", f"0x{g:08x}"), ("h", f"0x{h:08x}"),
                    ("T1", f"0x{T1:08x}"), ("T2", f"0x{T2:08x}"),
                    ("K_i", f"0x{_K[i]:08x}"), ("W_i", f"0x{W[i]:08x}"),
                ),
                operation=(
                    f"T1 = h+Σ1(e)+Ch(e,f,g)+K[{i}]+W[{i}] = 0x{T1:08x}\n"
                    f"T2 = Σ0(a)+Maj(a,b,c)              = 0x{T2:08x}\n"
                    f"a ← T1+T2 = 0x{a:08x},  e ← d+T1 = 0x{e:08x}"
                ),
                step_name=f"Compression round {i}",
                highlighted=("a", "e", "T1", "T2"),
                bits=format(a & 0xFF, "08b"),
                result=None,
                description=(
                    f"Round {i}: compute T1 (Σ1+Ch+K+W) and T2 (Σ0+Maj), "
                    f"rotate state. a=0x{a:08x}, e=0x{e:08x}."
                ),
            )

        # Final hash addition
        H = [
            (_H0[0] + a) & _MASK32,
            (_H0[1] + b) & _MASK32,
            (_H0[2] + c) & _MASK32,
            (_H0[3] + d) & _MASK32,
            (_H0[4] + e) & _MASK32,
            (_H0[5] + f) & _MASK32,
            (_H0[6] + g) & _MASK32,
            (_H0[7] + h) & _MASK32,
        ]
        digest = "".join(f"{v:08x}" for v in H)
        expected = hashlib.sha256(_INPUT.encode()).hexdigest()

        return CryptoState(
            variables=(
                ("input", _INPUT),
                ("sha256", digest),
                ("verified", str(digest == expected)),
            ),
            operation="H_final = H0 + (a,b,c,d,e,f,g,h)",
            step_name="Final hash",
            highlighted=("sha256",),
            bits=format(H[0] & 0xFF, "08b"),
            result=digest,
            description=(
                f'SHA-256("{_INPUT}") = {digest}\n'
                f"Verified against stdlib: {digest == expected} ✓"
            ),
        )
