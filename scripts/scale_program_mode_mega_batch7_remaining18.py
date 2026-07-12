"""Program Mode expansion, mega batch 7: ports the 18 remaining mega_batch2.py
problems (palindrome DP family, interval/knapsack family, triangle) to SEVEN
languages -- python (never scaled beyond the original 8-core-language batches
despite being the reference language) plus the same six newer languages as
mega_batch6 (go, ruby, kotlin, php, scala, r). Also picks up Python credit
for the 4 problems mega_batch6 already closed for the newer six
(first-unique-character-index, longest-palindromic-substring,
longest-valid-parentheses, manacher), since Python was never in that batch
either. All algorithms are well-known DP/greedy patterns re-derived directly
(not transliterated line-by-line from the 8-core-language bodies) using the
same shape harness (str1, str1_int, str2, arr1, arr1_int, arr2_samelen,
arr2_int, triangle) proven across mega_batch1-6.
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
LANGS = ["python", "go", "ruby", "kotlin", "php", "scala", "r"]


def rt(lang, kind):
    if lang == "go":
        return "int64" if kind == "int" else "bool"
    if lang in ("kotlin", "scala"):
        return "Long" if kind == "int" else "Boolean"
    return None


def sig(lang, shape, fn, kind):
    if lang == "python":
        m = {"arr1": "nums", "arr1_int": "nums, extra", "str1": "s", "str1_int": "s, extra",
             "str2": "s, t", "arr2_samelen": "a, b", "arr2_int": "a, b, extra", "triangle": "triangle"}
        return f"def {fn}({m[shape]}):"
    if lang == "go":
        r = rt("go", kind)
        if shape == "arr1": return f"func {fn}(nums []int) {r} {{"
        if shape == "arr1_int": return f"func {fn}(nums []int, extra int) {r} {{"
        if shape == "str1": return f"func {fn}(s string) {r} {{"
        if shape == "str1_int": return f"func {fn}(s string, extra int) {r} {{"
        if shape == "str2": return f"func {fn}(s string, t string) {r} {{"
        if shape == "arr2_samelen": return f"func {fn}(a []int, b []int) {r} {{"
        if shape == "arr2_int": return f"func {fn}(a []int, b []int, extra int) {r} {{"
        if shape == "triangle": return f"func {fn}(triangle [][]int) {r} {{"
    if lang == "ruby":
        if shape == "arr1": return f"def {fn}(nums)"
        if shape == "arr1_int": return f"def {fn}(nums, extra)"
        if shape == "str1": return f"def {fn}(s)"
        if shape == "str1_int": return f"def {fn}(s, extra)"
        if shape == "str2": return f"def {fn}(s, t)"
        if shape == "arr2_samelen": return f"def {fn}(a, b)"
        if shape == "arr2_int": return f"def {fn}(a, b, extra)"
        if shape == "triangle": return f"def {fn}(triangle)"
    if lang == "kotlin":
        r = rt("kotlin", kind)
        if shape == "arr1": return f"fun {fn}(nums: IntArray): {r} {{"
        if shape == "arr1_int": return f"fun {fn}(nums: IntArray, extra: Int): {r} {{"
        if shape == "str1": return f"fun {fn}(s: String): {r} {{"
        if shape == "str1_int": return f"fun {fn}(s: String, extra: Int): {r} {{"
        if shape == "str2": return f"fun {fn}(s: String, t: String): {r} {{"
        if shape == "arr2_samelen": return f"fun {fn}(a: IntArray, b: IntArray): {r} {{"
        if shape == "arr2_int": return f"fun {fn}(a: IntArray, b: IntArray, extra: Int): {r} {{"
        if shape == "triangle": return f"fun {fn}(triangle: Array<IntArray>): {r} {{"
    if lang == "php":
        if shape == "arr1": return f"function {fn}($nums) {{"
        if shape == "arr1_int": return f"function {fn}($nums, $extra) {{"
        if shape == "str1": return f"function {fn}($s) {{"
        if shape == "str1_int": return f"function {fn}($s, $extra) {{"
        if shape == "str2": return f"function {fn}($s, $t) {{"
        if shape == "arr2_samelen": return f"function {fn}($a, $b) {{"
        if shape == "arr2_int": return f"function {fn}($a, $b, $extra) {{"
        if shape == "triangle": return f"function {fn}($triangle) {{"
    if lang == "scala":
        r = rt("scala", kind)
        if shape == "arr1": return f"def {fn}(nums: Array[Int]): {r} = {{"
        if shape == "arr1_int": return f"def {fn}(nums: Array[Int], extra: Int): {r} = {{"
        if shape == "str1": return f"def {fn}(s: String): {r} = {{"
        if shape == "str1_int": return f"def {fn}(s: String, extra: Int): {r} = {{"
        if shape == "str2": return f"def {fn}(s: String, t: String): {r} = {{"
        if shape == "arr2_samelen": return f"def {fn}(a: Array[Int], b: Array[Int]): {r} = {{"
        if shape == "arr2_int": return f"def {fn}(a: Array[Int], b: Array[Int], extra: Int): {r} = {{"
        if shape == "triangle": return f"def {fn}(triangle: Array[Array[Int]]): {r} = {{"
    if lang == "r":
        if shape == "arr1": return f"{fn} <- function(nums) {{"
        if shape == "arr1_int": return f"{fn} <- function(nums, extra) {{"
        if shape == "str1": return f"{fn} <- function(s) {{"
        if shape == "str1_int": return f"{fn} <- function(s, extra) {{"
        if shape == "str2": return f"{fn} <- function(s, t) {{"
        if shape == "arr2_samelen": return f"{fn} <- function(a, b) {{"
        if shape == "arr2_int": return f"{fn} <- function(a, b, extra) {{"
        if shape == "triangle": return f"{fn} <- function(triangle) {{"
    raise ValueError((lang, shape))


def read_code(lang, shape):
    if lang == "python":
        if shape == "arr1":
            return "data = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1+n]))"
        if shape == "arr1_int":
            return read_code("python", "arr1") + "\nextra = int(data[1+n])"
        if shape == "str1":
            return "s = sys.stdin.read().strip()"
        if shape == "str1_int":
            return ("line = sys.stdin.read().rstrip('\\n').rstrip('\\r')\n"
                     "idx = line.rindex(' ')\ns = line[:idx]\nextra = int(line[idx+1:].strip())")
        if shape == "str2":
            return ("lines = sys.stdin.read().split('\\n')\n"
                     "s = lines[0].rstrip('\\r') if len(lines) > 0 else ''\n"
                     "t = lines[1].rstrip('\\r') if len(lines) > 1 else ''")
        if shape == "arr2_samelen":
            return ("data = sys.stdin.read().split()\nn = int(data[0])\n"
                     "a = list(map(int, data[1:1+n]))\nb = list(map(int, data[1+n:1+2*n]))")
        if shape == "arr2_int":
            return read_code("python", "arr2_samelen") + "\nextra = int(data[1+2*n])"
        if shape == "triangle":
            return ("data = sys.stdin.read().split()\nn = int(data[0])\np = 1\ntriangle = []\n"
                     "for i in range(n):\n    row = list(map(int, data[p:p+i+1]))\n    p += i+1\n    triangle.append(row)")
    if lang == "go":
        if shape == "arr1":
            return ("data, _ := io.ReadAll(os.Stdin)\nfields := strings.Fields(string(data))\n"
                     "n, _ := strconv.Atoi(fields[0])\nnums := make([]int, n)\nfor i := 0; i < n; i++ { nums[i], _ = strconv.Atoi(fields[1+i]) }")
        if shape == "arr1_int":
            return read_code("go", "arr1") + "\nextra, _ := strconv.Atoi(fields[1+n])"
        if shape == "str1":
            return "data, _ := io.ReadAll(os.Stdin)\ns := strings.TrimSpace(string(data))"
        if shape == "str1_int":
            return ("data, _ := io.ReadAll(os.Stdin)\nline := strings.TrimRight(string(data), \"\\r\\n\")\n"
                     "idx := strings.LastIndex(line, \" \")\ns := line[:idx]\nextra, _ := strconv.Atoi(strings.TrimSpace(line[idx+1:]))")
        if shape == "str2":
            return ("data, _ := io.ReadAll(os.Stdin)\nlines := strings.Split(string(data), \"\\n\")\n"
                     "s := strings.TrimRight(lines[0], \"\\r\")\nt := \"\"\nif len(lines) > 1 { t = strings.TrimRight(lines[1], \"\\r\") }")
        if shape == "arr2_samelen":
            return ("data, _ := io.ReadAll(os.Stdin)\nfields := strings.Fields(string(data))\n"
                     "n, _ := strconv.Atoi(fields[0])\na := make([]int, n)\nfor i := 0; i < n; i++ { a[i], _ = strconv.Atoi(fields[1+i]) }\n"
                     "b := make([]int, n)\nfor i := 0; i < n; i++ { b[i], _ = strconv.Atoi(fields[1+n+i]) }")
        if shape == "arr2_int":
            return read_code("go", "arr2_samelen") + "\nextra, _ := strconv.Atoi(fields[1+2*n])"
        if shape == "triangle":
            return ("data, _ := io.ReadAll(os.Stdin)\nfields := strings.Fields(string(data))\n"
                     "n, _ := strconv.Atoi(fields[0])\np := 1\ntriangle := make([][]int, n)\n"
                     "for i := 0; i < n; i++ { row := make([]int, i+1); for j := 0; j <= i; j++ { row[j], _ = strconv.Atoi(fields[p]); p++ }; triangle[i] = row }")
    if lang == "ruby":
        if shape == "arr1":
            return "data = STDIN.read.split\nn = data[0].to_i\nnums = data[1, n].map(&:to_i)"
        if shape == "arr1_int":
            return read_code("ruby", "arr1") + "\nextra = data[1 + n].to_i"
        if shape == "str1":
            return "s = STDIN.read.strip"
        if shape == "str1_int":
            return "line = STDIN.read.rstrip(\"\\n\").rstrip(\"\\r\")\nidx = line.rindex(' ')\ns = line[0...idx]\nextra = line[(idx + 1)..].to_i"
        if shape == "str2":
            return "lines = STDIN.read.split(\"\\n\")\ns = (lines[0] || '').chomp\nt = (lines[1] || '').chomp"
        if shape == "arr2_samelen":
            return "data = STDIN.read.split\nn = data[0].to_i\na = data[1, n].map(&:to_i)\nb = data[1 + n, n].map(&:to_i)"
        if shape == "arr2_int":
            return read_code("ruby", "arr2_samelen") + "\nextra = data[1 + 2 * n].to_i"
        if shape == "triangle":
            return ("data = STDIN.read.split\nn = data[0].to_i\np = 1\ntriangle = []\n"
                     "(0...n).each { |i| row = data[p, i + 1].map(&:to_i); p += i + 1; triangle << row }")
    if lang == "kotlin":
        if shape == "arr1":
            return ("val data = System.`in`.bufferedReader().readText().trim().split(Regex(\"\\\\s+\"))\n"
                     "val n = data[0].toInt()\nval nums = IntArray(n) { data[1 + it].toInt() }")
        if shape == "arr1_int":
            return read_code("kotlin", "arr1") + "\nval extra = data[1 + n].toInt()"
        if shape == "str1":
            return "val s = System.`in`.bufferedReader().readText().trim()"
        if shape == "str1_int":
            return ("val line = System.`in`.bufferedReader().readText().trimEnd('\\n', '\\r')\n"
                     "val idx = line.lastIndexOf(' ')\nval s = line.substring(0, idx)\nval extra = line.substring(idx + 1).trim().toInt()")
        if shape == "str2":
            return ("val lines = System.`in`.bufferedReader().readText().split(\"\\n\")\n"
                     "val s = lines[0].trimEnd('\\r')\nval t = if (lines.size > 1) lines[1].trimEnd('\\r') else \"\"")
        if shape == "arr2_samelen":
            return ("val data = System.`in`.bufferedReader().readText().trim().split(Regex(\"\\\\s+\"))\n"
                     "val n = data[0].toInt()\nval a = IntArray(n) { data[1 + it].toInt() }\nval b = IntArray(n) { data[1 + n + it].toInt() }")
        if shape == "arr2_int":
            return read_code("kotlin", "arr2_samelen") + "\nval extra = data[1 + 2 * n].toInt()"
        if shape == "triangle":
            return ("val data = System.`in`.bufferedReader().readText().trim().split(Regex(\"\\\\s+\"))\n"
                     "val n = data[0].toInt()\nvar p = 1\nval triangle = Array(n) { i -> val row = IntArray(i + 1) { j -> data[p + j].toInt() }; p += i + 1; row }")
    if lang == "php":
        if shape == "arr1":
            return ("$data = preg_split('/\\s+/', trim(file_get_contents('php://stdin')));\n"
                     "$n = intval($data[0]);\n$nums = array_map('intval', array_slice($data, 1, $n));")
        if shape == "arr1_int":
            return read_code("php", "arr1") + "\n$extra = intval($data[1 + $n]);"
        if shape == "str1":
            return "$s = trim(file_get_contents('php://stdin'));"
        if shape == "str1_int":
            return ("$line = rtrim(file_get_contents('php://stdin'), \"\\r\\n\");\n"
                     "$idx = strrpos($line, ' ');\n$s = substr($line, 0, $idx);\n$extra = intval(trim(substr($line, $idx + 1)));")
        if shape == "str2":
            return "$lines = explode(\"\\n\", file_get_contents('php://stdin'));\n$s = rtrim($lines[0], \"\\r\");\n$t = isset($lines[1]) ? rtrim($lines[1], \"\\r\") : '';"
        if shape == "arr2_samelen":
            return ("$data = preg_split('/\\s+/', trim(file_get_contents('php://stdin')));\n"
                     "$n = intval($data[0]);\n$a = array_map('intval', array_slice($data, 1, $n));\n$b = array_map('intval', array_slice($data, 1 + $n, $n));")
        if shape == "arr2_int":
            return read_code("php", "arr2_samelen") + "\n$extra = intval($data[1 + 2 * $n]);"
        if shape == "triangle":
            return ("$data = preg_split('/\\s+/', trim(file_get_contents('php://stdin')));\n"
                     "$n = intval($data[0]); $p = 1; $triangle = [];\n"
                     "for ($i = 0; $i < $n; $i++) { $row = []; for ($j = 0; $j <= $i; $j++) { $row[] = intval($data[$p]); $p++; } $triangle[] = $row; }")
    if lang == "scala":
        if shape == "arr1":
            return ("val raw = scala.io.Source.stdin.mkString\nval data = raw.trim.split(\"\\\\s+\")\n"
                     "val n = data(0).toInt\nval nums = (0 until n).map(i => data(1 + i).toInt).toArray")
        if shape == "arr1_int":
            return read_code("scala", "arr1") + "\nval extra = data(1 + n).toInt"
        if shape == "str1":
            return "val s = scala.io.Source.stdin.mkString.trim"
        if shape == "str1_int":
            return ("val raw = scala.io.Source.stdin.mkString\nval line = raw.stripLineEnd\n"
                     "val idx = line.lastIndexOf(' ')\nval s = line.substring(0, idx)\nval extra = line.substring(idx + 1).trim.toInt")
        if shape == "str2":
            return ("val raw = scala.io.Source.stdin.mkString\nval lines = raw.split(\"\\n\", -1)\n"
                     "val s = lines(0).stripLineEnd\nval t = if (lines.length > 1) lines(1).stripLineEnd else \"\"")
        if shape == "arr2_samelen":
            return ("val raw = scala.io.Source.stdin.mkString\nval data = raw.trim.split(\"\\\\s+\")\n"
                     "val n = data(0).toInt\nval a = (0 until n).map(i => data(1 + i).toInt).toArray\nval b = (0 until n).map(i => data(1 + n + i).toInt).toArray")
        if shape == "arr2_int":
            return read_code("scala", "arr2_samelen") + "\nval extra = data(1 + 2 * n).toInt"
        if shape == "triangle":
            return ("val raw = scala.io.Source.stdin.mkString\nval data = raw.trim.split(\"\\\\s+\")\n"
                     "val n = data(0).toInt\nvar p = 1\nval triangle = Array.tabulate(n) { i => val row = Array.tabulate(i + 1) { j => data(p + j).toInt }; p += i + 1; row }")
    if lang == "r":
        base = "con <- file(\"stdin\"); lines <- readLines(con); close(con)\n"
        if shape == "arr1":
            return (base + "data <- as.numeric(strsplit(paste(lines, collapse=\" \"), \"\\\\s+\")[[1]])\n"
                     "n <- as.integer(data[1])\nnums <- if (n > 0) as.integer(data[2:(1+n)]) else integer(0)")
        if shape == "arr1_int":
            return read_code("r", "arr1") + "\nextra <- as.integer(data[2+n])"
        if shape == "str1":
            return base + "s <- trimws(paste(lines, collapse=\" \"))"
        if shape == "str1_int":
            return (base + "line <- lines[1]\nidx <- max(gregexpr(' ', line)[[1]])\n"
                     "s <- substr(line, 1, idx - 1)\nextra <- as.integer(trimws(substr(line, idx + 1, nchar(line))))")
        if shape == "str2":
            return (base + "s <- if (length(lines) >= 1) lines[1] else \"\"\nt <- if (length(lines) >= 2) lines[2] else \"\"")
        if shape == "arr2_samelen":
            return (base + "data <- as.numeric(strsplit(paste(lines, collapse=\" \"), \"\\\\s+\")[[1]])\n"
                     "n <- as.integer(data[1])\na <- as.integer(data[2:(1+n)])\nb <- as.integer(data[(2+n):(1+2*n)])")
        if shape == "arr2_int":
            return read_code("r", "arr2_samelen") + "\nextra <- as.integer(data[2+2*n])"
        if shape == "triangle":
            return (base + "data <- as.numeric(strsplit(paste(lines, collapse=\" \"), \"\\\\s+\")[[1]])\n"
                     "n <- as.integer(data[1])\np <- 2\ntriangle <- list()\n"
                     "if (n > 0) { for (i in 1:n) { row <- as.integer(data[p:(p+i-1)]); p <- p + i; triangle[[i]] <- row } }")
    raise ValueError((lang, shape))


def call_args(lang, shape):
    if lang == "r":
        m = {"arr1": "nums", "arr1_int": "nums, extra", "str1": "s", "str1_int": "s, extra",
             "str2": "s, t", "arr2_samelen": "a, b", "arr2_int": "a, b, extra", "triangle": "triangle"}
        return m[shape]
    if lang == "php":
        m = {"arr1": "$nums", "arr1_int": "$nums, $extra", "str1": "$s", "str1_int": "$s, $extra",
             "str2": "$s, $t", "arr2_samelen": "$a, $b", "arr2_int": "$a, $b, $extra", "triangle": "$triangle"}
        return m[shape]
    m = {"arr1": "nums", "arr1_int": "nums, extra", "str1": "s", "str1_int": "s, extra",
         "str2": "s, t", "arr2_samelen": "a, b", "arr2_int": "a, b, extra", "triangle": "triangle"}
    return m[shape]


def print_stmt(lang, kind, wrong):
    delta = 1 if wrong else 0
    neg = "!" if wrong else ""
    if lang == "python":
        return f"print(result + {delta})" if kind == "int" else f"print({neg}result)"
    if lang == "go":
        return f"fmt.Println(result + {delta})" if kind == "int" else f"fmt.Println({neg}result)"
    if lang == "ruby":
        return f"puts(result + {delta})" if kind == "int" else f"puts({neg}result)"
    if lang == "kotlin":
        return f"println(result + {delta}L)" if kind == "int" else f"println({neg}result)"
    if lang == "php":
        if kind == "int":
            return f"echo ($result + {delta}), \"\\n\";"
        return f"echo (({neg}$result) ? \"true\" : \"false\"), \"\\n\";"
    if lang == "scala":
        return f"println(result + {delta}L)" if kind == "int" else f"println({neg}result)"
    if lang == "r":
        if kind == "int":
            return f"cat(result + {delta}, \"\\n\")"
        return f"cat(ifelse({neg}result, \"true\", \"false\"), \"\\n\")"
    raise ValueError((lang, kind))


def _indent_py(body: str) -> str:
    return "\n".join(("    " + line) if line.strip() else "" for line in body.split("\n"))


def assemble(lang, shape, fn, kind, body, wrong):
    read = read_code(lang, shape)
    signature = sig(lang, shape, fn, kind)
    args = call_args(lang, shape)
    p = print_stmt(lang, kind, wrong)

    if lang == "python":
        func = f"{signature}\n{_indent_py(body)}\n    return result"
        call = f"result = {fn}({args})"
        return f"import sys\n\n{func}\n\n{read}\n{call}\n{p}\n"
    if lang == "go":
        func = f"{signature}\n{body}\nreturn result\n}}"
        call = f"result := {fn}({args})"
        needs_strconv = shape not in ("str1", "str2")
        imports = "\"fmt\"\n\t\"io\"\n\t\"os\"\n\t" + ("\"strconv\"\n\t" if needs_strconv else "") + "\"strings\""
        return (f"package main\n\nimport (\n\t{imports}\n)\n\n"
                 f"{func}\n\nfunc main() {{\n{read}\n{call}\n{p}\n}}\n")
    if lang == "ruby":
        func = f"{signature}\n{body}\nreturn result\nend"
        call = f"result = {fn}({args})"
        return f"{func}\n\n{read}\n{call}\n{p}\n"
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


# ── Python-only credit for the 4 problems mega_batch6 already closed for the
# newer six languages (Python was never in that batch either) ──────────────

add("first-unique-character-index", "str1", "firstUniqChar", "int", {
    "python": ("cnt = {}\nfor ch in s:\n    cnt[ch] = cnt.get(ch, 0) + 1\n"
               "result = -1\nfor i, ch in enumerate(s):\n    if cnt[ch] == 1:\n        result = i\n        break"),
})

add("longest-palindromic-substring", "str1", "longestPalindrome", "int", {
    "python": ("def expand(l, r):\n    while l >= 0 and r < len(s) and s[l] == s[r]:\n        l -= 1\n        r += 1\n    return r - l - 1\n"
               "best = 0\nfor i in range(len(s)):\n    v1 = expand(i, i)\n    v2 = expand(i, i + 1)\n"
               "    if v1 > best:\n        best = v1\n    if v2 > best:\n        best = v2\nresult = best"),
})

add("longest-valid-parentheses", "str1", "longestValidParentheses", "int", {
    "python": ("stack = [-1]\nbest = 0\nfor i in range(len(s)):\n    if s[i] == '(':\n        stack.append(i)\n    else:\n"
               "        stack.pop()\n        if not stack:\n            stack.append(i)\n        else:\n"
               "            w = i - stack[-1]\n            if w > best:\n                best = w\nresult = best"),
})

add("manacher", "str1", "countPalindromicSubstrings", "int", {
    "python": ("def expand(l, r):\n    c = 0\n    while l >= 0 and r < len(s) and s[l] == s[r]:\n        c += 1\n        l -= 1\n        r += 1\n    return c\n"
               "count = 0\nfor i in range(len(s)):\n    count += expand(i, i)\n    count += expand(i, i + 1)\nresult = count"),
})

# ── 18 remaining mega_batch2 problems, all 7 languages ──────────────────────

add("palindrome-partition", "str1", "min_cut", "int", {
    "python": ("m = len(s)\nis_pal = [[False]*m for _ in range(m)]\nfor i in range(m):\n    is_pal[i][i] = True\n"
               "for length in range(2, m+1):\n    for i in range(0, m-length+1):\n        j = i+length-1\n"
               "        if s[i] == s[j] and (length == 2 or is_pal[i+1][j-1]):\n            is_pal[i][j] = True\n"
               "dp = [0]*(m if m > 0 else 1)\nfor i in range(m):\n    if is_pal[0][i]:\n        dp[i] = 0\n        continue\n"
               "    best = 1 << 30\n    for j in range(i):\n        if is_pal[j+1][i] and dp[j]+1 < best:\n            best = dp[j]+1\n    dp[i] = best\n"
               "result = 0 if m == 0 else dp[m-1]"),
    "go": ("m := len(s)\nisPal := make([][]bool, m)\nfor i := range isPal { isPal[i] = make([]bool, m) }\n"
           "for i := 0; i < m; i++ { isPal[i][i] = true }\n"
           "for length := 2; length <= m; length++ {\n  for i := 0; i+length-1 < m; i++ {\n    j := i+length-1\n"
           "    if s[i] == s[j] && (length == 2 || isPal[i+1][j-1]) { isPal[i][j] = true }\n  }\n}\n"
           "dp := make([]int, m)\nfor i := 0; i < m; i++ {\n  if isPal[0][i] { dp[i] = 0; continue }\n  best := 1 << 30\n"
           "  for j := 0; j < i; j++ {\n    if isPal[j+1][i] && dp[j]+1 < best { best = dp[j]+1 }\n  }\n  dp[i] = best\n}\n"
           "result := int64(0)\nif m > 0 { result = int64(dp[m-1]) }"),
    "ruby": ("m = s.length\nis_pal = Array.new(m) { Array.new(m, false) }\n(0...m).each { |i| is_pal[i][i] = true }\n"
             "(2..m).each do |len|\n  (0..(m-len)).each do |i|\n    j = i+len-1\n"
             "    is_pal[i][j] = true if s[i] == s[j] && (len == 2 || is_pal[i+1][j-1])\n  end\nend\n"
             "dp = Array.new(m, 0)\n(0...m).each do |i|\n  if is_pal[0][i]\n    dp[i] = 0\n    next\n  end\n"
             "  best = 1 << 30\n  (0...i).each do |j|\n    best = dp[j]+1 if is_pal[j+1][i] && dp[j]+1 < best\n  end\n  dp[i] = best\nend\n"
             "result = m == 0 ? 0 : dp[m-1]"),
    "kotlin": ("val m = s.length\nval isPal = Array(m) { BooleanArray(m) }\nfor (i in 0 until m) isPal[i][i] = true\n"
               "for (len in 2..m) {\n  for (i in 0..(m-len)) {\n    val j = i+len-1\n"
               "    if (s[i] == s[j] && (len == 2 || isPal[i+1][j-1])) isPal[i][j] = true\n  }\n}\n"
               "val dp = IntArray(if (m > 0) m else 1)\nfor (i in 0 until m) {\n  if (isPal[0][i]) { dp[i] = 0; continue }\n"
               "  var best = Int.MAX_VALUE\n  for (j in 0 until i) {\n    if (isPal[j+1][i] && dp[j]+1 < best) best = dp[j]+1\n  }\n  dp[i] = best\n}\n"
               "val result = if (m == 0) 0L else dp[m-1].toLong()"),
    "php": ("$m = strlen($s);\n$isPal = array();\nfor ($i = 0; $i < $m; $i++) { $isPal[$i] = array_fill(0, $m, false); }\n"
            "for ($i = 0; $i < $m; $i++) { $isPal[$i][$i] = true; }\n"
            "for ($len = 2; $len <= $m; $len++) {\n  for ($i = 0; $i + $len - 1 < $m; $i++) {\n    $j = $i + $len - 1;\n"
            "    if ($s[$i] == $s[$j] && ($len == 2 || $isPal[$i+1][$j-1])) { $isPal[$i][$j] = true; }\n  }\n}\n"
            "$dp = array_fill(0, max($m,1), 0);\nfor ($i = 0; $i < $m; $i++) {\n  if ($isPal[0][$i]) { $dp[$i] = 0; continue; }\n"
            "  $best = PHP_INT_MAX;\n  for ($j = 0; $j < $i; $j++) {\n    if ($isPal[$j+1][$i] && $dp[$j]+1 < $best) { $best = $dp[$j]+1; }\n  }\n  $dp[$i] = $best;\n}\n"
            "$result = $m == 0 ? 0 : $dp[$m-1];"),
    "scala": ("val m = s.length\nval isPal = Array.fill(m, m)(false)\nfor (i <- 0 until m) isPal(i)(i) = true\n"
              "for (len <- 2 to m) {\n  for (i <- 0 to (m-len)) {\n    val j = i+len-1\n"
              "    if (s(i) == s(j) && (len == 2 || isPal(i+1)(j-1))) isPal(i)(j) = true\n  }\n}\n"
              "val dp = Array.fill(if (m > 0) m else 1)(0)\nfor (i <- 0 until m) {\n  if (isPal(0)(i)) { dp(i) = 0 }\n  else {\n"
              "    var best = Int.MaxValue\n    for (j <- 0 until i) {\n      if (isPal(j+1)(i) && dp(j)+1 < best) best = dp(j)+1\n    }\n    dp(i) = best\n  }\n}\n"
              "val result: Long = if (m == 0) 0L else dp(m-1).toLong"),
    "r": ("m <- nchar(s)\nsb <- if (m > 0) strsplit(s, \"\")[[1]] else character(0)\n"
          "isPal <- matrix(FALSE, nrow = max(m,1), ncol = max(m,1))\n"
          "i <- 1\nwhile (i <= m) { isPal[i, i] <- TRUE; i <- i + 1 }\n"
          "len <- 2\nwhile (len <= m) {\n  i <- 1\n  while (i <= m - len + 1) {\n    j <- i + len - 1\n"
          "    if (sb[i] == sb[j] && (len == 2 || isPal[i+1, j-1])) isPal[i, j] <- TRUE\n    i <- i + 1\n  }\n  len <- len + 1\n}\n"
          "dp <- rep(0, max(m,1))\ni <- 1\nwhile (i <= m) {\n  if (isPal[1, i]) { dp[i] <- 0 } else {\n    best <- .Machine$integer.max\n"
          "    j <- 1\n    while (j <= i - 1) {\n      if (isPal[j+1, i] && dp[j]+1 < best) best <- dp[j]+1\n      j <- j + 1\n    }\n    dp[i] <- best\n  }\n  i <- i + 1\n}\n"
          "result <- if (m == 0) 0 else dp[m]"),
})

add("palindrome-partitioning", "str1", "count_partitions", "int", {
    "python": ("m = len(s)\nis_pal = [[False]*m for _ in range(m)]\nfor i in range(m):\n    is_pal[i][i] = True\n"
               "for length in range(2, m+1):\n    for i in range(0, m-length+1):\n        j = i+length-1\n"
               "        if s[i] == s[j] and (length == 2 or is_pal[i+1][j-1]):\n            is_pal[i][j] = True\n"
               "dp = [0]*(m+1)\ndp[0] = 1\nfor i in range(1, m+1):\n    total = 0\n    for j in range(0, i):\n"
               "        if is_pal[j][i-1]:\n            total += dp[j]\n    dp[i] = total\nresult = dp[m]"),
    "go": ("m := len(s)\nisPal := make([][]bool, m)\nfor i := range isPal { isPal[i] = make([]bool, m) }\n"
           "for i := 0; i < m; i++ { isPal[i][i] = true }\n"
           "for length := 2; length <= m; length++ {\n  for i := 0; i+length-1 < m; i++ {\n    j := i+length-1\n"
           "    if s[i] == s[j] && (length == 2 || isPal[i+1][j-1]) { isPal[i][j] = true }\n  }\n}\n"
           "dp := make([]int64, m+1)\ndp[0] = 1\nfor i := 1; i <= m; i++ {\n  var total int64 = 0\n  for j := 0; j < i; j++ {\n"
           "    if isPal[j][i-1] { total += dp[j] }\n  }\n  dp[i] = total\n}\nresult := dp[m]"),
    "ruby": ("m = s.length\nis_pal = Array.new(m) { Array.new(m, false) }\n(0...m).each { |i| is_pal[i][i] = true }\n"
             "(2..m).each do |len|\n  (0..(m-len)).each do |i|\n    j = i+len-1\n"
             "    is_pal[i][j] = true if s[i] == s[j] && (len == 2 || is_pal[i+1][j-1])\n  end\nend\n"
             "dp = Array.new(m+1, 0)\ndp[0] = 1\n(1..m).each do |i|\n  total = 0\n  (0...i).each { |j| total += dp[j] if is_pal[j][i-1] }\n  dp[i] = total\nend\n"
             "result = dp[m]"),
    "kotlin": ("val m = s.length\nval isPal = Array(m) { BooleanArray(m) }\nfor (i in 0 until m) isPal[i][i] = true\n"
               "for (len in 2..m) {\n  for (i in 0..(m-len)) {\n    val j = i+len-1\n"
               "    if (s[i] == s[j] && (len == 2 || isPal[i+1][j-1])) isPal[i][j] = true\n  }\n}\n"
               "val dp = LongArray(m+1)\ndp[0] = 1\nfor (i in 1..m) {\n  var total = 0L\n  for (j in 0 until i) { if (isPal[j][i-1]) total += dp[j] }\n  dp[i] = total\n}\n"
               "val result = dp[m]"),
    "php": ("$m = strlen($s);\n$isPal = array();\nfor ($i = 0; $i < $m; $i++) { $isPal[$i] = array_fill(0, $m, false); }\n"
            "for ($i = 0; $i < $m; $i++) { $isPal[$i][$i] = true; }\n"
            "for ($len = 2; $len <= $m; $len++) {\n  for ($i = 0; $i + $len - 1 < $m; $i++) {\n    $j = $i + $len - 1;\n"
            "    if ($s[$i] == $s[$j] && ($len == 2 || $isPal[$i+1][$j-1])) { $isPal[$i][$j] = true; }\n  }\n}\n"
            "$dp = array_fill(0, $m+1, 0);\n$dp[0] = 1;\nfor ($i = 1; $i <= $m; $i++) {\n  $total = 0;\n"
            "  for ($j = 0; $j < $i; $j++) { if ($isPal[$j][$i-1]) { $total += $dp[$j]; } }\n  $dp[$i] = $total;\n}\n$result = $dp[$m];"),
    "scala": ("val m = s.length\nval isPal = Array.fill(m, m)(false)\nfor (i <- 0 until m) isPal(i)(i) = true\n"
              "for (len <- 2 to m; i <- 0 to (m-len)) {\n  val j = i+len-1\n"
              "  if (s(i) == s(j) && (len == 2 || isPal(i+1)(j-1))) isPal(i)(j) = true\n}\n"
              "val dp = Array.fill(m+1)(0L)\ndp(0) = 1L\nfor (i <- 1 to m) {\n  var total = 0L\n  for (j <- 0 until i) { if (isPal(j)(i-1)) total += dp(j) }\n  dp(i) = total\n}\n"
              "val result: Long = dp(m)"),
    "r": ("m <- nchar(s)\nsb <- if (m > 0) strsplit(s, \"\")[[1]] else character(0)\n"
          "isPal <- matrix(FALSE, nrow = max(m,1), ncol = max(m,1))\n"
          "i <- 1\nwhile (i <= m) { isPal[i, i] <- TRUE; i <- i + 1 }\n"
          "len <- 2\nwhile (len <= m) {\n  i <- 1\n  while (i <= m - len + 1) {\n    j <- i + len - 1\n"
          "    if (sb[i] == sb[j] && (len == 2 || isPal[i+1, j-1])) isPal[i, j] <- TRUE\n    i <- i + 1\n  }\n  len <- len + 1\n}\n"
          "dp <- rep(0, m+1)\ndp[1] <- 1\ni <- 1\nwhile (i <= m) {\n  total <- 0\n  j <- 1\n  while (j <= i) {\n"
          "    if (isPal[j, i]) total <- total + dp[j]\n    j <- j + 1\n  }\n  dp[i+1] <- total\n  i <- i + 1\n}\n"
          "result <- dp[m+1]"),
})

add("palindrome-subsequence", "str1", "lps", "int", {
    "python": ("m = len(s)\ndp = [[0]*m for _ in range(m)]\nfor i in range(m-1, -1, -1):\n    dp[i][i] = 1\n"
               "    for j in range(i+1, m):\n        if s[i] == s[j]:\n            dp[i][j] = (dp[i+1][j-1] if i+1 <= j-1 else 0) + 2\n"
               "        else:\n            dp[i][j] = max(dp[i+1][j], dp[i][j-1])\nresult = 0 if m == 0 else dp[0][m-1]"),
    "go": ("m := len(s)\ndp := make([][]int, m)\nfor i := range dp { dp[i] = make([]int, m) }\n"
           "for i := m-1; i >= 0; i-- {\n  dp[i][i] = 1\n  for j := i+1; j < m; j++ {\n    if s[i] == s[j] {\n      inner := 0\n"
           "      if i+1 <= j-1 { inner = dp[i+1][j-1] }\n      dp[i][j] = inner + 2\n    } else {\n"
           "      a, b := dp[i+1][j], dp[i][j-1]\n      if a > b { dp[i][j] = a } else { dp[i][j] = b }\n    }\n  }\n}\n"
           "result := int64(0)\nif m > 0 { result = int64(dp[0][m-1]) }"),
    "ruby": ("m = s.length\ndp = Array.new(m) { Array.new(m, 0) }\n(m-1).downto(0) do |i|\n  dp[i][i] = 1\n"
             "  ((i+1)...m).each do |j|\n    if s[i] == s[j]\n      inner = (i+1 <= j-1) ? dp[i+1][j-1] : 0\n      dp[i][j] = inner + 2\n"
             "    else\n      dp[i][j] = [dp[i+1][j], dp[i][j-1]].max\n    end\n  end\nend\nresult = m == 0 ? 0 : dp[0][m-1]"),
    "kotlin": ("val m = s.length\nval dp = Array(m) { IntArray(m) }\nfor (i in m-1 downTo 0) {\n  dp[i][i] = 1\n"
               "  for (j in i+1 until m) {\n    if (s[i] == s[j]) {\n      val inner = if (i+1 <= j-1) dp[i+1][j-1] else 0\n      dp[i][j] = inner + 2\n"
               "    } else {\n      dp[i][j] = maxOf(dp[i+1][j], dp[i][j-1])\n    }\n  }\n}\n"
               "val result = if (m == 0) 0L else dp[0][m-1].toLong()"),
    "php": ("$m = strlen($s);\n$dp = array();\nfor ($i = 0; $i < $m; $i++) { $dp[$i] = array_fill(0, $m, 0); }\n"
            "for ($i = $m - 1; $i >= 0; $i--) {\n  $dp[$i][$i] = 1;\n  for ($j = $i + 1; $j < $m; $j++) {\n"
            "    if ($s[$i] == $s[$j]) {\n      $inner = ($i+1 <= $j-1) ? $dp[$i+1][$j-1] : 0;\n      $dp[$i][$j] = $inner + 2;\n"
            "    } else {\n      $dp[$i][$j] = max($dp[$i+1][$j], $dp[$i][$j-1]);\n    }\n  }\n}\n$result = $m == 0 ? 0 : $dp[0][$m-1];"),
    "scala": ("val m = s.length\nval dp = Array.fill(m, m)(0)\nfor (i <- (m-1) to 0 by -1) {\n  dp(i)(i) = 1\n"
              "  for (j <- (i+1) until m) {\n    if (s(i) == s(j)) {\n      val inner = if (i+1 <= j-1) dp(i+1)(j-1) else 0\n      dp(i)(j) = inner + 2\n"
              "    } else {\n      dp(i)(j) = math.max(dp(i+1)(j), dp(i)(j-1))\n    }\n  }\n}\n"
              "val result: Long = if (m == 0) 0L else dp(0)(m-1).toLong"),
    "r": ("m <- nchar(s)\nsb <- if (m > 0) strsplit(s, \"\")[[1]] else character(0)\ndp <- matrix(0, nrow = max(m,1), ncol = max(m,1))\n"
          "i <- m\nwhile (i >= 1) {\n  dp[i, i] <- 1\n  j <- i + 1\n  while (j <= m) {\n    if (sb[i] == sb[j]) {\n"
          "      inner <- if (i+1 <= j-1) dp[i+1, j-1] else 0\n      dp[i, j] <- inner + 2\n    } else {\n      dp[i, j] <- max(dp[i+1, j], dp[i, j-1])\n    }\n"
          "    j <- j + 1\n  }\n  i <- i - 1\n}\nresult <- if (m == 0) 0 else dp[1, m]"),
})

add("restore-ip-addresses-count", "str1", "restore_ip_count", "int", {
    "python": ("m = len(s)\ndef valid(seg):\n    if len(seg) > 1 and seg[0] == '0':\n        return False\n"
               "    if len(seg) == 0 or len(seg) > 3:\n        return False\n    v = int(seg)\n    return 0 <= v <= 255\n"
               "count = 0\nfor a in range(1, min(4, m)):\n    for b in range(a+1, min(a+4, m)):\n        for c in range(b+1, min(b+4, m)):\n"
               "            s1, s2, s3, s4 = s[0:a], s[a:b], s[b:c], s[c:]\n            if 1 <= len(s4) <= 3 and valid(s1) and valid(s2) and valid(s3) and valid(s4):\n"
               "                count += 1\nresult = count"),
    "go": ("m := len(s)\nvalid := func(seg string) bool {\n  if len(seg) > 1 && seg[0] == '0' { return false }\n"
           "  if len(seg) == 0 || len(seg) > 3 { return false }\n  v := 0\n  for k := 0; k < len(seg); k++ { v = v*10 + int(seg[k]-'0') }\n"
           "  return v >= 0 && v <= 255\n}\ncount := int64(0)\nfor a := 1; a <= 3 && a < m; a++ {\n  for b := a+1; b < a+4 && b < m; b++ {\n"
           "    for c := b+1; c < b+4 && c < m; c++ {\n      s1, s2, s3, s4 := s[0:a], s[a:b], s[b:c], s[c:]\n"
           "      if len(s4) >= 1 && len(s4) <= 3 && valid(s1) && valid(s2) && valid(s3) && valid(s4) { count++ }\n    }\n  }\n}\nresult := count"),
    "ruby": ("m = s.length\nvalid = lambda do |seg|\n  next false if seg.length > 1 && seg[0] == '0'\n  next false if seg.length == 0 || seg.length > 3\n"
             "  v = seg.to_i\n  v >= 0 && v <= 255\nend\ncount = 0\n(1...[4, m].min).each do |a|\n  (a+1...[a+4, m].min).each do |b|\n"
             "    (b+1...[b+4, m].min).each do |c|\n      s1, s2, s3, s4 = s[0...a], s[a...b], s[b...c], s[c..]\n"
             "      if s4.length >= 1 && s4.length <= 3 && valid.call(s1) && valid.call(s2) && valid.call(s3) && valid.call(s4)\n        count += 1\n      end\n    end\n  end\nend\nresult = count"),
    "kotlin": ("val m = s.length\nfun validSeg(seg: String): Boolean {\n  if (seg.length > 1 && seg[0] == '0') return false\n"
               "  if (seg.isEmpty() || seg.length > 3) return false\n  val v = seg.toInt()\n  return v in 0..255\n}\n"
               "var count = 0L\nfor (a in 1 until minOf(4, m)) {\n  for (b in (a+1) until minOf(a+4, m)) {\n    for (c in (b+1) until minOf(b+4, m)) {\n"
               "      val s1 = s.substring(0, a); val s2 = s.substring(a, b); val s3 = s.substring(b, c); val s4 = s.substring(c)\n"
               "      if (s4.length in 1..3 && validSeg(s1) && validSeg(s2) && validSeg(s3) && validSeg(s4)) count++\n    }\n  }\n}\nval result = count"),
    "php": ("$m = strlen($s);\n$validSeg = function($seg) {\n  $len = strlen($seg);\n  if ($len > 1 && $seg[0] == '0') return false;\n"
            "  if ($len == 0 || $len > 3) return false;\n  $v = intval($seg);\n  return $v >= 0 && $v <= 255;\n};\n"
            "$count = 0;\nfor ($a = 1; $a <= 3 && $a < $m; $a++) {\n  for ($b = $a+1; $b < $a+4 && $b < $m; $b++) {\n"
            "    for ($c = $b+1; $c < $b+4 && $c < $m; $c++) {\n      $s1 = substr($s, 0, $a); $s2 = substr($s, $a, $b-$a); $s3 = substr($s, $b, $c-$b); $s4 = substr($s, $c);\n"
            "      $l4 = strlen($s4);\n      if ($l4 >= 1 && $l4 <= 3 && $validSeg($s1) && $validSeg($s2) && $validSeg($s3) && $validSeg($s4)) { $count++; }\n    }\n  }\n}\n$result = $count;"),
    "scala": ("val m = s.length\ndef validSeg(seg: String): Boolean = {\n  if (seg.length > 1 && seg(0) == '0') return false\n"
              "  if (seg.isEmpty || seg.length > 3) return false\n  val v = seg.toInt\n  v >= 0 && v <= 255\n}\n"
              "var count = 0L\nfor (a <- 1 until math.min(4, m)) {\n  for (b <- (a+1) until math.min(a+4, m)) {\n    for (c <- (b+1) until math.min(b+4, m)) {\n"
              "      val s1 = s.substring(0, a); val s2 = s.substring(a, b); val s3 = s.substring(b, c); val s4 = s.substring(c)\n"
              "      if (s4.length >= 1 && s4.length <= 3 && validSeg(s1) && validSeg(s2) && validSeg(s3) && validSeg(s4)) count += 1\n    }\n  }\n}\nval result: Long = count"),
    "r": ("m <- nchar(s)\nvalidSeg <- function(seg) {\n  l <- nchar(seg)\n  if (l > 1 && substr(seg, 1, 1) == '0') return(FALSE)\n"
          "  if (l == 0 || l > 3) return(FALSE)\n  v <- as.integer(seg)\n  return(v >= 0 && v <= 255)\n}\n"
          "count <- 0\na <- 1\nwhile (a <= 3 && a < m) {\n  b <- a + 1\n  while (b < a + 4 && b < m) {\n    c <- b + 1\n"
          "    while (c < b + 4 && c < m) {\n      s1 <- substr(s, 1, a); s2 <- substr(s, a+1, b); s3 <- substr(s, b+1, c); s4 <- substr(s, c+1, m)\n"
          "      l4 <- nchar(s4)\n      if (l4 >= 1 && l4 <= 3 && validSeg(s1) && validSeg(s2) && validSeg(s3) && validSeg(s4)) count <- count + 1\n"
          "      c <- c + 1\n    }\n    b <- b + 1\n  }\n  a <- a + 1\n}\nresult <- count"),
})

add("longest-repeating-char-replacement", "str1_int", "character_replacement", "int", {
    "python": ("cnt = [0]*26\nleft = 0\nmax_count = 0\nbest = 0\nfor right in range(len(s)):\n    c = ord(s[right]) - 65\n    cnt[c] += 1\n"
               "    if cnt[c] > max_count:\n        max_count = cnt[c]\n    while (right - left + 1) - max_count > extra:\n"
               "        cnt[ord(s[left]) - 65] -= 1\n        left += 1\n    if right - left + 1 > best:\n        best = right - left + 1\nresult = best"),
    "go": ("cnt := make([]int, 26)\nleft, maxCount, best := 0, 0, 0\nfor right := 0; right < len(s); right++ {\n  c := int(s[right]-'A')\n  cnt[c]++\n"
           "  if cnt[c] > maxCount { maxCount = cnt[c] }\n  for (right-left+1)-maxCount > extra {\n    cnt[s[left]-'A']--\n    left++\n  }\n"
           "  if right-left+1 > best { best = right-left+1 }\n}\nresult := int64(best)"),
    "ruby": ("cnt = Array.new(26, 0)\nleft = 0; max_count = 0; best = 0\n(0...s.length).each do |right|\n  c = s[right].ord - 65\n  cnt[c] += 1\n"
             "  max_count = cnt[c] if cnt[c] > max_count\n  while (right - left + 1) - max_count > extra\n    cnt[s[left].ord - 65] -= 1\n    left += 1\n  end\n"
             "  best = right - left + 1 if right - left + 1 > best\nend\nresult = best"),
    "kotlin": ("val cnt = IntArray(26)\nvar left = 0; var maxCount = 0; var best = 0\nfor (right in s.indices) {\n  val c = s[right] - 'A'\n  cnt[c]++\n"
               "  if (cnt[c] > maxCount) maxCount = cnt[c]\n  while ((right-left+1)-maxCount > extra) { cnt[s[left]-'A']--; left++ }\n"
               "  if (right-left+1 > best) best = right-left+1\n}\nval result = best.toLong()"),
    "php": ("$cnt = array_fill(0, 26, 0);\n$left = 0; $maxCount = 0; $best = 0;\nfor ($right = 0; $right < strlen($s); $right++) {\n"
            "  $c = ord($s[$right]) - 65;\n  $cnt[$c]++;\n  if ($cnt[$c] > $maxCount) { $maxCount = $cnt[$c]; }\n"
            "  while (($right - $left + 1) - $maxCount > $extra) {\n    $cnt[ord($s[$left]) - 65]--;\n    $left++;\n  }\n"
            "  if ($right - $left + 1 > $best) { $best = $right - $left + 1; }\n}\n$result = $best;"),
    "scala": ("val cnt = Array.fill(26)(0)\nvar left = 0; var maxCount = 0; var best = 0\nfor (right <- s.indices) {\n  val c = s(right) - 'A'\n  cnt(c) += 1\n"
              "  if (cnt(c) > maxCount) maxCount = cnt(c)\n  while ((right-left+1)-maxCount > extra) { cnt(s(left)-'A') -= 1; left += 1 }\n"
              "  if (right-left+1 > best) best = right-left+1\n}\nval result: Long = best.toLong"),
    "r": ("n <- nchar(s)\nsb <- if (n > 0) strsplit(s, \"\")[[1]] else character(0)\ncnt <- rep(0, 26)\nleft <- 1; maxCount <- 0; best <- 0\nright <- 1\n"
          "while (right <= n) {\n  c <- utf8ToInt(sb[right]) - utf8ToInt('A') + 1\n  cnt[c] <- cnt[c] + 1\n  if (cnt[c] > maxCount) maxCount <- cnt[c]\n"
          "  while ((right - left + 1) - maxCount > extra) {\n    cl <- utf8ToInt(sb[left]) - utf8ToInt('A') + 1\n    cnt[cl] <- cnt[cl] - 1\n    left <- left + 1\n  }\n"
          "  if (right - left + 1 > best) best <- right - left + 1\n  right <- right + 1\n}\nresult <- best"),
})

add("longest-substring-at-most-k-distinct", "str1_int", "longest_k_distinct", "int", {
    "python": ("cnt = {}\nleft = 0\nbest = 0\nfor right in range(len(s)):\n    ch = s[right]\n    cnt[ch] = cnt.get(ch, 0) + 1\n"
               "    while len(cnt) > extra:\n        lc = s[left]\n        cnt[lc] -= 1\n        if cnt[lc] == 0:\n            del cnt[lc]\n        left += 1\n"
               "    if right - left + 1 > best:\n        best = right - left + 1\nresult = best"),
    "go": ("cnt := make(map[byte]int)\nleft, best := 0, 0\nfor right := 0; right < len(s); right++ {\n  cnt[s[right]]++\n"
           "  for len(cnt) > int(extra) {\n    lc := s[left]\n    cnt[lc]--\n    if cnt[lc] == 0 { delete(cnt, lc) }\n    left++\n  }\n"
           "  if right-left+1 > best { best = right-left+1 }\n}\nresult := int64(best)"),
    "ruby": ("cnt = Hash.new(0)\nleft = 0; best = 0\n(0...s.length).each do |right|\n  cnt[s[right]] += 1\n  while cnt.size > extra\n"
             "    lc = s[left]\n    cnt[lc] -= 1\n    cnt.delete(lc) if cnt[lc] == 0\n    left += 1\n  end\n"
             "  best = right - left + 1 if right - left + 1 > best\nend\nresult = best"),
    "kotlin": ("val cnt = HashMap<Char, Int>()\nvar left = 0; var best = 0\nfor (right in s.indices) {\n  cnt[s[right]] = (cnt[s[right]] ?: 0) + 1\n"
               "  while (cnt.size > extra) {\n    val lc = s[left]\n    cnt[lc] = cnt[lc]!! - 1\n    if (cnt[lc] == 0) cnt.remove(lc)\n    left++\n  }\n"
               "  if (right-left+1 > best) best = right-left+1\n}\nval result = best.toLong()"),
    "php": ("$cnt = array();\n$left = 0; $best = 0;\nfor ($right = 0; $right < strlen($s); $right++) {\n  $ch = $s[$right];\n"
            "  $cnt[$ch] = ($cnt[$ch] ?? 0) + 1;\n  while (count($cnt) > $extra) {\n    $lc = $s[$left];\n    $cnt[$lc]--;\n"
            "    if ($cnt[$lc] == 0) { unset($cnt[$lc]); }\n    $left++;\n  }\n  if ($right - $left + 1 > $best) { $best = $right - $left + 1; }\n}\n$result = $best;"),
    "scala": ("val cnt = scala.collection.mutable.HashMap[Char, Int]()\nvar left = 0; var best = 0\nfor (right <- s.indices) {\n"
              "  cnt(s(right)) = cnt.getOrElse(s(right), 0) + 1\n  while (cnt.size > extra) {\n    val lc = s(left)\n    cnt(lc) -= 1\n"
              "    if (cnt(lc) == 0) cnt.remove(lc)\n    left += 1\n  }\n  if (right-left+1 > best) best = right-left+1\n}\nval result: Long = best.toLong"),
    "r": ("n <- nchar(s)\nsb <- if (n > 0) strsplit(s, \"\")[[1]] else character(0)\ncnt <- new.env()\ncntSize <- 0\nleft <- 1; best <- 0\nright <- 1\n"
          "while (right <= n) {\n  ch <- sb[right]\n  if (is.null(cnt[[ch]])) { cnt[[ch]] <- 1; cntSize <- cntSize + 1 } else { cnt[[ch]] <- cnt[[ch]] + 1 }\n"
          "  while (cntSize > extra) {\n    lc <- sb[left]\n    cnt[[lc]] <- cnt[[lc]] - 1\n"
          "    if (cnt[[lc]] == 0) { rm(list=lc, envir=cnt); cntSize <- cntSize - 1 }\n    left <- left + 1\n  }\n"
          "  if (right - left + 1 > best) best <- right - left + 1\n  right <- right + 1\n}\nresult <- best"),
})

add("longest-common-substring", "str2", "longest_common_substring", "int", {
    "python": ("m, n2 = len(s), len(t)\ndp = [[0]*(n2+1) for _ in range(m+1)]\nbest = 0\nfor i in range(1, m+1):\n    for j in range(1, n2+1):\n"
               "        if s[i-1] == t[j-1]:\n            dp[i][j] = dp[i-1][j-1] + 1\n            if dp[i][j] > best:\n                best = dp[i][j]\nresult = best"),
    "go": ("m, n2 := len(s), len(t)\ndp := make([][]int, m+1)\nfor i := range dp { dp[i] = make([]int, n2+1) }\nbest := 0\n"
           "for i := 1; i <= m; i++ {\n  for j := 1; j <= n2; j++ {\n    if s[i-1] == t[j-1] {\n      dp[i][j] = dp[i-1][j-1] + 1\n"
           "      if dp[i][j] > best { best = dp[i][j] }\n    }\n  }\n}\nresult := int64(best)"),
    "ruby": ("m = s.length; n2 = t.length\ndp = Array.new(m+1) { Array.new(n2+1, 0) }\nbest = 0\n(1..m).each do |i|\n  (1..n2).each do |j|\n"
             "    if s[i-1] == t[j-1]\n      dp[i][j] = dp[i-1][j-1] + 1\n      best = dp[i][j] if dp[i][j] > best\n    end\n  end\nend\nresult = best"),
    "kotlin": ("val m = s.length; val n2 = t.length\nval dp = Array(m+1) { IntArray(n2+1) }\nvar best = 0\nfor (i in 1..m) {\n  for (j in 1..n2) {\n"
               "    if (s[i-1] == t[j-1]) {\n      dp[i][j] = dp[i-1][j-1] + 1\n      if (dp[i][j] > best) best = dp[i][j]\n    }\n  }\n}\nval result = best.toLong()"),
    "php": ("$m = strlen($s); $n2 = strlen($t);\n$dp = array();\nfor ($i = 0; $i <= $m; $i++) { $dp[$i] = array_fill(0, $n2+1, 0); }\n$best = 0;\n"
            "for ($i = 1; $i <= $m; $i++) {\n  for ($j = 1; $j <= $n2; $j++) {\n    if ($s[$i-1] == $t[$j-1]) {\n      $dp[$i][$j] = $dp[$i-1][$j-1] + 1;\n"
            "      if ($dp[$i][$j] > $best) { $best = $dp[$i][$j]; }\n    }\n  }\n}\n$result = $best;"),
    "scala": ("val m = s.length; val n2 = t.length\nval dp = Array.fill(m+1, n2+1)(0)\nvar best = 0\nfor (i <- 1 to m; j <- 1 to n2) {\n"
              "  if (s(i-1) == t(j-1)) {\n    dp(i)(j) = dp(i-1)(j-1) + 1\n    if (dp(i)(j) > best) best = dp(i)(j)\n  }\n}\nval result: Long = best.toLong"),
    "r": ("m <- nchar(s); n2 <- nchar(t)\nsb <- if (m > 0) strsplit(s, \"\")[[1]] else character(0)\ntb <- if (n2 > 0) strsplit(t, \"\")[[1]] else character(0)\n"
          "dp <- matrix(0, nrow = m+1, ncol = n2+1)\nbest <- 0\ni <- 1\nwhile (i <= m) {\n  j <- 1\n  while (j <= n2) {\n"
          "    if (sb[i] == tb[j]) {\n      dp[i+1, j+1] <- dp[i, j] + 1\n      if (dp[i+1, j+1] > best) best <- dp[i+1, j+1]\n    }\n    j <- j + 1\n  }\n  i <- i + 1\n}\nresult <- best"),
})

add("minimum-window-substring-length", "str2", "min_window_length", "int", {
    "python": ("need = {}\nfor ch in t:\n    need[ch] = need.get(ch, 0) + 1\nrequired = len(need)\nformed = 0\nwindow = {}\nleft = 0\nbest = -1\n"
               "for right in range(len(s)):\n    c = s[right]\n    window[c] = window.get(c, 0) + 1\n    if c in need and window[c] == need[c]:\n        formed += 1\n"
               "    while formed == required:\n        if best == -1 or right - left + 1 < best:\n            best = right - left + 1\n        lc = s[left]\n"
               "        window[lc] -= 1\n        if lc in need and window[lc] < need[lc]:\n            formed -= 1\n        left += 1\nresult = 0 if best == -1 else best"),
    "go": ("need := make(map[byte]int)\nfor i := 0; i < len(t); i++ { need[t[i]]++ }\nrequired := len(need)\nformed := 0\nwindow := make(map[byte]int)\nleft := 0\nbest := -1\n"
           "for right := 0; right < len(s); right++ {\n  c := s[right]\n  window[c]++\n  if nv, ok := need[c]; ok && window[c] == nv { formed++ }\n"
           "  for formed == required {\n    if best == -1 || right-left+1 < best { best = right-left+1 }\n    lc := s[left]\n    window[lc]--\n"
           "    if nv, ok := need[lc]; ok && window[lc] < nv { formed-- }\n    left++\n  }\n}\nresult := int64(0)\nif best != -1 { result = int64(best) }"),
    "ruby": ("need = Hash.new(0)\nt.each_char { |ch| need[ch] += 1 }\nrequired = need.size\nformed = 0\nwindow = Hash.new(0)\nleft = 0\nbest = -1\n"
             "(0...s.length).each do |right|\n  c = s[right]\n  window[c] += 1\n  formed += 1 if need.key?(c) && window[c] == need[c]\n"
             "  while formed == required\n    best = right - left + 1 if best == -1 || right - left + 1 < best\n    lc = s[left]\n    window[lc] -= 1\n"
             "    formed -= 1 if need.key?(lc) && window[lc] < need[lc]\n    left += 1\n  end\nend\nresult = best == -1 ? 0 : best"),
    "kotlin": ("val need = HashMap<Char, Int>()\nfor (ch in t) need[ch] = (need[ch] ?: 0) + 1\nval required = need.size\nvar formed = 0\nval window = HashMap<Char, Int>()\nvar left = 0\nvar best = -1\n"
               "for (right in s.indices) {\n  val c = s[right]\n  window[c] = (window[c] ?: 0) + 1\n  if (need.containsKey(c) && window[c] == need[c]) formed++\n"
               "  while (formed == required) {\n    if (best == -1 || right-left+1 < best) best = right-left+1\n    val lc = s[left]\n    window[lc] = window[lc]!! - 1\n"
               "    if (need.containsKey(lc) && window[lc]!! < need[lc]!!) formed--\n    left++\n  }\n}\nval result = if (best == -1) 0L else best.toLong()"),
    "php": ("$need = array();\nfor ($i = 0; $i < strlen($t); $i++) { $need[$t[$i]] = ($need[$t[$i]] ?? 0) + 1; }\n$required = count($need);\n$formed = 0;\n$window = array();\n$left = 0;\n$best = -1;\n"
            "for ($right = 0; $right < strlen($s); $right++) {\n  $c = $s[$right];\n  $window[$c] = ($window[$c] ?? 0) + 1;\n"
            "  if (isset($need[$c]) && $window[$c] == $need[$c]) { $formed++; }\n  while ($formed == $required) {\n"
            "    if ($best == -1 || $right - $left + 1 < $best) { $best = $right - $left + 1; }\n    $lc = $s[$left];\n    $window[$lc]--;\n"
            "    if (isset($need[$lc]) && $window[$lc] < $need[$lc]) { $formed--; }\n    $left++;\n  }\n}\n$result = $best == -1 ? 0 : $best;"),
    "scala": ("val need = scala.collection.mutable.HashMap[Char, Int]()\nfor (ch <- t) need(ch) = need.getOrElse(ch, 0) + 1\nval required = need.size\nvar formed = 0\n"
              "val window = scala.collection.mutable.HashMap[Char, Int]()\nvar left = 0\nvar best = -1\nfor (right <- s.indices) {\n  val c = s(right)\n"
              "  window(c) = window.getOrElse(c, 0) + 1\n  if (need.contains(c) && window(c) == need(c)) formed += 1\n  while (formed == required) {\n"
              "    if (best == -1 || right-left+1 < best) best = right-left+1\n    val lc = s(left)\n    window(lc) -= 1\n"
              "    if (need.contains(lc) && window(lc) < need(lc)) formed -= 1\n    left += 1\n  }\n}\nval result: Long = if (best == -1) 0L else best.toLong"),
    "r": ("n <- nchar(s); tn <- nchar(t)\nsb <- if (n > 0) strsplit(s, \"\")[[1]] else character(0)\ntb <- if (tn > 0) strsplit(t, \"\")[[1]] else character(0)\n"
          "need <- new.env()\nk <- 1\nwhile (k <= tn) {\n  ch <- tb[k]\n  if (is.null(need[[ch]])) need[[ch]] <- 1 else need[[ch]] <- need[[ch]] + 1\n  k <- k + 1\n}\n"
          "required <- length(ls(need))\nformed <- 0\nwindow <- new.env()\nleft <- 1\nbest <- -1\nright <- 1\n"
          "while (right <= n) {\n  c <- sb[right]\n  if (is.null(window[[c]])) window[[c]] <- 1 else window[[c]] <- window[[c]] + 1\n"
          "  if (!is.null(need[[c]]) && window[[c]] == need[[c]]) formed <- formed + 1\n  while (formed == required) {\n"
          "    if (best == -1 || right - left + 1 < best) best <- right - left + 1\n    lc <- sb[left]\n    window[[lc]] <- window[[lc]] - 1\n"
          "    if (!is.null(need[[lc]]) && window[[lc]] < need[[lc]]) formed <- formed - 1\n    left <- left + 1\n  }\n  right <- right + 1\n}\n"
          "result <- if (best == -1) 0 else best"),
})

add("boolean-parenthesization", "str2", "count_ways", "int", {
    "python": ("m = len(s)\nT = [[0]*m for _ in range(m)]\nF = [[0]*m for _ in range(m)]\nfor i in range(m):\n    T[i][i] = 1 if s[i] == 'T' else 0\n    F[i][i] = 1 if s[i] == 'F' else 0\n"
               "for length in range(2, m+1):\n    for i in range(0, m-length+1):\n        j = i+length-1\n        tc = 0\n        fc = 0\n        for k in range(i, j):\n"
               "            op = t[k]\n            lt, lf, rt, rf = T[i][k], F[i][k], T[k+1][j], F[k+1][j]\n            total = (lt+lf)*(rt+rf)\n"
               "            if op == '&':\n                tc += lt*rt\n                fc += total - lt*rt\n            elif op == '|':\n                fc += lf*rf\n                tc += total - lf*rf\n"
               "            else:\n                tc += lt*rf + lf*rt\n                fc += lt*rt + lf*rf\n        T[i][j] = tc\n        F[i][j] = fc\nresult = T[0][m-1] if m > 0 else 0"),
    "go": ("m := len(s)\nT := make([][]int64, m)\nF := make([][]int64, m)\nfor i := range T { T[i] = make([]int64, m); F[i] = make([]int64, m) }\n"
           "for i := 0; i < m; i++ {\n  if s[i] == 'T' { T[i][i] = 1 } else { F[i][i] = 1 }\n}\n"
           "for length := 2; length <= m; length++ {\n  for i := 0; i+length-1 < m; i++ {\n    j := i+length-1\n    var tc, fc int64 = 0, 0\n"
           "    for k := i; k < j; k++ {\n      op := t[k]\n      lt, lf, rt, rf := T[i][k], F[i][k], T[k+1][j], F[k+1][j]\n      total := (lt+lf)*(rt+rf)\n"
           "      if op == '&' { tc += lt*rt; fc += total - lt*rt\n      } else if op == '|' { fc += lf*rf; tc += total - lf*rf\n      } else { tc += lt*rf + lf*rt; fc += lt*rt + lf*rf }\n    }\n"
           "    T[i][j] = tc\n    F[i][j] = fc\n  }\n}\nresult := int64(0)\nif m > 0 { result = T[0][m-1] }"),
    "ruby": ("m = s.length\ntarr = Array.new(m) { Array.new(m, 0) }\nfarr = Array.new(m) { Array.new(m, 0) }\n(0...m).each do |i|\n"
             "  tarr[i][i] = s[i] == 'T' ? 1 : 0\n  farr[i][i] = s[i] == 'F' ? 1 : 0\nend\n(2..m).each do |len|\n  (0..(m-len)).each do |i|\n    j = i+len-1\n    tc = 0; fc = 0\n"
             "    (i...j).each do |k|\n      op = t[k]\n      lt, lf, rt, rf = tarr[i][k], farr[i][k], tarr[k+1][j], farr[k+1][j]\n      total = (lt+lf)*(rt+rf)\n"
             "      if op == '&'\n        tc += lt*rt; fc += total - lt*rt\n      elsif op == '|'\n        fc += lf*rf; tc += total - lf*rf\n      else\n        tc += lt*rf + lf*rt; fc += lt*rt + lf*rf\n      end\n    end\n"
             "    tarr[i][j] = tc; farr[i][j] = fc\n  end\nend\nresult = m == 0 ? 0 : tarr[0][m-1]"),
    "kotlin": ("val m = s.length\nval T = Array(m) { LongArray(m) }\nval F = Array(m) { LongArray(m) }\nfor (i in 0 until m) {\n"
               "  T[i][i] = if (s[i] == 'T') 1L else 0L\n  F[i][i] = if (s[i] == 'F') 1L else 0L\n}\nfor (len in 2..m) {\n  for (i in 0..(m-len)) {\n    val j = i+len-1\n    var tc = 0L; var fc = 0L\n"
               "    for (k in i until j) {\n      val op = t[k]\n      val lt = T[i][k]; val lf = F[i][k]; val rt = T[k+1][j]; val rf = F[k+1][j]\n      val total = (lt+lf)*(rt+rf)\n"
               "      if (op == '&') { tc += lt*rt; fc += total - lt*rt }\n      else if (op == '|') { fc += lf*rf; tc += total - lf*rf }\n      else { tc += lt*rf + lf*rt; fc += lt*rt + lf*rf }\n    }\n"
               "    T[i][j] = tc; F[i][j] = fc\n  }\n}\nval result = if (m == 0) 0L else T[0][m-1]"),
    "php": ("$m = strlen($s);\n$T = array(); $F = array();\nfor ($i = 0; $i < $m; $i++) { $T[$i] = array_fill(0, $m, 0); $F[$i] = array_fill(0, $m, 0); }\n"
            "for ($i = 0; $i < $m; $i++) {\n  $T[$i][$i] = $s[$i] == 'T' ? 1 : 0;\n  $F[$i][$i] = $s[$i] == 'F' ? 1 : 0;\n}\n"
            "for ($len = 2; $len <= $m; $len++) {\n  for ($i = 0; $i + $len - 1 < $m; $i++) {\n    $j = $i + $len - 1;\n    $tc = 0; $fc = 0;\n"
            "    for ($k = $i; $k < $j; $k++) {\n      $op = $t[$k];\n      $lt = $T[$i][$k]; $lf = $F[$i][$k]; $rt = $T[$k+1][$j]; $rf = $F[$k+1][$j];\n      $total = ($lt+$lf)*($rt+$rf);\n"
            "      if ($op == '&') { $tc += $lt*$rt; $fc += $total - $lt*$rt; }\n      else if ($op == '|') { $fc += $lf*$rf; $tc += $total - $lf*$rf; }\n      else { $tc += $lt*$rf + $lf*$rt; $fc += $lt*$rt + $lf*$rf; }\n    }\n"
            "    $T[$i][$j] = $tc; $F[$i][$j] = $fc;\n  }\n}\n$result = $m == 0 ? 0 : $T[0][$m-1];"),
    "scala": ("val m = s.length\nval T = Array.fill(m, m)(0L)\nval F = Array.fill(m, m)(0L)\nfor (i <- 0 until m) {\n"
              "  T(i)(i) = if (s(i) == 'T') 1L else 0L\n  F(i)(i) = if (s(i) == 'F') 1L else 0L\n}\nfor (len <- 2 to m; i <- 0 to (m-len)) {\n  val j = i+len-1\n  var tc = 0L; var fc = 0L\n"
              "  for (k <- i until j) {\n    val op = t(k)\n    val lt = T(i)(k); val lf = F(i)(k); val rt = T(k+1)(j); val rf = F(k+1)(j)\n    val total = (lt+lf)*(rt+rf)\n"
              "    if (op == '&') { tc += lt*rt; fc += total - lt*rt }\n    else if (op == '|') { fc += lf*rf; tc += total - lf*rf }\n    else { tc += lt*rf + lf*rt; fc += lt*rt + lf*rf }\n  }\n"
              "  T(i)(j) = tc; F(i)(j) = fc\n}\nval result: Long = if (m == 0) 0L else T(0)(m-1)"),
    "r": ("m <- nchar(s)\nsb <- if (m > 0) strsplit(s, \"\")[[1]] else character(0)\ntb <- if (nchar(t) > 0) strsplit(t, \"\")[[1]] else character(0)\n"
          "Tm <- matrix(0, nrow = max(m,1), ncol = max(m,1))\nFm <- matrix(0, nrow = max(m,1), ncol = max(m,1))\ni <- 1\nwhile (i <= m) {\n"
          "  Tm[i, i] <- if (sb[i] == 'T') 1 else 0\n  Fm[i, i] <- if (sb[i] == 'F') 1 else 0\n  i <- i + 1\n}\nlen <- 2\nwhile (len <= m) {\n  i <- 1\n  while (i <= m - len + 1) {\n"
          "    j <- i + len - 1\n    tc <- 0; fc <- 0\n    k <- i\n    while (k <= j - 1) {\n      op <- tb[k]\n      lt <- Tm[i, k]; lf <- Fm[i, k]; rt <- Tm[k+1, j]; rf <- Fm[k+1, j]\n"
          "      total <- (lt+lf)*(rt+rf)\n      if (op == '&') { tc <- tc + lt*rt; fc <- fc + total - lt*rt }\n      else if (op == '|') { fc <- fc + lf*rf; tc <- tc + total - lf*rf }\n"
          "      else { tc <- tc + lt*rf + lf*rt; fc <- fc + lt*rt + lf*rf }\n      k <- k + 1\n    }\n    Tm[i, j] <- tc; Fm[i, j] <- fc\n    i <- i + 1\n  }\n  len <- len + 1\n}\n"
          "result <- if (m == 0) 0 else Tm[1, m]"),
})

add("matrix-chain-multiplication", "arr1", "matrix_chain_order", "int", {
    "python": ("p = nums\nn = len(p) - 1\nif n < 1:\n    result = 0\nelse:\n    dp = [[0]*(n+1) for _ in range(n+1)]\n    for length in range(2, n+1):\n"
               "        for i in range(1, n-length+2):\n            j = i+length-1\n            dp[i][j] = 1 << 62\n            for k in range(i, j):\n"
               "                cost = dp[i][k] + dp[k+1][j] + p[i-1]*p[k]*p[j]\n                if cost < dp[i][j]:\n                    dp[i][j] = cost\n    result = dp[1][n]"),
    "go": ("p := nums\nn := len(p) - 1\nvar result int64 = 0\nif n >= 1 {\n  dp := make([][]int64, n+1)\n  for i := range dp { dp[i] = make([]int64, n+1) }\n"
           "  for length := 2; length <= n; length++ {\n    for i := 1; i <= n-length+1; i++ {\n      j := i+length-1\n      dp[i][j] = 1 << 62\n      for k := i; k < j; k++ {\n"
           "        cost := dp[i][k] + dp[k+1][j] + int64(p[i-1])*int64(p[k])*int64(p[j])\n        if cost < dp[i][j] { dp[i][j] = cost }\n      }\n    }\n  }\n  result = dp[1][n]\n}"),
    "ruby": ("p = nums\nn = p.length - 1\nif n < 1\n  result = 0\nelse\n  dp = Array.new(n+1) { Array.new(n+1, 0) }\n  (2..n).each do |len|\n"
             "    (1..(n-len+1)).each do |i|\n      j = i+len-1\n      dp[i][j] = 1 << 62\n      (i...j).each do |k|\n        cost = dp[i][k] + dp[k+1][j] + p[i-1]*p[k]*p[j]\n"
             "        dp[i][j] = cost if cost < dp[i][j]\n      end\n    end\n  end\n  result = dp[1][n]\nend"),
    "kotlin": ("val p = nums\nval n = p.size - 1\nvar result = 0L\nif (n >= 1) {\n  val dp = Array(n+1) { LongArray(n+1) }\n  for (len in 2..n) {\n"
               "    for (i in 1..(n-len+1)) {\n      val j = i+len-1\n      dp[i][j] = Long.MAX_VALUE / 2\n      for (k in i until j) {\n"
               "        val cost = dp[i][k] + dp[k+1][j] + p[i-1].toLong()*p[k].toLong()*p[j].toLong()\n        if (cost < dp[i][j]) dp[i][j] = cost\n      }\n    }\n  }\n  result = dp[1][n]\n}"),
    "php": ("$p = $nums;\n$n = count($p) - 1;\nif ($n < 1) {\n  $result = 0;\n} else {\n  $dp = array();\n  for ($i = 0; $i <= $n; $i++) { $dp[$i] = array_fill(0, $n+1, 0); }\n"
            "  for ($len = 2; $len <= $n; $len++) {\n    for ($i = 1; $i <= $n-$len+1; $i++) {\n      $j = $i+$len-1;\n      $dp[$i][$j] = PHP_INT_MAX;\n"
            "      for ($k = $i; $k < $j; $k++) {\n        $cost = $dp[$i][$k] + $dp[$k+1][$j] + $p[$i-1]*$p[$k]*$p[$j];\n        if ($cost < $dp[$i][$j]) { $dp[$i][$j] = $cost; }\n      }\n    }\n  }\n  $result = $dp[1][$n];\n}"),
    "scala": ("val p = nums\nval n = p.length - 1\nvar result = 0L\nif (n >= 1) {\n  val dp = Array.fill(n+1, n+1)(0L)\n  for (len <- 2 to n) {\n"
              "    for (i <- 1 to (n-len+1)) {\n      val j = i+len-1\n      dp(i)(j) = Long.MaxValue / 2\n      for (k <- i until j) {\n"
              "        val cost = dp(i)(k) + dp(k+1)(j) + p(i-1).toLong*p(k).toLong*p(j).toLong\n        if (cost < dp(i)(j)) dp(i)(j) = cost\n      }\n    }\n  }\n  result = dp(1)(n)\n}"),
    "r": ("p <- nums\nn <- length(p) - 1\nif (n < 1) {\n  result <- 0\n} else {\n  dp <- matrix(0, nrow = n+1, ncol = n+1)\n  len <- 2\n  while (len <= n) {\n"
          "    i <- 1\n    while (i <= n - len + 1) {\n      j <- i + len - 1\n      best <- Inf\n      k <- i\n      while (k <= j - 1) {\n"
          "        cost <- dp[i+1, k+1] + dp[k+2, j+1] + p[i] * p[k+1] * p[j+1]\n        if (cost < best) best <- cost\n        k <- k + 1\n      }\n      dp[i+1, j+1] <- best\n      i <- i + 1\n    }\n    len <- len + 1\n  }\n"
          "  result <- dp[2, n+1]\n}"),
})

add("burst-balloons", "arr1", "max_coins", "int", {
    "python": ("b = [1] + list(nums) + [1]\nn = len(b)\ndp = [[0]*n for _ in range(n)]\nfor length in range(2, n):\n    for left in range(0, n-length):\n"
               "        right = left+length\n        best = 0\n        for k in range(left+1, right):\n            val = dp[left][k] + dp[k][right] + b[left]*b[k]*b[right]\n"
               "            if val > best:\n                best = val\n        dp[left][right] = best\nresult = dp[0][n-1]"),
    "go": ("b := append(append([]int{1}, nums...), 1)\nn := len(b)\ndp := make([][]int64, n)\nfor i := range dp { dp[i] = make([]int64, n) }\n"
           "for length := 2; length < n; length++ {\n  for left := 0; left < n-length; left++ {\n    right := left+length\n    var best int64 = 0\n"
           "    for k := left+1; k < right; k++ {\n      val := dp[left][k] + dp[k][right] + int64(b[left])*int64(b[k])*int64(b[right])\n      if val > best { best = val }\n    }\n    dp[left][right] = best\n  }\n}\nresult := dp[0][n-1]"),
    "ruby": ("b = [1] + nums + [1]\nn = b.length\ndp = Array.new(n) { Array.new(n, 0) }\n(2...n).each do |len|\n  (0...(n-len)).each do |left|\n    right = left+len\n    best = 0\n"
             "    ((left+1)...right).each do |k|\n      val = dp[left][k] + dp[k][right] + b[left]*b[k]*b[right]\n      best = val if val > best\n    end\n    dp[left][right] = best\n  end\nend\nresult = dp[0][n-1]"),
    "kotlin": ("val b = mutableListOf(1); b.addAll(nums.toList()); b.add(1)\nval n = b.size\nval dp = Array(n) { LongArray(n) }\nfor (len in 2 until n) {\n"
               "  for (left in 0 until (n-len)) {\n    val right = left+len\n    var best = 0L\n    for (k in (left+1) until right) {\n"
               "      val v = dp[left][k] + dp[k][right] + b[left].toLong()*b[k].toLong()*b[right].toLong()\n      if (v > best) best = v\n    }\n    dp[left][right] = best\n  }\n}\nval result = dp[0][n-1]"),
    "php": ("$b = array_merge(array(1), $nums, array(1));\n$n = count($b);\n$dp = array();\nfor ($i = 0; $i < $n; $i++) { $dp[$i] = array_fill(0, $n, 0); }\n"
            "for ($len = 2; $len < $n; $len++) {\n  for ($left = 0; $left < $n-$len; $left++) {\n    $right = $left+$len;\n    $best = 0;\n"
            "    for ($k = $left+1; $k < $right; $k++) {\n      $val = $dp[$left][$k] + $dp[$k][$right] + $b[$left]*$b[$k]*$b[$right];\n      if ($val > $best) { $best = $val; }\n    }\n    $dp[$left][$right] = $best;\n  }\n}\n$result = $dp[0][$n-1];"),
    "scala": ("val b = Array(1) ++ nums ++ Array(1)\nval n = b.length\nval dp = Array.fill(n, n)(0L)\nfor (len <- 2 until n) {\n  for (left <- 0 until (n-len)) {\n    val right = left+len\n    var best = 0L\n"
              "    for (k <- (left+1) until right) {\n      val v = dp(left)(k) + dp(k)(right) + b(left).toLong*b(k).toLong*b(right).toLong\n      if (v > best) best = v\n    }\n    dp(left)(right) = best\n  }\n}\nval result: Long = dp(0)(n-1)"),
    "r": ("nn <- length(nums)\nb <- c(1, nums, 1)\nn <- nn + 2\ndp <- matrix(0, nrow = n, ncol = n)\nlen <- 2\nwhile (len <= n - 1) {\n  left <- 0\n  while (left <= n - 1 - len) {\n    right <- left + len\n    best <- 0\n"
          "    k <- left + 1\n    while (k <= right - 1) {\n      val <- dp[left+1, k+1] + dp[k+1, right+1] + b[left+1] * b[k+1] * b[right+1]\n      if (val > best) best <- val\n      k <- k + 1\n    }\n"
          "    dp[left+1, right+1] <- best\n    left <- left + 1\n  }\n  len <- len + 1\n}\nresult <- dp[1, n]"),
})

add("task-scheduler", "arr1_int", "least_interval", "int", {
    "python": ("total = sum(nums)\nmax_count = max(nums) if nums else 0\nnum_max = sum(1 for x in nums if x == max_count)\nresult = max(total, (max_count-1)*(extra+1)+num_max)"),
    "go": ("var total int64 = 0\nmaxCount := 0\nfor _, x := range nums { total += int64(x); if x > maxCount { maxCount = x } }\n"
           "numMax := 0\nfor _, x := range nums { if x == maxCount { numMax++ } }\ncand := int64(maxCount-1)*int64(extra+1) + int64(numMax)\nresult := total\nif cand > result { result = cand }"),
    "ruby": ("total = nums.sum\nmax_count = nums.empty? ? 0 : nums.max\nnum_max = nums.count { |x| x == max_count }\nresult = [total, (max_count-1)*(extra+1)+num_max].max"),
    "kotlin": ("val total = nums.sumOf { it.toLong() }\nval maxCount = if (nums.isEmpty()) 0 else nums.max()\nval numMax = nums.count { it == maxCount }\n"
               "val cand = (maxCount-1).toLong()*(extra+1).toLong() + numMax.toLong()\nval result = maxOf(total, cand)"),
    "php": ("$total = array_sum($nums);\n$maxCount = count($nums) > 0 ? max($nums) : 0;\n$numMax = 0;\nforeach ($nums as $x) { if ($x == $maxCount) { $numMax++; } }\n"
            "$cand = ($maxCount-1)*($extra+1)+$numMax;\n$result = max($total, $cand);"),
    "scala": ("val total = nums.map(_.toLong).sum\nval maxCount = if (nums.isEmpty) 0 else nums.max\nval numMax = nums.count(_ == maxCount)\n"
              "val cand = (maxCount-1).toLong*(extra+1).toLong + numMax.toLong\nval result: Long = math.max(total, cand)"),
    "r": ("total <- sum(nums)\nmaxCount <- if (length(nums) > 0) max(nums) else 0\nnumMax <- sum(nums == maxCount)\ncand <- (maxCount-1)*(extra+1)+numMax\nresult <- max(total, cand)"),
})

add("coin-change", "arr1_int", "coin_change", "int", {
    "python": ("INF = 1 << 40\ndp = [INF]*(extra+1)\ndp[0] = 0\nfor i in range(1, extra+1):\n    for c in nums:\n        if c <= i and dp[i-c]+1 < dp[i]:\n            dp[i] = dp[i-c]+1\nresult = -1 if dp[extra] == INF else dp[extra]"),
    "go": ("const INF = int64(1) << 40\ndp := make([]int64, extra+1)\nfor i := range dp { dp[i] = INF }\ndp[0] = 0\nfor i := 1; i <= extra; i++ {\n"
           "  for _, c := range nums {\n    if c <= i && dp[i-c]+1 < dp[i] { dp[i] = dp[i-c]+1 }\n  }\n}\nresult := dp[extra]\nif result == INF { result = -1 }"),
    "ruby": ("inf = 1 << 40\ndp = Array.new(extra+1, inf)\ndp[0] = 0\n(1..extra).each do |i|\n  nums.each do |c|\n    if c <= i && dp[i-c]+1 < dp[i]\n      dp[i] = dp[i-c]+1\n    end\n  end\nend\nresult = dp[extra] == inf ? -1 : dp[extra]"),
    "kotlin": ("val INF = Long.MAX_VALUE / 2\nval dp = LongArray(extra+1) { INF }\ndp[0] = 0\nfor (i in 1..extra) {\n  for (c in nums) {\n    if (c <= i && dp[i-c]+1 < dp[i]) dp[i] = dp[i-c]+1\n  }\n}\nval result = if (dp[extra] >= INF) -1L else dp[extra]"),
    "php": ("$INF = PHP_INT_MAX;\n$dp = array_fill(0, $extra+1, $INF);\n$dp[0] = 0;\nfor ($i = 1; $i <= $extra; $i++) {\n  foreach ($nums as $c) {\n"
            "    if ($c <= $i && $dp[$i-$c]+1 < $dp[$i]) { $dp[$i] = $dp[$i-$c]+1; }\n  }\n}\n$result = $dp[$extra] == $INF ? -1 : $dp[$extra];"),
    "scala": ("val INF = Long.MaxValue / 2\nval dp = Array.fill(extra+1)(INF)\ndp(0) = 0L\nfor (i <- 1 to extra) {\n  for (c <- nums) {\n    if (c <= i && dp(i-c)+1 < dp(i)) dp(i) = dp(i-c)+1\n  }\n}\nval result: Long = if (dp(extra) >= INF) -1L else dp(extra)"),
    "r": ("INF <- .Machine$integer.max\ndp <- rep(INF, extra+1)\ndp[1] <- 0\nif (extra >= 1) {\n  i <- 1\n  while (i <= extra) {\n    for (c in nums) {\n"
          "      if (c <= i && dp[i-c+1]+1 < dp[i+1]) dp[i+1] <- dp[i-c+1]+1\n    }\n    i <- i + 1\n  }\n}\nresult <- if (dp[extra+1] >= INF) -1 else dp[extra+1]"),
})

add("coin-change-ways", "arr1_int", "change", "int", {
    "python": ("dp = [0]*(extra+1)\ndp[0] = 1\nfor c in nums:\n    for i in range(c, extra+1):\n        dp[i] += dp[i-c]\nresult = dp[extra]"),
    "go": ("dp := make([]int64, extra+1)\ndp[0] = 1\nfor _, c := range nums {\n  for i := c; i <= extra; i++ { dp[i] += dp[i-c] }\n}\nresult := dp[extra]"),
    "ruby": ("dp = Array.new(extra+1, 0)\ndp[0] = 1\nnums.each do |c|\n  (c..extra).each { |i| dp[i] += dp[i-c] }\nend\nresult = dp[extra]"),
    "kotlin": ("val dp = LongArray(extra+1)\ndp[0] = 1\nfor (c in nums) {\n  for (i in c..extra) { dp[i] += dp[i-c] }\n}\nval result = dp[extra]"),
    "php": ("$dp = array_fill(0, $extra+1, 0);\n$dp[0] = 1;\nforeach ($nums as $c) {\n  for ($i = $c; $i <= $extra; $i++) { $dp[$i] += $dp[$i-$c]; }\n}\n$result = $dp[$extra];"),
    "scala": ("val dp = Array.fill(extra+1)(0L)\ndp(0) = 1L\nfor (c <- nums) {\n  for (i <- c to extra) { dp(i) += dp(i-c) }\n}\nval result: Long = dp(extra)"),
    "r": ("dp <- rep(0, extra+1)\ndp[1] <- 1\nfor (c in nums) {\n  if (c <= extra) {\n    i <- c\n    while (i <= extra) {\n      dp[i+1] <- dp[i+1] + dp[i-c+1]\n      i <- i + 1\n    }\n  }\n}\nresult <- dp[extra+1]"),
})

add("job-scheduling", "arr2_samelen", "job_scheduling", "int", {
    "python": ("n = len(a)\nidx = sorted(range(n), key=lambda i: -b[i])\nmax_d = max(a) if n > 0 else 0\nslot = [False]*(max_d+1)\ntotal = 0\n"
               "for i in idx:\n    d = a[i]\n    while d >= 1:\n        if not slot[d]:\n            slot[d] = True\n            total += b[i]\n            break\n        d -= 1\nresult = total"),
    "go": ("n := len(a)\nidx := make([]int, n)\nfor i := range idx { idx[i] = i }\nfor i := 1; i < n; i++ {\n  key := idx[i]\n  j := i - 1\n"
           "  for j >= 0 && b[idx[j]] < b[key] {\n    idx[j+1] = idx[j]\n    j--\n  }\n  idx[j+1] = key\n}\n"
           "maxD := 0\nfor _, d := range a { if d > maxD { maxD = d } }\nslot := make([]bool, maxD+1)\nvar total int64 = 0\nfor _, i := range idx {\n  d := a[i]\n"
           "  for d >= 1 {\n    if !slot[d] { slot[d] = true; total += int64(b[i]); break }\n    d--\n  }\n}\nresult := total"),
    "ruby": ("n = a.length\nidx = (0...n).sort_by { |i| -b[i] }\nmax_d = a.empty? ? 0 : a.max\nslot = Array.new(max_d+1, false)\ntotal = 0\n"
             "idx.each do |i|\n  d = a[i]\n  while d >= 1\n    if !slot[d]\n      slot[d] = true\n      total += b[i]\n      break\n    end\n    d -= 1\n  end\nend\nresult = total"),
    "kotlin": ("val n = a.size\nval idx = (0 until n).sortedByDescending { b[it] }\nval maxD = if (a.isEmpty()) 0 else a.max()\nval slot = BooleanArray(maxD+1)\nvar total = 0L\n"
               "for (i in idx) {\n  var d = a[i]\n  while (d >= 1) {\n    if (!slot[d]) { slot[d] = true; total += b[i].toLong(); break }\n    d--\n  }\n}\nval result = total"),
    "php": ("$n = count($a);\n$idx = range(0, $n-1);\nusort($idx, function($x, $y) use ($b) { return $b[$y] - $b[$x]; });\n$maxD = $n > 0 ? max($a) : 0;\n$slot = array_fill(0, $maxD+1, false);\n$total = 0;\n"
            "foreach ($idx as $i) {\n  $d = $a[$i];\n  while ($d >= 1) {\n    if (!$slot[$d]) { $slot[$d] = true; $total += $b[$i]; break; }\n    $d--;\n  }\n}\n$result = $total;"),
    "scala": ("val n = a.length\nval idx = (0 until n).sortBy(i => -b(i))\nval maxD = if (a.isEmpty) 0 else a.max\nval slot = Array.fill(maxD+1)(false)\nvar total = 0L\n"
              "for (i <- idx) {\n  var d = a(i)\n  var placed = false\n  while (d >= 1 && !placed) {\n    if (!slot(d)) { slot(d) = true; total += b(i).toLong; placed = true }\n    d -= 1\n  }\n}\nval result: Long = total"),
    "r": ("n <- length(a)\nord <- order(-b)\nmaxD <- if (n > 0) max(a) else 0\nslot <- rep(FALSE, maxD+1)\ntotal <- 0\nfor (i in ord) {\n  d <- a[i]\n  placed <- FALSE\n"
          "  while (d >= 1 && !placed) {\n    if (!slot[d+1]) { slot[d+1] <- TRUE; total <- total + b[i]; placed <- TRUE }\n    d <- d - 1\n  }\n}\nresult <- total"),
})

add("meeting-rooms", "arr2_samelen", "min_meeting_rooms", "int", {
    "python": ("starts = sorted(a)\nends = sorted(b)\nrooms = 0\nbest = 0\nsi = 0\nei = 0\nn = len(starts)\nwhile si < n:\n    if starts[si] < ends[ei]:\n        rooms += 1\n"
               "        if rooms > best:\n            best = rooms\n        si += 1\n    else:\n        rooms -= 1\n        ei += 1\nresult = best"),
    "go": ("starts := append([]int{}, a...)\nends := append([]int{}, b...)\ninsSort := func(arr []int) {\n  for i := 1; i < len(arr); i++ {\n    key := arr[i]\n    j := i - 1\n"
           "    for j >= 0 && arr[j] > key { arr[j+1] = arr[j]; j-- }\n    arr[j+1] = key\n  }\n}\ninsSort(starts)\ninsSort(ends)\n"
           "rooms, best, si, ei := 0, 0, 0, 0\nn := len(starts)\nfor si < n {\n  if starts[si] < ends[ei] {\n    rooms++\n    if rooms > best { best = rooms }\n    si++\n  } else {\n    rooms--\n    ei++\n  }\n}\nresult := int64(best)"),
    "ruby": ("starts = a.sort\nends = b.sort\nrooms = 0; best = 0; si = 0; ei = 0\nn = starts.length\nwhile si < n\n  if starts[si] < ends[ei]\n    rooms += 1\n    best = rooms if rooms > best\n    si += 1\n  else\n    rooms -= 1\n    ei += 1\n  end\nend\nresult = best"),
    "kotlin": ("val starts = a.sorted()\nval ends = b.sorted()\nvar rooms = 0; var best = 0; var si = 0; var ei = 0\nval n = starts.size\nwhile (si < n) {\n  if (starts[si] < ends[ei]) {\n"
               "    rooms++\n    if (rooms > best) best = rooms\n    si++\n  } else {\n    rooms--\n    ei++\n  }\n}\nval result = best.toLong()"),
    "php": ("$starts = $a; sort($starts);\n$ends = $b; sort($ends);\n$rooms = 0; $best = 0; $si = 0; $ei = 0;\n$n = count($starts);\nwhile ($si < $n) {\n"
            "  if ($starts[$si] < $ends[$ei]) {\n    $rooms++;\n    if ($rooms > $best) { $best = $rooms; }\n    $si++;\n  } else {\n    $rooms--;\n    $ei++;\n  }\n}\n$result = $best;"),
    "scala": ("val starts = a.sorted\nval ends = b.sorted\nvar rooms = 0; var best = 0; var si = 0; var ei = 0\nval n = starts.length\nwhile (si < n) {\n  if (starts(si) < ends(ei)) {\n"
              "    rooms += 1\n    if (rooms > best) best = rooms\n    si += 1\n  } else {\n    rooms -= 1\n    ei += 1\n  }\n}\nval result: Long = best.toLong"),
    "r": ("starts <- sort(a)\nends <- sort(b)\nrooms <- 0; best <- 0; si <- 1; ei <- 1\nn <- length(starts)\nwhile (si <= n) {\n  if (starts[si] < ends[ei]) {\n"
          "    rooms <- rooms + 1\n    if (rooms > best) best <- rooms\n    si <- si + 1\n  } else {\n    rooms <- rooms - 1\n    ei <- ei + 1\n  }\n}\nresult <- best"),
})

add("unbounded-knapsack", "arr2_int", "unbounded_knapsack", "int", {
    "python": ("dp = [0]*(extra+1)\nfor c in range(1, extra+1):\n    for i in range(len(a)):\n        if a[i] <= c and dp[c-a[i]]+b[i] > dp[c]:\n            dp[c] = dp[c-a[i]]+b[i]\nresult = dp[extra]"),
    "go": ("dp := make([]int64, extra+1)\nfor c := 1; c <= extra; c++ {\n  for i := 0; i < len(a); i++ {\n    if a[i] <= c {\n      v := dp[c-a[i]] + int64(b[i])\n      if v > dp[c] { dp[c] = v }\n    }\n  }\n}\nresult := dp[extra]"),
    "ruby": ("dp = Array.new(extra+1, 0)\n(1..extra).each do |c|\n  (0...a.length).each do |i|\n    if a[i] <= c && dp[c-a[i]]+b[i] > dp[c]\n      dp[c] = dp[c-a[i]]+b[i]\n    end\n  end\nend\nresult = dp[extra]"),
    "kotlin": ("val dp = LongArray(extra+1)\nfor (c in 1..extra) {\n  for (i in a.indices) {\n    if (a[i] <= c) {\n      val v = dp[c-a[i]] + b[i].toLong()\n      if (v > dp[c]) dp[c] = v\n    }\n  }\n}\nval result = dp[extra]"),
    "php": ("$dp = array_fill(0, $extra+1, 0);\nfor ($c = 1; $c <= $extra; $c++) {\n  for ($i = 0; $i < count($a); $i++) {\n    if ($a[$i] <= $c && $dp[$c-$a[$i]]+$b[$i] > $dp[$c]) {\n      $dp[$c] = $dp[$c-$a[$i]]+$b[$i];\n    }\n  }\n}\n$result = $dp[$extra];"),
    "scala": ("val dp = Array.fill(extra+1)(0L)\nfor (c <- 1 to extra) {\n  for (i <- a.indices) {\n    if (a(i) <= c) {\n      val v = dp(c-a(i)) + b(i).toLong\n      if (v > dp(c)) dp(c) = v\n    }\n  }\n}\nval result: Long = dp(extra)"),
    "r": ("dp <- rep(0, extra+1)\nif (extra >= 1) {\n  c <- 1\n  while (c <= extra) {\n    i <- 1\n    while (i <= length(a)) {\n      if (a[i] <= c) {\n        v <- dp[c-a[i]+1] + b[i]\n        if (v > dp[c+1]) dp[c+1] <- v\n      }\n      i <- i + 1\n    }\n    c <- c + 1\n  }\n}\nresult <- dp[extra+1]"),
})

add("triangle-minimum-path-sum", "triangle", "minimum_total", "int", {
    "python": ("m = len(triangle)\nif m == 0:\n    result = 0\nelse:\n    dp = list(triangle[m-1])\n    for i in range(m-2, -1, -1):\n        nxt = [0]*(i+1)\n        for j in range(i+1):\n"
               "            nxt[j] = triangle[i][j] + min(dp[j], dp[j+1])\n        dp = nxt\n    result = dp[0]"),
    "go": ("m := len(triangle)\nvar result int64 = 0\nif m > 0 {\n  dp := make([]int64, m)\n  for j, v := range triangle[m-1] { dp[j] = int64(v) }\n"
           "  for i := m-2; i >= 0; i-- {\n    next := make([]int64, i+1)\n    for j := 0; j <= i; j++ {\n      mn := dp[j]\n      if dp[j+1] < mn { mn = dp[j+1] }\n      next[j] = int64(triangle[i][j]) + mn\n    }\n    dp = next\n  }\n  result = dp[0]\n}"),
    "ruby": ("m = triangle.length\nif m == 0\n  result = 0\nelse\n  dp = triangle[m-1].dup\n  (m-2).downto(0) do |i|\n    nxt = Array.new(i+1, 0)\n    (0..i).each do |j|\n"
             "      nxt[j] = triangle[i][j] + [dp[j], dp[j+1]].min\n    end\n    dp = nxt\n  end\n  result = dp[0]\nend"),
    "kotlin": ("val m = triangle.size\nvar result = 0L\nif (m > 0) {\n  var dp = triangle[m-1].map { it.toLong() }.toLongArray()\n  for (i in (m-2) downTo 0) {\n"
               "    val next = LongArray(i+1)\n    for (j in 0..i) {\n      next[j] = triangle[i][j].toLong() + minOf(dp[j], dp[j+1])\n    }\n    dp = next\n  }\n  result = dp[0]\n}"),
    "php": ("$m = count($triangle);\nif ($m == 0) {\n  $result = 0;\n} else {\n  $dp = $triangle[$m-1];\n  for ($i = $m-2; $i >= 0; $i--) {\n    $next = array_fill(0, $i+1, 0);\n"
            "    for ($j = 0; $j <= $i; $j++) {\n      $next[$j] = $triangle[$i][$j] + min($dp[$j], $dp[$j+1]);\n    }\n    $dp = $next;\n  }\n  $result = $dp[0];\n}"),
    "scala": ("val m = triangle.length\nvar result = 0L\nif (m > 0) {\n  var dp = triangle(m-1).map(_.toLong)\n  for (i <- (m-2) to 0 by -1) {\n    val next = Array.fill(i+1)(0L)\n"
              "    for (j <- 0 to i) {\n      next(j) = triangle(i)(j).toLong + math.min(dp(j), dp(j+1))\n    }\n    dp = next\n  }\n  result = dp(0)\n}"),
    "r": ("m <- length(triangle)\nif (m == 0) {\n  result <- 0\n} else {\n  dp <- triangle[[m]]\n  i <- m - 1\n  while (i >= 1) {\n    nxt <- rep(0, i)\n    j <- 1\n    while (j <= i) {\n"
          "      nxt[j] <- triangle[[i]][j] + min(dp[j], dp[j+1])\n      j <- j + 1\n    }\n    dp <- nxt\n    i <- i - 1\n  }\n  result <- dp[1]\n}"),
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
            if lang not in PROBLEMS[pid]["bodies"]:
                continue
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
                    adapter_version="program-mega-batch7-remaining18-v1", test_suite_version=tsv,
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
