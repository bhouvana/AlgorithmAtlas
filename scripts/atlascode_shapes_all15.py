"""Shared Program Mode shape harness covering ALL 15 target languages
(javascript, typescript, java, cpp, csharp, perl, c, rust, go, kotlin, php,
r, ruby, scala, swift) -- NOT a subset. Extends the 6-language shape system
from scale_program_mode_mega_batch6_multilang2.py (go/ruby/kotlin/php/
scala/r) with the other 9 so future batches never need to special-case
"the 8 core languages" vs "the newer 6" again (explicit user instruction,
2026-07-12: never scope a batch to a language subset).

Shapes supported (same set as mega_batch6): arr1, arr1_int, str1, str1_int,
str2, arr2_samelen, arr2_int, triangle. Every problem's `add()` call must
supply a body for ALL 15 languages -- the harness's own already_verified
check skips cells a prior session already covered, so redundant bodies for
already-covered languages cost nothing but do need to exist (build_program
indexes bodies[lang] unconditionally for any language reached).

kind is "int" or "bool". The harness auto-generates the "wrong" variant by
printing (result + 1) for int or (!result) for bool -- no separate
wrong-body needs to be hand-authored.
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

LANGS = ["javascript", "typescript", "java", "cpp", "csharp", "perl", "c", "rust",
          "go", "kotlin", "php", "r", "ruby", "scala", "swift"]

SHAPES = ("arr1", "arr1_int", "str1", "str1_int", "str2", "arr2_samelen", "arr2_int", "triangle",
          "int1", "int2", "int3")


def rt(lang, kind):
    """Native return-type token for typed languages; None for dynamic ones."""
    if lang == "go":
        return "int64" if kind == "int" else "bool"
    if lang in ("kotlin", "scala"):
        return "Long" if kind == "int" else "Boolean"
    if lang == "typescript":
        return "number" if kind == "int" else "boolean"
    if lang in ("java", "cpp", "csharp", "c"):
        return "int"
    if lang == "rust":
        return "i32" if kind == "int" else "bool"
    if lang == "swift":
        return "Int" if kind == "int" else "Bool"
    return None


# ═════════════════════════════════════════════════════════════════════════
# sig() -- function/method signature line for each (lang, shape)
# ═════════════════════════════════════════════════════════════════════════

def sig(lang, shape, fn, kind):
    r = rt(lang, kind)
    if lang == "go":
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
    if lang == "javascript":
        if shape == "arr1": return f"function {fn}(nums) {{"
        if shape == "arr1_int": return f"function {fn}(nums, extra) {{"
        if shape == "str1": return f"function {fn}(s) {{"
        if shape == "str1_int": return f"function {fn}(s, extra) {{"
        if shape == "str2": return f"function {fn}(s, t) {{"
        if shape == "arr2_samelen": return f"function {fn}(a, b) {{"
        if shape == "arr2_int": return f"function {fn}(a, b, extra) {{"
        if shape == "triangle": return f"function {fn}(triangle) {{"
    if lang == "typescript":
        if shape == "arr1": return f"function {fn}(nums: number[]): {r} {{"
        if shape == "arr1_int": return f"function {fn}(nums: number[], extra: number): {r} {{"
        if shape == "str1": return f"function {fn}(s: string): {r} {{"
        if shape == "str1_int": return f"function {fn}(s: string, extra: number): {r} {{"
        if shape == "str2": return f"function {fn}(s: string, t: string): {r} {{"
        if shape == "arr2_samelen": return f"function {fn}(a: number[], b: number[]): {r} {{"
        if shape == "arr2_int": return f"function {fn}(a: number[], b: number[], extra: number): {r} {{"
        if shape == "triangle": return f"function {fn}(triangle: number[][]): {r} {{"
    if lang == "perl":
        if shape == "arr1": return f"sub {fn} {{ my ($nums) = @_;"
        if shape == "arr1_int": return f"sub {fn} {{ my ($nums, $extra) = @_;"
        if shape == "str1": return f"sub {fn} {{ my ($s) = @_;"
        if shape == "str1_int": return f"sub {fn} {{ my ($s, $extra) = @_;"
        if shape == "str2": return f"sub {fn} {{ my ($s, $t) = @_;"
        if shape == "arr2_samelen": return f"sub {fn} {{ my ($a, $b) = @_;"
        if shape == "arr2_int": return f"sub {fn} {{ my ($a, $b, $extra) = @_;"
        if shape == "triangle": return f"sub {fn} {{ my ($triangle) = @_;"
    if lang == "java":
        if shape == "arr1": return f"static {r} {fn}(int[] nums) {{"
        if shape == "arr1_int": return f"static {r} {fn}(int[] nums, int extra) {{"
        if shape == "str1": return f"static {r} {fn}(String s) {{"
        if shape == "str1_int": return f"static {r} {fn}(String s, int extra) {{"
        if shape == "str2": return f"static {r} {fn}(String s, String t) {{"
        if shape == "arr2_samelen": return f"static {r} {fn}(int[] a, int[] b) {{"
        if shape == "arr2_int": return f"static {r} {fn}(int[] a, int[] b, int extra) {{"
        if shape == "triangle": return f"static {r} {fn}(int[][] triangle) {{"
    if lang == "cpp":
        if shape == "arr1": return f"{r} {fn}(std::vector<int>& nums) {{"
        if shape == "arr1_int": return f"{r} {fn}(std::vector<int>& nums, int extra) {{"
        if shape == "str1": return f"{r} {fn}(std::string s) {{"
        if shape == "str1_int": return f"{r} {fn}(std::string s, int extra) {{"
        if shape == "str2": return f"{r} {fn}(std::string s, std::string t) {{"
        if shape == "arr2_samelen": return f"{r} {fn}(std::vector<int>& a, std::vector<int>& b) {{"
        if shape == "arr2_int": return f"{r} {fn}(std::vector<int>& a, std::vector<int>& b, int extra) {{"
        if shape == "triangle": return f"{r} {fn}(std::vector<std::vector<int>>& triangle) {{"
    if lang == "csharp":
        if shape == "arr1": return f"static {r} {fn}(int[] nums) {{"
        if shape == "arr1_int": return f"static {r} {fn}(int[] nums, int extra) {{"
        if shape == "str1": return f"static {r} {fn}(string s) {{"
        if shape == "str1_int": return f"static {r} {fn}(string s, int extra) {{"
        if shape == "str2": return f"static {r} {fn}(string s, string t) {{"
        if shape == "arr2_samelen": return f"static {r} {fn}(int[] a, int[] b) {{"
        if shape == "arr2_int": return f"static {r} {fn}(int[] a, int[] b, int extra) {{"
        if shape == "triangle": return f"static {r} {fn}(int[][] triangle) {{"
    if lang == "c":
        if shape == "arr1": return f"{r} {fn}(int* nums, int n) {{"
        if shape == "arr1_int": return f"{r} {fn}(int* nums, int n, int extra) {{"
        if shape == "str1": return f"{r} {fn}(char* s) {{"
        if shape == "str1_int": return f"{r} {fn}(char* s, int extra) {{"
        if shape == "str2": return f"{r} {fn}(char* s, char* t) {{"
        if shape == "arr2_samelen": return f"{r} {fn}(int* a, int* b, int n) {{"
        if shape == "arr2_int": return f"{r} {fn}(int* a, int* b, int n, int extra) {{"
        if shape == "triangle": return f"{r} {fn}(int** triangle, int n) {{"
    if lang == "rust":
        if shape == "arr1": return f"fn {fn}(nums: &Vec<i32>) -> {r} {{"
        if shape == "arr1_int": return f"fn {fn}(nums: &Vec<i32>, extra: i32) -> {r} {{"
        if shape == "str1": return f"fn {fn}(s: &str) -> {r} {{"
        if shape == "str1_int": return f"fn {fn}(s: &str, extra: i32) -> {r} {{"
        if shape == "str2": return f"fn {fn}(s: &str, t: &str) -> {r} {{"
        if shape == "arr2_samelen": return f"fn {fn}(a: &Vec<i32>, b: &Vec<i32>) -> {r} {{"
        if shape == "arr2_int": return f"fn {fn}(a: &Vec<i32>, b: &Vec<i32>, extra: i32) -> {r} {{"
        if shape == "triangle": return f"fn {fn}(triangle: &Vec<Vec<i32>>) -> {r} {{"
    if lang == "swift":
        if shape == "arr1": return f"func {fn}(_ nums: [Int]) -> {r} {{"
        if shape == "arr1_int": return f"func {fn}(_ nums: [Int], _ extra: Int) -> {r} {{"
        if shape == "str1": return f"func {fn}(_ s: String) -> {r} {{"
        if shape == "str1_int": return f"func {fn}(_ s: String, _ extra: Int) -> {r} {{"
        if shape == "str2": return f"func {fn}(_ s: String, _ t: String) -> {r} {{"
        if shape == "arr2_samelen": return f"func {fn}(_ a: [Int], _ b: [Int]) -> {r} {{"
        if shape == "arr2_int": return f"func {fn}(_ a: [Int], _ b: [Int], _ extra: Int) -> {r} {{"
        if shape == "triangle": return f"func {fn}(_ triangle: [[Int]]) -> {r} {{"
    if shape == "int1":
        if lang == "go": return f"func {fn}(n int) {r} {{"
        if lang == "ruby": return f"def {fn}(n)"
        if lang == "kotlin": return f"fun {fn}(n: Int): {r} {{"
        if lang == "php": return f"function {fn}($n) {{"
        if lang == "scala": return f"def {fn}(n: Int): {r} = {{"
        if lang == "r": return f"{fn} <- function(n) {{"
        if lang == "javascript": return f"function {fn}(n) {{"
        if lang == "typescript": return f"function {fn}(n: number): {r} {{"
        if lang == "perl": return f"sub {fn} {{ my ($n) = @_;"
        if lang == "java": return f"static {r} {fn}(int n) {{"
        if lang == "cpp": return f"{r} {fn}(int n) {{"
        if lang == "csharp": return f"static {r} {fn}(int n) {{"
        if lang == "c": return f"{r} {fn}(int n) {{"
        if lang == "rust": return f"fn {fn}(n: i32) -> {r} {{"
        if lang == "swift": return f"func {fn}(_ n: Int) -> {r} {{"
    if shape == "int2":
        if lang == "go": return f"func {fn}(a int, b int) {r} {{"
        if lang == "ruby": return f"def {fn}(a, b)"
        if lang == "kotlin": return f"fun {fn}(a: Int, b: Int): {r} {{"
        if lang == "php": return f"function {fn}($a, $b) {{"
        if lang == "scala": return f"def {fn}(a: Int, b: Int): {r} = {{"
        if lang == "r": return f"{fn} <- function(a, b) {{"
        if lang == "javascript": return f"function {fn}(a, b) {{"
        if lang == "typescript": return f"function {fn}(a: number, b: number): {r} {{"
        if lang == "perl": return f"sub {fn} {{ my ($a, $b) = @_;"
        if lang == "java": return f"static {r} {fn}(int a, int b) {{"
        if lang == "cpp": return f"{r} {fn}(int a, int b) {{"
        if lang == "csharp": return f"static {r} {fn}(int a, int b) {{"
        if lang == "c": return f"{r} {fn}(int a, int b) {{"
        if lang == "rust": return f"fn {fn}(a: i32, b: i32) -> {r} {{"
        if lang == "swift": return f"func {fn}(_ a: Int, _ b: Int) -> {r} {{"
    if shape == "int3":
        if lang == "go": return f"func {fn}(a int, b int, c int) {r} {{"
        if lang == "ruby": return f"def {fn}(a, b, c)"
        if lang == "kotlin": return f"fun {fn}(a: Int, b: Int, c: Int): {r} {{"
        if lang == "php": return f"function {fn}($a, $b, $c) {{"
        if lang == "scala": return f"def {fn}(a: Int, b: Int, c: Int): {r} = {{"
        if lang == "r": return f"{fn} <- function(a, b, c) {{"
        if lang == "javascript": return f"function {fn}(a, b, c) {{"
        if lang == "typescript": return f"function {fn}(a: number, b: number, c: number): {r} {{"
        if lang == "perl": return f"sub {fn} {{ my ($a, $b, $c) = @_;"
        if lang == "java": return f"static {r} {fn}(int a, int b, int c) {{"
        if lang == "cpp": return f"{r} {fn}(int a, int b, int c) {{"
        if lang == "csharp": return f"static {r} {fn}(int a, int b, int c) {{"
        if lang == "c": return f"{r} {fn}(int a, int b, int c) {{"
        if lang == "rust": return f"fn {fn}(a: i32, b: i32, c: i32) -> {r} {{"
        if lang == "swift": return f"func {fn}(_ a: Int, _ b: Int, _ c: Int) -> {r} {{"
    raise ValueError((lang, shape))


# ═════════════════════════════════════════════════════════════════════════
# read_code() -- stdin-parsing statements for each (lang, shape)
# ═════════════════════════════════════════════════════════════════════════

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
                     "n <- as.integer(data[1])\nnums <- if (n > 0) data[2:(1+n)] else numeric(0)")
        if shape == "arr1_int":
            return read_code("r", "arr1") + "\nextra <- data[2+n]"
        if shape == "str1":
            return base + "s <- trimws(paste(lines, collapse=\" \"))"
        if shape == "str1_int":
            return (base + "line <- lines[1]\nidx <- max(gregexpr(' ', line)[[1]])\n"
                     "s <- substr(line, 1, idx - 1)\nextra <- as.numeric(trimws(substr(line, idx + 1, nchar(line))))")
        if shape == "str2":
            return (base + "s <- if (length(lines) >= 1) lines[1] else \"\"\nt <- if (length(lines) >= 2) lines[2] else \"\"")
        if shape == "arr2_samelen":
            return (base + "data <- as.numeric(strsplit(paste(lines, collapse=\" \"), \"\\\\s+\")[[1]])\n"
                     "n <- as.integer(data[1])\na <- data[2:(1+n)]\nb <- data[(2+n):(1+2*n)]")
        if shape == "arr2_int":
            return read_code("r", "arr2_samelen") + "\nextra <- data[2+2*n]"
        if shape == "triangle":
            return (base + "data <- as.numeric(strsplit(paste(lines, collapse=\" \"), \"\\\\s+\")[[1]])\n"
                     "n <- as.integer(data[1])\np <- 2\ntriangle <- list()\n"
                     "if (n > 0) { for (i in 1:n) { row <- as.integer(data[p:(p+i-1)]); p <- p + i; triangle[[i]] <- row } }")
    if lang == "javascript":
        if shape == "arr1":
            return ("const __data = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
                     "const n = __data[0];\nconst nums = __data.slice(1, 1 + n);")
        if shape == "arr1_int":
            return read_code("javascript", "arr1") + "\nconst extra = __data[1 + n];"
        if shape == "str1":
            return "const s = require('fs').readFileSync(0, 'utf8').trim();"
        if shape == "str1_int":
            return ("const __raw = require('fs').readFileSync(0, 'utf8').replace(/[\\r\\n]+$/, '');\n"
                     "const __idx = __raw.lastIndexOf(' ');\nconst s = __raw.slice(0, __idx);\nconst extra = Number(__raw.slice(__idx + 1).trim());")
        if shape == "str2":
            return ("const __lines = require('fs').readFileSync(0, 'utf8').split('\\n');\n"
                     "const s = (__lines[0] || '').replace(/\\r$/, '');\nconst t = (__lines[1] || '').replace(/\\r$/, '');")
        if shape == "arr2_samelen":
            return ("const __data = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
                     "const n = __data[0];\nconst a = __data.slice(1, 1 + n);\nconst b = __data.slice(1 + n, 1 + 2 * n);")
        if shape == "arr2_int":
            return read_code("javascript", "arr2_samelen") + "\nconst extra = __data[1 + 2 * n];"
        if shape == "triangle":
            return ("const __data = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
                     "const n = __data[0];\nlet __p = 1;\nconst triangle = [];\n"
                     "for (let i = 0; i < n; i++) { triangle.push(__data.slice(__p, __p + i + 1)); __p += i + 1; }")
    if lang == "typescript":
        # Same convention as javascript -- run_typescript executes via tsx (loose `any` on __data is fine).
        return read_code("javascript", shape)
    if lang == "perl":
        if shape == "arr1":
            return "my @__data = split ' ', do { local $/; <STDIN> };\nmy $n = $__data[0];\nmy @nums = @__data[1..$n];"
        if shape == "arr1_int":
            return read_code("perl", "arr1") + "\nmy $extra = $__data[1 + $n];"
        if shape == "str1":
            return "my $s = do { local $/; <STDIN> };\n$s =~ s/^\\s+|\\s+$//g;"
        if shape == "str1_int":
            return ("my $__raw = do { local $/; <STDIN> };\n$__raw =~ s/[\\r\\n]+$//;\n"
                     "my $__idx = rindex($__raw, ' ');\nmy $s = substr($__raw, 0, $__idx);\nmy $extra = substr($__raw, $__idx + 1) + 0;")
        if shape == "str2":
            return ("my @__lines = split /\\n/, do { local $/; <STDIN> };\n"
                     "my $s = $__lines[0] // ''; $s =~ s/\\r$//;\nmy $t = $__lines[1] // ''; $t =~ s/\\r$//;")
        if shape == "arr2_samelen":
            return ("my @__data = split ' ', do { local $/; <STDIN> };\nmy $n = $__data[0];\n"
                     "my @a = @__data[1..$n];\nmy @b = @__data[($n+1)..(2*$n)];")
        if shape == "arr2_int":
            return read_code("perl", "arr2_samelen") + "\nmy $extra = $__data[1 + 2 * $n];"
        if shape == "triangle":
            return ("my @__data = split ' ', do { local $/; <STDIN> };\nmy $n = $__data[0];\nmy $__p = 1;\nmy @triangle;\n"
                     "for (my $i = 0; $i < $n; $i++) { push @triangle, [@__data[$__p..($__p+$i)]]; $__p += $i + 1; }")
    if lang == "java":
        if shape == "arr1":
            return ("java.util.Scanner __sc = new java.util.Scanner(System.in);\n"
                     "int n = __sc.nextInt();\nint[] nums = new int[n];\nfor (int __i = 0; __i < n; __i++) nums[__i] = __sc.nextInt();")
        if shape == "arr1_int":
            return read_code("java", "arr1") + "\nint extra = __sc.nextInt();"
        if shape == "str1":
            return "java.util.Scanner __sc = new java.util.Scanner(System.in);\nString s = __sc.nextLine().trim();"
        if shape == "str1_int":
            return ("java.util.Scanner __sc = new java.util.Scanner(System.in);\nString __line = __sc.nextLine();\n"
                     "int __idx = __line.lastIndexOf(' ');\nString s = __line.substring(0, __idx);\nint extra = Integer.parseInt(__line.substring(__idx + 1).trim());")
        if shape == "str2":
            return ("java.util.Scanner __sc = new java.util.Scanner(System.in);\nString s = __sc.nextLine();\n"
                     "String t = __sc.hasNextLine() ? __sc.nextLine() : \"\";")
        if shape == "arr2_samelen":
            return ("java.util.Scanner __sc = new java.util.Scanner(System.in);\n"
                     "int n = __sc.nextInt();\nint[] a = new int[n];\nfor (int __i = 0; __i < n; __i++) a[__i] = __sc.nextInt();\n"
                     "int[] b = new int[n];\nfor (int __i = 0; __i < n; __i++) b[__i] = __sc.nextInt();")
        if shape == "arr2_int":
            return read_code("java", "arr2_samelen") + "\nint extra = __sc.nextInt();"
        if shape == "triangle":
            return ("java.util.Scanner __sc = new java.util.Scanner(System.in);\nint n = __sc.nextInt();\n"
                     "int[][] triangle = new int[n][];\nfor (int __i = 0; __i < n; __i++) { triangle[__i] = new int[__i + 1]; for (int __j = 0; __j <= __i; __j++) triangle[__i][__j] = __sc.nextInt(); }")
    if lang == "cpp":
        if shape == "arr1":
            return "int n; std::cin >> n;\nstd::vector<int> nums(n);\nfor (int __i = 0; __i < n; __i++) std::cin >> nums[__i];"
        if shape == "arr1_int":
            return read_code("cpp", "arr1") + "\nint extra; std::cin >> extra;"
        if shape == "str1":
            return "std::ostringstream __oss; __oss << std::cin.rdbuf();\nstd::string s = __oss.str();\nwhile (!s.empty() && (s.back() == '\\n' || s.back() == '\\r' || s.back() == ' ')) s.pop_back();\nsize_t __st = 0; while (__st < s.size() && isspace((unsigned char) s[__st])) __st++;\ns = s.substr(__st);"
        if shape == "str1_int":
            return ("std::string s; int extra;\nstd::string __rest;\nstd::getline(std::cin, __rest);\n"
                     "size_t __idx = __rest.find_last_of(' ');\ns = __rest.substr(0, __idx);\nextra = std::stoi(__rest.substr(__idx + 1));")
        if shape == "str2":
            return "std::string s, t;\nstd::getline(std::cin, s);\nif (!s.empty() && s.back() == '\\r') s.pop_back();\nstd::getline(std::cin, t);\nif (!t.empty() && t.back() == '\\r') t.pop_back();"
        if shape == "arr2_samelen":
            return ("int n; std::cin >> n;\nstd::vector<int> a(n), b(n);\nfor (int __i = 0; __i < n; __i++) std::cin >> a[__i];\nfor (int __i = 0; __i < n; __i++) std::cin >> b[__i];")
        if shape == "arr2_int":
            return read_code("cpp", "arr2_samelen") + "\nint extra; std::cin >> extra;"
        if shape == "triangle":
            return ("int n; std::cin >> n;\nstd::vector<std::vector<int>> triangle(n);\n"
                     "for (int __i = 0; __i < n; __i++) { triangle[__i].resize(__i + 1); for (int __j = 0; __j <= __i; __j++) std::cin >> triangle[__i][__j]; }")
    if lang == "csharp":
        if shape in ("arr1", "arr1_int", "arr2_samelen", "arr2_int", "triangle"):
            base_tok = ("var __tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
                        "System.StringSplitOptions.RemoveEmptyEntries);\nint __idx = 0;\n")
        if shape == "arr1":
            return base_tok + "int n = int.Parse(__tokens[__idx++]);\nint[] nums = new int[n];\nfor (int __i = 0; __i < n; __i++) nums[__i] = int.Parse(__tokens[__idx++]);"
        if shape == "arr1_int":
            return read_code("csharp", "arr1") + "\nint extra = int.Parse(__tokens[__idx++]);"
        if shape == "str1":
            return "string s = System.Console.In.ReadToEnd().Trim();"
        if shape == "str1_int":
            return ("string __raw = System.Console.In.ReadToEnd().TrimEnd('\\r', '\\n');\n"
                     "int __sp = __raw.LastIndexOf(' ');\nstring s = __raw.Substring(0, __sp);\nint extra = int.Parse(__raw.Substring(__sp + 1).Trim());")
        if shape == "str2":
            return ("var __lines = System.Console.In.ReadToEnd().Split('\\n');\n"
                     "string s = __lines[0].TrimEnd('\\r');\nstring t = __lines.Length > 1 ? __lines[1].TrimEnd('\\r') : \"\";")
        if shape == "arr2_samelen":
            return base_tok + "int n = int.Parse(__tokens[__idx++]);\nint[] a = new int[n];\nfor (int __i = 0; __i < n; __i++) a[__i] = int.Parse(__tokens[__idx++]);\nint[] b = new int[n];\nfor (int __i = 0; __i < n; __i++) b[__i] = int.Parse(__tokens[__idx++]);"
        if shape == "arr2_int":
            return read_code("csharp", "arr2_samelen") + "\nint extra = int.Parse(__tokens[__idx++]);"
        if shape == "triangle":
            return base_tok + "int n = int.Parse(__tokens[__idx++]);\nint[][] triangle = new int[n][];\nfor (int __i = 0; __i < n; __i++) { triangle[__i] = new int[__i + 1]; for (int __j = 0; __j <= __i; __j++) triangle[__i][__j] = int.Parse(__tokens[__idx++]); }"
    if lang == "c":
        if shape == "arr1":
            return "int n; scanf(\"%d\", &n);\nint *nums = (int *)malloc(sizeof(int) * (n > 0 ? n : 1));\nfor (int __i = 0; __i < n; __i++) scanf(\"%d\", &nums[__i]);"
        if shape == "arr1_int":
            return read_code("c", "arr1") + "\nint extra; scanf(\"%d\", &extra);"
        if shape == "str1":
            return ("char __buf[1 << 20];\nsize_t __len = fread(__buf, 1, sizeof(__buf) - 1, stdin);\n__buf[__len] = '\\0';\n"
                     "char *s = __buf;\nwhile (*s && isspace((unsigned char) *s)) s++;\nchar *__end = s + strlen(s) - 1;\nwhile (__end > s && isspace((unsigned char) *__end)) { *__end = '\\0'; __end--; }")
        if shape == "str1_int":
            return ("char __buf[1 << 20];\nsize_t __len = fread(__buf, 1, sizeof(__buf) - 1, stdin);\n__buf[__len] = '\\0';\n"
                     "while (__len > 0 && (__buf[__len-1] == '\\n' || __buf[__len-1] == '\\r')) { __buf[--__len] = '\\0'; }\n"
                     "char *__sp = strrchr(__buf, ' ');\n*__sp = '\\0';\nchar *s = __buf;\nint extra = atoi(__sp + 1);")
        if shape == "str2":
            return ("char __buf[1 << 20];\nsize_t __len = fread(__buf, 1, sizeof(__buf) - 1, stdin);\n__buf[__len] = '\\0';\n"
                     "char *s = __buf;\nchar *__nl = strchr(__buf, '\\n');\nchar *t = \"\";\nif (__nl) { *__nl = '\\0'; t = __nl + 1; size_t __tl = strlen(t); while (__tl > 0 && (t[__tl-1]=='\\n'||t[__tl-1]=='\\r')) t[--__tl] = '\\0'; }\n"
                     "size_t __sl = strlen(s); while (__sl > 0 && s[__sl-1] == '\\r') s[--__sl] = '\\0';")
        if shape == "arr2_samelen":
            return ("int n; scanf(\"%d\", &n);\nint *a = (int *)malloc(sizeof(int) * (n > 0 ? n : 1));\nint *b = (int *)malloc(sizeof(int) * (n > 0 ? n : 1));\n"
                     "for (int __i = 0; __i < n; __i++) scanf(\"%d\", &a[__i]);\nfor (int __i = 0; __i < n; __i++) scanf(\"%d\", &b[__i]);")
        if shape == "arr2_int":
            return read_code("c", "arr2_samelen") + "\nint extra; scanf(\"%d\", &extra);"
        if shape == "triangle":
            return ("int n; scanf(\"%d\", &n);\nint **triangle = (int **)malloc(sizeof(int *) * (n > 0 ? n : 1));\n"
                     "for (int __i = 0; __i < n; __i++) { triangle[__i] = (int *)malloc(sizeof(int) * (__i + 1)); for (int __j = 0; __j <= __i; __j++) scanf(\"%d\", &triangle[__i][__j]); }")
    if lang == "rust":
        if shape == "arr1":
            return ("let mut __input = String::new();\nstd::io::Read::read_to_string(&mut std::io::stdin(), &mut __input).unwrap();\n"
                     "let mut __it = __input.split_whitespace();\nlet n: usize = __it.next().unwrap().parse().unwrap();\n"
                     "let nums: Vec<i32> = (0..n).map(|_| __it.next().unwrap().parse().unwrap()).collect();")
        if shape == "arr1_int":
            return read_code("rust", "arr1") + "\nlet extra: i32 = __it.next().unwrap().parse().unwrap();"
        if shape == "str1":
            return "let mut s = String::new();\nstd::io::Read::read_to_string(&mut std::io::stdin(), &mut s).unwrap();\nlet s = s.trim().to_string();\nlet s: &str = &s;"
        if shape == "str1_int":
            return ("let mut __raw = String::new();\nstd::io::Read::read_to_string(&mut std::io::stdin(), &mut __raw).unwrap();\n"
                     "let __raw = __raw.trim_end_matches(['\\n', '\\r']);\nlet __idx = __raw.rfind(' ').unwrap();\n"
                     "let s = &__raw[..__idx];\nlet extra: i32 = __raw[__idx+1..].trim().parse().unwrap();")
        if shape == "str2":
            return ("let mut __raw = String::new();\nstd::io::Read::read_to_string(&mut std::io::stdin(), &mut __raw).unwrap();\n"
                     "let mut __lines = __raw.split('\\n');\nlet s = __lines.next().unwrap_or(\"\").trim_end_matches('\\r').to_string();\n"
                     "let t = __lines.next().unwrap_or(\"\").trim_end_matches('\\r').to_string();\nlet s: &str = &s;\nlet t: &str = &t;")
        if shape == "arr2_samelen":
            return ("let mut __input = String::new();\nstd::io::Read::read_to_string(&mut std::io::stdin(), &mut __input).unwrap();\n"
                     "let mut __it = __input.split_whitespace();\nlet n: usize = __it.next().unwrap().parse().unwrap();\n"
                     "let a: Vec<i32> = (0..n).map(|_| __it.next().unwrap().parse().unwrap()).collect();\n"
                     "let b: Vec<i32> = (0..n).map(|_| __it.next().unwrap().parse().unwrap()).collect();")
        if shape == "arr2_int":
            return read_code("rust", "arr2_samelen") + "\nlet extra: i32 = __it.next().unwrap().parse().unwrap();"
        if shape == "triangle":
            return ("let mut __input = String::new();\nstd::io::Read::read_to_string(&mut std::io::stdin(), &mut __input).unwrap();\n"
                     "let mut __it = __input.split_whitespace();\nlet n: usize = __it.next().unwrap().parse().unwrap();\n"
                     "let triangle: Vec<Vec<i32>> = (0..n).map(|i| (0..=i).map(|_| __it.next().unwrap().parse().unwrap()).collect()).collect();")
    if lang == "swift":
        if shape == "arr1":
            return ("let __all = String(data: FileHandle.standardInput.readDataToEndOfFile(), encoding: .utf8) ?? \"\"\n"
                     "let __fields = __all.split(whereSeparator: { $0 == \" \" || $0 == \"\\n\" || $0 == \"\\r\" || $0 == \"\\t\" }).map { String($0) }\n"
                     "let n = Int(__fields[0])!\nlet nums: [Int] = (0..<n).map { Int(__fields[1 + $0])! }")
        if shape == "arr1_int":
            return read_code("swift", "arr1") + "\nlet extra = Int(__fields[1 + n])!"
        if shape == "str1":
            return "let __allS = String(data: FileHandle.standardInput.readDataToEndOfFile(), encoding: .utf8) ?? \"\"\nlet s = __allS.trimmingCharacters(in: .whitespacesAndNewlines)"
        if shape == "str1_int":
            return ("let __rawS = String(data: FileHandle.standardInput.readDataToEndOfFile(), encoding: .utf8) ?? \"\"\n"
                     "let __trimmed = __rawS.trimmingCharacters(in: CharacterSet(charactersIn: \"\\r\\n\"))\n"
                     "let __sp = __trimmed.lastIndex(of: \" \")!\nlet s = String(__trimmed[__trimmed.startIndex..<__sp])\n"
                     "let extra = Int(__trimmed[__trimmed.index(after: __sp)...].trimmingCharacters(in: .whitespaces))!")
        if shape == "str2":
            return ("let __rawS2 = String(data: FileHandle.standardInput.readDataToEndOfFile(), encoding: .utf8) ?? \"\"\n"
                     "let __linesS = __rawS2.components(separatedBy: \"\\n\")\n"
                     "let s = __linesS[0].trimmingCharacters(in: CharacterSet(charactersIn: \"\\r\"))\n"
                     "let t = __linesS.count > 1 ? __linesS[1].trimmingCharacters(in: CharacterSet(charactersIn: \"\\r\")) : \"\"")
        if shape == "arr2_samelen":
            return ("let __all2 = String(data: FileHandle.standardInput.readDataToEndOfFile(), encoding: .utf8) ?? \"\"\n"
                     "let __fields2 = __all2.split(whereSeparator: { $0 == \" \" || $0 == \"\\n\" || $0 == \"\\r\" || $0 == \"\\t\" }).map { String($0) }\n"
                     "let n = Int(__fields2[0])!\nlet a: [Int] = (0..<n).map { Int(__fields2[1 + $0])! }\nlet b: [Int] = (0..<n).map { Int(__fields2[1 + n + $0])! }")
        if shape == "arr2_int":
            return read_code("swift", "arr2_samelen") + "\nlet extra = Int(__fields2[1 + 2 * n])!"
        if shape == "triangle":
            return ("let __all3 = String(data: FileHandle.standardInput.readDataToEndOfFile(), encoding: .utf8) ?? \"\"\n"
                     "let __fields3 = __all3.split(whereSeparator: { $0 == \" \" || $0 == \"\\n\" || $0 == \"\\r\" || $0 == \"\\t\" }).map { String($0) }\n"
                     "let n = Int(__fields3[0])!\nvar __p = 1\nvar triangle: [[Int]] = []\n"
                     "for i in 0..<n { var row: [Int] = []; for _ in 0...i { row.append(Int(__fields3[__p])!); __p += 1 }; triangle.append(row) }")
    if shape in ("int1", "int2", "int3"):
        names = {"int1": ["n"], "int2": ["a", "b"], "int3": ["a", "b", "c"]}[shape]
        if lang == "go":
            lines = ["data, _ := io.ReadAll(os.Stdin)", "fields := strings.Fields(string(data))"]
            for i, nm in enumerate(names): lines.append(f"{nm}, _ := strconv.Atoi(fields[{i}])")
            return "\n".join(lines)
        if lang == "ruby":
            lines = ["data = STDIN.read.split"]
            for i, nm in enumerate(names): lines.append(f"{nm} = data[{i}].to_i")
            return "\n".join(lines)
        if lang == "kotlin":
            lines = ["val data = System.`in`.bufferedReader().readText().trim().split(Regex(\"\\\\s+\"))"]
            for i, nm in enumerate(names): lines.append(f"val {nm} = data[{i}].toInt()")
            return "\n".join(lines)
        if lang == "php":
            lines = ["$data = preg_split('/\\s+/', trim(file_get_contents('php://stdin')));"]
            for i, nm in enumerate(names): lines.append(f"${nm} = intval($data[{i}]);")
            return "\n".join(lines)
        if lang == "scala":
            lines = ["val raw = scala.io.Source.stdin.mkString", "val data = raw.trim.split(\"\\\\s+\")"]
            for i, nm in enumerate(names): lines.append(f"val {nm} = data({i}).toInt")
            return "\n".join(lines)
        if lang == "r":
            lines = ["con <- file(\"stdin\"); lines <- readLines(con); close(con)",
                      "data <- as.numeric(strsplit(paste(lines, collapse=\" \"), \"\\\\s+\")[[1]])"]
            for i, nm in enumerate(names): lines.append(f"{nm} <- as.integer(data[{i + 1}])")
            return "\n".join(lines)
        if lang in ("javascript", "typescript"):
            lines = ["const __data = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);"]
            for i, nm in enumerate(names): lines.append(f"const {nm} = __data[{i}];")
            return "\n".join(lines)
        if lang == "perl":
            lines = ["my @__data = split ' ', do { local $/; <STDIN> };"]
            for i, nm in enumerate(names): lines.append(f"my ${nm} = $__data[{i}];")
            return "\n".join(lines)
        if lang == "java":
            lines = ["java.util.Scanner __sc = new java.util.Scanner(System.in);"]
            for nm in names: lines.append(f"int {nm} = __sc.nextInt();")
            return "\n".join(lines)
        if lang == "cpp":
            return "\n".join(f"int {nm}; std::cin >> {nm};" for nm in names)
        if lang == "csharp":
            lines = ["var __tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
                      "System.StringSplitOptions.RemoveEmptyEntries);", "int __idx = 0;"]
            for nm in names: lines.append(f"int {nm} = int.Parse(__tokens[__idx++]);")
            return "\n".join(lines)
        if lang == "c":
            return "\n".join(f"int {nm}; scanf(\"%d\", &{nm});" for nm in names)
        if lang == "rust":
            lines = ["let mut __input = String::new();",
                      "std::io::Read::read_to_string(&mut std::io::stdin(), &mut __input).unwrap();",
                      "let mut __it = __input.split_whitespace();"]
            for nm in names: lines.append(f"let {nm}: i32 = __it.next().unwrap().parse().unwrap();")
            return "\n".join(lines)
        if lang == "swift":
            lines = ["let __all = String(data: FileHandle.standardInput.readDataToEndOfFile(), encoding: .utf8) ?? \"\"",
                      "let __fields = __all.split(whereSeparator: { $0 == \" \" || $0 == \"\\n\" || $0 == \"\\r\" || $0 == \"\\t\" }).map { String($0) }"]
            for i, nm in enumerate(names): lines.append(f"let {nm} = Int(__fields[{i}])!")
            return "\n".join(lines)
    raise ValueError((lang, shape))


# ═════════════════════════════════════════════════════════════════════════
# call_args() -- argument list at the call site (mirrors sig()'s params)
# ═════════════════════════════════════════════════════════════════════════

def call_args(lang, shape):
    if lang == "r":
        m = {"arr1": "nums", "arr1_int": "nums, extra", "str1": "s", "str1_int": "s, extra",
             "str2": "s, t", "arr2_samelen": "a, b", "arr2_int": "a, b, extra", "triangle": "triangle",
             "int1": "n", "int2": "a, b", "int3": "a, b, c"}
        return m[shape]
    if lang == "php":
        m = {"arr1": "$nums", "arr1_int": "$nums, $extra", "str1": "$s", "str1_int": "$s, $extra",
             "str2": "$s, $t", "arr2_samelen": "$a, $b", "arr2_int": "$a, $b, $extra", "triangle": "$triangle",
             "int1": "$n", "int2": "$a, $b", "int3": "$a, $b, $c"}
        return m[shape]
    if lang == "c":
        m = {"arr1": "nums, n", "arr1_int": "nums, n, extra", "str1": "s", "str1_int": "s, extra",
             "str2": "s, t", "arr2_samelen": "a, b, n", "arr2_int": "a, b, n, extra", "triangle": "triangle, n",
             "int1": "n", "int2": "a, b", "int3": "a, b, c"}
        return m[shape]
    if lang == "rust":
        m = {"arr1": "&nums", "arr1_int": "&nums, extra", "str1": "s", "str1_int": "s, extra",
             "str2": "s, t", "arr2_samelen": "&a, &b", "arr2_int": "&a, &b, extra", "triangle": "&triangle",
             "int1": "n", "int2": "a, b", "int3": "a, b, c"}
        return m[shape]
    m = {"arr1": "nums", "arr1_int": "nums, extra", "str1": "s", "str1_int": "s, extra",
         "str2": "s, t", "arr2_samelen": "a, b", "arr2_int": "a, b, extra", "triangle": "triangle",
         "int1": "n", "int2": "a, b", "int3": "a, b, c"}
    return m[shape]


# ═════════════════════════════════════════════════════════════════════════
# print_stmt() -- prints `result` (applying the auto-generated "wrong"
# corruption: +1 for int, negation for bool)
# ═════════════════════════════════════════════════════════════════════════

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
    if lang in ("javascript", "typescript"):
        return f"console.log(result + {delta});" if kind == "int" else f"console.log({neg}result);"
    if lang == "perl":
        if kind == "int":
            return f"print(($result + {delta}), \"\\n\");"
        return f"print(({neg}$result) ? \"true\" : \"false\", \"\\n\");"
    if lang == "java":
        return f"System.out.println(result + {delta});" if kind == "int" else f"System.out.println({neg}result);"
    if lang == "cpp":
        if kind == "int":
            return f"std::cout << (result + {delta}) << std::endl;"
        return f"std::cout << (({neg}result) ? \"true\" : \"false\") << std::endl;"
    if lang == "csharp":
        if kind == "int":
            return f"System.Console.WriteLine(result + {delta});"
        return f"System.Console.WriteLine(({neg}result) ? \"true\" : \"false\");"
    if lang == "c":
        if kind == "int":
            return f"printf(\"%d\\n\", result + {delta});"
        cond = f"(!result)" if wrong else "(result)"
        return f"printf(\"%s\\n\", {cond} ? \"true\" : \"false\");"
    if lang == "rust":
        return f"println!(\"{{}}\", result + {delta});" if kind == "int" else f"println!(\"{{}}\", {neg}result);"
    if lang == "swift":
        return f"print(result + {delta})" if kind == "int" else f"print({neg}result)"
    raise ValueError((lang, kind))


# ═════════════════════════════════════════════════════════════════════════
# assemble() -- full standalone program for (lang, shape, problem)
# ═════════════════════════════════════════════════════════════════════════

def assemble(lang, shape, fn, kind, body, wrong):
    read = read_code(lang, shape)
    signature = sig(lang, shape, fn, kind)
    args = call_args(lang, shape)
    p = print_stmt(lang, kind, wrong)

    if lang == "go":
        func = f"{signature}\n{body}\nreturn result\n}}"
        call = f"result := {fn}({args})"
        needs_strconv = shape not in ("str1", "str2")
        needs_math = "math." in body
        needs_sort = "sort." in body
        imports = ("\"fmt\"\n\t\"io\"\n\t\"os\"\n\t" + ("\"strconv\"\n\t" if needs_strconv else "")
                   + ("\"math\"\n\t" if needs_math else "") + ("\"sort\"\n\t" if needs_sort else "") + "\"strings\"")
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
    if lang == "javascript":
        func = f"{signature}\n{body}\nreturn result;\n}}"
        call = f"const result = {fn}({args});"
        return f"{read}\n\n{func}\n\n{call}\n{p}\n"
    if lang == "typescript":
        func = f"{signature}\n{body}\nreturn result;\n}}"
        call = f"const result: {rt('typescript', kind)} = {fn}({args});"
        return f"{read}\n\n{func}\n\n{call}\n{p}\n"
    if lang == "perl":
        func = f"{signature}\n{body}\nreturn $result;\n}}"
        call = f"my $result = {fn}({args});"
        # Perl's shape params (nums/a/b/triangle) are array refs; body code
        # written against @{$nums} etc, consistent with the rest of this
        # codebase's PerlFunctionAdapter convention (see adapters.py).
        arg_prep = ""
        if shape in ("arr1", "arr1_int"):
            arg_prep = "my $nums_ref = \\@nums;\n"
            call = f"my $result = {fn}($nums_ref" + (", $extra);" if shape == "arr1_int" else ");")
        elif shape in ("arr2_samelen", "arr2_int"):
            arg_prep = "my $a_ref = \\@a;\nmy $b_ref = \\@b;\n"
            call = f"my $result = {fn}($a_ref, $b_ref" + (", $extra);" if shape == "arr2_int" else ");")
        elif shape == "triangle":
            arg_prep = "my $triangle_ref = \\@triangle;\n"
            call = f"my $result = {fn}($triangle_ref);"
        return f"{read}\n{arg_prep}\n{func}\n\n{call}\n{p}\n"
    if lang == "java":
        func = f"{signature}\n{body}\nreturn result;\n}}"
        call = f"{rt('java', kind)} result = {fn}({args});"
        return (f"import java.util.*;\n\npublic class Main {{\n"
                 f"    public static void main(String[] args) {{\n{read}\n{call}\n{p}\n    }}\n\n"
                 f"    {func}\n}}\n")
    if lang == "cpp":
        func = f"{signature}\n{body}\nreturn result;\n}}"
        call = f"{rt('cpp', kind)} result = {fn}({args});"
        headers = ("#include <iostream>\n#include <sstream>\n#include <vector>\n#include <string>\n"
                    "#include <algorithm>\n#include <unordered_map>\n#include <unordered_set>\n"
                    "#include <map>\n#include <set>\n#include <cmath>\n#include <cctype>\n#include <climits>\nusing namespace std;\n\n")
        return f"{headers}{func}\n\nint main() {{\n{read}\n{call}\n{p}\n return 0;\n}}\n"
    if lang == "csharp":
        func = f"{signature}\n{body}\nreturn result;\n}}"
        call = f"{rt('csharp', kind)} result = {fn}({args});"
        return (f"using System;\nusing System.Collections.Generic;\nusing System.Linq;\n\n"
                 f"class Program {{\n    static void Main() {{\n{read}\n{call}\n{p}\n    }}\n\n    {func}\n}}\n")
    if lang == "c":
        func = f"{signature}\n{body}\nreturn result;\n}}"
        call = f"{rt('c', kind)} result = {fn}({args});"
        headers = "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <ctype.h>\n#include <math.h>\n\n"
        return f"{headers}{func}\n\nint main() {{\n{read}\n{call}\n{p}\n return 0;\n}}\n"
    if lang == "rust":
        func = f"#[allow(unused)]\n{signature}\n{body}\nresult\n}}"
        call = f"let result: {rt('rust', kind)} = {fn}({args});"
        return f"{func}\n\nfn main() {{\n{read}\n{call}\n{p}\n}}\n"
    if lang == "swift":
        func = f"{signature}\n{body}\nreturn result\n}}"
        call = f"let result = {fn}({args})"
        return f"import Foundation\n\n{func}\n\n{read}\n{call}\n{p}\n"
    raise ValueError(lang)


# ═════════════════════════════════════════════════════════════════════════
# Problem registry + harness plumbing
# ═════════════════════════════════════════════════════════════════════════

PROBLEMS: dict[str, dict] = {}


def add(pid, shape, fn, kind, bodies, skip=None):
    """skip: languages to deliberately exclude for this problem (e.g. a
    32-bit-int overflow risk in java/cpp/csharp/c/rust's hard-mapped
    `int`/`i32` kind) -- documented exclusion, not a silent gap. Bodies
    are not required for skipped languages."""
    skip = set(skip or [])
    missing = [l for l in LANGS if l not in bodies and l not in skip]
    if missing:
        raise ValueError(f"{pid}: missing bodies for {missing}")
    PROBLEMS[pid] = {"shape": shape, "fn": fn, "kind": kind, "bodies": bodies, "skip": skip}


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


async def main(only_pids=None, only_langs=None):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)

    results = []
    pids = [p for p in PROBLEMS if not only_pids or p in only_pids]
    langs = [l for l in LANGS if not only_langs or l in only_langs]
    for pid in pids:
        cases, tsv = load_cases(con, pid)
        for lang in langs:
            if lang in PROBLEMS[pid].get("skip", ()):
                print(f"[EXCLUDED] {pid}/{lang} deliberately skipped (see add() call)")
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
                    adapter_version="atlascode-shapes-all15-v1", test_suite_version=tsv,
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
