"""
Migrate the 19 LEGACY curated AtlasCode problems to the exactly-40-test
standard, using the independent oracles + case plans already built in
`algorithm_atlas.atlascode.families.legacy_audit_testdata` (LEGACY_PLANS).

Deliberately does NOT call `seed_atlas_code.assemble_catalog()` — that
rebuilds every generated family's full 40-test data (~150+ problems with
randomized/adversarial search) purely to obtain the small, static
`curated_algorithm_to_problem` mapping this script actually needs. That
mapping is just a dict comprehension over `seed_atlas_code.PROBLEMS` (the
hand-authored curated list), so it's reproduced directly here instead —
keeps this migration fast and independent of the rest of the catalog.

LEGACY_PLANS is keyed by ALGORITHM SLUG (e.g. "bfs", "dijkstra", "kmp",
"min-path-sum"), which for 4 of the 19 problems differs from the actual
DB `Problem.id` (e.g. "graph-bfs", "dijkstra-shortest-path",
"kmp-string-matching", "minimum-path-sum") — resolved via
curated_algorithm_to_problem before touching TestCase rows.

Usage:
    python scripts/migrate_legacy_audit_to_forty.py --dry-run
    python scripts/migrate_legacy_audit_to_forty.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))

import loguru
loguru.logger.remove()
loguru.logger.disable("algorithm_atlas")
import logging
logging.disable(logging.CRITICAL + 10)

from sqlalchemy import delete, select

from algorithm_atlas.database import AsyncSessionLocal, init_db
from algorithm_atlas.models.atlas_code import Problem, TestCase
from algorithm_atlas.atlascode import testgen as tg
from algorithm_atlas.atlascode.families.legacy_audit_testdata import (
    LEGACY_PLANS, N_QUEENS_REDUCED_CASES, _to_input_nqueens,
)
from algorithm_atlas.atlascode.families import legacy_audit_oracles as oracles_mod

import seed_atlas_code as seed_mod

# n-queens is a documented, deliberate exception to the 40-unique-test
# standard (see N_QUEENS_REDUCED_CASES's docstring in legacy_audit_testdata.py):
# its single-integer domain (1<=n<=14) only has 14 possible distinct values.
# Ships all 14 achievable uniques instead of 40.
_ALL_LEGACY_SLUGS = sorted(set(LEGACY_PLANS) | {"n-queens"})


async def main(dry_run: bool = False) -> int:
    curated_algorithm_to_problem = {
        p[0]["algorithm_slug"]: p[0]["id"] for p in seed_mod.PROBLEMS if p[0].get("algorithm_slug")
    }

    manifest = tg.load_manifest()
    await init_db()
    updated = 0
    failed: list[tuple[str, str]] = []

    async with AsyncSessionLocal() as db:
        for algo_slug in _ALL_LEGACY_SLUGS:
            problem_id = curated_algorithm_to_problem.get(algo_slug, algo_slug)

            existing = await db.execute(select(Problem).where(Problem.id == problem_id))
            if existing.scalar_one_or_none() is None:
                failed.append((algo_slug, f"no Problem row for resolved id '{problem_id}'"))
                continue

            try:
                if algo_slug == "n-queens":
                    rows = [
                        {
                            "input_data": _to_input_nqueens(n),
                            "expected_output": str(oracles_mod.n_queens_count(n)),
                            "is_hidden": hidden,
                            "explanation": "",
                            "order": i,
                        }
                        for i, (n, hidden) in enumerate(N_QUEENS_REDUCED_CASES)
                    ]
                else:
                    to_input, format_output, oracle, plan_fn = LEGACY_PLANS[algo_slug]
                    rng = tg.problem_rng(problem_id)
                    case_plan = plan_fn(rng)
                    spec = tg.TestSpec(oracle=oracle, to_input=to_input, format_output=format_output)
                    rows = tg.build_forty(problem_id, spec, case_plan)
            except tg.TestPlanError as exc:
                failed.append((algo_slug, str(exc)))
                continue

            existing_count = len((await db.execute(
                select(TestCase.id).where(TestCase.problem_id == problem_id)
            )).all())

            if dry_run:
                print(f"  [dry-run] {algo_slug} -> {problem_id}: {existing_count} -> {len(rows)}")
                continue

            await db.execute(delete(TestCase).where(TestCase.problem_id == problem_id))
            for row in rows:
                db.add(TestCase(problem_id=problem_id, **row))
            manifest[problem_id] = tg.manifest_entries_for(problem_id, rows)
            updated += 1
            visible = sum(1 for r in rows if not r["is_hidden"])
            print(f"  migrated {algo_slug} -> {problem_id}: {existing_count} -> {len(rows)} ({visible} visible)")

        if not dry_run and updated:
            await db.commit()
            tg.write_manifest(manifest)

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Migrated: {updated}/{len(_ALL_LEGACY_SLUGS)}, Failed: {len(failed)}")
    if failed:
        print("Failures:")
        for slug, reason in failed:
            print(f"  {slug}: {reason}")
    return 1 if failed else 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    code = asyncio.run(main(dry_run=dry_run))
    print("Done.")
    sys.exit(code)
