"""
Bit-manipulation pattern-problem family. `origin_type = PATTERN_PROBLEM` for
all 8 — no single canonical algorithm backs "bit trick" as its own registry
entry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .bit_manipulation_variants_testdata import BIT_MANIPULATION_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


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
    difficulty: str = "Easy"
    estimated_minutes: int = 15
    format_output: Callable[[object], str] = _fmt_int


_SPECS: dict[str, _Spec] = {
    "single-number": _Spec(
        oracle=oracles.single_number,
        cases=[
            ("3 2 2 1", ([2, 2, 1],), False), ("5 4 1 2 1 2", ([4, 1, 2, 1, 2],), False),
            ("1 7", ([7],), True), ("5 0 0 3 3 9", ([0, 0, 3, 3, 9],), True),
        ],
        statement=(
            "Given an array where every element appears exactly **twice** "
            "except one, print that single element, in O(n) time and O(1) space."
        ),
        constraints=["1 ≤ nums.length ≤ 3×10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def single_number(nums):\n    pass\n\nprint(single_number(nums))\n"
        ),
        title="Single Number",
    ),
    "single-number-ii": _Spec(
        oracle=oracles.single_number_ii,
        cases=[
            ("4 2 2 3 2", ([2, 2, 3, 2],), False),
            ("7 0 1 0 1 0 1 99", ([0, 1, 0, 1, 0, 1, 99],), False),
            ("1 5", ([5],), True),
            ("7 6 6 6 8 8 8 15", ([6, 6, 6, 8, 8, 8, 15],), True),
        ],
        statement=(
            "Given an array where every element appears exactly **three times** "
            "except one, print that single element, in O(n) time and O(1) space."
        ),
        constraints=["1 ≤ nums.length ≤ 3×10^4", "0 ≤ nums[i] < 2^31"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def single_number(nums):\n    pass\n\nprint(single_number(nums))\n"
        ),
        difficulty="Medium",
        estimated_minutes=25,
        title="Single Number II",
    ),
    "counting-bits": _Spec(
        oracle=oracles.counting_bits,
        cases=[
            ("2", (2,), False), ("5", (5,), False),
            ("0", (0,), True), ("8", (8,), True),
        ],
        statement=(
            "Given `n`, print an array where the `i`-th value (for `i` from `0` "
            "to `n`) is the number of `1` bits in the binary representation of `i`."
        ),
        constraints=["0 ≤ n ≤ 10^5"],
        starter_code=(
            "import sys\nn = int(sys.stdin.read().strip())\n\n"
            "def count_bits(n):\n    pass\n\nprint(' '.join(map(str, count_bits(n))))\n"
        ),
        format_output=_fmt_int_list,
        title="Counting Bits",
    ),
    "reverse-bits": _Spec(
        oracle=oracles.reverse_bits_32,
        cases=[
            ("43261596", (43261596,), False), ("0", (0,), False),
            ("1", (1,), True), ("4294967293", (4294967293,), True),
        ],
        statement=(
            "Given a 32-bit unsigned integer `n`, print the integer obtained by "
            "**reversing its bits**."
        ),
        constraints=["0 ≤ n < 2^32"],
        starter_code=(
            "import sys\nn = int(sys.stdin.read().strip())\n\n"
            "def reverse_bits(n):\n    pass\n\nprint(reverse_bits(n))\n"
        ),
        title="Reverse Bits",
    ),
    "hamming-distance": _Spec(
        oracle=oracles.hamming_distance,
        cases=[
            ("1 4", (1, 4), False), ("3 1", (3, 1), False),
            ("0 0", (0, 0), True), ("15 0", (15, 0), True),
        ],
        statement=(
            "Given two integers `x` and `y`, print the **Hamming distance** — "
            "the number of bit positions at which they differ."
        ),
        constraints=["0 ≤ x, y ≤ 2^31 - 1"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "x, y = int(data[0]), int(data[1])\n\n"
            "def hamming_distance(x, y):\n    pass\n\nprint(hamming_distance(x, y))\n"
        ),
        title="Hamming Distance",
    ),
    "power-of-two": _Spec(
        oracle=oracles.is_power_of_two,
        cases=[
            ("1", (1,), False), ("16", (16,), False),
            ("3", (3,), True), ("0", (0,), True),
        ],
        statement="Given an integer `n`, print `true` if `n` is a power of two, else `false`.",
        constraints=["-2^31 ≤ n ≤ 2^31 - 1"],
        starter_code=(
            "import sys\nn = int(sys.stdin.read().strip())\n\n"
            "def is_power_of_two(n):\n    pass\n\nprint('true' if is_power_of_two(n) else 'false')\n"
        ),
        format_output=_fmt_bool,
        title="Power of Two",
    ),
    "number-of-1-bits": _Spec(
        oracle=oracles.count_set_bits,
        cases=[
            ("11", (11,), False), ("128", (128,), False),
            ("0", (0,), True), ("2147483647", (2147483647,), True),
        ],
        statement="Given a non-negative integer `n`, print the number of `1` bits in its binary representation.",
        constraints=["0 ≤ n ≤ 2^31 - 1"],
        starter_code=(
            "import sys\nn = int(sys.stdin.read().strip())\n\n"
            "def hamming_weight(n):\n    pass\n\nprint(hamming_weight(n))\n"
        ),
        title="Number of 1 Bits",
    ),
    "maximum-xor-of-two-numbers": _Spec(
        oracle=oracles.max_xor_of_two_numbers,
        cases=[
            ("6 3 10 5 25 2 8", ([3, 10, 5, 25, 2, 8],), False),
            ("2 0 1", ([0, 1],), False),
            ("2 0 0", ([0, 0],), True),
            ("4 1 2 3 4", ([1, 2, 3, 4],), True),
        ],
        statement=(
            "Given an array `nums`, print the **maximum XOR** of any two "
            "elements. Solve in O(n) using a bitwise trie."
        ),
        constraints=["2 ≤ nums.length ≤ 2×10^5", "0 ≤ nums[i] < 2^31"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def find_max_xor(nums):\n    pass\n\nprint(find_max_xor(nums))\n"
        ),
        difficulty="Hard",
        estimated_minutes=30,
        title="Maximum XOR of Two Numbers",
    ),
}


def build_bit_manipulation_variant_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue

        test_plan = BIT_MANIPULATION_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in bit_manipulation_variants_testdata.py"))
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
            "category": "bit-manipulation",
            "algorithm_slug": None,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": "Think in terms of XOR, AND, and shifting rather than arithmetic."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
