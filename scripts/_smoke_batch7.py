"""Ad-hoc smoke test for mega_batch7: runs a handful of (problem, language)
pairs on a 6-case subset before committing to the full 40-case x 22-problem
x 7-language run. Not part of the permanent scripts/ pattern -- deleted
after use.
"""
import asyncio
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))
import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.submission.evaluator import evaluate
import scale_program_mode_mega_batch7_remaining18 as batch7

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"

PAIRS = [
    ("palindrome-partition", "python"), ("palindrome-partition", "r"),
    ("palindrome-partitioning", "go"), ("palindrome-subsequence", "kotlin"),
    ("restore-ip-addresses-count", "php"), ("restore-ip-addresses-count", "r"),
    ("longest-repeating-char-replacement", "scala"), ("longest-substring-at-most-k-distinct", "r"),
    ("longest-common-substring", "ruby"), ("minimum-window-substring-length", "r"),
    ("boolean-parenthesization", "python"), ("boolean-parenthesization", "r"),
    ("matrix-chain-multiplication", "r"), ("matrix-chain-multiplication", "go"),
    ("burst-balloons", "r"), ("task-scheduler", "php"),
    ("coin-change", "r"), ("coin-change-ways", "kotlin"),
    ("job-scheduling", "r"), ("job-scheduling", "go"),
    ("meeting-rooms", "r"), ("unbounded-knapsack", "r"),
    ("triangle-minimum-path-sum", "r"), ("triangle-minimum-path-sum", "scala"),
]


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ok, bad = 0, 0
    for pid, lang in PAIRS:
        cur = con.execute(
            "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
            "WHERE problem_id=? ORDER BY \"order\" LIMIT 6", (pid,)
        )
        cases = [batch7.SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                                    is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
        if not cases:
            print(f"[NOCASES] {pid}")
            continue
        prog = batch7.build_program(lang, pid, False)
        res = await evaluate(prog, lang, cases)
        status = "PASS" if res.tests_passed == res.tests_total else "FAIL"
        if status == "FAIL":
            bad += 1
            extra = res.compile_output or ""
            if not extra and res.test_results:
                for tr in res.test_results:
                    if not tr.passed:
                        extra = f"stderr={tr.stderr[:200]} actual={tr.actual_output[:80]!r} expected={tr.expected_output[:80]!r}"
                        break
            print(f"[{status}] {pid}/{lang} {res.tests_passed}/{res.tests_total} {extra[:250]}")
        else:
            ok += 1
            print(f"[{status}] {pid}/{lang} {res.tests_passed}/{res.tests_total}")
    print(f"\nSMOKE TOTAL: ok={ok} bad={bad}")
    con.close()


if __name__ == "__main__":
    asyncio.run(main())
