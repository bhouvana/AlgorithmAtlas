"""
Gradient Descent 1D — Algorithm Atlas Plugin

Minimizes f(x) = x² - 4x + 5 on [-1, 6] using first-order gradient descent.
Gradient: f'(x) = 2x - 4. Optimum at x=2, f(2)=1.
Start: x=5. Update rule: x ← x - lr * grad.
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

_DOMAIN_LO = -1.0
_DOMAIN_HI = 6.0
_N_LANDSCAPE = 100


def _f(x: float) -> float:
    return x * x - 4.0 * x + 5.0


def _grad(x: float) -> float:
    return 2.0 * x - 4.0


def _landscape():
    xs = [_DOMAIN_LO + (_DOMAIN_HI - _DOMAIN_LO) * i / (_N_LANDSCAPE - 1)
          for i in range(_N_LANDSCAPE)]
    return tuple(xs), tuple(_f(x) for x in xs)


_LS_X, _LS_Y = _landscape()


class GradientDescent1d:
    """Instrumented 1-D gradient descent simulation using CurveState."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="gradient-descent-1d",
            name="Gradient Descent (1D)",
            category="optimization",
            visualization_type="CURVE",
            description=(
                "Iteratively minimizes f(x)=x²-4x+5 by stepping in the direction "
                "opposite to the gradient. Converges to the global minimum at x=2."
            ),
            intuition=(
                "Imagine rolling a ball down a hill — it always moves in the steepest "
                "downhill direction and eventually settles at the lowest valley."
            ),
            complexity_time_best="O(steps)",
            complexity_time_average="O(steps)",
            complexity_time_worst="O(steps)",
            complexity_space="O(1)",
            tags=("optimization", "gradient", "calculus", "convex", "1d"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CurveState:
        lr = float(params.inputs.get("lr", 0.3))
        steps = int(params.inputs.get("steps", 50))
        x0 = 5.0
        y0 = _f(x0)
        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=x0,
            current_y=y0,
            history_x=(x0,),
            history_y=(y0,),
            iteration=0,
            best_x=x0,
            best_y=y0,
            gradient=_grad(x0),
            extra=json.dumps({"lr": lr, "steps": steps}),
            description=f"Start: x={x0:.4f}, f(x)={y0:.4f}",
        )

    def steps(
        self,
        initial_state: AlgorithmState,
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CurveState)
        extra = json.loads(initial_state.extra)
        lr: float = extra["lr"]
        steps: int = extra["steps"]

        x = initial_state.current_x
        best_x = x
        best_y = _f(x)
        history_x = list(initial_state.history_x)
        history_y = list(initial_state.history_y)

        for i in range(1, steps + 1):
            g = _grad(x)
            x_new = x - lr * g
            # Clamp to domain
            x_new = max(_DOMAIN_LO, min(_DOMAIN_HI, x_new))
            y_new = _f(x_new)

            if y_new < best_y:
                best_x, best_y = x_new, y_new

            history_x.append(x_new)
            history_y.append(y_new)
            x = x_new

            yield CurveState(
                landscape_x=_LS_X,
                landscape_y=_LS_Y,
                current_x=x,
                current_y=y_new,
                history_x=tuple(history_x),
                history_y=tuple(history_y),
                iteration=i,
                best_x=best_x,
                best_y=best_y,
                gradient=g,
                extra=json.dumps({"lr": lr, "steps": steps, "grad": round(g, 6)}),
                description=(
                    f"Step {i}: grad={g:.4f}, x={x:.4f}→{x_new:.4f}, "
                    f"f(x)={y_new:.4f}"
                ),
            )

        final_y = _f(x)
        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=x,
            current_y=final_y,
            history_x=tuple(history_x),
            history_y=tuple(history_y),
            iteration=steps,
            best_x=best_x,
            best_y=best_y,
            gradient=_grad(x),
            extra=json.dumps({"lr": lr, "steps": steps}),
            description=f"Done — best x={best_x:.4f}, f(x)={best_y:.4f}",
        )
