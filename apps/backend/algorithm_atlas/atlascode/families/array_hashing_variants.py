"""
Array/Hashing pattern-problem family. `origin_type = PATTERN_PROBLEM` for all
15 — no single canonical algorithm backs "hash map lookup patterns" as its
own registry entry. `top-k-frequent` and `majority-element-ii` fix a
deterministic tie-break (ascending value) so their list output is unique
despite ties in frequency/count being possible. `three-sum-count-triplets`
counts DISTINCT VALUE triples (not index triples) to keep the answer
well-defined regardless of duplicate values in the input.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .array_hashing_variants_testdata import ARRAY_HASHING_TEST_PLANS
from ..function_mode.adapters import PythonFunctionAdapter
from ..function_mode.contracts import FunctionContract, Parameter, TypeSpec
from ...plugins.registry import RegisteredAlgorithm

_INT = TypeSpec("integer")
_BOOL = TypeSpec("boolean")
_INT_ARRAY = TypeSpec("array", _INT)

_PY_ADAPTER = PythonFunctionAdapter()


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_bool(answer: object) -> str:
    return "true" if answer else "false"


def _fmt_int_list(answer: object) -> str:
    return " ".join(str(x) for x in answer)


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
    # Function Mode support (Phase 22 honest support matrix). None means
    # Program Mode only -- most of this family's 15 problems are, deliberately,
    # not migrated yet (see docs/atlascode-dual-run-modes.md for the batch
    # rationale). Function names below match the EXISTING Program Mode starter
    # exactly (see each entry's starter_code) so both modes teach the same
    # function signature.
    function_contract: FunctionContract | None = None


_SPECS: dict[str, _Spec] = {
    "contains-duplicate-within-k": _Spec(
        oracle=oracles.contains_duplicate_within_k,
        cases=[
            ("4 1 2 3 1 3", ([1, 2, 3, 1], 3), False),
            ("4 1 2 3 1 2", ([1, 2, 3, 1], 2), False),
            ("4 1 0 1 1 1", ([1, 0, 1, 1], 1), True),
            ("1 1 0", ([1], 0), True),
        ],
        statement=(
            "Given an array `nums` and an integer `k`, print `true` if two equal "
            "elements exist within index distance `k` (i.e. `abs(i-j) <= k`), else "
            "`false`."
        ),
        constraints=["1 ≤ nums.length ≤ 10^5", "0 ≤ k ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def contains_nearby_duplicate(nums, k):\n    pass\n\n"
            "print('true' if contains_nearby_duplicate(nums, k) else 'false')\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        format_output=_fmt_bool,
        title="Contains Duplicate Within K",
        function_contract=FunctionContract(
            function_name="contains_nearby_duplicate",
            parameters=[Parameter("nums", _INT_ARRAY), Parameter("k", _INT)],
            return_type=_BOOL,
        ),
    ),
    "product-of-array-except-self": _Spec(
        oracle=oracles.product_except_self,
        cases=[
            ("4 1 2 3 4", ([1, 2, 3, 4],), False),
            ("5 -1 1 0 -3 3", ([-1, 1, 0, -3, 3],), False),
            ("2 5 5", ([5, 5],), True),
            ("3 2 2 2", ([2, 2, 2],), True),
        ],
        statement=(
            "Given an array `nums`, print an array where `result[i]` is the "
            "product of all elements except `nums[i]`, **without using "
            "division**, in O(n) time."
        ),
        constraints=["2 ≤ nums.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def product_except_self(nums):\n    pass\n\n"
            "print(' '.join(map(str, product_except_self(nums))))\n"
        ),
        format_output=_fmt_int_list,
        title="Product of Array Except Self",
        function_contract=FunctionContract(
            function_name="product_except_self",
            parameters=[Parameter("nums", _INT_ARRAY)],
            return_type=_INT_ARRAY,
        ),
    ),
    "subarray-sum-equals-k": _Spec(
        oracle=oracles.subarray_sum_equals_k,
        cases=[
            ("3 1 1 1 2", ([1, 1, 1], 2), False),
            ("3 1 2 3 3", ([1, 2, 3], 3), False),
            ("3 1 -1 0 0", ([1, -1, 0], 0), True),
            ("1 0 0", ([0], 0), True),
        ],
        statement=(
            "Given an array `nums` and an integer `k`, print the number of "
            "**contiguous subarrays** whose elements sum to `k`."
        ),
        constraints=["1 ≤ nums.length ≤ 2×10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def subarray_sum(nums, k):\n    pass\n\nprint(subarray_sum(nums, k))\n"
        ),
        title="Subarray Sum Equals K",
        function_contract=FunctionContract(
            function_name="subarray_sum",
            parameters=[Parameter("nums", _INT_ARRAY), Parameter("k", _INT)],
            return_type=_INT,
        ),
    ),
    "top-k-frequent-elements": _Spec(
        oracle=oracles.top_k_frequent,
        cases=[
            ("6 1 1 1 2 2 3 2", ([1, 1, 1, 2, 2, 3], 2), False),
            ("1 1 1", ([1], 1), False),
            ("4 4 4 4 4 1", ([4, 4, 4, 4], 1), True),
            ("6 5 5 6 6 7 7 2", ([5, 5, 6, 6, 7, 7], 2), True),
        ],
        statement=(
            "Given an array `nums` and integer `k`, print the `k` most frequent "
            "elements, space-separated. Break ties by **smaller value first**."
        ),
        constraints=["1 ≤ nums.length ≤ 10^5", "k ≤ number of distinct elements"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def top_k_frequent(nums, k):\n    pass\n\n"
            "print(' '.join(map(str, top_k_frequent(nums, k))))\n"
        ),
        format_output=_fmt_int_list,
        title="Top K Frequent Elements",
        function_contract=FunctionContract(
            function_name="top_k_frequent",
            parameters=[Parameter("nums", _INT_ARRAY), Parameter("k", _INT)],
            return_type=_INT_ARRAY,
        ),
    ),
    "longest-consecutive-sequence": _Spec(
        oracle=oracles.longest_consecutive_sequence,
        cases=[
            ("6 100 4 200 1 3 2", ([100, 4, 200, 1, 3, 2],), False),
            ("10 0 3 7 2 5 8 4 6 0 1", ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1],), False),
            ("0", ([],), True),
            ("1 5", ([5],), True),
        ],
        statement=(
            "Given an unsorted array `nums`, print the length of the **longest "
            "run of consecutive integers** present (in any order), in O(n) time."
        ),
        constraints=["0 ≤ nums.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def longest_consecutive(nums):\n    pass\n\nprint(longest_consecutive(nums))\n"
        ),
        title="Longest Consecutive Sequence",
        function_contract=FunctionContract(
            function_name="longest_consecutive",
            parameters=[Parameter("nums", _INT_ARRAY)],
            return_type=_INT,
        ),
    ),
    "group-anagrams-count": _Spec(
        oracle=oracles.group_anagrams_count,
        cases=[
            ("6\neat\ntea\ntan\nate\nnat\nbat", (["eat", "tea", "tan", "ate", "nat", "bat"],), False),
            ("1\n", ([""],), False),
            ("3\na\na\na", (["a", "a", "a"],), True),
            ("4\nab\nba\ncd\ndc", (["ab", "ba", "cd", "dc"],), True),
        ],
        statement=(
            "Given `n` strings, print the number of **distinct anagram groups** "
            "when grouping strings that are anagrams of each other."
        ),
        constraints=["1 ≤ n ≤ 10^4"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "n = int(lines[0])\nstrs = lines[1:1+n]\n\n"
            "def group_anagrams_count(strs):\n    pass\n\nprint(group_anagrams_count(strs))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
        title="Group Anagrams Count",
    ),
    "valid-anagram": _Spec(
        oracle=oracles.is_anagram,
        cases=[
            ("anagram\nnagaram", ("anagram", "nagaram"), False),
            ("rat\ncar", ("rat", "car"), False),
            ("a\na", ("a", "a"), True),
            ("ab\naa", ("ab", "aa"), True),
        ],
        statement="Given strings `s` and `t`, print `true` if `t` is an anagram of `s`, else `false`.",
        constraints=["1 ≤ s.length, t.length ≤ 5×10^4"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\ns, t = lines[0], lines[1]\n\n"
            "def is_anagram(s, t):\n    pass\n\nprint('true' if is_anagram(s, t) else 'false')\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        format_output=_fmt_bool,
        title="Valid Anagram",
    ),
    "first-unique-character-index": _Spec(
        oracle=oracles.first_unique_char_index,
        cases=[
            ("leetcode", ("leetcode",), False), ("loveleetcode", ("loveleetcode",), False),
            ("aabb", ("aabb",), True), ("z", ("z",), True),
        ],
        statement=(
            "Given a string `s`, print the index of the **first character that "
            "appears exactly once**, or **-1** if none does."
        ),
        constraints=["1 ≤ s.length ≤ 10^5"],
        starter_code=(
            "import sys\ns = sys.stdin.read().rstrip('\\n')\n\n"
            "def first_uniq_char(s):\n    pass\n\nprint(first_uniq_char(s))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        title="First Unique Character Index",
    ),
    "intersection-of-two-arrays": _Spec(
        oracle=oracles.intersection_sorted,
        cases=[
            ("4 1 2 2 1 2 2 2", ([1, 2, 2, 1], [2, 2]), False),
            ("3 4 9 5 5 9 4 9 8 4", ([4, 9, 5], [9, 4, 9, 8, 4]), False),
            ("0 2 1 2", ([], [1, 2]), True),
            ("2 1 2 0", ([1, 2], []), True),
        ],
        statement=(
            "Given two arrays `nums1` and `nums2`, print their **distinct common "
            "elements**, sorted ascending."
        ),
        constraints=["0 ≤ nums1.length, nums2.length ≤ 1000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "n1=int(data[idx]);idx+=1\nnums1=list(map(int,data[idx:idx+n1]));idx+=n1\n"
            "n2=int(data[idx]);idx+=1\nnums2=list(map(int,data[idx:idx+n2]))\n\n"
            "def intersection(nums1, nums2):\n    pass\n\n"
            "print(' '.join(map(str, intersection(nums1, nums2))))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        format_output=_fmt_int_list,
        title="Intersection of Two Arrays",
    ),
    "missing-number": _Spec(
        oracle=oracles.missing_number,
        cases=[
            ("3 3 0 1", ([3, 0, 1],), False), ("2 0 1", ([0, 1],), False),
            ("9 9 6 4 2 3 5 7 0 1", ([9, 6, 4, 2, 3, 5, 7, 0, 1],), True),
            ("1 0", ([0],), True),
        ],
        statement=(
            "Given `n` distinct numbers taken from the range `[0, n]` with exactly "
            "one missing, print the **missing number**."
        ),
        constraints=["1 ≤ n ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def missing_number(nums):\n    pass\n\nprint(missing_number(nums))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        title="Missing Number",
    ),
    "majority-element-ii": _Spec(
        oracle=oracles.majority_element_ii,
        cases=[
            ("3 3 2 3", ([3, 2, 3],), False),
            ("1 1", ([1],), False),
            ("3 1 2 3", ([1, 2, 3],), True),
            ("6 1 2 1 3 1 4", ([1, 2, 1, 3, 1, 4],), True),
        ],
        statement=(
            "Given an array `nums`, print all elements occurring **more than "
            "n/3 times** (there are at most 2 such values), sorted ascending, "
            "space-separated. Print an empty line if none."
        ),
        constraints=["1 ≤ nums.length ≤ 5×10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def majority_element_ii(nums):\n    pass\n\n"
            "print(' '.join(map(str, majority_element_ii(nums))))\n"
        ),
        format_output=_fmt_int_list,
        title="Majority Element II",
    ),
    "two-sum-count-pairs": _Spec(
        oracle=oracles.two_sum_count_pairs,
        cases=[
            ("3 1 1 1 2", ([1, 1, 1], 2), False),
            ("5 1 5 3 3 3 6", ([1, 5, 3, 3, 3], 6), False),
            ("0 0 5", ([], 5), True),
            ("2 3 3 6", ([3, 3], 6), True),
        ],
        statement=(
            "Given an array `nums` and an integer `target`, print the **number "
            "of index pairs** `(i, j)` with `i < j` such that `nums[i] + nums[j] "
            "== target`."
        ),
        constraints=["0 ≤ nums.length ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def count_pairs(nums, target):\n    pass\n\nprint(count_pairs(nums, target))\n"
        ),
        title="Two Sum Count Pairs",
        function_contract=FunctionContract(
            function_name="count_pairs",
            parameters=[Parameter("nums", _INT_ARRAY), Parameter("target", _INT)],
            return_type=_INT,
        ),
    ),
    "subarray-sums-divisible-by-k": _Spec(
        oracle=oracles.subarray_sums_divisible_by_k,
        cases=[
            ("6 4 5 0 -2 -3 1 5", ([4, 5, 0, -2, -3, 1], 5), False),
            ("1 5 9", ([5], 9), False),
            ("3 1 2 3 3", ([1, 2, 3], 3), True),
            ("4 -1 2 9 -1 2", ([-1, 2, 9, -1], 2), True),
        ],
        statement=(
            "Given an array `nums` and a positive integer `k`, print the number "
            "of **contiguous subarrays** whose sum is divisible by `k`."
        ),
        constraints=["1 ≤ nums.length ≤ 3×10^4", "1 ≤ k ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def subarrays_div_by_k(nums, k):\n    pass\n\nprint(subarrays_div_by_k(nums, k))\n"
        ),
        title="Subarray Sums Divisible by K",
    ),
    "three-sum-count-triplets": _Spec(
        oracle=oracles.three_sum_count_triplets,
        cases=[
            ("6 -1 0 1 2 -1 -4", ([-1, 0, 1, 2, -1, -4],), False),
            ("3 0 1 1", ([0, 1, 1],), False),
            ("3 0 0 0", ([0, 0, 0],), True),
            ("4 1 2 3 4", ([1, 2, 3, 4],), True),
        ],
        statement=(
            "Given an array `nums`, print the number of **distinct value-"
            "triplets** `(a, b, c)` from `nums` (as a multiset, `a <= b <= c`) "
            "that sum to zero."
        ),
        constraints=["3 ≤ nums.length ≤ 1000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def three_sum_count(nums):\n    pass\n\nprint(three_sum_count(nums))\n"
        ),
        difficulty="Hard",
        estimated_minutes=30,
        title="3Sum Count Distinct Triplets",
    ),
    "container-with-most-water": _Spec(
        oracle=oracles.container_with_most_water,
        cases=[
            ("9 1 8 6 2 5 4 8 3 7", ([1, 8, 6, 2, 5, 4, 8, 3, 7],), False),
            ("2 1 1", ([1, 1],), False),
            ("2 4 3", ([4, 3],), True),
            ("5 1 2 4 3 5", ([1, 2, 4, 3, 5],), True),
        ],
        statement=(
            "Given `n` vertical lines with `heights[i]`, print the **maximum "
            "area** of water a container formed by two lines (and the x-axis "
            "between them) can hold."
        ),
        constraints=["2 ≤ heights.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nheights = list(map(int, data[1:n+1]))\n\n"
            "def max_area(heights):\n    pass\n\nprint(max_area(heights))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
        title="Container With Most Water",
    ),
}


def build_array_hashing_variant_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue

        test_plan = ARRAY_HASHING_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in array_hashing_variants_testdata.py"))
            continue
        to_input, format_output, plan_fn = test_plan
        try:
            rng = tg.problem_rng(slug)
            case_plan = plan_fn(rng)
            test_spec = tg.TestSpec(
                oracle=spec.oracle, to_input=to_input, format_output=format_output,
                function_arg_names=(
                    spec.function_contract.parameter_names if spec.function_contract else None
                ),
            )
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
            "category": "hashing",
            "algorithm_slug": None,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": "A hash map/set usually turns an O(n^2) scan into O(n)."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
            "function_contract": spec.function_contract.to_dict() if spec.function_contract else None,
            "starter_code_function": (
                {"python": _PY_ADAPTER.generate_starter(spec.function_contract)}
                if spec.function_contract else {}
            ),
        }
        problems.append((problem, test_cases))

    return problems, skipped
