"""
AlgorithmTestHarness — standardized test infrastructure for plugins.

Every algorithm test file must use this harness.
It enforces the correctness invariants that the CI gate validates.
"""
from __future__ import annotations

import json
from typing import Callable, List

from .protocols import AlgorithmPlugin
from .types import AlgorithmState, SimulationParams


class AlgorithmTestHarness:
    """
    Standard test harness for algorithm plugins.

    Usage:
        harness = AlgorithmTestHarness(BubbleSortSimulation())
        states = harness.run_to_completion(params)
        harness.assert_deterministic(params)
        harness.assert_json_serializable(params)
    """

    def __init__(self, algorithm: AlgorithmPlugin) -> None:
        self.algorithm = algorithm

    def run_to_completion(self, params: SimulationParams) -> List[AlgorithmState]:
        """
        Run the algorithm from start to finish and return every state.

        Index 0 is the initial state (from initialize()).
        Index -1 is the terminal state (StopIteration.value from steps()).
        """
        initial = self.algorithm.initialize(params)
        states: List[AlgorithmState] = [initial]
        gen = self.algorithm.steps(initial)
        try:
            while True:
                states.append(next(gen))
        except StopIteration as e:
            if e.value is not None:
                states.append(e.value)
        return states

    def assert_deterministic(self, params: SimulationParams) -> None:
        """
        Identical params must produce identical frame sequences.
        Violation means the algorithm has hidden mutable state or unseeded randomness.
        """
        run1 = [s.to_dict() for s in self.run_to_completion(params)]
        run2 = [s.to_dict() for s in self.run_to_completion(params)]
        assert run1 == run2, (
            f"Algorithm '{type(self.algorithm).__name__}' is not deterministic. "
            f"Run 1 produced {len(run1)} frames, run 2 produced {len(run2)} frames."
        )

    def assert_json_serializable(self, params: SimulationParams) -> None:
        """
        Every state must be JSON-serializable.
        Violation means to_dict() returns non-primitive types (e.g., numpy arrays,
        frozensets, custom objects) that cannot cross the WebSocket boundary.
        """
        states = self.run_to_completion(params)
        for i, state in enumerate(states):
            try:
                json.dumps(state.to_dict())
            except (TypeError, ValueError) as e:
                raise AssertionError(
                    f"Frame {i} of '{type(self.algorithm).__name__}' "
                    f"is not JSON-serializable: {e}\n"
                    f"State dict: {state.to_dict()}"
                ) from e

    def assert_terminal_state(
        self,
        params: SimulationParams,
        validator: Callable[[AlgorithmState], bool],
        message: str = "Terminal state failed domain correctness check",
    ) -> None:
        """
        The final state must pass the provided correctness validator.

        Example:
            harness.assert_terminal_state(
                params,
                lambda s: list(s.array) == sorted(s.array),
                "Array must be sorted at termination"
            )
        """
        states = self.run_to_completion(params)
        assert states, "Algorithm produced no states (not even the initial state)"
        terminal = states[-1]
        assert validator(terminal), (
            f"{message}\n"
            f"Terminal state: {terminal.to_dict()}"
        )

    def get_frame_count(self, params: SimulationParams) -> int:
        """Return the total number of frames produced for the given params."""
        return len(self.run_to_completion(params))

    def get_terminal_state(self, params: SimulationParams) -> AlgorithmState:
        """Run to completion and return only the terminal state."""
        return self.run_to_completion(params)[-1]
