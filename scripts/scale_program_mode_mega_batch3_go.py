"""Program Mode expansion, mega batch 3: ports mega_batch1.py's 36 problems
(all of which use only the 5 simplest shapes: arr1, arr1_int, int1, int2,
int3) to Go -- the highest-leverage newer-language target since the
toolchain is confirmed working this session (see
project_atlascode_toolchain_env memory) and the algorithms are already
proven correct in 8 other languages; this is pure syntax translation, not
new algorithm design.

Go is strict about unused imports (compile error, not a warning), so the
harness fixes on exactly {fmt, io, os, strconv, strings} for every program
and every body avoids the `sort`/`math` packages in favor of manual loops
(mirrors the style already used for the C bodies in mega_batch1.py).
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))
import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.submission.evaluator import evaluate
import atlascode_ledger as ledger

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "atlas.db"
LANGS = ["go"]


def sig(shape, fn, kind):
    rt = "int64" if kind == "int" else "bool"
    if shape == "arr1":
        return f"func {fn}(nums []int) {rt} {{"
    if shape == "arr1_int":
        return f"func {fn}(nums []int, extra int) {rt} {{"
    if shape == "int1":
        return f"func {fn}(n int64) {rt} {{"
    if shape == "int2":
        return f"func {fn}(a int64, b int64) {rt} {{"
    if shape == "int3":
        return f"func {fn}(a int64, b int64, c int64) {rt} {{"
    raise ValueError(shape)


def read_code(shape):
    if shape == "arr1":
        return ("data, _ := io.ReadAll(os.Stdin)\n"
                 "fields := strings.Fields(string(data))\n"
                 "n, _ := strconv.Atoi(fields[0])\n"
                 "nums := make([]int, n)\n"
                 "for i := 0; i < n; i++ { nums[i], _ = strconv.Atoi(fields[1+i]) }")
    if shape == "arr1_int":
        return read_code("arr1") + "\nextra, _ := strconv.Atoi(fields[1+n])"
    if shape == "int1":
        return ("data, _ := io.ReadAll(os.Stdin)\n"
                 "n, _ := strconv.ParseInt(strings.TrimSpace(string(data)), 10, 64)")
    if shape == "int2":
        return ("data, _ := io.ReadAll(os.Stdin)\n"
                 "fields := strings.Fields(string(data))\n"
                 "a, _ := strconv.ParseInt(fields[0], 10, 64)\n"
                 "b, _ := strconv.ParseInt(fields[1], 10, 64)")
    if shape == "int3":
        return ("data, _ := io.ReadAll(os.Stdin)\n"
                 "fields := strings.Fields(string(data))\n"
                 "a, _ := strconv.ParseInt(fields[0], 10, 64)\n"
                 "b, _ := strconv.ParseInt(fields[1], 10, 64)\n"
                 "c, _ := strconv.ParseInt(fields[2], 10, 64)")
    raise ValueError(shape)


def call_args(shape):
    if shape == "arr1": return "nums"
    if shape == "arr1_int": return "nums, extra"
    if shape == "int1": return "n"
    if shape == "int2": return "a, b"
    if shape == "int3": return "a, b, c"
    raise ValueError(shape)


def print_stmt(kind, wrong):
    if kind == "int":
        delta = 1 if wrong else 0
        return f"fmt.Println(result + {delta})"
    neg = "!" if wrong else ""
    return f"fmt.Println({neg}result)"


def assemble(shape, fn, kind, body, wrong):
    read = read_code(shape)
    signature = sig(shape, fn, kind)
    args = call_args(shape)
    func = f"{signature}\n{body}\nreturn result\n}}"
    call = f"result := {fn}({args})"
    p = print_stmt(kind, wrong)
    return (
        "package main\n\n"
        "import (\n\t\"fmt\"\n\t\"io\"\n\t\"os\"\n\t\"strconv\"\n\t\"strings\"\n)\n\n"
        f"{func}\n\n"
        "func main() {\n"
        f"{read}\n{call}\n{p}\n"
        "}\n"
    )


PROBLEMS: dict[str, dict] = {}


def add(pid, shape, fn, kind, body):
    PROBLEMS[pid] = {"shape": shape, "fn": fn, "kind": kind, "body": body}


add("bitonic-peak-index", "arr1", "peakIndex", "int",
    "lo, hi := 0, len(nums)-1\nfor lo < hi { mid := (lo + hi) / 2; if nums[mid] < nums[mid+1] { lo = mid + 1 } else { hi = mid } }\nresult := int64(lo)")

add("find-minimum-rotated-sorted-array", "arr1", "findMin", "int",
    "lo, hi := 0, len(nums)-1\nfor lo < hi { mid := (lo + hi) / 2; if nums[mid] > nums[hi] { lo = mid + 1 } else { hi = mid } }\nresult := int64(nums[lo])")

add("count-occurrences-sorted", "arr1_int", "countOccurrences", "int",
    "var result int64 = 0\nfor _, x := range nums { if x == extra { result++ } }")

add("last-occurrence", "arr1_int", "lastOccurrence", "int",
    "lo, hi, ans := 0, len(nums)-1, -1\nfor lo <= hi { mid := (lo + hi) / 2; if nums[mid] == extra { ans = mid; lo = mid + 1 } else if nums[mid] < extra { lo = mid + 1 } else { hi = mid - 1 } }\nresult := int64(ans)")

add("koko-eating-bananas", "arr1_int", "minEatingSpeed", "int",
    ("hiV := 0\nfor _, p := range nums { if p > hiV { hiV = p } }\n"
     "var lo, hi int64 = 1, int64(hiV)\n"
     "for lo < hi {\n"
     "  mid := (lo + hi) / 2\n"
     "  var h int64 = 0\n"
     "  for _, p := range nums { h += (int64(p) + mid - 1) / mid }\n"
     "  if h <= int64(extra) { hi = mid } else { lo = mid + 1 }\n"
     "}\nresult := lo"))

add("kth-largest-element", "arr1_int", "kthLargest", "int",
    ("s := make([]int, len(nums)); copy(s, nums)\n"
     "for i := 0; i < len(s); i++ { for j := 0; j < len(s)-i-1; j++ { if s[j] > s[j+1] { s[j], s[j+1] = s[j+1], s[j] } } }\n"
     "result := int64(s[len(s)-extra])"))

add("largest-rectangle-in-histogram", "arr1", "largestRectangle", "int",
    ("h := make([]int, len(nums)+1); copy(h, nums); h[len(nums)] = 0\n"
     "st := make([]int, 0, len(h)+1)\n"
     "var best int64 = 0\n"
     "for i := 0; i < len(h); i++ {\n"
     "  for len(st) > 0 && h[st[len(st)-1]] >= h[i] {\n"
     "    top := st[len(st)-1]; st = st[:len(st)-1]\n"
     "    width := i\n"
     "    if len(st) > 0 { width = i - st[len(st)-1] - 1 }\n"
     "    area := int64(h[top]) * int64(width)\n"
     "    if area > best { best = area }\n"
     "  }\n"
     "  st = append(st, i)\n"
     "}\nresult := best"))

add("longest-bitonic-subsequence", "arr1", "longestBitonicSubsequence", "int",
    ("m := len(nums)\ninc := make([]int64, m); dec := make([]int64, m)\n"
     "for i := 0; i < m; i++ { inc[i] = 1; dec[i] = 1 }\n"
     "for i := 0; i < m; i++ { for j := 0; j < i; j++ { if nums[j] < nums[i] && inc[j]+1 > inc[i] { inc[i] = inc[j] + 1 } } }\n"
     "for i := m - 1; i >= 0; i-- { for j := m - 1; j > i; j-- { if nums[j] < nums[i] && dec[j]+1 > dec[i] { dec[i] = dec[j] + 1 } } }\n"
     "var best int64 = 0\nfor i := 0; i < m; i++ { v := inc[i] + dec[i] - 1; if v > best { best = v } }\nresult := best"))

add("max-consecutive-ones-with-k-flips", "arr1_int", "maxConsecutiveOnes", "int",
    ("left, zeros, best := 0, 0, 0\n"
     "for right := 0; right < len(nums); right++ {\n"
     "  if nums[right] == 0 { zeros++ }\n"
     "  for zeros > extra { if nums[left] == 0 { zeros-- }; left++ }\n"
     "  if right-left+1 > best { best = right - left + 1 }\n"
     "}\nresult := int64(best)"))

add("max-sum-subarray-fixed-k", "arr1_int", "maxSumFixedK", "int",
    ("var sum int64 = 0\nfor i := 0; i < extra; i++ { sum += int64(nums[i]) }\n"
     "best := sum\n"
     "for i := extra; i < len(nums); i++ { sum += int64(nums[i]) - int64(nums[i-extra]); if sum > best { best = sum } }\n"
     "result := best"))

add("maximum-subarray-circular", "arr1", "maxSubarrayCircular", "int",
    ("var total, maxCur, minCur int64 = 0, 0, 0\n"
     "maxBest := int64(-1) << 62\nminBest := int64(1) << 62\n"
     "for _, xx := range nums {\n"
     "  x := int64(xx)\n"
     "  total += x\n"
     "  if x > maxCur+x { maxCur = x } else { maxCur = maxCur + x }\n"
     "  if maxCur > maxBest { maxBest = maxCur }\n"
     "  if x < minCur+x { minCur = x } else { minCur = minCur + x }\n"
     "  if minCur < minBest { minBest = minCur }\n"
     "}\n"
     "var result int64\n"
     "if maxBest < 0 { result = maxBest } else if maxBest > total-minBest { result = maxBest } else { result = total - minBest }"))

add("maximum-xor-of-two-numbers", "arr1", "findMaximumXor", "int",
    ("var best int64 = 0\n"
     "for i := 0; i < len(nums); i++ { for j := i + 1; j < len(nums); j++ { v := int64(nums[i] ^ nums[j]); if v > best { best = v } } }\n"
     "result := best"))

add("middle-of-linked-list", "arr1", "middleNode", "int",
    "slow, fast, m := 0, 0, len(nums)\nfor fast < m-1 { slow++; fast += 2 }\nresult := int64(nums[slow])")

add("min-subarray-len-target-sum", "arr1_int", "minSubarrayLen", "int",
    ("left := 0\nvar sum int64 = 0\nbest := int64(1) << 62\n"
     "for right := 0; right < len(nums); right++ {\n"
     "  sum += int64(nums[right])\n"
     "  for sum >= int64(extra) {\n"
     "    if int64(right-left+1) < best { best = int64(right - left + 1) }\n"
     "    sum -= int64(nums[left]); left++\n"
     "  }\n"
     "}\nvar result int64\nif best == int64(1)<<62 { result = 0 } else { result = best }"))

add("partition-equal-subset-sum", "arr1", "canPartition", "bool",
    ("var total int64 = 0\nfor _, x := range nums { total += int64(x) }\n"
     "var result bool\n"
     "if total%2 != 0 {\n"
     "  result = false\n"
     "} else {\n"
     "  target := int(total / 2)\n"
     "  dp := make([]bool, target+1); dp[0] = true\n"
     "  for _, x := range nums { for j := target; j >= x; j-- { if dp[j-x] { dp[j] = true } } }\n"
     "  result = dp[target]\n"
     "}"))

add("perfect-squares-min-count", "int1", "numSquares", "int",
    ("N := int(n)\ndp := make([]int64, N+1)\nfor i := 1; i <= N; i++ { dp[i] = int64(1) << 40 }\n"
     "for i := 1; i <= N; i++ { for j := 1; j*j <= i; j++ { if dp[i-j*j]+1 < dp[i] { dp[i] = dp[i-j*j] + 1 } } }\n"
     "result := dp[N]"))

add("rod-cutting", "arr1", "rodCutting", "int",
    ("m := len(nums)\ndp := make([]int64, m+1)\n"
     "for i := 1; i <= m; i++ {\n"
     "  best := int64(-1) << 62\n"
     "  for cut := 1; cut <= i; cut++ { v := int64(nums[cut-1]) + dp[i-cut]; if v > best { best = v } }\n"
     "  dp[i] = best\n"
     "}\nresult := dp[m]"))

add("single-number-ii", "arr1", "singleNumber", "int",
    ("var result int64 = 0\n"
     "for bit := 0; bit < 32; bit++ {\n"
     "  var cnt int64 = 0\n"
     "  for _, x := range nums {\n"
     "    var ux int64\n"
     "    if x < 0 { ux = int64(x) + 4294967296 } else { ux = int64(x) }\n"
     "    cnt += (ux >> uint(bit)) & 1\n"
     "  }\n"
     "  if cnt%3 != 0 { result += int64(1) << uint(bit) }\n"
     "}\nif result >= 2147483648 { result -= 4294967296 }"))

add("subset-sum", "arr1_int", "subsetSum", "bool",
    ("dp := make([]bool, extra+1); dp[0] = true\n"
     "for _, x := range nums { if x <= extra { for j := extra; j >= x; j-- { if dp[j-x] { dp[j] = true } } } }\n"
     "var result bool\nif extra >= 0 { result = dp[extra] } else { result = false }"))

add("target-sum-ways", "arr1_int", "findTargetSumWays", "int",
    ("var total int64 = 0\nfor _, x := range nums { total += int64(x) }\n"
     "e := int64(extra)\nabsE := e\nif absE < 0 { absE = -absE }\n"
     "var result int64\n"
     "if (total+e)%2 != 0 || total < absE {\n"
     "  result = 0\n"
     "} else {\n"
     "  s := int((total + e) / 2)\n"
     "  dp := make([]int64, s+1); dp[0] = 1\n"
     "  for _, x := range nums { for j := s; j >= x; j-- { dp[j] += dp[j-x] } }\n"
     "  result = dp[s]\n"
     "}"))

add("two-sum-count-pairs", "arr1_int", "countPairs", "int",
    ("freq := make(map[int]int64)\nfor _, x := range nums { freq[x]++ }\n"
     "var result int64 = 0\n"
     "for v, c := range freq {\n"
     "  comp := extra - v\n"
     "  if comp == v { result += c * (c - 1) / 2 } else if comp > v { result += c * freq[comp] }\n"
     "}"))

add("unique-permutations-count", "arr1", "countUniquePermutations", "int",
    ("freq := make(map[int]int64)\nfor _, x := range nums { freq[x]++ }\n"
     "var num int64 = 1\nfor i := int64(2); i <= int64(len(nums)); i++ { num *= i }\n"
     "var denom int64 = 1\n"
     "for _, c := range freq { var f int64 = 1; for i := int64(2); i <= c; i++ { f *= i }; denom *= f }\n"
     "result := num / denom"))

add("ship-packages-within-days", "arr1_int", "shipWithinDays", "int",
    ("var hiV, maxV int64 = 0, 0\nfor _, w := range nums { hiV += int64(w); if int64(w) > maxV { maxV = int64(w) } }\n"
     "lo := maxV\nhi := hiV\n"
     "for lo < hi {\n"
     "  mid := (lo + hi) / 2\n"
     "  var days, cur int64 = 1, 0\n"
     "  for _, w := range nums { if cur+int64(w) > mid { days++; cur = int64(w) } else { cur += int64(w) } }\n"
     "  if days <= int64(extra) { hi = mid } else { lo = mid + 1 }\n"
     "}\nresult := lo"))

add("subarray-product-less-than-k", "arr1_int", "numSubarrayProductLessThanK", "int",
    ("var result int64\n"
     "if extra <= 1 {\n"
     "  result = 0\n"
     "} else {\n"
     "  left := 0\n"
     "  var prod, count int64 = 1, 0\n"
     "  for right := 0; right < len(nums); right++ {\n"
     "    prod *= int64(nums[right])\n"
     "    for prod >= int64(extra) { prod /= int64(nums[left]); left++ }\n"
     "    count += int64(right - left + 1)\n"
     "  }\n"
     "  result = count\n"
     "}"))

add("subarray-sums-divisible-by-k", "arr1_int", "subarraysDivByK", "int",
    ("seen := make(map[int64]int64)\nseen[0] = 1\n"
     "var sum, count int64 = 0, 0\n"
     "for _, x := range nums {\n"
     "  sum += int64(x)\n"
     "  r := ((sum % int64(extra)) + int64(extra)) % int64(extra)\n"
     "  count += seen[r]\n"
     "  seen[r]++\n"
     "}\nresult := count"))

add("euler-phi-sieve", "int1", "eulerPhiSieve", "int",
    ("N := n\nresult := N\nnum := N\n"
     "for p := int64(2); p*p <= num; p++ {\n"
     "  if num%p == 0 {\n"
     "    for num%p == 0 { num /= p }\n"
     "    result -= result / p\n"
     "  }\n"
     "}\nif num > 1 { result -= result / num }"))

add("integer-square-root", "int1", "mySqrt", "int",
    "lo, hi := int64(0), n\nfor lo < hi { mid := (lo + hi + 1) / 2; if mid*mid <= n { lo = mid } else { hi = mid - 1 } }\nresult := lo")

add("miller-rabin", "int1", "millerRabin", "bool",
    ("var result bool\n"
     "if n < 2 {\n"
     "  result = false\n"
     "} else {\n"
     "  result = true\n"
     "  for i := int64(2); i*i <= n; i++ { if n%i == 0 { result = false; break } }\n"
     "}"))

add("number-of-divisors", "int1", "numberOfDivisors", "int",
    ("var count int64 = 0\n"
     "for i := int64(1); i*i <= n; i++ { if n%i == 0 { if i*i == n { count++ } else { count += 2 } } }\n"
     "result := count"))

add("palindrome-linked-list", "arr1", "isPalindrome", "bool",
    "lo, hi := 0, len(nums)-1\nresult := true\nfor lo < hi { if nums[lo] != nums[hi] { result = false; break }; lo++; hi-- }")

add("delete-and-earn", "arr1", "deleteAndEarn", "int",
    ("maxV := 0\nfor _, x := range nums { if x > maxV { maxV = x } }\n"
     "points := make([]int64, maxV+1)\nfor _, x := range nums { points[x] += int64(x) }\n"
     "var prev2, prev1 int64 = 0, 0\n"
     "for _, p := range points { cur := prev1; if prev2+p > cur { cur = prev2 + p }; prev2 = prev1; prev1 = cur }\n"
     "result := prev1"))

add("jump-game-ii-min-jumps", "arr1", "jump", "int",
    ("jumps, curEnd, farthest := 0, 0, 0\n"
     "for i := 0; i < len(nums)-1; i++ {\n"
     "  if i+nums[i] > farthest { farthest = i + nums[i] }\n"
     "  if i == curEnd { jumps++; curEnd = farthest }\n"
     "}\nresult := int64(jumps)"))

add("linked-list-cycle-detect", "arr1_int", "hasCycle", "bool",
    "result := extra != -1")

add("lucas-theorem", "int3", "lucasTheorem", "int",
    ("var powMod func(base, exp, mod int64) int64\n"
     "powMod = func(base, exp, mod int64) int64 {\n"
     "  base = base % mod\n"
     "  var r int64 = 1\n"
     "  for exp > 0 { if exp%2 == 1 { r = r * base % mod }; base = base * base % mod; exp /= 2 }\n"
     "  return r\n"
     "}\n"
     "var smallC func(nn, kk, pp int64) int64\n"
     "smallC = func(nn, kk, pp int64) int64 {\n"
     "  if kk < 0 || kk > nn { return 0 }\n"
     "  var num int64 = 1\n"
     "  for i := nn - kk + 1; i <= nn; i++ { num = num * (i % pp) % pp }\n"
     "  var den int64 = 1\n"
     "  for i := int64(1); i <= kk; i++ { den = den * i % pp }\n"
     "  return num * powMod(den, pp-2, pp) % pp\n"
     "}\n"
     "var lucas func(nn, kk, pp int64) int64\n"
     "lucas = func(nn, kk, pp int64) int64 {\n"
     "  if kk == 0 { return 1 % pp }\n"
     "  ni, ki := nn%pp, kk%pp\n"
     "  return smallC(ni, ki, pp) * lucas(nn/pp, kk/pp, pp) % pp\n"
     "}\n"
     "result := lucas(a, b, c)"))

add("modular-exponentiation", "int3", "modularExponentiation", "int",
    ("base := a % c\nexp := b\nmod := c\nvar r int64 = 1 % mod\n"
     "for exp > 0 { if exp%2 == 1 { r = r * base % mod }; base = base * base % mod; exp /= 2 }\n"
     "result := r"))

add("minimum-knight-moves", "int2", "minKnightMoves", "int",
    ("tx, ty := a, b\nif tx < 0 { tx = -tx }\nif ty < 0 { ty = -ty }\n"
     "type pt struct{ x, y, d int64 }\n"
     "q := []pt{{0, 0, 0}}\n"
     "visited := make(map[[2]int64]bool)\n"
     "visited[[2]int64{0, 0}] = true\n"
     "dirs := [8][2]int64{{1, 2}, {2, 1}, {-1, 2}, {-2, 1}, {1, -2}, {2, -1}, {-1, -2}, {-2, -1}}\n"
     "var ans int64 = 0\n"
     "for len(q) > 0 {\n"
     "  cur := q[0]; q = q[1:]\n"
     "  if cur.x == tx && cur.y == ty { ans = cur.d; break }\n"
     "  for _, dir := range dirs {\n"
     "    nx, ny := cur.x+dir[0], cur.y+dir[1]\n"
     "    if nx >= -2 && ny >= -2 && nx <= tx+2 && ny <= ty+2 {\n"
     "      key := [2]int64{nx, ny}\n"
     "      if !visited[key] { visited[key] = true; q = append(q, pt{nx, ny, cur.d + 1}) }\n"
     "    }\n"
     "  }\n"
     "}\nresult := ans"))


@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


def build_program(pid, wrong):
    spec = PROBLEMS[pid]
    return assemble(spec["shape"], spec["fn"], spec["kind"], spec["body"], wrong)


def load_cases(con, pid):
    cur = con.execute(
        "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = [SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                         is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
    row = con.execute("SELECT test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    return cases, row["test_suite_version"]


async def verify_one(pid, cases):
    t0 = time.monotonic()
    correct_result = await evaluate(build_program(pid, False), "go", cases)
    if correct_result.tests_passed != correct_result.tests_total:
        extra = correct_result.compile_output or ""
        if not extra and correct_result.test_results:
            for tr in correct_result.test_results:
                if not tr.passed:
                    extra = f"verdict={tr.verdict} stderr={tr.stderr[:150]} actual={tr.actual_output[:60]!r} expected={tr.expected_output[:60]!r}"
                    break
        return {"pid": pid, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict} {extra[:200]}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate(build_program(pid, True), "go", cases)
    if wrong_result.tests_passed >= wrong_result.tests_total:
        return {"pid": pid, "outcome": "corpus_weakness", "detail": "wrong solution still passed all cases",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "outcome": "verified",
            "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} correct, "
                      f"wrong rejected on {wrong_result.tests_total - wrong_result.tests_passed}/{wrong_result.tests_total}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)

    results = []
    for pid in PROBLEMS:
        cases, tsv = load_cases(con, pid)
        if ledger.already_verified(con, pid, "go", "program", test_suite_version=tsv):
            print(f"[SKIP] {pid}/go already verified")
            continue
        r = await verify_one(pid, cases)
        results.append(r)
        status = "PASS" if r["outcome"] == "verified" else "FAIL"
        print(f"[{status}] go(program) {pid:38s} {r['outcome']:18s} {r['detail'][:140]}", flush=True)
        if r["outcome"] == "verified":
            row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
            sc = json.loads(row["starter_code"])
            sc["go"] = build_program(pid, False)
            con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
            con.commit()
            ledger.record_cell(
                con, problem_id=pid, language="go", mode="program",
                verification_level=ledger.LEVEL_VERIFIED, status="pass",
                adapter_version="program-mega-batch3-go-v1", test_suite_version=tsv,
                duration_ms=r["duration_ms"],
            )

    verified = [r for r in results if r["outcome"] == "verified"]
    failed = [r for r in results if r["outcome"] != "verified"]
    print(f"\nTOTAL: {len(results)}  verified={len(verified)}  failed={len(failed)}")
    if failed:
        print("\nFAILED CELLS:")
        for r in failed:
            print(f"  {r['pid']}: {r['outcome']} -- {r['detail'][:160]}")
    con.close()
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
