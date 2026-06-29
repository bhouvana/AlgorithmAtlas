"""
Base classes for polyglot algorithm compilers.

Each compiler wraps a language toolchain (gcc, javac, dotnet, …) and follows
a shared frame output protocol:

  Protocol
  --------
  The compiled program writes one JSON object per line to stdout.  Each line
  is a simulation frame with the structure:

  {
    "frame_index": 0,
    "state": {
      "array":          [3, 1, 2, ...],
      "comparisons":    0,
      "swaps":          0,
      "comparing":      [i, j],   // indices being compared, or []
      "last_swap":      [i, j],   // indices just swapped, or []
      "sorted_indices": [],       // indices in final position
      "description":    "Comparing"
    }
  }

  The program receives three command-line arguments: seed  n  input_order
  where input_order is one of: random | sorted | reverse
"""
from __future__ import annotations

import abc
import json
import shutil
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CompilerResult:
    stdout:     str
    stderr:     str
    returncode: int
    lang:       str


class CompilerBase(abc.ABC):
    """Abstract base for all language compilers."""

    name:       str
    extensions: list[str]

    # ── availability ──────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """Return True if the required toolchain executables are on PATH."""
        return all(shutil.which(exe) is not None for exe in self._required_executables())

    def _required_executables(self) -> list[str]:
        """Return the list of executables that must be present."""
        return []

    # ── compilation ───────────────────────────────────────────────────────────

    @abc.abstractmethod
    def compile_and_run(
        self,
        source:      str,
        seed:        int,
        array_size:  int,
        input_order: str,
        timeout:     int = 30,
    ) -> CompilerResult:
        """Compile user source, inject harness, run, return stdout frames."""

    # ── helpers ───────────────────────────────────────────────────────────────

    def unavailable_error(self) -> RuntimeError:
        exes = self._required_executables()
        return RuntimeError(
            f"Language '{self.name}' requires {exes} on PATH but they were not found.\n"
            "Install the toolchain and make sure it is in your system PATH."
        )


def parse_frames(stdout: str) -> list[dict[str, Any]]:
    """
    Parse newline-delimited JSON frames from a compiled program's stdout.

    Non-JSON lines (debug prints, empty lines) are silently skipped.
    Missing optional fields are filled with safe defaults so the player
    never crashes on incomplete harness output.
    """
    frames: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Ensure outer structure
        if "frame_index" not in obj:
            obj["frame_index"] = len(frames)
        if "timestamp_ms" not in obj:
            obj["timestamp_ms"] = float(len(frames) * 100)
        if "event_label" not in obj:
            obj["event_label"] = None

        # Ensure state fields expected by the player
        state: dict[str, Any] = obj.get("state", {})
        for list_field in ("comparing", "last_swap", "sorted_indices"):
            if list_field not in state:
                state[list_field] = []
        if "comparisons" not in state:
            state["comparisons"] = 0
        if "swaps" not in state:
            state["swaps"] = 0
        if "description" not in state:
            state["description"] = ""
        obj["state"] = state

        frames.append(obj)

    return frames
