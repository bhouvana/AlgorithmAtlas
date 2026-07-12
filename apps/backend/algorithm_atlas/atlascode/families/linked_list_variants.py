"""
Linked-list pattern-problem family. `origin_type = PATTERN_PROBLEM` for all
6 — no single canonical algorithm backs "linked list traversal technique" as
its own registry entry. Represented as plain arrays over stdin/stdout (the
standard online-judge simplification — no pointer structure is needed to
test two-pointer/reversal logic via a text judge).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .linked_list_variants_testdata import LINKED_LIST_TEST_PLANS
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
    "reverse-linked-list": _Spec(
        oracle=oracles.reverse_linked_list,
        cases=[
            ("5 1 2 3 4 5", ([1, 2, 3, 4, 5],), False), ("0", ([],), False),
            ("1 7", ([7],), True), ("4 3 1 4 2", ([3, 1, 4, 2],), True),
        ],
        statement="Given a singly linked list represented as an array `values`, print it **reversed**.",
        constraints=["0 ≤ values.length ≤ 5000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\n\n"
            "def reverse_list(values):\n    pass\n\n"
            "print(' '.join(map(str, reverse_list(values))))\n"
        ),
        format_output=_fmt_int_list,
        title="Reverse Linked List",
    ),
    "linked-list-cycle-detect": _Spec(
        # linked_list_has_cycle(pos) only needs pos (cycle existence doesn't
        # depend on the values) but the 40-test plan's to_input needs BOTH
        # (values, pos) to build the stdin string, and tg.build_forty calls
        # oracle(*args) with the same tuple it passes to to_input — adapt here
        # rather than changing the shared independent_oracles.py signature.
        oracle=lambda values, pos: oracles.linked_list_has_cycle(pos),
        cases=[
            ("3 1 2 3 1", (1,), False),
            ("2 1 2 -1", (-1,), False),
            ("1 1 0", (0,), True),
            ("4 1 2 3 4 -1", (-1,), True),
        ],
        statement=(
            "A singly linked list has `n` nodes with `values`; its tail's next "
            "pointer connects back to index `pos` (0-indexed), or `pos = -1` if "
            "the list is acyclic. Print `true` if the list has a **cycle**, else "
            "`false`. Solve with **O(1) extra space** (Floyd's algorithm)."
        ),
        constraints=["0 ≤ n ≤ 10^4", "-1 ≤ pos < n"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\npos = int(data[n+1])\n\n"
            "def has_cycle(values, pos):\n    pass\n\n"
            "print('true' if has_cycle(values, pos) else 'false')\n"
        ),
        format_output=_fmt_bool,
        title="Linked List Cycle Detection",
    ),
    "merge-two-sorted-lists": _Spec(
        oracle=oracles.merge_two_sorted_lists,
        cases=[
            ("3 1 2 4\n3 1 3 4", ([1, 2, 4], [1, 3, 4]), False),
            ("0\n0", ([], []), False),
            ("0\n1 0", ([], [0]), True),
            ("2 1 5\n3 0 2 6", ([1, 5], [0, 2, 6]), True),
        ],
        statement="Given two already-sorted linked lists (as arrays), print the **merged, still-sorted** list.",
        constraints=["0 ≤ list lengths ≤ 5000"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "def parse(line):\n"
            "    parts = line.split()\n    n = int(parts[0])\n"
            "    return list(map(int, parts[1:1+n]))\n"
            "a = parse(lines[0])\nb = parse(lines[1])\n\n"
            "def merge_two_lists(a, b):\n    pass\n\n"
            "print(' '.join(map(str, merge_two_lists(a, b))))\n"
        ),
        format_output=_fmt_int_list,
        title="Merge Two Sorted Lists",
    ),
    "remove-nth-from-end": _Spec(
        oracle=oracles.remove_nth_from_end,
        cases=[
            ("5 1 2 3 4 5 2", ([1, 2, 3, 4, 5], 2), False),
            ("1 1 1", ([1], 1), False),
            ("2 1 2 2", ([1, 2], 2), True),
            ("3 1 2 3 1", ([1, 2, 3], 1), True),
        ],
        statement="Given a linked list (as an array) and an integer `n`, remove the **n-th node from the end** (1-indexed) and print the resulting list.",
        constraints=["1 ≤ n ≤ values.length ≤ 5000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def remove_nth_from_end(values, k):\n    pass\n\n"
            "print(' '.join(map(str, remove_nth_from_end(values, k))))\n"
        ),
        format_output=_fmt_int_list,
        title="Remove Nth Node From End of List",
    ),
    "middle-of-linked-list": _Spec(
        oracle=oracles.middle_of_linked_list,
        cases=[
            ("5 1 2 3 4 5", ([1, 2, 3, 4, 5],), False),
            ("6 1 2 3 4 5 6", ([1, 2, 3, 4, 5, 6],), False),
            ("1 9", ([9],), True),
            ("2 1 2", ([1, 2],), True),
        ],
        statement="Given a linked list (as an array), print the value of its **middle node** (for even length, the second of the two middle nodes).",
        constraints=["1 ≤ values.length ≤ 100"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\n\n"
            "def middle_node(values):\n    pass\n\nprint(middle_node(values))\n"
        ),
        title="Middle of the Linked List",
    ),
    "palindrome-linked-list": _Spec(
        oracle=oracles.is_palindrome_linked_list,
        cases=[
            ("4 1 2 2 1", ([1, 2, 2, 1],), False), ("2 1 2", ([1, 2],), False),
            ("1 5", ([5],), True), ("3 1 2 1", ([1, 2, 1],), True),
        ],
        statement="Given a linked list (as an array), print `true` if it reads the same forwards and backwards, else `false`. Solve with **O(1) extra space**.",
        constraints=["1 ≤ values.length ≤ 5×10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nvalues = list(map(int, data[1:n+1]))\n\n"
            "def is_palindrome(values):\n    pass\n\nprint('true' if is_palindrome(values) else 'false')\n"
        ),
        format_output=_fmt_bool,
        title="Palindrome Linked List",
    ),
}


def build_linked_list_variant_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue

        test_plan = LINKED_LIST_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in linked_list_variants_testdata.py"))
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
            "category": "linked-list",
            "algorithm_slug": None,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": "Two pointers (slow/fast, or prev/curr) solve most linked-list problems in one pass."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
