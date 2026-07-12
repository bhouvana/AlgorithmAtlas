"""Program Mode expansion, batch 9: 13 easy/medium array problems (single-
number, majority-element, missing-number, maximum-subarray, house-robber,
jump-game, counting-inversions, longest-consecutive-sequence,
find-duplicate-number, trapping-rain-water, contains-duplicate-within-k,
longest-increasing-subsequence, three-sum-count-triplets) through the
all-15-language shape harness. Continuous-implementation pass per explicit
user direction: reuse existing infra, no re-architecture, keep batching.
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
# single_number(nums) -> XOR of all elements
# ═════════════════════════════════════════════════════════════════════════
add("single-number", "arr1", "single_number", "int", {
    "go": "result := int64(0)\nfor _, v := range nums { result ^= int64(v) }",
    "ruby": "result = 0\nnums.each { |v| result ^= v }",
    "kotlin": "var result = 0L\nfor (v in nums) result = result xor v.toLong()",
    "php": "$result = 0;\nforeach ($nums as $v) { $result ^= $v; }",
    "scala": "var result: Long = 0L\nfor (v <- nums) result ^= v.toLong",
    "r": "xor32 <- function(a, b) {\n  ua <- if (a < 0) a + 4294967296 else a\n  ub <- if (b < 0) b + 4294967296 else b\n  res <- 0\n  power <- 1\n  for (i in 0:31) {\n    bitA <- ua %% 2\n    bitB <- ub %% 2\n    if (bitA != bitB) res <- res + power\n    ua <- (ua - bitA) / 2\n    ub <- (ub - bitB) / 2\n    power <- power * 2\n  }\n  if (res >= 2147483648) res - 4294967296 else res\n}\nresult <- 0\nfor (v in nums) { result <- xor32(result, v) }",
    "javascript": "let result = 0;\nfor (const v of nums) result ^= v;",
    "typescript": "let result = 0;\nfor (const v of nums) result ^= v;",
    "perl": "my $result = 0;\nforeach my $v (@{$nums}) { $result ^= $v; }",
    "java": "int result = 0;\nfor (int v : nums) result ^= v;",
    "cpp": "int result = 0;\nfor (int v : nums) result ^= v;",
    "csharp": "int result = 0;\nforeach (var v in nums) result ^= v;",
    "c": "int result = 0;\nfor (int i = 0; i < n; i++) result ^= nums[i];",
    "rust": "let mut result: i32 = 0;\nfor v in nums.iter() { result ^= v; }",
    "swift": "var result = 0\nfor v in nums { result ^= v }",
})

# ═════════════════════════════════════════════════════════════════════════
# majority_element(nums) -> Boyer-Moore voting
# ═════════════════════════════════════════════════════════════════════════
add("majority-element", "arr1", "majority_element", "int", {
    "go": "count := 0\ncandidate := 0\nfor _, v := range nums {\n\tif count == 0 { candidate = v }\n\tif v == candidate { count++ } else { count-- }\n}\nresult := int64(candidate)",
    "ruby": "count = 0\ncandidate = 0\nnums.each do |v|\n  candidate = v if count == 0\n  count += (v == candidate ? 1 : -1)\nend\nresult = candidate",
    "kotlin": "var count = 0\nvar candidate = 0\nfor (v in nums) {\n    if (count == 0) candidate = v\n    count += if (v == candidate) 1 else -1\n}\nval result = candidate.toLong()",
    "php": "$count = 0; $candidate = 0;\nforeach ($nums as $v) {\n    if ($count == 0) { $candidate = $v; }\n    $count += ($v == $candidate) ? 1 : -1;\n}\n$result = $candidate;",
    "scala": "var count = 0\nvar candidate = 0\nfor (v <- nums) {\n  if (count == 0) candidate = v\n  count += (if (v == candidate) 1 else -1)\n}\nval result: Long = candidate",
    "r": "count <- 0\ncandidate <- 0\nfor (v in nums) {\n  if (count == 0) candidate <- v\n  count <- count + (if (v == candidate) 1 else -1)\n}\nresult <- candidate",
    "javascript": "let count = 0, candidate = 0;\nfor (const v of nums) {\n    if (count === 0) candidate = v;\n    count += (v === candidate) ? 1 : -1;\n}\nconst result = candidate;",
    "typescript": "let count = 0, candidate = 0;\nfor (const v of nums) {\n    if (count === 0) candidate = v;\n    count += (v === candidate) ? 1 : -1;\n}\nconst result = candidate;",
    "perl": "my $count = 0; my $candidate = 0;\nforeach my $v (@{$nums}) {\n    $candidate = $v if $count == 0;\n    $count += ($v == $candidate) ? 1 : -1;\n}\nmy $result = $candidate;",
    "java": "int count = 0, candidate = 0;\nfor (int v : nums) {\n    if (count == 0) candidate = v;\n    count += (v == candidate) ? 1 : -1;\n}\nint result = candidate;",
    "cpp": "int count = 0, candidate = 0;\nfor (int v : nums) {\n    if (count == 0) candidate = v;\n    count += (v == candidate) ? 1 : -1;\n}\nint result = candidate;",
    "csharp": "int count = 0, candidate = 0;\nforeach (var v in nums) {\n    if (count == 0) candidate = v;\n    count += (v == candidate) ? 1 : -1;\n}\nint result = candidate;",
    "c": "int count = 0, candidate = 0;\nfor (int i = 0; i < n; i++) {\n    if (count == 0) candidate = nums[i];\n    count += (nums[i] == candidate) ? 1 : -1;\n}\nint result = candidate;",
    "rust": "let mut count = 0;\nlet mut candidate = 0;\nfor &v in nums.iter() {\n    if count == 0 { candidate = v; }\n    count += if v == candidate { 1 } else { -1 };\n}\nlet result: i32 = candidate;",
    "swift": "var count = 0\nvar candidate = 0\nfor v in nums {\n    if count == 0 { candidate = v }\n    count += (v == candidate) ? 1 : -1\n}\nlet result = candidate",
})

# ═════════════════════════════════════════════════════════════════════════
# missing_number(nums) -> n*(n+1)/2 - sum(nums), array holds n distinct
# values from 0..n
# ═════════════════════════════════════════════════════════════════════════
add("missing-number", "arr1", "missing_number", "int", {
    "go": "n := len(nums)\nsum := 0\nfor _, v := range nums { sum += v }\nresult := int64(n*(n+1)/2 - sum)",
    "ruby": "n = nums.length\nsum = nums.sum\nresult = n * (n + 1) / 2 - sum",
    "kotlin": "val n = nums.size\nvar sum = 0\nfor (v in nums) sum += v\nval result = (n.toLong() * (n + 1) / 2 - sum)",
    "php": "$n = count($nums);\n$sum = array_sum($nums);\n$result = intdiv($n * ($n + 1), 2) - $sum;",
    "scala": "val n = nums.length\nvar sum = 0\nfor (v <- nums) sum += v\nval result: Long = n.toLong * (n + 1) / 2 - sum",
    "r": "n <- length(nums)\nresult <- as.integer(n * (n + 1) / 2 - sum(nums))",
    "javascript": "const n = nums.length;\nlet sum = 0;\nfor (const v of nums) sum += v;\nconst result = n * (n + 1) / 2 - sum;",
    "typescript": "const n = nums.length;\nlet sum = 0;\nfor (const v of nums) sum += v;\nconst result = n * (n + 1) / 2 - sum;",
    "perl": "my $n = scalar(@{$nums});\nmy $sum = 0;\nforeach my $v (@{$nums}) { $sum += $v; }\nmy $result = $n * ($n + 1) / 2 - $sum;",
    "java": "int n = nums.length;\nlong sum = 0;\nfor (int v : nums) sum += v;\nint result = (int) ((long) n * (n + 1) / 2 - sum);",
    "cpp": "int n = (int) nums.size();\nlong long sum = 0;\nfor (int v : nums) sum += v;\nint result = (int) ((long long) n * (n + 1) / 2 - sum);",
    "csharp": "int n = nums.Length;\nlong sum = 0;\nforeach (var v in nums) sum += v;\nint result = (int) ((long) n * (n + 1) / 2 - sum);",
    "c": "long sum = 0;\nfor (int i = 0; i < n; i++) sum += nums[i];\nint result = (int) ((long) n * (n + 1) / 2 - sum);",
    "rust": "let n = nums.len() as i64;\nlet mut sum: i64 = 0;\nfor v in nums.iter() { sum += *v as i64; }\nlet result: i32 = (n * (n + 1) / 2 - sum) as i32;",
    "swift": "let n = nums.count\nvar sum = 0\nfor v in nums { sum += v }\nlet result = n * (n + 1) / 2 - sum",
})

# ═════════════════════════════════════════════════════════════════════════
# max_subarray(nums) -> Kadane's algorithm
# ═════════════════════════════════════════════════════════════════════════
add("maximum-subarray", "arr1", "max_subarray", "int", {
    "go": "best := nums[0]\ncur := nums[0]\nfor i := 1; i < len(nums); i++ {\n\tif nums[i] > cur+nums[i] { cur = nums[i] } else { cur = cur + nums[i] }\n\tif cur > best { best = cur }\n}\nresult := int64(best)",
    "ruby": "best = nums[0]\ncur = nums[0]\n(1...nums.length).each do |i|\n  cur = [nums[i], cur + nums[i]].max\n  best = cur if cur > best\nend\nresult = best",
    "kotlin": "var best = nums[0]\nvar cur = nums[0]\nfor (i in 1 until nums.size) {\n    cur = maxOf(nums[i], cur + nums[i])\n    if (cur > best) best = cur\n}\nval result = best.toLong()",
    "php": "$best = $nums[0]; $cur = $nums[0];\nfor ($i = 1; $i < count($nums); $i++) {\n    $cur = max($nums[$i], $cur + $nums[$i]);\n    if ($cur > $best) { $best = $cur; }\n}\n$result = $best;",
    "scala": "var best = nums(0)\nvar cur = nums(0)\nfor (i <- 1 until nums.length) {\n  cur = math.max(nums(i), cur + nums(i))\n  if (cur > best) best = cur\n}\nval result: Long = best",
    "r": "best <- nums[1]\ncur <- nums[1]\nif (length(nums) > 1) { for (i in 2:length(nums)) {\n  cur <- max(nums[i], cur + nums[i])\n  if (cur > best) best <- cur\n} }\nresult <- best",
    "javascript": "let best = nums[0], cur = nums[0];\nfor (let i = 1; i < nums.length; i++) {\n    cur = Math.max(nums[i], cur + nums[i]);\n    if (cur > best) best = cur;\n}\nconst result = best;",
    "typescript": "let best = nums[0], cur = nums[0];\nfor (let i = 1; i < nums.length; i++) {\n    cur = Math.max(nums[i], cur + nums[i]);\n    if (cur > best) best = cur;\n}\nconst result = best;",
    "perl": "my $best = $nums->[0]; my $cur = $nums->[0];\nfor (my $i = 1; $i < scalar(@{$nums}); $i++) {\n    my $v = $nums->[$i];\n    $cur = ($v > $cur + $v) ? $v : $cur + $v;\n    $best = $cur if $cur > $best;\n}\nmy $result = $best;",
    "java": "int best = nums[0], cur = nums[0];\nfor (int i = 1; i < nums.length; i++) {\n    cur = Math.max(nums[i], cur + nums[i]);\n    if (cur > best) best = cur;\n}\nint result = best;",
    "cpp": "int best = nums[0], cur = nums[0];\nfor (int i = 1; i < (int) nums.size(); i++) {\n    cur = std::max(nums[i], cur + nums[i]);\n    if (cur > best) best = cur;\n}\nint result = best;",
    "csharp": "int best = nums[0], cur = nums[0];\nfor (int i = 1; i < nums.Length; i++) {\n    cur = System.Math.Max(nums[i], cur + nums[i]);\n    if (cur > best) best = cur;\n}\nint result = best;",
    "c": "int best = nums[0], cur = nums[0];\nfor (int i = 1; i < n; i++) {\n    int v = nums[i];\n    cur = (v > cur + v) ? v : cur + v;\n    if (cur > best) best = cur;\n}\nint result = best;",
    "rust": "let mut best = nums[0];\nlet mut cur = nums[0];\nfor i in 1..nums.len() {\n    cur = std::cmp::max(nums[i], cur + nums[i]);\n    if cur > best { best = cur; }\n}\nlet result: i32 = best;",
    "swift": "var best = nums[0]\nvar cur = nums[0]\nfor i in 1..<nums.count {\n    cur = max(nums[i], cur + nums[i])\n    if cur > best { best = cur }\n}\nlet result = best",
})

# ═════════════════════════════════════════════════════════════════════════
# rob(nums) -> house-robber DP
# ═════════════════════════════════════════════════════════════════════════
add("house-robber", "arr1", "rob", "int", {
    "go": "prev2, prev1 := 0, 0\nfor _, v := range nums {\n\tcur := prev1\n\tif prev2+v > cur { cur = prev2 + v }\n\tprev2 = prev1\n\tprev1 = cur\n}\nresult := int64(prev1)",
    "ruby": "prev2 = 0\nprev1 = 0\nnums.each do |v|\n  cur = [prev1, prev2 + v].max\n  prev2 = prev1\n  prev1 = cur\nend\nresult = prev1",
    "kotlin": "var prev2 = 0\nvar prev1 = 0\nfor (v in nums) {\n    val cur = maxOf(prev1, prev2 + v)\n    prev2 = prev1\n    prev1 = cur\n}\nval result = prev1.toLong()",
    "php": "$prev2 = 0; $prev1 = 0;\nforeach ($nums as $v) {\n    $cur = max($prev1, $prev2 + $v);\n    $prev2 = $prev1;\n    $prev1 = $cur;\n}\n$result = $prev1;",
    "scala": "var prev2 = 0\nvar prev1 = 0\nfor (v <- nums) {\n  val cur = math.max(prev1, prev2 + v)\n  prev2 = prev1\n  prev1 = cur\n}\nval result: Long = prev1",
    "r": "prev2 <- 0\nprev1 <- 0\nfor (v in nums) {\n  cur <- max(prev1, prev2 + v)\n  prev2 <- prev1\n  prev1 <- cur\n}\nresult <- prev1",
    "javascript": "let prev2 = 0, prev1 = 0;\nfor (const v of nums) {\n    const cur = Math.max(prev1, prev2 + v);\n    prev2 = prev1;\n    prev1 = cur;\n}\nconst result = prev1;",
    "typescript": "let prev2 = 0, prev1 = 0;\nfor (const v of nums) {\n    const cur = Math.max(prev1, prev2 + v);\n    prev2 = prev1;\n    prev1 = cur;\n}\nconst result = prev1;",
    "perl": "my $prev2 = 0; my $prev1 = 0;\nforeach my $v (@{$nums}) {\n    my $cur = $prev1 > $prev2 + $v ? $prev1 : $prev2 + $v;\n    $prev2 = $prev1;\n    $prev1 = $cur;\n}\nmy $result = $prev1;",
    "java": "int prev2 = 0, prev1 = 0;\nfor (int v : nums) {\n    int cur = Math.max(prev1, prev2 + v);\n    prev2 = prev1;\n    prev1 = cur;\n}\nint result = prev1;",
    "cpp": "int prev2 = 0, prev1 = 0;\nfor (int v : nums) {\n    int cur = std::max(prev1, prev2 + v);\n    prev2 = prev1;\n    prev1 = cur;\n}\nint result = prev1;",
    "csharp": "int prev2 = 0, prev1 = 0;\nforeach (var v in nums) {\n    int cur = System.Math.Max(prev1, prev2 + v);\n    prev2 = prev1;\n    prev1 = cur;\n}\nint result = prev1;",
    "c": "int prev2 = 0, prev1 = 0;\nfor (int i = 0; i < n; i++) {\n    int cur = prev1 > prev2 + nums[i] ? prev1 : prev2 + nums[i];\n    prev2 = prev1;\n    prev1 = cur;\n}\nint result = prev1;",
    "rust": "let mut prev2 = 0;\nlet mut prev1 = 0;\nfor v in nums.iter() {\n    let cur = std::cmp::max(prev1, prev2 + v);\n    prev2 = prev1;\n    prev1 = cur;\n}\nlet result: i32 = prev1;",
    "swift": "var prev2 = 0\nvar prev1 = 0\nfor v in nums {\n    let cur = max(prev1, prev2 + v)\n    prev2 = prev1\n    prev1 = cur\n}\nlet result = prev1",
})

# ═════════════════════════════════════════════════════════════════════════
# can_jump(nums) -> greedy reachability, bool
# ═════════════════════════════════════════════════════════════════════════
add("jump-game", "arr1", "can_jump", "bool", {
    "go": "reach := 0\nresult := true\nfor i, v := range nums {\n\tif i > reach { result = false; break }\n\tif i+v > reach { reach = i + v }\n}",
    "ruby": "reach = 0\nresult = true\nnums.each_with_index do |v, i|\n  if i > reach\n    result = false\n    break\n  end\n  reach = [reach, i + v].max\nend",
    "kotlin": "var reach = 0\nvar result = true\nfor (i in nums.indices) {\n    if (i > reach) { result = false; break }\n    if (i + nums[i] > reach) reach = i + nums[i]\n}",
    "php": "$reach = 0; $result = true;\nforeach ($nums as $i => $v) {\n    if ($i > $reach) { $result = false; break; }\n    if ($i + $v > $reach) { $reach = $i + $v; }\n}",
    "scala": "var reach = 0\nvar result = true\nvar stop = false\nfor (i <- nums.indices if !stop) {\n  if (i > reach) { result = false; stop = true }\n  else if (i + nums(i) > reach) reach = i + nums(i)\n}",
    "r": "reach <- 0\nresult <- TRUE\nif (length(nums) > 0) { for (i in 1:length(nums)) {\n  idx <- i - 1\n  if (idx > reach) { result <- FALSE; break }\n  if (idx + nums[i] > reach) reach <- idx + nums[i]\n} }",
    "javascript": "let reach = 0;\nlet result = true;\nfor (let i = 0; i < nums.length; i++) {\n    if (i > reach) { result = false; break; }\n    if (i + nums[i] > reach) reach = i + nums[i];\n}",
    "typescript": "let reach = 0;\nlet result = true;\nfor (let i = 0; i < nums.length; i++) {\n    if (i > reach) { result = false; break; }\n    if (i + nums[i] > reach) reach = i + nums[i];\n}",
    "perl": "my $reach = 0; my $result = 1;\nfor (my $i = 0; $i < scalar(@{$nums}); $i++) {\n    if ($i > $reach) { $result = 0; last; }\n    if ($i + $nums->[$i] > $reach) { $reach = $i + $nums->[$i]; }\n}",
    "java": "int reach = 0;\nboolean result = true;\nfor (int i = 0; i < nums.length; i++) {\n    if (i > reach) { result = false; break; }\n    if (i + nums[i] > reach) reach = i + nums[i];\n}",
    "cpp": "int reach = 0;\nbool result = true;\nfor (int i = 0; i < (int) nums.size(); i++) {\n    if (i > reach) { result = false; break; }\n    if (i + nums[i] > reach) reach = i + nums[i];\n}",
    "csharp": "int reach = 0;\nbool result = true;\nfor (int i = 0; i < nums.Length; i++) {\n    if (i > reach) { result = false; break; }\n    if (i + nums[i] > reach) reach = i + nums[i];\n}",
    "c": "int reach = 0;\nint result = 1;\nfor (int i = 0; i < n; i++) {\n    if (i > reach) { result = 0; break; }\n    if (i + nums[i] > reach) reach = i + nums[i];\n}",
    "rust": "let mut reach: i32 = 0;\nlet mut result = true;\nfor i in 0..nums.len() {\n    if i as i32 > reach { result = false; break; }\n    if i as i32 + nums[i] > reach { reach = i as i32 + nums[i]; }\n}",
    "swift": "var reach = 0\nvar result = true\nfor i in 0..<nums.count {\n    if i > reach { result = false; break }\n    if i + nums[i] > reach { reach = i + nums[i] }\n}",
})

# ═════════════════════════════════════════════════════════════════════════
# count_inversions(nums) -> O(n^2) pair count (n <= ~1500 in corpus)
# ═════════════════════════════════════════════════════════════════════════
add("counting-inversions", "arr1", "count_inversions", "int", {
    "go": "n := len(nums)\nresult := int64(0)\nfor i := 0; i < n; i++ {\n\tfor j := i + 1; j < n; j++ {\n\t\tif nums[i] > nums[j] { result++ }\n\t}\n}",
    "ruby": "n = nums.length\nresult = 0\n(0...n).each do |i|\n  ((i + 1)...n).each do |j|\n    result += 1 if nums[i] > nums[j]\n  end\nend",
    "kotlin": "val n = nums.size\nvar result = 0L\nfor (i in 0 until n) { for (j in i + 1 until n) { if (nums[i] > nums[j]) result++ } }",
    "php": "$n = count($nums);\n$result = 0;\nfor ($i = 0; $i < $n; $i++) { for ($j = $i + 1; $j < $n; $j++) { if ($nums[$i] > $nums[$j]) { $result++; } } }",
    "scala": "val n = nums.length\nvar result: Long = 0L\nfor (i <- 0 until n) { for (j <- i + 1 until n) { if (nums(i) > nums(j)) result += 1 } }",
    "r": "n <- length(nums)\nresult <- 0\nif (n > 1) { for (i in 1:(n - 1)) { for (j in (i + 1):n) { if (nums[i] > nums[j]) result <- result + 1 } } }",
    "javascript": "const n = nums.length;\nlet result = 0;\nfor (let i = 0; i < n; i++) { for (let j = i + 1; j < n; j++) { if (nums[i] > nums[j]) result++; } }",
    "typescript": "const n = nums.length;\nlet result = 0;\nfor (let i = 0; i < n; i++) { for (let j = i + 1; j < n; j++) { if (nums[i] > nums[j]) result++; } }",
    "perl": "my $n = scalar(@{$nums});\nmy $result = 0;\nfor (my $i = 0; $i < $n; $i++) { for (my $j = $i + 1; $j < $n; $j++) { $result++ if $nums->[$i] > $nums->[$j]; } }",
    "java": "int n = nums.length;\nint result = 0;\nfor (int i = 0; i < n; i++) { for (int j = i + 1; j < n; j++) { if (nums[i] > nums[j]) result++; } }",
    "cpp": "int n = (int) nums.size();\nint result = 0;\nfor (int i = 0; i < n; i++) { for (int j = i + 1; j < n; j++) { if (nums[i] > nums[j]) result++; } }",
    "csharp": "int n = nums.Length;\nint result = 0;\nfor (int i = 0; i < n; i++) { for (int j = i + 1; j < n; j++) { if (nums[i] > nums[j]) result++; } }",
    "c": "int result = 0;\nfor (int i = 0; i < n; i++) { for (int j = i + 1; j < n; j++) { if (nums[i] > nums[j]) result++; } }",
    "rust": "let n = nums.len();\nlet mut result: i32 = 0;\nfor i in 0..n { for j in (i + 1)..n { if nums[i] > nums[j] { result += 1; } } }",
    "swift": "let n = nums.count\nvar result = 0\nfor i in 0..<n { for j in (i + 1)..<n { if nums[i] > nums[j] { result += 1 } } }",
})

# ═════════════════════════════════════════════════════════════════════════
# longest_consecutive(nums) -> hash-set O(n) longest run
# ═════════════════════════════════════════════════════════════════════════
add("longest-consecutive-sequence", "arr1", "longest_consecutive", "int", {
    "go": "set := make(map[int]bool)\nfor _, v := range nums { set[v] = true }\nbest := 0\nfor v := range set {\n\tif !set[v-1] {\n\t\tlength := 1\n\t\tfor set[v+length] { length++ }\n\t\tif length > best { best = length }\n\t}\n}\nresult := int64(best)",
    "ruby": "set = nums.to_set\nbest = 0\nset.each do |v|\n  if !set.include?(v - 1)\n    length = 1\n    length += 1 while set.include?(v + length)\n    best = length if length > best\n  end\nend\nresult = best",
    "kotlin": "val set = nums.toHashSet()\nvar best = 0\nfor (v in set) {\n    if (!set.contains(v - 1)) {\n        var length = 1\n        while (set.contains(v + length)) length++\n        if (length > best) best = length\n    }\n}\nval result = best.toLong()",
    "php": "$set = array_flip($nums);\n$best = 0;\nforeach (array_keys($set) as $v) {\n    if (!isset($set[$v - 1])) {\n        $length = 1;\n        while (isset($set[$v + $length])) { $length++; }\n        if ($length > $best) { $best = $length; }\n    }\n}\n$result = $best;",
    "scala": "val set = nums.toSet\nvar best = 0\nfor (v <- set) {\n  if (!set.contains(v - 1)) {\n    var length = 1\n    while (set.contains(v + length)) length += 1\n    if (length > best) best = length\n  }\n}\nval result: Long = best",
    "r": "set <- unique(nums)\nsetHash <- new.env()\nfor (v in set) { assign(as.character(v), TRUE, envir = setHash) }\nhas <- function(x) exists(as.character(x), envir = setHash)\nbest <- 0\nfor (v in set) {\n  if (!has(v - 1)) {\n    length <- 1\n    while (has(v + length)) { length <- length + 1 }\n    if (length > best) best <- length\n  }\n}\nresult <- best",
    "javascript": "const set = new Set(nums);\nlet best = 0;\nfor (const v of set) {\n    if (!set.has(v - 1)) {\n        let length = 1;\n        while (set.has(v + length)) length++;\n        if (length > best) best = length;\n    }\n}\nconst result = best;",
    "typescript": "const set = new Set(nums);\nlet best = 0;\nfor (const v of set) {\n    if (!set.has(v - 1)) {\n        let length = 1;\n        while (set.has(v + length)) length++;\n        if (length > best) best = length;\n    }\n}\nconst result = best;",
    "perl": "my %set = map { $_ => 1 } @{$nums};\nmy $best = 0;\nforeach my $v (keys %set) {\n    if (!exists $set{$v - 1}) {\n        my $length = 1;\n        $length++ while exists $set{$v + $length};\n        $best = $length if $length > $best;\n    }\n}\nmy $result = $best;",
    "java": "java.util.Set<Integer> set = new java.util.HashSet<>();\nfor (int v : nums) set.add(v);\nint best = 0;\nfor (int v : set) {\n    if (!set.contains(v - 1)) {\n        int length = 1;\n        while (set.contains(v + length)) length++;\n        if (length > best) best = length;\n    }\n}\nint result = best;",
    "cpp": "std::unordered_set<int> set(nums.begin(), nums.end());\nint best = 0;\nfor (int v : set) {\n    if (!set.count(v - 1)) {\n        int length = 1;\n        while (set.count(v + length)) length++;\n        if (length > best) best = length;\n    }\n}\nint result = best;",
    "csharp": "var set = new System.Collections.Generic.HashSet<int>(nums);\nint best = 0;\nforeach (var v in set) {\n    if (!set.Contains(v - 1)) {\n        int length = 1;\n        while (set.Contains(v + length)) length++;\n        if (length > best) best = length;\n    }\n}\nint result = best;",
    "c": "int best = 0;\nfor (int i = 0; i < n; i++) {\n    int v = nums[i];\n    int hasPrev = 0;\n    for (int k = 0; k < n; k++) { if (nums[k] == v - 1) { hasPrev = 1; break; } }\n    if (!hasPrev) {\n        int length = 1;\n        int found = 1;\n        while (found) {\n            found = 0;\n            for (int k = 0; k < n; k++) { if (nums[k] == v + length) { found = 1; break; } }\n            if (found) length++;\n        }\n        if (length > best) best = length;\n    }\n}\nint result = best;",
    "rust": "let set: std::collections::HashSet<i32> = nums.iter().copied().collect();\nlet mut best = 0;\nfor &v in set.iter() {\n    if !set.contains(&(v - 1)) {\n        let mut length = 1;\n        while set.contains(&(v + length)) { length += 1; }\n        if length > best { best = length; }\n    }\n}\nlet result: i32 = best;",
    "swift": "let set = Set(nums)\nvar best = 0\nfor v in set {\n    if !set.contains(v - 1) {\n        var length = 1\n        while set.contains(v + length) { length += 1 }\n        if length > best { best = length }\n    }\n}\nlet result = best",
})

# ═════════════════════════════════════════════════════════════════════════
# find_duplicate(nums) -> Floyd's cycle detection (n+1 values in [1,n])
# ═════════════════════════════════════════════════════════════════════════
add("find-duplicate-number", "arr1", "find_duplicate", "int", {
    "go": "slow := nums[0]\nfast := nums[nums[0]]\nfor slow != fast { slow = nums[slow]; fast = nums[nums[fast]] }\nslow2 := 0\nfor slow2 != slow { slow2 = nums[slow2]; slow = nums[slow] }\nresult := int64(slow)",
    "ruby": "slow = nums[0]\nfast = nums[nums[0]]\nwhile slow != fast\n  slow = nums[slow]\n  fast = nums[nums[fast]]\nend\nslow2 = 0\nwhile slow2 != slow\n  slow2 = nums[slow2]\n  slow = nums[slow]\nend\nresult = slow",
    "kotlin": "var slow = nums[0]\nvar fast = nums[nums[0]]\nwhile (slow != fast) { slow = nums[slow]; fast = nums[nums[fast]] }\nvar slow2 = 0\nwhile (slow2 != slow) { slow2 = nums[slow2]; slow = nums[slow] }\nval result = slow.toLong()",
    "php": "$slow = $nums[0]; $fast = $nums[$nums[0]];\nwhile ($slow != $fast) { $slow = $nums[$slow]; $fast = $nums[$nums[$fast]]; }\n$slow2 = 0;\nwhile ($slow2 != $slow) { $slow2 = $nums[$slow2]; $slow = $nums[$slow]; }\n$result = $slow;",
    "scala": "var slow = nums(0)\nvar fast = nums(nums(0))\nwhile (slow != fast) { slow = nums(slow); fast = nums(nums(fast)) }\nvar slow2 = 0\nwhile (slow2 != slow) { slow2 = nums(slow2); slow = nums(slow) }\nval result: Long = slow",
    "r": "slow <- nums[nums[1] + 1]\nfast <- nums[nums[nums[1] + 1] + 1]\nwhile (slow != fast) { slow <- nums[slow + 1]; fast <- nums[nums[fast + 1] + 1] }\nslow2 <- 0\nwhile (slow2 != slow) { slow2 <- nums[slow2 + 1]; slow <- nums[slow + 1] }\nresult <- slow",
    "javascript": "let slow = nums[nums[0]], fast = nums[nums[nums[0]]];\nwhile (slow !== fast) { slow = nums[slow]; fast = nums[nums[fast]]; }\nlet slow2 = 0;\nwhile (slow2 !== slow) { slow2 = nums[slow2]; slow = nums[slow]; }\nconst result = slow;",
    "typescript": "let slow = nums[nums[0]], fast = nums[nums[nums[0]]];\nwhile (slow !== fast) { slow = nums[slow]; fast = nums[nums[fast]]; }\nlet slow2 = 0;\nwhile (slow2 !== slow) { slow2 = nums[slow2]; slow = nums[slow]; }\nconst result = slow;",
    "perl": "my $slow = $nums->[0]; my $fast = $nums->[$nums->[0]];\nwhile ($slow != $fast) { $slow = $nums->[$slow]; $fast = $nums->[$nums->[$fast]]; }\nmy $slow2 = 0;\nwhile ($slow2 != $slow) { $slow2 = $nums->[$slow2]; $slow = $nums->[$slow]; }\nmy $result = $slow;",
    "java": "int slow = nums[0], fast = nums[nums[0]];\nwhile (slow != fast) { slow = nums[slow]; fast = nums[nums[fast]]; }\nint slow2 = 0;\nwhile (slow2 != slow) { slow2 = nums[slow2]; slow = nums[slow]; }\nint result = slow;",
    "cpp": "int slow = nums[0], fast = nums[nums[0]];\nwhile (slow != fast) { slow = nums[slow]; fast = nums[nums[fast]]; }\nint slow2 = 0;\nwhile (slow2 != slow) { slow2 = nums[slow2]; slow = nums[slow]; }\nint result = slow;",
    "csharp": "int slow = nums[0], fast = nums[nums[0]];\nwhile (slow != fast) { slow = nums[slow]; fast = nums[nums[fast]]; }\nint slow2 = 0;\nwhile (slow2 != slow) { slow2 = nums[slow2]; slow = nums[slow]; }\nint result = slow;",
    "c": "int slow = nums[0], fast = nums[nums[0]];\nwhile (slow != fast) { slow = nums[slow]; fast = nums[nums[fast]]; }\nint slow2 = 0;\nwhile (slow2 != slow) { slow2 = nums[slow2]; slow = nums[slow]; }\nint result = slow;",
    "rust": "let mut slow = nums[0] as usize;\nlet mut fast = nums[nums[0] as usize] as usize;\nwhile slow != fast { slow = nums[slow] as usize; fast = nums[nums[fast] as usize] as usize; }\nlet mut slow2 = 0usize;\nwhile slow2 != slow { slow2 = nums[slow2] as usize; slow = nums[slow] as usize; }\nlet result: i32 = slow as i32;",
    "swift": "var slow = nums[nums[0]]\nvar fast = nums[nums[nums[0]]]\nwhile slow != fast { slow = nums[slow]; fast = nums[nums[fast]] }\nvar slow2 = 0\nwhile slow2 != slow { slow2 = nums[slow2]; slow = nums[slow] }\nlet result = slow",
})

# ═════════════════════════════════════════════════════════════════════════
# trap(heights) -> two-pointer O(n) trapping rain water
# ═════════════════════════════════════════════════════════════════════════
add("trapping-rain-water", "arr1", "trap", "int", {
    "go": "l, r := 0, len(nums)-1\nleftMax, rightMax := 0, 0\nresult := int64(0)\nfor l < r {\n\tif nums[l] < nums[r] {\n\t\tif nums[l] >= leftMax { leftMax = nums[l] } else { result += int64(leftMax - nums[l]) }\n\t\tl++\n\t} else {\n\t\tif nums[r] >= rightMax { rightMax = nums[r] } else { result += int64(rightMax - nums[r]) }\n\t\tr--\n\t}\n}",
    "ruby": "l = 0\nr = nums.length - 1\nleft_max = 0\nright_max = 0\nresult = 0\nwhile l < r\n  if nums[l] < nums[r]\n    if nums[l] >= left_max\n      left_max = nums[l]\n    else\n      result += left_max - nums[l]\n    end\n    l += 1\n  else\n    if nums[r] >= right_max\n      right_max = nums[r]\n    else\n      result += right_max - nums[r]\n    end\n    r -= 1\n  end\nend",
    "kotlin": "var l = 0\nvar r = nums.size - 1\nvar leftMax = 0\nvar rightMax = 0\nvar result = 0L\nwhile (l < r) {\n    if (nums[l] < nums[r]) {\n        if (nums[l] >= leftMax) leftMax = nums[l] else result += (leftMax - nums[l]).toLong()\n        l++\n    } else {\n        if (nums[r] >= rightMax) rightMax = nums[r] else result += (rightMax - nums[r]).toLong()\n        r--\n    }\n}",
    "php": "$l = 0; $r = count($nums) - 1; $leftMax = 0; $rightMax = 0; $result = 0;\nwhile ($l < $r) {\n    if ($nums[$l] < $nums[$r]) {\n        if ($nums[$l] >= $leftMax) { $leftMax = $nums[$l]; } else { $result += $leftMax - $nums[$l]; }\n        $l++;\n    } else {\n        if ($nums[$r] >= $rightMax) { $rightMax = $nums[$r]; } else { $result += $rightMax - $nums[$r]; }\n        $r--;\n    }\n}",
    "scala": "var l = 0\nvar r = nums.length - 1\nvar leftMax = 0\nvar rightMax = 0\nvar result: Long = 0L\nwhile (l < r) {\n  if (nums(l) < nums(r)) {\n    if (nums(l) >= leftMax) leftMax = nums(l) else result += (leftMax - nums(l)).toLong\n    l += 1\n  } else {\n    if (nums(r) >= rightMax) rightMax = nums(r) else result += (rightMax - nums(r)).toLong\n    r -= 1\n  }\n}",
    "r": "l <- 1; r <- length(nums); leftMax <- 0; rightMax <- 0; result <- 0\nwhile (l < r) {\n  if (nums[l] < nums[r]) {\n    if (nums[l] >= leftMax) { leftMax <- nums[l] } else { result <- result + (leftMax - nums[l]) }\n    l <- l + 1\n  } else {\n    if (nums[r] >= rightMax) { rightMax <- nums[r] } else { result <- result + (rightMax - nums[r]) }\n    r <- r - 1\n  }\n}",
    "javascript": "let l = 0, r = nums.length - 1, leftMax = 0, rightMax = 0, result = 0;\nwhile (l < r) {\n    if (nums[l] < nums[r]) {\n        if (nums[l] >= leftMax) leftMax = nums[l]; else result += leftMax - nums[l];\n        l++;\n    } else {\n        if (nums[r] >= rightMax) rightMax = nums[r]; else result += rightMax - nums[r];\n        r--;\n    }\n}",
    "typescript": "let l = 0, r = nums.length - 1, leftMax = 0, rightMax = 0, result = 0;\nwhile (l < r) {\n    if (nums[l] < nums[r]) {\n        if (nums[l] >= leftMax) leftMax = nums[l]; else result += leftMax - nums[l];\n        l++;\n    } else {\n        if (nums[r] >= rightMax) rightMax = nums[r]; else result += rightMax - nums[r];\n        r--;\n    }\n}",
    "perl": "my $l = 0; my $r = scalar(@{$nums}) - 1; my $leftMax = 0; my $rightMax = 0; my $result = 0;\nwhile ($l < $r) {\n    if ($nums->[$l] < $nums->[$r]) {\n        if ($nums->[$l] >= $leftMax) { $leftMax = $nums->[$l]; } else { $result += $leftMax - $nums->[$l]; }\n        $l++;\n    } else {\n        if ($nums->[$r] >= $rightMax) { $rightMax = $nums->[$r]; } else { $result += $rightMax - $nums->[$r]; }\n        $r--;\n    }\n}",
    "java": "int l = 0, r = nums.length - 1, leftMax = 0, rightMax = 0;\nlong result = 0;\nwhile (l < r) {\n    if (nums[l] < nums[r]) {\n        if (nums[l] >= leftMax) leftMax = nums[l]; else result += leftMax - nums[l];\n        l++;\n    } else {\n        if (nums[r] >= rightMax) rightMax = nums[r]; else result += rightMax - nums[r];\n        r--;\n    }\n}",
    "cpp": "int l = 0, r = (int) nums.size() - 1, leftMax = 0, rightMax = 0;\nlong long result = 0;\nwhile (l < r) {\n    if (nums[l] < nums[r]) {\n        if (nums[l] >= leftMax) leftMax = nums[l]; else result += leftMax - nums[l];\n        l++;\n    } else {\n        if (nums[r] >= rightMax) rightMax = nums[r]; else result += rightMax - nums[r];\n        r--;\n    }\n}",
    "csharp": "int l = 0, r = nums.Length - 1, leftMax = 0, rightMax = 0;\nlong result = 0;\nwhile (l < r) {\n    if (nums[l] < nums[r]) {\n        if (nums[l] >= leftMax) leftMax = nums[l]; else result += leftMax - nums[l];\n        l++;\n    } else {\n        if (nums[r] >= rightMax) rightMax = nums[r]; else result += rightMax - nums[r];\n        r--;\n    }\n}",
    "c": "int l = 0, r = n - 1, leftMax = 0, rightMax = 0;\nlong result = 0;\nwhile (l < r) {\n    if (nums[l] < nums[r]) {\n        if (nums[l] >= leftMax) leftMax = nums[l]; else result += leftMax - nums[l];\n        l++;\n    } else {\n        if (nums[r] >= rightMax) rightMax = nums[r]; else result += rightMax - nums[r];\n        r--;\n    }\n}",
    "rust": "let mut l: i32 = 0;\nlet mut r: i32 = nums.len() as i32 - 1;\nlet mut left_max = 0;\nlet mut right_max = 0;\nlet mut result: i32 = 0;\nwhile l < r {\n    if nums[l as usize] < nums[r as usize] {\n        if nums[l as usize] >= left_max { left_max = nums[l as usize]; } else { result += left_max - nums[l as usize]; }\n        l += 1;\n    } else {\n        if nums[r as usize] >= right_max { right_max = nums[r as usize]; } else { result += right_max - nums[r as usize]; }\n        r -= 1;\n    }\n}",
    "swift": "var l = 0\nvar r = nums.count - 1\nvar leftMax = 0\nvar rightMax = 0\nvar result = 0\nwhile l < r {\n    if nums[l] < nums[r] {\n        if nums[l] >= leftMax { leftMax = nums[l] } else { result += leftMax - nums[l] }\n        l += 1\n    } else {\n        if nums[r] >= rightMax { rightMax = nums[r] } else { result += rightMax - nums[r] }\n        r -= 1\n    }\n}",
})

# ═════════════════════════════════════════════════════════════════════════
# contains_nearby_duplicate(nums, extra=k) -> sliding window last-seen map
# ═════════════════════════════════════════════════════════════════════════
add("contains-duplicate-within-k", "arr1_int", "contains_nearby_duplicate", "bool", {
    "go": "last := make(map[int]int)\nresult := false\nfor i, v := range nums {\n\tif p, ok := last[v]; ok && i-p <= extra { result = true; break }\n\tlast[v] = i\n}",
    "ruby": "last = {}\nresult = false\nnums.each_with_index do |v, i|\n  if last.key?(v) && i - last[v] <= extra\n    result = true\n    break\n  end\n  last[v] = i\nend",
    "kotlin": "val last = HashMap<Int, Int>()\nvar result = false\nfor (i in nums.indices) {\n    val v = nums[i]\n    if (last.containsKey(v) && i - last[v]!! <= extra) { result = true; break }\n    last[v] = i\n}",
    "php": "$last = []; $result = false;\nforeach ($nums as $i => $v) {\n    if (isset($last[$v]) && $i - $last[$v] <= $extra) { $result = true; break; }\n    $last[$v] = $i;\n}",
    "scala": "val last = scala.collection.mutable.HashMap[Int, Int]()\nvar result = false\nvar stop = false\nfor (i <- nums.indices if !stop) {\n  val v = nums(i)\n  if (last.contains(v) && i - last(v) <= extra) { result = true; stop = true }\n  else last(v) = i\n}",
    "r": "last <- new.env()\nresult <- FALSE\nif (length(nums) > 0) { for (i in 1:length(nums)) {\n  v <- as.character(nums[i])\n  if (exists(v, envir = last)) {\n    if ((i - 1) - get(v, envir = last) <= extra) { result <- TRUE; break }\n  }\n  assign(v, i - 1, envir = last)\n} }",
    "javascript": "const last = new Map();\nlet result = false;\nfor (let i = 0; i < nums.length; i++) {\n    const v = nums[i];\n    if (last.has(v) && i - last.get(v) <= extra) { result = true; break; }\n    last.set(v, i);\n}",
    "typescript": "const last = new Map<number, number>();\nlet result = false;\nfor (let i = 0; i < nums.length; i++) {\n    const v = nums[i];\n    if (last.has(v) && i - last.get(v)! <= extra) { result = true; break; }\n    last.set(v, i);\n}",
    "perl": "my %last; my $result = 0;\nfor (my $i = 0; $i < scalar(@{$nums}); $i++) {\n    my $v = $nums->[$i];\n    if (exists $last{$v} && $i - $last{$v} <= $extra) { $result = 1; last; }\n    $last{$v} = $i;\n}",
    "java": "java.util.Map<Integer, Integer> last = new java.util.HashMap<>();\nboolean result = false;\nfor (int i = 0; i < nums.length; i++) {\n    int v = nums[i];\n    if (last.containsKey(v) && i - last.get(v) <= extra) { result = true; break; }\n    last.put(v, i);\n}",
    "cpp": "std::unordered_map<int, int> last;\nbool result = false;\nfor (int i = 0; i < (int) nums.size(); i++) {\n    int v = nums[i];\n    auto it = last.find(v);\n    if (it != last.end() && i - it->second <= extra) { result = true; break; }\n    last[v] = i;\n}",
    "csharp": "var last = new System.Collections.Generic.Dictionary<int, int>();\nbool result = false;\nfor (int i = 0; i < nums.Length; i++) {\n    int v = nums[i];\n    if (last.ContainsKey(v) && i - last[v] <= extra) { result = true; break; }\n    last[v] = i;\n}",
    "c": "int result = 0;\nfor (int i = 0; i < n && !result; i++) {\n    for (int j = i + 1; j < n && j - i <= extra; j++) {\n        if (nums[i] == nums[j]) { result = 1; break; }\n    }\n}",
    "rust": "let mut last = std::collections::HashMap::new();\nlet mut result = false;\nfor i in 0..nums.len() {\n    let v = nums[i];\n    if let Some(&p) = last.get(&v) {\n        if (i as i32) - p <= extra { result = true; break; }\n    }\n    last.insert(v, i as i32);\n}",
    "swift": "var last: [Int: Int] = [:]\nvar result = false\nfor i in 0..<nums.count {\n    let v = nums[i]\n    if let p = last[v], i - p <= extra { result = true; break }\n    last[v] = i\n}",
})

# ═════════════════════════════════════════════════════════════════════════
# lis(nums) -> longest strictly-increasing subsequence, O(n log n)
# patience-sorting (tails array + binary search)
# ═════════════════════════════════════════════════════════════════════════
add("longest-increasing-subsequence", "arr1", "lis", "int", {
    "go": ("tails := []int{}\nfor _, x := range nums {\n\tlo, hi := 0, len(tails)\n\tfor lo < hi {\n\t\tmid := (lo + hi) / 2\n\t\tif tails[mid] < x { lo = mid + 1 } else { hi = mid }\n\t}\n\tif lo == len(tails) { tails = append(tails, x) } else { tails[lo] = x }\n}\nresult := int64(len(tails))"),
    "ruby": ("tails = []\nnums.each do |x|\n  lo = 0\n  hi = tails.length\n  while lo < hi\n    mid = (lo + hi) / 2\n    if tails[mid] < x\n      lo = mid + 1\n    else\n      hi = mid\n    end\n  end\n  if lo == tails.length\n    tails.push(x)\n  else\n    tails[lo] = x\n  end\nend\nresult = tails.length"),
    "kotlin": ("val tails = mutableListOf<Int>()\nfor (x in nums) {\n    var lo = 0\n    var hi = tails.size\n    while (lo < hi) {\n        val mid = (lo + hi) / 2\n        if (tails[mid] < x) lo = mid + 1 else hi = mid\n    }\n    if (lo == tails.size) tails.add(x) else tails[lo] = x\n}\nval result = tails.size.toLong()"),
    "php": ("$tails = [];\nforeach ($nums as $x) {\n    $lo = 0; $hi = count($tails);\n    while ($lo < $hi) {\n        $mid = intdiv($lo + $hi, 2);\n        if ($tails[$mid] < $x) { $lo = $mid + 1; } else { $hi = $mid; }\n    }\n    if ($lo == count($tails)) { $tails[] = $x; } else { $tails[$lo] = $x; }\n}\n$result = count($tails);"),
    "scala": ("val tails = scala.collection.mutable.ArrayBuffer[Int]()\nfor (x <- nums) {\n  var lo = 0\n  var hi = tails.length\n  while (lo < hi) {\n    val mid = (lo + hi) / 2\n    if (tails(mid) < x) lo = mid + 1 else hi = mid\n  }\n  if (lo == tails.length) tails += x else tails(lo) = x\n}\nval result: Long = tails.length"),
    "r": ("tails <- integer(0)\nfor (x in nums) {\n  lo <- 1; hi <- length(tails) + 1\n  while (lo < hi) {\n    mid <- (lo + hi) %/% 2\n    if (tails[mid] < x) { lo <- mid + 1 } else { hi <- mid }\n  }\n  if (lo > length(tails)) { tails <- c(tails, x) } else { tails[lo] <- x }\n}\nresult <- length(tails)"),
    "javascript": ("const tails = [];\nfor (const x of nums) {\n    let lo = 0, hi = tails.length;\n    while (lo < hi) {\n        const mid = (lo + hi) >> 1;\n        if (tails[mid] < x) lo = mid + 1; else hi = mid;\n    }\n    if (lo === tails.length) tails.push(x); else tails[lo] = x;\n}\nconst result = tails.length;"),
    "typescript": ("const tails: number[] = [];\nfor (const x of nums) {\n    let lo = 0, hi = tails.length;\n    while (lo < hi) {\n        const mid = (lo + hi) >> 1;\n        if (tails[mid] < x) lo = mid + 1; else hi = mid;\n    }\n    if (lo === tails.length) tails.push(x); else tails[lo] = x;\n}\nconst result = tails.length;"),
    "perl": ("my @tails;\nforeach my $x (@{$nums}) {\n    my $lo = 0; my $hi = scalar(@tails);\n    while ($lo < $hi) {\n        my $mid = int(($lo + $hi) / 2);\n        if ($tails[$mid] < $x) { $lo = $mid + 1; } else { $hi = $mid; }\n    }\n    if ($lo == scalar(@tails)) { push @tails, $x; } else { $tails[$lo] = $x; }\n}\nmy $result = scalar(@tails);"),
    "java": ("java.util.List<Integer> tails = new java.util.ArrayList<>();\nfor (int x : nums) {\n    int lo = 0, hi = tails.size();\n    while (lo < hi) {\n        int mid = (lo + hi) / 2;\n        if (tails.get(mid) < x) lo = mid + 1; else hi = mid;\n    }\n    if (lo == tails.size()) tails.add(x); else tails.set(lo, x);\n}\nint result = tails.size();"),
    "cpp": ("std::vector<int> tails;\nfor (int x : nums) {\n    int lo = 0, hi = (int) tails.size();\n    while (lo < hi) {\n        int mid = (lo + hi) / 2;\n        if (tails[mid] < x) lo = mid + 1; else hi = mid;\n    }\n    if (lo == (int) tails.size()) tails.push_back(x); else tails[lo] = x;\n}\nint result = (int) tails.size();"),
    "csharp": ("var tails = new System.Collections.Generic.List<int>();\nforeach (var x in nums) {\n    int lo = 0, hi = tails.Count;\n    while (lo < hi) {\n        int mid = (lo + hi) / 2;\n        if (tails[mid] < x) lo = mid + 1; else hi = mid;\n    }\n    if (lo == tails.Count) tails.Add(x); else tails[lo] = x;\n}\nint result = tails.Count;"),
    "c": ("int *tails = (int *)malloc(sizeof(int) * (size_t)(n > 0 ? n : 1));\nint tlen = 0;\nfor (int i = 0; i < n; i++) {\n    int x = nums[i];\n    int lo = 0, hi = tlen;\n    while (lo < hi) {\n        int mid = (lo + hi) / 2;\n        if (tails[mid] < x) lo = mid + 1; else hi = mid;\n    }\n    if (lo == tlen) { tails[tlen++] = x; } else { tails[lo] = x; }\n}\nint result = tlen;\nfree(tails);"),
    "rust": ("let mut tails: Vec<i32> = Vec::new();\nfor &x in nums.iter() {\n    let mut lo = 0usize;\n    let mut hi = tails.len();\n    while lo < hi {\n        let mid = (lo + hi) / 2;\n        if tails[mid] < x { lo = mid + 1; } else { hi = mid; }\n    }\n    if lo == tails.len() { tails.push(x); } else { tails[lo] = x; }\n}\nlet result: i32 = tails.len() as i32;"),
    "swift": ("var tails: [Int] = []\nfor x in nums {\n    var lo = 0\n    var hi = tails.count\n    while lo < hi {\n        let mid = (lo + hi) / 2\n        if tails[mid] < x { lo = mid + 1 } else { hi = mid }\n    }\n    if lo == tails.count { tails.append(x) } else { tails[lo] = x }\n}\nlet result = tails.count"),
})

# ═════════════════════════════════════════════════════════════════════════
# three_sum_count(nums) -> distinct value-triplets summing to 0
# (sort + two-pointer with duplicate skipping)
# ═════════════════════════════════════════════════════════════════════════
add("three-sum-count-triplets", "arr1", "three_sum_count", "int", {
    "go": ("s := append([]int{}, nums...)\nsort.Ints(s)\nn := len(s)\nresult := int64(0)\nfor i := 0; i < n-2; i++ {\n\tif i > 0 && s[i] == s[i-1] { continue }\n\tl, r := i+1, n-1\n\tfor l < r {\n\t\tsum := s[i] + s[l] + s[r]\n\t\tif sum < 0 { l++ } else if sum > 0 { r-- } else {\n\t\t\tresult++\n\t\t\tl++; r--\n\t\t\tfor l < r && s[l] == s[l-1] { l++ }\n\t\t\tfor l < r && s[r] == s[r+1] { r-- }\n\t\t}\n\t}\n}"),
    "ruby": ("s = nums.sort\nn = s.length\nresult = 0\n(0...(n - 2)).each do |i|\n  next if i > 0 && s[i] == s[i - 1]\n  l = i + 1\n  r = n - 1\n  while l < r\n    sum = s[i] + s[l] + s[r]\n    if sum < 0\n      l += 1\n    elsif sum > 0\n      r -= 1\n    else\n      result += 1\n      l += 1\n      r -= 1\n      l += 1 while l < r && s[l] == s[l - 1]\n      r -= 1 while l < r && s[r] == s[r + 1]\n    end\n  end\nend"),
    "kotlin": ("val s = nums.sortedArray()\nval n = s.size\nvar result = 0L\nfor (i in 0 until n - 2) {\n    if (i > 0 && s[i] == s[i - 1]) continue\n    var l = i + 1\n    var r = n - 1\n    while (l < r) {\n        val sum = s[i] + s[l] + s[r]\n        if (sum < 0) l++\n        else if (sum > 0) r--\n        else {\n            result++\n            l++; r--\n            while (l < r && s[l] == s[l - 1]) l++\n            while (l < r && s[r] == s[r + 1]) r--\n        }\n    }\n}"),
    "php": ("$s = $nums; sort($s);\n$n = count($s);\n$result = 0;\nfor ($i = 0; $i < $n - 2; $i++) {\n    if ($i > 0 && $s[$i] == $s[$i - 1]) { continue; }\n    $l = $i + 1; $r = $n - 1;\n    while ($l < $r) {\n        $sum = $s[$i] + $s[$l] + $s[$r];\n        if ($sum < 0) { $l++; }\n        elseif ($sum > 0) { $r--; }\n        else {\n            $result++;\n            $l++; $r--;\n            while ($l < $r && $s[$l] == $s[$l - 1]) { $l++; }\n            while ($l < $r && $s[$r] == $s[$r + 1]) { $r--; }\n        }\n    }\n}"),
    "scala": ("val s = nums.sorted\nval n = s.length\nvar result: Long = 0L\nfor (i <- 0 until n - 2) {\n  if (!(i > 0 && s(i) == s(i - 1))) {\n    var l = i + 1\n    var r = n - 1\n    while (l < r) {\n      val sum = s(i) + s(l) + s(r)\n      if (sum < 0) l += 1\n      else if (sum > 0) r -= 1\n      else {\n        result += 1\n        l += 1; r -= 1\n        while (l < r && s(l) == s(l - 1)) l += 1\n        while (l < r && s(r) == s(r + 1)) r -= 1\n      }\n    }\n  }\n}"),
    "r": ("s <- sort(nums)\nn <- length(s)\nresult <- 0\nif (n >= 3) { for (i in 1:(n - 2)) {\n  if (!(i > 1 && s[i] == s[i - 1])) {\n    l <- i + 1; r <- n\n    while (l < r) {\n      sum <- s[i] + s[l] + s[r]\n      if (sum < 0) { l <- l + 1 }\n      else if (sum > 0) { r <- r - 1 }\n      else {\n        result <- result + 1\n        l <- l + 1; r <- r - 1\n        while (l < r && s[l] == s[l - 1]) { l <- l + 1 }\n        while (l < r && s[r] == s[r + 1]) { r <- r - 1 }\n      }\n    }\n  }\n} }"),
    "javascript": ("const s = nums.slice().sort((a, b) => a - b);\nconst n = s.length;\nlet result = 0;\nfor (let i = 0; i < n - 2; i++) {\n    if (i > 0 && s[i] === s[i - 1]) continue;\n    let l = i + 1, r = n - 1;\n    while (l < r) {\n        const sum = s[i] + s[l] + s[r];\n        if (sum < 0) l++;\n        else if (sum > 0) r--;\n        else {\n            result++;\n            l++; r--;\n            while (l < r && s[l] === s[l - 1]) l++;\n            while (l < r && s[r] === s[r + 1]) r--;\n        }\n    }\n}"),
    "typescript": ("const s = nums.slice().sort((a, b) => a - b);\nconst n = s.length;\nlet result = 0;\nfor (let i = 0; i < n - 2; i++) {\n    if (i > 0 && s[i] === s[i - 1]) continue;\n    let l = i + 1, r = n - 1;\n    while (l < r) {\n        const sum = s[i] + s[l] + s[r];\n        if (sum < 0) l++;\n        else if (sum > 0) r--;\n        else {\n            result++;\n            l++; r--;\n            while (l < r && s[l] === s[l - 1]) l++;\n            while (l < r && s[r] === s[r + 1]) r--;\n        }\n    }\n}"),
    "perl": ("my @s = sort { $a <=> $b } @{$nums};\nmy $n = scalar(@s);\nmy $result = 0;\nfor (my $i = 0; $i < $n - 2; $i++) {\n    next if $i > 0 && $s[$i] == $s[$i - 1];\n    my $l = $i + 1; my $r = $n - 1;\n    while ($l < $r) {\n        my $sum = $s[$i] + $s[$l] + $s[$r];\n        if ($sum < 0) { $l++; }\n        elsif ($sum > 0) { $r--; }\n        else {\n            $result++;\n            $l++; $r--;\n            while ($l < $r && $s[$l] == $s[$l - 1]) { $l++; }\n            while ($l < $r && $s[$r] == $s[$r + 1]) { $r--; }\n        }\n    }\n}"),
    "java": ("int[] s = nums.clone();\njava.util.Arrays.sort(s);\nint n = s.length;\nint result = 0;\nfor (int i = 0; i < n - 2; i++) {\n    if (i > 0 && s[i] == s[i - 1]) continue;\n    int l = i + 1, r = n - 1;\n    while (l < r) {\n        int sum = s[i] + s[l] + s[r];\n        if (sum < 0) l++;\n        else if (sum > 0) r--;\n        else {\n            result++;\n            l++; r--;\n            while (l < r && s[l] == s[l - 1]) l++;\n            while (l < r && s[r] == s[r + 1]) r--;\n        }\n    }\n}"),
    "cpp": ("std::vector<int> s = nums;\nstd::sort(s.begin(), s.end());\nint n = (int) s.size();\nint result = 0;\nfor (int i = 0; i < n - 2; i++) {\n    if (i > 0 && s[i] == s[i - 1]) continue;\n    int l = i + 1, r = n - 1;\n    while (l < r) {\n        int sum = s[i] + s[l] + s[r];\n        if (sum < 0) l++;\n        else if (sum > 0) r--;\n        else {\n            result++;\n            l++; r--;\n            while (l < r && s[l] == s[l - 1]) l++;\n            while (l < r && s[r] == s[r + 1]) r--;\n        }\n    }\n}"),
    "csharp": ("int[] s = (int[]) nums.Clone();\nSystem.Array.Sort(s);\nint n = s.Length;\nint result = 0;\nfor (int i = 0; i < n - 2; i++) {\n    if (i > 0 && s[i] == s[i - 1]) continue;\n    int l = i + 1, r = n - 1;\n    while (l < r) {\n        int sum = s[i] + s[l] + s[r];\n        if (sum < 0) l++;\n        else if (sum > 0) r--;\n        else {\n            result++;\n            l++; r--;\n            while (l < r && s[l] == s[l - 1]) l++;\n            while (l < r && s[r] == s[r + 1]) r--;\n        }\n    }\n}"),
    "c": ("int *s = (int *)malloc(sizeof(int) * (size_t)(n > 0 ? n : 1));\nmemcpy(s, nums, sizeof(int) * (size_t) n);\nfor (int a = 0; a < n; a++) { for (int b = a + 1; b < n; b++) { if (s[b] < s[a]) { int t = s[a]; s[a] = s[b]; s[b] = t; } } }\nint result = 0;\nfor (int i = 0; i < n - 2; i++) {\n    if (i > 0 && s[i] == s[i - 1]) continue;\n    int l = i + 1, r = n - 1;\n    while (l < r) {\n        int sum = s[i] + s[l] + s[r];\n        if (sum < 0) l++;\n        else if (sum > 0) r--;\n        else {\n            result++;\n            l++; r--;\n            while (l < r && s[l] == s[l - 1]) l++;\n            while (l < r && s[r] == s[r + 1]) r--;\n        }\n    }\n}\nfree(s);"),
    "rust": ("let mut s = nums.clone();\ns.sort();\nlet n = s.len() as i32;\nlet mut result: i32 = 0;\nlet mut i = 0;\nwhile i < n - 2 {\n    if !(i > 0 && s[i as usize] == s[(i - 1) as usize]) {\n        let mut l = i + 1;\n        let mut r = n - 1;\n        while l < r {\n            let sum = s[i as usize] + s[l as usize] + s[r as usize];\n            if sum < 0 { l += 1; }\n            else if sum > 0 { r -= 1; }\n            else {\n                result += 1;\n                l += 1; r -= 1;\n                while l < r && s[l as usize] == s[(l - 1) as usize] { l += 1; }\n                while l < r && s[r as usize] == s[(r + 1) as usize] { r -= 1; }\n            }\n        }\n    }\n    i += 1;\n}"),
    "swift": ("let s = nums.sorted()\nlet n = s.count\nvar result = 0\nvar i = 0\nwhile i < n - 2 {\n    if !(i > 0 && s[i] == s[i - 1]) {\n        var l = i + 1\n        var r = n - 1\n        while l < r {\n            let sum = s[i] + s[l] + s[r]\n            if sum < 0 { l += 1 }\n            else if sum > 0 { r -= 1 }\n            else {\n                result += 1\n                l += 1; r -= 1\n                while l < r && s[l] == s[l - 1] { l += 1 }\n                while l < r && s[r] == s[r + 1] { r -= 1 }\n            }\n        }\n    }\n    i += 1\n}"),
})


if __name__ == "__main__":
    sys.exit(asyncio.run(sh.main()))
