"""
Backtracking-count family. `palindrome-partition` and `palindrome-partitioning`
are REAL canonical algorithms (both existed, deferred in the dynamic-programming
batch as a near-duplicate pair with no assigned contract) — resolved here by
giving each its own well-known, distinct objective: minimum cuts vs. count of
ways. The other three are `origin_type = PATTERN_PROBLEM`. Every answer is a
COUNT (or a minimum count), never an enumeration of the actual structures —
this is what keeps backtracking problems out of PROPERTY_JUDGE territory.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .backtracking_count_variants_testdata import BACKTRACKING_COUNT_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


@dataclass(frozen=True)
class _Spec:
    algorithm_slug: str | None
    oracle: Callable[..., object]
    cases: list[tuple[str, tuple, bool]]
    statement: str
    constraints: list[str]
    starter_code: str
    title: str
    difficulty: str = "Medium"
    estimated_minutes: int = 25
    format_output: Callable[[object], str] = _fmt_int


_SPECS: dict[str, _Spec] = {
    "palindrome-partition": _Spec(
        algorithm_slug="palindrome-partition",
        oracle=oracles.palindrome_partition_min_cuts,
        cases=[
            ("aab", ("aab",), False), ("a", ("a",), False),
            ("ab", ("ab",), True), ("racecar", ("racecar",), True),
        ],
        statement=(
            "Given a string `s`, partition it so that every substring is a "
            "palindrome. Print the **minimum number of cuts** needed."
        ),
        constraints=["1 ≤ s.length ≤ 2000"],
        starter_code=(
            "import sys\ns = sys.stdin.read().strip()\n\n"
            "def min_cut(s):\n    pass\n\nprint(min_cut(s))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
        title="Palindrome Partitioning II (Minimum Cuts)",
    ),
    "palindrome-partitioning": _Spec(
        algorithm_slug="palindrome-partitioning",
        oracle=oracles.palindrome_partition_count_ways,
        cases=[
            ("aab", ("aab",), False), ("a", ("a",), False),
            ("aaa", ("aaa",), True), ("abc", ("abc",), True),
        ],
        statement=(
            "Given a string `s`, print the **number of ways** to partition it "
            "so that every substring is a palindrome."
        ),
        constraints=["1 ≤ s.length ≤ 16"],
        starter_code=(
            "import sys\ns = sys.stdin.read().strip()\n\n"
            "def count_partitions(s):\n    pass\n\nprint(count_partitions(s))\n"
        ),
        title="Palindrome Partitioning (Count Ways)",
    ),
    "restore-ip-addresses-count": _Spec(
        algorithm_slug=None,
        oracle=oracles.restore_ip_addresses_count,
        cases=[
            ("25525511135", ("25525511135",), False), ("0000", ("0000",), False),
            ("101023", ("101023",), True), ("1111", ("1111",), True),
        ],
        statement=(
            "Given a digit string `s`, print the number of ways to insert 3 dots "
            "to form a **valid IPv4 address** (each segment 0-255, no leading zeros "
            "unless the segment is exactly `0`)."
        ),
        constraints=["4 ≤ s.length ≤ 12"],
        starter_code=(
            "import sys\ns = sys.stdin.read().strip()\n\n"
            "def restore_ip_count(s):\n    pass\n\nprint(restore_ip_count(s))\n"
        ),
        title="Restore IP Addresses (Count)",
    ),
    "word-break-count-ways": _Spec(
        algorithm_slug=None,
        oracle=oracles.word_break_count_ways,
        cases=[
            ("catsanddog\ncats cat and sand dog", ("catsanddog", ["cats", "cat", "and", "sand", "dog"]), False),
            ("leetcode\nleet code", ("leetcode", ["leet", "code"]), False),
            ("a\na", ("a", ["a"]), True),
            ("aaaa\na aa", ("aaaa", ["a", "aa"]), True),
        ],
        statement=(
            "Given a string `s` and a dictionary of words `wordDict` (one line, "
            "space separated), print the number of **distinct ways** to segment "
            "`s` into a space-separated sequence of dictionary words."
        ),
        constraints=["1 ≤ s.length ≤ 20"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "s = lines[0]\nword_dict = lines[1].split()\n\n"
            "def word_break_count(s, word_dict):\n    pass\n\n"
            "print(word_break_count(s, word_dict))\n"
        ),
        difficulty="Hard",
        estimated_minutes=30,
        title="Word Break II (Count Ways)",
    ),
    "unique-permutations-count": _Spec(
        algorithm_slug=None,
        oracle=oracles.unique_permutations_count,
        cases=[
            ("3 1 1 2", ([1, 1, 2],), False), ("3 1 2 3", ([1, 2, 3],), False),
            ("3 1 1 1", ([1, 1, 1],), True), ("4 1 1 2 2", ([1, 1, 2, 2],), True),
        ],
        statement=(
            "Given an array `nums` that may contain duplicates, print the number "
            "of **distinct permutations** of `nums`."
        ),
        constraints=["1 ≤ nums.length ≤ 10"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def count_unique_permutations(nums):\n    pass\n\n"
            "print(count_unique_permutations(nums))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
        title="Distinct Permutations Count",
    ),
}


def build_backtracking_count_variant_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    by_slug = {r.slug: r for r in algorithms}
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue
        reg = by_slug.get(spec.algorithm_slug) if spec.algorithm_slug else None
        if spec.algorithm_slug and reg is None:
            skipped.append((slug, f"linked algorithm '{spec.algorithm_slug}' not found in canonical registry"))
            continue

        test_plan = BACKTRACKING_COUNT_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in backtracking_count_variants_testdata.py"))
            continue
        to_input, format_output, plan_fn = test_plan
        try:
            rng = tg.problem_rng(slug)
            case_plan = plan_fn(rng)
            test_spec = tg.TestSpec(oracle=spec.oracle, to_input=to_input, format_output=format_output)
            test_cases = tg.build_forty(slug, test_spec, case_plan)
        except (oracles.OracleError, tg.TestPlanError) as exc:
            skipped.append((slug, str(exc)))
            continue

        if not test_cases:
            skipped.append((slug, "no test cases produced"))
            continue

        intuition = reg.manifest.get("intuition", "") or reg.manifest.get("description", "") if reg else ""
        problem = {
            "id": slug,
            "title": spec.title,
            "difficulty": spec.difficulty,
            "category": "backtracking",
            "algorithm_slug": spec.algorithm_slug,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": intuition[:300] or "Count via DP on prefixes rather than enumerating every structure."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
