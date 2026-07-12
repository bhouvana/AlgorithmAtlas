"""Closes the small partial-coverage gap discovered by auditing the ledger:
7 problems (two-sum, maximum-subarray, prime-factorization,
contains-duplicate-within-k, merge-overlapping-intervals,
max-depth-binary-tree, construct-tree-preorder-inorder) were already
Level-6 verified for csharp/perl/c/rust (their original bounded ladders)
but never attempted for javascript/typescript/java/cpp. min-stack-simulation
(missing only for c) is EXCLUDED here on purpose -- it needs a tuple-typed
parameter, and docs/atlascode-bigint-numeric-audit.json's sibling audit
(docs/atlascode-tuple-capability-matrix.json) already established C has no
tuple support at all (a permanent architectural gap, not a to-do).

Unlike sort/search, these 7 problems are NOT one shared shape -- each gets
its own genuine algorithm per language (hashmap two-sum, Kadane's, trial-
division factorization, sliding-window duplicate check, interval merge,
recursive tree depth, preorder+inorder tree reconstruction), verified via
the real judge before being trusted, same as every other batch this session.
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))
import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.atlascode.function_mode.contracts import FunctionContract
from algorithm_atlas.atlascode.function_mode.runner import FunctionCase, evaluate_function

import atlascode_ledger as ledger

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"

_TARGET_LANGUAGES = ["javascript", "typescript", "java", "cpp"]

_JAVA_TREE_HELPER = (
    "class TreeNode {\n"
    "    int val;\n"
    "    TreeNode left;\n"
    "    TreeNode right;\n"
    "    TreeNode() {}\n"
    "    TreeNode(int val) { this.val = val; }\n"
    "    TreeNode(int val, TreeNode left, TreeNode right) { this.val = val; this.left = left; this.right = right; }\n"
    "}\n"
)
_CPP_TREE_HELPER = (
    "struct TreeNode {\n"
    "    int val;\n"
    "    TreeNode *left;\n"
    "    TreeNode *right;\n"
    "    TreeNode() : val(0), left(nullptr), right(nullptr) {}\n"
    "    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}\n"
    "    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}\n"
    "};\n"
)
_TS_TREE_HELPER = (
    "interface TreeNode {\n  val: number;\n  left: TreeNode | null;\n  right: TreeNode | null;\n}\n"
)


# ── two-sum ──────────────────────────────────────────────────────────────────
def _js_two_sum(wrong):
    body = (
        "function two_sum(nums, target) {\n"
        "    const seen = {};\n"
        "    for (let i = 0; i < nums.length; i++) {\n"
        "        const c = target - nums[i];\n"
        "        if (seen[c] !== undefined) return [seen[c]" + (" + 1" if wrong else "") + ", i" + (" + 1" if wrong else "") + "];\n"
        "        if (!(nums[i] in seen)) seen[nums[i]] = i;\n"
        "    }\n"
        "    return [-1, -1];\n"
        "}\n"
    )
    return body


def _ts_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "function two_sum(nums: number[], target: number): number[] {\n"
        "    const seen: Record<number, number> = {};\n"
        "    for (let i = 0; i < nums.length; i++) {\n"
        "        const c = target - nums[i];\n"
        f"        if (seen[c] !== undefined) return [seen[c]{a}, i{a}];\n"
        "        if (!(nums[i] in seen)) seen[nums[i]] = i;\n"
        "    }\n"
        "    return [-1, -1];\n"
        "}\n"
    )


def _java_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public int[] two_sum(int[] nums, int target) {\n"
        "        java.util.HashMap<Integer,Integer> seen = new java.util.HashMap<>();\n"
        "        for (int i=0;i<nums.length;i++) {\n"
        "            int c = target - nums[i];\n"
        f"            if (seen.containsKey(c)) return new int[]{{seen.get(c){a}, i{a}}};\n"
        "            if (!seen.containsKey(nums[i])) seen.put(nums[i], i);\n"
        "        }\n"
        "        return new int[]{-1,-1};\n"
        "    }\n"
        "}\n"
    )


def _cpp_two_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    std::vector<int> two_sum(std::vector<int> nums, int target) {\n"
        "        std::unordered_map<int,int> seen;\n"
        "        for (int i=0;i<(int)nums.size();i++) {\n"
        "            int c = target - nums[i];\n"
        "            auto it = seen.find(c);\n"
        f"            if (it != seen.end()) return {{it->second{a}, i{a}}};\n"
        "            if (seen.find(nums[i]) == seen.end()) seen[nums[i]] = i;\n"
        "        }\n"
        "        return {-1,-1};\n"
        "    }\n"
        "};\n"
    )


# ── maximum-subarray (Kadane's) ──────────────────────────────────────────────
def _js_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "function max_subarray(nums) {\n"
        "    let best = nums[0], cur = nums[0];\n"
        "    for (let i = 1; i < nums.length; i++) { cur = Math.max(nums[i], cur + nums[i]); best = Math.max(best, cur); }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _ts_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "function max_subarray(nums: number[]): number {\n"
        "    let best = nums[0], cur = nums[0];\n"
        "    for (let i = 1; i < nums.length; i++) { cur = Math.max(nums[i], cur + nums[i]); best = Math.max(best, cur); }\n"
        f"    return best{a};\n"
        "}\n"
    )


def _java_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "    public int max_subarray(int[] nums) {\n"
        "        int best = nums[0], cur = nums[0];\n"
        "        for (int i=1;i<nums.length;i++) { cur = Math.max(nums[i], cur+nums[i]); best = Math.max(best, cur); }\n"
        f"        return best{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_max_subarray(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Solution {\n"
        "public:\n"
        "    int max_subarray(std::vector<int> nums) {\n"
        "        int best = nums[0], cur = nums[0];\n"
        "        for (int i=1;i<(int)nums.size();i++) { cur = std::max(nums[i], cur+nums[i]); best = std::max(best, cur); }\n"
        f"        return best{a};\n"
        "    }\n"
        "};\n"
    )


# ── prime-factorization (trial division, space-joined ascending factors) ────
def _js_prime_fact(wrong):
    push = "factors.push(d + 1);" if wrong else "factors.push(d);"
    return (
        "function prime_factorization(n) {\n"
        "    const factors = [];\n"
        "    let d = 2;\n"
        "    while (d * d <= n) {\n"
        "        while (n % d === 0) { " + push + " n = Math.floor(n / d); }\n"
        "        d++;\n"
        "    }\n"
        "    if (n > 1) factors.push(n);\n"
        "    return factors.join(' ');\n"
        "}\n"
    )


def _ts_prime_fact(wrong):
    push = "factors.push(d + 1);" if wrong else "factors.push(d);"
    return (
        "function prime_factorization(n: number): string {\n"
        "    const factors: number[] = [];\n"
        "    let d = 2;\n"
        "    while (d * d <= n) {\n"
        "        while (n % d === 0) { " + push + " n = Math.floor(n / d); }\n"
        "        d++;\n"
        "    }\n"
        "    if (n > 1) factors.push(n);\n"
        "    return factors.join(' ');\n"
        "}\n"
    )


def _java_prime_fact(wrong):
    push = "factors.add(d + 1);" if wrong else "factors.add(d);"
    return (
        "class Solution {\n"
        "    public String prime_factorization(int n) {\n"
        "        java.util.List<Integer> factors = new java.util.ArrayList<>();\n"
        "        int d = 2;\n"
        "        while ((long) d * d <= n) {\n"
        "            while (n % d == 0) { " + push + " n /= d; }\n"
        "            d++;\n"
        "        }\n"
        "        if (n > 1) factors.add(n);\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        for (int i=0;i<factors.size();i++) { if (i>0) sb.append(' '); sb.append(factors.get(i)); }\n"
        "        return sb.toString();\n"
        "    }\n"
        "}\n"
    )


def _cpp_prime_fact(wrong):
    push = "factors.push_back(d + 1);" if wrong else "factors.push_back(d);"
    return (
        "class Solution {\n"
        "public:\n"
        "    std::string prime_factorization(int n) {\n"
        "        std::vector<int> factors;\n"
        "        int d = 2;\n"
        "        while ((long long)d * d <= n) {\n"
        "            while (n % d == 0) { " + push + " n /= d; }\n"
        "            d++;\n"
        "        }\n"
        "        if (n > 1) factors.push_back(n);\n"
        "        std::string out;\n"
        "        for (size_t i=0;i<factors.size();i++) { if (i) out += ' '; out += std::to_string(factors[i]); }\n"
        "        return out;\n"
        "    }\n"
        "};\n"
    )


# ── contains-duplicate-within-k ──────────────────────────────────────────────
def _js_contains_dup(wrong):
    ret = "return false; // negated" if wrong else "return true;"
    neg = "!(" if wrong else "("
    close = ")" if wrong else ""
    return (
        "function contains_nearby_duplicate(nums, k) {\n"
        "    const last = {};\n"
        "    let found = false;\n"
        "    for (let i = 0; i < nums.length; i++) {\n"
        "        if (last[nums[i]] !== undefined && i - last[nums[i]] <= k) { found = true; }\n"
        "        last[nums[i]] = i;\n"
        "    }\n"
        f"    return {'!found' if wrong else 'found'};\n"
        "}\n"
    )


def _ts_contains_dup(wrong):
    return (
        "function contains_nearby_duplicate(nums: number[], k: number): boolean {\n"
        "    const last: Record<number, number> = {};\n"
        "    let found = false;\n"
        "    for (let i = 0; i < nums.length; i++) {\n"
        "        if (last[nums[i]] !== undefined && i - last[nums[i]] <= k) { found = true; }\n"
        "        last[nums[i]] = i;\n"
        "    }\n"
        f"    return {'!found' if wrong else 'found'};\n"
        "}\n"
    )


def _java_contains_dup(wrong):
    return (
        "class Solution {\n"
        "    public boolean contains_nearby_duplicate(int[] nums, int k) {\n"
        "        java.util.HashMap<Integer,Integer> last = new java.util.HashMap<>();\n"
        "        boolean found = false;\n"
        "        for (int i=0;i<nums.length;i++) {\n"
        "            if (last.containsKey(nums[i]) && i - last.get(nums[i]) <= k) { found = true; }\n"
        "            last.put(nums[i], i);\n"
        "        }\n"
        f"        return {'!found' if wrong else 'found'};\n"
        "    }\n"
        "}\n"
    )


def _cpp_contains_dup(wrong):
    return (
        "class Solution {\n"
        "public:\n"
        "    bool contains_nearby_duplicate(std::vector<int> nums, int k) {\n"
        "        std::unordered_map<int,int> last;\n"
        "        bool found = false;\n"
        "        for (int i=0;i<(int)nums.size();i++) {\n"
        "            auto it = last.find(nums[i]);\n"
        "            if (it != last.end() && i - it->second <= k) { found = true; }\n"
        "            last[nums[i]] = i;\n"
        "        }\n"
        f"        return {'!found' if wrong else 'found'};\n"
        "    }\n"
        "};\n"
    )


# ── merge-overlapping-intervals ──────────────────────────────────────────────
def _js_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "function merge_intervals(intervals) {\n"
        "    if (intervals.length === 0) return [];\n"
        "    const sorted = intervals.slice().map(x => x.slice()).sort((a,b) => a[0]-b[0]);\n"
        "    const result = [sorted[0]];\n"
        "    for (let i = 1; i < sorted.length; i++) {\n"
        "        const last = result[result.length-1];\n"
        "        const cur = sorted[i];\n"
        f"        if (cur[0] {op} last[1]) {{ last[1] = Math.max(last[1], cur[1]); }}\n"
        "        else result.push(cur);\n"
        "    }\n"
        "    return result;\n"
        "}\n"
    )


def _ts_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "function merge_intervals(intervals: number[][]): number[][] {\n"
        "    if (intervals.length === 0) return [];\n"
        "    const sorted = intervals.map(x => x.slice()).sort((a,b) => a[0]-b[0]);\n"
        "    const result: number[][] = [sorted[0]];\n"
        "    for (let i = 1; i < sorted.length; i++) {\n"
        "        const last = result[result.length-1];\n"
        "        const cur = sorted[i];\n"
        f"        if (cur[0] {op} last[1]) {{ last[1] = Math.max(last[1], cur[1]); }}\n"
        "        else result.push(cur);\n"
        "    }\n"
        "    return result;\n"
        "}\n"
    )


def _java_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "class Solution {\n"
        "    public int[][] merge_intervals(int[][] intervals) {\n"
        "        int n = intervals.length;\n"
        "        if (n == 0) return new int[0][0];\n"
        "        Integer[] idx = new Integer[n];\n"
        "        for (int i=0;i<n;i++) idx[i]=i;\n"
        "        java.util.Arrays.sort(idx, (a,b) -> intervals[a][0]-intervals[b][0]);\n"
        "        java.util.List<int[]> result = new java.util.ArrayList<>();\n"
        "        for (int k=0;k<n;k++) {\n"
        "            int[] cur = intervals[idx[k]];\n"
        "            if (!result.isEmpty()) {\n"
        "                int[] last = result.get(result.size()-1);\n"
        f"                if (cur[0] {op} last[1]) {{ last[1] = Math.max(last[1], cur[1]); continue; }}\n"
        "            }\n"
        "            result.add(new int[]{cur[0], cur[1]});\n"
        "        }\n"
        "        return result.toArray(new int[0][]);\n"
        "    }\n"
        "}\n"
    )


def _cpp_merge_intervals(wrong):
    op = "<" if wrong else "<="
    return (
        "class Solution {\n"
        "public:\n"
        "    std::vector<std::vector<int>> merge_intervals(std::vector<std::vector<int>> intervals) {\n"
        "        if (intervals.empty()) return {};\n"
        "        std::sort(intervals.begin(), intervals.end(), [](const std::vector<int>& a, const std::vector<int>& b){ return a[0] < b[0]; });\n"
        "        std::vector<std::vector<int>> result;\n"
        "        result.push_back(intervals[0]);\n"
        "        for (size_t i=1;i<intervals.size();i++) {\n"
        "            auto& last = result.back();\n"
        "            auto& cur = intervals[i];\n"
        f"            if (cur[0] {op} last[1]) {{ last[1] = std::max(last[1], cur[1]); }}\n"
        "            else result.push_back(cur);\n"
        "        }\n"
        "        return result;\n"
        "    }\n"
        "};\n"
    )


# ── max-depth-binary-tree ────────────────────────────────────────────────────
def _js_max_depth(wrong):
    a = "" if wrong else "1 + "
    return (
        "function max_depth(root) {\n"
        "    if (root === null) return 0;\n"
        f"    return {a}Math.max(max_depth(root.left), max_depth(root.right));\n"
        "}\n"
    )


def _ts_max_depth(wrong):
    a = "" if wrong else "1 + "
    return (
        _TS_TREE_HELPER +
        "function max_depth(root: TreeNode | null): number {\n"
        "    if (root === null) return 0;\n"
        f"    return {a}Math.max(max_depth(root.left), max_depth(root.right));\n"
        "}\n"
    )


def _java_max_depth(wrong):
    a = "" if wrong else "1 + "
    return (
        _JAVA_TREE_HELPER +
        "class Solution {\n"
        "    public int max_depth(TreeNode root) {\n"
        "        if (root == null) return 0;\n"
        f"        return {a}Math.max(max_depth(root.left), max_depth(root.right));\n"
        "    }\n"
        "}\n"
    )


def _cpp_max_depth(wrong):
    a = "" if wrong else "1 + "
    return (
        _CPP_TREE_HELPER +
        "class Solution {\n"
        "public:\n"
        "    int max_depth(TreeNode* root) {\n"
        "        if (root == nullptr) return 0;\n"
        f"        return {a}std::max(max_depth(root->left), max_depth(root->right));\n"
        "    }\n"
        "};\n"
    )


# ── construct-tree-preorder-inorder (swap left/right subtree calls if wrong) ─
def _js_build_tree(wrong):
    left_expr, right_expr = ("preorder.slice(1 + mid), inorder.slice(mid + 1)",
                              "preorder.slice(1, 1 + mid), inorder.slice(0, mid)") if wrong else \
        ("preorder.slice(1, 1 + mid), inorder.slice(0, mid)",
         "preorder.slice(1 + mid), inorder.slice(mid + 1)")
    return (
        "function build_tree(preorder, inorder) {\n"
        "    if (preorder.length === 0) return null;\n"
        "    const rootVal = preorder[0];\n"
        "    const mid = inorder.indexOf(rootVal);\n"
        "    const root = { val: rootVal, left: null, right: null };\n"
        f"    root.left = build_tree({left_expr});\n"
        f"    root.right = build_tree({right_expr});\n"
        "    return root;\n"
        "}\n"
    )


def _ts_build_tree(wrong):
    left_expr, right_expr = ("preorder.slice(1 + mid), inorder.slice(mid + 1)",
                              "preorder.slice(1, 1 + mid), inorder.slice(0, mid)") if wrong else \
        ("preorder.slice(1, 1 + mid), inorder.slice(0, mid)",
         "preorder.slice(1 + mid), inorder.slice(mid + 1)")
    return (
        _TS_TREE_HELPER +
        "function build_tree(preorder: number[], inorder: number[]): TreeNode | null {\n"
        "    if (preorder.length === 0) return null;\n"
        "    const rootVal = preorder[0];\n"
        "    const mid = inorder.indexOf(rootVal);\n"
        "    const root: TreeNode = { val: rootVal, left: null, right: null };\n"
        f"    root.left = build_tree({left_expr});\n"
        f"    root.right = build_tree({right_expr});\n"
        "    return root;\n"
        "}\n"
    )


def _java_build_tree(wrong):
    return (
        _JAVA_TREE_HELPER +
        "class Solution {\n"
        "    public TreeNode build_tree(int[] preorder, int[] inorder) {\n"
        "        return helper(preorder, 0, preorder.length, inorder, 0, inorder.length);\n"
        "    }\n"
        "    private TreeNode helper(int[] pre, int ps, int pe, int[] in, int is, int ie) {\n"
        "        if (ps >= pe) return null;\n"
        "        int rootVal = pre[ps];\n"
        "        int mid = is;\n"
        "        while (in[mid] != rootVal) mid++;\n"
        "        int leftSize = mid - is;\n"
        "        TreeNode root = new TreeNode(rootVal);\n"
        + ("        root.left = helper(pre, ps + 1 + leftSize, pe, in, mid + 1, ie);\n"
           "        root.right = helper(pre, ps + 1, ps + 1 + leftSize, in, is, mid);\n"
           if wrong else
           "        root.left = helper(pre, ps + 1, ps + 1 + leftSize, in, is, mid);\n"
           "        root.right = helper(pre, ps + 1 + leftSize, pe, in, mid + 1, ie);\n") +
        "        return root;\n"
        "    }\n"
        "}\n"
    )


def _cpp_build_tree(wrong):
    return (
        _CPP_TREE_HELPER +
        "class Solution {\n"
        "public:\n"
        "    TreeNode* build_tree(std::vector<int> preorder, std::vector<int> inorder) {\n"
        "        return helper(preorder, 0, (int)preorder.size(), inorder, 0, (int)inorder.size());\n"
        "    }\n"
        "    TreeNode* helper(std::vector<int>& pre, int ps, int pe, std::vector<int>& in, int is, int ie) {\n"
        "        if (ps >= pe) return nullptr;\n"
        "        int rootVal = pre[ps];\n"
        "        int mid = is;\n"
        "        while (in[mid] != rootVal) mid++;\n"
        "        int leftSize = mid - is;\n"
        "        TreeNode* root = new TreeNode(rootVal);\n"
        + ("        root->left = helper(pre, ps + 1 + leftSize, pe, in, mid + 1, ie);\n"
           "        root->right = helper(pre, ps + 1, ps + 1 + leftSize, in, is, mid);\n"
           if wrong else
           "        root->left = helper(pre, ps + 1, ps + 1 + leftSize, in, is, mid);\n"
           "        root->right = helper(pre, ps + 1 + leftSize, pe, in, mid + 1, ie);\n") +
        "        return root;\n"
        "    }\n"
        "};\n"
    )


_PROBLEM_BUILDERS = {
    "two-sum": {"javascript": _js_two_sum, "typescript": _ts_two_sum, "java": _java_two_sum, "cpp": _cpp_two_sum},
    "maximum-subarray": {"javascript": _js_max_subarray, "typescript": _ts_max_subarray, "java": _java_max_subarray, "cpp": _cpp_max_subarray},
    "prime-factorization": {"javascript": _js_prime_fact, "typescript": _ts_prime_fact, "java": _java_prime_fact, "cpp": _cpp_prime_fact},
    "contains-duplicate-within-k": {"javascript": _js_contains_dup, "typescript": _ts_contains_dup, "java": _java_contains_dup, "cpp": _cpp_contains_dup},
    "merge-overlapping-intervals": {"javascript": _js_merge_intervals, "typescript": _ts_merge_intervals, "java": _java_merge_intervals, "cpp": _cpp_merge_intervals},
    "max-depth-binary-tree": {"javascript": _js_max_depth, "typescript": _ts_max_depth, "java": _java_max_depth, "cpp": _cpp_max_depth},
    "construct-tree-preorder-inorder": {"javascript": _js_build_tree, "typescript": _ts_build_tree, "java": _java_build_tree, "cpp": _cpp_build_tree},
}


def _maybe_json(v):
    return json.loads(v) if isinstance(v, str) else v


def load_problem(con, pid):
    row = con.execute("SELECT function_contract, test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    contract = FunctionContract.from_dict(json.loads(row["function_contract"]))
    cur = con.execute(
        "SELECT id, function_args, function_expected, \"order\" FROM test_cases "
        "WHERE problem_id=? AND function_args IS NOT NULL ORDER BY \"order\"", (pid,),
    )
    cases = [
        FunctionCase(id=r["id"], arguments=_maybe_json(r["function_args"]), expected=_maybe_json(r["function_expected"]),
                     has_expected=True, is_hidden=False, order=r["order"])
        for r in cur.fetchall()
    ]
    return contract, cases, row["function_contract"], row["test_suite_version"]


async def verify_one(pid, lang, contract, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate_function(build(False), lang, contract, cases)
    n_pass = sum(1 for r in correct_result.case_results if r.passed)
    if n_pass != len(cases):
        sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{n_pass}/{len(cases)} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:200]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:200]} "
                          f"actual={(sample_fail.actual_return if sample_fail else '')!r} "
                          f"expected={(sample_fail.expected_return if sample_fail else '')!r}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate_function(build(True), lang, contract, cases)
    n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
    if n_wrong_pass >= len(cases):
        return {"pid": pid, "lang": lang, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {len(cases)}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "lang": lang, "outcome": "verified",
            "detail": f"{n_pass}/{len(cases)} correct, wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)

    results = []
    skipped = 0
    for lang in _TARGET_LANGUAGES:
        for pid, per_lang_builders in _PROBLEM_BUILDERS.items():
            contract, cases, raw_contract, tsv = load_problem(con, pid)
            cv = ledger.contract_hash(raw_contract)
            if ledger.already_verified(con, pid, lang, "function", contract_version=cv, test_suite_version=tsv):
                skipped += 1
                continue
            r = await verify_one(pid, lang, contract, cases, per_lang_builders[lang])
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s} {pid:32s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(
                    con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-ladder-gap-v1",
                    contract_version=cv, test_suite_version=tsv,
                    duration_ms=r["duration_ms"],
                )

    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL attempted: {len(results)}  skipped: {skipped}")
    print(f"verified={len(verified)}  reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")

    (REPO_ROOT / "docs" / "atlascode-ladder-gap-closure.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
