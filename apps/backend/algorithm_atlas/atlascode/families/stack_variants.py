"""
Stack / monotonic-stack pattern-problem family. `origin_type =
PATTERN_PROBLEM` for all 8 — no single canonical algorithm backs "stack-based
technique" as its own registry entry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .stack_variants_testdata import STACK_VARIANT_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_bool(answer: object) -> str:
    return "true" if answer else "false"


def _fmt_int_list(answer: object) -> str:
    return " ".join(str(x) for x in answer)


def _fmt_str(answer: object) -> str:
    return str(answer)


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
    "valid-parentheses": _Spec(
        oracle=oracles.valid_parentheses,
        cases=[
            ("()[]{}", ("()[]{}",), False), ("(]", ("(]",), False),
            ("([)]", ("([)]",), True), ("{[]}", ("{[]}",), True),
        ],
        statement=(
            "Given a string `s` containing only `()[]{}`, print `true` if the "
            "brackets are well-formed (correctly nested and matched), else `false`."
        ),
        constraints=["1 ≤ s.length ≤ 10^4"],
        starter_code=(
            "import sys\ns = sys.stdin.read().strip()\n\n"
            "def is_valid(s):\n    pass\n\nprint('true' if is_valid(s) else 'false')\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        format_output=_fmt_bool,
        title="Valid Parentheses",
    ),
    "daily-temperatures": _Spec(
        oracle=oracles.daily_temperatures,
        cases=[
            ("8 73 74 75 71 69 72 76 73", ([73, 74, 75, 71, 69, 72, 76, 73],), False),
            ("4 30 40 50 60", ([30, 40, 50, 60],), False),
            ("1 50", ([50],), True),
            ("4 60 50 40 30", ([60, 50, 40, 30],), True),
        ],
        statement=(
            "Given daily temperatures `temps`, print for each day the number of "
            "days to wait for a **strictly warmer** temperature, or `0` if none."
        ),
        constraints=["1 ≤ temps.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\ntemps = list(map(int, data[1:n+1]))\n\n"
            "def daily_temperatures(temps):\n    pass\n\n"
            "print(' '.join(map(str, daily_temperatures(temps))))\n"
        ),
        format_output=_fmt_int_list,
        title="Daily Temperatures",
    ),
    "next-greater-element": _Spec(
        oracle=oracles.next_greater_element,
        cases=[
            ("3 4 1 2", ([4, 1, 2],), False), ("4 1 3 4 2", ([1, 3, 4, 2],), False),
            ("1 5", ([5],), True), ("3 2 1 3", ([2, 1, 3],), True),
        ],
        statement=(
            "Given an array `nums`, print for each element the **next greater "
            "element to its right**, or `-1` if none exists (non-circular)."
        ),
        constraints=["1 ≤ nums.length ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
            "def next_greater_element(nums):\n    pass\n\n"
            "print(' '.join(map(str, next_greater_element(nums))))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
        format_output=_fmt_int_list,
        title="Next Greater Element",
    ),
    "largest-rectangle-in-histogram": _Spec(
        oracle=oracles.largest_rectangle_in_histogram,
        cases=[
            ("6 2 1 5 6 2 3", ([2, 1, 5, 6, 2, 3],), False),
            ("2 2 4", ([2, 4],), False),
            ("1 5", ([5],), True),
            ("4 1 1 1 1", ([1, 1, 1, 1],), True),
        ],
        statement=(
            "Given bar heights `heights` of a histogram (width 1 each), print "
            "the area of the **largest rectangle** that fits within the histogram."
        ),
        constraints=["1 ≤ heights.length ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nheights = list(map(int, data[1:n+1]))\n\n"
            "def largest_rectangle_area(heights):\n    pass\n\n"
            "print(largest_rectangle_area(heights))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
        title="Largest Rectangle in Histogram",
    ),
    "min-stack-simulation": _Spec(
        oracle=oracles.min_stack_simulate,
        cases=[
            (
                "5\nPUSH 5\nPUSH 2\nPUSH 7\nPOP\nPUSH 1",
                ([("PUSH", 5), ("PUSH", 2), ("PUSH", 7), ("POP", None), ("PUSH", 1)],),
                False,
            ),
            ("2\nPUSH 3\nPUSH 3", ([("PUSH", 3), ("PUSH", 3)],), False),
            ("3\nPUSH -1\nPUSH -2\nPUSH 0", ([("PUSH", -1), ("PUSH", -2), ("PUSH", 0)],), True),
            (
                "4\nPUSH 4\nPUSH 1\nPOP\nPUSH 2",
                ([("PUSH", 4), ("PUSH", 1), ("POP", None), ("PUSH", 2)],),
                True,
            ),
        ],
        statement=(
            "Simulate `n` operations on a stack, each either `PUSH x` or `POP`. "
            "After every `PUSH`, print the **current minimum** of the stack "
            "(space-separated, in order); `POP` produces no output."
        ),
        constraints=["1 ≤ n ≤ 10^4"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "n = int(lines[0])\nops = []\n"
            "for i in range(1, n+1):\n"
            "    parts = lines[i].split()\n"
            "    ops.append((parts[0], int(parts[1])) if len(parts) > 1 else (parts[0], None))\n\n"
            "def min_stack_simulate(ops):\n    pass\n\n"
            "print(' '.join(map(str, min_stack_simulate(ops))))\n"
        ),
        format_output=_fmt_int_list,
        title="Min Stack Simulation",
    ),
    "evaluate-reverse-polish-notation": _Spec(
        oracle=oracles.evaluate_rpn,
        cases=[
            ("5 2 1 + 3 *", (["2", "1", "+", "3", "*"],), False),
            ("5 4 13 5 / +", (["4", "13", "5", "/", "+"],), False),
            ("1 5", (["5"],), True),
            ("3 10 2 /", (["10", "2", "/"],), True),
        ],
        statement=(
            "Given a Reverse Polish Notation expression as `n` space-separated "
            "tokens, print its integer result. Division truncates toward zero."
        ),
        constraints=["1 ≤ n ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\ntokens = data[1:1+n]\n\n"
            "def eval_rpn(tokens):\n    pass\n\nprint(eval_rpn(tokens))\n"
        ),
        title="Evaluate Reverse Polish Notation",
    ),
    "remove-k-digits": _Spec(
        oracle=oracles.remove_k_digits,
        cases=[
            ("1432219 3", ("1432219", 3), False), ("10200 1", ("10200", 1), False),
            ("10 2", ("10", 2), True), ("9 1", ("9", 1), True),
        ],
        statement=(
            "Given a non-negative integer `num` as a string and an integer `k`, "
            "print the **smallest possible number** (no leading zeros, as a "
            "string) after removing exactly `k` digits."
        ),
        constraints=["1 ≤ num.length ≤ 10^5", "0 ≤ k ≤ num.length"],
        starter_code=(
            "import sys\nline = sys.stdin.read().rstrip('\\n')\nnum, k = line.rsplit(' ', 1)\nk = int(k)\n\n"
            "def remove_k_digits(num, k):\n    pass\n\nprint(remove_k_digits(num, k))\n"
        ),
        format_output=_fmt_str,
        title="Remove K Digits",
    ),
    "trapping-rain-water": _Spec(
        oracle=oracles.trapping_rain_water,
        cases=[
            ("12 0 1 0 2 1 0 1 3 2 1 2 1", ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],), False),
            ("6 4 2 0 3 2 5", ([4, 2, 0, 3, 2, 5],), False),
            ("1 5", ([5],), True),
            ("3 3 0 3", ([3, 0, 3],), True),
        ],
        statement=(
            "Given bar heights `heights`, print the total amount of **water "
            "trapped** between the bars after raining."
        ),
        constraints=["1 ≤ heights.length ≤ 2×10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nheights = list(map(int, data[1:n+1]))\n\n"
            "def trap(heights):\n    pass\n\nprint(trap(heights))\n"
        ),
        difficulty="Hard",
        estimated_minutes=30,
        title="Trapping Rain Water",
    ),
}


def build_stack_variant_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue

        test_plan = STACK_VARIANT_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in stack_variants_testdata.py"))
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
            "category": "stack",
            "algorithm_slug": None,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": "A stack tracks pending elements until a condition resolves them."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
