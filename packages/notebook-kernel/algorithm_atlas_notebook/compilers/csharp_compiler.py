"""
C# / .NET compiler wrapper for Algorithm Atlas polyglot kernel.

User contract
-------------
Write a single static method named `Sort`:

    static void Sort(int[] arr) {
        int n = arr.Length;
        for (int i = 0; i < n-1; i++) {
            for (int j = 0; j < n-i-1; j++) {
                Compare(j, j+1);
                if (arr[j] > arr[j+1])
                    Swap(arr, j, j+1);
            }
        }
    }

Available helpers (in scope, no prefix needed):
  Compare(i, j)           - emit a Comparing frame
  Swap(arr, i, j)         - swap elements and emit a Swapped frame
  EmitFrame(arr, desc)    - emit a custom frame

Requires: dotnet (.NET 6+) on PATH.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from .base import CompilerBase, CompilerResult

_CSPROJ = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
    <AllowUnsafeBlocks>true</AllowUnsafeBlocks>
    <Optimize>true</Optimize>
  </PropertyGroup>
</Project>
"""

# JSON built with char q = '"' to avoid Python/C# string-escape collision.
_CS_PREFIX = """\
using System;
using System.Text;

static class Atlas
{
    public static int[] arr = Array.Empty<int>();
    public static int Comparisons;
    public static int Swaps;
    private static int _frameIdx;
    private static int _cmpA = -1, _cmpB = -1, _swA = -1, _swB = -1;

    private static void Emit(string desc)
    {
        const char q = '"';
        var sb = new StringBuilder();
        sb.Append('{').Append(q).Append("frame_index").Append(q)
          .Append(':').Append(_frameIdx++)
          .Append(',').Append(q).Append("state").Append(q).Append(":{")
          .Append(q).Append("array").Append(q).Append(":[");
        for (int i = 0; i < arr.Length; i++) { if (i > 0) sb.Append(','); sb.Append(arr[i]); }
        sb.Append("],")
          .Append(q).Append("comparisons").Append(q).Append(':').Append(Comparisons)
          .Append(',').Append(q).Append("swaps").Append(q).Append(':').Append(Swaps)
          .Append(',').Append(q).Append("comparing").Append(q).Append(":[");
        if (_cmpA >= 0) sb.Append(_cmpA).Append(',').Append(_cmpB);
        sb.Append("],").Append(q).Append("last_swap").Append(q).Append(":[");
        if (_swA >= 0) sb.Append(_swA).Append(',').Append(_swB);
        sb.Append("],")
          .Append(q).Append("sorted_indices").Append(q).Append(":[],")
          .Append(q).Append("description").Append(q).Append(':')
          .Append(q).Append(desc).Append(q)
          .Append("}}");
        Console.WriteLine(sb);
        Console.Out.Flush();
        _cmpA = _cmpB = _swA = _swB = -1;
    }

    public static void Compare(int i, int j) { _cmpA = i; _cmpB = j; Comparisons++; Emit("Comparing"); }

    public static void Swap(int[] a, int i, int j)
    {
        (a[i], a[j]) = (a[j], a[i]);
        _swA = i; _swB = j; Swaps++;
        Emit("Swapped");
    }

    public static void EmitFrame(int[] a, string desc) { arr = a; Emit(desc); }

    private static uint _rng;
    private static uint Xorshift32() { _rng ^= _rng << 13; _rng ^= _rng >> 17; _rng ^= _rng << 5; return _rng; }

    public static void Main(string[] args)
    {
        int seed   = args.Length > 0 ? int.Parse(args[0]) : 42;
        int n      = args.Length > 1 ? int.Parse(args[1]) : 20;
        string ord = args.Length > 2 ? args[2] : "random";

        arr  = new int[n];
        _rng = (uint)(seed <= 0 ? 42 : seed);

        if (ord == "sorted")
            for (int i = 0; i < n; i++) arr[i] = i + 1;
        else if (ord == "reverse")
            for (int i = 0; i < n; i++) arr[i] = n - i;
        else {
            for (int i = 0; i < n; i++) arr[i] = i + 1;
            for (int i = n - 1; i > 0; i--) {
                int j = (int)(Xorshift32() % (uint)(i + 1));
                (arr[i], arr[j]) = (arr[j], arr[i]);
            }
        }

        Emit("Initial state");
        Sort(arr);

        const char q = '"';
        var sb2 = new StringBuilder();
        sb2.Append('{').Append(q).Append("frame_index").Append(q)
           .Append(':').Append(_frameIdx++)
           .Append(',').Append(q).Append("state").Append(q).Append(":{")
           .Append(q).Append("array").Append(q).Append(":[");
        for (int i = 0; i < n; i++) { if (i > 0) sb2.Append(','); sb2.Append(arr[i]); }
        sb2.Append("],")
           .Append(q).Append("comparisons").Append(q).Append(':').Append(Comparisons)
           .Append(',').Append(q).Append("swaps").Append(q).Append(':').Append(Swaps)
           .Append(',').Append(q).Append("comparing").Append(q).Append(":[],")
           .Append(q).Append("last_swap").Append(q).Append(":[],")
           .Append(q).Append("sorted_indices").Append(q).Append(":[");
        for (int i = 0; i < n; i++) { if (i > 0) sb2.Append(','); sb2.Append(i); }
        sb2.Append("],").Append(q).Append("description").Append(q).Append(':')
           .Append(q).Append("Sorted!").Append(q).Append("}}");
        Console.WriteLine(sb2);
    }

    /* ====== USER CODE BELOW ====================================== */
"""

_CS_SUFFIX = "\n}\n"


class CSharpCompiler(CompilerBase):
    name       = "csharp"
    extensions = [".cs"]

    def _required_executables(self) -> list[str]:
        return ["dotnet"]

    def compile_and_run(
        self,
        source:      str,
        seed:        int,
        array_size:  int,
        input_order: str,
        timeout:     int = 60,
    ) -> CompilerResult:
        if not self.is_available():
            raise self.unavailable_error()

        with tempfile.TemporaryDirectory(prefix="atlas_cs_") as tmp:
            Path(tmp, "AtlasRun.csproj").write_text(_CSPROJ, encoding="utf-8")
            Path(tmp, "Program.cs").write_text(
                _CS_PREFIX + source + _CS_SUFFIX, encoding="utf-8"
            )

            run_proc = subprocess.run(
                ["dotnet", "run", "--project", str(Path(tmp, "AtlasRun.csproj")),
                 "--", str(seed), str(array_size), input_order],
                capture_output=True, text=True, timeout=timeout, cwd=tmp,
            )
            return CompilerResult(
                stdout=run_proc.stdout,
                stderr=run_proc.stderr,
                returncode=run_proc.returncode,
                lang="csharp",
            )
