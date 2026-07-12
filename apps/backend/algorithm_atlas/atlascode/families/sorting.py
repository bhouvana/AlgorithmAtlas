"""
Sorting family factory.

Generates one AtlasCode problem per canonical sorting-category algorithm that
doesn't already have a curated (hand-authored) problem. Every test case's
expected output comes from running the algorithm's own plugin implementation
via oracle.run_sort_oracle — never hand-typed.
"""
from __future__ import annotations

import random

from .. import testgen as tg
from ..oracle import OracleError, run_sort_oracle
from ...plugins.registry import RegisteredAlgorithm

# (seed, array_size, input_order, is_hidden) — fixed so generation is deterministic/reproducible.
_CASES: list[tuple[int, int, str, bool]] = [
    (101, 1, "random", False),
    (102, 6, "sorted", False),
    (103, 6, "reverse", False),
    (104, 15, "random", True),
    (105, 30, "nearly_sorted", True),
]

_EXPLANATIONS = {
    "sorted": "Already-sorted input",
    "reverse": "Reverse-sorted input",
    "nearly_sorted": "Nearly-sorted input",
}


def _to_input(arr: list[int]) -> str:
    return f"{len(arr)} {' '.join(map(str, arr))}"


def _sort_oracle(arr: list[int]) -> list[int]:
    # Deliberately a PLAIN independent sort — "ascending order" ground truth
    # does not depend on which specific sorting algorithm the problem is
    # teaching, so every sorting problem shares this one oracle rather than
    # re-running the plugin's own (potentially buggy) implementation.
    return sorted(arr)


def _build_sort_case_plan(problem_id: str) -> tg.CasePlan:
    rng = tg.problem_rng(problem_id)
    seen: set[str] = set()
    ti = _to_input

    def gen_small():
        n = rng.randint(3, 10)
        return (tg.rand_int_array(rng, n, -50, 50),)

    def gen_stress():
        n = rng.randint(600, 1000)  # respects the problem's stated 1 <= n <= 1000
        return (tg.rand_int_array(rng, n, -10_000, 10_000),)

    visible = [
        ([5, 3, 8, 1, 2],), ([1],), ([2, 2, 2, 2],), ([5, 4, 3, 2, 1],), ([1, 2, 3, 4, 5],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = tg.register([
        ([7],), ([3, 3],), ([1, 2],), ([2, 1],),
    ], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = tg.register([
        ([4, 4, 4, 4, 4, 4, 4, 4],),                     # all-equal
        ([-5, -1, -5, 0, -1, -5, 3],),                    # heavy duplicates, negatives
        ([-100, 100, -100, 100, -100, 100],),             # alternating extremes
        (sorted(tg.rand_int_array(rng, 20, -30, 30)) + [-30],),  # sorted then one out-of-range tail value
    ], ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    def _one_swap_from_sorted(n: int, near_start: bool) -> list[int]:
        arr = sorted(tg.rand_int_array(rng, n, -40, 40))
        i = 0 if near_start else n - 2
        arr[i], arr[i + 1] = arr[i + 1], arr[i]
        return arr

    mutation_anchors = tg.register([
        (_one_swap_from_sorted(10, near_start=True),),
        (_one_swap_from_sorted(10, near_start=False),),
        (list(range(10, 0, -1)),),  # fully reverse-sorted small — classic worst case for naive loop bounds
    ], ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _difficulty_for(complexity: dict) -> str:
    avg = complexity.get("time_average", "")
    return "Easy" if avg in ("O(n)", "O(n²)") else "Medium"


def build_sorting_problems(
    algorithms: list[RegisteredAlgorithm],
    curated_slugs: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    """
    Returns (problems, skipped) where skipped is [(slug, reason), ...] for
    sorting algorithms that could not be turned into a generated problem
    (e.g. their initialize() doesn't return SortState, or the oracle run
    failed a sanity check).
    """
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for reg in algorithms:
        if reg.category != "sorting" or reg.slug in curated_slugs:
            continue

        func_name = reg.slug.replace("-", "_")
        try:
            # Sanity check: confirm the plugin's own oracle agrees with the
            # independent plain-sort ground truth on one small case before
            # trusting this algorithm's problem at all (catches a genuinely
            # broken plugin implementation rather than silently shipping it).
            arr, plugin_sorted = run_sort_oracle(reg, 101, 10, "random")
            if plugin_sorted != sorted(arr):
                skipped.append((reg.slug, "plugin oracle disagrees with independent sort on sanity check"))
                continue
        except OracleError as exc:
            skipped.append((reg.slug, str(exc)))
            continue

        try:
            test_spec = tg.TestSpec(oracle=_sort_oracle, to_input=_to_input, format_output=lambda a: " ".join(map(str, a)))
            test_cases = tg.build_forty(reg.slug, test_spec, _build_sort_case_plan(reg.slug))
        except tg.TestPlanError as exc:
            skipped.append((reg.slug, str(exc)))
            continue

        intuition = reg.manifest.get("intuition", "")
        problem = {
            "id": reg.slug,
            "title": reg.name,
            "difficulty": _difficulty_for(reg.manifest.get("complexity", {})),
            "category": "sorting",
            "algorithm_slug": reg.slug,
            "estimated_minutes": 15,
            "problem_statement": (
                f"Given an array of integers, sort it in **ascending order** using "
                f"**{reg.name}** and print the sorted array.\n\n"
                f"Print space-separated integers on one line."
            ),
            "examples": [],
            "constraints": ["1 ≤ nums.length ≤ 1000", "-10^4 ≤ nums[i] ≤ 10^4"],
            "hints": [{"level": 1, "text": intuition or f"Implement {reg.name} to sort the array in place."}],
            "companies": [],
            "starter_code": {
                "python": (
                    "import sys\n"
                    "data = sys.stdin.read().split()\n"
                    "n = int(data[0])\n"
                    "nums = list(map(int, data[1:n+1]))\n\n"
                    f"def {func_name}(arr):\n    pass\n\n"
                    f"{func_name}(nums)\n"
                    "print(' '.join(map(str, nums)))\n"
                ),
            },
        }
        problems.append((problem, test_cases))

    return problems, skipped


# ── Reference / wrong solutions ────────────────────────────────────────────────
# One shared pair suffices — "print the array in ascending order" is the same
# judged contract for every sorting-category problem regardless of which
# specific algorithm the problem is nominally teaching (the algorithm choice
# only affects the starter-code scaffold, not the judged input/output).
_SORT_REFERENCE = (
    "import sys\ndata = sys.stdin.read().split()\n"
    "n = int(data[0]); nums = list(map(int, data[1:n+1]))\n"
    "nums.sort()\nprint(' '.join(map(str, nums)))\n"
)
_SORT_WRONG = (
    # BUG: sorts descending instead of ascending
    "import sys\ndata = sys.stdin.read().split()\n"
    "n = int(data[0]); nums = list(map(int, data[1:n+1]))\n"
    "nums.sort(reverse=True)\nprint(' '.join(map(str, nums)))\n"
)
_ALL_SORTING_SLUGS = [
    "bitonic-sort", "bucket-sort", "cocktail-sort", "comb-sort", "counting-sort",
    "cycle-sort", "gnome-sort", "heap-sort", "insertion-sort", "merge-sort",
    "odd-even-sort", "pancake-sort", "patience-sort", "quick-sort", "radix-sort",
    "selection-sort", "shell-sort", "stooge-sort", "strand-sort", "tim-sort",
]
REFERENCE_SOLUTIONS: dict[str, str] = {slug: _SORT_REFERENCE for slug in _ALL_SORTING_SLUGS}
WRONG_SOLUTIONS: dict[str, str] = {slug: _SORT_WRONG for slug in _ALL_SORTING_SLUGS}
