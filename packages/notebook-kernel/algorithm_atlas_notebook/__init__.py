"""
Algorithm Atlas Notebook — interactive algorithm visualization for Jupyter.

Polyglot: run algorithms in C, C++, Java, C#, or Python and get the same
animated bar-chart visualization as output.

Quick start (SDK algorithms)
    from algorithm_atlas_notebook import run, compare
    run("bubble-sort")
    run("quick-sort", seed=7, array_size=40)
    compare("bubble-sort", "insertion-sort", array_size=30)

Quick start (polyglot — your own code)
    from algorithm_atlas_notebook import run_c, run_java, run_code

    run_c(r'''
    void atlas_sort(int* arr, int n) {
        for (int i=0;i<n-1;i++) for (int j=0;j<n-i-1;j++) {
            ATLAS_COMPARE(arr,n,j,j+1);
            if(arr[j]>arr[j+1]) ATLAS_SWAP(arr,n,j,j+1);
        }
    }
    ''', seed=42, array_size=20)

Cell magics (Jupyter)
    from algorithm_atlas_notebook import register_magics
    register_magics()

    %%atlas_c seed=42 n=20
    void atlas_sort(int* arr, int n) { ... }
"""

from .api     import run, compare
from .display import AtlasDisplay
from .polyglot import (
    run_code,
    run_c,
    run_cpp,
    run_java,
    run_csharp,
    run_python,
)
from .magics import register_magics
from .compilers import available_languages, all_languages

__all__ = [
    # SDK-backed (slug-based)
    "run",
    "compare",
    "AtlasDisplay",
    # Polyglot (source-based)
    "run_code",
    "run_c",
    "run_cpp",
    "run_java",
    "run_csharp",
    "run_python",
    # Jupyter cell magics
    "register_magics",
    # Toolchain introspection
    "available_languages",
    "all_languages",
]
__version__ = "0.5.0"
