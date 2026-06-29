"""
Python runner — wraps the existing Algorithm Atlas SDK so Python algorithms
appear as first-class citizens in the polyglot run_code() API.

User contract
-------------
Write a function named `atlas_sort` that accepts a list and a callback:

    def atlas_sort(arr, cb):
        n = len(arr)
        for i in range(n - 1):
            for j in range(n - i - 1):
                cb(arr, "compare", j, j + 1)
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    cb(arr, "swap", j, j + 1)

Callback signature: cb(arr, action, i, j)
  action = "compare" | "swap" | <any string used as description>
"""
from __future__ import annotations

import json
import types

from .base import CompilerBase, CompilerResult

_PYTHON_HARNESS = """\
import json, sys, random

def _xorshift32(s):
    s = s & 0xFFFFFFFF
    s ^= (s << 13) & 0xFFFFFFFF
    s ^= (s >> 17) & 0xFFFFFFFF
    s ^= (s << 5)  & 0xFFFFFFFF
    return s

def _make_array(seed, n, order):
    arr = list(range(1, n + 1))
    if order == "sorted":
        return arr
    if order == "reverse":
        return list(reversed(arr))
    s = 42 if seed <= 0 else seed
    for i in range(n - 1, 0, -1):
        s = _xorshift32(s)
        j = s % (i + 1)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

_frames = []
_comparisons = 0
_swaps = 0

def _cb(arr, action, i=-1, j=-1):
    global _comparisons, _swaps
    cmp_idx  = [i, j] if action in ("compare", "comparing") and i >= 0 else []
    swap_idx = []
    desc = action
    if action in ("compare", "comparing"):
        _comparisons += 1
        desc = "Comparing"
        cmp_idx = [i, j] if i >= 0 else []
    elif action in ("swap", "swapped"):
        _swaps += 1
        desc = "Swapped"
        swap_idx = [i, j] if i >= 0 else []
    _frames.append({
        "frame_index": len(_frames),
        "timestamp_ms": float(len(_frames) * 100),
        "event_label": None,
        "state": {
            "array":          list(arr),
            "comparisons":    _comparisons,
            "swaps":          _swaps,
            "comparing":      cmp_idx,
            "last_swap":      swap_idx,
            "sorted_indices": [],
            "description":    desc,
        }
    })

def _run(seed, n, order):
    arr = _make_array(seed, n, order)
    _frames.append({"frame_index": 0, "timestamp_ms": 0.0, "event_label": None,
                    "state": {"array": list(arr), "comparisons": 0, "swaps": 0,
                              "comparing": [], "last_swap": [], "sorted_indices": [],
                              "description": "Initial state"}})
    atlas_sort(arr, _cb)
    _frames[0]["frame_index"] = 0  # fix up index
    # renumber
    for fi, f in enumerate(_frames):
        f["frame_index"] = fi
    # final sorted frame
    _frames.append({"frame_index": len(_frames), "timestamp_ms": float(len(_frames)*100),
                    "event_label": None,
                    "state": {"array": list(arr), "comparisons": _comparisons, "swaps": _swaps,
                              "comparing": [], "last_swap": [],
                              "sorted_indices": list(range(len(arr))),
                              "description": "Sorted!"}})
    for line in _frames:
        print(json.dumps(line))

_seed  = int(sys.argv[1]) if len(sys.argv) > 1 else 42
_n     = int(sys.argv[2]) if len(sys.argv) > 2 else 20
_order = sys.argv[3]      if len(sys.argv) > 3 else "random"
"""

_PYTHON_FOOTER = "\n_run(_seed, _n, _order)\n"


class PythonRunner(CompilerBase):
    name       = "python"
    extensions = [".py"]

    def _required_executables(self) -> list[str]:
        return []  # Python is always available

    def is_available(self) -> bool:
        return True

    def compile_and_run(
        self,
        source:      str,
        seed:        int,
        array_size:  int,
        input_order: str,
        timeout:     int = 30,
    ) -> CompilerResult:
        """Execute the Python source in the current interpreter process."""
        import io, sys as _sys, contextlib

        full_source = _PYTHON_HARNESS + source + _PYTHON_FOOTER
        namespace: dict = {}
        old_argv = _sys.argv
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        try:
            _sys.argv = ["atlas", str(seed), str(array_size), input_order]
            with contextlib.redirect_stdout(stdout_buf), \
                 contextlib.redirect_stderr(stderr_buf):
                exec(compile(full_source, "<atlas_python>", "exec"), namespace)
            returncode = 0
        except SystemExit as e:
            returncode = int(e.code) if e.code is not None else 0
        except Exception as exc:
            stderr_buf.write(f"{type(exc).__name__}: {exc}\n")
            returncode = 1
        finally:
            _sys.argv = old_argv

        return CompilerResult(
            stdout=stdout_buf.getvalue(),
            stderr=stderr_buf.getvalue(),
            returncode=returncode,
            lang="python",
        )
