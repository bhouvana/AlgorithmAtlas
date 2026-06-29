"""
Golden Section Search — Algorithm Atlas Plugin

Minimizes f(x) = (x-3)² on [0, 6].
Uses the golden ratio to eliminate portions of the bracket each iteration.
history: midpoints of the bracket as (midpoint, f(midpoint)).
landscape: 100 points of f on [0, 6].
Shows bracket narrowing until tolerance is met.
"""
from __future__ import annotations

import json
import math
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CurveState,
    SimulationParams,
)

_DOMAIN_LO = 0.0
_DOMAIN_HI = 6.0
_N_LANDSCAPE = 100
_PHI = (math.sqrt(5.0) - 1.0) / 2.0  # ≈ 0.6180


def _f(x: float) -> float:
    return (x - 3.0) ** 2


def _landscape():
    xs = [_DOMAIN_LO + (_DOMAIN_HI - _DOMAIN_LO) * i / (_N_LANDSCAPE - 1)
          for i in range(_N_LANDSCAPE)]
    return tuple(xs), tuple(_f(x) for x in xs)


_LS_X, _LS_Y = _landscape()


class GoldenSection:
    """Instrumented golden section search simulation using CurveState."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="golden-section",
            name="Golden Section Search",
            category="optimization",
            visualization_type="CURVE",
            description=(
                "Minimizes f(x)=(x-3)² on [0,6] by repeatedly narrowing the bracket "
                "using the golden ratio, guaranteeing convergence with minimal evaluations."
            ),
            intuition=(
                "Like binary search for a minimum — each step eliminates a golden-ratio "
                "fraction of the remaining interval, converging quickly without derivatives."
            ),
            complexity_time_best="O(log(1/tolerance))",
            complexity_time_average="O(log(1/tolerance))",
            complexity_time_worst="O(log(1/tolerance))",
            complexity_space="O(1)",
            tags=("optimization", "golden-ratio", "bracket", "derivative-free", "unimodal"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CurveState:
        tolerance = float(params.inputs.get("tolerance", 0.01))
        a, b = _DOMAIN_LO, _DOMAIN_HI
        mid = (a + b) / 2.0
        y0 = _f(mid)
        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=mid,
            current_y=y0,
            history_x=(mid,),
            history_y=(y0,),
            iteration=0,
            best_x=mid,
            best_y=y0,
            gradient=None,
            extra=json.dumps({
                "a": a,
                "b": b,
                "c": a + (1.0 - _PHI) * (b - a),
                "d": a + _PHI * (b - a),
                "tolerance": tolerance,
            }),
            description=f"Init bracket: [{a:.4f}, {b:.4f}], width={b-a:.4f}",
        )

    def steps(
        self,
        initial_state: AlgorithmState,
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CurveState)
        extra_data = json.loads(initial_state.extra)
        tolerance: float = extra_data["tolerance"]

        a: float = extra_data["a"]
        b: float = extra_data["b"]
        c: float = extra_data["c"]
        d: float = extra_data["d"]

        fc = _f(c)
        fd = _f(d)

        best_x = initial_state.best_x
        best_y = initial_state.best_y
        history_x = list(initial_state.history_x)
        history_y = list(initial_state.history_y)
        iteration = 0

        while (b - a) > tolerance:
            iteration += 1
            fc = _f(c)
            fd = _f(d)

            if fc < fd:
                b = d
                action = "shrink right (fc < fd)"
            else:
                a = c
                action = "shrink left (fd ≤ fc)"

            c = a + (1.0 - _PHI) * (b - a)
            d = a + _PHI * (b - a)

            mid = (a + b) / 2.0
            mid_y = _f(mid)

            if mid_y < best_y:
                best_x, best_y = mid, mid_y

            history_x.append(mid)
            history_y.append(mid_y)

            yield CurveState(
                landscape_x=_LS_X,
                landscape_y=_LS_Y,
                current_x=mid,
                current_y=mid_y,
                history_x=tuple(history_x),
                history_y=tuple(history_y),
                iteration=iteration,
                best_x=best_x,
                best_y=best_y,
                gradient=None,
                extra=json.dumps({
                    "a": round(a, 6),
                    "b": round(b, 6),
                    "c": round(c, 6),
                    "d": round(d, 6),
                    "tolerance": tolerance,
                    "bracket_width": round(b - a, 6),
                    "action": action,
                }),
                description=(
                    f"Step {iteration} ({action}): bracket=[{a:.4f},{b:.4f}], "
                    f"width={b-a:.6f}, mid f={mid_y:.6f}"
                ),
            )

        final_mid = (a + b) / 2.0
        final_y = _f(final_mid)
        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=final_mid,
            current_y=final_y,
            history_x=tuple(history_x),
            history_y=tuple(history_y),
            iteration=iteration,
            best_x=best_x,
            best_y=best_y,
            gradient=None,
            extra=json.dumps({
                "a": round(a, 6),
                "b": round(b, 6),
                "c": round(c, 6),
                "d": round(d, 6),
                "tolerance": tolerance,
                "bracket_width": round(b - a, 8),
                "action": "converged",
            }),
            description=(
                f"Converged — bracket=[{a:.6f},{b:.6f}], "
                f"best x={best_x:.6f}, f(x)={best_y:.8f}"
            ),
        )
