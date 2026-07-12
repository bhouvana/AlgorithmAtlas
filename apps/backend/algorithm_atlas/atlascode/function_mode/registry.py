"""
Honest per-language Function Mode support matrix (Phase 22). Adding a new
language means implementing and registering a FunctionModeAdapter here --
Program Mode support for that language (notebook.py RUNNERS) is completely
unaffected either way.
"""
from __future__ import annotations

from .adapters import (
    FunctionModeAdapter,
    JavaScriptFunctionAdapter,
    PerlFunctionAdapter,
    PhpFunctionAdapter,
    PythonFunctionAdapter,
    RFunctionAdapter,
    RubyFunctionAdapter,
    TypeScriptFunctionAdapter,
)
from .compiled_adapters import (
    CFunctionAdapter,
    CppFunctionAdapter,
    CSharpFunctionAdapter,
    GoFunctionAdapter,
    JavaFunctionAdapter,
    KotlinFunctionAdapter,
    RustFunctionAdapter,
    ScalaFunctionAdapter,
    SwiftFunctionAdapter,
)

# Compile-once adapters (Phase 7/29): these implement compose_program(user_code,
# contract) instead of compose_source(user_code, contract, arguments) --
# runner.py detects this via hasattr and routes through notebook.PREPARERS'
# existing compile-once infrastructure instead of recomposing+recompiling
# full source per test case.
COMPILED_LANGUAGES: frozenset[str] = frozenset(
    {"java", "cpp", "rust", "c", "csharp", "go", "kotlin", "scala", "swift"}
)

ADAPTERS: dict[str, FunctionModeAdapter] = {
    "python": PythonFunctionAdapter(),
    "javascript": JavaScriptFunctionAdapter(),
    "typescript": TypeScriptFunctionAdapter(),
    "java": JavaFunctionAdapter(),
    "cpp": CppFunctionAdapter(),
    "rust": RustFunctionAdapter(),
    "c": CFunctionAdapter(),
    "csharp": CSharpFunctionAdapter(),
    "perl": PerlFunctionAdapter(),
    "go": GoFunctionAdapter(),
    "ruby": RubyFunctionAdapter(),
    "php": PhpFunctionAdapter(),
    "r": RFunctionAdapter(),
    "kotlin": KotlinFunctionAdapter(),
    "scala": ScalaFunctionAdapter(),
    "swift": SwiftFunctionAdapter(),
}


def get_adapter(language: str) -> FunctionModeAdapter | None:
    return ADAPTERS.get(language)


def supported_languages() -> list[str]:
    return sorted(ADAPTERS.keys())


# ── Shell: deliberate policy decision, not a gap (mission Phase 13) ─────────
# Shell (cmd/batch on this Windows deployment; notebook.py's `run_shell`) has
# NO Function Mode adapter and none is planned. This is a considered
# architectural decision, not a missing-implementation gap to fill later:
#
#   - Batch has no JSON parser, no arrays, no structs -- there is no sane way
#     to decode a typed argument map or encode a typed return value without
#     inventing a fake, fragile ad hoc text protocol that wouldn't resemble
#     "calling a function" in any way a real user would recognize.
#   - Batch subroutines (`call :label`) don't have parameters or return
#     values in the sense every other adapter's contract models -- forcing
#     one would misrepresent what the language can actually express.
#
# Shell remains Program Mode ONLY. `docs/atlascode-complete-matrix.json`
# should record this as ARCHITECTURAL_LIMITATION for shell/function, not
# TOOLCHAIN_UNAVAILABLE (the toolchain -- cmd.exe -- is present and working)
# and not "not yet implemented" (nothing here is pending).
SHELL_FUNCTION_MODE_POLICY = "architectural_limitation_program_mode_only"
