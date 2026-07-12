"""
Tree pattern-problem family. Establishes ONE canonical tree serialization
format shared by every tree problem in AtlasCode (per docs/atlascode-progress.md
"Define a canonical tree serialization format" — not done before this batch):
level-order list with the literal token `null` for a missing child (LeetCode
convention), e.g. `3 9 20 null null 15 7`.

3 of 15 link to real canonical algorithms already in the registry
(`diameter`, `lca`, `level-order`) — genuine new coverage, promoted the same
way `is-bipartite`/`bipartite-check` was in bfs_graph_variants.py. The rest
are `origin_type = PATTERN_PROBLEM` (`algorithm_slug=None`) since no single
canonical algorithm backs "binary tree recursion pattern" generically.
`lowest-common-ancestor-bst` and `kth-smallest-in-bst` specifically require a
BST (not a general binary tree) so their answers are well-defined and unique.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .tree_variants_testdata import TREE_VARIANT_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_bool(answer: object) -> str:
    return "true" if answer else "false"


def _fmt_int_list(answer: object) -> str:
    return " ".join(str(x) for x in answer)


def _fmt_levels(answer: object) -> str:
    return "\n".join(" ".join(str(x) for x in level) for level in answer)


def _tree_line(values: list) -> str:
    return " ".join("null" if v is None else str(v) for v in values)


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


@dataclass(frozen=True)
class _Spec:
    algorithm_slug: str | None
    oracle: Callable[..., object]
    cases: list[tuple[str, tuple, bool]]
    statement: str
    constraints: list[str]
    starter_code: str
    title: str
    difficulty: str = "Medium"
    estimated_minutes: int = 25
    format_output: Callable[[object], str] = _fmt_int


_TREE_A = [3, 9, 20, None, None, 15, 7]

_SPECS: dict[str, _Spec] = {
    "max-depth-binary-tree": _Spec(
        algorithm_slug=None,
        oracle=oracles.max_depth_binary_tree,
        cases=[
            (_tree_line(_TREE_A), (_TREE_A,), False),
            (_tree_line([1, None, 2]), ([1, None, 2],), False),
            (_tree_line([]), ([],), True),
            (_tree_line([1]), ([1],), True),
        ],
        statement="Given a binary tree, print its **maximum depth** (number of nodes on the longest root-to-leaf path).",
        constraints=["0 ≤ number of nodes ≤ 10^4"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def max_depth(root):\n    pass\n\nprint(max_depth(root))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        title="Maximum Depth of Binary Tree",
    ),
    "diameter-of-binary-tree": _Spec(
        algorithm_slug="diameter",
        oracle=oracles.diameter_of_binary_tree,
        cases=[
            (_tree_line([1, 2, 3, 4, 5]), ([1, 2, 3, 4, 5],), False),
            (_tree_line([1, 2]), ([1, 2],), False),
            (_tree_line([1]), ([1],), True),
            (_tree_line([3, None, 7, 6, 0, 2, None, 5]), ([3, None, 7, 6, 0, 2, None, 5],), True),
        ],
        statement="Given a binary tree, print the **diameter** — the length (in edges) of the longest path between any two nodes.",
        constraints=["1 ≤ number of nodes ≤ 10^4"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def diameter(root):\n    pass\n\nprint(diameter(root))\n"
        ),
        title="Diameter of Binary Tree",
    ),
    "is-balanced-binary-tree": _Spec(
        algorithm_slug=None,
        oracle=oracles.is_balanced_binary_tree,
        cases=[
            (_tree_line(_TREE_A), (_TREE_A,), False),
            (_tree_line([1, 2, 2, 3, 3, None, None, 4, 4]), ([1, 2, 2, 3, 3, None, None, 4, 4],), False),
            (_tree_line([]), ([],), True),
            (_tree_line([2, 2, 0, 8, None, 8, None, 7]), ([2, 2, 0, 8, None, 8, None, 7],), True),
        ],
        statement="Given a binary tree, print `true` if it is **height-balanced** (every node's two subtree heights differ by at most 1), else `false`.",
        constraints=["0 ≤ number of nodes ≤ 5000"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def is_balanced(root):\n    pass\n\nprint('true' if is_balanced(root) else 'false')\n"
        ),
        format_output=_fmt_bool,
        title="Balanced Binary Tree",
    ),
    "is-valid-bst": _Spec(
        algorithm_slug=None,
        oracle=oracles.is_valid_bst,
        cases=[
            (_tree_line([2, 1, 3]), ([2, 1, 3],), False),
            (_tree_line([5, 1, 4, None, None, 3, 6]), ([5, 1, 4, None, None, 3, 6],), False),
            (_tree_line([1]), ([1],), True),
            (_tree_line([4, 0, None, None, 5, None, 9]), ([4, 0, None, None, 5, None, 9],), True),
        ],
        statement="Given a binary tree, print `true` if it satisfies the **binary search tree** property, else `false`.",
        constraints=["1 ≤ number of nodes ≤ 10^4"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def is_valid_bst(root):\n    pass\n\nprint('true' if is_valid_bst(root) else 'false')\n"
        ),
        format_output=_fmt_bool,
        title="Validate Binary Search Tree",
    ),
    "is-symmetric-tree": _Spec(
        algorithm_slug=None,
        oracle=oracles.is_symmetric_tree,
        cases=[
            (_tree_line([1, 2, 2, 3, 4, 4, 3]), ([1, 2, 2, 3, 4, 4, 3],), False),
            (_tree_line([1, 2, 2, None, 3, None, 3]), ([1, 2, 2, None, 3, None, 3],), False),
            (_tree_line([1]), ([1],), True),
            (_tree_line([]), ([],), True),
        ],
        statement="Given a binary tree, print `true` if it is a **mirror image** of itself around its center, else `false`.",
        constraints=["0 ≤ number of nodes ≤ 1000"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def is_symmetric(root):\n    pass\n\nprint('true' if is_symmetric(root) else 'false')\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
        format_output=_fmt_bool,
        title="Symmetric Tree",
    ),
    "invert-tree-preorder": _Spec(
        algorithm_slug=None,
        oracle=oracles.invert_tree_preorder,
        cases=[
            (_tree_line([4, 2, 7, 1, 3, 6, 9]), ([4, 2, 7, 1, 3, 6, 9],), False),
            (_tree_line([2, 1, 3]), ([2, 1, 3],), False),
            (_tree_line([]), ([],), True),
            (_tree_line([1]), ([1],), True),
        ],
        statement="Given a binary tree, invert it (swap every left/right child) and print the **preorder traversal** of the result, space-separated.",
        constraints=["0 ≤ number of nodes ≤ 100"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def invert_preorder(root):\n    pass\n\n"
            "print(' '.join(map(str, invert_preorder(root))))\n"
        ),
        difficulty="Easy",
        estimated_minutes=20,
        format_output=_fmt_int_list,
        title="Invert Binary Tree (Preorder Output)",
    ),
    "path-sum-exists": _Spec(
        algorithm_slug=None,
        oracle=oracles.path_sum_exists,
        cases=[
            (_tree_line([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]) + " 22",
             ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22), False),
            (_tree_line([1, 2, 3]) + " 5", ([1, 2, 3], 5), False),
            (_tree_line([1, 2]) + " 1", ([1, 2], 1), True),
            (_tree_line([]) + " 0", ([], 0), True),
        ],
        statement="Given a binary tree and an integer `target`, print `true` if some **root-to-leaf path** sums exactly to `target`, else `false`.",
        constraints=["0 ≤ number of nodes ≤ 5000"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\ntokens, target = data[:-1], int(data[-1])\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def has_path_sum(root, target):\n    pass\n\n"
            "print('true' if has_path_sum(root, target) else 'false')\n"
        ),
        format_output=_fmt_bool,
        title="Path Sum",
    ),
    "count-tree-nodes": _Spec(
        algorithm_slug=None,
        oracle=oracles.count_tree_nodes,
        cases=[
            (_tree_line([1, None, 2]), ([1, None, 2],), False),
            (_tree_line([1, 2, 3, 4, 5]), ([1, 2, 3, 4, 5],), False),
            (_tree_line([]), ([],), True),
            (_tree_line([1]), ([1],), True),
        ],
        statement="Given a binary tree, print the **total number of nodes**.",
        constraints=["0 ≤ number of nodes ≤ 10^4"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def count_nodes(root):\n    pass\n\nprint(count_nodes(root))\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        title="Count Complete Tree Nodes",
    ),
    "lowest-common-ancestor-bst": _Spec(
        algorithm_slug="lca",
        oracle=oracles.lowest_common_ancestor_bst,
        cases=[
            (_tree_line([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5]) + " 2 8",
             ([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 8), False),
            (_tree_line([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5]) + " 2 4",
             ([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 4), False),
            (_tree_line([2, 1]) + " 1 2", ([2, 1], 1, 2), True),
            (_tree_line([4, 2, 6, 1, 3, 5, 7]) + " 1 3", ([4, 2, 6, 1, 3, 5, 7], 1, 3), True),
        ],
        statement="Given a **binary search tree** and two values `p`, `q` known to exist in it, print the value of their **lowest common ancestor**.",
        constraints=["2 ≤ number of nodes ≤ 10^4", "all values distinct"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\ntokens, p, q = data[:-2], int(data[-2]), int(data[-1])\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def lowest_common_ancestor(root, p, q):\n    pass\n\n"
            "print(lowest_common_ancestor(root, p, q))\n"
        ),
        title="Lowest Common Ancestor of a BST",
    ),
    "kth-smallest-in-bst": _Spec(
        algorithm_slug=None,
        oracle=oracles.kth_smallest_in_bst,
        cases=[
            (_tree_line([3, 1, 4, None, 2]) + " 1", ([3, 1, 4, None, 2], 1), False),
            (_tree_line([5, 3, 6, 2, 4, None, None, 1]) + " 3", ([5, 3, 6, 2, 4, None, None, 1], 3), False),
            (_tree_line([1]) + " 1", ([1], 1), True),
            (_tree_line([2, 1, 3]) + " 3", ([2, 1, 3], 3), True),
        ],
        statement="Given a **binary search tree** and an integer `k`, print the `k`-th smallest value in it (1-indexed).",
        constraints=["1 ≤ k ≤ number of nodes ≤ 10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\ntokens, k = data[:-1], int(data[-1])\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def kth_smallest(root, k):\n    pass\n\nprint(kth_smallest(root, k))\n"
        ),
        title="Kth Smallest Element in a BST",
    ),
    "level-order-traversal": _Spec(
        algorithm_slug="level-order",
        oracle=oracles.level_order_traversal,
        cases=[
            (_tree_line(_TREE_A), (_TREE_A,), False),
            (_tree_line([1]), ([1],), False),
            (_tree_line([]), ([],), True),
            (_tree_line([1, 2, 3, 4]), ([1, 2, 3, 4],), True),
        ],
        statement="Given a binary tree, print its **level-order traversal**: one line per depth level, values space-separated top to bottom.",
        constraints=["0 ≤ number of nodes ≤ 2000"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def level_order(root):\n    pass\n\n"
            "print('\\n'.join(' '.join(map(str, level)) for level in level_order(root)))\n"
        ),
        format_output=_fmt_levels,
        title="Binary Tree Level Order Traversal",
    ),
    "right-side-view": _Spec(
        algorithm_slug=None,
        oracle=oracles.right_side_view,
        cases=[
            (_tree_line([1, 2, 3, None, 5, None, 4]), ([1, 2, 3, None, 5, None, 4],), False),
            (_tree_line([1, None, 3]), ([1, None, 3],), False),
            (_tree_line([]), ([],), True),
            (_tree_line([1, 2]), ([1, 2],), True),
        ],
        statement="Given a binary tree, print the value of the **rightmost node** visible at each depth level, from top to bottom, space-separated.",
        constraints=["0 ≤ number of nodes ≤ 100"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def right_side_view(root):\n    pass\n\n"
            "print(' '.join(map(str, right_side_view(root))))\n"
        ),
        format_output=_fmt_int_list,
        title="Binary Tree Right Side View",
    ),
    "same-tree": _Spec(
        algorithm_slug=None,
        oracle=oracles.same_tree,
        cases=[
            (_tree_line([1, 2, 3]) + "\n" + _tree_line([1, 2, 3]), ([1, 2, 3], [1, 2, 3]), False),
            (_tree_line([1, 2]) + "\n" + _tree_line([1, None, 2]), ([1, 2], [1, None, 2]), False),
            (_tree_line([]) + "\n" + _tree_line([]), ([], []), True),
            (_tree_line([1, 2, 1]) + "\n" + _tree_line([1, 1, 2]), ([1, 2, 1], [1, 1, 2]), True),
        ],
        statement="Given two binary trees, print `true` if they are **structurally identical** with the same node values, else `false`.",
        constraints=["0 ≤ number of nodes ≤ 100 (each tree)"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "tokens1, tokens2 = lines[0].split(), lines[1].split()\n\n"
            + _parse_tree_code()
            + "root1 = parse_tree(tokens1)\nroot2 = parse_tree(tokens2)\n\n"
            "def is_same_tree(p, q):\n    pass\n\n"
            "print('true' if is_same_tree(root1, root2) else 'false')\n"
        ),
        difficulty="Easy",
        estimated_minutes=15,
        format_output=_fmt_bool,
        title="Same Tree",
    ),
    "sum-root-to-leaf-numbers": _Spec(
        algorithm_slug=None,
        oracle=oracles.sum_root_to_leaf_numbers,
        cases=[
            (_tree_line([1, 2, 3]), ([1, 2, 3],), False),
            (_tree_line([4, 9, 0, 5, 1]), ([4, 9, 0, 5, 1],), False),
            (_tree_line([0]), ([0],), True),
            (_tree_line([1]), ([1],), True),
        ],
        statement="Given a binary tree with single-digit node values, treat each root-to-leaf path as a decimal number; print the **sum over all such numbers**.",
        constraints=["1 ≤ number of nodes ≤ 1000", "0 ≤ node value ≤ 9"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def sum_numbers(root):\n    pass\n\nprint(sum_numbers(root))\n"
        ),
        title="Sum Root to Leaf Numbers",
    ),
    "binary-tree-max-path-sum": _Spec(
        algorithm_slug=None,
        oracle=oracles.binary_tree_max_path_sum,
        cases=[
            (_tree_line([1, 2, 3]), ([1, 2, 3],), False),
            (_tree_line([-10, 9, 20, None, None, 15, 7]), ([-10, 9, 20, None, None, 15, 7],), False),
            (_tree_line([-3]), ([-3],), True),
            (_tree_line([2, -1]), ([2, -1],), True),
        ],
        statement="Given a binary tree with possibly negative values, print the **maximum path sum** of any non-empty path (a path may start and end at any node, need not pass through the root).",
        constraints=["1 ≤ number of nodes ≤ 3×10^4", "-1000 ≤ node value ≤ 1000"],
        starter_code=(
            "import sys\ntokens = sys.stdin.read().split()\n\n"
            + _parse_tree_code()
            + "root = parse_tree(tokens)\n\n"
            "def max_path_sum(root):\n    pass\n\nprint(max_path_sum(root))\n"
        ),
        difficulty="Hard",
        estimated_minutes=35,
        title="Binary Tree Maximum Path Sum",
    ),
}


def build_tree_variant_problems(
    algorithms: list[RegisteredAlgorithm],
    existing_problem_ids: set[str],
) -> tuple[list[tuple[dict, list[dict]]], list[tuple[str, str]]]:
    by_slug = {r.slug: r for r in algorithms}
    problems: list[tuple[dict, list[dict]]] = []
    skipped: list[tuple[str, str]] = []

    for slug, spec in _SPECS.items():
        if slug in existing_problem_ids:
            skipped.append((slug, "problem slug already exists"))
            continue
        reg = by_slug.get(spec.algorithm_slug) if spec.algorithm_slug else None
        if spec.algorithm_slug and reg is None:
            skipped.append((slug, f"linked algorithm '{spec.algorithm_slug}' not found in canonical registry"))
            continue

        test_plan = TREE_VARIANT_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in tree_variants_testdata.py"))
            continue
        to_input, format_output, plan_fn = test_plan
        try:
            rng = tg.problem_rng(slug)
            case_plan = plan_fn(rng)
            test_spec = tg.TestSpec(oracle=spec.oracle, to_input=to_input, format_output=format_output)
            test_cases = tg.build_forty(slug, test_spec, case_plan)
        except (oracles.OracleError, tg.TestPlanError) as exc:
            skipped.append((slug, str(exc)))
            continue

        if not test_cases:
            skipped.append((slug, "no test cases produced"))
            continue

        intuition = reg.manifest.get("intuition", "") or reg.manifest.get("description", "") if reg else ""
        problem = {
            "id": slug,
            "title": spec.title,
            "difficulty": spec.difficulty,
            "category": "tree",
            "algorithm_slug": spec.algorithm_slug,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": intuition[:300] or "Recursion mirrors the tree's own structure — think base case (None) and combine child results."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
