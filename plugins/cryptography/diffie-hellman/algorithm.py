"""
Diffie-Hellman Key Exchange — Algorithm Atlas Plugin

Demonstrates the classic DH protocol with small numbers for pedagogy:
  - Public params: prime p=23, generator g=5
  - Alice's secret: a=6
  - Bob's secret:   b=15
  - Steps: compute A=g^a mod p, B=g^b mod p, exchange, compute shared secret.

~10 frames.
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

_ALICE_SECRET = 6
_BOB_SECRET = 15


class DiffieHellman:
    """Diffie-Hellman Key Exchange simulation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="diffie-hellman",
            name="Diffie-Hellman Key Exchange",
            category="cryptography",
            visualization_type="STATE_MACHINE",
            description=(
                "Demonstrates the Diffie-Hellman key exchange: Alice and Bob agree on "
                "public parameters (p, g), each choose a secret exponent, exchange public "
                "values, and independently compute the same shared secret."
            ),
            intuition=(
                "Alice and Bob mix their private colors into a shared public color, "
                "send the mixture to each other, then mix in their private color again — "
                "the result is identical without either ever revealing their private color."
            ),
            complexity_time_best="O(log p)",
            complexity_time_average="O(log p)",
            complexity_time_worst="O(log p)",
            complexity_space="O(1)",
            tags=("cryptography", "key-exchange", "diffie-hellman", "number-theory", "intermediate"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CryptoState:
        p = int(params.inputs.get("p", 23))
        g = int(params.inputs.get("g", 5))
        return CryptoState(
            variables=(
                ("p", str(p)),
                ("g", str(g)),
                ("alice_secret_a", "?"),
                ("bob_secret_b", "?"),
                ("A", "?"),
                ("B", "?"),
                ("shared_secret", "?"),
            ),
            operation="",
            step_name="Agree on public parameters",
            highlighted=("p", "g"),
            bits=format(g, "08b"),
            result=None,
            description=(
                f"Public parameters agreed upon: prime p={p}, generator g={g}. "
                "These are shared openly — anyone can see them."
            ),
        )

    def steps(
        self, initial_state: AlgorithmState
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CryptoState)

        var_map = dict(initial_state.variables)
        p = int(var_map["p"])
        g = int(var_map["g"])
        a = _ALICE_SECRET
        b = _BOB_SECRET

        # Frame 1: Alice picks secret
        yield CryptoState(
            variables=(("p", str(p)), ("g", str(g)),
                       ("alice_secret_a", str(a)), ("bob_secret_b", "?"),
                       ("A", "?"), ("B", "?"), ("shared_secret", "?")),
            operation=f"Alice chooses secret a = {a}  (kept private)",
            step_name="Alice picks secret a",
            highlighted=("alice_secret_a",),
            bits=format(a, "08b"),
            result=None,
            description=(
                f"Alice privately picks a random secret exponent a={a}. "
                "She never reveals this value to anyone."
            ),
        )

        # Frame 2: Bob picks secret
        yield CryptoState(
            variables=(("p", str(p)), ("g", str(g)),
                       ("alice_secret_a", str(a)), ("bob_secret_b", str(b)),
                       ("A", "?"), ("B", "?"), ("shared_secret", "?")),
            operation=f"Bob chooses secret b = {b}  (kept private)",
            step_name="Bob picks secret b",
            highlighted=("bob_secret_b",),
            bits=format(b, "08b"),
            result=None,
            description=(
                f"Bob privately picks a random secret exponent b={b}. "
                "He never reveals this value to anyone."
            ),
        )

        # Frame 3: Alice computes A
        A = pow(g, a, p)
        yield CryptoState(
            variables=(("p", str(p)), ("g", str(g)),
                       ("alice_secret_a", str(a)), ("bob_secret_b", str(b)),
                       ("A", str(A)), ("B", "?"), ("shared_secret", "?")),
            operation=f"A = g^a mod p = {g}^{a} mod {p} = {A}",
            step_name="Alice computes public value A",
            highlighted=("A", "alice_secret_a"),
            bits=format(A, "08b"),
            result=None,
            description=(
                f"Alice computes her public value A = {g}^{a} mod {p} = {A}. "
                "A is sent publicly to Bob."
            ),
        )

        # Frame 4: Bob computes B
        B = pow(g, b, p)
        yield CryptoState(
            variables=(("p", str(p)), ("g", str(g)),
                       ("alice_secret_a", str(a)), ("bob_secret_b", str(b)),
                       ("A", str(A)), ("B", str(B)), ("shared_secret", "?")),
            operation=f"B = g^b mod p = {g}^{b} mod {p} = {B}",
            step_name="Bob computes public value B",
            highlighted=("B", "bob_secret_b"),
            bits=format(B, "08b"),
            result=None,
            description=(
                f"Bob computes his public value B = {g}^{b} mod {p} = {B}. "
                "B is sent publicly to Alice."
            ),
        )

        # Frame 5: Exchange
        yield CryptoState(
            variables=(("p", str(p)), ("g", str(g)),
                       ("alice_secret_a", str(a)), ("bob_secret_b", str(b)),
                       ("A", str(A)), ("B", str(B)), ("shared_secret", "?")),
            operation=f"Alice sends A={A} to Bob. Bob sends B={B} to Alice.",
            step_name="Exchange public values",
            highlighted=("A", "B"),
            bits=None,
            result=None,
            description=(
                f"Public exchange over insecure channel: Alice sends A={A}, Bob sends B={B}. "
                "An eavesdropper sees g, p, A, B — but not a or b."
            ),
        )

        # Frame 6: Alice computes shared secret
        s_alice = pow(B, a, p)
        yield CryptoState(
            variables=(("p", str(p)), ("g", str(g)),
                       ("alice_secret_a", str(a)), ("bob_secret_b", str(b)),
                       ("A", str(A)), ("B", str(B)),
                       ("alice_shared", str(s_alice)), ("bob_shared", "?")),
            operation=f"Alice: S = B^a mod p = {B}^{a} mod {p} = {s_alice}",
            step_name="Alice computes shared secret",
            highlighted=("alice_shared", "B", "alice_secret_a"),
            bits=format(s_alice, "08b"),
            result=None,
            description=(
                f"Alice computes S = B^a mod p = {B}^{a} mod {p} = {s_alice}. "
                f"Note: B^a = (g^b)^a = g^(ab) mod p."
            ),
        )

        # Frame 7: Bob computes shared secret
        s_bob = pow(A, b, p)
        yield CryptoState(
            variables=(("p", str(p)), ("g", str(g)),
                       ("alice_secret_a", str(a)), ("bob_secret_b", str(b)),
                       ("A", str(A)), ("B", str(B)),
                       ("alice_shared", str(s_alice)), ("bob_shared", str(s_bob))),
            operation=f"Bob: S = A^b mod p = {A}^{b} mod {p} = {s_bob}",
            step_name="Bob computes shared secret",
            highlighted=("bob_shared", "A", "bob_secret_b"),
            bits=format(s_bob, "08b"),
            result=None,
            description=(
                f"Bob computes S = A^b mod p = {A}^{b} mod {p} = {s_bob}. "
                f"Note: A^b = (g^a)^b = g^(ab) mod p."
            ),
        )

        # Frame 8: Match!
        shared = s_alice
        assert s_alice == s_bob

        yield CryptoState(
            variables=(("p", str(p)), ("g", str(g)),
                       ("alice_secret_a", str(a)), ("bob_secret_b", str(b)),
                       ("A", str(A)), ("B", str(B)),
                       ("shared_secret", str(shared))),
            operation=(
                f"Alice's S = {s_alice} == Bob's S = {s_bob} ✓\n"
                f"Shared secret = g^(ab) mod p = {g}^({a}×{b}) mod {p} = {shared}"
            ),
            step_name="Shared secret established",
            highlighted=("shared_secret",),
            bits=format(shared, "08b"),
            result=str(shared),
            description=(
                f"Both parties independently computed the same shared secret S={shared}. "
                "An eavesdropper who knows g, p, A, B would need to solve the Discrete "
                "Logarithm Problem to recover a or b — computationally infeasible for large p."
            ),
        )

        return CryptoState(
            variables=(("p", str(p)), ("g", str(g)),
                       ("alice_secret_a", str(a)), ("bob_secret_b", str(b)),
                       ("A", str(A)), ("B", str(B)),
                       ("shared_secret", str(shared))),
            operation=f"Key exchange complete. shared_secret = {shared}",
            step_name="Done",
            highlighted=("shared_secret",),
            bits=None,
            result=str(shared),
            description=(
                f"Diffie-Hellman complete. Shared secret = {shared}. "
                "Alice and Bob can now use this secret as a symmetric key."
            ),
        )
