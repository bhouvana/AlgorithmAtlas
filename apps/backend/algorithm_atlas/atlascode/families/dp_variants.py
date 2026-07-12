"""
Dynamic-programming variant family — new problem CONTRACTS distinct from
the dynamic-programming family's existing 18 (e.g. `coin-change-ways` already
covers unbounded combination counting; `combination-sum-iv-count` here is
deliberately a PERMUTATION count over the same kind of input, a genuinely
different objective, not a relabeled duplicate). All `origin_type =
PATTERN_PROBLEM` (`algorithm_slug=None`) — none map to a distinct canonical
algorithm not already covered by the dynamic-programming family's own slugs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .dp_variants_testdata import DP_VARIANT_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_bool(answer: object) -> str:
    return "true" if answer else "false"


@dataclass(frozen=True)
class _Spec:
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
    "triangle-minimum-path-sum": _Spec(
        oracle=oracles.triangle_min_path_sum,
        cases=[
            ("4\n2\n3 4\n6 5 7\n4 1 8 3", ([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]],), False),
            ("1\n-10", ([[-10]],), False),
            ("2\n1\n2 3", ([[1], [2, 3]],), True),
            (
                "5\n-1\n0 5\n3 -5 2\n-2 5 -5 -3\n-4 0 2 -2 1",
                ([[-1], [0, 5], [3, -5, 2], [-2, 5, -5, -3], [-4, 0, 2, -2, 1]],),
                True,
            ),
        ],
        statement=(
            "Given a triangle array (row `i` has `i+1` values), print the "
            "**minimum path sum** from the top to the bottom, moving to an "
            "adjacent number in the row below at each step."
        ),
        constraints=["1 ≤ rows ≤ 200"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "n = int(lines[0])\ntriangle = [list(map(int, lines[1+i].split())) for i in range(n)]\n\n"
            "def minimum_total(triangle):\n    pass\n\nprint(minimum_total(triangle))\n"
        ),
        title="Triangle Minimum Path Sum",
    ),
    "best-time-to-buy-sell-stock": _Spec(
        oracle=oracles.max_profit_single_transaction,
        cases=[
            ("6 7 1 5 3 6 4", ([7, 1, 5, 3, 6, 4],), False),
            ("5 7 6 4 3 1", ([7, 6, 4, 3, 1],), False),
            ("1 5", ([5],), True),
            ("2 1 2", ([1, 2],), True),
        ],
        statement=(
            "Given daily stock `prices`, print the **maximum profit** from buying "
            "on one day and selling on a later day (0 if no profit is possible)."
        ),
        constraints=["1 ≤ prices.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nprices = list(map(int, data[1:n+1]))\n\n"
            "def max_profit(prices):\n    pass\n\nprint(max_profit(prices))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        title="Best Time to Buy and Sell Stock",
    ),
    "best-time-to-buy-sell-stock-ii": _Spec(
        oracle=oracles.max_profit_unlimited_transactions,
        cases=[
            ("6 7 1 5 3 6 4", ([7, 1, 5, 3, 6, 4],), False),
            ("5 1 2 3 4 5", ([1, 2, 3, 4, 5],), False),
            ("5 7 6 4 3 1", ([7, 6, 4, 3, 1],), True),
            ("1 5", ([5],), True),
        ],
        statement=(
            "Given daily stock `prices`, print the **maximum profit** achievable "
            "with **unlimited** buy/sell transactions (no overlapping holdings)."
        ),
        constraints=["1 ≤ prices.length ≤ 3×10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nprices = list(map(int, data[1:n+1]))\n\n"
            "def max_profit(prices):\n    pass\n\nprint(max_profit(prices))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        title="Best Time to Buy and Sell Stock II",
    ),
    "partition-equal-subset-sum": _Spec(
        oracle=oracles.can_partition_equal_subset,
        cases=[
            ("4 1 5 11 5", ([1, 5, 11, 5],), False),
            ("4 1 2 3 5", ([1, 2, 3, 5],), False),
            ("1 1", ([1],), True),
            ("3 1 2 5", ([1, 2, 5],), True),
        ],
        statement=(
            "Given an array `nums`, print `true` if it can be **partitioned into "
            "two subsets with equal sum**, else `false`."
        ),
        constraints=["1 ≤ nums.length ≤ 200"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def can_partition(nums):\n    pass\n\nprint('true' if can_partition(nums) else 'false')\n"
        ),
        format_output=_fmt_bool,
        title="Partition Equal Subset Sum",
    ),
    "target-sum-ways": _Spec(
        oracle=oracles.target_sum_ways,
        cases=[
            ("5 1 1 1 1 1 3", ([1, 1, 1, 1, 1], 3), False),
            ("1 1 1", ([1], 1), False),
            ("1 0 0", ([0], 0), True),
            ("3 1 1 1 1", ([1, 1, 1], 1), True),
        ],
        statement=(
            "Given an array `nums` and a `target`, print the number of ways to "
            "assign a `+` or `-` sign to each element so the expression evaluates "
            "to `target`."
        ),
        constraints=["1 ≤ nums.length ≤ 20", "0 ≤ nums[i] ≤ 1000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def find_target_sum_ways(nums, target):\n    pass\n\n"
            "print(find_target_sum_ways(nums, target))\n"
        ),
        title="Target Sum",
    ),
    "perfect-squares-min-count": _Spec(
        oracle=oracles.perfect_squares_min_count,
        cases=[
            ("12", (12,), False), ("13", (13,), False),
            ("1", (1,), True), ("100", (100,), True),
        ],
        statement=(
            "Given an integer `n`, print the **fewest number of perfect squares** "
            "(1, 4, 9, 16, ...) that sum to `n`."
        ),
        constraints=["1 ≤ n ≤ 10^4"],
        starter_code=(
            "import sys\nn = int(sys.stdin.read().strip())\n\n"
            "def num_squares(n):\n    pass\n\nprint(num_squares(n))\n"
        ),
        title="Perfect Squares",
    ),
    "combination-sum-iv-count": _Spec(
        oracle=oracles.combination_sum_iv_count,
        cases=[
            ("3 1 2 3 4", ([1, 2, 3], 4), False),
            ("1 9 3", ([9], 3), False),
            ("1 5 0", ([5], 0), True),
            ("2 1 2 3", ([1, 2], 3), True),
        ],
        statement=(
            "Given a set of distinct positive integers `nums` and a `target`, "
            "print the number of **ordered sequences** (elements may repeat, "
            "order matters) drawn from `nums` that sum to `target`."
        ),
        constraints=["1 ≤ nums.length ≤ 200", "1 ≤ target ≤ 1000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def combination_sum4(nums, target):\n    pass\n\n"
            "print(combination_sum4(nums, target))\n"
        ),
        title="Combination Sum IV (Ordered Count)",
    ),
    "delete-and-earn": _Spec(
        oracle=oracles.delete_and_earn,
        cases=[
            ("4 3 4 2 3", ([3, 4, 2, 3],), False),
            ("6 2 2 3 3 3 4", ([2, 2, 3, 3, 3, 4],), False),
            ("1 5", ([5],), True),
            ("3 1 1 1", ([1, 1, 1],), True),
        ],
        statement=(
            "Given an array `nums`, repeatedly pick a value `x`, earn `x` points "
            "for **every occurrence** of `x`, and delete every element equal to "
            "`x-1` or `x+1` from the array. Print the **maximum points** earnable."
        ),
        constraints=["1 ≤ nums.length ≤ 2×10^4", "1 ≤ nums[i] ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def delete_and_earn(nums):\n    pass\n\nprint(delete_and_earn(nums))\n"
        ),
        difficulty="Hard",
        estimated_minutes=30,
        title="Delete and Earn",
    ),
    "maximum-subarray-circular": _Spec(
        oracle=oracles.max_subarray_circular,
        cases=[
            ("4 1 -2 3 -2", ([1, -2, 3, -2],), False),
            ("3 5 -3 5", ([5, -3, 5],), False),
            ("3 -2 -3 -1", ([-2, -3, -1],), True),
            ("1 -5", ([-5],), True),
        ],
        statement=(
            "Given a **circular** array `nums` (the end wraps to the start), "
            "print the **maximum sum** of a non-empty contiguous subarray, where "
            "the subarray may wrap around."
        ),
        constraints=["1 ≤ nums.length ≤ 3×10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def max_subarray_sum_circular(nums):\n    pass\n\n"
            "print(max_subarray_sum_circular(nums))\n"
        ),
        difficulty="Hard",
        estimated_minutes=30,
        title="Maximum Sum Circular Subarray",
    ),
    "jump-game-ii-min-jumps": _Spec(
        oracle=oracles.jump_game_ii_min_jumps,
        cases=[
            ("5 2 3 1 1 4", ([2, 3, 1, 1, 4],), False),
            ("5 2 3 0 1 4", ([2, 3, 0, 1, 4],), False),
            ("1 0", ([0],), True),
            ("2 1 1", ([1, 1],), True),
        ],
        statement=(
            "Given an array `nums` where `nums[i]` is the max jump length from "
            "index `i` (guaranteed reachable), print the **minimum number of "
            "jumps** to reach the last index."
        ),
        constraints=["1 ≤ nums.length ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def jump(nums):\n    pass\n\nprint(jump(nums))\n"
        ),
        title="Jump Game II (Minimum Jumps)",
    ),
}


def build_dp_variant_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue

        test_plan = DP_VARIANT_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in dp_variants_testdata.py"))
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

        problem = {
            "id": slug,
            "title": spec.title,
            "difficulty": spec.difficulty,
            "category": "dynamic-programming",
            "algorithm_slug": None,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": "Define the state, find the recurrence, then decide table order."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
