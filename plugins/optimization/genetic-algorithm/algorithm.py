"""
Genetic Algorithm — Algorithm Atlas Plugin

Maximizes f(x) = -(x-3)² + 9 on [-1, 7].
Population of individuals (floats), each representing an x coordinate.
Selection: tournament (pick best of 2). Crossover: weighted blend.
Mutation: add Gaussian noise clamped to domain.
extra JSON: {"population": [...], "gen": n, "fitnesses": [...]}
"""
from __future__ import annotations

import json
import math
import random
from typing import Generator, List, Tuple

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    CurveState,
    SimulationParams,
)

_DOMAIN_LO = -1.0
_DOMAIN_HI = 7.0
_N_LANDSCAPE = 100


def _f(x: float) -> float:
    return -(x - 3.0) ** 2 + 9.0


def _landscape():
    xs = [_DOMAIN_LO + (_DOMAIN_HI - _DOMAIN_LO) * i / (_N_LANDSCAPE - 1)
          for i in range(_N_LANDSCAPE)]
    return tuple(xs), tuple(_f(x) for x in xs)


_LS_X, _LS_Y = _landscape()

_MUTATION_STD = 0.3


def _clamp(x: float) -> float:
    return max(_DOMAIN_LO, min(_DOMAIN_HI, x))


def _tournament(pop: List[float], rng: random.Random) -> float:
    a, b = rng.sample(pop, 2)
    return a if _f(a) >= _f(b) else b


def _crossover(p1: float, p2: float, rng: random.Random) -> float:
    alpha = rng.random()
    return _clamp(alpha * p1 + (1.0 - alpha) * p2)


def _mutate(x: float, rng: random.Random) -> float:
    return _clamp(x + rng.gauss(0.0, _MUTATION_STD))


class GeneticAlgorithm:
    """Instrumented Genetic Algorithm simulation using CurveState."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="genetic-algorithm",
            name="Genetic Algorithm",
            category="optimization",
            visualization_type="CURVE",
            description=(
                "Maximizes f(x)=-(x-3)²+9 on [-1,7] using a population of candidate "
                "solutions evolved through selection, crossover, and mutation."
            ),
            intuition=(
                "Evolution in miniature — only the fittest individuals survive to breed, "
                "and random mutations explore new regions of the solution space."
            ),
            complexity_time_best="O(generations × pop_size)",
            complexity_time_average="O(generations × pop_size)",
            complexity_time_worst="O(generations × pop_size)",
            complexity_space="O(pop_size)",
            tags=("optimization", "metaheuristic", "evolutionary", "population-based"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CurveState:
        rng = random.Random(params.seed)
        generations = int(params.inputs.get("generations", 50))
        pop_size = int(params.inputs.get("pop_size", 10))

        population = [rng.uniform(_DOMAIN_LO, _DOMAIN_HI) for _ in range(pop_size)]
        best_x = max(population, key=_f)
        best_y = _f(best_x)
        fitnesses = [round(_f(x), 4) for x in population]

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
                "population": [round(x, 4) for x in population],
                "gen": 0,
                "fitnesses": fitnesses,
                "generations": generations,
                "pop_size": pop_size,
            }),
            description=f"Gen 0: best x={best_x:.4f}, f(x)={best_y:.4f}",
        )

    def steps(
        self,
        initial_state: AlgorithmState,
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CurveState)
        extra_data = json.loads(initial_state.extra)
        generations: int = extra_data["generations"]
        pop_size: int = extra_data["pop_size"]

        # Re-derive deterministic state from the initial population
        population: List[float] = extra_data["population"]
        rng = random.Random(42)  # fixed sub-seed for reproducibility of GA steps

        best_x = initial_state.best_x
        best_y = initial_state.best_y
        history_x = list(initial_state.history_x)
        history_y = list(initial_state.history_y)

        for gen in range(1, generations + 1):
            # Selection + crossover + mutation → new population
            new_pop: List[float] = []
            for _ in range(pop_size):
                p1 = _tournament(population, rng)
                p2 = _tournament(population, rng)
                child = _crossover(p1, p2, rng)
                child = _mutate(child, rng)
                new_pop.append(child)

            # Elitism: keep the best from the old population
            old_best = max(population, key=_f)
            worst_idx = min(range(pop_size), key=lambda i: _f(new_pop[i]))
            new_pop[worst_idx] = old_best
            population = new_pop

            gen_best_x = max(population, key=_f)
            gen_best_y = _f(gen_best_x)
            fitnesses = [round(_f(x), 4) for x in population]

            if gen_best_y > best_y:
                best_x, best_y = gen_best_x, gen_best_y

            history_x.append(best_x)
            history_y.append(best_y)

            yield CurveState(
                landscape_x=_LS_X,
                landscape_y=_LS_Y,
                current_x=gen_best_x,
                current_y=gen_best_y,
                history_x=tuple(history_x),
                history_y=tuple(history_y),
                iteration=gen,
                best_x=best_x,
                best_y=best_y,
                gradient=None,
                extra=json.dumps({
                    "population": [round(x, 4) for x in population],
                    "gen": gen,
                    "fitnesses": fitnesses,
                    "generations": generations,
                    "pop_size": pop_size,
                }),
                description=(
                    f"Gen {gen}: best x={gen_best_x:.4f}, f(x)={gen_best_y:.4f} "
                    f"(overall best={best_y:.4f})"
                ),
            )

        final_y = _f(best_x)
        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=best_x,
            current_y=final_y,
            history_x=tuple(history_x),
            history_y=tuple(history_y),
            iteration=generations,
            best_x=best_x,
            best_y=best_y,
            gradient=None,
            extra=json.dumps({
                "population": [round(x, 4) for x in population],
                "gen": generations,
                "fitnesses": [round(_f(x), 4) for x in population],
                "generations": generations,
                "pop_size": pop_size,
            }),
            description=f"Done — best x={best_x:.4f}, f(x)={best_y:.4f}",
        )
