"""
GCC compiler wrapper for Algorithm Atlas polyglot kernel.

User contract
-------------
Write a single C function:

    void atlas_sort(int* arr, int n) {
        for (int i = 0; i < n-1; i++) {
            for (int j = 0; j < n-i-1; j++) {
                ATLAS_COMPARE(arr, n, j, j+1);
                if (arr[j] > arr[j+1])
                    ATLAS_SWAP(arr, n, j, j+1);
            }
        }
    }

The harness provides:
  ATLAS_COMPARE(arr, n, i, j)  — emit a "Comparing" frame
  ATLAS_SWAP(arr, n, i, j)     — swap elements and emit a "Swapped" frame
  ATLAS_EMIT(arr, n, desc)     — emit a custom frame (no implicit action)

main(), array generation (xorshift32 Fisher-Yates), and JSON output are
handled automatically.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from .base import CompilerBase, CompilerResult

# ── C harness (prepended to user code) ───────────────────────────────────────

_C_HARNESS = r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ── Atlas frame state ──────────────────────────────────────────────── */
static int _at_cmp_a = -1, _at_cmp_b = -1;
static int _at_sw_a  = -1, _at_sw_b  = -1;
static int _at_comparisons = 0, _at_swaps = 0;
static int _at_frame_idx   = 0;

static void _at_emit(int* arr, int n, const char* desc) {
    int i;
    printf("{\"frame_index\":%d,\"state\":{\"array\":[", _at_frame_idx++);
    for (i = 0; i < n; i++) printf("%d%s", arr[i], i < n-1 ? "," : "");
    printf("],\"comparisons\":%d,\"swaps\":%d,\"comparing\":[",
           _at_comparisons, _at_swaps);
    if (_at_cmp_a >= 0) printf("%d,%d", _at_cmp_a, _at_cmp_b);
    printf("],\"last_swap\":[");
    if (_at_sw_a >= 0) printf("%d,%d", _at_sw_a, _at_sw_b);
    printf("],\"sorted_indices\":[],\"description\":\"%s\"}}\n",
           desc ? desc : "");
    fflush(stdout);
    _at_cmp_a = _at_cmp_b = _at_sw_a = _at_sw_b = -1;
}

#define ATLAS_COMPARE(arr, n, i, j) do { \
    _at_cmp_a = (i); _at_cmp_b = (j); _at_comparisons++; \
    _at_emit(arr, n, "Comparing"); \
} while(0)

#define ATLAS_SWAP(arr, n, i, j) do { \
    int _at_tmp = (arr)[i]; (arr)[i] = (arr)[j]; (arr)[j] = _at_tmp; \
    _at_sw_a = (i); _at_sw_b = (j); _at_swaps++; \
    _at_emit(arr, n, "Swapped"); \
} while(0)

#define ATLAS_EMIT(arr, n, desc) _at_emit(arr, n, desc)

/* ── PRNG (xorshift32, matches Rust engine) ─────────────────────────── */
static unsigned int _at_xorshift32(unsigned int* s) {
    unsigned int x = *s;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    *s = x; return x;
}

/* ── Forward declaration — user implements this below ───────────────── */
void atlas_sort(int* arr, int n);

/* ── main ────────────────────────────────────────────────────────────── */
int main(int argc, char* argv[]) {
    int seed  = argc > 1 ? atoi(argv[1]) : 42;
    int n     = argc > 2 ? atoi(argv[2]) : 20;
    char* ord = argc > 3 ? argv[3] : "random";
    int i, j;

    int* arr = (int*)malloc((size_t)n * sizeof(int));
    if (!arr) { fprintf(stderr, "OOM\n"); return 1; }

    unsigned int s = (unsigned int)(seed <= 0 ? 42 : seed);

    if (strcmp(ord, "sorted") == 0) {
        for (i = 0; i < n; i++) arr[i] = i + 1;
    } else if (strcmp(ord, "reverse") == 0) {
        for (i = 0; i < n; i++) arr[i] = n - i;
    } else {
        /* Fisher-Yates shuffle */
        for (i = 0; i < n; i++) arr[i] = i + 1;
        for (i = n - 1; i > 0; i--) {
            j = (int)(_at_xorshift32(&s) % (unsigned int)(i + 1));
            int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
        }
    }

    _at_emit(arr, n, "Initial state");
    atlas_sort(arr, n);

    /* Final frame — mark all indices sorted */
    printf("{\"frame_index\":%d,\"state\":{\"array\":[", _at_frame_idx++);
    for (i = 0; i < n; i++) printf("%d%s", arr[i], i < n-1 ? "," : "");
    printf("],\"comparisons\":%d,\"swaps\":%d,"
           "\"comparing\":[],\"last_swap\":[],\"sorted_indices\":[",
           _at_comparisons, _at_swaps);
    for (i = 0; i < n; i++) printf("%d%s", i, i < n-1 ? "," : "");
    printf("],\"description\":\"Sorted!\"}}\n");

    free(arr);
    return 0;
}

/* ════════════════ USER CODE BELOW ════════════════════════════════════ */
"""


class CCompiler(CompilerBase):
    name       = "c"
    extensions = [".c"]

    def _required_executables(self) -> list[str]:
        return ["gcc"]

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

        with tempfile.TemporaryDirectory(prefix="atlas_c_") as tmp:
            src  = Path(tmp) / "algo.c"
            exe  = Path(tmp) / "algo.exe"
            src.write_text(_C_HARNESS + source, encoding="utf-8")

            compile_proc = subprocess.run(
                ["gcc", "-O2", "-o", str(exe), str(src), "-lm"],
                capture_output=True, text=True,
            )
            if compile_proc.returncode != 0:
                return CompilerResult(
                    stdout="",
                    stderr=compile_proc.stderr,
                    returncode=compile_proc.returncode,
                    lang="c",
                )

            run_proc = subprocess.run(
                [str(exe), str(seed), str(array_size), input_order],
                capture_output=True, text=True, timeout=timeout,
            )
            return CompilerResult(
                stdout=run_proc.stdout,
                stderr=run_proc.stderr,
                returncode=run_proc.returncode,
                lang="c",
            )
