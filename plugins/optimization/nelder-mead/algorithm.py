"""
Nelder-Mead Simplex — Algorithm Atlas Plugin

Minimizes f(x) = (x-2)² + 1 in 1D.
1D simplex = 2 points (not 3 — a triangle in 1D degenerates to a pair).
Uses the standard Nelder-Mead operations: reflect, expand, contract, shrink.
In 1D: simplex = [a, b] sorted so f(a) ≤ f(b).
  best = a, worst = b.
  centroid of all-except-worst = a.
  reflect: xr = a + (a - b) = 2a - b
  expand:  xe = a + 2(a - b) = 3a - 2b
  contract: xc = a + 0.5*(b - a) or outside
  shrink:  b = a + 0.5*(b - a)
landscape: f on [-1, 6]. history: best point per step.
"""
from __future__ import annotations

import json
import math
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CurveState,
    SimulationParams,
)

_DOMAIN_LO = -1.0
_DOMAIN_HI = 6.0
_N_LANDSCAPE = 100

_ALPHA = 1.0   # reflection
_GAMMA = 2.0   # expansion
_RHO = 0.5     # contraction
_SIGMA = 0.5   # shrink


def _f(x: float) -> float:
    return (x - 2.0) ** 2 + 1.0


def _landscape():
    xs = [_DOMAIN_LO + (_DOMAIN_HI - _DOMAIN_LO) * i / (_N_LANDSCAPE - 1)
          for i in range(_N_LANDSCAPE)]
    return tuple(xs), tuple(_f(x) for x in xs)


_LS_X, _LS_Y = _landscape()


class NelderMead:
    """Instrumented 1D Nelder-Mead simulation using CurveState."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="nelder-mead",
            name="Nelder-Mead Simplex",
            category="optimization",
            visualization_type="CURVE",
            description=(
                "Minimizes f(x)=(x-2)²+1 using a 2-point simplex in 1D. "
                "Applies reflection, expansion, contraction, and shrink operations "
                "to guide the simplex toward the minimum."
            ),
            intuition=(
                "An amoeba that reshapes itself to squeeze toward lower function values — "
                "it reflects bad points across the best, expands promising directions, "
                "and shrinks when stuck."
            ),
            complexity_time_best="O(steps)",
            complexity_time_average="O(steps)",
            complexity_time_worst="O(steps)",
            complexity_space="O(1)",
            tags=("optimization", "simplex", "derivative-free", "direct-search"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CurveState:
        steps = int(params.inputs.get("steps", 50))
        # Initial simplex: two points
        a, b = 0.5, 5.0
        best_x = a if _f(a) <= _f(b) else b
        best_y = _f(best_x)
        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=best_x,
            current_y=best_y,
            history_x=(best_x,),
            history_y=(best_y,),
            iteration=0,
            best_x=best_x,
            best_y=best_y,
            gradient=None,
            extra=json.dumps({
                "simplex": [round(a, 4), round(b, 4)],
                "steps": steps,
                "operation": "init",
            }),
            description=f"Init simplex: [{a}, {b}], best f={best_y:.4f}",
        )

    def steps(
        self,
        initial_state: AlgorithmState,
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CurveState)
        extra_data = json.loads(initial_state.extra)
        steps: int = extra_data["steps"]

        simplex: List[float] = extra_data["simplex"]
        best_x = initial_state.best_x
        best_y = initial_state.best_y
        history_x = list(initial_state.history_x)
        history_y = list(initial_state.history_y)

        for i in range(1, steps + 1):
            # Sort: a = best, b = worst
            simplex.sort(key=_f)
            a, b = simplex[0], simplex[1]
            fa, fb = _f(a), _f(b)

            # Centroid of all-except-worst = just 'a' in 1D
            centroid = a

            # Reflect
            xr = centroid + _ALPHA * (centroid - b)
            fr = _f(xr)

            operation = "?"
            if fr < fa:
                # Try expansion
                xe = centroid + _GAMMA * (xr - centroid)
                fe = _f(xe)
                if fe < fr:
                    simplex[1] = xe
                    operation = "expand"
                else:
                    simplex[1] = xr
                    operation = "reflect"
            elif fr < fb:
                simplex[1] = xr
                operation = "reflect"
            else:
                # Contract
                xc = centroid + _RHO * (b - centroid)
                fc = _f(xc)
                if fc < fb:
                    simplex[1] = xc
                    operation = "contract"
                else:
                    # Shrink
                    simplex[1] = a + _SIGMA * (b - a)
                    operation = "shrink"

            # Update best
            current_best = min(simplex, key=_f)
            current_best_y = _f(current_best)
            if current_best_y < best_y:
                best_x, best_y = current_best, current_best_y

            history_x.append(best_x)
            history_y.append(best_y)

            yield CurveState(
                landscape_x=_LS_X,
                landscape_y=_LS_Y,
                current_x=current_best,
                current_y=current_best_y,
                history_x=tuple(history_x),
                history_y=tuple(history_y),
                iteration=i,
                best_x=best_x,
                best_y=best_y,
                gradient=None,
                extra=json.dumps({
                    "simplex": [round(x, 6) for x in simplex],
                    "steps": steps,
                    "operation": operation,
                }),
                description=(
                    f"Step {i} ({operation}): simplex={[round(x,4) for x in simplex]}, "
                    f"best f={best_y:.6f}"
                ),
            )

        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=best_x,
            current_y=best_y,
            history_x=tuple(history_x),
            history_y=tuple(history_y),
            iteration=steps,
            best_x=best_x,
            best_y=best_y,
            gradient=None,
            extra=json.dumps({"simplex": [round(x, 6) for x in simplex], "steps": steps, "operation": "done"}),
            description=f"Done — best x={best_x:.6f}, f(x)={best_y:.8f}",
        )
