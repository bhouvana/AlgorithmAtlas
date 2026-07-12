"""
40-test case plans for the `tree_variants` family (see testgen.py for the
shared bucket contract: visible 5 / basic 7 / boundary 8 / adversarial 8 /
mutation 7 / stress 5 = 40). One entry per slug in tree_variants.py's
`_SPECS`.

All tree-shaped inputs use the project's ONE canonical level-order-with-
`null` serialization (see tree_variants.py's `_parse_tree_code`), produced
via `tg.tree_shape_patterns` / `tg.rand_tree_level_order` for general binary
trees. Three slugs specifically require a valid BST (`is-valid-bst` also
needs *invalid*-BST adversarial cases, so it uses a mix): `kth-smallest-in-bst`
and `lowest-common-ancestor-bst` always need a genuine BST since their oracle
functions raise `OracleError` (kth: k out of range; lca: p/q not both present
or traversal falls off the tree) on malformed input. A dedicated
`_rand_bst_level_order` helper builds a balanced BST from a sorted distinct
value sample and BFS-serializes it — validated to round-trip through the
project's `_parse_tree_code()` parser.
"""
from __future__ import annotations

import random

from .. import testgen as tg


def _tree_line(values: list) -> str:
    return " ".join("null" if v is None else str(v) for v in values)


# ── shared tree generators ────────────────────────────────────────────────────

def _rand_bst_level_order(rng: random.Random, n: int, lo: int = -50, hi: int = 50) -> list[int | None]:
    """A balanced BST (built from a sorted sample of n distinct values),
    BFS-serialized to the canonical level-order-with-null format. Guarantees
    a genuine, unique-valued BST — safe for kth-smallest / LCA oracles."""
    if n == 0:
        return []
    span = hi - lo + 1
    n = min(n, span)
    vals = sorted(rng.sample(range(lo, hi + 1), n))

    class _Node:
        __slots__ = ("v", "l", "r")

        def __init__(self, v):
            self.v = v
            self.l = None
            self.r = None

    def build(a, b):
        if a > b:
            return None
        mid = (a + b) // 2
        node = _Node(vals[mid])
        node.l = build(a, mid - 1)
        node.r = build(mid + 1, b)
        return node

    root = build(0, len(vals) - 1)
    out: list[int | None] = [root.v]
    queue = [root]
    qi = 0
    while qi < len(queue):
        node = queue[qi]
        qi += 1
        for child in (node.l, node.r):
            if child is None:
                out.append(None)
            else:
                out.append(child.v)
                queue.append(child)
    while out and out[-1] is None:
        out.pop()
    return out


def _skewed_bst_level_order(rng: random.Random, n: int, lo: int = -50, hi: int = 50, side: str = "r") -> list[int | None]:
    """A degenerate (linked-list-shaped) BST: strictly increasing chain via
    right children (or decreasing via left children) — still a valid BST."""
    if n == 0:
        return []
    span = hi - lo + 1
    n = min(n, span)
    vals = sorted(rng.sample(range(lo, hi + 1), n))
    if side == "l":
        vals = list(reversed(vals))
    out: list[int | None] = [vals[0]]
    for v in vals[1:]:
        if side == "r":
            out.append(None)
            out.append(v)
        else:
            out.append(v)
            out.append(None)
    while out and out[-1] is None:
        out.pop()
    return out


def _digit_tree_level_order(rng: random.Random, n: int) -> list[int | None]:
    """A tree whose values are all single digits [0, 9] — required domain for
    sum-root-to-leaf-numbers."""
    return tg.rand_tree_level_order(rng, n, 0, 9)


def _bst_values(tree: list[int | None]) -> list[int]:
    return [v for v in tree if v is not None]


# ── max-depth-binary-tree: oracle(values) ─────────────────────────────────────

def _to_input_max_depth(values):
    return _tree_line(values)


def _plan_max_depth(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth

    def gen_random():
        n = rng.randint(2, 15)
        return (tg.rand_tree_level_order(rng, n),)

    def gen_stress():
        n = rng.randint(3000, 8000)
        return (tg.rand_tree_level_order(rng, n),)

    visible = [
        ([3, 9, 20, None, None, 15, 7],),
        ([1, None, 2],),
        ([],),
        ([1],),
        ([1, 2, 3, 4],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    boundary_anchors = [
        ([],),
        ([1],),
        ([1, 2],),
        ([1, None, 2],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random, ti, seen)

    shapes = tg.tree_shape_patterns(rng, 12)
    adversarial_anchors = tg.register(
        [(shapes["left_skewed"],), (shapes["right_skewed"],), (shapes["all_same_value"],)], ti, seen
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = tg.register(
        [([1, 2, None],), ([1, None, 2],), ([1, 2, 3],)], ti, seen
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── diameter-of-binary-tree: oracle(values) ───────────────────────────────────

def _plan_diameter(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth  # same single-tree shape

    def gen_random():
        n = rng.randint(2, 15)
        return (tg.rand_tree_level_order(rng, n),)

    def gen_stress():
        n = rng.randint(3000, 8000)
        return (tg.rand_tree_level_order(rng, n),)

    visible = [
        ([1, 2, 3, 4, 5],),
        ([1, 2],),
        ([1],),
        ([3, None, 7, 6, 0, 2, None, 5],),
        ([1, 2, 3, 4, None, None, 5],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    boundary_anchors = tg.register([([1],), ([1, 2],), ([1, None, 2],)], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random, ti, seen)

    shapes = tg.tree_shape_patterns(rng, 14)
    adversarial_anchors = tg.register(
        [(shapes["left_skewed"],), (shapes["right_skewed"],), (shapes["all_same_value"],)], ti, seen
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    # mutation targets: diameter NOT through the root (deep subtree diameter)
    mutation_anchors = tg.register(
        [
            ([1, 2, 3, None, None, 4, 5, None, None, 6, 7],),
            ([1, 2, None, 3, None, 4, None, 5],),
            ([1, 2, 3, 4, 5, 6, 7],),
        ], ti, seen,
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── is-balanced-binary-tree: oracle(values) ───────────────────────────────────

def _plan_is_balanced(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth

    def gen_random():
        n = rng.randint(1, 15)
        return (tg.rand_tree_level_order(rng, n),)

    def gen_stress():
        n = rng.randint(3000, 8000)
        return (tg.rand_tree_level_order(rng, n),)

    visible = [
        ([3, 9, 20, None, None, 15, 7],),
        ([1, 2, 2, 3, 3, None, None, 4, 4],),
        ([],),
        ([2, 2, 0, 8, None, 8, None, 7],),
        ([1],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    boundary_anchors = tg.register([([],), ([1],), ([1, 2],)], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random, ti, seen)

    shapes = tg.tree_shape_patterns(rng, 10)
    # left/right-skewed chains of length >= 3 are always UNbalanced — good adversarial signal
    adversarial_anchors = tg.register(
        [
            (shapes["left_skewed"],),
            (shapes["right_skewed"],),
            ([1, 2, 3, 4, None, None, None, 5],),  # unbalanced deep in one branch only
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    # mutation targets: imbalance NOT at the root (buggy solutions that only check root)
    mutation_anchors = tg.register(
        [
            ([1, 2, 3, 4, 5, None, None, 6, None, None, None, None, 7],),
            ([1, 2, 3, None, None, 4, 5, 6, None],),
            ([1, 2, 3],),
        ], ti, seen,
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── is-valid-bst: oracle(values) — mixes valid BSTs and near-miss invalid trees ─

def _plan_is_valid_bst(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth

    def gen_valid():
        n = rng.randint(1, 12)
        return (_rand_bst_level_order(rng, n),)

    def gen_invalid():
        # take a valid BST then corrupt one non-root value to break the global
        # (not just local) BST property
        n = rng.randint(3, 12)
        tree = _rand_bst_level_order(rng, n)
        idx_candidates = [i for i, v in enumerate(tree) if v is not None and i != 0]
        if not idx_candidates:
            return (tree,)
        idx = rng.choice(idx_candidates)
        tree = list(tree)
        tree[idx] = tree[0]  # duplicate root's value somewhere deep — breaks strict BST
        return (tree,)

    def gen_stress_valid():
        n = rng.randint(3000, 8000)
        return (_rand_bst_level_order(rng, n, -100_000, 100_000),)

    def gen_stress_invalid():
        n = rng.randint(3000, 8000)
        tree = list(_rand_bst_level_order(rng, n, -100_000, 100_000))
        idx_candidates = [i for i, v in enumerate(tree) if v is not None and i != 0]
        if idx_candidates:
            tree[rng.choice(idx_candidates)] = tree[0]
        return (tree,)

    visible = [
        ([2, 1, 3],),
        ([5, 1, 4, None, None, 3, 6],),
        ([1],),
        ([4, 0, None, None, 5, None, 9],),
        ([5, 3, 8, 1, 4, 7, 9],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(4, gen_valid, ti, seen) + tg.fill_unique(3, gen_invalid, ti, seen)

    boundary_anchors = tg.register(
        [([1],), ([],), ([1, 0],), ([1, None, 2],)], ti, seen
    )
    boundary = boundary_anchors + tg.fill_unique(4, gen_valid, ti, seen) + tg.fill_unique(
        8 - len(boundary_anchors) - 4, gen_invalid, ti, seen
    )

    # classic "local check passes, global fails" traps — left child's RIGHT
    # grandchild value equal to/greater than root
    adversarial_anchors = tg.register(
        [
            ([5, 1, 6, None, 2, None, None, None, None, None, 17],),  # right grandchild of left child > root
            ([10, 5, 15, None, None, 6, 20],),  # 6 is a valid local child of 15 but < root's right bound
            ([3, 1, 5, 0, 2, 4, 6, None, None, None, None, None, None, None, 7],),
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(
        (8 - len(adversarial_anchors)) // 2, gen_stress_valid, ti, seen
    ) + tg.fill_unique(8 - len(adversarial_anchors) - (8 - len(adversarial_anchors)) // 2, gen_stress_invalid, ti, seen)

    # mutation: equal values (duplicates) must be INVALID for a strict BST
    mutation_anchors = tg.register(
        [
            ([2, 2, 2],),
            ([1, 1],),
            ([5, 4, 6, 4],),
        ], ti, seen,
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_invalid, ti, seen)

    stress = tg.fill_unique(3, gen_stress_valid, ti, seen) + tg.fill_unique(2, gen_stress_invalid, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── is-symmetric-tree: oracle(values) ─────────────────────────────────────────

def _mirror_tree(rng: random.Random, half_n: int, lo=-50, hi=50) -> list[int | None]:
    """Build a genuinely symmetric tree: random left subtree, mirrored right
    subtree, sharing a root value."""

    class _Node:
        __slots__ = ("v", "l", "r")

        def __init__(self, v):
            self.v = v
            self.l = None
            self.r = None

    def rand_subtree(n):
        if n <= 0:
            return None
        node = _Node(rng.randint(lo, hi))
        remaining = n - 1
        left_n = rng.randint(0, remaining)
        right_n = remaining - left_n
        node.l = rand_subtree(left_n)
        node.r = rand_subtree(right_n)
        return node

    def mirror_copy(node):
        if node is None:
            return None
        m = _Node(node.v)
        m.l = mirror_copy(node.r)
        m.r = mirror_copy(node.l)
        return m

    root = _Node(rng.randint(lo, hi))
    left = rand_subtree(half_n)
    root.l = left
    root.r = mirror_copy(left)

    if root is None:
        return []
    out: list[int | None] = [root.v]
    queue = [root]
    qi = 0
    while qi < len(queue):
        node = queue[qi]
        qi += 1
        for child in (node.l, node.r):
            if child is None:
                out.append(None)
            else:
                out.append(child.v)
                queue.append(child)
    while out and out[-1] is None:
        out.pop()
    return out


def _plan_is_symmetric(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth

    def gen_symmetric():
        n = rng.randint(0, 6)
        return (_mirror_tree(rng, n),)

    def gen_asymmetric():
        n = rng.randint(2, 15)
        return (tg.rand_tree_level_order(rng, n),)

    def gen_stress_symmetric():
        n = rng.randint(1500, 3500)
        return (_mirror_tree(rng, n),)

    def gen_stress_asymmetric():
        n = rng.randint(3000, 8000)
        return (tg.rand_tree_level_order(rng, n),)

    visible = [
        ([1, 2, 2, 3, 4, 4, 3],),
        ([1, 2, 2, None, 3, None, 3],),
        ([1],),
        ([],),
        ([1, 2, 2],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(4, gen_symmetric, ti, seen) + tg.fill_unique(3, gen_asymmetric, ti, seen)

    boundary_anchors = tg.register([([],), ([1],), ([1, 2, 2],), ([1, 2],)], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(4, gen_symmetric, ti, seen) + tg.fill_unique(
        8 - len(boundary_anchors) - 4, gen_asymmetric, ti, seen
    )

    # values that look symmetric as a preorder palindrome sequence but are
    # NOT structurally mirrored (traps a "value list is a palindrome" bug)
    adversarial_anchors = tg.register(
        [
            ([1, 2, 3, None, None, 3, 2],),  # preorder [1,2,3,3,2] is palindrome-ish but structure differs from true mirror
            ([7, 3, 3, None, 5, 5, None],),
            ([1, 2, 2, 2, None, None, 2],),
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(
        4, gen_stress_symmetric, ti, seen
    ) + tg.fill_unique(8 - len(adversarial_anchors) - 4, gen_stress_asymmetric, ti, seen)

    mutation_anchors = tg.register(
        [
            ([1, 2, 2, 3, None, None, 3],),  # symmetric
            ([1, 2, 2, None, 3, 3, None],),  # asymmetric — inner grandchildren swapped
            ([5, 4, 4, None, None, None, None],),
        ], ti, seen,
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_symmetric, ti, seen)

    stress = tg.fill_unique(3, gen_stress_symmetric, ti, seen) + tg.fill_unique(2, gen_stress_asymmetric, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── invert-tree-preorder: oracle(values) ──────────────────────────────────────

def _plan_invert(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth

    def gen_random():
        n = rng.randint(1, 15)
        return (tg.rand_tree_level_order(rng, n),)

    def gen_stress():
        n = rng.randint(3000, 8000)
        return (tg.rand_tree_level_order(rng, n),)

    visible = [
        ([4, 2, 7, 1, 3, 6, 9],),
        ([2, 1, 3],),
        ([],),
        ([1],),
        ([1, 2],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    boundary_anchors = tg.register([([],), ([1],), ([1, 2],), ([1, None, 2],)], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random, ti, seen)

    shapes = tg.tree_shape_patterns(rng, 10)
    adversarial_anchors = tg.register(
        [(shapes["left_skewed"],), (shapes["right_skewed"],), (shapes["all_same_value"],)], ti, seen
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = tg.register(
        [([1, 2, None],), ([1, None, 2],), ([1, 2, 3, 4],)], ti, seen
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── path-sum-exists: oracle(values, target) ───────────────────────────────────

def _to_input_path_sum(values, target):
    return f"{_tree_line(values)} {target}".strip()


def _path_sums(values: list[int | None]) -> list[int]:
    """All root-to-leaf sums for a canonical level-order tree — used to pick a
    target that DOES or DOES NOT exist, deterministically."""
    if not values or values[0] is None:
        return []

    class _N:
        __slots__ = ("v", "l", "r")

    nodes: list[_N | None] = [None] * len(values)
    for i, v in enumerate(values):
        if v is not None:
            n = _N()
            n.v = v
            n.l = None
            n.r = None
            nodes[i] = n
    # relink using the same BFS convention as _build_tree
    from collections import deque
    root = nodes[0]
    queue = deque([0])
    idx = 1
    n_len = len(values)
    while queue and idx < n_len:
        cur = queue.popleft()
        if idx < n_len:
            if values[idx] is not None:
                nodes[cur].l = nodes[idx]
                queue.append(idx)
            idx += 1
        if idx < n_len:
            if values[idx] is not None:
                nodes[cur].r = nodes[idx]
                queue.append(idx)
            idx += 1

    sums: list[int] = []

    def dfs(node, cur):
        if node is None:
            return
        cur += node.v
        if node.l is None and node.r is None:
            sums.append(cur)
            return
        dfs(node.l, cur)
        dfs(node.r, cur)

    dfs(root, 0)
    return sums


def _plan_path_sum(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_path_sum

    def gen_hit():
        n = rng.randint(2, 12)
        tree = tg.rand_tree_level_order(rng, n)
        sums = _path_sums(tree)
        target = rng.choice(sums) if sums else 0
        return (tree, target)

    def gen_miss():
        n = rng.randint(2, 12)
        tree = tg.rand_tree_level_order(rng, n)
        sums = set(_path_sums(tree))
        target = rng.randint(-500, 500)
        tries = 0
        while target in sums and tries < 50:
            target = rng.randint(-500, 500)
            tries += 1
        return (tree, target)

    def gen_stress():
        n = rng.randint(3000, 5000)
        tree = tg.rand_tree_level_order(rng, n)
        sums = _path_sums(tree)
        target = rng.choice(sums) if (sums and rng.random() < 0.5) else rng.randint(-100_000, 100_000)
        return (tree, target)

    visible = [
        ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22),
        ([1, 2, 3], 5),
        ([1, 2], 1),
        ([], 0),
        ([1, 2, 3], 4),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(4, gen_hit, ti, seen) + tg.fill_unique(3, gen_miss, ti, seen)

    boundary_anchors = tg.register(
        [([], 0), ([], 1), ([1], 1), ([1], 0), ([1, 2], 3)], ti, seen
    )
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_hit, ti, seen)

    adversarial_anchors = tg.register(
        [
            ([1, -2, -3], -1),  # negative values, path must hit exact negative sum
            ([0, 1, 1], 1),     # zero root plus tie between two leaf sums
            ([-1], -1),
            ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 26),  # sum of ALL nodes but not a root-leaf path
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_miss, ti, seen)

    mutation_anchors = tg.register(
        [
            ([1, 2, 3], 3),   # matches an INTERNAL prefix sum but not any leaf path
            ([1, 2], 1),      # only the root before reaching leaf — must not falsely match
            ([2, 1, 3], 5),
        ], ti, seen,
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_hit, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── count-tree-nodes: oracle(values) ──────────────────────────────────────────

def _plan_count_nodes(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth

    def gen_random():
        n = rng.randint(1, 15)
        return (tg.rand_tree_level_order(rng, n),)

    def gen_stress():
        n = rng.randint(3000, 9000)
        return (tg.rand_tree_level_order(rng, n),)

    visible = [
        ([1, None, 2],),
        ([1, 2, 3, 4, 5],),
        ([],),
        ([1],),
        ([1, 2, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    boundary_anchors = tg.register([([],), ([1],), ([1, 2],), ([1, None, 2],)], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random, ti, seen)

    # incomplete/non-perfect trees are the key adversarial signal (wrong sol.
    # assumes perfect-tree formula 2^depth - 1)
    adversarial_anchors = tg.register(
        [
            ([1, 2, 3, 4],),               # depth 3 but only 4 nodes, not 7
            ([1, 2, None, 3],),             # depth 3, only 3 nodes
            ([1, 2, 3, 4, 5, 6, 7],),       # perfect tree — this one the wrong sol gets right
            ([1, None, 2, None, 3, None, 4],),  # right-skewed chain, depth 4, only 4 nodes
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = tg.register(
        [([1, 2],), ([1, None, 2],), ([1, 2, 3, 4, None, None, None],)], ti, seen
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── lowest-common-ancestor-bst: oracle(values, p, q) ──────────────────────────

def _to_input_lca(values, p, q):
    return f"{_tree_line(values)} {p} {q}".strip()


def _plan_lca(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_lca

    def gen_random(n_lo=3, n_hi=15):
        n = rng.randint(n_lo, n_hi)
        tree = _rand_bst_level_order(rng, n)
        vals = _bst_values(tree)
        p, q = rng.sample(vals, 2) if len(vals) >= 2 else (vals[0], vals[0])
        return (tree, p, q)

    def gen_stress():
        n = rng.randint(3000, 8000)
        tree = _rand_bst_level_order(rng, n, -1_000_000, 1_000_000)
        vals = _bst_values(tree)
        p, q = rng.sample(vals, 2)
        return (tree, p, q)

    base_tree = [6, 2, 8, 0, 4, 7, 9, None, None, 3, 5]
    visible = [
        (base_tree, 2, 8),
        (base_tree, 2, 4),
        ([2, 1], 1, 2),
        ([4, 2, 6, 1, 3, 5, 7], 1, 3),
        (base_tree, 0, 5),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    boundary_anchors = tg.register(
        [
            ([2, 1], 1, 2),
            ([1, None, 2], 1, 2),
            ([5, 3], 3, 5),
        ], ti, seen,
    )
    def gen_tiny():
        return gen_random(2, 3)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_tiny, ti, seen)

    adversarial_anchors = tg.register(
        [
            (base_tree, 0, 9),   # LCA is the root
            (base_tree, 3, 5),   # both under same subtree, deep LCA
            (base_tree, 7, 9),   # LCA is node 8, both on right subtree
            (base_tree, 0, 4),   # LCA is node 2 (p is q's grandparent)
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = tg.register(
        [
            (base_tree, 4, 4),   # p == q — LCA is itself
            ([8, 4, 12, 2, 6, 10, 14], 2, 6),  # ancestor-descendant relationship, not siblings
            ([8, 4, 12, 2, 6, 10, 14], 4, 12),
        ], ti, seen,
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── kth-smallest-in-bst: oracle(values, k) ────────────────────────────────────

def _to_input_kth(values, k):
    return f"{_tree_line(values)} {k}".strip()


def _plan_kth_smallest(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_kth

    def gen_random(n_lo=1, n_hi=15):
        n = rng.randint(n_lo, n_hi)
        tree = _rand_bst_level_order(rng, n)
        vals = _bst_values(tree)
        k = rng.randint(1, len(vals))
        return (tree, k)

    def gen_stress():
        n = rng.randint(3000, 8000)
        tree = _rand_bst_level_order(rng, n, -1_000_000, 1_000_000)
        vals = _bst_values(tree)
        k = rng.randint(1, len(vals))
        return (tree, k)

    visible = [
        ([3, 1, 4, None, 2], 1),
        ([5, 3, 6, 2, 4, None, None, 1], 3),
        ([1], 1),
        ([2, 1, 3], 3),
        ([2, 1, 3], 1),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    def gen_tiny():
        return gen_random(1, 3)
    boundary_anchors = tg.register(
        [([1], 1), ([2, 1], 1), ([2, 1], 2), ([1, None, 2], 2)], ti, seen
    )
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_tiny, ti, seen)

    shapes_r = _skewed_bst_level_order(rng, 10, side="r")
    shapes_l = _skewed_bst_level_order(rng, 10, side="l")
    adversarial_anchors = tg.register(
        [
            (shapes_r, 1),    # smallest of a right-skewed chain — must not stop at root
            (shapes_r, 10),   # largest of a right-skewed chain
            (shapes_l, 1),
            (shapes_l, 10),
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    # mutation: k in the MIDDLE of a wide tree (traps preorder-instead-of-inorder bugs)
    mid_tree = _rand_bst_level_order(rng, 9)
    mid_vals = _bst_values(mid_tree)
    mutation_anchors = tg.register(
        [
            (mid_tree, len(mid_vals) // 2),
            (mid_tree, 1),
            (mid_tree, len(mid_vals)),
        ], ti, seen,
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── level-order-traversal: oracle(values) ─────────────────────────────────────

def _plan_level_order(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth

    def gen_random():
        n = rng.randint(1, 15)
        return (tg.rand_tree_level_order(rng, n),)

    def gen_stress():
        n = rng.randint(2000, 6000)
        return (tg.rand_tree_level_order(rng, n),)

    visible = [
        ([3, 9, 20, None, None, 15, 7],),
        ([1],),
        ([],),
        ([1, 2, 3, 4],),
        ([1, None, 2, None, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    boundary_anchors = tg.register([([],), ([1],), ([1, 2],), ([1, None, 2],)], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random, ti, seen)

    shapes = tg.tree_shape_patterns(rng, 10)
    adversarial_anchors = tg.register(
        [(shapes["left_skewed"],), (shapes["right_skewed"],), (shapes["all_same_value"],)], ti, seen
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = tg.register(
        [([1, 2, 3],), ([1, 2, None, 3],), ([1, None, 2, 3],)], ti, seen
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── right-side-view: oracle(values) ───────────────────────────────────────────

def _plan_right_side_view(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth

    def gen_random():
        n = rng.randint(1, 15)
        return (tg.rand_tree_level_order(rng, n),)

    def gen_stress():
        n = rng.randint(2000, 6000)
        return (tg.rand_tree_level_order(rng, n),)

    visible = [
        ([1, 2, 3, None, 5, None, 4],),
        ([1, None, 3],),
        ([],),
        ([1, 2],),
        ([1, 2, 3],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    boundary_anchors = tg.register([([],), ([1],), ([1, 2],), ([1, None, 2],)], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random, ti, seen)

    # key adversarial trap: the rightmost node at some level is on the LEFT
    # branch (right branch doesn't reach that depth)
    adversarial_anchors = tg.register(
        [
            ([1, 2, 3, 4, None, None, None, 5],),  # deepest node hangs off the LEFT subtree
            ([1, 2, 3, 4],),
            ([1, 2, None, 3, None, 4],),  # left-only chain — right side view is still the whole chain
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = tg.register(
        [([1, 2, 3, 4],), ([1, 2, 3, None, 4],), ([1, 2],)], ti, seen
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── same-tree: oracle(values1, values2) ───────────────────────────────────────

def _to_input_same_tree(values1, values2):
    return f"{_tree_line(values1)}\n{_tree_line(values2)}"


def _plan_same_tree(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_same_tree

    def gen_equal():
        n = rng.randint(0, 12)
        tree = tg.rand_tree_level_order(rng, n)
        return (tree, list(tree))

    def gen_different():
        n = rng.randint(1, 12)
        m = rng.randint(1, 12)
        return (tg.rand_tree_level_order(rng, n), tg.rand_tree_level_order(rng, m))

    def gen_stress_equal():
        n = rng.randint(2000, 5000)
        tree = tg.rand_tree_level_order(rng, n)
        return (tree, list(tree))

    def gen_stress_different():
        n = rng.randint(2000, 5000)
        return (tg.rand_tree_level_order(rng, n), tg.rand_tree_level_order(rng, n))

    visible = [
        ([1, 2, 3], [1, 2, 3]),
        ([1, 2], [1, None, 2]),
        ([], []),
        ([1, 2, 1], [1, 1, 2]),
        ([1], [1]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(4, gen_equal, ti, seen) + tg.fill_unique(3, gen_different, ti, seen)

    boundary_anchors = tg.register(
        [([], []), ([1], [1]), ([1], []), ([], [1]), ([1, 2], [1, 2])], ti, seen
    )
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_different, ti, seen)

    # same MULTISET of values, different structure — traps a "compare sorted
    # value lists" bug
    adversarial_anchors = tg.register(
        [
            ([1, 2, 1], [1, 1, 2]),
            ([1, 2, None, 3], [1, None, 2, None, None, 3]),
            ([5, 3, 8], [5, 8, 3]),
            ([1, 2, 3, 4], [1, 2, 3, 5]),  # nearly identical, one leaf value differs
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_different, ti, seen)

    mutation_anchors = tg.register(
        [
            ([1, 2, 3], [1, 3, 2]),   # swapped children — same multiset, different structure
            ([2, 1, 3], [2, 1, 3]),
            ([1, None, 2], [1, 2, None]),
        ], ti, seen,
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_equal, ti, seen)

    stress = tg.fill_unique(3, gen_stress_equal, ti, seen) + tg.fill_unique(2, gen_stress_different, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── sum-root-to-leaf-numbers: oracle(values) — digits 0-9 only ───────────────

def _plan_sum_root_to_leaf(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth

    def gen_random():
        n = rng.randint(1, 12)
        return (_digit_tree_level_order(rng, n),)

    def gen_stress():
        n = rng.randint(2000, 5000)
        return (_digit_tree_level_order(rng, n),)

    visible = [
        ([1, 2, 3],),
        ([4, 9, 0, 5, 1],),
        ([0],),
        ([1],),
        ([1, 0, 1],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    boundary_anchors = tg.register([([0],), ([9],), ([1],), ([1, 0],)], ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random, ti, seen)

    shapes = tg.tree_shape_patterns(rng, 9, lo=0, hi=9)
    adversarial_anchors = tg.register(
        [
            (shapes["left_skewed"],),
            (shapes["right_skewed"],),
            ([0, 0, 0],),   # all zeros — every leaf path sums to 0
            ([9, 9, 9, 9, 9, 9, 9],),  # all nines, deep tree
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = tg.register(
        [([1, 2, 3],), ([1, 0],), ([1, None, 0],)], ti, seen
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── binary-tree-max-path-sum: oracle(values) — allows negative values ────────

def _plan_max_path_sum(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_max_depth

    def gen_random():
        n = rng.randint(1, 15)
        return (tg.rand_tree_level_order(rng, n, -20, 20),)

    def gen_stress():
        n = rng.randint(2000, 6000)
        return (tg.rand_tree_level_order(rng, n, -1000, 1000),)

    visible = [
        ([1, 2, 3],),
        ([-10, 9, 20, None, None, 15, 7],),
        ([-3],),
        ([2, -1],),
        ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))
    basic = tg.fill_unique(7, gen_random, ti, seen)

    boundary_anchors = tg.register(
        [([-1000],), ([1000],), ([0],), ([1, 2],)], ti, seen
    )
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random, ti, seen)

    # key adversarial trap: best path doesn't pass through the root, or best
    # path is a SINGLE node (all-negative surroundings)
    adversarial_anchors = tg.register(
        [
            ([-1, -2, -3],),           # every value negative — best path is the least-negative single node
            ([2, -1, -2],),            # negative children — best path excludes them
            ([1, -2, 3, None, None, -1, 4],),  # best path in the right subtree, not through root
            ([-2, -1],),
        ], ti, seen,
    )
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = tg.register(
        [([1, 2, 3],), ([-3, 4, 5],), ([1, -2, 3],)], ti, seen
    )
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)
    return {"visible": visible, "basic": basic, "boundary": boundary,
            "adversarial": adversarial, "mutation": mutation, "stress": stress}


# ── registry ───────────────────────────────────────────────────────────────────

TREE_VARIANT_TEST_PLANS: dict[str, tuple] = {
    # slug -> (to_input, format_output, plan_fn)
    "max-depth-binary-tree": (_to_input_max_depth, str, _plan_max_depth),
    "diameter-of-binary-tree": (_to_input_max_depth, str, _plan_diameter),
    "is-balanced-binary-tree": (_to_input_max_depth, lambda a: "true" if a else "false", _plan_is_balanced),
    "is-valid-bst": (_to_input_max_depth, lambda a: "true" if a else "false", _plan_is_valid_bst),
    "is-symmetric-tree": (_to_input_max_depth, lambda a: "true" if a else "false", _plan_is_symmetric),
    "invert-tree-preorder": (_to_input_max_depth, lambda a: " ".join(str(x) for x in a), _plan_invert),
    "path-sum-exists": (_to_input_path_sum, lambda a: "true" if a else "false", _plan_path_sum),
    "count-tree-nodes": (_to_input_max_depth, str, _plan_count_nodes),
    "lowest-common-ancestor-bst": (_to_input_lca, str, _plan_lca),
    "kth-smallest-in-bst": (_to_input_kth, str, _plan_kth_smallest),
    "level-order-traversal": (
        _to_input_max_depth,
        lambda a: "\n".join(" ".join(str(x) for x in level) for level in a),
        _plan_level_order,
    ),
    "right-side-view": (_to_input_max_depth, lambda a: " ".join(str(x) for x in a), _plan_right_side_view),
    "same-tree": (_to_input_same_tree, lambda a: "true" if a else "false", _plan_same_tree),
    "sum-root-to-leaf-numbers": (_to_input_max_depth, str, _plan_sum_root_to_leaf),
    "binary-tree-max-path-sum": (_to_input_max_depth, str, _plan_max_path_sum),
}
