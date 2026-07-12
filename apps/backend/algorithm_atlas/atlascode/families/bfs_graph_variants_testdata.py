"""
40-test case plans for the `bfs-graph-variants` family (see testgen.py for
the shared bucket contract: visible 5 / basic 7 / boundary 8 / adversarial 8
/ mutation 7 / stress 5 = 40). One entry per slug in bfs_graph_variants.py's
`_SPECS`.

Each `to_input` mirrors the exact stdin format the original hand-written
`_Spec.cases` already used (verified against bfs_graph_variants.py and the
reference solutions in scripts/verify_atlascode_family.py before writing
this). Grid problems use `rows cols` header + row-per-line body (matching
`_grid_input`); edge-list problems (`is-bipartite`) use `n m` header +
one `u v` per line (matching its existing cases); `word-ladder-length` and
`minimum-knight-moves` use their own simple line/token formats.
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _arr(xs) -> str:
    return " ".join(str(x) for x in xs)


def _grid_input(rows: list[list[int]]) -> str:
    return f"{len(rows)} {len(rows[0])}\n" + "\n".join(" ".join(map(str, r)) for r in rows)


# ── rotten-oranges-minutes: oracle(grid); cells in {0,1,2} ────────────────────

def _plan_rotten_oranges(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _grid_input

    def gen_small():
        rows = rng.randint(1, 5)
        cols = rng.randint(1, 5)
        grid = [[rng.choices([0, 1, 2], weights=[3, 5, 2])[0] for _ in range(cols)] for _ in range(rows)]
        return (grid,)

    def gen_stress():
        rows = rng.randint(40, 60)
        cols = rng.randint(40, 60)
        grid = [[rng.choices([0, 1, 2], weights=[2, 6, 2])[0] for _ in range(cols)] for _ in range(rows)]
        return (grid,)

    visible = [
        ([[2, 1, 1], [1, 1, 0], [0, 1, 1]],),
        ([[2, 1, 1], [0, 1, 1], [1, 0, 1]],),
        ([[0, 2]],),
        ([[0]],),
        ([[2, 1], [1, 1]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([[0]],), ([[1]],), ([[2]],), ([[1, 1, 1]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([[1, 0, 0, 0, 2]],),                      # rot must cross a wide gap of zeros — impossible
        ([[2, 0, 1]],),                             # isolated fresh orange blocked by water
        ([[1, 1, 1], [1, 1, 1], [1, 1, 2]],),       # single rotten corner, must spread to all
        ([[2, 1, 1], [1, 1, 1], [1, 1, 1]],),       # rotten in opposite corner
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([[2, 1]],),         # minimal 2-cell case, minutes == 1
        ([[1, 2]],),         # rotten on the right, tests direction symmetry
        ([[2, 1, 1, 1]],),   # tests minute-counting off-by-one over a line
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── max-distance-to-zero: oracle(grid); cells in {0,1}, at least one 0 ────────

def _plan_max_distance_to_zero(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _grid_input

    def gen_small():
        rows = rng.randint(1, 6)
        cols = rng.randint(1, 6)
        while True:
            grid = [[rng.choices([0, 1], weights=[3, 5])[0] for _ in range(cols)] for _ in range(rows)]
            if any(0 in row for row in grid):
                return (grid,)

    def gen_stress():
        rows = rng.randint(40, 60)
        cols = rng.randint(40, 60)
        while True:
            grid = [[rng.choices([0, 1], weights=[1, 9])[0] for _ in range(cols)] for _ in range(rows)]
            if any(0 in row for row in grid):
                return (grid,)

    visible = [
        ([[0, 0, 0], [0, 1, 0], [0, 0, 0]],),
        ([[0, 0, 1], [1, 1, 1], [1, 1, 1]],),
        ([[0]],),
        ([[1, 0], [1, 1]],),
        ([[0, 1, 1], [1, 1, 1], [1, 1, 1]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([[0]],), ([[0, 1]],), ([[1, 0]],), ([[0], [1]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([[0, 1, 1, 1, 1]],),                        # single 0 at the far edge
        ([[1, 1, 1, 1, 0]],),                        # single 0 at the opposite edge
        ([[1, 1, 1], [1, 0, 1], [1, 1, 1]],),        # 0 dead center, symmetric distances
        ([[0, 1, 1], [1, 1, 1], [1, 1, 0]],),        # two 0s at opposite corners
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([[0, 1]],),      # minimal 2-cell, distance 1
        ([[1, 0]],),
        ([[0, 1, 1]],),   # tests multi-source BFS layering (distance 2)
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── number-of-islands: oracle(grid); cells in {0,1} ───────────────────────────

def _plan_number_of_islands(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _grid_input

    def gen_small():
        rows = rng.randint(1, 6)
        cols = rng.randint(1, 6)
        grid = [[rng.choices([0, 1], weights=[1, 1])[0] for _ in range(cols)] for _ in range(rows)]
        return (grid,)

    def gen_stress():
        rows = rng.randint(45, 50)
        cols = rng.randint(45, 50)
        grid = [[rng.choices([0, 1], weights=[1, 1])[0] for _ in range(cols)] for _ in range(rows)]
        return (grid,)

    visible = [
        ([[1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 1]],),
        ([[1, 0, 0, 1, 0], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0]],),
        ([[0]],),
        ([[1, 1], [1, 1]],),
        ([[1, 0, 1], [0, 0, 0], [1, 0, 1]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([[0]],), ([[1]],), ([[1, 1, 1, 1, 1]],), ([[0, 0, 0, 0, 0]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([[1, 0, 1, 0, 1, 0, 1]],),                     # checkerboard row — many islands, size 1
        ([[1, 1, 1, 1, 1, 1, 1]],),                     # single long island
        ([[1, 0], [0, 1], [1, 0], [0, 1]],),            # diagonal-only adjacency (not 4-connected)
        ([[1, 1, 0], [1, 1, 0], [0, 0, 1]],),           # one big + one isolated single cell
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([[1, 1]],),   # single row, one island of size 2
        ([[1, 0, 1]],),  # single row, two separate islands
        ([[1], [1]],),   # single column, one island
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── shortest-path-binary-matrix: oracle(grid); n x n, cells in {0,1} ──────────

def _plan_shortest_path_binary_matrix(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _grid_input

    def gen_small():
        n = rng.randint(1, 6)
        grid = [[rng.choices([0, 1], weights=[3, 2])[0] for _ in range(n)] for _ in range(n)]
        return (grid,)

    def gen_stress():
        n = rng.randint(60, 90)
        grid = [[rng.choices([0, 1], weights=[4, 1])[0] for _ in range(n)] for _ in range(n)]
        return (grid,)

    visible = [
        ([[0, 1], [1, 0]],),
        ([[0, 0, 0], [1, 1, 0], [1, 1, 0]],),
        ([[1, 0, 0]],),
        ([[0]],),
        ([[0, 0], [0, 0]],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ([[0]],), ([[1]],), ([[0, 1]],), ([[1, 0]],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ([[0, 0, 0], [0, 1, 0], [0, 0, 0]],),          # obstacle exactly in the middle, forces diagonal
        ([[0, 1, 1], [1, 1, 1], [1, 1, 0]],),          # fully walled off — no path
        ([[0, 0, 0, 0, 0], [1, 1, 1, 1, 0], [0, 0, 0, 0, 0], [0, 1, 1, 1, 1], [0, 0, 0, 0, 0]],),  # zigzag forced path
        ([[0, 1], [1, 0]],),                            # only diagonal move works
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ([[0, 0], [0, 0]],),   # diagonal shortcut should beat manhattan path
        ([[0, 0, 0], [0, 0, 0], [0, 0, 0]],),
        ([[0, 1, 0], [0, 1, 0], [0, 0, 0]],),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── word-ladder-length: oracle(begin_word, end_word, word_list) ──────────────

def _to_input_word_ladder(begin_word, end_word, word_list):
    return f"{begin_word}\n{end_word}\n{_arr(word_list)}"


_ALPHA = "abcdefgh"


def _mutate_word(rng: random.Random, w: str, alphabet: str = _ALPHA) -> str:
    i = rng.randrange(len(w))
    ch = rng.choice([c for c in alphabet if c != w[i]])
    return w[:i] + ch + w[i + 1:]


def _plan_word_ladder(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_word_ladder

    def gen_chain(length_hint: int, reachable: bool = True):
        wl = rng.randint(3, 4)
        begin = "".join(rng.choice(_ALPHA) for _ in range(wl))
        chain = [begin]
        cur = begin
        steps = max(1, length_hint)
        for _ in range(steps):
            nxt = _mutate_word(rng, cur)
            chain.append(nxt)
            cur = nxt
        end = cur
        word_list = chain[1:]
        if not reachable:
            # remove the end word so no path exists
            word_list = [w for w in word_list if w != end]
            if not word_list:
                word_list = ["z" * wl]
        rng.shuffle(word_list)
        return (begin, end, word_list)

    def gen_small():
        return gen_chain(rng.randint(1, 4), reachable=rng.random() < 0.8)

    def gen_stress():
        wl = 4
        begin = "".join(rng.choice(_ALPHA) for _ in range(wl))
        # build a large random word bank plus a guaranteed chain to end
        chain = [begin]
        cur = begin
        for _ in range(rng.randint(6, 10)):
            cur = _mutate_word(rng, cur)
            chain.append(cur)
        end = chain[-1]
        bank = set(chain[1:])
        # Cap the target by the actual reachable domain size (len(_ALPHA)**wl)
        # so this can never demand more unique words than combinatorially
        # exist — the previous version (4-letter alphabet, target 300-600 vs.
        # only 4**4=256 possible words) was a guaranteed infinite loop, found
        # via py-spy on a live migration run stuck here for 100+ minutes.
        target = min(rng.randint(300, 600), len(_ALPHA) ** wl - 1)
        while len(bank) < target:
            bank.add("".join(rng.choice(_ALPHA) for _ in range(wl)))
        word_list = list(bank)
        rng.shuffle(word_list)
        return (begin, end, word_list)

    visible = [
        ("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]),
        ("hit", "cog", ["hot", "dot", "dog", "lot", "log"]),
        ("a", "c", ["a", "b", "c"]),
        ("hot", "dog", ["hot", "dog"]),
        ("aa", "cc", ["ab", "ac", "bc", "cc"]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        ("hit", "hit", ["hit"]),           # begin == end, trivially length 1
        ("hit", "hot", ["hot"]),           # single-step ladder
        ("abc", "xyz", ["def"]),           # end word not even in list
        ("aaa", "aab", []),                # empty word list, end unreachable
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        ("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog", "hig", "hig"[::-1]]),  # extra decoy words
        ("aaaa", "bbbb", ["aaab", "aabb", "abbb", "bbbb"]),  # exact minimal 1-letter-at-a-time chain
        ("abcd", "abcd", ["abcd", "abce", "abcf"]),          # begin==end with distractors present
        ("abab", "baba", ["baab", "abab", "aaab", "abaa", "baaa", "baba"]),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        ("hit", "hot", ["hot", "dot"]),     # tests inclusive step counting (should be 2, not 1)
        ("hit", "dot", ["hot", "dot"]),     # tests 2-step vs 3-step off-by-one
        ("aaaa", "aaab", ["aaab"]),
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── minimum-knight-moves: oracle(x, y) ────────────────────────────────────────

def _to_input_knight(x, y):
    return f"{x} {y}"


def _plan_knight_moves(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_knight

    def gen_small():
        return (rng.randint(-15, 15), rng.randint(-15, 15))

    def gen_stress():
        return (rng.randint(-300, 300), rng.randint(-300, 300))

    visible = [
        (2, 1), (5, 5), (0, 0), (1, 0), (3, 3),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        (0, 0), (1, 1), (0, 1), (1, 0),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (-5, -5), (300, 300), (-300, 300), (300, -300),
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (2, 0),   # not reachable in 1 move, tests exact move-count parity
        (1, 2),   # reachable in exactly 1 move
        (2, 2),   # reachable in exactly 2 moves
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── is-bipartite: oracle(n, edges) ────────────────────────────────────────────

def _to_input_bipartite(n, edges):
    lines = [f"{n} {len(edges)}"]
    lines += [f"{u} {v}" for u, v in edges]
    return "\n".join(lines)


def _plan_is_bipartite(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_bipartite

    def gen_bipartite_graph(n: int, extra_edge_prob: float = 0.0) -> tuple[int, list[tuple[int, int]]]:
        # split into two sides, only connect across sides -> guaranteed bipartite
        side = [rng.randint(0, 1) for _ in range(n)]
        possible = [(u, v) for u in range(n) for v in range(u + 1, n) if side[u] != side[v]]
        rng.shuffle(possible)
        m = rng.randint(0, len(possible))
        edges = possible[:m]
        return (n, edges)

    def gen_odd_cycle_graph(n: int) -> tuple[int, list[tuple[int, int]]]:
        # guarantee a non-bipartite graph by embedding an odd cycle (length >= 3, odd)
        cyc_len = 3 if n < 3 else rng.choice([l for l in range(3, n + 1) if l % 2 == 1] or [3])
        cyc_len = min(cyc_len, n)
        nodes = list(range(cyc_len))
        edges = [(nodes[i], nodes[(i + 1) % cyc_len]) for i in range(cyc_len)]
        return (n, edges)

    def gen_small():
        n = rng.randint(1, 8)
        if rng.random() < 0.5 or n < 3:
            return gen_bipartite_graph(n)
        return gen_odd_cycle_graph(n)

    def gen_stress():
        n = rng.randint(1000, 3000)
        if rng.random() < 0.5:
            return gen_bipartite_graph(n)
        return gen_odd_cycle_graph(n)

    visible = [
        (4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
        (3, [(0, 1), (1, 2), (2, 0)]),
        (4, [(0, 1), (2, 3)]),
        (1, []),
        (5, [(0, 1), (1, 2), (2, 3), (3, 4)]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_small, ti, seen)
    boundary_anchors = [
        (1, []), (2, []), (2, [(0, 1)]), (0, []),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)
    adversarial_anchors = [
        (6, [(0, 1), (2, 3), (4, 5)]),                      # disconnected components, all bipartite
        (7, [(0, 1), (1, 2), (2, 0), (3, 4)]),              # one odd-cycle component + one fine component
        (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]),      # 4-cycle plus a diagonal chord -> odd cycle formed
        (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]),      # 5-cycle, odd, not bipartite
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)
    mutation_anchors = [
        (2, [(0, 1)]),           # minimal bipartite edge
        (3, [(0, 1), (1, 2)]),   # path of length 2, bipartite
        (3, [(0, 1), (1, 2), (0, 2)]),  # triangle, tests odd-cycle detection exactly
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)
    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

def _fmt_bool(a) -> str:
    return "true" if a else "false"


BFS_GRAPH_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "rotten-oranges-minutes": (_grid_input, str, _plan_rotten_oranges),
    "max-distance-to-zero": (_grid_input, str, _plan_max_distance_to_zero),
    "number-of-islands": (_grid_input, str, _plan_number_of_islands),
    "shortest-path-binary-matrix": (_grid_input, str, _plan_shortest_path_binary_matrix),
    "word-ladder-length": (_to_input_word_ladder, str, _plan_word_ladder),
    "minimum-knight-moves": (_to_input_knight, str, _plan_knight_moves),
    "is-bipartite": (_to_input_bipartite, _fmt_bool, _plan_is_bipartite),
}
