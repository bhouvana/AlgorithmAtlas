"""Program Mode expansion, batch 7a: the 11-problem "searching" family
(binary/linear/jump/exponential/interpolation/fibonacci/ternary search,
rotated-binary-search, first-occurrence, search-insert-position,
subarray-sum-equals-k) ported to the 6 newer languages (go, ruby, kotlin,
php, scala, r) that are still stuck at 40/216 Program Mode coverage.

Reuses the exact shape harness from scale_program_mode_mega_batch6_multilang2.py
UNCHANGED (arr1_int -> int is already supported: read n+nums+target/k,
call fn(nums, extra), print int result; the harness's own print_stmt
already generates the "wrong" variant automatically by printing result+1,
so no separate wrong-body needs to be authored here).
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import logging
logging.disable(logging.CRITICAL)

import scale_program_mode_mega_batch6_multilang2 as harness

add = harness.add

# ═════════════════════════════════════════════════════════════════════════
# binary_search(nums, extra) -> index of extra in SORTED nums, or -1
# ═════════════════════════════════════════════════════════════════════════
add("binary-search", "arr1_int", "binary_search", "int", {
    "go": "lo, hi := 0, len(nums)-1\nresult := int64(-1)\nfor lo <= hi {\n\tmid := (lo + hi) / 2\n\tif nums[mid] == extra { result = int64(mid); break }\n\tif nums[mid] < extra { lo = mid + 1 } else { hi = mid - 1 }\n}",
    "ruby": "lo = 0\nhi = nums.length - 1\nresult = -1\nwhile lo <= hi\n  mid = (lo + hi) / 2\n  if nums[mid] == extra\n    result = mid\n    break\n  elsif nums[mid] < extra\n    lo = mid + 1\n  else\n    hi = mid - 1\n  end\nend",
    "kotlin": "var lo = 0\nvar hi = nums.size - 1\nvar result = -1L\nwhile (lo <= hi) {\n    val mid = (lo + hi) / 2\n    if (nums[mid] == extra) { result = mid.toLong(); break }\n    if (nums[mid] < extra) lo = mid + 1 else hi = mid - 1\n}",
    "php": "$lo = 0; $hi = count($nums) - 1; $result = -1;\nwhile ($lo <= $hi) {\n    $mid = intdiv($lo + $hi, 2);\n    if ($nums[$mid] == $extra) { $result = $mid; break; }\n    if ($nums[$mid] < $extra) { $lo = $mid + 1; } else { $hi = $mid - 1; }\n}",
    "scala": "var lo = 0\nvar hi = nums.length - 1\nvar result: Long = -1L\nvar found = false\nwhile (lo <= hi && !found) {\n  val mid = (lo + hi) / 2\n  if (nums(mid) == extra) { result = mid.toLong(); found = true }\n  else if (nums(mid) < extra) lo = mid + 1\n  else hi = mid - 1\n}",
    "r": "lo <- 1; hi <- length(nums); result <- -1\nwhile (lo <= hi) {\n  mid <- (lo + hi) %/% 2\n  if (nums[mid] == extra) { result <- mid - 1; break }\n  else if (nums[mid] < extra) { lo <- mid + 1 } else { hi <- mid - 1 }\n}",
})

# ═════════════════════════════════════════════════════════════════════════
# linear_search(nums, extra) -> first index of extra, or -1
# ═════════════════════════════════════════════════════════════════════════
add("linear-search", "arr1_int", "linear_search", "int", {
    "go": "result := int64(-1)\nfor i, v := range nums {\n\tif v == extra { result = int64(i); break }\n}",
    "ruby": "result = -1\nnums.each_with_index do |v, i|\n  if v == extra\n    result = i\n    break\n  end\nend",
    "kotlin": "var result = -1L\nfor (i in nums.indices) { if (nums[i] == extra) { result = i.toLong(); break } }",
    "php": "$result = -1;\nforeach ($nums as $i => $v) { if ($v == $extra) { $result = $i; break; } }",
    "scala": "var result: Long = -1L\nvar found = false\nfor (i <- nums.indices if !found) { if (nums(i) == extra) { result = i.toLong(); found = true } }",
    "r": "result <- -1\nif (length(nums) > 0) { for (i in 1:length(nums)) { if (nums[i] == extra) { result <- i - 1; break } } }",
})

# ═════════════════════════════════════════════════════════════════════════
# jump_search(nums, extra) -> index via block-jump then linear scan, or -1
# ═════════════════════════════════════════════════════════════════════════
add("jump-search", "arr1_int", "jump_search", "int", {
    "go": ("n := len(nums)\nresult := int64(-1)\nstep := int(math.Sqrt(float64(n)))\nif step < 1 { step = 1 }\nprev := 0\ncurr := step\nfor curr < n && nums[curr-1] < extra {\n\tprev = curr\n\tcurr += step\n}\nif prev > n { prev = n }\nif curr > n { curr = n }\nfor i := prev; i < curr; i++ {\n\tif nums[i] == extra { result = int64(i); break }\n}"),
    "ruby": ("n = nums.length\nresult = -1\nstep = Math.sqrt(n).to_i\nstep = 1 if step < 1\nprev = 0\ncurr = step\nwhile curr < n && nums[curr - 1] < extra\n  prev = curr\n  curr += step\nend\nprev = n if prev > n\ncurr = n if curr > n\n(prev...curr).each do |i|\n  if nums[i] == extra\n    result = i\n    break\n  end\nend"),
    "kotlin": ("val n = nums.size\nvar result = -1L\nvar step = Math.sqrt(n.toDouble()).toInt()\nif (step < 1) step = 1\nvar prev = 0\nvar curr = step\nwhile (curr < n && nums[curr - 1] < extra) { prev = curr; curr += step }\nif (prev > n) prev = n\nif (curr > n) curr = n\nfor (i in prev until curr) { if (nums[i] == extra) { result = i.toLong(); break } }"),
    "php": ("$n = count($nums);\n$result = -1;\n$step = (int) sqrt($n);\nif ($step < 1) { $step = 1; }\n$prev = 0; $curr = $step;\nwhile ($curr < $n && $nums[$curr - 1] < $extra) { $prev = $curr; $curr += $step; }\nif ($prev > $n) { $prev = $n; }\nif ($curr > $n) { $curr = $n; }\nfor ($i = $prev; $i < $curr; $i++) { if ($nums[$i] == $extra) { $result = $i; break; } }"),
    "scala": ("val n = nums.length\nvar result: Long = -1L\nvar step = math.sqrt(n.toDouble()).toInt\nif (step < 1) step = 1\nvar prev = 0\nvar curr = step\nwhile (curr < n && nums(curr - 1) < extra) { prev = curr; curr += step }\nif (prev > n) prev = n\nif (curr > n) curr = n\nvar found = false\nfor (i <- prev until curr if !found) { if (nums(i) == extra) { result = i.toLong(); found = true } }"),
    "r": ("n <- length(nums)\nresult <- -1\nstep <- as.integer(floor(sqrt(n)))\nif (step < 1) step <- 1\nprev <- 0\ncurr <- step\nwhile (curr < n && nums[curr] < extra) { prev <- curr; curr <- curr + step }\nif (prev > n) prev <- n\nif (curr > n) curr <- n\nif (prev < curr) { for (i in (prev + 1):curr) { if (nums[i] == extra) { result <- i - 1; break } } }"),
})

# ═════════════════════════════════════════════════════════════════════════
# exponential_search(nums, extra) -> range doubling then binary search
# ═════════════════════════════════════════════════════════════════════════
add("exponential-search", "arr1_int", "exponential_search", "int", {
    "go": ("n := len(nums)\nresult := int64(-1)\nif n > 0 {\n\tif nums[0] == extra {\n\t\tresult = 0\n\t} else {\n\t\tbound := 1\n\t\tfor bound < n && nums[bound] < extra { bound *= 2 }\n\t\tlo := bound / 2\n\t\thi := bound\n\t\tif hi >= n { hi = n - 1 }\n\t\tfor lo <= hi {\n\t\t\tmid := (lo + hi) / 2\n\t\t\tif nums[mid] == extra { result = int64(mid); break }\n\t\t\tif nums[mid] < extra { lo = mid + 1 } else { hi = mid - 1 }\n\t\t}\n\t}\n}"),
    "ruby": ("n = nums.length\nresult = -1\nif n > 0\n  if nums[0] == extra\n    result = 0\n  else\n    bound = 1\n    while bound < n && nums[bound] < extra\n      bound *= 2\n    end\n    lo = bound / 2\n    hi = [bound, n - 1].min\n    while lo <= hi\n      mid = (lo + hi) / 2\n      if nums[mid] == extra\n        result = mid\n        break\n      elsif nums[mid] < extra\n        lo = mid + 1\n      else\n        hi = mid - 1\n      end\n    end\n  end\nend"),
    "kotlin": ("val n = nums.size\nvar result = -1L\nif (n > 0) {\n    if (nums[0] == extra) {\n        result = 0L\n    } else {\n        var bound = 1\n        while (bound < n && nums[bound] < extra) bound *= 2\n        var lo = bound / 2\n        var hi = minOf(bound, n - 1)\n        while (lo <= hi) {\n            val mid = (lo + hi) / 2\n            if (nums[mid] == extra) { result = mid.toLong(); break }\n            if (nums[mid] < extra) lo = mid + 1 else hi = mid - 1\n        }\n    }\n}"),
    "php": ("$n = count($nums);\n$result = -1;\nif ($n > 0) {\n    if ($nums[0] == $extra) {\n        $result = 0;\n    } else {\n        $bound = 1;\n        while ($bound < $n && $nums[$bound] < $extra) { $bound *= 2; }\n        $lo = intdiv($bound, 2);\n        $hi = min($bound, $n - 1);\n        while ($lo <= $hi) {\n            $mid = intdiv($lo + $hi, 2);\n            if ($nums[$mid] == $extra) { $result = $mid; break; }\n            if ($nums[$mid] < $extra) { $lo = $mid + 1; } else { $hi = $mid - 1; }\n        }\n    }\n}"),
    "scala": ("val n = nums.length\nvar result: Long = -1L\nif (n > 0) {\n  if (nums(0) == extra) {\n    result = 0L\n  } else {\n    var bound = 1\n    while (bound < n && nums(bound) < extra) bound *= 2\n    var lo = bound / 2\n    var hi = math.min(bound, n - 1)\n    var found = false\n    while (lo <= hi && !found) {\n      val mid = (lo + hi) / 2\n      if (nums(mid) == extra) { result = mid.toLong(); found = true }\n      else if (nums(mid) < extra) lo = mid + 1\n      else hi = mid - 1\n    }\n  }\n}"),
    "r": ("n <- length(nums)\nresult <- -1\nif (n > 0) {\n  if (nums[1] == extra) {\n    result <- 0\n  } else {\n    bound <- 1\n    while (bound < n && nums[bound + 1] < extra) { bound <- bound * 2 }\n    lo <- bound %/% 2 + 1\n    hi <- min(bound + 1, n)\n    while (lo <= hi) {\n      mid <- (lo + hi) %/% 2\n      if (nums[mid] == extra) { result <- mid - 1; break }\n      else if (nums[mid] < extra) { lo <- mid + 1 } else { hi <- mid - 1 }\n    }\n  }\n}"),
})

# ═════════════════════════════════════════════════════════════════════════
# interpolation_search(nums, extra) -> probes by interpolated position
# ═════════════════════════════════════════════════════════════════════════
add("interpolation-search", "arr1_int", "interpolation_search", "int", {
    "go": ("lo, hi := 0, len(nums)-1\nresult := int64(-1)\nfor lo <= hi && extra >= nums[lo] && extra <= nums[hi] {\n\tif nums[hi] == nums[lo] {\n\t\tif nums[lo] == extra { result = int64(lo) }\n\t\tbreak\n\t}\n\tpos := lo + ((extra-nums[lo])*(hi-lo))/(nums[hi]-nums[lo])\n\tif pos < lo || pos > hi { break }\n\tif nums[pos] == extra { result = int64(pos); break }\n\tif nums[pos] < extra { lo = pos + 1 } else { hi = pos - 1 }\n}"),
    "ruby": ("lo = 0\nhi = nums.length - 1\nresult = -1\nwhile lo <= hi && extra >= nums[lo] && extra <= nums[hi]\n  if nums[hi] == nums[lo]\n    result = lo if nums[lo] == extra\n    break\n  end\n  pos = lo + ((extra - nums[lo]) * (hi - lo)) / (nums[hi] - nums[lo])\n  break if pos < lo || pos > hi\n  if nums[pos] == extra\n    result = pos\n    break\n  elsif nums[pos] < extra\n    lo = pos + 1\n  else\n    hi = pos - 1\n  end\nend"),
    "kotlin": ("var lo = 0\nvar hi = nums.size - 1\nvar result = -1L\nwhile (lo <= hi && extra >= nums[lo] && extra <= nums[hi]) {\n    if (nums[hi] == nums[lo]) {\n        if (nums[lo] == extra) result = lo.toLong()\n        break\n    }\n    val pos = lo + ((extra - nums[lo]) * (hi - lo)) / (nums[hi] - nums[lo])\n    if (pos < lo || pos > hi) break\n    if (nums[pos] == extra) { result = pos.toLong(); break }\n    if (nums[pos] < extra) lo = pos + 1 else hi = pos - 1\n}"),
    "php": ("$lo = 0; $hi = count($nums) - 1; $result = -1;\nwhile ($lo <= $hi && $extra >= $nums[$lo] && $extra <= $nums[$hi]) {\n    if ($nums[$hi] == $nums[$lo]) {\n        if ($nums[$lo] == $extra) { $result = $lo; }\n        break;\n    }\n    $pos = $lo + intdiv(($extra - $nums[$lo]) * ($hi - $lo), $nums[$hi] - $nums[$lo]);\n    if ($pos < $lo || $pos > $hi) { break; }\n    if ($nums[$pos] == $extra) { $result = $pos; break; }\n    if ($nums[$pos] < $extra) { $lo = $pos + 1; } else { $hi = $pos - 1; }\n}"),
    "scala": ("var lo = 0\nvar hi = nums.length - 1\nvar result: Long = -1L\nvar stop = false\nwhile (lo <= hi && extra >= nums(lo) && extra <= nums(hi) && !stop) {\n  if (nums(hi) == nums(lo)) {\n    if (nums(lo) == extra) result = lo.toLong()\n    stop = true\n  } else {\n    val pos = lo + ((extra - nums(lo)) * (hi - lo)) / (nums(hi) - nums(lo))\n    if (pos < lo || pos > hi) { stop = true }\n    else if (nums(pos) == extra) { result = pos.toLong(); stop = true }\n    else if (nums(pos) < extra) lo = pos + 1\n    else hi = pos - 1\n  }\n}"),
    "r": ("lo <- 1; hi <- length(nums); result <- -1\nwhile (lo <= hi && extra >= nums[lo] && extra <= nums[hi]) {\n  if (nums[hi] == nums[lo]) {\n    if (nums[lo] == extra) result <- lo - 1\n    break\n  }\n  pos <- lo + ((extra - nums[lo]) * (hi - lo)) %/% (nums[hi] - nums[lo])\n  if (pos < lo || pos > hi) break\n  if (nums[pos] == extra) { result <- pos - 1; break }\n  else if (nums[pos] < extra) { lo <- pos + 1 } else { hi <- pos - 1 }\n}"),
})

# ═════════════════════════════════════════════════════════════════════════
# fibonacci_search(nums, extra) -> classic Fibonacci-search technique
# ═════════════════════════════════════════════════════════════════════════
add("fibonacci-search", "arr1_int", "fibonacci_search", "int", {
    "go": ("n := len(nums)\nresult := int64(-1)\nfibMMm2 := 0\nfibMMm1 := 1\nfibM := fibMMm2 + fibMMm1\nfor fibM < n {\n\tfibMMm2 = fibMMm1\n\tfibMMm1 = fibM\n\tfibM = fibMMm2 + fibMMm1\n}\noffset := -1\nfor fibM > 1 {\n\ti := offset + fibMMm2\n\tif i < n-1 { i = i } else { i = n - 1 }\n\tif i < 0 { i = 0 }\n\tif nums[i] < extra {\n\t\tfibM = fibMMm1\n\t\tfibMMm1 = fibMMm2\n\t\tfibMMm2 = fibM - fibMMm1\n\t\toffset = i\n\t} else if nums[i] > extra {\n\t\tfibM = fibMMm2\n\t\tfibMMm1 = fibMMm1 - fibMMm2\n\t\tfibMMm2 = fibM - fibMMm1\n\t} else {\n\t\tresult = int64(i)\n\t\tbreak\n\t}\n}\nif result == -1 && fibMMm1 == 1 && offset+1 < n && nums[offset+1] == extra {\n\tresult = int64(offset + 1)\n}"),
    "ruby": ("n = nums.length\nresult = -1\nfib_mm2 = 0\nfib_mm1 = 1\nfib_m = fib_mm2 + fib_mm1\nwhile fib_m < n\n  fib_mm2 = fib_mm1\n  fib_mm1 = fib_m\n  fib_m = fib_mm2 + fib_mm1\nend\noffset = -1\nwhile fib_m > 1\n  i = [offset + fib_mm2, n - 1].min\n  i = 0 if i < 0\n  if nums[i] < extra\n    fib_m = fib_mm1\n    fib_mm1 = fib_mm2\n    fib_mm2 = fib_m - fib_mm1\n    offset = i\n  elsif nums[i] > extra\n    fib_m = fib_mm2\n    fib_mm1 = fib_mm1 - fib_mm2\n    fib_mm2 = fib_m - fib_mm1\n  else\n    result = i\n    break\n  end\nend\nif result == -1 && fib_mm1 == 1 && offset + 1 < n && nums[offset + 1] == extra\n  result = offset + 1\nend"),
    "kotlin": ("val n = nums.size\nvar result = -1L\nvar fibMMm2 = 0\nvar fibMMm1 = 1\nvar fibM = fibMMm2 + fibMMm1\nwhile (fibM < n) { fibMMm2 = fibMMm1; fibMMm1 = fibM; fibM = fibMMm2 + fibMMm1 }\nvar offset = -1\nwhile (fibM > 1) {\n    var i = minOf(offset + fibMMm2, n - 1)\n    if (i < 0) i = 0\n    if (nums[i] < extra) {\n        fibM = fibMMm1; fibMMm1 = fibMMm2; fibMMm2 = fibM - fibMMm1; offset = i\n    } else if (nums[i] > extra) {\n        fibM = fibMMm2; fibMMm1 -= fibMMm2; fibMMm2 = fibM - fibMMm1\n    } else {\n        result = i.toLong(); break\n    }\n}\nif (result == -1L && fibMMm1 == 1 && offset + 1 < n && nums[offset + 1] == extra) result = (offset + 1).toLong()"),
    "php": ("$n = count($nums);\n$result = -1;\n$fibMMm2 = 0; $fibMMm1 = 1; $fibM = $fibMMm2 + $fibMMm1;\nwhile ($fibM < $n) { $fibMMm2 = $fibMMm1; $fibMMm1 = $fibM; $fibM = $fibMMm2 + $fibMMm1; }\n$offset = -1;\nwhile ($fibM > 1) {\n    $i = min($offset + $fibMMm2, $n - 1);\n    if ($i < 0) { $i = 0; }\n    if ($nums[$i] < $extra) {\n        $fibM = $fibMMm1; $fibMMm1 = $fibMMm2; $fibMMm2 = $fibM - $fibMMm1; $offset = $i;\n    } elseif ($nums[$i] > $extra) {\n        $fibM = $fibMMm2; $fibMMm1 -= $fibMMm2; $fibMMm2 = $fibM - $fibMMm1;\n    } else {\n        $result = $i; break;\n    }\n}\nif ($result == -1 && $fibMMm1 == 1 && $offset + 1 < $n && $nums[$offset + 1] == $extra) { $result = $offset + 1; }"),
    "scala": ("val n = nums.length\nvar result: Long = -1L\nvar fibMMm2 = 0\nvar fibMMm1 = 1\nvar fibM = fibMMm2 + fibMMm1\nwhile (fibM < n) { fibMMm2 = fibMMm1; fibMMm1 = fibM; fibM = fibMMm2 + fibMMm1 }\nvar offset = -1\nvar found = false\nwhile (fibM > 1 && !found) {\n  var i = math.min(offset + fibMMm2, n - 1)\n  if (i < 0) i = 0\n  if (nums(i) < extra) {\n    fibM = fibMMm1; fibMMm1 = fibMMm2; fibMMm2 = fibM - fibMMm1; offset = i\n  } else if (nums(i) > extra) {\n    fibM = fibMMm2; fibMMm1 -= fibMMm2; fibMMm2 = fibM - fibMMm1\n  } else {\n    result = i.toLong(); found = true\n  }\n}\nif (!found && fibMMm1 == 1 && offset + 1 < n && nums(offset + 1) == extra) result = (offset + 1).toLong()"),
    "r": ("n <- length(nums)\nresult <- -1\nfibMMm2 <- 0; fibMMm1 <- 1; fibM <- fibMMm2 + fibMMm1\nwhile (fibM < n) { fibMMm2 <- fibMMm1; fibMMm1 <- fibM; fibM <- fibMMm2 + fibMMm1 }\noffset <- -1\nfound <- FALSE\nwhile (fibM > 1 && !found) {\n  i <- min(offset + fibMMm2, n - 1)\n  if (i < 0) i <- 0\n  if (nums[i + 1] < extra) {\n    fibM <- fibMMm1; fibMMm1 <- fibMMm2; fibMMm2 <- fibM - fibMMm1; offset <- i\n  } else if (nums[i + 1] > extra) {\n    fibM <- fibMMm2; fibMMm1 <- fibMMm1 - fibMMm2; fibMMm2 <- fibM - fibMMm1\n  } else {\n    result <- i; found <- TRUE\n  }\n}\nif (!found && fibMMm1 == 1 && offset + 1 < n && nums[offset + 2] == extra) result <- offset + 1"),
})

# ═════════════════════════════════════════════════════════════════════════
# ternary_search(nums, extra) -> divide sorted range into 3 parts each step
# ═════════════════════════════════════════════════════════════════════════
add("ternary-search", "arr1_int", "ternary_search", "int", {
    "go": ("lo, hi := 0, len(nums)-1\nresult := int64(-1)\nfor lo <= hi {\n\tthird := (hi - lo) / 3\n\tm1 := lo + third\n\tm2 := hi - third\n\tif nums[m1] == extra { result = int64(m1); break }\n\tif nums[m2] == extra { result = int64(m2); break }\n\tif extra < nums[m1] {\n\t\thi = m1 - 1\n\t} else if extra > nums[m2] {\n\t\tlo = m2 + 1\n\t} else {\n\t\tlo = m1 + 1\n\t\thi = m2 - 1\n\t}\n}"),
    "ruby": ("lo = 0\nhi = nums.length - 1\nresult = -1\nwhile lo <= hi\n  third = (hi - lo) / 3\n  m1 = lo + third\n  m2 = hi - third\n  if nums[m1] == extra\n    result = m1\n    break\n  elsif nums[m2] == extra\n    result = m2\n    break\n  elsif extra < nums[m1]\n    hi = m1 - 1\n  elsif extra > nums[m2]\n    lo = m2 + 1\n  else\n    lo = m1 + 1\n    hi = m2 - 1\n  end\nend"),
    "kotlin": ("var lo = 0\nvar hi = nums.size - 1\nvar result = -1L\nwhile (lo <= hi) {\n    val third = (hi - lo) / 3\n    val m1 = lo + third\n    val m2 = hi - third\n    if (nums[m1] == extra) { result = m1.toLong(); break }\n    if (nums[m2] == extra) { result = m2.toLong(); break }\n    if (extra < nums[m1]) hi = m1 - 1\n    else if (extra > nums[m2]) lo = m2 + 1\n    else { lo = m1 + 1; hi = m2 - 1 }\n}"),
    "php": ("$lo = 0; $hi = count($nums) - 1; $result = -1;\nwhile ($lo <= $hi) {\n    $third = intdiv($hi - $lo, 3);\n    $m1 = $lo + $third;\n    $m2 = $hi - $third;\n    if ($nums[$m1] == $extra) { $result = $m1; break; }\n    if ($nums[$m2] == $extra) { $result = $m2; break; }\n    if ($extra < $nums[$m1]) { $hi = $m1 - 1; }\n    elseif ($extra > $nums[$m2]) { $lo = $m2 + 1; }\n    else { $lo = $m1 + 1; $hi = $m2 - 1; }\n}"),
    "scala": ("var lo = 0\nvar hi = nums.length - 1\nvar result: Long = -1L\nvar found = false\nwhile (lo <= hi && !found) {\n  val third = (hi - lo) / 3\n  val m1 = lo + third\n  val m2 = hi - third\n  if (nums(m1) == extra) { result = m1.toLong(); found = true }\n  else if (nums(m2) == extra) { result = m2.toLong(); found = true }\n  else if (extra < nums(m1)) hi = m1 - 1\n  else if (extra > nums(m2)) lo = m2 + 1\n  else { lo = m1 + 1; hi = m2 - 1 }\n}"),
    "r": ("lo <- 1; hi <- length(nums); result <- -1\nwhile (lo <= hi) {\n  third <- (hi - lo) %/% 3\n  m1 <- lo + third\n  m2 <- hi - third\n  if (nums[m1] == extra) { result <- m1 - 1; break }\n  else if (nums[m2] == extra) { result <- m2 - 1; break }\n  else if (extra < nums[m1]) { hi <- m1 - 1 }\n  else if (extra > nums[m2]) { lo <- m2 + 1 }\n  else { lo <- m1 + 1; hi <- m2 - 1 }\n}"),
})

# ═════════════════════════════════════════════════════════════════════════
# search(nums, extra) -> index of extra in a ROTATED sorted array, or -1
# ═════════════════════════════════════════════════════════════════════════
add("rotated-binary-search", "arr1_int", "search", "int", {
    "go": ("lo, hi := 0, len(nums)-1\nresult := int64(-1)\nfor lo <= hi {\n\tmid := (lo + hi) / 2\n\tif nums[mid] == extra { result = int64(mid); break }\n\tif nums[lo] <= nums[mid] {\n\t\tif nums[lo] <= extra && extra < nums[mid] { hi = mid - 1 } else { lo = mid + 1 }\n\t} else {\n\t\tif nums[mid] < extra && extra <= nums[hi] { lo = mid + 1 } else { hi = mid - 1 }\n\t}\n}"),
    "ruby": ("lo = 0\nhi = nums.length - 1\nresult = -1\nwhile lo <= hi\n  mid = (lo + hi) / 2\n  if nums[mid] == extra\n    result = mid\n    break\n  end\n  if nums[lo] <= nums[mid]\n    if nums[lo] <= extra && extra < nums[mid]\n      hi = mid - 1\n    else\n      lo = mid + 1\n    end\n  else\n    if nums[mid] < extra && extra <= nums[hi]\n      lo = mid + 1\n    else\n      hi = mid - 1\n    end\n  end\nend"),
    "kotlin": ("var lo = 0\nvar hi = nums.size - 1\nvar result = -1L\nwhile (lo <= hi) {\n    val mid = (lo + hi) / 2\n    if (nums[mid] == extra) { result = mid.toLong(); break }\n    if (nums[lo] <= nums[mid]) {\n        if (nums[lo] <= extra && extra < nums[mid]) hi = mid - 1 else lo = mid + 1\n    } else {\n        if (nums[mid] < extra && extra <= nums[hi]) lo = mid + 1 else hi = mid - 1\n    }\n}"),
    "php": ("$lo = 0; $hi = count($nums) - 1; $result = -1;\nwhile ($lo <= $hi) {\n    $mid = intdiv($lo + $hi, 2);\n    if ($nums[$mid] == $extra) { $result = $mid; break; }\n    if ($nums[$lo] <= $nums[$mid]) {\n        if ($nums[$lo] <= $extra && $extra < $nums[$mid]) { $hi = $mid - 1; } else { $lo = $mid + 1; }\n    } else {\n        if ($nums[$mid] < $extra && $extra <= $nums[$hi]) { $lo = $mid + 1; } else { $hi = $mid - 1; }\n    }\n}"),
    "scala": ("var lo = 0\nvar hi = nums.length - 1\nvar result: Long = -1L\nvar found = false\nwhile (lo <= hi && !found) {\n  val mid = (lo + hi) / 2\n  if (nums(mid) == extra) { result = mid.toLong(); found = true }\n  else if (nums(lo) <= nums(mid)) {\n    if (nums(lo) <= extra && extra < nums(mid)) hi = mid - 1 else lo = mid + 1\n  } else {\n    if (nums(mid) < extra && extra <= nums(hi)) lo = mid + 1 else hi = mid - 1\n  }\n}"),
    "r": ("lo <- 1; hi <- length(nums); result <- -1\nwhile (lo <= hi) {\n  mid <- (lo + hi) %/% 2\n  if (nums[mid] == extra) { result <- mid - 1; break }\n  if (nums[lo] <= nums[mid]) {\n    if (nums[lo] <= extra && extra < nums[mid]) { hi <- mid - 1 } else { lo <- mid + 1 }\n  } else {\n    if (nums[mid] < extra && extra <= nums[hi]) { lo <- mid + 1 } else { hi <- mid - 1 }\n  }\n}"),
})

# ═════════════════════════════════════════════════════════════════════════
# first_occurrence(nums, extra) -> leftmost index of extra, or -1
# ═════════════════════════════════════════════════════════════════════════
add("first-occurrence", "arr1_int", "first_occurrence", "int", {
    "go": "lo, hi := 0, len(nums)-1\nresult := int64(-1)\nfor lo <= hi {\n\tmid := (lo + hi) / 2\n\tif nums[mid] == extra { result = int64(mid); hi = mid - 1 } else if nums[mid] < extra { lo = mid + 1 } else { hi = mid - 1 }\n}",
    "ruby": "lo = 0\nhi = nums.length - 1\nresult = -1\nwhile lo <= hi\n  mid = (lo + hi) / 2\n  if nums[mid] == extra\n    result = mid\n    hi = mid - 1\n  elsif nums[mid] < extra\n    lo = mid + 1\n  else\n    hi = mid - 1\n  end\nend",
    "kotlin": "var lo = 0\nvar hi = nums.size - 1\nvar result = -1L\nwhile (lo <= hi) {\n    val mid = (lo + hi) / 2\n    if (nums[mid] == extra) { result = mid.toLong(); hi = mid - 1 }\n    else if (nums[mid] < extra) lo = mid + 1 else hi = mid - 1\n}",
    "php": "$lo = 0; $hi = count($nums) - 1; $result = -1;\nwhile ($lo <= $hi) {\n    $mid = intdiv($lo + $hi, 2);\n    if ($nums[$mid] == $extra) { $result = $mid; $hi = $mid - 1; }\n    elseif ($nums[$mid] < $extra) { $lo = $mid + 1; } else { $hi = $mid - 1; }\n}",
    "scala": "var lo = 0\nvar hi = nums.length - 1\nvar result: Long = -1L\nwhile (lo <= hi) {\n  val mid = (lo + hi) / 2\n  if (nums(mid) == extra) { result = mid.toLong(); hi = mid - 1 }\n  else if (nums(mid) < extra) lo = mid + 1\n  else hi = mid - 1\n}",
    "r": "lo <- 1; hi <- length(nums); result <- -1\nwhile (lo <= hi) {\n  mid <- (lo + hi) %/% 2\n  if (nums[mid] == extra) { result <- mid - 1; hi <- mid - 1 }\n  else if (nums[mid] < extra) { lo <- mid + 1 } else { hi <- mid - 1 }\n}",
})

# ═════════════════════════════════════════════════════════════════════════
# search_insert(nums, extra) -> index where extra is / would be inserted
# ═════════════════════════════════════════════════════════════════════════
add("search-insert-position", "arr1_int", "search_insert", "int", {
    "go": "lo, hi := 0, len(nums)\nfor lo < hi {\n\tmid := (lo + hi) / 2\n\tif nums[mid] < extra { lo = mid + 1 } else { hi = mid }\n}\nresult := int64(lo)",
    "ruby": "lo = 0\nhi = nums.length\nwhile lo < hi\n  mid = (lo + hi) / 2\n  if nums[mid] < extra\n    lo = mid + 1\n  else\n    hi = mid\n  end\nend\nresult = lo",
    "kotlin": "var lo = 0\nvar hi = nums.size\nwhile (lo < hi) {\n    val mid = (lo + hi) / 2\n    if (nums[mid] < extra) lo = mid + 1 else hi = mid\n}\nval result = lo.toLong()",
    "php": "$lo = 0; $hi = count($nums);\nwhile ($lo < $hi) {\n    $mid = intdiv($lo + $hi, 2);\n    if ($nums[$mid] < $extra) { $lo = $mid + 1; } else { $hi = $mid; }\n}\n$result = $lo;",
    "scala": "var lo = 0\nvar hi = nums.length\nwhile (lo < hi) {\n  val mid = (lo + hi) / 2\n  if (nums(mid) < extra) lo = mid + 1 else hi = mid\n}\nval result: Long = lo",
    "r": "lo <- 1; hi <- length(nums) + 1\nwhile (lo < hi) {\n  mid <- (lo + hi) %/% 2\n  if (nums[mid] < extra) { lo <- mid + 1 } else { hi <- mid }\n}\nresult <- lo - 1",
})

# ═════════════════════════════════════════════════════════════════════════
# subarray_sum(nums, extra) -> count of contiguous subarrays summing to
# extra (prefix-sum + hashmap of counts)
# ═════════════════════════════════════════════════════════════════════════
add("subarray-sum-equals-k", "arr1_int", "subarray_sum", "int", {
    "go": ("counts := map[int]int{0: 1}\nsum := 0\nresult := int64(0)\nfor _, v := range nums {\n\tsum += v\n\tif c, ok := counts[sum-extra]; ok { result += int64(c) }\n\tcounts[sum]++\n}"),
    "ruby": "counts = Hash.new(0)\ncounts[0] = 1\nsum = 0\nresult = 0\nnums.each do |v|\n  sum += v\n  result += counts[sum - extra]\n  counts[sum] += 1\nend",
    "kotlin": "val counts = HashMap<Int, Int>()\ncounts[0] = 1\nvar sum = 0\nvar result = 0L\nfor (v in nums) {\n    sum += v\n    result += (counts[sum - extra] ?: 0)\n    counts[sum] = (counts[sum] ?: 0) + 1\n}",
    "php": "$counts = [0 => 1];\n$sum = 0;\n$result = 0;\nforeach ($nums as $v) {\n    $sum += $v;\n    $result += ($counts[$sum - $extra] ?? 0);\n    $counts[$sum] = ($counts[$sum] ?? 0) + 1;\n}",
    "scala": "val counts = scala.collection.mutable.HashMap[Int, Int](0 -> 1).withDefaultValue(0)\nvar sum = 0\nvar result: Long = 0L\nfor (v <- nums) {\n  sum += v\n  result += counts(sum - extra)\n  counts(sum) += 1\n}",
    "r": "counts <- new.env()\nassign('0', 1, envir = counts)\nsum <- 0\nresult <- 0\nfor (v in nums) {\n  sum <- sum + v\n  key <- as.character(sum - extra)\n  if (exists(key, envir = counts)) { result <- result + get(key, envir = counts) }\n  skey <- as.character(sum)\n  if (exists(skey, envir = counts)) { assign(skey, get(skey, envir = counts) + 1, envir = counts) } else { assign(skey, 1, envir = counts) }\n}",
})


if __name__ == "__main__":
    sys.exit(asyncio.run(harness.main()))
