"""
Elliptic Curve Point Addition — Algorithm Atlas Plugin

Demonstrates scalar multiplication on the curve y² ≡ x³ + ax + b (mod p)
with parameters a=-1 (≡ p-1 mod p), b=1, p=23.
Generator point G = (0, 1).

Computes kG for k = 1..10, showing each point addition step.
~10 frames.

Point at infinity is represented as None.
"""
from __future__ import annotations

from typing import Generator, Optional, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CryptoState,
    SimulationParams,
)

_P = 23       # prime modulus
_A = -1       # curve coefficient a (stored as p-1 mod p)
_B = 1        # curve coefficient b
_GX = 0       # generator x
_GY = 1       # generator y

Point = Optional[Tuple[int, int]]  # None = point at infinity


def _mod_inv(n: int, p: int) -> int:
    """Modular inverse via Fermat's little theorem (p is prime)."""
    return pow(n % p, p - 2, p)


def _point_add(P: Point, Q: Point, a: int, p: int) -> Tuple[Point, str]:
    """Add two points on y²=x³+ax+b mod p. Returns (result, operation_str)."""
    if P is None:
        return Q, f"O + Q = Q"
    if Q is None:
        return P, f"P + O = P"

    px, py = P
    qx, qy = Q

    if px == qx and py != qy % p:
        return None, f"({px},{py}) + ({qx},{qy}) = O (vertical tangent)"

    if px == qx and py == qy:
        # Point doubling
        if py == 0:
            return None, f"2·({px},{py}) = O (py=0)"
        lam_num = (3 * px * px + a) % p
        lam_den = (2 * py) % p
        lam = (lam_num * _mod_inv(lam_den, p)) % p
        op = f"λ = (3x²+a)/(2y) = ({3*px*px+a}) / ({2*py}) mod {p} = {lam}"
    else:
        # Point addition
        lam_num = (qy - py) % p
        lam_den = (qx - px) % p
        lam = (lam_num * _mod_inv(lam_den, p)) % p
        op = f"λ = (y2-y1)/(x2-x1) = ({(qy-py)%p}) / ({(qx-px)%p}) mod {p} = {lam}"

    rx = (lam * lam - px - qx) % p
    ry = (lam * (px - rx) - py) % p
    return (rx, ry), op + f"\n  R = ({rx}, {ry})"


class EllipticCurve:
    """Elliptic Curve scalar multiplication simulation."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="elliptic-curve",
            name="Elliptic Curve Point Addition",
            category="cryptography",
            visualization_type="STATE_MACHINE",
            description=(
                "Demonstrates elliptic curve scalar multiplication over a small prime field: "
                "computes kG for k=1..10 on the curve y² ≡ x³ - x + 1 (mod 23), "
                "showing each point addition step."
            ),
            intuition=(
                "Adding a point to itself on the curve repeatedly is easy to compute "
                "forward but impossible to reverse without knowing k — this 'trapdoor' "
                "property is the foundation of elliptic curve cryptography."
            ),
            complexity_time_best="O(log k)",
            complexity_time_average="O(log k)",
            complexity_time_worst="O(log k)",
            complexity_space="O(1)",
            tags=("cryptography", "elliptic-curve", "ecc", "public-key", "advanced"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CryptoState:
        return CryptoState(
            variables=(
                ("curve", f"y² ≡ x³ + ({_A})x + {_B} (mod {_P})"),
                ("p", str(_P)),
                ("a", str(_A)),
                ("b", str(_B)),
                ("G", f"({_GX}, {_GY})"),
                ("k", "1"),
                ("kG", f"({_GX}, {_GY})"),
            ),
            operation=f"Start: 1·G = G = ({_GX}, {_GY})",
            step_name="Generator point G = 1·G",
            highlighted=("G", "kG"),
            bits=format(_GX, "08b"),
            result=None,
            description=(
                f"Curve: y² ≡ x³ - x + 1 (mod {_P}). "
                f"Generator G = ({_GX}, {_GY}). "
                f"We will compute kG for k = 1..10 by repeated point addition."
            ),
        )

    def steps(
        self, initial_state: AlgorithmState
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CryptoState)

        a_mod = _A % _P  # store as positive residue for arithmetic
        G: Point = (_GX, _GY)
        current: Point = G  # 1·G

        for k in range(2, 11):
            prev = current
            current, op = _point_add(current, G, a_mod, _P)

            if current is None:
                rx_str, ry_str = "∞", "∞"
                bits_val = None
            else:
                rx_str, ry_str = str(current[0]), str(current[1])
                bits_val = format(current[0], "08b")

            prev_str = f"({prev[0]}, {prev[1]})" if prev is not None else "O"

            yield CryptoState(
                variables=(
                    ("curve", f"y² ≡ x³ - x + 1 (mod {_P})"),
                    ("p", str(_P)),
                    ("k", str(k)),
                    ("prev_k_minus_1", str(k - 1)),
                    ("Px", prev_str.split(",")[0].lstrip("(") if prev else "∞"),
                    ("Py", prev_str.split(",")[1].rstrip(")").strip() if prev else "∞"),
                    ("Gx", str(_GX)),
                    ("Gy", str(_GY)),
                    ("Rx", rx_str),
                    ("Ry", ry_str),
                    ("kG", f"({rx_str}, {ry_str})"),
                ),
                operation=f"{k}G = {k-1}G + G\n{op}",
                step_name=f"k={k}: compute {k}G",
                highlighted=("kG", "Rx", "Ry"),
                bits=bits_val,
                result=None,
                description=(
                    f"{k}G = {k-1}G + G = {prev_str} + ({_GX},{_GY}) = ({rx_str},{ry_str}). "
                    f"Using point addition formula on E: y²≡x³-x+1 (mod {_P})."
                ),
            )

        final = current
        final_str = (
            f"({final[0]}, {final[1]})" if final is not None else "O"
        )

        return CryptoState(
            variables=(
                ("curve", f"y² ≡ x³ - x + 1 (mod {_P})"),
                ("k", "10"),
                ("kG", final_str),
            ),
            operation=f"10G = {final_str}",
            step_name="Complete — 10G computed",
            highlighted=("kG",),
            bits=format(final[0], "08b") if final else None,
            result=final_str,
            description=(
                f"Scalar multiplication complete: 10G = {final_str} "
                f"on y² ≡ x³ - x + 1 (mod {_P})."
            ),
        )
