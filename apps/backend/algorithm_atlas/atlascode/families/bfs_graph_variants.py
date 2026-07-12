"""
BFS/graph variant family factory.

`is-bipartite` links to the real canonical algorithm `bipartite-check`
(graph category, previously PROPERTY_JUDGE-by-default) — its answer is a
provable unique boolean, so this promotes genuine new canonical coverage
rather than just adding another pattern problem. The other six are
`origin_type = ALGORITHM_VARIANT` of the technique `bfs` (grid/multi-source/
implicit-graph BFS shortest-path family) — deliberately NOT claimed as
canonical `bfs` re-implementations since `bfs` is already curated; they just
reuse its `algorithm_slug` for the learning/visualization link, matching the
established multi-problem-per-algorithm pattern from binary-search-variants.

Every non-scalar-looking task here (rotten oranges, 0/1 matrix, islands) is
deliberately phrased to return a SCALAR (minutes / max distance / count),
never "the" set of infected cells or "the" island shapes — avoiding the
multi-valid-answer trap that keeps `graph`/`tree`/`backtracking` in
PROPERTY_JUDGE for everything else.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .. import independent_oracles as oracles
from .. import testgen as tg
from .bfs_graph_variants_testdata import BFS_GRAPH_TEST_PLANS
from ...plugins.registry import RegisteredAlgorithm


def _fmt_int(answer: object) -> str:
    return str(answer)


def _fmt_bool(answer: object) -> str:
    return "true" if answer else "false"


def _grid_input(rows: list[list[int]]) -> str:
    return f"{len(rows)} {len(rows[0])}\n" + "\n".join(" ".join(map(str, r)) for r in rows)


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


_GRID_PARSE = (
    "import sys\ndata = sys.stdin.read().split('\\n')\n"
    "rows, cols = map(int, data[0].split())\n"
    "grid = [list(map(int, data[1+i].split())) for i in range(rows)]\n\n"
)

_SPECS: dict[str, _Spec] = {
    "rotten-oranges-minutes": _Spec(
        algorithm_slug="bfs",
        oracle=oracles.rotten_oranges_minutes,
        cases=[
            (_grid_input([[2, 1, 1], [1, 1, 0], [0, 1, 1]]), ([[2, 1, 1], [1, 1, 0], [0, 1, 1]],), False),
            (_grid_input([[2, 1, 1], [0, 1, 1], [1, 0, 1]]), ([[2, 1, 1], [0, 1, 1], [1, 0, 1]],), False),
            (_grid_input([[0, 2]]), ([[0, 2]],), True),
            (_grid_input([[0]]), ([[0]],), True),
        ],
        statement=(
            "A grid has cells: `0` empty, `1` fresh orange, `2` rotten orange. Every "
            "minute, a rotten orange rots each 4-directionally adjacent fresh orange. "
            "Print the **number of minutes** until no fresh orange remains, or "
            "**-1** if some fresh orange can never rot."
        ),
        constraints=["1 ≤ rows, cols ≤ 10"],
        starter_code=(
            _GRID_PARSE + "def oranges_rotting(grid):\n    pass\n\nprint(oranges_rotting(grid))\n"
        ),
        title="Rotting Oranges",
    ),
    "max-distance-to-zero": _Spec(
        algorithm_slug="bfs",
        oracle=oracles.max_distance_to_zero,
        cases=[
            (_grid_input([[0, 0, 0], [0, 1, 0], [0, 0, 0]]), ([[0, 0, 0], [0, 1, 0], [0, 0, 0]],), False),
            (_grid_input([[0, 0, 1], [1, 1, 1], [1, 1, 1]]), ([[0, 0, 1], [1, 1, 1], [1, 1, 1]],), False),
            (_grid_input([[0]]), ([[0]],), True),
            (_grid_input([[1, 0], [1, 1]]), ([[1, 0], [1, 1]],), True),
        ],
        statement=(
            "Given a grid of 0s and 1s (at least one 0), print the **maximum, over "
            "all cells**, of the 4-directional distance from that cell to the "
            "nearest 0 cell."
        ),
        constraints=["1 ≤ rows, cols ≤ 20", "at least one cell is 0"],
        starter_code=(
            _GRID_PARSE + "def max_dist_to_zero(grid):\n    pass\n\nprint(max_dist_to_zero(grid))\n"
        ),
        title="Maximum Distance to a Zero Cell",
    ),
    "number-of-islands": _Spec(
        algorithm_slug="bfs",
        oracle=oracles.count_islands,
        cases=[
            (_grid_input([[1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 1]]),
             ([[1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 1]],), False),
            (_grid_input([[1, 0, 0, 1, 0], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0]]),
             ([[1, 0, 0, 1, 0], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0]],), False),
            (_grid_input([[0]]), ([[0]],), True),
            (_grid_input([[1, 1], [1, 1]]), ([[1, 1], [1, 1]],), True),
        ],
        statement=(
            "Given a grid of 0s (water) and 1s (land), print the **number of "
            "islands** — maximal 4-directionally-connected groups of land cells."
        ),
        constraints=["1 ≤ rows, cols ≤ 50"],
        starter_code=(
            _GRID_PARSE + "def num_islands(grid):\n    pass\n\nprint(num_islands(grid))\n"
        ),
        title="Number of Islands",
        difficulty="Easy",
        estimated_minutes=20,
    ),
    "shortest-path-binary-matrix": _Spec(
        algorithm_slug="bfs",
        oracle=oracles.shortest_path_binary_matrix,
        cases=[
            (_grid_input([[0, 1], [1, 0]]), ([[0, 1], [1, 0]],), False),
            (_grid_input([[0, 0, 0], [1, 1, 0], [1, 1, 0]]), ([[0, 0, 0], [1, 1, 0], [1, 1, 0]],), False),
            (_grid_input([[1, 0, 0]]), ([[1, 0, 0]],), True),
            (_grid_input([[0]]), ([[0]],), True),
        ],
        statement=(
            "Given an `n x n` grid of 0 (open) and 1 (blocked) cells, print the "
            "length (in number of cells) of the shortest **8-directional** path "
            "from the top-left to the bottom-right cell, or **-1** if none exists."
        ),
        constraints=["1 ≤ n ≤ 100"],
        starter_code=(
            _GRID_PARSE + "def shortest_path(grid):\n    pass\n\nprint(shortest_path(grid))\n"
        ),
        title="Shortest Path in a Binary Matrix",
    ),
    "word-ladder-length": _Spec(
        algorithm_slug="bfs",
        oracle=oracles.word_ladder_length,
        cases=[
            ("hit\ncog\nhot dot dog lot log cog", ("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]), False),
            ("hit\ncog\nhot dot dog lot log", ("hit", "cog", ["hot", "dot", "dog", "lot", "log"]), False),
            ("a\nc\na b c", ("a", "c", ["a", "b", "c"]), True),
            ("hot\ndog\nhot dog", ("hot", "dog", ["hot", "dog"]), True),
        ],
        statement=(
            "Given `beginWord`, `endWord`, and a `wordList` (one-line, space "
            "separated), print the **number of words** in the shortest "
            "transformation sequence from `beginWord` to `endWord` (inclusive of "
            "both), changing exactly one letter per step, each intermediate word "
            "must be in `wordList`. Print **0** if no such sequence exists."
        ),
        constraints=["1 ≤ word length ≤ 10", "all words the same length, lowercase"],
        starter_code=(
            "import sys\nlines = sys.stdin.read().split('\\n')\n"
            "begin_word, end_word = lines[0], lines[1]\nword_list = lines[2].split()\n\n"
            "def ladder_length(begin_word, end_word, word_list):\n    pass\n\n"
            "print(ladder_length(begin_word, end_word, word_list))\n"
        ),
        title="Word Ladder Length",
        difficulty="Hard",
        estimated_minutes=35,
    ),
    "minimum-knight-moves": _Spec(
        algorithm_slug="bfs",
        oracle=oracles.min_knight_moves,
        cases=[
            ("2 1", (2, 1), False), ("5 5", (5, 5), False),
            ("0 0", (0, 0), True), ("1 0", (1, 0), True),
        ],
        statement=(
            "On an infinite chessboard, a knight starts at `(0, 0)`. Given a "
            "target `(x, y)`, print the **minimum number of knight moves** needed "
            "to reach it."
        ),
        constraints=["-300 ≤ x, y ≤ 300"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split()\nx, y = int(data[0]), int(data[1])\n\n"
            "def min_knight_moves(x, y):\n    pass\n\nprint(min_knight_moves(x, y))\n"
        ),
        title="Minimum Knight Moves",
    ),
    "is-bipartite": _Spec(
        algorithm_slug="bipartite-check",
        oracle=oracles.is_bipartite,
        cases=[
            ("4 4\n0 1\n1 2\n2 3\n3 0", (4, [(0, 1), (1, 2), (2, 3), (3, 0)]), False),
            ("3 3\n0 1\n1 2\n2 0", (3, [(0, 1), (1, 2), (2, 0)]), False),
            ("4 2\n0 1\n2 3", (4, [(0, 1), (2, 3)]), True),
            ("1 0", (1, []), True),
        ],
        statement=(
            "Given an undirected graph with `n` nodes (0-indexed) and `m` edges "
            "(possibly disconnected), print `true` if the graph is **bipartite** "
            "(2-colorable so no edge connects two same-colored nodes), else `false`."
        ),
        constraints=["1 ≤ n ≤ 10^4", "0 ≤ m ≤ 2×10^4"],
        starter_code=(
            "import sys\ndata = sys.stdin.read().split('\\n')\n"
            "n, m = map(int, data[0].split())\n"
            "edges = [tuple(map(int, data[1+i].split())) for i in range(m)]\n\n"
            "def is_bipartite(n, edges):\n    pass\n\n"
            "print('true' if is_bipartite(n, edges) else 'false')\n"
        ),
        title="Is Graph Bipartite?",
        format_output=_fmt_bool,
    ),
}


def build_bfs_graph_variant_problems(
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

        test_plan = BFS_GRAPH_TEST_PLANS.get(slug)
        if test_plan is None:
            skipped.append((slug, "no 40-test case plan registered in bfs_graph_variants_testdata.py"))
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
            "category": "graphs",
            "algorithm_slug": spec.algorithm_slug,
            "estimated_minutes": spec.estimated_minutes,
            "problem_statement": spec.statement,
            "examples": [],
            "constraints": spec.constraints,
            "hints": [{"level": 1, "text": intuition[:300] or "Use BFS to explore layer by layer."}],
            "companies": [],
            "starter_code": {"python": spec.starter_code},
        }
        problems.append((problem, test_cases))

    return problems, skipped
