"""
Core types shared between the Algorithm Atlas platform and all plugins.

This module is the single source of truth for the state contract.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Simulation parameters
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SimulationParams:
    """
    Immutable parameters for a single simulation run.
    seed guarantees identical output across runs with identical inputs.
    """
    seed: int
    inputs: Dict[str, Any]
    config: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Algorithm state base
# ---------------------------------------------------------------------------

class AlgorithmState:
    """
    Abstract base for all algorithm states.

    Invariants every subclass must satisfy:
    - Immutable: use @dataclass(frozen=True)
    - JSON-serializable: to_dict() must return only primitives, lists, dicts
    - Reconstructible: from_dict(state.to_dict()) == state
    """

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError(f"{self.__class__.__name__} must implement to_dict()")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlgorithmState":
        raise NotImplementedError(f"{cls.__name__} must implement from_dict()")

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        return self.to_dict() == other.to_dict()  # type: ignore[union-attr]

    def __hash__(self) -> int:
        return hash(repr(self.to_dict()))


# ---------------------------------------------------------------------------
# Sorting state
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SortState(AlgorithmState):
    """
    State for all comparison-based and non-comparison sorting algorithms.

    array:             Current ordering of elements.
    comparing:         Pair of indices being compared (amber in renderer).
    last_swap:         Pair of indices last swapped (red in renderer).
    sorted_indices:    Positions confirmed to be in final sorted position (green).
    auxiliary_indices: Algorithm-specific highlights — pivot index, tracked minimum,
                       current heap root, etc. (yellow/orange in renderer).
    comparisons:       Running total comparisons.
    swaps:             Running total swaps / moves.
    description:       Human-readable event description for the event log.
    """
    array: Tuple[int, ...]
    comparing: Optional[Tuple[int, int]]
    last_swap: Optional[Tuple[int, int]]
    sorted_indices: FrozenSet[int]
    comparisons: int
    swaps: int
    auxiliary_indices: FrozenSet[int] = frozenset()
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "array": list(self.array),
            "comparing": list(self.comparing) if self.comparing is not None else None,
            "last_swap": list(self.last_swap) if self.last_swap is not None else None,
            "sorted_indices": sorted(self.sorted_indices),
            "auxiliary_indices": sorted(self.auxiliary_indices),
            "comparisons": self.comparisons,
            "swaps": self.swaps,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SortState":
        return cls(
            array=tuple(data["array"]),
            comparing=tuple(data["comparing"]) if data.get("comparing") is not None else None,
            last_swap=tuple(data["last_swap"]) if data.get("last_swap") is not None else None,
            sorted_indices=frozenset(data.get("sorted_indices", [])),
            auxiliary_indices=frozenset(data.get("auxiliary_indices", [])),
            comparisons=data["comparisons"],
            swaps=data["swaps"],
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Search state
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SearchState(AlgorithmState):
    """
    State for searching algorithms.

    array:          The array being searched (must be sorted for binary/interpolation/etc.).
    target:         The value being searched for.
    current:        Index currently being examined (amber).
    low:            Left boundary of active search region (for range-based searches).
    high:           Right boundary of active search region.
    eliminated:     Indices ruled out (grayed in renderer).
    found_at:       Index where target was found, or None if not yet found.
    comparisons:    Running total.
    description:    Event log label.
    """
    array: Tuple[int, ...]
    target: int
    current: Optional[int]
    low: Optional[int]
    high: Optional[int]
    eliminated: FrozenSet[int]
    found_at: Optional[int]
    comparisons: int
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "array": list(self.array),
            "target": self.target,
            "current": self.current,
            "low": self.low,
            "high": self.high,
            "eliminated": sorted(self.eliminated),
            "found_at": self.found_at,
            "comparisons": self.comparisons,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchState":
        return cls(
            array=tuple(data["array"]),
            target=data["target"],
            current=data.get("current"),
            low=data.get("low"),
            high=data.get("high"),
            eliminated=frozenset(data.get("eliminated", [])),
            found_at=data.get("found_at"),
            comparisons=data["comparisons"],
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Graph state
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NodeState:
    node_id: str
    label: str
    x: float = 0.0
    y: float = 0.0
    weight: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"node_id": self.node_id, "label": self.label,
                "x": self.x, "y": self.y, "weight": self.weight}


@dataclass(frozen=True)
class EdgeState:
    edge_id: str
    source: str
    target: str
    weight: Optional[float] = None
    directed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {"edge_id": self.edge_id, "source": self.source,
                "target": self.target, "weight": self.weight, "directed": self.directed}


@dataclass(frozen=True)
class GraphTraversalState(AlgorithmState):
    """State for graph traversal and shortest-path algorithms."""
    nodes: Tuple[NodeState, ...]
    edges: Tuple[EdgeState, ...]
    visited: FrozenSet[str]
    frontier: Tuple[str, ...]       # BFS queue or DFS stack — shows exploration order
    current: Optional[str]
    distances: Dict[str, float]
    path: Tuple[str, ...]           # Current best or discovered path
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "visited": list(self.visited),
            "frontier": list(self.frontier),
            "current": self.current,
            "distances": {k: (None if not math.isfinite(v) else v) for k, v in self.distances.items()},
            "path": list(self.path),
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphTraversalState":
        return cls(
            nodes=tuple(NodeState(**n) for n in data["nodes"]),
            edges=tuple(EdgeState(**e) for e in data["edges"]),
            visited=frozenset(data["visited"]),
            frontier=tuple(data["frontier"]),
            current=data.get("current"),
            distances=data["distances"],
            path=tuple(data["path"]),
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# DP state
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DPState(AlgorithmState):
    """State for dynamic programming algorithms with a 2D memoization table."""
    table: Tuple[Tuple[Any, ...], ...]
    current_cell: Optional[Tuple[int, int]]
    computed_cells: FrozenSet[Tuple[int, int]]
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table": [list(row) for row in self.table],
            "current_cell": list(self.current_cell) if self.current_cell is not None else None,
            "computed_cells": [list(c) for c in sorted(self.computed_cells)],
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DPState":
        return cls(
            table=tuple(tuple(row) for row in data["table"]),
            current_cell=tuple(data["current_cell"]) if data.get("current_cell") is not None else None,  # type: ignore
            computed_cells=frozenset(tuple(c) for c in data.get("computed_cells", [])),  # type: ignore
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Grid state (A*, BFS grid, flood-fill, maze)
# ---------------------------------------------------------------------------

# Cell type constants
CELL_EMPTY   = 0
CELL_WALL    = 1
CELL_START   = 2
CELL_GOAL    = 3
CELL_OPEN    = 4  # in open/frontier set
CELL_CLOSED  = 5  # in closed/visited set
CELL_PATH    = 6  # final reconstructed path


@dataclass(frozen=True)
class GridState(AlgorithmState):
    """
    State for grid-based pathfinding algorithms (A*, BFS, flood-fill).

    grid:        2D tuple of cell values (CELL_* constants).
    current:     (row, col) currently being expanded, or None.
    path:        sequence of (row, col) tuples forming the found path.
    description: human-readable step label.
    """
    grid: Tuple[Tuple[int, ...], ...]
    current: Optional[Tuple[int, int]]
    path: Tuple[Tuple[int, int], ...]
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid": [list(row) for row in self.grid],
            "current": list(self.current) if self.current is not None else None,
            "path": [list(cell) for cell in self.path],
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GridState":
        return cls(
            grid=tuple(tuple(row) for row in data["grid"]),
            current=tuple(data["current"]) if data.get("current") is not None else None,  # type: ignore
            path=tuple(tuple(c) for c in data.get("path", [])),  # type: ignore
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Simulation frame — transport object wrapping a state
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SimulationFrame:
    frame_index: int
    state: AlgorithmState
    timestamp_ms: int
    event_label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_index": self.frame_index,
            "state": self.state.to_dict(),
            "timestamp_ms": self.timestamp_ms,
            "event_label": self.event_label,
        }


# ---------------------------------------------------------------------------
# Cellular Automata state (Game of Life, Boids, Forest Fire, 1D CAs…)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CellularAutomataState(AlgorithmState):
    """
    State for cellular automata and grid-based emergent simulations.

    grid:         2D tuple of non-negative ints. Cell semantics are algorithm-specific
                  but the convention is: 0 = dead/empty, 1+ = alive/active (type codes).
    width:        Grid columns.
    height:       Grid rows.
    generation:   Step counter.
    alive_count:  Total living/active cells at this generation.
    description:  Human-readable label.
    """
    grid: Tuple[Tuple[int, ...], ...]
    width: int
    height: int
    generation: int
    alive_count: int
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid": [list(row) for row in self.grid],
            "width": self.width,
            "height": self.height,
            "generation": self.generation,
            "alive_count": self.alive_count,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CellularAutomataState":
        return cls(
            grid=tuple(tuple(row) for row in data["grid"]),
            width=data["width"],
            height=data["height"],
            generation=data["generation"],
            alive_count=data["alive_count"],
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Distributed systems state (Raft, Paxos, Vector Clocks, Gossip…)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DSNode:
    """A single node in a distributed system simulation."""
    node_id: str
    role: str          # "follower" | "candidate" | "leader" | "down" | "participant" …
    term: int          # Raft term / Paxos ballot / logical clock
    log: Tuple[str, ...]     # simplified log entries as strings
    inbox: Tuple[str, ...]   # pending messages shown in node tooltip
    data: str          # JSON-serialisable extra (e.g. committed value, vote target)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "role": self.role,
            "term": self.term,
            "log": list(self.log),
            "inbox": list(self.inbox),
            "data": self.data,
        }


@dataclass(frozen=True)
class DSMessage:
    """An in-flight message between two nodes."""
    msg_id: str
    src: str
    dst: str
    msg_type: str      # "RequestVote" | "AppendEntries" | "Prepare" | "Promise" …
    payload: str       # short human-readable summary of content
    delivered: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "msg_id": self.msg_id,
            "src": self.src,
            "dst": self.dst,
            "msg_type": self.msg_type,
            "payload": self.payload,
            "delivered": self.delivered,
        }


@dataclass(frozen=True)
class DistributedSystemState(AlgorithmState):
    """
    Global snapshot of a distributed system at one discrete event.

    nodes:    All nodes with their current role, term, and log.
    messages: In-flight or recently-delivered messages.
    event:    Short tag for what triggered this step ("election_timeout", "vote_granted"…).
    description: Full human-readable step explanation.
    """
    nodes: Tuple[DSNode, ...]
    messages: Tuple[DSMessage, ...]
    event: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "messages": [m.to_dict() for m in self.messages],
            "event": self.event,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DistributedSystemState":
        return cls(
            nodes=tuple(DSNode(**n) for n in data["nodes"]),
            messages=tuple(DSMessage(**m) for m in data["messages"]),
            event=data.get("event", ""),
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Cryptography state (RSA, DH, AES rounds, SHA-256, cipher visualizations…)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CryptoState(AlgorithmState):
    """
    State for step-by-step cryptographic algorithm visualizations.

    variables:   Ordered key-value pairs shown in the variable table
                 e.g. (("p", "61"), ("q", "53"), ("n", "3233"), …)
    operation:   Current mathematical operation as a string
                 e.g. "n = p × q = 61 × 53"
    step_name:   Short label for the current phase
                 e.g. "Key Generation", "Encryption", "Decryption"
    highlighted: Variable names that are actively being used/produced in this step.
    bits:        Optional binary/hex string for bit-level visualizations (AES, SHA).
    result:      Final output or None if not yet complete.
    description: Human-readable explanation.
    """
    variables: Tuple[Tuple[str, str], ...]
    operation: str
    step_name: str
    highlighted: Tuple[str, ...]
    bits: Optional[str]
    result: Optional[str]
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "variables": [list(v) for v in self.variables],
            "operation": self.operation,
            "step_name": self.step_name,
            "highlighted": list(self.highlighted),
            "bits": self.bits,
            "result": self.result,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CryptoState":
        return cls(
            variables=tuple(tuple(v) for v in data["variables"]),  # type: ignore[arg-type]
            operation=data.get("operation", ""),
            step_name=data.get("step_name", ""),
            highlighted=tuple(data.get("highlighted", [])),
            bits=data.get("bits"),
            result=data.get("result"),
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Optimization / Curve state (Gradient Descent, Hill Climbing, GA, PSO…)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CurveState(AlgorithmState):
    """
    State for optimization algorithms plotted on a 1-D or 2-D landscape.

    landscape_x / landscape_y:  Pre-sampled points for drawing the objective function.
    current_x / current_y:      The optimizer's current position.
    history_x / history_y:      All positions visited so far (trajectory).
    iteration:                  Step counter.
    best_x / best_y:            Best position seen so far.
    gradient:                   Gradient at current_x (None if not applicable).
    extra:                      Algorithm-specific extra data as a JSON string
                                (e.g. population for GA, particles for PSO).
    description:                Human-readable step label.
    """
    landscape_x: Tuple[float, ...]
    landscape_y: Tuple[float, ...]
    current_x: float
    current_y: float
    history_x: Tuple[float, ...]
    history_y: Tuple[float, ...]
    iteration: int
    best_x: float
    best_y: float
    gradient: Optional[float]
    extra: str = ""      # JSON string for algorithm-specific data
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "landscape_x": list(self.landscape_x),
            "landscape_y": list(self.landscape_y),
            "current_x": self.current_x,
            "current_y": self.current_y,
            "history_x": list(self.history_x),
            "history_y": list(self.history_y),
            "iteration": self.iteration,
            "best_x": self.best_x,
            "best_y": self.best_y,
            "gradient": self.gradient,
            "extra": self.extra,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CurveState":
        return cls(
            landscape_x=tuple(data["landscape_x"]),
            landscape_y=tuple(data["landscape_y"]),
            current_x=data["current_x"],
            current_y=data["current_y"],
            history_x=tuple(data["history_x"]),
            history_y=tuple(data["history_y"]),
            iteration=data["iteration"],
            best_x=data["best_x"],
            best_y=data["best_y"],
            gradient=data.get("gradient"),
            extra=data.get("extra", ""),
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Probability / Simulation state (Monte Carlo, Markov Chains, Brownian…)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProbabilityState(AlgorithmState):
    """
    State for probability simulations and stochastic algorithm visualizations.

    samples:           Raw sample values collected so far.
    histogram_bins:    Left edge of each histogram bin.
    histogram_counts:  Count of samples in each bin.
    trial:             Current trial number.
    total_trials:      Total trials planned.
    estimate:          Running estimate of the quantity being computed.
    true_value:        Analytical true value (if known) for error display.
    path_x / path_y:   2-D walk or time-series trajectory (empty if not applicable).
    description:       Human-readable step label.
    """
    samples: Tuple[float, ...]
    histogram_bins: Tuple[float, ...]
    histogram_counts: Tuple[int, ...]
    trial: int
    total_trials: int
    estimate: float
    true_value: Optional[float]
    path_x: Tuple[float, ...] = ()
    path_y: Tuple[float, ...] = ()
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "samples": list(self.samples),
            "histogram_bins": list(self.histogram_bins),
            "histogram_counts": list(self.histogram_counts),
            "trial": self.trial,
            "total_trials": self.total_trials,
            "estimate": self.estimate,
            "true_value": self.true_value,
            "path_x": list(self.path_x),
            "path_y": list(self.path_y),
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProbabilityState":
        return cls(
            samples=tuple(data.get("samples", [])),
            histogram_bins=tuple(data.get("histogram_bins", [])),
            histogram_counts=tuple(data.get("histogram_counts", [])),
            trial=data["trial"],
            total_trials=data["total_trials"],
            estimate=data["estimate"],
            true_value=data.get("true_value"),
            path_x=tuple(data.get("path_x", [])),
            path_y=tuple(data.get("path_y", [])),
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Algorithm metadata
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AlgorithmMetadata:
    slug: str
    name: str
    category: str
    visualization_type: str
    description: str
    intuition: str
    complexity_time_best: str
    complexity_time_average: str
    complexity_time_worst: str
    complexity_space: str
    tags: Tuple[str, ...] = field(default_factory=tuple)
    execution_target: str = "server"
    version: str = "1.0.0"
