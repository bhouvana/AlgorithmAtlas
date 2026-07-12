"""
Greedy family factory — canonical algorithm coverage for 8 of the 9
uncurated `greedy` algorithms. Every contract returns a unique scalar/list;
e.g. `stable-matching` outputs the man-optimal Gale-Shapley matching, which
is a deterministic function of the input preference lists (not "a" stable
matching among several) — safe for exact-match STANDARD_JUDGE.
`fractional-knapsack` is the only float-valued output in this family;
formatted to 2 decimal places to avoid float-noise judging brittleness.

Deferred: `huffman-with-decode` — its contract (decode a bitstream given a
Huffman tree/code table) needs a canonical tree-construction tie-break
decision shared with `huffman-coding` before it can ship without risking a
near-duplicate of that problem; not resolved this batch.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .greedy_testdata import GREEDY_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_float2(answer: object) -> str:
    return f"{answer:.2f}"


def _fmt_int_list(answer: object) -> str:
    return " ".join(str(x) for x in answer)


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
    "activity-selection": _Spec(
        oracle=oracles.activity_selection_max_count,
        cases=[
            ("6 1 3 0 5 8 5 2 4 6 7 9 9", ([1, 3, 0, 5, 8, 5], [2, 4, 6, 7, 9, 9]), False),
            ("3 1 2 3 2 3 4", ([1, 2, 3], [2, 3, 4]), False),
            ("1 5 10", ([5], [10]), True),
            ("4 1 1 1 1 2 2 2 2", ([1, 1, 1, 1], [2, 2, 2, 2]), True),
        ],
        statement=(
            "Given `n` activities with `start[i]` and `end[i]` times, print the "
            "**maximum number of non-overlapping activities** a single person can "
            "attend (an activity ending at t and another starting at t do not overlap)."
        ),
        constraints=["1 ≤ n ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "n=int(data[idx]);idx+=1\nstarts=list(map(int,data[idx:idx+n]));idx+=n\n"
            "ends=list(map(int,data[idx:idx+n]))\n\n"
            "def max_activities(starts, ends):\n    pass\n\nprint(max_activities(starts, ends))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
    ),
    "fractional-knapsack": _Spec(
        oracle=oracles.fractional_knapsack_max_value,
        cases=[
            ("3 10 20 30 60 100 120 50", ([10, 20, 30], [60, 100, 120], 50), False),
            ("1 10 60 20", ([10], [60], 20), False),
            ("2 5 5 10 10 0", ([5, 5], [10, 10], 0), True),
            ("3 2 3 4 10 15 20 5", ([2, 3, 4], [10, 15, 20], 5), True),
        ],
        statement=(
            "Given `n` items with `weights` and `values`, and a knapsack `capacity`, "
            "print the **maximum total value** achievable, where fractional amounts "
            "of an item may be taken. Print the answer rounded to **2 decimal places**."
        ),
        constraints=["1 ≤ n ≤ 1000", "1 ≤ weights[i] ≤ 1000", "0 ≤ values[i] ≤ 1000", "0 ≤ capacity ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "n=int(data[idx]);idx+=1\nweights=list(map(int,data[idx:idx+n]));idx+=n\n"
            "values=list(map(int,data[idx:idx+n]));idx+=n\ncapacity=int(data[idx])\n\n"
            "def fractional_knapsack(weights, values, capacity):\n    pass\n\n"
            "print(f'{fractional_knapsack(weights, values, capacity):.2f}')\n"
        ),
        format_output=_fmt_float2,
    ),
    "gas-station": _Spec(
        oracle=oracles.gas_station_start_index,
        cases=[
            ("5 1 2 3 4 5 3 4 5 1 2", ([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), False),
            ("3 2 3 4 3 4 3", ([2, 3, 4], [3, 4, 3]), False),
            ("1 5 5", ([5], [5]), True),
            ("2 1 1 2 2", ([1, 1], [2, 2]), True),
        ],
        statement=(
            "There are `n` gas stations in a circle; `gas[i]` fuel is available at "
            "station i, and it costs `cost[i]` to travel to the next station. Print "
            "the **starting station index** from which a car with an empty tank can "
            "complete the full circuit, or **-1** if impossible. (Guaranteed unique "
            "if it exists.)"
        ),
        constraints=["1 ≤ n ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "n=int(data[idx]);idx+=1\ngas=list(map(int,data[idx:idx+n]));idx+=n\n"
            "cost=list(map(int,data[idx:idx+n]))\n\n"
            "def can_complete_circuit(gas, cost):\n    pass\n\nprint(can_complete_circuit(gas, cost))\n"
        ),
    ),
    "huffman-coding": _Spec(
        oracle=oracles.huffman_total_encoded_length,
        cases=[
            ("6 5 9 12 13 16 45", ([5, 9, 12, 13, 16, 45],), False),
            ("2 1 1", ([1, 1],), False),
            ("2 1 100", ([1, 100],), True),
            ("4 1 1 1 1", ([1, 1, 1, 1],), True),
        ],
        statement=(
            "Given the frequencies of `n` symbols, print the **total weighted path "
            "length** (sum of frequency × code length) of an optimal Huffman "
            "encoding — the total number of bits used to encode the whole message."
        ),
        constraints=["2 ≤ n ≤ 1000", "1 ≤ freq[i] ≤ 10^6"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nfreqs = list(map(int, data[1:n+1]))\n\n"
            "def huffman_total_length(freqs):\n    pass\n\nprint(huffman_total_length(freqs))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
    ),
    "job-scheduling": _Spec(
        oracle=oracles.job_scheduling_max_profit,
        cases=[
            ("5 2 1 2 1 3 100 19 27 25 15", ([2, 1, 2, 1, 3], [100, 19, 27, 25, 15]), False),
            ("3 1 1 1 5 3 8", ([1, 1, 1], [5, 3, 8]), False),
            ("1 1 10", ([1], [10]), True),
            ("2 1 1 10 20", ([1, 1], [10, 20]), True),
        ],
        statement=(
            "Given `n` jobs, each taking one unit of time with a `deadline` (job "
            "must finish by this time slot, 1-indexed) and a `profit`, print the "
            "**maximum total profit** achievable scheduling a subset of jobs "
            "(only one job runs per time slot)."
        ),
        constraints=["1 ≤ n ≤ 1000", "1 ≤ deadline[i] ≤ n", "0 ≤ profit[i] ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "n=int(data[idx]);idx+=1\ndeadlines=list(map(int,data[idx:idx+n]));idx+=n\n"
            "profits=list(map(int,data[idx:idx+n]))\n\n"
            "def job_scheduling(deadlines, profits):\n    pass\n\nprint(job_scheduling(deadlines, profits))\n"
        ),
    ),
    "meeting-rooms": _Spec(
        oracle=oracles.meeting_rooms_min_count,
        cases=[
            ("3 0 5 15 10 20 30", ([0, 5, 15], [10, 20, 30]), False),
            ("3 7 7 7 10 10 10", ([7, 7, 7], [10, 10, 10]), False),
            ("1 1 2", ([1], [2]), True),
            ("2 1 2 2 3", ([1, 2], [2, 3]), True),
        ],
        statement=(
            "Given `n` meetings with `start` and `end` times, print the **minimum "
            "number of meeting rooms** required so no two overlapping meetings "
            "share a room."
        ),
        constraints=["1 ≤ n ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "n=int(data[idx]);idx+=1\nstarts=list(map(int,data[idx:idx+n]));idx+=n\n"
            "ends=list(map(int,data[idx:idx+n]))\n\n"
            "def min_meeting_rooms(starts, ends):\n    pass\n\nprint(min_meeting_rooms(starts, ends))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
    ),
    "stable-matching": _Spec(
        oracle=oracles.stable_matching_gale_shapley,
        cases=[
            (
                "3\n0 1 2\n1 0 2\n2 0 1\n1 0 2\n2 1 0\n0 1 2",
                ([[0, 1, 2], [1, 0, 2], [2, 0, 1]], [[1, 0, 2], [2, 1, 0], [0, 1, 2]]),
                False,
            ),
            ("1\n0\n0", ([[0]], [[0]]), False),
            (
                "2\n0 1\n0 1\n0 1\n0 1",
                ([[0, 1], [0, 1]], [[0, 1], [0, 1]]),
                True,
            ),
            (
                "2\n1 0\n0 1\n1 0\n0 1",
                ([[1, 0], [0, 1]], [[1, 0], [0, 1]]),
                True,
            ),
        ],
        statement=(
            "Given `n` men and `n` women, each with a fully-ranked preference list "
            "over the other side (`men_prefs[i]`/`women_prefs[i]`, most preferred "
            "first), print the **man-optimal stable matching** produced by the "
            "Gale-Shapley algorithm (men propose): for each man `0..n-1`, print "
            "his assigned woman's index, space-separated."
        ),
        constraints=["1 ≤ n ≤ 100"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "n = int(lines[0])\n"
            "men_prefs = [list(map(int, lines[1+i].split())) for i in range(n)]\n"
            "women_prefs = [list(map(int, lines[1+n+i].split())) for i in range(n)]\n\n"
            "def stable_matching(men_prefs, women_prefs):\n    pass\n\n"
            "print(' '.join(map(str, stable_matching(men_prefs, women_prefs))))\n"
        ),
        difficulty="Hard",
        estimated_minutes=40,
        format_output=_fmt_int_list,
    ),
    "task-scheduler": _Spec(
        oracle=oracles.task_scheduler_min_intervals,
        cases=[
            ("2 3 3 2", ([3, 3], 2), False),
            ("3 1 1 1 0", ([1, 1, 1], 0), False),
            ("4 3 3 3 1 2", ([3, 3, 3, 1], 2), True),
            ("3 3 3 3 3", ([3, 3, 3], 3), True),
        ],
        statement=(
            "Given the counts of `n` task types and a `cooldown` (same task type "
            "must wait `cooldown` intervals before repeating), print the "
            "**minimum total number of intervals** (including idle slots) needed "
            "to run all tasks."
        ),
        constraints=["1 ≤ n ≤ 26", "1 ≤ count[i] ≤ 100", "0 ≤ cooldown ≤ 100"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\ncounts = list(map(int, data[1:n+1]))\ncooldown = int(data[n+1])\n\n"
            "def least_interval(counts, cooldown):\n    pass\n\nprint(least_interval(counts, cooldown))\n"
        ),
    ),
}


def build_greedy_problems(
    algorithms: list[RegisteredAlgorithm],
    curated_slugs: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    by_slug = {r.slug: r for r in algorithms if r.category == "greedy"}
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in curated_slugs:
            continue
        reg = by_slug.get(slug)
        if reg is None:
            skipped.append((slug, "not found in canonical registry"))
            continue

        test_plan = GREEDY_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in greedy_testdata.py"))
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
            "category": "greedy",
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
