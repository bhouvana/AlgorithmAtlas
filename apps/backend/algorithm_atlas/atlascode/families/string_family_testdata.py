"""
40-test case plans for the `string` family (see testgen.py for the shared
bucket contract: visible 5 / basic 7 / boundary 8 / adversarial 8 /
mutation 7 / stress 5 = 40). One entry per slug in string_family.py's
`_SPECS`.

Each `to_input` mirrors the exact stdin format the original hand-written
`_Spec.cases` already used (verified against string_family.py and the
reference/wrong solutions registered in scripts/verify_atlascode_family.py).

Stress-bucket sizes are deliberately kept well under each problem's stated
constraint because several REGISTERED REFERENCE solutions (used for the
verify script's smoke test, not just the independent oracle) are naive
O(n^2)/O(n^2 log n) implementations that would blow the judge's 5s/test
timeout at constraint-scale input on an all-same-character worst case:
  - `z-algorithm`'s reference is a naive O(n^2) double loop (all-same-char
    worst case) -> stress n capped around 1000-1200.
  - `longest-common-substring`'s reference is O(n*m) with an O(n) inner
    while-loop -> O(n^3) on an all-same-char/low-alphabet worst case ->
    stress n capped low (~250-350) AND given a 2-3 char alphabet (never
    single-repeated-char) to avoid the cubic blowup entirely.
  - `longest-palindromic-substring` / `manacher` references are O(n^2)
    substring+reverse scans -> stress n capped around 600-900.
  - `suffix-array`'s reference sorts with a slice-based key; empirically
    fast even at several thousand chars (Python's C-level string compare
    short-circuits), but still capped near the stated 1000 constraint.
  - `run-length-encoding` / `string-hashing` references are linear/rolling
    and can safely use much larger n.
"""
from __future__ import annotations

import random

from .. import testgen as tg


# ── z-algorithm: oracle(s) ────────────────────────────────────────────────────

def _to_input_s(s):
    return s


def _plan_z_algorithm(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_s

    def gen_small():
        n = rng.randint(1, 12)
        return (tg.rand_string(rng, n, "ab"),)

    def gen_stress():
        n = rng.randint(900, 1100)
        return (tg.rand_string(rng, n, "ab"),)

    visible = [
        ("aabcaabxaaz",), ("aaaa",), ("a",), ("abcabc",), ("aabaaab",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("a",), ("aa",), ("ab",), ("z",)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("a" * 30,),                          # all-same-char — every Z-value maximal, extend-loop trap
        ("ababababab",),                       # periodic pattern — Z-box reuse trap
        ("aaaaab",),                            # long run then a break
        ("abcdefghij",),                        # all-distinct — every Z-value is 0
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aaa",),      # Z = [0,2,1] — off-by-one extend trap
        ("aaaa",),     # Z = [0,3,2,1]
        ("abab",),     # Z = [0,0,2,0] — partial-prefix match trap
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── longest-common-substring: oracle(s1, s2) ──────────────────────────────────

def _to_input_two_strings(s1, s2):
    return f"{s1}\n{s2}"


def _plan_lcs(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_two_strings

    def gen_small():
        n1, n2 = rng.randint(1, 10), rng.randint(1, 10)
        return (tg.rand_string(rng, n1, "abc"), tg.rand_string(rng, n2, "abc"))

    def gen_stress():
        # Kept well below the low-alphabet cubic-worst-case danger zone for
        # the registered O(n*m) reference solution (see module docstring).
        n1, n2 = rng.randint(250, 320), rng.randint(250, 320)
        return (tg.rand_string(rng, n1, "abc"), tg.rand_string(rng, n2, "abc"))

    visible = [
        ("abcdef", "zabcf"), ("abc", "def"), ("a", "a"), ("aabbcc", "bbccdd"), ("hello", "yellow"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("a", "a"), ("a", "b"), ("a", "aa"), ("ab", "ba")]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("aaaa", "aaaa"),                     # identical strings, entirely overlapping
        ("abcxyz", "xyzabc"),                 # common substring only in the MIDDLE of one, edge of the other
        ("abcdefgh", "hgfedcba"),             # shared characters but reversed order — only length-1 common
        ("aaabaaa", "aaacaaa"),               # near-identical with a single differing character splitting the match
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("abcabc", "cabcab"),   # multiple overlapping candidate substrings, must pick the longest
        ("xyzab", "abxyz"),      # common substring straddles a rotation boundary
        ("aab", "ab"),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── longest-palindromic-substring: oracle(s) ──────────────────────────────────

def _plan_lps(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_s

    def gen_small():
        n = rng.randint(1, 12)
        return (tg.rand_string(rng, n, "ab"),)

    def gen_stress():
        n = rng.randint(550, 700)
        return (tg.rand_string(rng, n, "ab"),)

    visible = [
        ("babad",), ("cbbd",), ("a",), ("racecarxyz",), ("abacdfgdcaba",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("a",), ("aa",), ("ab",), ("aba",)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("a" * 25,),                          # all-same-char — the whole string is the palindrome
        ("ab" * 15,),                          # no palindrome longer than 2
        ("abcbaabcba",),                        # two overlapping palindromic candidates of equal length
        ("aabbbaa",),                            # even-center AND odd-center palindromes both present
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aa",),        # even-length palindrome — center-expansion off-by-one trap
        ("aba",),       # odd-length palindrome
        ("abba",),      # even-length, length-4 palindrome
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── manacher: oracle(s) — counts ALL palindromic substrings ───────────────────

def _plan_manacher(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_s

    def gen_small():
        n = rng.randint(0, 10)
        return (tg.rand_string(rng, n, "ab"),)

    def gen_stress():
        n = rng.randint(750, 900)
        return (tg.rand_string(rng, n, "ab"),)

    visible = [
        ("abc",), ("aaa",), ("",), ("aba",), ("abab",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("",), ("a",), ("aa",), ("ab",)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("a" * 20,),                           # all-same — max possible count for this length
        ("ab" * 12,),                           # minimal count — only single-char palindromes
        ("aabaa",),                              # nested odd + even palindromic centers
        ("abccba",),                             # single large even-length palindrome plus small ones
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aa",),      # even-length count — 3 total ('a','a','aa')
        ("aaa",),     # 6 total — undercount trap for length-2-only checkers
        ("aba",),     # 4 total: 'a','b','a','aba'
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── run-length-encoding: oracle(s) ────────────────────────────────────────────

def _plan_rle(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_s

    def gen_small():
        n = rng.randint(0, 12)
        return (tg.rand_string(rng, n, "abc"),)

    def gen_stress():
        n = rng.randint(20_000, 40_000)
        return (tg.rand_string(rng, n, "abcde"),)

    visible = [
        ("aaabbc",), ("a",), ("",), ("aabbccddeeff",), ("aaaabbbcc",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("",), ("a",), ("aa",), ("ab",)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("a" * 25,),                            # single giant run — count must exceed a single digit
        ("abababab",),                            # no runs longer than 1 — output nearly as long as input
        ("aabbaabbaabb",),                         # repeating multi-char block, runs never merge across blocks
        ("zzzzzzzzzzzzzzzzzzzz" + "y",),           # long run then a lone differing tail character
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aabb",),     # two equal-length runs — run-boundary off-by-one trap
        ("aaab",),      # unequal run lengths adjacent
        ("a",),         # single-char run, count must still print "1a" not just "a"
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── suffix-array: oracle(s) ───────────────────────────────────────────────────
# NOTE: the oracle raises OracleError on an empty string — every case needs
# len(s) >= 1.

def _plan_suffix_array(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_s

    def gen_small():
        n = rng.randint(1, 12)
        return (tg.rand_string(rng, n, "abc"),)

    def gen_stress():
        n = rng.randint(800, 950)
        return (tg.rand_string(rng, n, "abc"),)

    visible = [
        ("banana",), ("abc",), ("a",), ("aaaa",), ("abcabc",),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("a",), ("aa",), ("ab",), ("ba",)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("a" * 20,),                          # all-same-char — suffix order is purely by length (descending)
        ("".join(chr(ord("a") + i % 3) for i in range(20)),),  # periodic pattern, many close comparisons
        ("zyxwvutsrqponmlkjihg",),              # strictly descending alphabet — reverse of natural sort
        ("abcdefghijklmnopqrst",),               # strictly ascending alphabet — matches natural index order
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aab",),      # short prefix-sharing suffixes — tie-break by remaining length
        ("aba",),       # overlapping repeated pattern
        ("aa",),        # minimal all-same case
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── string-hashing: oracle(s, k) ──────────────────────────────────────────────
# NOTE: the oracle raises OracleError unless 1 <= k <= len(s).

def _to_input_string_k(s, k):
    return f"{s} {k}"


def _plan_string_hashing(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_string_k

    def gen_small():
        n = rng.randint(1, 12)
        s = tg.rand_string(rng, n, "abc")
        k = rng.randint(1, n)
        return (s, k)

    def gen_stress():
        n = rng.randint(2500, 3500)
        s = tg.rand_string(rng, n, "abcd")
        k = rng.randint(1, min(n, 50))
        return (s, k)

    visible = [
        ("aabcaab", 2), ("aaaa", 1), ("abcabc", 3), ("a", 1), ("aabb", 2),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("a", 1), ("ab", 1), ("ab", 2), ("aaa", 3)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("a" * 20, 5),                          # all-same-char — every length-5 substring is identical, answer=1
        ("abcabcabcabc", 3),                     # periodic pattern — few distinct substrings despite many positions
        ("abababababab", 2),                     # period-2 pattern, distinct count stays tiny
        ("".join(chr(ord("a") + i % 4) for i in range(20)), 4),  # period-4 pattern, tests hash-collision robustness
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("aaaa", 2),    # k=2 over all-same-char — must count DISTINCT (1), not total positions (3)
        ("abab", 2),    # exactly 2 distinct length-2 substrings ('ab','ba')
        ("aabb", 1),    # k=1 — distinct single characters
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

STRING_FAMILY_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "z-algorithm": (_to_input_s, lambda a: " ".join(map(str, a)), _plan_z_algorithm),
    "longest-common-substring": (_to_input_two_strings, str, _plan_lcs),
    "longest-palindromic-substring": (_to_input_s, str, _plan_lps),
    "manacher": (_to_input_s, str, _plan_manacher),
    "run-length-encoding": (_to_input_s, str, _plan_rle),
    "suffix-array": (_to_input_s, lambda a: " ".join(map(str, a)), _plan_suffix_array),
    "string-hashing": (_to_input_string_k, str, _plan_string_hashing),
}
