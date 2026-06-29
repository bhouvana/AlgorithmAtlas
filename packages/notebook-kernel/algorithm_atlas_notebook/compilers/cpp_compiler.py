"""
G++ compiler wrapper for Algorithm Atlas polyglot kernel.

User contract
-------------
Write a single C++ function (same signature as C, but STL is available):

    void atlas_sort(int* arr, int n) {
        for (int i = 0; i < n-1; i++) {
            for (int j = 0; j < n-i-1; j++) {
                ATLAS_COMPARE(arr, n, j, j+1);
                if (arr[j] > arr[j+1])
                    ATLAS_SWAP(arr, n, j, j+1);
            }
        }
    }

STL includes (<vector>, <algorithm>, <numeric>, <functional>) are available.
The same ATLAS_COMPARE / ATLAS_SWAP / ATLAS_EMIT macros as the C harness work.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from .base import CompilerBase, CompilerResult

_CPP_HARNESS = r"""
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <algorithm>
#include <numeric>
#include <functional>
#include <string>

/* ── Atlas frame state ──────────────────────────────────────────────── */
static int _at_cmp_a = -1, _at_cmp_b = -1;
static int _at_sw_a  = -1, _at_sw_b  = -1;
static int _at_comparisons = 0, _at_swaps = 0;
static int _at_frame_idx   = 0;

static void _at_emit(int* arr, int n, const char* desc) {
    std::printf("{\"frame_index\":%d,\"state\":{\"array\":[", _at_frame_idx++);
    for (int i = 0; i < n; i++)
        std::printf("%d%s", arr[i], i < n-1 ? "," : "");
    std::printf("],\"comparisons\":%d,\"swaps\":%d,\"comparing\":[",
                _at_comparisons, _at_swaps);
    if (_at_cmp_a >= 0) std::printf("%d,%d", _at_cmp_a, _at_cmp_b);
    std::printf("],\"last_swap\":[");
    if (_at_sw_a >= 0) std::printf("%d,%d", _at_sw_a, _at_sw_b);
    std::printf("],\"sorted_indices\":[],\"description\":\"%s\"}}\n",
                desc ? desc : "");
    std::fflush(stdout);
    _at_cmp_a = _at_cmp_b = _at_sw_a = _at_sw_b = -1;
}

#define ATLAS_COMPARE(arr, n, i, j) do { \
    _at_cmp_a = (i); _at_cmp_b = (j); _at_comparisons++; \
    _at_emit(arr, n, "Comparing"); \
} while(0)

#define ATLAS_SWAP(arr, n, i, j) do { \
    std::swap((arr)[i], (arr)[j]); \
    _at_sw_a = (i); _at_sw_b = (j); _at_swaps++; \
    _at_emit(arr, n, "Swapped"); \
} while(0)

#define ATLAS_EMIT(arr, n, desc) _at_emit(arr, n, desc)

/* ── PRNG (xorshift32) ───────────────────────────────────────────────── */
static unsigned int _at_xorshift32(unsigned int& s) {
    s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s;
}

/* ── Forward declaration ─────────────────────────────────────────────── */
void atlas_sort(int* arr, int n);

/* ── main ────────────────────────────────────────────────────────────── */
int main(int argc, char* argv[]) {
    int seed  = argc > 1 ? std::atoi(argv[1]) : 42;
    int n     = argc > 2 ? std::atoi(argv[2]) : 20;
    const char* ord = argc > 3 ? argv[3] : "random";

    std::vector<int> vec(n);
    unsigned int s = static_cast<unsigned int>(seed <= 0 ? 42 : seed);

    if (std::strcmp(ord, "sorted") == 0) {
        std::iota(vec.begin(), vec.end(), 1);
    } else if (std::strcmp(ord, "reverse") == 0) {
        for (int i = 0; i < n; i++) vec[i] = n - i;
    } else {
        std::iota(vec.begin(), vec.end(), 1);
        for (int i = n-1; i > 0; i--) {
            int j = static_cast<int>(_at_xorshift32(s) % static_cast<unsigned>(i+1));
            std::swap(vec[i], vec[j]);
        }
    }

    int* arr = vec.data();
    _at_emit(arr, n, "Initial state");
    atlas_sort(arr, n);

    std::printf("{\"frame_index\":%d,\"state\":{\"array\":[", _at_frame_idx++);
    for (int i = 0; i < n; i++) std::printf("%d%s", arr[i], i < n-1 ? "," : "");
    std::printf("],\"comparisons\":%d,\"swaps\":%d,"
                "\"comparing\":[],\"last_swap\":[],\"sorted_indices\":[",
                _at_comparisons, _at_swaps);
    for (int i = 0; i < n; i++) std::printf("%d%s", i, i < n-1 ? "," : "");
    std::printf("],\"description\":\"Sorted!\"}}\n");
    return 0;
}

/* ════════════════ USER CODE BELOW ════════════════════════════════════ */
"""


class CppCompiler(CompilerBase):
    name       = "cpp"
    extensions = [".cpp", ".cxx", ".cc"]

    def _required_executables(self) -> list[str]:
        return ["g++"]

    def compile_and_run(
        self,
        source:      str,
        seed:        int,
        array_size:  int,
        input_order: str,
        timeout:     int = 30,
    ) -> CompilerResult:
        if not self.is_available():
            raise self.unavailable_error()

        with tempfile.TemporaryDirectory(prefix="atlas_cpp_") as tmp:
            src = Path(tmp) / "algo.cpp"
            exe = Path(tmp) / "algo.exe"
            src.write_text(_CPP_HARNESS + source, encoding="utf-8")

            compile_proc = subprocess.run(
                ["g++", "-O2", "-std=c++17", "-o", str(exe), str(src)],
                capture_output=True, text=True,
            )
            if compile_proc.returncode != 0:
                return CompilerResult(
                    stdout="",
                    stderr=compile_proc.stderr,
                    returncode=compile_proc.returncode,
                    lang="cpp",
                )

            run_proc = subprocess.run(
                [str(exe), str(seed), str(array_size), input_order],
                capture_output=True, text=True, timeout=timeout,
            )
            return CompilerResult(
                stdout=run_proc.stdout,
                stderr=run_proc.stderr,
                returncode=run_proc.returncode,
                lang="cpp",
            )
