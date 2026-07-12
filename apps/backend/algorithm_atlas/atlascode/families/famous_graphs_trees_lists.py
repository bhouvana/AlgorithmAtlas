"""
Famous graphs/trees/lists pattern-problem family.

Seven `origin_type = PATTERN_PROBLEM` problems (algorithm_slug=None, same
convention as sliding_window_variants.py and most of tree_variants.py): no
single canonical registry algorithm backs "topological sort feasibility",
"grid backtracking", "subset counting with duplicates", "circular DP", or
"general-tree recursion" as its own entry, so linking them to an unrelated
canonical slug would misrepresent coverage.

This module is fully self-contained: it defines its own independent oracle
functions (rather than importing `independent_oracles.py`) since the task
that produced it forbids editing any existing file, including that shared
oracle module. Every oracle below is a short, from-scratch reference
implementation with no dependency on this project's plugin/visualization
layer.

Binary-tree problems use this project's ONE canonical serialization format
(see families/tree_variants.py's `_parse_tree_code()`): level-order with the
literal token `null` for a missing child, e.g. `3 9 20 null null 15 7`. The
parser is copied verbatim (as `_PARSE_TREE_SRC`) into every reference/wrong
solution that needs to reconstruct a tree from stdin, and the same shape is
used by `to_input` for judging.

Distinctions from existing AtlasCode problems (so these are not near-dupes):
  - `course-schedule-feasible` is cycle detection via topological sort
    (Kahn's algorithm), distinct from `is-bipartite` (BFS 2-coloring).
  - `house-robber-circular` handles the circular adjacency constraint (first
    and last house adjacent), distinct from the existing linear
    `house-robber` DP.
  - `lowest-common-ancestor-binary-tree` requires a general recursive
    two-subtree search with no ordering assumption, distinct from the
    existing `lowest-common-ancestor-bst` (BST comparison walk).
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from .. import testgen as tg
from ...plugins.registry import RegisteredAlgorithm


class OracleError(Exception):
    """Raised when an oracle is asked to evaluate an input outside its domain."""


# ── Canonical tree serialization (copied from tree_variants.py's
#    _parse_tree_code(), NOT imported, per the no-existing-file-edits rule;
#    text is byte-identical to that function's stdin-parser logic) ───────────

def _parse_tree_code() -> str:
    return (
        "def parse_tree(tokens):\n"
        "    if not tokens or tokens[0] == 'null':\n        return None\n"
        "    class Node:\n"
        "        def __init__(self, val):\n            self.val = val; self.left = None; self.right = None\n"
        "    root = Node(int(tokens[0]))\n"
        "    queue = [root]\n    i = 1\n    qi = 0\n"
        "    while qi < len(queue) and i < len(tokens):\n"
        "        node = queue[qi]; qi += 1\n"
        "        if i < len(tokens):\n"
        "            if tokens[i] != 'null':\n                node.left = Node(int(tokens[i])); queue.append(node.left)\n"
        "            i += 1\n"
        "        if i < len(tokens):\n"
        "            if tokens[i] != 'null':\n                node.right = Node(int(tokens[i])); queue.append(node.right)\n"
        "            i += 1\n"
        "    return root\n\n"
    )


class _TNode:
    __slots__ = ("val", "left", "right")

    def __init__(self, val: int):
        self.val = val
        self.left: "_TNode | None" = None
        self.right: "_TNode | None" = None


def _build_tree(values: list[int | None]) -> "_TNode | None":
    """Build a real node tree from the canonical level-order-with-null list
    (mirrors _parse_tree_code()'s parser exactly)."""
    if not values or values[0] is None:
        return None
    root = _TNode(values[0])
    queue = [root]
    i = 1
    qi = 0
    n = len(values)
    while qi < len(queue) and i < n:
        node = queue[qi]
        qi += 1
        if i < n:
            if values[i] is not None:
                node.left = _TNode(values[i])
                queue.append(node.left)
            i += 1
        if i < n:
            if values[i] is not None:
                node.right = _TNode(values[i])
                queue.append(node.right)
            i += 1
    return root


def _tree_line(values: list) -> str:
    return " ".join("null" if v is None else str(v) for v in values)


def _serialize_tree(root: "_TNode | None") -> list[int | None]:
    """Level-order serialize with trailing Nones trimmed (canonical form)."""
    if root is None:
        return []
    out: list[int | None] = [root.val]
    queue = [root]
    qi = 0
    while qi < len(queue):
        node = queue[qi]
        qi += 1
        for child in (node.left, node.right):
            if child is None:
                out.append(None)
            else:
                out.append(child.val)
                queue.append(child)
    while out and out[-1] is None:
        out.pop()
    return out


# ── Output formatters ────────────────────────────────────────────────────────

def _fmt_bool(answer: object) -> str:
    return "true" if answer else "false"


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_tree(answer: object) -> str:
    return _tree_line(answer)  # type: ignore[arg-type]


def _fmt_levels(answer: object) -> str:
    return "\n".join(" ".join(str(x) for x in level) for level in answer)  # type: ignore[union-attr]


# ── Oracles ───────────────────────────────────────────────────────────────────

def oracle_course_schedule_feasible(n: int, prereqs: list[tuple[int, int]]) -> bool:
    """True if all n courses (0..n-1) can be finished given (a, b) pairs
    meaning 'b must be taken before a'. Kahn's algorithm topological sort:
    feasible iff every node is eventually removed (no residual cycle)."""
    if n < 0:
        raise OracleError(f"course count must be >= 0, got {n}")
    adj: list[list[int]] = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in prereqs:
        if not (0 <= a < n and 0 <= b < n):
            raise OracleError(f"prereq ({a},{b}) out of range for n={n}")
        adj[b].append(a)
        indeg[a] += 1
    queue = [i for i in range(n) if indeg[i] == 0]
    seen = 0
    qi = 0
    while qi < len(queue):
        u = queue[qi]
        qi += 1
        seen += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return seen == n


def oracle_word_search_grid(grid: list[list[str]], word: str) -> bool:
    """True if `word` can be traced through orthogonally-adjacent, non-reused
    cells of `grid`."""
    if not grid or not grid[0]:
        return word == ""
    rows, cols = len(grid), len(grid[0])
    if word == "":
        return True

    def dfs(r: int, c: int, idx: int, visited: set[tuple[int, int]]) -> bool:
        if grid[r][c] != word[idx]:
            return False
        if idx == len(word) - 1:
            return True
        visited.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                if dfs(nr, nc, idx + 1, visited):
                    visited.discard((r, c))
                    return True
        visited.discard((r, c))
        return False

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0, set()):
                return True
    return False


def oracle_distinct_subsets_count(nums: list[int]) -> int:
    """Count of DISTINCT subsets (including empty) of a possibly-duplicated
    multiset. Sort + group by value; each value with count k contributes a
    (k+1) multiplicative choice (take 0..k copies)."""
    if not nums:
        return 1
    from collections import Counter
    counts = Counter(nums)
    total = 1
    for k in counts.values():
        total *= (k + 1)
    return total


def oracle_house_robber_circular(nums: list[int]) -> int:
    """Max sum of non-adjacent houses arranged in a circle (house 0 and
    house n-1 are adjacent)."""
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]

    def _linear(vals: list[int]) -> int:
        prev, curr = 0, 0
        for v in vals:
            prev, curr = curr, max(curr, prev + v)
        return curr

    return max(_linear(nums[:-1]), _linear(nums[1:]))


def oracle_lca_binary_tree(values: list[int | None], p: int, q: int) -> int:
    """Value of the lowest common ancestor of nodes with values p and q in a
    general binary tree (no ordering assumption). p != q, both guaranteed
    present."""
    root = _build_tree(values)
    if root is None:
        raise OracleError("empty tree has no LCA")

    def find(node: "_TNode | None") -> "_TNode | None":
        if node is None or node.val == p or node.val == q:
            return node
        left = find(node.left)
        right = find(node.right)
        if left is not None and right is not None:
            return node
        return left if left is not None else right

    result = find(root)
    if result is None:
        raise OracleError(f"neither {p} nor {q} found in tree")
    return result.val


def oracle_construct_tree_preorder_inorder(preorder: list[int], inorder: list[int]) -> list[int | None]:
    """Reconstruct a binary tree from its preorder + inorder traversals
    (distinct values) and return it in canonical level-order-with-null form."""
    if len(preorder) != len(inorder):
        raise OracleError("preorder/inorder length mismatch")
    if len(set(inorder)) != len(inorder):
        raise OracleError("inorder values must be distinct")

    index_of = {v: i for i, v in enumerate(inorder)}
    pre_iter = iter(preorder)

    def build(lo: int, hi: int) -> "_TNode | None":
        if lo > hi:
            return None
        try:
            root_val = next(pre_iter)
        except StopIteration:
            raise OracleError("preorder exhausted before inorder range")
        node = _TNode(root_val)
        mid = index_of[root_val]
        node.left = build(lo, mid - 1)
        node.right = build(mid + 1, hi)
        return node

    root = build(0, len(inorder) - 1)
    return _serialize_tree(root)


def oracle_zigzag_level_order(values: list[int | None]) -> list[list[int]]:
    """Zigzag level order: level 0 L->R, level 1 R->L, alternating."""
    root = _build_tree(values)
    if root is None:
        return []
    levels: list[list[int]] = []
    frontier = [root]
    left_to_right = True
    while frontier:
        vals = [n.val for n in frontier]
        if not left_to_right:
            vals.reverse()
        levels.append(vals)
        nxt: list[_TNode] = []
        for n in frontier:
            if n.left is not None:
                nxt.append(n.left)
            if n.right is not None:
                nxt.append(n.right)
        frontier = nxt
        left_to_right = not left_to_right
    return levels


# ── Spec dataclass (mirrors greedy.py) ───────────────────────────────────────

@dataclass(frozen=True)
class _Spec:
    oracle: Callable[..., object]
    to_input: Callable[..., str]
    format_output: Callable[[object], str]
    statement: str
    constraints: list[str]
    starter_code: str
    title: str
    category: str
    difficulty: str = "Medium"
    estimated_minutes: int = 25


# ── to_input serializers ─────────────────────────────────────────────────────

def _to_input_course_schedule(n: int, prereqs: list[tuple[int, int]]) -> str:
    lines = [f"{n} {len(prereqs)}"]
    lines += [f"{a} {b}" for a, b in prereqs]
    return "\n".join(lines)


def _to_input_word_search(grid: list[list[str]], word: str) -> str:
    rows, cols = len(grid), len(grid[0]) if grid else 0
    lines = [f"{rows} {cols}"]
    lines += ["".join(row) for row in grid]
    lines.append(word)
    return "\n".join(lines)


def _to_input_subsets(nums: list[int]) -> str:
    return f"{len(nums)} " + " ".join(str(x) for x in nums)


def _to_input_house_robber(nums: list[int]) -> str:
    return f"{len(nums)} " + " ".join(str(x) for x in nums)


def _to_input_lca_tree(values: list[int | None], p: int, q: int) -> str:
    return f"{_tree_line(values)} {p} {q}"


def _to_input_construct_tree(preorder: list[int], inorder: list[int]) -> str:
    return f"{_tree_line(preorder)}\n{_tree_line(inorder)}"


def _to_input_zigzag(values: list[int | None]) -> str:
    return _tree_line(values)


# ── Specs ─────────────────────────────────────────────────────────────────────

_SPECS: dict[str, _Spec] = {
    "course-schedule-feasible": _Spec(
        oracle=oracle_course_schedule_feasible,
        to_input=_to_input_course_schedule,
        format_output=_fmt_bool,
        statement=(
            "There are `n` courses labeled `0..n-1`. You are given `m` "
            "prerequisite pairs `(a, b)` meaning course `b` must be completed "
            "before course `a`. Print `true` if it is possible to finish **all** "
            "courses, or `false` if the prerequisites form a cycle that makes "
            "this impossible."
        ),
        constraints=["1 ≤ n ≤ 10^4", "0 ≤ m ≤ 5×10^4"],
        starter_code=(
            "import sys\n"
            "data = sys.stdin.read().split('\\n')\n"
            "n, m = map(int, data[0].split())\n"
            "prereqs = [tuple(map(int, data[1+i].split())) for i in range(m)]\n\n"
            "def can_finish(n, prereqs):\n    pass\n\n"
            "print('true' if can_finish(n, prereqs) else 'false')\n"
        ),
        title="Course Schedule Feasibility",
        category="graphs",
    ),
    "word-search-grid": _Spec(
        oracle=oracle_word_search_grid,
        to_input=_to_input_word_search,
        format_output=_fmt_bool,
        statement=(
            "Given an `rows x cols` grid of lowercase letters and a target "
            "`word`, print `true` if `word` can be built by moving between "
            "**orthogonally adjacent** cells (up, down, left, right) without "
            "reusing the same cell twice, else `false`."
        ),
        constraints=["1 ≤ rows, cols ≤ 12", "1 ≤ word.length ≤ 15"],
        starter_code=(
            "import sys\n"
            "data = sys.stdin.read().split('\\n')\n"
            "rows, cols = map(int, data[0].split())\n"
            "grid = [list(data[1+i]) for i in range(rows)]\n"
            "word = data[1+rows]\n\n"
            "def exist(grid, word):\n    pass\n\n"
            "print('true' if exist(grid, word) else 'false')\n"
        ),
        title="Word Search in a Grid",
        category="backtracking",
    ),
    "distinct-subsets-count": _Spec(
        oracle=oracle_distinct_subsets_count,
        to_input=_to_input_subsets,
        format_output=_fmt_int,
        statement=(
            "Given a multiset of `n` integers (it may contain duplicates), "
            "print the number of **distinct subsets** of it, counting the "
            "empty subset. Two subsets are the same if they contain the same "
            "multiset of values regardless of which original duplicate index "
            "they came from."
        ),
        constraints=["0 ≤ n ≤ 20", "-10 ≤ nums[i] ≤ 10"],
        starter_code=(
            "import sys\n"
            "data = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:1+n]))\n\n"
            "def count_distinct_subsets(nums):\n    pass\n\n"
            "print(count_distinct_subsets(nums))\n"
        ),
        title="Count Distinct Subsets",
        category="backtracking",
    ),
    "house-robber-circular": _Spec(
        oracle=oracle_house_robber_circular,
        to_input=_to_input_house_robber,
        format_output=_fmt_int,
        statement=(
            "`n` houses are arranged in a **circle**; house `i` holds "
            "`nums[i]` money. You may not rob two adjacent houses, and "
            "because the houses form a circle, the first and last houses "
            "are also considered adjacent. Print the **maximum total** you "
            "can rob."
        ),
        constraints=["1 ≤ n ≤ 10^5", "0 ≤ nums[i] ≤ 1000"],
        starter_code=(
            "import sys\n"
            "data = sys.stdin.read().split()\n"
            "n = int(data[0])\nnums = list(map(int, data[1:1+n]))\n\n"
            "def rob_circular(nums):\n    pass\n\n"
            "print(rob_circular(nums))\n"
        ),
        title="House Robber in a Circular Street",
        category="dynamic-programming",
    ),
    "lowest-common-ancestor-binary-tree": _Spec(
        oracle=oracle_lca_binary_tree,
        to_input=_to_input_lca_tree,
        format_output=_fmt_int,
        statement=(
            "Given a **general binary tree** (no ordering property assumed) "
            "and two distinct values `p` and `q` guaranteed to exist in it, "
            "print the value of their **lowest common ancestor** — the "
            "deepest node that has both `p` and `q` as descendants (a node "
            "is considered a descendant of itself)."
        ),
        constraints=["2 ≤ number of nodes ≤ 10^4", "all values distinct", "p != q"],
        starter_code=(
            "import sys\n"
            "data = sys.stdin.read().split()\ntokens, p, q = data[:-2], int(data[-2]), int(data[-1])\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def lowest_common_ancestor(root, p, q):\n    pass\n\n"
            "print(lowest_common_ancestor(root, p, q))\n"
        ),
        title="Lowest Common Ancestor of a Binary Tree",
        category="tree",
    ),
    "construct-tree-preorder-inorder": _Spec(
        oracle=oracle_construct_tree_preorder_inorder,
        to_input=_to_input_construct_tree,
        format_output=_fmt_tree,
        statement=(
            "Given a binary tree's **preorder** and **inorder** traversal "
            "results as two space-separated integer arrays (all values "
            "distinct), reconstruct the tree and print it back out using "
            "this project's canonical level-order format (`null` marks a "
            "missing child)."
        ),
        constraints=["1 ≤ number of nodes ≤ 3000", "all values distinct"],
        starter_code=(
            "import sys\n"
            "lines = sys.stdin.read().split('\\n')\n"
            "preorder = list(map(int, lines[0].split()))\n"
            "inorder = list(map(int, lines[1].split()))\n\n"
            "def build_tree(preorder, inorder):\n    pass\n\n"
            "def serialize(root):\n"
            "    if root is None:\n        return []\n"
            "    out = [root.val]\n    queue = [root]\n    qi = 0\n"
            "    while qi < len(queue):\n"
            "        node = queue[qi]; qi += 1\n"
            "        for child in (node.left, node.right):\n"
            "            if child is None:\n                out.append(None)\n"
            "            else:\n                out.append(child.val); queue.append(child)\n"
            "    while out and out[-1] is None:\n        out.pop()\n    return out\n\n"
            "root = build_tree(preorder, inorder)\n"
            "print(' '.join('null' if v is None else str(v) for v in serialize(root)))\n"
        ),
        title="Construct Binary Tree from Preorder and Inorder Traversal",
        category="tree",
    ),
    "binary-tree-zigzag-level-order": _Spec(
        oracle=oracle_zigzag_level_order,
        to_input=_to_input_zigzag,
        format_output=_fmt_levels,
        statement=(
            "Given a binary tree, print its **zigzag level-order traversal**: "
            "one line per depth level, values space-separated; level 0 reads "
            "left-to-right, level 1 right-to-left, level 2 left-to-right, and "
            "so on, alternating every level."
        ),
        constraints=["0 ≤ number of nodes ≤ 2000"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def zigzag_level_order(root):\n    pass\n\n"
            "print('\\n'.join(' '.join(map(str, level)) for level in zigzag_level_order(root)))\n"
        ),
        title="Binary Tree Zigzag Level Order Traversal",
        category="tree",
    ),
}


# ── Case plans (one per slug, 40-test contract via testgen.py) ──────────────

def _plan_course_schedule(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_course_schedule

    def _acyclic_edges(n: int, m: int) -> list[tuple[int, int]]:
        # Only edges (a, b) with b < a in a random permutation order -> DAG,
        # guaranteed acyclic regardless of how many edges chosen.
        order = list(range(n))
        rng.shuffle(order)
        possible = [(order[i], order[j]) for i in range(n) for j in range(i) ]
        rng.shuffle(possible)
        return possible[:min(m, len(possible))]

    def _cyclic_edges(n: int) -> list[tuple[int, int]]:
        # A simple directed cycle 0->1->...->(n-1)->0 expressed as (a,b) pairs
        # meaning "b before a": edges (1,0), (2,1), ..., (0, n-1).
        edges = [((i + 1) % n, i) for i in range(n)]
        return edges

    def gen_random_dag_small():
        n = rng.randint(2, 8)
        m = rng.randint(0, n * (n - 1) // 2)
        return (n, _acyclic_edges(n, m))

    def gen_random_cyclic_small():
        n = rng.randint(2, 8)
        return (n, _cyclic_edges(n))

    def gen_random_mixed_stress():
        n = rng.randint(500, 2000)
        if rng.random() < 0.5:
            m = rng.randint(0, min(4000, n * (n - 1) // 2))
            return (n, _acyclic_edges(n, m))
        return (n, _cyclic_edges(n))

    visible = [
        (2, [(1, 0)]),
        (2, [(1, 0), (0, 1)]),
        (4, [(1, 0), (2, 0), (3, 1), (3, 2)]),
        (1, []),
        (3, [(1, 0), (2, 1), (0, 2)]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_random_dag_small, ti, seen)

    boundary_anchors = [
        (1, []),
        (2, []),
        (2, [(0, 1)]),
        (5, []),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random_dag_small, ti, seen)

    adversarial_anchors = [
        (2, [(0, 0)]),  # self-loop -> always a cycle
        (3, [(1, 0), (2, 1), (0, 2)]),  # simple 3-cycle
        (5, [(1, 0), (2, 0), (3, 0), (4, 0)]),  # star DAG, no cycle
        (4, [(1, 0), (2, 1), (3, 2), (1, 3)]),  # cycle hidden among later nodes
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_random_cyclic_small, ti, seen)

    mutation_anchors = [
        (3, [(1, 0), (2, 1)]),  # chain, no cycle (transitive check)
        (4, [(1, 0), (2, 1), (3, 2), (3, 0)]),  # extra redundant edge, still a DAG
        (3, [(1, 0), (2, 0), (2, 1)]),  # diamond-shaped DAG, no cycle
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random_dag_small, ti, seen)

    stress = tg.fill_unique(5, gen_random_mixed_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_word_search(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_word_search
    alphabet = "abcde"

    def _rand_grid(rows: int, cols: int) -> list[list[str]]:
        return [[rng.choice(alphabet) for _ in range(cols)] for _ in range(rows)]

    def _path_word(grid: list[list[str]], length: int) -> str:
        rows, cols = len(grid), len(grid[0])
        r, c = rng.randint(0, rows - 1), rng.randint(0, cols - 1)
        visited = {(r, c)}
        chars = [grid[r][c]]
        for _ in range(length - 1):
            options = []
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    options.append((nr, nc))
            if not options:
                break
            r, c = rng.choice(options)
            visited.add((r, c))
            chars.append(grid[r][c])
        return "".join(chars)

    def gen_findable_small():
        rows, cols = rng.randint(2, 5), rng.randint(2, 5)
        grid = _rand_grid(rows, cols)
        word = _path_word(grid, rng.randint(1, min(rows * cols, 5)))
        return (grid, word)

    def gen_random_small():
        rows, cols = rng.randint(2, 5), rng.randint(2, 5)
        grid = _rand_grid(rows, cols)
        word = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 5)))
        return (grid, word)

    def gen_stress():
        rows, cols = rng.randint(8, 12), rng.randint(8, 12)
        grid = _rand_grid(rows, cols)
        if rng.random() < 0.5:
            word = _path_word(grid, rng.randint(8, 15))
        else:
            word = "".join(rng.choice(alphabet) for _ in range(rng.randint(8, 15)))
        return (grid, word)

    visible = [
        ([["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]], "abef"),
        ([["a", "a"], ["a", "a"]], "aaaa"),
        ([["a", "b"], ["c", "d"]], "abd"),
        ([["z"]], "z"),
        ([["a", "b", "c"], ["d", "e", "f"]], "abcfed"),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_findable_small, ti, seen)

    boundary_anchors = [
        ([["a"]], "a"),
        ([["a"]], "b"),
        ([["a", "b"]], "ab"),
        ([["a"], ["b"]], "ab"),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random_small, ti, seen)

    adversarial_anchors = [
        ([["a", "a"], ["a", "a"]], "aaaaa"),  # word longer than any simple path can supply without reuse
        ([["a", "b", "a"], ["b", "a", "b"], ["a", "b", "a"]], "ababab"),  # needs real backtracking, dead-ends possible
        ([["a", "b"], ["c", "a"]], "aba"),  # revisiting the same-valued but different cell is required, not the same cell
        ([["c", "a", "a"], ["a", "a", "a"], ["a", "a", "a"]], "caaaaaaaa"),  # classic word-search adversarial trap grid
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([["a", "b"], ["c", "d"]], "ac"),  # only vertical adjacency valid, no diagonal
        ([["a", "b"], ["c", "d"]], "ad"),  # diagonal-looking but NOT adjacent -> must be false
        ([["a", "a"]], "aa"),  # two distinct same-letter cells, valid without reuse
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_distinct_subsets(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_subsets

    def gen_small():
        n = rng.randint(1, 6)
        return (tg.rand_int_array(rng, n, -5, 5),)

    def gen_stress():
        n = rng.randint(15, 20)
        return (tg.rand_int_array(rng, n, -10, 10),)

    visible = [
        ([1, 2, 2],),
        ([1, 2, 3],),
        ([0],),
        ([],),
        ([2, 2],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([],),
        ([5],),
        ([5, 5],),
        ([5, 5, 5],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([1, 1, 1, 1, 1],),  # all identical -> only 6 distinct subsets, not 2^5
        ([1, 1, 2, 2, 3],),  # mixed duplicate groups
        ([-1, -1, 0, 1, 1],),  # negative + zero + duplicates
        (list(range(-3, 4)),),  # all distinct -> exactly 2^n, sanity boundary vs dup logic
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 1],),  # naive 2^n counting would give 4 instead of correct 3
        ([1, 1, 1],),  # naive would give 8 instead of correct 4
        ([1, 2, 2],),  # from the problem statement itself: correct answer is 6
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_house_robber_circular(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_house_robber

    def gen_small():
        n = rng.randint(1, 8)
        return (tg.rand_int_array(rng, n, 0, 100),)

    def gen_stress():
        n = rng.randint(5000, 20000)
        return (tg.rand_int_array(rng, n, 0, 1000),)

    visible = [
        ([2, 3, 2],),
        ([1, 2, 3, 1],),
        ([1, 2, 3],),
        ([5],),
        ([5, 5],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_small, ti, seen)

    boundary_anchors = [
        ([0],),
        ([1],),
        ([0, 0],),
        ([1, 2],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_small, ti, seen)

    adversarial_anchors = [
        ([10, 1, 1, 10],),  # naive linear DP would rob both 10s (adjacent via wrap) illegally
        ([100, 1, 1, 1, 100],),  # first/last both huge, only one may be taken
        ([1, 100, 1, 1, 100, 1],),  # two high-value peaks near the wrap seam
        ([50] * 10,),  # all-equal, alternating pattern must respect circular seam
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 2, 3, 1],),  # answer differs from plain linear house-robber (4) -> circular answer is 4? verify via oracle
        ([2, 3, 2],),  # classic circular example, answer 3 not 4
        ([1, 1, 1, 1, 1, 1],),  # exposes off-by-one in "exclude first" vs "exclude last" merge
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_lca_binary_tree(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_lca_tree

    def _values_and_two_distinct(values: list[int | None]) -> tuple[list[int | None], int, int]:
        present = [v for v in values if v is not None]
        if len(present) < 2:
            # pad with a synthetic second node by duplicating structure is
            # unsafe (values must stay distinct) -- caller guarantees n>=2.
            raise OracleError("need at least 2 nodes for an LCA case")
        p, q = rng.sample(present, 2)
        return (values, p, q)

    def gen_random_small():
        n = rng.randint(2, 8)
        shapes = tg.tree_shape_patterns(rng, n)
        values = shapes["random_shape"]
        return _values_and_two_distinct(values)

    def gen_stress():
        n = rng.randint(2000, 5000)
        values = tg.rand_tree_level_order(rng, n)
        return _values_and_two_distinct(values)

    # Distinct-valued hand trees for anchors (values must all differ).
    tree_a = [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]  # classic LCA example shape
    tree_b = [1, 2]
    tree_c = [1, 2, 3, 4, 5, 6, 7]

    visible = [
        (tree_a, 5, 1),
        (tree_a, 6, 4),
        (tree_b, 1, 2),
        (tree_c, 4, 5),
        (tree_c, 4, 7),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_random_small, ti, seen)

    boundary_anchors = [
        ([1, 2], 1, 2),  # root + one child, targets are root and child
        ([1, None, 2], 1, 2),  # right-only chain of 2
        ([1, 2, None, 3], 1, 3),  # left-skewed chain, targets are root+leaf
        ([1, 2, 3, 4, 5, 6, 7], 2, 3),  # targets are the two direct root children
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random_small, ti, seen)

    adversarial_anchors = [
        ([1, 2, 3, 4, 5, 6, 7], 4, 5),  # LCA is a non-root internal node (2), not the root
        ([1, 2, 3, 4, 5, 6, 7], 4, 7),  # targets on opposite sides of the root -> LCA is root
        (tree_a, 7, 4),  # LCA is a direct parent (2) of both targets
        ([1, 2, None, 3, None, 4, None, 5], 1, 5),  # one target is an ancestor of the other (left-skewed chain)
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        (tree_a, 0, 8),  # targets are siblings deep in the right subtree
        ([1, 2, 3], 2, 3),  # minimal case: LCA is exactly the root
        ([1, None, 2, None, 3], 1, 3),  # right-skewed chain, targets root and deepest leaf
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_construct_tree(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_construct_tree

    def _preorder_inorder_from_values(values: list[int | None]) -> tuple[list[int], list[int]]:
        root = _build_tree(values)

        def preorder(node):
            if node is None:
                return []
            return [node.val] + preorder(node.left) + preorder(node.right)

        def inorder(node):
            if node is None:
                return []
            return inorder(node.left) + [node.val] + inorder(node.right)

        return preorder(root), inorder(root)

    def gen_random_small():
        n = rng.randint(1, 8)
        values = tg.rand_tree_level_order(rng, n, lo=1, hi=200)
        # ensure distinctness (rand_tree_level_order may repeat by chance)
        seen_vals: set[int] = set()
        distinct: list[int | None] = []
        pool = iter(rng.sample(range(1, 5000), n))
        for v in values:
            if v is None:
                distinct.append(None)
            else:
                distinct.append(next(pool))
        return _preorder_inorder_from_values(distinct)

    def gen_stress():
        n = rng.randint(1500, 3000)
        shapes = tg.tree_shape_patterns(rng, n, lo=1, hi=5)
        values = shapes["random_shape"]
        pool = iter(rng.sample(range(1, 200_000), n))
        distinct = [None if v is None else next(pool) for v in values]
        return _preorder_inorder_from_values(distinct)

    visible = [
        ([3, 9, 20, 15, 7], [9, 3, 15, 20, 7]),
        ([1, 2], [2, 1]),
        ([1], [1]),
        ([1, 2, 3], [2, 1, 3]),
        ([5, 3, 1, 4, 6, 7], [1, 3, 4, 5, 6, 7]),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_random_small, ti, seen)

    boundary_anchors = [
        ([1], [1]),
        ([1, 2], [1, 2]),  # right-only chain (inorder == preorder means pure right skew)
        ([2, 1], [1, 2]),  # left-only chain of 2
        ([1, 2, 3, 4], [1, 2, 3, 4]),  # fully right-skewed chain of 4
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random_small, ti, seen)

    adversarial_anchors = [
        ([4, 3, 2, 1], [1, 2, 3, 4]),  # fully left-skewed chain of 4
        ([3, 1, 2, 5, 4], [1, 2, 3, 4, 5]),  # mixed shape, non-trivial split points
        ([10, 5, 1, 3, 8, 15, 12, 20], [1, 3, 5, 8, 10, 12, 15, 20]),  # balanced BST-shaped tree (values happen to be sorted in-order)
        ([50, -10, -20, 30], [-20, -10, 50, 30]),  # negative values mixed with positive
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 2, 3], [2, 1, 3]),  # root has both children -- catches "always attach right only" bug
        ([2, 1, 3], [1, 2, 3]),  # root's inorder split at index 1, not always mid
        ([1, 2], [2, 1]),  # single left child only
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


def _plan_zigzag_level_order(rng: random.Random) -> tg.CasePlan:
    seen: set[str] = set()
    ti = _to_input_zigzag

    def gen_random_small():
        n = rng.randint(0, 10)
        return (tg.rand_tree_level_order(rng, n),) if n > 0 else ([],)

    def gen_stress():
        n = rng.randint(2000, 5000)
        return (tg.rand_tree_level_order(rng, n),)

    visible = [
        ([3, 9, 20, None, None, 15, 7],),
        ([1],),
        ([],),
        ([1, 2, 3],),
        ([1, 2, 3, 4, 5, 6, 7],),
    ]
    for a in visible:
        seen.add(tg._dedup_key(ti(*a)))

    basic = tg.fill_unique(7, gen_random_small, ti, seen)

    boundary_anchors = [
        ([],),
        ([1],),
        ([1, 2],),
        ([1, None, 2],),
    ]
    boundary_anchors = tg.register(boundary_anchors, ti, seen)
    boundary = boundary_anchors + tg.fill_unique(8 - len(boundary_anchors), gen_random_small, ti, seen)

    adversarial_anchors = [
        ([1, 2, 3, 4, 5, 6, 7],),  # 3 full levels -- exercises both L->R and R->L
        ([1, 2, None, 3, None, 4, None, 5],),  # left-skewed chain, every level has 1 node (order shouldn't matter but reversal logic must still run)
        ([1, None, 2, None, 3, None, 4],),  # right-skewed chain
        (list(range(1, 16)),),  # perfect 4-level tree, reversal parity must be exactly right by depth 3
    ]
    adversarial_anchors = tg.register(adversarial_anchors, ti, seen)
    adversarial = adversarial_anchors + tg.fill_unique(8 - len(adversarial_anchors), gen_stress, ti, seen)

    mutation_anchors = [
        ([1, 2, 3],),  # naive "always L->R" bug caught: level 1 should print "3 2"
        ([1, 2, 3, 4, 5, 6, 7],),  # naive "reverse every level" bug caught: level 0 stays "1"
        ([5, 3, 8, 1, 4, 7, 9],),  # 3-level tree verifying alternation resets correctly at level 2
    ]
    mutation_anchors = tg.register(mutation_anchors, ti, seen)
    mutation = mutation_anchors + tg.fill_unique(7 - len(mutation_anchors), gen_random_small, ti, seen)

    stress = tg.fill_unique(5, gen_stress, ti, seen)

    return {
        "visible": visible, "basic": basic, "boundary": boundary,
        "adversarial": adversarial, "mutation": mutation, "stress": stress,
    }


_PLANS: dict[str, Callable[[random.Random], tg.CasePlan]] = {
    "course-schedule-feasible": _plan_course_schedule,
    "word-search-grid": _plan_word_search,
    "distinct-subsets-count": _plan_distinct_subsets,
    "house-robber-circular": _plan_house_robber_circular,
    "lowest-common-ancestor-binary-tree": _plan_lca_binary_tree,
    "construct-tree-preorder-inorder": _plan_construct_tree,
    "binary-tree-zigzag-level-order": _plan_zigzag_level_order,
}


# ── Builder function (mirrors sliding_window_variants.py's pattern) ─────────

def build_famous_graphs_trees_lists_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue

        plan_fn = _PLANS.get(slug)
        if plan_fn is None:
            skipped.append((slug, "no 40-test case plan registered"))
            continue

        try:
            rng = tg.problem_rng(slug)
            case_plan = plan_fn(rng)
            test_spec = tg.TestSpec(
                oracle=spec.oracle, to_input=spec.to_input, format_output=spec.format_output,
            )
            test_cases = tg.build_forty(slug, test_spec, case_plan)
        except (OracleError, tg.TestPlanError) as exc:
            skipped.append((slug, str(exc)))
            continue

        if not test_cases:
            skipped.append((slug, "no test cases produced"))
            continue

        problem = {
            "id": slug,
            "title": spec.title,
            "difficulty": spec.difficulty,
            "category": spec.category,
            "algorithm_slug": None,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": "Think about which classic pattern this maps to, then adapt it to this problem's exact constraint."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped


# ── Reference (correct) and wrong (plausible-bug) solutions ─────────────────
# Independently written from scratch, NOT calling into the oracle functions
# above -- matches verify_atlascode_family.py's three-level verification
# style (Level 3: real subprocess judge run).

_TREE_PARSE_REF = (
    "import sys\n"
    "class Node:\n"
    "    def __init__(self, val):\n        self.val = val; self.left = None; self.right = None\n"
    "def parse(tokens):\n"
    "    if not tokens or tokens[0] == 'null':\n        return None\n"
    "    root = Node(int(tokens[0]))\n"
    "    q = [root]; i = 1; qi = 0\n"
    "    while qi < len(q) and i < len(tokens):\n"
    "        node = q[qi]; qi += 1\n"
    "        if i < len(tokens):\n"
    "            if tokens[i] != 'null':\n                node.left = Node(int(tokens[i])); q.append(node.left)\n"
    "            i += 1\n"
    "        if i < len(tokens):\n"
    "            if tokens[i] != 'null':\n                node.right = Node(int(tokens[i])); q.append(node.right)\n"
    "            i += 1\n"
    "    return root\n"
)

_TREE_SERIALIZE_REF = (
    "def serialize(root):\n"
    "    if root is None:\n        return []\n"
    "    out = [root.val]\n    queue = [root]\n    qi = 0\n"
    "    while qi < len(queue):\n"
    "        node = queue[qi]; qi += 1\n"
    "        for child in (node.left, node.right):\n"
    "            if child is None:\n                out.append(None)\n"
    "            else:\n                out.append(child.val); queue.append(child)\n"
    "    while out and out[-1] is None:\n        out.pop()\n    return out\n"
)


REFERENCE_SOLUTIONS: dict[str, str] = {
    "course-schedule-feasible": (
        "import sys\n"
        "from collections import deque\n"
        "data = sys.stdin.read().split('\\n')\n"
        "n, m = map(int, data[0].split())\n"
        "adj = [[] for _ in range(n)]\n"
        "indeg = [0] * n\n"
        "for i in range(m):\n"
        "    a, b = map(int, data[1 + i].split())\n"
        "    adj[b].append(a)\n    indeg[a] += 1\n"
        "q = deque(i for i in range(n) if indeg[i] == 0)\n"
        "seen = 0\n"
        "while q:\n"
        "    u = q.popleft()\n    seen += 1\n"
        "    for v in adj[u]:\n"
        "        indeg[v] -= 1\n"
        "        if indeg[v] == 0:\n            q.append(v)\n"
        "print('true' if seen == n else 'false')\n"
    ),
    "word-search-grid": (
        "import sys\n"
        "data = sys.stdin.read().split('\\n')\n"
        "rows, cols = map(int, data[0].split())\n"
        "grid = [list(data[1 + i]) for i in range(rows)]\n"
        "word = data[1 + rows]\n"
        "def dfs(r, c, idx, visited):\n"
        "    if grid[r][c] != word[idx]:\n        return False\n"
        "    if idx == len(word) - 1:\n        return True\n"
        "    visited.add((r, c))\n"
        "    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n"
        "        nr, nc = r+dr, c+dc\n"
        "        if 0<=nr<rows and 0<=nc<cols and (nr,nc) not in visited:\n"
        "            if dfs(nr, nc, idx+1, visited):\n"
        "                visited.discard((r, c)); return True\n"
        "    visited.discard((r, c))\n    return False\n"
        "found = False\n"
        "if word == '':\n    found = True\n"
        "else:\n"
        "    for r in range(rows):\n"
        "        for c in range(cols):\n"
        "            if dfs(r, c, 0, set()):\n"
        "                found = True; break\n"
        "        if found:\n            break\n"
        "print('true' if found else 'false')\n"
    ),
    "distinct-subsets-count": (
        "import sys\n"
        "from collections import Counter\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:1+n]))\n"
        "counts = Counter(nums)\n"
        "total = 1\n"
        "for k in counts.values():\n"
        "    total *= (k + 1)\n"
        "print(total)\n"
    ),
    "house-robber-circular": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:1+n]))\n"
        "def linear(vals):\n"
        "    prev, curr = 0, 0\n"
        "    for v in vals:\n"
        "        prev, curr = curr, max(curr, prev + v)\n"
        "    return curr\n"
        "if n == 0:\n    print(0)\n"
        "elif n == 1:\n    print(nums[0])\n"
        "else:\n    print(max(linear(nums[:-1]), linear(nums[1:])))\n"
    ),
    "lowest-common-ancestor-binary-tree": (
        _TREE_PARSE_REF
        + "data = sys.stdin.read().split()\ntokens, p, q = data[:-2], int(data[-2]), int(data[-1])\n"
        "root = parse(tokens)\n"
        "def find(node):\n"
        "    if node is None or node.val == p or node.val == q:\n        return node\n"
        "    left = find(node.left)\n    right = find(node.right)\n"
        "    if left is not None and right is not None:\n        return node\n"
        "    return left if left is not None else right\n"
        "print(find(root).val)\n"
    ),
    "construct-tree-preorder-inorder": (
        _TREE_PARSE_REF
        + _TREE_SERIALIZE_REF
        + "lines = sys.stdin.read().split('\\n')\n"
        "preorder = list(map(int, lines[0].split()))\n"
        "inorder = list(map(int, lines[1].split()))\n"
        "index_of = {v: i for i, v in enumerate(inorder)}\n"
        "pre_iter = iter(preorder)\n"
        "def build(lo, hi):\n"
        "    if lo > hi:\n        return None\n"
        "    root_val = next(pre_iter)\n"
        "    node = Node(root_val)\n"
        "    mid = index_of[root_val]\n"
        "    node.left = build(lo, mid - 1)\n"
        "    node.right = build(mid + 1, hi)\n"
        "    return node\n"
        "root = build(0, len(inorder) - 1)\n"
        "print(' '.join('null' if v is None else str(v) for v in serialize(root)))\n"
    ),
    "binary-tree-zigzag-level-order": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "levels = []\n"
        "frontier = [root] if root else []\n"
        "ltr = True\n"
        "while frontier:\n"
        "    vals = [n.val for n in frontier]\n"
        "    if not ltr:\n        vals.reverse()\n"
        "    levels.append(vals)\n"
        "    nxt = []\n"
        "    for n in frontier:\n"
        "        if n.left:\n            nxt.append(n.left)\n"
        "        if n.right:\n            nxt.append(n.right)\n"
        "    frontier = nxt\n    ltr = not ltr\n"
        "print('\\n'.join(' '.join(map(str, level)) for level in levels))\n"
    ),
}


WRONG_SOLUTIONS: dict[str, str] = {
    # Bug: only checks each edge for a DIRECT 2-cycle (a->b and b->a), missing
    # longer transitive cycles entirely.
    "course-schedule-feasible": (
        "import sys\n"
        "data = sys.stdin.read().split('\\n')\n"
        "n, m = map(int, data[0].split())\n"
        "edges = [tuple(map(int, data[1 + i].split())) for i in range(m)]\n"
        "edge_set = set(edges)\n"
        "ok = True\n"
        "for a, b in edges:\n"
        "    if (b, a) in edge_set:\n"
        "        ok = False\n"
        "print('true' if ok else 'false')\n"
    ),
    # Bug: marks cells visited permanently (never backtracks/unmarks), so a
    # cell used on a failed path can never be reused by another path that
    # legitimately needs it.
    "word-search-grid": (
        "import sys\n"
        "data = sys.stdin.read().split('\\n')\n"
        "rows, cols = map(int, data[0].split())\n"
        "grid = [list(data[1 + i]) for i in range(rows)]\n"
        "word = data[1 + rows]\n"
        "visited_global = set()\n"
        "def dfs(r, c, idx):\n"
        "    if grid[r][c] != word[idx]:\n        return False\n"
        "    if idx == len(word) - 1:\n        return True\n"
        "    visited_global.add((r, c))\n"
        "    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n"
        "        nr, nc = r+dr, c+dc\n"
        "        if 0<=nr<rows and 0<=nc<cols and (nr,nc) not in visited_global:\n"
        "            if dfs(nr, nc, idx+1):\n                return True\n"
        "    return False\n"
        "found = False\n"
        "if word == '':\n    found = True\n"
        "else:\n"
        "    for r in range(rows):\n"
        "        for c in range(cols):\n"
        "            if dfs(r, c, 0):\n"
        "                found = True; break\n"
        "        if found:\n            break\n"
        "print('true' if found else 'false')\n"
    ),
    # Bug: naively computes 2^n instead of deduping subsets that arise from
    # duplicate values (correct only when all values happen to be distinct).
    "distinct-subsets-count": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "print(2 ** n)\n"
    ),
    # Bug: treats the houses as a plain linear array, ignoring the circular
    # adjacency between the first and last house entirely.
    "house-robber-circular": (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\nnums = list(map(int, data[1:1+n]))\n"
        "prev, curr = 0, 0\n"
        "for v in nums:\n"
        "    prev, curr = curr, max(curr, prev + v)\n"
        "print(curr)\n"
    ),
    # Bug: returns the FIRST node matching p or q found during the DFS without
    # checking whether both subtrees actually contain a match -- so when one
    # target is an ancestor of the other deep in one subtree, or when the
    # true LCA is an internal node with each target in a different subtree,
    # this can print the wrong (too-shallow or wrong-branch) node.
    "lowest-common-ancestor-binary-tree": (
        _TREE_PARSE_REF
        + "data = sys.stdin.read().split()\ntokens, p, q = data[:-2], int(data[-2]), int(data[-1])\n"
        "root = parse(tokens)\n"
        "def find_first(node):\n"
        "    if node is None:\n        return None\n"
        "    if node.val == p or node.val == q:\n        return node\n"
        "    left = find_first(node.left)\n"
        "    if left is not None:\n        return left\n"
        "    return find_first(node.right)\n"
        "print(find_first(root).val)\n"
    ),
    # Bug: always attaches every remaining subtree entirely to the LEFT
    # child, never using the inorder split index to decide left vs right
    # sizes -- produces a left-skewed tree unless the true shape already is
    # one, so it fails serialization comparison on any tree with a right
    # child.
    "construct-tree-preorder-inorder": (
        _TREE_PARSE_REF
        + _TREE_SERIALIZE_REF
        + "lines = sys.stdin.read().split('\\n')\n"
        "preorder = list(map(int, lines[0].split()))\n"
        "inorder = list(map(int, lines[1].split()))\n"
        "pre_iter = iter(preorder)\n"
        "def build(count):\n"
        "    if count <= 0:\n        return None\n"
        "    try:\n        root_val = next(pre_iter)\n    except StopIteration:\n        return None\n"
        "    node = Node(root_val)\n"
        "    node.left = build(count - 1)\n"
        "    return node\n"
        "root = build(len(inorder))\n"
        "print(' '.join('null' if v is None else str(v) for v in serialize(root)))\n"
    ),
    # Bug: always reverses every level's output (i.e. treats every level as
    # right-to-left), instead of alternating starting with left-to-right at
    # level 0.
    "binary-tree-zigzag-level-order": (
        _TREE_PARSE_REF
        + "root = parse(sys.stdin.read().split())\n"
        "levels = []\n"
        "frontier = [root] if root else []\n"
        "while frontier:\n"
        "    vals = [n.val for n in frontier]\n"
        "    vals.reverse()\n"
        "    levels.append(vals)\n"
        "    nxt = []\n"
        "    for n in frontier:\n"
        "        if n.left:\n            nxt.append(n.left)\n"
        "        if n.right:\n            nxt.append(n.right)\n"
        "    frontier = nxt\n"
        "print('\\n'.join(' '.join(map(str, level)) for level in levels))\n"
    ),
}
