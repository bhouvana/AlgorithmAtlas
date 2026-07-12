"""One-off verification: min-stack-simulation across every currently-
implemented Function Mode language (python/javascript/typescript/java/cpp),
proving the new heterogeneous-tuple TypeSpec (mission Phase 6) actually
executes correctly end-to-end, not just that it deserializes without an
exception. Real subprocess judge runs against the real 40-case corpus, both
a correct solution (must be 40/40 Accepted) and a genuinely-wrong one (must
be rejected on at least one case) per language.
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "apps" / "backend"))
import logging
logging.disable(logging.CRITICAL)

from algorithm_atlas.atlascode.function_mode.contracts import FunctionContract
from algorithm_atlas.atlascode.function_mode.runner import FunctionCase, evaluate_function

DB_PATH = REPO_ROOT / "atlas.db"

CORRECT = {
    "python": (
        "def min_stack_simulate(ops):\n"
        "    stack = []\n"
        "    mins = []\n"
        "    out = []\n"
        "    for cmd, val in ops:\n"
        "        if cmd == 'PUSH':\n"
        "            stack.append(val)\n"
        "            mins.append(val if not mins else min(val, mins[-1]))\n"
        "            out.append(mins[-1])\n"
        "        else:\n"
        "            stack.pop()\n"
        "            mins.pop()\n"
        "    return out\n"
    ),
    "javascript": (
        "function min_stack_simulate(ops) {\n"
        "  var mins = [];\n"
        "  var out = [];\n"
        "  for (var i = 0; i < ops.length; i++) {\n"
        "    var cmd = ops[i][0], val = ops[i][1];\n"
        "    if (cmd === 'PUSH') {\n"
        "      var m = mins.length === 0 ? val : Math.min(val, mins[mins.length - 1]);\n"
        "      mins.push(m);\n"
        "      out.push(m);\n"
        "    } else {\n"
        "      mins.pop();\n"
        "    }\n"
        "  }\n"
        "  return out;\n"
        "}\n"
    ),
    "typescript": (
        "function min_stack_simulate(ops: [string, number | null][]): number[] {\n"
        "  const mins: number[] = [];\n"
        "  const out: number[] = [];\n"
        "  for (const [cmd, val] of ops) {\n"
        "    if (cmd === 'PUSH') {\n"
        "      const m = mins.length === 0 ? (val as number) : Math.min(val as number, mins[mins.length - 1]);\n"
        "      mins.push(m);\n"
        "      out.push(m);\n"
        "    } else {\n"
        "      mins.pop();\n"
        "    }\n"
        "  }\n"
        "  return out;\n"
        "}\n"
    ),
    "java": (
        "class Solution {\n"
        "    public int[] min_stack_simulate(Object[][] ops) {\n"
        "        java.util.List<Integer> mins = new java.util.ArrayList<>();\n"
        "        java.util.List<Integer> out = new java.util.ArrayList<>();\n"
        "        for (Object[] op : ops) {\n"
        "            String cmd = (String) op[0];\n"
        "            if (cmd.equals(\"PUSH\")) {\n"
        "                int val = ((Number) op[1]).intValue();\n"
        "                int m = mins.isEmpty() ? val : Math.min(val, mins.get(mins.size() - 1));\n"
        "                mins.add(m);\n"
        "                out.add(m);\n"
        "            } else {\n"
        "                mins.remove(mins.size() - 1);\n"
        "            }\n"
        "        }\n"
        "        int[] arr = new int[out.size()];\n"
        "        for (int i = 0; i < arr.length; i++) arr[i] = out.get(i);\n"
        "        return arr;\n"
        "    }\n"
        "}\n"
    ),
    "cpp": (
        "class Solution {\n"
        "public:\n"
        "    std::vector<int> min_stack_simulate(std::vector<std::tuple<std::string, std::optional<int>>> ops) {\n"
        "        std::vector<int> mins, out;\n"
        "        for (auto &op : ops) {\n"
        "            std::string cmd = std::get<0>(op);\n"
        "            if (cmd == \"PUSH\") {\n"
        "                int val = *std::get<1>(op);\n"
        "                int m = mins.empty() ? val : std::min(val, mins.back());\n"
        "                mins.push_back(m);\n"
        "                out.push_back(m);\n"
        "            } else {\n"
        "                mins.pop_back();\n"
        "            }\n"
        "        }\n"
        "        return out;\n"
        "    }\n"
        "};\n"
    ),
}

WRONG = {
    "python": CORRECT["python"].replace("min(val, mins[-1])", "max(val, mins[-1])"),
    "javascript": CORRECT["javascript"].replace("Math.min(val, mins[mins.length - 1])", "Math.max(val, mins[mins.length - 1])"),
    "typescript": CORRECT["typescript"].replace(
        "Math.min(val as number, mins[mins.length - 1])", "Math.max(val as number, mins[mins.length - 1])"
    ),
    "java": CORRECT["java"].replace("Math.min(val, mins.get(mins.size() - 1))", "Math.max(val, mins.get(mins.size() - 1))"),
    "cpp": CORRECT["cpp"].replace("std::min(val, mins.back())", "std::max(val, mins.back())"),
}


async def main() -> int:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT function_contract FROM problems WHERE id='min-stack-simulation'").fetchone()
    contract = FunctionContract.from_dict(json.loads(row["function_contract"]))
    case_rows = con.execute(
        "SELECT id, function_args, function_expected, \"order\" FROM test_cases "
        "WHERE problem_id='min-stack-simulation' AND function_args IS NOT NULL ORDER BY \"order\""
    ).fetchall()
    cases = [
        FunctionCase(
            id=r["id"], arguments=json.loads(r["function_args"]), expected=json.loads(r["function_expected"]),
            has_expected=True, is_hidden=False, order=r["order"],
        )
        for r in case_rows
    ]
    con.close()
    print(f"min-stack-simulation: {len(cases)} test cases loaded\n")

    all_ok = True
    for lang in ("python", "javascript", "typescript", "java", "cpp"):
        print(f"=== {lang} ===")
        correct_result = await evaluate_function(CORRECT[lang], lang, contract, cases)
        n_pass = sum(1 for r in correct_result.case_results if r.passed)
        print(f"  correct solution: {n_pass}/{len(cases)} verdict={correct_result.verdict}")
        if n_pass != len(cases):
            all_ok = False
            for r in correct_result.case_results:
                if not r.passed:
                    print(f"    FIRST FAILURE: args={r.arguments} expected={r.expected_return} "
                          f"actual={r.actual_return} verdict={r.verdict} stderr={r.stderr[:400]}")
                    break
            if correct_result.compile_output:
                print(f"    compile_output: {correct_result.compile_output[:800]}")

        wrong_result = await evaluate_function(WRONG[lang], lang, contract, cases)
        n_wrong_pass = sum(1 for r in wrong_result.case_results if r.passed)
        rejected = n_wrong_pass < len(cases)
        print(f"  wrong solution:   {n_wrong_pass}/{len(cases)} passed (rejected={rejected})")
        if not rejected:
            all_ok = False
            print("    WEAK CORPUS -- corrupted solution still passed everything")
        print()

    print("ALL LANGUAGES LEVEL 6 VERIFIED" if all_ok else "SOME LANGUAGES FAILED -- see above")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
