"""Ports Scala (Function Mode) solutions for problems missing Scala coverage.

Follows the scale_mega_cluster6.py pattern but targets a single language
(scala) across a much larger batch of problems (~173 missing at start).
Solutions are authored directly in Scala 3 (top-level `def`, immutable
List/String/Boolean/Double/TreeNode types per compiled_adapters.py's
ScalaFunctionAdapter calling convention) rather than ported from another
language's builder, since the algorithms are standard/classic.
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
LANG = "scala"


def _ret(src: str, expr: str) -> str:
    """Replace the __RET__ placeholder in a raw Scala source template."""
    return src.replace("__RET__", expr)


def R_int(wrong: bool, expr: str = "result") -> str:
    return f"({expr}) + 1" if wrong else expr


def R_bool(wrong: bool, expr: str = "result") -> str:
    return f"!({expr})" if wrong else expr


def R_float(wrong: bool, expr: str = "result") -> str:
    return f"({expr}) + 1.0" if wrong else expr


def R_string(wrong: bool, expr: str = "result") -> str:
    return f"({expr}) + \"X\"" if wrong else expr


def R_list_int(wrong: bool, expr: str = "result") -> str:
    return f"({expr}).map(_ + 1)" if wrong else expr


def R_list_list_int(wrong: bool, expr: str = "result") -> str:
    return f"({expr}).map(_.map(_ + 1))" if wrong else expr


def R_list_string(wrong: bool, expr: str = "result") -> str:
    return f"({expr}).map(_ + \"X\")" if wrong else expr


_BUILDERS: dict[str, callable] = {}


def reg(pid):
    def deco(fn):
        _BUILDERS[pid] = fn
        return fn
    return deco


# ══════════════════════════════════════════════════════════════════════════
# Batch 1: basic array / bit / math
# ══════════════════════════════════════════════════════════════════════════

@reg("linear-search")
def _b_linear_search(wrong):
    src = r'''
def linear_search(nums: List[Int], target: Int): Int =
  val result = nums.indexOf(target)
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("first-occurrence")
def _b_first_occurrence(wrong):
    src = r'''
def first_occurrence(nums: List[Int], target: Int): Int =
  val result = nums.indexOf(target)
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("last-occurrence")
def _b_last_occurrence(wrong):
    src = r'''
def last_occurrence(nums: List[Int], target: Int): Int =
  val result = nums.lastIndexOf(target)
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("count-occurrences-sorted")
def _b_count_occurrences_sorted(wrong):
    src = r'''
def count_occurrences(nums: List[Int], target: Int): Int =
  val result = nums.count(_ == target)
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("search-insert-position")
def _b_search_insert_position(wrong):
    src = r'''
def search_insert(nums: List[Int], target: Int): Int =
  var lo = 0
  var hi = nums.length
  while lo < hi do
    val mid = (lo + hi) / 2
    if nums(mid) < target then lo = mid + 1
    else hi = mid
  val result = lo
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("rotated-binary-search")
def _b_rotated_binary_search(wrong):
    src = r'''
def search(nums: List[Int], target: Int): Int =
  var lo = 0
  var hi = nums.length - 1
  var result = -1
  while lo <= hi do
    val mid = (lo + hi) / 2
    if nums(mid) == target then
      result = mid
      lo = hi + 1
    else if nums(lo) <= nums(mid) then
      if nums(lo) <= target && target < nums(mid) then hi = mid - 1
      else lo = mid + 1
    else
      if nums(mid) < target && target <= nums(hi) then lo = mid + 1
      else hi = mid - 1
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("find-minimum-rotated-sorted-array")
def _b_find_minimum_rotated_sorted_array(wrong):
    src = r'''
def find_min(nums: List[Int]): Int =
  var lo = 0
  var hi = nums.length - 1
  while lo < hi do
    val mid = (lo + hi) / 2
    if nums(mid) > nums(hi) then lo = mid + 1
    else hi = mid
  val result = nums(lo)
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("bitonic-peak-index")
def _b_bitonic_peak_index(wrong):
    src = r'''
def peak_index(nums: List[Int]): Int =
  var lo = 0
  var hi = nums.length - 1
  while lo < hi do
    val mid = (lo + hi) / 2
    if nums(mid) < nums(mid + 1) then lo = mid + 1
    else hi = mid
  val result = lo
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("missing-number")
def _b_missing_number(wrong):
    src = r'''
def missing_number(nums: List[Int]): Int =
  val n = nums.length
  val result = n * (n + 1) / 2 - nums.sum
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("single-number")
def _b_single_number(wrong):
    src = r'''
def single_number(nums: List[Int]): Int =
  val result = nums.foldLeft(0)(_ ^ _)
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("single-number-ii")
def _b_single_number_ii(wrong):
    src = r'''
def single_number(nums: List[Int]): Int =
  var ones = 0
  var twos = 0
  for x <- nums do
    ones = (ones ^ x) & ~twos
    twos = (twos ^ x) & ~ones
  val result = ones
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("hamming-distance")
def _b_hamming_distance(wrong):
    src = r'''
def hamming_distance(x: Int, y: Int): Int =
  val result = Integer.bitCount(x ^ y)
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("number-of-1-bits")
def _b_number_of_1_bits(wrong):
    src = r'''
def hamming_weight(n: Int): Int =
  val result = Integer.bitCount(n)
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("reverse-bits")
def _b_reverse_bits(wrong):
    src = r'''
def reverse_bits(n: Int): Int =
  var result = 0
  var x = n
  for i <- 0 until 32 do
    result = (result << 1) | (x & 1)
    x = x >>> 1
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("power-of-two")
def _b_power_of_two(wrong):
    src = r'''
def is_power_of_two(n: Int): Boolean =
  val result = n > 0 && (n & (n - 1)) == 0
  __RET__
'''
    return _ret(src, R_bool(wrong))


@reg("collatz")
def _b_collatz(wrong):
    src = r'''
def collatz(n: Int): Int =
  var x = n.toLong
  var steps = 0
  while x != 1 do
    if x % 2 == 0 then x = x / 2
    else x = 3 * x + 1
    steps += 1
  val result = steps
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("fibonacci-dp")
def _b_fibonacci_dp(wrong):
    src = r'''
def fib(n: Int): Int =
  if n <= 1 then
    val result = n
    __RET__
  else
    var a = 0
    var b = 1
    for i <- 2 to n do
      val c = a + b
      a = b
      b = c
    val result = b
    __RET__
'''
    return _ret(src, R_int(wrong))


@reg("staircase")
def _b_staircase(wrong):
    src = r'''
def climb_stairs(n: Int): Int =
  var a = 1
  var b = 1
  for i <- 2 to n do
    val c = a + b
    a = b
    b = c
  val result = b
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("catalan-number")
def _b_catalan_number(wrong):
    src = r'''
def catalan_number(n: Int): Int =
  val dp = Array.fill(n + 1)(0L)
  dp(0) = 1L
  for i <- 1 to n do
    var s = 0L
    for j <- 0 until i do
      s += dp(j) * dp(i - 1 - j)
    dp(i) = s
  val result = dp(n).toInt
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("integer-square-root")
def _b_integer_square_root(wrong):
    src = r'''
def my_sqrt(n: Int): Int =
  var lo = 0L
  var hi = n.toLong
  while lo < hi do
    val mid = (lo + hi + 1) / 2
    if mid * mid <= n then lo = mid
    else hi = mid - 1
  val result = lo.toInt
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("move-zeroes")
def _b_move_zeroes(wrong):
    src = r'''
def move_zeroes(nums: List[Int]): List[Int] =
  val nonZero = nums.filter(_ != 0)
  val result = nonZero ++ List.fill(nums.length - nonZero.length)(0)
  __RET__
'''
    return _ret(src, R_list_int(wrong))


# ══════════════════════════════════════════════════════════════════════════
# Batch 2: number theory / math
# ══════════════════════════════════════════════════════════════════════════

@reg("fast-power")
def _b_fast_power(wrong):
    src = r'''
def fast_power(base: Int, exp: Int): Int =
  var result0 = 1L
  var b = base.toLong
  var e = exp
  while e > 0 do
    if (e & 1) == 1 then result0 *= b
    b *= b
    e >>= 1
  val result = result0.toInt
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("karatsuba")
def _b_karatsuba(wrong):
    src = r'''
def karatsuba(a: Int, b: Int): Int =
  val result = a.toLong * b.toLong
  val out = result.toInt
  val result2 = out
  __RET__
'''
    return _ret(src, R_int(wrong, "result2"))


@reg("modular-exponentiation")
def _b_modular_exponentiation(wrong):
    src = r'''
def modular_exponentiation(base: Int, exp: Int, mod: Int): Int =
  var r = 1L
  var b = ((base.toLong % mod) + mod) % mod
  var e = exp
  while e > 0 do
    if (e & 1) == 1 then r = (r * b) % mod
    b = (b * b) % mod
    e >>= 1
  val result = r.toInt
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("lucas-theorem")
def _b_lucas_theorem(wrong):
    src = r'''
def lucas_theorem(n: Int, k: Int, p: Int): Int =
  def binomSmall(nn: Int, kk: Int): Long =
    if kk < 0 || kk > nn then 0L
    else
      val c = Array.fill(kk + 1)(0L)
      c(0) = 1L
      for i <- 1 to nn do
        var j = math.min(i, kk)
        while j > 0 do
          c(j) = (c(j) + c(j - 1)) % p
          j -= 1
      c(kk)
  def lucas(nn: Long, kk: Long): Long =
    if kk == 0 then 1L
    else
      val ni = (nn % p).toInt
      val ki = (kk % p).toInt
      if ki > ni then 0L
      else (lucas(nn / p, kk / p) * binomSmall(ni, ki)) % p
  val result = lucas(n.toLong, k.toLong).toInt
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("miller-rabin")
def _b_miller_rabin(wrong):
    src = r'''
def miller_rabin(n: Int): Boolean =
  def power(a: Long, e: Long, m: Long): Long =
    var result0 = 1L
    var base = a % m
    var exp = e
    while exp > 0 do
      if (exp & 1) == 1 then result0 = (result0 * base) % m
      base = (base * base) % m
      exp >>= 1
    result0
  def isComposite(a: Long, d: Long, nn: Long, r: Int): Boolean =
    var x = power(a, d, nn)
    if x == 1L || x == nn - 1L then false
    else
      var i = 0
      var found = false
      var cont = true
      while cont && i < r - 1 do
        x = (x * x) % nn
        if x == nn - 1L then
          found = true
          cont = false
        i += 1
      !found
  val nn = n.toLong
  val result =
    if n < 2 then false
    else if n == 2 || n == 3 then true
    else if n % 2 == 0 then false
    else
      var d = nn - 1
      var r = 0
      while d % 2 == 0 do
        d /= 2
        r += 1
      val witnesses = List(2L, 3L, 5L, 7L, 11L, 13L, 17L, 19L, 23L, 29L, 31L, 37L)
      !witnesses.filter(_ < nn).exists(a => isComposite(a, d, nn, r))
  __RET__
'''
    return _ret(src, R_bool(wrong))


@reg("euler-totient")
def _b_euler_totient(wrong):
    src = r'''
def euler_totient(n: Int): Int =
  var result0 = n
  var x = n
  var p = 2
  while p.toLong * p <= x do
    if x % p == 0 then
      while x % p == 0 do x /= p
      result0 -= result0 / p
    p += 1
  if x > 1 then result0 -= result0 / x
  val result = result0
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("euler-phi-sieve")
def _b_euler_phi_sieve(wrong):
    src = r'''
def euler_phi_sieve(n: Int): Int =
  val phi = Array.tabulate(n + 1)(i => i)
  for i <- 2 to n do
    if phi(i) == i then
      var j = i
      while j <= n do
        phi(j) -= phi(j) / i
        j += i
  val result = phi(n)
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("number-of-divisors")
def _b_number_of_divisors(wrong):
    src = r'''
def number_of_divisors(n: Int): Int =
  var count = 0
  var i = 1
  while i.toLong * i <= n do
    if n % i == 0 then
      count += 1
      if i != n / i then count += 1
    i += 1
  val result = count
  __RET__
'''
    return _ret(src, R_int(wrong))


@reg("sieve-of-eratosthenes")
def _b_sieve_of_eratosthenes(wrong):
    src = r'''
def sieve_of_eratosthenes(n: Int): String =
  if n < 2 then
    val result = ""
    __RET__
  else
    val isComposite = Array.fill(n + 1)(false)
    var i = 2
    while i.toLong * i <= n do
      if !isComposite(i) then
        var j = i * i
        while j <= n do
          isComposite(j) = true
          j += i
      i += 1
    val result = (2 to n).filter(k => !isComposite(k)).mkString(" ")
    __RET__
'''
    return _ret(src, R_string(wrong))


@reg("polynomial-multiplication")
def _b_polynomial_multiplication(wrong):
    src = r'''
def multiply_polynomials(a: List[Int], b: List[Int]): List[Int] =
  if a.isEmpty || b.isEmpty then
    val result = List[Int]()
    __RET__
  else
    val out = Array.fill(a.length + b.length - 1)(0)
    for i <- a.indices do
      for j <- b.indices do
        out(i + j) += a(i) * b(j)
    val result = out.toList
    __RET__
'''
    return _ret(src, R_list_int(wrong))


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


async def verify_one(pid, contract, cases, build):
    t0 = time.monotonic()
    correct_result = await evaluate_function(build(False), LANG, contract, cases)
    n_pass = sum(1 for r in correct_result.case_results if r.passed)
    if n_pass != len(cases):
        sample_fail = next((r for r in correct_result.case_results if not r.passed), None)
        return {"pid": pid, "outcome": "reference_failed",
                "detail": f"{n_pass}/{len(cases)} verdict={correct_result.verdict} "
                          f"compile={(correct_result.compile_output or '')[:200]} "
                          f"stderr={(sample_fail.stderr if sample_fail else '')[:200]} "
                          f"actual={(sample_fail.actual_return if sample_fail else '')!r} "
                          f"expected={(sample_fail.expected_return if sample_fail else '')!r}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate_function(build(True), LANG, contract, cases)
    n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
    if n_wrong_pass >= len(cases):
        return {"pid": pid, "outcome": "corpus_weakness",
                "detail": f"corrupted solution still passed all {len(cases)}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "outcome": "verified",
            "detail": f"{n_pass}/{len(cases)} correct, wrong rejected on {len(cases) - n_wrong_pass}/{len(cases)}",
            "duration_ms": (time.monotonic() - t0) * 1000}


async def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    ledger.ensure_schema(con)
    results = []
    skipped = 0
    for pid, build in _BUILDERS.items():
        contract, cases, tsv = load_problem(con, pid)
        if ledger.already_verified(con, pid, LANG, "function", test_suite_version=tsv):
            skipped += 1
            continue
        r = await verify_one(pid, contract, cases, build)
        results.append(r)
        status = "PASS" if r["outcome"] == "verified" else "FAIL"
        print(f"[{status}] {pid:38s} {r['outcome']:18s} {r['detail'][:180]}", flush=True)
        if r["outcome"] == "verified":
            ledger.record_cell(con, problem_id=pid, language=LANG, mode="function",
                verification_level=ledger.LEVEL_VERIFIED, status="pass",
                adapter_version="scala-function-port-v1", test_suite_version=tsv,
                duration_ms=r["duration_ms"])
    verified = [r for r in results if r["outcome"] == "verified"]
    print(f"\nTOTAL: {len(results)}  skipped(already-verified): {skipped}  verified={len(verified)}  "
          f"reference_failed={sum(1 for r in results if r['outcome']=='reference_failed')}  "
          f"corpus_weakness={sum(1 for r in results if r['outcome']=='corpus_weakness')}")
    con.close()
    return 0 if all(r["outcome"] == "verified" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
