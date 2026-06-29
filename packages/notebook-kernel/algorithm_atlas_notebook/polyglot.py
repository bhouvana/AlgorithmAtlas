"""
Polyglot run_code() API — compile and visualize algorithms written in any
supported language (C, C++, Java, C#, Python).

Quick start
-----------
    from algorithm_atlas_notebook import run_code

    # C — implement void atlas_sort(int* arr, int n)
    run_code(lang="c", seed=42, array_size=20, source=r'''
    void atlas_sort(int* arr, int n) {
        for (int i = 0; i < n-1; i++)
            for (int j = 0; j < n-i-1; j++) {
                ATLAS_COMPARE(arr, n, j, j+1);
                if (arr[j] > arr[j+1])
                    ATLAS_SWAP(arr, n, j, j+1);
            }
    }
    ''')

    # C++ — same interface, STL available
    # Java — implement static void sort(int[] arr), call compare/swap helpers
    # C#   — implement static void Sort(int[] arr), call Compare/Swap helpers
    # Python — implement def atlas_sort(arr, cb), call cb(arr, "compare", i, j)

Each language-specific shortcut:
    run_c(source, seed=42, array_size=20, input_order="random")
    run_cpp(source, ...)
    run_java(source, ...)
    run_csharp(source, ...)
    run_python(source, ...)
"""
from __future__ import annotations

from typing import Any

from .compilers import get_compiler, available_languages, parse_frames
from .display import AtlasDisplay


def run_code(
    source:      str,
    lang:        str,
    seed:        int  = 42,
    array_size:  int  = 20,
    input_order: str  = "random",
    title:       str  = "",
    timeout:     int  = 60,
) -> AtlasDisplay:
    """
    Compile and run user source code in the given language, return AtlasDisplay.

    Parameters
    ----------
    source      : Algorithm source — see each compiler's docstring for the
                  required function signature and available helpers.
    lang        : Language name or alias. Supported: c, cpp (c++), java,
                  csharp (cs, c#), python (py).
    seed        : PRNG seed for deterministic array generation.
    array_size  : Number of elements in the input array.
    input_order : "random" | "sorted" | "reverse"
    title       : Optional display title (auto-generated if empty).
    timeout     : Compilation + execution timeout in seconds.

    Returns
    -------
    AtlasDisplay — renders as animated bar chart in Jupyter; call
    .save_html("out.html") to export as a static file.

    Raises
    ------
    RuntimeError  : If the toolchain is not available or compilation fails.
    ValueError    : If the language name is not recognised.
    """
    compiler = get_compiler(lang)
    if not compiler.is_available():
        raise compiler.unavailable_error()

    result = compiler.compile_and_run(
        source      = source,
        seed        = seed,
        array_size  = array_size,
        input_order = input_order,
        timeout     = timeout,
    )

    if result.returncode != 0 and not result.stdout.strip():
        stderr_preview = result.stderr[:1000] if result.stderr else "(no output)"
        raise RuntimeError(
            f"[{lang}] compilation/execution failed (exit {result.returncode}):\n"
            + stderr_preview
        )

    frames = parse_frames(result.stdout)
    if not frames:
        stderr_preview = result.stderr[:500] if result.stderr else ""
        raise RuntimeError(
            f"[{lang}] produced no frames. "
            "Check that your function calls the compare/swap helpers.\n"
            + stderr_preview
        )

    slug  = title or f"custom-{compiler.name}"
    label = title or f"{compiler.name}  ·  seed={seed}  ·  n={array_size}"
    return AtlasDisplay(
        frames = frames,
        slug   = slug,
        seed   = seed,
        params = {"array_size": array_size, "input_order": input_order,
                  "lang": compiler.name, "title": label},
    )


# ── Language-specific convenience wrappers ────────────────────────────────────

def run_c(
    source:      str,
    seed:        int = 42,
    array_size:  int = 20,
    input_order: str = "random",
    **kwargs: Any,
) -> AtlasDisplay:
    """Run a C algorithm. Implement: void atlas_sort(int* arr, int n)"""
    return run_code(source, "c", seed=seed, array_size=array_size,
                    input_order=input_order, **kwargs)


def run_cpp(
    source:      str,
    seed:        int = 42,
    array_size:  int = 20,
    input_order: str = "random",
    **kwargs: Any,
) -> AtlasDisplay:
    """Run a C++ algorithm. Implement: void atlas_sort(int* arr, int n)"""
    return run_code(source, "cpp", seed=seed, array_size=array_size,
                    input_order=input_order, **kwargs)


def run_java(
    source:      str,
    seed:        int = 42,
    array_size:  int = 20,
    input_order: str = "random",
    **kwargs: Any,
) -> AtlasDisplay:
    """Run a Java algorithm. Implement: static void sort(int[] arr)"""
    return run_code(source, "java", seed=seed, array_size=array_size,
                    input_order=input_order, **kwargs)


def run_csharp(
    source:      str,
    seed:        int = 42,
    array_size:  int = 20,
    input_order: str = "random",
    **kwargs: Any,
) -> AtlasDisplay:
    """Run a C# algorithm. Implement: static void Sort(int[] arr)"""
    return run_code(source, "csharp", seed=seed, array_size=array_size,
                    input_order=input_order, **kwargs)


def run_python(
    source:      str,
    seed:        int = 42,
    array_size:  int = 20,
    input_order: str = "random",
    **kwargs: Any,
) -> AtlasDisplay:
    """Run a Python algorithm. Implement: def atlas_sort(arr, cb)"""
    return run_code(source, "python", seed=seed, array_size=array_size,
                    input_order=input_order, **kwargs)
