"""
Audit every ACTIVE AtlasCode problem in the live database against the
exactly-40-test standard (docs/atlascode-40-test-standard.md).

Unlike the family-factory dry-run checks, this reads the REAL committed DB
state — it's the source of truth for "is the 40-test migration actually
done", not just "does the generator code produce 40 when re-run".

Usage:
    python scripts/audit_atlascode_test_counts.py

Exit code is non-zero if any active problem violates the 40-test rule.
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))

import logging
logging.disable(logging.CRITICAL)

from sqlalchemy import func, select

from algorithm_atlas.database import AsyncSessionLocal, init_db
from algorithm_atlas.models.atlas_code import Problem, TestCase

_WS_RE = re.compile(r"\s+")


def _dedup_key(s: str) -> str:
    return _WS_RE.sub(" ", s.strip())


async def main() -> int:
    await init_db()
    async with AsyncSessionLocal() as db:
        problem_ids = [pid for (pid,) in (await db.execute(select(Problem.id))).all()]
        active = len(problem_ids)

        exactly_40 = 0
        below_40 = 0
        above_40 = 0
        missing_visible = 0
        missing_hidden = 0
        duplicate_input_problems = 0
        below_list: list[tuple[str, int]] = []
        above_list: list[tuple[str, int]] = []

        for pid in problem_ids:
            rows = (await db.execute(
                select(TestCase.input_data, TestCase.is_hidden).where(TestCase.problem_id == pid)
            )).all()
            n = len(rows)
            if n == 40:
                exactly_40 += 1
            elif n < 40:
                below_40 += 1
                below_list.append((pid, n))
            else:
                above_40 += 1
                above_list.append((pid, n))

            if not any(not hidden for _, hidden in rows):
                missing_visible += 1
            if not any(hidden for _, hidden in rows):
                missing_hidden += 1

            keys = [_dedup_key(inp) for inp, _ in rows]
            if len(keys) != len(set(keys)):
                duplicate_input_problems += 1

    print("=" * 50)
    print("ATLASCODE TEST COUNT AUDIT")
    print("=" * 50)
    print(f"Active problems: {active}")
    print()
    print(f"Exactly 40 tests: {exactly_40}")
    print(f"Below 40: {below_40}")
    print(f"Above 40: {above_40}")
    print()
    print(f"Problems with duplicate test inputs: {duplicate_input_problems}")
    print(f"Missing visible tests: {missing_visible}")
    print(f"Missing hidden tests: {missing_hidden}")
    print("=" * 50)

    if below_list:
        print(f"\nBelow 40 ({len(below_list)}):")
        for pid, n in sorted(below_list, key=lambda x: x[1]):
            print(f"  {pid}: {n}")
    if above_list:
        print(f"\nAbove 40 ({len(above_list)}):")
        for pid, n in sorted(above_list, key=lambda x: -x[1]):
            print(f"  {pid}: {n}")

    violations = below_40 + above_40 + duplicate_input_problems + missing_visible + missing_hidden
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
