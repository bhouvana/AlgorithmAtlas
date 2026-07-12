"""
"Famous Hard" pattern-problem family — six widely-known Hard-tier algorithmic
challenges that don't already have canonical registry coverage under any
existing family. All six are `origin_type = PATTERN_PROBLEM`
(`algorithm_slug=None`): each teaches a specific hard technique (partition
binary search, regex DP, k-way heap merge, interval/burst DP, histogram-based
2D scanning, stack-based longest-run tracking) rather than implementing one
single canonical algorithm already in the registry.

Every problem here is deliberately distinct in technique/input-shape from an
existing AtlasCode problem it might otherwise resemble:

  - median-of-two-sorted-arrays: binary-search-on-partition, not a straight
    merge; distinct from every existing binary-search-variants problem.
  - regular-expression-matching: `.`/`*`(repeat-previous) regex DP transition,
    distinct from `wildcard-matching`'s `?`/`*`(glob) transition.
  - merge-k-sorted-lists: k-way heap merge over k linked lists, distinct from
    any 2-list or array-merge problem in the catalog.
  - burst-balloons: interval DP keyed on "last balloon burst in a range",
    distinct from `matrix-chain-multiplication`'s interval DP (which is keyed
    on split point, with a different recurrence and no synthetic boundary
    values).
  - maximal-rectangle: 2D matrix reduced row-by-row into histograms, distinct
    from `largest-rectangle-in-histogram`'s single 1D array input.
  - longest-valid-parentheses: longest contiguous *valid* run length via a
    stack-of-indices, distinct from `valid-parentheses`'s whole-string
    boolean check.

Each `oracle` is written directly in this module (no dependency on
`independent_oracles.py`) since these are new, self-contained algorithms not
shared with any other family.
"""
from __future__ import annotations

import heapq
import random
from dataclasses import dataclass
from typing import Callable

from .. import testgen as tg
from ...plugins.registry import RegisteredAlgorithm


class OracleError(Exception):
    pass


# ── Oracles ────────────────────────────────────────────────────────────────────

def median_of_two_sorted_arrays(a: list[int], b: list[int]) -> str:
    """O(log(min(m,n))) binary search on the partition point."""
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    lo, hi = 0, m
    half = (m + n + 1) // 2
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        a_left = a[i - 1] if i > 0 else float("-inf")
        a_right = a[i] if i < m else float("inf")
        b_left = b[j - 1] if j > 0 else float("-inf")
        b_right = b[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2 == 1:
                return str(int(max(a_left, b_left)))
            total = max(a_left, b_left) + min(a_right, b_right)
            return f"{total / 2:.1f}"
        elif a_left > b_right:
            hi = i - 1
        else:
            lo = i + 1
    raise OracleError("median_of_two_sorted_arrays: partition search failed (bad input?)")


def regex_is_match(s: str, p: str) -> bool:
    """Standard `.`/`*`(repeat-previous) regex full-match DP."""
    n, m = len(s), len(p)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    for j in range(1, m + 1):
        if p[j - 1] == "*" and j >= 2:
            dp[0][j] = dp[0][j - 2]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            pc = p[j - 1]
            if pc == "*":
                if j < 2:
                    raise OracleError("regex_is_match: pattern starts with '*' (no preceding element)")
                zero_case = dp[i][j - 2]
                prev = p[j - 2]
                one_or_more = (prev == "." or prev == s[i - 1]) and dp[i - 1][j]
                dp[i][j] = zero_case or one_or_more
            elif pc == "." or pc == s[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = False
    return dp[n][m]


def merge_k_sorted_lists(lists: list[list[int]]) -> list[int]:
    heap: list[tuple[int, int, int]] = []
    for li, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], li, 0))
    out: list[int] = []
    while heap:
        val, li, idx = heapq.heappop(heap)
        out.append(val)
        if idx + 1 < len(lists[li]):
            heapq.heappush(heap, (lists[li][idx + 1], li, idx + 1))
    return out


def burst_balloons_max_coins(balloons: list[int]) -> int:
    """Interval DP: dp[l][r] = max coins bursting all balloons strictly
    between padded boundary indices l and r (l, r themselves never burst,
    they're the synthetic 1-valued sentinels)."""
    nums = [1] + list(balloons) + [1]
    n = len(nums)
    if n <= 2:
        return 0
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):
        for l in range(0, n - length):
            r = l + length
            best = 0
            for k in range(l + 1, r):
                coins = nums[l] * nums[k] * nums[r] + dp[l][k] + dp[k][r]
                if coins > best:
                    best = coins
            dp[l][r] = best
    return dp[0][n - 1]


def _largest_rectangle_in_histogram(heights: list[int]) -> int:
    stack: list[int] = []
    best = 0
    for i, h in enumerate(heights + [0]):
        while stack and heights[stack[-1]] >= h:
            top = stack.pop()
            height = heights[top]
            width = i if not stack else i - stack[-1] - 1
            best = max(best, height * width)
        stack.append(i)
    return best


def maximal_rectangle_area(grid: list[list[int]]) -> int:
    if not grid or not grid[0]:
        return 0
    cols = len(grid[0])
    heights = [0] * cols
    best = 0
    for row in grid:
        for c in range(cols):
            heights[c] = heights[c] + 1 if row[c] == 1 else 0
        best = max(best, _largest_rectangle_in_histogram(heights))
    return best


def longest_valid_parentheses_length(s: str) -> int:
    stack: list[int] = [-1]
    best = 0
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                best = max(best, i - stack[-1])
    return best


# ── Formatters ─────────────────────────────────────────────────────────────────

def _fmt_identity(answer: object) -> str:
    return str(answer)


def _fmt_bool(answer: object) -> str:
    return "true" if answer else "false"


def _fmt_int_list(answer: object) -> str:
    return " ".join(str(x) for x in answer) if answer else ""


# ── to_input serializers ───────────────────────────────────────────────────────

def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


def _to_input_median(a: list[int], b: list[int]) -> str:
    return f"{len(a)} {_arr(a)}\n{len(b)} {_arr(b)}"


def _to_input_regex(s: str, p: str) -> str:
    return f"{s}\n{p}"


def _to_input_merge_k(lists: list[list[int]]) -> str:
    lines = [str(len(lists))]
    for lst in lists:
        lines.append(f"{len(lst)} {_arr(lst)}" if lst else "0")
    return "\n".join(lines)


def _to_input_balloons(balloons: list[int]) -> str:
    return f"{len(balloons)} {_arr(balloons)}"


def _to_input_grid(grid: list[list[int]]) -> str:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    lines = [f"{rows} {cols}"]
    lines += [_arr(row) for row in grid]
    return "\n".join(lines)


def _to_input_parens(s: str) -> str:
    return s


# ── Spec dataclass (mirrors greedy.py) ──────────────────────────────────────────

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
    difficulty: str = "Hard"
    estimated_minutes: int = 40


_SPECS: dict[str, _Spec] = {
    "median-of-two-sorted-arrays": _Spec(
        oracle=median_of_two_sorted_arrays,
        to_input=_to_input_median,
        format_output=_fmt_identity,
        statement=(
            "Given two sorted integer arrays `nums1` (length `m`) and `nums2` "
            "(length `n`), print the **median** of the combined sorted array "
            "without fully materializing and sorting the merge (aim for "
            "O(log(min(m, n))) time). Print the median as a plain integer if "
            "`m + n` is odd, otherwise print it with **exactly one decimal "
            "place** (e.g. `3.0`, `2.5`)."
        ),
        constraints=[
            "0 ≤ m, n ≤ 10^5", "1 ≤ m + n ≤ 2×10^5",
            "-10^6 ≤ nums1[i], nums2[i] ≤ 10^6",
        ],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "parts1 = lines[0].split()\nm = int(parts1[0])\nnums1 = list(map(int, parts1[1:1+m]))\n"
            "parts2 = lines[1].split()\nn = int(parts2[0])\nnums2 = list(map(int, parts2[1:1+n]))\n\n"
            "def find_median(nums1, nums2):\n    pass\n\nprint(find_median(nums1, nums2))\n"
        ),
        title="Median of Two Sorted Arrays",
        category="searching",
        estimated_minutes=40,
    ),
    "regular-expression-matching": _Spec(
        oracle=regex_is_match,
        to_input=_to_input_regex,
        format_output=_fmt_bool,
        statement=(
            "Given a string `s` of lowercase letters and a pattern `p` of "
            "lowercase letters, `.`, and `*`, print `true` if `p` matches the "
            "**entire** `s`, else `false`. Matching rules: `.` matches any "
            "single character; `*` matches **zero or more occurrences of the "
            "element immediately preceding it** (a letter or `.`) — this is "
            "regex-style repetition, not shell-glob wildcard matching."
        ),
        constraints=["0 ≤ s.length ≤ 20", "0 ≤ p.length ≤ 30", "p contains only a-z, '.', '*'"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\ns = lines[0]\np = lines[1] if len(lines) > 1 else ''\n\n"
            "def is_match(s, p):\n    pass\n\nprint('true' if is_match(s, p) else 'false')\n"
        ),
        title="Regular Expression Matching",
        category="dynamic-programming",
        estimated_minutes=45,
    ),
    "merge-k-sorted-lists": _Spec(
        oracle=merge_k_sorted_lists,
        to_input=_to_input_merge_k,
        format_output=_fmt_int_list,
        statement=(
            "Given `k` sorted singly-linked lists (each represented as its "
            "length followed by its values, space-separated, one list per "
            "line), print the **single fully merged sorted list**, "
            "space-separated. Use a min-heap based k-way merge for "
            "O(N log k) time, where N is the total number of nodes."
        ),
        constraints=["0 ≤ k ≤ 10^4", "0 ≤ total nodes ≤ 5×10^4", "-10^4 ≤ node value ≤ 10^4"],
        starter_code=(
            "import sys, heapq\nlines = sys.stdin.read().split('\\n')\n"
            "k = int(lines[0])\nlists = []\n"
            "for i in range(1, k + 1):\n"
            "    parts = lines[i].split()\n"
            "    cnt = int(parts[0])\n"
            "    lists.append(list(map(int, parts[1:1+cnt])))\n\n"
            "def merge_k_lists(lists):\n    pass\n\n"
            "print(' '.join(map(str, merge_k_lists(lists))))\n"
        ),
        title="Merge K Sorted Lists",
        category="linked-list",
        estimated_minutes=40,
    ),
    "burst-balloons": _Spec(
        oracle=burst_balloons_max_coins,
        to_input=_to_input_balloons,
        format_output=_fmt_identity,
        statement=(
            "You are given `n` balloons in a row, each with an integer value "
            "`balloons[i]`. Bursting balloon `i` earns "
            "`left * balloons[i] * right` coins, where `left`/`right` are the "
            "values of `i`'s CURRENT neighbors at the moment it is burst "
            "(treat both ends of the row as having an invisible balloon of "
            "value 1). Print the **maximum total coins** obtainable by "
            "bursting every balloon in some order."
        ),
        constraints=["1 ≤ n ≤ 300", "0 ≤ balloons[i] ≤ 100"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0])\nballoons = list(map(int, data[1:n+1]))\n\n"
            "def max_coins(balloons):\n    pass\n\nprint(max_coins(balloons))\n"
        ),
        title="Burst Balloons",
        category="dynamic-programming",
        estimated_minutes=45,
    ),
    "maximal-rectangle": _Spec(
        oracle=maximal_rectangle_area,
        to_input=_to_input_grid,
        format_output=_fmt_identity,
        statement=(
            "Given a `rows x cols` binary matrix (only `0`/`1` entries), "
            "print the **area of the largest rectangle** that contains only "
            "`1`s. Solve by treating each row as the base of a histogram "
            "(accumulating consecutive 1-heights column-by-column from the "
            "row above) and applying the largest-rectangle-in-histogram "
            "technique to each row's histogram."
        ),
        constraints=["0 ≤ rows, cols ≤ 200", "grid[i][j] ∈ {0, 1}"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "rows, cols = map(int, lines[0].split())\n"
            "grid = [list(map(int, lines[1+i].split())) for i in range(rows)]\n\n"
            "def maximal_rectangle(grid):\n    pass\n\nprint(maximal_rectangle(grid))\n"
        ),
        title="Maximal Rectangle",
        category="stack",
        estimated_minutes=40,
    ),
    "longest-valid-parentheses": _Spec(
        oracle=longest_valid_parentheses_length,
        to_input=_to_input_parens,
        format_output=_fmt_identity,
        statement=(
            "Given a string `s` containing only `(` and `)`, print the "
            "**length of the longest contiguous substring** of `s` that is a "
            "well-formed (valid) parentheses sequence."
        ),
        constraints=["0 ≤ s.length ≤ 5×10^4"],
        starter_code=(
            "import sys\ns = sys.stdin.read().rstrip('\\n')\n\n"
            "def longest_valid_parentheses(s):\n    pass\n\n"
            "print(longest_valid_parentheses(s))\n"
        ),
        title="Longest Valid Parentheses",
        category="stack",
        estimated_minutes=35,
    ),
}


# ── Case plans ───────────────────────────────────────────────────────────────

def _plan_median(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_median

    def gen_small():
        m = rng.randint(0, 8)
        n = rng.randint(0 if m else 1, 8)
        a = tg.rand_sorted_array(rng, m, -50, 50) if m else []
        b = tg.rand_sorted_array(rng, n, -50, 50) if n else []
        return (a, b)

    def gen_stress():
        m = rng.randint(2000, 8000)
        n = rng.randint(2000, 8000)
        a = tg.rand_sorted_array(rng, m, -10**6, 10**6)
        b = tg.rand_sorted_array(rng, n, -10**6, 10**6)
        return (a, b)

    visible = [
        ([1, 3], [2]),
        ([1, 2], [3, 4]),
        ([], [1]),
        ([2], []),
        ([1, 2, 3], [4, 5, 6, 7]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([], [1]),
        ([1], []),
        ([], [1, 2]),
        ([1, 1], [1, 1]),
        ([5], [5]),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([1, 2, 3, 4, 5], [6, 7, 8, 9, 10]),      # fully disjoint ranges, no interleave
        ([-5, -4, -3], [3, 4, 5]),                 # negative vs positive split
        ([0, 0, 0, 0], [0, 0, 0]),                 # all duplicates across both arrays
        (list(range(0, 20, 2)), list(range(1, 20, 2))),  # perfectly interleaved
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1], [2]),               # smallest odd-total case
        ([1], [2, 3]),            # smallest even-total case requiring averaging
        ([1, 3, 5], [2, 4]),      # odd total, interleaved
        ([1, 2], [1, 2]),         # even total with tie values at partition
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_regex(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_regex
    alphabet = "ab"

    def gen_small():
        n = rng.randint(0, 6)
        s = tg.rand_string(rng, n, alphabet)
        # build a plausibly-matching-ish pattern of similar length
        m = rng.randint(0, 6)
        toks = []
        while len("".join(toks)) < m:
            c = rng.choice(alphabet + ".")
            toks.append(c)
            if rng.random() < 0.4:
                toks.append("*")
        p = "".join(toks)
        return (s, p)

    def gen_stress():
        n = rng.randint(15, 20)
        s = tg.rand_string(rng, n, alphabet)
        # heavy star usage to stress the DP table size, still within constraints
        toks = []
        while len(toks) < 28:
            toks.append(rng.choice(alphabet + "."))
            if rng.random() < 0.5:
                toks.append("*")
        p = "".join(toks)[:30]
        if p.startswith("*"):
            p = alphabet[0] + p[1:]
        return (s, p)

    visible = [
        ("aa", "a"),
        ("aa", "a*"),
        ("ab", ".*"),
        ("mississippi", "mis*is*p*."),
        ("", ".*"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ("", ""),
        ("a", ""),
        ("", "a*"),
        ("", "a*b*c*"),
        ("a", "."),
        ("a", "a"),
        ("aaa", "a*a*a*"),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ("aab", "c*a*b"),          # leading unmatched-count star that must resolve to zero
        ("bbbba", ".*a*a"),        # multiple stars, only tail must match exactly
        ("aaaaaaaaaaaaaaaaa", "a*a*a*a*a*a*a*a*a*"),  # exponential-blowup trap for naive backtracking
        ("ab", ".*c"),             # pattern longer effectively but must fail (no 'c')
        ("abcd", "d*"),            # star of a char not in s at all, must fail
        ("", "a*b*.*c*"),          # every element optional via star, empty s must pass
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ("aaa", "a*"),             # simple repeat-previous, mutation: off-by-one in star transition
        ("aaa", "ab*a*c*a"),       # multiple stars chained (classic tricky reference case)
        ("a", "ab*"),              # star element absent entirely, must reduce to zero occurrences
        ("bbbba", "b*a*a"),        # star greedily consuming then must backtrack in DP
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_merge_k(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_merge_k

    def gen_small():
        k = rng.randint(1, 5)
        lists = []
        for _ in range(k):
            n = rng.randint(0, 5)
            lists.append(tg.rand_sorted_array(rng, n, -20, 20))
        return (lists,)

    def gen_stress():
        k = rng.randint(50, 200)
        lists = []
        total_budget = rng.randint(5000, 20000)
        per = max(1, total_budget // k)
        for _ in range(k):
            n = rng.randint(0, per)
            lists.append(tg.rand_sorted_array(rng, n, -10000, 10000))
        return (lists,)

    visible = [
        ([[1, 4, 5], [1, 3, 4], [2, 6]],),
        ([[]],),
        ([[1], [0]],),
        ([],),
        ([[1, 1, 1], [1, 1], [1]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([],),
        ([[]],),
        ([[], [], []],),
        ([[5]],),
        ([[1], [2], [3]],),
        ([[-5, -3, -1]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([[0] * 5, [0] * 5, [0] * 5],),                   # all-identical values across all lists
        ([[1, 100], [2, 99], [3, 98], [4, 97]],),           # interleaved extremes
        ([[i for i in range(10)], []],),                    # one list empty, one full
        ([[-1000], [1000], [0]],),                          # single-element extremes
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([[1, 2], [1, 2]],),        # two identical lists — dedup-prone mutation trap
        ([[1], [1], [1]],),         # many singleton ties
        ([[2, 4, 6], [1, 3, 5]],),  # exact alternation
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_burst_balloons(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_balloons

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, 0, 20),)

    def gen_stress():
        n = rng.randint(120, 180)
        return (tg.rand_int_array(rng, n, 0, 100),)

    visible = [
        ([3, 1, 5, 8],),
        ([1, 5],),
        ([7],),
        ([0, 0, 0],),
        ([2, 3, 2],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([1],),
        ([0],),
        ([100],),
        ([1, 1],),
        ([0, 1],),
        ([1, 0],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([1] * 8,),                      # all-equal — greedy tie-breaking trap
        ([100, 1, 1, 1, 1, 1, 1, 100],),  # two huge boundary values, small middle
        (list(range(1, 9)),),             # strictly increasing values
        (list(range(8, 0, -1)),),         # strictly decreasing values
        ([0, 100, 0, 100, 0],),           # alternating extremes with zeros
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 1],),        # smallest 2-balloon case, tests boundary sentinel handling
        ([3, 1, 5],),      # classic reference example (small)
        ([5, 3, 1],),      # order-sensitivity check on the same multiset as above (different order)
        ([2, 8, 4],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_maximal_rectangle(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_grid

    def gen_small():
        rows = rng.randint(1, 6)
        cols = rng.randint(1, 6)
        return ([[rng.randint(0, 1) for _ in range(cols)] for _ in range(rows)],)

    def gen_stress():
        rows = rng.randint(80, 150)
        cols = rng.randint(80, 150)
        return ([[1 if rng.random() < 0.6 else 0 for _ in range(cols)] for _ in range(rows)],)

    visible = [
        ([[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]],),
        ([[0]],),
        ([[1]],),
        ([[1, 1], [1, 1]],),
        ([[0, 1], [1, 0]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([[0]],),
        ([[1]],),
        ([[]],),
        ([[0, 0, 0]],),
        ([[1, 1, 1]],),
        ([[1], [1], [1]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([[1, 1, 0, 1, 1], [1, 1, 0, 1, 1], [0, 0, 0, 0, 0], [1, 1, 1, 1, 0]],),  # two disjoint blocks
        ([[1] * 6 for _ in range(1)] + [[0] * 6],),   # single wide row then all-zero row
        ([[1, 0] * 4 for _ in range(6)],),             # checker-like alternating columns
        ([[1, 1, 1, 1, 1] for _ in range(5)],),        # all-ones square (tests full-area case)
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([[1, 1, 1], [1, 1, 1]],),          # 2x3 all-ones: rectangle != square trap
        ([[1, 1, 0], [1, 1, 0], [1, 1, 0]],),  # 3x2 all-ones column block
        ([[1, 0, 1, 1, 1]],),                # single-row, longest run only
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_longest_valid_parens(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_parens

    def gen_small():
        n = rng.randint(0, 12)
        return ("".join(rng.choice("()") for _ in range(n)),)

    def gen_stress():
        n = rng.randint(3000, 8000)
        return ("".join(rng.choice("()") for _ in range(n)),)

    def gen_balanced_stress():
        # a fully balanced random string built from valid pieces, still random-shaped
        pieces = []
        total = 0
        target = rng.randint(3000, 8000)
        while total < target:
            k = rng.randint(1, 6)
            pieces.append("(" * k + ")" * k)
            total += 2 * k
        return ("".join(pieces),)

    visible = [
        ("(()",),
        (")()())",),
        ("",),
        ("()(()",),
        ("()()",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ("",),
        ("(",),
        (")",),
        ("()",),
        ("((",),
        ("))",),
        ("()()()()()()",),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ("()(()" ,),                 # dangling open in the middle after a valid pair
        ("())(" ,),                  # broken in the middle, valid on both sides separately
        ("(" * 20 + ")" * 10,),       # many unmatched opens before closes
        (")" * 10 + "(" * 20,),       # all closes first (all invalid) then all opens
        ("()" * 5 + "(" + "()" * 5,),  # single stray open splitting two valid runs
        ("("*3 + ")"*3 + "("*3 + ")"*2,),  # trailing dangling open at the very end
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ("(()",),      # classic: answer 2, tests base-index sentinel handling
        (")()())",),   # classic: answer 4
        ("()(())",),   # fully valid nested + sequential — tests whole-string case
        ("(((((",),    # all opens — answer 0
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress_candidates = tg.fill_unique(3, gen_stress, ti, seen) + tg.fill_unique(2, gen_balanced_stress, ti, seen)
    stress = stress_candidates

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


_PLANS: dict[str, Callable[[random.Random], tg.CasePlan]] = {
    "median-of-two-sorted-arrays": _plan_median,
    "regular-expression-matching": _plan_regex,
    "merge-k-sorted-lists": _plan_merge_k,
    "burst-balloons": _plan_burst_balloons,
    "maximal-rectangle": _plan_maximal_rectangle,
    "longest-valid-parentheses": _plan_longest_valid_parens,
}


# ── Builder ────────────────────────────────────────────────────────────────────

def build_famous_hard_problems(
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
        except (OracleError, tg.TestPlanError) as exc:
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
            "hints": [{"level": 1, "text": f"Study the classic hard-tier technique behind {spec.title.lower()} before attempting a brute force."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped


# ── Reference / Wrong solutions (independent of the oracles above) ─────────────

REFERENCE_SOLUTIONS: dict[str, str] = {
    "median-of-two-sorted-arrays": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "p1 = lines[0].split()\nm = int(p1[0])\na = list(map(int, p1[1:1+m]))\n"
        "p2 = lines[1].split()\nn = int(p2[0])\nb = list(map(int, p2[1:1+n]))\n"
        "if len(a) > len(b):\n    a, b = b, a\n    m, n = n, m\n"
        "lo, hi = 0, m\nhalf = (m + n + 1) // 2\n"
        "INF = float('inf')\n"
        "ans = None\n"
        "while lo <= hi:\n"
        "    i = (lo + hi) // 2\n"
        "    j = half - i\n"
        "    a_left = a[i-1] if i > 0 else -INF\n"
        "    a_right = a[i] if i < m else INF\n"
        "    b_left = b[j-1] if j > 0 else -INF\n"
        "    b_right = b[j] if j < n else INF\n"
        "    if a_left <= b_right and b_left <= a_right:\n"
        "        if (m + n) % 2 == 1:\n"
        "            ans = str(int(max(a_left, b_left)))\n"
        "        else:\n"
        "            total = max(a_left, b_left) + min(a_right, b_right)\n"
        "            ans = f'{total/2:.1f}'\n"
        "        break\n"
        "    elif a_left > b_right:\n"
        "        hi = i - 1\n"
        "    else:\n"
        "        lo = i + 1\n"
        "print(ans)\n"
    ),
    "regular-expression-matching": (
        "import sys\n"
        "from functools import lru_cache\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "s = lines[0]\np = lines[1] if len(lines) > 1 else ''\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, j):\n"
        "    if j == len(p):\n        return i == len(s)\n"
        "    first = i < len(s) and (p[j] == s[i] or p[j] == '.')\n"
        "    if j + 1 < len(p) and p[j+1] == '*':\n"
        "        return solve(i, j+2) or (first and solve(i+1, j))\n"
        "    return first and solve(i+1, j+1)\n"
        "print('true' if solve(0, 0) else 'false')\n"
    ),
    "merge-k-sorted-lists": (
        "import sys, heapq\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "k = int(lines[0])\n"
        "heap = []\n"
        "lists = []\n"
        "for i in range(1, k + 1):\n"
        "    parts = lines[i].split()\n"
        "    cnt = int(parts[0])\n"
        "    lst = list(map(int, parts[1:1+cnt]))\n"
        "    lists.append(lst)\n"
        "    if lst:\n"
        "        heapq.heappush(heap, (lst[0], i - 1, 0))\n"
        "out = []\n"
        "while heap:\n"
        "    val, li, idx = heapq.heappop(heap)\n"
        "    out.append(val)\n"
        "    if idx + 1 < len(lists[li]):\n"
        "        heapq.heappush(heap, (lists[li][idx+1], li, idx+1))\n"
        "print(' '.join(map(str, out)))\n"
    ),
    "burst-balloons": (
        "import sys\n"
        "from functools import lru_cache\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "vals = tuple([1] + list(map(int, data[1:n+1])) + [1])\n"
        "sys.setrecursionlimit(10000)\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(l, r):\n"
        "    if r - l < 2:\n        return 0\n"
        "    best = 0\n"
        "    for k in range(l + 1, r):\n"
        "        coins = vals[l] * vals[k] * vals[r] + solve(l, k) + solve(k, r)\n"
        "        if coins > best:\n            best = coins\n"
        "    return best\n"
        "print(solve(0, len(vals) - 1))\n"
    ),
    "maximal-rectangle": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "rows, cols = map(int, lines[0].split())\n"
        "grid = [list(map(int, lines[1+i].split())) for i in range(rows)]\n"
        "def largest_hist(heights):\n"
        "    stack = []\n"
        "    best = 0\n"
        "    hs = heights + [0]\n"
        "    for i, h in enumerate(hs):\n"
        "        while stack and hs[stack[-1]] >= h:\n"
        "            top = stack.pop()\n"
        "            height = hs[top]\n"
        "            width = i if not stack else i - stack[-1] - 1\n"
        "            best = max(best, height * width)\n"
        "        stack.append(i)\n"
        "    return best\n"
        "if rows == 0 or cols == 0:\n"
        "    print(0)\n"
        "else:\n"
        "    heights = [0] * cols\n"
        "    best = 0\n"
        "    for row in grid:\n"
        "        for c in range(cols):\n"
        "            heights[c] = heights[c] + 1 if row[c] == 1 else 0\n"
        "        best = max(best, largest_hist(heights))\n"
        "    print(best)\n"
    ),
    "longest-valid-parentheses": (
        "import sys\n"
        "s = sys.stdin.read().rstrip('\\n')\n"
        "n = len(s)\n"
        "dp = [0] * n\n"
        "best = 0\n"
        "for i in range(1, n):\n"
        "    if s[i] == ')':\n"
        "        if s[i-1] == '(':\n"
        "            dp[i] = (dp[i-2] if i >= 2 else 0) + 2\n"
        "        else:\n"
        "            j = i - dp[i-1] - 1\n"
        "            if j >= 0 and s[j] == '(':\n"
        "                dp[i] = dp[i-1] + 2 + (dp[j-1] if j >= 1 else 0)\n"
        "        best = max(best, dp[i])\n"
        "print(best)\n"
    ),
}


WRONG_SOLUTIONS: dict[str, str] = {
    # Wrong: naively merges + sorts, but computes the mean of the *whole*
    # arrays' midpoints instead of a true combined median (breaks whenever
    # the two arrays aren't the same length / interleave unevenly).
    "median-of-two-sorted-arrays": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "p1 = lines[0].split()\nm = int(p1[0])\na = list(map(int, p1[1:1+m]))\n"
        "p2 = lines[1].split()\nn = int(p2[0])\nb = list(map(int, p2[1:1+n]))\n"
        "merged = sorted(a + b)\n"
        "total = len(merged)\n"
        "if total == 0:\n"
        "    print(0)\n"
        "elif total % 2 == 1:\n"
        "    print(merged[total // 2])\n"
        "else:\n"
        "    # BUG: always averages the two GLOBAL middle values using integer\n"
        "    # division-truncated index, and prints an int, losing the .5 cases\n"
        "    mid = total // 2\n"
        "    avg = (merged[mid - 1] + merged[mid]) // 2\n"
        "    print(avg)\n"
    ),
    # Wrong: treats '*' as shell-glob (zero-or-more of ANY character), not
    # regex repeat-of-preceding-element semantics.
    "regular-expression-matching": (
        "import sys\n"
        "from functools import lru_cache\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "s = lines[0]\np = lines[1] if len(lines) > 1 else ''\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, j):\n"
        "    if j == len(p):\n        return i == len(s)\n"
        "    if p[j] == '*':\n"
        "        # BUG: glob semantics — '*' matches any sequence of any chars,\n"
        "        # ignoring the preceding element entirely\n"
        "        for k in range(i, len(s) + 1):\n"
        "            if solve(k, j + 1):\n"
        "                return True\n"
        "        return False\n"
        "    first = i < len(s) and (p[j] == s[i] or p[j] == '.')\n"
        "    return first and solve(i + 1, j + 1)\n"
        "print('true' if solve(0, 0) else 'false')\n"
    ),
    # Wrong: merges by concatenation + naive per-list pop of only the FIRST
    # element once (not a proper k-way merge) — produces wrong order whenever
    # a list has more than one remaining useful element after the first pass.
    "merge-k-sorted-lists": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "k = int(lines[0])\n"
        "lists = []\n"
        "for i in range(1, k + 1):\n"
        "    parts = lines[i].split()\n"
        "    cnt = int(parts[0])\n"
        "    lists.append(list(map(int, parts[1:1+cnt])))\n"
        "# BUG: just concatenates all lists and sorts — happens to be correct\n"
        "# for VALUES but this alternate bug instead drops every list after\n"
        "# the first that is longer than the first list (simulating a faulty\n"
        "# early-stop k-way merge implementation).\n"
        "out = list(lists[0]) if lists else []\n"
        "base_len = len(lists[0]) if lists else 0\n"
        "for lst in lists[1:]:\n"
        "    if len(lst) <= base_len:\n"
        "        out.extend(lst)\n"
        "out.sort()\n"
        "print(' '.join(map(str, out)))\n"
    ),
    # Wrong: greedy always-burst-the-current-maximum-value-balloon-first —
    # plausible heuristic, but not optimal interval DP.
    "burst-balloons": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "balloons = list(map(int, data[1:n+1]))\n"
        "arr = list(balloons)\n"
        "total = 0\n"
        "while arr:\n"
        "    # BUG: greedily burst the balloon with the max current value first\n"
        "    idx = arr.index(max(arr))\n"
        "    left = arr[idx - 1] if idx > 0 else 1\n"
        "    right = arr[idx + 1] if idx < len(arr) - 1 else 1\n"
        "    total += left * arr[idx] * right\n"
        "    arr.pop(idx)\n"
        "print(total)\n"
    ),
    # Wrong: only checks square sub-regions (side length s x s) instead of
    # general rectangles, so it under-counts wide-but-short (or tall-but-
    # narrow) all-ones regions.
    "maximal-rectangle": (
        "import sys\n"
        "lines = sys.stdin.read().split('\\n')\n"
        "rows, cols = map(int, lines[0].split())\n"
        "grid = [list(map(int, lines[1+i].split())) for i in range(rows)]\n"
        "best = 0\n"
        "if rows and cols:\n"
        "    # BUG: only searches SQUARE sub-regions, never rectangles\n"
        "    for r in range(rows):\n"
        "        for c in range(cols):\n"
        "            if grid[r][c] != 1:\n"
        "                continue\n"
        "            side = 1\n"
        "            while r + side < rows and c + side < cols:\n"
        "                ok = all(grid[r+dr][c+dc] == 1 for dr in range(side+1) for dc in range(side+1))\n"
        "                if not ok:\n"
        "                    break\n"
        "                side += 1\n"
        "            best = max(best, side * side)\n"
        "print(best)\n"
    ),
    # Wrong: counts total balanced-pair characters (a bracket-balance style
    # count) rather than the longest CONTIGUOUS valid run — over-counts when
    # valid runs are separated by invalid characters.
    "longest-valid-parentheses": (
        "import sys\n"
        "s = sys.stdin.read().rstrip('\\n')\n"
        "# BUG: counts total matched pairs anywhere (via a simple counter\n"
        "# stack) and reports 2x that count, ignoring contiguity entirely.\n"
        "stack = []\n"
        "matched_pairs = 0\n"
        "for ch in s:\n"
        "    if ch == '(':\n"
        "        stack.append(ch)\n"
        "    elif ch == ')' and stack:\n"
        "        stack.pop()\n"
        "        matched_pairs += 1\n"
        "print(matched_pairs * 2)\n"
    ),
}
