"""Mission Phase 23: the honest final matrix report, read from real sources
only -- the persistent ledger (scripts/atlascode_ledger.py), the canonical
DB, and the toolchain probe. Never hand-typed counts. Supersedes the older
scripts/generate_final_matrix_report.py (which predates the ledger and has
several hardcoded/stale numbers from earlier sessions -- kept as a historical
artifact, not deleted, but no longer the source of truth).

SUPERSEDED (2026-07-12): `scripts/generate_honest_matrix_report.py` is now
the actual source of truth for `docs/atlascode-complete-matrix.json/.md` --
it additionally accounts for the shell/function-mode architectural exclusion
and also refreshes the .md report, which this script does not. Prefer that
script; this one is kept side-by-side (not deleted) but running it will NOT
update the .md file, leaving it stale relative to the .json it overwrites.

Usage: python scripts/generate_complete_matrix_report.py
Writes docs/atlascode-complete-matrix.json and prints a human summary.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
import atlascode_ledger as L

DB_PATH = REPO_ROOT / "atlas.db"
ALL_LANGUAGES = [
    "python", "javascript", "typescript", "cpp", "c", "java", "go", "rust",
    "shell", "ruby", "kotlin", "swift", "r", "csharp", "php", "scala", "perl",
]


def load_json(name: str) -> dict:
    p = REPO_ROOT / "docs" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM problems")
    problems_total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM problems WHERE function_contract IS NOT NULL")
    contracts_total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT problem_id) FROM test_cases WHERE function_args IS NOT NULL")
    typed_corpora_total = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM (SELECT problem_id, COUNT(*) c FROM test_cases "
        "WHERE function_args IS NOT NULL GROUP BY problem_id HAVING c = 40)"
    )
    exact_40_total = cur.fetchone()[0]

    toolchains = load_json("atlascode-toolchain-report.json")
    quarantine = load_json("atlascode-quarantine.json")

    sys.path.insert(0, str(REPO_ROOT / "apps" / "backend"))
    import logging
    logging.disable(logging.CRITICAL)
    from algorithm_atlas.atlascode.function_mode.registry import supported_languages
    adapters_implemented = set(supported_languages())

    ledger_con = L.connect()
    L.ensure_schema(ledger_con)
    ledger_summary = L.summary(ledger_con)

    # Full target matrix, per the mission spec: problems x languages x TWO
    # execution modes (Function Mode + Program Mode) = 216 x 17 x 2 = 7344.
    # A prior run of scripts/generate_dual_mode_coverage.py printed
    # "Target combos: 3672" -- that is problems x languages for ONE mode
    # only, an undercount of the real target by exactly half. Flagged here,
    # not silently carried forward.
    modes = ("function", "program")
    full_target_cells = problems_total * len(ALL_LANGUAGES) * len(modes)

    per_language: dict[str, dict] = {}
    total_function_verified = 0
    total_program_verified = 0
    for lang in ALL_LANGUAGES:
        toolchain_info = toolchains.get(lang, {})
        toolchain_available = bool(toolchain_info.get("available"))
        function_adapter_exists = lang in adapters_implemented
        function_levels = ledger_summary.get(lang, {}).get("function", {})
        program_levels = ledger_summary.get(lang, {}).get("program", {})
        function_verified = function_levels.get("verified", 0)
        program_verified = program_levels.get("verified", 0)
        total_function_verified += function_verified
        total_program_verified += program_verified
        per_language[lang] = {
            "toolchain_available": toolchain_available,
            "function_adapter_exists": function_adapter_exists,
            "function_level6_verified_cells": function_verified,
            "function_verification_level_breakdown": function_levels,
            "program_level6_verified_cells": program_verified,
            "program_verification_level_breakdown": program_levels,
            "status": (
                "TOOLCHAIN_UNAVAILABLE" if not toolchain_available
                else "adapter_implemented" if function_adapter_exists
                else "adapter_not_implemented"
            ),
        }

    problems_complete = ledger_con.execute(
        "SELECT COUNT(DISTINCT problem_id) FROM atlascode_matrix_ledger WHERE verification_level=6"
    ).fetchone()[0]
    problems_in_progress = problems_total - problems_complete

    report = {
        "generated_from": "scripts/generate_complete_matrix_report.py (ledger + DB + toolchain probe, no hand-typed counts)",
        "completion_model": {
            "philosophy": (
                "Completion is measured at the PROBLEM level. A problem is COMPLETE "
                "once its algorithm is implemented, the judge can execute it, and at "
                "least one production-quality language implementation is verified "
                "(Level 6) -- additional languages are Language Coverage, an ongoing "
                "enhancement, never a completion blocker."
            ),
            "problems_total": problems_total,
            "problems_complete": problems_complete,
            "problems_in_progress": problems_in_progress,
            "problem_completion_pct": round(problems_complete / problems_total, 4) if problems_total else 0.0,
        },
        "problems_total": problems_total,
        "contracts_total": contracts_total,
        "typed_corpora_total": typed_corpora_total,
        "exact_40_total": exact_40_total,
        "known_corpus_exceptions": {
            "n-queens": "domain-capped at 12/40 by design -- only 12 distinct valid n values are both in-constraint (1<=n<=12) and computable within a safe time budget with a correctness-verified oracle; forcing 40 would require duplicate cases, which the mission explicitly forbids. See docs/atlascode-quarantine.json history / family source comment in legacy_audit_testdata.py.",
        },
        "quarantined_problems": quarantine,
        "languages_total": len(ALL_LANGUAGES),
        "modes": list(modes),
        "full_target_cells": full_target_cells,
        "total_function_level6_verified_cells": total_function_verified,
        "total_program_level6_verified_cells": total_program_verified,
        "total_level6_verified_cells": total_function_verified + total_program_verified,
        "languages": per_language,
        "ledger_total_rows": ledger_con.execute("SELECT COUNT(*) FROM atlascode_matrix_ledger").fetchone()[0],
    }

    out_path = REPO_ROOT / "docs" / "atlascode-complete-matrix.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=" * 70)
    print("ATLASCODE COMPLETE MATRIX REPORT (ledger-backed, honest)")
    print("=" * 70)
    print(f"Problems Completed (headline): {problems_complete}/{problems_total} "
          f"({problems_complete/problems_total:.1%})   In Progress: {problems_in_progress}")
    print(f"Problems: {problems_total}/216   Contracts: {contracts_total}/216   "
          f"Typed corpora: {typed_corpora_total}/216   Exactly-40: {exact_40_total}/216")
    print(f"Quarantined: {list(quarantine.keys())}")
    print(f"\nFull target matrix: {problems_total} problems x {len(ALL_LANGUAGES)} languages x "
          f"{len(modes)} modes = {full_target_cells} cells")
    print()
    for lang, info in per_language.items():
        print(f"  {lang:12s} toolchain={'OK' if info['toolchain_available'] else 'MISSING':7s} "
              f"adapter={'yes' if info['function_adapter_exists'] else 'no ':3s} "
              f"function_verified={info['function_level6_verified_cells']:<4d} "
              f"program_verified={info['program_level6_verified_cells']}")
    print(f"\nTotal Level-6-verified cells: {report['total_level6_verified_cells']} / {full_target_cells}")
    print(f"Ledger rows total: {report['ledger_total_rows']}")
    print(f"\nWrote {out_path}")
    con.close()
    ledger_con.close()


if __name__ == "__main__":
    main()
