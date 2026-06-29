"""
Poisson Process — Algorithm Atlas Plugin

Simulates a Poisson process with rate λ (events per second). Inter-arrival
times are exponentially distributed: T ~ Exp(λ), sampled as -ln(U)/λ where
U ~ Uniform(0,1).

Shows the inter-arrival time histogram converging to Exp(λ), the cumulative
event count (path_y) vs arrival times (path_x), and the empirical mean
inter-arrival time converging to the true value 1/λ.
"""
from __future__ import annotations

import math
import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    ProbabilityState,
    SimulationParams,
)


class PoissonProcess:
    """Poisson process simulation via exponential inter-arrivals."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="poisson-process",
            name="Poisson Process",
            category="probability",
            visualization_type="PROBABILITY_SPACE",
            description=(
                "Simulates a Poisson process with configurable rate λ (events/second). "
                "Inter-arrival times are drawn as -ln(U)/λ (exponential distribution). "
                "The histogram shows the inter-arrival distribution; the empirical mean "
                "converges to the true value 1/λ."
            ),
            intuition=(
                "Events occur randomly but at a steady average rate λ. The time between "
                "consecutive events follows an exponential distribution with mean 1/λ. "
                "A Poisson process is memoryless: the next event is equally likely "
                "regardless of how long you have already waited."
            ),
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=("probability", "poisson-process", "simulation", "exponential", "arrival"),
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> ProbabilityState:
        duration = float(params.inputs.get("duration", 20.0))
        rate = float(params.inputs.get("rate", 3.0))
        seed = int(params.inputs.get("seed", 42))
        # Histogram: 10 bins for inter-arrival times 0..2 (bin width 0.2)
        BIN_WIDTH = 0.2
        bins = tuple(i * BIN_WIDTH for i in range(10))
        total_trials = int(duration * rate * 3)  # generous upper bound for events
        return ProbabilityState(
            samples=(float(seed), rate),
            histogram_bins=bins,
            histogram_counts=tuple(0 for _ in range(10)),
            trial=0,
            total_trials=total_trials,
            estimate=0.0,
            true_value=round(1.0 / rate, 6),
            path_x=(),
            path_y=(),
            description=(
                f"Simulating Poisson process: rate={rate}/s, duration={duration}s. "
                f"True mean inter-arrival = {1/rate:.4f}s."
            ),
        )

    def steps(
        self,
        initial_state: ProbabilityState,
    ) -> Generator[ProbabilityState, None, ProbabilityState]:
        seed = int(initial_state.samples[0]) if initial_state.samples else 42
        rate = float(initial_state.samples[1]) if len(initial_state.samples) > 1 else 3.0
        rng = random.Random(seed)

        # Recover duration from total_trials heuristic (total_trials = duration*rate*3)
        total_trials = initial_state.total_trials
        duration = total_trials / (rate * 3)
        true_mean = 1.0 / rate

        BIN_EDGES = list(initial_state.histogram_bins)   # 0, 0.2, 0.4, ..., 1.8
        N_BINS = len(BIN_EDGES)
        BIN_WIDTH = BIN_EDGES[1] - BIN_EDGES[0] if N_BINS > 1 else 0.2
        bin_counts = [0] * N_BINS

        arrival_times: list[float] = []
        inter_arrivals: list[float] = []
        t = 0.0
        event_count = 0
        sum_inter = 0.0

        while True:
            # Sample next inter-arrival time
            u = rng.random()
            while u == 0.0:
                u = rng.random()
            inter = -math.log(u) / rate
            t += inter

            if t > duration:
                break

            event_count += 1
            inter_arrivals.append(inter)
            arrival_times.append(t)
            sum_inter += inter

            # Bin the inter-arrival time
            bin_idx = int(inter / BIN_WIDTH)
            bin_idx = max(0, min(bin_idx, N_BINS - 1))
            bin_counts[bin_idx] += 1

            empirical_mean = sum_inter / event_count

            if event_count % 10 == 0 or t >= duration:
                yield ProbabilityState(
                    samples=tuple(inter_arrivals[-20:]),
                    histogram_bins=tuple(BIN_EDGES),
                    histogram_counts=tuple(bin_counts),
                    trial=event_count,
                    total_trials=total_trials,
                    estimate=empirical_mean,
                    true_value=round(true_mean, 6),
                    path_x=tuple(arrival_times),
                    path_y=tuple(float(i + 1) for i in range(len(arrival_times))),
                    description=(
                        f"Event {event_count} at t={t:.3f}s. "
                        f"Mean inter-arrival={empirical_mean:.4f}s "
                        f"(true={true_mean:.4f}s)"
                    ),
                )

        empirical_mean = (sum_inter / event_count) if event_count > 0 else 0.0
        return ProbabilityState(
            samples=tuple(inter_arrivals[-20:]),
            histogram_bins=tuple(BIN_EDGES),
            histogram_counts=tuple(bin_counts),
            trial=event_count,
            total_trials=total_trials,
            estimate=empirical_mean,
            true_value=round(true_mean, 6),
            path_x=tuple(arrival_times),
            path_y=tuple(float(i + 1) for i in range(len(arrival_times))),
            description=(
                f"Simulation complete: {event_count} events in {duration}s. "
                f"Empirical mean={empirical_mean:.4f}s, true={true_mean:.4f}s"
            ),
        )
