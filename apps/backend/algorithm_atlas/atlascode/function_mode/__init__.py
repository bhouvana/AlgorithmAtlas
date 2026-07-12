"""
Function Mode -- the second Run contract for AtlasCode (see Program Mode's
existing submission/evaluator.py for the first).

Program Mode:  complete program -> stdin -> stdout -> stdout comparison.
Function Mode: only the requested function body -> server-generated driver ->
                typed arguments -> function invocation -> typed return ->
                semantic comparison.

Nothing here touches Submit (submissions.py) or the Program Mode evaluator --
this package is only ever invoked from the Run endpoint's function-mode branch.
"""
from __future__ import annotations
