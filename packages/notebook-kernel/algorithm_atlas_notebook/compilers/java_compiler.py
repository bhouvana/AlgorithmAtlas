"""
Java compiler wrapper for Algorithm Atlas polyglot kernel.

User contract
-------------
Write a single static method named `sort`:

    static void sort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n-1; i++) {
            for (int j = 0; j < n-i-1; j++) {
                compare(j, j+1);
                if (arr[j] > arr[j+1])
                    swap(arr, j, j+1);
            }
        }
    }

Available helpers (in scope, no prefix needed):
  compare(i, j)           - emit a Comparing frame
  swap(arr, i, j)         - swap elements and emit a Swapped frame
  emitFrame(arr, desc)    - emit a custom frame
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from .base import CompilerBase, CompilerResult

# JSON is built using char Q='"' to avoid any Python/Java string-escape collision.

_JAVA_PREFIX = """\
public class AtlasRun {
    public static int[] arr;
    public static int comparisons, swaps;
    private static int frameIdx, cmpA = -1, cmpB = -1, swA = -1, swB = -1;

    /* Frame emission - uses char Q to avoid nested-quote issues */
    private static void emit(String desc) {
        final char Q = '"';
        StringBuilder sb = new StringBuilder();
        sb.append('{').append(Q).append("frame_index").append(Q)
          .append(':').append(frameIdx++)
          .append(',').append(Q).append("state").append(Q).append(":{")
          .append(Q).append("array").append(Q).append(":[");
        for (int i = 0; i < arr.length; i++) {
            if (i > 0) sb.append(',');
            sb.append(arr[i]);
        }
        sb.append("],")
          .append(Q).append("comparisons").append(Q).append(':').append(comparisons)
          .append(',').append(Q).append("swaps").append(Q).append(':').append(swaps)
          .append(',').append(Q).append("comparing").append(Q).append(":[");
        if (cmpA >= 0) sb.append(cmpA).append(',').append(cmpB);
        sb.append("],").append(Q).append("last_swap").append(Q).append(":[");
        if (swA >= 0) sb.append(swA).append(',').append(swB);
        sb.append("],")
          .append(Q).append("sorted_indices").append(Q).append(":[],")
          .append(Q).append("description").append(Q).append(':')
          .append(Q).append(desc).append(Q)
          .append("}}");
        System.out.println(sb);
        System.out.flush();
        cmpA = cmpB = swA = swB = -1;
    }

    public static void compare(int i, int j) {
        cmpA = i; cmpB = j; comparisons++;
        emit("Comparing");
    }

    public static void swap(int[] a, int i, int j) {
        int t = a[i]; a[i] = a[j]; a[j] = t;
        swA = i; swB = j; swaps++;
        emit("Swapped");
    }

    public static void emitFrame(int[] a, String desc) { arr = a; emit(desc); }

    /* PRNG (xorshift32, unsigned via masking) */
    private static int _rng = 0;
    private static int xorshift32() {
        int x = _rng;
        x ^= (x << 13);
        x ^= (x >>> 17);
        x ^= (x << 5);
        _rng = x;
        return x;
    }

    public static void main(String[] args) {
        int seed   = args.length > 0 ? Integer.parseInt(args[0]) : 42;
        int n      = args.length > 1 ? Integer.parseInt(args[1]) : 20;
        String ord = args.length > 2 ? args[2] : "random";

        arr  = new int[n];
        _rng = seed <= 0 ? 42 : seed;

        if ("sorted".equals(ord)) {
            for (int i = 0; i < n; i++) arr[i] = i + 1;
        } else if ("reverse".equals(ord)) {
            for (int i = 0; i < n; i++) arr[i] = n - i;
        } else {
            for (int i = 0; i < n; i++) arr[i] = i + 1;
            for (int i = n - 1; i > 0; i--) {
                int j = (xorshift32() & 0x7fffffff) % (i + 1);
                int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
            }
        }

        emit("Initial state");
        sort(arr);

        /* Final sorted frame */
        final char Q = '"';
        StringBuilder sb = new StringBuilder();
        sb.append('{').append(Q).append("frame_index").append(Q)
          .append(':').append(frameIdx++)
          .append(',').append(Q).append("state").append(Q).append(":{")
          .append(Q).append("array").append(Q).append(":[");
        for (int i = 0; i < n; i++) { if (i > 0) sb.append(','); sb.append(arr[i]); }
        sb.append("],")
          .append(Q).append("comparisons").append(Q).append(':').append(comparisons)
          .append(',').append(Q).append("swaps").append(Q).append(':').append(swaps)
          .append(',').append(Q).append("comparing").append(Q).append(":[],")
          .append(Q).append("last_swap").append(Q).append(":[],")
          .append(Q).append("sorted_indices").append(Q).append(":[");
        for (int i = 0; i < n; i++) { if (i > 0) sb.append(','); sb.append(i); }
        sb.append("],").append(Q).append("description").append(Q).append(':')
          .append(Q).append("Sorted!").append(Q).append("}}");
        System.out.println(sb);
    }

    /* ====== USER CODE BELOW ====================================== */
"""

_JAVA_SUFFIX = "\n}\n"


class JavaCompiler(CompilerBase):
    name       = "java"
    extensions = [".java"]

    def _required_executables(self) -> list[str]:
        return ["javac", "java"]

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

        with tempfile.TemporaryDirectory(prefix="atlas_java_") as tmp:
            src = Path(tmp) / "AtlasRun.java"
            src.write_text(_JAVA_PREFIX + source + _JAVA_SUFFIX, encoding="utf-8")

            compile_proc = subprocess.run(
                ["javac", str(src)],
                capture_output=True, text=True, cwd=tmp,
            )
            if compile_proc.returncode != 0:
                return CompilerResult(
                    stdout="",
                    stderr=compile_proc.stderr,
                    returncode=compile_proc.returncode,
                    lang="java",
                )

            run_proc = subprocess.run(
                ["java", "-cp", tmp, "AtlasRun",
                 str(seed), str(array_size), input_order],
                capture_output=True, text=True, timeout=timeout,
            )
            return CompilerResult(
                stdout=run_proc.stdout,
                stderr=run_proc.stderr,
                returncode=run_proc.returncode,
                lang="java",
            )
