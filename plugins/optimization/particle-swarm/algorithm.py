"""
Particle Swarm Optimization — Algorithm Atlas Plugin

Minimizes f(x,y) = (x-1)² + (y-2)².
1D projection for CurveState: g(t) = f(t, t/2) = (t-1)² + (t/2-2)²
on t ∈ [-2, 4]. Global minimum of g at t=2 (f(2,1)=1, g(2)=0).
Actually g(t) = (t-1)² + (t/2-2)² = t²-2t+1 + t²/4 - 2t + 4
              = 5t²/4 - 4t + 5. Min at t = 4/(2*5/4) = 8/5 = 1.6.
6 particles with random positions and velocities seeded by params.seed.
extra JSON: {"particles": [t0..t5], "velocities": [...], "iter": n}
"""
from __future__ import annotations

import json
import math
import random
from typing import Generator, List

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CurveState,
    SimulationParams,
)

_DOMAIN_LO = -2.0
_DOMAIN_HI = 4.0
_N_LANDSCAPE = 100
_N_PARTICLES = 6

# PSO hyperparameters
_W = 0.7   # inertia
_C1 = 1.5  # cognitive (personal best)
_C2 = 1.5  # social (global best)


def _g(t: float) -> float:
    """1D projection of (x-1)²+(y-2)² along y=t/2."""
    return (t - 1.0) ** 2 + (t / 2.0 - 2.0) ** 2


def _landscape():
    xs = [_DOMAIN_LO + (_DOMAIN_HI - _DOMAIN_LO) * i / (_N_LANDSCAPE - 1)
          for i in range(_N_LANDSCAPE)]
    return tuple(xs), tuple(_g(x) for x in xs)


_LS_X, _LS_Y = _landscape()


def _clamp(t: float) -> float:
    return max(_DOMAIN_LO, min(_DOMAIN_HI, t))


class ParticleSwarm:
    """Instrumented PSO simulation projected to 1D using CurveState."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="particle-swarm",
            name="Particle Swarm Optimization",
            category="optimization",
            visualization_type="CURVE",
            description=(
                "Minimizes f(x,y)=(x-1)²+(y-2)² projected to 1D via g(t)=f(t,t/2). "
                "6 particles share information about the best position found globally."
            ),
            intuition=(
                "A flock of birds searching for food — each bird remembers its personal "
                "best spot but is also drawn toward the best location found by any bird."
            ),
            complexity_time_best="O(iterations × particles)",
            complexity_time_average="O(iterations × particles)",
            complexity_time_worst="O(iterations × particles)",
            complexity_space="O(particles)",
            tags=("optimization", "metaheuristic", "swarm", "population-based"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CurveState:
        rng = random.Random(params.seed)
        iterations = int(params.inputs.get("iterations", 60))

        positions = [rng.uniform(_DOMAIN_LO, _DOMAIN_HI) for _ in range(_N_PARTICLES)]
        velocities = [rng.uniform(-0.5, 0.5) for _ in range(_N_PARTICLES)]
        personal_bests = list(positions)

        gbest_t = min(positions, key=_g)
        gbest_y = _g(gbest_t)

        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=gbest_t,
            current_y=gbest_y,
            history_x=(gbest_t,),
            history_y=(gbest_y,),
            iteration=0,
            best_x=gbest_t,
            best_y=gbest_y,
            gradient=None,
            extra=json.dumps({
                "particles": [round(p, 4) for p in positions],
                "velocities": [round(v, 4) for v in velocities],
                "personal_bests": [round(p, 4) for p in personal_bests],
                "iterations": iterations,
                "iter": 0,
            }),
            description=f"Init: {_N_PARTICLES} particles, gbest t={gbest_t:.4f}, g={gbest_y:.4f}",
        )

    def steps(
        self,
        initial_state: AlgorithmState,
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CurveState)
        extra_data = json.loads(initial_state.extra)
        iterations: int = extra_data["iterations"]

        positions: List[float] = extra_data["particles"]
        velocities: List[float] = extra_data["velocities"]
        personal_bests: List[float] = extra_data["personal_bests"]

        rng = random.Random(7)  # fixed sub-seed for velocity update randomness

        gbest_t = min(personal_bests, key=_g)
        gbest_y = _g(gbest_t)
        best_x = gbest_t
        best_y = gbest_y
        history_x = list(initial_state.history_x)
        history_y = list(initial_state.history_y)

        for it in range(1, iterations + 1):
            for i in range(_N_PARTICLES):
                r1 = rng.random()
                r2 = rng.random()
                velocities[i] = (
                    _W * velocities[i]
                    + _C1 * r1 * (personal_bests[i] - positions[i])
                    + _C2 * r2 * (gbest_t - positions[i])
                )
                positions[i] = _clamp(positions[i] + velocities[i])
                if _g(positions[i]) < _g(personal_bests[i]):
                    personal_bests[i] = positions[i]

            gbest_t = min(personal_bests, key=_g)
            gbest_y = _g(gbest_t)

            if gbest_y < best_y:
                best_x, best_y = gbest_t, gbest_y

            history_x.append(best_x)
            history_y.append(best_y)

            yield CurveState(
                landscape_x=_LS_X,
                landscape_y=_LS_Y,
                current_x=gbest_t,
                current_y=gbest_y,
                history_x=tuple(history_x),
                history_y=tuple(history_y),
                iteration=it,
                best_x=best_x,
                best_y=best_y,
                gradient=None,
                extra=json.dumps({
                    "particles": [round(p, 4) for p in positions],
                    "velocities": [round(v, 4) for v in velocities],
                    "personal_bests": [round(p, 4) for p in personal_bests],
                    "iterations": iterations,
                    "iter": it,
                }),
                description=(
                    f"Iter {it}: gbest t={gbest_t:.4f}, g(t)={gbest_y:.4f}"
                ),
            )

        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=best_x,
            current_y=best_y,
            history_x=tuple(history_x),
            history_y=tuple(history_y),
            iteration=iterations,
            best_x=best_x,
            best_y=best_y,
            gradient=None,
            extra=json.dumps({
                "particles": [round(p, 4) for p in positions],
                "velocities": [round(v, 4) for v in velocities],
                "personal_bests": [round(p, 4) for p in personal_bests],
                "iterations": iterations,
                "iter": iterations,
            }),
            description=f"Done — gbest t={best_x:.4f}, g(t)={best_y:.4f}",
        )
