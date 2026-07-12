"""
Searching family factory.

Generates one AtlasCode problem per canonical searching-category algorithm
whose plugin uses the uniform SearchState contract (array + target + found_at)
and doesn't already have a curated problem. Algorithms in this category that
use a different state shape (e.g. bloom-filter, skip-list, peak-element —
which reuse SortState for a non-index-search contract) are reported as
skipped rather than forced into this contract.
"""
from __future__ import annotations

import bisect

from .. import testgen as tg
from ..oracle import OracleError, run_search_oracle
from ...plugins.registry import RegisteredAlgorithm

# (seed, array_size, is_hidden)
_CASES: list[tuple[int, int, bool]] = [
    (201, 8, False),
    (202, 12, False),
    (203, 20, True),
    (204, 35, True),
]


def _to_input(nums: list[int], target: int) -> str:
    return f"{len(nums)} {' '.join(map(str, nums))} {target}"


def _search_oracle(nums: list[int], target: int) -> int:
    # Independent ground truth via bisect — nums are always generated
    # SORTED + DISTINCT below specifically so "the" index is unambiguous
    # regardless of which search algorithm variant is being taught.
    i = bisect.bisect_left(nums, target)
    return i if i < len(nums) and nums[i] == target else -1


def _build_search_case_plan(problem_id: str) -> tg.CasePlan:
    rng = tg.problem_rng(problem_id)
    seen: set[str] = set()
    ti = _to_input

    def _sorted_distinct(n: int, lo: int, hi: int) -> list[int]:
        return sorted(tg.rand_distinct_int_array(rng, min(n, hi - lo + 1), lo, hi))

    def gen_small():
        arr = _sorted_distinct(rng.randint(3, 10), -50, 50)
        target = rng.choice(arr) if rng.random() < 0.6 else rng.randint(-60, 60)
        return (arr, target)

    def gen_stress():
        arr = _sorted_distinct(rng.randint(500, 1000), -50_000, 50_000)
        target = rng.choice(arr) if rng.random() < 0.5 else rng.randint(-60_000, 60_000)
        return (arr, target)

    visible = [
        ([-1, 0, 3, 5, 9, 12], 9), ([-1, 0, 3, 5, 9, 12], 2), ([5], 5), ([5], -5), ([1, 2, 3, 4, 5], 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = tg.register([
        ([1], 1), ([1], 0), ([1, 2], 1), ([1, 2], 2),
    ], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    arr20 = _sorted_distinct(20, -100, 100)
    adversarial_anchors = tg.register([
        (arr20, arr20[0]),           # target is the first element
        (arr20, arr20[-1]),          # target is the last element
        (arr20, arr20[len(arr20) // 2]),  # target is the exact middle element
        (arr20, min(arr20) - 1),     # target smaller than everything (below range)
    ], ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = tg.register([
        ([1, 3], 3),    # target at the very last valid index — off-by-one trap
        ([1, 3], 0),    # target below range — must not wrap to a valid index
        ([1, 3], 4),    # target above range
    ], ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def build_searching_problems(
    algorithms: list[RegisteredAlgorithm],
    curated_slugs: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for reg in algorithms:
        if reg.category != "searching" or reg.slug in curated_slugs:
            continue

        func_name = reg.slug.replace("-", "_")
        try:
            # Sanity check against the plugin's own oracle on one small,
            # distinct-valued case before trusting this algorithm at all.
            arr, target, plugin_found = run_search_oracle(reg, 201, 10)
            if len(set(arr)) == len(arr) and plugin_found != _search_oracle(sorted(arr), target):
                skipped.append((reg.slug, "plugin oracle disagrees with independent bisect search on sanity check"))
                continue
        except OracleError as exc:
            skipped.append((reg.slug, str(exc)))
            continue

        try:
            test_spec = tg.TestSpec(oracle=_search_oracle, to_input=_to_input, format_output=str)
            test_cases = tg.build_forty(reg.slug, test_spec, _build_search_case_plan(reg.slug))
        except tg.TestPlanError as exc:
            skipped.append((reg.slug, str(exc)))
            continue

        intuition = reg.manifest.get("intuition", "")
        problem = {
            "id": reg.slug,
            "title": reg.name,
            "difficulty": "Easy",
            "category": "searching",
            "algorithm_slug": reg.slug,
            "estimated_minutes": 15,
            "problem_statement": (
                f"Given a sorted array of integers `nums` and a target integer `target`, "
                f"return the **index** of `target` using **{reg.name}**, or **-1** if "
                f"it is not present."
            ),
            "examples": [],
            "constraints": ["1 ≤ nums.length ≤ 1000", "nums is sorted in ascending order"],
            "hints": [{"level": 1, "text": intuition or f"Implement {reg.name}."}],
            "companies": [],
            "starter_code": {
                "python": (
                    "import sys\n"
                    "data = sys.stdin.read().split()\n"
                    "n = int(data[0])\n"
                    "nums = list(map(int, data[1:n+1]))\n"
                    "target = int(data[n+1])\n\n"
                    f"def {func_name}(nums, target):\n    pass\n\n"
                    f"print({func_name}(nums, target))\n"
                ),
            },
        }
        problems.append((problem, test_cases))

    return problems, skipped


# ── Reference / wrong solutions ────────────────────────────────────────────────
# One shared pair suffices — every searching-category problem here judges the
# same contract (sorted+distinct array, print index of target or -1).
_SEARCH_REFERENCE = (
    "import sys\ndata = sys.stdin.read().split()\n"
    "n = int(data[0]); nums = list(map(int, data[1:n+1])); target = int(data[n+1])\n"
    "lo, hi, ans = 0, n - 1, -1\n"
    "while lo <= hi:\n"
    "    mid = (lo + hi) // 2\n"
    "    if nums[mid] == target:\n        ans = mid; break\n"
    "    elif nums[mid] < target:\n        lo = mid + 1\n"
    "    else:\n        hi = mid - 1\n"
    "print(ans)\n"
)
_SEARCH_WRONG = (
    # BUG: uses strict `<` instead of `<=`, never checks the case lo == hi
    "import sys\ndata = sys.stdin.read().split()\n"
    "n = int(data[0]); nums = list(map(int, data[1:n+1])); target = int(data[n+1])\n"
    "lo, hi, ans = 0, n - 1, -1\n"
    "while lo < hi:\n"
    "    mid = (lo + hi) // 2\n"
    "    if nums[mid] == target:\n        ans = mid; break\n"
    "    elif nums[mid] < target:\n        lo = mid + 1\n"
    "    else:\n        hi = mid - 1\n"
    "print(ans)\n"
)
_ALL_SEARCHING_SLUGS = ["exponential-search", "fibonacci-search", "interpolation-search", "jump-search", "ternary-search"]
REFERENCE_SOLUTIONS: dict[str, str] = {slug: _SEARCH_REFERENCE for slug in _ALL_SEARCHING_SLUGS}
WRONG_SOLUTIONS: dict[str, str] = {slug: _SEARCH_WRONG for slug in _ALL_SEARCHING_SLUGS}
