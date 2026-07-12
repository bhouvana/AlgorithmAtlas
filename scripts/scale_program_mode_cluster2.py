"""Extends Program Mode to the 11 problems already proven in Function Mode
this session (gcd-euclidean, house-robber, word-break, longest-increasing-
subsequence, longest-common-subsequence, edit-distance, minimum-path-sum,
n-queens, graph-bfs, dijkstra-shortest-path, kmp-string-matching) across
the 8 working languages. Same core algorithms as the Function Mode
versions -- only the stdin-parsing/stdout-formatting boilerplate is new,
each confirmed against the EXISTING Python starter_code before writing
(read directly, not assumed):
  - gcd-euclidean: "a b" -> print int
  - house-robber: "n" then n ints -> print int
  - word-break: line1=s, line2=space-separated dict words -> print true/false
  - lis: "n" then n ints -> print int
  - lcs: whitespace-split tokens s1, s2 (no internal whitespace) -> print int
  - edit-distance: 2 lines w1, w2 -> print int
  - minimum-path-sum: "m n" then m*n row-major ints -> print int
  - n-queens: single int -> print int
  - graph-bfs: "n m src" then m undirected edges "u v" -> print space-joined dist
  - dijkstra: "n m" then m directed weighted edges "u v w" -> print space-joined dist
  - kmp-string-matching: 2 lines T, P -> print space-joined result, or "-1" if empty
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


# ── gcd-euclidean ────────────────────────────────────────────────────────────
def _js_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "const [a0,b0] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "function gcd(a, b) { a=Math.abs(a); b=Math.abs(b); while (b!==0) { const t=b; b=a%b; a=t; } "
        f"return a{a}; }}\n"
        "console.log(gcd(a0, b0));\n"
    )


def _ts_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "const [a0,b0]: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "function gcd(a: number, b: number): number { a=Math.abs(a); b=Math.abs(b); while (b!==0) { const t=b; b=a%b; a=t; } "
        f"return a{a}; }}\n"
        "console.log(gcd(a0, b0));\n"
    )


def _java_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int a = sc.nextInt(); int b = sc.nextInt();\n"
        "    System.out.println(gcd(a,b));\n"
        "}\n"
        "static int gcd(int a, int b) { a=Math.abs(a); b=Math.abs(b); while (b!=0) { int t=b; b=a%b; a=t; } "
        f"return a{a}; }} }}\n"
    )


def _cpp_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <cstdlib>\nusing namespace std;\n"
        "int gcd(int a, int b) { a=abs(a); b=abs(b); while (b!=0) { int t=b; b=a%b; a=t; } "
        f"return a{a}; }}\n"
        "int main() { int a,b; cin>>a>>b; cout << gcd(a,b) << endl; return 0; }\n"
    )


def _csharp_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t2 = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int a = int.Parse(t2[0]); int b = int.Parse(t2[1]);\n"
        "    System.Console.WriteLine(gcd(a,b));\n"
        "}\n"
        "static int gcd(int a, int b) { a=System.Math.Abs(a); b=System.Math.Abs(b); while (b!=0) { int t=b; b=a%b; a=t; } "
        f"return a{a}; }} }}\n"
    )


def _perl_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "my ($a, $b) = split ' ', do { local $/; <STDIN> };\n"
        "sub gcd { my ($a,$b)=@_; $a=abs($a); $b=abs($b); while ($b!=0) { my $t=$b; $b=$a%$b; $a=$t; } "
        f"return $a{a}; }}\n"
        "print gcd($a, $b), \"\\n\";\n"
    )


def _c_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n"
        "int gcd(int a, int b) { a=a<0?-a:a; b=b<0?-b:b; while (b!=0) { int t=b; b=a%b; a=t; } "
        f"return a{a}; }}\n"
        "int main() { int a,b; scanf(\"%d %d\", &a, &b); printf(\"%d\\n\", gcd(a,b)); return 0; }\n"
    )


def _rust_gcd(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn gcd(a: i32, b: i32) -> i32 { let mut a=a.abs(); let mut b=b.abs(); while b!=0 { let t=b; b=a%b; a=t; } "
        f"a{a} }}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let a = it.next().unwrap(); let b = it.next().unwrap();\n"
        "    println!(\"{}\", gcd(a,b)); }\n"
    )


# ── house-robber ─────────────────────────────────────────────────────────────
def _js_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function rob(nums) { let prev=0,cur=0; for (const x of nums) { const t=Math.max(cur,prev+x); prev=cur; cur=t; } "
        f"return cur{a}; }}\n"
        "console.log(rob(nums));\n"
    )


def _ts_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function rob(nums: number[]): number { let prev=0,cur=0; for (const x of nums) { const t=Math.max(cur,prev+x); prev=cur; cur=t; } "
        f"return cur{a}; }}\n"
        "console.log(rob(nums));\n"
    )


def _java_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n];\n"
        "    for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(rob(nums));\n"
        "}\n"
        "static int rob(int[] nums) { int prev=0,cur=0; for (int x: nums) { int t=Math.max(cur,prev+x); prev=cur; cur=t; } "
        f"return cur{a}; }} }}\n"
    )


def _cpp_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"
        "int rob(vector<int>& nums) { int prev=0,cur=0; for (int x: nums) { int t=max(cur,prev+x); prev=cur; cur=t; } "
        f"return cur{a}; }}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << rob(nums) << endl; return 0; }\n"
    )


def _csharp_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n = int.Parse(t[idx++]); int[] nums = new int[n];\n"
        "    for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(rob(nums));\n"
        "}\n"
        "static int rob(int[] nums) { int prev=0,cur=0; foreach (int x in nums) { int t=System.Math.Max(cur,prev+x); prev=cur; cur=t; } "
        f"return cur{a}; }} }}\n"
    )


def _perl_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub rob { my ($nums)=@_; my $prev=0; my $cur=0; foreach my $x (@$nums) { my $t=($cur>$prev+$x)?$cur:$prev+$x; $prev=$cur; $cur=$t; } "
        f"return $cur{a}; }}\n"
        "print rob(\\@nums), \"\\n\";\n"
    )


def _c_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int rob(int* nums, int n) { int prev=0,cur=0; for (int i=0;i<n;i++) { int wc=prev+nums[i]; int t=cur>wc?cur:wc; prev=cur; cur=t; } "
        f"return cur{a}; }}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); "
        "printf(\"%d\\n\", rob(nums, n)); return 0; }\n"
    )


def _rust_rob(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn rob(nums: &Vec<i32>) -> i32 { let mut prev=0; let mut cur=0; for x in nums.iter() { let t=cur.max(prev+x); prev=cur; cur=t; } "
        f"cur{a} }}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", rob(&nums)); }\n"
    )


# ── word-break ───────────────────────────────────────────────────────────────
def _js_word_break(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const s = lines[0]; const word_dict = lines[1].trim().split(/\\s+/);\n"
        "function word_break(s, word_dict) {\n"
        "    const dict = new Set(word_dict); const n = s.length;\n"
        "    const dp = new Array(n+1).fill(false); dp[0]=true;\n"
        "    for (let i=1;i<=n;i++) for (let j=0;j<i;j++) if (dp[j] && dict.has(s.substring(j,i))) { dp[i]=true; break; }\n"
        f"    return {ret};\n"
        "}\n"
        "console.log(word_break(s, word_dict) ? 'true' : 'false');\n"
    )


def _ts_word_break(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const s: string = lines[0]; const word_dict: string[] = lines[1].trim().split(/\\s+/);\n"
        "function word_break(s: string, word_dict: string[]): boolean {\n"
        "    const dict = new Set(word_dict); const n = s.length;\n"
        "    const dp: boolean[] = new Array(n+1).fill(false); dp[0]=true;\n"
        "    for (let i=1;i<=n;i++) for (let j=0;j<i;j++) if (dp[j] && dict.has(s.substring(j,i))) { dp[i]=true; break; }\n"
        f"    return {ret};\n"
        "}\n"
        "console.log(word_break(s, word_dict) ? 'true' : 'false');\n"
    )


def _java_word_break(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (
        "import java.util.*;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    String s = sc.nextLine();\n"
        "    String[] word_dict = sc.nextLine().trim().split(\"\\\\s+\");\n"
        "    System.out.println(word_break(s, word_dict) ? \"true\" : \"false\");\n"
        "}\n"
        "static boolean word_break(String s, String[] word_dict) {\n"
        "    Set<String> dict = new HashSet<>(Arrays.asList(word_dict));\n"
        "    int n = s.length(); boolean[] dp = new boolean[n+1]; dp[0]=true;\n"
        "    for (int i=1;i<=n;i++) for (int j=0;j<i;j++) if (dp[j] && dict.contains(s.substring(j,i))) { dp[i]=true; break; }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _cpp_word_break(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (
        "#include <iostream>\n#include <vector>\n#include <string>\n#include <unordered_set>\n#include <sstream>\nusing namespace std;\n"
        "bool word_break(string s, vector<string> word_dict) {\n"
        "    unordered_set<string> dict(word_dict.begin(), word_dict.end());\n"
        "    int n = s.size(); vector<bool> dp(n+1, false); dp[0]=true;\n"
        "    for (int i=1;i<=n;i++) for (int j=0;j<i;j++) if (dp[j] && dict.count(s.substr(j,i-j))) { dp[i]=true; break; }\n"
        f"    return {ret};\n"
        "}\n"
        "int main() {\n"
        "    string s; getline(cin, s);\n"
        "    string line2; getline(cin, line2);\n"
        "    vector<string> word_dict; istringstream ss(line2); string w;\n"
        "    while (ss >> w) word_dict.push_back(w);\n"
        "    cout << (word_break(s, word_dict) ? \"true\" : \"false\") << endl;\n"
        "    return 0;\n"
        "}\n"
    )


def _csharp_word_break(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (
        "class Program { static void Main() {\n"
        "    string s = System.Console.In.ReadLine();\n"
        "    string[] word_dict = System.Console.In.ReadLine().Trim().Split(new char[]{' '}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    System.Console.WriteLine(word_break(s, word_dict) ? \"true\" : \"false\");\n"
        "}\n"
        "static bool word_break(string s, string[] word_dict) {\n"
        "    var dict = new System.Collections.Generic.HashSet<string>(word_dict);\n"
        "    int n = s.Length; bool[] dp = new bool[n+1]; dp[0]=true;\n"
        "    for (int i=1;i<=n;i++) for (int j=0;j<i;j++) if (dp[j] && dict.Contains(s.Substring(j,i-j))) { dp[i]=true; break; }\n"
        f"    return {ret};\n"
        "} }\n"
    )


def _perl_word_break(wrong):
    ret = "!$dp[$n]" if wrong else "$dp[$n]"
    return (
        "my @lines = split /\\n/, do { local $/; <STDIN> };\n"
        "my $s = $lines[0];\n"
        "my @word_dict = split ' ', $lines[1];\n"
        "sub word_break {\n"
        "    my ($s, $word_dict) = @_;\n"
        "    my %dict = map { $_ => 1 } @$word_dict;\n"
        "    my $n = length($s); my @dp = (0) x ($n+1); $dp[0] = 1;\n"
        "    for (my $i=1;$i<=$n;$i++) { for (my $j=0;$j<$i;$j++) { if ($dp[$j] && exists $dict{substr($s,$j,$i-$j)}) { $dp[$i]=1; last; } } }\n"
        f"    return {ret};\n"
        "}\n"
        "print word_break($s, \\@word_dict) ? \"true\\n\" : \"false\\n\";\n"
    )


def _c_word_break(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
        "int word_break(char* s, char** words, int wc) {\n"
        "    int n = strlen(s);\n"
        "    int* dp = (int*)calloc(n+1, sizeof(int)); dp[0]=1;\n"
        "    for (int i=1;i<=n;i++) {\n"
        "        for (int j=0;j<i;j++) {\n"
        "            if (!dp[j]) continue;\n"
        "            int len = i-j;\n"
        "            for (int w=0;w<wc;w++) {\n"
        "                if ((int)strlen(words[w]) == len && strncmp(s+j, words[w], len) == 0) { dp[i]=1; break; }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        f"    int result = {ret};\n"
        "    free(dp);\n"
        "    return result;\n"
        "}\n"
        "int main() {\n"
        "    char s[10001]; fgets(s, sizeof(s), stdin);\n"
        "    s[strcspn(s, \"\\r\\n\")] = 0;\n"
        "    char line2[10001]; fgets(line2, sizeof(line2), stdin);\n"
        "    char* words[2000]; int wc = 0;\n"
        "    char* tok = strtok(line2, \" \\r\\n\");\n"
        "    while (tok) { words[wc++] = tok; tok = strtok(NULL, \" \\r\\n\"); }\n"
        "    printf(\"%s\\n\", word_break(s, words, wc) ? \"true\" : \"false\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_word_break(wrong):
    ret = "!dp[n]" if wrong else "dp[n]"
    return (
        "use std::io::{self, BufRead};\nuse std::collections::HashSet;\n"
        "fn word_break(s: String, word_dict: Vec<String>) -> bool {\n"
        "    let dict: HashSet<String> = word_dict.into_iter().collect();\n"
        "    let chars: Vec<char> = s.chars().collect(); let n = chars.len();\n"
        "    let mut dp = vec![false; n+1]; dp[0] = true;\n"
        "    for i in 1..=n { for j in 0..i { if dp[j] { let sub: String = chars[j..i].iter().collect(); if dict.contains(&sub) { dp[i]=true; break; } } } }\n"
        f"    {ret}\n"
        "}\n"
        "fn main() {\n"
        "    let stdin = io::stdin();\n"
        "    let mut lines = stdin.lock().lines();\n"
        "    let s = lines.next().unwrap().unwrap();\n"
        "    let l2 = lines.next().unwrap().unwrap();\n"
        "    let word_dict: Vec<String> = l2.split_whitespace().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", if word_break(s, word_dict) { \"true\" } else { \"false\" });\n"
        "}\n"
    )


# ── longest-increasing-subsequence ───────────────────────────────────────────
def _js_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function lis(nums) {\n"
        "    const tails = [];\n"
        "    for (const x of nums) { let lo=0,hi=tails.length; while(lo<hi){const mid=(lo+hi)>>1; if(tails[mid]<x)lo=mid+1;else hi=mid;} "
        "if(lo===tails.length)tails.push(x);else tails[lo]=x; }\n"
        f"    return tails.length{a};\n"
        "}\n"
        "console.log(lis(nums));\n"
    )


def _ts_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const n = data[0]; const nums = data.slice(1,1+n);\n"
        "function lis(nums: number[]): number {\n"
        "    const tails: number[] = [];\n"
        "    for (const x of nums) { let lo=0,hi=tails.length; while(lo<hi){const mid=(lo+hi)>>1; if(tails[mid]<x)lo=mid+1;else hi=mid;} "
        "if(lo===tails.length)tails.push(x);else tails[lo]=x; }\n"
        f"    return tails.length{a};\n"
        "}\n"
        "console.log(lis(nums));\n"
    )


def _java_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n = sc.nextInt(); int[] nums = new int[n]; for (int i=0;i<n;i++) nums[i]=sc.nextInt();\n"
        "    System.out.println(lis(nums));\n"
        "}\n"
        "static int lis(int[] nums) {\n"
        "    int[] tails = new int[nums.length]; int size=0;\n"
        "    for (int x: nums) { int lo=0,hi=size; while(lo<hi){int mid=(lo+hi)/2; if(tails[mid]<x)lo=mid+1;else hi=mid;} tails[lo]=x; if(lo==size)size++; }\n"
        f"    return size{a};\n"
        "} }\n"
    )


def _cpp_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"
        "int lis(vector<int>& nums) {\n"
        "    vector<int> tails;\n"
        "    for (int x: nums) { auto it=lower_bound(tails.begin(),tails.end(),x); if(it==tails.end())tails.push_back(x);else *it=x; }\n"
        f"    return (int)tails.size(){a};\n"
        "}\n"
        "int main() { int n; cin>>n; vector<int> nums(n); for (int i=0;i<n;i++) cin>>nums[i]; cout << lis(nums) << endl; return 0; }\n"
    )


def _csharp_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int[] nums=new int[n]; for (int i=0;i<n;i++) nums[i]=int.Parse(t[idx++]);\n"
        "    System.Console.WriteLine(lis(nums));\n"
        "}\n"
        "static int lis(int[] nums) {\n"
        "    var tails = new System.Collections.Generic.List<int>();\n"
        "    foreach (int x in nums) { int lo=0,hi=tails.Count; while(lo<hi){int mid=(lo+hi)/2; if(tails[mid]<x)lo=mid+1;else hi=mid;} if(lo==tails.Count)tails.Add(x);else tails[lo]=x; }\n"
        f"    return tails.Count{a};\n"
        "} }\n"
    )


def _perl_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my @nums = @data[0..$n-1];\n"
        "sub lis {\n"
        "    my ($nums) = @_; my @tails;\n"
        "    foreach my $x (@$nums) { my $lo=0; my $hi=scalar(@tails); while($lo<$hi){my $mid=int(($lo+$hi)/2); if($tails[$mid]<$x){$lo=$mid+1;}else{$hi=$mid;}} $tails[$lo]=$x; }\n"
        f"    return scalar(@tails){a};\n"
        "}\n"
        "print lis(\\@nums), \"\\n\";\n"
    )


def _c_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int lis(int* nums, int n) {\n"
        "    int* tails = (int*)malloc(sizeof(int)*(n>0?n:1)); int size=0;\n"
        "    for (int k=0;k<n;k++) { int x=nums[k]; int lo=0,hi=size; while(lo<hi){int mid=(lo+hi)/2; if(tails[mid]<x)lo=mid+1;else hi=mid;} tails[lo]=x; if(lo==size)size++; }\n"
        "    free(tails);\n"
        f"    return size{a};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); int* nums=(int*)malloc(sizeof(int)*(n>0?n:1)); for (int i=0;i<n;i++) scanf(\"%d\",&nums[i]); printf(\"%d\\n\", lis(nums,n)); return 0; }\n"
    )


def _rust_lis(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn lis(nums: Vec<i32>) -> i32 {\n"
        "    let mut tails: Vec<i32> = Vec::new();\n"
        "    for x in nums.iter() { let pos = tails.partition_point(|&t| t < *x); if pos==tails.len() { tails.push(*x); } else { tails[pos]=*x; } }\n"
        f"    tails.len() as i32{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let nums: Vec<i32> = (0..n).map(|_| it.next().unwrap()).collect();\n"
        "    println!(\"{}\", lis(nums)); }\n"
    )


# ── longest-common-subsequence ───────────────────────────────────────────────
def _js_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "const [s1, s2] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/);\n"
        "function lcs(s1, s2) {\n"
        "    const n=s1.length, m=s2.length;\n"
        "    const dp = Array.from({length:n+1}, () => new Array(m+1).fill(0));\n"
        "    for (let i=1;i<=n;i++) for (let j=1;j<=m;j++) { if (s1[i-1]===s2[j-1]) dp[i][j]=dp[i-1][j-1]+1; else dp[i][j]=Math.max(dp[i-1][j],dp[i][j-1]); }\n"
        f"    return dp[n][m]{a};\n"
        "}\n"
        "console.log(lcs(s1, s2));\n"
    )


def _ts_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "const [s1, s2]: string[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/);\n"
        "function lcs(s1: string, s2: string): number {\n"
        "    const n=s1.length, m=s2.length;\n"
        "    const dp: number[][] = Array.from({length:n+1}, () => new Array(m+1).fill(0));\n"
        "    for (let i=1;i<=n;i++) for (let j=1;j<=m;j++) { if (s1[i-1]===s2[j-1]) dp[i][j]=dp[i-1][j-1]+1; else dp[i][j]=Math.max(dp[i-1][j],dp[i][j-1]); }\n"
        f"    return dp[n][m]{a};\n"
        "}\n"
        "console.log(lcs(s1, s2));\n"
    )


def _java_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    String s1 = sc.next(); String s2 = sc.next();\n"
        "    System.out.println(lcs(s1, s2));\n"
        "}\n"
        "static int lcs(String s1, String s2) {\n"
        "    int n=s1.length(), m=s2.length(); int[][] dp = new int[n+1][m+1];\n"
        "    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) { if (s1.charAt(i-1)==s2.charAt(j-1)) dp[i][j]=dp[i-1][j-1]+1; else dp[i][j]=Math.max(dp[i-1][j],dp[i][j-1]); }\n"
        f"    return dp[n][m]{a};\n"
        "} }\n"
    )


def _cpp_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <string>\n#include <algorithm>\nusing namespace std;\n"
        "int lcs(string s1, string s2) {\n"
        "    int n=s1.size(), m=s2.size(); vector<vector<int>> dp(n+1, vector<int>(m+1, 0));\n"
        "    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) { if (s1[i-1]==s2[j-1]) dp[i][j]=dp[i-1][j-1]+1; else dp[i][j]=max(dp[i-1][j],dp[i][j-1]); }\n"
        f"    return dp[n][m]{a};\n"
        "}\n"
        "int main() { string s1,s2; cin>>s1>>s2; cout << lcs(s1,s2) << endl; return 0; }\n"
    )


def _csharp_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    string s1 = t[0]; string s2 = t[1];\n"
        "    System.Console.WriteLine(lcs(s1, s2));\n"
        "}\n"
        "static int lcs(string s1, string s2) {\n"
        "    int n=s1.Length, m=s2.Length; int[,] dp = new int[n+1,m+1];\n"
        "    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) { if (s1[i-1]==s2[j-1]) dp[i,j]=dp[i-1,j-1]+1; else dp[i,j]=System.Math.Max(dp[i-1,j],dp[i,j-1]); }\n"
        f"    return dp[n,m]{a};\n"
        "} }\n"
    )


def _perl_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "my ($s1, $s2) = split ' ', do { local $/; <STDIN> };\n"
        "sub lcs {\n"
        "    my ($s1, $s2) = @_; my $n=length($s1); my $m=length($s2);\n"
        "    my @dp; for my $i (0..$n) { for my $j (0..$m) { $dp[$i][$j]=0; } }\n"
        "    for (my $i=1;$i<=$n;$i++) { for (my $j=1;$j<=$m;$j++) {\n"
        "        if (substr($s1,$i-1,1) eq substr($s2,$j-1,1)) { $dp[$i][$j]=$dp[$i-1][$j-1]+1; }\n"
        "        else { $dp[$i][$j]=($dp[$i-1][$j]>$dp[$i][$j-1])?$dp[$i-1][$j]:$dp[$i][$j-1]; }\n"
        "    } }\n"
        f"    return $dp[$n][$m]{a};\n"
        "}\n"
        "print lcs($s1, $s2), \"\\n\";\n"
    )


def _c_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int lcs(char* s1, char* s2) {\n"
        "    int n=0; while(s1[n])n++; int m=0; while(s2[m])m++;\n"
        "    int** dp = (int**)malloc(sizeof(int*)*(n+1)); for (int i=0;i<=n;i++) dp[i]=(int*)calloc(m+1,sizeof(int));\n"
        "    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) { if (s1[i-1]==s2[j-1]) dp[i][j]=dp[i-1][j-1]+1; else dp[i][j]=dp[i-1][j]>dp[i][j-1]?dp[i-1][j]:dp[i][j-1]; }\n"
        f"    int result = dp[n][m]{a};\n"
        "    for (int i=0;i<=n;i++) free(dp[i]); free(dp);\n"
        "    return result;\n"
        "}\n"
        "int main() { char s1[4001], s2[4001]; scanf(\"%s %s\", s1, s2); printf(\"%d\\n\", lcs(s1, s2)); return 0; }\n"
    )


def _rust_lcs(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn lcs(s1: &str, s2: &str) -> i32 {\n"
        "    let a: Vec<char> = s1.chars().collect(); let b: Vec<char> = s2.chars().collect();\n"
        "    let n=a.len(); let m=b.len(); let mut dp = vec![vec![0i32; m+1]; n+1];\n"
        "    for i in 1..=n { for j in 1..=m { if a[i-1]==b[j-1] { dp[i][j]=dp[i-1][j-1]+1; } else { dp[i][j]=dp[i-1][j].max(dp[i][j-1]); } } }\n"
        f"    dp[n][m]{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace(); let s1 = it.next().unwrap(); let s2 = it.next().unwrap();\n"
        "    println!(\"{}\", lcs(s1, s2)); }\n"
    )


# ── edit-distance ────────────────────────────────────────────────────────────
def _js_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const w1 = lines[0], w2 = lines[1];\n"
        "function edit_distance(w1, w2) {\n"
        "    const n=w1.length, m=w2.length;\n"
        "    const dp = Array.from({length:n+1}, () => new Array(m+1).fill(0));\n"
        "    for (let i=0;i<=n;i++) dp[i][0]=i; for (let j=0;j<=m;j++) dp[0][j]=j;\n"
        "    for (let i=1;i<=n;i++) for (let j=1;j<=m;j++) { if (w1[i-1]===w2[j-1]) dp[i][j]=dp[i-1][j-1]; else dp[i][j]=1+Math.min(dp[i-1][j],dp[i][j-1],dp[i-1][j-1]); }\n"
        f"    return dp[n][m]{a};\n"
        "}\n"
        "console.log(edit_distance(w1, w2));\n"
    )


def _ts_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const w1: string = lines[0], w2: string = lines[1];\n"
        "function edit_distance(w1: string, w2: string): number {\n"
        "    const n=w1.length, m=w2.length;\n"
        "    const dp: number[][] = Array.from({length:n+1}, () => new Array(m+1).fill(0));\n"
        "    for (let i=0;i<=n;i++) dp[i][0]=i; for (let j=0;j<=m;j++) dp[0][j]=j;\n"
        "    for (let i=1;i<=n;i++) for (let j=1;j<=m;j++) { if (w1[i-1]===w2[j-1]) dp[i][j]=dp[i-1][j-1]; else dp[i][j]=1+Math.min(dp[i-1][j],dp[i][j-1],dp[i-1][j-1]); }\n"
        f"    return dp[n][m]{a};\n"
        "}\n"
        "console.log(edit_distance(w1, w2));\n"
    )


def _java_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    String w1 = sc.nextLine(); String w2 = sc.nextLine();\n"
        "    System.out.println(edit_distance(w1, w2));\n"
        "}\n"
        "static int edit_distance(String w1, String w2) {\n"
        "    int n=w1.length(), m=w2.length(); int[][] dp = new int[n+1][m+1];\n"
        "    for (int i=0;i<=n;i++) dp[i][0]=i; for (int j=0;j<=m;j++) dp[0][j]=j;\n"
        "    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) { if (w1.charAt(i-1)==w2.charAt(j-1)) dp[i][j]=dp[i-1][j-1]; else dp[i][j]=1+Math.min(dp[i-1][j],Math.min(dp[i][j-1],dp[i-1][j-1])); }\n"
        f"    return dp[n][m]{a};\n"
        "} }\n"
    )


def _cpp_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <string>\n#include <algorithm>\nusing namespace std;\n"
        "int edit_distance(string w1, string w2) {\n"
        "    int n=w1.size(), m=w2.size(); vector<vector<int>> dp(n+1, vector<int>(m+1, 0));\n"
        "    for (int i=0;i<=n;i++) dp[i][0]=i; for (int j=0;j<=m;j++) dp[0][j]=j;\n"
        "    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) { if (w1[i-1]==w2[j-1]) dp[i][j]=dp[i-1][j-1]; else dp[i][j]=1+min({dp[i-1][j],dp[i][j-1],dp[i-1][j-1]}); }\n"
        f"    return dp[n][m]{a};\n"
        "}\n"
        "int main() { string w1, w2; getline(cin,w1); getline(cin,w2); cout << edit_distance(w1,w2) << endl; return 0; }\n"
    )


def _csharp_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    string w1 = System.Console.In.ReadLine(); string w2 = System.Console.In.ReadLine();\n"
        "    System.Console.WriteLine(edit_distance(w1, w2));\n"
        "}\n"
        "static int edit_distance(string w1, string w2) {\n"
        "    int n=w1.Length, m=w2.Length; int[,] dp = new int[n+1,m+1];\n"
        "    for (int i=0;i<=n;i++) dp[i,0]=i; for (int j=0;j<=m;j++) dp[0,j]=j;\n"
        "    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) { if (w1[i-1]==w2[j-1]) dp[i,j]=dp[i-1,j-1]; else dp[i,j]=1+System.Math.Min(dp[i-1,j],System.Math.Min(dp[i,j-1],dp[i-1,j-1])); }\n"
        f"    return dp[n,m]{a};\n"
        "} }\n"
    )


def _perl_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @lines = split /\\n/, do { local $/; <STDIN> };\n"
        "my $w1 = $lines[0]; my $w2 = $lines[1];\n"
        "sub edit_distance {\n"
        "    my ($w1, $w2) = @_; my $n=length($w1); my $m=length($w2);\n"
        "    my @dp; for my $i (0..$n) { $dp[$i][0]=$i; } for my $j (0..$m) { $dp[0][$j]=$j; }\n"
        "    for (my $i=1;$i<=$n;$i++) { for (my $j=1;$j<=$m;$j++) {\n"
        "        if (substr($w1,$i-1,1) eq substr($w2,$j-1,1)) { $dp[$i][$j]=$dp[$i-1][$j-1]; }\n"
        "        else { my $mn=$dp[$i-1][$j]; $mn=$dp[$i][$j-1] if $dp[$i][$j-1]<$mn; $mn=$dp[$i-1][$j-1] if $dp[$i-1][$j-1]<$mn; $dp[$i][$j]=1+$mn; }\n"
        "    } }\n"
        f"    return $dp[$n][$m]{a};\n"
        "}\n"
        "print edit_distance($w1, $w2), \"\\n\";\n"
    )


def _c_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
        "int edit_distance(char* w1, char* w2) {\n"
        "    int n=strlen(w1), m=strlen(w2);\n"
        "    int** dp = (int**)malloc(sizeof(int*)*(n+1)); for (int i=0;i<=n;i++) dp[i]=(int*)malloc(sizeof(int)*(m+1));\n"
        "    for (int i=0;i<=n;i++) dp[i][0]=i; for (int j=0;j<=m;j++) dp[0][j]=j;\n"
        "    for (int i=1;i<=n;i++) for (int j=1;j<=m;j++) {\n"
        "        if (w1[i-1]==w2[j-1]) dp[i][j]=dp[i-1][j-1];\n"
        "        else { int mn=dp[i-1][j]; if(dp[i][j-1]<mn)mn=dp[i][j-1]; if(dp[i-1][j-1]<mn)mn=dp[i-1][j-1]; dp[i][j]=1+mn; }\n"
        "    }\n"
        f"    int result = dp[n][m]{a};\n"
        "    for (int i=0;i<=n;i++) free(dp[i]); free(dp);\n"
        "    return result;\n"
        "}\n"
        "int main() { char w1[1001], w2[1001]; fgets(w1,sizeof(w1),stdin); w1[strcspn(w1,\"\\r\\n\")]=0; fgets(w2,sizeof(w2),stdin); w2[strcspn(w2,\"\\r\\n\")]=0; printf(\"%d\\n\", edit_distance(w1,w2)); return 0; }\n"
    )


def _rust_edit_distance(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::{self, BufRead};\n"
        "fn edit_distance(w1: &str, w2: &str) -> i32 {\n"
        "    let a: Vec<char> = w1.chars().collect(); let b: Vec<char> = w2.chars().collect();\n"
        "    let n=a.len(); let m=b.len(); let mut dp = vec![vec![0i32; m+1]; n+1];\n"
        "    for i in 0..=n { dp[i][0]=i as i32; } for j in 0..=m { dp[0][j]=j as i32; }\n"
        "    for i in 1..=n { for j in 1..=m {\n"
        "        if a[i-1]==b[j-1] { dp[i][j]=dp[i-1][j-1]; } else { dp[i][j]=1+dp[i-1][j].min(dp[i][j-1]).min(dp[i-1][j-1]); }\n"
        "    } }\n"
        f"    dp[n][m]{a}\n"
        "}\n"
        "fn main() { let stdin = io::stdin(); let mut lines = stdin.lock().lines();\n"
        "    let w1 = lines.next().unwrap().unwrap(); let w2 = lines.next().unwrap().unwrap();\n"
        "    println!(\"{}\", edit_distance(&w1, &w2)); }\n"
    )


# ── minimum-path-sum ─────────────────────────────────────────────────────────
def _js_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const m = data[0], n = data[1];\n"
        "const grid = []; let idx = 2;\n"
        "for (let i=0;i<m;i++) { grid.push(data.slice(idx, idx+n)); idx += n; }\n"
        "function min_path_sum(grid) {\n"
        "    const dp = Array.from({length:m}, () => new Array(n).fill(0)); dp[0][0]=grid[0][0];\n"
        "    for (let j=1;j<n;j++) dp[0][j]=dp[0][j-1]+grid[0][j];\n"
        "    for (let i=1;i<m;i++) dp[i][0]=dp[i-1][0]+grid[i][0];\n"
        "    for (let i=1;i<m;i++) for (let j=1;j<n;j++) dp[i][j]=grid[i][j]+Math.min(dp[i-1][j],dp[i][j-1]);\n"
        f"    return dp[m-1][n-1]{a};\n"
        "}\n"
        "console.log(min_path_sum(grid));\n"
    )


def _ts_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "const m = data[0], n = data[1];\n"
        "const grid: number[][] = []; let idx = 2;\n"
        "for (let i=0;i<m;i++) { grid.push(data.slice(idx, idx+n)); idx += n; }\n"
        "function min_path_sum(grid: number[][]): number {\n"
        "    const dp: number[][] = Array.from({length:m}, () => new Array(n).fill(0)); dp[0][0]=grid[0][0];\n"
        "    for (let j=1;j<n;j++) dp[0][j]=dp[0][j-1]+grid[0][j];\n"
        "    for (let i=1;i<m;i++) dp[i][0]=dp[i-1][0]+grid[i][0];\n"
        "    for (let i=1;i<m;i++) for (let j=1;j<n;j++) dp[i][j]=grid[i][j]+Math.min(dp[i-1][j],dp[i][j-1]);\n"
        f"    return dp[m-1][n-1]{a};\n"
        "}\n"
        "console.log(min_path_sum(grid));\n"
    )


def _java_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int m = sc.nextInt(), n = sc.nextInt();\n"
        "    int[][] grid = new int[m][n];\n"
        "    for (int i=0;i<m;i++) for (int j=0;j<n;j++) grid[i][j]=sc.nextInt();\n"
        "    System.out.println(min_path_sum(grid, m, n));\n"
        "}\n"
        "static int min_path_sum(int[][] grid, int m, int n) {\n"
        "    int[][] dp = new int[m][n]; dp[0][0]=grid[0][0];\n"
        "    for (int j=1;j<n;j++) dp[0][j]=dp[0][j-1]+grid[0][j];\n"
        "    for (int i=1;i<m;i++) dp[i][0]=dp[i-1][0]+grid[i][0];\n"
        "    for (int i=1;i<m;i++) for (int j=1;j<n;j++) dp[i][j]=grid[i][j]+Math.min(dp[i-1][j],dp[i][j-1]);\n"
        f"    return dp[m-1][n-1]{a};\n"
        "} }\n"
    )


def _cpp_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n"
        "int min_path_sum(vector<vector<int>>& grid, int m, int n) {\n"
        "    vector<vector<int>> dp(m, vector<int>(n, 0)); dp[0][0]=grid[0][0];\n"
        "    for (int j=1;j<n;j++) dp[0][j]=dp[0][j-1]+grid[0][j];\n"
        "    for (int i=1;i<m;i++) dp[i][0]=dp[i-1][0]+grid[i][0];\n"
        "    for (int i=1;i<m;i++) for (int j=1;j<n;j++) dp[i][j]=grid[i][j]+min(dp[i-1][j],dp[i][j-1]);\n"
        f"    return dp[m-1][n-1]{a};\n"
        "}\n"
        "int main() { int m,n; cin>>m>>n; vector<vector<int>> grid(m, vector<int>(n));\n"
        "    for (int i=0;i<m;i++) for (int j=0;j<n;j++) cin>>grid[i][j];\n"
        "    cout << min_path_sum(grid,m,n) << endl; return 0; }\n"
    )


def _csharp_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int m=int.Parse(t[idx++]); int n=int.Parse(t[idx++]);\n"
        "    int[][] grid = new int[m][];\n"
        "    for (int i=0;i<m;i++) { grid[i]=new int[n]; for (int j=0;j<n;j++) grid[i][j]=int.Parse(t[idx++]); }\n"
        "    System.Console.WriteLine(min_path_sum(grid, m, n));\n"
        "}\n"
        "static int min_path_sum(int[][] grid, int m, int n) {\n"
        "    int[,] dp = new int[m,n]; dp[0,0]=grid[0][0];\n"
        "    for (int j=1;j<n;j++) dp[0,j]=dp[0,j-1]+grid[0][j];\n"
        "    for (int i=1;i<m;i++) dp[i,0]=dp[i-1,0]+grid[i][0];\n"
        "    for (int i=1;i<m;i++) for (int j=1;j<n;j++) dp[i,j]=grid[i][j]+System.Math.Min(dp[i-1,j],dp[i,j-1]);\n"
        f"    return dp[m-1,n-1]{a};\n"
        "} }\n"
    )


def _perl_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $m = shift @data; my $n = shift @data;\n"
        "my @grid; for (my $i=0;$i<$m;$i++) { my @row = splice(@data, 0, $n); $grid[$i] = \\@row; }\n"
        "sub min_path_sum {\n"
        "    my ($grid, $m, $n) = @_;\n"
        "    my @dp; $dp[0][0] = $grid->[0][0];\n"
        "    for (my $j=1;$j<$n;$j++) { $dp[0][$j] = $dp[0][$j-1] + $grid->[0][$j]; }\n"
        "    for (my $i=1;$i<$m;$i++) { $dp[$i][0] = $dp[$i-1][0] + $grid->[$i][0]; }\n"
        "    for (my $i=1;$i<$m;$i++) { for (my $j=1;$j<$n;$j++) {\n"
        "        my $mn = ($dp[$i-1][$j] < $dp[$i][$j-1]) ? $dp[$i-1][$j] : $dp[$i][$j-1];\n"
        "        $dp[$i][$j] = $grid->[$i][$j] + $mn;\n"
        "    } }\n"
        f"    return $dp[$m-1][$n-1]{a};\n"
        "}\n"
        "print min_path_sum(\\@grid, $m, $n), \"\\n\";\n"
    )


def _c_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "int min_path_sum(int** grid, int m, int n) {\n"
        "    int** dp = (int**)malloc(sizeof(int*)*m); for (int i=0;i<m;i++) dp[i]=(int*)calloc(n,sizeof(int));\n"
        "    dp[0][0]=grid[0][0];\n"
        "    for (int j=1;j<n;j++) dp[0][j]=dp[0][j-1]+grid[0][j];\n"
        "    for (int i=1;i<m;i++) dp[i][0]=dp[i-1][0]+grid[i][0];\n"
        "    for (int i=1;i<m;i++) for (int j=1;j<n;j++) { int mn=dp[i-1][j]<dp[i][j-1]?dp[i-1][j]:dp[i][j-1]; dp[i][j]=grid[i][j]+mn; }\n"
        f"    int result = dp[m-1][n-1]{a};\n"
        "    for (int i=0;i<m;i++) free(dp[i]); free(dp);\n"
        "    return result;\n"
        "}\n"
        "int main() {\n"
        "    int m,n; scanf(\"%d %d\", &m, &n);\n"
        "    int** grid = (int**)malloc(sizeof(int*)*m);\n"
        "    for (int i=0;i<m;i++) { grid[i]=(int*)malloc(sizeof(int)*n); for (int j=0;j<n;j++) scanf(\"%d\", &grid[i][j]); }\n"
        "    printf(\"%d\\n\", min_path_sum(grid, m, n));\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_min_path_sum(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn min_path_sum(grid: &Vec<Vec<i32>>, m: usize, n: usize) -> i32 {\n"
        "    let mut dp = vec![vec![0i32; n]; m]; dp[0][0] = grid[0][0];\n"
        "    for j in 1..n { dp[0][j] = dp[0][j-1] + grid[0][j]; }\n"
        "    for i in 1..m { dp[i][0] = dp[i-1][0] + grid[i][0]; }\n"
        "    for i in 1..m { for j in 1..n { dp[i][j] = grid[i][j] + dp[i-1][j].min(dp[i][j-1]); } }\n"
        f"    dp[m-1][n-1]{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let m = it.next().unwrap() as usize; let n = it.next().unwrap() as usize;\n"
        "    let mut grid = vec![vec![0i32; n]; m];\n"
        "    for i in 0..m { for j in 0..n { grid[i][j] = it.next().unwrap(); } }\n"
        "    println!(\"{}\", min_path_sum(&grid, m, n)); }\n"
    )


# ── n-queens ─────────────────────────────────────────────────────────────────
def _js_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "const n = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function solve_n_queens(n) {\n"
        "    if (n === 0) return 1; let count = 0;\n"
        "    const cols=new Set(), d1=new Set(), d2=new Set();\n"
        "    function bt(row) { if (row===n) { count++; return; } for (let col=0;col<n;col++) { if (cols.has(col)||d1.has(row-col)||d2.has(row+col)) continue; cols.add(col);d1.add(row-col);d2.add(row+col); bt(row+1); cols.delete(col);d1.delete(row-col);d2.delete(row+col); } }\n"
        "    bt(0);\n"
        f"    return count{a};\n"
        "}\n"
        "console.log(solve_n_queens(n));\n"
    )


def _ts_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "const n: number = parseInt(require('fs').readFileSync(0,'utf8').trim());\n"
        "function solve_n_queens(n: number): number {\n"
        "    if (n === 0) return 1; let count = 0;\n"
        "    const cols=new Set<number>(), d1=new Set<number>(), d2=new Set<number>();\n"
        "    function bt(row: number): void { if (row===n) { count++; return; } for (let col=0;col<n;col++) { if (cols.has(col)||d1.has(row-col)||d2.has(row+col)) continue; cols.add(col);d1.add(row-col);d2.add(row+col); bt(row+1); cols.delete(col);d1.delete(row-col);d2.delete(row+col); } }\n"
        "    bt(0);\n"
        f"    return count{a};\n"
        "}\n"
        "console.log(solve_n_queens(n));\n"
    )


def _java_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "import java.util.Scanner;\n"
        "public class Main {\n"
        "    static int count = 0;\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = Integer.parseInt(sc.nextLine().trim());\n"
        "        System.out.println(solve_n_queens(n));\n"
        "    }\n"
        "    static int solve_n_queens(int n) {\n"
        "        if (n == 0) return 1;\n"
        "        count = 0;\n"
        "        boolean[] cols = new boolean[n]; boolean[] d1 = new boolean[4*n+2]; boolean[] d2 = new boolean[4*n+2];\n"
        "        bt(0, n, cols, d1, d2, 2*n);\n"
        f"        return count{a};\n"
        "    }\n"
        "    static void bt(int row, int n, boolean[] cols, boolean[] d1, boolean[] d2, int off) {\n"
        "        if (row == n) { count++; return; }\n"
        "        for (int col=0;col<n;col++) { int i1=row-col+off, i2=row+col; if (cols[col]||d1[i1]||d2[i2]) continue; cols[col]=true;d1[i1]=true;d2[i2]=true; bt(row+1,n,cols,d1,d2,off); cols[col]=false;d1[i1]=false;d2[i2]=false; }\n"
        "    }\n"
        "}\n"
    )


def _cpp_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <iostream>\n#include <vector>\nusing namespace std;\n"
        "int count_ = 0;\n"
        "void bt(int row, int n, vector<bool>& cols, vector<bool>& d1, vector<bool>& d2, int off) {\n"
        "    if (row==n) { count_++; return; }\n"
        "    for (int col=0;col<n;col++) { int i1=row-col+off, i2=row+col; if (cols[col]||d1[i1]||d2[i2]) continue; cols[col]=true;d1[i1]=true;d2[i2]=true; bt(row+1,n,cols,d1,d2,off); cols[col]=false;d1[i1]=false;d2[i2]=false; }\n"
        "}\n"
        "int solve_n_queens(int n) {\n"
        "    if (n==0) return 1;\n"
        "    count_ = 0;\n"
        "    vector<bool> cols(n,false), d1(4*n+2,false), d2(4*n+2,false);\n"
        "    bt(0,n,cols,d1,d2,2*n);\n"
        f"    return count_{a};\n"
        "}\n"
        "int main() { int n; cin>>n; cout << solve_n_queens(n) << endl; return 0; }\n"
    )


def _csharp_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "class Program {\n"
        "    static int count = 0;\n"
        "    static void Main() {\n"
        "        int n = int.Parse(System.Console.In.ReadToEnd().Trim());\n"
        "        System.Console.WriteLine(solve_n_queens(n));\n"
        "    }\n"
        "    static int solve_n_queens(int n) {\n"
        "        if (n == 0) return 1;\n"
        "        count = 0;\n"
        "        var cols = new bool[n]; var d1 = new bool[4*n+2]; var d2 = new bool[4*n+2];\n"
        "        Bt(0, n, cols, d1, d2, 2*n);\n"
        f"        return count{a};\n"
        "    }\n"
        "    static void Bt(int row, int n, bool[] cols, bool[] d1, bool[] d2, int off) {\n"
        "        if (row == n) { count++; return; }\n"
        "        for (int col=0;col<n;col++) { int i1=row-col+off, i2=row+col; if (cols[col]||d1[i1]||d2[i2]) continue; cols[col]=true;d1[i1]=true;d2[i2]=true; Bt(row+1,n,cols,d1,d2,off); cols[col]=false;d1[i1]=false;d2[i2]=false; }\n"
        "    }\n"
        "}\n"
    )


def _perl_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "my $n = <STDIN>; chomp $n; $n = $n + 0;\n"
        "my $count;\n"
        "sub bt {\n"
        "    my ($row, $n, $cols, $d1, $d2) = @_;\n"
        "    if ($row == $n) { $count++; return; }\n"
        "    for (my $col=0;$col<$n;$col++) {\n"
        "        next if exists $cols->{$col} || exists $d1->{$row-$col} || exists $d2->{$row+$col};\n"
        "        $cols->{$col}=1; $d1->{$row-$col}=1; $d2->{$row+$col}=1;\n"
        "        bt($row+1, $n, $cols, $d1, $d2);\n"
        "        delete $cols->{$col}; delete $d1->{$row-$col}; delete $d2->{$row+$col};\n"
        "    }\n"
        "}\n"
        "sub solve_n_queens {\n"
        "    my ($n) = @_;\n"
        "    return 1 if $n == 0;\n"
        "    $count = 0;\n"
        "    my %cols; my %d1; my %d2;\n"
        "    bt(0, $n, \\%cols, \\%d1, \\%d2);\n"
        f"    return {'$count + 1' if wrong else '$count'};\n"
        "}\n"
        "print solve_n_queens($n), \"\\n\";\n"
    )


def _c_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "static int g_count;\n"
        "static void bt(int row, int n, int* cols, int* d1, int* d2, int off) {\n"
        "    if (row==n) { g_count++; return; }\n"
        "    for (int col=0;col<n;col++) { int i1=row-col+off, i2=row+col; if (cols[col]||d1[i1]||d2[i2]) continue; cols[col]=1;d1[i1]=1;d2[i2]=1; bt(row+1,n,cols,d1,d2,off); cols[col]=0;d1[i1]=0;d2[i2]=0; }\n"
        "}\n"
        "int solve_n_queens(int n) {\n"
        "    if (n==0) return 1;\n"
        "    g_count = 0;\n"
        "    int* cols=(int*)calloc(n,sizeof(int)); int* d1=(int*)calloc(4*n+2,sizeof(int)); int* d2=(int*)calloc(4*n+2,sizeof(int));\n"
        "    bt(0,n,cols,d1,d2,2*n);\n"
        "    free(cols); free(d1); free(d2);\n"
        f"    return g_count{a};\n"
        "}\n"
        "int main() { int n; scanf(\"%d\",&n); printf(\"%d\\n\", solve_n_queens(n)); return 0; }\n"
    )


def _rust_nqueens(wrong):
    a = " + 1" if wrong else ""
    return (
        "use std::io::Read;\n"
        "fn bt(row: i32, n: i32, cols: &mut Vec<bool>, d1: &mut Vec<bool>, d2: &mut Vec<bool>, off: i32, count: &mut i32) {\n"
        "    if row == n { *count += 1; return; }\n"
        "    for col in 0..n {\n"
        "        let i1 = (row-col+off) as usize; let i2 = (row+col) as usize;\n"
        "        if cols[col as usize] || d1[i1] || d2[i2] { continue; }\n"
        "        cols[col as usize]=true; d1[i1]=true; d2[i2]=true;\n"
        "        bt(row+1, n, cols, d1, d2, off, count);\n"
        "        cols[col as usize]=false; d1[i1]=false; d2[i2]=false;\n"
        "    }\n"
        "}\n"
        "fn solve_n_queens(n: i32) -> i32 {\n"
        "    if n == 0 { return 1; }\n"
        "    let mut count = 0;\n"
        "    let mut cols = vec![false; n as usize]; let mut d1 = vec![false; (4*n+2) as usize]; let mut d2 = vec![false; (4*n+2) as usize];\n"
        "    bt(0, n, &mut cols, &mut d1, &mut d2, 2*n, &mut count);\n"
        f"    count{a}\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let n: i32 = s.trim().parse().unwrap();\n"
        "    println!(\"{}\", solve_n_queens(n)); }\n"
    )


# ── graph-bfs (edge-list input, build adj, reuse bfs(adj,src,n)) ────────────
def _js_bfs(wrong):
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "let idx=0; const n=data[idx++], m=data[idx++], src=data[idx++];\n"
        "const adj = Array.from({length:n}, () => []);\n"
        "for (let e=0;e<m;e++) { const u=data[idx++], v=data[idx++]; adj[u].push(v); adj[v].push(u); }\n"
        "function bfs(adj, src, n) {\n"
        "    const dist = new Array(n).fill(-1); dist[src]=0; const q=[src]; let qi=0;\n"
        "    while (qi<q.length) { const u=q[qi]; qi++; for (const v of adj[u]) { if (dist[v]===-1) { dist[v]=dist[u]+1; q.push(v); } } }\n"
        f"    return {'dist.map(x => x + 1)' if wrong else 'dist'};\n"
        "}\n"
        "console.log(bfs(adj, src, n).join(' '));\n"
    )


def _ts_bfs(wrong):
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "let idx=0; const n=data[idx++], m=data[idx++], src=data[idx++];\n"
        "const adj: number[][] = Array.from({length:n}, () => []);\n"
        "for (let e=0;e<m;e++) { const u=data[idx++], v=data[idx++]; adj[u].push(v); adj[v].push(u); }\n"
        "function bfs(adj: number[][], src: number, n: number): number[] {\n"
        "    const dist: number[] = new Array(n).fill(-1); dist[src]=0; const q: number[]=[src]; let qi=0;\n"
        "    while (qi<q.length) { const u=q[qi]; qi++; for (const v of adj[u]) { if (dist[v]===-1) { dist[v]=dist[u]+1; q.push(v); } } }\n"
        f"    return {'dist.map(x => x + 1)' if wrong else 'dist'};\n"
        "}\n"
        "console.log(bfs(adj, src, n).join(' '));\n"
    )


def _java_bfs(wrong):
    return (
        "import java.util.*;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n=sc.nextInt(), m=sc.nextInt(), src=sc.nextInt();\n"
        "    List<List<Integer>> adj = new ArrayList<>(); for (int i=0;i<n;i++) adj.add(new ArrayList<>());\n"
        "    for (int e=0;e<m;e++) { int u=sc.nextInt(), v=sc.nextInt(); adj.get(u).add(v); adj.get(v).add(u); }\n"
        "    int[] r = bfs(adj, src, n);\n"
        "    StringBuilder sb = new StringBuilder(); for (int i=0;i<n;i++) { if (i>0) sb.append(' '); sb.append(r[i]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static int[] bfs(List<List<Integer>> adj, int src, int n) {\n"
        "    int[] dist = new int[n]; Arrays.fill(dist,-1); dist[src]=0;\n"
        "    ArrayDeque<Integer> q = new ArrayDeque<>(); q.add(src);\n"
        "    while (!q.isEmpty()) { int u=q.poll(); for (int v: adj.get(u)) { if (dist[v]==-1) { dist[v]=dist[u]+1; q.add(v); } } }\n"
        + ("    for (int i=0;i<n;i++) dist[i]++;\n" if wrong else "") +
        "    return dist;\n"
        "} }\n"
    )


def _cpp_bfs(wrong):
    return (
        "#include <iostream>\n#include <vector>\n#include <queue>\nusing namespace std;\n"
        "vector<int> bfs(vector<vector<int>>& adj, int src, int n) {\n"
        "    vector<int> dist(n,-1); dist[src]=0; queue<int> q; q.push(src);\n"
        "    while (!q.empty()) { int u=q.front(); q.pop(); for (int v: adj[u]) { if (dist[v]==-1) { dist[v]=dist[u]+1; q.push(v); } } }\n"
        + ("    for (int i=0;i<n;i++) dist[i]++;\n" if wrong else "") +
        "    return dist;\n"
        "}\n"
        "int main() {\n"
        "    int n,m,src; cin>>n>>m>>src;\n"
        "    vector<vector<int>> adj(n);\n"
        "    for (int e=0;e<m;e++) { int u,v; cin>>u>>v; adj[u].push_back(v); adj[v].push_back(u); }\n"
        "    auto r = bfs(adj, src, n);\n"
        "    for (size_t i=0;i<r.size();i++) { if (i) cout << ' '; cout << r[i]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_bfs(wrong):
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int m=int.Parse(t[idx++]); int src=int.Parse(t[idx++]);\n"
        "    var adj = new System.Collections.Generic.List<int>[n]; for (int i=0;i<n;i++) adj[i]=new System.Collections.Generic.List<int>();\n"
        "    for (int e=0;e<m;e++) { int u=int.Parse(t[idx++]); int v=int.Parse(t[idx++]); adj[u].Add(v); adj[v].Add(u); }\n"
        "    int[] r = bfs(adj, src, n);\n"
        "    System.Console.WriteLine(string.Join(\" \", r));\n"
        "}\n"
        "static int[] bfs(System.Collections.Generic.List<int>[] adj, int src, int n) {\n"
        "    int[] dist = new int[n]; for (int i=0;i<n;i++) dist[i]=-1; dist[src]=0;\n"
        "    var q = new System.Collections.Generic.Queue<int>(); q.Enqueue(src);\n"
        "    while (q.Count > 0) { int u=q.Dequeue(); foreach (int v in adj[u]) { if (dist[v]==-1) { dist[v]=dist[u]+1; q.Enqueue(v); } } }\n"
        + ("    for (int i=0;i<n;i++) dist[i]++;\n" if wrong else "") +
        "    return dist;\n"
        "} }\n"
    )


def _perl_bfs(wrong):
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my $m = shift @data; my $src = shift @data;\n"
        "my @adj; for (my $i=0;$i<$n;$i++) { $adj[$i] = []; }\n"
        "for (my $e=0;$e<$m;$e++) { my $u=shift @data; my $v=shift @data; push @{$adj[$u]}, $v; push @{$adj[$v]}, $u; }\n"
        "sub bfs {\n"
        "    my ($adj, $src, $n) = @_;\n"
        "    my @dist = (-1) x $n; $dist[$src] = 0;\n"
        "    my @q = ($src); my $qi = 0;\n"
        "    while ($qi < scalar(@q)) { my $u = $q[$qi]; $qi++; foreach my $v (@{$adj->[$u]}) { if ($dist[$v] == -1) { $dist[$v] = $dist[$u] + 1; push @q, $v; } } }\n"
        + ("    for (my $i=0;$i<$n;$i++) { $dist[$i]++; }\n" if wrong else "") +
        "    return \\@dist;\n"
        "}\n"
        "print join(' ', @{bfs(\\@adj, $src, $n)}), \"\\n\";\n"
    )


def _c_bfs(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "typedef struct { int* data; int size; int cap; } IntList;\n"
        "void il_push(IntList* l, int v) { if (l->size==l->cap) { l->cap = l->cap? l->cap*2:4; l->data=(int*)realloc(l->data,sizeof(int)*l->cap); } l->data[l->size++]=v; }\n"
        "int main() {\n"
        "    int n,m,src; scanf(\"%d %d %d\", &n, &m, &src);\n"
        "    IntList* adj = (IntList*)calloc(n, sizeof(IntList));\n"
        "    for (int e=0;e<m;e++) { int u,v; scanf(\"%d %d\", &u, &v); il_push(&adj[u], v); il_push(&adj[v], u); }\n"
        "    int* dist = (int*)malloc(sizeof(int)*n); for (int i=0;i<n;i++) dist[i]=-1; dist[src]=0;\n"
        "    int* q = (int*)malloc(sizeof(int)*n*n); int qh=0, qt=0; q[qt++]=src;\n"
        "    while (qh < qt) { int u=q[qh++]; for (int k=0;k<adj[u].size;k++) { int v=adj[u].data[k]; if (dist[v]==-1) { dist[v]=dist[u]+1; q[qt++]=v; } } }\n"
        + ("    for (int i=0;i<n;i++) dist[i]++;\n" if wrong else "") +
        "    for (int i=0;i<n;i++) { if (i) printf(\" \"); printf(\"%d\", dist[i]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_bfs(wrong):
    return (
        "use std::io::Read;\nuse std::collections::VecDeque;\n"
        "fn bfs(adj: &Vec<Vec<i32>>, src: i32, n: i32) -> Vec<i32> {\n"
        "    let mut dist = vec![-1i32; n as usize]; dist[src as usize] = 0;\n"
        "    let mut q: VecDeque<i32> = VecDeque::new(); q.push_back(src);\n"
        "    while let Some(u) = q.pop_front() {\n"
        "        for &v in adj[u as usize].iter() { if dist[v as usize] == -1 { dist[v as usize] = dist[u as usize] + 1; q.push_back(v); } }\n"
        "    }\n"
        + ("    for i in 0..n as usize { dist[i] += 1; }\n" if wrong else "") +
        "    dist\n"
        "}\n"
        "fn main() { let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i32>().unwrap());\n"
        "    let n = it.next().unwrap(); let m = it.next().unwrap(); let src = it.next().unwrap();\n"
        "    let mut adj: Vec<Vec<i32>> = vec![Vec::new(); n as usize];\n"
        "    for _ in 0..m { let u = it.next().unwrap(); let v = it.next().unwrap(); adj[u as usize].push(v); adj[v as usize].push(u); }\n"
        "    let r = bfs(&adj, src, n);\n"
        "    let strs: Vec<String> = r.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \")); }\n"
    )


# ── dijkstra (edge-list input, build adj as (v,w) pairs, reuse dijkstra(adj,n)) ─
def _js_dijkstra(wrong):
    return (
        "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "let idx=0; const n=data[idx++], m=data[idx++];\n"
        "const adj = Array.from({length:n}, () => []);\n"
        "for (let e=0;e<m;e++) { const u=data[idx++], v=data[idx++], w=data[idx++]; adj[u].push([v,w]); }\n"
        "function dijkstra(adj, n) {\n"
        "    const INF = Infinity; const dist = new Array(n).fill(INF); dist[0]=0; const visited = new Array(n).fill(false);\n"
        "    for (let iter=0;iter<n;iter++) { let u=-1, best=INF; for (let i=0;i<n;i++) if (!visited[i] && dist[i]<best) { best=dist[i]; u=i; } if (u===-1) break; visited[u]=true;\n"
        "        for (const [v,w] of adj[u]) { if (dist[u]+w < dist[v]) dist[v]=dist[u]+w; } }\n"
        "    const out = dist.map(d => d===INF?-1:d);\n"
        f"    return {'out.map(x => x === -1 ? -1 : x + 1)' if wrong else 'out'};\n"
        "}\n"
        "console.log(dijkstra(adj, n).join(' '));\n"
    )


def _ts_dijkstra(wrong):
    return (
        "const data: number[] = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
        "let idx=0; const n=data[idx++], m=data[idx++];\n"
        "const adj: number[][][] = Array.from({length:n}, () => []);\n"
        "for (let e=0;e<m;e++) { const u=data[idx++], v=data[idx++], w=data[idx++]; adj[u].push([v,w]); }\n"
        "function dijkstra(adj: number[][][], n: number): number[] {\n"
        "    const INF = Infinity; const dist: number[] = new Array(n).fill(INF); dist[0]=0; const visited: boolean[] = new Array(n).fill(false);\n"
        "    for (let iter=0;iter<n;iter++) { let u=-1, best=INF; for (let i=0;i<n;i++) if (!visited[i] && dist[i]<best) { best=dist[i]; u=i; } if (u===-1) break; visited[u]=true;\n"
        "        for (const e2 of adj[u]) { const v=e2[0], w=e2[1]; if (dist[u]+w < dist[v]) dist[v]=dist[u]+w; } }\n"
        "    const out = dist.map(d => d===INF?-1:d);\n"
        f"    return {'out.map(x => x === -1 ? -1 : x + 1)' if wrong else 'out'};\n"
        "}\n"
        "console.log(dijkstra(adj, n).join(' '));\n"
    )


def _java_dijkstra(wrong):
    return (
        "import java.util.*;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    int n=sc.nextInt(), m=sc.nextInt();\n"
        "    List<int[]>[] adj = new List[n]; for (int i=0;i<n;i++) adj[i]=new ArrayList<>();\n"
        "    for (int e=0;e<m;e++) { int u=sc.nextInt(), v=sc.nextInt(), w=sc.nextInt(); adj[u].add(new int[]{v,w}); }\n"
        "    int[] r = dijkstra(adj, n);\n"
        "    StringBuilder sb = new StringBuilder(); for (int i=0;i<n;i++) { if (i>0) sb.append(' '); sb.append(r[i]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static int[] dijkstra(List<int[]>[] adj, int n) {\n"
        "    long INF = Long.MAX_VALUE/2; long[] dist = new long[n]; Arrays.fill(dist, INF); dist[0]=0;\n"
        "    boolean[] visited = new boolean[n];\n"
        "    for (int iter=0;iter<n;iter++) {\n"
        "        int u=-1; long best=INF; for (int i=0;i<n;i++) if (!visited[i] && dist[i]<best) { best=dist[i]; u=i; }\n"
        "        if (u==-1) break; visited[u]=true;\n"
        "        for (int[] e2: adj[u]) { int v=e2[0], w=e2[1]; if (dist[u]+w < dist[v]) dist[v]=dist[u]+w; }\n"
        "    }\n"
        "    int[] out = new int[n]; for (int i=0;i<n;i++) out[i] = dist[i]>=INF?-1:(int)dist[i];\n"
        + ("    for (int i=0;i<n;i++) if (out[i] != -1) out[i]++;\n" if wrong else "") +
        "    return out;\n"
        "} }\n"
    )


def _cpp_dijkstra(wrong):
    return (
        "#include <iostream>\n#include <vector>\n#include <climits>\nusing namespace std;\n"
        "vector<int> dijkstra(vector<vector<pair<int,int>>>& adj, int n) {\n"
        "    const long long INF = LLONG_MAX/2; vector<long long> dist(n, INF); dist[0]=0; vector<bool> visited(n,false);\n"
        "    for (int iter=0;iter<n;iter++) {\n"
        "        int u=-1; long long best=INF; for (int i=0;i<n;i++) if (!visited[i] && dist[i]<best) { best=dist[i]; u=i; }\n"
        "        if (u==-1) break; visited[u]=true;\n"
        "        for (auto& e: adj[u]) { int v=e.first, w=e.second; if (dist[u]+w < dist[v]) dist[v]=dist[u]+w; }\n"
        "    }\n"
        "    vector<int> out(n); for (int i=0;i<n;i++) out[i] = dist[i]>=INF?-1:(int)dist[i];\n"
        + ("    for (int i=0;i<n;i++) if (out[i]!=-1) out[i]++;\n" if wrong else "") +
        "    return out;\n"
        "}\n"
        "int main() {\n"
        "    int n,m; cin>>n>>m; vector<vector<pair<int,int>>> adj(n);\n"
        "    for (int e=0;e<m;e++) { int u,v,w; cin>>u>>v>>w; adj[u].push_back({v,w}); }\n"
        "    auto r = dijkstra(adj, n);\n"
        "    for (size_t i=0;i<r.size();i++) { if (i) cout<<' '; cout<<r[i]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_dijkstra(wrong):
    return (
        "class Program { static void Main() {\n"
        "    var t = System.Console.In.ReadToEnd().Split(new char[]{' ','\\n','\\r','\\t'}, System.StringSplitOptions.RemoveEmptyEntries);\n"
        "    int idx=0; int n=int.Parse(t[idx++]); int m=int.Parse(t[idx++]);\n"
        "    var adj = new System.Collections.Generic.List<int[]>[n]; for (int i=0;i<n;i++) adj[i]=new System.Collections.Generic.List<int[]>();\n"
        "    for (int e=0;e<m;e++) { int u=int.Parse(t[idx++]); int v=int.Parse(t[idx++]); int w=int.Parse(t[idx++]); adj[u].Add(new int[]{v,w}); }\n"
        "    int[] r = dijkstra(adj, n);\n"
        "    System.Console.WriteLine(string.Join(\" \", r));\n"
        "}\n"
        "static int[] dijkstra(System.Collections.Generic.List<int[]>[] adj, int n) {\n"
        "    long INF = long.MaxValue/2; long[] dist = new long[n]; for (int i=0;i<n;i++) dist[i]=INF; dist[0]=0;\n"
        "    bool[] visited = new bool[n];\n"
        "    for (int iter=0;iter<n;iter++) {\n"
        "        int u=-1; long best=INF; for (int i=0;i<n;i++) if (!visited[i] && dist[i]<best) { best=dist[i]; u=i; }\n"
        "        if (u==-1) break; visited[u]=true;\n"
        "        foreach (var e in adj[u]) { int v=e[0], w=e[1]; if (dist[u]+w < dist[v]) dist[v]=dist[u]+w; }\n"
        "    }\n"
        "    int[] outArr = new int[n]; for (int i=0;i<n;i++) outArr[i] = dist[i]>=INF?-1:(int)dist[i];\n"
        + ("    for (int i=0;i<n;i++) if (outArr[i]!=-1) outArr[i]++;\n" if wrong else "") +
        "    return outArr;\n"
        "} }\n"
    )


def _perl_dijkstra(wrong):
    return (
        "my @data = split ' ', do { local $/; <STDIN> };\n"
        "my $n = shift @data; my $m = shift @data;\n"
        "my @adj; for (my $i=0;$i<$n;$i++) { $adj[$i] = []; }\n"
        "for (my $e=0;$e<$m;$e++) { my $u=shift @data; my $v=shift @data; my $w=shift @data; push @{$adj[$u]}, [$v,$w]; }\n"
        "sub dijkstra {\n"
        "    my ($adj, $n) = @_;\n"
        "    my $INF = 1e18; my @dist = ($INF) x $n; $dist[0] = 0; my @visited = (0) x $n;\n"
        "    for (my $iter=0;$iter<$n;$iter++) {\n"
        "        my $u = -1; my $best = $INF;\n"
        "        for (my $i=0;$i<$n;$i++) { if (!$visited[$i] && $dist[$i] < $best) { $best = $dist[$i]; $u = $i; } }\n"
        "        last if $u == -1;\n"
        "        $visited[$u] = 1;\n"
        "        foreach my $e (@{$adj->[$u]}) { my ($v,$w) = @$e; if ($dist[$u]+$w < $dist[$v]) { $dist[$v] = $dist[$u]+$w; } }\n"
        "    }\n"
        "    my @out = map { $_ >= $INF ? -1 : $_ } @dist;\n"
        + ("    @out = map { $_ == -1 ? -1 : $_ + 1 } @out;\n" if wrong else "") +
        "    return \\@out;\n"
        "}\n"
        "print join(' ', @{dijkstra(\\@adj, $n)}), \"\\n\";\n"
    )


def _c_dijkstra(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n"
        "typedef struct { int v; int w; } Edge;\n"
        "typedef struct { Edge* data; int size; int cap; } EdgeList;\n"
        "void el_push(EdgeList* l, int v, int w) { if (l->size==l->cap) { l->cap=l->cap?l->cap*2:4; l->data=(Edge*)realloc(l->data,sizeof(Edge)*l->cap); } l->data[l->size].v=v; l->data[l->size].w=w; l->size++; }\n"
        "int main() {\n"
        "    int n,m; scanf(\"%d %d\", &n, &m);\n"
        "    EdgeList* adj = (EdgeList*)calloc(n, sizeof(EdgeList));\n"
        "    for (int e=0;e<m;e++) { int u,v,w; scanf(\"%d %d %d\", &u, &v, &w); el_push(&adj[u], v, w); }\n"
        "    long long INF = 1000000000000LL;\n"
        "    long long* dist = (long long*)malloc(sizeof(long long)*n); for (int i=0;i<n;i++) dist[i]=INF; dist[0]=0;\n"
        "    int* visited = (int*)calloc(n, sizeof(int));\n"
        "    for (int iter=0;iter<n;iter++) {\n"
        "        int u=-1; long long best=INF;\n"
        "        for (int i=0;i<n;i++) if (!visited[i] && dist[i]<best) { best=dist[i]; u=i; }\n"
        "        if (u==-1) break; visited[u]=1;\n"
        "        for (int k=0;k<adj[u].size;k++) { int v=adj[u].data[k].v; int w=adj[u].data[k].w; if (dist[u]+w < dist[v]) dist[v]=dist[u]+w; }\n"
        "    }\n"
        "    for (int i=0;i<n;i++) {\n"
        "        int val = (dist[i]>=INF) ? -1 : (int)dist[i];\n"
        + ("        if (val != -1) val++;\n" if wrong else "") +
        "        if (i) printf(\" \"); printf(\"%d\", val);\n"
        "    }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_dijkstra(wrong):
    return (
        "use std::io::Read;\n"
        "fn main() {\n"
        "    let mut s=String::new(); std::io::stdin().read_to_string(&mut s).unwrap();\n"
        "    let mut it = s.split_whitespace().map(|x| x.parse::<i64>().unwrap());\n"
        "    let n = it.next().unwrap() as usize; let m = it.next().unwrap() as usize;\n"
        "    let mut adj: Vec<Vec<(usize, i64)>> = vec![Vec::new(); n];\n"
        "    for _ in 0..m { let u = it.next().unwrap() as usize; let v = it.next().unwrap() as usize; let w = it.next().unwrap(); adj[u].push((v, w)); }\n"
        "    const INF: i64 = 1_000_000_000_000;\n"
        "    let mut dist = vec![INF; n]; dist[0] = 0;\n"
        "    let mut visited = vec![false; n];\n"
        "    for _ in 0..n {\n"
        "        let mut u: i64 = -1; let mut best = INF;\n"
        "        for i in 0..n { if !visited[i] && dist[i] < best { best = dist[i]; u = i as i64; } }\n"
        "        if u == -1 { break; }\n"
        "        let u = u as usize; visited[u] = true;\n"
        "        for &(v, w) in adj[u].iter() { if dist[u] + w < dist[v] { dist[v] = dist[u] + w; } }\n"
        "    }\n"
        "    let mut out: Vec<i64> = dist.iter().map(|&d| if d >= INF { -1 } else { d }).collect();\n"
        + ("    for i in 0..n { if out[i] != -1 { out[i] += 1; } }\n" if wrong else "") +
        "    let strs: Vec<String> = out.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \"));\n"
        "}\n"
    )


# ── kmp-string-matching (print "-1" if no matches) ──────────────────────────
def _js_kmp(wrong):
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const T = lines[0], P = lines[1];\n"
        "function kmp_search(T, P) {\n"
        "    const n = P.length; const lps = new Array(n).fill(0); let len=0, i=1;\n"
        "    while (i<n) { if (P[i]===P[len]) { len++; lps[i]=len; i++; } else if (len!==0) len=lps[len-1]; else { lps[i]=0; i++; } }\n"
        "    const result=[]; let ti=0, pi=0;\n"
        "    while (ti<T.length) { if (T[ti]===P[pi]) { ti++; pi++; if (pi===n) { result.push(ti-pi); pi=lps[pi-1]; } } else if (pi!==0) pi=lps[pi-1]; else ti++; }\n"
        f"    return {'result.map(x => x + 1)' if wrong else 'result'};\n"
        "}\n"
        "const r = kmp_search(T, P);\n"
        "console.log(r.length ? r.join(' ') : '-1');\n"
    )


def _ts_kmp(wrong):
    return (
        "const lines = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const T: string = lines[0], P: string = lines[1];\n"
        "function kmp_search(T: string, P: string): number[] {\n"
        "    const n = P.length; const lps: number[] = new Array(n).fill(0); let len=0, i=1;\n"
        "    while (i<n) { if (P[i]===P[len]) { len++; lps[i]=len; i++; } else if (len!==0) len=lps[len-1]; else { lps[i]=0; i++; } }\n"
        "    const result: number[]=[]; let ti=0, pi=0;\n"
        "    while (ti<T.length) { if (T[ti]===P[pi]) { ti++; pi++; if (pi===n) { result.push(ti-pi); pi=lps[pi-1]; } } else if (pi!==0) pi=lps[pi-1]; else ti++; }\n"
        f"    return {'result.map(x => x + 1)' if wrong else 'result'};\n"
        "}\n"
        "const r = kmp_search(T, P);\n"
        "console.log(r.length ? r.join(' ') : '-1');\n"
    )


def _java_kmp(wrong):
    return (
        "import java.util.*;\n"
        "public class Main { public static void main(String[] args) {\n"
        "    Scanner sc = new Scanner(System.in);\n"
        "    String T = sc.nextLine(); String P = sc.nextLine();\n"
        "    int[] r = kmp_search(T, P);\n"
        "    if (r.length == 0) { System.out.println(-1); return; }\n"
        "    StringBuilder sb = new StringBuilder(); for (int i=0;i<r.length;i++) { if (i>0) sb.append(' '); sb.append(r[i]); }\n"
        "    System.out.println(sb.toString());\n"
        "}\n"
        "static int[] kmp_search(String T, String P) {\n"
        "    int n = P.length(); int[] lps = new int[n]; int len=0, i=1;\n"
        "    while (i<n) { if (P.charAt(i)==P.charAt(len)) { len++; lps[i]=len; i++; } else if (len!=0) len=lps[len-1]; else { lps[i]=0; i++; } }\n"
        "    List<Integer> result = new ArrayList<>(); int ti=0, pi=0;\n"
        "    while (ti<T.length()) { if (T.charAt(ti)==P.charAt(pi)) { ti++; pi++; if (pi==n) { result.add(ti-pi); pi=lps[pi-1]; } } else if (pi!=0) pi=lps[pi-1]; else ti++; }\n"
        "    int[] out = new int[result.size()];\n"
        "    for (int k=0;k<out.length;k++) out[k] = result.get(k)" + (" + 1" if wrong else "") + ";\n"
        "    return out;\n"
        "} }\n"
    )


def _cpp_kmp(wrong):
    return (
        "#include <iostream>\n#include <vector>\n#include <string>\nusing namespace std;\n"
        "vector<int> kmp_search(string T, string P) {\n"
        "    int n = P.size(); vector<int> lps(n,0); int len=0, i=1;\n"
        "    while (i<n) { if (P[i]==P[len]) { len++; lps[i]=len; i++; } else if (len!=0) len=lps[len-1]; else { lps[i]=0; i++; } }\n"
        "    vector<int> result; int ti=0, pi=0;\n"
        "    while (ti<(int)T.size()) { if (T[ti]==P[pi]) { ti++; pi++; if (pi==n) { result.push_back(ti-pi); pi=lps[pi-1]; } } else if (pi!=0) pi=lps[pi-1]; else ti++; }\n"
        + ("    for (auto& x: result) x++;\n" if wrong else "") +
        "    return result;\n"
        "}\n"
        "int main() {\n"
        "    string T, P; getline(cin, T); getline(cin, P);\n"
        "    auto r = kmp_search(T, P);\n"
        "    if (r.empty()) { cout << -1 << endl; return 0; }\n"
        "    for (size_t i=0;i<r.size();i++) { if (i) cout<<' '; cout<<r[i]; }\n"
        "    cout << endl; return 0;\n"
        "}\n"
    )


def _csharp_kmp(wrong):
    return (
        "class Program { static void Main() {\n"
        "    string T = System.Console.In.ReadLine(); string P = System.Console.In.ReadLine();\n"
        "    var r = kmp_search(T, P);\n"
        "    if (r.Count == 0) { System.Console.WriteLine(-1); return; }\n"
        "    System.Console.WriteLine(string.Join(\" \", r));\n"
        "}\n"
        "static System.Collections.Generic.List<int> kmp_search(string T, string P) {\n"
        "    int n = P.Length; int[] lps = new int[n]; int len=0, i=1;\n"
        "    while (i<n) { if (P[i]==P[len]) { len++; lps[i]=len; i++; } else if (len!=0) len=lps[len-1]; else { lps[i]=0; i++; } }\n"
        "    var result = new System.Collections.Generic.List<int>(); int ti=0, pi=0;\n"
        "    while (ti<T.Length) { if (T[ti]==P[pi]) { ti++; pi++; if (pi==n) { result.Add(ti-pi); pi=lps[pi-1]; } } else if (pi!=0) pi=lps[pi-1]; else ti++; }\n"
        + ("    for (int k=0;k<result.Count;k++) result[k]++;\n" if wrong else "") +
        "    return result;\n"
        "} }\n"
    )


def _perl_kmp(wrong):
    return (
        "my @lines = split /\\n/, do { local $/; <STDIN> };\n"
        "my $T = $lines[0]; my $P = $lines[1];\n"
        "sub kmp_search {\n"
        "    my ($T, $P) = @_;\n"
        "    my $n = length($P); my @lps = (0) x $n; my $len = 0; my $i = 1;\n"
        "    while ($i < $n) {\n"
        "        if (substr($P,$i,1) eq substr($P,$len,1)) { $len++; $lps[$i] = $len; $i++; }\n"
        "        elsif ($len != 0) { $len = $lps[$len-1]; }\n"
        "        else { $lps[$i] = 0; $i++; }\n"
        "    }\n"
        "    my @result; my $ti = 0; my $pi = 0; my $tlen = length($T);\n"
        "    while ($ti < $tlen) {\n"
        "        if (substr($T,$ti,1) eq substr($P,$pi,1)) { $ti++; $pi++; if ($pi == $n) { push @result, $ti-$pi; $pi = $lps[$pi-1]; } }\n"
        "        elsif ($pi != 0) { $pi = $lps[$pi-1]; }\n"
        "        else { $ti++; }\n"
        "    }\n"
        + ("    @result = map { $_ + 1 } @result;\n" if wrong else "") +
        "    return \\@result;\n"
        "}\n"
        "my $r = kmp_search($T, $P);\n"
        "print(scalar(@$r) ? join(' ', @$r) . \"\\n\" : \"-1\\n\");\n"
    )


def _c_kmp(wrong):
    return (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
        "int main() {\n"
        "    char T[65537], P[65537];\n"
        "    fgets(T, sizeof(T), stdin); T[strcspn(T, \"\\r\\n\")]=0;\n"
        "    fgets(P, sizeof(P), stdin); P[strcspn(P, \"\\r\\n\")]=0;\n"
        "    int n = strlen(P); int tlen = strlen(T);\n"
        "    int* lps = (int*)calloc(n, sizeof(int));\n"
        "    int len=0, i=1;\n"
        "    while (i<n) { if (P[i]==P[len]) { len++; lps[i]=len; i++; } else if (len!=0) len=lps[len-1]; else { lps[i]=0; i++; } }\n"
        "    int* result = (int*)malloc(sizeof(int)*(tlen+1)); int rc=0;\n"
        "    int ti=0, pi=0;\n"
        "    while (ti<tlen) { if (T[ti]==P[pi]) { ti++; pi++; if (pi==n) { result[rc++]=ti-pi; pi=lps[pi-1]; } } else if (pi!=0) pi=lps[pi-1]; else ti++; }\n"
        + ("    for (int k=0;k<rc;k++) result[k]++;\n" if wrong else "") +
        "    if (rc == 0) { printf(\"-1\\n\"); return 0; }\n"
        "    for (int k=0;k<rc;k++) { if (k) printf(\" \"); printf(\"%d\", result[k]); }\n"
        "    printf(\"\\n\");\n"
        "    return 0;\n"
        "}\n"
    )


def _rust_kmp(wrong):
    return (
        "use std::io::{self, BufRead};\n"
        "fn kmp_search(t: &str, p: &str) -> Vec<i32> {\n"
        "    let tb: Vec<u8> = t.bytes().collect(); let pb: Vec<u8> = p.bytes().collect(); let n = pb.len();\n"
        "    let mut lps = vec![0usize; n]; let mut len = 0usize; let mut i = 1usize;\n"
        "    while i < n { if pb[i]==pb[len] { len+=1; lps[i]=len; i+=1; } else if len!=0 { len=lps[len-1]; } else { lps[i]=0; i+=1; } }\n"
        "    let mut result: Vec<i32> = Vec::new(); let mut ti = 0usize; let mut pi = 0usize;\n"
        "    while ti < tb.len() { if tb[ti]==pb[pi] { ti+=1; pi+=1; if pi==n { result.push((ti-pi) as i32); pi=lps[pi-1]; } } else if pi!=0 { pi=lps[pi-1]; } else { ti+=1; } }\n"
        + ("    for x in result.iter_mut() { *x += 1; }\n" if wrong else "") +
        "    result\n"
        "}\n"
        "fn main() { let stdin = io::stdin(); let mut lines = stdin.lock().lines();\n"
        "    let t = lines.next().unwrap().unwrap(); let p = lines.next().unwrap().unwrap();\n"
        "    let r = kmp_search(&t, &p);\n"
        "    if r.is_empty() { println!(\"-1\"); return; }\n"
        "    let strs: Vec<String> = r.iter().map(|x| x.to_string()).collect();\n"
        "    println!(\"{}\", strs.join(\" \")); }\n"
    )


_BUILDERS = {
    "gcd-euclidean": {"javascript": _js_gcd, "typescript": _ts_gcd, "java": _java_gcd, "cpp": _cpp_gcd,
                      "csharp": _csharp_gcd, "perl": _perl_gcd, "c": _c_gcd, "rust": _rust_gcd},
    "house-robber": {"javascript": _js_rob, "typescript": _ts_rob, "java": _java_rob, "cpp": _cpp_rob,
                     "csharp": _csharp_rob, "perl": _perl_rob, "c": _c_rob, "rust": _rust_rob},
    "word-break": {"javascript": _js_word_break, "typescript": _ts_word_break, "java": _java_word_break, "cpp": _cpp_word_break,
                   "csharp": _csharp_word_break, "perl": _perl_word_break, "c": _c_word_break, "rust": _rust_word_break},
    "longest-increasing-subsequence": {"javascript": _js_lis, "typescript": _ts_lis, "java": _java_lis, "cpp": _cpp_lis,
                                       "csharp": _csharp_lis, "perl": _perl_lis, "c": _c_lis, "rust": _rust_lis},
    "longest-common-subsequence": {"javascript": _js_lcs, "typescript": _ts_lcs, "java": _java_lcs, "cpp": _cpp_lcs,
                                   "csharp": _csharp_lcs, "perl": _perl_lcs, "c": _c_lcs, "rust": _rust_lcs},
    "edit-distance": {"javascript": _js_edit_distance, "typescript": _ts_edit_distance, "java": _java_edit_distance, "cpp": _cpp_edit_distance,
                      "csharp": _csharp_edit_distance, "perl": _perl_edit_distance, "c": _c_edit_distance, "rust": _rust_edit_distance},
    "minimum-path-sum": {"javascript": _js_min_path_sum, "typescript": _ts_min_path_sum, "java": _java_min_path_sum, "cpp": _cpp_min_path_sum,
                         "csharp": _csharp_min_path_sum, "perl": _perl_min_path_sum, "c": _c_min_path_sum, "rust": _rust_min_path_sum},
    "n-queens": {"javascript": _js_nqueens, "typescript": _ts_nqueens, "java": _java_nqueens, "cpp": _cpp_nqueens,
                "csharp": _csharp_nqueens, "perl": _perl_nqueens, "c": _c_nqueens, "rust": _rust_nqueens},
    "graph-bfs": {"javascript": _js_bfs, "typescript": _ts_bfs, "java": _java_bfs, "cpp": _cpp_bfs,
                 "csharp": _csharp_bfs, "perl": _perl_bfs, "c": _c_bfs, "rust": _rust_bfs},
    "dijkstra-shortest-path": {"javascript": _js_dijkstra, "typescript": _ts_dijkstra, "java": _java_dijkstra, "cpp": _cpp_dijkstra,
                               "csharp": _csharp_dijkstra, "perl": _perl_dijkstra, "c": _c_dijkstra, "rust": _rust_dijkstra},
    "kmp-string-matching": {"javascript": _js_kmp, "typescript": _ts_kmp, "java": _java_kmp, "cpp": _cpp_kmp,
                            "csharp": _csharp_kmp, "perl": _perl_kmp, "c": _c_kmp, "rust": _rust_kmp},
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
                          f"compile={(correct_result.compile_output or '')[:200]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:200]} "
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
            print(f"[{status}] {lang:10s}(program) {pid:24s} {r['outcome']:18s} {r['detail'][:130]}", flush=True)
            if r["outcome"] == "verified":
                row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
                sc = json.loads(row["starter_code"])
                sc[lang] = builders[lang](False)
                con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
                con.commit()
                ledger.record_cell(
                    con, problem_id=pid, language=lang, mode="program",
                    verification_level=ledger.LEVEL_VERIFIED, status="pass",
                    adapter_version=f"{lang}-program-cluster2-v1",
                    test_suite_version=tsv, duration_ms=r["duration_ms"],
                )

    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL attempted: {len(results)}  skipped: {skipped}")
    print(f"verified={len(verified)}  reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    (REPO_ROOT / "docs" / "atlascode-program-mode-cluster2.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
