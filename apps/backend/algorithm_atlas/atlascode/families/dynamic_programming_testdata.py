"""
40-test case plans for the `dynamic-programming` family (see testgen.py for
the shared bucket contract: visible 5 / basic 7 / boundary 8 / adversarial 8
/ mutation 7 / stress 5 = 40). One entry per slug in dynamic_programming.py's
`_SPECS`.

Each `to_input` mirrors the exact stdin format the original hand-written
`_Spec.cases` already used (verified against dynamic_programming.py before
writing this).

Stress-bucket sizing note: several reference solutions registered in
scripts/verify_atlascode_family.py use `functools.lru_cache` RECURSION
(interleaving-strings, wildcard-matching, distinct-subsequences,
matrix-chain-multiplication, palindrome-subsequence, boolean-parenthesization,
word-wrap, egg-drop's inner loop is iterative but O(eggs*floors^2)) rather
than an explicit iterative table. Python's default recursion limit is 1000,
and the judge subprocess does not raise it, so stress inputs for those slugs
are kept well below a few hundred to avoid RecursionError, independent of
whatever the family's stated constraint upper bound is. This mirrors the
project's standing rule: stress cases must comfortably finish (both in time
AND without blowing the recursion stack) inside the judge's 5-second-per-test
budget, not necessarily hit the full documented constraint ceiling.
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


def _fmt_bool(a) -> str:
    return "true" if a else "false"


# ── staircase: oracle(n) ───────────────────────────────────────────────────────

def _to_input_staircase(n):
    return f"{n}"


def _plan_staircase(rng: random.Random) -> tg.CasePlan:
    # staircase's entire domain is a single integer n in [0, 40] — only 41
    # possible distinct stdin strings total. 40 unique tests need almost the
    # whole domain, so buckets use non-overlapping anchor sets instead of
    # relying on random collision-avoidance to find enough unique values.
    # (Previous version's boundary_anchors reused 0/1/2, already claimed by
    # visible/basic — tg.register() silently drops the duplicates, leaving
    # boundary 3 short. This partition uses each of 0-40 (except 35) exactly
    # once, verified by construction, not by re-running and hoping.)
    seen: set[str] = set()
    ti = _to_input_staircase

    visible = [(0,), (1,), (5,), (10,), (30,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic_anchors = [(6,), (7,), (8,), (9,), (11,), (12,), (13,)]
    basic = tg.register(basic_anchors, ti, seen)

    boundary_anchors = [(2,), (3,), (4,), (36,), (37,), (38,), (39,), (40,)]
    boundary = tg.register(boundary_anchors, ti, seen)

    adversarial_anchors = [(14,), (15,), (16,), (17,), (18,), (19,), (20,), (21,)]
    adversarial = tg.register(adversarial_anchors, ti, seen)

    mutation_anchors = [(22,), (23,), (24,), (25,), (26,), (27,), (28,)]
    mutation = tg.register(mutation_anchors, ti, seen)

    stress_anchors = [(29,), (31,), (32,), (33,), (34,)]
    stress = tg.register(stress_anchors, ti, seen)

    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── jump-game: oracle(nums) ───────────────────────────────────────────────────

def _to_input_jump(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_jump_game(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_jump

    def gen_small():
        n = rng.randint(2, 8)
        return (tg.rand_int_array(rng, n, 0, 5),)

    def gen_stress():
        n = rng.randint(5000, 10_000)
        return (tg.rand_int_array(rng, n, 0, 3),)

    visible = [
        ([2, 3, 1, 1, 4],), ([3, 2, 1, 0, 4],), ([0],), ([1, 0, 1, 0],), ([2, 0, 0],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([0],), ([1],), ([1, 1],), ([100000],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 0, 1, 0, 1],),      # dead zero right after a jump lands exactly on it
        ([3, 0, 0, 0, 1],),      # must clear a run of zeros in one big jump
        ([2, 5, 0, 0, 0, 0, 0],),  # early big jump masks later zero desert
        ([1, 1, 1, 1, 0],),      # exactly reaches the last index with 1s
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([0, 1],),      # last index has a zero but it's already reached
        ([1, 2, 0, 1],),
        ([5, 0, 0, 0, 0, 0],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── subset-sum: oracle(nums, target) ──────────────────────────────────────────

def _to_input_subset_sum(nums, target):
    return f"{len(nums)} {_arr(nums)} {target}"


def _plan_subset_sum(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_subset_sum

    def gen_small():
        n = rng.randint(1, 8)
        nums = tg.rand_int_array(rng, n, 0, 50)
        target = rng.randint(0, 200)
        return (nums, target)

    def gen_stress():
        n = 20
        nums = tg.rand_int_array(rng, n, 0, 1000)
        target = rng.randint(0, 5000)
        return (nums, target)

    visible = [
        ([3, 34, 4, 12, 5, 2], 9), ([3, 34, 4, 12, 5, 2], 30), ([], 0),
        ([1, 5, 10, 20], 25), ([2, 4, 6], 5),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([], 0), ([0], 0), ([5], 5), ([5], 4)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 1, 1, 1, 1], 3),        # many equal small values, several subsets sum right
        ([100, 200, 300], 5000),     # target unreachable, larger than total
        ([0, 0, 0, 5], 5),           # zeros that don't affect reachability
        ([1000, 1, 1, 1, 1], 4),     # one huge value that must be excluded
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 3], 5),   # exact total sum
        ([2, 3], 6),   # one more than total sum: unreachable
        ([5, 5, 5], 10),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── coin-change-ways: oracle(coins, amount) ───────────────────────────────────

def _to_input_coin_change(coins, amount):
    return f"{len(coins)} {_arr(coins)} {amount}"


def _plan_coin_change_ways(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_coin_change

    def gen_small():
        n = rng.randint(1, 5)
        coins = sorted(set(tg.rand_int_array(rng, n, 1, 20))) or [1]
        amount = rng.randint(0, 50)
        return (coins, amount)

    def gen_stress():
        coins = sorted(set(tg.rand_int_array(rng, 10, 1, 100))) or [1]
        amount = 500
        return (coins, amount)

    visible = [
        ([1, 2, 5], 5), ([2], 3), ([1], 0), ([1, 5, 10, 25], 30), ([1, 2], 4),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1], 0), ([100], 500), ([1], 1), ([500], 499)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([2, 4, 6], 5),          # all even coins, odd target unreachable
        ([3, 5], 7),             # small coprime pair, tests exact combination counting
        ([1, 2, 3], 10),         # multiple overlapping ways to double count
        ([50, 25, 10, 5, 1], 100),  # denominations resembling real currency
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2], 3),     # order-dependent counting trap: combos not permutations
        ([2, 3], 5),
        ([1, 3, 4], 6),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── decode-ways: oracle(s) ─────────────────────────────────────────────────────

def _to_input_decode(s):
    return s


def _plan_decode_ways(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_decode

    def gen_small():
        n = rng.randint(1, 8)
        return ("".join(rng.choice("0123456789") for _ in range(n)),)

    def gen_stress():
        # alternating '1'/'2' followed by non-'0' digits maximizes the number
        # of valid decodings (Fibonacci-like branching) without recursion —
        # decode_ways is iterative O(n), so a longer string is fine here, but
        # kept well under the 100-char constraint's upper bound isn't required
        # since this oracle has no recursion risk; n=100 stays instant.
        n = 100
        digits = []
        for _ in range(n):
            digits.append(rng.choice("12"))
        return ("".join(digits),)

    visible = [("12",), ("226",), ("06",), ("100",), ("10",)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("0",), ("1",), ("9",), ("10",)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("100",),     # zero preceded by a valid two-digit group only
        ("27",),      # '27' > 26, only single-digit decoding valid
        ("110",),     # trailing zero forces exact grouping
        ("1010101010",),  # alternating traps for greedy off-by-one bugs
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("00",),   # double leading zero: always invalid
        ("30",),   # '30' invalid two-digit, '0' alone invalid -> 0 ways
        ("11",),   # two single digits AND one double digit -> 2 ways
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── knapsack-01: oracle(weights, values, capacity) ────────────────────────────

def _to_input_knapsack01(weights, values, capacity):
    return f"{len(weights)} {_arr(weights)} {_arr(values)} {capacity}"


def _plan_knapsack_01(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_knapsack01

    def gen_small():
        n = rng.randint(1, 6)
        w = tg.rand_int_array(rng, n, 0, 50)
        v = tg.rand_int_array(rng, n, 0, 50)
        cap = rng.randint(0, 100)
        return (w, v, cap)

    def gen_stress():
        n = 100
        w = tg.rand_int_array(rng, n, 1, 50)
        v = tg.rand_int_array(rng, n, 1, 100)
        cap = 1000
        return (w, v, cap)

    visible = [
        ([1, 3, 4, 5], [1, 4, 5, 7], 7), ([10], [60], 5), ([2, 2, 2], [3, 3, 3], 0),
        ([2, 3, 4, 5, 9], [3, 4, 5, 8, 10], 20), ([1, 2, 3], [10, 15, 40], 6),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([0], [0], 0), ([1000], [1000], 1000), ([1000], [1000], 999), ([1], [1000], 0)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([5, 5], [10, 10], 5),          # identical ratio items, only room for one
        ([1, 1, 1, 1, 1], [1, 2, 3, 4, 5], 3),  # greedy-by-value would fail
        ([4, 5, 1], [1, 1, 1000], 5),    # tiny high-value item is essential
        ([10, 20, 30], [60, 100, 120], 50),  # classic fractional-knapsack input reused as 0/1
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([3, 4], [4, 5], 7),   # capacity fits both, tests taking all vs skipping
        ([3, 4], [4, 5], 3),   # capacity fits only the smaller item
        ([2, 2, 2], [3, 5, 8], 4),  # equal weights, must pick highest values
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── unbounded-knapsack: oracle(weights, values, capacity) ─────────────────────

def _to_input_unbounded_knapsack(weights, values, capacity):
    return f"{len(weights)} {_arr(weights)} {_arr(values)} {capacity}"


def _plan_unbounded_knapsack(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_unbounded_knapsack

    def gen_small():
        n = rng.randint(1, 5)
        w = tg.rand_int_array(rng, n, 1, 30)
        v = tg.rand_int_array(rng, n, 0, 50)
        cap = rng.randint(0, 60)
        return (w, v, cap)

    def gen_stress():
        n = 50
        w = tg.rand_int_array(rng, n, 1, 200)
        v = tg.rand_int_array(rng, n, 0, 1000)
        cap = 2000
        return (w, v, cap)

    visible = [
        ([5, 10, 15], [10, 30, 20], 100), ([1, 3, 4, 5], [10, 40, 50, 70], 8),
        ([3, 5], [4, 6], 0), ([4, 6], [5, 8], 15), ([2], [3], 10),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([200], [1000], 0), ([200], [1000], 2000), ([1], [0], 5), ([200], [1000], 199)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1], [1], 50),          # best strategy is take-the-cheapest-item repeatedly
        ([3, 5], [4, 7], 12),    # ratio-tie trap between two item types
        ([7], [10], 20),         # capacity not a clean multiple of the only weight
        ([2, 3, 5], [3, 5, 8], 17),  # coin-change-like combination search
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2], [3], 5),    # unlimited supply: floor(5/2)=2 copies = value 6, remainder wasted
        ([3], [5], 9),    # capacity is an exact multiple
        ([2, 3], [3, 5], 6),  # tie between two ways to fill capacity 6
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── rod-cutting: oracle(prices, length) — length == len(prices) always ───────

def _to_input_rod_cutting(prices, length):
    return f"{length} {_arr(prices)}"


def _plan_rod_cutting(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_rod_cutting

    def gen_small():
        n = rng.randint(1, 8)
        prices = tg.rand_int_array(rng, n, 0, 30)
        return (prices, n)

    def gen_stress():
        n = 100
        prices = tg.rand_int_array(rng, n, 0, 1000)
        return (prices, n)

    visible = [
        ([1, 5, 8, 9, 10, 17, 17, 20], 8), ([1, 5, 8, 9], 4), ([5], 1),
        ([2, 5, 7, 8], 4), ([3, 5, 8, 9, 10], 5),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([0], 1), ([1000], 1), ([0] * 5, 5), ([1000] * 5, 5)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 2, 3, 4, 5], 5),        # linear prices: cutting into 1s ties whole-rod value
        ([2, 5, 7, 8, 10], 5),       # cutting into pieces beats keeping whole
        ([3, 5, 8, 9, 10, 17, 17, 20], 8),  # slightly perturbed classic case
        ([10, 1, 1, 1, 1], 5),       # keeping the rod whole (piece len 1) dominates
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2], 2),   # off-by-one on piece-length indexing (prices[i-1] for length i)
        ([5, 8], 2),
        ([2, 4, 6], 3),  # perfectly proportional prices, no benefit from cutting
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── maximum-product-subarray: oracle(nums) ────────────────────────────────────

def _to_input_max_product(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_max_product_subarray(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_product

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, -10, 10),)

    def gen_stress():
        # The registered independent REFERENCE solution for this slug is a
        # naive O(n^2) double loop (recomputing the running product for every
        # start index), not the O(n) running-min/max oracle in
        # independent_oracles.py — and with values including +-1 and 0,
        # products can still grow in bit-length across a long run. n=300
        # keeps the O(n^2) call count (~45K) and big-int arithmetic well
        # inside the 5s judge budget.
        n = rng.randint(250, 300)
        return (tg.rand_int_array(rng, n, -10, 10),)

    visible = [
        ([2, 3, -2, 4],), ([-2, 0, -1],), ([-2, 3, -4],), ([-2],), ([1, -2, 3, -4],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([0],), ([-1],), ([10],), ([-10],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([0, 2, -3, 4, 0, -5],),   # zeros reset both running max/min trackers
        ([-1, -1, -1, -1],),       # even count of negatives -> whole array is best
        ([-1, -1, -1],),           # odd count of negatives -> must exclude one end
        ([2, -5, -2, -4, 3],),     # min-tracking needed to catch negative*negative
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([-2, 3, -4],),   # classic min-tracker trap: sum-based Kadane would miss this
        ([0, -1],),
        ([2, 0, -3, -4],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── longest-bitonic-subsequence: oracle(nums) — O(n^2) iterative ─────────────

def _to_input_bitonic(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_longest_bitonic_subsequence(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_bitonic

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, -20, 20),)

    def gen_stress():
        # O(n^2) iterative reference — n=800 is 640K comparisons, comfortably
        # under the 5s budget in pure Python.
        n = 800
        return (tg.rand_int_array(rng, n, -10_000, 10_000),)

    visible = [
        ([1, 11, 2, 10, 4, 5, 2, 1],), ([12, 11, 40, 5, 3, 1],),
        ([80, 60, 30, 40, 20, 10],), ([1, 2, 3, 4, 5],), ([5, 4, 3, 2, 1],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([0],), ([1, 1],), ([1, 1, 1, 1],), ([-20, 20],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(10)),),               # pure increasing: bitonic = whole increasing run
        (list(range(10, 0, -1)),),        # pure decreasing: bitonic = whole decreasing run
        ([1, 2, 3, 2, 1, 2, 3],),          # repeated bitonic shape, must find best peak
        ([5, 5, 5, 5],),                   # all-equal: strict inequality means length 1
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 3, 2],),     # minimal true bitonic shape length 3
        ([3, 1, 2],),     # decreasing-then-increasing (NOT bitonic under this def)
        ([1, 2, 1, 2, 1],),  # multiple local peaks, only one is globally optimal
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── palindrome-subsequence: oracle(s) — reference is O(n^2) RECURSIVE memo ───

def _to_input_palindrome_subseq(s):
    return s


def _plan_palindrome_subsequence(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_palindrome_subseq

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_string(rng, n, "ab"),)

    def gen_stress():
        # Reference solution recurses on (i, j) with depth up to n — keep well
        # under Python's default 1000-frame recursion limit.
        n = 400
        return (tg.rand_string(rng, n, "ab"),)

    visible = [("bbbab",), ("cbbd",), ("a",), ("abcaba",), ("aaaa",)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("a",), ("aa",), ("ab",), ("z",)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("abababab",),     # alternating chars, palindromic subsequence via skipping
        ("aaaaaaaa",),     # all same char -> whole string is the answer
        ("abcdefgh",),     # all distinct -> answer is 1
        ("racecar",),      # already a palindrome itself
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aa",),    # both chars match: length 2, not defaulting to 1
        ("ba",),    # no match: length 1, not 0
        ("aba",),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── interleaving-strings: oracle(s1, s2, s3) — reference recurses depth n+m ──

def _to_input_interleave(s1, s2, s3):
    return f"{s1}\n{s2}\n{s3}"


def _plan_interleaving_strings(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_interleave

    def _interleave(rng, a, b):
        """Build a true interleaving of a and b (always a valid 'true' case)."""
        i = j = 0
        out = []
        while i < len(a) or j < len(b):
            if i < len(a) and (j >= len(b) or rng.random() < 0.5):
                out.append(a[i]); i += 1
            else:
                out.append(b[j]); j += 1
        return "".join(out)

    def gen_small_true():
        s1 = tg.rand_string(rng, rng.randint(0, 5), "ab")
        s2 = tg.rand_string(rng, rng.randint(0, 5), "cd")
        s3 = _interleave(rng, s1, s2)
        return (s1, s2, s3)

    def gen_small_false():
        s1 = tg.rand_string(rng, rng.randint(1, 5), "ab")
        s2 = tg.rand_string(rng, rng.randint(1, 5), "ab")
        s3 = tg.rand_string(rng, len(s1) + len(s2), "ab")
        return (s1, s2, s3)

    def gen_stress():
        # Recursion depth ~ len(s1)+len(s2); keep total well under 1000.
        s1 = tg.rand_string(rng, 150, "a")
        s2 = tg.rand_string(rng, 150, "b")
        s3 = _interleave(rng, s1, s2)
        return (s1, s2, s3)

    visible = [
        ("aabcc", "dbbca", "aadbbcbcac"), ("aabcc", "dbbca", "aadbbbaccc"),
        ("", "", ""), ("abc", "def", "adbcef"), ("a", "b", "ab"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small_true, ti, seen)
    boundary_anchors = [
        ("", "", ""), ("a", "", "a"), ("", "a", "a"), ("a", "b", "ba"),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small_true, ti, seen)
    adversarial_anchors = [
        ("aa", "ab", "aaab"),        # ambiguous shared-prefix greedily matches wrong branch
        ("ab", "ab", "aabb"),        # both strings identical, must still interleave correctly
        ("aab", "aab", "aaaabb"),    # length matches but multiset order is wrong -> false
        ("aabb", "abab", "aabbabab"),  # long shared alphabet needs true DP, not greedy
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_small_false, ti, seen)
    mutation_anchors = [
        ("a", "a", "aa"),     # single-char repeats, order-independent multiset trap
        ("ab", "ba", "abba"),
        ("ab", "ba", "baab"),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small_true, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── wildcard-matching: oracle(s, p) — reference recurses depth ~ len(s)+len(p) ─

def _to_input_wildcard(s, p):
    return f"{s}\n{p}"


def _plan_wildcard_matching(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_wildcard

    def gen_small():
        n = rng.randint(0, 6)
        s = tg.rand_string(rng, n, "ab")
        m = rng.randint(0, 6)
        p = "".join(rng.choice("ab?*") for _ in range(m))
        return (s, p)

    def gen_stress():
        # Recursion depth bounded by len(s)+len(p); keep both modest.
        s = tg.rand_string(rng, 150, "ab")
        p = "*" + "".join(rng.choice("ab?*") for _ in range(150))
        return (s, p)

    visible = [
        ("aa", "a"), ("aa", "*"), ("cb", "?a"), ("adceb", "*a*b"), ("acdcb", "a*c?b"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("", ""), ("", "*"), ("", "?"), ("a", ""),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaaab", "a*a*a*a*b"),   # many redundant stars, naive backtracking blows up
        ("mississippi", "m??*ss*?i*pi"),  # classic wildcard trap combining ? and *
        ("abcabczzzde", "*abc???de*"),    # star must match a variable-length middle
        ("", "*****"),                     # only stars, must match empty string
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("ab", "?*"),    # '?' must consume exactly one char, not treated like '*'
        ("a", "*?"),     # star matching empty, then '?' consuming the one char
        ("", "?"),       # '?' cannot match empty string -> false
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── distinct-subsequences: oracle(s, t) — reference recurses depth ~ len(s) ──

def _to_input_distinct_subseq(s, t):
    return f"{s}\n{t}"


def _plan_distinct_subsequences(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_distinct_subseq

    def gen_small():
        n = rng.randint(1, 8)
        s = tg.rand_string(rng, n, "ab")
        m = rng.randint(1, min(4, n))
        t = tg.rand_string(rng, m, "ab")
        return (s, t)

    def gen_stress():
        # Recursion depth ~ len(s); keep it comfortably under the 1000 limit.
        s = tg.rand_string(rng, 300, "ab")
        t = tg.rand_string(rng, 6, "ab")
        return (s, t)

    visible = [
        ("rabbbit", "rabbit"), ("babgbag", "bag"), ("abc", "abcd"),
        ("aaaa", "aa"), ("aaa", "a"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("a", "a"), ("a", "b"), ("aaaa", "aaaa"), ("ab", "aaa"),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaaaaaa", "aa"),     # heavily repeated char inflates the count combinatorially
        ("abababab", "aba"),    # repeating pattern with overlapping matches
        ("aaaaa", "aaaaaa"),    # t longer than s -> always 0
        ("bbbbb", "a"),         # target char never appears -> 0
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aa", "a"),    # 2 distinct positions to pick the single char from
        ("aab", "ab"),  # must skip duplicate 'a's correctly
        ("aa", "aa"),   # exact match, 1 way
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── matrix-chain-multiplication: oracle(dims) — reference recurses interval depth ~n ─

def _to_input_matrix_chain(dims):
    return f"{len(dims)} {_arr(dims)}"


def _plan_matrix_chain_multiplication(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_matrix_chain

    def gen_small():
        n = rng.randint(2, 8)  # 1..7 matrices
        return (tg.rand_int_array(rng, n, 1, 50),)

    def gen_stress():
        # Reference recurses on interval (i, j); worst-case call depth is
        # bounded by chain length (n-1 matrices), kept modest to stay well
        # under the 1000-frame recursion limit while still exercising O(n^3).
        n = 60  # 59 matrices
        return (tg.rand_int_array(rng, n, 1, 200),)

    visible = [
        ([40, 20, 30, 10, 30],), ([10, 20, 30],), ([10, 20],),
        ([5, 10, 3, 12, 5, 50],), ([1, 2, 3, 4],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1, 1],), ([200, 200],), ([1, 200],), ([200, 1],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([10, 100, 10, 100, 10],),   # alternating dims, naive left-to-right order is very costly
        ([1, 100, 1, 100, 1, 100],), # extreme oscillation punishes wrong parenthesization
        ([50, 1, 50, 1, 50],),       # thin-fat-thin-fat chain
        ([30, 35, 15, 5, 10, 20, 25],),  # classic CLRS textbook example
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([10, 20, 30, 40],),   # 3 matrices, only 2 parenthesizations to compare
        ([40, 30, 20, 10],),   # reversed dims of the above
        ([5, 4, 6, 2, 7],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── egg-drop: oracle(eggs, floors) ────────────────────────────────────────────

def _to_input_egg_drop(eggs, floors):
    return f"{eggs} {floors}"


def _plan_egg_drop(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_egg_drop

    def gen_small():
        return (rng.randint(1, 5), rng.randint(0, 50))

    def gen_stress():
        # The registered reference solution is the classic O(eggs*floors^2)
        # DP (inner loop tries every split point), NOT the O(eggs*answer)
        # formulation independent_oracles.py uses — so floors must stay small
        # enough for eggs*floors^2 python-level ops to finish in 5s. With
        # eggs<=10 and floors=140, worst case is 10*140^2 ~= 196K inner-loop
        # iterations, comfortably fast; floors=1000 (10*1e6=10M) would still
        # likely pass but is cut down for margin given interpreter overhead.
        return (rng.randint(2, 10), rng.randint(100, 140))

    visible = [(2, 10), (1, 5), (2, 36), (3, 14), (1, 0)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(1, 0), (10, 0), (1, 1000), (10, 1)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (1, 100),   # single egg forces linear worst case, easy to under-count
        (2, 100),   # classic quadratic-vs-optimal trap for 2 eggs
        (5, 32),    # floors == 2^eggs boundary for binary-search intuition
        (3, 50),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (1, 10),    # eggs=1: answer must equal floors exactly (no binary search possible)
        (2, 1),     # single floor: always 1 trial regardless of eggs
        (10, 1),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── boolean-parenthesization: oracle(symbols, ops) — reference recurses depth ~n ─

def _to_input_boolean_paren(symbols, ops):
    return f"{symbols}\n{ops}"


def _plan_boolean_parenthesization(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_boolean_paren

    def gen_random(n):
        symbols = "".join(rng.choice("TF") for _ in range(n))
        ops = "".join(rng.choice("&|^") for _ in range(n - 1))
        return (symbols, ops)

    def gen_small():
        return gen_random(rng.randint(1, 6))

    def gen_stress():
        # Constraint caps symbols.length <= 15; O(n^3) with cubic recursion
        # over ~120 subintervals is instant, but recursion depth (interval
        # length) is bounded by n itself, well under any limit.
        return gen_random(15)

    visible = [
        ("TFT", "^&"), ("TTFT", "|&^"), ("TFTFTF", "^^^^^"), ("TTTT", "&&&"), ("T", ""),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("T", ""), ("F", ""), ("TF", "&"), ("TF", "|")]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("TFTFTFTFTFTFTFT", "^^^^^^^^^^^^^^"),  # all XOR, max symbols, alternating T/F
        ("TTTTTTTTTTTTTTT", "&&&&&&&&&&&&&&"),  # all AND, all-true operands
        ("FFFFFFFFFFFFFFF", "||||||||||||||"),  # all OR, all-false operands
        ("TFTFTFTFTFTFTFT", "&|^&|^&|^&|^&|"),   # mixed operators, max length
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("TF", "^"),   # XOR of exactly one T and one F -> both orderings True
        ("TT", "^"),   # XOR of two equal -> always False
        ("TF", "&"),   # AND requires both True -> always False
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── word-wrap: oracle(word_lengths, line_width) — reference recurses depth ~n ─

def _to_input_word_wrap(lengths, width):
    return f"{len(lengths)} {_arr(lengths)} {width}"


def _plan_word_wrap(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_word_wrap

    def gen_small():
        width = rng.randint(5, 15)
        n = rng.randint(1, 8)
        lengths = [rng.randint(1, width) for _ in range(n)]
        return (lengths, width)

    def gen_stress():
        # Constraint caps n <= 50; recursion depth ~ n, instant either way.
        width = 50
        n = 50
        lengths = [rng.randint(1, width) for _ in range(n)]
        return (lengths, width)

    visible = [
        ([3, 2, 2, 5], 6), ([1, 1, 1, 1], 5), ([3], 3), ([2, 3, 2, 5, 2], 8),
        ([4, 4, 4], 9),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1], 1), ([50], 50), ([1] * 5, 5), ([50], 50)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([5, 5, 5, 5, 5], 5),        # every word exactly fills a line, badness always 0
        ([1, 1, 1, 1, 1, 1, 1], 3),  # many tiny words, several valid line-break counts
        ([10, 1, 1, 1, 1, 1, 10], 12),  # long words bookending short ones
        ([2, 2, 2, 2, 2, 2, 2, 2], 7),  # near-tie between 2-per-line and 3-per-line packing
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([3, 3], 3),    # each word needs its own line (last line free, first line badness)
        ([3, 3], 7),    # both words fit on one line exactly
        ([2, 2, 2], 5),  # greedy-fill (fit as many as possible) is suboptimal here
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

DYNAMIC_PROGRAMMING_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "staircase": (_to_input_staircase, str, _plan_staircase),
    "jump-game": (_to_input_jump, _fmt_bool, _plan_jump_game),
    "subset-sum": (_to_input_subset_sum, _fmt_bool, _plan_subset_sum),
    "coin-change-ways": (_to_input_coin_change, str, _plan_coin_change_ways),
    "decode-ways": (_to_input_decode, str, _plan_decode_ways),
    "knapsack-01": (_to_input_knapsack01, str, _plan_knapsack_01),
    "unbounded-knapsack": (_to_input_unbounded_knapsack, str, _plan_unbounded_knapsack),
    "rod-cutting": (_to_input_rod_cutting, str, _plan_rod_cutting),
    "maximum-product-subarray": (_to_input_max_product, str, _plan_max_product_subarray),
    "longest-bitonic-subsequence": (_to_input_bitonic, str, _plan_longest_bitonic_subsequence),
    "palindrome-subsequence": (_to_input_palindrome_subseq, str, _plan_palindrome_subsequence),
    "interleaving-strings": (_to_input_interleave, _fmt_bool, _plan_interleaving_strings),
    "wildcard-matching": (_to_input_wildcard, _fmt_bool, _plan_wildcard_matching),
    "distinct-subsequences": (_to_input_distinct_subseq, str, _plan_distinct_subsequences),
    "matrix-chain-multiplication": (_to_input_matrix_chain, str, _plan_matrix_chain_multiplication),
    "egg-drop": (_to_input_egg_drop, str, _plan_egg_drop),
    "boolean-parenthesization": (_to_input_boolean_paren, str, _plan_boolean_parenthesization),
    "word-wrap": (_to_input_word_wrap, str, _plan_word_wrap),
}
