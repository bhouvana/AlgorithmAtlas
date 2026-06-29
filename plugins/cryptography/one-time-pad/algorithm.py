"""
One-Time Pad (OTP) — Algorithm Atlas Plugin

Encrypts "HELLO" with a random key derived from a configurable seed.
Shows byte-by-byte XOR for encryption, then byte-by-byte XOR for decryption.
The `bits` field shows the 8-bit binary of the plaintext byte XOR'd with the key byte.

~12 frames:
  1 init
  5 encrypt frames (one per character)
  1 ciphertext summary
  5 decrypt frames
  1 final match
"""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CryptoState,
    SimulationParams,
)

_PLAINTEXT = "HELLO"


def _xor_bits(a: int, b: int) -> str:
    """Return '  a_bits  XOR  b_bits  =  result_bits' as a compact operation string."""
    return (
        f"{format(a, '08b')} XOR {format(b, '08b')} = {format(a ^ b, '08b')}"
    )


class OneTimePad:
    """One-Time Pad simulation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="one-time-pad",
            name="One-Time Pad (OTP)",
            category="cryptography",
            visualization_type="STATE_MACHINE",
            description=(
                "Demonstrates the One-Time Pad cipher: XOR each plaintext byte with a "
                "corresponding random key byte to produce ciphertext, then XOR with the "
                "same key to decrypt — the only provably unbreakable cipher."
            ),
            intuition=(
                "XOR is its own inverse: A⊕K=C and C⊕K=A. Because the key is truly "
                "random and never reused, the ciphertext reveals zero information about "
                "the plaintext — every possible message is equally likely."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("cryptography", "otp", "xor", "information-theoretic", "beginner"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CryptoState:
        seed = int(params.inputs.get("seed", 42))
        rng = random.Random(seed)
        key_bytes = [rng.randint(0, 255) for _ in range(len(_PLAINTEXT))]
        key_str = " ".join(format(b, "02x") for b in key_bytes)
        plain_bytes = [ord(c) for c in _PLAINTEXT]
        plain_str = " ".join(format(b, "02x") for b in plain_bytes)
        return CryptoState(
            variables=(
                ("plaintext", _PLAINTEXT),
                ("plaintext_hex", plain_str),
                ("key_hex", key_str),
                ("ciphertext_hex", ""),
                ("seed", str(seed)),
            ),
            operation="Generate random key",
            step_name="Initialise",
            highlighted=("plaintext", "key_hex"),
            bits=format(plain_bytes[0], "08b"),
            result=None,
            description=(
                f'One-Time Pad: plaintext = "{_PLAINTEXT}". '
                f"Random key (seed={seed}): {key_str}. "
                "Key length must equal message length. Key must never be reused."
            ),
        )

    def steps(
        self, initial_state: AlgorithmState
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CryptoState)

        var_map = dict(initial_state.variables)
        seed = int(var_map["seed"])
        rng = random.Random(seed)
        key_bytes = [rng.randint(0, 255) for _ in range(len(_PLAINTEXT))]
        plain_bytes = [ord(c) for c in _PLAINTEXT]

        cipher_bytes = []

        # Encryption phase
        for i, (pb, kb) in enumerate(zip(plain_bytes, key_bytes)):
            cb = pb ^ kb
            cipher_bytes.append(cb)

            cipher_so_far = " ".join(format(b, "02x") for b in cipher_bytes)

            yield CryptoState(
                variables=(
                    ("step", f"encrypt {i + 1}/{len(_PLAINTEXT)}"),
                    ("plaintext_char", _PLAINTEXT[i]),
                    ("plaintext_byte", f"0x{pb:02x}"),
                    ("key_byte", f"0x{kb:02x}"),
                    ("cipher_byte", f"0x{cb:02x}"),
                    ("operation", "XOR"),
                    ("ciphertext_so_far", cipher_so_far),
                ),
                operation=_xor_bits(pb, kb),
                step_name=f"Encrypt byte {i + 1}: '{_PLAINTEXT[i]}'",
                highlighted=("plaintext_byte", "key_byte", "cipher_byte"),
                bits=format(pb, "08b"),
                result=None,
                description=(
                    f"Encrypt '{_PLAINTEXT[i]}': "
                    f"0x{pb:02x} ({format(pb,'08b')}) "
                    f"XOR 0x{kb:02x} ({format(kb,'08b')}) "
                    f"= 0x{cb:02x} ({format(cb,'08b')})"
                ),
            )

        cipher_hex = " ".join(format(b, "02x") for b in cipher_bytes)

        yield CryptoState(
            variables=(
                ("plaintext", _PLAINTEXT),
                ("key_hex", " ".join(f"0x{b:02x}" for b in key_bytes)),
                ("ciphertext_hex", cipher_hex),
                ("phase", "encryption complete"),
            ),
            operation=f'"{_PLAINTEXT}" encrypted → {cipher_hex}',
            step_name="Encryption complete",
            highlighted=("ciphertext_hex",),
            bits=format(cipher_bytes[0], "08b"),
            result=None,
            description=(
                f"Encryption complete. Ciphertext: {cipher_hex}. "
                "Now decrypting by XOR-ing ciphertext with the same key."
            ),
        )

        # Decryption phase
        decrypted = []
        for i, (cb, kb) in enumerate(zip(cipher_bytes, key_bytes)):
            rb = cb ^ kb
            decrypted.append(chr(rb))

            decrypted_so_far = "".join(decrypted)

            yield CryptoState(
                variables=(
                    ("step", f"decrypt {i + 1}/{len(_PLAINTEXT)}"),
                    ("cipher_byte", f"0x{cb:02x}"),
                    ("key_byte", f"0x{kb:02x}"),
                    ("recovered_byte", f"0x{rb:02x}"),
                    ("recovered_char", chr(rb)),
                    ("operation", "XOR"),
                    ("decrypted_so_far", decrypted_so_far),
                ),
                operation=_xor_bits(cb, kb),
                step_name=f"Decrypt byte {i + 1}",
                highlighted=("cipher_byte", "key_byte", "recovered_byte", "recovered_char"),
                bits=format(cb, "08b"),
                result=None,
                description=(
                    f"Decrypt byte {i + 1}: "
                    f"0x{cb:02x} XOR 0x{kb:02x} = 0x{rb:02x} = '{chr(rb)}'"
                ),
            )

        recovered = "".join(decrypted)

        return CryptoState(
            variables=(
                ("plaintext", _PLAINTEXT),
                ("ciphertext_hex", cipher_hex),
                ("key_hex", " ".join(f"0x{b:02x}" for b in key_bytes)),
                ("recovered", recovered),
                ("match", str(recovered == _PLAINTEXT)),
            ),
            operation=f'decrypt("{cipher_hex}") = "{recovered}"',
            step_name="Decryption complete",
            highlighted=("recovered", "plaintext"),
            bits=None,
            result=recovered,
            description=(
                f'OTP complete. Plaintext="{_PLAINTEXT}", Ciphertext="{cipher_hex}", '
                f'Recovered="{recovered}". Match: {recovered == _PLAINTEXT} ✓. '
                "The key must be discarded — reusing it would break the perfect secrecy guarantee."
            ),
        )
