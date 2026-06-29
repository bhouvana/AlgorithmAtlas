"""
Compiler registry — maps language names/aliases to CompilerBase instances.

Supported languages (all optional, depend on toolchain availability):
  c, cpp/c++, java, csharp/cs/c#, python/py
"""
from __future__ import annotations

from .base import CompilerBase, CompilerResult, parse_frames
from .c_compiler import CCompiler
from .cpp_compiler import CppCompiler
from .java_compiler import JavaCompiler
from .csharp_compiler import CSharpCompiler
from .python_runner import PythonRunner

# Canonical compiler instances
_COMPILERS: dict[str, CompilerBase] = {
    "c":      CCompiler(),
    "cpp":    CppCompiler(),
    "java":   JavaCompiler(),
    "csharp": CSharpCompiler(),
    "python": PythonRunner(),
}

# Alias map → canonical name
_ALIASES: dict[str, str] = {
    "c":       "c",
    "c++":     "cpp",
    "cpp":     "cpp",
    "cxx":     "cpp",
    "java":    "java",
    "c#":      "csharp",
    "cs":      "csharp",
    "csharp":  "csharp",
    "python":  "python",
    "py":      "python",
}


def get_compiler(lang: str) -> CompilerBase:
    """
    Return the compiler for the given language name or alias.

    Raises ValueError for unknown languages.  Does NOT check availability —
    call compiler.is_available() separately.
    """
    key = _ALIASES.get(lang.lower())
    if key is None:
        raise ValueError(
            f"Unknown language '{lang}'. "
            f"Supported: {sorted(_ALIASES.keys())}"
        )
    return _COMPILERS[key]


def available_languages() -> list[str]:
    """Return canonical names of languages whose toolchain is on PATH."""
    return [name for name, comp in _COMPILERS.items() if comp.is_available()]


def all_languages() -> list[str]:
    """Return all canonical language names regardless of availability."""
    return list(_COMPILERS.keys())


__all__ = [
    "CompilerBase",
    "CompilerResult",
    "parse_frames",
    "get_compiler",
    "available_languages",
    "all_languages",
]
