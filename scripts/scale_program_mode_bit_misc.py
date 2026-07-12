"""Extends Program Mode to the bit-misc cluster (valid-parentheses,
valid-anagram, missing-number, single-number, number-of-1-bits,
power-of-two, hamming-distance, move-zeroes, majority-element) across the
8 working languages -- same algorithms already proven in Function Mode
(scale_bit_misc_cluster.py), including the Perl `use integer` fix for
single-number, wrapped in stdin/stdout matching each problem's existing
Python starter_code convention.
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
_TARGET_LANGUAGES = ["javascript", "typescript", "java", "cpp", "csharp", "perl", "c", "rust"]


@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


# ── valid-parentheses ────────────────────────────────────────────────────────
def _js_valid_paren(wrong):
    return (
        "const s = require('fs').readFileSync(0,'utf8').trim();\n"
        "function is_valid(s) {\n"
        "    const stack = []; const pairs = {')':'(', ']':'[', '}':'{'};\n"
        "    for (const ch of s) {\n"
        "        if (ch==='('||ch==='['||ch==='{') stack.push(ch);\n"
        "        else { if (stack.length===0 || stack.pop() !== pairs[ch]) return false; }\n"
        "    }\n"
        f"    return {'stack.length !== 0' if wrong else 'stack.length === 0'};\n"
        "}\n"
        "console.log(is_valid(s) ? 'true' : 'false');\n"
    )


def _ts_valid_paren(wrong):
    return (
        "const s: string = require('fs').readFileSync(0,'utf8').trim();\n"
        "function is_valid(s: string): boolean {\n"
        "    const stack: string[] = []; const pairs: Record<string,string> = {')':'(', ']':'[', '}':'{'};\n"
        "    for (const ch of s) {\n"
        "        if (ch==='('||ch==='['||ch==='{') stack.push(ch);\n"
        "        else { if (stack.length===0 || stack.pop() !== pairs[ch]) return false; }\n"
        "    }\n"
        f"    return {'stack.length !== 0' if wrong else 'stack.length === 0'};\n"
        "}\n"
        "console.log(is_valid(s) ? 'true' : 'false');\n"
    )


def _java_valid_paren(wrong):
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    String s = sc.nextLine();\n"
        "    System.out.println(is_valid(s) ? \"true\" : \"false\");\n"
        "}\n"
        "static boolean is_valid(String s) {\n"
        "    java.util.Deque<Character> stack = new java.util.ArrayDeque<>();\n"
        "    for (char ch : s.toCharArray()) {\n"
        "        if (ch=='('||ch=='['||ch=='{') stack.push(ch);\n"
        "        else {\n"
        "            if (stack.isEmpty()) return false;\n"
        "            char top = stack.pop();\n"
        "            if ((ch==')'&&top!='(') || (ch==']'&&top!='[') || (ch=='}'&&top!='{')) return false;\n"
        "        }\n"
        "    }\n"
        f"    return {'!stack.isEmpty()' if wrong else 'stack.isEmpty()'};\n"
        "} }\n"
    )


def _cpp_valid_paren(wrong):
    return (
        "#include <iostream>\n#include <string>\nusing namespace std;\n"
        "bool is_valid(string s) {\n"
        "    string stack;\n"
        "    for (char ch : s) {\n"
        "        if (ch=='('||ch=='['||ch=='{') stack.push_back(ch);\n"
        "        else {\n"
        "            if (stack.empty()) return false;\n"
        "            char top = stack.back(); stack.pop_back();\n"
        "            if ((ch==')'&&top!='(') || (ch==']'&&top!='[') || (ch=='}'&&top!='{')) return false;\n"
        "        }\n"
        "    }\n"
        f"    return {'!stack.empty()' if wrong else 'stack.empty()'};\n"
        "}\n"
        "int main() { string s; getline(cin, s); cout << (is_valid(s) ? \"true\" : \"false\") << endl; return 0; }\n"
    )


def _csharp_valid_paren(wrong):
    return (
        "class Program { static void Main() {\n"
        "    string s = System.Console.In.ReadLine();\n"
        "    System.Console.WriteLine(is_valid(s) ? \"true\" : \"false\");\n"
        "}\n"
        "static bool is_valid(string s) {\n"
        "    var stack = new System.Collections.Generic.Stack<char>();\n"
        "    foreach (char ch in s) {\n"
        "        if (ch=='('||ch=='['||ch=='{') stack.Push(ch);\n"
        "        else {\n"
        "            if (stack.Count==0) return false;\n"
        "            char top = stack.Pop();\n"
        "            if ((ch==')'&&top!='(') || (ch==']'&&top!='[') || (ch=='}'&&top!='{')) return false;\n"
        "        }\n"
        "    }\n"
        f"    return {'stack.Count != 0' if wrong else 'stack.Count == 0'};\n"
        "} }\n"
    )


def _perl_valid_paren(wrong):
    return (
        "my $s = <STDIN>; chomp $s;\n"
        "sub is_valid {\n"
        "    my ($s) = @_;\n"
        "    my @stack;\n"
        "    my %pairs = (')' => '(', ']' => '[', '}' => '{');\n"
        "    foreach my $ch (split //, $s) {\n"
        "        if ($ch eq '(' || $ch eq '[' || $ch eq '{') { push @stack, $ch; }\n"
        "        else { return 0 if !@stack; my $top = pop @stack; return 0 if $top ne $pairs{$ch}; }\n"
        "    }\n"
        f"    return {'scalar(@stack) != 0' if wrong else 'scalar(@stack) == 0'};\n"
        "}\n"
        "print is_valid($s) ? \"true\\n\" : \"false\\n\";\n"
    )


def _c_valid_paren(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
        "int is_valid(char* s) {\n"
        "    int n = strlen(s);\n"
        "    char* stack = (char*)malloc(n+1); int top = 0;\n"
        "    int ok = 1;\n"
        "    for (int i=0;i<n;i++) {\n"
        "        char ch = s[i];\n"
        "        if (ch=='('||ch=='['||ch=='{') { stack[top++] = ch; }\n"
        "        else {\n"
        "            if (top==0) { ok = 0; break; }\n"
        "            char t = stack[--top];\n"
        "            if ((ch==')'&&t!='(') || (ch==']'&&t!='[') || (ch=='}'&&t!='{')) { ok = 0; break; }\n"
        "        }\n"
        "    }\n"
        f"    int result = ok && {'top != 0' if wrong else 'top == 0'};\n"
        "    free(stack);\n"
        "    return result;\n"
        "}\n"
        "int main() {\n"
        "    char s[10001]; fgets(s, sizeof(s), stdin); s[strcspn(s, \"\\r\\n\")]=0;\n"
        "    printf(\"%s\\n\", is_valid(s) ? \"true\" : \"false\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_valid_paren(wrong):
    return (
        "use std::io::Read;\n"
        "fn is_valid(s: &str) -> bool {\n"
        "    let mut stack: Vec<char> = Vec::new();\n"
        "    for ch in s.chars() {\n"
        "        if ch=='('||ch=='['||ch=='{' { stack.push(ch); }\n"
        "        else {\n"
        "            let top = stack.pop();\n"
        "            match (ch, top) {\n"
        "                (')', Some('(')) => {},\n"
        "                (']', Some('[')) => {},\n"
        "                ('}', Some('{')) => {},\n"
        "                _ => return false,\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    {'!stack.is_empty()' if wrong else 'stack.is_empty()'}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    println!(\"{}\", if is_valid(s.trim()) { \"true\" } else { \"false\" }); }\n"
    )


# ── valid-anagram ────────────────────────────────────────────────────────────
def _js_valid_anagram(wrong):
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const s = lines[0], t = lines[1];\n"
        "function is_anagram(s, t) {\n"
        "    if (s.length !== t.length) return false;\n"
        "    const count = {};\n"
        "    for (const ch of s) count[ch] = (count[ch]||0) + 1;\n"
        "    for (const ch of t) { count[ch] = (count[ch]||0) - 1; if (count[ch] < 0) return false; }\n"
        f"    return {'!Object.values(count).every(v => v === 0)' if wrong else 'Object.values(count).every(v => v === 0)'};\n"
        "}\n"
        "console.log(is_anagram(s, t) ? 'true' : 'false');\n"
    )


def _ts_valid_anagram(wrong):
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const s: string = lines[0], t: string = lines[1];\n"
        "function is_anagram(s: string, t: string): boolean {\n"
        "    if (s.length !== t.length) return false;\n"
        "    const count: Record<string, number> = {};\n"
        "    for (const ch of s) count[ch] = (count[ch]||0) + 1;\n"
        "    for (const ch of t) { count[ch] = (count[ch]||0) - 1; if (count[ch] < 0) return false; }\n"
        f"    return {'!Object.values(count).every(v => v === 0)' if wrong else 'Object.values(count).every(v => v === 0)'};\n"
        "}\n"
        "console.log(is_anagram(s, t) ? 'true' : 'false');\n"
    )


def _java_valid_anagram(wrong):
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    String s = sc.nextLine(); String t = sc.nextLine();\n"
        "    System.out.println(is_anagram(s, t) ? \"true\" : \"false\");\n"
        "}\n"
        "static boolean is_anagram(String s, String t) {\n"
        "    if (s.length() != t.length()) return false;\n"
        "    int[] count = new int[256];\n"
        "    for (char c : s.toCharArray()) count[c]++;\n"
        "    for (char c : t.toCharArray()) count[c]--;\n"
        "    for (int c : count) if (c != 0) return " + ("true" if wrong else "false") + ";\n"
        f"    return {'false' if wrong else 'true'};\n"
        "} }\n"
    )


def _cpp_valid_anagram(wrong):
    return (
        "#include <iostream>\n#include <string>\nusing namespace std;\n"
        "bool is_anagram(string s, string t) {\n"
        "    if (s.size() != t.size()) return false;\n"
        "    int count[256] = {0};\n"
        "    for (char c : s) count[(unsigned char)c]++;\n"
        "    for (char c : t) count[(unsigned char)c]--;\n"
        "    for (int c : count) if (c != 0) return " + ("true" if wrong else "false") + ";\n"
        f"    return {'false' if wrong else 'true'};\n"
        "}\n"
        "int main() { string s, t; getline(cin, s); getline(cin, t); cout << (is_anagram(s,t) ? \"true\" : \"false\") << endl; return 0; }\n"
    )


def _csharp_valid_anagram(wrong):
    return (
        "class Program { static void Main() {\n"
        "    string s = System.Console.In.ReadLine(); string t = System.Console.In.ReadLine();\n"
        "    System.Console.WriteLine(is_anagram(s, t) ? \"true\" : \"false\");\n"
        "}\n"
        "static bool is_anagram(string s, string t) {\n"
        "    if (s.Length != t.Length) return false;\n"
        "    int[] count = new int[256];\n"
        "    foreach (char c in s) count[c]++;\n"
        "    foreach (char c in t) count[c]--;\n"
        "    foreach (int c in count) if (c != 0) return " + ("true" if wrong else "false") + ";\n"
        f"    return {'false' if wrong else 'true'};\n"
        "} }\n"
    )


def _perl_valid_anagram(wrong):
    return (
        "my @lines = split /\\n/, do { local $/; <STDIN> };\n"
        "my $s = $lines[0]; my $t = $lines[1];\n"
        "sub is_anagram {\n"
        "    my ($s, $t) = @_;\n"
        "    return 0 if length($s) != length($t);\n"
        "    my %count;\n"
        "    foreach my $ch (split //, $s) { $count{$ch}++; }\n"
        "    foreach my $ch (split //, $t) { $count{$ch}--; return 0 if $count{$ch} < 0; }\n"
        "    foreach my $v (values %count) { return " + ("1" if wrong else "0") + " if $v != 0; }\n"
        f"    return {'0' if wrong else '1'};\n"
        "}\n"
        "print is_anagram($s, $t) ? \"true\\n\" : \"false\\n\";\n"
    )


def _c_valid_anagram(wrong):
    return (
        "#include <stdio.h>\n#include <string.h>\n"
        "int is_anagram(char* s, char* t) {\n"
        "    int ns = strlen(s), nt = strlen(t);\n"
        "    if (ns != nt) return 0;\n"
        "    int count[256] = {0};\n"
        "    for (int i=0;i<ns;i++) count[(unsigned char)s[i]]++;\n"
        "    for (int i=0;i<nt;i++) count[(unsigned char)t[i]]--;\n"
        "    for (int i=0;i<256;i++) if (count[i] != 0) return " + ("1" if wrong else "0") + ";\n"
        f"    return {'0' if wrong else '1'};\n"
        "}\n"
        "int main() {\n"
        "    char s[10001], t[10001];\n"
        "    fgets(s, sizeof(s), stdin); s[strcspn(s, \"\\r\\n\")]=0;\n"
        "    fgets(t, sizeof(t), stdin); t[strcspn(t, \"\\r\\n\")]=0;\n"
        "    printf(\"%s\\n\", is_anagram(s,t) ? \"true\" : \"false\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_valid_anagram(wrong):
    return (
        "use std::io::{self, BufRead};\n"
        "fn is_anagram(s: &str, t: &str) -> bool {\n"
        "    if s.len() != t.len() { return false; }\n"
        "    let mut count = [0i32; 256];\n"
        "    for b in s.bytes() { count[b as usize] += 1; }\n"
        "    for b in t.bytes() { count[b as usize] -= 1; }\n"
        "    for c in count.iter() { if *c != 0 { return " + ("true" if wrong else "false") + "; } }\n"
        f"    {'false' if wrong else 'true'}\n"
        "}\n"
        "fn main() { let stdin = io::stdin(); let mut lines = stdin.lock().lines();\n"
        "    let s = lines.next().unwrap().unwrap(); let t = lines.next().unwrap().unwrap();\n"
        "    println!(\"{}\", if is_anagram(&s, &t) { \"true\" } else { \"false\" }); }\n"
    )


# ── missing-number ───────────────────────────────────────────────────────────
def _js_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function missing_number(nums) {\n"
        "    const nn = nums.length; let expected = nn*(nn+1)/2; let actual = 0;\n"
        "    for (const x of nums) actual += x;\n"
        f"    return (expected - actual){a};\n"
        "}\n"
        "console.log(missing_number(nums));\n"
    )


def _ts_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function missing_number(nums: number[]): number {\n"
        "    const nn = nums.length; let expected = nn*(nn+1)/2; let actual = 0;\n"
        "    for (const x of nums) actual += x;\n"
        f"    return (expected - actual){a};\n"
        "}\n"
        "console.log(missing_number(nums));\n"
    )


def _java_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(missing_number(nums));\n"
        "}\n"
        "static int missing_number(int[] nums) {\n"
        "    int n = nums.length; long expected = (long)n*(n+1)/2; long actual = 0;\n"
        "    for (int x : nums) actual += x;\n"
        f"    return (int)(expected - actual){a};\n"
        "} }\n"
    )


def _cpp_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "int missing_number(vector<int>& nums) {\n"
        "    long long n = nums.size(); long long expected = n*(n+1)/2; long long actual = 0;\n"
        "    for (int x : nums) actual += x;\n"
        f"    return (int)(expected - actual){a};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << missing_number(nums) << endl; return 0; }\n"
    )


def _csharp_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n = int.Parse(t[idx++]); int[] nums = new int[n];\n"
        "    for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(missing_number(nums));\n"
        "}\n"
        "static int missing_number(int[] nums) {\n"
        "    long n = nums.Length; long expected = n*(n+1)/2; long actual = 0;\n"
        "    foreach (int x in nums) actual += x;\n"
        f"    return (int)(expected - actual){a};\n"
        "} }\n"
    )


def _perl_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub missing_number {\n"
        "    my ($nums) = @_;\n"
        "    my $nn = scalar(@$nums); my $expected = $nn*($nn+1)/2; my $actual = 0;\n"
        "    foreach my $x (@$nums) { $actual += $x; }\n"
        f"    return ($expected - $actual){a};\n"
        "}\n"
        "print missing_number(\\@nums), \"\\n\";\n"
    )


def _c_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int missing_number(int* nums, int n) {\n"
        "    long long expected = (long long)n*(n+1)/2; long long actual = 0;\n"
        "    for (int i=0;i<n;i++) actual += nums[i];\n"
        f"    return (int)(expected - actual){a};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); printf(\"%d\\n\", missing_number(nums,n)); return 0; }\n"
    )


def _rust_missing(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn missing_number(nums: &Vec<i32>) -> i32 {\n"
        "    let n = nums.len() as i64; let expected = n*(n+1)/2;\n"
        "    let actual: i64 = nums.iter().map(|&x| x as i64).sum();\n"
        f"    (expected - actual) as i32{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", missing_number(&nums)); }\n"
    )


# ── single-number ────────────────────────────────────────────────────────────
def _js_single(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        f"function single_number(nums) {{ let r=0; for (const x of nums) r ^= x; return r{a}; }}\n"
        "console.log(single_number(nums));\n"
    )


def _ts_single(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        f"function single_number(nums: number[]): number {{ let r=0; for (const x of nums) r ^= x; return r{a}; }}\n"
        "console.log(single_number(nums));\n"
    )


def _java_single(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(single_number(nums));\n"
        "}\n"
        f"static int single_number(int[] nums) {{ int r=0; for (int x: nums) r ^= x; return r{a}; }} }}\n"
    )


def _cpp_single(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        f"int single_number(vector<int>& nums) {{ int r=0; for (int x: nums) r ^= x; return r{a}; }}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << single_number(nums) << endl; return 0; }\n"
    )


def _csharp_single(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(single_number(nums));\n"
        "}\n"
        f"static int single_number(int[] nums) {{ int r=0; foreach (int x in nums) r ^= x; return r{a}; }} }}\n"
    )


def _perl_single(wrong):
    # Perl's ^ defaults to unsigned 64-bit semantics -- `use integer` forces
    # signed native-integer arithmetic (real bug found+fixed in the
    # Function Mode version of this same problem).
    a = " + 1" if wrong else ""
    return (
        "use integer;\n"
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        f"sub single_number {{ my ($nums) = @_; my $r=0; foreach my $x (@$nums) {{ $r ^= $x; }} return $r{a}; }}\n"
        "print single_number(\\@nums), \"\\n\";\n"
    )


def _c_single(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        f"int single_number(int* nums, int n) {{ int r=0; for (int i=0;i<n;i++) r ^= nums[i]; return r{a}; }}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); printf(\"%d\\n\", single_number(nums,n)); return 0; }\n"
    )


def _rust_single(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        f"fn single_number(nums: &Vec<i32>) -> i32 {{ let mut r=0; for x in nums.iter() {{ r ^= x; }} r{a} }}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", single_number(&nums)); }\n"
    )


# ── number-of-1-bits ─────────────────────────────────────────────────────────
def _js_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "const n = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function hamming_weight(n) {\n"
        "    let count = 0; let x = n >>> 0;\n"
        "    while (x !== 0) { count += x & 1; x = x >>> 1; }\n"
        f"    return count{a};\n"
        "}\n"
        "console.log(hamming_weight(n));\n"
    )


def _ts_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "const n: number = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function hamming_weight(n: number): number {\n"
        "    let count = 0; let x = n >>> 0;\n"
        "    while (x !== 0) { count += x & 1; x = x >>> 1; }\n"
        f"    return count{a};\n"
        "}\n"
        "console.log(hamming_weight(n));\n"
    )


def _java_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    int n = Integer.parseInt(new Scanner(System.in).nextLine().trim());\n"
        f"    System.out.println(Integer.bitCount(n){a});\n"
        "} }\n"
    )


def _cpp_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\nusing namespace std;\n"
        f"int main() {{ int n; cin>>n; cout << (__builtin_popcount((unsigned int)n){a}) << endl; return 0; }}\n"
    )


def _csharp_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    int n = int.Parse(System.Console.In.ReadToEnd().Trim());\n"
        f"    System.Console.WriteLine(System.Numerics.BitOperations.PopCount((uint)n){a});\n"
        "} }\n"
    )


def _perl_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "my $n = <STDIN>; chomp $n; $n = $n + 0;\n"
        "sub hamming_weight {\n"
        "    my ($n) = @_;\n"
        "    my $x = $n & 0xFFFFFFFF;\n"
        "    my $count = 0;\n"
        "    while ($x != 0) { $count += $x & 1; $x = $x >> 1; }\n"
        f"    return $count{a};\n"
        "}\n"
        "print hamming_weight($n), \"\\n\";\n"
    )


def _c_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n"
        f"int main() {{ int n; scanf(\"%d\",&n); printf(\"%d\\n\", __builtin_popcount((unsigned int)n){a}); return 0; }}\n"
    )


def _rust_popcount(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let n: i32 = s.trim().parse().unwrap();\n"
        f"    println!(\"{{}}\", (n as u32).count_ones() as i32{a}); }}\n"
    )


# ── power-of-two ─────────────────────────────────────────────────────────────
def _js_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) === 0)" if wrong else "n > 0 && (n & (n - 1)) === 0"
    return (
        "const n = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        f"console.log(({ret}) ? 'true' : 'false');\n"
    )


def _ts_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) === 0)" if wrong else "n > 0 && (n & (n - 1)) === 0"
    return (
        "const n: number = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        f"console.log(({ret}) ? 'true' : 'false');\n"
    )


def _java_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) == 0)" if wrong else "n > 0 && (n & (n - 1)) == 0"
    return (
        "public class Main { public static void main(String[] args) {\n"
        "    int n = Integer.parseInt(new java.util.Scanner(System.in).nextLine().trim());\n"
        f"    System.out.println(({ret}) ? \"true\" : \"false\");\n"
        "} }\n"
    )


def _cpp_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) == 0)" if wrong else "n > 0 && (n & (n - 1)) == 0"
    return (
        "#include <iostream>\nusing namespace std;\n"
        f"int main() {{ int n; cin>>n; cout << (({ret}) ? \"true\" : \"false\") << endl; return 0; }}\n"
    )


def _csharp_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) == 0)" if wrong else "n > 0 && (n & (n - 1)) == 0"
    return (
        "class Program { static void Main() {\n"
        "    int n = int.Parse(System.Console.In.ReadToEnd().Trim());\n"
        f"    System.Console.WriteLine(({ret}) ? \"true\" : \"false\");\n"
        "} }\n"
    )


def _perl_pow2(wrong):
    ret = "!($n > 0 && ($n & ($n - 1)) == 0)" if wrong else "$n > 0 && ($n & ($n - 1)) == 0"
    return (
        "my $n = <STDIN>; chomp $n; $n = $n + 0;\n"
        f"print (({ret}) ? \"true\\n\" : \"false\\n\");\n"
    )


def _c_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) == 0)" if wrong else "n > 0 && (n & (n - 1)) == 0"
    return (
        "#include <stdio.h>\n"
        f"int main() {{ int n; scanf(\"%d\",&n); printf(\"%s\\n\", ({ret}) ? \"true\" : \"false\"); return 0; }}\n"
    )


def _rust_pow2(wrong):
    ret = "!(n > 0 && (n & (n - 1)) == 0)" if wrong else "n > 0 && (n & (n - 1)) == 0"
    return (
        "use std::io::Read;\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let n: i32 = s.trim().parse().unwrap();\n"
        f"    println!(\"{{}}\", if {ret} {{ \"true\" }} else {{ \"false\" }}); }}\n"
    )


# ── hamming-distance ─────────────────────────────────────────────────────────
def _js_hamdist(wrong):
    a = " + 1" if wrong else ""
    return (
        "const [x0,y0] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "function hamming_distance(x, y) {\n"
        "    let v = (x ^ y) >>> 0; let count = 0;\n"
        "    while (v !== 0) { count += v & 1; v = v >>> 1; }\n"
        f"    return count{a};\n"
        "}\n"
        "console.log(hamming_distance(x0, y0));\n"
    )


def _ts_hamdist(wrong):
    a = " + 1" if wrong else ""
    return (
        "const [x0,y0]: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "function hamming_distance(x: number, y: number): number {\n"
        "    let v = (x ^ y) >>> 0; let count = 0;\n"
        "    while (v !== 0) { count += v & 1; v = v >>> 1; }\n"
        f"    return count{a};\n"
        "}\n"
        "console.log(hamming_distance(x0, y0));\n"
    )


def _java_hamdist(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int x = sc.nextInt(); int y = sc.nextInt();\n"
        f"    System.out.println(Integer.bitCount(x ^ y){a});\n"
        "} }\n"
    )


def _cpp_hamdist(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\nusing namespace std;\n"
        f"int main() {{ int x,y; cin>>x>>y; cout << (__builtin_popcount((unsigned int)(x ^ y)){a}) << endl; return 0; }}\n"
    )


def _csharp_hamdist(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int x = int.Parse(t[0]); int y = int.Parse(t[1]);\n"
        f"    System.Console.WriteLine(System.Numerics.BitOperations.PopCount((uint)(x ^ y)){a});\n"
        "} }\n"
    )


def _perl_hamdist(wrong):
    # Perl's ^ does STRING (byte-wise) xor on operands that have never been
    # used numerically -- values straight from split() are plain strings,
    # so force numeric context first or ^ silently xors ASCII bytes instead
    # of the integer values (real bug found via this batch's run).
    a = " + 1" if wrong else ""
    return (
        "my ($x, $y) = split ' ', do { local $/; <STDIN> };\n"
        "$x = $x + 0; $y = $y + 0;\n"
        "sub hamming_distance {\n"
        "    my ($x, $y) = @_;\n"
        "    my $v = ($x ^ $y) & 0xFFFFFFFF;\n"
        "    my $count = 0;\n"
        "    while ($v != 0) { $count += $v & 1; $v = $v >> 1; }\n"
        f"    return $count{a};\n"
        "}\n"
        "print hamming_distance($x, $y), \"\\n\";\n"
    )


def _c_hamdist(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n"
        f"int main() {{ int x,y; scanf(\"%d %d\",&x,&y); printf(\"%d\\n\", __builtin_popcount((unsigned int)(x ^ y)){a}); return 0; }}\n"
    )


def _rust_hamdist(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let x = it.next().unwrap(); let y = it.next().unwrap();\n"
        f"    println!(\"{{}}\", ((x ^ y) as u32).count_ones() as i32{a}); }}\n"
    )


# ── move-zeroes ──────────────────────────────────────────────────────────────
def _js_move_zeroes(wrong):
    op = "===" if wrong else "!=="
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function move_zeroes(nums) {\n"
        "    let j = 0;\n"
        f"    for (let i=0;i<nums.length;i++) {{ if (nums[i] {op} 0) {{ const t=nums[j]; nums[j]=nums[i]; nums[i]=t; j++; }} }}\n"
        "    return nums;\n"
        "}\n"
        "console.log(move_zeroes(nums).join(' '));\n"
    )


def _ts_move_zeroes(wrong):
    op = "===" if wrong else "!=="
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function move_zeroes(nums: number[]): number[] {\n"
        "    let j = 0;\n"
        f"    for (let i=0;i<nums.length;i++) {{ if (nums[i] {op} 0) {{ const t=nums[j]; nums[j]=nums[i]; nums[i]=t; j++; }} }}\n"
        "    return nums;\n"
        "}\n"
        "console.log(move_zeroes(nums).join(' '));\n"
    )


def _java_move_zeroes(wrong):
    op = "==" if wrong else "!="
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    move_zeroes(nums);\n"
        "    StringBuilder sb = new StringBuilder(); for (int i=0;i<n;i++) { if (i>0) sb.append(' '); sb.append(nums[i]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static void move_zeroes(int[] nums) {\n"
        "    int j = 0;\n"
        f"    for (int i=0;i<nums.length;i++) {{ if (nums[i] {op} 0) {{ int t=nums[j]; nums[j]=nums[i]; nums[i]=t; j++; }} }}\n"
        "} }\n"
    )


def _cpp_move_zeroes(wrong):
    op = "==" if wrong else "!="
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "void move_zeroes(vector<int>& nums) {\n"
        "    int j = 0;\n"
        f"    for (int i=0;i<(int)nums.size();i++) {{ if (nums[i] {op} 0) {{ swap(nums[j], nums[i]); j++; }} }}\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i];\n"
        "    move_zeroes(nums);\n"
        "    for (int i=0;i<n;i++) { if (i) cout<<' '; cout<<nums[i]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_move_zeroes(wrong):
    op = "==" if wrong else "!="
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    move_zeroes(nums);\n"
        "    System.Console.WriteLine(string.Join(\" \", nums));\n"
        "}\n"
        "static void move_zeroes(int[] nums) {\n"
        "    int j = 0;\n"
        f"    for (int i=0;i<nums.Length;i++) {{ if (nums[i] {op} 0) {{ int t=nums[j]; nums[j]=nums[i]; nums[i]=t; j++; }} }}\n"
        "} }\n"
    )


def _perl_move_zeroes(wrong):
    op = "==" if wrong else "!="
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "my $j = 0;\n"
        f"for (my $i=0;$i<$n;$i++) {{ if ($nums[$i] {op} 0) {{ my $t=$nums[$j]; $nums[$j]=$nums[$i]; $nums[$i]=$t; $j++; }} }}\n"
        "print join(' ', @nums), \"\\n\";\n"
    )


def _c_move_zeroes(wrong):
    op = "==" if wrong else "!="
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "void move_zeroes(int* nums, int n) {\n"
        "    int j = 0;\n"
        f"    for (int i=0;i<n;i++) {{ if (nums[i] {op} 0) {{ int t=nums[j]; nums[j]=nums[i]; nums[i]=t; j++; }} }}\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1));\n"
        "    for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]);\n"
        "    move_zeroes(nums, n);\n"
        "    for (int i=0;i<n;i++) { if (i) printf(\" \"); printf(\"%d\", nums[i]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_move_zeroes(wrong):
    op = "== 0" if wrong else "!= 0"
    return (
        "use std::io::Read;\n"
        "fn move_zeroes(nums: &mut Vec<i32>) {\n"
        "    let mut j = 0;\n"
        f"    for i in 0..nums.len() {{ if nums[i] {op} {{ nums.swap(i, j); j += 1; }} }}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let mut nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    move_zeroes(&mut nums);\n"
        "    let strs: Vec<String> = nums.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \")); }\n"
    )


# ── majority-element ─────────────────────────────────────────────────────────
def _js_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function majority_element(nums) {\n"
        "    let count = 0, candidate = 0;\n"
        "    for (const x of nums) { if (count === 0) candidate = x; count += (x === candidate) ? 1 : -1; }\n"
        f"    return candidate{a};\n"
        "}\n"
        "console.log(majority_element(nums));\n"
    )


def _ts_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function majority_element(nums: number[]): number {\n"
        "    let count = 0, candidate = 0;\n"
        "    for (const x of nums) { if (count === 0) candidate = x; count += (x === candidate) ? 1 : -1; }\n"
        f"    return candidate{a};\n"
        "}\n"
        "console.log(majority_element(nums));\n"
    )


def _java_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(majority_element(nums));\n"
        "}\n"
        "static int majority_element(int[] nums) {\n"
        "    int count=0, candidate=0;\n"
        "    for (int x: nums) { if (count==0) candidate=x; count += (x==candidate) ? 1 : -1; }\n"
        f"    return candidate{a};\n"
        "} }\n"
    )


def _cpp_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "int majority_element(vector<int>& nums) {\n"
        "    int count=0, candidate=0;\n"
        "    for (int x: nums) { if (count==0) candidate=x; count += (x==candidate) ? 1 : -1; }\n"
        f"    return candidate{a};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << majority_element(nums) << endl; return 0; }\n"
    )


def _csharp_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(majority_element(nums));\n"
        "}\n"
        "static int majority_element(int[] nums) {\n"
        "    int count=0, candidate=0;\n"
        "    foreach (int x in nums) { if (count==0) candidate=x; count += (x==candidate) ? 1 : -1; }\n"
        f"    return candidate{a};\n"
        "} }\n"
    )


def _perl_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub majority_element {\n"
        "    my ($nums) = @_;\n"
        "    my $count = 0; my $candidate = 0;\n"
        "    foreach my $x (@$nums) { if ($count == 0) { $candidate = $x; } $count += ($x == $candidate) ? 1 : -1; }\n"
        f"    return $candidate{a};\n"
        "}\n"
        "print majority_element(\\@nums), \"\\n\";\n"
    )


def _c_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int majority_element(int* nums, int n) {\n"
        "    int count=0, candidate=0;\n"
        "    for (int i=0;i<n;i++) { if (count==0) candidate=nums[i]; count += (nums[i]==candidate) ? 1 : -1; }\n"
        f"    return candidate{a};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); printf(\"%d\\n\", majority_element(nums,n)); return 0; }\n"
    )


def _rust_majority(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn majority_element(nums: &Vec<i32>) -> i32 {\n"
        "    let mut count = 0; let mut candidate = 0;\n"
        "    for x in nums.iter() { if count == 0 { candidate = *x; } count += if *x == candidate { 1 } else { -1 }; }\n"
        f"    candidate{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", majority_element(&nums)); }\n"
    )


_BUILDERS = {
    "valid-parentheses": {"javascript": _js_valid_paren, "typescript": _ts_valid_paren, "java": _java_valid_paren, "cpp": _cpp_valid_paren,
                          "csharp": _csharp_valid_paren, "perl": _perl_valid_paren, "c": _c_valid_paren, "rust": _rust_valid_paren},
    "valid-anagram": {"javascript": _js_valid_anagram, "typescript": _ts_valid_anagram, "java": _java_valid_anagram, "cpp": _cpp_valid_anagram,
                      "csharp": _csharp_valid_anagram, "perl": _perl_valid_anagram, "c": _c_valid_anagram, "rust": _rust_valid_anagram},
    "missing-number": {"javascript": _js_missing, "typescript": _ts_missing, "java": _java_missing, "cpp": _cpp_missing,
                       "csharp": _csharp_missing, "perl": _perl_missing, "c": _c_missing, "rust": _rust_missing},
    "single-number": {"javascript": _js_single, "typescript": _ts_single, "java": _java_single, "cpp": _cpp_single,
                      "csharp": _csharp_single, "perl": _perl_single, "c": _c_single, "rust": _rust_single},
    "number-of-1-bits": {"javascript": _js_popcount, "typescript": _ts_popcount, "java": _java_popcount, "cpp": _cpp_popcount,
                         "csharp": _csharp_popcount, "perl": _perl_popcount, "c": _c_popcount, "rust": _rust_popcount},
    "power-of-two": {"javascript": _js_pow2, "typescript": _ts_pow2, "java": _java_pow2, "cpp": _cpp_pow2,
                     "csharp": _csharp_pow2, "perl": _perl_pow2, "c": _c_pow2, "rust": _rust_pow2},
    "hamming-distance": {"javascript": _js_hamdist, "typescript": _ts_hamdist, "java": _java_hamdist, "cpp": _cpp_hamdist,
                         "csharp": _csharp_hamdist, "perl": _perl_hamdist, "c": _c_hamdist, "rust": _rust_hamdist},
    "move-zeroes": {"javascript": _js_move_zeroes, "typescript": _ts_move_zeroes, "java": _java_move_zeroes, "cpp": _cpp_move_zeroes,
                    "csharp": _csharp_move_zeroes, "perl": _perl_move_zeroes, "c": _c_move_zeroes, "rust": _rust_move_zeroes},
    "majority-element": {"javascript": _js_majority, "typescript": _ts_majority, "java": _java_majority, "cpp": _cpp_majority,
                         "csharp": _csharp_majority, "perl": _perl_majority, "c": _c_majority, "rust": _rust_majority},
}


def load_cases(con, pid):
    cur = con.execute(
        "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = [SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                         is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
    row = con.execute("SELECT test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    return cases, row["test_suite_version"]


async def verify_one(pid, lang, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate(build(False), lang, cases)
    if correct_result.tests_passed != correct_result.tests_total:
        sample_fail = next((r for r in correct_result.test_results if not r.passed), None)
        return {"pid": pid, "lang": lang, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:150]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:150]} "
                          f"actual={(sample_fail.actual_output if sample_fail else '')[:80]!r} "
                          f"expected={(sample_fail.expected_output if sample_fail else '')[:80]!r}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate(build(True), lang, cases)
    if wrong_result.tests_passed >= wrong_result.tests_total:
        return {"pid": pid, "lang": lang, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {wrong_result.tests_total}",
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
    skipped = 0
    for pid, builders in _BUILDERS.items():
        for lang in _TARGET_LANGUAGES:
            cases, tsv = load_cases(con, pid)
            if ledger.already_verified(con, pid, lang, "program", test_suite_version=tsv):
                skipped += 1
                continue
            r = await verify_one(pid, lang, cases, builders[lang])
            results.append(r)
            status = "PASS" if r["outcome"] == "verified" else "FAIL"
            print(f"[{status}] {lang:10s}(program) {pid:20s} {r['outcome']:18s} {r['detail'][:120]}", flush=True)
            if r["outcome"] == "verified":
                row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
                sc = json.loads(row["starter_code"])
                sc[lang] = builders[lang](False)
                con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
                con.commit()
                ledger.record_cell(con, problem_id=pid, language=lang, mode="program",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-program-bit-misc-v1", test_suite_version=tsv,
                    duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped: {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
