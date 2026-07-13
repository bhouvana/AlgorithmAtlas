"""Export `problems` + `test_cases` to a compressed, committable snapshot --
apps/backend/algorithm_atlas/atlascode/problems_snapshot.json.gz.

Why this exists: regenerating all 216 problems' test data via
assemble_catalog() (see seed.py) is real, CPU/memory-heavy work -- dozens
of family builders doing brute-force adversarial test generation,
dedup-checking, and independent-oracle verification. That's appropriate
for a dev machine building NEW problems, but it's fatal on a
memory-constrained deploy target: confirmed on Render's free tier (512MB),
the boot-time auto-seed OOM-killed the container every single time before
finishing, in an infinite crash-loop (no persistent disk means every
restart starts from an empty DB and tries again, forever).

This snapshot sidesteps the generation step entirely for a fresh boot --
loading pre-built rows via bulk INSERT is orders of magnitude cheaper than
recomputing them. Uncompressed this is ~220MB (8612 test cases, some with
large "stress"-bucket inputs); gzip -9 brings it to ~75MB, which is under
GitHub's 100MB hard limit. Still large -- re-run this and re-commit only
when problem/test-case data actually changes (new problems, corpus
fixes), not for unrelated commits.

Usage: python scripts/export_problems_snapshot.py
"""
from __future__ import annotations

import gzip
import json
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"
OUT_PATH = REPO_ROOT / "apps" / "backend" / "algorithm_atlas" / "atlascode" / "problems_snapshot.json.gz"


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    problems = con.execute("SELECT * FROM problems").fetchall()
    test_cases = con.execute("SELECT * FROM test_cases").fetchall()
    con.close()

    if not problems:
        raise SystemExit("atlas.db has zero problems -- refusing to export an empty snapshot")

    p_cols = list(problems[0].keys())
    tc_cols = list(test_cases[0].keys())

    data = {
        "generated_from": "scripts/export_problems_snapshot.py (live atlas.db, no hand-typed rows)",
        "problems_count": len(problems),
        "test_cases_count": len(test_cases),
        # Columnar (column names once + plain value-list rows) instead of
        # list-of-dicts -- measured negligible size difference after gzip,
        # but keeps the raw (uncompressed, in-memory-at-load-time) form
        # smaller, which matters more than compressed size for a
        # memory-constrained boot.
        "problems_columns": p_cols,
        "problems_rows": [[r[c] for c in p_cols] for r in problems],
        "test_cases_columns": tc_cols,
        "test_cases_rows": [[r[c] for c in tc_cols] for r in test_cases],
    }

    raw = json.dumps(data, default=str, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=9)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(compressed)
    print(
        f"Exported {len(problems)} problems / {len(test_cases)} test cases to {OUT_PATH}\n"
        f"  raw: {len(raw):,} bytes ({len(raw) / 1024 / 1024:.1f} MB)\n"
        f"  gzip: {len(compressed):,} bytes ({len(compressed) / 1024 / 1024:.1f} MB)"
    )


if __name__ == "__main__":
    main()
