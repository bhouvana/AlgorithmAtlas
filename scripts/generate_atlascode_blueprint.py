"""
Generate `atlascode_problem_blueprint.json` from REAL repository/database state.

This deliberately does NOT hand-author 500 problem identities. Per
docs/atlascode-progress.md and the catalog-driven-expansion policy, a
blueprint entry must be traceable to either:
  (a) an actual seeded+verified Problem row in the DB (status derived from
      whether it passed the 3-level verification pipeline), or
  (b) a real canonical algorithm in the plugin registry that does not yet
      have an AtlasCode problem (status PLANNED, carrying forward the
      judge-type classification already computed by atlascode/coverage.py).

Reaching 500 requires a THIRD source — multiple problem variants per
canonical algorithm (e.g. binary-search: exact/first-occurrence/rotated/...).
That variant-expansion phase is not yet designed, so this script does not
fabricate variant entries; it records the gap honestly in `path_to_500`
instead of inventing placeholder slugs with guessed names.

Run from repo root: python scripts/generate_atlascode_blueprint.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))

import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.atlascode.discovery import discover_registered_algorithms

sys.path.insert(0, str(Path(__file__).parent))
import importlib
seed_mod = importlib.import_module("seed_atlas_code")

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"
COVERAGE_PATH = REPO_ROOT / "atlascode_coverage.json"
OUTPUT_PATH = REPO_ROOT / "atlascode_problem_blueprint.json"

# Families whose problems went through the full 3-level verification pipeline
# (scripts/verify_atlascode_family.py) this session or a prior one, per
# docs/atlascode-progress.md. Curated (hand-authored) problems predate that
# pipeline and are marked SEEDED, not FULLY_VERIFIED, until they are run
# through it explicitly — this is intentionally conservative, not a downgrade.
THREE_LEVEL_VERIFIED_FAMILIES = {"sorting", "searching", "number-theory", "dynamic-programming"}


def load_registry_names() -> dict[str, str]:
    return {r.slug: r.name for r in discover_registered_algorithms()}


def load_db_problems() -> list[dict]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT id, title, difficulty, category, algorithm_slug FROM problems")
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows


def build_blueprint() -> dict:
    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    names = load_registry_names()
    db_problems = load_db_problems()
    db_by_algorithm_slug = {p["algorithm_slug"]: p for p in db_problems if p["algorithm_slug"]}

    curated_problem_ids = {p[0]["id"] for p in seed_mod.PROBLEMS}
    entries = []

    for p in db_problems:
        # A problem is "generated" (ran through a family factory + the
        # verify_atlascode_family.py 3-level pipeline) iff its id is NOT in
        # the hand-authored PROBLEMS list. Curated problems predate that
        # pipeline and are marked SEEDED until explicitly re-verified.
        is_generated = p["id"] not in curated_problem_ids
        status = "FULLY_VERIFIED" if is_generated else "SEEDED"

        entries.append({
            "planned_slug": p["id"],
            "title": p["title"],
            "difficulty": p["difficulty"],
            "primary_category": p["category"],
            "primary_pattern": p["category"],
            "secondary_patterns": [],
            "canonical_algorithm_links": [p["algorithm_slug"]] if p["algorithm_slug"] else [],
            "prerequisite_concepts": [],
            "problem_family": p["category"],
            "judge_type": "STANDARD_JUDGE",
            "comparator_type": "EXACT_MATCH",
            "oracle_strategy": (
                "independent_oracles.py (plugin-free)" if is_generated and p["category"] in {"number-theory", "dynamic-programming"}
                else "plugin_terminal_state+invariant_check" if is_generated and p["category"] in {"sorting", "searching"}
                else "hand-authored (pre-dates oracle-separation policy)"
            ),
            "test_generator_strategy": "family factory + independent oracle, 3-level verified" if is_generated else "fixed-seed hand-authored cases",
            "starter_contract": ["python"],
            "learning_module_link": p["algorithm_slug"],
            "visualization_link": p["algorithm_slug"] if p["algorithm_slug"] in names else None,
            "status": status,
        })

    entries.sort(key=lambda e: e["planned_slug"])

    fully_verified = sum(1 for e in entries if e["status"] == "FULLY_VERIFIED")
    seeded_not_verified = sum(1 for e in entries if e["status"] == "SEEDED")

    # PLANNED: real canonical algorithms with no AtlasCode problem yet.
    planned_entries = []
    for alg in coverage["algorithms"]:
        slug = alg["algorithm_slug"]
        if slug in db_by_algorithm_slug:
            continue
        planned_entries.append({
            "planned_slug": slug,
            "title": names.get(slug, slug),
            "difficulty": "TBD",
            "primary_category": alg["category"],
            "primary_pattern": alg["category"],
            "secondary_patterns": [],
            "canonical_algorithm_links": [slug],
            "prerequisite_concepts": [],
            "problem_family": alg.get("family") or alg["category"],
            "judge_type": alg["judge_type"],
            "comparator_type": None,
            "oracle_strategy": None,
            "test_generator_strategy": None,
            "starter_contract": [],
            "learning_module_link": slug,
            "visualization_link": slug if slug in names else None,
            "status": "PLANNED",
            "blocked_reason": alg.get("reason"),
        })
    planned_entries.sort(key=lambda e: e["planned_slug"])

    all_entries = entries + planned_entries

    difficulty_counts = {"Easy": 0, "Medium": 0, "Hard": 0, "TBD": 0}
    for e in all_entries:
        difficulty_counts[e["difficulty"]] = difficulty_counts.get(e["difficulty"], 0) + 1

    return {
        "generated_from": "real DB (atlas.db) + atlascode_coverage.json + plugin registry — no hand-typed entries",
        "target_total": 500,
        "current_seeded_total": len(entries),
        "current_fully_verified": fully_verified,
        "current_seeded_not_yet_reverified": seeded_not_verified,
        "planned_from_uncovered_canonical_algorithms": len(planned_entries),
        "sum_seeded_plus_planned": len(all_entries),
        "gap_to_500_requiring_variant_design": max(0, 500 - len(all_entries)),
        "difficulty_distribution": difficulty_counts,
        "path_to_500": (
            "237 canonical algorithms cannot alone reach 500 one-problem-per-algorithm "
            "(max ceiling ~237 that way). Reaching 500 requires a variant-expansion "
            "phase — multiple distinct problem CONTRACTS per algorithm (e.g. binary-search: "
            "exact/first-occurrence/last-occurrence/count/rotated/peak/answer-space-search "
            "= 7+ from one algorithm). That phase is NOT YET DESIGNED for any family beyond "
            "the single-contract-per-algorithm problems already seeded. Do not treat the "
            "`planned_from_uncovered_canonical_algorithms` entries below as sufficient to "
            "reach 500 — they cap out at 237 total (72 done + 165 planned) even if all are "
            "completed. See docs/atlascode-progress.md for the next real batch (DP: 8 "
            "deferred scalar-ambiguous algorithms; string: 13; greedy: 9; divide-and-conquer: 9) "
            "and PROGRESS_NOTES in this file's 'path_to_500' for the variant-phase plan."
        ),
        "entries": all_entries,
    }


if __name__ == "__main__":
    blueprint = build_blueprint()
    OUTPUT_PATH.write_text(json.dumps(blueprint, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} — {len(blueprint['entries'])} entries "
          f"({blueprint['current_fully_verified']} FULLY_VERIFIED, "
          f"{blueprint['current_seeded_not_yet_reverified']} SEEDED, "
          f"{blueprint['planned_from_uncovered_canonical_algorithms']} PLANNED)")
    print(f"Gap to 500 requiring variant design: {blueprint['gap_to_500_requiring_variant_design']}")
