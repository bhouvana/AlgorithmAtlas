"""Scales Function Mode coverage for 16 already-proven "core" problems
(ladder-gap, gcd/house-robber, dp-string, graph-grid clusters) across the
6 newly-confirmed languages: go, kotlin, ruby, php, r, scala. Reuses the
exact algorithms already proven correct in the 8-language versions earlier
this session -- only syntax translation, no new algorithm design.
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
_TARGET_LANGUAGES = ["go", "kotlin", "ruby", "php", "r", "scala"]


# ── two-sum (first-index-wins duplicate semantics, sorted-comparator output) ─
def _go_twosum(wrong):
    a = " + 1" if wrong else ""
    return (f"func two_sum(nums []int, target int) []int {{\n"
            f"\tseen := map[int]int{{}}\n"
            f"\tfor i, x := range nums {{\n"
            f"\t\tif j, ok := seen[target-x]; ok {{\n"
            f"\t\t\treturn []int{{j, i{a}}}\n"
            f"\t\t}}\n"
            f"\t\tif _, exists := seen[x]; !exists {{\n"
            f"\t\t\tseen[x] = i\n"
            f"\t\t}}\n"
            f"\t}}\n"
            f"\treturn []int{{}}\n"
            f"}}\n")


def _kotlin_twosum(wrong):
    a = " + 1" if wrong else ""
    return (f"fun two_sum(nums: List<Int>, target: Int): List<Int> {{\n"
            f"    val seen = HashMap<Int, Int>()\n"
            f"    for (i in nums.indices) {{\n"
            f"        val x = nums[i]\n"
            f"        val need = target - x\n"
            f"        if (seen.containsKey(need)) return listOf(seen[need]!!, i{a})\n"
            f"        if (!seen.containsKey(x)) seen[x] = i\n"
            f"    }}\n"
            f"    return listOf()\n"
            f"}}\n")


def _scala_twosum(wrong):
    a = " + 1" if wrong else ""
    return (f"def two_sum(nums: List[Int], target: Int): List[Int] = {{\n"
            f"  val seen = scala.collection.mutable.HashMap[Int, Int]()\n"
            f"  for (i <- nums.indices) {{\n"
            f"    val x = nums(i)\n"
            f"    val need = target - x\n"
            f"    if (seen.contains(need)) return List(seen(need), i{a})\n"
            f"    if (!seen.contains(x)) seen(x) = i\n"
            f"  }}\n"
            f"  List()\n"
            f"}}\n")


def _ruby_twosum(wrong):
    a = " + 1" if wrong else ""
    return (f"def two_sum(nums, target)\n"
            f"  seen = {{}}\n"
            f"  nums.each_with_index do |x, i|\n"
            f"    need = target - x\n"
            f"    return [seen[need], i{a}] if seen.key?(need)\n"
            f"    seen[x] = i unless seen.key?(x)\n"
            f"  end\n"
            f"  []\n"
            f"end\n")


def _php_twosum(wrong):
    a = " + 1" if wrong else ""
    return (f"function two_sum($nums, $target) {{\n"
            f"    $seen = [];\n"
            f"    foreach ($nums as $i => $x) {{\n"
            f"        $need = $target - $x;\n"
            f"        if (array_key_exists($need, $seen)) return [$seen[$need], $i{a}];\n"
            f"        if (!array_key_exists($x, $seen)) $seen[$x] = $i;\n"
            f"    }}\n"
            f"    return [];\n"
            f"}}\n")


def _r_twosum(wrong):
    a = " + 1" if wrong else ""
    return (f"two_sum <- function(nums, target) {{\n"
            f"  seen <- new.env()\n"
            f"  n <- length(nums)\n"
            f"  for (i in 1:n) {{\n"
            f"    x <- nums[[i]]\n"
            f"    need <- as.character(target - x)\n"
            f"    if (exists(need, envir = seen, inherits = FALSE)) {{\n"
            f"      j <- get(need, envir = seen)\n"
            f"      return(list(j - 1, i - 1{a}))\n"
            f"    }}\n"
            f"    key <- as.character(x)\n"
            f"    if (!exists(key, envir = seen, inherits = FALSE)) assign(key, i, envir = seen)\n"
            f"  }}\n"
            f"  return(list())\n"
            f"}}\n")


# ── maximum-subarray (Kadane) ─────────────────────────────────────────────
def _go_maxsub(wrong):
    a = " + 1" if wrong else ""
    return (f"func max_subarray(nums []int) int {{\n"
            f"\tbest, cur := nums[0], nums[0]\n"
            f"\tfor i := 1; i < len(nums); i++ {{\n"
            f"\t\tif cur+nums[i] > nums[i] {{ cur = cur + nums[i] }} else {{ cur = nums[i] }}\n"
            f"\t\tif cur > best {{ best = cur }}\n"
            f"\t}}\n"
            f"\treturn best{a}\n"
            f"}}\n")


def _kotlin_maxsub(wrong):
    a = " + 1" if wrong else ""
    return (f"fun max_subarray(nums: List<Int>): Int {{\n"
            f"    var best = nums[0]; var cur = nums[0]\n"
            f"    for (i in 1 until nums.size) {{\n"
            f"        cur = maxOf(cur + nums[i], nums[i])\n"
            f"        best = maxOf(best, cur)\n"
            f"    }}\n"
            f"    return best{a}\n"
            f"}}\n")


def _scala_maxsub(wrong):
    a = " + 1" if wrong else ""
    return (f"def max_subarray(nums: List[Int]): Int = {{\n"
            f"  var best = nums(0); var cur = nums(0)\n"
            f"  for (i <- 1 until nums.length) {{\n"
            f"    cur = math.max(cur + nums(i), nums(i))\n"
            f"    best = math.max(best, cur)\n"
            f"  }}\n"
            f"  best{a}\n"
            f"}}\n")


def _ruby_maxsub(wrong):
    a = " + 1" if wrong else ""
    return (f"def max_subarray(nums)\n"
            f"  best = nums[0]; cur = nums[0]\n"
            f"  (1...nums.length).each do |i|\n"
            f"    cur = [cur + nums[i], nums[i]].max\n"
            f"    best = [best, cur].max\n"
            f"  end\n"
            f"  best{a}\n"
            f"end\n")


def _php_maxsub(wrong):
    a = " + 1" if wrong else ""
    return (f"function max_subarray($nums) {{\n"
            f"    $best = $nums[0]; $cur = $nums[0];\n"
            f"    for ($i=1; $i<count($nums); $i++) {{\n"
            f"        $cur = max($cur + $nums[$i], $nums[$i]);\n"
            f"        $best = max($best, $cur);\n"
            f"    }}\n"
            f"    return $best{a};\n"
            f"}}\n")


def _r_maxsub(wrong):
    a = " + 1" if wrong else ""
    return (f"max_subarray <- function(nums) {{\n"
            f"  best <- nums[[1]]; cur <- nums[[1]]\n"
            f"  n <- length(nums)\n"
            f"  if (n > 1) {{\n"
            f"    for (i in 2:n) {{\n"
            f"      cur <- max(cur + nums[[i]], nums[[i]])\n"
            f"      best <- max(best, cur)\n"
            f"    }}\n"
            f"  }}\n"
            f"  return(best{a})\n"
            f"}}\n")


# ── prime-factorization (returns STRING, format: "p1^e1 * p2^e2 ...") ──────
# NOTE: exact string format confirmed via existing proven 8-language impl
# before porting -- see scale_ladder_gap_closure.py's already-verified
# javascript/typescript builders.
def _go_primefact(wrong):
    a = ' + "x"' if wrong else ""
    return (f"func prime_factorization(n int) string {{\n"
            f"\tparts := []string{{}}\n"
            f"\tx := n\n"
            f"\tfor p := 2; p*p <= x; p++ {{\n"
            f"\t\tif x%p == 0 {{\n"
            f"\t\t\te := 0\n"
            f"\t\t\tfor x%p == 0 {{ x /= p; e++ }}\n"
            f"\t\t\tif e == 1 {{ parts = append(parts, fmt.Sprintf(\"%d\", p)) }} else {{ parts = append(parts, fmt.Sprintf(\"%d^%d\", p, e)) }}\n"
            f"\t\t}}\n"
            f"\t}}\n"
            f"\tif x > 1 {{ parts = append(parts, fmt.Sprintf(\"%d\", x)) }}\n"
            f"\treturn strings.Join(parts, \" * \"){a}\n"
            f"}}\n")


def _kotlin_primefact(wrong):
    a = ' + "x"' if wrong else ""
    return (f"fun prime_factorization(n: Int): String {{\n"
            f"    val parts = mutableListOf<String>()\n"
            f"    var x = n; var p = 2\n"
            f"    while (p * p <= x) {{\n"
            f"        if (x % p == 0) {{\n"
            f"            var e = 0\n"
            f"            while (x % p == 0) {{ x /= p; e++ }}\n"
            f"            parts.add(if (e == 1) \"$p\" else \"$p^$e\")\n"
            f"        }}\n"
            f"        p++\n"
            f"    }}\n"
            f"    if (x > 1) parts.add(\"$x\")\n"
            f"    return parts.joinToString(\" * \"){a}\n"
            f"}}\n")


def _scala_primefact(wrong):
    a = ' + "x"' if wrong else ""
    return (f"def prime_factorization(n: Int): String = {{\n"
            f"  val parts = scala.collection.mutable.ListBuffer[String]()\n"
            f"  var x = n; var p = 2\n"
            f"  while (p * p <= x) {{\n"
            f"    if (x % p == 0) {{\n"
            f"      var e = 0\n"
            f"      while (x % p == 0) {{ x /= p; e += 1 }}\n"
            f"      parts += (if (e == 1) s\"$p\" else s\"$p^$e\")\n"
            f"    }}\n"
            f"    p += 1\n"
            f"  }}\n"
            f"  if (x > 1) parts += s\"$x\"\n"
            f"  parts.mkString(\" * \"){a}\n"
            f"}}\n")


def _ruby_primefact(wrong):
    a = ' + "x"' if wrong else ""
    return (f"def prime_factorization(n)\n"
            f"  parts = []\n"
            f"  x = n; p = 2\n"
            f"  while p * p <= x\n"
            f"    if x % p == 0\n"
            f"      e = 0\n"
            f"      while x % p == 0\n"
            f"        x /= p; e += 1\n"
            f"      end\n"
            f"      parts << (e == 1 ? \"#{{p}}\" : \"#{{p}}^#{{e}}\")\n"
            f"    end\n"
            f"    p += 1\n"
            f"  end\n"
            f"  parts << \"#{{x}}\" if x > 1\n"
            f"  parts.join(' * '){a}\n"
            f"end\n")


def _php_primefact(wrong):
    a = ' . "x"' if wrong else ""
    return (f"function prime_factorization($n) {{\n"
            f"    $parts = [];\n"
            f"    $x = $n; $p = 2;\n"
            f"    while ($p * $p <= $x) {{\n"
            f"        if ($x % $p == 0) {{\n"
            f"            $e = 0;\n"
            f"            while ($x % $p == 0) {{ $x = intdiv($x, $p); $e++; }}\n"
            f"            $parts[] = ($e == 1) ? \"$p\" : \"$p^$e\";\n"
            f"        }}\n"
            f"        $p++;\n"
            f"    }}\n"
            f"    if ($x > 1) $parts[] = \"$x\";\n"
            f"    return implode(' * ', $parts){a};\n"
            f"}}\n")


def _r_primefact(wrong):
    a = ' , "x", sep=""' if wrong else ""
    prefix = "paste0(" if wrong else ""
    suffix = ")" if wrong else ""
    return (f"prime_factorization <- function(n) {{\n"
            f"  parts <- c()\n"
            f"  x <- n; p <- 2\n"
            f"  while (p * p <= x) {{\n"
            f"    if (x %% p == 0) {{\n"
            f"      e <- 0\n"
            f"      while (x %% p == 0) {{ x <- x %/% p; e <- e + 1 }}\n"
            f"      parts <- c(parts, if (e == 1) paste0(p) else paste0(p, \"^\", e))\n"
            f"    }}\n"
            f"    p <- p + 1\n"
            f"  }}\n"
            f"  if (x > 1) parts <- c(parts, paste0(x))\n"
            f"  return({prefix}paste(parts, collapse=' * '){suffix}{a})\n"
            f"}}\n")


# ── contains-duplicate-within-k (sliding window index set) ─────────────────
def _go_dupwithink(wrong):
    ret = "false" if wrong else "true"
    return (f"func contains_nearby_duplicate(nums []int, k int) bool {{\n"
            f"\tseen := map[int]int{{}}\n"
            f"\tfor i, x := range nums {{\n"
            f"\t\tif j, ok := seen[x]; ok && i-j <= k {{\n"
            f"\t\t\treturn {ret}\n"
            f"\t\t}}\n"
            f"\t\tseen[x] = i\n"
            f"\t}}\n"
            f"\treturn false\n"
            f"}}\n")


def _kotlin_dupwithink(wrong):
    ret = "false" if wrong else "true"
    return (f"fun contains_nearby_duplicate(nums: List<Int>, k: Int): Boolean {{\n"
            f"    val seen = HashMap<Int, Int>()\n"
            f"    for (i in nums.indices) {{\n"
            f"        val x = nums[i]\n"
            f"        if (seen.containsKey(x) && i - seen[x]!! <= k) return {ret}\n"
            f"        seen[x] = i\n"
            f"    }}\n"
            f"    return false\n"
            f"}}\n")


def _scala_dupwithink(wrong):
    ret = "false" if wrong else "true"
    return (f"def contains_nearby_duplicate(nums: List[Int], k: Int): Boolean = {{\n"
            f"  val seen = scala.collection.mutable.HashMap[Int, Int]()\n"
            f"  for (i <- nums.indices) {{\n"
            f"    val x = nums(i)\n"
            f"    if (seen.contains(x) && i - seen(x) <= k) return {ret}\n"
            f"    seen(x) = i\n"
            f"  }}\n"
            f"  false\n"
            f"}}\n")


def _ruby_dupwithink(wrong):
    ret = "false" if wrong else "true"
    return (f"def contains_nearby_duplicate(nums, k)\n"
            f"  seen = {{}}\n"
            f"  nums.each_with_index do |x, i|\n"
            f"    return {ret} if seen.key?(x) && (i - seen[x]) <= k\n"
            f"    seen[x] = i\n"
            f"  end\n"
            f"  false\n"
            f"end\n")


def _php_dupwithink(wrong):
    ret = "false" if wrong else "true"
    return (f"function contains_nearby_duplicate($nums, $k) {{\n"
            f"    $seen = [];\n"
            f"    foreach ($nums as $i => $x) {{\n"
            f"        if (array_key_exists($x, $seen) && ($i - $seen[$x]) <= $k) return {ret};\n"
            f"        $seen[$x] = $i;\n"
            f"    }}\n"
            f"    return false;\n"
            f"}}\n")


def _r_dupwithink(wrong):
    ret = "FALSE" if wrong else "TRUE"
    return (f"contains_nearby_duplicate <- function(nums, k) {{\n"
            f"  seen <- new.env()\n"
            f"  n <- length(nums)\n"
            f"  for (i in 1:n) {{\n"
            f"    x <- as.character(nums[[i]])\n"
            f"    if (exists(x, envir = seen, inherits = FALSE)) {{\n"
            f"      j <- get(x, envir = seen)\n"
            f"      if ((i - j) <= k) return({ret})\n"
            f"    }}\n"
            f"    assign(x, i, envir = seen)\n"
            f"  }}\n"
            f"  return(FALSE)\n"
            f"}}\n")


# ── merge-overlapping-intervals (sort by start, merge) ──────────────────────
def _go_mergeintervals(wrong):
    incr = "\n\tfor i := range out { out[i][1]++ }" if wrong else ""
    return (f"func merge_intervals(intervals [][]int) [][]int {{\n"
            f"\tsort.Slice(intervals, func(i, j int) bool {{ return intervals[i][0] < intervals[j][0] }})\n"
            f"\tout := [][]int{{}}\n"
            f"\tfor _, iv := range intervals {{\n"
            f"\t\tif len(out) > 0 && iv[0] <= out[len(out)-1][1] {{\n"
            f"\t\t\tif iv[1] > out[len(out)-1][1] {{ out[len(out)-1][1] = iv[1] }}\n"
            f"\t\t}} else {{\n"
            f"\t\t\tout = append(out, []int{{iv[0], iv[1]}})\n"
            f"\t\t}}\n"
            f"\t}}{incr}\n"
            f"\treturn out\n"
            f"}}\n")


def _kotlin_mergeintervals(wrong):
    incr = "\n    for (r in out) r[1] = r[1] + 1" if wrong else ""
    return (f"fun merge_intervals(intervals: List<MutableList<Int>>): List<MutableList<Int>> {{\n"
            f"    val sorted = intervals.sortedBy {{ it[0] }}\n"
            f"    val out = mutableListOf<MutableList<Int>>()\n"
            f"    for (iv in sorted) {{\n"
            f"        if (out.isNotEmpty() && iv[0] <= out.last()[1]) {{\n"
            f"            if (iv[1] > out.last()[1]) out.last()[1] = iv[1]\n"
            f"        }} else {{\n"
            f"            out.add(mutableListOf(iv[0], iv[1]))\n"
            f"        }}\n"
            f"    }}{incr}\n"
            f"    return out\n"
            f"}}\n")


def _scala_mergeintervals(wrong):
    incr = "\n  for (r <- out) r(1) = r(1) + 1" if wrong else ""
    return (f"def merge_intervals(intervals: List[List[Int]]): List[List[Int]] = {{\n"
            f"  val sorted = intervals.sortBy(_(0))\n"
            f"  val out = scala.collection.mutable.ArrayBuffer[Array[Int]]()\n"
            f"  for (iv <- sorted) {{\n"
            f"    if (out.nonEmpty && iv(0) <= out.last(1)) {{\n"
            f"      if (iv(1) > out.last(1)) out.last(1) = iv(1)\n"
            f"    }} else {{\n"
            f"      out += Array(iv(0), iv(1))\n"
            f"    }}\n"
            f"  }}{incr}\n"
            f"  out.map(_.toList).toList\n"
            f"}}\n")


def _ruby_mergeintervals(wrong):
    incr = "\n  out.each { |r| r[1] += 1 }" if wrong else ""
    return (f"def merge_intervals(intervals)\n"
            f"  sorted = intervals.sort_by {{ |iv| iv[0] }}\n"
            f"  out = []\n"
            f"  sorted.each do |iv|\n"
            f"    if !out.empty? && iv[0] <= out[-1][1]\n"
            f"      out[-1][1] = iv[1] if iv[1] > out[-1][1]\n"
            f"    else\n"
            f"      out << [iv[0], iv[1]]\n"
            f"    end\n"
            f"  end{incr}\n"
            f"  out\n"
            f"end\n")


def _php_mergeintervals(wrong):
    incr = "\n    foreach ($out as &$r) { $r[1] += 1; }" if wrong else ""
    return (f"function merge_intervals($intervals) {{\n"
            f"    usort($intervals, function($a, $b) {{ return $a[0] <=> $b[0]; }});\n"
            f"    $out = [];\n"
            f"    foreach ($intervals as $iv) {{\n"
            f"        $lastIdx = count($out) - 1;\n"
            f"        if ($lastIdx >= 0 && $iv[0] <= $out[$lastIdx][1]) {{\n"
            f"            if ($iv[1] > $out[$lastIdx][1]) $out[$lastIdx][1] = $iv[1];\n"
            f"        }} else {{\n"
            f"            $out[] = [$iv[0], $iv[1]];\n"
            f"        }}\n"
            f"    }}{incr}\n"
            f"    return $out;\n"
            f"}}\n")


def _r_mergeintervals(wrong):
    incr = "\n  for (i in seq_along(out)) out[[i]][2] <- out[[i]][2] + 1" if wrong else ""
    return (f"merge_intervals <- function(intervals) {{\n"
            f"  starts <- sapply(intervals, function(iv) iv[[1]])\n"
            f"  sorted <- intervals[order(starts)]\n"
            f"  out <- list()\n"
            f"  for (iv in sorted) {{\n"
            f"    n <- length(out)\n"
            f"    if (n > 0 && iv[[1]] <= out[[n]][[2]]) {{\n"
            f"      if (iv[[2]] > out[[n]][[2]]) out[[n]][[2]] <- iv[[2]]\n"
            f"    }} else {{\n"
            f"      out[[length(out) + 1]] <- list(iv[[1]], iv[[2]])\n"
            f"    }}\n"
            f"  }}{incr}\n"
            f"  return(out)\n"
            f"}}\n")


# ── gcd-euclidean ────────────────────────────────────────────────────────────
def _go_gcd(wrong):
    a = " + 1" if wrong else ""
    return f"func gcd(a int, b int) int {{\n\tfor b != 0 {{ a, b = b, a%b }}\n\treturn a{a}\n}}\n"


def _kotlin_gcd(wrong):
    a = " + 1" if wrong else ""
    return f"fun gcd(a: Int, b: Int): Int {{\n    var x = a; var y = b\n    while (y != 0) {{ val t = y; y = x % y; x = t }}\n    return x{a}\n}}\n"


def _scala_gcd(wrong):
    a = " + 1" if wrong else ""
    return f"def gcd(a: Int, b: Int): Int = {{\n  var x = a; var y = b\n  while (y != 0) {{ val t = y; y = x % y; x = t }}\n  x{a}\n}}\n"


def _ruby_gcd(wrong):
    a = " + 1" if wrong else ""
    return f"def gcd(a, b)\n  x = a; y = b\n  while y != 0\n    x, y = y, x % y\n  end\n  x{a}\nend\n"


def _php_gcd(wrong):
    a = " + 1" if wrong else ""
    return f"function gcd($a, $b) {{\n    while ($b != 0) {{ [$a, $b] = [$b, $a % $b]; }}\n    return $a{a};\n}}\n"


def _r_gcd(wrong):
    a = " + 1" if wrong else ""
    return f"gcd <- function(a, b) {{\n  while (b != 0) {{ t <- b; b <- a %% b; a <- t }}\n  return(a{a})\n}}\n"


# ── house-robber (classic DP) ─────────────────────────────────────────────
def _go_houserobber(wrong):
    a = " + 1" if wrong else ""
    return (f"func rob(nums []int) int {{\n"
            f"\tprev, cur := 0, 0\n"
            f"\tfor _, x := range nums {{\n"
            f"\t\tt := cur\n"
            f"\t\tif prev+x > cur {{ t = prev + x }}\n"
            f"\t\tprev = cur\n"
            f"\t\tcur = t\n"
            f"\t}}\n"
            f"\treturn cur{a}\n"
            f"}}\n")


def _kotlin_houserobber(wrong):
    a = " + 1" if wrong else ""
    return (f"fun rob(nums: List<Int>): Int {{\n"
            f"    var prev = 0; var cur = 0\n"
            f"    for (x in nums) {{\n"
            f"        val t = maxOf(cur, prev + x)\n"
            f"        prev = cur; cur = t\n"
            f"    }}\n"
            f"    return cur{a}\n"
            f"}}\n")


def _scala_houserobber(wrong):
    a = " + 1" if wrong else ""
    return (f"def rob(nums: List[Int]): Int = {{\n"
            f"  var prev = 0; var cur = 0\n"
            f"  for (x <- nums) {{\n"
            f"    val t = math.max(cur, prev + x)\n"
            f"    prev = cur; cur = t\n"
            f"  }}\n"
            f"  cur{a}\n"
            f"}}\n")


def _ruby_houserobber(wrong):
    a = " + 1" if wrong else ""
    return (f"def rob(nums)\n"
            f"  prev = 0; cur = 0\n"
            f"  nums.each do |x|\n"
            f"    t = [cur, prev + x].max\n"
            f"    prev = cur; cur = t\n"
            f"  end\n"
            f"  cur{a}\n"
            f"end\n")


def _php_houserobber(wrong):
    a = " + 1" if wrong else ""
    return (f"function rob($nums) {{\n"
            f"    $prev = 0; $cur = 0;\n"
            f"    foreach ($nums as $x) {{\n"
            f"        $t = max($cur, $prev + $x);\n"
            f"        $prev = $cur; $cur = $t;\n"
            f"    }}\n"
            f"    return $cur{a};\n"
            f"}}\n")


def _r_houserobber(wrong):
    a = " + 1" if wrong else ""
    return (f"rob <- function(nums) {{\n"
            f"  prev <- 0; cur <- 0\n"
            f"  for (x in nums) {{\n"
            f"    t <- max(cur, prev + x)\n"
            f"    prev <- cur; cur <- t\n"
            f"  }}\n"
            f"  return(cur{a})\n"
            f"}}\n")


# ── word-break (DP, string + array<string>) ─────────────────────────────────
def _go_wordbreak(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (f"func word_break(s string, word_dict []string) bool {{\n"
            f"\tn := len(s)\n"
            f"\twordSet := map[string]bool{{}}\n"
            f"\tfor _, w := range word_dict {{ wordSet[w] = true }}\n"
            f"\tdp := make([]bool, n+1)\n"
            f"\tdp[0] = true\n"
            f"\tfor i := 1; i <= n; i++ {{\n"
            f"\t\tfor j := 0; j < i; j++ {{\n"
            f"\t\t\tif dp[j] && wordSet[s[j:i]] {{ dp[i] = true; break }}\n"
            f"\t\t}}\n"
            f"\t}}\n"
            f"\treturn {ret}\n"
            f"}}\n")


def _kotlin_wordbreak(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (f"fun word_break(s: String, word_dict: List<String>): Boolean {{\n"
            f"    val n = s.length\n"
            f"    val wordSet = word_dict.toHashSet()\n"
            f"    val dp = BooleanArray(n+1)\n"
            f"    dp[0] = true\n"
            f"    for (i in 1..n) {{\n"
            f"        for (j in 0 until i) {{\n"
            f"            if (dp[j] && wordSet.contains(s.substring(j, i))) {{ dp[i] = true; break }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return {ret}\n"
            f"}}\n")


def _scala_wordbreak(wrong):
    ret = "!dp(n)" if wrong else "dp(n)"
    return (f"def word_break(s: String, word_dict: List[String]): Boolean = {{\n"
            f"  val n = s.length\n"
            f"  val wordSet = word_dict.toSet\n"
            f"  val dp = Array.fill(n+1)(false)\n"
            f"  dp(0) = true\n"
            f"  for (i <- 1 to n) {{\n"
            f"    var j = 0\n"
            f"    while (j < i && !dp(i)) {{\n"
            f"      if (dp(j) && wordSet.contains(s.substring(j, i))) dp(i) = true\n"
            f"      j += 1\n"
            f"    }}\n"
            f"  }}\n"
            f"  {ret}\n"
            f"}}\n")


def _ruby_wordbreak(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (f"def word_break(s, word_dict)\n"
            f"  n = s.length\n"
            f"  word_set = word_dict.to_set rescue word_dict\n"
            f"  dp = Array.new(n+1, false)\n"
            f"  dp[0] = true\n"
            f"  (1..n).each do |i|\n"
            f"    (0...i).each do |j|\n"
            f"      if dp[j] && word_dict.include?(s[j...i])\n"
            f"        dp[i] = true\n"
            f"        break\n"
            f"      end\n"
            f"    end\n"
            f"  end\n"
            f"  {ret}\n"
            f"end\n")


def _php_wordbreak(wrong):
    ret = "!$dp[$n]" if wrong else "$dp[$n]"
    return (f"function word_break($s, $word_dict) {{\n"
            f"    $n = strlen($s);\n"
            f"    $wordSet = array_flip($word_dict);\n"
            f"    $dp = array_fill(0, $n+1, false);\n"
            f"    $dp[0] = true;\n"
            f"    for ($i=1; $i<=$n; $i++) {{\n"
            f"        for ($j=0; $j<$i; $j++) {{\n"
            f"            if ($dp[$j] && isset($wordSet[substr($s, $j, $i-$j)])) {{ $dp[$i] = true; break; }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return {ret};\n"
            f"}}\n")


def _r_wordbreak(wrong):
    ret = "!dp[n+1]" if wrong else "dp[n+1]"
    return (f"word_break <- function(s, word_dict) {{\n"
            f"  n <- nchar(s)\n"
            f"  dp <- rep(FALSE, n+1); dp[1] <- TRUE\n"
            f"  for (i in 1:n) {{\n"
            f"    for (j in 0:(i-1)) {{\n"
            f"      if (dp[j+1] && substr(s, j+1, i) %in% word_dict) {{ dp[i+1] <- TRUE; break }}\n"
            f"    }}\n"
            f"  }}\n"
            f"  return({ret})\n"
            f"}}\n")


# ── longest-increasing-subsequence (O(n^2) DP) ──────────────────────────────
def _go_lis(wrong):
    a = " + 1" if wrong else ""
    return (f"func lis(nums []int) int {{\n"
            f"\tn := len(nums)\n"
            f"\tdp := make([]int, n)\n"
            f"\tbest := 0\n"
            f"\tfor i := 0; i < n; i++ {{\n"
            f"\t\tdp[i] = 1\n"
            f"\t\tfor j := 0; j < i; j++ {{\n"
            f"\t\t\tif nums[j] < nums[i] && dp[j]+1 > dp[i] {{ dp[i] = dp[j] + 1 }}\n"
            f"\t\t}}\n"
            f"\t\tif dp[i] > best {{ best = dp[i] }}\n"
            f"\t}}\n"
            f"\treturn best{a}\n"
            f"}}\n")


def _kotlin_lis(wrong):
    a = " + 1" if wrong else ""
    return (f"fun lis(nums: List<Int>): Int {{\n"
            f"    val n = nums.size\n"
            f"    val dp = IntArray(n) {{ 1 }}\n"
            f"    var best = 0\n"
            f"    for (i in 0 until n) {{\n"
            f"        for (j in 0 until i) {{\n"
            f"            if (nums[j] < nums[i] && dp[j]+1 > dp[i]) dp[i] = dp[j]+1\n"
            f"        }}\n"
            f"        best = maxOf(best, dp[i])\n"
            f"    }}\n"
            f"    return best{a}\n"
            f"}}\n")


def _scala_lis(wrong):
    a = " + 1" if wrong else ""
    return (f"def lis(nums: List[Int]): Int = {{\n"
            f"  val n = nums.length\n"
            f"  val dp = Array.fill(n)(1)\n"
            f"  var best = 0\n"
            f"  for (i <- 0 until n) {{\n"
            f"    for (j <- 0 until i) {{\n"
            f"      if (nums(j) < nums(i) && dp(j)+1 > dp(i)) dp(i) = dp(j)+1\n"
            f"    }}\n"
            f"    best = math.max(best, dp(i))\n"
            f"  }}\n"
            f"  best{a}\n"
            f"}}\n")


def _ruby_lis(wrong):
    a = " + 1" if wrong else ""
    return (f"def lis(nums)\n"
            f"  n = nums.length\n"
            f"  dp = Array.new(n, 1)\n"
            f"  best = 0\n"
            f"  (0...n).each do |i|\n"
            f"    (0...i).each do |j|\n"
            f"      dp[i] = dp[j]+1 if nums[j] < nums[i] && dp[j]+1 > dp[i]\n"
            f"    end\n"
            f"    best = [best, dp[i]].max\n"
            f"  end\n"
            f"  best{a}\n"
            f"end\n")


def _php_lis(wrong):
    a = " + 1" if wrong else ""
    return (f"function lis($nums) {{\n"
            f"    $n = count($nums);\n"
            f"    $dp = array_fill(0, $n, 1);\n"
            f"    $best = 0;\n"
            f"    for ($i=0; $i<$n; $i++) {{\n"
            f"        for ($j=0; $j<$i; $j++) {{\n"
            f"            if ($nums[$j] < $nums[$i] && $dp[$j]+1 > $dp[$i]) $dp[$i] = $dp[$j]+1;\n"
            f"        }}\n"
            f"        $best = max($best, $dp[$i]);\n"
            f"    }}\n"
            f"    return $best{a};\n"
            f"}}\n")


def _r_lis(wrong):
    a = " + 1" if wrong else ""
    return (f"lis <- function(nums) {{\n"
            f"  n <- length(nums)\n"
            f"  dp <- rep(1, n)\n"
            f"  best <- 0\n"
            f"  for (i in 1:n) {{\n"
            f"    if (i > 1) {{\n"
            f"      for (j in 1:(i-1)) {{\n"
            f"        if (nums[[j]] < nums[[i]] && dp[j]+1 > dp[i]) dp[i] <- dp[j]+1\n"
            f"      }}\n"
            f"    }}\n"
            f"    best <- max(best, dp[i])\n"
            f"  }}\n"
            f"  return(best{a})\n"
            f"}}\n")


# ── longest-common-subsequence (DP O(n*m)) ──────────────────────────────────
def _go_lcs(wrong):
    a = " + 1" if wrong else ""
    return (f"func lcs(s1 string, s2 string) int {{\n"
            f"\tn, m := len(s1), len(s2)\n"
            f"\tdp := make([][]int, n+1)\n"
            f"\tfor i := range dp {{ dp[i] = make([]int, m+1) }}\n"
            f"\tfor i := 1; i <= n; i++ {{\n"
            f"\t\tfor j := 1; j <= m; j++ {{\n"
            f"\t\t\tif s1[i-1] == s2[j-1] {{ dp[i][j] = dp[i-1][j-1] + 1 }} else if dp[i-1][j] > dp[i][j-1] {{ dp[i][j] = dp[i-1][j] }} else {{ dp[i][j] = dp[i][j-1] }}\n"
            f"\t\t}}\n"
            f"\t}}\n"
            f"\treturn dp[n][m]{a}\n"
            f"}}\n")


def _kotlin_lcs(wrong):
    a = " + 1" if wrong else ""
    return (f"fun lcs(s1: String, s2: String): Int {{\n"
            f"    val n = s1.length; val m = s2.length\n"
            f"    val dp = Array(n+1) {{ IntArray(m+1) }}\n"
            f"    for (i in 1..n) for (j in 1..m) {{\n"
            f"        dp[i][j] = if (s1[i-1] == s2[j-1]) dp[i-1][j-1]+1 else maxOf(dp[i-1][j], dp[i][j-1])\n"
            f"    }}\n"
            f"    return dp[n][m]{a}\n"
            f"}}\n")


def _scala_lcs(wrong):
    a = " + 1" if wrong else ""
    return (f"def lcs(s1: String, s2: String): Int = {{\n"
            f"  val n = s1.length; val m = s2.length\n"
            f"  val dp = Array.ofDim[Int](n+1, m+1)\n"
            f"  for (i <- 1 to n; j <- 1 to m) {{\n"
            f"    dp(i)(j) = if (s1(i-1) == s2(j-1)) dp(i-1)(j-1)+1 else math.max(dp(i-1)(j), dp(i)(j-1))\n"
            f"  }}\n"
            f"  dp(n)(m){a}\n"
            f"}}\n")


def _ruby_lcs(wrong):
    a = " + 1" if wrong else ""
    return (f"def lcs(s1, s2)\n"
            f"  n = s1.length; m = s2.length\n"
            f"  dp = Array.new(n+1) {{ Array.new(m+1, 0) }}\n"
            f"  (1..n).each do |i|\n"
            f"    (1..m).each do |j|\n"
            f"      dp[i][j] = if s1[i-1] == s2[j-1] then dp[i-1][j-1]+1 else [dp[i-1][j], dp[i][j-1]].max end\n"
            f"    end\n"
            f"  end\n"
            f"  dp[n][m]{a}\n"
            f"end\n")


def _php_lcs(wrong):
    a = " + 1" if wrong else ""
    return (f"function lcs($s1, $s2) {{\n"
            f"    $n = strlen($s1); $m = strlen($s2);\n"
            f"    $dp = array_fill(0, $n+1, array_fill(0, $m+1, 0));\n"
            f"    for ($i=1; $i<=$n; $i++) {{\n"
            f"        for ($j=1; $j<=$m; $j++) {{\n"
            f"            $dp[$i][$j] = ($s1[$i-1] == $s2[$j-1]) ? $dp[$i-1][$j-1]+1 : max($dp[$i-1][$j], $dp[$i][$j-1]);\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $dp[$n][$m]{a};\n"
            f"}}\n")


def _r_lcs(wrong):
    a = " + 1" if wrong else ""
    return (f"lcs <- function(s1, s2) {{\n"
            f"  n <- nchar(s1); m <- nchar(s2)\n"
            f"  dp <- matrix(0, n+1, m+1)\n"
            f"  if (n>0 && m>0) {{\n"
            f"    for (i in 1:n) {{\n"
            f"      for (j in 1:m) {{\n"
            f"        if (substr(s1,i,i) == substr(s2,j,j)) {{ dp[i+1,j+1] <- dp[i,j]+1 }}\n"
            f"        else {{ dp[i+1,j+1] <- max(dp[i,j+1], dp[i+1,j]) }}\n"
            f"      }}\n"
            f"    }}\n"
            f"  }}\n"
            f"  return(dp[n+1,m+1]{a})\n"
            f"}}\n")


# ── edit-distance (DP O(n*m)) ────────────────────────────────────────────────
def _go_editdist(wrong):
    a = " + 1" if wrong else ""
    return (f"func edit_distance(w1 string, w2 string) int {{\n"
            f"\tn, m := len(w1), len(w2)\n"
            f"\tdp := make([][]int, n+1)\n"
            f"\tfor i := range dp {{ dp[i] = make([]int, m+1) }}\n"
            f"\tfor i := 0; i <= n; i++ {{ dp[i][0] = i }}\n"
            f"\tfor j := 0; j <= m; j++ {{ dp[0][j] = j }}\n"
            f"\tfor i := 1; i <= n; i++ {{\n"
            f"\t\tfor j := 1; j <= m; j++ {{\n"
            f"\t\t\tif w1[i-1] == w2[j-1] {{\n"
            f"\t\t\t\tdp[i][j] = dp[i-1][j-1]\n"
            f"\t\t\t}} else {{\n"
            f"\t\t\t\tm3 := dp[i-1][j-1]\n"
            f"\t\t\t\tif dp[i-1][j] < m3 {{ m3 = dp[i-1][j] }}\n"
            f"\t\t\t\tif dp[i][j-1] < m3 {{ m3 = dp[i][j-1] }}\n"
            f"\t\t\t\tdp[i][j] = m3 + 1\n"
            f"\t\t\t}}\n"
            f"\t\t}}\n"
            f"\t}}\n"
            f"\treturn dp[n][m]{a}\n"
            f"}}\n")


def _kotlin_editdist(wrong):
    a = " + 1" if wrong else ""
    return (f"fun edit_distance(w1: String, w2: String): Int {{\n"
            f"    val n = w1.length; val m = w2.length\n"
            f"    val dp = Array(n+1) {{ IntArray(m+1) }}\n"
            f"    for (i in 0..n) dp[i][0] = i\n"
            f"    for (j in 0..m) dp[0][j] = j\n"
            f"    for (i in 1..n) for (j in 1..m) {{\n"
            f"        dp[i][j] = if (w1[i-1] == w2[j-1]) dp[i-1][j-1]\n"
            f"                   else 1 + minOf(dp[i-1][j-1], dp[i-1][j], dp[i][j-1])\n"
            f"    }}\n"
            f"    return dp[n][m]{a}\n"
            f"}}\n")


def _scala_editdist(wrong):
    a = " + 1" if wrong else ""
    return (f"def edit_distance(w1: String, w2: String): Int = {{\n"
            f"  val n = w1.length; val m = w2.length\n"
            f"  val dp = Array.ofDim[Int](n+1, m+1)\n"
            f"  for (i <- 0 to n) dp(i)(0) = i\n"
            f"  for (j <- 0 to m) dp(0)(j) = j\n"
            f"  for (i <- 1 to n; j <- 1 to m) {{\n"
            f"    dp(i)(j) = if (w1(i-1) == w2(j-1)) dp(i-1)(j-1)\n"
            f"               else 1 + math.min(dp(i-1)(j-1), math.min(dp(i-1)(j), dp(i)(j-1)))\n"
            f"  }}\n"
            f"  dp(n)(m){a}\n"
            f"}}\n")


def _ruby_editdist(wrong):
    a = " + 1" if wrong else ""
    return (f"def edit_distance(w1, w2)\n"
            f"  n = w1.length; m = w2.length\n"
            f"  dp = Array.new(n+1) {{ Array.new(m+1, 0) }}\n"
            f"  (0..n).each {{ |i| dp[i][0] = i }}\n"
            f"  (0..m).each {{ |j| dp[0][j] = j }}\n"
            f"  (1..n).each do |i|\n"
            f"    (1..m).each do |j|\n"
            f"      dp[i][j] = if w1[i-1] == w2[j-1] then dp[i-1][j-1] else 1 + [dp[i-1][j-1], dp[i-1][j], dp[i][j-1]].min end\n"
            f"    end\n"
            f"  end\n"
            f"  dp[n][m]{a}\n"
            f"end\n")


def _php_editdist(wrong):
    a = " + 1" if wrong else ""
    return (f"function edit_distance($w1, $w2) {{\n"
            f"    $n = strlen($w1); $m = strlen($w2);\n"
            f"    $dp = array_fill(0, $n+1, array_fill(0, $m+1, 0));\n"
            f"    for ($i=0; $i<=$n; $i++) $dp[$i][0] = $i;\n"
            f"    for ($j=0; $j<=$m; $j++) $dp[0][$j] = $j;\n"
            f"    for ($i=1; $i<=$n; $i++) {{\n"
            f"        for ($j=1; $j<=$m; $j++) {{\n"
            f"            if ($w1[$i-1] == $w2[$j-1]) {{ $dp[$i][$j] = $dp[$i-1][$j-1]; }}\n"
            f"            else {{ $dp[$i][$j] = 1 + min($dp[$i-1][$j-1], $dp[$i-1][$j], $dp[$i][$j-1]); }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $dp[$n][$m]{a};\n"
            f"}}\n")


def _r_editdist(wrong):
    a = " + 1" if wrong else ""
    return (f"edit_distance <- function(w1, w2) {{\n"
            f"  n <- nchar(w1); m <- nchar(w2)\n"
            f"  dp <- matrix(0, n+1, m+1)\n"
            f"  for (i in 0:n) dp[i+1,1] <- i\n"
            f"  for (j in 0:m) dp[1,j+1] <- j\n"
            f"  if (n>0 && m>0) {{\n"
            f"    for (i in 1:n) {{\n"
            f"      for (j in 1:m) {{\n"
            f"        if (substr(w1,i,i) == substr(w2,j,j)) {{ dp[i+1,j+1] <- dp[i,j] }}\n"
            f"        else {{ dp[i+1,j+1] <- 1 + min(dp[i,j], dp[i,j+1], dp[i+1,j]) }}\n"
            f"      }}\n"
            f"    }}\n"
            f"  }}\n"
            f"  return(dp[n+1,m+1]{a})\n"
            f"}}\n")


# ── minimum-path-sum (2D grid DP) ────────────────────────────────────────────
def _go_minpathsum(wrong):
    a = " + 1" if wrong else ""
    return (f"func min_path_sum(grid [][]int) int {{\n"
            f"\tm, n := len(grid), len(grid[0])\n"
            f"\tdp := make([][]int, m)\n"
            f"\tfor i := range dp {{ dp[i] = make([]int, n) }}\n"
            f"\tfor i := 0; i < m; i++ {{\n"
            f"\t\tfor j := 0; j < n; j++ {{\n"
            f"\t\t\tif i == 0 && j == 0 {{ dp[i][j] = grid[i][j] }} else if i == 0 {{ dp[i][j] = dp[i][j-1] + grid[i][j] }} else if j == 0 {{ dp[i][j] = dp[i-1][j] + grid[i][j] }} else {{\n"
            f"\t\t\t\tm2 := dp[i-1][j]\n"
            f"\t\t\t\tif dp[i][j-1] < m2 {{ m2 = dp[i][j-1] }}\n"
            f"\t\t\t\tdp[i][j] = m2 + grid[i][j]\n"
            f"\t\t\t}}\n"
            f"\t\t}}\n"
            f"\t}}\n"
            f"\treturn dp[m-1][n-1]{a}\n"
            f"}}\n")


def _kotlin_minpathsum(wrong):
    a = " + 1" if wrong else ""
    return (f"fun min_path_sum(grid: List<List<Int>>): Int {{\n"
            f"    val m = grid.size; val n = grid[0].size\n"
            f"    val dp = Array(m) {{ IntArray(n) }}\n"
            f"    for (i in 0 until m) for (j in 0 until n) {{\n"
            f"        dp[i][j] = if (i==0 && j==0) grid[i][j]\n"
            f"                   else if (i==0) dp[i][j-1]+grid[i][j]\n"
            f"                   else if (j==0) dp[i-1][j]+grid[i][j]\n"
            f"                   else minOf(dp[i-1][j], dp[i][j-1])+grid[i][j]\n"
            f"    }}\n"
            f"    return dp[m-1][n-1]{a}\n"
            f"}}\n")


def _scala_minpathsum(wrong):
    a = " + 1" if wrong else ""
    return (f"def min_path_sum(grid: List[List[Int]]): Int = {{\n"
            f"  val m = grid.length; val n = grid(0).length\n"
            f"  val dp = Array.ofDim[Int](m, n)\n"
            f"  for (i <- 0 until m; j <- 0 until n) {{\n"
            f"    dp(i)(j) = if (i==0 && j==0) grid(i)(j)\n"
            f"               else if (i==0) dp(i)(j-1)+grid(i)(j)\n"
            f"               else if (j==0) dp(i-1)(j)+grid(i)(j)\n"
            f"               else math.min(dp(i-1)(j), dp(i)(j-1))+grid(i)(j)\n"
            f"  }}\n"
            f"  dp(m-1)(n-1){a}\n"
            f"}}\n")


def _ruby_minpathsum(wrong):
    a = " + 1" if wrong else ""
    return (f"def min_path_sum(grid)\n"
            f"  m = grid.length; n = grid[0].length\n"
            f"  dp = Array.new(m) {{ Array.new(n, 0) }}\n"
            f"  (0...m).each do |i|\n"
            f"    (0...n).each do |j|\n"
            f"      dp[i][j] = if i==0 && j==0 then grid[i][j]\n"
            f"                  elsif i==0 then dp[i][j-1]+grid[i][j]\n"
            f"                  elsif j==0 then dp[i-1][j]+grid[i][j]\n"
            f"                  else [dp[i-1][j], dp[i][j-1]].min+grid[i][j]\n"
            f"                  end\n"
            f"    end\n"
            f"  end\n"
            f"  dp[m-1][n-1]{a}\n"
            f"end\n")


def _php_minpathsum(wrong):
    a = " + 1" if wrong else ""
    return (f"function min_path_sum($grid) {{\n"
            f"    $m = count($grid); $n = count($grid[0]);\n"
            f"    $dp = array_fill(0, $m, array_fill(0, $n, 0));\n"
            f"    for ($i=0; $i<$m; $i++) {{\n"
            f"        for ($j=0; $j<$n; $j++) {{\n"
            f"            if ($i==0 && $j==0) $dp[$i][$j] = $grid[$i][$j];\n"
            f"            elseif ($i==0) $dp[$i][$j] = $dp[$i][$j-1]+$grid[$i][$j];\n"
            f"            elseif ($j==0) $dp[$i][$j] = $dp[$i-1][$j]+$grid[$i][$j];\n"
            f"            else $dp[$i][$j] = min($dp[$i-1][$j], $dp[$i][$j-1])+$grid[$i][$j];\n"
            f"        }}\n"
            f"    }}\n"
            f"    return $dp[$m-1][$n-1]{a};\n"
            f"}}\n")


def _r_minpathsum(wrong):
    a = " + 1" if wrong else ""
    return (f"min_path_sum <- function(grid) {{\n"
            f"  m <- length(grid); n <- length(grid[[1]])\n"
            f"  dp <- matrix(0, m, n)\n"
            f"  for (i in 1:m) {{\n"
            f"    for (j in 1:n) {{\n"
            f"      g <- grid[[i]][[j]]\n"
            f"      if (i==1 && j==1) {{ dp[i,j] <- g }}\n"
            f"      else if (i==1) {{ dp[i,j] <- dp[i,j-1]+g }}\n"
            f"      else if (j==1) {{ dp[i,j] <- dp[i-1,j]+g }}\n"
            f"      else {{ dp[i,j] <- min(dp[i-1,j], dp[i,j-1])+g }}\n"
            f"    }}\n"
            f"  }}\n"
            f"  return(dp[m,n]{a})\n"
            f"}}\n")


# ── n-queens (backtracking count) ────────────────────────────────────────────
def _go_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (f"func solve_n_queens(n int) int {{\n"
            f"\tcols := make([]bool, n)\n"
            f"\tdiag1 := make([]bool, 2*n)\n"
            f"\tdiag2 := make([]bool, 2*n)\n"
            f"\tcount := 0\n"
            f"\tvar bt func(row int)\n"
            f"\tbt = func(row int) {{\n"
            f"\t\tif row == n {{ count++; return }}\n"
            f"\t\tfor c := 0; c < n; c++ {{\n"
            f"\t\t\tif !cols[c] && !diag1[row+c] && !diag2[row-c+n] {{\n"
            f"\t\t\t\tcols[c], diag1[row+c], diag2[row-c+n] = true, true, true\n"
            f"\t\t\t\tbt(row + 1)\n"
            f"\t\t\t\tcols[c], diag1[row+c], diag2[row-c+n] = false, false, false\n"
            f"\t\t\t}}\n"
            f"\t\t}}\n"
            f"\t}}\n"
            f"\tbt(0)\n"
            f"\treturn count{a}\n"
            f"}}\n")


def _kotlin_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (f"fun solve_n_queens(n: Int): Int {{\n"
            f"    val cols = BooleanArray(n); val diag1 = BooleanArray(2*n); val diag2 = BooleanArray(2*n)\n"
            f"    var count = 0\n"
            f"    fun bt(row: Int) {{\n"
            f"        if (row == n) {{ count++; return }}\n"
            f"        for (c in 0 until n) {{\n"
            f"            if (!cols[c] && !diag1[row+c] && !diag2[row-c+n]) {{\n"
            f"                cols[c] = true; diag1[row+c] = true; diag2[row-c+n] = true\n"
            f"                bt(row+1)\n"
            f"                cols[c] = false; diag1[row+c] = false; diag2[row-c+n] = false\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"    bt(0)\n"
            f"    return count{a}\n"
            f"}}\n")


def _scala_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (f"def solve_n_queens(n: Int): Int = {{\n"
            f"  val cols = Array.fill(n)(false); val diag1 = Array.fill(2*n)(false); val diag2 = Array.fill(2*n)(false)\n"
            f"  var count = 0\n"
            f"  def bt(row: Int): Unit = {{\n"
            f"    if (row == n) {{ count += 1; return }}\n"
            f"    for (c <- 0 until n) {{\n"
            f"      if (!cols(c) && !diag1(row+c) && !diag2(row-c+n)) {{\n"
            f"        cols(c) = true; diag1(row+c) = true; diag2(row-c+n) = true\n"
            f"        bt(row+1)\n"
            f"        cols(c) = false; diag1(row+c) = false; diag2(row-c+n) = false\n"
            f"      }}\n"
            f"    }}\n"
            f"  }}\n"
            f"  bt(0)\n"
            f"  count{a}\n"
            f"}}\n")


def _ruby_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (f"def solve_n_queens(n)\n"
            f"  cols = Array.new(n, false); diag1 = Array.new(2*n, false); diag2 = Array.new(2*n, false)\n"
            f"  count = 0\n"
            f"  bt = lambda do |row|\n"
            f"    if row == n\n"
            f"      count += 1\n"
            f"      next\n"
            f"    end\n"
            f"    (0...n).each do |c|\n"
            f"      if !cols[c] && !diag1[row+c] && !diag2[row-c+n]\n"
            f"        cols[c] = diag1[row+c] = diag2[row-c+n] = true\n"
            f"        bt.call(row+1)\n"
            f"        cols[c] = diag1[row+c] = diag2[row-c+n] = false\n"
            f"      end\n"
            f"    end\n"
            f"  end\n"
            f"  bt.call(0)\n"
            f"  count{a}\n"
            f"end\n")


def _php_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (f"function solve_n_queens($n) {{\n"
            f"    $cols = array_fill(0, $n, false);\n"
            f"    $diag1 = array_fill(0, 2*$n, false);\n"
            f"    $diag2 = array_fill(0, 2*$n, false);\n"
            f"    $count = 0;\n"
            f"    $bt = function($row) use (&$bt, &$cols, &$diag1, &$diag2, &$count, $n) {{\n"
            f"        if ($row == $n) {{ $count++; return; }}\n"
            f"        for ($c=0; $c<$n; $c++) {{\n"
            f"            if (!$cols[$c] && !$diag1[$row+$c] && !$diag2[$row-$c+$n]) {{\n"
            f"                $cols[$c] = $diag1[$row+$c] = $diag2[$row-$c+$n] = true;\n"
            f"                $bt($row+1);\n"
            f"                $cols[$c] = $diag1[$row+$c] = $diag2[$row-$c+$n] = false;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }};\n"
            f"    $bt(0);\n"
            f"    return $count{a};\n"
            f"}}\n")


def _r_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (f"solve_n_queens <- function(n) {{\n"
            f"  cols <- rep(FALSE, n); diag1 <- rep(FALSE, 2*n); diag2 <- rep(FALSE, 2*n)\n"
            f"  count <- 0\n"
            f"  bt <- function(row) {{\n"
            f"    if (row == n) {{ count <<- count + 1; return(invisible(NULL)) }}\n"
            f"    for (c in 0:(n-1)) {{\n"
            f"      if (!cols[c+1] && !diag1[row+c+1] && !diag2[row-c+n+1]) {{\n"
            f"        cols[c+1] <<- TRUE; diag1[row+c+1] <<- TRUE; diag2[row-c+n+1] <<- TRUE\n"
            f"        bt(row+1)\n"
            f"        cols[c+1] <<- FALSE; diag1[row+c+1] <<- FALSE; diag2[row-c+n+1] <<- FALSE\n"
            f"      }}\n"
            f"    }}\n"
            f"  }}\n"
            f"  bt(0)\n"
            f"  return(count{a})\n"
            f"}}\n")


# ── graph-bfs (adjacency list, BFS from src, returns visit order) ──────────
def _go_graphbfs(wrong):
    incr = "\n\tfor i := range order { order[i]++ }" if wrong else ""
    return (f"func bfs(adj [][]int, src int, n int) []int {{\n"
            f"\tvisited := make([]bool, n)\n"
            f"\torder := []int{{}}\n"
            f"\tqueue := []int{{src}}\n"
            f"\tvisited[src] = true\n"
            f"\tfor len(queue) > 0 {{\n"
            f"\t\tcur := queue[0]; queue = queue[1:]\n"
            f"\t\torder = append(order, cur)\n"
            f"\t\tfor _, nb := range adj[cur] {{\n"
            f"\t\t\tif !visited[nb] {{ visited[nb] = true; queue = append(queue, nb) }}\n"
            f"\t\t}}\n"
            f"\t}}{incr}\n"
            f"\treturn order\n"
            f"}}\n")


def _kotlin_graphbfs(wrong):
    incr = "\n    for (i in out.indices) out[i] = out[i] + 1" if wrong else ""
    return (f"fun bfs(adj: List<List<Int>>, src: Int, n: Int): List<Int> {{\n"
            f"    val visited = BooleanArray(n)\n"
            f"    val out = mutableListOf<Int>()\n"
            f"    val queue = java.util.ArrayDeque<Int>()\n"
            f"    queue.add(src); visited[src] = true\n"
            f"    while (queue.isNotEmpty()) {{\n"
            f"        val cur = queue.poll(); out.add(cur)\n"
            f"        for (nb in adj[cur]) {{ if (!visited[nb]) {{ visited[nb] = true; queue.add(nb) }} }}\n"
            f"    }}{incr}\n"
            f"    return out\n"
            f"}}\n")


def _scala_graphbfs(wrong):
    incr = "\n  for (i <- out.indices) out(i) = out(i) + 1" if wrong else ""
    return (f"def bfs(adj: List[List[Int]], src: Int, n: Int): List[Int] = {{\n"
            f"  val visited = Array.fill(n)(false)\n"
            f"  val out = scala.collection.mutable.ArrayBuffer[Int]()\n"
            f"  val queue = scala.collection.mutable.Queue[Int]()\n"
            f"  queue.enqueue(src); visited(src) = true\n"
            f"  while (queue.nonEmpty) {{\n"
            f"    val cur = queue.dequeue(); out += cur\n"
            f"    for (nb <- adj(cur)) {{ if (!visited(nb)) {{ visited(nb) = true; queue.enqueue(nb) }} }}\n"
            f"  }}{incr}\n"
            f"  out.toList\n"
            f"}}\n")


def _ruby_graphbfs(wrong):
    incr = "\n  out.map! { |x| x + 1 }" if wrong else ""
    return (f"def bfs(adj, src, n)\n"
            f"  visited = Array.new(n, false)\n"
            f"  out = []\n"
            f"  queue = [src]\n"
            f"  visited[src] = true\n"
            f"  until queue.empty?\n"
            f"    cur = queue.shift\n"
            f"    out << cur\n"
            f"    adj[cur].each do |nb|\n"
            f"      unless visited[nb]\n"
            f"        visited[nb] = true\n"
            f"        queue << nb\n"
            f"      end\n"
            f"    end\n"
            f"  end{incr}\n"
            f"  out\n"
            f"end\n")


def _php_graphbfs(wrong):
    incr = "\n    $out = array_map(function($x) { return $x + 1; }, $out);" if wrong else ""
    return (f"function bfs($adj, $src, $n) {{\n"
            f"    $visited = array_fill(0, $n, false);\n"
            f"    $out = [];\n"
            f"    $queue = [$src];\n"
            f"    $visited[$src] = true;\n"
            f"    while (count($queue) > 0) {{\n"
            f"        $cur = array_shift($queue);\n"
            f"        $out[] = $cur;\n"
            f"        foreach ($adj[$cur] as $nb) {{\n"
            f"            if (!$visited[$nb]) {{ $visited[$nb] = true; $queue[] = $nb; }}\n"
            f"        }}\n"
            f"    }}{incr}\n"
            f"    return $out;\n"
            f"}}\n")


def _r_graphbfs(wrong):
    incr = "\n  out <- lapply(out, function(x) x + 1)" if wrong else ""
    return (f"bfs <- function(adj, src, n) {{\n"
            f"  visited <- rep(FALSE, n)\n"
            f"  out <- list()\n"
            f"  queue <- c(src)\n"
            f"  visited[src+1] <- TRUE\n"
            f"  while (length(queue) > 0) {{\n"
            f"    cur <- queue[1]; queue <- queue[-1]\n"
            f"    out[[length(out)+1]] <- cur\n"
            f"    neighbors <- adj[[cur+1]]\n"
            f"    for (nb in neighbors) {{\n"
            f"      if (!visited[nb+1]) {{ visited[nb+1] <- TRUE; queue <- c(queue, nb) }}\n"
            f"    }}\n"
            f"  }}{incr}\n"
            f"  return(out)\n"
            f"}}\n")


# ── dijkstra-shortest-path (adj[node] = list of [neighbor, weight]) ────────
def _go_dijkstra(wrong):
    incr = "\n\tfor i := range dist { if dist[i] < INF { dist[i]++ } }" if wrong else ""
    return (f"func dijkstra(adj [][][]int, n int) []int {{\n"
            f"\tconst INF = 1 << 30\n"
            f"\tdist := make([]int, n)\n"
            f"\tfor i := range dist {{ dist[i] = INF }}\n"
            f"\tdist[0] = 0\n"
            f"\tvisited := make([]bool, n)\n"
            f"\tfor iter := 0; iter < n; iter++ {{\n"
            f"\t\tu := -1\n"
            f"\t\tfor i := 0; i < n; i++ {{\n"
            f"\t\t\tif !visited[i] && (u == -1 || dist[i] < dist[u]) {{ u = i }}\n"
            f"\t\t}}\n"
            f"\t\tif u == -1 || dist[u] == INF {{ break }}\n"
            f"\t\tvisited[u] = true\n"
            f"\t\tfor _, edge := range adj[u] {{\n"
            f"\t\t\tv, w := edge[0], edge[1]\n"
            f"\t\t\tif dist[u]+w < dist[v] {{ dist[v] = dist[u] + w }}\n"
            f"\t\t}}\n"
            f"\t}}{incr}\n"
            f"\treturn dist\n"
            f"}}\n")


def _kotlin_dijkstra(wrong):
    incr = "\n    for (i in dist.indices) if (dist[i] < INF) dist[i] = dist[i] + 1" if wrong else ""
    return (f"fun dijkstra(adj: List<List<List<Int>>>, n: Int): List<Int> {{\n"
            f"    val INF = 1 shl 30\n"
            f"    val dist = IntArray(n) {{ INF }}\n"
            f"    dist[0] = 0\n"
            f"    val visited = BooleanArray(n)\n"
            f"    for (iter in 0 until n) {{\n"
            f"        var u = -1\n"
            f"        for (i in 0 until n) {{ if (!visited[i] && (u == -1 || dist[i] < dist[u])) u = i }}\n"
            f"        if (u == -1 || dist[u] == INF) break\n"
            f"        visited[u] = true\n"
            f"        for (edge in adj[u]) {{\n"
            f"            val v = edge[0]; val w = edge[1]\n"
            f"            if (dist[u]+w < dist[v]) dist[v] = dist[u]+w\n"
            f"        }}\n"
            f"    }}{incr}\n"
            f"    return dist.toList()\n"
            f"}}\n")


def _scala_dijkstra(wrong):
    incr = "\n  for (i <- dist.indices) if (dist(i) < INF) dist(i) = dist(i) + 1" if wrong else ""
    return (f"def dijkstra(adj: List[List[List[Int]]], n: Int): List[Int] = {{\n"
            f"  val INF = 1 << 30\n"
            f"  val dist = Array.fill(n)(INF)\n"
            f"  dist(0) = 0\n"
            f"  val visited = Array.fill(n)(false)\n"
            f"  for (iter <- 0 until n) {{\n"
            f"    var u = -1\n"
            f"    for (i <- 0 until n) {{ if (!visited(i) && (u == -1 || dist(i) < dist(u))) u = i }}\n"
            f"    if (u == -1 || dist(u) == INF) {{}} else {{\n"
            f"      visited(u) = true\n"
            f"      for (edge <- adj(u)) {{\n"
            f"        val v = edge(0); val w = edge(1)\n"
            f"        if (dist(u)+w < dist(v)) dist(v) = dist(u)+w\n"
            f"      }}\n"
            f"    }}\n"
            f"  }}{incr}\n"
            f"  dist.toList\n"
            f"}}\n")


def _ruby_dijkstra(wrong):
    incr = "\n  dist.map! { |d| d < inf ? d + 1 : d }" if wrong else ""
    return (f"def dijkstra(adj, n)\n"
            f"  inf = 1 << 30\n"
            f"  dist = Array.new(n, inf)\n"
            f"  dist[0] = 0\n"
            f"  visited = Array.new(n, false)\n"
            f"  n.times do\n"
            f"    u = -1\n"
            f"    (0...n).each do |i|\n"
            f"      u = i if !visited[i] && (u == -1 || dist[i] < dist[u])\n"
            f"    end\n"
            f"    break if u == -1 || dist[u] == inf\n"
            f"    visited[u] = true\n"
            f"    adj[u].each do |edge|\n"
            f"      v, w = edge[0], edge[1]\n"
            f"      dist[v] = dist[u] + w if dist[u] + w < dist[v]\n"
            f"    end\n"
            f"  end{incr}\n"
            f"  dist\n"
            f"end\n")


def _php_dijkstra(wrong):
    incr = "\n    $dist = array_map(function($d) use ($INF) { return $d < $INF ? $d + 1 : $d; }, $dist);" if wrong else ""
    return (f"function dijkstra($adj, $n) {{\n"
            f"    $INF = 1 << 30;\n"
            f"    $dist = array_fill(0, $n, $INF);\n"
            f"    $dist[0] = 0;\n"
            f"    $visited = array_fill(0, $n, false);\n"
            f"    for ($iter=0; $iter<$n; $iter++) {{\n"
            f"        $u = -1;\n"
            f"        for ($i=0; $i<$n; $i++) {{\n"
            f"            if (!$visited[$i] && ($u == -1 || $dist[$i] < $dist[$u])) $u = $i;\n"
            f"        }}\n"
            f"        if ($u == -1 || $dist[$u] == $INF) break;\n"
            f"        $visited[$u] = true;\n"
            f"        foreach ($adj[$u] as $edge) {{\n"
            f"            $v = $edge[0]; $w = $edge[1];\n"
            f"            if ($dist[$u]+$w < $dist[$v]) $dist[$v] = $dist[$u]+$w;\n"
            f"        }}\n"
            f"    }}{incr}\n"
            f"    return $dist;\n"
            f"}}\n")


def _r_dijkstra(wrong):
    incr = "\n  dist <- sapply(dist, function(d) if (d < INF) d + 1 else d)" if wrong else ""
    return (f"dijkstra <- function(adj, n) {{\n"
            f"  INF <- 2^30\n"
            f"  dist <- rep(INF, n)\n"
            f"  dist[1] <- 0\n"
            f"  visited <- rep(FALSE, n)\n"
            f"  for (iter in 1:n) {{\n"
            f"    u <- -1\n"
            f"    for (i in 0:(n-1)) {{\n"
            f"      if (!visited[i+1] && (u == -1 || dist[i+1] < dist[u+1])) u <- i\n"
            f"    }}\n"
            f"    if (u == -1 || dist[u+1] == INF) break\n"
            f"    visited[u+1] <- TRUE\n"
            f"    edges <- adj[[u+1]]\n"
            f"    if (length(edges) > 0) {{\n"
            f"      for (edge in edges) {{\n"
            f"        v <- edge[[1]]; w <- edge[[2]]\n"
            f"        if (dist[u+1]+w < dist[v+1]) dist[v+1] <- dist[u+1]+w\n"
            f"      }}\n"
            f"    }}\n"
            f"  }}{incr}\n"
            f"  return(as.list(dist))\n"
            f"}}\n")


# ── kmp-string-matching (returns array of match start indices) ─────────────
def _go_kmp(wrong):
    incr = "\n\tfor i := range out { out[i]++ }" if wrong else ""
    return (f"func kmp_search(T string, P string) []int {{\n"
            f"\tn, m := len(T), len(P)\n"
            f"\tout := []int{{}}\n"
            f"\tif m == 0 {{ return out }}\n"
            f"\tlps := make([]int, m)\n"
            f"\tk := 0\n"
            f"\tfor i := 1; i < m; i++ {{\n"
            f"\t\tfor k > 0 && P[i] != P[k] {{ k = lps[k-1] }}\n"
            f"\t\tif P[i] == P[k] {{ k++ }}\n"
            f"\t\tlps[i] = k\n"
            f"\t}}\n"
            f"\tj := 0\n"
            f"\tfor i := 0; i < n; i++ {{\n"
            f"\t\tfor j > 0 && T[i] != P[j] {{ j = lps[j-1] }}\n"
            f"\t\tif T[i] == P[j] {{ j++ }}\n"
            f"\t\tif j == m {{ out = append(out, i-m+1); j = lps[j-1] }}\n"
            f"\t}}{incr}\n"
            f"\treturn out\n"
            f"}}\n")


def _kotlin_kmp(wrong):
    incr = "\n    for (i in out.indices) out[i] = out[i] + 1" if wrong else ""
    return (f"fun kmp_search(T: String, P: String): List<Int> {{\n"
            f"    val n = T.length; val m = P.length\n"
            f"    val out = mutableListOf<Int>()\n"
            f"    if (m == 0) return out\n"
            f"    val lps = IntArray(m)\n"
            f"    var k = 0\n"
            f"    for (i in 1 until m) {{\n"
            f"        while (k > 0 && P[i] != P[k]) k = lps[k-1]\n"
            f"        if (P[i] == P[k]) k++\n"
            f"        lps[i] = k\n"
            f"    }}\n"
            f"    var j = 0\n"
            f"    for (i in 0 until n) {{\n"
            f"        while (j > 0 && T[i] != P[j]) j = lps[j-1]\n"
            f"        if (T[i] == P[j]) j++\n"
            f"        if (j == m) {{ out.add(i-m+1); j = lps[j-1] }}\n"
            f"    }}{incr}\n"
            f"    return out\n"
            f"}}\n")


def _scala_kmp(wrong):
    incr = "\n  for (i <- out.indices) out(i) = out(i) + 1" if wrong else ""
    return (f"def kmp_search(T: String, P: String): List[Int] = {{\n"
            f"  val n = T.length; val m = P.length\n"
            f"  val out = scala.collection.mutable.ArrayBuffer[Int]()\n"
            f"  if (m == 0) return out.toList\n"
            f"  val lps = Array.fill(m)(0)\n"
            f"  var k = 0\n"
            f"  for (i <- 1 until m) {{\n"
            f"    while (k > 0 && P(i) != P(k)) k = lps(k-1)\n"
            f"    if (P(i) == P(k)) k += 1\n"
            f"    lps(i) = k\n"
            f"  }}\n"
            f"  var j = 0\n"
            f"  for (i <- 0 until n) {{\n"
            f"    while (j > 0 && T(i) != P(j)) j = lps(j-1)\n"
            f"    if (T(i) == P(j)) j += 1\n"
            f"    if (j == m) {{ out += (i-m+1); j = lps(j-1) }}\n"
            f"  }}{incr}\n"
            f"  out.toList\n"
            f"}}\n")


def _ruby_kmp(wrong):
    incr = "\n  out.map! { |x| x + 1 }" if wrong else ""
    return (f"def kmp_search(t, p)\n"
            f"  n = t.length; m = p.length\n"
            f"  out = []\n"
            f"  return out if m == 0\n"
            f"  lps = Array.new(m, 0)\n"
            f"  k = 0\n"
            f"  (1...m).each do |i|\n"
            f"    while k > 0 && p[i] != p[k]\n"
            f"      k = lps[k-1]\n"
            f"    end\n"
            f"    k += 1 if p[i] == p[k]\n"
            f"    lps[i] = k\n"
            f"  end\n"
            f"  j = 0\n"
            f"  (0...n).each do |i|\n"
            f"    while j > 0 && t[i] != p[j]\n"
            f"      j = lps[j-1]\n"
            f"    end\n"
            f"    j += 1 if t[i] == p[j]\n"
            f"    if j == m\n"
            f"      out << (i-m+1)\n"
            f"      j = lps[j-1]\n"
            f"    end\n"
            f"  end{incr}\n"
            f"  out\n"
            f"end\n")


def _php_kmp(wrong):
    incr = "\n    $out = array_map(function($x) { return $x + 1; }, $out);" if wrong else ""
    return (f"function kmp_search($T, $P) {{\n"
            f"    $n = strlen($T); $m = strlen($P);\n"
            f"    $out = [];\n"
            f"    if ($m == 0) return $out;\n"
            f"    $lps = array_fill(0, $m, 0);\n"
            f"    $k = 0;\n"
            f"    for ($i=1; $i<$m; $i++) {{\n"
            f"        while ($k > 0 && $P[$i] != $P[$k]) $k = $lps[$k-1];\n"
            f"        if ($P[$i] == $P[$k]) $k++;\n"
            f"        $lps[$i] = $k;\n"
            f"    }}\n"
            f"    $j = 0;\n"
            f"    for ($i=0; $i<$n; $i++) {{\n"
            f"        while ($j > 0 && $T[$i] != $P[$j]) $j = $lps[$j-1];\n"
            f"        if ($T[$i] == $P[$j]) $j++;\n"
            f"        if ($j == $m) {{ $out[] = $i-$m+1; $j = $lps[$j-1]; }}\n"
            f"    }}{incr}\n"
            f"    return $out;\n"
            f"}}\n")


def _r_kmp(wrong):
    incr = "\n  out <- lapply(out, function(x) x + 1)" if wrong else ""
    return (f"kmp_search <- function(T, P) {{\n"
            f"  n <- nchar(T); m <- nchar(P)\n"
            f"  out <- list()\n"
            f"  if (m == 0) return(out)\n"
            f"  lps <- rep(0, m)\n"
            f"  k <- 0\n"
            f"  if (m > 1) {{\n"
            f"    for (i in 1:(m-1)) {{\n"
            f"      while (k > 0 && substr(P,i+1,i+1) != substr(P,k+1,k+1)) k <- lps[k]\n"
            f"      if (substr(P,i+1,i+1) == substr(P,k+1,k+1)) k <- k + 1\n"
            f"      lps[i+1] <- k\n"
            f"    }}\n"
            f"  }}\n"
            f"  j <- 0\n"
            f"  if (n > 0) {{\n"
            f"    for (i in 0:(n-1)) {{\n"
            f"      while (j > 0 && substr(T,i+1,i+1) != substr(P,j+1,j+1)) j <- lps[j]\n"
            f"      if (substr(T,i+1,i+1) == substr(P,j+1,j+1)) j <- j + 1\n"
            f"      if (j == m) {{ out[[length(out)+1]] <- i-m+1; j <- lps[j] }}\n"
            f"    }}\n"
            f"  }}{incr}\n"
            f"  return(out)\n"
            f"}}\n")


_BUILDERS = {
    "two-sum": {"go": _go_twosum, "kotlin": _kotlin_twosum, "scala": _scala_twosum, "ruby": _ruby_twosum, "php": _php_twosum, "r": _r_twosum},
    "maximum-subarray": {"go": _go_maxsub, "kotlin": _kotlin_maxsub, "scala": _scala_maxsub, "ruby": _ruby_maxsub, "php": _php_maxsub, "r": _r_maxsub},
    "prime-factorization": {"go": _go_primefact, "kotlin": _kotlin_primefact, "scala": _scala_primefact, "ruby": _ruby_primefact, "php": _php_primefact, "r": _r_primefact},
    "contains-duplicate-within-k": {"go": _go_dupwithink, "kotlin": _kotlin_dupwithink, "scala": _scala_dupwithink, "ruby": _ruby_dupwithink, "php": _php_dupwithink, "r": _r_dupwithink},
    "merge-overlapping-intervals": {"go": _go_mergeintervals, "kotlin": _kotlin_mergeintervals, "scala": _scala_mergeintervals, "ruby": _ruby_mergeintervals, "php": _php_mergeintervals, "r": _r_mergeintervals},
    "gcd-euclidean": {"go": _go_gcd, "kotlin": _kotlin_gcd, "scala": _scala_gcd, "ruby": _ruby_gcd, "php": _php_gcd, "r": _r_gcd},
    "house-robber": {"go": _go_houserobber, "kotlin": _kotlin_houserobber, "scala": _scala_houserobber, "ruby": _ruby_houserobber, "php": _php_houserobber, "r": _r_houserobber},
    "word-break": {"go": _go_wordbreak, "kotlin": _kotlin_wordbreak, "scala": _scala_wordbreak, "ruby": _ruby_wordbreak, "php": _php_wordbreak, "r": _r_wordbreak},
    "longest-increasing-subsequence": {"go": _go_lis, "kotlin": _kotlin_lis, "scala": _scala_lis, "ruby": _ruby_lis, "php": _php_lis, "r": _r_lis},
    "longest-common-subsequence": {"go": _go_lcs, "kotlin": _kotlin_lcs, "scala": _scala_lcs, "ruby": _ruby_lcs, "php": _php_lcs, "r": _r_lcs},
    "edit-distance": {"go": _go_editdist, "kotlin": _kotlin_editdist, "scala": _scala_editdist, "ruby": _ruby_editdist, "php": _php_editdist, "r": _r_editdist},
    "minimum-path-sum": {"go": _go_minpathsum, "kotlin": _kotlin_minpathsum, "scala": _scala_minpathsum, "ruby": _ruby_minpathsum, "php": _php_minpathsum, "r": _r_minpathsum},
    "n-queens": {"go": _go_nqueens, "kotlin": _kotlin_nqueens, "scala": _scala_nqueens, "ruby": _ruby_nqueens, "php": _php_nqueens, "r": _r_nqueens},
    "graph-bfs": {"go": _go_graphbfs, "kotlin": _kotlin_graphbfs, "scala": _scala_graphbfs, "ruby": _ruby_graphbfs, "php": _php_graphbfs, "r": _r_graphbfs},
    "dijkstra-shortest-path": {"go": _go_dijkstra, "kotlin": _kotlin_dijkstra, "scala": _scala_dijkstra, "ruby": _ruby_dijkstra, "php": _php_dijkstra, "r": _r_dijkstra},
    "kmp-string-matching": {"go": _go_kmp, "kotlin": _kotlin_kmp, "scala": _scala_kmp, "ruby": _ruby_kmp, "php": _php_kmp, "r": _r_kmp},
}


def _maybe_json(v):
    return json.loads(v) if isinstance(v, str) else v


def load_problem(con, pid):
    row = con.execute("SELECT function_contract, test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    contract = FunctionContract.from_dict(json.loads(row["function_contract"]))
    cur = con.execute(
        "SELECT id, function_args, function_expected, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = []
    for r in cur.fetchall():
        args = _maybe_json(r["function_args"])
        expected = _maybe_json(r["function_expected"])
        cases.append(FunctionCase(id=r["id"], arguments=args, expected=expected, has_expected=True,
                                   is_hidden=bool(r["is_hidden"]), order=r["order"]))
    return contract, cases, row["test_suite_version"]


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
    for pid, builders in _BUILDERS.items():
        contract, cases, tsv = load_problem(con, pid)
        for lang in _TARGET_LANGUAGES:
            if ledger.already_verified(con, pid, lang, "function", test_suite_version=tsv):
                skipped += 1
                continue
            r = await verify_one(pid, lang, contract, cases, builders[lang])
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s}(function) {pid:34s} {r['outcome']:18s} {r['detail'][:150]}", flush=True)
            if r["outcome"] == "verified":
                ledger.record_cell(con, problem_id=pid, language=lang, mode="function",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-function-core16-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
