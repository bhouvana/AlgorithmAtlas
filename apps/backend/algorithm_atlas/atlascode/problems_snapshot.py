"""Loads the committed problems+test_cases snapshot (problems_snapshot.db.gz,
alongside this file) into the live database via SQLite's own ATTACH DATABASE
bulk copy.

Why SQLite-to-SQLite instead of JSON: an earlier version of this snapshot
shipped as gzip-compressed JSON, decompressed and json.loads()'d in one shot.
That materializes ~220MB of raw JSON text into hundreds of thousands of
Python dict/list/str objects all at once -- confirmed via Render's dashboard
to STILL OOM-kill the free-tier 512MB container even though the actual DB
insert only took ~3 seconds locally once run; the memory spike was in Python
object construction during json.loads(), not the insert itself. Copying
table-to-table with SQLite's own ATTACH DATABASE + INSERT...SELECT does the
row copy entirely inside the C library's page cache -- no Python object
materialization of row data at all, and the gzip decompression is streamed
in fixed-size chunks rather than one giant in-memory blob.

Why `problems` and `test_cases` are loaded on two entirely different
schedules: measured directly against the committed snapshot, the `problems`
table (216 rows: title, difficulty, category, acceptance_rate, starter code,
etc. -- everything the catalog list/detail views read) is ~1.2MB. `test_cases`
(8,612 rows of adversarial stress-test input/expected/function_args data) is
~225MB -- almost the entire snapshot. The catalog list endpoint never reads
test_cases at all, and the detail/run/submit endpoints only ever need ONE
problem's cases at a time. Bulk-copying all 225MB of test_cases on every cold
boot (as this module used to) is what was blowing Render's 512MB budget on
every restart, in a container with no persistent disk. So:
  - `load_problems_snapshot()` runs once at boot -- ~1.2MB, effectively free.
  - `load_test_cases_for_problem()` runs lazily, the first time a specific
    problem's detail/run/submit endpoint is hit -- scoped to that one
    problem_id, so a user who never opens problem X never pays for it.

Runs on a worker thread via run_in_executor: sqlite3 (the stdlib sync
driver) is used directly against the live db file rather than going through
the app's async SQLAlchemy/aiosqlite engine, both to avoid SQLite's
restriction on ATTACH inside an already-open transaction (SQLAlchemy's
engine.begin()/session.execute() always starts one) and to keep this CPU/IO-
bound work off the event loop -- same reasoning as assemble_catalog() in
seed.py. Callers in problems.py/submissions.py must invoke
`ensure_test_cases_loaded()` BEFORE their request's first `db.execute()` --
see that function's docstring for why.
"""
from __future__ import annotations

import asyncio
import gzip
import os
import shutil
import sqlite3
from pathlib import Path

SNAPSHOT_PATH = Path(__file__).parent / "problems_snapshot.db.gz"

# SQLite busy-wait before giving up on a lock held by another connection
# (the async engine's aiosqlite connections, or another lazy-load in
# flight). Generous because these are short, infrequent writes, not a hot
# path -- see database.py's matching engine-side timeout + WAL mode, which
# together are what make a sync writer and the app's async readers safe to
# hit the same file concurrently.
_BUSY_TIMEOUT_S = 30


def _decompressed_snapshot_path(db_path: Path) -> Path:
    """Where the one-time-decompressed snapshot is cached for this process's
    lifetime, next to the live DB. ATTACHing this file for a per-problem
    copy is paged by SQLite's C-level I/O, not materialized into Python
    objects, so keeping it around across many lazy loads costs disk, not
    RAM -- it just saves re-running gzip decompression (~1-3s) on every
    distinct problem's first open."""
    return db_path.parent / f".problems_snapshot_decompressed_{os.getpid()}.db"


def _ensure_decompressed(db_path: Path) -> Path | None:
    """Decompresses SNAPSHOT_PATH to the cached path on first call; a no-op
    on every later call in this process. Returns None if the snapshot isn't
    committed in this checkout. Writes via a .tmp + atomic rename so a
    process crash mid-decompression can never leave a corrupt file that a
    later call would mistake for a valid cache."""
    if not SNAPSHOT_PATH.exists():
        return None
    target = _decompressed_snapshot_path(db_path)
    if target.exists():
        return target
    tmp_path = target.with_suffix(".tmp")
    # Streamed in fixed-size chunks -- bounded memory regardless of the
    # decompressed size (~230MB), unlike a single gzip.decompress() call.
    with gzip.open(SNAPSHOT_PATH, "rb") as f_in, open(tmp_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out, length=1024 * 1024)
    os.replace(tmp_path, target)
    return target


def _load_problems_sync(db_path: Path) -> int:
    """Runs on a worker thread. Copies ONLY the `problems` table from the
    snapshot into the live DB -- see module docstring for why test_cases is
    excluded here. Returns the number of problems inserted (0 if the
    snapshot is missing, or every problem already exists)."""
    snap_path = _ensure_decompressed(db_path)
    if snap_path is None:
        return 0

    con = sqlite3.connect(str(db_path), timeout=_BUSY_TIMEOUT_S)
    try:
        con.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_S * 1000}")
        before = con.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
        con.execute("ATTACH DATABASE ? AS snap", (str(snap_path),))
        try:
            # Explicit, name-matched column lists (not `SELECT *`, which
            # matches by position) -- robust if the live schema has since
            # gained columns the snapshot predates (they're just left
            # NULL/default); a genuinely removed column is a real error,
            # same as it would be for any stale snapshot.
            p_cols = [r[1] for r in con.execute("PRAGMA snap.table_info(problems)").fetchall()]
            p_col_list = ", ".join(f'"{c}"' for c in p_cols)
            con.execute(
                f'INSERT OR IGNORE INTO problems ({p_col_list}) '
                f'SELECT {p_col_list} FROM snap.problems'
            )
            con.commit()
        finally:
            con.execute("DETACH DATABASE snap")
        after = con.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
    finally:
        con.close()
    return after - before


def _load_test_cases_sync(db_path: Path, problem_id: str) -> int:
    """Runs on a worker thread. Lazily copies ONE problem's test_cases
    (visible + hidden, Program and Function Mode representations alike) from
    the snapshot into the live DB. A no-op if that problem's cases are
    already present -- checked here (not just by the caller) so two
    concurrent first-requests for the same never-yet-opened problem can't
    race into a double copy. Returns the number of test_case rows inserted."""
    con = sqlite3.connect(str(db_path), timeout=_BUSY_TIMEOUT_S)
    try:
        con.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_S * 1000}")
        already_loaded = con.execute(
            "SELECT COUNT(*) FROM test_cases WHERE problem_id = ?", (problem_id,)
        ).fetchone()[0]
        if already_loaded > 0:
            return 0

        snap_path = _ensure_decompressed(db_path)
        if snap_path is None:
            return 0

        before = con.execute("SELECT COUNT(*) FROM test_cases").fetchone()[0]
        con.execute("ATTACH DATABASE ? AS snap", (str(snap_path),))
        try:
            tc_cols = [r[1] for r in con.execute("PRAGMA snap.table_info(test_cases)").fetchall()]
            tc_col_list = ", ".join(f'"{c}"' for c in tc_cols)
            con.execute(
                f'INSERT OR IGNORE INTO test_cases ({tc_col_list}) '
                f'SELECT {tc_col_list} FROM snap.test_cases WHERE problem_id = ?',
                (problem_id,),
            )
            con.commit()
        finally:
            con.execute("DETACH DATABASE snap")
        after = con.execute("SELECT COUNT(*) FROM test_cases").fetchone()[0]
    finally:
        con.close()
    return after - before


async def load_problems_snapshot(db_path: Path) -> int:
    """Boot-time fast path: `problems` table only (~1.2MB for 216 rows).
    See _load_problems_sync and the module docstring."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _load_problems_sync, db_path)


async def load_test_cases_for_problem(db_path: Path, problem_id: str) -> int:
    """Request-time: one problem's test_cases, lazily, on first access to
    that problem's detail/run/submit endpoint. See _load_test_cases_sync."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _load_test_cases_sync, db_path, problem_id)


async def ensure_test_cases_loaded(problem_id: str) -> None:
    """Call as the FIRST thing in any endpoint that queries TestCase rows for
    a specific problem (detail/run/submit) -- before that request's
    AsyncSession has issued its own first db.execute(). SQLAlchemy's asyncio
    session only opens an actual DB transaction on first use ("autobegin"),
    so calling this before that point means the sync writer connection used
    here never contends with an already-open transaction on the same
    request's session (see database.py's WAL mode + busy_timeout for the
    remaining, expected case: a *different* concurrent request's session
    holding a lock at the same moment).

    A no-op for a non-sqlite DATABASE_URL (e.g. Postgres in production) or
    when the snapshot isn't committed in this checkout -- both cases mean
    the live DB was already fully populated by the slow-path full
    generation at boot (see main.py's _auto_seed_atlascode_if_empty), so
    there is nothing left to lazily fetch.
    """
    from ..config import get_settings

    db_path = get_settings().resolved_sqlite_path()
    if db_path is None:
        return
    await load_test_cases_for_problem(db_path, problem_id)
