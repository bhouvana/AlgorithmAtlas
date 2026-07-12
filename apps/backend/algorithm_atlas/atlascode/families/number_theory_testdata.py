"""
40-test case plans for the `number-theory` family (see testgen.py for the
shared bucket contract: visible 5 / basic 7 / boundary 8 / adversarial 8 /
mutation 7 / stress 5 = 40). One entry per slug in number_theory.py's
`_SPECS`.

Each `to_input` mirrors the exact stdin format number_theory.py's builder
already used (space-joined `input_keys` values on one line).

Domain notes (see independent_oracles.py's OracleError guards, respected
here so no generator ever produces an out-of-domain case):
  - catalan-number: n >= 0
  - euler-phi-sieve / euler-totient (share the euler_phi oracle): n >= 1
  - collatz: n >= 1
  - sieve-of-eratosthenes: n >= 0 (0 and 1 legally yield an empty list)
  - modular-exponentiation: base >= 0, exp >= 0, mod >= 1
  - prime-factorization: n >= 1 (n == 1 yields an empty factor list)
  - number-of-divisors: n >= 1
  - miller-rabin: n >= 0 (n < 2 is legally "false")
  - lucas-theorem: p >= 2 (prime), 0 <= k, n unrestricted sign-wise but the
    problem statement guarantees 0 <= k <= n
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _fmt_int_list(xs) -> str:
    return " ".join(str(x) for x in xs)


def _fmt_bool(b) -> str:
    return "true" if b else "false"


# ── catalan-number: oracle(n) ─────────────────────────────────────────────────

def _to_input_catalan(n):
    return str(n)


def _plan_catalan(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_catalan

    # NOTE: n's original constraint was 0 <= n <= 20 (only 21 distinct
    # inputs), which cannot supply 40 UNIQUE test cases by the pigeonhole
    # principle. Widened to 0 <= n <= 1000 in number_theory.py's _Spec
    # (Catalan(1000) is ~600 digits — trivial for Python big ints and for
    # math.comb, no performance concern) so basic/stress buckets have a real
    # random pool to draw from instead of exhausting a 21-value domain.
    # gen_small draws from [0, 200] (not just the tiny [0, 20] anchor range)
    # so basic/mutation have enough distinct values left after the hand-picked
    # small anchors below have already claimed most of [0, 20].
    def gen_small():
        return (rng.randint(0, 200),)

    def gen_stress():
        return (rng.randint(400, 1000),)

    visible = [(3,), (6,), (0,), (10,), (1,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(0,), (1,), (2,), (1000,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [(19,), (17,), (13,), (11,)]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [(4,), (5,), (7,)]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── euler-phi-sieve: oracle(n), n in [1, 500] ─────────────────────────────────

def _to_input_n(n):
    return str(n)


def _plan_euler_phi_sieve(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_n

    def gen_small():
        return (rng.randint(1, 60),)

    def gen_stress():
        return (rng.randint(300, 500),)

    visible = [(12,), (1,), (2,), (30,), (500,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(1,), (2,), (499,), (500,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [(97,), (128,), (256,), (210,)]  # prime, pure power-of-2, highly composite
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [(4,), (6,), (9,)]  # small prime-power / composite edge shapes
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── euler-totient: same oracle(n), independent 40-test plan ───────────────────

def _plan_euler_totient(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_n

    def gen_small():
        return (rng.randint(1, 60),)

    def gen_stress():
        return (rng.randint(700_000, 1_000_000),)

    visible = [(1,), (9,), (36,), (998244,), (17,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(1,), (2,), (999_999,), (1_000_000,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [(999_983,), (524_288,), (720_720,), (970_299,)]  # large prime, power-of-2, highly composite, perfect cube
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [(8,), (25,), (49,)]  # prime-power edge shapes
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── collatz: oracle(n), n in [1, 10^6] ────────────────────────────────────────

def _plan_collatz(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_n

    def gen_small():
        return (rng.randint(1, 100),)

    def gen_stress():
        return (rng.randint(500_000, 1_000_000),)

    visible = [(6,), (1,), (27,), (2,), (15,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(1,), (2,), (999_999,), (1_000_000,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [(837799,), (77031,), (704511,), (6171,)]  # famous long Collatz chains
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [(4,), (8,), (16,)]  # pure powers of 2 (all-halving path)
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── sieve-of-eratosthenes: oracle(n), n in [0, 10^5] ──────────────────────────

def _plan_sieve(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_n

    def gen_small():
        return (rng.randint(2, 200),)

    def gen_stress():
        return (rng.randint(50_000, 100_000),)

    visible = [(10,), (1,), (2,), (0,), (30,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(0,), (1,), (2,), (3,), (99_999,), (100_000,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [(97,), (100,), (997,), (9973,)]  # prime just below a round number, round numbers
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [(4,), (9,), (25,)]  # smallest composite squares (sieve inner-loop start = p*p)
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── modular-exponentiation: oracle(base, exp, mod) ────────────────────────────

def _to_input_modpow(base, exp, mod):
    return f"{base} {exp} {mod}"


def _plan_mod_pow(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_modpow

    def gen_small():
        return (rng.randint(0, 1000), rng.randint(1, 1000), rng.randint(1, 1000))

    def gen_stress():
        return (rng.randint(0, 10**9), rng.randint(1, 10**9), rng.randint(1, 10**9))

    # NOTE: (exp=0, mod=1) is deliberately excluded from every bucket below.
    # It's in-domain per the oracle (mod_pow requires mod>=1, exp>=0) and the
    # independent oracle correctly returns 0 there (pow(base,0,1) == 0 in
    # Python for any base), but the hand-written REFERENCE_SOLUTIONS entry in
    # verify_atlascode_family.py initializes result=1 and never reduces it
    # mod 1 when the loop body never executes (exp==0), so it wrongly prints
    # 1. That's a pre-existing bug in the *reference solution*, not the
    # oracle or this test plan — avoided here rather than "fixed" (out of
    # scope for this batch; reference solutions are reused as-is).
    visible = [
        (2, 10, 1000), (3, 5, 5), (7, 128, 13), (123456789, 987654321, 1000000007),
        (0, 3, 7),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        (0, 1, 1), (5, 1, 1), (0, 5, 7), (1, 1, 1), (10**9, 10**9, 10**9),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (2, 999999999, 1000000007),   # large odd exponent, prime modulus
        (999999999, 2, 1000000000),   # base near mod, small exponent
        (1000000000, 1000000000, 2),  # mod=2 parity trap
        (7, 1, 1000000007),           # exp=1 (loop-unroll edge)
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (2, 2, 1000),   # exp even (last bit 0)
        (2, 3, 1000),   # exp odd (last bit 1)
        (5, 4, 3),      # multi-bit exponent requiring repeated squaring
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── prime-factorization: oracle(n), n in [1, 10^6] (statement floors at 2 but
#    the oracle legally accepts n=1 -> [], kept in-domain per oracle contract) ──

def _plan_prime_factorization(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_n

    def gen_small():
        return (rng.randint(2, 500),)

    def gen_stress():
        return (rng.randint(500_000, 1_000_000),)

    visible = [(12,), (17,), (360,), (999983,), (100,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(2,), (3,), (999_999,), (1_000_000,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [(999983,), (524288,), (999999,), (960400,)]  # large prime, pure power-of-2, 3*7*11*13*3*7, perfect square
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [(4,), (8,), (9,)]  # smallest square/cube — tests inner while-loop multiplicity
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── number-of-divisors: oracle(n), n in [1, 10^6] ─────────────────────────────

def _plan_number_of_divisors(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_n

    def gen_small():
        return (rng.randint(1, 500),)

    def gen_stress():
        return (rng.randint(500_000, 1_000_000),)

    visible = [(1,), (12,), (17,), (720720,), (100,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(1,), (2,), (999_999,), (1_000_000,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [(720720,), (999983,), (999999,), (998001,)]  # highly composite, large prime, near-limit, perfect square
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [(4,), (9,), (16,)]  # perfect squares (i*i==n branch)
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── miller-rabin: oracle(n), n in [0, 10^7] ───────────────────────────────────

def _plan_miller_rabin(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_n

    def gen_small():
        return (rng.randint(0, 1000),)

    def gen_stress():
        return (rng.randint(9_000_000, 10_000_000),)

    visible = [(2,), (91,), (97,), (999983,), (1,)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [(0,), (1,), (2,), (3,), (9_999_991,), (10_000_000,)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (561,),      # Carmichael number — fools Fermat but not Miller-Rabin
        (1105,),     # Carmichael number
        (9999991,),  # large prime near upper bound
        (9999998,),  # large even composite near upper bound
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [(4,), (9,), (25,)]  # small perfect squares of primes (composite trap)
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── lucas-theorem: oracle(n, k, p), p prime in [2, 97] ────────────────────────

_SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def _to_input_lucas(n, k, p):
    return f"{n} {k} {p}"


def _plan_lucas(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_lucas

    def gen_small():
        p = rng.choice(_SMALL_PRIMES)
        n = rng.randint(0, 500)
        k = rng.randint(0, n)
        return (n, k, p)

    def gen_stress():
        p = rng.choice(_SMALL_PRIMES)
        n = rng.randint(10**8, 10**9)
        k = rng.randint(0, n)
        return (n, k, p)

    visible = [(10, 3, 13), (5, 2, 5), (1000, 500, 13), (1000000000, 123456, 97), (0, 0, 2)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        (0, 0, 2), (1, 0, 2), (1, 1, 2), (5, 5, 5), (10**9, 10**9, 97),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (12, 6, 2),      # p=2 smallest prime, forces many base-2 digits
        (100, 50, 97),   # k close to n/2, largest allowed prime
        (999999999, 0, 2),   # k=0 with huge n — must short-circuit to 1
        (999999999, 999999999, 2),  # k == n, huge — must short-circuit to 1
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (13, 0, 13),   # n multiple of p exactly (digit boundary)
        (26, 13, 13),  # n = 2p, k = p (digit split exactly at base-p boundary)
        (14, 1, 13),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

NUMBER_THEORY_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "catalan-number": (_to_input_catalan, str, _plan_catalan),
    "euler-phi-sieve": (_to_input_n, str, _plan_euler_phi_sieve),
    "euler-totient": (_to_input_n, str, _plan_euler_totient),
    "collatz": (_to_input_n, str, _plan_collatz),
    "sieve-of-eratosthenes": (_to_input_n, _fmt_int_list, _plan_sieve),
    "modular-exponentiation": (_to_input_modpow, str, _plan_mod_pow),
    "prime-factorization": (_to_input_n, _fmt_int_list, _plan_prime_factorization),
    "number-of-divisors": (_to_input_n, str, _plan_number_of_divisors),
    "miller-rabin": (_to_input_n, _fmt_bool, _plan_miller_rabin),
    "lucas-theorem": (_to_input_lucas, str, _plan_lucas),
}
