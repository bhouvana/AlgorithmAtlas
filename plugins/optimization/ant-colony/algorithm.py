"""
Ant Colony Optimization — Algorithm Atlas Plugin

Solves TSP on 5 cities arranged as a regular pentagon.
City coordinates: c_i = (cos(2πi/5), sin(2πi/5)).
x-axis = iteration, y-axis = best tour length found so far.
landscape_y range covers from worst possible to best possible tour length.
extra JSON: {"best_tour": [...], "pheromones": [[...], ...], "iter": n}
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

_N_CITIES = 5
_N_LANDSCAPE = 100

# Pentagon city coordinates
_CITIES: List[Tuple[float, float]] = [
    (math.cos(2 * math.pi * i / _N_CITIES),
     math.sin(2 * math.pi * i / _N_CITIES))
    for i in range(_N_CITIES)
]

# Precompute distances
_DIST: List[List[float]] = [
    [math.hypot(_CITIES[i][0] - _CITIES[j][0],
                _CITIES[i][1] - _CITIES[j][1])
     for j in range(_N_CITIES)]
    for i in range(_N_CITIES)
]

# ACO hyperparameters
_ALPHA = 1.0   # pheromone importance
_BETA = 2.0    # heuristic importance
_RHO = 0.1     # evaporation rate
_Q = 1.0       # pheromone deposit constant
_TAU_INIT = 0.5


def _tour_length(tour: List[int]) -> float:
    return sum(_DIST[tour[i]][tour[(i + 1) % _N_CITIES]] for i in range(_N_CITIES))


def _all_tour_lengths() -> List[float]:
    """Enumerate all (5-1)!/2 = 12 distinct tours to find bounds."""
    from itertools import permutations
    perms = list(permutations(range(1, _N_CITIES)))
    lengths = []
    for p in perms:
        tour = [0] + list(p)
        lengths.append(_tour_length(tour))
    return lengths


_ALL_LENGTHS = _all_tour_lengths()
_MIN_TOUR = min(_ALL_LENGTHS)
_MAX_TOUR = max(_ALL_LENGTHS)


def _landscape():
    xs = list(range(_N_LANDSCAPE))
    # y shows best possible range
    span = _MAX_TOUR - _MIN_TOUR
    ys = [_MAX_TOUR - span * i / (_N_LANDSCAPE - 1) for i in range(_N_LANDSCAPE)]
    return tuple(float(x) for x in xs), tuple(ys)


_LS_X, _LS_Y = _landscape()


def _construct_tour(
    pheromones: List[List[float]],
    rng: random.Random,
) -> List[int]:
    start = 0
    tour = [start]
    unvisited = list(range(1, _N_CITIES))
    current = start
    while unvisited:
        probs = []
        for j in unvisited:
            tau = pheromones[current][j] ** _ALPHA
            eta = (1.0 / _DIST[current][j]) ** _BETA if _DIST[current][j] > 0 else 1e9
            probs.append(tau * eta)
        total = sum(probs)
        r = rng.random() * total
        cumulative = 0.0
        chosen = unvisited[-1]
        for k, p in enumerate(probs):
            cumulative += p
            if cumulative >= r:
                chosen = unvisited[k]
                break
        tour.append(chosen)
        unvisited.remove(chosen)
        current = chosen
    return tour


class AntColony:
    """Instrumented ACO TSP simulation using CurveState."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="ant-colony",
            name="Ant Colony Optimization",
            category="optimization",
            visualization_type="CURVE",
            description=(
                "Solves TSP on 5 pentagon cities. Ants deposit pheromone on short tours; "
                "pheromone evaporates each iteration, guiding ants toward shorter paths."
            ),
            intuition=(
                "Real ants find the shortest path to food by reinforcing shorter trails "
                "with stronger pheromone — the colony converges on the optimal route."
            ),
            complexity_time_best="O(iterations × ants × cities²)",
            complexity_time_average="O(iterations × ants × cities²)",
            complexity_time_worst="O(iterations × ants × cities²)",
            complexity_space="O(cities²)",
            tags=("optimization", "metaheuristic", "swarm", "tsp", "combinatorial"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> CurveState:
        iterations = int(params.inputs.get("iterations", 80))
        ants = int(params.inputs.get("ants", 10))

        # Init pheromones
        pheromones = [[_TAU_INIT] * _N_CITIES for _ in range(_N_CITIES)]
        # Nearest-neighbour heuristic for initial best
        best_tour = list(range(_N_CITIES))
        best_length = _tour_length(best_tour)

        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=0.0,
            current_y=best_length,
            history_x=(0.0,),
            history_y=(best_length,),
            iteration=0,
            best_x=0.0,
            best_y=best_length,
            gradient=None,
            extra=json.dumps({
                "best_tour": best_tour,
                "pheromones": [[round(v, 4) for v in row] for row in pheromones],
                "iter": 0,
                "iterations": iterations,
                "ants": ants,
            }),
            description=f"Init: best tour length={best_length:.4f}",
        )

    def steps(
        self,
        initial_state: AlgorithmState,
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        assert isinstance(initial_state, CurveState)
        extra_data = json.loads(initial_state.extra)
        iterations: int = extra_data["iterations"]
        ants: int = extra_data["ants"]

        pheromones: List[List[float]] = extra_data["pheromones"]
        best_tour: List[int] = extra_data["best_tour"]
        best_length: float = _tour_length(best_tour)
        history_x = list(initial_state.history_x)
        history_y = list(initial_state.history_y)

        rng = random.Random(13)

        for it in range(1, iterations + 1):
            all_tours = [_construct_tour(pheromones, rng) for _ in range(ants)]
            all_lengths = [_tour_length(t) for t in all_tours]

            # Evaporate
            for i in range(_N_CITIES):
                for j in range(_N_CITIES):
                    pheromones[i][j] *= (1.0 - _RHO)

            # Deposit
            for tour, length in zip(all_tours, all_lengths):
                deposit = _Q / length
                for k in range(_N_CITIES):
                    a = tour[k]
                    b = tour[(k + 1) % _N_CITIES]
                    pheromones[a][b] += deposit
                    pheromones[b][a] += deposit
                if length < best_length:
                    best_length = length
                    best_tour = tour[:]

            history_x.append(float(it))
            history_y.append(best_length)

            yield CurveState(
                landscape_x=_LS_X,
                landscape_y=_LS_Y,
                current_x=float(it),
                current_y=best_length,
                history_x=tuple(history_x),
                history_y=tuple(history_y),
                iteration=it,
                best_x=float(it),
                best_y=best_length,
                gradient=None,
                extra=json.dumps({
                    "best_tour": best_tour,
                    "pheromones": [[round(v, 4) for v in row] for row in pheromones],
                    "iter": it,
                    "iterations": iterations,
                    "ants": ants,
                }),
                description=(
                    f"Iter {it}: best tour={best_tour}, length={best_length:.4f}"
                ),
            )

        return CurveState(
            landscape_x=_LS_X,
            landscape_y=_LS_Y,
            current_x=float(iterations),
            current_y=best_length,
            history_x=tuple(history_x),
            history_y=tuple(history_y),
            iteration=iterations,
            best_x=float(iterations),
            best_y=best_length,
            gradient=None,
            extra=json.dumps({
                "best_tour": best_tour,
                "pheromones": [[round(v, 4) for v in row] for row in pheromones],
                "iter": iterations,
                "iterations": iterations,
                "ants": ants,
            }),
            description=f"Done — best tour={best_tour}, length={best_length:.4f}",
        )
