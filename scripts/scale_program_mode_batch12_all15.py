"""Program Mode expansion, batch 12: 3 more problems that were showing as
fully unstarted (15/15 gap) but fit EXISTING shapes with zero harness
changes: distinct-subsets-count (arr1), combination-sum-count (arr1_int,
same unbounded-combinations DP as coin-change-ways), knapsack-01
(arr2_int: weights=a, values=b, capacity=extra -- exact fit).
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import logging
logging.disable(logging.CRITICAL)

import atlascode_shapes_all15 as sh

add = sh.add

# ═════════════════════════════════════════════════════════════════════════
# count_distinct_subsets(nums) -> int, product of (multiplicity+1) over
# distinct values
# ═════════════════════════════════════════════════════════════════════════
add("distinct-subsets-count", "arr1", "count_distinct_subsets", "int", {
    "go": "counts := make(map[int]int)\nfor _, v := range nums { counts[v]++ }\nresult := int64(1)\nfor _, c := range counts { result *= int64(c + 1) }",
    "ruby": "counts = Hash.new(0)\nnums.each { |v| counts[v] += 1 }\nresult = 1\ncounts.each_value { |c| result *= (c + 1) }",
    "kotlin": "val counts = HashMap<Int, Int>()\nfor (v in nums) counts[v] = (counts[v] ?: 0) + 1\nvar result = 1L\nfor (c in counts.values) result *= (c + 1)",
    "php": "$counts = [];\nforeach ($nums as $v) { $counts[$v] = ($counts[$v] ?? 0) + 1; }\n$result = 1;\nforeach ($counts as $c) { $result *= ($c + 1); }",
    "scala": "val counts = scala.collection.mutable.HashMap[Int, Int]().withDefaultValue(0)\nfor (v <- nums) counts(v) += 1\nvar result: Long = 1\nfor (c <- counts.values) result *= (c + 1)",
    "r": "counts <- table(nums)\nresult <- 1\nfor (c in counts) result <- result * (c + 1)",
    "javascript": "const counts = new Map();\nfor (const v of nums) counts.set(v, (counts.get(v) || 0) + 1);\nlet result = 1;\nfor (const c of counts.values()) result *= (c + 1);",
    "typescript": "const counts = new Map<number, number>();\nfor (const v of nums) counts.set(v, (counts.get(v) || 0) + 1);\nlet result = 1;\nfor (const c of counts.values()) result *= (c + 1);",
    "perl": "my %counts;\nforeach my $v (@{$nums}) { $counts{$v}++; }\nmy $result = 1;\nforeach my $c (values %counts) { $result *= ($c + 1); }",
    "java": "java.util.Map<Integer, Integer> counts = new java.util.HashMap<>();\nfor (int v : nums) counts.merge(v, 1, Integer::sum);\nlong resultLong = 1;\nfor (int c : counts.values()) resultLong *= (c + 1);\nint result = (int) resultLong;",
    "cpp": "std::unordered_map<int, int> counts;\nfor (int v : nums) counts[v]++;\nlong long result = 1;\nfor (auto &p : counts) result *= (p.second + 1);",
    "csharp": "var counts = new System.Collections.Generic.Dictionary<int, int>();\nforeach (var v in nums) { counts[v] = counts.ContainsKey(v) ? counts[v] + 1 : 1; }\nlong result = 1;\nforeach (var c in counts.Values) result *= (c + 1);",
    "c": "int *vals = (int *)malloc(sizeof(int) * (size_t)(n > 0 ? n : 1));\nint *cnts = (int *)malloc(sizeof(int) * (size_t)(n > 0 ? n : 1));\nint m = 0;\nfor (int i = 0; i < n; i++) {\n    int x = nums[i];\n    int found = 0;\n    for (int j = 0; j < m; j++) { if (vals[j] == x) { cnts[j]++; found = 1; break; } }\n    if (!found) { vals[m] = x; cnts[m] = 1; m++; }\n}\nlong long result = 1;\nfor (int j = 0; j < m; j++) result *= (cnts[j] + 1);\nfree(vals); free(cnts);",
    "rust": "let mut counts = std::collections::HashMap::new();\nfor &v in nums.iter() { *counts.entry(v).or_insert(0) += 1; }\nlet mut result: i64 = 1;\nfor c in counts.values() { result *= (*c as i64 + 1); }\nlet result: i32 = result as i32;",
    "swift": "var counts: [Int: Int] = [:]\nfor v in nums { counts[v, default: 0] += 1 }\nvar result = 1\nfor c in counts.values { result *= (c + 1) }",
})

# ═════════════════════════════════════════════════════════════════════════
# combination_sum_count(nums=candidates, extra=target) -> int, count of
# combinations (order-independent, unlimited reuse) summing to target
# (identical structure to coin-change-ways: dp[0]=1, outer candidate,
# inner amount ascending)
# ═════════════════════════════════════════════════════════════════════════
# NOTE: expected values reach into the hundreds of billions (e.g.
# 720,411,193,148) -- same 32-bit overflow class as the documented
# bigint-blocked problems. go/kotlin/scala already map "int" kind to a
# 64-bit type (int64/Long) so they're safe; java/cpp/csharp/c/rust map it
# to a hard 32-bit int/i32 in this harness and would silently truncate --
# deliberately excluded below rather than shipping a wrong "verified" cell.
add("combination-sum-count", "arr1_int", "combination_sum_count", "int", {
    "go": "target := extra\ndp := make([]int64, target+1)\ndp[0] = 1\nfor _, c := range nums {\n\tfor i := c; i <= target; i++ { dp[i] += dp[i-c] }\n}\nresult := dp[target]",
    "ruby": "target = extra\ndp = Array.new(target + 1, 0)\ndp[0] = 1\nnums.each do |c|\n  (c..target).each { |i| dp[i] += dp[i - c] }\nend\nresult = dp[target]",
    "kotlin": "val target = extra\nval dp = LongArray(target + 1)\ndp[0] = 1\nfor (c in nums) {\n    for (i in c..target) dp[i] += dp[i - c]\n}\nval result = dp[target]",
    "php": "$target = $extra;\n$dp = array_fill(0, $target + 1, 0);\n$dp[0] = 1;\nforeach ($nums as $c) {\n    for ($i = $c; $i <= $target; $i++) { $dp[$i] += $dp[$i - $c]; }\n}\n$result = $dp[$target];",
    "scala": "val target = extra\nval dp = Array.fill(target + 1)(0L)\ndp(0) = 1\nfor (c <- nums) {\n  for (i <- c to target) dp(i) += dp(i - c)\n}\nval result: Long = dp(target)",
    "r": "target <- extra\ndp <- rep(0, target + 1)\ndp[1] <- 1\nfor (c in nums) {\n  if (c <= target) { for (i in c:target) { dp[i + 1] <- dp[i + 1] + dp[i - c + 1] } }\n}\nresult <- dp[target + 1]",
    "javascript": "const target = extra;\nconst dp = new Array(target + 1).fill(0);\ndp[0] = 1;\nfor (const c of nums) {\n    for (let i = c; i <= target; i++) dp[i] += dp[i - c];\n}\nconst result = dp[target];",
    "typescript": "const target = extra;\nconst dp: number[] = new Array(target + 1).fill(0);\ndp[0] = 1;\nfor (const c of nums) {\n    for (let i = c; i <= target; i++) dp[i] += dp[i - c];\n}\nconst result = dp[target];",
    "perl": "my $target = $extra;\nmy @dp = (0) x ($target + 1);\n$dp[0] = 1;\nforeach my $c (@{$nums}) {\n    for (my $i = $c; $i <= $target; $i++) { $dp[$i] += $dp[$i - $c]; }\n}\nmy $result = $dp[$target];",
    "swift": "let target = extra\nvar dp = [Int64](repeating: 0, count: target + 1)\ndp[0] = 1\nfor c in nums {\n    if c <= target {\n        for i in c...target { dp[i] += dp[i - c] }\n    }\n}\nlet result = Int(dp[target])",
}, skip=["java", "cpp", "csharp", "c", "rust"])

# ═════════════════════════════════════════════════════════════════════════
# knapsack(a=weights, b=values, extra=capacity) -> int, 0/1 knapsack max
# value
# ═════════════════════════════════════════════════════════════════════════
add("knapsack-01", "arr2_int", "knapsack", "int", {
    "go": "capacity := extra\ndp := make([]int, capacity+1)\nfor i := range a {\n\tw, v := a[i], b[i]\n\tfor cap := capacity; cap >= w; cap-- {\n\t\tif dp[cap-w]+v > dp[cap] { dp[cap] = dp[cap-w] + v }\n\t}\n}\nresult := int64(dp[capacity])",
    "ruby": "capacity = extra\ndp = Array.new(capacity + 1, 0)\na.each_index do |i|\n  w = a[i]\n  v = b[i]\n  capacity.downto(w) do |cap|\n    dp[cap] = [dp[cap], dp[cap - w] + v].max\n  end\nend\nresult = dp[capacity]",
    "kotlin": "val capacity = extra\nval dp = IntArray(capacity + 1)\nfor (i in a.indices) {\n    val w = a[i]\n    val v = b[i]\n    for (cap in capacity downTo w) {\n        if (dp[cap - w] + v > dp[cap]) dp[cap] = dp[cap - w] + v\n    }\n}\nval result = dp[capacity].toLong()",
    "php": "$capacity = $extra;\n$dp = array_fill(0, $capacity + 1, 0);\nfor ($i = 0; $i < count($a); $i++) {\n    $w = $a[$i]; $v = $b[$i];\n    for ($cap = $capacity; $cap >= $w; $cap--) {\n        if ($dp[$cap - $w] + $v > $dp[$cap]) { $dp[$cap] = $dp[$cap - $w] + $v; }\n    }\n}\n$result = $dp[$capacity];",
    "scala": "val capacity = extra\nval dp = Array.fill(capacity + 1)(0)\nfor (i <- a.indices) {\n  val w = a(i)\n  val v = b(i)\n  for (cap <- capacity to w by -1) {\n    if (dp(cap - w) + v > dp(cap)) dp(cap) = dp(cap - w) + v\n  }\n}\nval result: Long = dp(capacity)",
    "r": "capacity <- extra\ndp <- rep(0, capacity + 1)\nfor (i in seq_along(a)) {\n  w <- a[i]; v <- b[i]\n  if (w <= capacity) { for (cap in capacity:w) { if (dp[cap - w + 1] + v > dp[cap + 1]) dp[cap + 1] <- dp[cap - w + 1] + v } }\n}\nresult <- dp[capacity + 1]",
    "javascript": "const capacity = extra;\nconst dp = new Array(capacity + 1).fill(0);\nfor (let i = 0; i < a.length; i++) {\n    const w = a[i], v = b[i];\n    for (let cap = capacity; cap >= w; cap--) {\n        if (dp[cap - w] + v > dp[cap]) dp[cap] = dp[cap - w] + v;\n    }\n}\nconst result = dp[capacity];",
    "typescript": "const capacity = extra;\nconst dp: number[] = new Array(capacity + 1).fill(0);\nfor (let i = 0; i < a.length; i++) {\n    const w = a[i], v = b[i];\n    for (let cap = capacity; cap >= w; cap--) {\n        if (dp[cap - w] + v > dp[cap]) dp[cap] = dp[cap - w] + v;\n    }\n}\nconst result = dp[capacity];",
    "perl": "my $capacity = $extra;\nmy @dp = (0) x ($capacity + 1);\nfor (my $i = 0; $i < scalar(@{$a}); $i++) {\n    my $w = $a->[$i]; my $v = $b->[$i];\n    for (my $cap = $capacity; $cap >= $w; $cap--) {\n        if ($dp[$cap - $w] + $v > $dp[$cap]) { $dp[$cap] = $dp[$cap - $w] + $v; }\n    }\n}\nmy $result = $dp[$capacity];",
    "java": "int capacity = extra;\nint[] dp = new int[capacity + 1];\nfor (int i = 0; i < a.length; i++) {\n    int w = a[i], v = b[i];\n    for (int cap = capacity; cap >= w; cap--) {\n        if (dp[cap - w] + v > dp[cap]) dp[cap] = dp[cap - w] + v;\n    }\n}\nint result = dp[capacity];",
    "cpp": "int capacity = extra;\nstd::vector<int> dp(capacity + 1, 0);\nfor (size_t i = 0; i < a.size(); i++) {\n    int w = a[i], v = b[i];\n    for (int cap = capacity; cap >= w; cap--) {\n        if (dp[cap - w] + v > dp[cap]) dp[cap] = dp[cap - w] + v;\n    }\n}\nint result = dp[capacity];",
    "csharp": "int capacity = extra;\nvar dp = new int[capacity + 1];\nfor (int i = 0; i < a.Length; i++) {\n    int w = a[i], v = b[i];\n    for (int cap = capacity; cap >= w; cap--) {\n        if (dp[cap - w] + v > dp[cap]) dp[cap] = dp[cap - w] + v;\n    }\n}\nint result = dp[capacity];",
    "c": "int capacity = extra;\nint *dp = (int *)calloc((size_t)(capacity + 1), sizeof(int));\nfor (int i = 0; i < n; i++) {\n    int w = a[i], v = b[i];\n    for (int cap = capacity; cap >= w; cap--) {\n        if (dp[cap - w] + v > dp[cap]) dp[cap] = dp[cap - w] + v;\n    }\n}\nint result = dp[capacity];\nfree(dp);",
    "rust": "let capacity = extra as usize;\nlet mut dp = vec![0i32; capacity + 1];\nfor i in 0..a.len() {\n    let w = a[i] as usize;\n    let v = b[i];\n    let mut cap = capacity;\n    while cap >= w {\n        if dp[cap - w] + v > dp[cap] { dp[cap] = dp[cap - w] + v; }\n        if cap == 0 { break; }\n        cap -= 1;\n    }\n}\nlet result: i32 = dp[capacity];",
    "swift": "let capacity = extra\nvar dp = Array(repeating: 0, count: capacity + 1)\nfor i in 0..<a.count {\n    let w = a[i]\n    let v = b[i]\n    if w <= capacity {\n        var cap = capacity\n        while cap >= w {\n            if dp[cap - w] + v > dp[cap] { dp[cap] = dp[cap - w] + v }\n            cap -= 1\n        }\n    }\n}\nlet result = dp[capacity]",
})


if __name__ == "__main__":
    sys.exit(asyncio.run(sh.main()))
