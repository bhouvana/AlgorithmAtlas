"""
Dynamic-programming family factory.

Follows the oracle-separation architecture established by
`families/number_theory.py` (see docs/atlascode-progress.md): every expected
output comes exclusively from a hand-reviewed, unit-tested, brute-force-
cross-checked function in `independent_oracles.py` — never from a
visualization plugin's terminal state. `dynamic-programming` plugins use
`DPState`, and every algorithm has a DIFFERENT answer location in its table
(table[0][-1], table[m][n], table[n][W], ...) with no shared formula — reading
plugin state directly was explicitly rejected for this family in the prior
session's audit, which is why every problem below defines its own contract
and its own independent oracle instead.

Of the 26 uncurated dynamic-programming canonical algorithms, this batch
covers the 18 whose answer is an unambiguous scalar/boolean. Deferred to a
later batch (non-scalar output, unclear canonical contract, or needs a
comparator that doesn't exist yet):
  - optimal-bst (needs frequency-array contract decision)
  - bitmask-tsp (needs a decision on directed vs undirected + adjacency contract)
  - convex-hull-trick (a technique/building block, not itself a problem)
  - sequence-alignment (needs a gap/mismatch-penalty contract decision)
  - floyd-warshall (matrix output — feasible but deferred to keep this batch
    scalar-only; a good STANDARD_JUDGE candidate with fixed-format matrix rows)
  - palindrome-partition / palindrome-partitioning (near-duplicate slugs —
    needs a product decision on which contract each should own before shipping
    both, to avoid a semantic duplicate)
  - stock-cooldown (needs decision on transaction-fee/cooldown-length variant)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .dynamic_programming_testdata import DYNAMIC_PROGRAMMING_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_bool(answer: object) -> str:
    return "true" if answer else "false"


@dataclass(frozen=True)
class _Spec:
    oracle: Callable[..., object]
    # (input_data stdin text, positional args to pass to oracle, is_hidden)
    cases: list[tuple[str, tuple, bool]]
    statement: str
    constraints: list[str]
    starter_code: str
    difficulty: str = "Medium"
    estimated_minutes: int = 25
    format_output: Callable[[object], str] = _fmt_int


_SPECS: dict[str, _Spec] = {
    "staircase": _Spec(
        oracle=oracles.climbing_stairs,
        cases=[
            ("0", (0,), False), ("1", (1,), False), ("5", (5,), False),
            ("10", (10,), True), ("30", (30,), True),
        ],
        statement=(
            "You are climbing a staircase with `n` steps. Each move you can climb "
            "**1 or 2 steps**. Print the number of **distinct ways** to reach the top."
        ),
        constraints=["0 ≤ n ≤ 40"],
        starter_code=(
            "import sys\nn = int(sys.stdin.read().strip())\n\n"
            "def climb_stairs(n):\n    pass\n\nprint(climb_stairs(n))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
    ),
    "jump-game": _Spec(
        oracle=oracles.can_jump,
        cases=[
            ("5 2 3 1 1 4", ([2, 3, 1, 1, 4],), False),
            ("5 3 2 1 0 4", ([3, 2, 1, 0, 4],), False),
            ("1 0", ([0],), True),
            ("4 1 0 1 0", ([1, 0, 1, 0],), True),
        ],
        statement=(
            "Given an array `nums` where `nums[i]` is the max jump length from index i, "
            "starting at index 0, print `true` if you can reach the last index, else `false`."
        ),
        constraints=["1 ≤ nums.length ≤ 10^4", "0 ≤ nums[i] ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def can_jump(nums):\n    pass\n\n"
            "print('true' if can_jump(nums) else 'false')\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        format_output=_fmt_bool,
    ),
    "subset-sum": _Spec(
        oracle=oracles.subset_sum_exists,
        cases=[
            ("6 3 34 4 12 5 2 9", ([3, 34, 4, 12, 5, 2], 9), False),
            ("6 3 34 4 12 5 2 30", ([3, 34, 4, 12, 5, 2], 30), False),
            ("0 0", ([], 0), True),
            ("4 1 5 10 20 25", ([1, 5, 10, 20], 25), True),
        ],
        statement=(
            "Given a set of non-negative integers `nums` and a `target`, print `true` "
            "if some subset of `nums` sums exactly to `target`, else `false`."
        ),
        constraints=["0 ≤ nums.length ≤ 20", "0 ≤ nums[i] ≤ 1000", "0 ≤ target ≤ 5000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def subset_sum(nums, target):\n    pass\n\n"
            "print('true' if subset_sum(nums, target) else 'false')\n"
        ),
        format_output=_fmt_bool,
    ),
    "coin-change-ways": _Spec(
        oracle=oracles.coin_change_ways,
        cases=[
            ("3 1 2 5 5", ([1, 2, 5], 5), False),
            ("1 2 3", ([2], 3), False),
            ("1 1 0", ([1], 0), True),
            ("4 1 5 10 25 30", ([1, 5, 10, 25], 30), True),
        ],
        statement=(
            "Given coin denominations `coins` (unlimited supply of each) and a target "
            "`amount`, print the number of **distinct combinations** (order does not "
            "matter) that make up `amount`."
        ),
        constraints=["1 ≤ coins.length ≤ 10", "1 ≤ coins[i] ≤ 100", "0 ≤ amount ≤ 500"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "k = int(data[0])\ncoins = list(map(int, data[1:k+1]))\namount = int(data[k+1])\n\n"
            "def change(coins, amount):\n    pass\n\nprint(change(coins, amount))\n"
        ),
    ),
    "decode-ways": _Spec(
        oracle=oracles.decode_ways,
        cases=[
            ("12", ("12",), False), ("226", ("226",), False),
            ("06", ("06",), True), ("100", ("100",), True), ("10", ("10",), True),
        ],
        statement=(
            "A digit string can be decoded into letters via `'1'->'A', ..., '26'->'Z'`. "
            "Given a digit string `s`, print the **number of ways** to decode it "
            "(0 if none — e.g. a stray leading zero in a group)."
        ),
        constraints=["1 ≤ s.length ≤ 100", "s consists of digits '0'-'9'"],
        starter_code=(
            "import sys\ns = sys.stdin.read().strip()\n\n"
            "def num_decodings(s):\n    pass\n\nprint(num_decodings(s))\n"
        ),
    ),
    "knapsack-01": _Spec(
        oracle=oracles.knapsack_01,
        cases=[
            ("4 1 3 4 5 1 4 5 7 7", ([1, 3, 4, 5], [1, 4, 5, 7], 7), False),
            ("1 10 60 5", ([10], [60], 5), False),
            ("3 2 2 2 3 3 3 0", ([2, 2, 2], [3, 3, 3], 0), True),
            ("5 2 3 4 5 9 3 4 5 8 10 20", ([2, 3, 4, 5, 9], [3, 4, 5, 8, 10], 20), True),
        ],
        statement=(
            "Given `n` items with `weights` and `values`, and a knapsack `capacity`, "
            "print the **maximum total value** achievable picking each item at most once."
        ),
        constraints=["1 ≤ n ≤ 100", "0 ≤ weights[i], values[i] ≤ 1000", "0 ≤ capacity ≤ 1000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "n=int(data[idx]);idx+=1\nweights=list(map(int,data[idx:idx+n]));idx+=n\n"
            "values=list(map(int,data[idx:idx+n]));idx+=n\ncapacity=int(data[idx])\n\n"
            "def knapsack(weights, values, capacity):\n    pass\n\n"
            "print(knapsack(weights, values, capacity))\n"
        ),
    ),
    "unbounded-knapsack": _Spec(
        oracle=oracles.unbounded_knapsack,
        cases=[
            ("3 5 10 15 10 30 20 100", ([5, 10, 15], [10, 30, 20], 100), False),
            ("4 1 3 4 5 10 40 50 70 8", ([1, 3, 4, 5], [10, 40, 50, 70], 8), False),
            ("2 3 5 4 6 0", ([3, 5], [4, 6], 0), True),
            ("2 4 6 5 8 15", ([4, 6], [5, 8], 15), True),
        ],
        statement=(
            "Given `n` item types with `weights` and `values` (unlimited supply of each), "
            "and a knapsack `capacity`, print the **maximum total value** achievable."
        ),
        constraints=["1 ≤ n ≤ 50", "1 ≤ weights[i] ≤ 200", "0 ≤ values[i] ≤ 1000", "0 ≤ capacity ≤ 2000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "n=int(data[idx]);idx+=1\nweights=list(map(int,data[idx:idx+n]));idx+=n\n"
            "values=list(map(int,data[idx:idx+n]));idx+=n\ncapacity=int(data[idx])\n\n"
            "def unbounded_knapsack(weights, values, capacity):\n    pass\n\n"
            "print(unbounded_knapsack(weights, values, capacity))\n"
        ),
    ),
    "rod-cutting": _Spec(
        oracle=oracles.rod_cutting,
        cases=[
            ("8 1 5 8 9 10 17 17 20", ([1, 5, 8, 9, 10, 17, 17, 20], 8), False),
            ("4 1 5 8 9", ([1, 5, 8, 9], 4), False),
            ("1 5", ([5], 1), True),
            ("4 2 5 7 8", ([2, 5, 7, 8], 4), True),
        ],
        statement=(
            "Given a rod of length `n` and `prices[i]` = the price of a piece of length "
            "`i+1`, print the **maximum revenue** obtainable by cutting the rod into "
            "integer-length pieces (or not cutting it at all)."
        ),
        constraints=["1 ≤ n ≤ 100", "0 ≤ prices[i] ≤ 1000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nprices = list(map(int, data[1:n+1]))\n\n"
            "def rod_cutting(prices, n):\n    pass\n\nprint(rod_cutting(prices, n))\n"
        ),
    ),
    "maximum-product-subarray": _Spec(
        oracle=oracles.max_product_subarray,
        cases=[
            ("4 2 3 -2 4", ([2, 3, -2, 4],), False),
            ("3 -2 0 -1", ([-2, 0, -1],), False),
            ("3 -2 3 -4", ([-2, 3, -4],), True),
            ("1 -2", ([-2],), True),
        ],
        statement=(
            "Given an integer array `nums`, print the **largest product** of a "
            "contiguous, non-empty subarray."
        ),
        constraints=["1 ≤ nums.length ≤ 2×10^4", "-10 ≤ nums[i] ≤ 10"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def max_product(nums):\n    pass\n\nprint(max_product(nums))\n"
        ),
    ),
    "longest-bitonic-subsequence": _Spec(
        oracle=oracles.longest_bitonic_subsequence,
        cases=[
            ("8 1 11 2 10 4 5 2 1", ([1, 11, 2, 10, 4, 5, 2, 1],), False),
            ("6 12 11 40 5 3 1", ([12, 11, 40, 5, 3, 1],), False),
            ("6 80 60 30 40 20 10", ([80, 60, 30, 40, 20, 10],), True),
            ("5 1 2 3 4 5", ([1, 2, 3, 4, 5],), True),
        ],
        statement=(
            "Given an array `nums`, print the length of the **longest bitonic "
            "subsequence** — a subsequence that first strictly increases, then "
            "strictly decreases (either part may be empty)."
        ),
        constraints=["1 ≤ nums.length ≤ 1000", "-10^4 ≤ nums[i] ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def lbs(nums):\n    pass\n\nprint(lbs(nums))\n"
        ),
    ),
    "palindrome-subsequence": _Spec(
        oracle=oracles.longest_palindromic_subsequence,
        cases=[
            ("bbbab", ("bbbab",), False), ("cbbd", ("cbbd",), False),
            ("a", ("a",), True), ("abcaba", ("abcaba",), True),
        ],
        statement=(
            "Given a string `s`, print the length of the **longest palindromic "
            "subsequence** of `s`."
        ),
        constraints=["1 ≤ s.length ≤ 1000", "s consists of lowercase English letters"],
        starter_code=(
            "import sys\ns = sys.stdin.read().strip()\n\n"
            "def lps(s):\n    pass\n\nprint(lps(s))\n"
        ),
    ),
    "interleaving-strings": _Spec(
        oracle=oracles.is_interleave,
        cases=[
            ("aabcc\ndbbca\naadbbcbcac", ("aabcc", "dbbca", "aadbbcbcac"), False),
            ("aabcc\ndbbca\naadbbbaccc", ("aabcc", "dbbca", "aadbbbaccc"), False),
            ("\n\n", ("", "", ""), True),
            ("abc\ndef\nadbcef", ("abc", "def", "adbcef"), True),
        ],
        statement=(
            "Given strings `s1`, `s2`, `s3`, print `true` if `s3` is formed by an "
            "**interleaving** of `s1` and `s2` (preserving each string's relative "
            "character order), else `false`."
        ),
        constraints=["0 ≤ s1.length, s2.length ≤ 100"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "s1, s2, s3 = lines[0], lines[1], lines[2]\n\n"
            "def is_interleave(s1, s2, s3):\n    pass\n\n"
            "print('true' if is_interleave(s1, s2, s3) else 'false')\n"
        ),
        format_output=_fmt_bool,
    ),
    "wildcard-matching": _Spec(
        oracle=oracles.wildcard_match,
        cases=[
            ("aa\na", ("aa", "a"), False), ("aa\n*", ("aa", "*"), False),
            ("cb\n?a", ("cb", "?a"), False),
            ("adceb\n*a*b", ("adceb", "*a*b"), True),
            ("acdcb\na*c?b", ("acdcb", "a*c?b"), True),
        ],
        statement=(
            "Given a string `s` and a wildcard pattern `p` (`'?'` matches any single "
            "character, `'*'` matches any sequence of characters, including the empty "
            "sequence), print `true` if `p` matches the **entire** `s`, else `false`."
        ),
        constraints=["0 ≤ s.length ≤ 2000", "0 ≤ p.length ≤ 2000"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "s, p = lines[0], lines[1]\n\n"
            "def is_match(s, p):\n    pass\n\n"
            "print('true' if is_match(s, p) else 'false')\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
        format_output=_fmt_bool,
    ),
    "distinct-subsequences": _Spec(
        oracle=oracles.num_distinct_subsequences,
        cases=[
            ("rabbbit\nrabbit", ("rabbbit", "rabbit"), False),
            ("babgbag\nbag", ("babgbag", "bag"), False),
            ("abc\nabcd", ("abc", "abcd"), True),
            ("aaaa\naa", ("aaaa", "aa"), True),
        ],
        statement=(
            "Given strings `s` and `t`, print the number of **distinct subsequences** "
            "of `s` that equal `t`."
        ),
        constraints=["1 ≤ s.length, t.length ≤ 1000"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "s, t = lines[0], lines[1]\n\n"
            "def num_distinct(s, t):\n    pass\n\nprint(num_distinct(s, t))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
    ),
    "matrix-chain-multiplication": _Spec(
        oracle=oracles.matrix_chain_order,
        cases=[
            ("5 40 20 30 10 30", ([40, 20, 30, 10, 30],), False),
            ("3 10 20 30", ([10, 20, 30],), False),
            ("2 10 20", ([10, 20],), True),
            ("6 5 10 3 12 5 50", ([5, 10, 3, 12, 5, 50],), True),
        ],
        statement=(
            "Given the dimensions of a chain of matrices as `dims` (matrix i has shape "
            "`dims[i] x dims[i+1]`), print the **minimum number of scalar "
            "multiplications** needed to compute the full product via optimal "
            "parenthesization."
        ),
        constraints=["2 ≤ dims.length ≤ 20", "1 ≤ dims[i] ≤ 200"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\ndims = list(map(int, data[1:n+1]))\n\n"
            "def matrix_chain_order(dims):\n    pass\n\nprint(matrix_chain_order(dims))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
    ),
    "egg-drop": _Spec(
        oracle=oracles.egg_drop_min_trials,
        cases=[
            ("2 10", (2, 10), False), ("1 5", (1, 5), False),
            ("2 36", (2, 36), True), ("3 14", (3, 14), True),
        ],
        statement=(
            "Given `eggs` identical eggs and a building with `floors` floors, print "
            "the **minimum number of trials** needed in the worst case to find the "
            "critical floor (the highest floor an egg survives a drop from)."
        ),
        constraints=["1 ≤ eggs ≤ 10", "0 ≤ floors ≤ 1000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "eggs, floors = int(data[0]), int(data[1])\n\n"
            "def egg_drop(eggs, floors):\n    pass\n\nprint(egg_drop(eggs, floors))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
    ),
    "boolean-parenthesization": _Spec(
        oracle=oracles.boolean_parenthesization_true_ways,
        cases=[
            ("TFT\n^&", ("TFT", "^&"), False),
            ("TTFT\n|&^", ("TTFT", "|&^"), False),
            ("TFTFTF\n^^^^^", ("TFTFTF", "^^^^^"), True),
            ("TTTT\n&&&", ("TTTT", "&&&"), True),
        ],
        statement=(
            "Given a boolean expression as a string of symbols `T`/`F` and a string of "
            "operators `&` (AND), `|` (OR), `^` (XOR) between them, print the number "
            "of ways to **parenthesize** the expression so that it evaluates to `True`."
        ),
        constraints=["1 ≤ symbols.length ≤ 15"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "symbols, ops = lines[0], lines[1]\n\n"
            "def count_ways(symbols, ops):\n    pass\n\nprint(count_ways(symbols, ops))\n"
        ),
        difficulty="Hard",
        estimated_minutes=40,
    ),
    "word-wrap": _Spec(
        oracle=oracles.word_wrap_min_cost,
        cases=[
            ("4 3 2 2 5 6", ([3, 2, 2, 5], 6), False),
            ("4 1 1 1 1 5", ([1, 1, 1, 1], 5), False),
            ("1 3 3", ([3], 3), True),
            ("5 2 3 2 5 2 8", ([2, 3, 2, 5, 2], 8), True),
        ],
        statement=(
            "Given `n` word lengths and a maximum `line_width`, print the **minimum "
            "total badness** of wrapping the words into lines in order, where the "
            "badness of a line (except the last) with `extra` unused characters is "
            "`extra^3`, and the last line always costs 0."
        ),
        constraints=["1 ≤ n ≤ 50", "1 ≤ word length ≤ line_width ≤ 50"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "n=int(data[idx]);idx+=1\nlengths=list(map(int,data[idx:idx+n]));idx+=n\n"
            "width=int(data[idx])\n\n"
            "def word_wrap(lengths, width):\n    pass\n\nprint(word_wrap(lengths, width))\n"
        ),
    ),
}


def build_dynamic_programming_problems(
    algorithms: list[RegisteredAlgorithm],
    curated_slugs: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    by_slug = {r.slug: r for r in algorithms if r.category == "dynamic-programming"}
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in curated_slugs:
            continue
        reg = by_slug.get(slug)
        if reg is None:
            skipped.append((slug, "not found in canonical registry"))
            continue

        test_plan = DYNAMIC_PROGRAMMING_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in dynamic_programming_testdata.py"))
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
            "category": "dynamic-programming",
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
