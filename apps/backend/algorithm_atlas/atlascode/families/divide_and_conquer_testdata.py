"""
40-test case plans for the `divide-and-conquer` family (see testgen.py for
the shared bucket contract: visible 5 / basic 7 / boundary 8 / adversarial 8
/ mutation 7 / stress 5 = 40). One entry per slug in divide_and_conquer.py's
`_SPECS`.

Each `to_input` mirrors the exact stdin format the original hand-written
`_Spec.cases` already used (verified against divide_and_conquer.py before
writing this) — in particular the multi-line matrix / point-list formats
that join rows with '\\n'.

Stress-bucket sizes for `matrix-exponentiation` and `strassen` are kept
modest (matrix dimension <= ~12, exponent <= ~10^6) since their reference
solutions are pure-Python O(n^3 log k) / O(n^3) and run inside the judge's
per-test wall-clock budget — a naive 64x64 Strassen-shaped stress case would
be safe by constraint (n,m,p <= 64) but multiplies judge subprocess overhead
across 40 cases, so we stay well under the ceiling instead of chasing it.
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


# ── closest-pair: oracle(points) — list[(x, y)] ───────────────────────────────

def _to_input_closest_pair(points):
    lines = [str(len(points))]
    lines += [f"{x} {y}" for x, y in points]
    return "\n".join(lines)


def _plan_closest_pair(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_closest_pair

    def gen_small():
        n = rng.randint(3, 8)
        pts = [(rng.randint(-30, 30), rng.randint(-30, 30)) for _ in range(n)]
        return (pts,)

    def gen_stress():
        # NOTE: closest_pair_min_sq_distance in independent_oracles.py is a
        # naive O(n^2) double loop (used only to compute expected_output at
        # generation time, not by the judge). Keep n modest so 40-test
        # generation itself stays fast — the judge still exercises the
        # divide-and-conquer reference solution's O(n log n) path just as
        # thoroughly at this size.
        n = rng.randint(300, 600)
        pts = [(rng.randint(-10_000, 10_000), rng.randint(-10_000, 10_000)) for _ in range(n)]
        return (pts,)

    visible = [
        ([(0, 0), (3, 4), (1, 1)],),
        ([(0, 0), (10, 10)],),
        ([(5, 5), (5, 5)],),
        ([(0, 0), (0, 10), (1, 1)],),
        ([(-5, -5), (5, 5), (0, 0)],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([(0, 0), (1, 0)],),
        ([(0, 0), (0, 1)],),
        ([(-10_000, -10_000), (10_000, 10_000)],),
        ([(0, 0), (0, 0), (0, 0)],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([(i, 0) for i in range(10)],),                      # all collinear on x-axis
        ([(0, i) for i in range(10)],),                       # all collinear on y-axis
        ([(i, i) for i in range(10)],),                       # diagonal — tests strip-merge step
        ([(0, 0), (10, 10), (5, 5), (5, 5), (20, 0)],),       # duplicate point plus a close pair
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([(0, 0), (1, 1), (100, 100)],),   # closest pair not adjacent when sorted by x
        ([(0, 0), (2, 0), (1, 0)],),        # closest pair is a middle split-boundary case
        ([(0, 0), (1, 0), (0, 1)],),        # ties between two equally-close pairs
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


# ── counting-inversions: oracle(nums) ─────────────────────────────────────────

def _to_input_inversions(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_counting_inversions(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_inversions

    def gen_small():
        n = rng.randint(2, 8)
        return (tg.rand_int_array(rng, n, -50, 50),)

    def gen_stress():
        # NOTE: count_inversions in independent_oracles.py is a naive O(n^2)
        # double loop (used only to compute expected_output at generation
        # time, not by the judge). Keep n modest so 40-test generation itself
        # stays fast — the *judge* still exercises the divide-and-conquer
        # reference solution's O(n log n) path just as thoroughly at this size.
        n = rng.randint(800, 1500)
        return (tg.rand_int_array(rng, n, -10**6, 10**6),)

    visible = [
        ([2, 4, 1, 3, 5],), ([1, 2, 3],), ([5],), ([5, 4, 3, 2, 1],),
        ([3, 1, 2],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([1],),
        ([1, 1],),
        ([1, 2],),
        ([2, 1],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        (list(range(20)),),                                  # already sorted — zero inversions
        (list(range(20, 0, -1)),),                            # fully reversed — max inversions
        ([5] * 10,),                                          # all-equal — ties must not count
        ([1, 3, 2, 5, 4, 7, 6, 9, 8, 10],),                   # many adjacent-only swaps
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([2, 1],),          # smallest single inversion (merge step off-by-one trap)
        ([1, 3, 2],),        # inversion count = 1 hidden in the middle
        ([-1, -2, -3],),     # negative numbers, fully reversed
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


# ── fast-power: oracle(base, exp) ─────────────────────────────────────────────

def _to_input_fast_power(base, exp):
    return f"{base} {exp}"


def _plan_fast_power(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_fast_power

    def gen_small():
        return (rng.randint(1, 20), rng.randint(0, 50))

    def gen_stress():
        return (rng.randint(2, 20), rng.randint(250, 300))

    visible = [(2, 10), (3, 0), (5, 3), (7, 15), (2, 1)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        (1, 0), (1, 300), (20, 0), (1, 1),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        (20, 300),   # max base and max exp together
        (2, 300),    # small base, max exp — huge but exact bigint result
        (1, 299),    # base 1 across an odd exponent (tests squaring-branch parity)
        (19, 299),   # odd base and odd exponent together
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        (2, 2),    # smallest even exponent
        (2, 3),    # smallest odd exponent > 1 (catches missing odd-exponent multiply)
        (5, 1),    # exponent 1 — must return base itself, not 1
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


# ── karatsuba: oracle(a, b) ────────────────────────────────────────────────────

def _to_input_karatsuba(a, b):
    return f"{a} {b}"


def _plan_karatsuba(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_karatsuba

    def gen_small():
        return (rng.randint(0, 10_000), rng.randint(0, 10_000))

    def gen_stress():
        hi = 10**18
        return (rng.randint(0, hi), rng.randint(0, hi))

    visible = [
        (1234, 5678), (0, 100), (999, 999), (123456789, 987654321), (7, 8),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        (0, 0), (0, 10**18), (1, 1), (10**18, 10**18),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        (999999999, 999999999),      # repunit-ish, exercises many carries
        (10**9, 10**9 - 1),          # differing digit lengths near a power-of-ten split
        (100000000, 1),              # one operand a bare power of ten
        (123, 100000000000000),      # very different magnitudes (asymmetric split)
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        (9, 9),          # smallest case below any base-case split threshold
        (10, 10),        # smallest case that forces at least one split
        (99, 101),       # unequal digit lengths straddling a split boundary
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


# ── majority-element: oracle(nums) — guaranteed majority exists ──────────────

def _to_input_majority(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_majority_element(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_majority

    def _with_majority(n, lo, hi):
        maj_val = rng.randint(lo, hi)
        maj_count = n // 2 + 1
        rest_count = n - maj_count
        vals = [maj_val] * maj_count + tg.rand_int_array(rng, rest_count, lo, hi)
        rng.shuffle(vals)
        return vals

    def gen_small():
        n = rng.randint(1, 9)
        return (_with_majority(n, -20, 20),)

    def gen_stress():
        n = rng.randint(20_000, 50_000)
        return (_with_majority(n, -10**6, 10**6),)

    visible = [
        ([3, 2, 3],), ([2, 2, 1, 1, 1, 2, 2],), ([5],), ([1, 1, 1, 2, 2],),
        ([4, 4, 4, 4, 1],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([1],),
        ([1, 1],),
        ([0, 0, 1],),
        ([-1, -1, 2],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([1] * 6 + [2] * 5,),                     # bare-minimum majority (n//2 + 1)
        ([7, 1, 7, 2, 7, 3, 7],),                  # majority interleaved with distinct decoys
        ([5, 5, 5, 5, 5, 5, 5, 1, 2, 3, 4, 5, 6],),  # majority spread with many distinct others
        ([-5] * 4 + [5] * 3,),                     # negative majority value vs positive decoys
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 2, 1],),        # smallest odd-length majority (Boyer-Moore reset trap)
        ([2, 1, 2, 1, 2],),  # majority with alternating decoys
        ([1, 1, 2],),        # smallest even+1 case
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


# ── matrix-exponentiation: oracle(matrix, k, mod) ─────────────────────────────

def _to_input_matrix_pow(matrix, k, mod):
    n = len(matrix)
    lines = [f"{n} {k} {mod}"]
    lines += [_arr(row) for row in matrix]
    return "\n".join(lines)


def _rand_matrix(rng: random.Random, n: int, lo: int, hi: int) -> list[list[int]]:
    return [[rng.randint(lo, hi) for _ in range(n)] for _ in range(n)]


def _plan_matrix_exponentiation(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_matrix_pow
    mod_default = 1_000_000_007

    def gen_small():
        n = rng.randint(1, 4)
        k = rng.randint(0, 50)
        m = _rand_matrix(rng, n, -10, 10)
        return (m, k, mod_default)

    def gen_stress():
        # Kept modest: n<=8, k<=10^6 — well inside the 5s/test judge budget for
        # a pure-Python O(n^3 log k) reference implementation.
        n = rng.randint(6, 8)
        k = rng.randint(200_000, 1_000_000)
        m = _rand_matrix(rng, n, -5, 5)
        return (m, k, mod_default)

    visible = [
        ([[1, 1], [1, 0]], 0, 1000000007),
        ([[1, 1], [1, 0]], 10, 1000000007),
        ([[2]], 5, 1000000007),
        ([[2, 0], [0, 2]], 3, 100),
        ([[1, 2], [3, 4]], 2, 1000),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([[1]], 0, 2),               # 1x1, k=0 -> identity
        ([[5]], 1, 3),               # 1x1, k=1
        ([[0, 0], [0, 0]], 5, 7),    # all-zero matrix
        ([[1, 0], [0, 1]], 1000, 2), # identity matrix, mod=2
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([[1, 1], [1, 0]], 1_000_000_000, 1_000_000_007),  # classic Fibonacci matrix, huge k
        ([[-1, 0], [0, -1]], 7, 1000),                       # negative entries, odd exponent parity
        ([[3, 0, 0], [0, 3, 0], [0, 0, 3]], 20, 1_000_000_007),  # diagonal matrix — easy to over-simplify
        ([[1, 1, 0], [0, 1, 1], [0, 0, 1]], 15, 97),         # upper-triangular, small prime mod
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([[2, 0], [0, 2]], 1, 1000),   # k=1 must return matrix mod itself, not identity
        ([[2, 0], [0, 2]], 2, 1000),   # smallest even exponent > 0
        ([[2, 0], [0, 2]], 3, 1000),   # smallest odd exponent > 1
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


# ── median-of-medians: oracle(nums, k) — k-th smallest, 1-indexed ────────────

def _to_input_median_of_medians(nums, k):
    return f"{len(nums)} {_arr(nums)} {k}"


def _plan_median_of_medians(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_median_of_medians

    def gen_small():
        n = rng.randint(1, 9)
        nums = tg.rand_int_array(rng, n, -50, 50)
        k = rng.randint(1, n)
        return (nums, k)

    def gen_stress():
        n = rng.randint(20_000, 60_000)
        nums = tg.rand_int_array(rng, n, -10**6, 10**6)
        k = rng.randint(1, n)
        return (nums, k)

    visible = [
        ([7, 10, 4, 3, 20, 15], 3),
        ([7, 10, 4, 3, 20, 15], 1),
        ([5], 1),
        ([5, 4, 3, 2, 1], 5),
        ([1, 2, 3, 4, 5], 3),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([1], 1),
        ([1, 2], 1),
        ([1, 2], 2),
        ([9] * 5, 3),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        (list(range(20, 0, -1)), 1),          # reverse-sorted, ask for the smallest
        (list(range(20, 0, -1)), 20),         # reverse-sorted, ask for the largest
        ([3] * 15 + [1, 2],                   # heavy duplicates around the target rank
          8),
        (list(range(1, 26)), 13),             # exact-median request on sorted input
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([2, 1], 1),         # smallest pair, k=1 (off-by-one on 1-indexing)
        ([2, 1], 2),         # smallest pair, k=n
        ([1, 1, 1], 2),      # all-duplicates, middle rank
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


# ── polynomial-multiplication: oracle(a, b) — coefficient lists ──────────────

def _to_input_poly_mult(a, b):
    return f"{len(a)} {_arr(a)} {len(b)} {_arr(b)}"


def _plan_polynomial_multiplication(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_poly_mult

    def gen_small():
        na = rng.randint(1, 6)
        nb = rng.randint(1, 6)
        a = tg.rand_int_array(rng, na, -20, 20)
        b = tg.rand_int_array(rng, nb, -20, 20)
        return (a, b)

    def gen_stress():
        na = rng.randint(400, 1000)
        nb = rng.randint(400, 1000)
        a = tg.rand_int_array(rng, na, -1000, 1000)
        b = tg.rand_int_array(rng, nb, -1000, 1000)
        return (a, b)

    visible = [
        ([1, 2, 3], [0, 1]), ([1, 1], [1, 1]), ([5], [3]), ([0, 0], [1, 2]),
        ([2, -1, 3], [1, 1]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([0], [0]),
        ([1], [1]),
        ([0], [5]),
        ([-1], [-1]),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([1, 0, 0, 0, 1], [1, 0, 0, 0, -1]),   # sparse, cancellation-prone coefficients
        ([1000, -1000, 1000], [-1000, 1000, -1000]),  # sign alternation at extremes
        ([1] * 8, [1] * 8),                     # all-ones — every cross term contributes
        ([-1000] * 3, [1000] * 3),              # extreme magnitude in opposite signs
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 1], [1]),        # unequal lengths, b shorter (asymmetric split trap)
        ([1], [1, 1]),        # unequal lengths, a shorter
        ([1, 2], [3, 4]),     # smallest genuine 2x2 cross-multiplication
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


# ── strassen: oracle(A, B) — matrix product A (n x m) times B (m x p) ────────

def _to_input_strassen(a, b):
    n = len(a)
    m = len(a[0])
    p = len(b[0])
    lines = [f"{n} {m} {p}"]
    lines += [_arr(row) for row in a]
    lines += [_arr(row) for row in b]
    return "\n".join(lines)


def _rand_rect_matrix(rng: random.Random, rows: int, cols: int, lo: int, hi: int) -> list[list[int]]:
    return [[rng.randint(lo, hi) for _ in range(cols)] for _ in range(rows)]


def _plan_strassen(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_strassen

    def gen_small():
        n = rng.randint(1, 4)
        m = rng.randint(1, 4)
        p = rng.randint(1, 4)
        a = _rand_rect_matrix(rng, n, m, -10, 10)
        b = _rand_rect_matrix(rng, m, p, -10, 10)
        return (a, b)

    def gen_stress():
        # Kept modest: dims <= 12 (constraint allows up to 64) so 40 judge
        # subprocess invocations of the pure-Python O(n^3) reference solution
        # stay comfortably inside the per-test time budget.
        n = rng.randint(8, 12)
        m = rng.randint(8, 12)
        p = rng.randint(8, 12)
        a = _rand_rect_matrix(rng, n, m, -20, 20)
        b = _rand_rect_matrix(rng, m, p, -20, 20)
        return (a, b)

    visible = [
        ([[1, 2], [3, 4]], [[5, 6], [7, 8]]),
        ([[5]], [[3]]),
        ([[1, 0], [0, 1]], [[7], [9]]),
        ([[1], [1]], [[2, 3]]),
        ([[2, 0], [0, 2]], [[1, 2], [3, 4]]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([[0]], [[0]]),
        ([[1]], [[1]]),
        ([[1, 1, 1]], [[1], [1], [1]]),
        ([[0, 0], [0, 0]], [[0, 0], [0, 0]]),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([[1, 0], [0, 1], [1, 1]], [[2, 3], [4, 5]]),          # non-square 3x2 * 2x2
        ([[-1, -2], [-3, -4]], [[-5, -6], [-7, -8]]),           # all-negative entries
        ([[3, 0, 0], [0, 3, 0], [0, 0, 3]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),  # scaled-identity trap
        ([[1, 1], [1, 1], [1, 1]], [[1, 1, 1], [1, 1, 1]]),     # 3x2 * 2x3, all-ones dims mismatch check
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([[1, 2], [3, 4]], [[1, 0], [0, 1]]),   # identity on the right — should return A unchanged
        ([[1, 0], [0, 1]], [[1, 2], [3, 4]]),   # identity on the left — should return B unchanged
        ([[2, 3], [4, 5]], [[6, 7], [8, 9]]),   # smallest genuinely mixed 2x2 * 2x2 (Strassen's 7-mult path)
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


# ── registry ───────────────────────────────────────────────────────────────────

def _fmt_int_list(a) -> str:
    return " ".join(str(x) for x in a)


def _fmt_matrix(a) -> str:
    return "\n".join(" ".join(str(x) for x in row) for row in a)


DIVIDE_AND_CONQUER_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "closest-pair": (_to_input_closest_pair, str, _plan_closest_pair),
    "counting-inversions": (_to_input_inversions, str, _plan_counting_inversions),
    "fast-power": (_to_input_fast_power, str, _plan_fast_power),
    "karatsuba": (_to_input_karatsuba, str, _plan_karatsuba),
    "majority-element": (_to_input_majority, str, _plan_majority_element),
    "matrix-exponentiation": (_to_input_matrix_pow, _fmt_matrix, _plan_matrix_exponentiation),
    "median-of-medians": (_to_input_median_of_medians, str, _plan_median_of_medians),
    "polynomial-multiplication": (_to_input_poly_mult, _fmt_int_list, _plan_polynomial_multiplication),
    "strassen": (_to_input_strassen, _fmt_matrix, _plan_strassen),
}
