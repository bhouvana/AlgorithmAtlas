"""Persistent, per-cell matrix ledger for the AtlasCode dual-mode completion
pass (mission Phase 1).

This is deliberately NOT the same thing as `docs/atlascode-orchestrator-checkpoint.json`
(complete_dual_mode_matrix.py's checkpoint), which only tracks whether a whole
SCRIPT/PHASE succeeded. This ledger tracks the finer-grained unit the mission
requires: one row per (problem_id, language, mode) cell, with an honest
verification_level (0-6, never collapsed) so "adapter exists" can never be
misreported as "runs correctly."

Stored as a table in the canonical atlas.db (resolved the same way the rest
of the backend resolves it -- repo-root absolute path, never a relative
`./atlas.db` that silently picks up the wrong cwd-dependent file). A ledger
table alongside `problems`/`test_cases` is appropriate here: it is real,
durable judge-verification history, not throwaway script state.

Verification levels (never collapsed into each other):
  0 unsupported               -- no adapter/toolchain for this language at all
  1 adapter_exists             -- adapter class registered, nothing executed yet
  2 syntax_valid                -- generated driver source parses / is well-formed
  3 compiles_or_loads          -- compiler/interpreter accepts the generated program
  4 correct_passes             -- a correct reference solution passes the full corpus
  5 wrong_rejected              -- a genuinely-wrong solution is rejected on >=1 case
  6 verified                    -- both 4 AND 5 hold: the real Level-6 bar
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"

LEVEL_UNSUPPORTED = 0
LEVEL_ADAPTER_EXISTS = 1
LEVEL_SYNTAX_VALID = 2
LEVEL_COMPILES_OR_LOADS = 3
LEVEL_CORRECT_PASSES = 4
LEVEL_WRONG_REJECTED = 5
LEVEL_VERIFIED = 6

LEVEL_NAMES = {
    0: "unsupported",
    1: "adapter_exists",
    2: "syntax_valid",
    3: "compiles_or_loads",
    4: "correct_passes",
    5: "wrong_rejected",
    6: "verified",
}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS atlascode_matrix_ledger (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id          TEXT NOT NULL,
    language            TEXT NOT NULL,
    mode                TEXT NOT NULL,              -- 'function' | 'program'
    adapter_version     TEXT,
    contract_version    TEXT,                       -- hash of function_contract JSON at verification time
    test_suite_version  TEXT,                        -- problems.test_suite_version at verification time
    toolchain_version   TEXT,                        -- e.g. compiler/interpreter version string
    verification_level  INTEGER NOT NULL,
    status              TEXT NOT NULL,               -- pass | fail | error | timeout | toolchain_unavailable
    failure_class       TEXT,
    failure_message      TEXT,
    duration_ms         REAL,
    timestamp           REAL NOT NULL,
    UNIQUE(problem_id, language, mode)
);
CREATE INDEX IF NOT EXISTS idx_ledger_lang_mode ON atlascode_matrix_ledger(language, mode);
CREATE INDEX IF NOT EXISTS idx_ledger_level ON atlascode_matrix_ledger(verification_level);
"""


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def ensure_schema(con: sqlite3.Connection) -> None:
    con.executescript(_SCHEMA)
    con.commit()


def record_cell(
    con: sqlite3.Connection,
    *,
    problem_id: str,
    language: str,
    mode: str,
    verification_level: int,
    status: str,
    adapter_version: str | None = None,
    contract_version: str | None = None,
    test_suite_version: str | None = None,
    toolchain_version: str | None = None,
    failure_class: str | None = None,
    failure_message: str | None = None,
    duration_ms: float | None = None,
) -> None:
    """Upserts one cell. A re-verification of the same (problem, language,
    mode) OVERWRITES the previous row -- the ledger records current truth,
    not a history log (a separate append-only run log can be layered on top
    later if audit history is ever needed; not built now because nothing in
    the mission asks for it)."""
    con.execute(
        """
        INSERT INTO atlascode_matrix_ledger
            (problem_id, language, mode, adapter_version, contract_version,
             test_suite_version, toolchain_version, verification_level,
             status, failure_class, failure_message, duration_ms, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(problem_id, language, mode) DO UPDATE SET
            adapter_version=excluded.adapter_version,
            contract_version=excluded.contract_version,
            test_suite_version=excluded.test_suite_version,
            toolchain_version=excluded.toolchain_version,
            verification_level=excluded.verification_level,
            status=excluded.status,
            failure_class=excluded.failure_class,
            failure_message=excluded.failure_message,
            duration_ms=excluded.duration_ms,
            timestamp=excluded.timestamp
        """,
        (
            problem_id, language, mode, adapter_version, contract_version,
            test_suite_version, toolchain_version, verification_level,
            status, failure_class, failure_message, duration_ms, time.time(),
        ),
    )
    con.commit()


def get_cell(con: sqlite3.Connection, problem_id: str, language: str, mode: str) -> sqlite3.Row | None:
    cur = con.execute(
        "SELECT * FROM atlascode_matrix_ledger WHERE problem_id=? AND language=? AND mode=?",
        (problem_id, language, mode),
    )
    return cur.fetchone()


def already_verified(
    con: sqlite3.Connection, problem_id: str, language: str, mode: str,
    *, min_level: int = LEVEL_VERIFIED,
    contract_version: str | None = None, test_suite_version: str | None = None,
) -> bool:
    """Used by --resume: a cell only counts as 'done' if it already reached
    min_level AND (when provided) the contract/test-suite versions it was
    verified against still match current state -- prevents a stale pass from
    a since-changed contract or corpus from being silently trusted."""
    row = get_cell(con, problem_id, language, mode)
    if row is None or row["verification_level"] < min_level:
        return False
    if contract_version is not None and row["contract_version"] != contract_version:
        return False
    if test_suite_version is not None and row["test_suite_version"] != test_suite_version:
        return False
    return True


def summary(con: sqlite3.Connection) -> dict:
    cur = con.execute(
        "SELECT language, mode, verification_level, COUNT(*) as n "
        "FROM atlascode_matrix_ledger GROUP BY language, mode, verification_level"
    )
    out: dict[str, dict] = {}
    for row in cur.fetchall():
        lang, mode = row["language"], row["mode"]
        out.setdefault(lang, {}).setdefault(mode, {})[LEVEL_NAMES[row["verification_level"]]] = row["n"]
    return out


def contract_hash(function_contract_json: str | None) -> str | None:
    """A cheap version fingerprint for a contract -- not cryptographic, just
    enough to detect 'the contract changed since this cell was verified.'"""
    if function_contract_json is None:
        return None
    import hashlib
    return hashlib.sha256(function_contract_json.encode("utf-8")).hexdigest()[:16]


def main() -> None:
    """`python scripts/atlascode_ledger.py` prints the current honest summary
    -- no args, read-only, safe to run anytime."""
    con = connect()
    ensure_schema(con)
    s = summary(con)
    print(json.dumps(s, indent=2))
    total = con.execute("SELECT COUNT(*) FROM atlascode_matrix_ledger").fetchone()[0]
    print(f"\ntotal ledger rows: {total}")
    con.close()


if __name__ == "__main__":
    main()
