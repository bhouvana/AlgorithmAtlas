"""
AtlasCode problem catalog + seeding logic.

Moved out of scripts/seed_atlas_code.py (2026-07-12) so it is importable
from inside the deployed backend package itself -- the standalone scripts/
directory is a convenience for local full-repo checkouts and is NOT copied
into the Docker image (see apps/backend/Dockerfile), so anything the running
app needs at boot time (see main.py's lifespan: auto-seed on first boot if
the problems table is empty) has to live in the algorithm_atlas package
proper, not under scripts/.

scripts/seed_atlas_code.py now re-exports PROBLEMS/assemble_catalog/seed
from here so the existing `python scripts/seed_atlas_code.py` CLI workflow
and the handful of other scripts that `import seed_atlas_code as seed_mod`
(check_atlascode_duplicates.py, migrate_*_to_forty.py, time_bsv.py,
time_families.py) are completely unaffected -- same names, same behavior,
just a different home for the implementation.

Idempotent: skips problems that already exist.
"""
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from sqlalchemy import text

from algorithm_atlas.atlascode.coverage import build_coverage_manifest, summarize
from algorithm_atlas.atlascode.discovery import discover_registered_algorithms
from algorithm_atlas.atlascode.families.array_hashing_variants import build_array_hashing_variant_problems
from algorithm_atlas.atlascode.families.backtracking_count_variants import build_backtracking_count_variant_problems
from algorithm_atlas.atlascode.families.bfs_graph_variants import build_bfs_graph_variant_problems
from algorithm_atlas.atlascode.families.bit_manipulation_variants import build_bit_manipulation_variant_problems
from algorithm_atlas.atlascode.families.binary_search_variants import build_binary_search_variant_problems
from algorithm_atlas.atlascode.families.divide_and_conquer import build_divide_and_conquer_problems
from algorithm_atlas.atlascode.families.dp_variants import build_dp_variant_problems
from algorithm_atlas.atlascode.families.dynamic_programming import build_dynamic_programming_problems
from algorithm_atlas.atlascode.families.greedy import build_greedy_problems
from algorithm_atlas.atlascode.families.linked_list_variants import build_linked_list_variant_problems
from algorithm_atlas.atlascode.families.number_theory import build_number_theory_problems
from algorithm_atlas.atlascode.families.searching import build_searching_problems
from algorithm_atlas.atlascode.families.sliding_window_variants import build_sliding_window_variant_problems
from algorithm_atlas.atlascode.families.sorting import build_sorting_problems
from algorithm_atlas.atlascode.families.stack_variants import build_stack_variant_problems
from algorithm_atlas.atlascode.families.string_family import build_string_problems
from algorithm_atlas.atlascode.families.tree_variants import build_tree_variant_problems
from algorithm_atlas.atlascode.families.famous_easy import build_famous_easy_problems
from algorithm_atlas.atlascode.families.famous_arrays_matrix import build_famous_arrays_matrix_problems
from algorithm_atlas.atlascode.families.famous_graphs_trees_lists import build_famous_graphs_trees_lists_problems
from algorithm_atlas.atlascode.families.famous_hard import build_famous_hard_problems
from algorithm_atlas.database import AsyncSessionLocal, init_db
from algorithm_atlas.models.atlas_code import DailyChallenge, Problem, TestCase
from datetime import date
from sqlalchemy import select

# ── Problem definitions ───────────────────────────────────────────────────────
# Each entry: (problem_dict, [test_case_dicts])
# test_case: { input_data, expected_output, is_hidden, explanation, order }

PROBLEMS = [
    # ── EASY ─────────────────────────────────────────────────────────────────
    (
        {
            "id": "binary-search",
            "title": "Binary Search",
            "difficulty": "Easy",
            "category": "searching",
            "algorithm_slug": "binary-search",
            "estimated_minutes": 15,
            "problem_statement": (
                "Given a sorted array of integers `nums` and a target integer `target`, "
                "return the **index** of `target` if it is in the array, or **-1** if not.\n\n"
                "You must implement an algorithm with **O(log n)** time complexity."
            ),
            "examples": [
                {"input": "nums = [-1,0,3,5,9,12], target = 9", "output": "4",
                 "explanation": "9 exists at index 4"},
                {"input": "nums = [-1,0,3,5,9,12], target = 2", "output": "-1",
                 "explanation": "2 does not exist"},
            ],
            "constraints": [
                "1 ≤ nums.length ≤ 10^4",
                "-10^4 < nums[i], target < 10^4",
                "All integers in nums are unique",
                "nums is sorted in ascending order",
            ],
            "hints": [
                {"level": 1, "text": "Think about how you narrow down the search space each step."},
                {"level": 2, "text": "Maintain left and right pointers. Compare mid to target."},
                {"level": 3, "text": "mid = left + (right - left) // 2 avoids integer overflow."},
            ],
            "companies": ["Google", "Amazon", "Microsoft"],
            "starter_code": {
                "python": (
                    "import sys\n\ndef binary_search(nums, target):\n"
                    "    # TODO: implement\n    pass\n\n"
                    "data = sys.stdin.read().split()\nn = int(data[0])\n"
                    "nums = list(map(int, data[1:n+1]))\ntarget = int(data[n+1])\n"
                    "print(binary_search(nums, target))\n"
                ),
                "javascript": (
                    "const lines = require('fs').readFileSync('/dev/stdin','utf8').trim().split('\\n');\n"
                    "const parts = lines[0].split(' ');\nconst n = parseInt(parts[0]);\n"
                    "const nums = parts.slice(1, n+1).map(Number);\n"
                    "const target = parseInt(parts[n+1]);\n\n"
                    "function binarySearch(nums, target) {\n  // TODO\n}\n\n"
                    "console.log(binarySearch(nums, target));\n"
                ),
            },
        },
        [
            {"input_data": "6 -1 0 3 5 9 12 9", "expected_output": "4", "is_hidden": False,
             "explanation": "Target 9 is at index 4", "order": 0},
            {"input_data": "6 -1 0 3 5 9 12 2", "expected_output": "-1", "is_hidden": False,
             "explanation": "Target 2 not found", "order": 1},
            {"input_data": "1 5 5", "expected_output": "0", "is_hidden": False,
             "explanation": "Single element, found", "order": 2},
            {"input_data": "1 5 3", "expected_output": "-1", "is_hidden": True,
             "explanation": "Single element, not found", "order": 3},
            {"input_data": "5 1 3 5 7 9 1", "expected_output": "0", "is_hidden": True,
             "explanation": "First element", "order": 4},
        ],
    ),
    (
        {
            "id": "linear-search",
            "title": "Linear Search",
            "difficulty": "Easy",
            "category": "searching",
            "algorithm_slug": "linear-search",
            "estimated_minutes": 10,
            "problem_statement": (
                "Given an array `nums` and a target, return the **index** of the first occurrence "
                "of `target`, or **-1** if not found.\n\nNo sorting is guaranteed."
            ),
            "examples": [
                {"input": "nums = [4, 2, 7, 1, 9], target = 7", "output": "2"},
                {"input": "nums = [1, 2, 3], target = 5", "output": "-1"},
            ],
            "constraints": [
                "1 ≤ nums.length ≤ 10^5",
                "-10^9 ≤ nums[i], target ≤ 10^9",
            ],
            "hints": [
                {"level": 1, "text": "Iterate through the array from left to right."},
                {"level": 2, "text": "Return the index as soon as you find the element."},
            ],
            "companies": [],
            "starter_code": {
                "python": (
                    "import sys\ndata = sys.stdin.read().split()\n"
                    "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
                    "target = int(data[n+1])\n\ndef linear_search(nums, target):\n"
                    "    pass\n\nprint(linear_search(nums, target))\n"
                ),
            },
        },
        [
            {"input_data": "5 4 2 7 1 9 7", "expected_output": "2", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "3 1 2 3 5", "expected_output": "-1", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "1 42 42", "expected_output": "0", "is_hidden": True, "explanation": "", "order": 2},
        ],
    ),
    (
        {
            "id": "bubble-sort",
            "title": "Bubble Sort",
            "difficulty": "Easy",
            "category": "sorting",
            "algorithm_slug": "bubble-sort",
            "estimated_minutes": 15,
            "problem_statement": (
                "Given an array of integers, sort it in **ascending order** using the "
                "Bubble Sort algorithm and print the sorted array.\n\n"
                "Print integers separated by spaces on one line."
            ),
            "examples": [
                {"input": "nums = [5, 3, 8, 1, 2]", "output": "1 2 3 5 8"},
            ],
            "constraints": [
                "1 ≤ nums.length ≤ 10^3",
                "-10^4 ≤ nums[i] ≤ 10^4",
            ],
            "hints": [
                {"level": 1, "text": "In each pass, compare adjacent elements and swap if out of order."},
                {"level": 2, "text": "After k passes, the k largest elements are in their final positions."},
                {"level": 3, "text": "Use an 'already sorted' flag to exit early when no swaps occur."},
            ],
            "companies": [],
            "starter_code": {
                "python": (
                    "import sys\ndata = sys.stdin.read().split()\n"
                    "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
                    "def bubble_sort(arr):\n    pass\n\n"
                    "bubble_sort(nums)\nprint(' '.join(map(str, nums)))\n"
                ),
            },
        },
        [
            {"input_data": "5 5 3 8 1 2", "expected_output": "1 2 3 5 8", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "1 42", "expected_output": "42", "is_hidden": False, "explanation": "Single element", "order": 1},
            {"input_data": "3 3 2 1", "expected_output": "1 2 3", "is_hidden": False, "explanation": "Reversed", "order": 2},
            {"input_data": "4 -3 0 5 -1", "expected_output": "-3 -1 0 5", "is_hidden": True, "explanation": "Negatives", "order": 3},
        ],
    ),
    (
        {
            "id": "fibonacci-dp",
            "title": "Fibonacci Number (DP)",
            "difficulty": "Easy",
            "category": "dynamic-programming",
            "algorithm_slug": "fibonacci-dp",
            "estimated_minutes": 15,
            "problem_statement": (
                "Given `n`, return the n-th Fibonacci number where F(0)=0, F(1)=1, "
                "F(n)=F(n-1)+F(n-2).\n\nSolve it in **O(n)** time and **O(1)** space."
            ),
            "examples": [
                {"input": "n = 0", "output": "0"},
                {"input": "n = 5", "output": "5"},
                {"input": "n = 10", "output": "55"},
            ],
            "constraints": ["0 ≤ n ≤ 30"],
            "hints": [
                {"level": 1, "text": "Keep track of only the previous two values."},
            ],
            "companies": ["Amazon"],
            "starter_code": {
                "python": (
                    "import sys\nn = int(sys.stdin.read().strip())\n\n"
                    "def fib(n):\n    pass\n\nprint(fib(n))\n"
                ),
            },
        },
        [
            {"input_data": "0", "expected_output": "0", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "1", "expected_output": "1", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "5", "expected_output": "5", "is_hidden": False, "explanation": "", "order": 2},
            {"input_data": "10", "expected_output": "55", "is_hidden": True, "explanation": "", "order": 3},
            {"input_data": "30", "expected_output": "832040", "is_hidden": True, "explanation": "", "order": 4},
        ],
    ),
    (
        {
            "id": "gcd-euclidean",
            "title": "GCD (Euclidean Algorithm)",
            "difficulty": "Easy",
            "category": "math",
            "algorithm_slug": "gcd-euclidean",
            "estimated_minutes": 10,
            "problem_statement": (
                "Given two non-negative integers `a` and `b`, return their "
                "**Greatest Common Divisor** using the Euclidean algorithm."
            ),
            "examples": [
                {"input": "a = 48, b = 18", "output": "6"},
                {"input": "a = 0, b = 5", "output": "5"},
            ],
            "constraints": ["0 ≤ a, b ≤ 10^9", "Not both zero"],
            "hints": [
                {"level": 1, "text": "GCD(a, b) = GCD(b, a mod b). Base case: GCD(a, 0) = a."},
            ],
            "companies": [],
            "starter_code": {
                "python": (
                    "import sys\ndata = sys.stdin.read().split()\n"
                    "a, b = int(data[0]), int(data[1])\n\n"
                    "def gcd(a, b):\n    pass\n\nprint(gcd(a, b))\n"
                ),
            },
        },
        [
            {"input_data": "48 18", "expected_output": "6", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "0 5", "expected_output": "5", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "100 75", "expected_output": "25", "is_hidden": True, "explanation": "", "order": 2},
        ],
    ),
    (
        {
            "id": "two-sum",
            "title": "Two Sum",
            "difficulty": "Easy",
            "category": "hashing",
            "algorithm_slug": "two-sum",
            "estimated_minutes": 15,
            "problem_statement": (
                "Given an array `nums` and an integer `target`, return the **indices** of the "
                "two numbers such that they add up to `target`.\n\n"
                "Output the two indices in ascending order, space-separated."
            ),
            "examples": [
                {"input": "nums = [2,7,11,15], target = 9", "output": "0 1"},
                {"input": "nums = [3,2,4], target = 6", "output": "1 2"},
            ],
            "constraints": [
                "2 ≤ nums.length ≤ 10^4",
                "-10^9 ≤ nums[i] ≤ 10^9",
                "Exactly one valid answer exists",
            ],
            "hints": [
                {"level": 1, "text": "A hash map lets you look up the complement in O(1)."},
                {"level": 2, "text": "For each element x, check if target - x is already in the map."},
            ],
            "companies": ["Google", "Amazon", "Facebook", "Apple"],
            "starter_code": {
                "python": (
                    "import sys\ndata = sys.stdin.read().split()\n"
                    "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n"
                    "target = int(data[n+1])\n\n"
                    "def two_sum(nums, target):\n    pass\n\n"
                    "i, j = two_sum(nums, target)\nprint(min(i,j), max(i,j))\n"
                ),
            },
        },
        [
            {"input_data": "4 2 7 11 15 9", "expected_output": "0 1", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "3 3 2 4 6", "expected_output": "1 2", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "2 3 3 6", "expected_output": "0 1", "is_hidden": True, "explanation": "", "order": 2},
        ],
    ),
    (
        {
            "id": "maximum-subarray",
            "title": "Maximum Subarray (Kadane's)",
            "difficulty": "Easy",
            "category": "dynamic-programming",
            "algorithm_slug": "maximum-subarray",
            "estimated_minutes": 20,
            "problem_statement": (
                "Given an integer array `nums`, find the contiguous subarray "
                "(containing at least one element) which has the **largest sum** and return its sum."
            ),
            "examples": [
                {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6",
                 "explanation": "[4,-1,2,1] has sum 6"},
                {"input": "nums = [1]", "output": "1"},
            ],
            "constraints": [
                "1 ≤ nums.length ≤ 10^5",
                "-10^4 ≤ nums[i] ≤ 10^4",
            ],
            "hints": [
                {"level": 1, "text": "At each position, decide: extend the current subarray or start fresh?"},
                {"level": 2, "text": "current = max(nums[i], current + nums[i]). Track the running maximum."},
            ],
            "companies": ["Amazon", "Microsoft"],
            "starter_code": {
                "python": (
                    "import sys\ndata = sys.stdin.read().split()\n"
                    "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
                    "def max_subarray(nums):\n    pass\n\nprint(max_subarray(nums))\n"
                ),
            },
        },
        [
            {"input_data": "9 -2 1 -3 4 -1 2 1 -5 4", "expected_output": "6", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "1 1", "expected_output": "1", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "3 -1 -2 -3", "expected_output": "-1", "is_hidden": False, "explanation": "All negative", "order": 2},
            {"input_data": "5 5 4 -1 7 8", "expected_output": "23", "is_hidden": True, "explanation": "", "order": 3},
        ],
    ),
    # ── MEDIUM ────────────────────────────────────────────────────────────────
    (
        {
            "id": "coin-change",
            "title": "Coin Change",
            "difficulty": "Medium",
            "category": "dynamic-programming",
            "algorithm_slug": "coin-change",
            "estimated_minutes": 25,
            "problem_statement": (
                "Given an array of coin denominations `coins` and an integer `amount`, "
                "return the **fewest number of coins** needed to make up the amount, "
                "or **-1** if it is impossible."
            ),
            "examples": [
                {"input": "coins = [1,5,6,9], amount = 11", "output": "2",
                 "explanation": "5 + 6 = 11"},
                {"input": "coins = [2], amount = 3", "output": "-1"},
            ],
            "constraints": [
                "1 ≤ coins.length ≤ 12",
                "1 ≤ coins[i] ≤ 2^31 - 1",
                "0 ≤ amount ≤ 10^4",
            ],
            "hints": [
                {"level": 1, "text": "Build a dp table of size amount+1. dp[0]=0, rest=infinity."},
                {"level": 2, "text": "For each amount i, try every coin c: dp[i] = min(dp[i], dp[i-c]+1)."},
                {"level": 3, "text": "If dp[amount] is still infinity, return -1."},
            ],
            "companies": ["Amazon", "Google", "Apple"],
            "starter_code": {
                "python": (
                    "import sys\ndata = sys.stdin.read().split()\n"
                    "k = int(data[0])\ncoins = list(map(int, data[1:k+1]))\n"
                    "amount = int(data[k+1])\n\n"
                    "def coin_change(coins, amount):\n    pass\n\n"
                    "print(coin_change(coins, amount))\n"
                ),
            },
        },
        [
            {"input_data": "4 1 5 6 9 11", "expected_output": "2", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "1 2 3", "expected_output": "-1", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "3 1 2 5 11", "expected_output": "3", "is_hidden": False, "explanation": "", "order": 2},
            {"input_data": "1 1 0", "expected_output": "0", "is_hidden": True, "explanation": "amount=0", "order": 3},
        ],
    ),
    (
        {
            "id": "longest-common-subsequence",
            "title": "Longest Common Subsequence",
            "difficulty": "Medium",
            "category": "dynamic-programming",
            "algorithm_slug": "longest-common-subsequence",
            "estimated_minutes": 30,
            "problem_statement": (
                "Given two strings `s1` and `s2`, return the length of their "
                "**Longest Common Subsequence** (LCS)."
            ),
            "examples": [
                {"input": 's1 = "abcde", s2 = "ace"', "output": "3",
                 "explanation": "LCS is 'ace'"},
                {"input": 's1 = "abc", s2 = "abc"', "output": "3"},
                {"input": 's1 = "abc", s2 = "def"', "output": "0"},
            ],
            "constraints": [
                "1 ≤ s1.length, s2.length ≤ 1000",
                "s1 and s2 consist only of lowercase English letters",
            ],
            "hints": [
                {"level": 1, "text": "Define dp[i][j] = LCS of s1[:i] and s2[:j]."},
                {"level": 2, "text": "If s1[i-1]==s2[j-1]: dp[i][j] = dp[i-1][j-1] + 1, else max(dp[i-1][j], dp[i][j-1])."},
            ],
            "companies": ["Google", "Amazon", "Microsoft"],
            "starter_code": {
                "python": (
                    "import sys\nlines = sys.stdin.read().split()\n"
                    "s1, s2 = lines[0], lines[1]\n\n"
                    "def lcs(s1, s2):\n    pass\n\nprint(lcs(s1, s2))\n"
                ),
            },
        },
        [
            {"input_data": "abcde ace", "expected_output": "3", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "abc abc", "expected_output": "3", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "abc def", "expected_output": "0", "is_hidden": False, "explanation": "", "order": 2},
            {"input_data": "bsbininm jmjkbhmim", "expected_output": "4", "is_hidden": True, "explanation": "", "order": 3},
        ],
    ),
    (
        {
            "id": "house-robber",
            "title": "House Robber",
            "difficulty": "Medium",
            "category": "dynamic-programming",
            "algorithm_slug": "house-robber",
            "estimated_minutes": 20,
            "problem_statement": (
                "You are a professional robber. Houses are arranged in a line; "
                "adjacent houses cannot both be robbed. Given `nums` representing money "
                "in each house, return the **maximum amount you can rob tonight**."
            ),
            "examples": [
                {"input": "nums = [1,2,3,1]", "output": "4",
                 "explanation": "Rob house 0 (1) + house 2 (3) = 4"},
                {"input": "nums = [2,7,9,3,1]", "output": "12"},
            ],
            "constraints": [
                "1 ≤ nums.length ≤ 100",
                "0 ≤ nums[i] ≤ 400",
            ],
            "hints": [
                {"level": 1, "text": "At each house, choose: rob it (add to prev-prev total) or skip (keep prev total)."},
                {"level": 2, "text": "dp[i] = max(dp[i-1], dp[i-2] + nums[i])"},
            ],
            "companies": ["Google", "Amazon"],
            "starter_code": {
                "python": (
                    "import sys\ndata = sys.stdin.read().split()\n"
                    "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
                    "def rob(nums):\n    pass\n\nprint(rob(nums))\n"
                ),
            },
        },
        [
            {"input_data": "4 1 2 3 1", "expected_output": "4", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "5 2 7 9 3 1", "expected_output": "12", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "1 0", "expected_output": "0", "is_hidden": True, "explanation": "", "order": 2},
            {"input_data": "2 1 2", "expected_output": "2", "is_hidden": True, "explanation": "", "order": 3},
        ],
    ),
    (
        {
            "id": "longest-increasing-subsequence",
            "title": "Longest Increasing Subsequence",
            "difficulty": "Medium",
            "category": "dynamic-programming",
            "algorithm_slug": "longest-increasing-subsequence",
            "estimated_minutes": 30,
            "problem_statement": (
                "Given an integer array `nums`, return the length of the "
                "**longest strictly increasing subsequence**."
            ),
            "examples": [
                {"input": "nums = [10,9,2,5,3,7,101,18]", "output": "4",
                 "explanation": "[2,3,7,101]"},
                {"input": "nums = [0,1,0,3,2,3]", "output": "4"},
            ],
            "constraints": [
                "1 ≤ nums.length ≤ 2500",
                "-10^4 ≤ nums[i] ≤ 10^4",
            ],
            "hints": [
                {"level": 1, "text": "dp[i] = length of LIS ending at index i."},
                {"level": 2, "text": "dp[i] = max(dp[j]+1) for all j<i where nums[j]<nums[i]."},
                {"level": 3, "text": "For O(n log n): use patience sorting with binary search."},
            ],
            "companies": ["Google", "Amazon", "Microsoft"],
            "starter_code": {
                "python": (
                    "import sys\ndata = sys.stdin.read().split()\n"
                    "n = int(data[0])\nnums = list(map(int, data[1:n+1]))\n\n"
                    "def lis(nums):\n    pass\n\nprint(lis(nums))\n"
                ),
            },
        },
        [
            {"input_data": "8 10 9 2 5 3 7 101 18", "expected_output": "4", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "6 0 1 0 3 2 3", "expected_output": "4", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "1 1", "expected_output": "1", "is_hidden": True, "explanation": "", "order": 2},
        ],
    ),
    (
        {
            "id": "graph-bfs",
            "title": "BFS Shortest Path",
            "difficulty": "Medium",
            "category": "graphs",
            "algorithm_slug": "bfs",
            "estimated_minutes": 25,
            "problem_statement": (
                "Given an undirected graph with `n` nodes (0-indexed) and `m` edges, "
                "and a source node `src`, print the **shortest distance** from `src` to "
                "every other node (space-separated, in order 0..n-1). "
                "If a node is unreachable, print -1 for it.\n\n"
                "Input format:\n"
                "- Line 1: `n m src`\n"
                "- Next `m` lines: `u v` (undirected edge)"
            ),
            "examples": [
                {"input": "4 4 0\n0 1\n0 2\n1 3\n2 3", "output": "0 1 1 2"},
            ],
            "constraints": [
                "1 ≤ n ≤ 10^4",
                "0 ≤ m ≤ 2×10^4",
            ],
            "hints": [
                {"level": 1, "text": "Use a queue. Start with src at distance 0."},
                {"level": 2, "text": "Mark nodes visited when enqueued, not when dequeued."},
            ],
            "companies": ["Google", "Facebook", "Amazon"],
            "starter_code": {
                "python": (
                    "import sys\nfrom collections import deque\n\n"
                    "data = sys.stdin.read().split()\nidx = 0\n"
                    "n, m, src = int(data[idx]), int(data[idx+1]), int(data[idx+2])\nidx+=3\n"
                    "adj = [[] for _ in range(n)]\n"
                    "for _ in range(m):\n    u,v=int(data[idx]),int(data[idx+1]);idx+=2\n"
                    "    adj[u].append(v);adj[v].append(u)\n\n"
                    "def bfs(adj, src, n):\n    pass\n\n"
                    "print(' '.join(map(str, bfs(adj, src, n))))\n"
                ),
            },
        },
        [
            {"input_data": "4 4 0\n0 1\n0 2\n1 3\n2 3", "expected_output": "0 1 1 2", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "3 1 0\n0 1", "expected_output": "0 1 -1", "is_hidden": False, "explanation": "Node 2 unreachable", "order": 1},
            {"input_data": "1 0 0", "expected_output": "0", "is_hidden": True, "explanation": "Single node", "order": 2},
        ],
    ),
    (
        {
            "id": "word-break",
            "title": "Word Break",
            "difficulty": "Medium",
            "category": "dynamic-programming",
            "algorithm_slug": "word-break",
            "estimated_minutes": 25,
            "problem_statement": (
                "Given a string `s` and a dictionary of words `wordDict`, "
                "return `true` if `s` can be segmented into space-separated dictionary words, "
                "or `false` otherwise.\n\n"
                "Input: first line is `s`, second line is space-separated words."
            ),
            "examples": [
                {"input": 's = "leetcode", wordDict = ["leet","code"]', "output": "true"},
                {"input": 's = "catsandog", wordDict = ["cats","dog","sand","and","cat"]', "output": "false"},
            ],
            "constraints": [
                "1 ≤ s.length ≤ 300",
                "1 ≤ wordDict.length ≤ 1000",
            ],
            "hints": [
                {"level": 1, "text": "dp[i] = True if s[:i] can be segmented."},
                {"level": 2, "text": "For each i, check all j<i: if dp[j] and s[j:i] in wordDict, set dp[i]=True."},
            ],
            "companies": ["Amazon", "Google"],
            "starter_code": {
                "python": (
                    "import sys\nlines = sys.stdin.read().splitlines()\n"
                    "s = lines[0]\nword_dict = set(lines[1].split())\n\n"
                    "def word_break(s, word_dict):\n    pass\n\n"
                    "print('true' if word_break(s, word_dict) else 'false')\n"
                ),
            },
        },
        [
            {"input_data": "leetcode\nleet code", "expected_output": "true", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "catsandog\ncats dog sand and cat", "expected_output": "false", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "applepenapple\napple pen", "expected_output": "true", "is_hidden": True, "explanation": "", "order": 2},
        ],
    ),
    (
        {
            "id": "edit-distance",
            "title": "Edit Distance (Levenshtein)",
            "difficulty": "Medium",
            "category": "dynamic-programming",
            "algorithm_slug": "edit-distance",
            "estimated_minutes": 30,
            "problem_statement": (
                "Given two strings `word1` and `word2`, return the minimum number of operations "
                "(insert, delete, replace) to convert `word1` to `word2`."
            ),
            "examples": [
                {"input": 'word1 = "horse", word2 = "ros"', "output": "3"},
                {"input": 'word1 = "intention", word2 = "execution"', "output": "5"},
            ],
            "constraints": [
                "0 ≤ word1.length, word2.length ≤ 500",
            ],
            "hints": [
                {"level": 1, "text": "dp[i][j] = edit distance between word1[:i] and word2[:j]."},
                {"level": 2, "text": "If chars match: dp[i][j]=dp[i-1][j-1], else 1+min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])."},
            ],
            "companies": ["Google", "Amazon", "Microsoft"],
            "starter_code": {
                "python": (
                    "import sys\nlines = sys.stdin.read().splitlines()\n"
                    "w1 = lines[0] if len(lines) > 0 else ''\n"
                    "w2 = lines[1] if len(lines) > 1 else ''\n\n"
                    "def edit_distance(w1, w2):\n    pass\n\n"
                    "print(edit_distance(w1, w2))\n"
                ),
            },
        },
        [
            {"input_data": "horse ros", "expected_output": "3", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "intention execution", "expected_output": "5", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "a b", "expected_output": "1", "is_hidden": True, "explanation": "", "order": 2},
            {"input_data": "abc abc", "expected_output": "0", "is_hidden": True, "explanation": "", "order": 3},
        ],
    ),
    (
        {
            "id": "unique-paths",
            "title": "Unique Paths",
            "difficulty": "Medium",
            "category": "dynamic-programming",
            "algorithm_slug": "unique-paths",
            "estimated_minutes": 20,
            "problem_statement": (
                "A robot starts at the top-left of an `m × n` grid and wants to reach "
                "the bottom-right corner. It can only move right or down. "
                "Return the number of unique paths."
            ),
            "examples": [
                {"input": "m = 3, n = 7", "output": "28"},
                {"input": "m = 3, n = 2", "output": "3"},
            ],
            "constraints": ["1 ≤ m, n ≤ 100"],
            "hints": [
                {"level": 1, "text": "dp[i][j] = dp[i-1][j] + dp[i][j-1]. First row and column are all 1s."},
                {"level": 2, "text": "This is also C(m+n-2, m-1) — a combinatorics formula."},
            ],
            "companies": ["Amazon", "Google"],
            "starter_code": {
                "python": (
                    "import sys\ndata = sys.stdin.read().split()\nm, n = int(data[0]), int(data[1])\n\n"
                    "def unique_paths(m, n):\n    pass\n\nprint(unique_paths(m, n))\n"
                ),
            },
        },
        [
            {"input_data": "3 7", "expected_output": "28", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "3 2", "expected_output": "3", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "1 1", "expected_output": "1", "is_hidden": True, "explanation": "", "order": 2},
            {"input_data": "10 10", "expected_output": "48620", "is_hidden": True, "explanation": "", "order": 3},
        ],
    ),
    # ── HARD ──────────────────────────────────────────────────────────────────
    (
        {
            "id": "n-queens",
            "title": "N-Queens",
            "difficulty": "Hard",
            "category": "backtracking",
            "algorithm_slug": "n-queens",
            "estimated_minutes": 45,
            "problem_statement": (
                "Place `n` non-attacking queens on an `n × n` chessboard. "
                "Return the **number of distinct solutions**."
            ),
            "examples": [
                {"input": "n = 4", "output": "2"},
                {"input": "n = 1", "output": "1"},
            ],
            "constraints": ["1 ≤ n ≤ 12"],
            "hints": [
                {"level": 1, "text": "Place queens row by row using backtracking."},
                {"level": 2, "text": "Use three boolean arrays: cols, diag1 (row-col), diag2 (row+col)."},
                {"level": 3, "text": "No two queens can share the same column or diagonal."},
                {"level": 4, "text": "The constraint sets have size n, n*2-1, n*2-1 respectively."},
            ],
            "companies": ["Google", "Amazon", "Microsoft"],
            "starter_code": {
                "python": (
                    "import sys\nn = int(sys.stdin.read().strip())\n\n"
                    "def solve_n_queens(n):\n    pass\n\nprint(solve_n_queens(n))\n"
                ),
            },
        },
        [
            {"input_data": "4", "expected_output": "2", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "1", "expected_output": "1", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "8", "expected_output": "92", "is_hidden": True, "explanation": "", "order": 2},
            {"input_data": "9", "expected_output": "352", "is_hidden": True, "explanation": "", "order": 3},
        ],
    ),
    (
        {
            "id": "dijkstra-shortest-path",
            "title": "Dijkstra's Shortest Path",
            "difficulty": "Hard",
            "category": "graphs",
            "algorithm_slug": "dijkstra",
            "estimated_minutes": 40,
            "problem_statement": (
                "Given a directed weighted graph, find the shortest path distances "
                "from source node 0 to all other nodes.\n\n"
                "Input:\n"
                "- Line 1: `n m` (nodes, edges)\n"
                "- Next `m` lines: `u v w` (directed edge u→v with weight w)\n\n"
                "Output: n space-separated distances (0-indexed). Print -1 for unreachable nodes."
            ),
            "examples": [
                {"input": "5 6\n0 1 4\n0 2 1\n2 1 2\n1 3 1\n2 3 5\n3 4 3", "output": "0 3 1 4 7"},
            ],
            "constraints": [
                "1 ≤ n ≤ 10^4",
                "0 ≤ m ≤ 5×10^4",
                "0 ≤ w ≤ 10^9",
            ],
            "hints": [
                {"level": 1, "text": "Use a min-heap (priority queue) keyed by distance."},
                {"level": 2, "text": "Initialize dist[0]=0, all others=infinity. Relax edges greedily."},
                {"level": 3, "text": "Skip a node if we've already found a shorter path to it."},
                {"level": 4, "text": "Use heapq.heappush(heap, (cost, node)) in Python."},
            ],
            "companies": ["Google", "Amazon", "Uber", "Microsoft"],
            "starter_code": {
                "python": (
                    "import sys, heapq\ndata = sys.stdin.read().split()\nidx=0\n"
                    "n,m=int(data[idx]),int(data[idx+1]);idx+=2\n"
                    "adj=[[] for _ in range(n)]\n"
                    "for _ in range(m):\n    u,v,w=int(data[idx]),int(data[idx+1]),int(data[idx+2]);idx+=3\n"
                    "    adj[u].append((v,w))\n\n"
                    "def dijkstra(adj, n):\n    pass\n\n"
                    "print(' '.join(map(str, dijkstra(adj, n))))\n"
                ),
            },
        },
        [
            {"input_data": "5 6\n0 1 4\n0 2 1\n2 1 2\n1 3 1\n2 3 5\n3 4 3", "expected_output": "0 3 1 4 7", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "3 1\n0 1 5", "expected_output": "0 5 -1", "is_hidden": False, "explanation": "Node 2 unreachable", "order": 1},
            {"input_data": "2 0", "expected_output": "0 -1", "is_hidden": True, "explanation": "", "order": 2},
        ],
    ),
    (
        {
            "id": "kmp-string-matching",
            "title": "KMP String Matching",
            "difficulty": "Hard",
            "category": "strings",
            "algorithm_slug": "kmp",
            "estimated_minutes": 45,
            "problem_statement": (
                "Given a text string `T` and a pattern string `P`, find all **0-indexed starting "
                "positions** where `P` occurs in `T`. Print them space-separated.\n\n"
                "If there are no matches, print `-1`."
            ),
            "examples": [
                {"input": 'T = "aabaacaadaabaaba", P = "aaba"', "output": "0 9 12"},
            ],
            "constraints": [
                "1 ≤ |T| ≤ 10^6",
                "1 ≤ |P| ≤ 10^4",
            ],
            "hints": [
                {"level": 1, "text": "Build the failure function (prefix table) from P in O(|P|)."},
                {"level": 2, "text": "The failure function: lps[i] = length of longest proper prefix of P[:i+1] that is also a suffix."},
                {"level": 3, "text": "During matching, on mismatch fall back using lps rather than restarting."},
            ],
            "companies": ["Google", "Amazon"],
            "starter_code": {
                "python": (
                    "import sys\nlines = sys.stdin.read().splitlines()\n"
                    "T, P = lines[0], lines[1]\n\n"
                    "def kmp_search(T, P):\n    pass\n\n"
                    "result = kmp_search(T, P)\n"
                    "print(' '.join(map(str, result)) if result else '-1')\n"
                ),
            },
        },
        [
            {"input_data": "aabaacaadaabaaba\naaba", "expected_output": "0 9 12", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "abcde\nfgh", "expected_output": "-1", "is_hidden": False, "explanation": "No match", "order": 1},
            {"input_data": "aaa\naa", "expected_output": "0 1", "is_hidden": True, "explanation": "Overlapping", "order": 2},
        ],
    ),
    (
        {
            "id": "minimum-path-sum",
            "title": "Minimum Path Sum",
            "difficulty": "Hard",
            "category": "dynamic-programming",
            "algorithm_slug": "min-path-sum",
            "estimated_minutes": 30,
            "problem_statement": (
                "Given an `m × n` grid filled with non-negative integers, find a path "
                "from the top-left to the bottom-right (only right or down moves) "
                "which **minimizes the sum** of all numbers along the path.\n\n"
                "Input: first line is `m n`, then `m` lines each with `n` integers."
            ),
            "examples": [
                {"input": "3 3\n1 3 1\n1 5 1\n4 2 1", "output": "7",
                 "explanation": "1→3→1→1→1 = 7"},
            ],
            "constraints": [
                "1 ≤ m, n ≤ 200",
                "0 ≤ grid[i][j] ≤ 100",
            ],
            "hints": [
                {"level": 1, "text": "dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])."},
                {"level": 2, "text": "First row: cumulative sum left-to-right. First col: cumulative sum top-to-bottom."},
            ],
            "companies": ["Amazon", "Google", "Apple"],
            "starter_code": {
                "python": (
                    "import sys\ndata = sys.stdin.read().split()\nidx=0\n"
                    "m,n=int(data[idx]),int(data[idx+1]);idx+=2\n"
                    "grid=[list(map(int,data[idx+i*n:idx+(i+1)*n])) for i in range(m)]\n\n"
                    "def min_path_sum(grid):\n    pass\n\nprint(min_path_sum(grid))\n"
                ),
            },
        },
        [
            {"input_data": "3 3\n1 3 1\n1 5 1\n4 2 1", "expected_output": "7", "is_hidden": False, "explanation": "", "order": 0},
            {"input_data": "1 1\n5", "expected_output": "5", "is_hidden": False, "explanation": "", "order": 1},
            {"input_data": "2 3\n1 2 3\n4 5 6", "expected_output": "12", "is_hidden": True, "explanation": "", "order": 2},
        ],
    ),
]

# ── Catalog assembly ──────────────────────────────────────────────────────────
# Curated (hand-authored, above) + generated (family factories, derived from the
# canonical plugin catalog). Discovery and generation always run — the catalog
# is never a static count, it reflects the real repository every time this
# script runs.

def assemble_catalog() -> tuple[
    list[tuple[dict, list[dict]]],   # all problems to upsert (curated + generated)
    list,                              # canonical algorithms (discovery.CanonicalAlgorithm via registered)
    dict[str, tuple[str, str]],        # algorithm_slug -> (family name, problem_id)
    dict[str, str],                    # skipped_slug -> reason (attempted by a factory, declined)
]:
    # Canonical algorithm slugs already covered by a hand-authored problem.
    # NOTE: a curated problem's own id does not always equal its algorithm_slug
    # (e.g. problem "kmp-string-matching" maps to algorithm "kmp") — family
    # factories must dedup against the ALGORITHM slug, not the problem id.
    curated_algorithm_slugs = {p[0]["algorithm_slug"] for p in PROBLEMS if p[0].get("algorithm_slug")}
    curated_algorithm_to_problem = {p[0]["algorithm_slug"]: p[0]["id"] for p in PROBLEMS if p[0].get("algorithm_slug")}

    registered = discover_registered_algorithms()

    # Per-family timing, always on: assemble_catalog() built every family's
    # full 40-test data with zero progress output until this incident (a
    # single pathological rejection loop in one family — see
    # binary_search_variants_testdata.py's _gen_bitonic history — burned 100+
    # minutes of blind CPU time with no way to tell which family was stuck).
    # This is a permanent, low-noise (~20 lines total) safety net, not
    # per-problem/per-test verbosity.
    import time as _time

    def _timed(tag: str, fn, *args):
        t0 = _time.time()
        result = fn(*args)
        dt = _time.time() - t0
        level = " SEVERE" if dt > 30 else (" WARNING" if dt > 5 else "")
        print(f"  [assemble_catalog] {tag}: {dt:.2f}s ({len(result[0])}p, {len(result[1])} skipped){level}", flush=True)
        return result

    sorting_problems, sorting_skipped = _timed("sorting", build_sorting_problems, registered, curated_algorithm_slugs)
    searching_problems, searching_skipped = _timed("searching", build_searching_problems, registered, curated_algorithm_slugs)
    nt_problems, nt_skipped = _timed("number-theory", build_number_theory_problems, registered, curated_algorithm_slugs)
    dp_problems, dp_skipped = _timed("dynamic-programming", build_dynamic_programming_problems, registered, curated_algorithm_slugs)
    greedy_problems, greedy_skipped = _timed("greedy", build_greedy_problems, registered, curated_algorithm_slugs)
    dc_problems, dc_skipped = _timed("divide-and-conquer", build_divide_and_conquer_problems, registered, curated_algorithm_slugs)
    string_problems, string_skipped = _timed("string", build_string_problems, registered, curated_algorithm_slugs)

    # Variant families dedup by PROBLEM SLUG against everything seeded so far
    # (not by algorithm_slug — multiple variant problems legitimately share
    # one underlying canonical algorithm, e.g. many share "binary-search").
    existing_problem_ids = (
        {p[0]["id"] for p in PROBLEMS}
        | {p[0]["id"] for p in sorting_problems}
        | {p[0]["id"] for p in searching_problems}
        | {p[0]["id"] for p in nt_problems}
        | {p[0]["id"] for p in dp_problems}
        | {p[0]["id"] for p in greedy_problems}
        | {p[0]["id"] for p in dc_problems}
        | {p[0]["id"] for p in string_problems}
    )
    bsv_problems, bsv_skipped = _timed("binary-search-variants", build_binary_search_variant_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in bsv_problems}
    sw_problems, sw_skipped = _timed("sliding-window-variants", build_sliding_window_variant_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in sw_problems}
    bfs_problems, bfs_skipped = _timed("bfs-graph-variants", build_bfs_graph_variant_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in bfs_problems}
    ah_problems, ah_skipped = _timed("array-hashing-variants", build_array_hashing_variant_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in ah_problems}
    stack_problems, stack_skipped = _timed("stack-variants", build_stack_variant_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in stack_problems}
    bit_problems, bit_skipped = _timed("bit-manipulation-variants", build_bit_manipulation_variant_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in bit_problems}
    tree_problems, tree_skipped = _timed("tree-variants", build_tree_variant_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in tree_problems}
    dpv_problems, dpv_skipped = _timed("dp-variants", build_dp_variant_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in dpv_problems}
    ll_problems, ll_skipped = _timed("linked-list-variants", build_linked_list_variant_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in ll_problems}
    bt_problems, bt_skipped = _timed("backtracking-count-variants", build_backtracking_count_variant_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in bt_problems}

    # Famous-concepts families (docs/atlascode-famous-concepts-audit.md) —
    # registry-independent (algorithm_slug=None), same variant-family dedup
    # mechanism as everything else in this block.
    fe_problems, fe_skipped = _timed("famous-easy", build_famous_easy_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in fe_problems}
    fam_problems, fam_skipped = _timed("famous-arrays-matrix", build_famous_arrays_matrix_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in fam_problems}
    fgtl_problems, fgtl_skipped = _timed("famous-graphs-trees-lists", build_famous_graphs_trees_lists_problems, registered, existing_problem_ids)
    existing_problem_ids = existing_problem_ids | {p[0]["id"] for p in fgtl_problems}
    fh_problems, fh_skipped = _timed("famous-hard", build_famous_hard_problems, registered, existing_problem_ids)

    generated_problems = (
        sorting_problems + searching_problems + nt_problems + dp_problems
        + greedy_problems + dc_problems + string_problems
        + bsv_problems + sw_problems + bfs_problems
        + ah_problems + stack_problems + bit_problems + tree_problems
        + dpv_problems + ll_problems + bt_problems
        + fe_problems + fam_problems + fgtl_problems + fh_problems
    )
    # Keyed by ALGORITHM SLUG (not problem id — they differ for most variant
    # problems, e.g. "is-bipartite" implements "bipartite-check") so coverage.py
    # can correctly attribute canonical-algorithm coverage regardless of what
    # the problem itself is named. Value is (family, problem_id) — family
    # determines oracle-kind classification (was, bug fixed this session,
    # incorrectly inferred from category, which stopped being 1:1 with family
    # once binary-search-variants reused category="searching"). Pattern
    # problems with algorithm_slug=None (e.g. sliding-window) are excluded —
    # they don't claim canonical algorithm coverage.
    def _family_map(problems: list, family: str) -> dict[str, tuple[str, str]]:
        return {p[0]["algorithm_slug"]: (family, p[0]["id"]) for p in problems if p[0].get("algorithm_slug")}

    generated_slugs: dict[str, tuple[str, str]] = (
        _family_map(sorting_problems, "sorting")
        | _family_map(searching_problems, "searching")
        | _family_map(nt_problems, "number-theory")
        | _family_map(dp_problems, "dynamic-programming")
        | _family_map(greedy_problems, "greedy")
        | _family_map(dc_problems, "divide-and-conquer")
        | _family_map(string_problems, "string")
        | _family_map(bsv_problems, "binary-search-variants")
        | _family_map(sw_problems, "sliding-window-variants")
        | _family_map(bfs_problems, "bfs-graph-variants")
        | _family_map(ah_problems, "array-hashing-variants")
        | _family_map(stack_problems, "stack-variants")
        | _family_map(bit_problems, "bit-manipulation-variants")
        | _family_map(tree_problems, "tree-variants")
        | _family_map(dpv_problems, "dp-variants")
        | _family_map(ll_problems, "linked-list-variants")
        | _family_map(bt_problems, "backtracking-count-variants")
    )
    skipped = dict(
        sorting_skipped + searching_skipped + nt_skipped + dp_skipped
        + greedy_skipped + dc_skipped + string_skipped
        + bsv_skipped + sw_skipped + bfs_skipped
        + ah_skipped + stack_skipped + bit_skipped + tree_skipped
        + dpv_skipped + ll_skipped + bt_skipped
        + fe_skipped + fam_skipped + fgtl_skipped + fh_skipped
    )

    all_problems = PROBLEMS + generated_problems
    return all_problems, registered, generated_slugs, curated_algorithm_to_problem, skipped


# ── Seeder ────────────────────────────────────────────────────────────────────

async def seed(dry_run: bool = False, validate_only: bool = False) -> None:
    # assemble_catalog() is pure synchronous CPU work (up to several minutes
    # on a cold run -- some family builders do real adversarial-test-data
    # generation, e.g. bfs-graph-variants alone took ~60s measured locally).
    # Run it in a worker thread rather than directly on the event loop: when
    # seed() is invoked as a fire-and-forget background task at app boot
    # (see main.py's _auto_seed_atlascode_if_empty), calling this inline
    # would monopolize the single-threaded event loop for the entire
    # duration, starving every other coroutine -- including incoming HTTP
    # requests and Render's own health check -- confirmed locally (a
    # concurrent request took 60+ seconds to even start being handled with
    # this called directly). run_in_executor keeps the event loop free.
    all_problems, registered, generated_slugs, curated_algorithm_to_problem, skipped = (
        await asyncio.get_running_loop().run_in_executor(None, assemble_catalog)
    )
    curated_slugs = set(curated_algorithm_to_problem.keys())

    from algorithm_atlas.atlascode.discovery import CanonicalAlgorithm
    canonical = [CanonicalAlgorithm.from_registered(r) for r in registered]

    coverage = build_coverage_manifest(canonical, curated_algorithm_to_problem, generated_slugs, skipped)
    coverage_summary = summarize(coverage)

    # Best-effort diagnostic artifact -- writes to the current working
    # directory rather than assuming a specific repo-root path, since this
    # module is imported both from a full repo checkout (scripts/
    # seed_atlas_code.py, cwd = repo root) and from inside the deployed
    # backend (main.py's boot-time auto-seed, cwd = /app in Docker). Never
    # allowed to fail seeding itself -- a read-only or unexpected filesystem
    # should not block the actual database writes below.
    try:
        manifest_path = Path.cwd() / "atlascode_coverage.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "canonical_algorithm_count": len(canonical),
                    "status_summary": coverage_summary,
                    "algorithms": [e.to_dict() for e in coverage],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Coverage manifest written: {manifest_path} ({len(coverage)} canonical algorithms)")
    except OSError as exc:
        print(f"Coverage manifest write skipped ({exc}) -- non-fatal, seeding continues.")

    visible_tests = sum(1 for _, tcs in all_problems for tc in tcs if not tc["is_hidden"])
    hidden_tests = sum(1 for _, tcs in all_problems for tc in tcs if tc["is_hidden"])
    language_templates = sum(len(p["starter_code"]) for p, _ in all_problems)
    validation_failures = 0

    # ── Validation (runs regardless of dry-run/validate-only) ────────────────
    seen_slugs: set[str] = set()
    for prob_data, tc_list in all_problems:
        if prob_data["id"] in seen_slugs:
            print(f"  VALIDATION FAILURE: duplicate problem slug '{prob_data['id']}'")
            validation_failures += 1
            continue
        seen_slugs.add(prob_data["id"])
        if not tc_list:
            print(f"  VALIDATION FAILURE: '{prob_data['id']}' has zero test cases")
            validation_failures += 1
        if not any(not tc["is_hidden"] for tc in tc_list):
            print(f"  VALIDATION FAILURE: '{prob_data['id']}' has no visible test case")
            validation_failures += 1
        if not any(tc["is_hidden"] for tc in tc_list):
            print(f"  VALIDATION FAILURE: '{prob_data['id']}' has no hidden test case")
            validation_failures += 1

    if validate_only:
        print(f"\nValidate-only run — {len(all_problems)} problem(s) checked, "
              f"{validation_failures} failure(s). No database writes performed.")
        _print_summary(canonical, curated_slugs, generated_slugs, coverage_summary,
                        len(all_problems), visible_tests, hidden_tests, language_templates,
                        validation_failures)
        return

    await init_db()
    async with AsyncSessionLocal() as db:
        seeded = 0
        for prob_data, tc_list in all_problems:
            existing = await db.execute(select(Problem).where(Problem.id == prob_data["id"]))
            existing_row = existing.scalar_one_or_none()
            if existing_row:
                print(f"  skip  {prob_data['id']} (already exists)")
                continue

            if dry_run:
                seeded += 1
                print(f"  [dry-run] would add {prob_data['id']} ({prob_data['difficulty']}) — {len(tc_list)} test cases")
                continue

            problem = Problem(**prob_data)
            db.add(problem)
            await db.flush()

            for tc in tc_list:
                db.add(TestCase(problem_id=problem.id, **tc))

            # Record Python Function Mode as verified (Level 6) the moment a
            # problem is seeded -- not an assumption, a fact: every problem's
            # test data here was generated FROM a Python reference solution
            # (see the family builders' independent oracles / plugin-terminal-
            # state-with-invariant-check), so Python correctness is guaranteed
            # by construction. Without this, a freshly auto-seeded database
            # (e.g. a first Render deploy) would show every problem as
            # "In Progress" until a separate multi-language verification pass
            # runs, contradicting the actual state of the data. Matches the
            # schema in apps/backend/algorithm_atlas/database.py's
            # _ensure_ledger_table / scripts/atlascode_ledger.py.
            await db.execute(text(
                "INSERT OR IGNORE INTO atlascode_matrix_ledger "
                "(problem_id, language, mode, verification_level, status, timestamp) "
                "VALUES (:pid, 'python', 'function', 6, 'pass', :ts)"
            ), {"pid": problem.id, "ts": time.time()})

            seeded += 1
            print(f"  added {problem.id} ({problem.difficulty}) — {len(tc_list)} test cases")

        if not dry_run:
            # Seed today's daily challenge to the first Easy problem if not set
            today = date.today()
            existing_dc = await db.execute(select(DailyChallenge).where(DailyChallenge.date == today))
            if not existing_dc.scalar_one_or_none() and PROBLEMS:
                db.add(DailyChallenge(date=today, problem_id=PROBLEMS[0][0]["id"], bonus_xp=50))
                print(f"  daily challenge set for {today}: {PROBLEMS[0][0]['id']}")

            await db.commit()

        print(f"\n{'[dry-run] would seed' if dry_run else 'Done — seeded'} {seeded} new problem(s).")

    _print_summary(canonical, curated_slugs, generated_slugs, coverage_summary,
                    len(all_problems), visible_tests, hidden_tests, language_templates,
                    validation_failures)


def _print_summary(canonical, curated_slugs, generated_slugs, coverage_summary,
                    total_problems, visible_tests, hidden_tests, language_templates,
                    validation_failures) -> None:
    mapped = len(curated_slugs) + len(generated_slugs)
    print("\n" + "=" * 50)
    print("ATLASCODE SEED SUMMARY")
    print("=" * 50)
    print(f"Canonical algorithms: {len(canonical)}")
    print(f"Curated algorithms covered: {len(curated_slugs)}")
    print(f"Generated-family algorithms covered: {len(generated_slugs)} (problem COUNT may exceed this — variant families ship multiple problems per algorithm)")
    print(f"Total AtlasCode problems (all rows, curated+generated+variants): {total_problems}")
    print(f"Mapped algorithms: {mapped}")
    print(f"Unsupported algorithms: {coverage_summary.get('UNSUPPORTED', 0)}")
    print(f"Needs review: {coverage_summary.get('NEEDS_REVIEW', 0)}")
    print(f"Visible tests: {visible_tests}")
    print(f"Hidden tests: {hidden_tests}")
    print(f"Language templates: {language_templates}")
    print(f"Validation failures: {validation_failures}")
    print("=" * 50)
    print("Status breakdown:")
    for status, count in sorted(coverage_summary.items()):
        print(f"  {status}: {count}")
    print("=" * 50)
