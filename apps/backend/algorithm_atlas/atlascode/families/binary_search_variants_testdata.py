"""
40-test case plans for the `binary-search-variants` family (see testgen.py
for the shared bucket contract: visible 5 / basic 7 / boundary 8 /
adversarial 8 / mutation 7 / stress 5 = 40). One entry per slug in
binary_search_variants.py's `_SPECS`.

Each `to_input` mirrors the exact stdin format the original hand-written
`_Spec.cases` already used (verified against binary_search_variants.py and
the reference solutions in scripts/verify_atlascode_family.py before writing
this). Several of these problems fundamentally require SORTED input arrays
(the whole point of binary search) — every generator for those slugs
produces genuinely sorted (non-decreasing, or strictly increasing where the
contract demands distinct elements) arrays.
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


# ── rotated-binary-search: oracle(nums, target); nums = rotated ascending distinct ──

def _to_input_rotated_search(nums, target):
    return f"{len(nums)} {_arr(nums)} {target}"


def _rotate(xs: list[int], k: int) -> list[int]:
    if not xs:
        return xs
    k %= len(xs)
    return xs[k:] + xs[:k]


def _plan_rotated_search(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_rotated_search

    def gen_small(hit: bool | None = None):
        n = rng.randint(3, 8)
        base = sorted(rng.sample(range(-50, 50), n))
        k = rng.randint(0, n - 1)
        rotated = _rotate(base, k)
        if hit is True:
            target = rng.choice(rotated)
        elif hit is False:
            target = 10_000
        else:
            target = rng.choice(rotated) if rng.random() < 0.5 else 10_000
        return (rotated, target)

    def gen_stress():
        n = rng.randint(2000, 5000)
        base = sorted(rng.sample(range(-1_000_000, 1_000_000), n))
        k = rng.randint(0, n - 1)
        rotated = _rotate(base, k)
        target = rng.choice(rotated) if rng.random() < 0.5 else 1_500_000
        return (rotated, target)

    visible = [
        ([4, 5, 6, 7, 0, 1, 2], 0),
        ([4, 5, 6, 7, 0, 1, 2], 3),
        ([1], 1),
        ([5, 1, 3], 5),
        ([6, 7, 1, 2, 3, 4, 5], 6),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1], 1),
        ([1], 2),
        ([1, 2], 1),
        ([2, 1], 1),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(10)), 0),               # no rotation — pivot at index 0
        (_rotate(list(range(10)), 1), 9),   # minimal rotation, target at the wrap
        (_rotate(list(range(10)), 9), 0),   # rotation of n-1
        ([3, 1], 1),                        # two-element rotated
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([4, 5, 6, 7, 0, 1, 2], 4),   # target == nums[lo], left-half boundary check
        ([4, 5, 6, 7, 0, 1, 2], 2),   # target == nums[hi], right-half boundary check
        ([1, 2, 3, 4, 5], 5),         # not rotated, target is last element
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── bitonic-peak-index: oracle(nums); strictly increase-then-decrease, len >= 3 ──

def _to_input_bitonic(nums):
    return f"{len(nums)} {_arr(nums)}"


def _gen_bitonic(rng: random.Random, n: int, lo: int = -50, hi: int = 50) -> list[int]:
    # Draw all n values ONCE and construct the bitonic shape by partitioning
    # them (largest = peak), rather than rejection-sampling an independent
    # "up"/"down" pair until max(down) < max(up). The old approach could
    # retry effectively forever: when `peak` (the up-side sample size) is
    # small relative to n (very plausible at stress scale, n up to 5000),
    # max(up) is the max of only a couple of draws while max(down) is the
    # max of thousands of draws from the same range, making the exit
    # condition astronomically unlikely per retry (confirmed via py-spy: a
    # live migration run was stuck in this exact loop for 100+ minutes on
    # one unlucky peak draw). This construction guarantees a valid strictly
    # increasing-then-decreasing sequence with zero retries.
    peak = rng.randint(1, n - 2)
    vals = rng.sample(range(lo, hi), n)
    vals.sort()
    peak_val = vals[-1]
    rest = vals[:-1]
    rng.shuffle(rest)
    up = sorted(rest[:peak]) + [peak_val]
    down = sorted(rest[peak:], reverse=True)
    return up + down


def _plan_bitonic(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_bitonic

    def gen_small():
        n = rng.randint(3, 10)
        return (_gen_bitonic(rng, n),)

    def gen_stress():
        n = rng.randint(2000, 5000)
        return (_gen_bitonic(rng, n, -1_000_000, 1_000_000),)

    visible = [
        ([1, 2, 3, 1],), ([1, 2, 3, 4, 5, 6, 7, 1],), ([1, 9, 8, 7, 6, 5, 4, 3],),
        ([1, 2, 5, 4, 3],), ([5, 10, 20, 15, 2],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1, 3, 2],),        # smallest valid length-3 bitonic
        ([-10, 0, -5],),     # negative values
        ([1, 100, 2],),      # peak far from both edges relatively
        ([-5, -1, -2],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 2, 3, 4, 5, 4],),        # peak second-to-last
        ([2, 5, 4, 3, 2, 1],),        # peak second element
        ([1, 2, 3, 4, 5, 6, 7, 8, 1],),  # peak near the very end
        ([1, 8, 7, 6, 5, 4, 3, 2],),  # peak near the very start
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 3, 2],),   # off-by-one on lo/hi mid comparison
        ([1, 2, 4, 3],),
        ([3, 4, 5, 2, 1],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── first-occurrence / last-occurrence / count-occurrences-sorted: oracle(nums, target) ──
# nums = sorted (non-decreasing), may be empty.

def _to_input_occ(nums, target):
    return f"{len(nums)} {_arr(nums)} {target}"


def _plan_occurrence(rng: random.Random, visible: list, boundary_extra: list, adversarial_extra: list, mutation_extra: list) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_occ

    def gen_small():
        n = rng.randint(1, 8)
        nums = tg.rand_sorted_array(rng, n, 0, 10)
        target = rng.choice(nums) if rng.random() < 0.6 else rng.randint(-2, 12)
        return (nums, target)

    def gen_stress():
        n = rng.randint(2000, 8000)
        nums = tg.rand_sorted_array(rng, n, 0, 50)
        target = rng.choice(nums) if rng.random() < 0.7 else rng.randint(-5, 55)
        return (nums, target)

    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([], 5), ([1], 1), ([1], 2), ([2, 2, 2, 2, 2], 2)] + boundary_extra
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1] * 10, 1),
        (list(range(10)), 0),
        (list(range(10)), 9),
        ([0, 0, 1, 1, 1, 1, 2, 2], 1),
    ] + adversarial_extra
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 1], 1),
        ([1, 2], 1),
        ([1, 2], 2),
    ] + mutation_extra
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


def _plan_first_occurrence(rng: random.Random) -> tg.CasePlan:
    visible = [
        ([5, 7, 7, 8, 8, 10], 8),
        ([5, 7, 7, 8, 8, 10], 6),
        ([], 5),
        ([1, 1, 1, 1, 1], 1),
        ([1, 3, 3, 3, 5], 3),
    ]
    return _plan_occurrence(rng, visible, [], [], [])


def _plan_last_occurrence(rng: random.Random) -> tg.CasePlan:
    visible = [
        ([5, 7, 7, 8, 8, 10], 8),
        ([5, 7, 7, 8, 8, 10], 6),
        ([1, 1, 1, 1, 1], 1),
        ([9], 9),
        ([1, 3, 3, 3, 5], 3),
    ]
    return _plan_occurrence(rng, visible, [], [], [])


def _plan_count_occurrences(rng: random.Random) -> tg.CasePlan:
    visible = [
        ([5, 7, 7, 8, 8, 8, 10], 8),
        ([5, 7, 7, 8, 8, 10], 6),
        ([], 3),
        ([2, 2, 2, 2, 2], 2),
        ([1, 3, 3, 3, 5], 3),
    ]
    return _plan_occurrence(rng, visible, [], [], [])


# ── search-insert-position: oracle(nums, target); nums sorted distinct, may be empty ──

def _to_input_insert(nums, target):
    return f"{len(nums)} {_arr(nums)} {target}"


def _plan_search_insert(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_insert

    def gen_small():
        n = rng.randint(0, 8)
        nums = tg.rand_sorted_array(rng, n, 0, 30, strict=True) if n else []
        target = rng.choice(nums) if nums and rng.random() < 0.5 else rng.randint(-5, 35)
        return (nums, target)

    def gen_stress():
        n = rng.randint(2000, 8000)
        nums = tg.rand_sorted_array(rng, n, 0, 200_000, strict=True)
        target = rng.choice(nums) if rng.random() < 0.5 else rng.randint(-100, 200_100)
        return (nums, target)

    visible = [
        ([1, 3, 5, 6], 5),
        ([1, 3, 5, 6], 2),
        ([], 4),
        ([1, 3, 5, 6], 7),
        ([1, 3, 5, 6], 0),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([], 0), ([5], 5), ([5], 4), ([5], 6),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(0, 20, 2)), 1),    # falls exactly between two elements
        (list(range(0, 20, 2)), -5),   # insert before everything
        (list(range(0, 20, 2)), 100),  # insert after everything
        (list(range(10)), 5),          # exact match mid-array
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 3], 2),   # midpoint insert, off-by-one lo/hi check
        ([1, 3], 0),
        ([1, 3], 4),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── koko-eating-bananas: oracle(piles, h); requires len(piles) <= h ──

def _to_input_koko(piles, h):
    return f"{len(piles)} {_arr(piles)} {h}"


def _plan_koko(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_koko

    def gen_small():
        n = rng.randint(1, 6)
        piles = tg.rand_int_array(rng, n, 1, 50)
        h = rng.randint(n, n + 20)
        return (piles, h)

    def gen_stress():
        n = rng.randint(2000, 5000)
        piles = tg.rand_int_array(rng, n, 1, 1_000_000_000)
        h = rng.randint(n, n * 3)
        return (piles, h)

    visible = [
        ([3, 6, 7, 11], 8),
        ([30, 11, 23, 4, 20], 5),
        ([30, 11, 23, 4, 20], 6),
        ([5], 5),
        ([1, 1, 1], 3),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1], 1), ([1_000_000_000], 1), ([1, 1, 1, 1], 4), ([5, 5, 5], 3),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 1, 1, 1, 1, 1, 1, 1, 1, 100], 10),   # one huge outlier pile
        ([10, 10, 10, 10], 4),                     # exactly n hours — must finish each in 1 hr
        ([10, 10, 10, 10], 40),                     # lots of slack — speed 1 suffices
        ([7, 7, 7, 7, 7, 7, 7], 7),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([4], 2),   # ceil-division boundary: 4/2 exactly
        ([5], 2),   # ceil-division boundary: needs rounding up
        ([3, 3], 2),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── ship-packages-within-days: oracle(weights, days); days <= len(weights) ──

def _to_input_ship(weights, days):
    return f"{len(weights)} {_arr(weights)} {days}"


def _plan_ship(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_ship

    def gen_small():
        n = rng.randint(1, 8)
        weights = tg.rand_int_array(rng, n, 1, 20)
        days = rng.randint(1, n)
        return (weights, days)

    def gen_stress():
        n = rng.randint(3000, 8000)
        weights = tg.rand_int_array(rng, n, 1, 500)
        days = rng.randint(max(1, n // 20), n)
        return (weights, days)

    visible = [
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5),
        ([3, 2, 2, 4, 1, 4], 3),
        ([1, 2, 3, 1, 1], 4),
        ([7], 1),
        ([1, 1, 1, 1, 1], 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1], 1), ([500], 1), ([1, 1, 1], 3), ([1, 1, 1], 1),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 1, 1, 1, 1, 1, 1, 1, 1, 100], 2),   # one huge outlier package
        ([10] * 10, 10),                          # days == n, capacity == max weight
        ([10] * 10, 1),                            # days == 1, capacity == sum
        ([5, 4, 3, 2, 1], 2),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2, 3, 4, 5], 5),   # days == n, must ship each item separately
        ([5, 4, 3], 2),
        ([2, 2, 2, 2], 2),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── integer-square-root: oracle(n); n >= 0 ────────────────────────────────────

def _to_input_sqrt(n):
    return str(n)


def _plan_integer_sqrt(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_sqrt

    def gen_small():
        return (rng.randint(0, 10_000),)

    def gen_stress():
        return (rng.randint(10**9, 2**31 - 1),)

    visible = [(4,), (8,), (0,), (2147395599,), (16,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(0,), (1,), (2,), (2**31 - 1,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (99,),          # just below a perfect square (100)
        (101,),         # just above a perfect square (100)
        (2**31 - 2,),   # near max, non-perfect-square
        (46340 * 46340,),  # exact perfect square near sqrt(2^31) boundary
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (3,),   # floor(sqrt(3)) == 1, off-by-one trap
        (2,),   # floor(sqrt(2)) == 1
        (15,),  # floor(sqrt(15)) == 3, just under 16
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── search-2d-matrix: oracle(matrix, target); rows ascending, row0[0] > prevRow[-1] ──

def _to_input_matrix(matrix, target):
    m, n = len(matrix), len(matrix[0])
    body = "\n".join(_arr(row) for row in matrix)
    return f"{m} {n}\n{body}\n{target}"


def _gen_sorted_matrix(rng: random.Random, m: int, n: int, lo: int = 0, spread: int = 5) -> list[list[int]]:
    total = m * n
    start = rng.randint(lo, lo + 20)
    flat = [start]
    for _ in range(total - 1):
        flat.append(flat[-1] + rng.randint(1, spread))
    return [flat[i * n:(i + 1) * n] for i in range(m)]


def _plan_search_2d_matrix(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_matrix

    def gen_small(hit: bool | None = None):
        m = rng.randint(1, 5)
        n = rng.randint(1, 5)
        matrix = _gen_sorted_matrix(rng, m, n)
        flat = [v for row in matrix for v in row]
        if hit is True:
            target = rng.choice(flat)
        elif hit is False:
            target = flat[-1] + 1000
        else:
            target = rng.choice(flat) if rng.random() < 0.5 else flat[-1] + 1000
        return (matrix, target)

    def gen_stress():
        m = rng.randint(50, 100)
        n = rng.randint(50, 100)
        matrix = _gen_sorted_matrix(rng, m, n, 0, 3)
        flat = [v for row in matrix for v in row]
        target = rng.choice(flat) if rng.random() < 0.5 else flat[-1] + 500
        return (matrix, target)

    visible = [
        ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3),
        ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13),
        ([[5]], 5),
        ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 34),
        ([[1, 2], [3, 4]], 4),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([[1]], 1), ([[1]], 2), ([[1, 2, 3, 4, 5]], 1), ([[1, 2, 3, 4, 5]], 5),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([[1, 3], [5, 7], [9, 11]], 7),    # target is last element of a middle row
        ([[1, 3], [5, 7], [9, 11]], 8),    # target falls in the gap between rows
        ([[1, 3], [5, 7], [9, 11]], 0),    # below everything
        ([[1, 3], [5, 7], [9, 11]], 12),   # above everything
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([[1, 3, 5], [7, 9, 11]], 1),    # target at flattened index 0
        ([[1, 3, 5], [7, 9, 11]], 11),   # target at flattened index n-1
        ([[1, 3, 5], [7, 9, 11]], 5),    # target at row boundary
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── find-minimum-rotated-sorted-array: oracle(nums); rotated ascending distinct ──

def _to_input_find_min(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_find_min_rotated(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_find_min

    def gen_small():
        n = rng.randint(1, 8)
        base = sorted(rng.sample(range(-50, 50), n))
        k = rng.randint(0, n - 1)
        return (_rotate(base, k),)

    def gen_stress():
        n = rng.randint(2000, 5000)
        base = sorted(rng.sample(range(-1_000_000, 1_000_000), n))
        k = rng.randint(0, n - 1)
        return (_rotate(base, k),)

    visible = [
        ([3, 4, 5, 1, 2],), ([4, 5, 6, 7, 0, 1, 2],), ([11, 13, 15, 17],),
        ([2, 1],), ([5, 1, 2, 3, 4],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1],), ([1, 2],), ([2, 1],), ([1, 2, 3],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(10)),),                    # no rotation
        (_rotate(list(range(10)), 1),),        # minimal rotation
        (_rotate(list(range(10)), 9),),        # rotation of n-1
        (_rotate(list(range(-5, 5)), 5),),     # negatives, midpoint rotation
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 3, 4, 5, 1],),   # min at the very end
        ([5, 1, 2, 3, 4],),   # min right after the pivot
        ([1, 2, 3, 4, 5],),   # already sorted (k=0)
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

def _fmt_bool(a) -> str:
    return "true" if a else "false"


BINARY_SEARCH_VARIANT_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "rotated-binary-search": (_to_input_rotated_search, str, _plan_rotated_search),
    "bitonic-peak-index": (_to_input_bitonic, str, _plan_bitonic),
    "first-occurrence": (_to_input_occ, str, _plan_first_occurrence),
    "last-occurrence": (_to_input_occ, str, _plan_last_occurrence),
    "count-occurrences-sorted": (_to_input_occ, str, _plan_count_occurrences),
    "search-insert-position": (_to_input_insert, str, _plan_search_insert),
    "koko-eating-bananas": (_to_input_koko, str, _plan_koko),
    "ship-packages-within-days": (_to_input_ship, str, _plan_ship),
    "integer-square-root": (_to_input_sqrt, str, _plan_integer_sqrt),
    "search-2d-matrix": (_to_input_matrix, _fmt_bool, _plan_search_2d_matrix),
    "find-minimum-rotated-sorted-array": (_to_input_find_min, str, _plan_find_min_rotated),
}
