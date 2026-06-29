"""
Coordinate Descent — Algorithm Atlas Plugin

Minimizes f(x,y) = x² + 2y² + xy.
Alternates between:
  - Fix y, minimize over x: optimal x* = -y/2
  - Fix x, minimize over y: optimal y* = -x/4

CurveState projection: x_axis = iteration index, y_axis = f(x, y).
landscape: shows f range from max down to minimum (0 at origin).
Starts at (x0, y0) = (3.0, 3.0).
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

_N_LANDSCAPE = 100


def _f(x: float, y: float) -> float:
    return x * x + 2.0 * y * y + x * y


def _f_at_iter(iteration: int) -> float:
    """Helper used only for the landscape — not relevant."""
    return 0.0


def _landscape(steps: int):
    """Landscape shows iteration index vs a smooth decay curve as reference."""
    # Show a reference decay from high f value to 0 over steps
    x0, y0 = 3.0, 3.0
    f0 = _f(x0, y0)
    xs = tuple(float(i) for i in range(_N_LANDSCAPE))
    # Exponential reference decay as background
    ys = tuple(f0 * math.exp(-4.0 * i / (_N_LANDSCAPE - 1)) for i in range(_N_LANDSCAPE))
    return xs, ys


class CoordinateDescent:
    """Instrumented coordinate descent simulation using CurveState."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="coordinate-descent",
            name="Coordinate Descent",
            category="optimization",
            visualization_type="CURVE",
            description=(
                "Minimizes f(x,y)=x²+2y²+xy by alternating exact line searches: "
                "fix y and minimize over x, then fix x and minimize over y."
            ),
            intuition=(
                "Like tuning two knobs alternately — each turn gets one variable to its "
                "optimal value given the other, spiraling toward the global minimum."
            ),
            complexity_time_best="O(steps)",
            complexity_time_average="O(steps)",
            complexity_time_worst="O(steps)",
            complexity_space="O(1)",
            tags=("optimization", "coordinate-descent", "convex", "analytic"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CurveState:
        steps = int(params.inputs.get("steps", 40))
        x0, y0 = 3.0, 3.0
        f0 = _f(x0, y0)
        ls_x, ls_y = _landscape(steps)
        return CurveState(
            landscape_x=ls_x,
            landscape_y=ls_y,
            current_x=0.0,
            current_y=f0,
            history_x=(0.0,),
            history_y=(f0,),
            iteration=0,
            best_x=0.0,
            best_y=f0,
            gradient=None,
            extra=json.dumps({
                "x": x0,
                "y": y0,
                "steps": steps,
                "phase": "init",
            }),
            description=f"Start: x={x0}, y={y0}, f={f0:.4f}",
        )

    def steps(
        self,
        initial_state: AlgorithmState,
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CurveState)
        extra_data = json.loads(initial_state.extra)
        steps: int = extra_data["steps"]
        x: float = extra_data["x"]
        y: float = extra_data["y"]

        ls_x = initial_state.landscape_x
        ls_y = initial_state.landscape_y

        best_y = _f(x, y)
        best_iter = 0.0
        history_x = list(initial_state.history_x)
        history_y = list(initial_state.history_y)

        for i in range(1, steps + 1):
            if i % 2 == 1:
                # Fix y, minimize over x: ∂f/∂x = 2x + y = 0 → x = -y/2
                x = -y / 2.0
                phase = "minimize over x (fix y)"
            else:
                # Fix x, minimize over y: ∂f/∂y = 4y + x = 0 → y = -x/4
                y = -x / 4.0
                phase = "minimize over y (fix x)"

            fval = _f(x, y)

            if fval < best_y:
                best_y = fval
                best_iter = float(i)

            history_x.append(float(i))
            history_y.append(fval)

            yield CurveState(
                landscape_x=ls_x,
                landscape_y=ls_y,
                current_x=float(i),
                current_y=fval,
                history_x=tuple(history_x),
                history_y=tuple(history_y),
                iteration=i,
                best_x=best_iter,
                best_y=best_y,
                gradient=None,
                extra=json.dumps({
                    "x": round(x, 6),
                    "y": round(y, 6),
                    "steps": steps,
                    "phase": phase,
                }),
                description=(
                    f"Step {i} ({phase}): x={x:.4f}, y={y:.4f}, f={fval:.6f}"
                ),
            )

        final_f = _f(x, y)
        return CurveState(
            landscape_x=ls_x,
            landscape_y=ls_y,
            current_x=float(steps),
            current_y=final_f,
            history_x=tuple(history_x),
            history_y=tuple(history_y),
            iteration=steps,
            best_x=best_iter,
            best_y=best_y,
            gradient=None,
            extra=json.dumps({"x": round(x, 6), "y": round(y, 6), "steps": steps, "phase": "done"}),
            description=f"Done — x={x:.6f}, y={y:.6f}, f={final_f:.8f}",
        )
