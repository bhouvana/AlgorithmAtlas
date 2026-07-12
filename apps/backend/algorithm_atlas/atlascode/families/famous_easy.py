"""
Famous-concepts family (Easy tier) — see docs/atlascode-famous-concepts-audit.md
for the selection process (each slug here was verified NOT already present in
the 189-problem catalog before being written). Original AtlasCode wording,
oracles, and tests throughout — no LeetCode statement/example/test data
copied.

Registry-independent (`algorithm_slug=None` for all five, same as
sliding_window_variants.py) — these are recognizable interview patterns, not
1:1 implementations of a single canonical visualization algorithm.

Every problem ships exactly 40 tests via testgen.py from birth (no legacy
4-test debt to migrate) — see testgen.py for the bucket contract.
"""
from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass
from typing import Callable

from .. import testgen as tg
from ...plugins.registry import RegisteredAlgorithm


class OracleError(Exception):
    """Raised when an oracle is asked to evaluate an input outside its domain."""


# ── Independent oracles (pure, no shared-module reuse) ────────────────────────

def move_zeroes(nums: list[int]) -> list[int]:
    non_zero = [x for x in nums if x != 0]
    return non_zero + [0] * (len(nums) - len(non_zero))


def flood_fill(grid: list[list[int]], sr: int, sc: int, new_color: int) -> list[list[int]]:
    if not grid or not (0 <= sr < len(grid)) or not (0 <= sc < len(grid[0])):
        raise OracleError("flood_fill: start cell out of bounds")
    rows, cols = len(grid), len(grid[0])
    old_color = grid[sr][sc]
    result = [row[:] for row in grid]
    if old_color == new_color:
        return result
    stack = [(sr, sc)]
    result[sr][sc] = new_color
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and result[nr][nc] == old_color:
                result[nr][nc] = new_color
                stack.append((nr, nc))
    return result


def merge_sorted_arrays(nums1: list[int], nums2: list[int]) -> list[int]:
    return sorted(nums1 + nums2)


def valid_palindrome_string(s: str) -> bool:
    filtered = [c.lower() for c in s if c.isalnum()]
    return filtered == filtered[::-1]


def find_duplicate_number(nums: list[int]) -> int:
    counts = Counter(nums)
    for val, cnt in counts.items():
        if cnt > 1:
            return val
    raise OracleError("find_duplicate_number: no duplicate present")


# ── to_input / format_output ──────────────────────────────────────────────────

def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


def _ti_move_zeroes(nums):
    return f"{len(nums)} {_arr(nums)}"


def _ti_flood_fill(grid, sr, sc, new_color):
    rows, cols = len(grid), len(grid[0]) if grid else 0
    lines = [f"{rows} {cols} {sr} {sc} {new_color}"]
    lines += [_arr(row) for row in grid]
    return "\n".join(lines)


def _ti_merge_arrays(nums1, nums2):
    return f"{len(nums1)} {_arr(nums1)} {len(nums2)} {_arr(nums2)}"


def _ti_valid_palindrome(s):
    return s


def _ti_find_dup(nums):
    return f"{len(nums)} {_arr(nums)}"


def _fmt_bool(a) -> str:
    return "true" if a else "false"


def _fmt_grid(rows) -> str:
    return "\n".join(_arr(row) for row in rows)


# ── Spec ───────────────────────────────────────────────────────────────────────

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
    difficulty: str = "Easy"
    estimated_minutes: int = 15


# ── Case plans ─────────────────────────────────────────────────────────────────

def _plan_move_zeroes(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _ti_move_zeroes

    def gen_small():
        n = rng.randint(3, 8)
        return ([rng.choice([0, 0, rng.randint(-20, 20)]) for _ in range(n)],)

    def gen_stress():
        n = rng.randint(2000, 5000)
        return ([rng.choice([0, 0, 0, rng.randint(-1000, 1000)]) for _ in range(n)],)

    visible = [
        ([0, 1, 0, 3, 12],), ([0, 0, 0],), ([1, 2, 3],), ([0],), ([4, 0, 5, 0, 6],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = tg.register([([0, 0, 0, 0],), ([1, 2, 3, 4],), ([5],), ([0, 5],)], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = tg.register([
        ([-1, 0, -2, 0, 3],), ([2, 0, 2, 0, 2],), ([0, 0, 0, 0, 0, 7],), ([0, 0, 1, 2, 3],),
    ], ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = tg.register([([0, 1],), ([1, 0],), ([1, 0, 0, 2],)], ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_flood_fill(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _ti_flood_fill

    def gen_small():
        rows, cols = rng.randint(2, 4), rng.randint(2, 4)
        grid = [[rng.choice([0, 1, 2]) for _ in range(cols)] for _ in range(rows)]
        sr, sc = rng.randint(0, rows - 1), rng.randint(0, cols - 1)
        new_color = rng.randint(0, 3)
        return (grid, sr, sc, new_color)

    def gen_stress():
        rows, cols = rng.randint(30, 60), rng.randint(30, 60)
        grid = [[rng.choice([0, 1]) for _ in range(cols)] for _ in range(rows)]
        sr, sc = rng.randint(0, rows - 1), rng.randint(0, cols - 1)
        return (grid, sr, sc, rng.randint(2, 5))

    visible = [
        ([[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2),
        ([[0, 0, 0], [0, 1, 0]], 0, 0, 2),
        ([[1]], 0, 0, 1),
        ([[1, 1], [1, 1]], 0, 0, 9),
        ([[0]], 0, 0, 5),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = tg.register([
        ([[3]], 0, 0, 3), ([[3]], 0, 0, 7), ([[1, 2, 3, 4]], 0, 0, 9), ([[1], [2], [3]], 1, 0, 8),
    ], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = tg.register([
        ([[1, 2, 1], [2, 1, 2], [1, 2, 1]], 0, 0, 9),  # checkerboard — no spread
        ([[5, 5, 5], [5, 5, 5], [5, 5, 5]], 1, 1, 8),  # entire grid one color
        ([[1, 1, 0, 1, 1]], 0, 0, 2),  # two disjoint same-color regions, only left should change
        ([[1, 1], [1, 1]], 0, 0, 1),  # new_color == old_color, must be a true no-op
    ], ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = tg.register([
        # diagonal neighbor shares old_color but is NOT 4-connected — must NOT be filled
        ([[1, 2], [2, 1]], 0, 0, 9),
        ([[1, 0, 1], [0, 0, 0], [1, 0, 1]], 1, 1, 4),
        ([[2, 2, 2], [2, 3, 2], [2, 2, 2]], 0, 0, 5),
    ], ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_merge_arrays(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _ti_merge_arrays

    def gen_small():
        n1, n2 = rng.randint(1, 5), rng.randint(1, 5)
        a = sorted(tg.rand_int_array(rng, n1, -20, 20))
        b = sorted(tg.rand_int_array(rng, n2, -20, 20))
        return (a, b)

    def gen_stress():
        n1, n2 = rng.randint(1000, 3000), rng.randint(1000, 3000)
        a = sorted(tg.rand_int_array(rng, n1, -10_000, 10_000))
        b = sorted(tg.rand_int_array(rng, n2, -10_000, 10_000))
        return (a, b)

    visible = [
        ([1, 3, 5], [2, 4, 6]), ([1, 2, 3], []), ([], [1, 2, 3]), ([1, 1, 1], [1, 1]), ([-5, 0, 5], [-3, 3]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = tg.register([([], []), ([1], []), ([], [1]), ([1], [1])], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = tg.register([
        ([1, 1, 1, 1], [1, 1]),           # heavy duplicate overlap
        ([1, 2, 3], [4, 5, 6]),           # a entirely before b
        ([4, 5, 6], [1, 2, 3]),           # b entirely before a — exercises b's remainder path
        ([1, 3, 5, 7, 9], [2, 4]),        # b exhausted early, a has long remainder
    ], ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = tg.register([
        ([1], [1, 2, 3]),   # a exhausted first — must append b's remainder
        ([1, 2, 3], [1]),   # b exhausted first — must append a's remainder
        ([5], [5]),         # exact tie
    ], ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_valid_palindrome(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _ti_valid_palindrome
    alphabet_letters = "abcdefghijklmnopqrstuvwxyz"
    punctuation = ",.: -'!?"

    def _inject_punct(core: str) -> str:
        out = []
        for ch in core:
            out.append(ch)
            if rng.random() < 0.3:
                out.append(rng.choice(punctuation))
        return "".join(out)

    def gen_small():
        n = rng.randint(1, 8)
        s = "".join(rng.choice(alphabet_letters + alphabet_letters.upper()) for _ in range(n))
        return (_inject_punct(s),)

    def gen_stress():
        n = rng.randint(1000, 3000)
        if rng.random() < 0.5:
            half = "".join(rng.choice(alphabet_letters) for _ in range(n // 2))
            core = half + (rng.choice(alphabet_letters) if n % 2 else "") + half[::-1]
        else:
            core = "".join(rng.choice(alphabet_letters) for _ in range(n))
        return (_inject_punct(core),)

    visible = [
        ("A man, a plan, a canal: Panama",), ("race a car",), ("",), ("a",), ("0P",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = tg.register([
        ("",), ("a",), (".,!?",), ("aa",), ("ab",),
    ], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = tg.register([
        ("Aa",),                              # mixed case true palindrome
        ("Was it a car or a cat I saw?",),    # long true palindrome with punctuation
        ("12321",),                            # numeric palindrome
        ("1a2",),                              # false — digit/letter mismatch across mirror
    ], ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = tg.register([
        ("Aba",),   # fails if case not normalized
        ("A.a",),   # fails if punctuation not stripped
        ("Ab",),    # true negative, case-normalized
    ], ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_find_duplicate(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _ti_find_dup

    def _make(n: int, extra_copies: int = 1) -> tuple[list[int]]:
        perm = list(range(1, n + 1))
        rng.shuffle(perm)
        dup_val = rng.choice(perm)
        arr = perm[:]
        for _ in range(extra_copies):
            idx = rng.randint(0, len(arr))
            arr.insert(idx, dup_val)
        return (arr,)

    def gen_small():
        return _make(rng.randint(2, 10))

    def gen_stress():
        return _make(rng.randint(2000, 5000))

    visible = [
        ([1, 3, 4, 2, 2],), ([3, 1, 3, 4, 2],), ([1, 1],), ([2, 2, 2, 1, 3, 4],), ([1, 2, 3, 4, 5, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = tg.register([_make(2), _make(2), _make(3), _make(3)], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = tg.register([
        _make(10, extra_copies=1),
        (list(range(1, 11)) + [1],),       # duplicate is the minimum value, at the very end
        ([10] + list(range(1, 11)),),      # duplicate is the maximum value, at the very start
        _make(15, extra_copies=2),          # duplicate appears three times total
    ], ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = tg.register([
        ([1, 2, 2],),   # smallest possible array, dup adjacent
        ([2, 1, 2],),   # dup non-adjacent, smallest case
        ([1, 2, 3, 1],),  # dup wraps first-to-last
    ], ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── Specs ──────────────────────────────────────────────────────────────────────

_SPECS: dict[str, _Spec] = {
    "move-zeroes": _Spec(
        oracle=move_zeroes, to_input=_ti_move_zeroes, format_output=_arr,
        statement=(
            "Given an integer array `nums`, print the array after moving all `0`s "
            "to the end while preserving the **relative order** of the non-zero "
            "elements."
        ),
        constraints=["1 ≤ nums.length ≤ 10^4", "-10^9 ≤ nums[i] ≤ 10^9"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0]); nums = list(map(int, data[1:1+n]))\n\n"
            "def move_zeroes(nums):\n    pass\n\n"
            "print(' '.join(map(str, move_zeroes(nums))))\n"
        ),
        title="Move Zeroes to End", category="arrays",
    ),
    "flood-fill": _Spec(
        oracle=flood_fill, to_input=_ti_flood_fill, format_output=_fmt_grid,
        statement=(
            "Given a grid of colors and a starting cell `(sr, sc)`, print the grid "
            "after **flood-filling** the 4-directionally-connected region of cells "
            "sharing the starting cell's original color with `new_color` (no change "
            "if `new_color` already equals the starting color)."
        ),
        constraints=["1 ≤ rows, cols ≤ 100", "0 ≤ grid[i][j], new_color ≤ 65535"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split('\\n')\n"
            "rows, cols, sr, sc, new_color = map(int, data[0].split())\n"
            "grid = [list(map(int, data[1+i].split())) for i in range(rows)]\n\n"
            "def flood_fill(grid, sr, sc, new_color):\n    pass\n\n"
            "result = flood_fill(grid, sr, sc, new_color)\n"
            "print('\\n'.join(' '.join(map(str, row)) for row in result))\n"
        ),
        title="Flood Fill", category="graphs", estimated_minutes=20,
    ),
    "merge-sorted-arrays-inplace": _Spec(
        oracle=merge_sorted_arrays, to_input=_ti_merge_arrays, format_output=_arr,
        statement=(
            "Given two already-sorted integer arrays, print the single sorted "
            "array formed by merging them."
        ),
        constraints=["0 ≤ nums1.length, nums2.length ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
            "n1=int(data[idx]);idx+=1\na=list(map(int,data[idx:idx+n1]));idx+=n1\n"
            "n2=int(data[idx]);idx+=1\nb=list(map(int,data[idx:idx+n2]))\n\n"
            "def merge_sorted(a, b):\n    pass\n\nprint(' '.join(map(str, merge_sorted(a, b))))\n"
        ),
        title="Merge Two Sorted Arrays", category="arrays",
    ),
    "valid-palindrome-string": _Spec(
        oracle=valid_palindrome_string, to_input=_ti_valid_palindrome, format_output=_fmt_bool,
        statement=(
            "Given a string, considering only alphanumeric characters and ignoring "
            "case, print `true` if it reads the same forward and backward, else "
            "`false`."
        ),
        constraints=["0 ≤ s.length ≤ 2×10^5"],
        starter_code=(
            "import sys\ns = sys.stdin.readline().rstrip('\\n')\n\n"
            "def is_valid_palindrome(s):\n    pass\n\n"
            "print('true' if is_valid_palindrome(s) else 'false')\n"
        ),
        title="Valid Palindrome String", category="strings",
    ),
    "find-duplicate-number": _Spec(
        oracle=find_duplicate_number, to_input=_ti_find_dup, format_output=str,
        statement=(
            "An array of length `n+1` contains integers in `[1, n]` with exactly "
            "one value repeated one or more times (all others appear exactly "
            "once). Print the repeated value."
        ),
        constraints=["2 ≤ n ≤ 10^5"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\n"
            "n = int(data[0]); nums = list(map(int, data[1:1+n]))\n\n"
            "def find_duplicate(nums):\n    pass\n\nprint(find_duplicate(nums))\n"
        ),
        title="Find the Duplicate Number", category="arrays", estimated_minutes=20,
    ),
}

_PLANS: dict[str, Callable[[random.Random], tg.CasePlan]] = {
    "move-zeroes": _plan_move_zeroes,
    "flood-fill": _plan_flood_fill,
    "merge-sorted-arrays-inplace": _plan_merge_arrays,
    "valid-palindrome-string": _plan_valid_palindrome,
    "find-duplicate-number": _plan_find_duplicate,
}


# ── Builder ─────────────────────────────────────────────────────────────────────

def build_famous_easy_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue

        plan_fn = _PLANS[slug]
        try:
            rng = tg.problem_rng(slug)
            case_plan = plan_fn(rng)
            test_spec = tg.TestSpec(oracle=spec.oracle, to_input=spec.to_input, format_output=spec.format_output)
            test_cases = tg.build_forty(slug, test_spec, case_plan)
        except (OracleError, tg.TestPlanError) as exc:
            skipped.append((slug, str(exc)))
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
            "hints": [{"level": 1, "text": f"Think about the classic {spec.title} pattern."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped


# ── Reference / wrong solutions (for verify_atlascode_family.py integration) ──

REFERENCE_SOLUTIONS: dict[str, str] = {
    "move-zeroes": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0]); nums = list(map(int, data[1:1+n]))\n"
        "pos = 0\n"
        "for i in range(n):\n"
        "    if nums[i] != 0:\n"
        "        nums[pos], nums[i] = nums[i], nums[pos]\n"
        "        pos += 1\n"
        "print(' '.join(map(str, nums)))\n"
    ),
    "flood-fill": (
        "import sys\nfrom collections import deque\n"
        "data = sys.stdin.read().split('\\n')\n"
        "rows, cols, sr, sc, new_color = map(int, data[0].split())\n"
        "grid = [list(map(int, data[1+i].split())) for i in range(rows)]\n"
        "old_color = grid[sr][sc]\n"
        "if old_color != new_color:\n"
        "    q = deque([(sr, sc)]); grid[sr][sc] = new_color\n"
        "    while q:\n"
        "        r, c = q.popleft()\n"
        "        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n"
        "            nr, nc = r+dr, c+dc\n"
        "            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==old_color:\n"
        "                grid[nr][nc] = new_color; q.append((nr, nc))\n"
        "print('\\n'.join(' '.join(map(str, row)) for row in grid))\n"
    ),
    "merge-sorted-arrays-inplace": (
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n1=int(data[idx]);idx+=1\na=list(map(int,data[idx:idx+n1]));idx+=n1\n"
        "n2=int(data[idx]);idx+=1\nb=list(map(int,data[idx:idx+n2]))\n"
        "i=j=0\nresult=[]\n"
        "while i<len(a) and j<len(b):\n"
        "    if a[i]<=b[j]:\n        result.append(a[i]); i+=1\n"
        "    else:\n        result.append(b[j]); j+=1\n"
        "result.extend(a[i:]); result.extend(b[j:])\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "valid-palindrome-string": (
        "import sys\ns = sys.stdin.readline().rstrip('\\n')\n"
        "filtered = [c.lower() for c in s if c.isalnum()]\n"
        "print('true' if filtered == filtered[::-1] else 'false')\n"
    ),
    "find-duplicate-number": (
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0]); nums = list(map(int, data[1:1+n]))\n"
        "slow = fast = nums[0]\n"
        "while True:\n"
        "    slow = nums[slow]; fast = nums[nums[fast]]\n"
        "    if slow == fast:\n        break\n"
        "slow2 = nums[0]\n"
        "while slow2 != slow:\n    slow2 = nums[slow2]; slow = nums[slow]\n"
        "print(slow2)\n"
    ),
}

WRONG_SOLUTIONS: dict[str, str] = {
    "move-zeroes": (
        # BUG: moves zeros to the FRONT instead of the end (reversed spec)
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0]); nums = list(map(int, data[1:1+n]))\n"
        "zeros = [x for x in nums if x == 0]\n"
        "nonzeros = [x for x in nums if x != 0]\n"
        "print(' '.join(map(str, zeros + nonzeros)))\n"
    ),
    "flood-fill": (
        # BUG: uses 8-directional (diagonal-inclusive) adjacency instead of 4-directional
        "import sys\nfrom collections import deque\n"
        "data = sys.stdin.read().split('\\n')\n"
        "rows, cols, sr, sc, new_color = map(int, data[0].split())\n"
        "grid = [list(map(int, data[1+i].split())) for i in range(rows)]\n"
        "old_color = grid[sr][sc]\n"
        "if old_color != new_color:\n"
        "    q = deque([(sr, sc)]); grid[sr][sc] = new_color\n"
        "    while q:\n"
        "        r, c = q.popleft()\n"
        "        for dr in (-1,0,1):\n"
        "            for dc in (-1,0,1):\n"
        "                if dr==0 and dc==0: continue\n"
        "                nr, nc = r+dr, c+dc\n"
        "                if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==old_color:\n"
        "                    grid[nr][nc]=new_color; q.append((nr,nc))\n"
        "print('\\n'.join(' '.join(map(str, row)) for row in grid))\n"
    ),
    "merge-sorted-arrays-inplace": (
        # BUG: forgets to append the remainder of b once a is exhausted
        "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
        "n1=int(data[idx]);idx+=1\na=list(map(int,data[idx:idx+n1]));idx+=n1\n"
        "n2=int(data[idx]);idx+=1\nb=list(map(int,data[idx:idx+n2]))\n"
        "i=j=0\nresult=[]\n"
        "while i<len(a) and j<len(b):\n"
        "    if a[i]<=b[j]:\n        result.append(a[i]); i+=1\n"
        "    else:\n        result.append(b[j]); j+=1\n"
        "result.extend(a[i:])\n"
        "print(' '.join(map(str, result)))\n"
    ),
    "valid-palindrome-string": (
        # BUG: forgets to lowercase before comparing (case-sensitive)
        "import sys\ns = sys.stdin.readline().rstrip('\\n')\n"
        "filtered = [c for c in s if c.isalnum()]\n"
        "print('true' if filtered == filtered[::-1] else 'false')\n"
    ),
    "find-duplicate-number": (
        # BUG: only detects ADJACENT duplicates, misses non-adjacent ones
        "import sys\ndata = sys.stdin.read().split()\n"
        "n = int(data[0]); nums = list(map(int, data[1:1+n]))\n"
        "for i in range(len(nums)-1):\n"
        "    if nums[i] == nums[i+1]:\n        print(nums[i]); sys.exit()\n"
        "print(-1)\n"
    ),
}
