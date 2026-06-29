"""
Benchmark Runner — measures algorithm performance across input sizes.

Runs each algorithm multiple trials per size and reports median timing.
Separates initialize() time from steps() time so callers can distinguish
setup cost from algorithmic work.
"""
from __future__ import annotations

import statistics
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from algorithm_atlas_sdk.protocols import AlgorithmPlugin
from algorithm_atlas_sdk.types import SimulationParams


@dataclass
class SizeResult:
    """Aggregated benchmark result for a single input size."""
    input_size: int
    frame_count: int
    init_ms: float
    steps_ms: float
    total_ms: float


class BenchmarkRunner:
    """
    Times an AlgorithmPlugin across a range of input sizes.

    Each (size, trial) pair creates fresh SimulationParams so:
    - Seed varies per trial (seed + trial_index) → different data each trial
    - Results are aggregated as medians across trials
    """

    def run(
        self,
        algorithm: AlgorithmPlugin,
        sizes: List[int],
        size_param: str = "array_size",
        param_overrides: Optional[Dict[str, Any]] = None,
        trials: int = 3,
        base_seed: int = 42,
    ) -> List[SizeResult]:
        """
        Run the algorithm for each size and return one SizeResult per size.

        Args:
            algorithm:       A fresh (or re-usable) plugin instance.
            sizes:           List of input sizes to benchmark.
            size_param:      The params.inputs key that controls the input size
                             (e.g., "array_size", "node_count").
            param_overrides: Additional fixed inputs merged into every run.
            trials:          Number of independent runs per size (for median).
            base_seed:       Seeds are base_seed + trial_index for variety.
        """
        overrides = param_overrides or {}
        results: List[SizeResult] = []

        for size in sizes:
            init_times: List[float] = []
            step_times: List[float] = []
            frame_count = 0

            for trial in range(trials):
                params = SimulationParams(
                    seed=base_seed + trial,
                    inputs={size_param: size, **overrides},
                )

                # ── initialize ────────────────────────────────────────────────
                t0 = time.perf_counter()
                initial_state = algorithm.initialize(params)
                init_times.append((time.perf_counter() - t0) * 1000)

                # ── steps ─────────────────────────────────────────────────────
                t1 = time.perf_counter()
                gen = algorithm.steps(initial_state)
                count = 1  # initial_state counts as frame 0
                try:
                    while True:
                        next(gen)
                        count += 1
                except StopIteration as exc:
                    if exc.value is not None:
                        count += 1   # terminal state
                step_times.append((time.perf_counter() - t1) * 1000)
                frame_count = count

            results.append(SizeResult(
                input_size=size,
                frame_count=frame_count,
                init_ms=round(statistics.median(init_times), 4),
                steps_ms=round(statistics.median(step_times), 4),
                total_ms=round(
                    statistics.median(init_times) + statistics.median(step_times), 4
                ),
            ))

        return results
