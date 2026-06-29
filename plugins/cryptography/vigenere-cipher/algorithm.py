"""
Vigenère Cipher — Algorithm Atlas Plugin

Encrypts "ATTACKATDAWN" using key "LEMON".  Each frame shows a single
character transformation: the plaintext char, the key char for that position,
and the resulting ciphertext char, along with the repeating key index.
"""
from __future__ import annotations

from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CryptoState,
    SimulationParams,
)

_PLAINTEXT = "ATTACKATDAWN"
_DEFAULT_KEY = "LEMON"


class VigenereCipher:
    """Vigenère Cipher simulation — one frame per plaintext character."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="vigenere-cipher",
            name="Vigenère Cipher",
            category="cryptography",
            visualization_type="STATE_MACHINE",
            description=(
                "A polyalphabetic substitution cipher that encrypts text using a "
                "repeating keyword, applying a different Caesar shift for each letter."
            ),
            intuition=(
                "Each plaintext character is shifted by the value of the corresponding "
                "keyword character. Because the shift changes with each letter, "
                "frequency analysis that breaks Caesar fails here."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("cryptography", "cipher", "polyalphabetic", "classical", "intermediate"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CryptoState:
        key_raw = str(params.inputs.get("key", _DEFAULT_KEY)).upper()
        key = "".join(c for c in key_raw if c.isalpha()) or _DEFAULT_KEY
        return CryptoState(
            variables=(
                ("plaintext", _PLAINTEXT),
                ("key", key),
                ("ciphertext", ""),
                ("position", "0"),
                ("key_char", ""),
                ("plain_char", ""),
                ("cipher_char", ""),
            ),
            operation="",
            step_name="Initialise",
            highlighted=("plaintext", "key"),
            bits=None,
            result=None,
            description=(
                f'Ready to encrypt "{_PLAINTEXT}" with key "{key}". '
                "Key repeats cyclically across the plaintext."
            ),
        )

    def steps(
        self, initial_state: AlgorithmState
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CryptoState)

        var_map = dict(initial_state.variables)
        key_raw = str(var_map.get("key", _DEFAULT_KEY)).upper()
        key = "".join(c for c in key_raw if c.isalpha()) or _DEFAULT_KEY
        plaintext = _PLAINTEXT
        ciphertext = ""
        key_index = 0

        for i, plain_char in enumerate(plaintext):
            key_char = key[key_index % len(key)]
            shift = ord(key_char) - ord("A")
            cipher_char = chr((ord(plain_char) - ord("A") + shift) % 26 + ord("A"))

            plain_pos = ord(plain_char) - ord("A")
            key_pos = ord(key_char) - ord("A")
            cipher_pos = (plain_pos + key_pos) % 26

            ciphertext += cipher_char
            key_index += 1

            op = (
                f"({plain_pos} + {key_pos}) mod 26 = {cipher_pos}"
                f"  →  '{plain_char}' + '{key_char}' → '{cipher_char}'"
            )

            yield CryptoState(
                variables=(
                    ("plaintext", plaintext),
                    ("key", key),
                    ("ciphertext", ciphertext),
                    ("position", str(i)),
                    ("key_index", str(key_index - 1)),
                    ("key_char", key_char),
                    ("plain_char", plain_char),
                    ("cipher_char", cipher_char),
                    ("shift", str(shift)),
                ),
                operation=op,
                step_name=f"Encrypt position {i + 1}/{len(plaintext)}",
                highlighted=("plain_char", "key_char", "cipher_char"),
                bits=format(ord(plain_char), "08b"),
                result=None,
                description=(
                    f"Position {i}: plain='{plain_char}' (idx {plain_pos}), "
                    f"key='{key_char}' (shift {key_pos}), "
                    f"cipher='{cipher_char}' (idx {cipher_pos})"
                ),
            )

        return CryptoState(
            variables=(
                ("plaintext", plaintext),
                ("key", key),
                ("ciphertext", ciphertext),
                ("position", str(len(plaintext))),
                ("key_char", ""),
                ("plain_char", ""),
                ("cipher_char", ""),
            ),
            operation=f'"{plaintext}" + key "{key}" → "{ciphertext}"',
            step_name="Complete",
            highlighted=("ciphertext",),
            bits=None,
            result=ciphertext,
            description=(
                f'Encryption complete. "{plaintext}" encrypted with key "{key}" '
                f'→ "{ciphertext}".'
            ),
        )
