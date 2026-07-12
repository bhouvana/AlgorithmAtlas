"""
40-test case plans for the `stack-variants` family (see testgen.py for the
shared bucket contract: visible 5 / basic 7 / boundary 8 / adversarial 8 /
mutation 7 / stress 5 = 40). One entry per slug in stack_variants.py's
`_SPECS`.

Each `to_input` mirrors the exact stdin format stack_variants.py's builder
already used (verified against the original hand-written `_Spec.cases`
before writing this).
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


def _fmt_int_list(xs) -> str:
    return " ".join(str(x) for x in xs)


def _fmt_bool(b) -> str:
    return "true" if b else "false"


# ── valid-parentheses: oracle(s), s in ()[]{}  only ───────────────────────────

def _to_input_str(s):
    return s


_BRACKET_ALPHABET = "()[]{}"


def _plan_valid_parentheses(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_str

    def _rand_bracket_string(n: int) -> str:
        return "".join(rng.choice(_BRACKET_ALPHABET) for _ in range(n))

    def _rand_balanced(depth: int) -> str:
        # Build a genuinely well-formed string by nesting/concatenating pairs.
        pairs = ["()", "[]", "{}"]
        parts = []
        for _ in range(depth):
            p = rng.choice(pairs)
            if parts and rng.random() < 0.5:
                parts[-1] = p[0] + parts[-1] + p[1]
            else:
                parts.append(p)
        return "".join(parts)

    def gen_small():
        if rng.random() < 0.5:
            return (_rand_balanced(rng.randint(1, 4)),)
        return (_rand_bracket_string(rng.randint(1, 8)),)

    def gen_stress():
        if rng.random() < 0.5:
            return (_rand_balanced(rng.randint(1000, 3000)),)
        return (_rand_bracket_string(rng.randint(2000, 6000)),)

    visible = [("()[]{}",), ("(]",), ("([)]",), ("{[]}",), ("(())",)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [("(",), (")",), ("()",), ("((",)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("((((((((((",),         # deeply nested opens, never closed
        ("))))))))))",),         # only closers
        ("()" * 20 + "]",),      # long valid prefix, single bad trailing char
        ("([{}])",),             # correctly nested mixed types
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("()()",),   # sequential (not nested) pairs — trips "always match last open" bugs
        ("([)]",),   # interleaved/crossed types — must fail despite balanced counts
        ("(]",),     # type mismatch on a single pair
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── daily-temperatures: oracle(temps) ─────────────────────────────────────────

def _to_input_int_array(nums):
    return f"{len(nums)} {_arr(nums)}"


def _plan_daily_temperatures(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_int_array

    def gen_small():
        n = rng.randint(1, 10)
        return (tg.rand_int_array(rng, n, 30, 100),)

    def gen_stress():
        n = rng.randint(50_000, 100_000)
        return (tg.rand_int_array(rng, n, 30, 100),)

    visible = [
        ([73, 74, 75, 71, 69, 72, 76, 73],), ([30, 40, 50, 60],), ([50],),
        ([60, 50, 40, 30],), ([55, 55, 55],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([50],), ([50, 50],), ([50, 51],), ([51, 50],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(100, 50, -1)),),      # strictly decreasing — every answer is 0
        (list(range(50, 100)),),          # strictly increasing — answer is always 1 (except last)
        ([50] * 20,),                      # all equal — no strictly warmer day exists
        ([60, 30, 60, 30, 60, 30, 90],),   # oscillating with a final spike
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([70, 70, 71],),   # equal values must NOT count as "warmer"
        ([80, 79, 80],),   # tie broken by exact next occurrence, not global max
        ([65, 70, 65, 75],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── next-greater-element: oracle(nums), non-circular ──────────────────────────

def _plan_next_greater_element(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_int_array

    def gen_small():
        n = rng.randint(1, 10)
        return (tg.rand_int_array(rng, n, -20, 20),)

    def gen_stress():
        n = rng.randint(50_000, 100_000)
        return (tg.rand_int_array(rng, n, -10_000, 10_000),)

    visible = [([4, 1, 2],), ([1, 3, 4, 2],), ([5],), ([2, 1, 3],), ([3, 3, 3],)]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([5],), ([5, 5],), ([5, 6],), ([6, 5],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(20, 0, -1)),),   # strictly decreasing — all -1
        (list(range(1, 21)),),       # strictly increasing — each is the next element
        ([5] * 15,),                  # all equal — all -1
        ([1, 3, 2, 4, 2, 5, 1],),     # mixed pattern with repeated values
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 2, 3],),  # equal-then-greater — must not treat equal as "greater"
        ([1, 2, 1],),  # middle spike, must pop stack correctly
        ([3, 1, 2],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── largest-rectangle-in-histogram: oracle(heights), heights[i] >= 0 ─────────

def _plan_largest_rectangle(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_int_array

    def gen_small():
        n = rng.randint(1, 10)
        return (tg.rand_int_array(rng, n, 0, 20),)

    def gen_stress():
        n = rng.randint(20_000, 50_000)
        return (tg.rand_int_array(rng, n, 0, 1_000_000),)

    visible = [
        ([2, 1, 5, 6, 2, 3],), ([2, 4],), ([5],), ([1, 1, 1, 1],), ([0, 0, 0],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([0],), ([1],), ([0, 0],), ([1, 1],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(1, 21)),),        # strictly increasing staircase
        (list(range(20, 0, -1)),),    # strictly decreasing staircase
        ([5, 1, 5, 1, 5, 1, 5],),     # alternating tall/short (classic trap)
        ([1_000_000] * 10,),           # uniformly tall — full-width rectangle
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 1, 2],),     # dip in the middle — must consider width across the dip
        ([6, 2, 5, 4, 5, 1, 6],),  # classic LeetCode example, many tie widths
        ([3, 3, 3],),     # uniform plateau — width == n
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── min-stack-simulation: oracle(ops), ops = [("PUSH", x) | ("POP", None)] ────

def _to_input_ops(ops):
    lines = [str(len(ops))]
    for op, val in ops:
        lines.append(f"{op} {val}" if val is not None else op)
    return "\n".join(lines)


def _rand_ops(rng: random.Random, n: int, lo: int = -50, hi: int = 50) -> list[tuple]:
    """A random op sequence guaranteed never to POP an empty stack."""
    ops = []
    depth = 0
    for _ in range(n):
        if depth == 0 or rng.random() < 0.7:
            ops.append(("PUSH", rng.randint(lo, hi)))
            depth += 1
        else:
            ops.append(("POP", None))
            depth -= 1
    return ops


def _plan_min_stack_simulate(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_ops

    def gen_small():
        n = rng.randint(1, 10)
        return (_rand_ops(rng, n),)

    def gen_stress():
        n = rng.randint(5000, 10_000)
        return (_rand_ops(rng, n, -1_000_000, 1_000_000),)

    visible = [
        ([("PUSH", 5), ("PUSH", 2), ("PUSH", 7), ("POP", None), ("PUSH", 1)],),
        ([("PUSH", 3), ("PUSH", 3)],),
        ([("PUSH", -1), ("PUSH", -2), ("PUSH", 0)],),
        ([("PUSH", 4), ("PUSH", 1), ("POP", None), ("PUSH", 2)],),
        ([("PUSH", 0)],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([("PUSH", 0)],),
        ([("PUSH", 1), ("POP", None), ("PUSH", 1)],),
        ([("PUSH", -50)],),
        ([("PUSH", 50)],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([("PUSH", i) for i in range(20, 0, -1)],),          # decreasing pushes — min updates every time
        ([("PUSH", i) for i in range(1, 21)],),               # increasing pushes — min never changes after first
        ([("PUSH", 5), ("PUSH", -5), ("POP", None), ("PUSH", -5), ("POP", None), ("PUSH", 5)],),  # min re-derived after pops
        ([("PUSH", 1)] * 10,),                                  # repeated identical value
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([("PUSH", 3), ("PUSH", 1), ("POP", None), ("PUSH", 2)],),  # min must "pop back" to a prior value correctly
        ([("PUSH", -1), ("PUSH", -1), ("POP", None)],),              # duplicate minimums, one popped
        ([("PUSH", 2), ("PUSH", 0), ("PUSH", 3), ("POP", None), ("POP", None)],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── evaluate-reverse-polish-notation: oracle(tokens) ──────────────────────────

def _to_input_tokens(tokens):
    return f"{len(tokens)} {' '.join(tokens)}"


def _rand_rpn(rng: random.Random, n_numbers: int) -> list[str]:
    """Build a valid RPN expression with exactly n_numbers operands via a
    random binary-tree-shaped composition (avoids division by zero)."""
    if n_numbers == 1:
        return [str(rng.randint(-20, 20) or 1)]
    split = rng.randint(1, n_numbers - 1)
    left = _rand_rpn(rng, split)
    right = _rand_rpn(rng, n_numbers - split)
    op = rng.choice(["+", "-", "*", "/"])
    if op == "/":
        # guarantee non-zero divisor by forcing the right subtree to a literal
        right = [str(rng.choice([1, 2, 3, 4, 5, -1, -2]))]
    return left + right + [op]


def _plan_evaluate_rpn(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_tokens

    def gen_small():
        n = rng.randint(1, 6)
        return (_rand_rpn(rng, n),)

    def gen_stress():
        n = rng.randint(2000, 5000)
        return (_rand_rpn(rng, n),)

    visible = [
        (["2", "1", "+", "3", "*"],), (["4", "13", "5", "/", "+"],), (["5"],),
        (["10", "2", "/"],), (["3", "4", "+"],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        (["0"],), (["1"],), (["-1"],), (["1", "1", "+"],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (["7", "2", "/"],),          # truncation toward zero, positive operands
        (["-7", "2", "/"],),         # truncation toward zero with a negative dividend
        (["10", "3", "-", "2", "*"],),   # chained ops, order sensitivity
        (["4", "2", "3", "*", "-"],),    # operator precedence only via RPN order
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (["4", "3", "-"],),   # subtraction operand order (a-b, not b-a)
        (["4", "3", "/"],),   # division operand order (a/b, not b/a)
        (["2", "3", "4", "*", "+"],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── remove-k-digits: oracle(num, k), 0 <= k <= len(num) ───────────────────────

def _to_input_num_k(num, k):
    return f"{num} {k}"


def _plan_remove_k_digits(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_num_k

    def gen_small():
        n = rng.randint(1, 10)
        num = "".join(str(rng.randint(0, 9)) for _ in range(n))
        if num[0] == "0" and n > 1:
            num = str(rng.randint(1, 9)) + num[1:]
        k = rng.randint(0, n)
        return (num, k)

    def gen_stress():
        n = rng.randint(20_000, 50_000)
        num = "".join(str(rng.randint(0, 9)) for _ in range(n))
        if num[0] == "0":
            num = str(rng.randint(1, 9)) + num[1:]
        k = rng.randint(0, n)
        return (num, k)

    visible = [
        ("1432219", 3), ("10200", 1), ("10", 2), ("9", 1), ("112", 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("1", 0), ("1", 1), ("9", 0), ("10", 1),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("9" * 10, 5),          # all-same-digit — result should just be shorter
        ("1" + "0" * 9, 1),     # leading digit removed exposes leading zeros to strip
        ("123456789", 9),        # k == length — remaining result must be "0"
        ("100000000", 1),        # removing the leading 1 exposes all-zero remainder
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("112", 1),      # must remove the LAST descending digit, not just any
        ("1173", 2),      # multiple pops in sequence needed
        ("10", 1),        # leading-zero stripping after single removal
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── trapping-rain-water: oracle(heights), heights[i] >= 0 ─────────────────────

def _plan_trapping_rain_water(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_int_array

    def gen_small():
        n = rng.randint(1, 10)
        return (tg.rand_int_array(rng, n, 0, 10),)

    def gen_stress():
        n = rng.randint(20_000, 50_000)
        return (tg.rand_int_array(rng, n, 0, 1_000_000),)

    visible = [
        ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],), ([4, 2, 0, 3, 2, 5],), ([5],),
        ([3, 0, 3],), ([0, 0, 0],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([0],), ([5],), ([0, 0],), ([1, 0],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (list(range(1, 21)),),        # strictly increasing — traps nothing
        (list(range(20, 0, -1)),),    # strictly decreasing — traps nothing
        ([5, 0, 0, 0, 0, 5],),        # a deep basin between two tall walls
        ([1_000_000, 0, 1_000_000],),  # huge single-unit-wide basin
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 0, 2],),           # symmetric single-cell basin
        ([3, 1, 2, 1, 3],),     # two-sided pointer must use min(left_max,right_max)
        ([4, 1, 1, 1, 4],),     # flat basin floor of width > 1
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

STACK_VARIANT_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "valid-parentheses": (_to_input_str, _fmt_bool, _plan_valid_parentheses),
    "daily-temperatures": (_to_input_int_array, _fmt_int_list, _plan_daily_temperatures),
    "next-greater-element": (_to_input_int_array, _fmt_int_list, _plan_next_greater_element),
    "largest-rectangle-in-histogram": (_to_input_int_array, str, _plan_largest_rectangle),
    "min-stack-simulation": (_to_input_ops, _fmt_int_list, _plan_min_stack_simulate),
    "evaluate-reverse-polish-notation": (_to_input_tokens, str, _plan_evaluate_rpn),
    "remove-k-digits": (_to_input_num_k, str, _plan_remove_k_digits),
    "trapping-rain-water": (_to_input_int_array, str, _plan_trapping_rain_water),
}
