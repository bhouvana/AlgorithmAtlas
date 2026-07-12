"""
Binary-search variant family factory.

This is the first "variant" family (as opposed to sorting/searching/number-
theory/dynamic-programming, which each map AT MOST ONE problem per canonical
algorithm). Reaching the user's 500-problem target requires MULTIPLE distinct
problem CONTRACTS per underlying technique — see docs/atlascode-progress.md
"variant-expansion phase". A single canonical algorithm (`binary-search`) here
backs 9 genuinely different objectives (boundary-finding, counting,
insertion-position, search-on-answer, grid search, rotated-array search);
`rotated-binary-search` is real, previously-uncovered canonical-algorithm
coverage in its own right.

Dedup here is by the NEW problem's own slug against ALL existing problem ids
(curated + already-generated), NOT by algorithm_slug — multiple problems are
expected to legitimately share one algorithm_slug (e.g. many share
"binary-search"), which is different from every other family factory so far.

`bitonic-peak-index` is deliberately NOT linked to the canonical
`peak-element` algorithm's slug: that algorithm's real contract (find *a*
peak in an arbitrary array) is not unique-answer in general (multiple valid
peaks can exist) and needs a property validator, not built yet. This problem
instead promises a strictly bitonic (increase-then-decrease) input, which
makes the peak index provably unique — so it's filed as a `binary-search`
variant, not as canonical `peak-element` coverage, to avoid overclaiming.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .binary_search_variants_testdata import BINARY_SEARCH_VARIANT_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_bool(answer: object) -> str:
    return "true" if answer else "false"


@dataclass(frozen=True)
class _Spec:
    algorithm_slug: str          # canonical algorithm this links to (for learning/viz)
    oracle: Callable[..., object]
    cases: list[tuple[str, tuple, bool]]   # (input_data, oracle_args, is_hidden)
    statement: str
    constraints: list[str]
    starter_code: str
    difficulty: str = "Medium"
    estimated_minutes: int = 25
    format_output: Callable[[object], str] = _fmt_int
    title: str = ""


_SPECS: dict[str, _Spec] = {
    "rotated-binary-search": _Spec(
        algorithm_slug="rotated-binary-search",
        oracle=oracles.rotated_search,
        cases=[
            ("7 4 5 6 7 0 1 2 0", ([4, 5, 6, 7, 0, 1, 2], 0), False),
            ("7 4 5 6 7 0 1 2 3", ([4, 5, 6, 7, 0, 1, 2], 3), False),
            ("1 1 1", ([1], 1), True),
            ("3 5 1 3 5", ([5, 1, 3], 5), True),
        ],
        statement=(
            "An ascending array of **distinct** integers was rotated at an unknown "
            "pivot. Given the rotated array `nums` and a `target`, print the index "
            "of `target`, or **-1** if it is not present. Solve in **O(log n)** time."
        ),
        constraints=["1 ≤ nums.length ≤ 5000", "all elements distinct"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def search(nums, target):\n    pass\n\nprint(search(nums, target))\n"
        ),
        title="Search in Rotated Sorted Array",
    ),
    "bitonic-peak-index": _Spec(
        algorithm_slug="binary-search",
        oracle=oracles.bitonic_peak_index,
        cases=[
            ("4 1 2 3 1", ([1, 2, 3, 1],), False),
            ("8 1 2 3 4 5 6 7 1", ([1, 2, 3, 4, 5, 6, 7, 1],), False),
            ("8 1 9 8 7 6 5 4 3", ([1, 9, 8, 7, 6, 5, 4, 3],), True),
            ("5 1 2 5 4 3", ([1, 2, 5, 4, 3],), True),
        ],
        statement=(
            "You are given an array `nums` that **strictly increases then strictly "
            "decreases** (exactly one peak, guaranteed). Print the **index of the "
            "peak** element in **O(log n)** time."
        ),
        constraints=["3 ≤ nums.length ≤ 10^5", "array is strictly bitonic"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def peak_index(nums):\n    pass\n\nprint(peak_index(nums))\n"
        ),
        title="Peak Index in a Bitonic Array",
    ),
    "first-occurrence": _Spec(
        algorithm_slug="binary-search",
        oracle=oracles.first_occurrence,
        cases=[
            ("6 5 7 7 8 8 10 8", ([5, 7, 7, 8, 8, 10], 8), False),
            ("6 5 7 7 8 8 10 6", ([5, 7, 7, 8, 8, 10], 6), False),
            ("0 0 5", ([], 5), True),
            ("5 1 1 1 1 1 1", ([1, 1, 1, 1, 1], 1), True),
        ],
        statement=(
            "Given a sorted (non-decreasing) array `nums` and a `target`, print the "
            "**leftmost index** where `target` occurs, or **-1**. Solve in O(log n)."
        ),
        constraints=["0 ≤ nums.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def first_occurrence(nums, target):\n    pass\n\nprint(first_occurrence(nums, target))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
    ),
    "last-occurrence": _Spec(
        algorithm_slug="binary-search",
        oracle=oracles.last_occurrence,
        cases=[
            ("6 5 7 7 8 8 10 8", ([5, 7, 7, 8, 8, 10], 8), False),
            ("6 5 7 7 8 8 10 6", ([5, 7, 7, 8, 8, 10], 6), False),
            ("5 1 1 1 1 1 1", ([1, 1, 1, 1, 1], 1), True),
            ("1 9 9", ([9], 9), True),
        ],
        statement=(
            "Given a sorted (non-decreasing) array `nums` and a `target`, print the "
            "**rightmost index** where `target` occurs, or **-1**. Solve in O(log n)."
        ),
        constraints=["0 ≤ nums.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def last_occurrence(nums, target):\n    pass\n\nprint(last_occurrence(nums, target))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
    ),
    "count-occurrences-sorted": _Spec(
        algorithm_slug="binary-search",
        oracle=oracles.count_occurrences,
        cases=[
            ("7 5 7 7 8 8 8 10 8", ([5, 7, 7, 8, 8, 8, 10], 8), False),
            ("6 5 7 7 8 8 10 6", ([5, 7, 7, 8, 8, 10], 6), False),
            ("0 0 3", ([], 3), True),
            ("5 2 2 2 2 2 2", ([2, 2, 2, 2, 2], 2), True),
        ],
        statement=(
            "Given a sorted (non-decreasing) array `nums` and a `target`, print the "
            "**number of times** `target` occurs. Solve in O(log n), not O(n)."
        ),
        constraints=["0 ≤ nums.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def count_occurrences(nums, target):\n    pass\n\nprint(count_occurrences(nums, target))\n"
        ),
    ),
    "search-insert-position": _Spec(
        algorithm_slug="binary-search",
        oracle=oracles.search_insert_position,
        cases=[
            ("4 1 3 5 6 5", ([1, 3, 5, 6], 5), False),
            ("4 1 3 5 6 2", ([1, 3, 5, 6], 2), False),
            ("0 0 4", ([], 4), True),
            ("4 1 3 5 6 7", ([1, 3, 5, 6], 7), True),
        ],
        statement=(
            "Given a sorted array `nums` (distinct integers) and a `target`, print "
            "the index at which `target` would be inserted to keep `nums` sorted."
        ),
        constraints=["0 ≤ nums.length ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def search_insert(nums, target):\n    pass\n\nprint(search_insert(nums, target))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
    ),
    "koko-eating-bananas": _Spec(
        algorithm_slug="binary-search",
        oracle=oracles.min_eating_speed,
        cases=[
            ("4 3 6 7 11 8", ([3, 6, 7, 11], 8), False),
            ("5 30 11 23 4 20 5", ([30, 11, 23, 4, 20], 5), False),
            ("5 30 11 23 4 20 6", ([30, 11, 23, 4, 20], 6), True),
            ("1 5 5", ([5], 5), True),
        ],
        statement=(
            "Koko has `piles` of bananas and `h` hours. Each hour she picks one pile "
            "and eats up to `k` bananas from it (if the pile has fewer than `k`, she "
            "finishes it and stops for the hour). Print the **minimum integer `k`** "
            "so she finishes all piles within `h` hours. Solve via binary search on "
            "the answer, not brute force."
        ),
        constraints=["1 ≤ piles.length ≤ h ≤ 10^4", "1 ≤ piles[i] ≤ 10^9"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\npiles = list(map(int, data[1:n+1]))\nh = int(data[n+1])\n\n"
            "def min_eating_speed(piles, h):\n    pass\n\nprint(min_eating_speed(piles, h))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
    ),
    "ship-packages-within-days": _Spec(
        algorithm_slug="binary-search",
        oracle=oracles.ship_within_days,
        cases=[
            ("10 1 2 3 4 5 6 7 8 9 10 5", ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5), False),
            ("6 3 2 2 4 1 4 3", ([3, 2, 2, 4, 1, 4], 3), False),
            ("5 1 2 3 1 1 4", ([1, 2, 3, 1, 1], 4), True),
            ("1 7 1", ([7], 1), True),
        ],
        statement=(
            "Packages with `weights` (in order) must all ship, one per day in "
            "order, within `days` days on a ship of fixed daily `capacity`. Print "
            "the **minimum capacity** that lets all packages ship within `days` days. "
            "Solve via binary search on the answer."
        ),
        constraints=["1 ≤ weights.length ≤ 5×10^4", "1 ≤ weights[i] ≤ 500", "days ≤ weights.length"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nweights = list(map(int, data[1:n+1]))\ndays = int(data[n+1])\n\n"
            "def ship_within_days(weights, days):\n    pass\n\nprint(ship_within_days(weights, days))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
    ),
    "integer-square-root": _Spec(
        algorithm_slug="binary-search",
        oracle=oracles.integer_sqrt,
        cases=[
            ("4", (4,), False), ("8", (8,), False),
            ("0", (0,), True), ("2147395599", (2147395599,), True),
        ],
        statement=(
            "Given a non-negative integer `n`, print `floor(sqrt(n))` **without "
            "using a built-in square-root function**. Solve via binary search."
        ),
        constraints=["0 ≤ n ≤ 2^31 - 1"],
        starter_code=(
            "import sys\nn = int(sys.stdin.read().strip())\n\n"
            "def my_sqrt(n):\n    pass\n\nprint(my_sqrt(n))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
    ),
    "search-2d-matrix": _Spec(
        algorithm_slug="binary-search",
        oracle=oracles.search_2d_matrix,
        cases=[
            ("3 4\n1 3 5 7\n10 11 16 20\n23 30 34 60\n3", ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3), False),
            ("3 4\n1 3 5 7\n10 11 16 20\n23 30 34 60\n13", ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13), False),
            ("1 1\n5\n5", ([[5]], 5), True),
            ("3 4\n1 3 5 7\n10 11 16 20\n23 30 34 60\n34", ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 34), True),
        ],
        statement=(
            "Given an `m x n` matrix where each row is sorted ascending and each "
            "row's first integer is greater than the previous row's last integer, "
            "print `true` if `target` exists in the matrix, else `false`. Solve in "
            "**O(log(m*n))** time by treating the matrix as one flattened sorted array."
        ),
        constraints=["1 ≤ m, n ≤ 100"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split('\\n')\n"
            "m, n = map(int, data[0].split())\n"
            "matrix = [list(map(int, data[1+i].split())) for i in range(m)]\n"
            "target = int(data[1+m])\n\n"
            "def search_matrix(matrix, target):\n    pass\n\n"
            "print('true' if search_matrix(matrix, target) else 'false')\n"
        ),
        format_output=_fmt_bool,
    ),
    "find-minimum-rotated-sorted-array": _Spec(
        algorithm_slug="rotated-binary-search",
        oracle=oracles.find_min_rotated,
        cases=[
            ("5 3 4 5 1 2", ([3, 4, 5, 1, 2],), False),
            ("7 4 5 6 7 0 1 2", ([4, 5, 6, 7, 0, 1, 2],), False),
            ("4 11 13 15 17", ([11, 13, 15, 17],), True),
            ("2 2 1", ([2, 1],), True),
        ],
        statement=(
            "An ascending array of **distinct** integers was rotated at an unknown "
            "pivot. Given the rotated array `nums`, print its **minimum element** "
            "in **O(log n)** time."
        ),
        constraints=["1 ≤ nums.length ≤ 5000", "all elements distinct"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def find_min(nums):\n    pass\n\nprint(find_min(nums))\n"
        ),
        title="Find Minimum in Rotated Sorted Array",
    ),
}


def build_binary_search_variant_problems(
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
        reg = by_slug.get(spec.algorithm_slug)
        if reg is None:
            skipped.append((slug, f"linked algorithm '{spec.algorithm_slug}' not found in canonical registry"))
            continue

        test_plan = BINARY_SEARCH_VARIANT_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in binary_search_variants_testdata.py"))
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

        intuition = reg.manifest.get("intuition", "") or reg.manifest.get("description", "")
        problem = {
            "id": slug,
            "title": spec.title or reg.name,
            "difficulty": spec.difficulty,
            "category": "searching",
            "algorithm_slug": spec.algorithm_slug,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": intuition[:300] or f"Uses binary search: {reg.name}."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
