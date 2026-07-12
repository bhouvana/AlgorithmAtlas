"""
40-test case plans for the `greedy` family (see testgen.py for the shared
bucket contract: visible 5 / basic 7 / boundary 8 / adversarial 8 /
mutation 7 / stress 5 = 40). One entry per slug in greedy.py's `_SPECS`.

Each `to_input` mirrors the exact stdin format the original hand-written
`_Spec.cases` already used (verified against greedy.py before writing this).
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _fmt(*parts: object) -> str:
    return " ".join(str(p) for p in parts)


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


# ── activity-selection: oracle(starts, ends) ──────────────────────────────────

def _to_input_activity(starts, ends):
    return f"{len(starts)} {_arr(starts)} {_arr(ends)}"


def _plan_activity(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_activity

    def gen_random_small():
        n = rng.randint(3, 6)
        s, e = tg.interval_patterns(rng, n, 0, 30)["random"]
        return (s, e)

    def gen_random_stress():
        n = rng.randint(500, 2000)
        s, e = tg.interval_patterns(rng, n, 0, 10_000)["random"]
        return (s, e)

    visible = [
        ([1, 3, 0, 5, 8, 5], [2, 4, 6, 7, 9, 9]),
        ([1, 2, 3], [2, 3, 4]),
        ([5], [10]),
        ([1, 1, 1, 1], [2, 2, 2, 2]),
        ([1, 4, 7], [2, 5, 8]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_random_small, ti, seen)

    boundary_anchors = [
        ([0], [1]),
        ([0, 5], [5, 10]),  # touching exactly
        ([0, 0, 0], [1, 1, 1]),
        ([0, 1, 2, 3, 4], [1, 2, 3, 4, 5]),  # chain of touching
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(
        8 - len(boundary_anchors), gen_random_small, ti, seen
    )

    adversarial_anchors = [
        ([0, 0, 0, 0], [100, 3, 3, 3]),  # one huge interval vs many short
        (list(range(9, -1, -1)), list(range(10, 20))),  # reverse-sorted starts
        ([-5, -3, -1], [0, 2, 4]),  # negative values
        ([0, 2, 4, 6, 8], [10, 3, 5, 7, 9]),  # end-time ties/near-ties mixed order
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(
        8 - len(adversarial_anchors), gen_random_stress, ti, seen
    )

    mutation_anchors = [
        ([0, 3, 6], [3, 6, 9]),  # exact touching chain len 3
        ([0, 2, 4, 6], [2, 4, 6, 8]),  # exact touching chain len 4
        ([0, 1], [1, 2]),  # minimal touching pair (>= vs > boundary)
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(
        7 - len(mutation_anchors), gen_random_small, ti, seen
    )

    stress = tg.fill_unique(5, gen_random_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


# ── fractional-knapsack: oracle(weights, values, capacity) ────────────────────

def _to_input_knapsack(weights, values, capacity):
    return f"{len(weights)} {_arr(weights)} {_arr(values)} {capacity}"


def _plan_fractional_knapsack(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_knapsack

    def gen_small():
        n = rng.randint(2, 6)
        w = tg.rand_int_array(rng, n, 1, 50)
        v = tg.rand_int_array(rng, n, 0, 100)
        cap = rng.randint(0, 100)
        return (w, v, cap)

    def gen_stress():
        n = rng.randint(200, 1000)
        w = tg.rand_int_array(rng, n, 1, 1000)
        v = tg.rand_int_array(rng, n, 0, 1000)
        cap = rng.randint(1000, 100_000)
        return (w, v, cap)

    visible = [
        ([10, 20, 30], [60, 100, 120], 50),
        ([10], [60], 20),
        ([5, 5], [10, 10], 0),
        ([2, 3, 4], [10, 15, 20], 5),
        ([1, 1, 1], [1, 2, 3], 2),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1], [1], 0),
        ([1], [100], 1),
        ([100], [1], 1000),
        ([1, 1], [0, 0], 5),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 1000], [1, 1], 1),   # tiny high-ratio item vs huge low-ratio item
        ([1000, 1], [1, 1000], 1),  # ratio ordering reversed
        ([10, 10, 10], [10, 20, 30], 10),  # ties broken only by which item picked
        ([1, 2, 3, 4], [4, 3, 2, 1], 5),  # inversely correlated weight/value
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([5, 5], [10, 10], 5),   # equal ratio items — exact-half take
        ([1, 2], [2, 2], 3),     # capacity exactly fits both
        ([4], [8], 3),           # partial take on the only item
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── gas-station: oracle(gas, cost) ────────────────────────────────────────────

def _to_input_gas(gas, cost):
    return f"{len(gas)} {_arr(gas)} {_arr(cost)}"


def _plan_gas_station(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_gas

    def gen_small():
        n = rng.randint(3, 6)
        return (tg.rand_int_array(rng, n, 0, 10), tg.rand_int_array(rng, n, 0, 10))

    def gen_stress():
        n = rng.randint(1000, 5000)
        return (tg.rand_int_array(rng, n, 0, 100), tg.rand_int_array(rng, n, 0, 100))

    visible = [
        ([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]),
        ([2, 3, 4], [3, 4, 3]),
        ([5], [5]),
        ([1, 1], [2, 2]),
        ([4, 5, 6], [3, 4, 5]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([0], [0]),
        ([1], [0]),
        ([0], [1]),
        ([3, 3, 3], [3, 3, 3]),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 0, 0, 0, 5], [0, 1, 1, 1, 1]),  # exact-total-feasible with a mid dip
        ([0, 0, 0, 10], [1, 1, 1, 0]),        # deficit until last station
        ([5, 1, 2, 3, 4], [4, 5, 1, 2, 3]),   # start index must wrap
        ([2, 2, 2, 2], [1, 1, 1, 10]),        # feasible except one huge cost
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 2, 3], [3, 2, 1]),   # tank dips negative then recovers (tests reset-on-negative)
        ([0, 0, 5], [1, 1, 0]),   # deficit only at index 0
        ([10, 0, 0], [0, 5, 5]),  # deficit only at the wrap point
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── huffman-coding: oracle(freqs) ─────────────────────────────────────────────

def _to_input_huffman(freqs):
    return f"{len(freqs)} {_arr(freqs)}"


def _plan_huffman(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_huffman

    def gen_small():
        n = rng.randint(2, 8)
        return (tg.rand_int_array(rng, n, 1, 100),)

    def gen_stress():
        n = rng.randint(300, 1000)
        return (tg.rand_int_array(rng, n, 1, 1_000_000),)

    visible = [
        ([5, 9, 12, 13, 16, 45],), ([1, 1],), ([1, 100],), ([1, 1, 1, 1],),
        ([2, 3, 5, 7, 11],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1, 2],), ([1, 1_000_000],), ([3, 3, 3],), ([1000000, 1000000],)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 1, 1, 1, 1, 1, 1, 1],),      # all-equal — many tie-breaks during merges
        ([1, 2, 4, 8, 16, 32],),           # powers of two, skewed merges
        ([50, 1, 1, 1, 1, 1, 1, 1, 1],),   # one dominant symbol
        ([1, 1, 2, 3, 5, 8, 13],),         # fibonacci-ish, easy to mis-tie-break
    ]
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([1, 1, 1],),   # smallest valid odd-count merge chain
        ([2, 2],),      # two equal — single merge
        ([1, 2, 3],),
    ]
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── job-scheduling: oracle(deadlines, profits) ────────────────────────────────

def _to_input_job(deadlines, profits):
    return f"{len(deadlines)} {_arr(deadlines)} {_arr(profits)}"


def _plan_job_scheduling(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_job

    def gen_small():
        n = rng.randint(2, 6)
        d = tg.rand_int_array(rng, n, 1, n)
        p = tg.rand_int_array(rng, n, 0, 100)
        return (d, p)

    def gen_stress():
        n = rng.randint(300, 1000)
        d = tg.rand_int_array(rng, n, 1, n)
        p = tg.rand_int_array(rng, n, 0, 10_000)
        return (d, p)

    visible = [
        ([2, 1, 2, 1, 3], [100, 19, 27, 25, 15]),
        ([1, 1, 1], [5, 3, 8]),
        ([1], [10]),
        ([1, 1], [10, 20]),
        ([3, 1, 2], [50, 10, 40]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([1], [0]), ([1, 1, 1, 1], [1, 1, 1, 1]), ([4, 4, 4], [1, 2, 3]), ([1, 2, 3, 4], [1, 1, 1, 1]),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([1, 1, 1, 1, 1], [5, 4, 3, 2, 1]),   # all same deadline, only one slot exists
        ([5, 1, 1, 1, 1, 1], [1, 100, 99, 98, 97, 96]),  # one loose deadline, rest crammed
        ([2, 2, 1, 1], [10, 20, 30, 40]),      # highest profit has tightest deadline
        (list(range(1, 6)), [1, 1, 1, 1, 100]),  # last job most valuable, latest deadline
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 2], [10, 20]),   # tie deadline, must keep higher profit
        ([1, 2], [20, 10]),
        ([3, 3, 3], [5, 5, 5]),  # all-tied profits and deadlines
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── meeting-rooms: oracle(starts, ends) — same shape as activity-selection ────

def _to_input_meetings(starts, ends):
    return f"{len(starts)} {_arr(starts)} {_arr(ends)}"


def _plan_meeting_rooms(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_meetings

    def gen_small():
        n = rng.randint(2, 6)
        return tg.interval_patterns(rng, n, 0, 30)["random"]

    def gen_stress():
        n = rng.randint(1000, 3000)
        return tg.interval_patterns(rng, n, 0, 50_000)["random"]

    visible = [
        ([0, 5, 15], [10, 20, 30]),
        ([7, 7, 7], [10, 10, 10]),
        ([1], [2]),
        ([1, 2], [2, 3]),
        ([0, 10, 20], [5, 15, 25]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([0], [1]), ([0, 0], [1, 1]), ([1, 2, 3, 4], [2, 3, 4, 5]), ([5, 5, 5, 5], [6, 6, 6, 6]),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([0, 1, 2, 3, 4], [100, 100, 100, 100, 100]),  # all overlap at the end
        ([0, 0, 0, 0, 0], [1, 2, 3, 4, 5]),             # all start together, stagger ends
        (list(range(10)), [x + 1 for x in range(10)]),  # touching chain — needs 1 room
        ([0, 5, 0, 5, 0], [5, 10, 5, 10, 5]),           # two interleaved groups
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([0, 1], [1, 2]),   # touching pair: needs 1 room, not 2
        ([0, 0], [1, 1]),   # exact overlap: needs 2 rooms
        ([1, 2, 3], [2, 3, 4]),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── stable-matching: oracle(men_prefs, women_prefs) ───────────────────────────

def _to_input_stable(men_prefs, women_prefs):
    n = len(men_prefs)
    lines = [str(n)]
    lines += [_arr(p) for p in men_prefs]
    lines += [_arr(p) for p in women_prefs]
    return "\n".join(lines)


def _rand_prefs(rng: random.Random, n: int) -> list[list[int]]:
    return [tg.rand_permutation(rng, n) for _ in range(n)]


def _plan_stable_matching(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_stable

    def gen_small():
        n = rng.randint(2, 4)
        return (_rand_prefs(rng, n), _rand_prefs(rng, n))

    def gen_stress():
        n = rng.randint(60, 100)
        return (_rand_prefs(rng, n), _rand_prefs(rng, n))

    visible = [
        ([[0, 1, 2], [1, 0, 2], [2, 0, 1]], [[1, 0, 2], [2, 1, 0], [0, 1, 2]]),
        ([[0]], [[0]]),
        ([[0, 1], [0, 1]], [[0, 1], [0, 1]]),
        ([[1, 0], [0, 1]], [[1, 0], [0, 1]]),
        ([[0, 1, 2], [0, 1, 2], [0, 1, 2]], [[0, 1, 2], [0, 1, 2], [0, 1, 2]]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([[0]], [[0]]),
        ([[0, 1], [1, 0]], [[0, 1], [1, 0]]),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        # everyone shares identical preferences — tests tie-break stability
        ([[0, 1, 2, 3]] * 4, [[0, 1, 2, 3]] * 4),
        # men's top choices form a cycle (0->1->2->0)
        ([[1, 2, 0], [2, 0, 1], [0, 1, 2]], [[0, 1, 2], [1, 2, 0], [2, 0, 1]]),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([[0, 1], [0, 1]], [[1, 0], [1, 0]]),
        ([[1, 0], [1, 0]], [[0, 1], [0, 1]]),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── task-scheduler: oracle(task_counts, cooldown) ─────────────────────────────

def _to_input_task(counts, cooldown):
    return f"{len(counts)} {_arr(counts)} {cooldown}"


def _plan_task_scheduler(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_task

    def gen_small():
        n = rng.randint(1, 6)
        return (tg.rand_int_array(rng, n, 1, 10), rng.randint(0, 5))

    def gen_stress():
        n = rng.randint(20, 26)
        return (tg.rand_int_array(rng, n, 1, 100), rng.randint(0, 100))

    visible = [
        ([3, 3], 2), ([1, 1, 1], 0), ([3, 3, 3, 1], 2), ([3, 3, 3], 3), ([1], 5),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [([1], 0), ([1], 100), ([100], 0), ([1, 1], 0)]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([10, 1, 1, 1, 1, 1, 1, 1, 1, 1], 1),  # one dominant task type forces idles
        ([5, 5, 5, 5, 5], 0),                    # no cooldown — total tasks is the answer
        ([2, 2, 2], 10),                          # huge cooldown relative to counts
        ([10] * 5, 4),                            # multiple tied max-count types
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([2, 1], 1),   # cooldown formula vs total-tasks formula crossover point
        ([3, 1], 2),
        ([2, 2, 1], 2),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

GREEDY_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "activity-selection": (_to_input_activity, str, _plan_activity),
    "fractional-knapsack": (_to_input_knapsack, lambda a: f"{a:.2f}", _plan_fractional_knapsack),
    "gas-station": (_to_input_gas, str, _plan_gas_station),
    "huffman-coding": (_to_input_huffman, str, _plan_huffman),
    "job-scheduling": (_to_input_job, str, _plan_job_scheduling),
    "meeting-rooms": (_to_input_meetings, str, _plan_meeting_rooms),
    "stable-matching": (_to_input_stable, lambda a: " ".join(map(str, a)), _plan_stable_matching),
    "task-scheduler": (_to_input_task, str, _plan_task_scheduler),
}
