"""
RSA Key Generation — Algorithm Atlas Plugin

Pedagogical walkthrough of RSA key generation:
  1. Choose primes p and q
  2. Compute n = p * q
  3. Compute phi = (p-1)(q-1)
  4. Choose public exponent e = 17
  5. Compute private exponent d = mod_inverse(e, phi) via Extended Euclidean
  6. Output public key (n, e) and private key (n, d)

~15 frames total, showing extended Euclidean algorithm steps.
"""
from __future__ import annotations

from math import gcd
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CryptoState,
    SimulationParams,
)


def _extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Return (gcd, x, y) such that a*x + b*y = gcd(a, b)."""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = _extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y


def _mod_inverse(e: int, phi: int) -> int:
    """Return d such that e*d ≡ 1 (mod phi)."""
    _, x, _ = _extended_gcd(e % phi, phi)
    return x % phi


def _ext_gcd_steps(a: int, b: int) -> List[Tuple[int, int, int, int]]:
    """
    Return list of (a, b, quotient, remainder) rows for the extended Euclidean
    algorithm, suitable for displaying step-by-step.
    """
    rows: List[Tuple[int, int, int, int]] = []
    while b != 0:
        q, r = divmod(a, b)
        rows.append((a, b, q, r))
        a, b = b, r
    return rows


class RsaKeyGen:
    """RSA Key Generation simulation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="rsa-key-gen",
            name="RSA Key Generation",
            category="cryptography",
            visualization_type="STATE_MACHINE",
            description=(
                "Step-by-step RSA public/private key generation: choose primes p and q, "
                "compute modulus n and Euler totient phi(n), select public exponent e, "
                "and derive private exponent d via the Extended Euclidean Algorithm."
            ),
            intuition=(
                "RSA security rests on the difficulty of factoring n = p·q. "
                "Knowing p and q lets you compute phi(n) and invert e mod phi(n) "
                "to get d — but without the primes that inversion is infeasible."
            ),
            complexity_time_best="O(log² n)",
            complexity_time_average="O(log² n)",
            complexity_time_worst="O(log² n)",
            complexity_space="O(log n)",
            tags=("cryptography", "rsa", "public-key", "number-theory", "intermediate"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CryptoState:
        p = int(params.inputs.get("p", 61))
        q = int(params.inputs.get("q", 53))
        return CryptoState(
            variables=(
                ("p", str(p)),
                ("q", str(q)),
                ("n", "?"),
                ("phi", "?"),
                ("e", "?"),
                ("d", "?"),
            ),
            operation="",
            step_name="Choose primes",
            highlighted=("p", "q"),
            bits=format(p & 0xFF, "08b"),
            result=None,
            description=(
                f"RSA key generation begins. We have chosen two primes: "
                f"p = {p} and q = {q}."
            ),
        )

    def steps(
        self, initial_state: AlgorithmState
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CryptoState)

        var_map = dict(initial_state.variables)
        p = int(var_map["p"])
        q = int(var_map["q"])

        # Frame 1: Compute n
        n = p * q
        yield CryptoState(
            variables=(("p", str(p)), ("q", str(q)), ("n", str(n)),
                       ("phi", "?"), ("e", "?"), ("d", "?")),
            operation=f"n = p × q = {p} × {q} = {n}",
            step_name="Compute modulus n",
            highlighted=("n",),
            bits=format(n & 0xFF, "08b"),
            result=None,
            description=(
                f"n = p × q = {p} × {q} = {n}. "
                "This is the RSA modulus — used in both the public and private key."
            ),
        )

        # Frame 2: Compute phi
        phi = (p - 1) * (q - 1)
        yield CryptoState(
            variables=(("p", str(p)), ("q", str(q)), ("n", str(n)),
                       ("phi", str(phi)), ("e", "?"), ("d", "?")),
            operation=f"phi(n) = (p-1)(q-1) = ({p}-1)({q}-1) = {p-1}×{q-1} = {phi}",
            step_name="Compute Euler totient phi(n)",
            highlighted=("phi",),
            bits=format(phi & 0xFF, "08b"),
            result=None,
            description=(
                f"phi(n) = (p-1)(q-1) = {p - 1} × {q - 1} = {phi}. "
                "phi(n) counts the integers up to n that are coprime with n."
            ),
        )

        # Frame 3: Choose e
        e = 17
        assert gcd(e, phi) == 1, f"e={e} is not coprime with phi={phi}"
        yield CryptoState(
            variables=(("p", str(p)), ("q", str(q)), ("n", str(n)),
                       ("phi", str(phi)), ("e", str(e)), ("d", "?")),
            operation=f"Choose e = {e},  gcd({e}, {phi}) = {gcd(e, phi)} ✓",
            step_name="Choose public exponent e",
            highlighted=("e",),
            bits=format(e, "08b"),
            result=None,
            description=(
                f"We choose public exponent e = {e}. "
                f"Requirement: 1 < e < phi(n) and gcd(e, phi) = 1. "
                f"gcd({e}, {phi}) = {gcd(e, phi)} — valid."
            ),
        )

        # Extended Euclidean frames
        rows = _ext_gcd_steps(e % phi, phi)
        for idx, (a, b, q_val, r) in enumerate(rows):
            yield CryptoState(
                variables=(("p", str(p)), ("q", str(q)), ("n", str(n)),
                           ("phi", str(phi)), ("e", str(e)), ("d", "?"),
                           ("ext_a", str(a)), ("ext_b", str(b)),
                           ("ext_q", str(q_val)), ("ext_r", str(r))),
                operation=f"{a} = {q_val} × {b} + {r}",
                step_name=f"Extended Euclidean step {idx + 1}",
                highlighted=("ext_a", "ext_b", "ext_r"),
                bits=format(r & 0xFF, "08b"),
                result=None,
                description=(
                    f"Extended GCD step {idx + 1}: "
                    f"{a} = {q_val} × {b} + {r}. "
                    "Back-substituting these rows gives us the Bezout coefficients."
                ),
            )

        # Frame: d computed
        d = _mod_inverse(e, phi)
        yield CryptoState(
            variables=(("p", str(p)), ("q", str(q)), ("n", str(n)),
                       ("phi", str(phi)), ("e", str(e)), ("d", str(d))),
            operation=(
                f"d = e⁻¹ mod phi = {e}⁻¹ mod {phi} = {d}\n"
                f"Verify: ({e} × {d}) mod {phi} = {(e * d) % phi}"
            ),
            step_name="Compute private exponent d",
            highlighted=("d",),
            bits=format(d & 0xFF, "08b"),
            result=None,
            description=(
                f"Private exponent d = {d}. "
                f"Verification: {e} × {d} mod {phi} = {(e * d) % phi} ✓"
            ),
        )

        # Frame: Public key
        yield CryptoState(
            variables=(("public_key_n", str(n)), ("public_key_e", str(e)),
                       ("private_key_n", str(n)), ("private_key_d", str(d))),
            operation=f"Public key = (n={n}, e={e})  |  Private key = (n={n}, d={d})",
            step_name="Key pair complete",
            highlighted=("public_key_n", "public_key_e"),
            bits=None,
            result=f"Public({n},{e}) / Private({n},{d})",
            description=(
                f"RSA key generation complete!\n"
                f"Public key  : (n={n}, e={e})\n"
                f"Private key : (n={n}, d={d})\n"
                f"Share the public key freely; keep d secret."
            ),
        )

        return CryptoState(
            variables=(("public_key_n", str(n)), ("public_key_e", str(e)),
                       ("private_key_n", str(n)), ("private_key_d", str(d))),
            operation=f"Public key = ({n}, {e})  |  Private key = ({n}, {d})",
            step_name="Done",
            highlighted=("public_key_n", "public_key_e", "private_key_d"),
            bits=None,
            result=f"Public({n},{e}) / Private({n},{d})",
            description=(
                f"RSA key pair generated from primes p={p}, q={q}. "
                f"Public key: (n={n}, e={e}). Private key: (n={n}, d={d})."
            ),
        )
