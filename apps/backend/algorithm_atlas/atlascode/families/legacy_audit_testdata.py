"""
40-test case plans for the 19 LEGACY curated AtlasCode problems (see
testgen.py for the shared bucket contract: visible 5 / basic 7 / boundary 8 /
adversarial 8 / mutation 7 / stress 5 = 40).

These 19 problems already have LIVE `problem_statement` / `starter_code` rows
in the database (hand-curated, not factory-generated originally) — this
module does NOT touch that data. Each `to_input` here reproduces the EXACT
stdin shape the existing starter code already parses (verified against the
live starter code + sample I/O in the task brief before writing this file;
see legacy_audit_oracles.py's module docstring for the same note).

Also exports:
  LEGACY_PLANS: dict[str, tuple(to_input, format_output, oracle, plan_fn)]
  REFERENCE_SOLUTIONS: dict[str, str]   -- independently written correct programs
  WRONG_SOLUTIONS: dict[str, str]       -- plausible-bug wrong programs
"""
from __future__ import annotations

import random

from . import legacy_audit_oracles as oracles
from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


def _fmt_list(vals) -> str:
    return " ".join(str(x) for x in vals)


def _fmt_bool_true_false(b: bool) -> str:
    return "true" if b else "false"


def _fmt_pair(pair) -> str:
    i, j = pair
    return f"{min(i, j)} {max(i, j)}"


def _fmt_kmp(result: list[int]) -> str:
    return " ".join(map(str, result)) if result else "-1"


# ══════════════════════════════════════════════════════════════════════════
# binary-search: oracle(nums, target) — nums SORTED
# ══════════════════════════════════════════════════════════════════════════

def _to_input_binary_search(nums, target):
    return f"{len(nums)} {_arr(nums)} {target}"


def _plan_binary_search(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_binary_search

    def gen_small():
        n = rng.randint(3, 8)
        nums = tg.rand_sorted_array(rng, n, -50, 50, strict=True)
        target = rng.choice(nums) if rng.random() < 0.5 else rng.randint(-60, 60)
        return (nums, target)

    def gen_stress():
        n = rng.randint(5000, 20000)
        nums = sorted(tg.rand_distinct_int_array(rng, n, -1_000_000, 1_000_000)) if n <= 2_000_001 else sorted(tg.rand_int_array(rng, n, -1_000_000, 1_000_000))
        target = rng.choice(nums) if rng.random() < 0.5 else rng.randint(-1_100_000, 1_100_000)
        return (nums, target)

    visible = [
        ([-1, 0, 3, 5, 9, 12], 9),
        ([-1, 0, 3, 5, 9, 12], 2),
        ([1], 1),
        ([1], 5),
        ([1, 3, 5, 7, 9, 11, 13], 7),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1], -1),
        ([-5, -3, -1], -5),
        ([-5, -3, -1], -1),
        ([1, 2], 1),
        ([1, 2], 2),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([2, 2, 2, 2, 2], 2),        # all-equal, must return SOME valid index
        ([1, 3, 5, 7, 9], 4),        # target between elements -> -1
        ([-100, -50, 0, 50, 100], -50),
        ([1, 2, 3, 4, 5, 6, 7, 8], 8),  # last element (upper-bound off-by-one trap)
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2, 3, 4, 5], 1),   # first element (lo boundary)
        ([1, 2, 3, 4, 5], 5),   # last element (hi boundary)
        ([1, 2, 3, 4, 5], 3),   # exact middle
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# linear-search: oracle(nums, target) — nums NOT sorted, first index or -1
# ══════════════════════════════════════════════════════════════════════════

def _to_input_linear_search(nums, target):
    return f"{len(nums)} {_arr(nums)} {target}"


def _plan_linear_search(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_linear_search

    def gen_small():
        n = rng.randint(3, 8)
        nums = tg.rand_int_array(rng, n, -50, 50)
        target = rng.choice(nums) if rng.random() < 0.5 else rng.randint(-60, 60)
        return (nums, target)

    def gen_stress():
        n = rng.randint(5000, 20000)
        nums = tg.rand_int_array(rng, n, -1000, 1000)
        target = rng.choice(nums) if rng.random() < 0.5 else 99999
        return (nums, target)

    visible = [
        ([4, 2, 7, 1, 9], 7),
        ([1, 2, 3], 5),
        ([5], 5),
        ([9, 8, 7, 6], 9),
        ([3, 1, 4, 1, 5], 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1], -1),
        ([-5, -3, -1], -5),
        ([0], 0),
        ([1, 2], 2),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([2, 2, 2, 2, 2], 2),        # all-equal, must return FIRST (index 0)
        ([5, 4, 3, 2, 1], 1),        # target at the very end
        ([1, 1, 2, 1, 1], 2),        # target unique in a sea of duplicates
        ([7, 7, 7, 3, 7, 7], 3),     # target sandwiched between duplicates
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([9, 1, 2, 3], 9),      # first element
        ([1, 2, 3, 9], 9),      # last element
        ([1, 2, 9, 2, 9], 9),   # duplicate target -> first occurrence
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# bubble-sort: oracle(nums) -> fully sorted array
# ══════════════════════════════════════════════════════════════════════════

def _to_input_bubble_sort(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_bubble_sort(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_bubble_sort

    def gen_small():
        n = rng.randint(2, 8)
        return (tg.rand_int_array(rng, n, -50, 50),)

    def gen_stress():
        n = rng.randint(800, 2000)
        return (tg.rand_int_array(rng, n, -10_000, 10_000),)

    visible = [
        ([5, 3, 8, 1, 2],), ([42],), ([1, 2, 3, 4],), ([4, 3, 2, 1],), ([2, 2, 1, 1],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1],), ([0],), ([-1, -2],), ([5, 5],), ([0, 0, 0],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(20, 0, -1)),),           # fully reverse-sorted (worst case swaps)
        ([3] * 10,),                          # all-equal
        (list(range(1, 21)),),                # already sorted
        ([1, -1, 1, -1, 1, -1, 1, -1],),      # alternating extremes
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 1],),          # minimal single swap
        ([1, 2],),          # minimal already-sorted pair
        ([3, 1, 2],),       # needs multiple passes
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# fibonacci-dp: oracle(n)
# ══════════════════════════════════════════════════════════════════════════

def _to_input_fib(n):
    return str(n)


def _plan_fibonacci(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_fib

    def gen_small():
        return (rng.randint(2, 30),)

    def gen_stress():
        return (rng.randint(500, 5000),)

    visible = [(0,), (1,), (2,), (5,), (10,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(0,), (1,), (3,), (4,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [(20,), (30,), (35,), (40,)]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [(6,), (7,), (8,)]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# gcd-euclidean: oracle(a, b)
# ══════════════════════════════════════════════════════════════════════════

def _to_input_gcd(a, b):
    return f"{a} {b}"


def _plan_gcd(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_gcd

    def gen_small():
        return (rng.randint(1, 1000), rng.randint(1, 1000))

    def gen_stress():
        return (rng.randint(10**9, 2 * 10**9), rng.randint(10**9, 2 * 10**9))

    visible = [(48, 18), (0, 5), (17, 13), (100, 75), (7, 7)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(0, 0), (0, 1), (1, 0), (1, 1), (5, 0)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (1_000_000_007, 999_999_937),  # two large primes (coprime, gcd=1)
        (123_456_789, 987_654_321),
        (2, 1_000_000_000),             # power-of-two edge
        (999_999_999, 999_999_998),     # consecutive large numbers
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [(12, 8), (8, 12), (9, 6)]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# two-sum: oracle(nums, target) -> (i, j) canonical hashmap-scan pair
# ══════════════════════════════════════════════════════════════════════════

def _to_input_two_sum(nums, target):
    return f"{len(nums)} {_arr(nums)} {target}"


def _make_two_sum_case(rng: random.Random, n: int, lo: int, hi: int):
    """Build an array guaranteed to contain exactly the pair semantics the
    oracle expects: pick two distinct positions i<j, set nums[i]+nums[j]=target,
    fill the rest randomly but re-verify via the oracle so plan generation
    never emits an input with no valid pair."""
    nums = tg.rand_int_array(rng, n, lo, hi)
    i, j = rng.sample(range(n), 2)
    target = nums[i] + nums[j]
    # Ensure oracle's greedy first-match doesn't accidentally point elsewhere
    # in a way that breaks nothing (any valid pair is fine — oracle always
    # returns *a* valid pair, so no need to force it to be exactly i,j).
    try:
        oracles.two_sum_indices(nums, target)
    except oracles.OracleError:
        # fall back: extremely unlikely, but retry with a clean pair only
        nums = [0] * n
        nums[i], nums[j] = 1, target - 1
    return (nums, target)


def _plan_two_sum(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_two_sum

    def gen_small():
        n = rng.randint(2, 8)
        return _make_two_sum_case(rng, n, -50, 50)

    def gen_stress():
        n = rng.randint(2000, 8000)
        return _make_two_sum_case(rng, n, -100_000, 100_000)

    visible = [
        ([2, 7, 11, 15], 9),
        ([3, 2, 4], 6),
        ([1, 1], 2),
        ([0, 4, 3, 0], 0),
        ([-3, 4, 3, 90], 0),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1, 2], 3),
        ([0, 0], 0),
        ([-1, -2, -3, -6], -9),
        ([5, 5, 5], 10),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([3, 3, 3, 3, 3], 6),           # many identical values, many valid pairs
        ([1, 2, 3, 4, 5, 6, 7, -3], 4),  # complement appears AFTER the match in scan order
        ([100000, -99999, 1, 2], 1),
        ([0, -1, 2, -3, 1], -2),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 5, 5, 1], 6),     # duplicate complements — tests "first index wins"
        ([2, 2, 3], 4),
        ([-1, 0, 1], -1 + 0),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# maximum-subarray: oracle(nums) -- Kadane's
# ══════════════════════════════════════════════════════════════════════════

def _to_input_max_subarray(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_max_subarray(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_subarray

    def gen_small():
        n = rng.randint(2, 10)
        return (tg.rand_int_array(rng, n, -30, 30),)

    def gen_stress():
        n = rng.randint(2000, 10000)
        return (tg.rand_int_array(rng, n, -1000, 1000),)

    visible = [
        ([-2, 1, -3, 4, -1, 2, 1, -5, 4],), ([1],), ([5, 4, -1, 7, 8],),
        ([-1],), ([-2, -1],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([0],), ([-100],), ([100],), ([-1, -1, -1],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([-5, -4, -3, -2, -1],),        # all negative — answer is the least-negative single element
        ([1, -1, 1, -1, 1, -1, 1],),    # alternating tiny profits
        ([10, -1, -1, -1, -1, 10],),    # crossing a negative valley is worth it
        ([-1, 10, -1, 10, -1],),        # multiple peaks separated by dips
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([-3, -2],),   # both negative, pick the max single (not sum)
        ([2, -1, 2],), # crossing single negative is still worth it
        ([1, 2, 3],),  # all positive — whole array wins
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# coin-change: oracle(coins, amount) -> min coins or -1
# ══════════════════════════════════════════════════════════════════════════

def _to_input_coin_change(coins, amount):
    return f"{len(coins)} {_arr(coins)} {amount}"


def _plan_coin_change(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_coin_change

    def gen_small():
        k = rng.randint(1, 5)
        coins = sorted(set(tg.rand_int_array(rng, k, 1, 20)))
        amount = rng.randint(0, 50)
        return (coins, amount)

    def gen_stress():
        k = rng.randint(10, 20)
        coins = sorted(set(tg.rand_int_array(rng, k, 1, 200)))
        amount = rng.randint(1000, 5000)
        return (coins, amount)

    visible = [
        ([1, 5, 6, 9], 11), ([2], 3), ([1], 0), ([1, 2, 5], 11), ([5], 5),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1], 1), ([1], 0), ([100], 99), ([1, 2], 0), ([7], 14),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([3, 7], 5),                 # impossible amount despite plentiful coins
        ([1, 3, 4], 6),              # greedy (largest-first) would give 3 coins (4+1+1); optimal is 2 (3+3)
        ([186, 419, 83, 408], 6249), # classic adversarial DP coin set
        ([2, 5, 10, 1], 27),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1], 2),      # exactly 2 coins of the only denomination
        ([2], 3),      # odd amount with only even coin -> impossible
        ([1, 2, 5], 0),  # amount zero -> 0 coins, not -1
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# longest-common-subsequence: oracle(s1, s2) -> length
# ══════════════════════════════════════════════════════════════════════════

def _to_input_lcs(s1, s2):
    return f"{s1} {s2}"


def _plan_lcs(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_lcs

    def gen_small():
        n1, n2 = rng.randint(1, 8), rng.randint(1, 8)
        return (tg.rand_string(rng, n1, "abc"), tg.rand_string(rng, n2, "abc"))

    def gen_stress():
        n1, n2 = rng.randint(400, 800), rng.randint(400, 800)
        return (tg.rand_string(rng, n1, "ab"), tg.rand_string(rng, n2, "ab"))

    visible = [
        ("abcde", "ace"), ("abc", "abc"), ("abc", "def"), ("a", "a"), ("abcdef", "fedcba"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("a", "b"), ("a", "a"), ("ab", "a"), ("a", "ab"),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaaaaaa", "aaaa"),          # all-same-char, subsequence trivially fits
        ("abababab", "babababa"),      # interleaved alternation
        ("xyzxyzxyz", "zyxzyxzyx"),    # reversed pattern blocks
        ("aaabaaab", "abaaaba"),       # multiple near-miss alignments
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("ab", "ba"),     # off-by-one in comparator: LCS is 1 not 2
        ("aa", "aa"),     # duplicate chars, LCS = 2
        ("abc", "acb"),   # order matters
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# house-robber: oracle(nums) -> max sum, no two adjacent
# ══════════════════════════════════════════════════════════════════════════

def _to_input_house_robber(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_house_robber(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_house_robber

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, 0, 50),)

    def gen_stress():
        n = rng.randint(2000, 10000)
        return (tg.rand_int_array(rng, n, 0, 1000),)

    visible = [
        ([1, 2, 3, 1],), ([2, 7, 9, 3, 1],), ([5],), ([2, 1],), ([1, 2],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([0],), ([1],), ([0, 0],), ([100, 1],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([5, 5, 5, 5, 5, 5],),           # all equal — every-other pattern
        ([10, 1, 1, 1, 1, 1, 10],),      # two big houses at the ends
        ([1, 100, 1, 1, 100, 1],),       # two dominant non-adjacent houses
        (list(range(1, 21)),),           # increasing sequence
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 1, 1, 2],),   # picking ends beats picking middle
        ([1, 3, 1],),      # classic middle-vs-ends off by one
        ([4, 1, 1, 4, 1],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# longest-increasing-subsequence: oracle(nums) -> length, STRICT
# ══════════════════════════════════════════════════════════════════════════

def _to_input_lis(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_lis(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_lis

    def gen_small():
        n = rng.randint(1, 10)
        return (tg.rand_int_array(rng, n, 0, 20),)

    def gen_stress():
        n = rng.randint(2000, 5000)
        return (tg.rand_int_array(rng, n, 0, 1_000_000),)

    visible = [
        ([10, 9, 2, 5, 3, 7, 101, 18],), ([0, 1, 0, 3, 2, 3],), ([7],),
        ([1, 1, 1, 1],), ([1, 2, 3, 4, 5],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([0],), ([5, 5],), ([1, 2],), ([2, 1],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(20, 0, -1)),),        # strictly decreasing -> LIS length 1
        ([5] * 15,),                       # all-equal -> LIS length 1 (STRICT!)
        ([1, 3, 2, 4, 3, 5, 4, 6],),       # zig-zag with an increasing envelope
        (list(range(1, 11)) + list(range(1, 11)),),  # duplicated increasing run
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 1, 2],),   # duplicate then increase — tests strict vs non-strict
        ([2, 2],),      # equal pair -> length 1, not 2
        ([1, 2, 2, 3],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# bfs (graph-bfs): oracle(adj, src, n) -> hop distances; undirected unweighted
# to_input args: (n, edges, src) where edges: list[(u,v)]
# ══════════════════════════════════════════════════════════════════════════

def _build_undirected_adj(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def _to_input_bfs(n, edges, src):
    lines = [f"{n} {len(edges)} {src}"]
    lines += [f"{u} {v}" for u, v in edges]
    return "\n".join(lines)


def _oracle_bfs(n, edges, src):
    adj = _build_undirected_adj(n, edges)
    return oracles.bfs_distances(adj, src, n)


def _plan_bfs(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_bfs

    def gen_small():
        n = rng.randint(2, 8)
        max_m = n * (n - 1) // 2
        m = rng.randint(0, max_m)
        edges = tg.rand_graph_edges(rng, n, m, directed=False)
        src = rng.randint(0, n - 1)
        return (n, edges, src)

    def gen_stress():
        n = rng.randint(500, 1500)
        max_m = min(n * (n - 1) // 2, 4000)
        m = rng.randint(n - 1, max_m) if max_m >= n - 1 else 0
        edges = tg.rand_graph_edges(rng, n, m, directed=False)
        src = rng.randint(0, n - 1)
        return (n, edges, src)

    visible = [
        (4, [(0, 1), (0, 2), (1, 3), (2, 3)], 0),
        (3, [(0, 1)], 0),
        (1, [], 0),
        (5, [(0, 1), (1, 2), (2, 3), (3, 4)], 0),
        (4, [(0, 1), (2, 3)], 0),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        (1, [], 0),
        (2, [], 0),
        (2, [(0, 1)], 0),
        (2, [(0, 1)], 1),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)], 0),       # long chain from one end
        (6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)], 3),       # long chain from the middle
        (6, [(0, 1), (2, 3), (4, 5)], 0),                        # disconnected components
        (5, [(0, 1), (0, 2), (0, 3), (0, 4)], 0),                # star graph from center
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (3, [(0, 1), (1, 2), (0, 2)], 0),   # cycle/triangle — off-by-one in distance
        (4, [(0, 1), (1, 2), (1, 3)], 1),   # src not node 0
        (3, [], 1),                          # isolated src with no edges at all
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# word-break: oracle(s, word_dict) -> bool
# ══════════════════════════════════════════════════════════════════════════

def _to_input_word_break(s, words):
    return f"{s}\n{' '.join(words)}"


def _oracle_word_break(s, words):
    return oracles.word_break_feasible(s, set(words))


def _plan_word_break(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_word_break

    def gen_small():
        alphabet = "abc"
        dict_size = rng.randint(2, 5)
        words = sorted({tg.rand_string(rng, rng.randint(1, 3), alphabet) for _ in range(dict_size)})
        if not words:
            words = ["a"]
        # build s by concatenating random dict words some of the time
        pieces = [rng.choice(words) for _ in range(rng.randint(1, 4))]
        s = "".join(pieces)
        if rng.random() < 0.3:
            s += tg.rand_string(rng, rng.randint(1, 2), alphabet)  # maybe break feasibility
        return (s, words)

    def gen_stress():
        alphabet = "ab"
        words = sorted({tg.rand_string(rng, rng.randint(1, 4), alphabet) for _ in range(20)})
        pieces = [rng.choice(words) for _ in range(rng.randint(50, 150))]
        s = "".join(pieces)[:300]
        return (s, words)

    visible = [
        ("leetcode", ["leet", "code"]),
        ("catsandog", ["cats", "dog", "sand", "and", "cat"]),
        ("a", ["a"]),
        ("applepenapple", ["apple", "pen"]),
        ("abcd", ["a", "abc", "b", "cd"]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("a", ["b"]),
        ("a", ["a"]),
        ("ab", ["a", "b"]),
        ("ab", ["ab"]),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab", ["a", "aa"]),  # classic exponential-backtrack trap
        ("catsandog", ["cats", "dog", "sand", "and", "cat"]),
        ("abcabcabc", ["abc", "ab", "c", "bc"]),                       # many overlapping segmentations
        ("pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"]),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aa", ["a"]),          # simple repeat, tests dp[i] propagation
        ("aaa", ["a", "aa"]),   # multiple valid segmentations of same feasibility
        ("ab", ["a"]),          # tail cannot be covered -> infeasible
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# edit-distance: oracle(w1, w2) -> Levenshtein distance
# ══════════════════════════════════════════════════════════════════════════

def _to_input_edit_distance(w1, w2):
    # Newline-separated, NOT space-joined: word1/word2 may legitimately be
    # empty (constraint allows length 0), and a whitespace-split parse
    # silently drops empty tokens, losing the empty word entirely (e.g.
    # ("", "a") -> " a" -> split() -> ["a"], only one token). Confirmed via
    # verify_atlascode_family.py: the visible ("", "a") case crashed the
    # reference solution with an IndexError before this fix.
    return f"{w1}\n{w2}"


def _plan_edit_distance(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_edit_distance

    def gen_small():
        n1, n2 = rng.randint(1, 8), rng.randint(1, 8)
        return (tg.rand_string(rng, n1, "abc"), tg.rand_string(rng, n2, "abc"))

    def gen_stress():
        n1, n2 = rng.randint(400, 700), rng.randint(400, 700)
        return (tg.rand_string(rng, n1, "ab"), tg.rand_string(rng, n2, "ab"))

    visible = [
        ("horse", "ros"), ("intention", "execution"), ("a", "a"), ("abc", "abc"), ("", "a"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("a", "b"), ("a", "a"), ("ab", "a"), ("a", "ab"),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaaaaaa", "bbbbbbbb"),      # completely disjoint alphabets -> all-replace
        ("abcdefgh", "hgfedcba"),      # reversed string
        ("aaaabaaaa", "aaaacaaaa"),    # single middle-char difference
        ("abababab", "babababa"),      # shift-by-one alternation
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("ab", "ba"),      # swap: insert+delete vs 2 replaces (still 2, but tests recurrence)
        ("abc", "ac"),     # single deletion
        ("ac", "abc"),     # single insertion
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# unique-paths: oracle(m, n) -> count
# ══════════════════════════════════════════════════════════════════════════

def _to_input_unique_paths(m, n):
    return f"{m} {n}"


def _plan_unique_paths(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_unique_paths

    def gen_small():
        return (rng.randint(1, 10), rng.randint(1, 10))

    def gen_stress():
        return (rng.randint(50, 100), rng.randint(50, 100))

    visible = [(3, 7), (3, 2), (1, 1), (1, 5), (5, 1)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(1, 1), (1, 2), (2, 1), (2, 2)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (1, 100),    # single row — only 1 path but large n (loop-bound trap)
        (100, 1),    # single column
        (20, 20),    # square grid, large binomial
        (10, 50),    # rectangular skew
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (2, 3), (3, 3), (4, 2),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# n-queens: oracle(n) -> count of solutions
# ══════════════════════════════════════════════════════════════════════════

def _to_input_nqueens(n):
    return str(n)


# n-queens is a documented, deliberate EXCEPTION to the 40-unique-test
# standard: its entire input is a single integer n, and the problem's own
# stated contract (1 <= n <= 12, widened from the original 1 <= n <= 9 by
# explicit product decision) has only 12 possible distinct values — no
# generator can manufacture 40 unique test cases from a 12-value domain.
# (Confirmed via tg.fill_unique raising "only found 3/7 unique cases in 2000
# attempts" — a real domain-size limit, not a weak generator.) The cap is
# n<=12, NOT n<=14: measured runtime (not estimated) of this oracle's plain
# set-based backtracking is ~1.1s at n=12 but ~6.2s at n=13 and >30s at n=14
# — an earlier version of this comment claimed n<=14 was "fast," which was
# wrong and was corrected after actually timing it. This ships all 12
# achievable unique cases instead of 40 — see migrate_legacy_audit_to_forty.py
# and docs/atlascode-final-checkpoint.md. Every value from 1..12 is used
# exactly once (previous version's boundary bucket tested n=0, violating the
# problem's own n>=1 constraint).
N_QUEENS_REDUCED_CASES: list[tuple[int, bool]] = [
    (1, False), (2, False), (4, False), (5, False), (6, False),  # visible
    (3, True), (7, True), (8, True), (9, True), (10, True),
    (11, True), (12, True),                                        # hidden
]


# ══════════════════════════════════════════════════════════════════════════
# dijkstra: directed weighted graph, source=0, non-negative weights
# to_input args: (n, edges) where edges: list[(u,v,w)]
# ══════════════════════════════════════════════════════════════════════════

def _build_directed_weighted_adj(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    return adj


def _to_input_dijkstra(n, edges):
    lines = [f"{n} {len(edges)}"]
    lines += [f"{u} {v} {w}" for u, v, w in edges]
    return "\n".join(lines)


def _oracle_dijkstra(n, edges):
    adj = _build_directed_weighted_adj(n, edges)
    return oracles.dijkstra_distances(adj, n)


def _rand_directed_edges(rng, n, m, max_w):
    possible = [(u, v) for u in range(n) for v in range(n) if u != v]
    m = min(m, len(possible))
    chosen = rng.sample(possible, m)
    return [(u, v, rng.randint(0, max_w)) for u, v in chosen]


def _plan_dijkstra(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_dijkstra

    def gen_small():
        n = rng.randint(2, 7)
        max_m = n * (n - 1)
        m = rng.randint(0, min(max_m, 12))
        edges = _rand_directed_edges(rng, n, m, 20)
        return (n, edges)

    def gen_stress():
        n = rng.randint(300, 800)
        m = rng.randint(n, min(n * 3, 3000))
        edges = _rand_directed_edges(rng, n, m, 1000)
        return (n, edges)

    visible = [
        (5, [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5), (3, 4, 3)]),
        (3, [(0, 1, 5)]),
        (1, []),
        (4, [(0, 1, 1), (1, 2, 1), (2, 3, 1)]),
        (3, [(0, 1, 2), (0, 2, 2), (1, 2, 1)]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        (1, []),
        (2, []),
        (2, [(0, 1, 0)]),          # zero-weight edge
        (2, [(1, 0, 5)]),          # edge points away from source -> node 1 unreachable
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (4, [(0, 1, 10), (0, 2, 1), (2, 1, 1), (1, 3, 1), (2, 3, 100)]),  # cheaper indirect path
        (5, [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1)]),                  # star, all equal weights
        (4, [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 100)]),                # direct edge is worse than the path
        (3, [(0, 1, 5), (0, 2, 5), (1, 2, 0)]),                              # zero-weight edge shortcut
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (3, [(0, 1, 1), (1, 2, 1), (0, 2, 3)]),   # relax via intermediate node
        (3, [(0, 1, 2), (0, 2, 2), (1, 2, 2)]),   # tie in distances, must not double count
        (2, [(0, 1, 1), (0, 1, 2)]),               # parallel edges, must take the min
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# kmp: oracle(T, P) -> occurrence indices, [-1] formatted as "-1" if none
# ══════════════════════════════════════════════════════════════════════════

def _to_input_kmp(T, P):
    return f"{T}\n{P}"


def _plan_kmp(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_kmp

    def gen_small():
        alphabet = "ab"
        text_len = rng.randint(3, 20)
        pat_len = rng.randint(1, min(4, text_len))
        T = tg.rand_string(rng, text_len, alphabet)
        # sometimes embed the pattern to guarantee a match, sometimes not
        if rng.random() < 0.5:
            P = tg.rand_string(rng, pat_len, alphabet)
        else:
            start = rng.randint(0, text_len - pat_len)
            P = T[start:start + pat_len]
        return (T, P)

    def gen_stress():
        alphabet = "ab"
        text_len = rng.randint(5000, 20000)
        pat_len = rng.randint(1, 50)
        T = tg.rand_string(rng, text_len, alphabet)
        P = tg.rand_string(rng, pat_len, alphabet)
        return (T, P)

    visible = [
        ("aabaacaadaabaaba", "aaba"),
        ("abcde", "fgh"),
        ("aaaa", "aa"),
        ("hello", "hello"),
        ("mississippi", "issi"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("a", "a"),
        ("a", "b"),
        ("ab", "a"),
        ("ab", "b"),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaaaaaaaaaaaaaaaaaa", "aaaaa"),    # overlapping matches, classic KMP failure-function stress
        ("abababababababab", "ababab"),        # periodic pattern with overlaps
        ("aabaabaabaabaabaab", "aabaab"),      # longer periodic pattern
        ("xxxxxxxxxxxxxxxxxxxx", "y"),          # pattern never occurs
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aaa", "aa"),         # overlapping matches at consecutive positions
        ("abcabc", "abc"),     # non-overlapping repeated matches
        ("aaaa", "aaaa"),      # pattern equals text exactly
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# minimum-path-sum: oracle(grid) -> min path sum, right/down only
# to_input args: (grid,) where grid: list[list[int]]
# ══════════════════════════════════════════════════════════════════════════

def _to_input_min_path_sum(grid):
    m = len(grid)
    n = len(grid[0]) if m else 0
    lines = [f"{m} {n}"]
    lines += [_arr(row) for row in grid]
    return "\n".join(lines)


def _plan_min_path_sum(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_min_path_sum

    def gen_small():
        m, n = rng.randint(1, 6), rng.randint(1, 6)
        grid = [tg.rand_int_array(rng, n, 0, 20) for _ in range(m)]
        return (grid,)

    def gen_stress():
        m, n = rng.randint(80, 150), rng.randint(80, 150)
        grid = [tg.rand_int_array(rng, n, 0, 1000) for _ in range(m)]
        return (grid,)

    visible = [
        ([[1, 3, 1], [1, 5, 1], [4, 2, 1]],),
        ([[5]],),
        ([[1, 2, 3]],),
        ([[1], [2], [3]],),
        ([[1, 2], [1, 1]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([[0]],),
        ([[1, 1]],),
        ([[1], [1]],),
        ([[0, 0], [0, 0]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([[1, 100, 1], [1, 100, 1], [1, 1, 1]],),   # wall of high costs forces a specific detour
        ([[1, 1, 1], [100, 100, 1], [1, 1, 1]],),   # cheap path only via top-then-right
        ([[9, 1, 1], [1, 1, 9], [1, 1, 1]],),        # multiple valid low-cost paths
        ([[1] * 10] * 10,),                            # uniform grid — many equally optimal paths
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([[1, 2], [3, 4]],),      # smallest 2x2 case with a clear better path
        ([[1, 5], [1, 1]],),      # forces down-then-right
        ([[1, 1], [5, 1]],),      # forces right-then-down
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ══════════════════════════════════════════════════════════════════════════
# LEGACY_PLANS registry: slug -> (to_input, format_output, oracle, plan_fn)
# ══════════════════════════════════════════════════════════════════════════

LEGACY_PLANS: dict[str, tuple] = {
    "binary-search": (_to_input_binary_search, str, oracles.binary_search_index, _plan_binary_search),
    "linear-search": (_to_input_linear_search, str, oracles.linear_search_first_index, _plan_linear_search),
    "bubble-sort": (_to_input_bubble_sort, _fmt_list, oracles.bubble_sort_result, _plan_bubble_sort),
    "fibonacci-dp": (_to_input_fib, str, oracles.fibonacci, _plan_fibonacci),
    "gcd-euclidean": (_to_input_gcd, str, oracles.gcd_euclidean, _plan_gcd),
    "two-sum": (_to_input_two_sum, _fmt_pair, oracles.two_sum_indices, _plan_two_sum),
    "maximum-subarray": (_to_input_max_subarray, str, oracles.max_subarray, _plan_max_subarray),
    "coin-change": (_to_input_coin_change, str, oracles.coin_change_min_coins, _plan_coin_change),
    "longest-common-subsequence": (_to_input_lcs, str, oracles.lcs_length, _plan_lcs),
    "house-robber": (_to_input_house_robber, str, oracles.house_robber_max, _plan_house_robber),
    "longest-increasing-subsequence": (_to_input_lis, str, oracles.lis_length, _plan_lis),
    "bfs": (_to_input_bfs, _fmt_list, _oracle_bfs, _plan_bfs),
    "word-break": (_to_input_word_break, _fmt_bool_true_false, _oracle_word_break, _plan_word_break),
    "edit-distance": (_to_input_edit_distance, str, oracles.edit_distance, _plan_edit_distance),
    "unique-paths": (_to_input_unique_paths, str, oracles.unique_paths_count, _plan_unique_paths),
    # "n-queens" deliberately excluded from LEGACY_PLANS -- its domain (14
    # possible integers) can't reach 40 uniques; handled separately via
    # N_QUEENS_REDUCED_CASES (see above) in migrate_legacy_audit_to_forty.py
    # and verify_atlascode_family.py.
    "dijkstra": (_to_input_dijkstra, _fmt_list, _oracle_dijkstra, _plan_dijkstra),
    "kmp": (_to_input_kmp, _fmt_kmp, oracles.kmp_occurrences, _plan_kmp),
    "min-path-sum": (_to_input_min_path_sum, str, oracles.min_path_sum, _plan_min_path_sum),
}


# ══════════════════════════════════════════════════════════════════════════
# REFERENCE_SOLUTIONS — independently written correct Python programs, using
# the EXACT existing stdin/stdout contract of each problem's starter code.
# ══════════════════════════════════════════════════════════════════════════

REFERENCE_SOLUTIONS: dict[str, str] = {
    "binary-search": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "target = int(data[n+1])\n"
        "lo, hi, ans = 0, n - 1, -1\n"
        "while lo <= hi:\n"
        "    mid = (lo + hi) // 2\n"
        "    if nums[mid] == target:\n"
        "        ans = mid\n"
        "        break\n"
        "    elif nums[mid] < target:\n"
        "        lo = mid + 1\n"
        "    else:\n"
        "        hi = mid - 1\n"
        "print(ans)\n"
    ),
    "linear-search": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "target = int(data[n+1])\n"
        "ans = -1\n"
        "for idx in range(n):\n"
        "    if nums[idx] == target:\n"
        "        ans = idx\n"
        "        break\n"
        "print(ans)\n"
    ),
    "bubble-sort": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "swapped = True\n"
        "while swapped:\n"
        "    swapped = False\n"
        "    for i in range(len(nums) - 1):\n"
        "        if nums[i] > nums[i+1]:\n"
        "            nums[i], nums[i+1] = nums[i+1], nums[i]\n"
        "            swapped = True\n"
        "print(' '.join(map(str, nums)))\n"
    ),
    "fibonacci-dp": (
        # Iterative, NOT recursive memoization: the stress bucket generates n
        # up to 5000, far past Python's default recursion limit (1000) --
        # confirmed via verify_atlascode_family.py, a recursive version hit
        # RecursionError on a real stress case.
        "import sys\n"
        "n = int(sys.stdin.read().strip())\n"
        "a, b = 0, 1\n"
        "for _ in range(n):\n"
        "    a, b = b, a + b\n"
        "print(a)\n"
    ),
    "gcd-euclidean": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "a, b = int(data[0]), int(data[1])\n"
        "def gcd(x, y):\n"
        "    while y:\n"
        "        x, y = y, x % y\n"
        "    return x\n"
        "print(gcd(a, b))\n"
    ),
    "two-sum": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "target = int(data[n+1])\n"
        "seen = {}\n"
        "ans = None\n"
        "for idx, val in enumerate(nums):\n"
        "    need = target - val\n"
        "    if need in seen:\n"
        "        ans = (seen[need], idx)\n"
        "        break\n"
        "    if val not in seen:\n"
        "        seen[val] = idx\n"
        "i, j = ans\n"
        "print(min(i, j), max(i, j))\n"
    ),
    "maximum-subarray": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "best = cur = nums[0]\n"
        "for x in nums[1:]:\n"
        "    cur = x if cur < 0 else cur + x\n"
        "    best = max(best, cur)\n"
        "print(best)\n"
    ),
    "coin-change": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "k = int(data[0])\n"
        "coins = list(map(int, data[1:k+1]))\n"
        "amount = int(data[k+1])\n"
        "INF = float('inf')\n"
        "dp = [0] + [INF] * amount\n"
        "for a in range(1, amount + 1):\n"
        "    best = INF\n"
        "    for c in coins:\n"
        "        if c <= a and dp[a-c] + 1 < best:\n"
        "            best = dp[a-c] + 1\n"
        "    dp[a] = best\n"
        "print(dp[amount] if dp[amount] != INF else -1)\n"
    ),
    "longest-common-subsequence": (
        "import sys\n"
        "from functools import lru_cache\n"
        "lines = sys.stdin.read().split()\n"
        "s1, s2 = lines[0], lines[1]\n"
        "sys.setrecursionlimit(10000)\n"
        "@lru_cache(maxsize=None)\n"
        "def solve(i, j):\n"
        "    if i == len(s1) or j == len(s2):\n        return 0\n"
        "    if s1[i] == s2[j]:\n        return 1 + solve(i+1, j+1)\n"
        "    return max(solve(i+1, j), solve(i, j+1))\n"
        "print(solve(0, 0))\n"
    ),
    "house-robber": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "take, skip = 0, 0\n"
        "for x in nums:\n"
        "    take, skip = skip + x, max(take, skip)\n"
        "print(max(take, skip))\n"
    ),
    "longest-increasing-subsequence": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "if n == 0:\n"
        "    print(0)\n"
        "else:\n"
        "    dp = [1] * n\n"
        "    for i in range(n):\n"
        "        for j in range(i):\n"
        "            if nums[j] < nums[i] and dp[j] + 1 > dp[i]:\n"
        "                dp[i] = dp[j] + 1\n"
        "    print(max(dp))\n"
    ),
    "bfs": (
        "import sys\n"
        "from collections import deque\n"
        "data = sys.stdin.read().split()\n"
        "idx = 0\n"
        "n, m, src = int(data[idx]), int(data[idx+1]), int(data[idx+2])\n"
        "idx += 3\n"
        "adj = [[] for _ in range(n)]\n"
        "for _ in range(m):\n"
        "    u, v = int(data[idx]), int(data[idx+1])\n"
        "    idx += 2\n"
        "    adj[u].append(v)\n"
        "    adj[v].append(u)\n"
        "dist = [-1] * n\n"
        "dist[src] = 0\n"
        "q = deque([src])\n"
        "while q:\n"
        "    u = q.popleft()\n"
        "    for v in adj[u]:\n"
        "        if dist[v] == -1:\n"
        "            dist[v] = dist[u] + 1\n"
        "            q.append(v)\n"
        "print(' '.join(map(str, dist)))\n"
    ),
    "word-break": (
        "import sys\n"
        "lines = sys.stdin.read().splitlines()\n"
        "s = lines[0] if lines else ''\n"
        "word_dict = set(lines[1].split()) if len(lines) > 1 else set()\n"
        "n = len(s)\n"
        "dp = [False] * (n + 1)\n"
        "dp[0] = True\n"
        "for end in range(1, n + 1):\n"
        "    for start in range(end):\n"
        "        if dp[start] and s[start:end] in word_dict:\n"
        "            dp[end] = True\n"
        "            break\n"
        "print('true' if dp[n] else 'false')\n"
    ),
    "edit-distance": (
        "import sys\n"
        "lines = sys.stdin.read().splitlines()\n"
        "w1 = lines[0] if len(lines) > 0 else ''\n"
        "w2 = lines[1] if len(lines) > 1 else ''\n"
        "n, m = len(w1), len(w2)\n"
        "prev = list(range(m + 1))\n"
        "for i in range(1, n + 1):\n"
        "    cur = [i] + [0] * m\n"
        "    for j in range(1, m + 1):\n"
        "        if w1[i-1] == w2[j-1]:\n"
        "            cur[j] = prev[j-1]\n"
        "        else:\n"
        "            cur[j] = 1 + min(prev[j], cur[j-1], prev[j-1])\n"
        "    prev = cur\n"
        "print(prev[m])\n"
    ),
    "unique-paths": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "m, n = int(data[0]), int(data[1])\n"
        "import math\n"
        "print(math.comb(m + n - 2, m - 1))\n"
    ),
    "n-queens": (
        "import sys\n"
        "n = int(sys.stdin.read().strip())\n"
        "count = 0\n"
        "cols = [False] * n\n"
        "diag1 = [False] * (2 * n)\n"
        "diag2 = [False] * (2 * n)\n"
        "def place(row):\n"
        "    global count\n"
        "    if row == n:\n"
        "        count += 1\n"
        "        return\n"
        "    for col in range(n):\n"
        "        d1, d2 = row - col + n, row + col\n"
        "        if cols[col] or diag1[d1] or diag2[d2]:\n"
        "            continue\n"
        "        cols[col] = diag1[d1] = diag2[d2] = True\n"
        "        place(row + 1)\n"
        "        cols[col] = diag1[d1] = diag2[d2] = False\n"
        "if n > 0:\n"
        "    place(0)\n"
        "    print(count)\n"
        "else:\n"
        "    print(1)\n"
    ),
    "dijkstra": (
        "import sys, heapq\n"
        "data = sys.stdin.read().split()\n"
        "idx = 0\n"
        "n, m = int(data[idx]), int(data[idx+1])\n"
        "idx += 2\n"
        "adj = [[] for _ in range(n)]\n"
        "for _ in range(m):\n"
        "    u, v, w = int(data[idx]), int(data[idx+1]), int(data[idx+2])\n"
        "    idx += 3\n"
        "    adj[u].append((v, w))\n"
        "INF = float('inf')\n"
        "dist = [INF] * n\n"
        "dist[0] = 0\n"
        "pq = [(0, 0)]\n"
        "done = [False] * n\n"
        "while pq:\n"
        "    d, u = heapq.heappop(pq)\n"
        "    if done[u]:\n"
        "        continue\n"
        "    done[u] = True\n"
        "    for v, w in adj[u]:\n"
        "        if d + w < dist[v]:\n"
        "            dist[v] = d + w\n"
        "            heapq.heappush(pq, (dist[v], v))\n"
        "print(' '.join(str(d) if d != INF else '-1' for d in dist))\n"
    ),
    "kmp": (
        "import sys\n"
        "lines = sys.stdin.read().splitlines()\n"
        "T, P = lines[0], lines[1]\n"
        "n, m = len(T), len(P)\n"
        "lps = [0] * m\n"
        "k = 0\n"
        "for i in range(1, m):\n"
        "    while k > 0 and P[i] != P[k]:\n"
        "        k = lps[k-1]\n"
        "    if P[i] == P[k]:\n"
        "        k += 1\n"
        "    lps[i] = k\n"
        "result = []\n"
        "k = 0\n"
        "for i in range(n):\n"
        "    while k > 0 and T[i] != P[k]:\n"
        "        k = lps[k-1]\n"
        "    if T[i] == P[k]:\n"
        "        k += 1\n"
        "    if k == m:\n"
        "        result.append(i - m + 1)\n"
        "        k = lps[k-1]\n"
        "print(' '.join(map(str, result)) if result else '-1')\n"
    ),
    "min-path-sum": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "idx = 0\n"
        "m, n = int(data[idx]), int(data[idx+1])\n"
        "idx += 2\n"
        "grid = [list(map(int, data[idx+i*n:idx+(i+1)*n])) for i in range(m)]\n"
        "dp = [[0] * n for _ in range(m)]\n"
        "for i in range(m):\n"
        "    for j in range(n):\n"
        "        if i == 0 and j == 0:\n"
        "            dp[i][j] = grid[i][j]\n"
        "        elif i == 0:\n"
        "            dp[i][j] = dp[i][j-1] + grid[i][j]\n"
        "        elif j == 0:\n"
        "            dp[i][j] = dp[i-1][j] + grid[i][j]\n"
        "        else:\n"
        "            dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + grid[i][j]\n"
        "print(dp[m-1][n-1])\n"
    ),
}


# ══════════════════════════════════════════════════════════════════════════
# WRONG_SOLUTIONS — plausible-bug wrong programs, one real subtle bug each.
# ══════════════════════════════════════════════════════════════════════════

WRONG_SOLUTIONS: dict[str, str] = {
    "binary-search": (
        # BUG: uses mid = (lo+hi)//2 but never adjusts hi = mid (off-by-one:
        # uses hi = mid instead of mid-1), causing infinite-loop-avoidance
        # via wrong shrink -- here simulated as strict '<' on hi so it misses
        # the last element check; concretely: fails when target is at hi.
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "target = int(data[n+1])\n"
        "lo, hi, ans = 0, n - 1, -1\n"
        "while lo < hi:\n"  # BUG: should be lo <= hi, misses single-element ranges
        "    mid = (lo + hi) // 2\n"
        "    if nums[mid] == target:\n"
        "        ans = mid\n"
        "        break\n"
        "    elif nums[mid] < target:\n"
        "        lo = mid + 1\n"
        "    else:\n"
        "        hi = mid - 1\n"
        "print(ans)\n"
    ),
    "linear-search": (
        # BUG: returns the LAST index instead of the FIRST.
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "target = int(data[n+1])\n"
        "ans = -1\n"
        "for idx in range(n):\n"
        "    if nums[idx] == target:\n"
        "        ans = idx\n"  # BUG: no break -- keeps overwriting with later matches
        "print(ans)\n"
    ),
    "bubble-sort": (
        # BUG: inner loop range is off by one short, leaving the array
        # partially unsorted for certain inputs (misses the final comparison).
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "for i in range(len(nums)):\n"
        "    for j in range(0, len(nums) - i - 2):\n"  # BUG: -2 instead of -1
        "        if nums[j] > nums[j+1]:\n"
        "            nums[j], nums[j+1] = nums[j+1], nums[j]\n"
        "print(' '.join(map(str, nums)))\n"
    ),
    "fibonacci-dp": (
        # BUG: swapped base cases -- fib(0)=1, fib(1)=0.
        "import sys\n"
        "n = int(sys.stdin.read().strip())\n"
        "if n == 0:\n"
        "    print(1)\n"
        "elif n == 1:\n"
        "    print(0)\n"
        "else:\n"
        "    a, b = 1, 0\n"
        "    for _ in range(n - 1):\n"
        "        a, b = b, a + b\n"
        "    print(b)\n"
    ),
    "gcd-euclidean": (
        # BUG: uses subtraction-based Euclid but forgets to handle b > a
        # ordering, hangs/errors or gives wrong result when a < b initially
        # since it only subtracts a -= b without ever swapping.
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "a, b = int(data[0]), int(data[1])\n"
        "if a == 0:\n"
        "    print(b)\n"
        "elif b == 0:\n"
        "    print(a)\n"
        "else:\n"
        "    while a != b:\n"
        "        if a > b:\n"
        "            a -= b\n"
        # BUG: missing 'else: b -= a' branch -- infinite loop avoided only
        # because we cap iterations, but result is wrong when b > a stays true
        "        if a < b:\n"
        "            pass\n"
        "    print(a)\n"
    ),
    "two-sum": (
        # BUG: allows using the SAME index twice (checks complement including
        # itself before recording), so e.g. nums=[3,3] target=6 might print "0 0".
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "target = int(data[n+1])\n"
        "seen = {}\n"
        "ans = None\n"
        "for idx, val in enumerate(nums):\n"
        "    seen[val] = idx\n"  # BUG: records BEFORE checking complement
        "    need = target - val\n"
        "    if need in seen:\n"
        "        ans = (seen[need], idx)\n"
        "        break\n"
        "i, j = ans\n"
        "print(min(i, j), max(i, j))\n"
    ),
    "maximum-subarray": (
        # BUG: resets `cur` to 0 instead of tracking max(x, cur+x); fails on
        # all-negative arrays (returns 0 instead of the least-negative value).
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "best = 0\n"
        "cur = 0\n"
        "for x in nums:\n"
        "    cur = cur + x\n"
        "    if cur < 0:\n"
        "        cur = 0\n"
        "    best = max(best, cur)\n"
        "print(best)\n"
    ),
    "coin-change": (
        # BUG: greedy largest-coin-first approach -- wrong for non-canonical
        # coin systems (e.g. coins=[1,3,4], amount=6 -> greedy gives 3 (4+1+1)
        # instead of optimal 2 (3+3)).
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "k = int(data[0])\n"
        "coins = sorted(map(int, data[1:k+1]), reverse=True)\n"
        "amount = int(data[k+1])\n"
        "count = 0\n"
        "remaining = amount\n"
        "for c in coins:\n"
        "    if c <= remaining:\n"
        "        take = remaining // c\n"
        "        count += take\n"
        "        remaining -= take * c\n"
        "print(count if remaining == 0 else -1)\n"
    ),
    "longest-common-subsequence": (
        # BUG: only checks matching characters at the SAME index (subsequence
        # via zip), not a true LCS -- badly undercounts for shifted matches.
        "import sys\n"
        "lines = sys.stdin.read().split()\n"
        "s1, s2 = lines[0], lines[1]\n"
        "count = 0\n"
        "for a, b in zip(s1, s2):\n"
        "    if a == b:\n"
        "        count += 1\n"
        "print(count)\n"
    ),
    "house-robber": (
        # BUG: greedy alternating (always pick even indices) instead of DP;
        # wrong when the optimal selection isn't every-other-starting-at-0.
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "print(sum(nums[i] for i in range(0, n, 2)))\n"
    ),
    "longest-increasing-subsequence": (
        # BUG: uses non-strict '<=' comparator, over-counting equal elements
        # as part of an increasing run.
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:n+1]))\n"
        "if n == 0:\n"
        "    print(0)\n"
        "else:\n"
        "    dp = [1] * n\n"
        "    for i in range(n):\n"
        "        for j in range(i):\n"
        "            if nums[j] <= nums[i] and dp[j] + 1 > dp[i]:\n"  # BUG: <= not <
        "                dp[i] = dp[j] + 1\n"
        "    print(max(dp))\n"
    ),
    "bfs": (
        # BUG: uses DFS-style stack (LIFO via list.pop()) instead of a proper
        # BFS queue, which can produce non-shortest hop distances.
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "idx = 0\n"
        "n, m, src = int(data[idx]), int(data[idx+1]), int(data[idx+2])\n"
        "idx += 3\n"
        "adj = [[] for _ in range(n)]\n"
        "for _ in range(m):\n"
        "    u, v = int(data[idx]), int(data[idx+1])\n"
        "    idx += 2\n"
        "    adj[u].append(v)\n"
        "    adj[v].append(u)\n"
        "dist = [-1] * n\n"
        "dist[src] = 0\n"
        "stack = [src]\n"
        "while stack:\n"
        "    u = stack.pop()\n"  # BUG: LIFO instead of FIFO -- not real BFS
        "    for v in adj[u]:\n"
        "        if dist[v] == -1:\n"
        "            dist[v] = dist[u] + 1\n"
        "            stack.append(v)\n"
        "print(' '.join(map(str, dist)))\n"
    ),
    "word-break": (
        # BUG: greedy longest-prefix-match instead of DP -- fails when the
        # greedy longest match blocks a valid later segmentation.
        "import sys\n"
        "lines = sys.stdin.read().splitlines()\n"
        "s = lines[0] if lines else ''\n"
        "word_dict = set(lines[1].split()) if len(lines) > 1 else set()\n"
        "i = 0\n"
        "n = len(s)\n"
        "ok = True\n"
        "while i < n:\n"
        "    matched = False\n"
        "    for end in range(n, i, -1):\n"  # BUG: greedily takes longest match first
        "        if s[i:end] in word_dict:\n"
        "            i = end\n"
        "            matched = True\n"
        "            break\n"
        "    if not matched:\n"
        "        ok = False\n"
        "        break\n"
        "print('true' if ok else 'false')\n"
    ),
    "edit-distance": (
        # BUG: forgets the substitution option, only allows insert/delete
        # (equivalent to computing via LCS-style edit distance), overcounts.
        "import sys\n"
        "lines = sys.stdin.read().splitlines()\n"
        "w1 = lines[0] if len(lines) > 0 else ''\n"
        "w2 = lines[1] if len(lines) > 1 else ''\n"
        "n, m = len(w1), len(w2)\n"
        "dp = [[0]*(m+1) for _ in range(n+1)]\n"
        "for i in range(n+1):\n"
        "    dp[i][0] = i\n"
        "for j in range(m+1):\n"
        "    dp[0][j] = j\n"
        "for i in range(1, n+1):\n"
        "    for j in range(1, m+1):\n"
        "        if w1[i-1] == w2[j-1]:\n"
        "            dp[i][j] = dp[i-1][j-1]\n"
        "        else:\n"
        "            dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1])\n"  # BUG: missing dp[i-1][j-1] (no substitution)
        "print(dp[n][m])\n"
    ),
    "unique-paths": (
        # BUG: computes m*n (total cells) instead of the binomial path count.
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "m, n = int(data[0]), int(data[1])\n"
        "print(m * n)\n"
    ),
    "n-queens": (
        # BUG: only checks column and one diagonal direction, not both
        # diagonals -- overcounts solutions (accepts invalid placements).
        "import sys\n"
        "n = int(sys.stdin.read().strip())\n"
        "count = 0\n"
        "cols = [False] * n\n"
        "diag1 = [False] * (2 * n)\n"
        "def place(row):\n"
        "    global count\n"
        "    if row == n:\n"
        "        count += 1\n"
        "        return\n"
        "    for col in range(n):\n"
        "        d1 = row - col + n\n"
        "        if cols[col] or diag1[d1]:\n"  # BUG: missing anti-diagonal check
        "            continue\n"
        "        cols[col] = diag1[d1] = True\n"
        "        place(row + 1)\n"
        "        cols[col] = diag1[d1] = False\n"
        "if n > 0:\n"
        "    place(0)\n"
        "    print(count)\n"
        "else:\n"
        "    print(1)\n"
    ),
    "dijkstra": (
        # BUG: Bellman-Ford-style single relaxation pass only ONCE through
        # edges in input order (not repeated to convergence) -- misses
        # multi-hop shortest paths that require several relaxation rounds.
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "idx = 0\n"
        "n, m = int(data[idx]), int(data[idx+1])\n"
        "idx += 2\n"
        "edges = []\n"
        "for _ in range(m):\n"
        "    u, v, w = int(data[idx]), int(data[idx+1]), int(data[idx+2])\n"
        "    idx += 3\n"
        "    edges.append((u, v, w))\n"
        "INF = float('inf')\n"
        "dist = [INF] * n\n"
        "dist[0] = 0\n"
        "for u, v, w in edges:\n"  # BUG: single pass, not repeated to fixpoint
        "    if dist[u] != INF and dist[u] + w < dist[v]:\n"
        "        dist[v] = dist[u] + w\n"
        "print(' '.join(str(d) if d != INF else -1 for d in dist))\n"
    ),
    "kmp": (
        # BUG: naive O(n*m) matching that forgets to allow overlapping
        # matches correctly is actually fine for overlap; instead inject a
        # real bug: it advances i by len(P) after a match (skips overlaps).
        "import sys\n"
        "lines = sys.stdin.read().splitlines()\n"
        "T, P = lines[0], lines[1]\n"
        "n, m = len(T), len(P)\n"
        "result = []\n"
        "i = 0\n"
        "while i <= n - m:\n"
        "    if T[i:i+m] == P:\n"
        "        result.append(i)\n"
        "        i += m\n"  # BUG: skips overlapping occurrences
        "    else:\n"
        "        i += 1\n"
        "print(' '.join(map(str, result)) if result else '-1')\n"
    ),
    "min-path-sum": (
        # BUG: always moves right until the last column, then down --
        # a fixed greedy path, not the true minimum.
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "idx = 0\n"
        "m, n = int(data[idx]), int(data[idx+1])\n"
        "idx += 2\n"
        "grid = [list(map(int, data[idx+i*n:idx+(i+1)*n])) for i in range(m)]\n"
        "total = grid[0][0]\n"
        "r, c = 0, 0\n"
        "while c < n - 1:\n"
        "    c += 1\n"
        "    total += grid[r][c]\n"
        "while r < m - 1:\n"
        "    r += 1\n"
        "    total += grid[r][c]\n"
        "print(total)\n"
    ),
}
