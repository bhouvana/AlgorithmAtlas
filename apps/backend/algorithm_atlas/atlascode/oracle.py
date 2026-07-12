"""
Oracle harness.

Generated AtlasCode test cases must never have hand-typed expected outputs.
Instead we run the REAL plugin implementation — the same code that powers
the visualization and is already covered by the plugin test suite — via
AlgorithmTestHarness, and read the ground truth off its terminal state.

Each oracle function also runs a cheap independent sanity assertion (e.g.
"the output is actually a permutation-sorted version of the input") so a
broken plugin can never silently produce a wrong "expected" value.
"""
from __future__ import annotations

import re
from typing import Callable

from algorithm_atlas_sdk import AlgorithmTestHarness, SimulationParams
from algorithm_atlas_sdk.types import AlgorithmState, SearchState, SortState

from ..plugins.registry import RegisteredAlgorithm


class OracleError(Exception):
    """Raised when a plugin can't serve as an oracle for a given contract."""


def run_generic_oracle(
    registered: RegisteredAlgorithm,
    seed: int,
    inputs: dict,
    extractor: Callable[[AlgorithmState, AlgorithmState], object],
) -> object:
    """
    Runs initialize()/steps() to completion and hands (initial, terminal)
    state to `extractor`, which must return the answer or raise OracleError.

    This is the escape hatch for state shapes without a uniform contract
    (DPState's answer position varies per algorithm, CryptoState's answer key
    varies per algorithm, etc.) — the extractor still only ever *reads* the
    real plugin's own terminal state, it never computes an answer itself.
    """
    plugin = registered.instantiate()
    params = SimulationParams(seed=seed, inputs=inputs)
    initial = plugin.initialize(params)
    terminal = AlgorithmTestHarness(plugin).get_terminal_state(params)
    try:
        return extractor(initial, terminal)
    except OracleError:
        raise
    except Exception as exc:
        raise OracleError(f"{registered.slug}: extractor failed: {exc}") from exc


def extract_last_int(description: str, slug: str) -> int:
    """Last integer literal in a terminal-state description string."""
    matches = re.findall(r"-?\d+", description)
    if not matches:
        raise OracleError(f"{slug}: no integer found in description {description!r}")
    return int(matches[-1])


def extract_int_after(description: str, marker: str, slug: str) -> int:
    """First integer immediately following `marker` in the description string."""
    m = re.search(re.escape(marker) + r"\s*(-?\d+)", description)
    if not m:
        raise OracleError(f"{slug}: pattern {marker!r} not found in description {description!r}")
    return int(m.group(1))


def run_sort_oracle(
    registered: RegisteredAlgorithm,
    seed: int,
    array_size: int,
    input_order: str = "random",
) -> tuple[list[int], list[int]]:
    """
    Returns (input_array, sorted_array).

    input_array/sorted_array come straight from the plugin's own
    initialize()/steps() — never independently re-typed.
    """
    plugin = registered.instantiate()
    params = SimulationParams(seed=seed, inputs={"array_size": array_size, "input_order": input_order})
    initial = plugin.initialize(params)
    if not isinstance(initial, SortState):
        raise OracleError(f"{registered.slug}: initialize() did not return SortState")

    terminal = AlgorithmTestHarness(plugin).get_terminal_state(params)
    if not isinstance(terminal, SortState):
        raise OracleError(f"{registered.slug}: terminal state is not SortState")

    if sorted(initial.array) != list(terminal.array):
        raise OracleError(
            f"{registered.slug}: terminal array is not a valid ascending sort of the input "
            f"(input={initial.array!r}, terminal={terminal.array!r})"
        )
    return list(initial.array), list(terminal.array)


def run_search_oracle(
    registered: RegisteredAlgorithm,
    seed: int,
    array_size: int,
) -> tuple[list[int], int, int]:
    """
    Returns (sorted_array, target, found_index) with found_index == -1 when
    the target isn't present.
    """
    plugin = registered.instantiate()
    params = SimulationParams(seed=seed, inputs={"array_size": array_size})
    initial = plugin.initialize(params)
    if not isinstance(initial, SearchState):
        raise OracleError(f"{registered.slug}: initialize() did not return SearchState")

    terminal = AlgorithmTestHarness(plugin).get_terminal_state(params)
    if not isinstance(terminal, SearchState):
        raise OracleError(f"{registered.slug}: terminal state is not SearchState")

    found_at = terminal.found_at
    if found_at is not None:
        if not (0 <= found_at < len(initial.array)) or initial.array[found_at] != initial.target:
            raise OracleError(
                f"{registered.slug}: found_at={found_at} does not point at the target "
                f"in array {initial.array!r} (target={initial.target})"
            )
    elif len(set(initial.array)) == len(initial.array) and initial.target in initial.array:
        raise OracleError(
            f"{registered.slug}: claimed target not found, but {initial.target} is in the array"
        )

    return list(initial.array), initial.target, (found_at if found_at is not None else -1)
