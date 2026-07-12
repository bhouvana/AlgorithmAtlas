"""
Shared stdout sentinel protocol between an adapter's generated driver and
runner.py's result parsing. A driver never prints anything else it can
control; a user's own debug prints (or accidental print() calls inside their
function) are tolerated by only trusting the LAST line starting with a known
sentinel, never the first line or a raw stdout compare.
"""
from __future__ import annotations

RESULT_SENTINEL = "@@ATLASCODE_RESULT@@"
CONTRACT_ERROR_SENTINEL = "@@ATLASCODE_CONTRACT_ERROR@@"


def find_sentinel_payload(stdout: str, sentinel: str) -> str | None:
    """Returns the JSON payload after the LAST occurrence of `sentinel` at the
    start of a line, or None if the sentinel never appears."""
    payload: str | None = None
    for line in stdout.splitlines():
        if line.startswith(sentinel):
            payload = line[len(sentinel):]
    return payload
