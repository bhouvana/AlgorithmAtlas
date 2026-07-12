"""
Divide-and-conquer family factory — canonical algorithm coverage (all 9
uncurated `divide-and-conquer` algorithms). Matrix/array outputs
(`matrix-exponentiation`, `polynomial-multiplication`, `strassen`) are
deterministic and exact-match safe (no floating point, no multi-valid-answer
ambiguity). `closest-pair` outputs squared distance (integer) specifically
to avoid float-judging brittleness.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .divide_and_conquer_testdata import DIVIDE_AND_CONQUER_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_int_list(answer: object) -> str:
    return " ".join(str(x) for x in answer)


def _fmt_matrix(answer: object) -> str:
    return "\n".join(" ".join(str(x) for x in row) for row in answer)


@dataclass(frozen=True)
class _Spec:
    oracle: Callable[..., object]
    cases: list[tuple[str, tuple, bool]]
    statement: str
    constraints: list[str]
    starter_code: str
    difficulty: str = "Medium"
    estimated_minutes: int = 25
    format_output: Callable[[object], str] = _fmt_int


_SPECS: dict[str, _Spec] = {
    "closest-pair": _Spec(
        oracle=oracles.closest_pair_min_sq_distance,
        cases=[
            ("3\n0 0\n3 4\n1 1", ([(0, 0), (3, 4), (1, 1)],), False),
            ("2\n0 0\n10 10", ([(0, 0), (10, 10)],), False),
            ("2\n5 5\n5 5", ([(5, 5), (5, 5)],), True),
            ("3\n0 0\n0 10\n1 1", ([(0, 0), (0, 10), (1, 1)],), True),
        ],
        statement=(
            "Given `n` 2D points, print the **minimum squared Euclidean distance** "
            "between any two distinct points (squared to keep the answer an exact "
            "integer)."
        ),
        constraints=["2 ≤ n ≤ 10^4", "-10^4 ≤ x, y ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split('\\n')\n"
            "n = int(data[0])\n"
            "points = [tuple(map(int, data[1+i].split())) for i in range(n)]\n\n"
            "def closest_pair_sq_dist(points):\n    pass\n\nprint(closest_pair_sq_dist(points))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
    ),
    "counting-inversions": _Spec(
        oracle=oracles.count_inversions,
        cases=[
            ("5 2 4 1 3 5", ([2, 4, 1, 3, 5],), False),
            ("3 1 2 3", ([1, 2, 3],), False),
            ("1 5", ([5],), True),
            ("5 5 4 3 2 1", ([5, 4, 3, 2, 1],), True),
        ],
        statement=(
            "Given an array `nums`, print the number of **inversions** — pairs "
            "`(i, j)` with `i < j` and `nums[i] > nums[j]`. Solve via merge-sort-"
            "style divide and conquer in O(n log n)."
        ),
        constraints=["1 ≤ nums.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def count_inversions(nums):\n    pass\n\nprint(count_inversions(nums))\n"
        ),
    ),
    "fast-power": _Spec(
        oracle=oracles.fast_power_exact,
        cases=[
            ("2 10", (2, 10), False), ("3 0", (3, 0), False),
            ("5 3", (5, 3), True), ("7 15", (7, 15), True),
        ],
        statement=(
            "Given `base` and a non-negative integer `exp`, print `base^exp` "
            "**exactly** (arbitrary precision), computed via fast exponentiation "
            "by squaring in O(log exp) multiplications."
        ),
        constraints=["1 ≤ base ≤ 20", "0 ≤ exp ≤ 300"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "base, exp = int(data[0]), int(data[1])\n\n"
            "def fast_power(base, exp):\n    pass\n\nprint(fast_power(base, exp))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
    ),
    "karatsuba": _Spec(
        oracle=oracles.karatsuba_multiply,
        cases=[
            ("1234 5678", (1234, 5678), False), ("0 100", (0, 100), False),
            ("999 999", (999, 999), True),
            ("123456789 987654321", (123456789, 987654321), True),
        ],
        statement=(
            "Given two non-negative integers `a` and `b`, print their **exact "
            "product**, computed via Karatsuba's divide-and-conquer multiplication."
        ),
        constraints=["0 ≤ a, b ≤ 10^18"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "a, b = int(data[0]), int(data[1])\n\n"
            "def karatsuba(a, b):\n    pass\n\nprint(karatsuba(a, b))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
    ),
    "majority-element": _Spec(
        oracle=oracles.majority_element,
        cases=[
            ("3 3 2 3", ([3, 2, 3],), False),
            ("7 2 2 1 1 1 2 2", ([2, 2, 1, 1, 1, 2, 2],), False),
            ("1 5", ([5],), True),
            ("5 1 1 1 2 2", ([1, 1, 1, 2, 2],), True),
        ],
        statement=(
            "Given an array `nums` guaranteed to contain a **majority element** "
            "(appearing more than n/2 times), print it. Solve via divide and "
            "conquer (or the Boyer-Moore voting algorithm)."
        ),
        constraints=["1 ≤ nums.length ≤ 5×10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def majority_element(nums):\n    pass\n\nprint(majority_element(nums))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
    ),
    "matrix-exponentiation": _Spec(
        oracle=oracles.matrix_power_mod,
        cases=[
            ("2 0 1000000007\n1 1\n1 0", ([[1, 1], [1, 0]], 0, 1000000007), False),
            ("2 10 1000000007\n1 1\n1 0", ([[1, 1], [1, 0]], 10, 1000000007), False),
            ("1 5 1000000007\n2", ([[2]], 5, 1000000007), True),
            ("2 3 100\n2 0\n0 2", ([[2, 0], [0, 2]], 3, 100), True),
        ],
        statement=(
            "Given an `n x n` matrix, an exponent `k`, and a `mod`, print "
            "`matrix^k mod mod` (each row on its own line, space-separated), "
            "computed via fast matrix exponentiation by squaring in O(n^3 log k)."
        ),
        constraints=["1 ≤ n ≤ 20", "0 ≤ k ≤ 10^9", "1 ≤ mod ≤ 10^9"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split('\\n')\n"
            "n, k, mod = map(int, data[0].split())\n"
            "matrix = [list(map(int, data[1+i].split())) for i in range(n)]\n\n"
            "def matrix_power(matrix, k, mod):\n    pass\n\n"
            "result = matrix_power(matrix, k, mod)\n"
            "print('\\n'.join(' '.join(map(str, row)) for row in result))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
        format_output=_fmt_matrix,
    ),
    "median-of-medians": _Spec(
        oracle=oracles.median_of_medians_kth_smallest,
        cases=[
            ("6 7 10 4 3 20 15 3", ([7, 10, 4, 3, 20, 15], 3), False),
            ("6 7 10 4 3 20 15 1", ([7, 10, 4, 3, 20, 15], 1), False),
            ("1 5 1", ([5], 1), True),
            ("5 5 4 3 2 1 5", ([5, 4, 3, 2, 1], 5), True),
        ],
        statement=(
            "Given an array `nums` and an integer `k`, print the **k-th smallest** "
            "element (1-indexed), computed via the median-of-medians selection "
            "algorithm in guaranteed O(n) worst-case time."
        ),
        constraints=["1 ≤ k ≤ nums.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def kth_smallest(nums, k):\n    pass\n\nprint(kth_smallest(nums, k))\n"
        ),
    ),
    "polynomial-multiplication": _Spec(
        oracle=oracles.polynomial_multiply,
        cases=[
            ("3 1 2 3 2 0 1", ([1, 2, 3], [0, 1]), False),
            ("2 1 1 2 1 1", ([1, 1], [1, 1]), False),
            ("1 5 1 3", ([5], [3]), True),
            ("2 0 0 2 1 2", ([0, 0], [1, 2]), True),
        ],
        statement=(
            "Given two polynomials as integer coefficient lists `a` and `b` "
            "(`a[i]` = coefficient of x^i), print the coefficient list of their "
            "**product**, space-separated, computed via divide-and-conquer "
            "(Karatsuba-style) polynomial multiplication."
        ),
        constraints=["1 ≤ a.length, b.length ≤ 1000", "-1000 ≤ coefficients ≤ 1000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "na=int(data[idx]);idx+=1\na=list(map(int,data[idx:idx+na]));idx+=na\n"
            "nb=int(data[idx]);idx+=1\nb=list(map(int,data[idx:idx+nb]))\n\n"
            "def multiply_polynomials(a, b):\n    pass\n\n"
            "print(' '.join(map(str, multiply_polynomials(a, b))))\n"
        ),
        format_output=_fmt_int_list,
    ),
    "strassen": _Spec(
        oracle=oracles.strassen_matrix_multiply,
        cases=[
            ("2 2 2\n1 2\n3 4\n5 6\n7 8", ([[1, 2], [3, 4]], [[5, 6], [7, 8]]), False),
            ("1 1 1\n5\n3", ([[5]], [[3]]), False),
            ("2 2 1\n1 0\n0 1\n7\n9", ([[1, 0], [0, 1]], [[7], [9]]), True),
            ("2 1 2\n1\n1\n2 3", ([[1], [1]], [[2, 3]]), True),
        ],
        statement=(
            "Given matrix `A` (`n x m`) and matrix `B` (`m x p`), print their "
            "product `A x B` (each row on its own line, space-separated), "
            "computed via Strassen's divide-and-conquer algorithm."
        ),
        constraints=["1 ≤ n, m, p ≤ 64", "-100 ≤ entries ≤ 100"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split('\\n')\n"
            "n, m, p = map(int, data[0].split())\n"
            "A = [list(map(int, data[1+i].split())) for i in range(n)]\n"
            "B = [list(map(int, data[1+n+i].split())) for i in range(m)]\n\n"
            "def matrix_multiply(A, B):\n    pass\n\n"
            "result = matrix_multiply(A, B)\n"
            "print('\\n'.join(' '.join(map(str, row)) for row in result))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
        format_output=_fmt_matrix,
    ),
}


def build_divide_and_conquer_problems(
    algorithms: list[RegisteredAlgorithm],
    curated_slugs: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    by_slug = {r.slug: r for r in algorithms if r.category == "divide-and-conquer"}
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in curated_slugs:
            continue
        reg = by_slug.get(slug)
        if reg is None:
            skipped.append((slug, "not found in canonical registry"))
            continue

        test_plan = DIVIDE_AND_CONQUER_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in divide_and_conquer_testdata.py"))
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
            "title": reg.name,
            "difficulty": spec.difficulty,
            "category": "divide-and-conquer",
            "algorithm_slug": slug,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": intuition[:300] or f"Implement {reg.name}."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
