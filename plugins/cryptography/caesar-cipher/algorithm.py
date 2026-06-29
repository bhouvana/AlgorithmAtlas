"""
Caesar Cipher — Algorithm Atlas Plugin

Encrypts "HELLO WORLD" character by character with a configurable shift.
Each letter transformation is shown as a distinct frame so the viewer can
follow exactly how the substitution works.  Non-alpha characters are kept
as-is and produce a "pass-through" frame.
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

_PLAINTEXT = "HELLO WORLD"


def _shift_char(ch: str, shift: int) -> str:
    """Shift a single uppercase letter by shift positions (mod 26)."""
    if ch.isalpha():
        return chr((ord(ch) - ord("A") + shift) % 26 + ord("A"))
    return ch


class CaesarCipher:
    """Caesar Cipher simulation — one frame per character."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="caesar-cipher",
            name="Caesar Cipher",
            category="cryptography",
            visualization_type="STATE_MACHINE",
            description=(
                "A substitution cipher that shifts each letter in the plaintext "
                "by a fixed number of positions in the alphabet."
            ),
            intuition=(
                "Each letter is rotated forward by a constant shift. "
                "'A' with shift 3 becomes 'D'; 'Z' wraps around to 'C'. "
                "Julius Caesar reportedly used shift 3 for military messages."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("cryptography", "cipher", "substitution", "classical", "beginner"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CryptoState:
        shift = int(params.inputs.get("shift", 3)) % 26
        return CryptoState(
            variables=(
                ("plaintext", _PLAINTEXT),
                ("ciphertext", ""),
                ("shift", str(shift)),
                ("current_char", ""),
                ("shifted_char", ""),
            ),
            operation="",
            step_name="Initialise",
            highlighted=("plaintext", "shift"),
            bits=None,
            result=None,
            description=(
                f'Ready to encrypt "{_PLAINTEXT}" with shift={shift}. '
                "Each letter will be rotated forward by the shift amount."
            ),
        )

    def steps(
        self, initial_state: AlgorithmState
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CryptoState)

        # Recover parameters from initial state
        var_map = dict(initial_state.variables)
        shift = int(var_map["shift"])
        plaintext = _PLAINTEXT
        ciphertext = ""

        for i, ch in enumerate(plaintext):
            shifted = _shift_char(ch, shift)

            if ch.isalpha():
                plain_ord = ord(ch) - ord("A")
                cipher_ord = (plain_ord + shift) % 26
                op = (
                    f"({ord(ch) - ord('A')} + {shift}) mod 26 = {cipher_ord}"
                    f"  →  '{ch}' → '{shifted}'"
                )
                desc = (
                    f"Step {i + 1}: character '{ch}' (position {plain_ord}) "
                    f"shifted by {shift} → position {cipher_ord} → '{shifted}'"
                )
                highlighted = ("current_char", "shifted_char", "shift")
            else:
                op = f"'{ch}' is not a letter — pass through unchanged"
                desc = f"Step {i + 1}: '{ch}' is not a letter; keeping it as-is."
                highlighted = ("current_char",)

            ciphertext += shifted

            yield CryptoState(
                variables=(
                    ("plaintext", plaintext),
                    ("ciphertext", ciphertext),
                    ("shift", str(shift)),
                    ("current_char", ch),
                    ("shifted_char", shifted),
                    ("position", str(i)),
                ),
                operation=op,
                step_name=f"Encrypt char {i + 1}/{len(plaintext)}",
                highlighted=highlighted,
                bits=format(ord(ch), "08b") if ch.isalpha() else None,
                result=None,
                description=desc,
            )

        # Final frame
        return CryptoState(
            variables=(
                ("plaintext", plaintext),
                ("ciphertext", ciphertext),
                ("shift", str(shift)),
                ("current_char", ""),
                ("shifted_char", ""),
            ),
            operation=f'"{plaintext}" encrypted with shift {shift}',
            step_name="Complete",
            highlighted=("ciphertext",),
            bits=None,
            result=ciphertext,
            description=(
                f'Encryption complete. "{plaintext}" → "{ciphertext}" '
                f"using Caesar shift={shift}."
            ),
        )
