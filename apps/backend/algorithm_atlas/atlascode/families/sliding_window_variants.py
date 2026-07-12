"""
Sliding-window variant family factory.

Unlike every prior family, these are `origin_type = PATTERN_PROBLEM`: no
single canonical algorithm in the registry backs "sliding window" as its own
entry, so these problems have NO `algorithm_slug` link (None) — they teach a
reasoning pattern shared across many canonical algorithms rather than
implementing one specific one. This is a deliberate, honest choice: linking
them to an unrelated canonical slug just to populate the field would
misrepresent coverage, exactly what docs/atlascode-progress.md warns against.

Every oracle lives in `independent_oracles.py` with brute-force-cross-checked
unit tests. Dedup is by problem slug against the full existing catalog, same
mechanism as `binary_search_variants.py`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .sliding_window_variants_testdata import SLIDING_WINDOW_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_int_list(answer: object) -> str:
    return " ".join(str(x) for x in answer) if answer else ""


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
    "max-sum-subarray-fixed-k": _Spec(
        oracle=oracles.max_sum_subarray_fixed_k,
        cases=[
            ("6 2 1 5 1 3 2 3", ([2, 1, 5, 1, 3, 2], 3), False),
            ("5 2 3 4 1 5 2", ([2, 3, 4, 1, 5], 2), False),
            ("1 7 1", ([7], 1), True),
            ("4 -1 -2 -3 -4 2", ([-1, -2, -3, -4], 2), True),
        ],
        statement=(
            "Given an integer array `nums` and an integer `k`, print the **maximum "
            "sum** of any contiguous subarray of exactly length `k`."
        ),
        constraints=["1 ≤ k ≤ nums.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def max_sum_fixed_k(nums, k):\n    pass\n\nprint(max_sum_fixed_k(nums, k))\n"
        ),
        title="Maximum Sum Subarray of Fixed Size K",
        difficulty="Easy",
        estimated_minutes=15,
    ),
    "min-subarray-len-target-sum": _Spec(
        oracle=oracles.min_subarray_len_at_least_target,
        cases=[
            ("6 2 3 1 2 4 3 7", ([2, 3, 1, 2, 4, 3], 7), False),
            ("3 1 4 4 4", ([1, 4, 4], 4), False),
            ("4 1 1 1 1 11", ([1, 1, 1, 1], 11), True),
            ("1 5 5", ([5], 5), True),
        ],
        statement=(
            "Given a positive-integer array `nums` and a positive integer `target`, "
            "print the **length of the shortest contiguous subarray** whose sum is "
            "`>= target`, or **0** if no such subarray exists. Solve in O(n)."
        ),
        constraints=["1 ≤ nums.length ≤ 10^5", "1 ≤ nums[i] ≤ 10^4", "1 ≤ target ≤ 10^9"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def min_subarray_len(nums, target):\n    pass\n\nprint(min_subarray_len(nums, target))\n"
        ),
        title="Minimum Size Subarray Sum",
    ),
    "longest-substring-without-repeating": _Spec(
        oracle=oracles.longest_substring_without_repeat,
        cases=[
            ("abcabcbb", ("abcabcbb",), False), ("bbbbb", ("bbbbb",), False),
            ("pwwkew", ("pwwkew",), True), ("", ("",), True),
        ],
        statement=(
            "Given a string `s`, print the length of the **longest substring** "
            "without repeating characters."
        ),
        constraints=["0 ≤ s.length ≤ 5×10^4"],
        starter_code=(
            "import sys\ns = sys.stdin.read().rstrip('\\n')\n\n"
            "def length_of_longest_substring(s):\n    pass\n\n"
            "print(length_of_longest_substring(s))\n"
        ),
        title="Longest Substring Without Repeating Characters",
    ),
    "longest-substring-at-most-k-distinct": _Spec(
        oracle=oracles.longest_substring_at_most_k_distinct,
        cases=[
            ("eceba 2", ("eceba", 2), False), ("aa 1", ("aa", 1), False),
            ("a 0", ("a", 0), True), ("abcabcabc 3", ("abcabcabc", 3), True),
        ],
        statement=(
            "Given a string `s` and an integer `k`, print the length of the "
            "**longest substring** that contains **at most `k` distinct "
            "characters**."
        ),
        constraints=["0 ≤ s.length ≤ 5×10^4", "0 ≤ k ≤ 26"],
        starter_code=(
            "import sys\nline = sys.stdin.read().rstrip('\\n')\n"
            "s, k = line.rsplit(' ', 1)\nk = int(k)\n\n"
            "def longest_k_distinct(s, k):\n    pass\n\nprint(longest_k_distinct(s, k))\n"
        ),
        title="Longest Substring with At Most K Distinct Characters",
    ),
    "longest-repeating-char-replacement": _Spec(
        oracle=oracles.longest_repeating_char_replacement,
        cases=[
            ("ABAB 2", ("ABAB", 2), False), ("AABABBA 1", ("AABABBA", 1), False),
            ("A 0", ("A", 0), True), ("AAAA 5", ("AAAA", 5), True),
        ],
        statement=(
            "Given a string `s` of uppercase letters and an integer `k`, you may "
            "replace up to `k` characters with any other uppercase letter. Print "
            "the length of the **longest substring** that can be made to consist "
            "of a single repeated character this way."
        ),
        constraints=["1 ≤ s.length ≤ 10^5", "0 ≤ k ≤ s.length"],
        starter_code=(
            "import sys\nline = sys.stdin.read().rstrip('\\n')\n"
            "s, k = line.rsplit(' ', 1)\nk = int(k)\n\n"
            "def character_replacement(s, k):\n    pass\n\nprint(character_replacement(s, k))\n"
        ),
        title="Longest Repeating Character Replacement",
    ),
    "max-consecutive-ones-with-k-flips": _Spec(
        oracle=oracles.max_consecutive_ones_with_k_flips,
        cases=[
            ("11 1 1 1 0 0 0 1 1 1 1 0 2", ([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2), False),
            ("6 0 0 1 1 0 0 0", ([0, 0, 1, 1, 0, 0], 0), False),
            ("1 0 5", ([0], 5), True),
            ("5 1 1 1 1 1 0", ([1, 1, 1, 1, 1], 0), True),
        ],
        statement=(
            "Given a binary array `nums` and an integer `k`, you may flip up to "
            "`k` zeros to ones. Print the **length of the longest contiguous run "
            "of 1s** achievable."
        ),
        constraints=["1 ≤ nums.length ≤ 10^5", "0 ≤ k ≤ nums.length"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def longest_ones(nums, k):\n    pass\n\nprint(longest_ones(nums, k))\n"
        ),
        title="Max Consecutive Ones with K Flips",
    ),
    "minimum-window-substring-length": _Spec(
        oracle=oracles.minimum_window_length,
        cases=[
            ("ADOBECODEBANC\nABC", ("ADOBECODEBANC", "ABC"), False),
            ("a\na", ("a", "a"), False),
            ("a\naa", ("a", "aa"), True),
            ("aa\naa", ("aa", "aa"), True),
        ],
        statement=(
            "Given strings `s` and `t`, print the **length of the smallest "
            "substring** of `s` that contains every character of `t` (respecting "
            "multiplicity), or **0** if no such window exists."
        ),
        constraints=["1 ≤ s.length, t.length ≤ 10^5"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\ns, t = lines[0], lines[1]\n\n"
            "def min_window_length(s, t):\n    pass\n\nprint(min_window_length(s, t))\n"
        ),
        title="Minimum Window Substring Length",
        difficulty="Hard",
        estimated_minutes=35,
    ),
    "find-all-anagrams-in-string": _Spec(
        oracle=oracles.find_all_anagram_starts,
        cases=[
            ("cbaebabacd\nabc", ("cbaebabacd", "abc"), False),
            ("abab\nab", ("abab", "ab"), False),
            ("a\nab", ("a", "ab"), True),
            ("aaaaaaaaaa\naaa", ("aaaaaaaaaa", "aaa"), True),
        ],
        statement=(
            "Given strings `s` and `p`, print all **starting indices** (ascending, "
            "space-separated) in `s` where a permutation (anagram) of `p` occurs. "
            "Print an empty line if there are none."
        ),
        constraints=["1 ≤ s.length, p.length ≤ 3×10^4"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\ns, p = lines[0], lines[1]\n\n"
            "def find_anagrams(s, p):\n    pass\n\n"
            "print(' '.join(map(str, find_anagrams(s, p))))\n"
        ),
        title="Find All Anagrams in a String",
        format_output=_fmt_int_list,
    ),
}


def build_sliding_window_variant_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue

        test_plan = SLIDING_WINDOW_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in sliding_window_variants_testdata.py"))
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
            "category": "sliding-window",
            "algorithm_slug": None,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": "Maintain a window with two pointers; expand right, shrink left when the window becomes invalid."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
