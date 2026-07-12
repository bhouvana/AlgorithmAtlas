"""
40-test case plans for the `dp-variants` family (see testgen.py for the
shared bucket contract: visible 5 / basic 7 / boundary 8 / adversarial 8 /
mutation 7 / stress 5 = 40). One entry per slug in dp_variants.py's `_SPECS`.

Each `to_input` mirrors the exact stdin format the original hand-written
`_Spec.cases` already used (verified against dp_variants.py before writing
this) and matches the reference/wrong solutions registered in
scripts/verify_atlascode_family.py.

Stress-bucket sizes are deliberately kept well below the problems' stated
constraints where an O(n^2) (or worse) REFERENCE solution is registered for
smoke-testing (not just the oracle) — e.g. `maximum-subarray-circular`'s
reference is an O(n^2) two-loop scan, and `best-time-to-buy-sell-stock`'s
reference is an O(n^2) nested loop, so both cap stress n well under their
10^4/10^5-scale problem constraints to stay inside the judge's 5s/test
timeout.
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


# ── triangle-minimum-path-sum: oracle(triangle) ───────────────────────────────

def _to_input_triangle(triangle):
    lines = [str(len(triangle))] + [_arr(row) for row in triangle]
    return "\n".join(lines)


def _rand_triangle(rng: random.Random, rows: int, lo: int, hi: int) -> list[list[int]]:
    return [[rng.randint(lo, hi) for _ in range(r + 1)] for r in range(rows)]


def _plan_triangle(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_triangle

    def gen_small():
        rows = rng.randint(2, 6)
        return (_rand_triangle(rng, rows, -20, 20),)

    def gen_stress():
        rows = rng.randint(120, 180)
        return (_rand_triangle(rng, rows, -1000, 1000),)

    visible = [
        ([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]],),
        ([[-10]],),
        ([[1], [2, 3]],),
        ([[-1], [0, 5], [3, -5, 2], [-2, 5, -5, -3], [-4, 0, 2, -2, 1]],),
        ([[5], [1, 2], [3, 4, 5]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([[0]],),
        ([[1], [1, 1]],),
        ([[0], [0, 0]],),
        ([[-1], [-1, -1]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([[0], [100, -100], [1, 1, 1]],),          # deceptive huge negative mid-row
        ([[1], [2, 2], [3, 100, 3], [4, 4, 4, 4]],),  # single expensive interior cell
        ([[10], [-10, -10], [10, -10, 10]],),
        ([[0], [0, 0], [0, 0, 0], [-50, 0, 0, 0]],),  # cheap path only on far edge
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([[1], [2, 1], [1, 2, 1]],),   # symmetric rows — off-by-one column index catchable
        ([[1], [1, 1], [1, 1, 1]],),   # all-equal, sums determined purely by path LENGTH
        ([[2], [1, 3]],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── best-time-to-buy-sell-stock: oracle(prices) ───────────────────────────────

def _to_input_prices(prices):
    return f"{len(prices)} {_arr(prices)}"


def _plan_stock1(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_prices

    def gen_small():
        n = rng.randint(2, 8)
        return (tg.rand_int_array(rng, n, 1, 100),)

    def gen_stress():
        n = rng.randint(600, 900)
        return (tg.rand_int_array(rng, n, 1, 10_000),)

    visible = [
        ([7, 1, 5, 3, 6, 4],), ([7, 6, 4, 3, 1],), ([5],), ([1, 2],), ([3, 3, 3, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1],), ([1, 1],), ([1, 100],), ([100, 1],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(20, 0, -1)),),               # strictly descending — best profit is 0
        (list(range(1, 20)),),                    # strictly ascending — buy first sell last
        ([1, 100, 1, 100, 1, 100],),               # oscillating, only one transaction allowed
        ([50, 1, 100, 2, 99],),                    # best pair not adjacent
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 1],),      # descending pair — must NOT buy-then-sell backward
        ([1, 2],),      # minimal ascending pair
        ([3, 1, 4],),   # min after first, still improving later
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── best-time-to-buy-sell-stock-ii: oracle(prices) ────────────────────────────

def _plan_stock2(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_prices

    def gen_small():
        n = rng.randint(2, 8)
        return (tg.rand_int_array(rng, n, 1, 100),)

    def gen_stress():
        n = rng.randint(2000, 5000)
        return (tg.rand_int_array(rng, n, 1, 10_000),)

    visible = [
        ([7, 1, 5, 3, 6, 4],), ([1, 2, 3, 4, 5],), ([7, 6, 4, 3, 1],), ([5],), ([2, 4, 1, 7],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1],), ([1, 1],), ([1, 100],), ([100, 1],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(20, 0, -1)),),                # all descending — profit 0
        ([1, 5, 1, 5, 1, 5, 1, 5],),                # many small alternating gains
        ([10, 10, 10, 10],),                        # all flat — profit 0
        ([1, 2, 1, 2, 1, 2, 1, 2, 1, 2],),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2, 3],),      # must sum EVERY daily gain, not just first-to-last
        ([3, 2, 1],),      # no gains at all
        ([1, 3, 2, 4],),   # gain, dip, gain — two separate transactions
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── partition-equal-subset-sum: oracle(nums) ──────────────────────────────────

def _plan_partition(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_prices

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, 1, 30),)

    def gen_stress():
        n = rng.randint(150, 200)
        return (tg.rand_int_array(rng, n, 1, 100),)

    visible = [
        ([1, 5, 11, 5],), ([1, 2, 3, 5],), ([1],), ([1, 2, 5],), ([2, 2, 2, 2],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1],), ([2],), ([1, 1],), ([1, 3],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1] * 21,),                          # odd count of 1s — odd total, impossible
        ([1] * 20,),                          # even count of 1s — always splittable
        ([100, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],),  # one dominant value blocks a naive split
        ([3, 3, 3, 3, 3, 3],),                 # all-equal, splittable only with even count
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 1, 1, 1],),   # sum=4, target=2, easy dup-based split
        ([2, 2, 3, 3],),   # sum=10, target=5, needs cross-value split
        ([1, 2, 3],),      # sum=6, target=3, exact single-element hit
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── target-sum-ways: oracle(nums, target) ─────────────────────────────────────

def _to_input_target(nums, target):
    return f"{len(nums)} {_arr(nums)} {target}"


def _plan_target_sum(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_target

    def gen_small():
        n = rng.randint(1, 6)
        nums = tg.rand_int_array(rng, n, 0, 10)
        target = rng.randint(-sum(nums), sum(nums))
        return (nums, target)

    def gen_stress():
        n = rng.randint(16, 20)
        nums = tg.rand_int_array(rng, n, 0, 20)
        target = rng.randint(-sum(nums), sum(nums))
        return (nums, target)

    visible = [
        ([1, 1, 1, 1, 1], 3), ([1], 1), ([0], 0), ([1, 1, 1], 1), ([2, 3], 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([0], 0), ([1], -1), ([0, 0], 0), ([5], 5)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([0, 0, 0, 0], 0),        # every zero can flip sign freely, all 16 assignments valid
        ([10, 1, 1, 1, 1], 8),    # one big value forces a specific sign choice
        ([1, 1, 1, 1, 1, 1], 100),  # unreachable target — must print 0
        ([5, 5, 5], 5),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2], 1),     # +1-2=-1, -1+2=1 — exactly one of two sign flips works
        ([1, 2], -1),    # the mirror-sign target of the case above
        ([1, 1], 0),     # symmetric zero target
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── perfect-squares-min-count: oracle(n) ──────────────────────────────────────

def _to_input_n(n):
    return str(n)


def _plan_perfect_squares(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_n

    def gen_small():
        return (rng.randint(1, 60),)

    def gen_stress():
        return (rng.randint(9000, 10_000),)

    visible = [(12,), (13,), (1,), (100,), (2,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(1,), (2,), (3,), (4,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (9999,),   # near-limit non-square, forces the full DP fill
        (9801,),   # 99^2, a perfect square itself — answer should be 1
        (7,),      # 4+1+1+1 vs naively greedy 4+1+1+1 — needs true DP, not greedy
        (23,),     # classic greedy-fails case (4*5+1*3=... true answer differs from greedy)
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (12,),   # greedy (9+1+1+1=4) vs optimal (4+4+4=3) mismatch
        (28,),   # greedy vs optimal mismatch
        (6,),    # 4+1+1=3 vs true optimal check
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── combination-sum-iv-count: oracle(nums, target) ────────────────────────────

def _plan_combination_sum4(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_target

    def gen_small():
        n = rng.randint(1, 4)
        nums = sorted(set(tg.rand_int_array(rng, n, 1, 8)))
        target = rng.randint(0, 12)
        return (nums, target)

    def gen_stress():
        n = rng.randint(15, 20)
        nums = sorted(set(tg.rand_int_array(rng, n, 1, 30)))
        target = rng.randint(400, 1000)
        return (nums, target)

    visible = [
        ([1, 2, 3], 4), ([9], 3), ([5], 0), ([1, 2], 3), ([1], 5),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1], 0), ([1], 1), ([1000], 1000), ([2], 1)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 2, 3], 32),        # target large enough to blow up a memo-less recursion
        ([3, 5, 7], 1),          # no element fits — must print 0
        ([1], 30),               # single element repeated many times — only 1 valid sequence
        ([2, 4, 6], 5),          # all even elements, odd target — unreachable, must print 0
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2], 3),   # (1,2) and (2,1) count as 2 DIFFERENT ordered sequences
        ([1, 2], 2),   # (1,1) and (2) both valid — order-sensitive vs combination-only mismatch
        ([2, 3], 5),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── delete-and-earn: oracle(nums) ─────────────────────────────────────────────

def _plan_delete_and_earn(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_prices

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, 1, 20),)

    def gen_stress():
        n = rng.randint(3000, 5000)
        return (tg.rand_int_array(rng, n, 1, 10_000),)

    visible = [
        ([3, 4, 2, 3],), ([2, 2, 3, 3, 3, 4],), ([5],), ([1, 1, 1],), ([1, 2, 3, 4],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1],), ([1, 1],), ([10000],), ([1, 2],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(1, 15)),),                 # fully consecutive run — classic house-robber trap
        ([5] * 10,),                             # all-equal, single value dominates
        ([1, 3, 5, 7, 9],),                      # alternating gaps of 2 — every value independently takeable
        ([2, 2, 3, 3, 4, 4, 5, 5],),             # every value duplicated, mixed consecutive runs
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 2, 3, 3, 3, 4],),   # earning 3 requires deleting BOTH 2s and the 4
        ([1, 2, 3],),             # simple consecutive chain of 3
        ([1, 1, 1, 2, 2, 2],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── maximum-subarray-circular: oracle(nums) ───────────────────────────────────
# NOTE: the registered REFERENCE solution is an O(n^2) double loop (see
# scripts/verify_atlascode_family.py) — stress n is capped well under the
# problem's stated 3x10^4 constraint to keep the reference inside 5s/test.

def _plan_max_subarray_circular(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_prices

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, -20, 20),)

    def gen_stress():
        n = rng.randint(500, 700)
        return (tg.rand_int_array(rng, n, -1000, 1000),)

    visible = [
        ([1, -2, 3, -2],), ([5, -3, 5],), ([-2, -3, -1],), ([-5],), ([3, -1, 2, -1],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1],), ([-1],), ([0],), ([1, -1],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([-1, -2, -3, -4],),          # all negative — must return the single LEAST-negative element
        ([5, -2, 5, -2, 5],),          # wraparound sum beats any non-wrapping subarray
        ([10, -100, 10, -100, 10],),   # extreme dip in the middle, edges must wrap together
        ([1, 1, 1, 1, 1],),            # all positive — whole array (no wrap needed) is optimal
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([3, -2, 3],),   # wraparound (3+3=6) beats non-wrap best (3)
        ([-1, 3, -1],),  # non-wrap best beats any wraparound candidate
        ([2, -1, 2, -1, 2],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── jump-game-ii-min-jumps: oracle(nums) ──────────────────────────────────────
# NOTE: every generated array MUST guarantee the last index is reachable (the
# problem's own stated precondition) — both the oracle and the registered
# reference solution behave unpredictably (oracle) / print `inf` (reference,
# via its lru_cache recursion hitting a nums[i]==0 dead end) otherwise.

def _reachable_jump_array(rng: random.Random, n: int, max_jump: int) -> list[int]:
    """Build an n-length array with nums[-1] guaranteed reachable from index 0:
    walk backward from the last index, each step picking a predecessor within
    max_jump and a jump value that reaches (or overshoots) the current index."""
    if n == 1:
        return [rng.randint(0, max_jump)]
    nums = [0] * n
    pos = n - 1
    while pos > 0:
        step = rng.randint(1, min(max_jump, pos))
        prev = pos - step
        nums[prev] = max(nums[prev] if nums[prev] else 0, step, rng.randint(0, max_jump))
        pos = prev
    for i in range(n - 1):
        if nums[i] == 0:
            nums[i] = rng.randint(1, max_jump)
    return nums


def _plan_jump_game2(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_prices

    def gen_small():
        n = rng.randint(1, 8)
        return (_reachable_jump_array(rng, n, 4),)

    def gen_stress():
        n = rng.randint(600, 900)
        return (_reachable_jump_array(rng, n, 6),)

    visible = [
        ([2, 3, 1, 1, 4],), ([2, 3, 0, 1, 4],), ([0],), ([1, 1],), ([1, 2, 1, 1, 1],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([0],), ([1],), ([1, 0],), ([2, 0, 0],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1] * 10,),                        # every step exactly 1 — must take n-1 jumps
        ([9] + [0] * 9,),                    # a single huge first jump clears everything
        ([3, 2, 1, 0, 4],),                  # a zero cell that must be jumped OVER, never landed on
        ([2, 1, 1, 1, 1, 1, 1, 1, 1],),      # marginal first jump forces many small hops
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 3, 1, 1, 4],),   # greedy-max-jump (index0->2) vs optimal window-based choice differ
        ([1, 3, 2],),          # taking the max jump early wastes reach vs optimal
        ([3, 1, 1, 1],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

DP_VARIANT_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "triangle-minimum-path-sum": (_to_input_triangle, str, _plan_triangle),
    "best-time-to-buy-sell-stock": (_to_input_prices, str, _plan_stock1),
    "best-time-to-buy-sell-stock-ii": (_to_input_prices, str, _plan_stock2),
    "partition-equal-subset-sum": (_to_input_prices, lambda a: "true" if a else "false", _plan_partition),
    "target-sum-ways": (_to_input_target, str, _plan_target_sum),
    "perfect-squares-min-count": (_to_input_n, str, _plan_perfect_squares),
    "combination-sum-iv-count": (_to_input_target, str, _plan_combination_sum4),
    "delete-and-earn": (_to_input_prices, str, _plan_delete_and_earn),
    "maximum-subarray-circular": (_to_input_prices, str, _plan_max_subarray_circular),
    "jump-game-ii-min-jumps": (_to_input_prices, str, _plan_jump_game2),
}
