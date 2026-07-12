"""Stale-evidence invalidation sweep (mission Phase 2).

The ledger (`atlascode_matrix_ledger`) stores contract_version/test_suite_version/
toolchain_version at verification time, but nothing had ever cross-checked
those recorded values against CURRENT live state. This script is that check.
It never mutates the ledger's historical `pass` rows (the mission's own
`record_cell` docstring says the ledger records current truth via upsert, and
overwriting a real historical pass with an inferred "stale" status would
destroy evidence of what actually happened at verification time) -- instead
it produces a side report layering current-truth staleness on top of the raw
ledger, which is what every report generator (Phase 38) should read instead
of trusting `status=pass` blindly.

Two independent staleness checks, both grounded in a live re-probe, never
inferred:
  1. CONTRACT_CHANGED -- the problem's function_contract in the DB right now
     hashes differently than what was recorded at verification time.
  2. TOOLCHAIN_UNAVAILABLE_NOW -- the language's toolchain does not resolve
     in THIS process's environment right now (via the same shutil.which-based
     probe as discover_toolchains.py), even though the row was recorded pass.
     Python/JavaScript/TypeScript/etc are still checked (not just the 7
     recently-installed ones) since environments can regress for any language.

A row that is CURRENT means: neither check fired. A row can have both
problems simultaneously; both are reported.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"

import atlascode_ledger as ledger
import discover_toolchains as tc

# Ledger language name -> discover_toolchains.py language key (identical in
# every case currently, but kept as an explicit map rather than assumed
# identity, since "cpp" vs "c++" naming drift is exactly the kind of thing
# that silently breaks a cross-check like this).
_LANG_MAP = {
    "python": "python", "javascript": "javascript", "typescript": "typescript",
    "java": "java", "cpp": "cpp", "c": "c", "rust": "rust", "go": "go",
    "csharp": "csharp", "perl": "perl", "ruby": "ruby", "php": "php",
    "r": "r", "kotlin": "kotlin", "scala": "scala", "swift": "swift",
    "shell": "shell",
}


def main() -> int:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)

    toolchain_report = tc.discover()
    available_now = {lang: r["available"] for lang, r in toolchain_report.items()}

    cur = con.execute(
        "SELECT id, problem_id, language, mode, contract_version, toolchain_version, status, verification_level "
        "FROM atlascode_matrix_ledger WHERE verification_level = 6"
    )
    rows = cur.fetchall()

    contract_cache: dict[str, str | None] = {}

    def current_contract_hash(pid: str) -> str | None:
        if pid not in contract_cache:
            r = con.execute("SELECT function_contract FROM problems WHERE id=?", (pid,)).fetchone()
            contract_cache[pid] = ledger.contract_hash(r["function_contract"]) if r else None
        return contract_cache[pid]

    results = {"current": [], "stale": []}
    per_language: dict[str, dict[str, int]] = {}

    for row in rows:
        pid, lang, mode = row["problem_id"], row["language"], row["mode"]
        problems_found = []

        live_hash = current_contract_hash(pid)
        if row["contract_version"] is not None and live_hash is not None and live_hash != row["contract_version"]:
            problems_found.append("CONTRACT_CHANGED")

        tc_lang = _LANG_MAP.get(lang)
        if tc_lang is not None and not available_now.get(tc_lang, False):
            problems_found.append("TOOLCHAIN_UNAVAILABLE_NOW")

        entry = {"id": row["id"], "problem_id": pid, "language": lang, "mode": mode}
        bucket = per_language.setdefault(lang, {"current": 0, "stale": 0})
        if problems_found:
            entry["reasons"] = problems_found
            results["stale"].append(entry)
            bucket["stale"] += 1
        else:
            results["current"].append(entry)
            bucket["current"] += 1

    print("LEDGER STALENESS SWEEP (Level-6 rows only)")
    print(f"  total Level-6 rows checked: {len(rows)}")
    print(f"  CURRENT (reproducible right now): {len(results['current'])}")
    print(f"  STALE (evidence real, but not reproducible in THIS environment right now): {len(results['stale'])}")
    print()
    for lang in sorted(per_language):
        b = per_language[lang]
        print(f"  {lang:12s} current={b['current']:3d}  stale={b['stale']:3d}")

    stale_by_reason: dict[str, int] = {}
    for e in results["stale"]:
        for r in e["reasons"]:
            stale_by_reason[r] = stale_by_reason.get(r, 0) + 1
    print("\nStale reasons:")
    for reason, n in stale_by_reason.items():
        print(f"  {reason}: {n}")

    out = {
        "summary": {
            "total_level6_checked": len(rows),
            "current": len(results["current"]),
            "stale": len(results["stale"]),
            "stale_by_reason": stale_by_reason,
            "per_language": per_language,
        },
        "stale_rows": results["stale"],
    }
    out_path = REPO_ROOT / "docs" / "atlascode-ledger-staleness.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nReport written: {out_path}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
