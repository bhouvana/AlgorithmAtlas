"""Program Mode expansion, mega batch 4: ports mega_batch1.py's 36 problems
to Ruby -- same rationale as mega_batch3_go.py (proven algorithms, pure
syntax translation). Ruby integers are natively arbitrary-precision, so
none of the overflow/BigInt concerns from JS/C/Java etc. apply here.
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


def sig(shape, fn):
    if shape == "arr1": return f"def {fn}(nums)"
    if shape == "arr1_int": return f"def {fn}(nums, extra)"
    if shape == "int1": return f"def {fn}(n)"
    if shape == "int2": return f"def {fn}(a, b)"
    if shape == "int3": return f"def {fn}(a, b, c)"
    raise ValueError(shape)


def read_code(shape):
    if shape == "arr1":
        return "data = STDIN.read.split\nn = data[0].to_i\nnums = data[1, n].map(&:to_i)"
    if shape == "arr1_int":
        return read_code("arr1") + "\nextra = data[1 + n].to_i"
    if shape == "int1":
        return "n = STDIN.read.strip.to_i"
    if shape == "int2":
        return "data = STDIN.read.split\na = data[0].to_i\nb = data[1].to_i"
    if shape == "int3":
        return "data = STDIN.read.split\na = data[0].to_i\nb = data[1].to_i\nc = data[2].to_i"
    raise ValueError(shape)


def call_args(shape):
    if shape == "arr1": return "nums"
    if shape == "arr1_int": return "nums, extra"
    if shape == "int1": return "n"
    if shape == "int2": return "a, b"
    if shape == "int3": return "a, b, c"
    raise ValueError(shape)


def print_stmt(kind, wrong):
    if kind == "int":
        delta = 1 if wrong else 0
        return f"puts(result + {delta})"
    return f"puts({'!' if wrong else ''}result)"


def assemble(shape, fn, kind, body, wrong):
    read = read_code(shape)
    signature = sig(shape, fn)
    args = call_args(shape)
    func = f"{signature}\n{body}\nreturn result\nend"
    call = f"result = {fn}({args})"
    p = print_stmt(kind, wrong)
    return f"{func}\n\n{read}\n{call}\n{p}\n"


PROBLEMS: dict[str, dict] = {}


def add(pid, shape, fn, kind, body):
    PROBLEMS[pid] = {"shape": shape, "fn": fn, "kind": kind, "body": body}


add("bitonic-peak-index", "arr1", "peak_index", "int",
    "lo = 0\nhi = nums.length - 1\nwhile lo < hi\n  mid = (lo + hi) / 2\n  if nums[mid] < nums[mid + 1] then lo = mid + 1 else hi = mid end\nend\nresult = lo")

add("find-minimum-rotated-sorted-array", "arr1", "find_min", "int",
    "lo = 0\nhi = nums.length - 1\nwhile lo < hi\n  mid = (lo + hi) / 2\n  if nums[mid] > nums[hi] then lo = mid + 1 else hi = mid end\nend\nresult = nums[lo]")

add("count-occurrences-sorted", "arr1_int", "count_occurrences", "int",
    "result = nums.count { |x| x == extra }")

add("last-occurrence", "arr1_int", "last_occurrence", "int",
    "lo = 0\nhi = nums.length - 1\nans = -1\nwhile lo <= hi\n  mid = (lo + hi) / 2\n  if nums[mid] == extra\n    ans = mid\n    lo = mid + 1\n  elsif nums[mid] < extra\n    lo = mid + 1\n  else\n    hi = mid - 1\n  end\nend\nresult = ans")

add("koko-eating-bananas", "arr1_int", "min_eating_speed", "int",
    "lo = 1\nhi = nums.max\nwhile lo < hi\n  mid = (lo + hi) / 2\n  h = nums.reduce(0) { |s, p| s + (p + mid - 1) / mid }\n  if h <= extra then hi = mid else lo = mid + 1 end\nend\nresult = lo")

add("kth-largest-element", "arr1_int", "kth_largest", "int",
    "s = nums.sort\nresult = s[s.length - extra]")

add("largest-rectangle-in-histogram", "arr1", "largest_rectangle", "int",
    "h = nums + [0]\nst = []\nbest = 0\nh.each_with_index do |val, i|\n  while !st.empty? && h[st[-1]] >= val\n    top = st.pop\n    width = st.empty? ? i : i - st[-1] - 1\n    area = h[top] * width\n    best = area if area > best\n  end\n  st.push(i)\nend\nresult = best")

add("longest-bitonic-subsequence", "arr1", "longest_bitonic_subsequence", "int",
    "m = nums.length\ninc = Array.new(m, 1)\ndec = Array.new(m, 1)\n(0...m).each do |i|\n  (0...i).each do |j|\n    inc[i] = inc[j] + 1 if nums[j] < nums[i] && inc[j] + 1 > inc[i]\n  end\nend\n(m - 1).downto(0) do |i|\n  (m - 1).downto(i + 1) do |j|\n    dec[i] = dec[j] + 1 if nums[j] < nums[i] && dec[j] + 1 > dec[i]\n  end\nend\nbest = 0\n(0...m).each { |i| v = inc[i] + dec[i] - 1; best = v if v > best }\nresult = best")

add("max-consecutive-ones-with-k-flips", "arr1_int", "max_consecutive_ones", "int",
    "left = 0\nzeros = 0\nbest = 0\n(0...nums.length).each do |right|\n  zeros += 1 if nums[right] == 0\n  while zeros > extra\n    zeros -= 1 if nums[left] == 0\n    left += 1\n  end\n  len = right - left + 1\n  best = len if len > best\nend\nresult = best")

add("max-sum-subarray-fixed-k", "arr1_int", "max_sum_fixed_k", "int",
    "sum = nums[0, extra].reduce(0, :+)\nbest = sum\n(extra...nums.length).each do |i|\n  sum += nums[i] - nums[i - extra]\n  best = sum if sum > best\nend\nresult = best")

add("maximum-subarray-circular", "arr1", "max_subarray_circular", "int",
    "total = 0\nmax_cur = 0\nmax_best = -(10**18)\nmin_cur = 0\nmin_best = 10**18\nnums.each do |x|\n  total += x\n  max_cur = [x, max_cur + x].max\n  max_best = max_cur if max_cur > max_best\n  min_cur = [x, min_cur + x].min\n  min_best = min_cur if min_cur < min_best\nend\nresult = max_best < 0 ? max_best : [max_best, total - min_best].max")

add("maximum-xor-of-two-numbers", "arr1", "find_maximum_xor", "int",
    "best = 0\n(0...nums.length).each do |i|\n  ((i + 1)...nums.length).each do |j|\n    v = nums[i] ^ nums[j]\n    best = v if v > best\n  end\nend\nresult = best")

add("middle-of-linked-list", "arr1", "middle_node", "int",
    "slow = 0\nfast = 0\nm = nums.length\nwhile fast < m - 1\n  slow += 1\n  fast += 2\nend\nresult = nums[slow]")

add("min-subarray-len-target-sum", "arr1_int", "min_subarray_len", "int",
    "left = 0\nsum = 0\nbest = nil\n(0...nums.length).each do |right|\n  sum += nums[right]\n  while sum >= extra\n    len = right - left + 1\n    best = len if best.nil? || len < best\n    sum -= nums[left]\n    left += 1\n  end\nend\nresult = best.nil? ? 0 : best")

add("partition-equal-subset-sum", "arr1", "can_partition", "bool",
    "total = nums.reduce(0, :+)\nif total.odd?\n  result = false\nelse\n  target = total / 2\n  dp = Array.new(target + 1, false)\n  dp[0] = true\n  nums.each do |x|\n    target.downto(x) do |j|\n      dp[j] = true if dp[j - x]\n    end\n  end\n  result = dp[target]\nend")

add("perfect-squares-min-count", "int1", "num_squares", "int",
    "dp = Array.new(n + 1, Float::INFINITY)\ndp[0] = 0\n(1..n).each do |i|\n  j = 1\n  while j * j <= i\n    dp[i] = dp[i - j * j] + 1 if dp[i - j * j] + 1 < dp[i]\n    j += 1\n  end\nend\nresult = dp[n]")

add("rod-cutting", "arr1", "rod_cutting", "int",
    "m = nums.length\ndp = Array.new(m + 1, 0)\n(1..m).each do |i|\n  best = -(10**18)\n  (1..i).each do |cut|\n    v = nums[cut - 1] + dp[i - cut]\n    best = v if v > best\n  end\n  dp[i] = best\nend\nresult = dp[m]")

add("single-number-ii", "arr1", "single_number", "int",
    "result = 0\n(0...32).each do |bit|\n  cnt = 0\n  nums.each do |x|\n    ux = x < 0 ? x + 4294967296 : x\n    cnt += (ux >> bit) & 1\n  end\n  result += (1 << bit) if cnt % 3 != 0\nend\nresult -= 4294967296 if result >= 2147483648")

add("subset-sum", "arr1_int", "subset_sum", "bool",
    "dp = Array.new(extra + 1, false)\ndp[0] = true\nnums.each do |x|\n  if x <= extra\n    extra.downto(x) do |j|\n      dp[j] = true if dp[j - x]\n    end\n  end\nend\nresult = extra >= 0 ? dp[extra] : false")

add("target-sum-ways", "arr1_int", "find_target_sum_ways", "int",
    "total = nums.reduce(0, :+)\nif (total + extra).odd? || total < extra.abs\n  result = 0\nelse\n  s = (total + extra) / 2\n  dp = Array.new(s + 1, 0)\n  dp[0] = 1\n  nums.each do |x|\n    s.downto(x) do |j|\n      dp[j] += dp[j - x]\n    end\n  end\n  result = dp[s]\nend")

add("two-sum-count-pairs", "arr1_int", "count_pairs", "int",
    "freq = Hash.new(0)\nnums.each { |x| freq[x] += 1 }\nresult = 0\nfreq.each do |v, c|\n  comp = extra - v\n  if comp == v\n    result += c * (c - 1) / 2\n  elsif comp > v\n    result += c * freq[comp]\n  end\nend")

add("unique-permutations-count", "arr1", "count_unique_permutations", "int",
    "freq = Hash.new(0)\nnums.each { |x| freq[x] += 1 }\nnum = (1..nums.length).reduce(1, :*)\ndenom = 1\nfreq.each_value { |c| denom *= (1..c).reduce(1, :*) }\nresult = num / denom")

add("ship-packages-within-days", "arr1_int", "ship_within_days", "int",
    "lo = nums.max\nhi = nums.reduce(0, :+)\nwhile lo < hi\n  mid = (lo + hi) / 2\n  days = 1\n  cur = 0\n  nums.each do |w|\n    if cur + w > mid\n      days += 1\n      cur = w\n    else\n      cur += w\n    end\n  end\n  if days <= extra then hi = mid else lo = mid + 1 end\nend\nresult = lo")

add("subarray-product-less-than-k", "arr1_int", "num_subarray_product_less_than_k", "int",
    "if extra <= 1\n  result = 0\nelse\n  left = 0\n  prod = 1\n  count = 0\n  (0...nums.length).each do |right|\n    prod *= nums[right]\n    while prod >= extra\n      prod /= nums[left]\n      left += 1\n    end\n    count += right - left + 1\n  end\n  result = count\nend")

add("subarray-sums-divisible-by-k", "arr1_int", "subarrays_div_by_k", "int",
    "seen = Hash.new(0)\nseen[0] = 1\nsum = 0\ncount = 0\nnums.each do |x|\n  sum += x\n  r = ((sum % extra) + extra) % extra\n  count += seen[r]\n  seen[r] += 1\nend\nresult = count")

add("euler-phi-sieve", "int1", "euler_phi_sieve", "int",
    "result = n\nnum = n\np = 2\nwhile p * p <= num\n  if num % p == 0\n    while num % p == 0\n      num /= p\n    end\n    result -= result / p\n  end\n  p += 1\nend\nresult -= result / num if num > 1")

add("integer-square-root", "int1", "my_sqrt", "int",
    "lo = 0\nhi = n\nwhile lo < hi\n  mid = (lo + hi + 1) / 2\n  if mid * mid <= n then lo = mid else hi = mid - 1 end\nend\nresult = lo")

add("miller-rabin", "int1", "miller_rabin", "bool",
    "if n < 2\n  result = false\nelse\n  result = true\n  i = 2\n  while i * i <= n\n    if n % i == 0\n      result = false\n      break\n    end\n    i += 1\n  end\nend")

add("number-of-divisors", "int1", "number_of_divisors", "int",
    "count = 0\ni = 1\nwhile i * i <= n\n  if n % i == 0\n    count += (i * i == n) ? 1 : 2\n  end\n  i += 1\nend\nresult = count")

add("palindrome-linked-list", "arr1", "is_palindrome", "bool",
    "lo = 0\nhi = nums.length - 1\nresult = true\nwhile lo < hi\n  if nums[lo] != nums[hi]\n    result = false\n    break\n  end\n  lo += 1\n  hi -= 1\nend")

add("delete-and-earn", "arr1", "delete_and_earn", "int",
    "max_v = nums.max\npoints = Array.new(max_v + 1, 0)\nnums.each { |x| points[x] += x }\nprev2 = 0\nprev1 = 0\npoints.each do |p|\n  cur = [prev1, prev2 + p].max\n  prev2 = prev1\n  prev1 = cur\nend\nresult = prev1")

add("jump-game-ii-min-jumps", "arr1", "jump", "int",
    "jumps = 0\ncur_end = 0\nfarthest = 0\n(0...(nums.length - 1)).each do |i|\n  v = i + nums[i]\n  farthest = v if v > farthest\n  if i == cur_end\n    jumps += 1\n    cur_end = farthest\n  end\nend\nresult = jumps")

add("linked-list-cycle-detect", "arr1_int", "has_cycle", "bool",
    "result = extra != -1")

add("lucas-theorem", "int3", "lucas_theorem", "int",
    "pow_mod = lambda do |base, exp, mod|\n  base = base % mod\n  r = 1\n  while exp > 0\n    r = r * base % mod if exp % 2 == 1\n    base = base * base % mod\n    exp /= 2\n  end\n  r\nend\nsmall_c = lambda do |nn, kk, pp|\n  next 0 if kk < 0 || kk > nn\n  num = 1\n  ((nn - kk + 1)..nn).each { |i| num = num * (i % pp) % pp }\n  den = 1\n  (1..kk).each { |i| den = den * i % pp }\n  num * pow_mod.call(den, pp - 2, pp) % pp\nend\nlucas = lambda do |nn, kk, pp|\n  next 1 % pp if kk == 0\n  ni = nn % pp\n  ki = kk % pp\n  small_c.call(ni, ki, pp) * lucas.call(nn / pp, kk / pp, pp) % pp\nend\nresult = lucas.call(a, b, c)")

add("modular-exponentiation", "int3", "modular_exponentiation", "int",
    "base = a % c\nexp = b\nmod = c\nr = 1 % mod\nwhile exp > 0\n  r = r * base % mod if exp % 2 == 1\n  base = base * base % mod\n  exp /= 2\nend\nresult = r")

add("minimum-knight-moves", "int2", "min_knight_moves", "int",
    "tx = a.abs\nty = b.abs\nqueue = [[0, 0, 0]]\nvisited = { [0, 0] => true }\ndirs = [[1, 2], [2, 1], [-1, 2], [-2, 1], [1, -2], [2, -1], [-1, -2], [-2, -1]]\nans = 0\nuntil queue.empty?\n  x, y, d = queue.shift\n  if x == tx && y == ty\n    ans = d\n    break\n  end\n  dirs.each do |dx, dy|\n    nx = x + dx\n    ny = y + dy\n    if nx >= -2 && ny >= -2 && nx <= tx + 2 && ny <= ty + 2\n      key = [nx, ny]\n      unless visited[key]\n        visited[key] = true\n        queue.push([nx, ny, d + 1])\n      end\n    end\n  end\nend\nresult = ans")


@dataclass
class SimpleCase:
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int


def build_program(pid, wrong):
    spec = PROBLEMS[pid]
    return assemble(spec["shape"], spec["fn"], spec["kind"], spec["body"], wrong)


def load_cases(con, pid):
    cur = con.execute(
        "SELECT id, input_data, expected_output, is_hidden, \"order\" FROM test_cases "
        "WHERE problem_id=? ORDER BY \"order\"", (pid,)
    )
    cases = [SimpleCase(id=r["id"], input_data=r["input_data"], expected_output=r["expected_output"],
                         is_hidden=bool(r["is_hidden"]), order=r["order"]) for r in cur.fetchall()]
    row = con.execute("SELECT test_suite_version FROM problems WHERE id=?", (pid,)).fetchone()
    return cases, row["test_suite_version"]


async def verify_one(pid, cases):
    t0 = time.monotonic()
    correct_result = await evaluate(build_program(pid, False), "ruby", cases)
    if correct_result.tests_passed != correct_result.tests_total:
        extra = correct_result.compile_output or ""
        if not extra and correct_result.test_results:
            for tr in correct_result.test_results:
                if not tr.passed:
                    extra = f"verdict={tr.verdict} stderr={tr.stderr[:150]} actual={tr.actual_output[:60]!r} expected={tr.expected_output[:60]!r}"
                    break
        return {"pid": pid, "outcome": "reference_failed",
                "detail": f"{correct_result.tests_passed}/{correct_result.tests_total} verdict={correct_result.verdict} {extra[:200]}",
                "duration_ms": (time.monotonic() - t0) * 1000}
    wrong_result = await evaluate(build_program(pid, True), "ruby", cases)
    if wrong_result.tests_passed >= wrong_result.tests_total:
        return {"pid": pid, "outcome": "corpus_weakness", "detail": "wrong solution still passed all cases",
                "duration_ms": (time.monotonic() - t0) * 1000}
    return {"pid": pid, "outcome": "verified",
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
        if ledger.already_verified(con, pid, "ruby", "program", test_suite_version=tsv):
            print(f"[SKIP] {pid}/ruby already verified")
            continue
        r = await verify_one(pid, cases)
        results.append(r)
        status = "PASS" if r["outcome"] == "verified" else "FAIL"
        print(f"[{status}] ruby(program) {pid:38s} {r['outcome']:18s} {r['detail'][:140]}", flush=True)
        if r["outcome"] == "verified":
            row = con.execute("SELECT starter_code FROM problems WHERE id=?", (pid,)).fetchone()
            sc = json.loads(row["starter_code"])
            sc["ruby"] = build_program(pid, False)
            con.execute("UPDATE problems SET starter_code=? WHERE id=?", (json.dumps(sc), pid))
            con.commit()
            ledger.record_cell(
                con, problem_id=pid, language="ruby", mode="program",
                verification_level=ledger.LEVEL_VERIFIED, status="pass",
                adapter_version="program-mega-batch4-ruby-v1", test_suite_version=tsv,
                duration_ms=r["duration_ms"],
            )

    verified = [r for r in results if r["outcome"] == "verified"]
    failed = [r for r in results if r["outcome"] != "verified"]
    print(f"\nTOTAL: {len(results)}  verified={len(verified)}  failed={len(failed)}")
    if failed:
        print("\nFAILED CELLS:")
        for r in failed:
            print(f"  {r['pid']}: {r['outcome']} -- {r['detail'][:160]}")
    con.close()
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
