"""Real, subprocess-verified 8-problem Swift Function Mode ladder (mission
Phase 30). Mirrors the manual verification already done for Rust/C/C#/Perl/
Go/Ruby/PHP/R/Kotlin/Scala this session -- runs BOTH a correct and a
deliberately-wrong solution through the actual judge pipeline (real swiftc
subprocess compiles, real executable runs), never inferred.

No tuple support yet (see compiled_adapters.py's Swift section docstring) --
min-stack-simulation excluded, same as C_LADDER/GO_LADDER.

NOTE: calling `algorithm_atlas.main.app` directly via ASGITransport (bypassing
uvicorn) leaves an aiosqlite background thread alive after the real work
finishes, which hangs the interpreter's own clean-shutdown thread-join
indefinitely -- confirmed via faulthandler.dump_traceback_later that the
actual test coroutine had already completed and only a daemon DB thread
remained. Not a bug in the Swift adapter; worked around here with os._exit(0)
once every case has been printed.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "apps/backend")
from algorithm_atlas.main import app  # noqa: E402

LADDER = [
    "two-sum", "max-depth-binary-tree", "construct-tree-preorder-inorder",
    "bubble-sort", "maximum-subarray", "contains-duplicate-within-k",
    "merge-overlapping-intervals", "prime-factorization",
]

SOLUTIONS: dict[str, tuple[str, str]] = {
    "two-sum": (
        "func two_sum(_ nums: [Int], _ target: Int) -> [Int] {\n"
        "    var seen: [Int: Int] = [:]\n"
        "    for (i, n) in nums.enumerated() {\n"
        "        if let j = seen[target - n] { return [j, i] }\n"
        "        seen[n] = i\n"
        "    }\n"
        "    return []\n"
        "}\n",
        "func two_sum(_ nums: [Int], _ target: Int) -> [Int] { return [0, 0] }\n",
    ),
    "max-depth-binary-tree": (
        "func max_depth(_ root: TreeNode?) -> Int {\n"
        "    guard let root = root else { return 0 }\n"
        "    return 1 + max(max_depth(root.left), max_depth(root.right))\n"
        "}\n",
        "func max_depth(_ root: TreeNode?) -> Int { return 0 }\n",
    ),
    "construct-tree-preorder-inorder": (
        "func build_tree(_ preorder: [Int], _ inorder: [Int]) -> TreeNode? {\n"
        "    if preorder.isEmpty { return nil }\n"
        "    let rootVal = preorder[0]\n"
        "    let root = TreeNode(rootVal)\n"
        "    let mid = inorder.firstIndex(of: rootVal)!\n"
        "    let leftIn = Array(inorder[0..<mid])\n"
        "    let rightIn = Array(inorder[(mid+1)...])\n"
        "    let leftPre = Array(preorder[1..<(1+leftIn.count)])\n"
        "    let rightPre = Array(preorder[(1+leftIn.count)...])\n"
        "    root.left = build_tree(leftPre, leftIn)\n"
        "    root.right = build_tree(rightPre, rightIn)\n"
        "    return root\n"
        "}\n",
        "func build_tree(_ preorder: [Int], _ inorder: [Int]) -> TreeNode? { return nil }\n",
    ),
    "bubble-sort": (
        "func bubble_sort(_ arr: inout [Int]) {\n"
        "    let n = arr.count\n"
        "    for i in 0..<n {\n"
        "        for j in 0..<(n-1-i) {\n"
        "            if arr[j] > arr[j+1] { arr.swapAt(j, j+1) }\n"
        "        }\n"
        "    }\n"
        "}\n",
        "func bubble_sort(_ arr: inout [Int]) { }\n",
    ),
    "maximum-subarray": (
        "func max_subarray(_ nums: [Int]) -> Int {\n"
        "    var best = nums[0]\n"
        "    var cur = nums[0]\n"
        "    for n in nums.dropFirst() {\n"
        "        cur = max(n, cur + n)\n"
        "        best = max(best, cur)\n"
        "    }\n"
        "    return best\n"
        "}\n",
        "func max_subarray(_ nums: [Int]) -> Int { return 0 }\n",
    ),
    "contains-duplicate-within-k": (
        "func contains_nearby_duplicate(_ nums: [Int], _ k: Int) -> Bool {\n"
        "    var last: [Int: Int] = [:]\n"
        "    for (i, n) in nums.enumerated() {\n"
        "        if let j = last[n], i - j <= k { return true }\n"
        "        last[n] = i\n"
        "    }\n"
        "    return false\n"
        "}\n",
        "func contains_nearby_duplicate(_ nums: [Int], _ k: Int) -> Bool { return false }\n",
    ),
    "merge-overlapping-intervals": (
        "func merge_intervals(_ intervals: [[Int]]) -> [[Int]] {\n"
        "    if intervals.isEmpty { return [] }\n"
        "    let sorted = intervals.sorted { $0[0] < $1[0] }\n"
        "    var out: [[Int]] = [sorted[0]]\n"
        "    for iv in sorted.dropFirst() {\n"
        "        if iv[0] <= out[out.count-1][1] {\n"
        "            out[out.count-1][1] = max(out[out.count-1][1], iv[1])\n"
        "        } else {\n"
        "            out.append(iv)\n"
        "        }\n"
        "    }\n"
        "    return out\n"
        "}\n",
        "func merge_intervals(_ intervals: [[Int]]) -> [[Int]] { return intervals }\n",
    ),
    "prime-factorization": (
        "func prime_factorization(_ n: Int) -> String {\n"
        "    var out: [Int] = []\n"
        "    var m = n\n"
        "    var p = 2\n"
        "    while p * p <= m {\n"
        "        while m % p == 0 { out.append(p); m /= p }\n"
        "        p += 1\n"
        "    }\n"
        "    if m > 1 { out.append(m) }\n"
        "    return out.map { String($0) }.joined(separator: \" \")\n"
        "}\n",
        "func prime_factorization(_ n: Int) -> String { return \"\" }\n",
    ),
}


async def run_one(client: AsyncClient, pid: str, code: str) -> dict:
    body = {"language": "swift", "code": code, "mode": "visible", "execution_mode": "function"}
    r = await client.post(f"/api/v1/problems/{pid}/run", json=body)
    return r.json()


async def main() -> None:
    transport = ASGITransport(app=app)
    failures = 0
    async with AsyncClient(transport=transport, base_url="http://test", timeout=120.0) as client:
        for pid in LADDER:
            good, wrong = SOLUTIONS[pid]
            gbody = await run_one(client, pid, good)
            gsummary = gbody.get("summary", {})
            gpassed = gsummary.get("passed", 0)
            gtotal = gsummary.get("total", 0)
            gverdict = gbody.get("status")
            wbody = await run_one(client, pid, wrong)
            wsummary = wbody.get("summary", {})
            wpassed = wsummary.get("passed", 0)
            wtotal = wsummary.get("total", 0)
            wrejected = wpassed < wtotal
            ok = (gpassed == gtotal and gtotal > 0) and wrejected
            if not ok:
                failures += 1
                print(f"!!! {pid}: correct compile_output={gbody.get('compile_output')!r} wrong compile_output={wbody.get('compile_output')!r}")
            print(f"=== {pid} === correct: {gpassed}/{gtotal} status={gverdict}  wrong: {wpassed}/{wtotal} rejected={wrejected}")
    print(f"\n{'ALL PASSED' if failures == 0 else f'{failures} FAILURES'}")
    os._exit(0 if failures == 0 else 1)


asyncio.run(main())
