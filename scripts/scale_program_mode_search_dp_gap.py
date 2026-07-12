"""Program Mode gap closure: staircase, search-insert-position, and
rotated-binary-search were already Level-6 Function Mode across all 8
core working languages (javascript, typescript, java, cpp, csharp, perl,
c, rust) but had zero Program Mode coverage in ANY of them. Closes that
gap by generating full-program (stdin -> stdout) wrappers per language,
reusing the existing Python starter_code's I/O contract verbatim.

Pattern: for each (problem, language) pair, run the correct solution on
the full real 40-case corpus (must pass all), then a genuinely-wrong
variant (must fail at least one case) -- only record Level 6 when both
hold. Mirrors scripts/scale_program_mode_ladder_gap.py.
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

LANGS = ["javascript", "typescript", "java", "cpp", "csharp", "perl", "c", "rust"]


@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


# ── staircase (climb_stairs(n) -> ways) ──────────────────────────────────────

def _js_staircase(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "const n = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        f"function {fn}(n) {{\n"
        "    if (n <= 1) return 1;\n"
        "    let a = 1, b = 1;\n"
        "    for (let i = 2; i <= n; i++) { const c = a + b; a = b; b = c; }\n"
        f"    return b{a};\n"
        "}\n"
        f"console.log({fn}(n));\n"
    )


def _ts_staircase(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "const n: number = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        f"function {fn}(n: number): number {{\n"
        "    if (n <= 1) return 1;\n"
        "    let a = 1, b = 1;\n"
        "    for (let i = 2; i <= n; i++) { const c = a + b; a = b; b = c; }\n"
        f"    return b{a};\n"
        "}\n"
        f"console.log({fn}(n));\n"
    )


def _java_staircase(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt();\n"
        f"        System.out.println({fn}(n));\n"
        "    }\n"
        f"    static int {fn}(int n) {{\n"
        "        if (n <= 1) return 1;\n"
        "        int a = 1, b = 1;\n"
        "        for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }\n"
        f"        return b{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_staircase(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\nusing namespace std;\n\n"
        f"int {fn}(int n) {{\n"
        "    if (n <= 1) return 1;\n"
        "    int a = 1, b = 1;\n"
        "    for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }\n"
        f"    return b{a};\n"
        "}\n\n"
        "int main() {\n"
        "    int n; cin >> n;\n"
        f"    cout << {fn}(n) << endl;\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_staircase(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program {\n"
        "    static void Main() {\n"
        "        int n = int.Parse(System.Console.In.ReadToEnd().Trim());\n"
        f"        System.Console.WriteLine({fn}(n));\n"
        "    }\n"
        f"    static int {fn}(int n) {{\n"
        "        if (n <= 1) return 1;\n"
        "        int a = 1, b = 1;\n"
        "        for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }\n"
        f"        return b{a};\n"
        "    }\n"
        "}\n"
    )


def _perl_staircase(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "my $n = do { local $/; <STDIN> };\n"
        "$n =~ s/^\\s+|\\s+$//g;\n"
        f"sub {fn} {{\n"
        "    my ($n) = @_;\n"
        "    return 1 if $n <= 1;\n"
        "    my ($a, $b) = (1, 1);\n"
        "    for (my $i = 2; $i <= $n; $i++) { my $c = $a + $b; $a = $b; $b = $c; }\n"
        f"    return $b{a};\n"
        "}\n"
        f"print {fn}($n), \"\\n\";\n"
    )


def _c_staircase(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n\n"
        f"int {fn}(int n) {{\n"
        "    if (n <= 1) return 1;\n"
        "    int a = 1, b = 1;\n"
        "    for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }\n"
        f"    return b{a};\n"
        "}\n\n"
        "int main() {\n"
        "    int n; scanf(\"%d\", &n);\n"
        f"    printf(\"%d\\n\", {fn}(n));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_staircase(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n\n"
        f"fn {fn}(n: i64) -> i64 {{\n"
        "    if n <= 1 { return 1; }\n"
        "    let (mut a, mut b) = (1i64, 1i64);\n"
        "    for _ in 2..=n { let c = a + b; a = b; b = c; }\n"
        f"    b{a}\n"
        "}\n\n"
        "fn main() {\n"
        "    let mut input = String::new();\n"
        "    std::io::stdin().read_to_string(&mut input).unwrap();\n"
        "    let n: i64 = input.trim().parse().unwrap();\n"
        f"    println!(\"{{}}\", {fn}(n));\n"
        "}\n"
    )


# ── search-insert-position (search_insert(nums, target) -> lower-bound idx) ──

def _js_search_insert(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const target = data[1+n];\n"
        f"function {fn}(nums, target) {{\n"
        "    let lo = 0, hi = nums.length;\n"
        "    while (lo < hi) { const mid = (lo + hi) >> 1; if (nums[mid] < target) lo = mid + 1; else hi = mid; }\n"
        f"    return lo{a};\n"
        "}\n"
        f"console.log({fn}(nums, target));\n"
    )


def _ts_search_insert(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const target = data[1+n];\n"
        f"function {fn}(nums: number[], target: number): number {{\n"
        "    let lo = 0, hi = nums.length;\n"
        "    while (lo < hi) { const mid = (lo + hi) >> 1; if (nums[mid] < target) lo = mid + 1; else hi = mid; }\n"
        f"    return lo{a};\n"
        "}\n"
        f"console.log({fn}(nums, target));\n"
    )


def _java_search_insert(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt();\n"
        "        int[] nums = new int[n];\n"
        "        for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "        int target = sc.nextInt();\n"
        f"        System.out.println({fn}(nums, target));\n"
        "    }\n"
        f"    static int {fn}(int[] nums, int target) {{\n"
        "        int lo = 0, hi = nums.length;\n"
        "        while (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] < target) lo = mid + 1; else hi = mid; }\n"
        f"        return lo{a};\n"
        "    }\n"
        "}\n"
    )


def _cpp_search_insert(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n\n"
        f"int {fn}(vector<int>& nums, int target) {{\n"
        "    int lo = 0, hi = (int)nums.size();\n"
        "    while (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] < target) lo = mid + 1; else hi = mid; }\n"
        f"    return lo{a};\n"
        "}\n\n"
        "int main() {\n"
        "    int n; cin >> n;\n"
        "    vector<int> nums(n);\n"
        "    for (int i=0;i<n;i++) cin >> nums[i];\n"
        "    int target; cin >> target;\n"
        f"    cout << {fn}(nums, target) << endl;\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_search_insert(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program {\n"
        "    static void Main() {\n"
        "        var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
        "System.StringSplitOptions.RemoveEmptyEntries);\n"
        "        int idx = 0;\n"
        "        int n = int.Parse(tokens[idx++]);\n"
        "        int[] nums = new int[n];\n"
        "        for (int i=0;i<n;i++) nums[i]=int.Parse(tokens[idx++]);\n"
        "        int target = int.Parse(tokens[idx++]);\n"
        f"        System.Console.WriteLine({fn}(nums, target));\n"
        "    }\n"
        f"    static int {fn}(int[] nums, int target) {{\n"
        "        int lo = 0, hi = nums.Length;\n"
        "        while (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] < target) lo = mid + 1; else hi = mid; }\n"
        f"        return lo{a};\n"
        "    }\n"
        "}\n"
    )


def _perl_search_insert(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data;\n"
        "my @nums = @data[0..$n-1];\n"
        "my $target = $data[$n];\n"
        f"sub {fn} {{\n"
        "    my ($nums, $target) = @_;\n"
        "    my $lo = 0; my $hi = scalar(@$nums);\n"
        "    while ($lo < $hi) {\n"
        "        my $mid = int(($lo + $hi) / 2);\n"
        "        if ($nums->[$mid] < $target) { $lo = $mid + 1; } else { $hi = $mid; }\n"
        "    }\n"
        f"    return $lo{a};\n"
        "}\n"
        f"print {fn}(\\@nums, $target), \"\\n\";\n"
    )


def _c_search_insert(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        f"int {fn}(int* nums, int n, int target) {{\n"
        "    int lo = 0, hi = n;\n"
        "    while (lo < hi) { int mid = (lo + hi) / 2; if (nums[mid] < target) lo = mid + 1; else hi = mid; }\n"
        f"    return lo{a};\n"
        "}\n\n"
        "int main() {\n"
        "    int n; scanf(\"%d\", &n);\n"
        "    int* nums = (int*)malloc(sizeof(int) * (n > 0 ? n : 1));\n"
        "    for (int i=0;i<n;i++) scanf(\"%d\", &nums[i]);\n"
        "    int target; scanf(\"%d\", &target);\n"
        f"    printf(\"%d\\n\", {fn}(nums, n, target));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_search_insert(fn, wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n\n"
        f"fn {fn}(nums: &Vec<i32>, target: i32) -> i32 {{\n"
        "    let mut lo = 0usize; let mut hi = nums.len();\n"
        "    while lo < hi { let mid = (lo + hi) / 2; if nums[mid] < target { lo = mid + 1; } else { hi = mid; } }\n"
        f"    lo as i32{a}\n"
        "}\n\n"
        "fn main() {\n"
        "    let mut input = String::new();\n"
        "    std::io::stdin().read_to_string(&mut input).unwrap();\n"
        "    let mut it = input.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize;\n"
        "    let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let target = it.next().unwrap();\n"
        f"    println!(\"{{}}\", {fn}(&nums, target));\n"
        "}\n"
    )


# ── rotated-binary-search (search(nums, target) -> idx or -1) ───────────────

def _js_rot_search(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const target = data[1+n];\n"
        f"function {fn}(nums, target) {{\n"
        "    let lo = 0, hi = nums.length - 1;\n"
        "    while (lo <= hi) {\n"
        "        const mid = (lo + hi) >> 1;\n"
        f"        if (nums[mid] === target) return {ret};\n"
        "        if (nums[lo] <= nums[mid]) {\n"
        "            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;\n"
        "        } else {\n"
        "            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;\n"
        "        }\n"
        "    }\n"
        "    return -1;\n"
        "}\n"
        f"console.log({fn}(nums, target));\n"
    )


def _ts_rot_search(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n); const target = data[1+n];\n"
        f"function {fn}(nums: number[], target: number): number {{\n"
        "    let lo = 0, hi = nums.length - 1;\n"
        "    while (lo <= hi) {\n"
        "        const mid = (lo + hi) >> 1;\n"
        f"        if (nums[mid] === target) return {ret};\n"
        "        if (nums[lo] <= nums[mid]) {\n"
        "            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;\n"
        "        } else {\n"
        "            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;\n"
        "        }\n"
        "    }\n"
        "    return -1;\n"
        "}\n"
        f"console.log({fn}(nums, target));\n"
    )


def _java_rot_search(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt();\n"
        "        int[] nums = new int[n];\n"
        "        for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "        int target = sc.nextInt();\n"
        f"        System.out.println({fn}(nums, target));\n"
        "    }\n"
        f"    static int {fn}(int[] nums, int target) {{\n"
        "        int lo = 0, hi = nums.length - 1;\n"
        "        while (lo <= hi) {\n"
        "            int mid = (lo + hi) / 2;\n"
        f"            if (nums[mid] == target) return {ret};\n"
        "            if (nums[lo] <= nums[mid]) {\n"
        "                if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;\n"
        "            } else {\n"
        "                if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;\n"
        "            }\n"
        "        }\n"
        "        return -1;\n"
        "    }\n"
        "}\n"
    )


def _cpp_rot_search(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n\n"
        f"int {fn}(vector<int>& nums, int target) {{\n"
        "    int lo = 0, hi = (int)nums.size() - 1;\n"
        "    while (lo <= hi) {\n"
        "        int mid = (lo + hi) / 2;\n"
        f"        if (nums[mid] == target) return {ret};\n"
        "        if (nums[lo] <= nums[mid]) {\n"
        "            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;\n"
        "        } else {\n"
        "            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;\n"
        "        }\n"
        "    }\n"
        "    return -1;\n"
        "}\n\n"
        "int main() {\n"
        "    int n; cin >> n;\n"
        "    vector<int> nums(n);\n"
        "    for (int i=0;i<n;i++) cin >> nums[i];\n"
        "    int target; cin >> target;\n"
        f"    cout << {fn}(nums, target) << endl;\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_rot_search(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "class Program {\n"
        "    static void Main() {\n"
        "        var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
        "System.StringSplitOptions.RemoveEmptyEntries);\n"
        "        int idx = 0;\n"
        "        int n = int.Parse(tokens[idx++]);\n"
        "        int[] nums = new int[n];\n"
        "        for (int i=0;i<n;i++) nums[i]=int.Parse(tokens[idx++]);\n"
        "        int target = int.Parse(tokens[idx++]);\n"
        f"        System.Console.WriteLine({fn}(nums, target));\n"
        "    }\n"
        f"    static int {fn}(int[] nums, int target) {{\n"
        "        int lo = 0, hi = nums.Length - 1;\n"
        "        while (lo <= hi) {\n"
        "            int mid = (lo + hi) / 2;\n"
        f"            if (nums[mid] == target) return {ret};\n"
        "            if (nums[lo] <= nums[mid]) {\n"
        "                if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;\n"
        "            } else {\n"
        "                if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;\n"
        "            }\n"
        "        }\n"
        "        return -1;\n"
        "    }\n"
        "}\n"
    )


def _perl_rot_search(fn, wrong):
    ret = "$mid + 1" if wrong else "$mid"
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data;\n"
        "my @nums = @data[0..$n-1];\n"
        "my $target = $data[$n];\n"
        f"sub {fn} {{\n"
        "    my ($nums, $target) = @_;\n"
        "    my $lo = 0; my $hi = scalar(@$nums) - 1;\n"
        "    while ($lo <= $hi) {\n"
        "        my $mid = int(($lo + $hi) / 2);\n"
        f"        return {ret} if $nums->[$mid] == $target;\n"
        "        if ($nums->[$lo] <= $nums->[$mid]) {\n"
        "            if ($nums->[$lo] <= $target && $target < $nums->[$mid]) { $hi = $mid - 1; } else { $lo = $mid + 1; }\n"
        "        } else {\n"
        "            if ($nums->[$mid] < $target && $target <= $nums->[$hi]) { $lo = $mid + 1; } else { $hi = $mid - 1; }\n"
        "        }\n"
        "    }\n"
        "    return -1;\n"
        "}\n"
        f"print {fn}(\\@nums, $target), \"\\n\";\n"
    )


def _c_rot_search(fn, wrong):
    ret = "mid + 1" if wrong else "mid"
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        f"int {fn}(int* nums, int n, int target) {{\n"
        "    int lo = 0, hi = n - 1;\n"
        "    while (lo <= hi) {\n"
        "        int mid = (lo + hi) / 2;\n"
        f"        if (nums[mid] == target) return {ret};\n"
        "        if (nums[lo] <= nums[mid]) {\n"
        "            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;\n"
        "        } else {\n"
        "            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;\n"
        "        }\n"
        "    }\n"
        "    return -1;\n"
        "}\n\n"
        "int main() {\n"
        "    int n; scanf(\"%d\", &n);\n"
        "    int* nums = (int*)malloc(sizeof(int) * (n > 0 ? n : 1));\n"
        "    for (int i=0;i<n;i++) scanf(\"%d\", &nums[i]);\n"
        "    int target; scanf(\"%d\", &target);\n"
        f"    printf(\"%d\\n\", {fn}(nums, n, target));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_rot_search(fn, wrong):
    ret = "(mid + 1) as i32" if wrong else "mid as i32"
    return (
        "use std::io::Read;\n\n"
        f"fn {fn}(nums: &Vec<i32>, target: i32) -> i32 {{\n"
        "    if nums.is_empty() { return -1; }\n"
        "    let mut lo: i64 = 0; let mut hi: i64 = nums.len() as i64 - 1;\n"
        "    while lo <= hi {\n"
        "        let mid = ((lo + hi) / 2) as usize;\n"
        f"        if nums[mid] == target {{ return {ret}; }}\n"
        "        if nums[lo as usize] <= nums[mid] {\n"
        "            if nums[lo as usize] <= target && target < nums[mid] { hi = mid as i64 - 1; } else { lo = mid as i64 + 1; }\n"
        "        } else {\n"
        "            if nums[mid] < target && target <= nums[hi as usize] { lo = mid as i64 + 1; } else { hi = mid as i64 - 1; }\n"
        "        }\n"
        "    }\n"
        "    -1\n"
        "}\n\n"
        "fn main() {\n"
        "    let mut input = String::new();\n"
        "    std::io::stdin().read_to_string(&mut input).unwrap();\n"
        "    let mut it = input.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize;\n"
        "    let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    let target = it.next().unwrap();\n"
        f"    println!(\"{{}}\", {fn}(&nums, target));\n"
        "}\n"
    )


PROBLEMS = {
    "staircase": {
        "javascript": _js_staircase, "typescript": _ts_staircase, "java": _java_staircase,
        "cpp": _cpp_staircase, "csharp": _csharp_staircase, "perl": _perl_staircase,
        "c": _c_staircase, "rust": _rust_staircase,
    },
    "search-insert-position": {
        "javascript": _js_search_insert, "typescript": _ts_search_insert, "java": _java_search_insert,
        "cpp": _cpp_search_insert, "csharp": _csharp_search_insert, "perl": _perl_search_insert,
        "c": _c_search_insert, "rust": _rust_search_insert,
    },
    "rotated-binary-search": {
        "javascript": _js_rot_search, "typescript": _ts_rot_search, "java": _java_rot_search,
        "cpp": _cpp_rot_search, "csharp": _csharp_rot_search, "perl": _perl_rot_search,
        "c": _c_rot_search, "rust": _rust_rot_search,
    },
}


def function_name_for(con, pid):
    row = con.execute("SELECT function_contract FROM problems WHERE id=?", (pid,)).fetchone()
    return json.loads(row["function_contract"])["function_name"]


def load_cases(con, pid):
    cur = con.execute(
        "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = [SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                         is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
    row = con.execute("SELECT test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    return cases, row["test_suite_version"]


async def verify_one(pid, lang, fn, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate(build(fn, False), lang, cases)
    if correct_result.tests_passed != correct_result.tests_total:
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate(build(fn, True), lang, cases)
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
    for pid, lang_builders in PROBLEMS.items():
        cases, tsv = load_cases(con, pid)
        fn = function_name_for(con, pid)
        for lang in LANGS:
            build = lang_builders[lang]
            if ledger.already_verified(con, pid, lang, "program", test_suite_version=tsv):
                print(f"[SKIP] {pid}/{lang} already verified")
                continue
            r = await verify_one(pid, lang, fn, cases, build)
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang}(program) {pid:24s} {r['outcome']:18s} {r['detail'][:100]}", flush=True)
            if r["outcome"] == "verified":
                row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
                sc = json.loads(row["starter_code"])
                sc[lang] = build(fn, False)
                con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
                con.commit()
                ledger.record_cell(
                    con, problem_id=pid, language=lang, mode="program",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version="program-search-dp-gap-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"],
                )

    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  verified={len(verified)}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
