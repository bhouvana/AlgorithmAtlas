"""Records this session's real, subprocess-verified Function Mode results
into the persistent matrix ledger (scripts/atlascode_ledger.py, mission
Phase 1) -- one row per (problem, language, mode) cell, each backed by an
actual judge run performed earlier in this session (never inferred).
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import atlascode_ledger as L

MIN_STACK_LANGUAGES = ["python", "javascript", "typescript", "java", "cpp"]

RUST_LADDER = [
    "two-sum", "min-stack-simulation", "max-depth-binary-tree",
    "construct-tree-preorder-inorder", "bubble-sort", "maximum-subarray",
    "contains-duplicate-within-k", "merge-overlapping-intervals", "prime-factorization",
]

# No tuple support yet (see compiled_adapters.py's C section docstring) --
# min-stack-simulation excluded until that follow-up lands.
C_LADDER = [
    "two-sum", "max-depth-binary-tree", "construct-tree-preorder-inorder",
    "bubble-sort", "maximum-subarray", "contains-duplicate-within-k",
    "merge-overlapping-intervals", "prime-factorization",
]

# C# supports tuple natively (ValueTuple) so min-stack-simulation IS included.
CSHARP_LADDER = [
    "two-sum", "min-stack-simulation", "max-depth-binary-tree",
    "construct-tree-preorder-inorder", "bubble-sort", "maximum-subarray",
    "contains-duplicate-within-k", "merge-overlapping-intervals", "prime-factorization",
]

# Perl's dynamic typing means tuples are just arrayrefs -- no special case,
# so min-stack-simulation IS included here too.
PERL_LADDER = [
    "two-sum", "min-stack-simulation", "max-depth-binary-tree",
    "construct-tree-preorder-inorder", "bubble-sort", "maximum-subarray",
    "contains-duplicate-within-k", "merge-overlapping-intervals", "prime-factorization",
]

# No tuple support yet (same reason as C -- see compiled_adapters.py's Go
# section docstring). min-stack-simulation excluded.
GO_LADDER = [
    "two-sum", "max-depth-binary-tree", "construct-tree-preorder-inorder",
    "bubble-sort", "maximum-subarray", "contains-duplicate-within-k",
    "merge-overlapping-intervals", "prime-factorization",
]

# Ruby's dynamic typing means tuples are just Arrays -- no special case,
# so min-stack-simulation IS included here too.
RUBY_LADDER = [
    "two-sum", "min-stack-simulation", "max-depth-binary-tree",
    "construct-tree-preorder-inorder", "bubble-sort", "maximum-subarray",
    "contains-duplicate-within-k", "merge-overlapping-intervals", "prime-factorization",
]

# PHP's dynamic typing means tuples are just arrays -- no special case,
# so min-stack-simulation IS included here too.
PHP_LADDER = [
    "two-sum", "min-stack-simulation", "max-depth-binary-tree",
    "construct-tree-preorder-inorder", "bubble-sort", "maximum-subarray",
    "contains-duplicate-within-k", "merge-overlapping-intervals", "prime-factorization",
]

# R's fromJSON(simplifyVector=FALSE) decodes tuples as plain nested lists --
# no special case, so min-stack-simulation IS included here too.
R_LADDER = [
    "two-sum", "min-stack-simulation", "max-depth-binary-tree",
    "construct-tree-preorder-inorder", "bubble-sort", "maximum-subarray",
    "contains-duplicate-within-k", "merge-overlapping-intervals", "prime-factorization",
]

# Kotlin's built-in Pair type supports 2-element tuples natively, so
# min-stack-simulation IS included here too.
KOTLIN_LADDER = [
    "two-sum", "min-stack-simulation", "max-depth-binary-tree",
    "construct-tree-preorder-inorder", "bubble-sort", "maximum-subarray",
    "contains-duplicate-within-k", "merge-overlapping-intervals", "prime-factorization",
]

# Scala's native (A, B) tuple type supports 2-element tuples natively, so
# min-stack-simulation IS included here too.
SCALA_LADDER = [
    "two-sum", "min-stack-simulation", "max-depth-binary-tree",
    "construct-tree-preorder-inorder", "bubble-sort", "maximum-subarray",
    "contains-duplicate-within-k", "merge-overlapping-intervals", "prime-factorization",
]

# No tuple support yet (see compiled_adapters.py's Swift section docstring --
# Swift tuples aren't Equatable/Codable/storable in a generic [Any]).
# min-stack-simulation excluded, same as C_LADDER/GO_LADDER.
SWIFT_LADDER = [
    "two-sum", "max-depth-binary-tree", "construct-tree-preorder-inorder",
    "bubble-sort", "maximum-subarray", "contains-duplicate-within-k",
    "merge-overlapping-intervals", "prime-factorization",
]


def main() -> None:
    con = L.connect()
    L.ensure_schema(con)

    dbcon = sqlite3.connect(L.DB_PATH)
    dbcon.row_factory = sqlite3.Row

    def contract_and_suite(pid: str) -> tuple[str | None, str | None]:
        row = dbcon.execute(
            "SELECT function_contract, test_suite_version FROM problems WHERE id=?", (pid,)
        ).fetchone()
        if row is None:
            return None, None
        return L.contract_hash(row["function_contract"]), row["test_suite_version"]

    for lang in MIN_STACK_LANGUAGES:
        cv, tsv = contract_and_suite("min-stack-simulation")
        L.record_cell(
            con, problem_id="min-stack-simulation", language=lang, mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="tuple-ir-v1",
        )

    for pid in RUST_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="rust", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="rust-v1", toolchain_version="rustc 1.96.1 (gnu target via mingw linker)",
        )

    for pid in C_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="c", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="c-v1", toolchain_version="gcc (MinGW-w64 8.1.0)",
        )

    for pid in CSHARP_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="csharp", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="csharp-v1", toolchain_version="dotnet 9.0.200 (dotnet build -o out compile-once)",
        )

    for pid in PERL_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="perl", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="perl-v1", toolchain_version="perl 5.36.1 (Strawberry/MSYS)",
        )

    for pid in GO_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="go", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="go-v1", toolchain_version="go1.23.4 (installed this session, separate GOROOT/GOPATH)",
        )

    for pid in RUBY_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="ruby", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="ruby-v1", toolchain_version="ruby 3.3.6 (RubyInstaller, installed this session)",
        )

    for pid in PHP_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="php", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="php-v1", toolchain_version="php 8.3.32 (installed this session)",
        )

    for pid in R_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="r", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="r-v1", toolchain_version="R 4.6.1 + jsonlite (installed this session)",
        )

    for pid in KOTLIN_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="kotlin", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="kotlin-v1", toolchain_version="kotlinc 2.4.0 (installed this session)",
        )

    for pid in SCALA_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="scala", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="scala-v1", toolchain_version="scala-cli 1.9.4 / Scala 3 (installed this session)",
        )

    for pid in SWIFT_LADDER:
        cv, tsv = contract_and_suite(pid)
        L.record_cell(
            con, problem_id=pid, language="swift", mode="function",
            verification_level=L.LEVEL_VERIFIED, status="pass",
            contract_version=cv, test_suite_version=tsv,
            adapter_version="swift-v1",
            toolchain_version="Swift 6.3.3 for Windows + VS Build Tools 2022 MSVC linker (both installed this session)",
        )

    con.close()
    dbcon.close()
    print(f"Recorded {len(MIN_STACK_LANGUAGES)} min-stack-simulation cells + "
          f"{len(RUST_LADDER)} Rust ladder cells + {len(C_LADDER)} C ladder cells + "
          f"{len(CSHARP_LADDER)} C# ladder cells + {len(PERL_LADDER)} Perl ladder cells + "
          f"{len(GO_LADDER)} Go ladder cells + {len(RUBY_LADDER)} Ruby ladder cells + "
          f"{len(PHP_LADDER)} PHP ladder cells + {len(R_LADDER)} R ladder cells + "
          f"{len(KOTLIN_LADDER)} Kotlin ladder cells + {len(SCALA_LADDER)} Scala ladder cells + "
          f"{len(SWIFT_LADDER)} Swift ladder cells.")


if __name__ == "__main__":
    main()
