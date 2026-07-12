"""Program Mode expansion, batch 11: pure-numeric problems (gcd-euclidean,
hamming-distance, power-of-two, number-of-1-bits, euler-totient, collatz,
staircase, egg-drop) using the NEW int1/int2/int3 shapes just added to
atlascode_shapes_all15.py (architectural extension: these shapes didn't
exist before this batch -- adding them once unblocks every future
pure-numeric-input problem, not just these 8), plus 5 more problems on
already-existing shapes (triangle-minimum-path-sum, coin-change,
coin-change-ways, activity-selection, gas-station, meeting-rooms).

prime-factorization and insert-interval were excluded: prime-factorization
returns a space-separated factor list (string output, not int/bool);
insert-interval returns multiple (s, e) lines (structured output). Neither
fits the harness's int/bool-kind shapes.
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
# gcd(a, b) -> int, Euclidean algorithm
# ═════════════════════════════════════════════════════════════════════════
add("gcd-euclidean", "int2", "gcd", "int", {
    "go": "for b != 0 { a, b = b, a%b }\nresult := int64(a)\nif result < 0 { result = -result }",
    "ruby": "while b != 0\n  a, b = b, a % b\nend\nresult = a.abs",
    "kotlin": "var x = a\nvar y = b\nwhile (y != 0) { val t = y; y = x % y; x = t }\nval result = kotlin.math.abs(x).toLong()",
    "php": "while ($b != 0) { $t = $b; $b = $a % $b; $a = $t; }\n$result = abs($a);",
    "scala": "var x = a\nvar y = b\nwhile (y != 0) { val t = y; y = x % y; x = t }\nval result: Long = math.abs(x)",
    "r": "x <- a; y <- b\nwhile (y != 0) { t <- y; y <- x %% y; x <- t }\nresult <- abs(x)",
    "javascript": "let x = a, y = b;\nwhile (y !== 0) { const t = y; y = x % y; x = t; }\nconst result = Math.abs(x);",
    "typescript": "let x = a, y = b;\nwhile (y !== 0) { const t = y; y = x % y; x = t; }\nconst result = Math.abs(x);",
    "perl": "my $x = $a; my $y = $b;\nwhile ($y != 0) { my $t = $y; $y = $x % $y; $x = $t; }\nmy $result = abs($x);",
    "java": "int x = a, y = b;\nwhile (y != 0) { int t = y; y = x % y; x = t; }\nint result = Math.abs(x);",
    "cpp": "int x = a, y = b;\nwhile (y != 0) { int t = y; y = x % y; x = t; }\nint result = std::abs(x);",
    "csharp": "int x = a, y = b;\nwhile (y != 0) { int t = y; y = x % y; x = t; }\nint result = System.Math.Abs(x);",
    "c": "int x = a, y = b;\nwhile (y != 0) { int t = y; y = x % y; x = t; }\nint result = x < 0 ? -x : x;",
    "rust": "let mut x = a;\nlet mut y = b;\nwhile y != 0 { let t = y; y = x % y; x = t; }\nlet result: i32 = x.abs();",
    "swift": "var x = a\nvar y = b\nwhile y != 0 { let t = y; y = x % y; x = t }\nlet result = abs(x)",
})

# ═════════════════════════════════════════════════════════════════════════
# hamming_distance(x, y) -> int, popcount(x xor y)
# ═════════════════════════════════════════════════════════════════════════
add("hamming-distance", "int2", "hamming_distance", "int", {
    "go": "v := a ^ b\ncount := 0\nfor v != 0 { count += v & 1; v >>= 1 }\nresult := int64(count)",
    "ruby": "v = a ^ b\ncount = 0\nwhile v != 0\n  count += v & 1\n  v >>= 1\nend\nresult = count",
    "kotlin": "var v = a xor b\nvar count = 0\nwhile (v != 0) { count += v and 1; v = v ushr 1 }\nval result = count.toLong()",
    "php": "$v = $a ^ $b;\n$count = 0;\nwhile ($v != 0) { $count += $v & 1; $v >>= 1; }\n$result = $count;",
    "scala": "var v = a ^ b\nvar count = 0\nwhile (v != 0) { count += v & 1; v = v >>> 1 }\nval result: Long = count",
    "r": "v <- bitwXor(a, b)\ncount <- 0\nwhile (v != 0) { count <- count + bitwAnd(v, 1); v <- bitwShiftR(v, 1) }\nresult <- count",
    "javascript": "let v = a ^ b;\nlet count = 0;\nwhile (v !== 0) { count += v & 1; v >>>= 1; }\nconst result = count;",
    "typescript": "let v = a ^ b;\nlet count = 0;\nwhile (v !== 0) { count += v & 1; v >>>= 1; }\nconst result = count;",
    "perl": "my $v = $a ^ $b;\nmy $count = 0;\nwhile ($v != 0) { $count += $v & 1; $v >>= 1; }\nmy $result = $count;",
    "java": "int v = a ^ b;\nint count = Integer.bitCount(v);\nint result = count;",
    "cpp": "int v = a ^ b;\nint count = 0;\nwhile (v != 0) { count += v & 1; v = (int)((unsigned int) v >> 1); }\nint result = count;",
    "csharp": "int v = a ^ b;\nint count = System.Numerics.BitOperations.PopCount((uint) v);\nint result = count;",
    "c": "unsigned int v = (unsigned int)(a ^ b);\nint count = 0;\nwhile (v != 0) { count += v & 1; v >>= 1; }\nint result = count;",
    "rust": "let v = (a ^ b) as u32;\nlet result: i32 = v.count_ones() as i32;",
    "swift": "let v = a ^ b\nlet result = v.nonzeroBitCount",
})

# ═════════════════════════════════════════════════════════════════════════
# is_power_of_two(n) -> bool
# ═════════════════════════════════════════════════════════════════════════
add("power-of-two", "int1", "is_power_of_two", "bool", {
    "go": "result := n > 0 && (n&(n-1)) == 0",
    "ruby": "result = n > 0 && (n & (n - 1)) == 0",
    "kotlin": "val result = n > 0 && (n and (n - 1)) == 0",
    "php": "$result = $n > 0 && ($n & ($n - 1)) == 0;",
    "scala": "val result = n > 0 && (n & (n - 1)) == 0",
    "r": "result <- n > 0 && bitwAnd(n, n - 1) == 0",
    "javascript": "const result = n > 0 && (n & (n - 1)) === 0;",
    "typescript": "const result = n > 0 && (n & (n - 1)) === 0;",
    "perl": "my $result = ($n > 0 && ($n & ($n - 1)) == 0) ? 1 : 0;",
    "java": "boolean result = n > 0 && (n & (n - 1)) == 0;",
    "cpp": "bool result = n > 0 && (n & (n - 1)) == 0;",
    "csharp": "bool result = n > 0 && (n & (n - 1)) == 0;",
    "c": "int result = n > 0 && (n & (n - 1)) == 0;",
    "rust": "let result: bool = n > 0 && (n & (n - 1)) == 0;",
    "swift": "let result = n > 0 && (n & (n - 1)) == 0",
})

# ═════════════════════════════════════════════════════════════════════════
# hamming_weight(n) -> int, popcount(n)
# ═════════════════════════════════════════════════════════════════════════
add("number-of-1-bits", "int1", "hamming_weight", "int", {
    "go": "v := n\ncount := 0\nfor v != 0 { count += v & 1; v = int(uint32(v) >> 1) }\nresult := int64(count)",
    "ruby": "v = n\ncount = 0\nwhile v != 0\n  count += v & 1\n  v >>= 1\nend\nresult = count",
    "kotlin": "var v = n\nvar count = 0\nwhile (v != 0) { count += v and 1; v = v ushr 1 }\nval result = count.toLong()",
    "php": "$v = $n;\n$count = 0;\nwhile ($v != 0) { $count += $v & 1; $v >>= 1; }\n$result = $count;",
    "scala": "var v = n\nvar count = 0\nwhile (v != 0) { count += v & 1; v = v >>> 1 }\nval result: Long = count",
    "r": "v <- n\ncount <- 0\nwhile (v != 0) { count <- count + bitwAnd(v, 1); v <- bitwShiftR(v, 1) }\nresult <- count",
    "javascript": "let v = n;\nlet count = 0;\nwhile (v !== 0) { count += v & 1; v >>>= 1; }\nconst result = count;",
    "typescript": "let v = n;\nlet count = 0;\nwhile (v !== 0) { count += v & 1; v >>>= 1; }\nconst result = count;",
    "perl": "my $v = $n;\nmy $count = 0;\nwhile ($v != 0) { $count += $v & 1; $v >>= 1; }\nmy $result = $count;",
    "java": "int result = Integer.bitCount(n);",
    "cpp": "unsigned int v = (unsigned int) n;\nint count = 0;\nwhile (v != 0) { count += v & 1; v >>= 1; }\nint result = count;",
    "csharp": "int result = System.Numerics.BitOperations.PopCount((uint) n);",
    "c": "unsigned int v = (unsigned int) n;\nint count = 0;\nwhile (v != 0) { count += v & 1; v >>= 1; }\nint result = count;",
    "rust": "let v = n as u32;\nlet result: i32 = v.count_ones() as i32;",
    "swift": "let result = n.nonzeroBitCount",
})

# ═════════════════════════════════════════════════════════════════════════
# euler_totient(n) -> int, count of integers in [1,n] coprime to n
# ═════════════════════════════════════════════════════════════════════════
add("euler-totient", "int1", "euler_totient", "int", {
    "go": "result64 := int64(n)\nx := n\np := 2\nfor p*p <= x {\n\tif x%p == 0 {\n\t\tfor x%p == 0 { x /= p }\n\t\tresult64 -= result64 / int64(p)\n\t}\n\tp++\n}\nif x > 1 { result64 -= result64 / int64(x) }\nresult := result64",
    "ruby": "result = n\nx = n\np = 2\nwhile p * p <= x\n  if x % p == 0\n    while x % p == 0\n      x /= p\n    end\n    result -= result / p\n  end\n  p += 1\nend\nresult -= result / x if x > 1",
    "kotlin": "var result = n.toLong()\nvar x = n\nvar p = 2\nwhile (p.toLong() * p <= x) {\n    if (x % p == 0) {\n        while (x % p == 0) x /= p\n        result -= result / p\n    }\n    p++\n}\nif (x > 1) result -= result / x",
    "php": "$result = $n;\n$x = $n;\n$p = 2;\nwhile ($p * $p <= $x) {\n    if ($x % $p == 0) {\n        while ($x % $p == 0) { $x = intdiv($x, $p); }\n        $result -= intdiv($result, $p);\n    }\n    $p++;\n}\nif ($x > 1) { $result -= intdiv($result, $x); }",
    "scala": "var result: Long = n\nvar x = n\nvar p = 2\nwhile (p.toLong() * p <= x) {\n  if (x % p == 0) {\n    while (x % p == 0) x /= p\n    result -= result / p\n  }\n  p += 1\n}\nif (x > 1) result -= result / x",
    "r": "result <- n\nx <- n\np <- 2\nwhile (p * p <= x) {\n  if (x %% p == 0) {\n    while (x %% p == 0) { x <- x %/% p }\n    result <- result - result %/% p\n  }\n  p <- p + 1\n}\nif (x > 1) result <- result - result %/% x",
    "javascript": "let result = n;\nlet x = n;\nlet p = 2;\nwhile (p * p <= x) {\n    if (x % p === 0) {\n        while (x % p === 0) x = Math.floor(x / p);\n        result -= Math.floor(result / p);\n    }\n    p++;\n}\nif (x > 1) result -= Math.floor(result / x);",
    "typescript": "let result = n;\nlet x = n;\nlet p = 2;\nwhile (p * p <= x) {\n    if (x % p === 0) {\n        while (x % p === 0) x = Math.floor(x / p);\n        result -= Math.floor(result / p);\n    }\n    p++;\n}\nif (x > 1) result -= Math.floor(result / x);",
    "perl": "my $result = $n;\nmy $x = $n;\nmy $p = 2;\nwhile ($p * $p <= $x) {\n    if ($x % $p == 0) {\n        while ($x % $p == 0) { $x = int($x / $p); }\n        $result -= int($result / $p);\n    }\n    $p++;\n}\nif ($x > 1) { $result -= int($result / $x); }",
    "java": "int result = n;\nint x = n;\nint p = 2;\nwhile ((long) p * p <= x) {\n    if (x % p == 0) {\n        while (x % p == 0) x /= p;\n        result -= result / p;\n    }\n    p++;\n}\nif (x > 1) result -= result / x;",
    "cpp": "int result = n;\nint x = n;\nint p = 2;\nwhile ((long long) p * p <= x) {\n    if (x % p == 0) {\n        while (x % p == 0) x /= p;\n        result -= result / p;\n    }\n    p++;\n}\nif (x > 1) result -= result / x;",
    "csharp": "int result = n;\nint x = n;\nint p = 2;\nwhile ((long) p * p <= x) {\n    if (x % p == 0) {\n        while (x % p == 0) x /= p;\n        result -= result / p;\n    }\n    p++;\n}\nif (x > 1) result -= result / x;",
    "c": "int result = n;\nint x = n;\nint p = 2;\nwhile ((long)p * p <= x) {\n    if (x % p == 0) {\n        while (x % p == 0) x /= p;\n        result -= result / p;\n    }\n    p++;\n}\nif (x > 1) result -= result / x;",
    "rust": "let mut result = n;\nlet mut x = n;\nlet mut p = 2;\nwhile (p as i64) * (p as i64) <= x as i64 {\n    if x % p == 0 {\n        while x % p == 0 { x /= p; }\n        result -= result / p;\n    }\n    p += 1;\n}\nif x > 1 { result -= result / x; }\nlet result: i32 = result;",
    "swift": "var result = n\nvar x = n\nvar p = 2\nwhile p * p <= x {\n    if x % p == 0 {\n        while x % p == 0 { x /= p }\n        result -= result / p\n    }\n    p += 1\n}\nif x > 1 { result -= result / x }",
})

# ═════════════════════════════════════════════════════════════════════════
# collatz(n) -> int, step count to reach 1
# ═════════════════════════════════════════════════════════════════════════
add("collatz", "int1", "collatz", "int", {
    "go": "steps := 0\nx := int64(n)\nfor x != 1 {\n\tif x%2 == 0 { x /= 2 } else { x = 3*x + 1 }\n\tsteps++\n}\nresult := int64(steps)",
    "ruby": "steps = 0\nx = n\nwhile x != 1\n  x = x.even? ? x / 2 : 3 * x + 1\n  steps += 1\nend\nresult = steps",
    "kotlin": "var steps = 0\nvar x = n.toLong()\nwhile (x != 1L) { x = if (x % 2 == 0L) x / 2 else 3 * x + 1; steps++ }\nval result = steps.toLong()",
    "php": "$steps = 0;\n$x = $n;\nwhile ($x != 1) { $x = ($x % 2 == 0) ? intdiv($x, 2) : 3 * $x + 1; $steps++; }\n$result = $steps;",
    "scala": "var steps = 0\nvar x: Long = n\nwhile (x != 1) { x = if (x % 2 == 0) x / 2 else 3 * x + 1; steps += 1 }\nval result: Long = steps",
    "r": "steps <- 0\nx <- as.double(n)\nwhile (x != 1) { x <- if (x %% 2 == 0) x / 2 else 3 * x + 1; steps <- steps + 1 }\nresult <- steps",
    "javascript": "let steps = 0;\nlet x = n;\nwhile (x !== 1) { x = x % 2 === 0 ? x / 2 : 3 * x + 1; steps++; }\nconst result = steps;",
    "typescript": "let steps = 0;\nlet x = n;\nwhile (x !== 1) { x = x % 2 === 0 ? x / 2 : 3 * x + 1; steps++; }\nconst result = steps;",
    "perl": "my $steps = 0;\nmy $x = $n;\nwhile ($x != 1) { $x = ($x % 2 == 0) ? $x / 2 : 3 * $x + 1; $steps++; }\nmy $result = $steps;",
    "java": "int steps = 0;\nlong x = n;\nwhile (x != 1) { x = (x % 2 == 0) ? x / 2 : 3 * x + 1; steps++; }\nint result = steps;",
    "cpp": "int steps = 0;\nlong long x = n;\nwhile (x != 1) { x = (x % 2 == 0) ? x / 2 : 3 * x + 1; steps++; }\nint result = steps;",
    "csharp": "int steps = 0;\nlong x = n;\nwhile (x != 1) { x = (x % 2 == 0) ? x / 2 : 3 * x + 1; steps++; }\nint result = steps;",
    "c": "int steps = 0;\nlong long x = n;\nwhile (x != 1) { x = (x % 2 == 0) ? x / 2 : 3 * x + 1; steps++; }\nint result = steps;",
    "rust": "let mut steps: i32 = 0;\nlet mut x: i64 = n as i64;\nwhile x != 1 { x = if x % 2 == 0 { x / 2 } else { 3 * x + 1 }; steps += 1; }\nlet result: i32 = steps;",
    "swift": "var steps = 0\nvar x = Int64(n)\nwhile x != 1 { x = x % 2 == 0 ? x / 2 : 3 * x + 1; steps += 1 }\nlet result = steps",
})

# ═════════════════════════════════════════════════════════════════════════
# climb_stairs(n) -> int, distinct ways to climb n stairs (1 or 2 at a
# time) -- Fibonacci-style DP
# ═════════════════════════════════════════════════════════════════════════
add("staircase", "int1", "climb_stairs", "int", {
    "go": "a, b := 1, 1\nfor i := 0; i < n; i++ { a, b = b, a+b }\nresult := int64(a)",
    "ruby": "a, b = 1, 1\nn.times { a, b = b, a + b }\nresult = a",
    "kotlin": "var a = 1L\nvar b = 1L\nfor (i in 0 until n) { val t = a + b; a = b; b = t }\nval result = a",
    "php": "$a = 1; $b = 1;\nfor ($i = 0; $i < $n; $i++) { $t = $a + $b; $a = $b; $b = $t; }\n$result = $a;",
    "scala": "var a: Long = 1\nvar b: Long = 1\nfor (i <- 0 until n) { val t = a + b; a = b; b = t }\nval result: Long = a",
    "r": "a <- 1; b <- 1\nif (n > 0) { for (i in 1:n) { t <- a + b; a <- b; b <- t } }\nresult <- a",
    "javascript": "let a = 1, b = 1;\nfor (let i = 0; i < n; i++) { const t = a + b; a = b; b = t; }\nconst result = a;",
    "typescript": "let a = 1, b = 1;\nfor (let i = 0; i < n; i++) { const t = a + b; a = b; b = t; }\nconst result = a;",
    "perl": "my $a = 1; my $b = 1;\nfor (my $i = 0; $i < $n; $i++) { my $t = $a + $b; $a = $b; $b = $t; }\nmy $result = $a;",
    "java": "long a = 1, b = 1;\nfor (int i = 0; i < n; i++) { long t = a + b; a = b; b = t; }\nint result = (int) a;",
    "cpp": "long long a = 1, b = 1;\nfor (int i = 0; i < n; i++) { long long t = a + b; a = b; b = t; }\nint result = (int) a;",
    "csharp": "long a = 1, b = 1;\nfor (int i = 0; i < n; i++) { long t = a + b; a = b; b = t; }\nint result = (int) a;",
    "c": "long long a = 1, b = 1;\nfor (int i = 0; i < n; i++) { long long t = a + b; a = b; b = t; }\nint result = (int) a;",
    "rust": "let mut a: i64 = 1;\nlet mut b: i64 = 1;\nfor _ in 0..n { let t = a + b; a = b; b = t; }\nlet result: i32 = a as i32;",
    "swift": "var a: Int64 = 1\nvar b: Int64 = 1\nfor _ in 0..<n { let t = a + b; a = b; b = t }\nlet result = Int(a)",
})

# ═════════════════════════════════════════════════════════════════════════
# egg_drop(eggs, floors) -> int, minimum trials for worst case (DP)
# ═════════════════════════════════════════════════════════════════════════
add("egg-drop", "int2", "egg_drop", "int", {
    "go": "eggs, floors := a, b\ndp := make([][]int, eggs+1)\nfor i := range dp { dp[i] = make([]int, floors+1) }\nfor j := 1; j <= floors; j++ { dp[1][j] = j }\nfor i := 2; i <= eggs; i++ {\n\tfor j := 1; j <= floors; j++ {\n\t\tdp[i][j] = j\n\t\tfor k := 1; k <= j; k++ {\n\t\t\tworst := 1 + max2(dp[i-1][k-1], dp[i][j-k])\n\t\t\tif worst < dp[i][j] { dp[i][j] = worst }\n\t\t}\n\t}\n}\nresult := int64(dp[eggs][floors])",
    "ruby": "eggs = a\nfloors = b\ndp = Array.new(eggs + 1) { Array.new(floors + 1, 0) }\n(1..floors).each { |j| dp[1][j] = j }\n(2..eggs).each do |i|\n  (1..floors).each do |j|\n    best = j\n    (1..j).each do |k|\n      worst = 1 + [dp[i - 1][k - 1], dp[i][j - k]].max\n      best = worst if worst < best\n    end\n    dp[i][j] = best\n  end\nend\nresult = eggs >= 1 ? dp[eggs][floors] : 0",
    "kotlin": "val eggs = a\nval floors = b\nval dp = Array(eggs + 1) { IntArray(floors + 1) }\nfor (j in 1..floors) dp[1][j] = j\nfor (i in 2..eggs) {\n    for (j in 1..floors) {\n        var best = j\n        for (k in 1..j) {\n            val worst = 1 + maxOf(dp[i - 1][k - 1], dp[i][j - k])\n            if (worst < best) best = worst\n        }\n        dp[i][j] = best\n    }\n}\nval result = dp[eggs][floors].toLong()",
    "php": "$eggs = $a; $floors = $b;\n$dp = array_fill(0, $eggs + 1, array_fill(0, $floors + 1, 0));\nfor ($j = 1; $j <= $floors; $j++) { $dp[1][$j] = $j; }\nfor ($i = 2; $i <= $eggs; $i++) {\n    for ($j = 1; $j <= $floors; $j++) {\n        $best = $j;\n        for ($k = 1; $k <= $j; $k++) {\n            $worst = 1 + max($dp[$i - 1][$k - 1], $dp[$i][$j - $k]);\n            if ($worst < $best) { $best = $worst; }\n        }\n        $dp[$i][$j] = $best;\n    }\n}\n$result = $dp[$eggs][$floors];",
    "scala": "val eggs = a\nval floors = b\nval dp = Array.ofDim[Int](eggs + 1, floors + 1)\nfor (j <- 1 to floors) dp(1)(j) = j\nfor (i <- 2 to eggs) {\n  for (j <- 1 to floors) {\n    var best = j\n    for (k <- 1 to j) {\n      val worst = 1 + math.max(dp(i - 1)(k - 1), dp(i)(j - k))\n      if (worst < best) best = worst\n    }\n    dp(i)(j) = best\n  }\n}\nval result: Long = dp(eggs)(floors)",
    "r": "eggs <- a; floors <- b\ndp <- matrix(0, nrow = eggs + 1, ncol = floors + 1)\nif (floors > 0) { for (j in 1:floors) dp[2, j + 1] <- j }\nif (eggs >= 2) {\n  for (i in 2:eggs) {\n    for (j in 1:floors) {\n      best <- j\n      for (k in 1:j) {\n        worst <- 1 + max(dp[i, k], dp[i + 1, j - k + 1])\n        if (worst < best) best <- worst\n      }\n      dp[i + 1, j + 1] <- best\n    }\n  }\n}\nresult <- dp[eggs + 1, floors + 1]",
    "javascript": "const eggs = a, floors = b;\nconst dp = Array.from({ length: eggs + 1 }, () => new Array(floors + 1).fill(0));\nfor (let j = 1; j <= floors; j++) dp[1][j] = j;\nfor (let i = 2; i <= eggs; i++) {\n    for (let j = 1; j <= floors; j++) {\n        let best = j;\n        for (let k = 1; k <= j; k++) {\n            const worst = 1 + Math.max(dp[i - 1][k - 1], dp[i][j - k]);\n            if (worst < best) best = worst;\n        }\n        dp[i][j] = best;\n    }\n}\nconst result = dp[eggs][floors];",
    "typescript": "const eggs = a, floors = b;\nconst dp: number[][] = Array.from({ length: eggs + 1 }, () => new Array(floors + 1).fill(0));\nfor (let j = 1; j <= floors; j++) dp[1][j] = j;\nfor (let i = 2; i <= eggs; i++) {\n    for (let j = 1; j <= floors; j++) {\n        let best = j;\n        for (let k = 1; k <= j; k++) {\n            const worst = 1 + Math.max(dp[i - 1][k - 1], dp[i][j - k]);\n            if (worst < best) best = worst;\n        }\n        dp[i][j] = best;\n    }\n}\nconst result = dp[eggs][floors];",
    "perl": "my $eggs = $a; my $floors = $b;\nmy @dp;\nfor my $i (0..$eggs) { for my $j (0..$floors) { $dp[$i][$j] = 0; } }\nfor my $j (1..$floors) { $dp[1][$j] = $j; }\nfor my $i (2..$eggs) {\n    for my $j (1..$floors) {\n        my $best = $j;\n        for my $k (1..$j) {\n            my $worst = 1 + ($dp[$i - 1][$k - 1] > $dp[$i][$j - $k] ? $dp[$i - 1][$k - 1] : $dp[$i][$j - $k]);\n            $best = $worst if $worst < $best;\n        }\n        $dp[$i][$j] = $best;\n    }\n}\nmy $result = $dp[$eggs][$floors];",
    "java": "int eggs = a, floors = b;\nint[][] dp = new int[eggs + 1][floors + 1];\nfor (int j = 1; j <= floors; j++) dp[1][j] = j;\nfor (int i = 2; i <= eggs; i++) {\n    for (int j = 1; j <= floors; j++) {\n        int best = j;\n        for (int k = 1; k <= j; k++) {\n            int worst = 1 + Math.max(dp[i - 1][k - 1], dp[i][j - k]);\n            if (worst < best) best = worst;\n        }\n        dp[i][j] = best;\n    }\n}\nint result = dp[eggs][floors];",
    "cpp": "int eggs = a, floors = b;\nstd::vector<std::vector<int>> dp(eggs + 1, std::vector<int>(floors + 1, 0));\nfor (int j = 1; j <= floors; j++) dp[1][j] = j;\nfor (int i = 2; i <= eggs; i++) {\n    for (int j = 1; j <= floors; j++) {\n        int best = j;\n        for (int k = 1; k <= j; k++) {\n            int worst = 1 + std::max(dp[i - 1][k - 1], dp[i][j - k]);\n            if (worst < best) best = worst;\n        }\n        dp[i][j] = best;\n    }\n}\nint result = dp[eggs][floors];",
    "csharp": "int eggs = a, floors = b;\nvar dp = new int[eggs + 1, floors + 1];\nfor (int j = 1; j <= floors; j++) dp[1, j] = j;\nfor (int i = 2; i <= eggs; i++) {\n    for (int j = 1; j <= floors; j++) {\n        int best = j;\n        for (int k = 1; k <= j; k++) {\n            int worst = 1 + System.Math.Max(dp[i - 1, k - 1], dp[i, j - k]);\n            if (worst < best) best = worst;\n        }\n        dp[i, j] = best;\n    }\n}\nint result = dp[eggs, floors];",
    "c": "int eggs = a, floors = b;\nint **dp = (int **)malloc(sizeof(int *) * (size_t)(eggs + 1));\nfor (int i = 0; i <= eggs; i++) dp[i] = (int *)calloc((size_t)(floors + 1), sizeof(int));\nfor (int j = 1; j <= floors; j++) dp[1][j] = j;\nfor (int i = 2; i <= eggs; i++) {\n    for (int j = 1; j <= floors; j++) {\n        int best = j;\n        for (int k = 1; k <= j; k++) {\n            int lo = dp[i - 1][k - 1], hi = dp[i][j - k];\n            int worst = 1 + (lo > hi ? lo : hi);\n            if (worst < best) best = worst;\n        }\n        dp[i][j] = best;\n    }\n}\nint result = dp[eggs][floors];",
    "rust": "let eggs = a as usize;\nlet floors = b as usize;\nlet mut dp = vec![vec![0i32; floors + 1]; eggs + 1];\nfor j in 1..=floors { dp[1][j] = j as i32; }\nfor i in 2..=eggs {\n    for j in 1..=floors {\n        let mut best = j as i32;\n        for k in 1..=j {\n            let worst = 1 + std::cmp::max(dp[i - 1][k - 1], dp[i][j - k]);\n            if worst < best { best = worst; }\n        }\n        dp[i][j] = best;\n    }\n}\nlet result: i32 = dp[eggs][floors];",
    "swift": "let eggs = a\nlet floors = b\nvar dp = Array(repeating: Array(repeating: 0, count: floors + 1), count: eggs + 1)\nif floors > 0 { for j in 1...floors { dp[1][j] = j } }\nif eggs >= 2 {\n    for i in 2...eggs {\n        for j in 1...floors {\n            var best = j\n            for k in 1...j {\n                let worst = 1 + max(dp[i - 1][k - 1], dp[i][j - k])\n                if worst < best { best = worst }\n            }\n            dp[i][j] = best\n        }\n    }\n}\nlet result = dp[eggs][floors]",
})

# ═════════════════════════════════════════════════════════════════════════
# minimum_total(triangle) -> int, minimum path sum top-to-bottom (existing
# "triangle" shape)
# ═════════════════════════════════════════════════════════════════════════
add("triangle-minimum-path-sum", "triangle", "minimum_total", "int", {
    "go": "n := len(triangle)\ndp := make([]int, n)\ncopy(dp, triangle[n-1])\nfor i := n - 2; i >= 0; i-- {\n\tfor j := 0; j <= i; j++ {\n\t\tif dp[j] < dp[j+1] { dp[j] = triangle[i][j] + dp[j] } else { dp[j] = triangle[i][j] + dp[j+1] }\n\t}\n}\nresult := int64(dp[0])",
    "ruby": "n = triangle.length\ndp = triangle[n - 1].dup\n(n - 2).downto(0) do |i|\n  (0..i).each do |j|\n    dp[j] = triangle[i][j] + [dp[j], dp[j + 1]].min\n  end\nend\nresult = dp[0]",
    "kotlin": "val n = triangle.size\nval dp = triangle[n - 1].copyOf()\nfor (i in n - 2 downTo 0) {\n    for (j in 0..i) {\n        dp[j] = triangle[i][j] + minOf(dp[j], dp[j + 1])\n    }\n}\nval result = dp[0].toLong()",
    "php": "$n = count($triangle);\n$dp = $triangle[$n - 1];\nfor ($i = $n - 2; $i >= 0; $i--) {\n    for ($j = 0; $j <= $i; $j++) {\n        $dp[$j] = $triangle[$i][$j] + min($dp[$j], $dp[$j + 1]);\n    }\n}\n$result = $dp[0];",
    "scala": "val n = triangle.length\nval dp = triangle(n - 1).clone()\nfor (i <- (n - 2) to 0 by -1) {\n  for (j <- 0 to i) {\n    dp(j) = triangle(i)(j) + math.min(dp(j), dp(j + 1))\n  }\n}\nval result: Long = dp(0)",
    "r": "n <- length(triangle)\ndp <- triangle[[n]]\nif (n >= 2) { for (i in (n - 1):1) {\n  for (j in 1:i) {\n    dp[j] <- triangle[[i]][j] + min(dp[j], dp[j + 1])\n  }\n} }\nresult <- dp[1]",
    "javascript": "const n = triangle.length;\nconst dp = triangle[n - 1].slice();\nfor (let i = n - 2; i >= 0; i--) {\n    for (let j = 0; j <= i; j++) {\n        dp[j] = triangle[i][j] + Math.min(dp[j], dp[j + 1]);\n    }\n}\nconst result = dp[0];",
    "typescript": "const n = triangle.length;\nconst dp = triangle[n - 1].slice();\nfor (let i = n - 2; i >= 0; i--) {\n    for (let j = 0; j <= i; j++) {\n        dp[j] = triangle[i][j] + Math.min(dp[j], dp[j + 1]);\n    }\n}\nconst result = dp[0];",
    "perl": "my $n = scalar(@{$triangle});\nmy @dp = @{$triangle->[$n - 1]};\nfor (my $i = $n - 2; $i >= 0; $i--) {\n    for (my $j = 0; $j <= $i; $j++) {\n        my $m = $dp[$j] < $dp[$j + 1] ? $dp[$j] : $dp[$j + 1];\n        $dp[$j] = $triangle->[$i][$j] + $m;\n    }\n}\nmy $result = $dp[0];",
    "java": "int n = triangle.length;\nint[] dp = triangle[n - 1].clone();\nfor (int i = n - 2; i >= 0; i--) {\n    for (int j = 0; j <= i; j++) {\n        dp[j] = triangle[i][j] + Math.min(dp[j], dp[j + 1]);\n    }\n}\nint result = dp[0];",
    "cpp": "int n = (int) triangle.size();\nstd::vector<int> dp = triangle[n - 1];\nfor (int i = n - 2; i >= 0; i--) {\n    for (int j = 0; j <= i; j++) {\n        dp[j] = triangle[i][j] + std::min(dp[j], dp[j + 1]);\n    }\n}\nint result = dp[0];",
    "csharp": "int n = triangle.Length;\nvar dp = (int[]) triangle[n - 1].Clone();\nfor (int i = n - 2; i >= 0; i--) {\n    for (int j = 0; j <= i; j++) {\n        dp[j] = triangle[i][j] + System.Math.Min(dp[j], dp[j + 1]);\n    }\n}\nint result = dp[0];",
    "c": "int n = triangle.size;\nint *dp = (int *)malloc(sizeof(int) * (size_t) n);\nmemcpy(dp, triangle.data[n - 1].data, sizeof(int) * (size_t) n);\nfor (int i = n - 2; i >= 0; i--) {\n    for (int j = 0; j <= i; j++) {\n        int m = dp[j] < dp[j + 1] ? dp[j] : dp[j + 1];\n        dp[j] = triangle.data[i].data[j] + m;\n    }\n}\nint result = dp[0];\nfree(dp);",
    "rust": "let n = triangle.len();\nlet mut dp = triangle[n - 1].clone();\nfor i in (0..n - 1).rev() {\n    for j in 0..=i {\n        dp[j] = triangle[i][j] + std::cmp::min(dp[j], dp[j + 1]);\n    }\n}\nlet result: i32 = dp[0];",
    "swift": "let n = triangle.count\nvar dp = triangle[n - 1]\nif n >= 2 {\n    for i in stride(from: n - 2, through: 0, by: -1) {\n        for j in 0...i {\n            dp[j] = triangle[i][j] + min(dp[j], dp[j + 1])\n        }\n    }\n}\nlet result = dp[0]",
})

# ═════════════════════════════════════════════════════════════════════════
# coin_change(coins, extra=amount) -> int, min coins to make amount (-1 if
# impossible)
# ═════════════════════════════════════════════════════════════════════════
add("coin-change", "arr1_int", "coin_change", "int", {
    "go": "amount := extra\ndp := make([]int, amount+1)\nfor i := 1; i <= amount; i++ { dp[i] = 1 << 30 }\nfor i := 1; i <= amount; i++ {\n\tfor _, c := range nums {\n\t\tif c <= i && dp[i-c]+1 < dp[i] { dp[i] = dp[i-c] + 1 }\n\t}\n}\nresult := int64(-1)\nif dp[amount] < 1<<30 { result = int64(dp[amount]) }",
    "ruby": "amount = extra\ndp = Array.new(amount + 1, 1 << 30)\ndp[0] = 0\n(1..amount).each do |i|\n  nums.each do |c|\n    dp[i] = [dp[i], dp[i - c] + 1].min if c <= i\n  end\nend\nresult = dp[amount] < (1 << 30) ? dp[amount] : -1",
    "kotlin": "val amount = extra\nval dp = IntArray(amount + 1) { if (it == 0) 0 else Int.MAX_VALUE / 2 }\nfor (i in 1..amount) {\n    for (c in nums) {\n        if (c <= i && dp[i - c] + 1 < dp[i]) dp[i] = dp[i - c] + 1\n    }\n}\nval result = if (dp[amount] >= Int.MAX_VALUE / 2) -1L else dp[amount].toLong()",
    "php": "$amount = $extra;\n$dp = array_fill(0, $amount + 1, PHP_INT_MAX);\n$dp[0] = 0;\nfor ($i = 1; $i <= $amount; $i++) {\n    foreach ($nums as $c) {\n        if ($c <= $i && $dp[$i - $c] + 1 < $dp[$i]) { $dp[$i] = $dp[$i - $c] + 1; }\n    }\n}\n$result = $dp[$amount] >= PHP_INT_MAX ? -1 : $dp[$amount];",
    "scala": "val amount = extra\nval dp = Array.fill(amount + 1)(Int.MaxValue / 2)\ndp(0) = 0\nfor (i <- 1 to amount) {\n  for (c <- nums) {\n    if (c <= i && dp(i - c) + 1 < dp(i)) dp(i) = dp(i - c) + 1\n  }\n}\nval result: Long = if (dp(amount) >= Int.MaxValue / 2) -1L else dp(amount)",
    "r": "amount <- extra\nBIG <- 2000000000\ndp <- rep(BIG, amount + 1)\ndp[1] <- 0\nif (amount >= 1) { for (i in 1:amount) {\n  for (c in nums) {\n    if (c <= i && dp[i - c + 1] + 1 < dp[i + 1]) dp[i + 1] <- dp[i - c + 1] + 1\n  }\n} }\nresult <- if (dp[amount + 1] >= BIG) -1 else dp[amount + 1]",
    "javascript": "const amount = extra;\nconst dp = new Array(amount + 1).fill(Infinity);\ndp[0] = 0;\nfor (let i = 1; i <= amount; i++) {\n    for (const c of nums) {\n        if (c <= i && dp[i - c] + 1 < dp[i]) dp[i] = dp[i - c] + 1;\n    }\n}\nconst result = dp[amount] === Infinity ? -1 : dp[amount];",
    "typescript": "const amount = extra;\nconst dp: number[] = new Array(amount + 1).fill(Infinity);\ndp[0] = 0;\nfor (let i = 1; i <= amount; i++) {\n    for (const c of nums) {\n        if (c <= i && dp[i - c] + 1 < dp[i]) dp[i] = dp[i - c] + 1;\n    }\n}\nconst result = dp[amount] === Infinity ? -1 : dp[amount];",
    "perl": "my $amount = $extra;\nmy @dp = (1000000000) x ($amount + 1);\n$dp[0] = 0;\nfor (my $i = 1; $i <= $amount; $i++) {\n    foreach my $c (@{$nums}) {\n        if ($c <= $i && $dp[$i - $c] + 1 < $dp[$i]) { $dp[$i] = $dp[$i - $c] + 1; }\n    }\n}\nmy $result = $dp[$amount] >= 1000000000 ? -1 : $dp[$amount];",
    "java": "int amount = extra;\nint[] dp = new int[amount + 1];\njava.util.Arrays.fill(dp, Integer.MAX_VALUE / 2);\ndp[0] = 0;\nfor (int i = 1; i <= amount; i++) {\n    for (int c : nums) {\n        if (c <= i && dp[i - c] + 1 < dp[i]) dp[i] = dp[i - c] + 1;\n    }\n}\nint result = dp[amount] >= Integer.MAX_VALUE / 2 ? -1 : dp[amount];",
    "cpp": "int amount = extra;\nstd::vector<int> dp(amount + 1, INT_MAX / 2);\ndp[0] = 0;\nfor (int i = 1; i <= amount; i++) {\n    for (int c : nums) {\n        if (c <= i && dp[i - c] + 1 < dp[i]) dp[i] = dp[i - c] + 1;\n    }\n}\nint result = dp[amount] >= INT_MAX / 2 ? -1 : dp[amount];",
    "csharp": "int amount = extra;\nvar dp = new int[amount + 1];\nfor (int i = 0; i <= amount; i++) dp[i] = int.MaxValue / 2;\ndp[0] = 0;\nfor (int i = 1; i <= amount; i++) {\n    foreach (var c in nums) {\n        if (c <= i && dp[i - c] + 1 < dp[i]) dp[i] = dp[i - c] + 1;\n    }\n}\nint result = dp[amount] >= int.MaxValue / 2 ? -1 : dp[amount];",
    "c": "int amount = extra;\nint *dp = (int *)malloc(sizeof(int) * (size_t)(amount + 1));\nfor (int i = 0; i <= amount; i++) dp[i] = 1000000000;\ndp[0] = 0;\nfor (int i = 1; i <= amount; i++) {\n    for (int k = 0; k < n; k++) {\n        int c = nums[k];\n        if (c <= i && dp[i - c] + 1 < dp[i]) dp[i] = dp[i - c] + 1;\n    }\n}\nint result = dp[amount] >= 1000000000 ? -1 : dp[amount];\nfree(dp);",
    "rust": "let amount = extra as usize;\nlet mut dp = vec![i32::MAX / 2; amount + 1];\ndp[0] = 0;\nfor i in 1..=amount {\n    for &c in nums.iter() {\n        let c = c as usize;\n        if c <= i && dp[i - c] + 1 < dp[i] { dp[i] = dp[i - c] + 1; }\n    }\n}\nlet result: i32 = if dp[amount] >= i32::MAX / 2 { -1 } else { dp[amount] };",
    "swift": "let amount = extra\nvar dp = Array(repeating: Int.max / 2, count: amount + 1)\ndp[0] = 0\nif amount >= 1 {\n    for i in 1...amount {\n        for c in nums {\n            if c <= i && dp[i - c] + 1 < dp[i] { dp[i] = dp[i - c] + 1 }\n        }\n    }\n}\nlet result = dp[amount] >= Int.max / 2 ? -1 : dp[amount]",
})

# ═════════════════════════════════════════════════════════════════════════
# change(coins, extra=amount) -> int, number of combinations to make
# amount (order-independent, unbounded)
# ═════════════════════════════════════════════════════════════════════════
add("coin-change-ways", "arr1_int", "change", "int", {
    "go": "amount := extra\ndp := make([]int64, amount+1)\ndp[0] = 1\nfor _, c := range nums {\n\tfor i := c; i <= amount; i++ { dp[i] += dp[i-c] }\n}\nresult := dp[amount]",
    "ruby": "amount = extra\ndp = Array.new(amount + 1, 0)\ndp[0] = 1\nnums.each do |c|\n  (c..amount).each { |i| dp[i] += dp[i - c] }\nend\nresult = dp[amount]",
    "kotlin": "val amount = extra\nval dp = LongArray(amount + 1)\ndp[0] = 1\nfor (c in nums) {\n    for (i in c..amount) dp[i] += dp[i - c]\n}\nval result = dp[amount]",
    "php": "$amount = $extra;\n$dp = array_fill(0, $amount + 1, 0);\n$dp[0] = 1;\nforeach ($nums as $c) {\n    for ($i = $c; $i <= $amount; $i++) { $dp[$i] += $dp[$i - $c]; }\n}\n$result = $dp[$amount];",
    "scala": "val amount = extra\nval dp = Array.fill(amount + 1)(0L)\ndp(0) = 1\nfor (c <- nums) {\n  for (i <- c to amount) dp(i) += dp(i - c)\n}\nval result: Long = dp(amount)",
    "r": "amount <- extra\ndp <- rep(0, amount + 1)\ndp[1] <- 1\nfor (c in nums) {\n  if (c <= amount) { for (i in c:amount) { dp[i + 1] <- dp[i + 1] + dp[i - c + 1] } }\n}\nresult <- dp[amount + 1]",
    "javascript": "const amount = extra;\nconst dp = new Array(amount + 1).fill(0);\ndp[0] = 1;\nfor (const c of nums) {\n    for (let i = c; i <= amount; i++) dp[i] += dp[i - c];\n}\nconst result = dp[amount];",
    "typescript": "const amount = extra;\nconst dp: number[] = new Array(amount + 1).fill(0);\ndp[0] = 1;\nfor (const c of nums) {\n    for (let i = c; i <= amount; i++) dp[i] += dp[i - c];\n}\nconst result = dp[amount];",
    "perl": "my $amount = $extra;\nmy @dp = (0) x ($amount + 1);\n$dp[0] = 1;\nforeach my $c (@{$nums}) {\n    for (my $i = $c; $i <= $amount; $i++) { $dp[$i] += $dp[$i - $c]; }\n}\nmy $result = $dp[$amount];",
    "java": "int amount = extra;\nlong[] dp = new long[amount + 1];\ndp[0] = 1;\nfor (int c : nums) {\n    for (int i = c; i <= amount; i++) dp[i] += dp[i - c];\n}\nint result = (int) dp[amount];",
    "cpp": "int amount = extra;\nstd::vector<long long> dp(amount + 1, 0);\ndp[0] = 1;\nfor (int c : nums) {\n    for (int i = c; i <= amount; i++) dp[i] += dp[i - c];\n}\nint result = (int) dp[amount];",
    "csharp": "int amount = extra;\nvar dp = new long[amount + 1];\ndp[0] = 1;\nforeach (var c in nums) {\n    for (int i = c; i <= amount; i++) dp[i] += dp[i - c];\n}\nint result = (int) dp[amount];",
    "c": "int amount = extra;\nlong long *dp = (long long *)calloc((size_t)(amount + 1), sizeof(long long));\ndp[0] = 1;\nfor (int k = 0; k < n; k++) {\n    int c = nums[k];\n    for (int i = c; i <= amount; i++) dp[i] += dp[i - c];\n}\nint result = (int) dp[amount];\nfree(dp);",
    "rust": "let amount = extra as usize;\nlet mut dp = vec![0i64; amount + 1];\ndp[0] = 1;\nfor &c in nums.iter() {\n    let c = c as usize;\n    for i in c..=amount { dp[i] += dp[i - c]; }\n}\nlet result: i32 = dp[amount] as i32;",
    "swift": "let amount = extra\nvar dp = [Int64](repeating: 0, count: amount + 1)\ndp[0] = 1\nfor c in nums {\n    if c <= amount {\n        for i in c...amount { dp[i] += dp[i - c] }\n    }\n}\nlet result = Int(dp[amount])",
})

# ═════════════════════════════════════════════════════════════════════════
# max_activities(a=starts, b=ends) -> int, max non-overlapping activities
# (greedy, sort by end time)
# ═════════════════════════════════════════════════════════════════════════
add("activity-selection", "arr2_samelen", "max_activities", "int", {
    "go": "n := len(a)\nidx := make([]int, n)\nfor i := range idx { idx[i] = i }\nsort.Slice(idx, func(x, y int) bool { return b[idx[x]] < b[idx[y]] })\ncount := 0\nlastEnd := -1 << 62\nfor _, i := range idx {\n\tif a[i] >= lastEnd { count++; lastEnd = b[i] }\n}\nresult := int64(count)",
    "ruby": "n = a.length\nidx = (0...n).sort_by { |i| b[i] }\ncount = 0\nlast_end = -(2**62)\nidx.each do |i|\n  if a[i] >= last_end\n    count += 1\n    last_end = b[i]\n  end\nend\nresult = count",
    "kotlin": "val n = a.size\nval idx = (0 until n).sortedBy { b[it] }\nvar count = 0\nvar lastEnd = Long.MIN_VALUE\nfor (i in idx) {\n    if (a[i] >= lastEnd) { count++; lastEnd = b[i].toLong() }\n}\nval result = count.toLong()",
    "php": "$n = count($a);\n$idx = range(0, $n - 1);\nusort($idx, function($x, $y) use ($b) { return $b[$x] <=> $b[$y]; });\n$count = 0;\n$lastEnd = PHP_INT_MIN;\nforeach ($idx as $i) {\n    if ($a[$i] >= $lastEnd) { $count++; $lastEnd = $b[$i]; }\n}\n$result = $count;",
    "scala": "val n = a.length\nval idx = (0 until n).sortBy(i => b(i))\nvar count = 0\nvar lastEnd = Long.MinValue\nfor (i <- idx) {\n  if (a(i) >= lastEnd) { count += 1; lastEnd = b(i).toLong }\n}\nval result: Long = count",
    "r": "n <- length(a)\nidx <- order(b)\ncount <- 0\nlastEnd <- -.Machine$integer.max\nfor (i in idx) {\n  if (a[i] >= lastEnd) { count <- count + 1; lastEnd <- b[i] }\n}\nresult <- count",
    "javascript": "const n = a.length;\nconst idx = Array.from({ length: n }, (_, i) => i).sort((x, y) => b[x] - b[y]);\nlet count = 0;\nlet lastEnd = -Infinity;\nfor (const i of idx) {\n    if (a[i] >= lastEnd) { count++; lastEnd = b[i]; }\n}\nconst result = count;",
    "typescript": "const n = a.length;\nconst idx = Array.from({ length: n }, (_, i) => i).sort((x, y) => b[x] - b[y]);\nlet count = 0;\nlet lastEnd = -Infinity;\nfor (const i of idx) {\n    if (a[i] >= lastEnd) { count++; lastEnd = b[i]; }\n}\nconst result = count;",
    "perl": "my $n = scalar(@{$a});\nmy @idx = sort { $b->[$a] <=> $b->[$b] } (0..$n-1);\n\nmy $count = 0;\nmy $lastEnd = -(2**31);\nforeach my $i (@idx) {\n    if ($a->[$i] >= $lastEnd) { $count++; $lastEnd = $b->[$i]; }\n}\nmy $result = $count;",
    "java": "int n = a.length;\nInteger[] idx = new Integer[n];\nfor (int i = 0; i < n; i++) idx[i] = i;\nfinal int[] bb = b;\njava.util.Arrays.sort(idx, (x, y) -> bb[x] - bb[y]);\nint count = 0;\nlong lastEnd = Long.MIN_VALUE;\nfor (int i : idx) {\n    if (a[i] >= lastEnd) { count++; lastEnd = b[i]; }\n}\nint result = count;",
    "cpp": "int n = (int) a.size();\nstd::vector<int> idx(n);\nfor (int i = 0; i < n; i++) idx[i] = i;\nstd::sort(idx.begin(), idx.end(), [&](int x, int y) { return b[x] < b[y]; });\nint count = 0;\nlong long lastEnd = LLONG_MIN;\nfor (int i : idx) {\n    if (a[i] >= lastEnd) { count++; lastEnd = b[i]; }\n}\nint result = count;",
    "csharp": "int n = a.Length;\nvar idx = new int[n];\nfor (int i = 0; i < n; i++) idx[i] = i;\nSystem.Array.Sort(idx, (x, y) => b[x].CompareTo(b[y]));\nint count = 0;\nlong lastEnd = long.MinValue;\nforeach (var i in idx) {\n    if (a[i] >= lastEnd) { count++; lastEnd = b[i]; }\n}\nint result = count;",
    "c": "int *idx = (int *)malloc(sizeof(int) * (size_t)(n > 0 ? n : 1));\nfor (int i = 0; i < n; i++) idx[i] = i;\nfor (int i = 0; i < n; i++) { for (int j = i + 1; j < n; j++) { if (b[idx[j]] < b[idx[i]]) { int t = idx[i]; idx[i] = idx[j]; idx[j] = t; } } }\nint count = 0;\nlong long lastEnd = -2000000000000LL;\nfor (int k = 0; k < n; k++) {\n    int i = idx[k];\n    if (a[i] >= lastEnd) { count++; lastEnd = b[i]; }\n}\nint result = count;\nfree(idx);",
    "rust": "let n = a.len();\nlet mut idx: Vec<usize> = (0..n).collect();\nidx.sort_by_key(|&i| b[i]);\nlet mut count: i32 = 0;\nlet mut last_end: i64 = i64::MIN;\nfor &i in idx.iter() {\n    if a[i] as i64 >= last_end { count += 1; last_end = b[i] as i64; }\n}\nlet result: i32 = count;",
    "swift": "let n = a.count\nvar idx = Array(0..<n)\nidx.sort { b[$0] < b[$1] }\nvar count = 0\nvar lastEnd = Int.min\nfor i in idx {\n    if a[i] >= lastEnd { count += 1; lastEnd = b[i] }\n}\nlet result = count",
})

# ═════════════════════════════════════════════════════════════════════════
# can_complete_circuit(a=gas, b=cost) -> int, starting index for a valid
# circular gas-station tour, or -1
# ═════════════════════════════════════════════════════════════════════════
add("gas-station", "arr2_samelen", "can_complete_circuit", "int", {
    "go": "n := len(a)\ntotal, tank, start := 0, 0, 0\nfor i := 0; i < n; i++ {\n\tdiff := a[i] - b[i]\n\ttotal += diff\n\ttank += diff\n\tif tank < 0 { start = i + 1; tank = 0 }\n}\nresult := int64(-1)\nif total >= 0 { result = int64(start) }",
    "ruby": "n = a.length\ntotal = 0\ntank = 0\nstart = 0\n(0...n).each do |i|\n  diff = a[i] - b[i]\n  total += diff\n  tank += diff\n  if tank < 0\n    start = i + 1\n    tank = 0\n  end\nend\nresult = total >= 0 ? start : -1",
    "kotlin": "val n = a.size\nvar total = 0\nvar tank = 0\nvar start = 0\nfor (i in 0 until n) {\n    val diff = a[i] - b[i]\n    total += diff\n    tank += diff\n    if (tank < 0) { start = i + 1; tank = 0 }\n}\nval result = if (total >= 0) start.toLong() else -1L",
    "php": "$n = count($a);\n$total = 0; $tank = 0; $start = 0;\nfor ($i = 0; $i < $n; $i++) {\n    $diff = $a[$i] - $b[$i];\n    $total += $diff;\n    $tank += $diff;\n    if ($tank < 0) { $start = $i + 1; $tank = 0; }\n}\n$result = $total >= 0 ? $start : -1;",
    "scala": "val n = a.length\nvar total = 0\nvar tank = 0\nvar start = 0\nfor (i <- 0 until n) {\n  val diff = a(i) - b(i)\n  total += diff\n  tank += diff\n  if (tank < 0) { start = i + 1; tank = 0 }\n}\nval result: Long = if (total >= 0) start else -1",
    "r": "n <- length(a)\ntotal <- 0; tank <- 0; start <- 0\nfor (i in 1:n) {\n  diff <- a[i] - b[i]\n  total <- total + diff\n  tank <- tank + diff\n  if (tank < 0) { start <- i; tank <- 0 }\n}\nresult <- if (total >= 0) start else -1",
    "javascript": "const n = a.length;\nlet total = 0, tank = 0, start = 0;\nfor (let i = 0; i < n; i++) {\n    const diff = a[i] - b[i];\n    total += diff;\n    tank += diff;\n    if (tank < 0) { start = i + 1; tank = 0; }\n}\nconst result = total >= 0 ? start : -1;",
    "typescript": "const n = a.length;\nlet total = 0, tank = 0, start = 0;\nfor (let i = 0; i < n; i++) {\n    const diff = a[i] - b[i];\n    total += diff;\n    tank += diff;\n    if (tank < 0) { start = i + 1; tank = 0; }\n}\nconst result = total >= 0 ? start : -1;",
    "perl": "my $n = scalar(@{$a});\nmy $total = 0; my $tank = 0; my $start = 0;\nfor (my $i = 0; $i < $n; $i++) {\n    my $diff = $a->[$i] - $b->[$i];\n    $total += $diff;\n    $tank += $diff;\n    if ($tank < 0) { $start = $i + 1; $tank = 0; }\n}\nmy $result = $total >= 0 ? $start : -1;",
    "java": "int n = a.length;\nint total = 0, tank = 0, start = 0;\nfor (int i = 0; i < n; i++) {\n    int diff = a[i] - b[i];\n    total += diff;\n    tank += diff;\n    if (tank < 0) { start = i + 1; tank = 0; }\n}\nint result = total >= 0 ? start : -1;",
    "cpp": "int n = (int) a.size();\nint total = 0, tank = 0, start = 0;\nfor (int i = 0; i < n; i++) {\n    int diff = a[i] - b[i];\n    total += diff;\n    tank += diff;\n    if (tank < 0) { start = i + 1; tank = 0; }\n}\nint result = total >= 0 ? start : -1;",
    "csharp": "int n = a.Length;\nint total = 0, tank = 0, start = 0;\nfor (int i = 0; i < n; i++) {\n    int diff = a[i] - b[i];\n    total += diff;\n    tank += diff;\n    if (tank < 0) { start = i + 1; tank = 0; }\n}\nint result = total >= 0 ? start : -1;",
    "c": "int total = 0, tank = 0, start = 0;\nfor (int i = 0; i < n; i++) {\n    int diff = a[i] - b[i];\n    total += diff;\n    tank += diff;\n    if (tank < 0) { start = i + 1; tank = 0; }\n}\nint result = total >= 0 ? start : -1;",
    "rust": "let n = a.len();\nlet mut total: i32 = 0;\nlet mut tank: i32 = 0;\nlet mut start: i32 = 0;\nfor i in 0..n {\n    let diff = a[i] - b[i];\n    total += diff;\n    tank += diff;\n    if tank < 0 { start = i as i32 + 1; tank = 0; }\n}\nlet result: i32 = if total >= 0 { start } else { -1 };",
    "swift": "let n = a.count\nvar total = 0\nvar tank = 0\nvar start = 0\nfor i in 0..<n {\n    let diff = a[i] - b[i]\n    total += diff\n    tank += diff\n    if tank < 0 { start = i + 1; tank = 0 }\n}\nlet result = total >= 0 ? start : -1",
})

# ═════════════════════════════════════════════════════════════════════════
# min_meeting_rooms(a=starts, b=ends) -> int, minimum concurrent rooms
# needed (sweep-line over sorted start/end events)
# ═════════════════════════════════════════════════════════════════════════
add("meeting-rooms", "arr2_samelen", "min_meeting_rooms", "int", {
    "go": "n := len(a)\nstarts := append([]int{}, a...)\nends := append([]int{}, b...)\nsort.Ints(starts)\nsort.Ints(ends)\nrooms, best := 0, 0\ni, j := 0, 0\nfor i < n {\n\tif starts[i] < ends[j] { rooms++; i++; if rooms > best { best = rooms } } else { rooms--; j++ }\n}\nresult := int64(best)",
    "ruby": "n = a.length\nstarts = a.sort\nends = b.sort\nrooms = 0\nbest = 0\ni = 0\nj = 0\nwhile i < n\n  if starts[i] < ends[j]\n    rooms += 1\n    i += 1\n    best = rooms if rooms > best\n  else\n    rooms -= 1\n    j += 1\n  end\nend\nresult = best",
    "kotlin": "val n = a.size\nval starts = a.sortedArray()\nval ends = b.sortedArray()\nvar rooms = 0\nvar best = 0\nvar i = 0\nvar j = 0\nwhile (i < n) {\n    if (starts[i] < ends[j]) { rooms++; i++; if (rooms > best) best = rooms } else { rooms--; j++ }\n}\nval result = best.toLong()",
    "php": "$n = count($a);\n$starts = $a; sort($starts);\n$ends = $b; sort($ends);\n$rooms = 0; $best = 0; $i = 0; $j = 0;\nwhile ($i < $n) {\n    if ($starts[$i] < $ends[$j]) { $rooms++; $i++; if ($rooms > $best) { $best = $rooms; } }\n    else { $rooms--; $j++; }\n}\n$result = $best;",
    "scala": "val n = a.length\nval starts = a.sorted\nval ends = b.sorted\nvar rooms = 0\nvar best = 0\nvar i = 0\nvar j = 0\nwhile (i < n) {\n  if (starts(i) < ends(j)) { rooms += 1; i += 1; if (rooms > best) best = rooms }\n  else { rooms -= 1; j += 1 }\n}\nval result: Long = best",
    "r": "n <- length(a)\nstarts <- sort(a)\nends <- sort(b)\nrooms <- 0; best <- 0; i <- 1; j <- 1\nwhile (i <= n) {\n  if (starts[i] < ends[j]) { rooms <- rooms + 1; i <- i + 1; if (rooms > best) best <- rooms }\n  else { rooms <- rooms - 1; j <- j + 1 }\n}\nresult <- best",
    "javascript": "const n = a.length;\nconst starts = a.slice().sort((x, y) => x - y);\nconst ends = b.slice().sort((x, y) => x - y);\nlet rooms = 0, best = 0, i = 0, j = 0;\nwhile (i < n) {\n    if (starts[i] < ends[j]) { rooms++; i++; if (rooms > best) best = rooms; }\n    else { rooms--; j++; }\n}\nconst result = best;",
    "typescript": "const n = a.length;\nconst starts = a.slice().sort((x, y) => x - y);\nconst ends = b.slice().sort((x, y) => x - y);\nlet rooms = 0, best = 0, i = 0, j = 0;\nwhile (i < n) {\n    if (starts[i] < ends[j]) { rooms++; i++; if (rooms > best) best = rooms; }\n    else { rooms--; j++; }\n}\nconst result = best;",
    "perl": "my $n = scalar(@{$a});\nmy @starts = sort { $a <=> $b } @{$a};\nmy @ends = sort { $a <=> $b } @{$b};\nmy $rooms = 0; my $best = 0; my $i = 0; my $j = 0;\nwhile ($i < $n) {\n    if ($starts[$i] < $ends[$j]) { $rooms++; $i++; $best = $rooms if $rooms > $best; }\n    else { $rooms--; $j++; }\n}\nmy $result = $best;",
    "java": "int n = a.length;\nint[] starts = a.clone();\nint[] ends = b.clone();\njava.util.Arrays.sort(starts);\njava.util.Arrays.sort(ends);\nint rooms = 0, best = 0, i = 0, j = 0;\nwhile (i < n) {\n    if (starts[i] < ends[j]) { rooms++; i++; if (rooms > best) best = rooms; }\n    else { rooms--; j++; }\n}\nint result = best;",
    "cpp": "int n = (int) a.size();\nstd::vector<int> starts = a, ends = b;\nstd::sort(starts.begin(), starts.end());\nstd::sort(ends.begin(), ends.end());\nint rooms = 0, best = 0, i = 0, j = 0;\nwhile (i < n) {\n    if (starts[i] < ends[j]) { rooms++; i++; if (rooms > best) best = rooms; }\n    else { rooms--; j++; }\n}\nint result = best;",
    "csharp": "int n = a.Length;\nvar starts = (int[]) a.Clone();\nvar ends = (int[]) b.Clone();\nSystem.Array.Sort(starts);\nSystem.Array.Sort(ends);\nint rooms = 0, best = 0, i = 0, j = 0;\nwhile (i < n) {\n    if (starts[i] < ends[j]) { rooms++; i++; if (rooms > best) best = rooms; }\n    else { rooms--; j++; }\n}\nint result = best;",
    "c": "int *starts = (int *)malloc(sizeof(int) * (size_t)(n > 0 ? n : 1));\nint *ends = (int *)malloc(sizeof(int) * (size_t)(n > 0 ? n : 1));\nmemcpy(starts, a, sizeof(int) * (size_t) n);\nmemcpy(ends, b, sizeof(int) * (size_t) n);\nfor (int i = 0; i < n; i++) { for (int j = i + 1; j < n; j++) { if (starts[j] < starts[i]) { int t = starts[i]; starts[i] = starts[j]; starts[j] = t; } if (ends[j] < ends[i]) { int t = ends[i]; ends[i] = ends[j]; ends[j] = t; } } }\nint rooms = 0, best = 0, i = 0, j = 0;\nwhile (i < n) {\n    if (starts[i] < ends[j]) { rooms++; i++; if (rooms > best) best = rooms; }\n    else { rooms--; j++; }\n}\nint result = best;\nfree(starts); free(ends);",
    "rust": "let n = a.len();\nlet mut starts = a.clone();\nlet mut ends = b.clone();\nstarts.sort();\nends.sort();\nlet mut rooms: i32 = 0;\nlet mut best: i32 = 0;\nlet mut i = 0;\nlet mut j = 0;\nwhile i < n {\n    if starts[i] < ends[j] { rooms += 1; i += 1; if rooms > best { best = rooms; } }\n    else { rooms -= 1; j += 1; }\n}\nlet result: i32 = best;",
    "swift": "let n = a.count\nlet starts = a.sorted()\nlet ends = b.sorted()\nvar rooms = 0\nvar best = 0\nvar i = 0\nvar j = 0\nwhile i < n {\n    if starts[i] < ends[j] { rooms += 1; i += 1; if rooms > best { best = rooms } }\n    else { rooms -= 1; j += 1 }\n}\nlet result = best",
})


if __name__ == "__main__":
    sys.exit(asyncio.run(sh.main()))
