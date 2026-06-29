"""
Hill Climbing — Algorithm Atlas Plugin

Maximizes f(x) = sin(x)*cos(x/2) + 0.5 on [0, 2π].
At each step, tries x ± step_size and moves to whichever is better.
Uses the simulation seed to pick the starting x.
"""
from __future__ import annotations

import json
import math
import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CurveState,
    SimulationParams,
)

_DOMAIN_LO = 0.0
_DOMAIN_HI = 2.0 * math.pi
_N_LANDSCAPE = 100


def _f(x: float) -> float:
    return math.sin(x) * math.cos(x / 2.0) + 0.5


def _landscape():
    xs = [_DOMAIN_LO + (_DOMAIN_HI - _DOMAIN_LO) * i / (_N_LANDSCAPE - 1)
          for i in range(_N_LANDSCAPE)]
    return tuple(xs), tuple(_f(x) for x in xs)


_LS_X, _LS_Y = _landscape()


class HillClimbing:
    """Instrumented stochastic hill climbing simulation using CurveState."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="hill-climbing",
            name="Hill Climbing",
            category="optimization",
            visualization_type="CURVE",
            description=(
                "Maximizes f(x)=sin(x)·cos(x/2)+0.5 on [0, 2π] by greedily "
                "accepting neighbors that improve the objective."
            ),
            intuition=(
                "Like a hiker in fog who always steps toward higher ground — "
                "eventually reaching a peak, though not necessarily the highest one."
            ),
            complexity_time_best="O(steps)",
            complexity_time_average="O(steps)",
            complexity_time_worst="O(steps)",
            complexity_space="O(1)",
            tags=("optimization", "local-search", "greedy", "metaheuristic"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CurveState:
        rng = random.Random(params.seed)
        steps = int(params.inputs.get("steps", 100))
        step_size = float(params.inputs.get("step_size", 0.1))

        x0 = rng.uniform(_DOMAIN_LO, _DOMAIN_HI)
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
            gradient=None,
            extra=json.dumps({"steps": steps, "step_size": step_size, "moves": 0}),
            description=f"Start: x={x0:.4f}, f(x)={y0:.4f}",
        )

    def steps(
        self,
        initial_state: AlgorithmState,
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CurveState)
        extra = json.loads(initial_state.extra)
        steps: int = extra["steps"]
        step_size: float = extra["step_size"]

        x = initial_state.current_x
        best_x = x
        best_y = _f(x)
        history_x = list(initial_state.history_x)
        history_y = list(initial_state.history_y)
        moves = 0

        for i in range(1, steps + 1):
            current_y = _f(x)
            # Try left and right neighbors
            x_left = max(_DOMAIN_LO, x - step_size)
            x_right = min(_DOMAIN_HI, x + step_size)
            y_left = _f(x_left)
            y_right = _f(x_right)

            # Pick best neighbor
            if y_left >= y_right and y_left > current_y:
                x_new, y_new = x_left, y_left
                direction = "left"
                moved = True
            elif y_right > y_left and y_right > current_y:
                x_new, y_new = x_right, y_right
                direction = "right"
                moved = True
            else:
                x_new, y_new = x, current_y
                direction = "none"
                moved = False

            if moved:
                moves += 1

            if y_new > best_y:
                best_x, best_y = x_new, y_new

            x = x_new
            history_x.append(x)
            history_y.append(y_new)

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
                gradient=None,
                extra=json.dumps({
                    "steps": steps,
                    "step_size": step_size,
                    "moves": moves,
                    "direction": direction,
                }),
                description=(
                    f"Step {i}: moved {direction}, x={x:.4f}, f(x)={y_new:.4f}"
                    if moved else
                    f"Step {i}: local maximum at x={x:.4f}, f(x)={y_new:.4f}"
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
            gradient=None,
            extra=json.dumps({"steps": steps, "step_size": step_size, "moves": moves}),
            description=f"Done — best x={best_x:.4f}, f(x)={best_y:.4f}",
        )
