"""Extends the Program Mode proof-of-concept (javascript, sort-family only)
to the remaining 7 currently-reproducible languages (typescript, java, cpp,
csharp, perl, c, rust), for BOTH the sort-family (21 problems) and
search-family (7 problems) -- the same 28 problems already proven in
Function Mode, now proven in Program Mode too.

Per-language wrapping behavior confirmed by reading notebook.py directly
before writing any wrapper (not assumed):
  - java: _wrap_java_source() auto-wraps bare statements into `class Main`
    ONLY if the source contains no "class " substring -- so a helper method
    requires writing the full class explicitly (bare statements can't
    declare a sibling method in Java).
  - rust: _wrap_rust_source() auto-wraps into `fn main()` ONLY if the source
    has no "fn main()" already -- writing fn main() explicitly (so a sibling
    fn can also be declared) opts out of the auto-wrap cleanly.
  - cpp/c/csharp: NO auto-wrap at all (_prepare_compiled / _prepare_csharp
    compile `source` verbatim) -- a complete program (own #include/main /
    Program.cs) is required.
  - typescript/perl: interpreted, run as a plain script, no wrapping concept.

Same wrong-solution conventions as the Function Mode sort/search batches
(descending sort; found-index+1), run through the REAL Program Mode judge
(submission.evaluator.evaluate) against the REAL input_data/expected_output
corpus, Level 6 recorded only on genuine all-pass + wrong-rejected.
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

_SORT_PROBLEMS = [
    "bubble-sort", "bitonic-sort", "bucket-sort", "cocktail-sort", "comb-sort",
    "counting-sort", "cycle-sort", "gnome-sort", "heap-sort", "insertion-sort",
    "merge-sort", "odd-even-sort", "pancake-sort", "patience-sort", "quick-sort",
    "radix-sort", "selection-sort", "shell-sort", "stooge-sort", "strand-sort", "tim-sort",
]
_BINARY_SEARCH_PROBLEMS = [
    "binary-search", "exponential-search", "fibonacci-search",
    "interpolation-search", "jump-search", "ternary-search",
]
_LINEAR_SEARCH_PROBLEMS = ["linear-search"]

_TARGET_LANGUAGES = ["typescript", "java", "cpp", "csharp", "perl", "c", "rust"]


@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


# ── SORT programs ────────────────────────────────────────────────────────────

def _ts_sort(fn: str, wrong: bool) -> str:
    cmp = "b-a" if wrong else "a-b"
    return (
        "const data: number[] = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0];\n"
        "const arr = data.slice(1, 1 + n);\n"
        f"function {fn}(arr: number[]): void {{ arr.sort((a,b)=>{cmp}); }}\n"
        f"{fn}(arr);\n"
        "console.log(arr.join(' '));\n"
    )


def _java_sort(fn: str, wrong: bool) -> str:
    reverse = (
        "        int i=0,j=arr.length-1; while(i<j){int t=arr[i];arr[i]=arr[j];arr[j]=t;i++;j--;}\n"
        if wrong else ""
    )
    return (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt();\n"
        "        int[] arr = new int[n];\n"
        "        for (int i=0;i<n;i++) arr[i]=sc.nextInt();\n"
        f"        {fn}(arr);\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        for (int i=0;i<n;i++) { if (i>0) sb.append(' '); sb.append(arr[i]); }\n"
        "        System.out.println(sb.toString());\n"
        "    }\n"
        f"    static void {fn}(int[] arr) {{\n"
        "        java.util.Arrays.sort(arr);\n"
        f"{reverse}"
        "    }\n"
        "}\n"
    )


def _cpp_sort(fn: str, wrong: bool) -> str:
    body = "std::sort(arr.rbegin(), arr.rend());" if wrong else "std::sort(arr.begin(), arr.end());"
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\n"
        f"void {fn}(vector<int>& arr) {{ {body} }}\n\n"
        "int main() {\n"
        "    int n; cin >> n;\n"
        "    vector<int> arr(n);\n"
        "    for (int i=0;i<n;i++) cin >> arr[i];\n"
        f"    {fn}(arr);\n"
        "    for (int i=0;i<n;i++) { if (i) cout << ' '; cout << arr[i]; }\n"
        "    cout << endl;\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_sort(fn: str, wrong: bool) -> str:
    body = "System.Array.Sort(arr); System.Array.Reverse(arr);" if wrong else "System.Array.Sort(arr);"
    return (
        "class Program {\n"
        "    static void Main() {\n"
        "        var tokens = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, "
        "System.StringSplitOptions.RemoveEmptyEntries);\n"
        "        int idx = 0;\n"
        "        int n = int.Parse(tokens[idx++]);\n"
        "        int[] arr = new int[n];\n"
        "        for (int i=0;i<n;i++) arr[i]=int.Parse(tokens[idx++]);\n"
        f"        {fn}(arr);\n"
        "        System.Console.WriteLine(string.Join(\" \", arr));\n"
        "    }\n"
        f"    static void {fn}(int[] arr) {{ {body} }}\n"
        "}\n"
    )


def _perl_sort(fn: str, wrong: bool) -> str:
    cmp = "$b <=> $a" if wrong else "$a <=> $b"
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data;\n"
        "my @arr = @data[0..$n-1];\n"
        f"sub {fn} {{ my ($r) = @_; @$r = sort {{ {cmp} }} @$r; }}\n"
        f"{fn}(\\@arr);\n"
        "print join(' ', @arr), \"\\n\";\n"
    )


def _c_sort(fn: str, wrong: bool) -> str:
    if wrong:
        cmp_loop = (
            f"void {fn}(int* arr, int n) {{\n"
            "    for (int i=0;i<n-1;i++) for (int j=0;j<n-1-i;j++)\n"
            "        if (arr[j] < arr[j+1]) { int t=arr[j]; arr[j]=arr[j+1]; arr[j+1]=t; }\n"
            "}\n"
        )
    else:
        cmp_loop = (
            f"void {fn}(int* arr, int n) {{\n"
            "    for (int i=0;i<n-1;i++) for (int j=0;j<n-1-i;j++)\n"
            "        if (arr[j] > arr[j+1]) { int t=arr[j]; arr[j]=arr[j+1]; arr[j+1]=t; }\n"
            "}\n"
        )
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        f"{cmp_loop}\n"
        "int main() {\n"
        "    int n; scanf(\"%d\", &n);\n"
        "    int* arr = (int*)malloc(sizeof(int) * (n > 0 ? n : 1));\n"
        "    for (int i=0;i<n;i++) scanf(\"%d\", &arr[i]);\n"
        f"    {fn}(arr, n);\n"
        "    for (int i=0;i<n;i++) { if (i) printf(\" \"); printf(\"%d\", arr[i]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_sort(fn: str, wrong: bool) -> str:
    body = "arr.sort(); arr.reverse();" if wrong else "arr.sort();"
    return (
        "use std::io::Read;\n\n"
        f"fn {fn}(arr: &mut Vec<i32>) {{ {body} }}\n\n"
        "fn main() {\n"
        "    let mut input = String::new();\n"
        "    std::io::stdin().read_to_string(&mut input).unwrap();\n"
        "    let mut it = input.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize;\n"
        "    let mut arr: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        f"    {fn}(&mut arr);\n"
        "    let strs: Vec<String> = arr.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \"));\n"
        "}\n"
    )


# ── SEARCH programs (binary-search-family: sorted array; ret = mid or mid+1) ─

def _ts_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        "const data: number[] = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0];\n"
        "const nums = data.slice(1, 1 + n);\n"
        "const target = data[1 + n];\n"
        f"function {fn}(nums: number[], target: number): number {{\n"
        "    let lo = 0, hi = nums.length - 1;\n"
        "    while (lo <= hi) {\n"
        "        const mid = (lo + hi) >> 1;\n"
        f"        if (nums[mid] === target) return {ret};\n"
        "        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n"
        "    }\n"
        "    return -1;\n"
        "}\n"
        f"console.log({fn}(nums, target));\n"
    )


def _java_bsearch(fn: str, wrong: bool) -> str:
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
        "        int lo=0, hi=nums.length-1;\n"
        "        while (lo<=hi) {\n"
        "            int mid=(lo+hi)/2;\n"
        f"            if (nums[mid]==target) return {ret};\n"
        "            if (nums[mid]<target) lo=mid+1; else hi=mid-1;\n"
        "        }\n"
        "        return -1;\n"
        "    }\n"
        "}\n"
    )


def _cpp_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n\n"
        f"int {fn}(vector<int>& nums, int target) {{\n"
        "    int lo=0, hi=(int)nums.size()-1;\n"
        "    while (lo<=hi) {\n"
        "        int mid=(lo+hi)/2;\n"
        f"        if (nums[mid]==target) return {ret};\n"
        "        if (nums[mid]<target) lo=mid+1; else hi=mid-1;\n"
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


def _csharp_bsearch(fn: str, wrong: bool) -> str:
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
        "        int lo=0, hi=nums.Length-1;\n"
        "        while (lo<=hi) {\n"
        "            int mid=(lo+hi)/2;\n"
        f"            if (nums[mid]==target) return {ret};\n"
        "            if (nums[mid]<target) lo=mid+1; else hi=mid-1;\n"
        "        }\n"
        "        return -1;\n"
        "    }\n"
        "}\n"
    )


def _perl_bsearch(fn: str, wrong: bool) -> str:
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
        f"        if ($nums->[$mid] == $target) {{ return {ret}; }}\n"
        "        if ($nums->[$mid] < $target) { $lo = $mid + 1; } else { $hi = $mid - 1; }\n"
        "    }\n"
        "    return -1;\n"
        "}\n"
        f"print {fn}(\\@nums, $target), \"\\n\";\n"
    )


def _c_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        f"int {fn}(int* nums, int n, int target) {{\n"
        "    int lo=0, hi=n-1;\n"
        "    while (lo<=hi) {\n"
        "        int mid=(lo+hi)/2;\n"
        f"        if (nums[mid]==target) return {ret};\n"
        "        if (nums[mid]<target) lo=mid+1; else hi=mid-1;\n"
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


def _rust_bsearch(fn: str, wrong: bool) -> str:
    ret = "mid + 1" if wrong else "mid"
    return (
        "use std::io::Read;\n\n"
        f"fn {fn}(nums: &Vec<i32>, target: i32) -> i32 {{\n"
        "    let mut lo: i32 = 0;\n"
        "    let mut hi: i32 = nums.len() as i32 - 1;\n"
        "    while lo <= hi {\n"
        "        let mid = (lo + hi) / 2;\n"
        f"        if nums[mid as usize] == target {{ return {ret}; }}\n"
        "        if nums[mid as usize] < target { lo = mid + 1; } else { hi = mid - 1; }\n"
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


# ── SEARCH programs (linear-search: unsorted, first match; ret = i or i+1) ──

def _ts_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
    return (
        "const data: number[] = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0];\n"
        "const nums = data.slice(1, 1 + n);\n"
        "const target = data[1 + n];\n"
        f"function {fn}(nums: number[], target: number): number {{\n"
        f"    for (let i = 0; i < nums.length; i++) {{ if (nums[i] === target) return {ret}; }}\n"
        "    return -1;\n"
        "}\n"
        f"console.log({fn}(nums, target));\n"
    )


def _java_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
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
        f"        for (int i=0;i<nums.length;i++) {{ if (nums[i]==target) return {ret}; }}\n"
        "        return -1;\n"
        "    }\n"
        "}\n"
    )


def _cpp_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n\n"
        f"int {fn}(vector<int>& nums, int target) {{\n"
        f"    for (int i=0;i<(int)nums.size();i++) {{ if (nums[i]==target) return {ret}; }}\n"
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


def _csharp_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
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
        f"        for (int i=0;i<nums.Length;i++) {{ if (nums[i]==target) return {ret}; }}\n"
        "        return -1;\n"
        "    }\n"
        "}\n"
    )


def _perl_linear(fn: str, wrong: bool) -> str:
    ret = "$i + 1" if wrong else "$i"
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data;\n"
        "my @nums = @data[0..$n-1];\n"
        "my $target = $data[$n];\n"
        f"sub {fn} {{\n"
        "    my ($nums, $target) = @_;\n"
        f"    for (my $i = 0; $i < scalar(@$nums); $i++) {{ if ($nums->[$i] == $target) {{ return {ret}; }} }}\n"
        "    return -1;\n"
        "}\n"
        f"print {fn}(\\@nums, $target), \"\\n\";\n"
    )


def _c_linear(fn: str, wrong: bool) -> str:
    ret = "i + 1" if wrong else "i"
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        f"int {fn}(int* nums, int n, int target) {{\n"
        f"    for (int i=0;i<n;i++) {{ if (nums[i]==target) return {ret}; }}\n"
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


def _rust_linear(fn: str, wrong: bool) -> str:
    ret = "i as i32 + 1" if wrong else "i as i32"
    return (
        "use std::io::Read;\n\n"
        f"fn {fn}(nums: &Vec<i32>, target: i32) -> i32 {{\n"
        f"    for i in 0..nums.len() {{ if nums[i] == target {{ return {ret}; }} }}\n"
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


_SORT_BUILDERS = {
    "typescript": _ts_sort, "java": _java_sort, "cpp": _cpp_sort,
    "csharp": _csharp_sort, "perl": _perl_sort, "c": _c_sort, "rust": _rust_sort,
}
_BSEARCH_BUILDERS = {
    "typescript": _ts_bsearch, "java": _java_bsearch, "cpp": _cpp_bsearch,
    "csharp": _csharp_bsearch, "perl": _perl_bsearch, "c": _c_bsearch, "rust": _rust_bsearch,
}
_LINEAR_BUILDERS = {
    "typescript": _ts_linear, "java": _java_linear, "cpp": _cpp_linear,
    "csharp": _csharp_linear, "perl": _perl_linear, "c": _c_linear, "rust": _rust_linear,
}


def load_cases(con: sqlite3.Connection, pid: str) -> tuple[list[SimpleCase], str]:
    cur = con.execute(
        "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = [SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                         is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
    row = con.execute("SELECT test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    return cases, row["test_suite_version"]


def function_name_for(con: sqlite3.Connection, pid: str) -> str:
    row = con.execute("SELECT function_contract FROM problems WHERE id=?", (pid,)).fetchone()
    return json.loads(row["function_contract"])["function_name"]


async def verify_one(pid: str, lang: str, fn: str, cases: list[SimpleCase], build) -> dict:
    t0 = time.monotonic()
    correct_result = await evaluate(build(fn, False), lang, cases)
    if correct_result.tests_passed != correct_result.tests_total:
        sample_fail = next((r for r in correct_result.test_results if not r.passed), None)
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:200]} "
                          f"sample_stderr={(sample_fail.stderr if sample_fail else '')[:200]} "
                          f"sample_actual={(sample_fail.actual_output if sample_fail else '')[:80]!r} "
                          f"sample_expected={(sample_fail.expected_output if sample_fail else '')[:80]!r}",
                "duration_ms": (time.monotonic() - t0) * 1000}

    wrong_result = await evaluate(build(fn, True), lang, cases)
    if wrong_result.tests_passed >= wrong_result.tests_total:
        return {"pid": pid, "lang": lang, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {wrong_result.tests_total}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "lang": lang, "outcome": "verified",
            "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} correct, "
                      f"wrong rejected on {wrong_result.tests_total - wrong_result.tests_passed}/{wrong_result.tests_total}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main() -> int:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)

    groups = [(p, _SORT_BUILDERS) for p in _SORT_PROBLEMS] + \
             [(p, _BSEARCH_BUILDERS) for p in _BINARY_SEARCH_PROBLEMS] + \
             [(p, _LINEAR_BUILDERS) for p in _LINEAR_SEARCH_PROBLEMS]

    results = []
    skipped = 0
    for lang in _TARGET_LANGUAGES:
        for pid, builders in groups:
            _, tsv = load_cases(con, pid)
            if ledger.already_verified(con, pid, lang, "program", test_suite_version=tsv):
                skipped += 1
                continue
            fn = function_name_for(con, pid)
            cases, tsv = load_cases(con, pid)
            r = await verify_one(pid, lang, fn, cases, builders[lang])
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s}(program) {pid:22s} {r['outcome']:18s} {r['detail'][:120]}", flush=True)

            if r["outcome"] == "verified":
                row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
                sc = json.loads(row["starter_code"])
                # Saved as the real working solution's source shape for now
                # (matches every other language's verified reference) --
                # additive per-language key, never overwrites another
                # language's entry.
                sc[lang] = builders[lang](fn, False)
                con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
                con.commit()
                ledger.record_cell(
                    con, problem_id=pid, language=lang, mode="program",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-program-sort-search-v1",
                    test_suite_version=tsv,
                    duration_ms=r["duration_ms"],
                )

    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL attempted: {len(results)}  skipped (already verified): {skipped}")
    print(f"verified={len(verified)}  reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")

    (REPO_ROOT / "docs" / "atlascode-program-mode-sort-search-remaining.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
