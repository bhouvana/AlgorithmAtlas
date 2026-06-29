"""
IPython cell magics for the Algorithm Atlas polyglot kernel.

Register once per Jupyter session:

    from algorithm_atlas_notebook import register_magics
    register_magics()

Then use in cells:

    %%atlas_c seed=42 n=20
    void atlas_sort(int* arr, int n) {
        // bubble sort in C
    }

    %%atlas_cpp seed=7 n=30 order=reverse
    void atlas_sort(int* arr, int n) {
        // bubble sort in C++
    }

    %%atlas_java seed=42 n=15
    static void sort(int[] arr) {
        // insertion sort in Java
    }

    %%atlas_cs seed=42 n=20
    static void Sort(int[] arr) {
        // selection sort in C#
    }

    %%atlas_py seed=1 n=12
    def atlas_sort(arr, cb):
        // merge sort in Python

Magic line syntax:  seed=<int>  n=<int>  order=random|sorted|reverse
All arguments are optional (defaults: seed=42, n=20, order=random).
"""
from __future__ import annotations

import shlex
from typing import Any


def _parse_line(line: str) -> dict[str, Any]:
    """Parse magic line: 'seed=42 n=20 order=random' → dict."""
    params: dict[str, Any] = {}
    for token in shlex.split(line):
        if "=" in token:
            key, _, val = token.partition("=")
            key = key.strip().lower()
            val = val.strip()
            if key in ("seed",):
                params["seed"] = int(val)
            elif key in ("n", "array_size", "size"):
                params["array_size"] = int(val)
            elif key in ("order", "input_order"):
                params["input_order"] = val
            elif key == "timeout":
                params["timeout"] = int(val)
            elif key == "title":
                params["title"] = val
    return params


def _make_magic(lang: str):
    """Factory — returns an IPython cell magic function for a given language."""
    from .polyglot import run_code

    def magic(line: str, cell: str) -> None:
        try:
            from IPython.display import display  # type: ignore[import]
        except ImportError:
            raise RuntimeError("IPython is required to use cell magics.")

        params = _parse_line(line)
        result = run_code(cell, lang=lang, **params)
        display(result)

    magic.__name__ = f"atlas_{lang}"
    magic.__doc__  = (
        f"Run {lang} algorithm source and display the animated visualization.\n"
        f"Line args: seed=42 n=20 order=random"
    )
    return magic


def register_magics() -> None:
    """
    Register all %%atlas_* cell magics with the current IPython kernel.

    Call once at the top of a notebook:

        from algorithm_atlas_notebook import register_magics
        register_magics()
    """
    try:
        from IPython import get_ipython  # type: ignore[import]
        from IPython.core.magic import register_cell_magic  # type: ignore[import]
    except ImportError:
        raise RuntimeError(
            "register_magics() requires IPython. "
            "Install with: pip install ipython"
        )

    ip = get_ipython()
    if ip is None:
        raise RuntimeError(
            "register_magics() must be called from within a running IPython kernel."
        )

    for lang in ("c", "cpp", "java", "cs", "py"):
        canonical = {"cs": "csharp", "py": "python"}.get(lang, lang)
        fn = _make_magic(canonical)
        register_cell_magic(f"atlas_{lang}")(fn)
        # Also register full name aliases
        if lang == "cs":
            register_cell_magic("atlas_csharp")(_make_magic("csharp"))
        if lang == "py":
            register_cell_magic("atlas_python")(_make_magic("python"))
        if lang == "cpp":
            register_cell_magic("atlas_c++")(_make_magic("cpp"))
