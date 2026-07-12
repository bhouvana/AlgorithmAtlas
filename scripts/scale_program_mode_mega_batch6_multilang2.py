"""Program Mode expansion, mega batch 6: ports mega_batch2.py's 22 problems
(string, multi-array, and 2D-triangle shapes) to SIX languages at once --
go, ruby, kotlin, php, scala, r -- continuing the combined-breadth pattern
from mega_batch5 per explicit user direction (many languages per batch,
not one at a time). All 22 algorithms are already proven correct in 8
other languages; this is syntax translation, reusing the shape harness
approach from mega_batch2/mega_batch5.
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
LANGS = ["go", "ruby", "kotlin", "php", "scala", "r"]


def rt(lang, kind):
    if lang in ("go", "kotlin", "scala"):
        return ("int64" if lang == "go" else "Long") if kind == "int" else ("bool" if lang == "go" else "Boolean")
    return None


def sig(lang, shape, fn, kind):
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


def assemble(lang, shape, fn, kind, body, wrong):
    read = read_code(lang, shape)
    signature = sig(lang, shape, fn, kind)
    args = call_args(lang, shape)
    p = print_stmt(lang, kind, wrong)

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


add("first-unique-character-index", "str1", "firstUniqChar", "int", {
    "go": ("cnt := make(map[rune]int)\nfor _, ch := range s { cnt[ch]++ }\nresult := int64(-1)\n"
           "for i, ch := range s { if cnt[ch] == 1 { result = int64(i); break } }"),
    "ruby": "cnt = Hash.new(0)\ns.each_char { |ch| cnt[ch] += 1 }\nresult = -1\ns.each_char.with_index { |ch, i| if cnt[ch] == 1 then result = i; break end }",
    "kotlin": "val cnt = HashMap<Char, Int>()\nfor (ch in s) cnt[ch] = (cnt[ch] ?: 0) + 1\nvar result = -1L\nfor (i in s.indices) { if (cnt[s[i]] == 1) { result = i.toLong(); break } }",
    "php": "$cnt = [];\nfor ($i = 0; $i < strlen($s); $i++) { $cnt[$s[$i]] = ($cnt[$s[$i]] ?? 0) + 1; }\n$result = -1;\nfor ($i = 0; $i < strlen($s); $i++) { if ($cnt[$s[$i]] == 1) { $result = $i; break; } }",
    "scala": "val cnt = scala.collection.mutable.HashMap[Char, Int]().withDefaultValue(0)\nfor (ch <- s) cnt(ch) += 1\nvar result = -1L\nfor (i <- s.indices) { if (result == -1L && cnt(s(i)) == 1) result = i }",
    "r": "chars <- strsplit(s, \"\")[[1]]\ncnt <- table(chars)\nresult <- -1\nif (length(chars) > 0) { for (i in 1:length(chars)) { if (cnt[[chars[i]]] == 1) { result <- i - 1; break } } }",
})

add("longest-palindromic-substring", "str1", "longestPalindrome", "int", {
    "go": ("expand := func(l, r int) int { for l >= 0 && r < len(s) && s[l] == s[r] { l--; r++ }; return r - l - 1 }\n"
           "best := 0\nfor i := 0; i < len(s); i++ { v1 := expand(i, i); v2 := expand(i, i+1); if v1 > best { best = v1 }; if v2 > best { best = v2 } }\nresult := int64(best)"),
    "ruby": "def expand_pal(s, l, r)\n  while l >= 0 && r < s.length && s[l] == s[r]\n    l -= 1\n    r += 1\n  end\n  r - l - 1\nend\nbest = 0\n(0...s.length).each do |i|\n  v1 = expand_pal(s, i, i)\n  v2 = expand_pal(s, i, i + 1)\n  best = v1 if v1 > best\n  best = v2 if v2 > best\nend\nresult = best",
    "kotlin": ("fun expandPal(s: String, lIn: Int, rIn: Int): Int { var l = lIn; var r = rIn; while (l >= 0 && r < s.length && s[l] == s[r]) { l--; r++ }; return r - l - 1 }\n"
               "var best = 0\nfor (i in s.indices) { val v1 = expandPal(s, i, i); val v2 = expandPal(s, i, i + 1); if (v1 > best) best = v1; if (v2 > best) best = v2 }\nval result = best.toLong()"),
    "php": ("function expandPal($s, $l, $r) { while ($l >= 0 && $r < strlen($s) && $s[$l] == $s[$r]) { $l--; $r++; } return $r - $l - 1; }\n"
            "$best = 0;\nfor ($i = 0; $i < strlen($s); $i++) { $v1 = expandPal($s, $i, $i); $v2 = expandPal($s, $i, $i + 1); if ($v1 > $best) $best = $v1; if ($v2 > $best) $best = $v2; }\n$result = $best;"),
    "scala": ("def expandPal(s: String, lIn: Int, rIn: Int): Int = { var l = lIn; var r = rIn; while (l >= 0 && r < s.length && s(l) == s(r)) { l -= 1; r += 1 }; r - l - 1 }\n"
              "var best = 0\nfor (i <- s.indices) { val v1 = expandPal(s, i, i); val v2 = expandPal(s, i, i + 1); if (v1 > best) best = v1; if (v2 > best) best = v2 }\nval result: Long = best"),
    "r": ("sb <- strsplit(s, \"\")[[1]]\nm <- length(sb)\nexpandPal <- function(l, r) {\n  while (l >= 1 && r <= m && sb[l] == sb[r]) { l <- l - 1; r <- r + 1 }\n  r - l - 1\n}\nbest <- 0\nif (m > 0) { for (i in 1:m) { v1 <- expandPal(i, i); v2 <- expandPal(i, i + 1); if (v1 > best) best <- v1; if (v2 > best) best <- v2 } }\nresult <- best"),
})

add("longest-valid-parentheses", "str1", "longestValidParentheses", "int", {
    "go": ("stack := []int{-1}\nbest := 0\nfor i := 0; i < len(s); i++ {\n  if s[i] == '(' { stack = append(stack, i) } else {\n    stack = stack[:len(stack)-1]\n    if len(stack) == 0 { stack = append(stack, i) } else { w := i - stack[len(stack)-1]; if w > best { best = w } }\n  }\n}\nresult := int64(best)"),
    "ruby": "stack = [-1]\nbest = 0\n(0...s.length).each do |i|\n  if s[i] == '('\n    stack.push(i)\n  else\n    stack.pop\n    if stack.empty?\n      stack.push(i)\n    else\n      w = i - stack[-1]\n      best = w if w > best\n    end\n  end\nend\nresult = best",
    "kotlin": ("val stack = ArrayDeque<Int>(); stack.addLast(-1)\nvar best = 0\nfor (i in s.indices) {\n  if (s[i] == '(') stack.addLast(i) else {\n    stack.removeLast()\n    if (stack.isEmpty()) stack.addLast(i) else { val w = i - stack.last(); if (w > best) best = w }\n  }\n}\nval result = best.toLong()"),
    "php": ("$stack = [-1];\n$best = 0;\nfor ($i = 0; $i < strlen($s); $i++) {\n  if ($s[$i] == '(') { $stack[] = $i; } else {\n    array_pop($stack);\n    if (empty($stack)) { $stack[] = $i; } else { $w = $i - end($stack); if ($w > $best) $best = $w; }\n  }\n}\n$result = $best;"),
    "scala": ("val stack = scala.collection.mutable.ArrayBuffer[Int](-1)\nvar best = 0\nfor (i <- s.indices) {\n  if (s(i) == '(') stack += i else {\n    stack.remove(stack.length - 1)\n    if (stack.isEmpty) stack += i else { val w = i - stack.last; if (w > best) best = w }\n  }\n}\nval result: Long = best"),
    "r": ("sb <- strsplit(s, \"\")[[1]]\nstack <- c(0)\nbest <- 0\nif (length(sb) > 0) {\n  for (i in 1:length(sb)) {\n    if (sb[i] == '(') { stack <- c(stack, i) } else {\n      stack <- stack[-length(stack)]\n      if (length(stack) == 0) { stack <- c(i) } else { w <- i - stack[length(stack)]; if (w > best) best <- w }\n    }\n  }\n}\nresult <- best"),
})

add("manacher", "str1", "countPalindromicSubstrings", "int", {
    "go": ("expand := func(l, r int) int { c := 0; for l >= 0 && r < len(s) && s[l] == s[r] { c++; l--; r++ }; return c }\n"
           "count := 0\nfor i := 0; i < len(s); i++ { count += expand(i, i); count += expand(i, i+1) }\nresult := int64(count)"),
    "ruby": "def expand_count(s, l, r)\n  c = 0\n  while l >= 0 && r < s.length && s[l] == s[r]\n    c += 1\n    l -= 1\n    r += 1\n  end\n  c\nend\ncount = 0\n(0...s.length).each do |i|\n  count += expand_count(s, i, i)\n  count += expand_count(s, i, i + 1)\nend\nresult = count",
    "kotlin": ("fun expandCount(s: String, lIn: Int, rIn: Int): Int { var l = lIn; var r = rIn; var c = 0; while (l >= 0 && r < s.length && s[l] == s[r]) { c++; l--; r++ }; return c }\n"
               "var count = 0\nfor (i in s.indices) { count += expandCount(s, i, i); count += expandCount(s, i, i + 1) }\nval result = count.toLong()"),
    "php": ("function expandCount($s, $l, $r) { $c = 0; while ($l >= 0 && $r < strlen($s) && $s[$l] == $s[$r]) { $c++; $l--; $r++; } return $c; }\n"
            "$count = 0;\nfor ($i = 0; $i < strlen($s); $i++) { $count += expandCount($s, $i, $i); $count += expandCount($s, $i, $i + 1); }\n$result = $count;"),
    "scala": ("def expandCount(s: String, lIn: Int, rIn: Int): Int = { var l = lIn; var r = rIn; var c = 0; while (l >= 0 && r < s.length && s(l) == s(r)) { c += 1; l -= 1; r += 1 }; c }\n"
              "var count = 0\nfor (i <- s.indices) { count += expandCount(s, i, i); count += expandCount(s, i, i + 1) }\nval result: Long = count"),
    "r": ("sb <- strsplit(s, \"\")[[1]]\nm <- length(sb)\nexpandCount <- function(l, r) {\n  c <- 0\n  while (l >= 1 && r <= m && sb[l] == sb[r]) { c <- c + 1; l <- l - 1; r <- r + 1 }\n  c\n}\ncount <- 0\nif (m > 0) { for (i in 1:m) { count <- count + expandCount(i, i) + expandCount(i, i + 1) } }\nresult <- count"),
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
                    adapter_version="program-mega-batch6-multilang2-v1", test_suite_version=tsv,
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
