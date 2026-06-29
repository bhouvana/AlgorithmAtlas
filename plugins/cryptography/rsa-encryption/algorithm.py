"""
RSA Encryption & Decryption — Algorithm Atlas Plugin

Uses pre-generated key pair: n=3233, e=17, d=2753 (from p=61, q=53).
Shows fast modular exponentiation (successive squaring) for both
encryption C = M^e mod n and decryption M' = C^d mod n.
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

# Fixed RSA parameters (from p=61, q=53)
_N = 3233
_E = 17
_D = 2753


def _mod_exp_steps(base: int, exp: int, mod: int) -> List[Tuple[int, int, int, int]]:
    """
    Return list of (bit, current_result, current_base, description_idx) tuples
    tracing fast modular exponentiation (right-to-left binary method).
    Each tuple: (bit_value, result_after_this_bit, square_value, bit_position)
    """
    steps: List[Tuple[int, int, int, int]] = []
    result = 1
    b = base % mod
    pos = 0
    while exp > 0:
        bit = exp & 1
        steps.append((bit, result, b, pos))
        if bit:
            result = (result * b) % mod
        b = (b * b) % mod
        exp >>= 1
        pos += 1
    return steps


class RsaEncryption:
    """RSA Encryption and Decryption simulation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="rsa-encryption",
            name="RSA Encryption & Decryption",
            category="cryptography",
            visualization_type="STATE_MACHINE",
            description=(
                "Encrypts a numeric message M using RSA public key (n, e) via "
                "modular exponentiation C = M^e mod n, then decrypts with "
                "private key (n, d) to recover M' = C^d mod n."
            ),
            intuition=(
                "Fast modular exponentiation breaks the exponent into a chain of "
                "squarings. Encryption and decryption are symmetric operations — "
                "only the exponent differs — but without d it is infeasible to reverse C."
            ),
            complexity_time_best="O(log e · log² n)",
            complexity_time_average="O(log e · log² n)",
            complexity_time_worst="O(log e · log² n)",
            complexity_space="O(log n)",
            tags=("cryptography", "rsa", "public-key", "modular-exponentiation", "intermediate"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CryptoState:
        M = int(params.inputs.get("message", 65))
        M = max(2, min(M, _N - 1))
        return CryptoState(
            variables=(
                ("n", str(_N)),
                ("e", str(_E)),
                ("d", str(_D)),
                ("M", str(M)),
                ("C", "?"),
                ("M_prime", "?"),
            ),
            operation="",
            step_name="Initialise",
            highlighted=("M", "n", "e"),
            bits=format(M & 0xFF, "08b"),
            result=None,
            description=(
                f"RSA parameters: n={_N}, e={_E} (public), d={_D} (private).\n"
                f"Message M={M}. We require M < n={_N}. ✓\n"
                "Now encrypting with C = M^e mod n."
            ),
        )

    def steps(
        self, initial_state: AlgorithmState
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CryptoState)

        var_map = dict(initial_state.variables)
        M = int(var_map["M"])

        # Validate M < n
        yield CryptoState(
            variables=(
                ("n", str(_N)), ("e", str(_E)), ("d", str(_D)),
                ("M", str(M)), ("C", "?"), ("M_prime", "?"),
            ),
            operation=f"Verify M < n: {M} < {_N} ✓",
            step_name="Verify M < n",
            highlighted=("M", "n"),
            bits=format(M & 0xFF, "08b"),
            result=None,
            description=(
                f"RSA requires the message M={M} to be less than the modulus n={_N}. "
                f"{M} < {_N} ✓"
            ),
        )

        # Encryption via modular exponentiation
        enc_steps = _mod_exp_steps(M, _E, _N)
        result_enc = 1
        b_enc = M % _N
        exp_enc = _E

        for bit, res_before, sq, pos in enc_steps:
            exp_bits = format(_E, "b")
            bit_char = exp_bits[-(pos + 1)] if pos < len(exp_bits) else "0"
            old_result = result_enc
            old_b = b_enc
            if bit:
                result_enc = (result_enc * b_enc) % _N
            b_enc = (b_enc * b_enc) % _N

            yield CryptoState(
                variables=(
                    ("n", str(_N)), ("e", str(_E)), ("d", str(_D)),
                    ("M", str(M)), ("C", "?"),
                    ("exp_bit", str(bit)), ("bit_pos", str(pos)),
                    ("result", str(result_enc)), ("base_sq", str(old_b)),
                ),
                operation=(
                    f"bit[{pos}]={bit}: "
                    + (f"result = ({old_result} × {old_b}) mod {_N} = {result_enc}"
                       if bit else f"result = {result_enc} (bit=0, no multiply)")
                    + f"\nbase² = ({old_b})² mod {_N} = {b_enc}"
                ),
                step_name=f"Encrypt: exp bit {pos} (={bit})",
                highlighted=("result", "exp_bit") if bit else ("exp_bit",),
                bits=format(bit, "08b"),
                result=None,
                description=(
                    f"Fast mod-exp encryption, bit position {pos} (value={bit}). "
                    + (f"bit=1: multiply result × base = {result_enc} mod {_N}."
                       if bit else "bit=0: skip multiply.")
                    + f" Square base → {b_enc}."
                ),
            )

        C = pow(M, _E, _N)

        yield CryptoState(
            variables=(
                ("n", str(_N)), ("e", str(_E)), ("d", str(_D)),
                ("M", str(M)), ("C", str(C)), ("M_prime", "?"),
            ),
            operation=f"C = M^e mod n = {M}^{_E} mod {_N} = {C}",
            step_name="Encryption result",
            highlighted=("C",),
            bits=format(C & 0xFF, "08b"),
            result=None,
            description=(
                f"Encryption complete: C = {M}^{_E} mod {_N} = {C}. "
                "The ciphertext C is sent to the recipient."
            ),
        )

        # Decryption
        dec_steps = _mod_exp_steps(C, _D, _N)
        result_dec = 1
        b_dec = C % _N

        for bit, res_before, sq, pos in dec_steps:
            old_result = result_dec
            old_b = b_dec
            if bit:
                result_dec = (result_dec * b_dec) % _N
            b_dec = (b_dec * b_dec) % _N

            yield CryptoState(
                variables=(
                    ("n", str(_N)), ("e", str(_E)), ("d", str(_D)),
                    ("M", str(M)), ("C", str(C)),
                    ("dec_bit", str(bit)), ("bit_pos", str(pos)),
                    ("dec_result", str(result_dec)),
                ),
                operation=(
                    f"bit[{pos}]={bit}: "
                    + (f"result = ({old_result} × {old_b}) mod {_N} = {result_dec}"
                       if bit else f"result = {result_dec} (bit=0)")
                ),
                step_name=f"Decrypt: exp bit {pos} (={bit})",
                highlighted=("dec_result", "dec_bit") if bit else ("dec_bit",),
                bits=format(bit, "08b"),
                result=None,
                description=(
                    f"Fast mod-exp decryption bit {pos} (value={bit}). "
                    + (f"bit=1: multiply → dec_result={result_dec}."
                       if bit else "bit=0: skip multiply.")
                ),
            )

        M_prime = pow(C, _D, _N)

        return CryptoState(
            variables=(
                ("n", str(_N)), ("e", str(_E)), ("d", str(_D)),
                ("M", str(M)), ("C", str(C)), ("M_prime", str(M_prime)),
            ),
            operation=(
                f"M' = C^d mod n = {C}^{_D} mod {_N} = {M_prime}\n"
                f"M == M' ? {M == M_prime}"
            ),
            step_name="Decryption complete",
            highlighted=("M_prime", "M"),
            bits=format(M_prime & 0xFF, "08b"),
            result=str(M_prime),
            description=(
                f"Decryption complete: M' = {C}^{_D} mod {_N} = {M_prime}. "
                f"Original message M={M} — match: {M == M_prime} ✓"
            ),
        )
