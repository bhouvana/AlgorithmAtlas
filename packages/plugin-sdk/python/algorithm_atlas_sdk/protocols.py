"""
AlgorithmPlugin protocol — the complete contract every plugin must satisfy.

Plugins import this and annotate their class to signal compliance.
The runtime validates with isinstance(plugin, AlgorithmPlugin).
"""
from __future__ import annotations

from typing import Generator, Protocol, runtime_checkable

from .types import AlgorithmMetadata, AlgorithmState, SimulationParams


@runtime_checkable
class AlgorithmPlugin(Protocol):
    """
    The full contract for an algorithm plugin.

    Rules that must never be violated by implementors:
    - metadata() must be pure and side-effect free
    - initialize() must respect params.seed for all random decisions
    - steps() must be a pure generator — no I/O, no side effects, no UI imports
    - steps() must be deterministic: same params → same frame sequence
    - Every yielded state must be JSON-serializable (state.to_dict() must not raise)
    """

    def metadata(self) -> AlgorithmMetadata:
        """Return static algorithm metadata. Called once at registration time."""
        ...

    def initialize(self, params: SimulationParams) -> AlgorithmState:
        """
        Construct and return the initial state for this simulation run.
        Must use params.seed to seed any random number generators.
        """
        ...

    def steps(
        self,
        initial_state: AlgorithmState,
    ) -> Generator[AlgorithmState, None, AlgorithmState]:
        """
        Yield each intermediate state transition.
        Return (via StopIteration.value) the terminal state.

        The generator is the simulation. There is no step() method.
        The simulation engine wraps this generator and materializes frames.
        """
        ...


