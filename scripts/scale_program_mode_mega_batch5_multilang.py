"""Program Mode expansion, mega batch 5: covers FOUR newer languages at
once (kotlin, php, scala, r) for the same 36 mega_batch1.py problems, per
explicit user direction to stop doing one language at a time and instead
run many languages together in a single batch (matching the breadth of
mega_batch1/2's 8-core-language runs). Combined with mega_batch3 (go) and
mega_batch4 (ruby), this closes out all 6 working newer languages for this
36-problem set.
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
LANGS = ["kotlin", "php", "scala", "r"]


def rt_kotlin(kind): return "Long" if kind == "int" else "Boolean"
def rt_scala(kind): return "Long" if kind == "int" else "Boolean"


def sig(lang, shape, fn, kind):
    if lang == "kotlin":
        rt = rt_kotlin(kind)
        if shape == "arr1": return f"fun {fn}(nums: IntArray): {rt} {{"
        if shape == "arr1_int": return f"fun {fn}(nums: IntArray, extra: Int): {rt} {{"
        if shape == "int1": return f"fun {fn}(n: Long): {rt} {{"
        if shape == "int2": return f"fun {fn}(a: Long, b: Long): {rt} {{"
        if shape == "int3": return f"fun {fn}(a: Long, b: Long, c: Long): {rt} {{"
    if lang == "php":
        if shape == "arr1": return f"function {fn}($nums) {{"
        if shape == "arr1_int": return f"function {fn}($nums, $extra) {{"
        if shape == "int1": return f"function {fn}($n) {{"
        if shape == "int2": return f"function {fn}($a, $b) {{"
        if shape == "int3": return f"function {fn}($a, $b, $c) {{"
    if lang == "scala":
        rt = rt_scala(kind)
        if shape == "arr1": return f"def {fn}(nums: Array[Int]): {rt} = {{"
        if shape == "arr1_int": return f"def {fn}(nums: Array[Int], extra: Int): {rt} = {{"
        if shape == "int1": return f"def {fn}(n: Long): {rt} = {{"
        if shape == "int2": return f"def {fn}(a: Long, b: Long): {rt} = {{"
        if shape == "int3": return f"def {fn}(a: Long, b: Long, c: Long): {rt} = {{"
    if lang == "r":
        if shape == "arr1": return f"{fn} <- function(nums) {{"
        if shape == "arr1_int": return f"{fn} <- function(nums, extra) {{"
        if shape == "int1": return f"{fn} <- function(n) {{"
        if shape == "int2": return f"{fn} <- function(a, b) {{"
        if shape == "int3": return f"{fn} <- function(a, b, c) {{"
    raise ValueError((lang, shape))


def read_code(lang, shape):
    if lang == "kotlin":
        if shape == "arr1":
            return ("val data = System.`in`.bufferedReader().readText().trim().split(Regex(\"\\\\s+\"))\n"
                     "val n = data[0].toInt()\n"
                     "val nums = IntArray(n) { data[1 + it].toInt() }")
        if shape == "arr1_int":
            return read_code("kotlin", "arr1") + "\nval extra = data[1 + n].toInt()"
        if shape == "int1":
            return "val n = System.`in`.bufferedReader().readText().trim().toLong()"
        if shape == "int2":
            return ("val data = System.`in`.bufferedReader().readText().trim().split(Regex(\"\\\\s+\"))\n"
                     "val a = data[0].toLong()\nval b = data[1].toLong()")
        if shape == "int3":
            return ("val data = System.`in`.bufferedReader().readText().trim().split(Regex(\"\\\\s+\"))\n"
                     "val a = data[0].toLong()\nval b = data[1].toLong()\nval c = data[2].toLong()")
    if lang == "php":
        if shape == "arr1":
            return ("$data = preg_split('/\\s+/', trim(file_get_contents('php://stdin')));\n"
                     "$n = intval($data[0]);\n"
                     "$nums = array_map('intval', array_slice($data, 1, $n));")
        if shape == "arr1_int":
            return read_code("php", "arr1") + "\n$extra = intval($data[1 + $n]);"
        if shape == "int1":
            return "$n = intval(trim(file_get_contents('php://stdin')));"
        if shape == "int2":
            return ("$data = preg_split('/\\s+/', trim(file_get_contents('php://stdin')));\n"
                     "$a = intval($data[0]);\n$b = intval($data[1]);")
        if shape == "int3":
            return ("$data = preg_split('/\\s+/', trim(file_get_contents('php://stdin')));\n"
                     "$a = intval($data[0]);\n$b = intval($data[1]);\n$c = intval($data[2]);")
    if lang == "scala":
        if shape == "arr1":
            return ("val raw = scala.io.Source.stdin.mkString\n"
                     "val data = raw.trim.split(\"\\\\s+\")\n"
                     "val n = data(0).toInt\n"
                     "val nums = (0 until n).map(i => data(1 + i).toInt).toArray")
        if shape == "arr1_int":
            return read_code("scala", "arr1") + "\nval extra = data(1 + n).toInt"
        if shape == "int1":
            return "val raw = scala.io.Source.stdin.mkString\nval n = raw.trim.toLong"
        if shape == "int2":
            return ("val raw = scala.io.Source.stdin.mkString\n"
                     "val data = raw.trim.split(\"\\\\s+\")\n"
                     "val a = data(0).toLong\nval b = data(1).toLong")
        if shape == "int3":
            return ("val raw = scala.io.Source.stdin.mkString\n"
                     "val data = raw.trim.split(\"\\\\s+\")\n"
                     "val a = data(0).toLong\nval b = data(1).toLong\nval c = data(2).toLong")
    if lang == "r":
        base = "con <- file(\"stdin\"); lines <- readLines(con); close(con)\n"
        if shape == "arr1":
            return (base + "data <- as.numeric(strsplit(paste(lines, collapse=\" \"), \"\\\\s+\")[[1]])\n"
                     "n <- as.integer(data[1])\n"
                     "nums <- if (n > 0) as.integer(data[2:(1+n)]) else integer(0)")
        if shape == "arr1_int":
            return read_code("r", "arr1") + "\nextra <- as.integer(data[2+n])"
        if shape == "int1":
            return base + "n <- as.numeric(trimws(paste(lines, collapse=\" \")))"
        if shape == "int2":
            return (base + "data <- as.numeric(strsplit(paste(lines, collapse=\" \"), \"\\\\s+\")[[1]])\n"
                     "a <- data[1]; b <- data[2]")
        if shape == "int3":
            return (base + "data <- as.numeric(strsplit(paste(lines, collapse=\" \"), \"\\\\s+\")[[1]])\n"
                     "a <- data[1]; b <- data[2]; c <- data[3]")
    raise ValueError((lang, shape))


def call_args(lang, shape):
    if lang == "r":
        if shape == "arr1": return "nums"
        if shape == "arr1_int": return "nums, extra"
        if shape == "int1": return "n"
        if shape == "int2": return "a, b"
        if shape == "int3": return "a, b, c"
    if lang == "php":
        if shape == "arr1": return "$nums"
        if shape == "arr1_int": return "$nums, $extra"
        if shape == "int1": return "$n"
        if shape == "int2": return "$a, $b"
        if shape == "int3": return "$a, $b, $c"
    if shape == "arr1": return "nums"
    if shape == "arr1_int": return "nums, extra"
    if shape == "int1": return "n"
    if shape == "int2": return "a, b"
    if shape == "int3": return "a, b, c"
    raise ValueError(shape)


def print_stmt(lang, kind, wrong):
    if lang == "kotlin":
        if kind == "int":
            delta = 1 if wrong else 0
            return f"println(result + {delta}L)"
        return f"println({'!' if wrong else ''}result)"
    if lang == "php":
        if kind == "int":
            delta = 1 if wrong else 0
            return f"echo ($result + {delta}), \"\\n\";"
        neg = "!" if wrong else ""
        return f"echo (({neg}$result) ? \"true\" : \"false\"), \"\\n\";"
    if lang == "scala":
        if kind == "int":
            delta = 1 if wrong else 0
            return f"println(result + {delta}L)"
        return f"println({'!' if wrong else ''}result)"
    if lang == "r":
        if kind == "int":
            delta = 1 if wrong else 0
            return f"cat(result + {delta}, \"\\n\")"
        neg = "!" if wrong else ""
        return f"cat(ifelse({neg}result, \"true\", \"false\"), \"\\n\")"
    raise ValueError((lang, kind))


def assemble(lang, shape, fn, kind, body, wrong):
    read = read_code(lang, shape)
    signature = sig(lang, shape, fn, kind)
    args = call_args(lang, shape)
    p = print_stmt(lang, kind, wrong)

    if lang == "kotlin":
        func = f"{signature}\n{body}\nreturn result\n}}"
        call = f"val result = {fn}({args})"
        return f"{func}\n\nfun main() {{\n{read}\n{call}\n{p}\n}}\n"
    if lang == "php":
        func = f"{signature}\n{body}\nreturn $result;\n}}"
        call = f"$result = {fn}({args});"
        return f"<?php\n{func}\n\n{read}\n{call}\n{p}\n"
    if lang == "scala":
        func = f"{signature}\n{body}\nresult\n}}"
        call = f"val result = {fn}({args})"
        return f"{func}\n\n@main def mainEntry(): Unit = {{\n{read}\n{call}\n{p}\n}}\n"
    if lang == "r":
        func = f"{signature}\n{body}\nreturn(result)\n}}"
        call = f"result <- {fn}({args})"
        return f"options(scipen = 999)\n\n{func}\n\n{read}\n{call}\n{p}\n"
    raise ValueError(lang)


PROBLEMS: dict[str, dict] = {}


def add(pid, shape, fn, kind, bodies):
    PROBLEMS[pid] = {"shape": shape, "fn": fn, "kind": kind, "bodies": bodies}


add("bitonic-peak-index", "arr1", "peakIndex", "int", {
    "kotlin": "var lo = 0\nvar hi = nums.size - 1\nwhile (lo < hi) {\n  val mid = (lo + hi) / 2\n  if (nums[mid] < nums[mid + 1]) lo = mid + 1 else hi = mid\n}\nval result = lo.toLong()",
    "php": "$lo = 0; $hi = count($nums) - 1;\nwhile ($lo < $hi) {\n  $mid = intdiv($lo + $hi, 2);\n  if ($nums[$mid] < $nums[$mid + 1]) { $lo = $mid + 1; } else { $hi = $mid; }\n}\n$result = $lo;",
    "scala": "var lo = 0\nvar hi = nums.length - 1\nwhile (lo < hi) {\n  val mid = (lo + hi) / 2\n  if (nums(mid) < nums(mid + 1)) lo = mid + 1 else hi = mid\n}\nval result: Long = lo",
    "r": "lo <- 0; hi <- length(nums) - 1\nwhile (lo < hi) {\n  mid <- (lo + hi) %/% 2\n  if (nums[mid+1] < nums[mid+2]) { lo <- mid + 1 } else { hi <- mid }\n}\nresult <- lo",
})

add("find-minimum-rotated-sorted-array", "arr1", "findMin", "int", {
    "kotlin": "var lo = 0\nvar hi = nums.size - 1\nwhile (lo < hi) {\n  val mid = (lo + hi) / 2\n  if (nums[mid] > nums[hi]) lo = mid + 1 else hi = mid\n}\nval result = nums[lo].toLong()",
    "php": "$lo = 0; $hi = count($nums) - 1;\nwhile ($lo < $hi) {\n  $mid = intdiv($lo + $hi, 2);\n  if ($nums[$mid] > $nums[$hi]) { $lo = $mid + 1; } else { $hi = $mid; }\n}\n$result = $nums[$lo];",
    "scala": "var lo = 0\nvar hi = nums.length - 1\nwhile (lo < hi) {\n  val mid = (lo + hi) / 2\n  if (nums(mid) > nums(hi)) lo = mid + 1 else hi = mid\n}\nval result: Long = nums(lo)",
    "r": "lo <- 0; hi <- length(nums) - 1\nwhile (lo < hi) {\n  mid <- (lo + hi) %/% 2\n  if (nums[mid+1] > nums[hi+1]) { lo <- mid + 1 } else { hi <- mid }\n}\nresult <- nums[lo+1]",
})

add("count-occurrences-sorted", "arr1_int", "countOccurrences", "int", {
    "kotlin": "val result = nums.count { it == extra }.toLong()",
    "php": "$result = 0;\nforeach ($nums as $x) { if ($x == $extra) $result++; }",
    "scala": "val result: Long = nums.count(_ == extra)",
    "r": "result <- sum(nums == extra)",
})

add("last-occurrence", "arr1_int", "lastOccurrence", "int", {
    "kotlin": "var lo = 0\nvar hi = nums.size - 1\nvar ans = -1\nwhile (lo <= hi) {\n  val mid = (lo + hi) / 2\n  if (nums[mid] == extra) { ans = mid; lo = mid + 1 }\n  else if (nums[mid] < extra) lo = mid + 1 else hi = mid - 1\n}\nval result = ans.toLong()",
    "php": "$lo = 0; $hi = count($nums) - 1; $ans = -1;\nwhile ($lo <= $hi) {\n  $mid = intdiv($lo + $hi, 2);\n  if ($nums[$mid] == $extra) { $ans = $mid; $lo = $mid + 1; }\n  elseif ($nums[$mid] < $extra) { $lo = $mid + 1; } else { $hi = $mid - 1; }\n}\n$result = $ans;",
    "scala": "var lo = 0\nvar hi = nums.length - 1\nvar ans = -1\nwhile (lo <= hi) {\n  val mid = (lo + hi) / 2\n  if (nums(mid) == extra) { ans = mid; lo = mid + 1 }\n  else if (nums(mid) < extra) lo = mid + 1 else hi = mid - 1\n}\nval result: Long = ans",
    "r": "lo <- 0; hi <- length(nums) - 1; ans <- -1\nwhile (lo <= hi) {\n  mid <- (lo + hi) %/% 2\n  if (nums[mid+1] == extra) { ans <- mid; lo <- mid + 1 }\n  else if (nums[mid+1] < extra) { lo <- mid + 1 } else { hi <- mid - 1 }\n}\nresult <- ans",
})

add("koko-eating-bananas", "arr1_int", "minEatingSpeed", "int", {
    "kotlin": "var lo = 1L\nvar hi = nums.max()!!.toLong()\nwhile (lo < hi) {\n  val mid = (lo + hi) / 2\n  var h = 0L\n  for (p in nums) h += (p + mid - 1) / mid\n  if (h <= extra) hi = mid else lo = mid + 1\n}\nval result = lo",
    "php": "$lo = 1; $hi = max($nums);\nwhile ($lo < $hi) {\n  $mid = intdiv($lo + $hi, 2);\n  $h = 0;\n  foreach ($nums as $p) { $h += intdiv($p + $mid - 1, $mid); }\n  if ($h <= $extra) { $hi = $mid; } else { $lo = $mid + 1; }\n}\n$result = $lo;",
    "scala": "var lo = 1L\nvar hi = nums.max.toLong\nwhile (lo < hi) {\n  val mid = (lo + hi) / 2\n  var h = 0L\n  for (p <- nums) h += (p + mid - 1) / mid\n  if (h <= extra) hi = mid else lo = mid + 1\n}\nval result: Long = lo",
    "r": "lo <- 1; hi <- max(nums)\nwhile (lo < hi) {\n  mid <- (lo + hi) %/% 2\n  h <- sum(ceiling(nums / mid))\n  if (h <= extra) { hi <- mid } else { lo <- mid + 1 }\n}\nresult <- lo",
})

add("kth-largest-element", "arr1_int", "kthLargest", "int", {
    "kotlin": "val s = nums.sortedArray()\nval result = s[s.size - extra].toLong()",
    "php": "$s = $nums;\nsort($s);\n$result = $s[count($s) - $extra];",
    "scala": "val s = nums.sorted\nval result: Long = s(s.length - extra)",
    "r": "s <- sort(nums)\nresult <- s[length(s) - extra + 1]",
})

add("largest-rectangle-in-histogram", "arr1", "largestRectangle", "int", {
    "kotlin": ("val h = nums.toMutableList(); h.add(0)\nval st = ArrayDeque<Int>()\nvar best = 0L\nfor (i in h.indices) {\n"
               "  while (st.isNotEmpty() && h[st.last()] >= h[i]) {\n    val top = st.removeLast()\n    val width = if (st.isEmpty()) i else i - st.last() - 1\n    val area = h[top].toLong() * width\n    if (area > best) best = area\n  }\n  st.addLast(i)\n}\nval result = best"),
    "php": ("$h = $nums; $h[] = 0;\n$st = [];\n$best = 0;\nfor ($i = 0; $i < count($h); $i++) {\n"
            "  while (!empty($st) && $h[end($st)] >= $h[$i]) {\n    $top = array_pop($st);\n    $width = empty($st) ? $i : $i - end($st) - 1;\n    $area = $h[$top] * $width;\n    if ($area > $best) $best = $area;\n  }\n  $st[] = $i;\n}\n$result = $best;"),
    "scala": ("val h = (nums.toBuffer :+ 0)\nval st = scala.collection.mutable.ArrayBuffer[Int]()\nvar best = 0L\nfor (i <- h.indices) {\n"
              "  while (st.nonEmpty && h(st.last) >= h(i)) {\n    val top = st.remove(st.length - 1)\n    val width = if (st.isEmpty) i else i - st.last - 1\n    val area = h(top).toLong * width\n    if (area > best) best = area\n  }\n  st += i\n}\nval result: Long = best"),
    "r": ("h <- c(nums, 0)\nst <- integer(0)\nbest <- 0\nfor (i in 1:length(h)) {\n"
          "  while (length(st) > 0 && h[st[length(st)]] >= h[i]) {\n    top <- st[length(st)]; st <- st[-length(st)]\n"
          "    width <- if (length(st) == 0) i - 1 else i - st[length(st)] - 1\n    area <- h[top] * width\n    if (area > best) best <- area\n  }\n  st <- c(st, i)\n}\nresult <- best"),
})

add("longest-bitonic-subsequence", "arr1", "longestBitonicSubsequence", "int", {
    "kotlin": ("val m = nums.size\nval inc = LongArray(m) { 1L }\nval dec = LongArray(m) { 1L }\n"
               "for (i in 0 until m) for (j in 0 until i) if (nums[j] < nums[i] && inc[j] + 1 > inc[i]) inc[i] = inc[j] + 1\n"
               "for (i in m - 1 downTo 0) for (j in m - 1 downTo i + 1) if (nums[j] < nums[i] && dec[j] + 1 > dec[i]) dec[i] = dec[j] + 1\n"
               "var best = 0L\nfor (i in 0 until m) { val v = inc[i] + dec[i] - 1; if (v > best) best = v }\nval result = best"),
    "php": ("$m = count($nums);\n$inc = array_fill(0, $m, 1); $dec = array_fill(0, $m, 1);\n"
            "for ($i = 0; $i < $m; $i++) { for ($j = 0; $j < $i; $j++) { if ($nums[$j] < $nums[$i] && $inc[$j] + 1 > $inc[$i]) $inc[$i] = $inc[$j] + 1; } }\n"
            "for ($i = $m - 1; $i >= 0; $i--) { for ($j = $m - 1; $j > $i; $j--) { if ($nums[$j] < $nums[$i] && $dec[$j] + 1 > $dec[$i]) $dec[$i] = $dec[$j] + 1; } }\n"
            "$best = 0;\nfor ($i = 0; $i < $m; $i++) { $v = $inc[$i] + $dec[$i] - 1; if ($v > $best) $best = $v; }\n$result = $best;"),
    "scala": ("val m = nums.length\nval inc = Array.fill(m)(1L)\nval dec = Array.fill(m)(1L)\n"
              "for (i <- 0 until m; j <- 0 until i) if (nums(j) < nums(i) && inc(j) + 1 > inc(i)) inc(i) = inc(j) + 1\n"
              "for (i <- (m - 1) to 0 by -1; j <- (m - 1) to (i + 1) by -1) if (nums(j) < nums(i) && dec(j) + 1 > dec(i)) dec(i) = dec(j) + 1\n"
              "var best = 0L\nfor (i <- 0 until m) { val v = inc(i) + dec(i) - 1; if (v > best) best = v }\nval result: Long = best"),
    "r": ("m <- length(nums)\ninc <- rep(1, m); dec <- rep(1, m)\n"
          "for (i in 1:m) { for (j in 1:m) { if (j < i && nums[j] < nums[i] && inc[j] + 1 > inc[i]) inc[i] <- inc[j] + 1 } }\n"
          "for (i in m:1) { for (j in m:1) { if (j > i && nums[j] < nums[i] && dec[j] + 1 > dec[i]) dec[i] <- dec[j] + 1 } }\n"
          "best <- 0\nfor (i in 1:m) { v <- inc[i] + dec[i] - 1; if (v > best) best <- v }\nresult <- best"),
})

add("max-consecutive-ones-with-k-flips", "arr1_int", "maxConsecutiveOnes", "int", {
    "kotlin": "var left = 0\nvar zeros = 0\nvar best = 0\nfor (right in nums.indices) {\n  if (nums[right] == 0) zeros++\n  while (zeros > extra) { if (nums[left] == 0) zeros--; left++ }\n  val len = right - left + 1\n  if (len > best) best = len\n}\nval result = best.toLong()",
    "php": "$left = 0; $zeros = 0; $best = 0;\nfor ($right = 0; $right < count($nums); $right++) {\n  if ($nums[$right] == 0) $zeros++;\n  while ($zeros > $extra) { if ($nums[$left] == 0) $zeros--; $left++; }\n  $len = $right - $left + 1;\n  if ($len > $best) $best = $len;\n}\n$result = $best;",
    "scala": "var left = 0\nvar zeros = 0\nvar best = 0\nfor (right <- nums.indices) {\n  if (nums(right) == 0) zeros += 1\n  while (zeros > extra) { if (nums(left) == 0) zeros -= 1; left += 1 }\n  val len = right - left + 1\n  if (len > best) best = len\n}\nval result: Long = best",
    "r": "left <- 0; zeros <- 0; best <- 0\nfor (right in 0:(length(nums)-1)) {\n  if (nums[right+1] == 0) zeros <- zeros + 1\n  while (zeros > extra) { if (nums[left+1] == 0) zeros <- zeros - 1; left <- left + 1 }\n  len <- right - left + 1\n  if (len > best) best <- len\n}\nresult <- best",
})

add("max-sum-subarray-fixed-k", "arr1_int", "maxSumFixedK", "int", {
    "kotlin": "var sum = 0L\nfor (i in 0 until extra) sum += nums[i]\nvar best = sum\nfor (i in extra until nums.size) { sum += nums[i] - nums[i - extra]; if (sum > best) best = sum }\nval result = best",
    "php": "$sum = 0;\nfor ($i = 0; $i < $extra; $i++) $sum += $nums[$i];\n$best = $sum;\nfor ($i = $extra; $i < count($nums); $i++) { $sum += $nums[$i] - $nums[$i - $extra]; if ($sum > $best) $best = $sum; }\n$result = $best;",
    "scala": "var sum = nums.slice(0, extra).map(_.toLong).sum\nvar best = sum\nfor (i <- extra until nums.length) { sum += nums(i) - nums(i - extra); if (sum > best) best = sum }\nval result: Long = best",
    "r": "total <- sum(nums[1:extra])\nbest <- total\ni <- extra\nwhile (i <= length(nums) - 1) { total <- total + nums[i+1] - nums[i-extra+1]; if (total > best) best <- total; i <- i + 1 }\nresult <- best",
})

add("maximum-subarray-circular", "arr1", "maxSubarrayCircular", "int", {
    "kotlin": ("var total = 0L; var maxCur = 0L; var maxBest = Long.MIN_VALUE; var minCur = 0L; var minBest = Long.MAX_VALUE\n"
               "for (xx in nums) {\n  val x = xx.toLong()\n  total += x\n  maxCur = maxOf(x, maxCur + x); maxBest = maxOf(maxBest, maxCur)\n  minCur = minOf(x, minCur + x); minBest = minOf(minBest, minCur)\n}\nval result = if (maxBest < 0) maxBest else maxOf(maxBest, total - minBest)"),
    "php": ("$total = 0; $maxCur = 0; $maxBest = -PHP_INT_MAX; $minCur = 0; $minBest = PHP_INT_MAX;\n"
            "foreach ($nums as $x) {\n  $total += $x;\n  $maxCur = max($x, $maxCur + $x); $maxBest = max($maxBest, $maxCur);\n  $minCur = min($x, $minCur + $x); $minBest = min($minBest, $minCur);\n}\n$result = $maxBest < 0 ? $maxBest : max($maxBest, $total - $minBest);"),
    "scala": ("var total = 0L; var maxCur = 0L; var maxBest = Long.MinValue; var minCur = 0L; var minBest = Long.MaxValue\n"
              "for (xx <- nums) {\n  val x = xx.toLong\n  total += x\n  maxCur = math.max(x, maxCur + x); maxBest = math.max(maxBest, maxCur)\n  minCur = math.min(x, minCur + x); minBest = math.min(minBest, minCur)\n}\nval result: Long = if (maxBest < 0) maxBest else math.max(maxBest, total - minBest)"),
    "r": ("total <- 0; maxCur <- 0; maxBest <- -Inf; minCur <- 0; minBest <- Inf\n"
          "for (x in nums) {\n  total <- total + x\n  maxCur <- max(x, maxCur + x); maxBest <- max(maxBest, maxCur)\n  minCur <- min(x, minCur + x); minBest <- min(minBest, minCur)\n}\nresult <- if (maxBest < 0) maxBest else max(maxBest, total - minBest)"),
})

add("maximum-xor-of-two-numbers", "arr1", "findMaximumXor", "int", {
    "kotlin": "var best = 0L\nfor (i in nums.indices) for (j in i + 1 until nums.size) { val v = (nums[i] xor nums[j]).toLong(); if (v > best) best = v }\nval result = best",
    "php": "$best = 0;\nfor ($i = 0; $i < count($nums); $i++) { for ($j = $i + 1; $j < count($nums); $j++) { $v = $nums[$i] ^ $nums[$j]; if ($v > $best) $best = $v; } }\n$result = $best;",
    "scala": "var best = 0L\nfor (i <- nums.indices; j <- (i + 1) until nums.length) { val v = (nums(i) ^ nums(j)).toLong; if (v > best) best = v }\nval result: Long = best",
    "r": "best <- 0\nfor (i in 1:length(nums)) { for (j in 1:length(nums)) { if (j > i) { v <- bitwXor(nums[i], nums[j]); if (v > best) best <- v } } }\nresult <- best",
})

add("middle-of-linked-list", "arr1", "middleNode", "int", {
    "kotlin": "var slow = 0\nvar fast = 0\nval m = nums.size\nwhile (fast < m - 1) { slow++; fast += 2 }\nval result = nums[slow].toLong()",
    "php": "$slow = 0; $fast = 0; $m = count($nums);\nwhile ($fast < $m - 1) { $slow++; $fast += 2; }\n$result = $nums[$slow];",
    "scala": "var slow = 0\nvar fast = 0\nval m = nums.length\nwhile (fast < m - 1) { slow += 1; fast += 2 }\nval result: Long = nums(slow)",
    "r": "slow <- 0; fast <- 0; m <- length(nums)\nwhile (fast < m - 1) { slow <- slow + 1; fast <- fast + 2 }\nresult <- nums[slow+1]",
})

add("min-subarray-len-target-sum", "arr1_int", "minSubarrayLen", "int", {
    "kotlin": "var left = 0\nvar sum = 0L\nvar best = Long.MAX_VALUE\nfor (right in nums.indices) {\n  sum += nums[right]\n  while (sum >= extra) { if ((right - left + 1).toLong() < best) best = (right - left + 1).toLong(); sum -= nums[left]; left++ }\n}\nval result = if (best == Long.MAX_VALUE) 0L else best",
    "php": "$left = 0; $sum = 0; $best = PHP_INT_MAX;\nfor ($right = 0; $right < count($nums); $right++) {\n  $sum += $nums[$right];\n  while ($sum >= $extra) { if ($right - $left + 1 < $best) $best = $right - $left + 1; $sum -= $nums[$left]; $left++; }\n}\n$result = ($best == PHP_INT_MAX) ? 0 : $best;",
    "scala": "var left = 0\nvar sum = 0L\nvar best = Long.MaxValue\nfor (right <- nums.indices) {\n  sum += nums(right)\n  while (sum >= extra) { if ((right - left + 1).toLong < best) best = (right - left + 1).toLong; sum -= nums(left); left += 1 }\n}\nval result: Long = if (best == Long.MaxValue) 0L else best",
    "r": "left <- 0; sum <- 0; best <- Inf\nfor (right in 0:(length(nums)-1)) {\n  sum <- sum + nums[right+1]\n  while (sum >= extra) { len <- right - left + 1; if (len < best) best <- len; sum <- sum - nums[left+1]; left <- left + 1 }\n}\nresult <- if (is.infinite(best)) 0 else best",
})

add("partition-equal-subset-sum", "arr1", "canPartition", "bool", {
    "kotlin": ("val total = nums.sumOf { it.toLong() }\nval result: Boolean\nif (total % 2 != 0L) {\n  result = false\n} else {\n"
               "  val target = (total / 2).toInt()\n  val dp = BooleanArray(target + 1); dp[0] = true\n"
               "  for (x in nums) { for (j in target downTo x) { if (dp[j - x]) dp[j] = true } }\n  result = dp[target]\n}"),
    "php": ("$total = array_sum($nums);\nif ($total % 2 != 0) {\n  $result = false;\n} else {\n"
            "  $target = intdiv($total, 2);\n  $dp = array_fill(0, $target + 1, false); $dp[0] = true;\n"
            "  foreach ($nums as $x) { for ($j = $target; $j >= $x; $j--) { if ($dp[$j - $x]) $dp[$j] = true; } }\n  $result = $dp[$target];\n}"),
    "scala": ("val total = nums.map(_.toLong).sum\nval result: Boolean = if (total % 2 != 0) {\n  false\n} else {\n"
              "  val target = (total / 2).toInt\n  val dp = Array.fill(target + 1)(false); dp(0) = true\n"
              "  for (x <- nums) { for (j <- target to x by -1) { if (dp(j - x)) dp(j) = true } }\n  dp(target)\n}"),
    "r": ("total <- sum(nums)\nif (total %% 2 != 0) {\n  result <- FALSE\n} else {\n"
          "  target <- total %/% 2\n  dp <- rep(FALSE, target + 1); dp[1] <- TRUE\n"
          "  for (x in nums) { if (x <= target) { for (j in target:x) { if (dp[j - x + 1]) dp[j + 1] <- TRUE } } }\n  result <- dp[target + 1]\n}"),
})

add("perfect-squares-min-count", "int1", "numSquares", "int", {
    "kotlin": "val N = n.toInt()\nval dp = LongArray(N + 1) { Long.MAX_VALUE / 2 }\ndp[0] = 0\nfor (i in 1..N) { var j = 1; while (j * j <= i) { if (dp[i - j * j] + 1 < dp[i]) dp[i] = dp[i - j * j] + 1; j++ } }\nval result = dp[N]",
    "php": "$N = intval($n);\n$dp = array_fill(0, $N + 1, PHP_INT_MAX / 2);\n$dp[0] = 0;\nfor ($i = 1; $i <= $N; $i++) { for ($j = 1; $j * $j <= $i; $j++) { if ($dp[$i - $j * $j] + 1 < $dp[$i]) $dp[$i] = $dp[$i - $j * $j] + 1; } }\n$result = $dp[$N];",
    "scala": "val N = n.toInt\nval dp = Array.fill(N + 1)(Long.MaxValue / 2)\ndp(0) = 0\nfor (i <- 1 to N) { var j = 1; while (j * j <= i) { if (dp(i - j * j) + 1 < dp(i)) dp(i) = dp(i - j * j) + 1; j += 1 } }\nval result: Long = dp(N)",
    "r": "N <- as.integer(n)\ndp <- rep(Inf, N + 1); dp[1] <- 0\nif (N >= 1) { for (i in 1:N) { j <- 1; while (j * j <= i) { if (dp[i - j * j + 1] + 1 < dp[i + 1]) dp[i + 1] <- dp[i - j * j + 1] + 1; j <- j + 1 } } }\nresult <- dp[N + 1]",
})

add("rod-cutting", "arr1", "rodCutting", "int", {
    "kotlin": "val m = nums.size\nval dp = LongArray(m + 1)\nfor (i in 1..m) {\n  var best = Long.MIN_VALUE\n  for (cut in 1..i) { val v = nums[cut - 1] + dp[i - cut]; if (v > best) best = v }\n  dp[i] = best\n}\nval result = dp[m]",
    "php": "$m = count($nums);\n$dp = array_fill(0, $m + 1, 0);\nfor ($i = 1; $i <= $m; $i++) {\n  $best = -PHP_INT_MAX;\n  for ($cut = 1; $cut <= $i; $cut++) { $v = $nums[$cut - 1] + $dp[$i - $cut]; if ($v > $best) $best = $v; }\n  $dp[$i] = $best;\n}\n$result = $dp[$m];",
    "scala": "val m = nums.length\nval dp = Array.fill(m + 1)(0L)\nfor (i <- 1 to m) {\n  var best = Long.MinValue\n  for (cut <- 1 to i) { val v = nums(cut - 1) + dp(i - cut); if (v > best) best = v }\n  dp(i) = best\n}\nval result: Long = dp(m)",
    "r": "m <- length(nums)\ndp <- rep(0, m + 1)\nfor (i in 1:m) {\n  best <- -Inf\n  for (cut in 1:i) { v <- nums[cut] + dp[i - cut + 1]; if (v > best) best <- v }\n  dp[i + 1] <- best\n}\nresult <- dp[m + 1]",
})

add("single-number-ii", "arr1", "singleNumber", "int", {
    "kotlin": ("var result = 0L\nfor (bit in 0 until 32) {\n  var cnt = 0L\n  for (x in nums) { val ux = if (x < 0) x.toLong() + 4294967296L else x.toLong(); cnt += (ux shr bit) and 1L }\n"
               "  if (cnt % 3 != 0L) result += (1L shl bit)\n}\nif (result >= 2147483648L) result -= 4294967296L"),
    "php": ("$result = 0;\nfor ($bit = 0; $bit < 32; $bit++) {\n  $cnt = 0;\n  foreach ($nums as $x) { $ux = $x < 0 ? $x + 4294967296 : $x; $cnt += ($ux >> $bit) & 1; }\n"
            "  if ($cnt % 3 != 0) $result += (1 << $bit);\n}\nif ($result >= 2147483648) $result -= 4294967296;"),
    "scala": ("var result = 0L\nfor (bit <- 0 until 32) {\n  var cnt = 0L\n  for (x <- nums) { val ux = if (x < 0) x.toLong + 4294967296L else x.toLong; cnt += (ux >> bit) & 1L }\n"
              "  if (cnt % 3 != 0) result += (1L << bit)\n}\nif (result >= 2147483648L) result -= 4294967296L"),
    "r": ("result <- 0\nfor (bit in 0:31) {\n  cnt <- 0\n  for (x in nums) { ux <- if (x < 0) x + 4294967296 else x; cnt <- cnt + bitwAnd(bitwShiftR(as.integer(ux %% 4294967296), bit), 1) }\n"
          "  if (cnt %% 3 != 0) result <- result + 2^bit\n}\nif (result >= 2147483648) result <- result - 4294967296"),
})

add("subset-sum", "arr1_int", "subsetSum", "bool", {
    "kotlin": "val dp = BooleanArray(extra + 1); dp[0] = true\nfor (x in nums) { if (x <= extra) { for (j in extra downTo x) { if (dp[j - x]) dp[j] = true } } }\nval result = if (extra >= 0) dp[extra] else false",
    "php": "$dp = array_fill(0, $extra + 1, false); $dp[0] = true;\nforeach ($nums as $x) { if ($x <= $extra) { for ($j = $extra; $j >= $x; $j--) { if ($dp[$j - $x]) $dp[$j] = true; } } }\n$result = ($extra >= 0) ? $dp[$extra] : false;",
    "scala": "val dp = Array.fill(extra + 1)(false); dp(0) = true\nfor (x <- nums) { if (x <= extra) { for (j <- extra to x by -1) { if (dp(j - x)) dp(j) = true } } }\nval result: Boolean = if (extra >= 0) dp(extra) else false",
    "r": "dp <- rep(FALSE, extra + 1); dp[1] <- TRUE\nfor (x in nums) { if (x <= extra) { for (j in extra:x) { if (dp[j - x + 1]) dp[j + 1] <- TRUE } } }\nresult <- if (extra >= 0) dp[extra + 1] else FALSE",
})

add("target-sum-ways", "arr1_int", "findTargetSumWays", "int", {
    "kotlin": ("val total = nums.sumOf { it.toLong() }\nval e = extra.toLong()\nval result: Long\n"
               "if ((total + e) % 2 != 0L || total < Math.abs(e)) {\n  result = 0L\n} else {\n"
               "  val s = ((total + e) / 2).toInt()\n  val dp = LongArray(s + 1); dp[0] = 1\n"
               "  for (x in nums) { for (j in s downTo x) { dp[j] += dp[j - x] } }\n  result = dp[s]\n}"),
    "php": ("$total = array_sum($nums);\nif (($total + $extra) % 2 != 0 || $total < abs($extra)) {\n  $result = 0;\n} else {\n"
            "  $s = intdiv($total + $extra, 2);\n  $dp = array_fill(0, $s + 1, 0); $dp[0] = 1;\n"
            "  foreach ($nums as $x) { for ($j = $s; $j >= $x; $j--) { $dp[$j] += $dp[$j - $x]; } }\n  $result = $dp[$s];\n}"),
    "scala": ("val total = nums.map(_.toLong).sum\nval e = extra.toLong\nval result: Long = if ((total + e) % 2 != 0 || total < math.abs(e)) {\n  0L\n} else {\n"
              "  val s = ((total + e) / 2).toInt\n  val dp = Array.fill(s + 1)(0L); dp(0) = 1\n"
              "  for (x <- nums) { for (j <- s to x by -1) { dp(j) += dp(j - x) } }\n  dp(s)\n}"),
    "r": ("total <- sum(nums)\nif ((total + extra) %% 2 != 0 || total < abs(extra)) {\n  result <- 0\n} else {\n"
          "  s <- (total + extra) %/% 2\n  dp <- rep(0, s + 1); dp[1] <- 1\n"
          "  for (x in nums) { if (x <= s) { for (j in s:x) { dp[j + 1] <- dp[j + 1] + dp[j - x + 1] } } }\n  result <- dp[s + 1]\n}"),
})

add("two-sum-count-pairs", "arr1_int", "countPairs", "int", {
    "kotlin": ("val freq = HashMap<Int, Long>()\nfor (x in nums) freq[x] = (freq[x] ?: 0L) + 1L\nvar result = 0L\n"
               "for ((v, c) in freq) {\n  val comp = extra - v\n  if (comp == v) result += c * (c - 1) / 2\n  else if (comp > v) result += c * (freq[comp] ?: 0L)\n}"),
    "php": ("$freq = [];\nforeach ($nums as $x) { $freq[$x] = ($freq[$x] ?? 0) + 1; }\n$result = 0;\n"
            "foreach ($freq as $v => $c) {\n  $comp = $extra - $v;\n  if ($comp == $v) { $result += $c * ($c - 1) / 2; }\n  elseif ($comp > $v) { $result += $c * ($freq[$comp] ?? 0); }\n}"),
    "scala": ("val freq = scala.collection.mutable.HashMap[Int, Long]().withDefaultValue(0L)\nfor (x <- nums) freq(x) += 1\nvar result = 0L\n"
              "for ((v, c) <- freq) {\n  val comp = extra - v\n  if (comp == v) result += c * (c - 1) / 2\n  else if (comp > v) result += c * freq(comp)\n}"),
    "r": ("freq <- table(nums)\nresult <- 0\nvals <- as.integer(names(freq))\nfor (i in seq_along(vals)) {\n  v <- vals[i]; c <- as.numeric(freq[i])\n  comp <- extra - v\n  if (comp == v) { result <- result + c * (c - 1) / 2 }\n  else if (comp > v && as.character(comp) %in% names(freq)) { result <- result + c * as.numeric(freq[as.character(comp)]) }\n}"),
})

add("unique-permutations-count", "arr1", "countUniquePermutations", "int", {
    "kotlin": ("val freq = HashMap<Int, Long>()\nfor (x in nums) freq[x] = (freq[x] ?: 0L) + 1L\n"
               "var num = 1L\nfor (i in 2..nums.size) num *= i\nvar denom = 1L\nfor (c in freq.values) { var f = 1L; for (i in 2..c.toInt()) f *= i; denom *= f }\nval result = num / denom"),
    "php": ("$freq = [];\nforeach ($nums as $x) { $freq[$x] = ($freq[$x] ?? 0) + 1; }\n"
            "$num = 1;\nfor ($i = 2; $i <= count($nums); $i++) $num *= $i;\n$denom = 1;\nforeach ($freq as $c) { $f = 1; for ($i = 2; $i <= $c; $i++) $f *= $i; $denom *= $f; }\n$result = intdiv($num, $denom);"),
    "scala": ("val freq = scala.collection.mutable.HashMap[Int, Long]().withDefaultValue(0L)\nfor (x <- nums) freq(x) += 1\n"
              "var num = 1L\nfor (i <- 2 to nums.length) num *= i\nvar denom = 1L\nfor (c <- freq.values) { var f = 1L; for (i <- 2 to c.toInt) f *= i; denom *= f }\nval result: Long = num / denom"),
    "r": ("freq <- table(nums)\nnum <- factorial(length(nums))\ndenom <- prod(factorial(as.numeric(freq)))\nresult <- round(num / denom)"),
})

add("ship-packages-within-days", "arr1_int", "shipWithinDays", "int", {
    "kotlin": ("var lo = nums.max()!!.toLong()\nvar hi = nums.sumOf { it.toLong() }\nwhile (lo < hi) {\n  val mid = (lo + hi) / 2\n"
               "  var days = 1L; var cur = 0L\n  for (w in nums) { if (cur + w > mid) { days++; cur = w.toLong() } else { cur += w } }\n"
               "  if (days <= extra) hi = mid else lo = mid + 1\n}\nval result = lo"),
    "php": ("$lo = max($nums); $hi = array_sum($nums);\nwhile ($lo < $hi) {\n  $mid = intdiv($lo + $hi, 2);\n"
            "  $days = 1; $cur = 0;\n  foreach ($nums as $w) { if ($cur + $w > $mid) { $days++; $cur = $w; } else { $cur += $w; } }\n"
            "  if ($days <= $extra) { $hi = $mid; } else { $lo = $mid + 1; }\n}\n$result = $lo;"),
    "scala": ("var lo = nums.max.toLong\nvar hi = nums.map(_.toLong).sum\nwhile (lo < hi) {\n  val mid = (lo + hi) / 2\n"
              "  var days = 1L; var cur = 0L\n  for (w <- nums) { if (cur + w > mid) { days += 1; cur = w } else { cur += w } }\n"
              "  if (days <= extra) hi = mid else lo = mid + 1\n}\nval result: Long = lo"),
    "r": ("lo <- max(nums); hi <- sum(nums)\nwhile (lo < hi) {\n  mid <- (lo + hi) %/% 2\n  days <- 1; cur <- 0\n"
          "  for (w in nums) { if (cur + w > mid) { days <- days + 1; cur <- w } else { cur <- cur + w } }\n"
          "  if (days <= extra) { hi <- mid } else { lo <- mid + 1 }\n}\nresult <- lo"),
})

add("subarray-product-less-than-k", "arr1_int", "numSubarrayProductLessThanK", "int", {
    "kotlin": ("val result: Long\nif (extra <= 1) {\n  result = 0L\n} else {\n  var left = 0\n  var prod = 1L\n  var count = 0L\n"
               "  for (right in nums.indices) {\n    prod *= nums[right]\n    while (prod >= extra) { prod /= nums[left]; left++ }\n    count += (right - left + 1)\n  }\n  result = count\n}"),
    "php": ("if ($extra <= 1) {\n  $result = 0;\n} else {\n  $left = 0; $prod = 1; $count = 0;\n"
            "  for ($right = 0; $right < count($nums); $right++) {\n    $prod *= $nums[$right];\n    while ($prod >= $extra) { $prod = intdiv($prod, $nums[$left]); $left++; }\n    $count += $right - $left + 1;\n  }\n  $result = $count;\n}"),
    "scala": ("val result: Long = if (extra <= 1) {\n  0L\n} else {\n  var left = 0\n  var prod = 1L\n  var count = 0L\n"
              "  for (right <- nums.indices) {\n    prod *= nums(right)\n    while (prod >= extra) { prod /= nums(left); left += 1 }\n    count += (right - left + 1)\n  }\n  count\n}"),
    "r": ("if (extra <= 1) {\n  result <- 0\n} else {\n  left <- 0; prod <- 1; count <- 0\n"
          "  for (right in 0:(length(nums)-1)) {\n    prod <- prod * nums[right+1]\n    while (prod >= extra) { prod <- prod %/% nums[left+1]; left <- left + 1 }\n    count <- count + (right - left + 1)\n  }\n  result <- count\n}"),
})

add("subarray-sums-divisible-by-k", "arr1_int", "subarraysDivByK", "int", {
    "kotlin": ("val seen = HashMap<Long, Long>(); seen[0L] = 1L\nvar sum = 0L\nvar count = 0L\n"
               "for (x in nums) {\n  sum += x\n  val r = ((sum % extra) + extra) % extra\n  count += seen[r] ?: 0L\n  seen[r] = (seen[r] ?: 0L) + 1L\n}\nval result = count"),
    "php": ("$seen = [0 => 1];\n$sum = 0; $count = 0;\n"
            "foreach ($nums as $x) {\n  $sum += $x;\n  $r = (($sum % $extra) + $extra) % $extra;\n  $count += ($seen[$r] ?? 0);\n  $seen[$r] = ($seen[$r] ?? 0) + 1;\n}\n$result = $count;"),
    "scala": ("val seen = scala.collection.mutable.HashMap[Long, Long](0L -> 1L).withDefaultValue(0L)\nvar sum = 0L\nvar count = 0L\n"
              "for (x <- nums) {\n  sum += x\n  val r = ((sum % extra) + extra) % extra\n  count += seen(r)\n  seen(r) += 1\n}\nval result: Long = count"),
    "r": ("seen <- new.env()\nassign(\"0\", 1, envir = seen)\nsum <- 0; count <- 0\n"
          "for (x in nums) {\n  sum <- sum + x\n  r <- ((sum %% extra) + extra) %% extra\n  key <- as.character(r)\n"
          "  cur <- if (exists(key, envir = seen)) get(key, envir = seen) else 0\n  count <- count + cur\n  assign(key, cur + 1, envir = seen)\n}\nresult <- count"),
})

add("euler-phi-sieve", "int1", "eulerPhiSieve", "int", {
    "kotlin": "val N = n\nvar result = N\nvar num = N\nvar p = 2L\nwhile (p * p <= num) {\n  if (num % p == 0L) { while (num % p == 0L) num /= p; result -= result / p }\n  p++\n}\nif (num > 1) result -= result / num",
    "php": "$N = $n;\n$result = $N; $num = $N;\n$p = 2;\nwhile ($p * $p <= $num) {\n  if ($num % $p == 0) { while ($num % $p == 0) { $num = intdiv($num, $p); } $result -= intdiv($result, $p); }\n  $p++;\n}\nif ($num > 1) $result -= intdiv($result, $num);",
    "scala": "val N = n\nvar result = N\nvar num = N\nvar p = 2L\nwhile (p * p <= num) {\n  if (num % p == 0) { while (num % p == 0) num /= p; result -= result / p }\n  p += 1\n}\nif (num > 1) result -= result / num",
    "r": "N <- n\nresult <- N; num <- N\np <- 2\nwhile (p * p <= num) {\n  if (num %% p == 0) { while (num %% p == 0) { num <- num %/% p }; result <- result - result %/% p }\n  p <- p + 1\n}\nif (num > 1) result <- result - result %/% num",
})

add("integer-square-root", "int1", "mySqrt", "int", {
    "kotlin": "var lo = 0L\nvar hi = n\nwhile (lo < hi) { val mid = (lo + hi + 1) / 2; if (mid * mid <= n) lo = mid else hi = mid - 1 }\nval result = lo",
    "php": "$lo = 0; $hi = $n;\nwhile ($lo < $hi) { $mid = intdiv($lo + $hi + 1, 2); if ($mid * $mid <= $n) { $lo = $mid; } else { $hi = $mid - 1; } }\n$result = $lo;",
    "scala": "var lo = 0L\nvar hi = n\nwhile (lo < hi) { val mid = (lo + hi + 1) / 2; if (mid * mid <= n) lo = mid else hi = mid - 1 }\nval result: Long = lo",
    "r": "lo <- 0; hi <- n\nwhile (lo < hi) { mid <- (lo + hi + 1) %/% 2; if (mid * mid <= n) { lo <- mid } else { hi <- mid - 1 } }\nresult <- lo",
})

add("miller-rabin", "int1", "millerRabin", "bool", {
    "kotlin": "val result: Boolean\nif (n < 2) {\n  result = false\n} else {\n  var prime = true\n  var i = 2L\n  while (i * i <= n) { if (n % i == 0L) { prime = false; break }; i++ }\n  result = prime\n}",
    "php": "if ($n < 2) {\n  $result = false;\n} else {\n  $result = true;\n  for ($i = 2; $i * $i <= $n; $i++) { if ($n % $i == 0) { $result = false; break; } }\n}",
    "scala": "val result: Boolean = if (n < 2) {\n  false\n} else {\n  var prime = true\n  var i = 2L\n  while (i * i <= n) { if (n % i == 0) { prime = false }; i += 1 }\n  prime\n}",
    "r": "if (n < 2) {\n  result <- FALSE\n} else {\n  result <- TRUE\n  i <- 2\n  while (i * i <= n) { if (n %% i == 0) { result <- FALSE; break }; i <- i + 1 }\n}",
})

add("number-of-divisors", "int1", "numberOfDivisors", "int", {
    "kotlin": "var count = 0L\nvar i = 1L\nwhile (i * i <= n) { if (n % i == 0L) { count += if (i * i == n) 1 else 2 }; i++ }\nval result = count",
    "php": "$count = 0;\nfor ($i = 1; $i * $i <= $n; $i++) { if ($n % $i == 0) { $count += ($i * $i == $n) ? 1 : 2; } }\n$result = $count;",
    "scala": "var count = 0L\nvar i = 1L\nwhile (i * i <= n) { if (n % i == 0) { count += (if (i * i == n) 1 else 2) }; i += 1 }\nval result: Long = count",
    "r": "count <- 0\ni <- 1\nwhile (i * i <= n) { if (n %% i == 0) { count <- count + (if (i * i == n) 1 else 2) }; i <- i + 1 }\nresult <- count",
})

add("palindrome-linked-list", "arr1", "isPalindrome", "bool", {
    "kotlin": "var lo = 0\nvar hi = nums.size - 1\nvar result = true\nwhile (lo < hi) { if (nums[lo] != nums[hi]) { result = false; break }; lo++; hi-- }",
    "php": "$lo = 0; $hi = count($nums) - 1; $result = true;\nwhile ($lo < $hi) { if ($nums[$lo] != $nums[$hi]) { $result = false; break; } $lo++; $hi--; }",
    "scala": "var lo = 0\nvar hi = nums.length - 1\nvar result = true\nwhile (lo < hi) { if (nums(lo) != nums(hi)) { result = false }; lo += 1; hi -= 1 }",
    "r": "lo <- 0; hi <- length(nums) - 1; result <- TRUE\nwhile (lo < hi) { if (nums[lo+1] != nums[hi+1]) { result <- FALSE; break }; lo <- lo + 1; hi <- hi - 1 }",
})

add("delete-and-earn", "arr1", "deleteAndEarn", "int", {
    "kotlin": "val maxV = nums.max()!!\nval points = LongArray(maxV + 1)\nfor (x in nums) points[x] += x\nvar prev2 = 0L\nvar prev1 = 0L\nfor (p in points) { val cur = maxOf(prev1, prev2 + p); prev2 = prev1; prev1 = cur }\nval result = prev1",
    "php": "$maxV = max($nums);\n$points = array_fill(0, $maxV + 1, 0);\nforeach ($nums as $x) { $points[$x] += $x; }\n$prev2 = 0; $prev1 = 0;\nforeach ($points as $p) { $cur = max($prev1, $prev2 + $p); $prev2 = $prev1; $prev1 = $cur; }\n$result = $prev1;",
    "scala": "val maxV = nums.max\nval points = Array.fill(maxV + 1)(0L)\nfor (x <- nums) points(x) += x\nvar prev2 = 0L\nvar prev1 = 0L\nfor (p <- points) { val cur = math.max(prev1, prev2 + p); prev2 = prev1; prev1 = cur }\nval result: Long = prev1",
    "r": "maxV <- max(nums)\npoints <- rep(0, maxV + 1)\nfor (x in nums) { points[x + 1] <- points[x + 1] + x }\nprev2 <- 0; prev1 <- 0\nfor (p in points) { cur <- max(prev1, prev2 + p); prev2 <- prev1; prev1 <- cur }\nresult <- prev1",
})

add("jump-game-ii-min-jumps", "arr1", "jump", "int", {
    "kotlin": "var jumps = 0\nvar curEnd = 0\nvar farthest = 0\nfor (i in 0 until nums.size - 1) {\n  if (i + nums[i] > farthest) farthest = i + nums[i]\n  if (i == curEnd) { jumps++; curEnd = farthest }\n}\nval result = jumps.toLong()",
    "php": "$jumps = 0; $curEnd = 0; $farthest = 0;\nfor ($i = 0; $i < count($nums) - 1; $i++) {\n  if ($i + $nums[$i] > $farthest) $farthest = $i + $nums[$i];\n  if ($i == $curEnd) { $jumps++; $curEnd = $farthest; }\n}\n$result = $jumps;",
    "scala": "var jumps = 0\nvar curEnd = 0\nvar farthest = 0\nfor (i <- 0 until nums.length - 1) {\n  if (i + nums(i) > farthest) farthest = i + nums(i)\n  if (i == curEnd) { jumps += 1; curEnd = farthest }\n}\nval result: Long = jumps",
    "r": "jumps <- 0; curEnd <- 0; farthest <- 0\nif (length(nums) > 1) {\n  for (i in 0:(length(nums)-2)) {\n    if (i + nums[i+1] > farthest) farthest <- i + nums[i+1]\n    if (i == curEnd) { jumps <- jumps + 1; curEnd <- farthest }\n  }\n}\nresult <- jumps",
})

add("linked-list-cycle-detect", "arr1_int", "hasCycle", "bool", {
    "kotlin": "val result = extra != -1",
    "php": "$result = ($extra != -1);",
    "scala": "val result: Boolean = extra != -1",
    "r": "result <- (extra != -1)",
})

add("lucas-theorem", "int3", "lucasTheorem", "int", {
    "kotlin": ("fun powModL(baseIn: Long, expIn: Long, mod: Long): Long {\n  var base = baseIn % mod\n  var exp = expIn\n  var r = 1L\n  while (exp > 0) { if (exp % 2 == 1L) r = r * base % mod; base = base * base % mod; exp /= 2 }\n  return r\n}\n"
               "fun smallCL(nn: Long, kk: Long, pp: Long): Long {\n  if (kk < 0 || kk > nn) return 0\n  var num = 1L\n  for (i in (nn - kk + 1)..nn) num = num * (i % pp) % pp\n  var den = 1L\n  for (i in 1..kk) den = den * i % pp\n  return num * powModL(den, pp - 2, pp) % pp\n}\n"
               "fun lucasL(nn: Long, kk: Long, pp: Long): Long {\n  if (kk == 0L) return 1 % pp\n  val ni = nn % pp; val ki = kk % pp\n  return smallCL(ni, ki, pp) * lucasL(nn / pp, kk / pp, pp) % pp\n}\n"
               "val result = lucasL(a, b, c)"),
    "php": ("function powModPhp($base, $exp, $mod) { $base = $base % $mod; $r = 1; while ($exp > 0) { if ($exp % 2 == 1) $r = $r * $base % $mod; $base = $base * $base % $mod; $exp = intdiv($exp, 2); } return $r; }\n"
            "function smallCPhp($nn, $kk, $pp) { if ($kk < 0 || $kk > $nn) return 0; $num = 1; for ($i = $nn - $kk + 1; $i <= $nn; $i++) { $num = $num * ($i % $pp) % $pp; } $den = 1; for ($i = 1; $i <= $kk; $i++) { $den = $den * $i % $pp; } return $num * powModPhp($den, $pp - 2, $pp) % $pp; }\n"
            "function lucasPhp($nn, $kk, $pp) { if ($kk == 0) return 1 % $pp; $ni = $nn % $pp; $ki = $kk % $pp; return smallCPhp($ni, $ki, $pp) * lucasPhp(intdiv($nn, $pp), intdiv($kk, $pp), $pp) % $pp; }\n"
            "$result = lucasPhp($a, $b, $c);"),
    "scala": ("def powModS(baseIn: Long, expIn: Long, mod: Long): Long = {\n  var base = baseIn % mod\n  var exp = expIn\n  var r = 1L\n  while (exp > 0) { if (exp % 2 == 1) r = r * base % mod; base = base * base % mod; exp /= 2 }\n  r\n}\n"
              "def smallCS(nn: Long, kk: Long, pp: Long): Long = {\n  if (kk < 0 || kk > nn) 0L\n  else {\n    var num = 1L\n    for (i <- (nn - kk + 1) to nn) num = num * (i % pp) % pp\n    var den = 1L\n    for (i <- 1L to kk) den = den * i % pp\n    num * powModS(den, pp - 2, pp) % pp\n  }\n}\n"
              "def lucasS(nn: Long, kk: Long, pp: Long): Long = {\n  if (kk == 0) 1 % pp\n  else {\n    val ni = nn % pp; val ki = kk % pp\n    smallCS(ni, ki, pp) * lucasS(nn / pp, kk / pp, pp) % pp\n  }\n}\n"
              "val result: Long = lucasS(a, b, c)"),
    "r": ("powModR <- function(base, exp, mod) {\n  base <- base %% mod\n  r <- 1\n  while (exp > 0) { if (exp %% 2 == 1) r <- (r * base) %% mod; base <- (base * base) %% mod; exp <- exp %/% 2 }\n  r\n}\n"
          "smallCR <- function(nn, kk, pp) {\n  if (kk < 0 || kk > nn) return(0)\n  num <- 1\n  if (nn - kk + 1 <= nn) { for (i in (nn - kk + 1):nn) { num <- (num * (i %% pp)) %% pp } }\n  den <- 1\n  if (kk >= 1) { for (i in 1:kk) { den <- (den * i) %% pp } }\n  (num * powModR(den, pp - 2, pp)) %% pp\n}\n"
          "lucasR <- function(nn, kk, pp) {\n  if (kk == 0) return(1 %% pp)\n  ni <- nn %% pp; ki <- kk %% pp\n  (smallCR(ni, ki, pp) * lucasR(nn %/% pp, kk %/% pp, pp)) %% pp\n}\n"
          "result <- lucasR(a, b, c)"),
})

add("modular-exponentiation", "int3", "modularExponentiation", "int", {
    "kotlin": "var base = a % c\nvar exp = b\nval mod = c\nvar r = 1L % mod\nwhile (exp > 0) { if (exp % 2 == 1L) r = r * base % mod; base = base * base % mod; exp /= 2 }\nval result = r",
    "php": "$base = $a % $c; $exp = $b; $mod = $c; $r = 1 % $mod;\nwhile ($exp > 0) { if ($exp % 2 == 1) $r = $r * $base % $mod; $base = $base * $base % $mod; $exp = intdiv($exp, 2); }\n$result = $r;",
    "scala": "var base = a % c\nvar exp = b\nval mod = c\nvar r = 1L % mod\nwhile (exp > 0) { if (exp % 2 == 1) r = r * base % mod; base = base * base % mod; exp /= 2 }\nval result: Long = r",
    "r": ("mulModR <- function(x, y, mod) {\n  x <- x %% mod; y <- y %% mod\n  acc <- 0\n  while (y > 0) { if (y %% 2 == 1) acc <- (acc + x) %% mod; x <- (x * 2) %% mod; y <- y %/% 2 }\n  acc\n}\n"
          "base <- a %% c\nexp <- b\nmod <- c\nr <- 1 %% mod\nwhile (exp > 0) { if (exp %% 2 == 1) r <- mulModR(r, base, mod); base <- mulModR(base, base, mod); exp <- exp %/% 2 }\nresult <- r"),
})

add("minimum-knight-moves", "int2", "minKnightMoves", "int", {
    "kotlin": ("val tx = Math.abs(a); val ty = Math.abs(b)\ndata class St(val x: Long, val y: Long, val d: Long)\nval q = ArrayDeque<St>(); q.addLast(St(0, 0, 0))\nval visited = HashSet<Pair<Long, Long>>(); visited.add(Pair(0L, 0L))\nval dirs = arrayOf(Pair(1L,2L), Pair(2L,1L), Pair(-1L,2L), Pair(-2L,1L), Pair(1L,-2L), Pair(2L,-1L), Pair(-1L,-2L), Pair(-2L,-1L))\nvar ans = 0L\nwhile (q.isNotEmpty()) {\n  val cur = q.removeFirst()\n  if (cur.x == tx && cur.y == ty) { ans = cur.d; break }\n  for ((dx, dy) in dirs) {\n    val nx = cur.x + dx; val ny = cur.y + dy\n    if (nx >= -2 && ny >= -2 && nx <= tx + 2 && ny <= ty + 2) {\n      val key = Pair(nx, ny)\n      if (!visited.contains(key)) { visited.add(key); q.addLast(St(nx, ny, cur.d + 1)) }\n    }\n  }\n}\nval result = ans"),
    "php": ("$tx = abs($a); $ty = abs($b);\n$queue = [[0, 0, 0]];\n$visited = ['0,0' => true];\n$dirs = [[1,2],[2,1],[-1,2],[-2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]];\n$ans = 0;\nwhile (!empty($queue)) {\n  $cur = array_shift($queue);\n  list($x, $y, $d) = $cur;\n  if ($x == $tx && $y == $ty) { $ans = $d; break; }\n  foreach ($dirs as $dir) {\n    $nx = $x + $dir[0]; $ny = $y + $dir[1];\n    if ($nx >= -2 && $ny >= -2 && $nx <= $tx + 2 && $ny <= $ty + 2) {\n      $key = \"$nx,$ny\";\n      if (!isset($visited[$key])) { $visited[$key] = true; $queue[] = [$nx, $ny, $d + 1]; }\n    }\n  }\n}\n$result = $ans;"),
    "scala": ("val tx = math.abs(a); val ty = math.abs(b)\nval q = scala.collection.mutable.Queue[(Long, Long, Long)]((0L, 0L, 0L))\nval visited = scala.collection.mutable.HashSet[(Long, Long)]((0L, 0L))\nval dirs = Array((1L,2L), (2L,1L), (-1L,2L), (-2L,1L), (1L,-2L), (2L,-1L), (-1L,-2L), (-2L,-1L))\nvar ans = 0L\nwhile (q.nonEmpty) {\n  val (x, y, d) = q.dequeue()\n  if (x == tx && y == ty) { ans = d } else {\n    for ((dx, dy) <- dirs) {\n      val nx = x + dx; val ny = y + dy\n      if (nx >= -2 && ny >= -2 && nx <= tx + 2 && ny <= ty + 2) {\n        val key = (nx, ny)\n        if (!visited.contains(key)) { visited.add(key); q.enqueue((nx, ny, d + 1)) }\n      }\n    }\n  }\n}\nval result: Long = ans"),
    "r": ("tx <- abs(a); ty <- abs(b)\n"
          "bound <- tx + 4; if (ty + 4 > bound) bound <- ty + 4\n"
          "side <- 2 * bound + 1; maxCells <- side * side\n"
          "qx <- integer(maxCells); qy <- integer(maxCells); qd <- integer(maxCells)\n"
          "qx[1] <- 0; qy[1] <- 0; qd[1] <- 0\n"
          "head <- 1; tail <- 1\n"
          "visited <- matrix(FALSE, nrow = side, ncol = side)\n"
          "visited[bound + 1, bound + 1] <- TRUE\n"
          "dxs <- c(1, 2, -1, -2, 1, 2, -1, -2)\ndys <- c(2, 1, 2, 1, -2, -1, -2, -1)\n"
          "ans <- 0\n"
          "while (head <= tail) {\n"
          "  x <- qx[head]; y <- qy[head]; d <- qd[head]; head <- head + 1\n"
          "  if (x == tx && y == ty) { ans <- d; break }\n"
          "  for (k in 1:8) {\n"
          "    nx <- x + dxs[k]; ny <- y + dys[k]\n"
          "    if (nx >= -2 && ny >= -2 && nx <= tx + 2 && ny <= ty + 2) {\n"
          "      ix <- nx + bound + 1; iy <- ny + bound + 1\n"
          "      if (!visited[ix, iy]) {\n"
          "        visited[ix, iy] <- TRUE\n"
          "        tail <- tail + 1; qx[tail] <- nx; qy[tail] <- ny; qd[tail] <- d + 1\n"
          "      }\n"
          "    }\n"
          "  }\n"
          "}\nresult <- ans"),
})


@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


def build_program(lang, pid, wrong):
    spec = PROBLEMS[pid]
    return assemble(lang, spec["shape"], spec["fn"], spec["kind"], spec["bodies"][lang], wrong)


def load_cases(con, pid):
    cur = con.execute(
        "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = [SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                         is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
    row = con.execute("SELECT test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    return cases, row["test_suite_version"]


async def verify_one(pid, lang, cases):
    t0 = time.monotonic()
    correct_result = await evaluate(build_program(lang, pid, False), lang, cases)
    if correct_result.tests_passed != correct_result.tests_total:
        extra = correct_result.compile_output or ""
        if not extra and correct_result.test_results:
            for tr in correct_result.test_results:
                if not tr.passed:
                    extra = f"verdict={tr.verdict} stderr={tr.stderr[:150]} actual={tr.actual_output[:60]!r} expected={tr.expected_output[:60]!r}"
                    break
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict} {extra[:200]}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate(build_program(lang, pid, True), lang, cases)
    if wrong_result.tests_passed >= wrong_result.tests_total:
        return {"pid": pid, "lang": lang, "outcome": "corpus_weakness", "detail": "wrong solution still passed all cases",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "lang": lang, "outcome": "verified",
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
        for lang in LANGS:
            if ledger.already_verified(con, pid, lang, "program", test_suite_version=tsv):
                print(f"[SKIP] {pid}/{lang} already verified")
                continue
            r = await verify_one(pid, lang, cases)
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang}(program) {pid:38s} {r['outcome']:18s} {r['detail'][:140]}", flush=True)
            if r["outcome"] == "verified":
                row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
                sc = json.loads(row["starter_code"])
                sc[lang] = build_program(lang, pid, False)
                con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
                con.commit()
                ledger.record_cell(
                    con, problem_id=pid, language=lang, mode="program",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version="program-mega-batch5-multilang-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"],
                )

    verified = [r for r in results if r["outcome"] == "verified"]
    failed = [r for r in results if r["outcome"] != "verified"]
    print(f"\nTOTAL: {len(results)}  verified={len(verified)}  failed={len(failed)}")
    if failed:
        print("\nFAILED CELLS:")
        for r in failed:
            print(f"  {r['pid']}/{r['lang']}: {r['outcome']} -- {r['detail'][:160]}")
    con.close()
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
