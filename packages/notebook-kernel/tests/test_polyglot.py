"""
Tests for the polyglot compiler backends.

Each test compiles and runs a bubble-sort implementation in one language,
then validates the AtlasDisplay output (frame count, structure, stats).
Tests are skipped automatically when the required toolchain is absent.
"""
import pathlib
import sys

_ROOT = pathlib.Path(__file__).parents[3]
sys.path.insert(0, str(_ROOT / "packages" / "plugin-sdk" / "python"))
sys.path.insert(0, str(_ROOT / "apps" / "backend"))
sys.path.insert(0, str(_ROOT / "packages" / "notebook-kernel"))

import pytest
from algorithm_atlas_notebook import run_c, run_cpp, run_java, run_csharp, run_python
from algorithm_atlas_notebook.compilers import get_compiler, available_languages
from algorithm_atlas_notebook.display import AtlasDisplay

# ── Shared bubble-sort implementations ──────────────────────────────────────

C_BUBBLE = r"""
void atlas_sort(int* arr, int n) {
    int i, j;
    for (i = 0; i < n-1; i++)
        for (j = 0; j < n-i-1; j++) {
            ATLAS_COMPARE(arr, n, j, j+1);
            if (arr[j] > arr[j+1])
                ATLAS_SWAP(arr, n, j, j+1);
        }
}
"""

CPP_BUBBLE = r"""
void atlas_sort(int* arr, int n) {
    for (int i = 0; i < n-1; i++)
        for (int j = 0; j < n-i-1; j++) {
            ATLAS_COMPARE(arr, n, j, j+1);
            if (arr[j] > arr[j+1])
                ATLAS_SWAP(arr, n, j, j+1);
        }
}
"""

JAVA_BUBBLE = """
    static void sort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n-1; i++)
            for (int j = 0; j < n-i-1; j++) {
                compare(j, j+1);
                if (arr[j] > arr[j+1])
                    swap(arr, j, j+1);
            }
    }
"""

CSHARP_BUBBLE = """
    static void Sort(int[] arr) {
        int n = arr.Length;
        for (int i = 0; i < n-1; i++)
            for (int j = 0; j < n-i-1; j++) {
                Compare(j, j+1);
                if (arr[j] > arr[j+1])
                    Swap(arr, j, j+1);
            }
    }
"""

PYTHON_BUBBLE = """
def atlas_sort(arr, cb):
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - i - 1):
            cb(arr, "compare", j, j + 1)
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                cb(arr, "swap", j, j + 1)
"""

N = 8
SEED = 42


# ── Helpers ──────────────────────────────────────────────────────────────────

def _check(result: AtlasDisplay, lang: str):
    assert isinstance(result, AtlasDisplay), f"{lang}: expected AtlasDisplay"
    assert result.total_frames > 1,          f"{lang}: too few frames"
    f0 = result.frames[0]
    assert "state" in f0,                    f"{lang}: frame missing 'state'"
    assert "array" in f0["state"],           f"{lang}: state missing 'array'"
    assert len(f0["state"]["array"]) == N,   f"{lang}: wrong array size"
    assert result.comparisons > 0,           f"{lang}: no comparisons recorded"


# ── C ────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif("c" not in available_languages(), reason="gcc not found")
def test_c_bubble_sort():
    result = run_c(C_BUBBLE, seed=SEED, array_size=N)
    _check(result, "c")

@pytest.mark.skipif("c" not in available_languages(), reason="gcc not found")
def test_c_returns_atlas_display():
    assert isinstance(run_c(C_BUBBLE, seed=1, array_size=6), AtlasDisplay)

@pytest.mark.skipif("c" not in available_languages(), reason="gcc not found")
def test_c_final_frame_sorted():
    result = run_c(C_BUBBLE, seed=SEED, array_size=N)
    last = result.frames[-1]["state"]["array"]
    assert last == sorted(last), "C: final array not sorted"

@pytest.mark.skipif("c" not in available_languages(), reason="gcc not found")
def test_c_input_order_sorted():
    result = run_c(C_BUBBLE, seed=SEED, array_size=N, input_order="sorted")
    assert result.total_frames >= 2

@pytest.mark.skipif("c" not in available_languages(), reason="gcc not found")
def test_c_save_html(tmp_path):
    result = run_c(C_BUBBLE, seed=SEED, array_size=N)
    out = result.save_html(tmp_path / "c_bubble.html")
    assert out.exists()
    assert "<canvas" in out.read_text(encoding="utf-8")


# ── C++ ──────────────────────────────────────────────────────────────────────

@pytest.mark.skipif("cpp" not in available_languages(), reason="g++ not found")
def test_cpp_bubble_sort():
    result = run_cpp(CPP_BUBBLE, seed=SEED, array_size=N)
    _check(result, "cpp")

@pytest.mark.skipif("cpp" not in available_languages(), reason="g++ not found")
def test_cpp_final_frame_sorted():
    result = run_cpp(CPP_BUBBLE, seed=SEED, array_size=N)
    last = result.frames[-1]["state"]["array"]
    assert last == sorted(last), "C++: final array not sorted"


# ── Java ─────────────────────────────────────────────────────────────────────

@pytest.mark.skipif("java" not in available_languages(), reason="javac not found")
def test_java_bubble_sort():
    result = run_java(JAVA_BUBBLE, seed=SEED, array_size=N)
    _check(result, "java")

@pytest.mark.skipif("java" not in available_languages(), reason="javac not found")
def test_java_final_frame_sorted():
    result = run_java(JAVA_BUBBLE, seed=SEED, array_size=N)
    last = result.frames[-1]["state"]["array"]
    assert last == sorted(last), "Java: final array not sorted"

@pytest.mark.skipif("java" not in available_languages(), reason="javac not found")
def test_java_repr_json():
    result = run_java(JAVA_BUBBLE, seed=SEED, array_size=N)
    data = result._repr_json_()
    assert data["seed"] == SEED
    assert len(data["frames"]) == result.total_frames


# ── C# ───────────────────────────────────────────────────────────────────────

@pytest.mark.skipif("csharp" not in available_languages(), reason="dotnet not found")
def test_csharp_bubble_sort():
    result = run_csharp(CSHARP_BUBBLE, seed=SEED, array_size=N)
    _check(result, "csharp")

@pytest.mark.skipif("csharp" not in available_languages(), reason="dotnet not found")
def test_csharp_final_frame_sorted():
    result = run_csharp(CSHARP_BUBBLE, seed=SEED, array_size=N)
    last = result.frames[-1]["state"]["array"]
    assert last == sorted(last), "C#: final array not sorted"


# ── Python ───────────────────────────────────────────────────────────────────

def test_python_bubble_sort():
    result = run_python(PYTHON_BUBBLE, seed=SEED, array_size=N)
    _check(result, "python")

def test_python_final_frame_sorted():
    result = run_python(PYTHON_BUBBLE, seed=SEED, array_size=N)
    last = result.frames[-1]["state"]["array"]
    assert last == sorted(last), "Python: final array not sorted"

def test_python_repr_html():
    result = run_python(PYTHON_BUBBLE, seed=SEED, array_size=N)
    html = result._repr_html_()
    assert "<canvas" in html
    assert "FRAMES" in html

def test_python_comparisons_positive():
    result = run_python(PYTHON_BUBBLE, seed=SEED, array_size=N)
    assert result.comparisons > 0


# ── Cross-language sanity ────────────────────────────────────────────────────

def test_available_languages_includes_python():
    assert "python" in available_languages()

def test_unknown_language_raises():
    from algorithm_atlas_notebook.compilers import get_compiler
    with pytest.raises(ValueError, match="Unknown language"):
        get_compiler("brainfuck")
