"""
Famous arrays/matrix pattern-problem family.

Like `sliding_window_variants.py`, none of these 9 problems are backed by a
single canonical algorithm in the registry — "kth largest via heap",
"interval merging", "spiral traversal", etc. are reasoning patterns rather
than a single named algorithm entry, so `algorithm_slug` is None for every
problem here (an honest PATTERN_PROBLEM classification, not a misleading
link to an unrelated canonical slug).

Every oracle is written from scratch in THIS file (not reused from
`independent_oracles.py` and not calling into any existing project
algorithm), per the task's independence requirement. Test data follows the
repo-wide 40-test standard (see `testgen.py`): each slug has a `_Spec` (the
problem's oracle/serialization/statement/metadata) in `_SPECS` and a
matching case-plan function in `_PLANS`, mirroring `greedy.py` +
`greedy_testdata.py`.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Callable

from .. import testgen as tg
from ...plugins.registry import RegisteredAlgorithm


# ── Independent oracles (hand-written in this file, not reused) ─────────────

def kth_largest_element(nums: list[int], k: int) -> int:
    return heapq.nlargest(k, nums)[-1]


def merge_overlapping_intervals(starts: list[int], ends: list[int]) -> list[tuple[int, int]]:
    ivals = sorted(zip(starts, ends), key=lambda p: p[0])
    merged: list[list[int]] = []
    for s, e in ivals:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [(a, b) for a, b in merged]


def insert_interval(
    starts: list[int], ends: list[int], new_start: int, new_end: int
) -> list[tuple[int, int]]:
    result: list[list[int]] = []
    ivals = list(zip(starts, ends))
    i, n = 0, len(ivals)
    ns, ne = new_start, new_end
    while i < n and ivals[i][1] < ns:
        result.append(list(ivals[i]))
        i += 1
    while i < n and ivals[i][0] <= ne:
        ns = min(ns, ivals[i][0])
        ne = max(ne, ivals[i][1])
        i += 1
    result.append([ns, ne])
    while i < n:
        result.append(list(ivals[i]))
        i += 1
    return [(a, b) for a, b in result]


def sliding_window_maximum(nums: list[int], k: int) -> list[int]:
    from collections import deque
    dq: "deque[int]" = deque()
    out: list[int] = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out


def subarray_product_less_than_k(nums: list[int], k: int) -> int:
    if k <= 1:
        return 0
    prod = 1
    left = 0
    count = 0
    for right, val in enumerate(nums):
        prod *= val
        while prod >= k:
            prod //= nums[left]
            left += 1
        count += right - left + 1
    return count


def spiral_matrix_traversal(matrix: list[list[int]]) -> list[int]:
    if not matrix or not matrix[0]:
        return []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    out: list[int] = []
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            out.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):
            out.append(matrix[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                out.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                out.append(matrix[r][left])
            left += 1
    return out


def rotate_image_90(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    return [[matrix[n - 1 - c][r] for c in range(n)] for r in range(n)]


def set_matrix_zeroes(matrix: list[list[int]]) -> list[list[int]]:
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    zero_rows = set()
    zero_cols = set()
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 0:
                zero_rows.add(r)
                zero_cols.add(c)
    out = [row[:] for row in matrix]
    for r in range(rows):
        for c in range(cols):
            if r in zero_rows or c in zero_cols:
                out[r][c] = 0
    return out


def combination_sum_count(candidates: list[int], target: int) -> int:
    candidates = sorted(candidates)
    n = len(candidates)
    # dp[t] = number of distinct multisets of candidates summing to t,
    # built incrementally per-candidate to avoid counting permutations.
    dp = [0] * (target + 1)
    dp[0] = 1
    for c in candidates:
        for t in range(c, target + 1):
            dp[t] += dp[t - c]
    return dp[target]


# ── Serialization + formatting helpers ───────────────────────────────────────

def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_int_list(answer: object) -> str:
    seq = list(answer)
    return " ".join(str(x) for x in seq) if seq else ""


def _fmt_interval_list(answer: object) -> str:
    pairs = list(answer)
    return "\n".join(f"{a} {b}" for a, b in pairs) if pairs else ""


def _fmt_matrix(answer: object) -> str:
    rows = list(answer)
    return "\n".join(_arr(row) for row in rows)


def _to_input_kth_largest(nums, k):
    return f"{len(nums)} {_arr(nums)} {k}"


def _to_input_intervals(starts, ends):
    lines = [str(len(starts))] + [f"{s} {e}" for s, e in zip(starts, ends)]
    return "\n".join(lines)


def _to_input_insert_interval(starts, ends, new_start, new_end):
    lines = [str(len(starts))] + [f"{s} {e}" for s, e in zip(starts, ends)] + [f"{new_start} {new_end}"]
    return "\n".join(lines)


def _to_input_window(nums, k):
    return f"{len(nums)} {_arr(nums)} {k}"


def _to_input_matrix(matrix):
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    body = "\n".join(_arr(row) for row in matrix)
    header = f"{rows} {cols}"
    return f"{header}\n{body}" if rows else header


def _to_input_combo(candidates, target):
    return f"{len(candidates)} {_arr(candidates)} {target}"


# ── Spec dataclass ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class _Spec:
    oracle: Callable[..., object]
    to_input: Callable[..., str]
    format_output: Callable[[object], str]
    statement: str
    constraints: list[str]
    starter_code: str
    title: str
    category: str
    difficulty: str = "Medium"
    estimated_minutes: int = 25


_SPECS: dict[str, _Spec] = {
    "kth-largest-element": _Spec(
        oracle=kth_largest_element,
        to_input=_to_input_kth_largest,
        format_output=_fmt_int,
        statement=(
            "Given an unsorted integer array `nums` and an integer `k`, print the "
            "**kth largest element** in the array (1-indexed: `k=1` means the "
            "single largest value). Duplicate values count separately by "
            "position in sorted order, not by distinct value."
        ),
        constraints=["1 ≤ k ≤ nums.length ≤ 10^5", "-10^9 ≤ nums[i] ≤ 10^9"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def kth_largest(nums, k):\n    pass\n\nprint(kth_largest(nums, k))\n"
        ),
        title="Kth Largest Element in an Array",
        category="arrays",
    ),
    "merge-overlapping-intervals": _Spec(
        oracle=merge_overlapping_intervals,
        to_input=_to_input_intervals,
        format_output=_fmt_interval_list,
        statement=(
            "Given `n` intervals `[start, end]` (each inclusive), merge all "
            "intervals that overlap (touching endpoints, e.g. `[1,3]` and "
            "`[3,5]`, count as overlapping) and print the resulting merged "
            "intervals sorted by start, one per line as `start end`."
        ),
        constraints=["0 ≤ n ≤ 10^5", "-10^9 ≤ start ≤ end ≤ 10^9"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "n = int(lines[0])\n"
            "intervals = [tuple(map(int, lines[1+i].split())) for i in range(n)]\n\n"
            "def merge_intervals(intervals):\n    pass\n\n"
            "for s, e in merge_intervals(intervals):\n    print(s, e)\n"
        ),
        title="Merge Overlapping Intervals",
        category="arrays",
    ),
    "insert-interval": _Spec(
        oracle=insert_interval,
        to_input=_to_input_insert_interval,
        format_output=_fmt_interval_list,
        statement=(
            "Given `n` pairwise non-overlapping intervals sorted by start, "
            "plus one new interval, insert the new interval and merge as "
            "needed. Print the resulting sorted, merged interval list, one "
            "per line as `start end`."
        ),
        constraints=["0 ≤ n ≤ 10^5", "-10^9 ≤ start ≤ end ≤ 10^9"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "n = int(lines[0])\n"
            "intervals = [tuple(map(int, lines[1+i].split())) for i in range(n)]\n"
            "new_s, new_e = map(int, lines[1+n].split())\n\n"
            "def insert_interval(intervals, new_s, new_e):\n    pass\n\n"
            "for s, e in insert_interval(intervals, new_s, new_e):\n    print(s, e)\n"
        ),
        title="Insert Interval",
        category="arrays",
    ),
    "sliding-window-maximum": _Spec(
        oracle=sliding_window_maximum,
        to_input=_to_input_window,
        format_output=_fmt_int_list,
        statement=(
            "Given an integer array `nums` and window size `k`, print the "
            "**maximum value** of every contiguous window of size `k` as it "
            "slides from left to right, space-separated in order."
        ),
        constraints=["1 ≤ k ≤ nums.length ≤ 10^5", "-10^9 ≤ nums[i] ≤ 10^9"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def max_sliding_window(nums, k):\n    pass\n\n"
            "print(' '.join(map(str, max_sliding_window(nums, k))))\n"
        ),
        title="Sliding Window Maximum",
        category="sliding-window",
        difficulty="Hard",
        estimated_minutes=30,
    ),
    "subarray-product-less-than-k": _Spec(
        oracle=subarray_product_less_than_k,
        to_input=_to_input_window,
        format_output=_fmt_int,
        statement=(
            "Given an array of **positive** integers `nums` and an integer `k`, "
            "print the **count of contiguous subarrays** whose product of all "
            "elements is strictly less than `k`."
        ),
        constraints=["1 ≤ nums.length ≤ 10^5", "1 ≤ nums[i] ≤ 1000", "0 ≤ k ≤ 10^9"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\nk = int(data[n+1])\n\n"
            "def num_subarrays_product_less_than_k(nums, k):\n    pass\n\n"
            "print(num_subarrays_product_less_than_k(nums, k))\n"
        ),
        title="Subarray Product Less Than K",
        category="sliding-window",
    ),
    "spiral-matrix-traversal": _Spec(
        oracle=spiral_matrix_traversal,
        to_input=_to_input_matrix,
        format_output=_fmt_int_list,
        statement=(
            "Given an `R x C` matrix, print all its elements in **clockwise "
            "spiral order** (outermost ring first, spiraling inward), "
            "space-separated."
        ),
        constraints=["1 ≤ R, C ≤ 200", "-10^9 ≤ matrix[i][j] ≤ 10^9"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "r, c = map(int, lines[0].split())\n"
            "matrix = [list(map(int, lines[1+i].split())) for i in range(r)]\n\n"
            "def spiral_order(matrix):\n    pass\n\n"
            "print(' '.join(map(str, spiral_order(matrix))))\n"
        ),
        title="Spiral Matrix Traversal",
        category="matrix",
    ),
    "rotate-image-90": _Spec(
        oracle=rotate_image_90,
        to_input=_to_input_matrix,
        format_output=_fmt_matrix,
        statement=(
            "Given an `N x N` matrix, print the matrix **rotated 90 degrees "
            "clockwise**, one row per line, space-separated values."
        ),
        constraints=["1 ≤ N ≤ 200", "-10^9 ≤ matrix[i][j] ≤ 10^9"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "n, _c = map(int, lines[0].split())\n"
            "matrix = [list(map(int, lines[1+i].split())) for i in range(n)]\n\n"
            "def rotate(matrix):\n    pass\n\n"
            "for row in rotate(matrix):\n    print(' '.join(map(str, row)))\n"
        ),
        title="Rotate Image by 90 Degrees",
        category="matrix",
    ),
    "set-matrix-zeroes": _Spec(
        oracle=set_matrix_zeroes,
        to_input=_to_input_matrix,
        format_output=_fmt_matrix,
        statement=(
            "Given an `R x C` matrix, if any cell equals `0`, set its entire "
            "row and entire column to `0`. Print the resulting matrix, one "
            "row per line, space-separated values."
        ),
        constraints=["1 ≤ R, C ≤ 200", "-10^9 ≤ matrix[i][j] ≤ 10^9"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "r, c = map(int, lines[0].split())\n"
            "matrix = [list(map(int, lines[1+i].split())) for i in range(r)]\n\n"
            "def set_zeroes(matrix):\n    pass\n\n"
            "for row in set_zeroes(matrix):\n    print(' '.join(map(str, row)))\n"
        ),
        title="Set Matrix Zeroes",
        category="matrix",
    ),
    "combination-sum-count": _Spec(
        oracle=combination_sum_count,
        to_input=_to_input_combo,
        format_output=_fmt_int,
        statement=(
            "Given a list of **distinct** positive integer candidates (each "
            "may be reused an unlimited number of times) and a positive "
            "integer `target`, print the **count of distinct combinations** "
            "(order-independent — multisets, not permutations) of candidates "
            "that sum exactly to `target`."
        ),
        constraints=["1 ≤ candidates.length ≤ 100", "1 ≤ candidates[i] ≤ 200", "1 ≤ target ≤ 500"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\ncandidates = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n\n"
            "def combination_sum_count(candidates, target):\n    pass\n\n"
            "print(combination_sum_count(candidates, target))\n"
        ),
        title="Combination Sum Count",
        category="backtracking",
    ),
}


# ── Case plans (40-test generation, per testgen.py contract) ────────────────

def _plan_kth_largest(rng) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_kth_largest

    def gen_small():
        n = rng.randint(1, 8)
        nums = tg.rand_int_array(rng, n, -50, 50)
        k = rng.randint(1, n)
        return (nums, k)

    def gen_stress():
        n = rng.randint(5000, 20000)
        nums = tg.rand_int_array(rng, n, -10**9, 10**9)
        k = rng.randint(1, n)
        return (nums, k)

    visible = [
        ([3, 2, 1, 5, 6, 4], 2),
        ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4),
        ([1], 1),
        ([7, 7, 7, 7], 2),
        ([-1, -2, -3, -4], 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([5], 1),
        ([1, 2], 1),
        ([1, 2], 2),
        ([0, 0, 0], 2),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([5, 5, 5, 5, 5, 5], 1),          # all duplicates
        (list(range(10)), 1),              # already ascending, k=1 (largest)
        (list(range(9, -1, -1)), 10),      # already descending, k=n (smallest)
        ([1, 1, 2, 2, 3, 3], 3),           # ties in the middle
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([2, 1], 1),   # smallest non-trivial: catches wrong end of sort
        ([2, 1], 2),   # k = n
        ([1, 2, 3], 1),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_merge_intervals(rng) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_intervals

    def gen_small():
        n = rng.randint(1, 6)
        s, e = tg.interval_patterns(rng, n, 0, 30)["random"]
        return (s, e)

    def gen_stress():
        n = rng.randint(1000, 5000)
        s, e = tg.interval_patterns(rng, n, 0, 100_000)["random"]
        return (s, e)

    visible = [
        ([1, 3, 6, 15], [3, 5, 7, 18]),
        ([1, 4], [4, 5]),
        ([1], [4]),
        ([1, 2, 3], [2, 3, 4]),
        ([1, 4, 8], [2, 6, 10]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([], []),
        ([5], [5]),
        ([0, 10], [10, 20]),   # touching exactly
        ([0, 0], [1, 1]),      # identical
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([1, 0], [5, 6]),                      # unsorted input, overlapping
        (list(range(9, -1, -1)), list(range(11, 21))),  # reverse-sorted starts
        ([0, 1, 2, 3, 4], [10, 2, 3, 4, 5]),   # one interval swallows all others
        ([-5, -3, -1], [0, 2, 4]),              # negatives
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 3], [3, 5]),      # touching, must merge (>= not >)
        ([1, 3], [2, 5]),      # true overlap
        ([1, 5], [2, 3]),      # fully nested interval
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_insert_interval(rng) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_insert_interval

    def _non_overlapping_sorted(n, lo, hi):
        if n == 0:
            return [], []
        starts, ends = [], []
        cur = lo
        for _ in range(n):
            gap = rng.randint(0, 3)
            s = cur + gap
            length = rng.randint(1, 5)
            e = s + length
            if e > hi:
                break
            starts.append(s)
            ends.append(e)
            cur = e + rng.randint(1, 3)
        return starts, ends

    def gen_small():
        n = rng.randint(0, 6)
        s, e = _non_overlapping_sorted(n, 0, 60)
        new_s = rng.randint(0, 60)
        new_e = new_s + rng.randint(0, 10)
        return (s, e, new_s, new_e)

    def gen_stress():
        n = rng.randint(1000, 3000)
        s, e = _non_overlapping_sorted(n, 0, 200_000)
        new_s = rng.randint(0, 200_000)
        new_e = new_s + rng.randint(0, 500)
        return (s, e, new_s, new_e)

    visible = [
        ([1, 3, 6, 8, 12], [2, 5, 7, 10, 16], 4, 9),
        ([], [], 5, 7),
        ([1, 5], [2, 6], 0, 0),
        ([1, 2, 3], [1, 2, 3], 0, 0),
        ([3, 5], [4, 6], 0, 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([], [], 0, 0),
        ([1], [2], 3, 4),      # after everything, no overlap
        ([1], [2], -5, -3),    # before everything
        ([5], [5], 5, 5),      # single-point interval, exact touch
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([1, 3, 6, 8, 12], [2, 5, 7, 10, 16], 0, 20),   # swallows everything
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], 0, 0),        # new interval touches nothing, prepend
        ([1, 2, 3, 4, 5], [2, 3, 4, 5, 6], 6, 6),        # touches only the last (merge boundary)
        ([0, 10, 20], [5, 15, 25], 6, 19),                # merges middle two, engulfs neither fully
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 5], [2, 6], 6, 8),   # touches end exactly (>= boundary)
        ([1, 5], [2, 6], 7, 8),   # does not touch (off by one from above)
        ([3, 5], [4, 6], 2, 3),   # touches start exactly
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_sliding_window_maximum(rng) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_window

    def gen_small():
        n = rng.randint(1, 8)
        nums = tg.rand_int_array(rng, n, -20, 20)
        k = rng.randint(1, n)
        return (nums, k)

    def gen_stress():
        n = rng.randint(5000, 20000)
        nums = tg.rand_int_array(rng, n, -10**6, 10**6)
        k = rng.randint(1, n)
        return (nums, k)

    visible = [
        ([1, 3, -1, -3, 5, 3, 6, 7], 3),
        ([1], 1),
        ([9, 11], 2),
        ([4, -2], 2),
        ([1, 3, 1, 2, 0, 5], 3),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([5], 1),
        ([1, 2, 3], 3),        # k == n
        ([1, 2, 3], 1),        # k == 1
        ([7, 7, 7, 7], 2),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        (list(range(10)), 3),               # strictly ascending — max always at right edge
        (list(range(9, -1, -1)), 3),        # strictly descending — max always at left edge
        ([5, 5, 5, 5, 5, 5], 3),             # all equal — tests stale-index eviction
        ([1, -1, 1, -1, 1, -1, 1], 2),       # alternating
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 2], 2),          # single window, whole array
        ([2, 1], 1),          # k=1: output equals input
        ([1, 3, 2], 2),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_subarray_product(rng) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_window

    def gen_small():
        n = rng.randint(1, 8)
        nums = tg.rand_int_array(rng, n, 1, 10)
        k = rng.randint(0, 200)
        return (nums, k)

    def gen_stress():
        n = rng.randint(3000, 10000)
        nums = tg.rand_int_array(rng, n, 1, 10)
        k = rng.randint(1, 10**9)
        return (nums, k)

    visible = [
        ([10, 5, 2, 6], 100),
        ([1, 2, 3], 0),
        ([1, 1, 1], 2),
        ([10], 11),
        ([1, 2, 3, 4, 5], 10),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([1], 1),        # k=1 excludes even the single-element product of 1
        ([1], 2),
        ([5], 5),        # product equals k exactly — excluded (strict <)
        ([1, 1, 1, 1], 1),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([1] * 10, 2),                    # all ones — every subarray qualifies
        ([10, 10, 10, 10, 10], 10),       # product hits k exactly at length 1
        ([1, 10, 1, 10, 1], 15),           # alternating small/large
        ([2, 2, 2, 2, 2, 2, 2, 2], 100),  # product grows exponentially, window shrinks repeatedly
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 2], 3),     # boundary at exactly k: catches >= vs > bug
        ([2, 3], 6),     # product == k exactly (whole array) — must exclude
        ([1, 2, 3], 6),  # product == k for a subarray in the middle
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _rand_matrix(rng, r, c, lo, hi):
    return [[rng.randint(lo, hi) for _ in range(c)] for _ in range(r)]


def _plan_spiral_matrix(rng) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_matrix

    def gen_small():
        r = rng.randint(1, 5)
        c = rng.randint(1, 5)
        return (_rand_matrix(rng, r, c, -20, 20),)

    def gen_stress():
        r = rng.randint(100, 150)
        c = rng.randint(100, 150)
        return (_rand_matrix(rng, r, c, -1000, 1000),)

    visible = [
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],),
        ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],),
        ([[1]],),
        ([[1, 2, 3]],),
        ([[1], [2], [3]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([[5]],),
        ([[1, 2]],),
        ([[1], [2]],),
        ([[1, 2], [3, 4]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        (_rand_matrix(rng, 1, 20, 0, 5),),     # single row, wide
        (_rand_matrix(rng, 20, 1, 0, 5),),     # single column, tall
        ([[0] * 6 for _ in range(6)],),         # all-equal values (6x6 square)
        (_rand_matrix(rng, 7, 3, -5, 5),),      # rows != cols, non-square
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([[1, 2], [3, 4], [5, 6]],),   # 3x2 — tests top/bottom vs left/right edge order
        ([[1, 2, 3], [4, 5, 6]],),      # 2x3
        ([[1, 2, 3], [8, 9, 4], [7, 6, 5]],),  # classic ring-then-center
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _rand_square(rng, n, lo, hi):
    return [[rng.randint(lo, hi) for _ in range(n)] for _ in range(n)]


def _plan_rotate_image(rng) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_matrix

    def gen_small():
        n = rng.randint(1, 6)
        return (_rand_square(rng, n, -20, 20),)

    def gen_stress():
        n = rng.randint(100, 150)
        return (_rand_square(rng, n, -1000, 1000),)

    visible = [
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],),
        ([[1, 2], [3, 4]],),
        ([[1]],),
        ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]],),
        ([[5, -1], [3, 8]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([[9]],),
        ([[1, 2], [3, 4]],),
        ([[0, 0], [0, 0]],),
        ([[-5, -5], [-5, -5]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([[i * 3 + j for j in range(3)] for i in range(3)],),   # sequential values, easy to eyeball a wrong rotation
        ([[1] * 5 for _ in range(5)],),                            # all-equal
        ([[i for i in range(4)] for _ in range(4)],),              # identical rows (columns become distinguishable after rotate)
        ([[(-1) ** (i + j) for j in range(5)] for i in range(5)],),  # checkerboard
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([[1, 2], [3, 4]],),                # smallest non-trivial: tests transpose direction
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],),  # catches 90-CW vs 90-CCW confusion
        ([[1, 0], [0, 1]],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_set_matrix_zeroes(rng) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_matrix

    def gen_small():
        r = rng.randint(1, 5)
        c = rng.randint(1, 5)
        m = _rand_matrix(rng, r, c, -10, 10)
        # bias toward containing at least one zero often
        if rng.random() < 0.7:
            rr, cc = rng.randint(0, r - 1), rng.randint(0, c - 1)
            m[rr][cc] = 0
        return (m,)

    def gen_stress():
        r = rng.randint(80, 120)
        c = rng.randint(80, 120)
        m = _rand_matrix(rng, r, c, -50, 50)
        for _ in range(rng.randint(1, 20)):
            rr, cc = rng.randint(0, r - 1), rng.randint(0, c - 1)
            m[rr][cc] = 0
        return (m,)

    visible = [
        ([[1, 1, 1], [1, 0, 1], [1, 1, 1]],),
        ([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]],),
        ([[1]],),
        ([[0]],),
        ([[1, 2], [3, 0]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([[5]],),
        ([[0]],),
        ([[1, 0]],),
        ([[1], [0]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([[0, 0, 0], [0, 0, 0], [0, 0, 0]],),        # all zero already
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],),          # no zeroes — matrix unchanged
        ([[0, 1, 1], [1, 1, 1], [1, 1, 0]],),          # two zeroes at opposite corners
        ([[1, 1, 1, 1], [1, 1, 1, 1], [1, 0, 1, 1], [1, 1, 1, 1]],),  # zero on an interior cell
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([[1, 1], [1, 0]],),           # zero in bottom-right — tests row/col both flagged
        ([[0, 1], [1, 1]],),           # zero in top-left
        ([[1, 1, 1], [1, 0, 1], [1, 1, 1]],),  # zero dead-center — tests using in-place matrix during scan (mutation bug)
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_combination_sum_count(rng) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_combo

    def gen_small():
        n = rng.randint(1, 5)
        cands = tg.rand_distinct_int_array(rng, n, 1, 15)
        target = rng.randint(1, 25)
        return (cands, target)

    def gen_stress():
        n = rng.randint(30, 80)
        cands = tg.rand_distinct_int_array(rng, n, 1, 200)
        target = rng.randint(400, 500)
        return (cands, target)

    visible = [
        ([2, 3, 6, 7], 7),
        ([2, 3, 5], 8),
        ([1], 1),
        ([1], 5),
        ([2, 5], 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([1], 1),
        ([5], 5),
        ([5], 4),           # no combination reaches target
        ([1, 2, 3, 4, 5], 1),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([1, 2, 3], 4),                  # multiple combos of different lengths reach 4
        ([2, 4, 6, 8], 8),                # only even candidates, target divisible many ways
        (list(range(1, 11)), 10),         # many candidates, mid target — combinatorially rich
        ([7, 11, 13], 100),                # candidates with no small common structure
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([2], 4),        # single candidate must repeat exactly twice
        ([3], 9),        # single candidate repeats exactly 3 times
        ([2, 3], 5),     # exactly one combo (2+3), tests off-by-one in DP loop bound
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


_PLANS: dict[str, Callable] = {
    "kth-largest-element": _plan_kth_largest,
    "merge-overlapping-intervals": _plan_merge_intervals,
    "insert-interval": _plan_insert_interval,
    "sliding-window-maximum": _plan_sliding_window_maximum,
    "subarray-product-less-than-k": _plan_subarray_product,
    "spiral-matrix-traversal": _plan_spiral_matrix,
    "rotate-image-90": _plan_rotate_image,
    "set-matrix-zeroes": _plan_set_matrix_zeroes,
    "combination-sum-count": _plan_combination_sum_count,
}


# ── Builder ────────────────────────────────────────────────────────────────

def build_famous_arrays_matrix_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue

        plan_fn = _PLANS.get(slug)
        if plan_fn is None:
            skipped.append((slug, "no 40-test case plan registered"))
            continue

        try:
            rng = tg.problem_rng(slug)
            case_plan = plan_fn(rng)
            test_spec = tg.TestSpec(
                oracle=spec.oracle, to_input=spec.to_input, format_output=spec.format_output
            )
            test_cases = tg.build_forty(slug, test_spec, case_plan)
        except tg.TestPlanError as exc:
            skipped.append((slug, str(exc)))
            continue

        if not test_cases:
            skipped.append((slug, "no test cases produced"))
            continue

        problem = {
            "id": slug,
            "title": spec.title,
            "difficulty": spec.difficulty,
            "category": spec.category,
            "algorithm_slug": None,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": f"Think about the classic pattern behind {spec.title.lower()}."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped


# ── Reference (correct) and wrong (plausible-bug) solutions ─────────────────

REFERENCE_SOLUTIONS: dict[str, str] = {
    "kth-largest-element": (
        "import sys, heapq\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "k = int(data[n+1])\n"
        "print(heapq.nlargest(k, nums)[-1])\n"
    ),
    "merge-overlapping-intervals": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\n"
        "ivals = sorted((tuple(map(int, lines[1+i].split())) for i in range(n)), key=lambda p: p[0])\n"
        "out = []\n"
        "for s, e in ivals:\n"
        "    if out and s <= out[-1][1]:\n"
        "        out[-1] = (out[-1][0], max(out[-1][1], e))\n"
        "    else:\n"
        "        out.append((s, e))\n"
        "for s, e in out:\n"
        "    print(s, e)\n"
    ),
    "insert-interval": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\n"
        "ivals = [tuple(map(int, lines[1+i].split())) for i in range(n)]\n"
        "ns, ne = map(int, lines[1+n].split())\n"
        "res = []\n"
        "i = 0\n"
        "while i < n and ivals[i][1] < ns:\n"
        "    res.append(ivals[i]); i += 1\n"
        "while i < n and ivals[i][0] <= ne:\n"
        "    ns = min(ns, ivals[i][0]); ne = max(ne, ivals[i][1]); i += 1\n"
        "res.append((ns, ne))\n"
        "while i < n:\n"
        "    res.append(ivals[i]); i += 1\n"
        "for s, e in res:\n"
        "    print(s, e)\n"
    ),
    "sliding-window-maximum": (
        "import sys\n"
        "from collections import deque\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "k = int(data[n+1])\n"
        "dq = deque()\n"
        "out = []\n"
        "for i, x in enumerate(nums):\n"
        "    while dq and nums[dq[-1]] < x:\n"
        "        dq.pop()\n"
        "    dq.append(i)\n"
        "    if dq[0] <= i - k:\n"
        "        dq.popleft()\n"
        "    if i >= k - 1:\n"
        "        out.append(nums[dq[0]])\n"
        "print(' '.join(map(str, out)))\n"
    ),
    "subarray-product-less-than-k": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "k = int(data[n+1])\n"
        "if k <= 1:\n"
        "    print(0)\n"
        "else:\n"
        "    prod = 1\n"
        "    left = 0\n"
        "    count = 0\n"
        "    for right in range(n):\n"
        "        prod *= nums[right]\n"
        "        while prod >= k:\n"
        "            prod //= nums[left]\n"
        "            left += 1\n"
        "        count += right - left + 1\n"
        "    print(count)\n"
    ),
    "spiral-matrix-traversal": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "r, c = map(int, lines[0].split())\n"
        "m = [list(map(int, lines[1+i].split())) for i in range(r)]\n"
        "res = []\n"
        "top, bot, left, right = 0, r - 1, 0, c - 1\n"
        "while top <= bot and left <= right:\n"
        "    for x in range(left, right + 1):\n"
        "        res.append(m[top][x])\n"
        "    top += 1\n"
        "    for y in range(top, bot + 1):\n"
        "        res.append(m[y][right])\n"
        "    right -= 1\n"
        "    if top <= bot:\n"
        "        for x in range(right, left - 1, -1):\n"
        "            res.append(m[bot][x])\n"
        "        bot -= 1\n"
        "    if left <= right:\n"
        "        for y in range(bot, top - 1, -1):\n"
        "            res.append(m[y][left])\n"
        "        left += 1\n"
        "print(' '.join(map(str, res)))\n"
    ),
    "rotate-image-90": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "n, _c = map(int, lines[0].split())\n"
        "m = [list(map(int, lines[1+i].split())) for i in range(n)]\n"
        "# transpose then reverse each row == rotate 90 clockwise\n"
        "t = [[m[y][x] for y in range(n)] for x in range(n)]\n"
        "for row in t:\n"
        "    print(' '.join(map(str, reversed(row))))\n"
    ),
    "set-matrix-zeroes": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "r, c = map(int, lines[0].split())\n"
        "m = [list(map(int, lines[1+i].split())) for i in range(r)]\n"
        "zr, zc = set(), set()\n"
        "for i in range(r):\n"
        "    for j in range(c):\n"
        "        if m[i][j] == 0:\n"
        "            zr.add(i); zc.add(j)\n"
        "for i in range(r):\n"
        "    for j in range(c):\n"
        "        if i in zr or j in zc:\n"
        "            m[i][j] = 0\n"
        "for row in m:\n"
        "    print(' '.join(map(str, row)))\n"
    ),
    "combination-sum-count": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "cands = list(map(int, data[1:n+1]))\n"
        "target = int(data[n+1])\n"
        "dp = [0] * (target + 1)\n"
        "dp[0] = 1\n"
        "for c in sorted(cands):\n"
        "    for t in range(c, target + 1):\n"
        "        dp[t] += dp[t - c]\n"
        "print(dp[target])\n"
    ),
}


WRONG_SOLUTIONS: dict[str, str] = {
    # Bug: uses a min-heap of size k incorrectly — sorts ascending and takes
    # index k-1 from the front instead of the kth from the end (off-by-one on
    # which end "largest" means for duplicate-heavy / small arrays it can
    # still get right by luck, but fails as soon as k and n diverge).
    "kth-largest-element": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "k = int(data[n+1])\n"
        "s = sorted(nums)\n"
        "print(s[k - 1])\n"  # ascending sort — this is actually kth SMALLEST
    ),
    # Bug: uses strict '<' instead of '<=' for the overlap test, so touching
    # intervals (end == next start) are NOT merged.
    "merge-overlapping-intervals": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\n"
        "ivals = sorted((tuple(map(int, lines[1+i].split())) for i in range(n)), key=lambda p: p[0])\n"
        "out = []\n"
        "for s, e in ivals:\n"
        "    if out and s < out[-1][1]:\n"
        "        out[-1] = (out[-1][0], max(out[-1][1], e))\n"
        "    else:\n"
        "        out.append((s, e))\n"
        "for s, e in out:\n"
        "    print(s, e)\n"
    ),
    # Bug: overlap test uses strict '<' for the merge-in condition, so a new
    # interval that exactly touches an existing interval's end is treated as
    # non-overlapping and appended separately instead of merged.
    "insert-interval": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "n = int(lines[0])\n"
        "ivals = [tuple(map(int, lines[1+i].split())) for i in range(n)]\n"
        "ns, ne = map(int, lines[1+n].split())\n"
        "res = []\n"
        "i = 0\n"
        "while i < n and ivals[i][1] < ns:\n"
        "    res.append(ivals[i]); i += 1\n"
        "while i < n and ivals[i][0] < ne:\n"
        "    ns = min(ns, ivals[i][0]); ne = max(ne, ivals[i][1]); i += 1\n"
        "res.append((ns, ne))\n"
        "while i < n:\n"
        "    res.append(ivals[i]); i += 1\n"
        "for s, e in res:\n"
        "    print(s, e)\n"
    ),
    # Bug: eviction check uses '<' instead of '<=', so the deque's front index
    # is evicted one step too late, occasionally reporting a value that just
    # fell outside the window as still the max.
    "sliding-window-maximum": (
        "import sys\n"
        "from collections import deque\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "k = int(data[n+1])\n"
        "dq = deque()\n"
        "out = []\n"
        "for i, x in enumerate(nums):\n"
        "    while dq and nums[dq[-1]] < x:\n"
        "        dq.pop()\n"
        "    dq.append(i)\n"
        "    if dq[0] < i - k:\n"  # should be <=
        "        dq.popleft()\n"
        "    if i >= k - 1:\n"
        "        out.append(nums[dq[0]])\n"
        "print(' '.join(map(str, out)))\n"
    ),
    # Bug: uses '>' instead of '>=' when shrinking the window, so subarrays
    # whose product exactly equals k are incorrectly counted as valid.
    "subarray-product-less-than-k": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "k = int(data[n+1])\n"
        "if k <= 1:\n"
        "    print(0)\n"
        "else:\n"
        "    prod = 1\n"
        "    left = 0\n"
        "    count = 0\n"
        "    for right in range(n):\n"
        "        prod *= nums[right]\n"
        "        while prod > k:\n"  # should be >=
        "            prod //= nums[left]\n"
        "            left += 1\n"
        "        count += right - left + 1\n"
        "    print(count)\n"
    ),
    # Bug: forgets the final "if left <= right" guard for the last left-column
    # pass, so a matrix with more rows than columns (or vice versa) emits an
    # extra spurious pass through a column strip that's already exhausted.
    "spiral-matrix-traversal": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "r, c = map(int, lines[0].split())\n"
        "m = [list(map(int, lines[1+i].split())) for i in range(r)]\n"
        "res = []\n"
        "top, bot, left, right = 0, r - 1, 0, c - 1\n"
        "while top <= bot and left <= right:\n"
        "    for x in range(left, right + 1):\n"
        "        res.append(m[top][x])\n"
        "    top += 1\n"
        "    for y in range(top, bot + 1):\n"
        "        res.append(m[y][right])\n"
        "    right -= 1\n"
        "    if top <= bot:\n"
        "        for x in range(right, left - 1, -1):\n"
        "            res.append(m[bot][x])\n"
        "        bot -= 1\n"
        "    for y in range(bot, top - 1, -1):\n"  # missing 'if left <= right' guard
        "        res.append(m[y][left])\n"
        "    left += 1\n"
        "print(' '.join(map(str, res)))\n"
    ),
    # Bug: rotates counter-clockwise instead of clockwise (reverses columns
    # order instead of reversing each row after transpose).
    "rotate-image-90": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "n, _c = map(int, lines[0].split())\n"
        "m = [list(map(int, lines[1+i].split())) for i in range(n)]\n"
        "t = [[m[y][x] for y in range(n)] for x in range(n)]\n"
        "for row in reversed(t):\n"  # wrong: reverses row order, not each row
        "    print(' '.join(map(str, row)))\n"
    ),
    # Bug: zeroes out rows/columns using the mutated matrix while still
    # scanning it, so a zero created by an earlier row/col clearing cascades
    # into clearing additional rows/columns that were never zero originally.
    "set-matrix-zeroes": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "r, c = map(int, lines[0].split())\n"
        "m = [list(map(int, lines[1+i].split())) for i in range(r)]\n"
        "for i in range(r):\n"
        "    for j in range(c):\n"
        "        if m[i][j] == 0:\n"
        "            for x in range(c):\n"
        "                m[i][x] = 0\n"
        "            for y in range(r):\n"
        "                m[y][j] = 0\n"
        "for row in m:\n"
        "    print(' '.join(map(str, row)))\n"
    ),
    # Bug: iterates the DP target loop in the wrong order relative to
    # candidates (counts permutations instead of combinations) by looping
    # target on the outside and candidates on the inside, which double-counts
    # different orderings of the same multiset.
    "combination-sum-count": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "cands = list(map(int, data[1:n+1]))\n"
        "target = int(data[n+1])\n"
        "dp = [0] * (target + 1)\n"
        "dp[0] = 1\n"
        "for t in range(1, target + 1):\n"
        "    for c in cands:\n"
        "        if c <= t:\n"
        "            dp[t] += dp[t - c]\n"
        "print(dp[target])\n"
    ),
}
