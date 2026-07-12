"""
Notebook execution endpoint — polyglot code runner.

POST /api/v1/notebook/run
  body: { "source": "...", "language": "python", "timeout": 10 }
  resp: { "output": "...", "error": "...", "duration_ms": ..., "language": "..." }

Supported languages:
  python, javascript, typescript, cpp, c, java, go, rust, shell, ruby,
  kotlin, swift, r, csharp, php, scala, perl
"""
from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Callable

import psutil
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...models.experiment import NotebookCell

router = APIRouter(prefix="/notebook", tags=["notebook"])

MAX_TIMEOUT = 30

# Ensure rustc/cargo (installed via rustup) are on PATH at runtime
_CARGO_BIN = Path.home() / ".cargo" / "bin"
if _CARGO_BIN.is_dir() and str(_CARGO_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = str(_CARGO_BIN) + os.pathsep + os.environ.get("PATH", "")


class RunRequest(BaseModel):
    source: str = Field(..., max_length=65_536)
    language: str = "python"
    timeout: float = Field(10.0, gt=0, le=MAX_TIMEOUT)
    input_data: str | None = None  # stdin content for problem test-case evaluation


class RunResponse(BaseModel):
    output: str
    error: str
    duration_ms: float
    language: str
    # Additive fields (optional, default None) so existing notebook-feature
    # consumers that only read output/error/duration_ms/language are unaffected.
    exit_code: int | None = None
    memory_kb: float | None = None
    compile_output: str | None = None


# ── Rich execution result ───────────────────────────────────────────────────────
#
# ExecResult is the low-level, single-process result (one subprocess launch).
# LangRunResult is what every per-language `run_*`/`prepare_*` function returns
# to callers (notebook endpoints AND the AtlasCode judge evaluator) — it
# distinguishes a compile failure from a run failure and carries real,
# measured peak memory instead of a placeholder.
#
# Memory measurement: sampled via psutil while the subprocess is alive (a
# background thread runs Popen.communicate() so this thread is free to poll).
# On Windows, psutil reports `peak_wset` (the OS's own tracked peak working
# set), so even sparse sampling reflects the true peak up to that sample. On
# POSIX, psutil only exposes current `rss`, so the running max across polls is
# an approximation bounded by the polling interval, not a kernel-tracked peak
# — documented in docs/atlascode-judge-workspace.md. A process that completes
# faster than one poll interval yields memory_kb=None (honestly "not
# captured"), never a fabricated value.

@dataclass
class ExecResult:
    stdout: str
    stderr: str
    duration_ms: float
    exit_code: int | None
    timed_out: bool = False
    memory_kb: float | None = None


@dataclass
class LangRunResult:
    stdout: str
    stderr: str
    duration_ms: float
    exit_code: int | None
    timed_out: bool = False
    memory_kb: float | None = None
    compile_output: str | None = None   # non-None only for a failed compile step
    compile_failed: bool = False


_executor = ThreadPoolExecutor(max_workers=8)
_MEM_POLL_INTERVAL_S = 0.003


def _peak_memory_sample(ps_proc: "psutil.Process | None") -> float | None:
    if ps_proc is None:
        return None
    try:
        mem = ps_proc.memory_info()
    except psutil.Error:
        return None
    # `peak_wset` (Windows) is the OS-tracked peak; fall back to current `rss`
    # (POSIX) — the caller keeps a running max across polls either way.
    value = getattr(mem, "peak_wset", None)
    return float(value if value is not None else mem.rss)


def _run_sync(
    cmd: list[str], timeout: float, cwd: str | None = None, input_bytes: bytes | None = None
) -> ExecResult:
    """Launch `cmd`, sampling peak memory while it runs.

    Uses Popen + a background communicate() thread (rather than
    subprocess.run) so this thread is free to poll psutil for memory while
    the child is alive — subprocess.run blocks until exit, which is too late
    to observe a short-lived process's memory at all.
    """
    t0 = time.perf_counter()
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE if input_bytes is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
        )
    except FileNotFoundError as exc:
        name = exc.filename or (cmd[0] if cmd else "unknown")
        elapsed = (time.perf_counter() - t0) * 1000
        return ExecResult(
            stdout="",
            stderr=(
                f"Runtime not available: '{name}' was not found. "
                "This language may require additional setup in the current environment."
            ),
            duration_ms=elapsed,
            exit_code=127,
        )
    except Exception as exc:
        elapsed = (time.perf_counter() - t0) * 1000
        return ExecResult(stdout="", stderr=str(exc), duration_ms=elapsed, exit_code=1)

    outcome: dict[str, object] = {}

    def _communicate() -> None:
        try:
            out, err = proc.communicate(input=input_bytes, timeout=timeout)
            outcome["stdout"], outcome["stderr"] = out, err
        except subprocess.TimeoutExpired:
            outcome["timed_out"] = True
        except Exception as exc:  # pragma: no cover - defensive
            outcome["error"] = str(exc)

    comm_thread = threading.Thread(target=_communicate, daemon=True)
    comm_thread.start()

    try:
        ps_proc = psutil.Process(proc.pid)
    except psutil.Error:
        ps_proc = None

    deadline = t0 + timeout
    peak_bytes = 0.0
    while comm_thread.is_alive() and time.perf_counter() < deadline:
        sample = _peak_memory_sample(ps_proc)
        if sample is not None:
            peak_bytes = max(peak_bytes, sample)
        time.sleep(_MEM_POLL_INTERVAL_S)

    comm_thread.join(timeout=max(0.0, deadline - time.perf_counter()) + 0.5)
    elapsed = (time.perf_counter() - t0) * 1000
    memory_kb = (peak_bytes / 1024) if peak_bytes > 0 else None

    if outcome.get("timed_out") or comm_thread.is_alive():
        try:
            proc.kill()
            proc.wait(timeout=2)
        except Exception:  # pragma: no cover - best effort cleanup
            pass
        return ExecResult(
            stdout="",
            stderr=f"TimeoutError: execution exceeded {timeout}s limit",
            duration_ms=elapsed,
            exit_code=None,
            timed_out=True,
            memory_kb=memory_kb,
        )

    if "error" in outcome:
        return ExecResult(stdout="", stderr=str(outcome["error"]), duration_ms=elapsed, exit_code=1)

    out = (outcome.get("stdout") or b"").decode("utf-8", errors="replace")  # type: ignore[union-attr]
    err = (outcome.get("stderr") or b"").decode("utf-8", errors="replace")  # type: ignore[union-attr]
    return ExecResult(
        stdout=out, stderr=err, duration_ms=elapsed, exit_code=proc.returncode, memory_kb=memory_kb,
    )


async def _run_subprocess(
    cmd: list[str], timeout: float, cwd: str | None = None, input_bytes: bytes | None = None
) -> ExecResult:
    loop = asyncio.get_event_loop()
    fn = partial(_run_sync, cmd, timeout, cwd, input_bytes)
    return await loop.run_in_executor(_executor, fn)


async def _compile_and_run(
    source: str,
    suffix: str,
    timeout: float,
    build_cmd_fn,
    run_cmd_fn,
    input_bytes: bytes | None = None,
) -> LangRunResult:
    """Write source to a temp dir, compile, then run. Uses returncode to detect errors."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / f"main{suffix}"
        src.write_text(source, encoding="utf-8")

        # Compile (no stdin)
        build_cmd = build_cmd_fn(src, tmp)
        build = await _run_subprocess(build_cmd, timeout, cwd=tmp)
        if build.exit_code != 0:
            combined_err = (build.stderr or build.stdout).strip() or (
                f"Compilation failed (exit code {build.exit_code})"
            )
            return LangRunResult(
                stdout="", stderr=combined_err, duration_ms=build.duration_ms,
                exit_code=build.exit_code, compile_output=combined_err, compile_failed=True,
            )

        remaining = max(1.0, timeout - build.duration_ms / 1000)

        # Run (inject stdin for problem evaluation)
        run_cmd = run_cmd_fn(src, tmp)
        run = await _run_subprocess(run_cmd, remaining, cwd=tmp, input_bytes=input_bytes)
        return LangRunResult(
            stdout=run.stdout, stderr=run.stderr, duration_ms=build.duration_ms + run.duration_ms,
            exit_code=run.exit_code, timed_out=run.timed_out, memory_kb=run.memory_kb,
        )


# ── Compile-once-per-submission ─────────────────────────────────────────────────
#
# The AtlasCode judge runs the SAME source against up to 40 test cases. Calling
# a single-shot run_* function (which compiles from scratch) once per case
# would recompile identical source up to 40 times — measured at ~460-490ms per
# g++ compile+run of a trivial program, i.e. ~18-20s of pure recompilation
# overhead for one C++ submission. PreparedProgram compiles once and is then
# invoked per test case with only the run step re-executed.

@dataclass
class PreparedProgram:
    run_cmd: list[str]
    cwd: str
    cleanup: Callable[[], None]


async def _prepare_compiled(
    source: str, suffix: str, timeout: float, build_cmd_fn, run_cmd_fn,
) -> tuple[PreparedProgram | None, LangRunResult | None]:
    """Compile once. Returns (prepared, None) on success, (None, failure) on a
    compile error. Caller MUST call prepared.cleanup() once every test case
    has run against it."""
    tmp = tempfile.mkdtemp()
    src = Path(tmp) / f"main{suffix}"
    src.write_text(source, encoding="utf-8")

    build_cmd = build_cmd_fn(src, tmp)
    build = await _run_subprocess(build_cmd, timeout, cwd=tmp)
    if build.exit_code != 0:
        combined_err = (build.stderr or build.stdout).strip() or (
            f"Compilation failed (exit code {build.exit_code})"
        )
        shutil.rmtree(tmp, ignore_errors=True)
        return None, LangRunResult(
            stdout="", stderr=combined_err, duration_ms=build.duration_ms,
            exit_code=build.exit_code, compile_output=combined_err, compile_failed=True,
        )

    run_cmd = run_cmd_fn(src, tmp)
    return PreparedProgram(run_cmd=run_cmd, cwd=tmp, cleanup=lambda: shutil.rmtree(tmp, ignore_errors=True)), None


async def _run_prepared(prepared: PreparedProgram, timeout: float, input_bytes: bytes | None) -> LangRunResult:
    r = await _run_subprocess(prepared.run_cmd, timeout, cwd=prepared.cwd, input_bytes=input_bytes)
    return LangRunResult(
        stdout=r.stdout, stderr=r.stderr, duration_ms=r.duration_ms,
        exit_code=r.exit_code, timed_out=r.timed_out, memory_kb=r.memory_kb,
    )


# ── Per-language runners ────────────────────────────────────────────────────────
# Every runner returns LangRunResult (real exit_code/memory_kb/compile_output),
# not a bare tuple — see the dataclass definitions above.

def _simple(r: ExecResult) -> LangRunResult:
    return LangRunResult(
        stdout=r.stdout, stderr=r.stderr, duration_ms=r.duration_ms,
        exit_code=r.exit_code, timed_out=r.timed_out, memory_kb=r.memory_kb,
    )


async def _run_via_tempfile(
    interpreter: str, suffix: str, source: str, timeout: float, input_bytes: bytes | None,
) -> LangRunResult:
    """Write `source` to a temp file and execute that, instead of passing it
    inline as a `-c`/`-e` command-line argument. Function Mode's generated
    drivers embed a test case's typed arguments directly in the source text
    (see function_mode/adapters.py), so a large test case (e.g. a few
    hundred-element array) can push the total command line past Windows'
    ~32,767-character CreateProcess limit -- which Python's subprocess module
    surfaces as a misleading FileNotFoundError ("runtime not found"), not a
    length error. A temp file has no such limit and matches the pattern
    run_typescript already uses."""
    with tempfile.NamedTemporaryFile(suffix=suffix, mode="w", delete=False, encoding="utf-8") as f:
        f.write(source)
        path = f.name
    try:
        return _simple(await _run_subprocess([interpreter, path], timeout, input_bytes=input_bytes))
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


async def run_python(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    return await _run_via_tempfile(sys.executable, ".py", source, timeout, input_bytes)


async def run_javascript(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    node = shutil.which("node") or "node"
    return await _run_via_tempfile(node, ".js", source, timeout, input_bytes)


async def run_typescript(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    npx = shutil.which("npx") or "npx"
    tsx = shutil.which("tsx")
    with tempfile.NamedTemporaryFile(suffix=".ts", mode="w", delete=False, encoding="utf-8") as f:
        f.write(source)
        path = f.name
    try:
        cmd = [tsx, path] if tsx else [npx, "tsx", path]
        return _simple(await _run_subprocess(cmd, timeout, input_bytes=input_bytes))
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def _cpp_cmds():
    compiler = shutil.which("g++") or shutil.which("c++") or "g++"

    def build(src: Path, tmp: str):
        return [
            compiler, str(src),
            "-o", str(Path(tmp) / "main"),
            "-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic",
        ]

    def run(src: Path, tmp: str):
        return [str(Path(tmp) / "main")]

    return ".cpp", build, run


async def run_cpp(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    suffix, build, run = _cpp_cmds()
    return await _compile_and_run(source, suffix, timeout, build, run, input_bytes=input_bytes)


def _c_cmds():
    compiler = shutil.which("gcc") or "gcc"

    def build(src: Path, tmp: str):
        return [
            compiler, str(src),
            "-o", str(Path(tmp) / "main"),
            "-std=c17", "-O2", "-Wall", "-Wextra", "-Wpedantic",
        ]

    def run(src: Path, tmp: str):
        return [str(Path(tmp) / "main")]

    return ".c", build, run


async def run_c(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    suffix, build, run = _c_cmds()
    return await _compile_and_run(source, suffix, timeout, build, run, input_bytes=input_bytes)


def _wrap_java_source(source: str) -> tuple[str, str]:
    """Returns (class_name, possibly-wrapped source)."""
    class_name = "Main"
    if "class " in source:
        return class_name, source
    indented = "\n".join("        " + l for l in source.splitlines())
    wrapped = (
        f"public class {class_name} {{\n"
        f"    public static void main(String[] args) {{\n"
        f"{indented}\n"
        f"    }}\n}}"
    )
    return class_name, wrapped


async def run_java(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    javac = shutil.which("javac") or "javac"
    java  = shutil.which("java")  or "java"
    class_name, wrapped = _wrap_java_source(source)
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / f"{class_name}.java"
        src.write_text(wrapped, encoding="utf-8")
        build = await _run_subprocess([javac, str(src)], timeout, cwd=tmp)
        if build.exit_code != 0:
            combined_err = (build.stderr or build.stdout).strip() or (
                f"Compilation failed (exit code {build.exit_code})"
            )
            return LangRunResult(
                stdout="", stderr=combined_err, duration_ms=build.duration_ms,
                exit_code=build.exit_code, compile_output=combined_err, compile_failed=True,
            )
        remaining = max(1.0, timeout - build.duration_ms / 1000)
        run = await _run_subprocess(
            [java, "-cp", tmp, class_name], remaining, cwd=tmp, input_bytes=input_bytes
        )
        return LangRunResult(
            stdout=run.stdout, stderr=run.stderr, duration_ms=build.duration_ms + run.duration_ms,
            exit_code=run.exit_code, timed_out=run.timed_out, memory_kb=run.memory_kb,
        )


async def _prepare_java(source: str, timeout: float) -> tuple[PreparedProgram | None, LangRunResult | None]:
    javac = shutil.which("javac") or "javac"
    java  = shutil.which("java")  or "java"
    class_name, wrapped = _wrap_java_source(source)
    tmp = tempfile.mkdtemp()
    src = Path(tmp) / f"{class_name}.java"
    src.write_text(wrapped, encoding="utf-8")
    build = await _run_subprocess([javac, str(src)], timeout, cwd=tmp)
    if build.exit_code != 0:
        combined_err = (build.stderr or build.stdout).strip() or (
            f"Compilation failed (exit code {build.exit_code})"
        )
        shutil.rmtree(tmp, ignore_errors=True)
        return None, LangRunResult(
            stdout="", stderr=combined_err, duration_ms=build.duration_ms,
            exit_code=build.exit_code, compile_output=combined_err, compile_failed=True,
        )
    return PreparedProgram(
        run_cmd=[java, "-cp", tmp, class_name], cwd=tmp,
        cleanup=lambda: shutil.rmtree(tmp, ignore_errors=True),
    ), None


async def _prepare_csharp(source: str, timeout: float) -> tuple[PreparedProgram | None, LangRunResult | None]:
    # Contradicts this codebase's prior documented assumption ("csharp ...
    # NOT included [in PREPARERS] ... compile+run as one indivisible step")
    # -- `dotnet build -o out` DOES have a real, isolable compile step; the
    # previously-assumed-indivisible `dotnet run` just conflates build+run
    # in one command. Measured directly in this environment: first-ever
    # `dotnet build` on a fresh project pays a ~10-16s one-time NuGet/SDK
    # resolution cost, but every subsequent build (this judge's actual
    # steady-state, since the SDK/package cache is warm after the first
    # submission) takes ~2s -- and the built DLL then runs in ~50ms per
    # invocation (measured: 0.57s first run incl. JIT warmup, 0.05s every
    # run after), comfortably supporting the same compile-once-then-run-per-
    # case pattern as cpp/c/java/rust via this exact PreparedProgram/
    # _run_prepared machinery.
    dotnet = shutil.which("dotnet") or "dotnet"
    tmp = tempfile.mkdtemp()
    src = Path(tmp) / "Program.cs"
    src.write_text(source, encoding="utf-8")
    (Path(tmp) / "app.csproj").write_text(
        '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
        "<OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>"
        "<Nullable>disable</Nullable><InvariantGlobalization>true</InvariantGlobalization>"
        "</PropertyGroup></Project>",
        encoding="utf-8",
    )
    build = await _run_subprocess(
        [dotnet, "build", "-o", "out", "-c", "Release", "--nologo", "-v", "quiet"], timeout, cwd=tmp
    )
    if build.exit_code != 0:
        combined_err = (build.stderr or build.stdout).strip() or (
            f"Compilation failed (exit code {build.exit_code})"
        )
        shutil.rmtree(tmp, ignore_errors=True)
        return None, LangRunResult(
            stdout="", stderr=combined_err, duration_ms=build.duration_ms,
            exit_code=build.exit_code, compile_output=combined_err, compile_failed=True,
        )
    return PreparedProgram(
        run_cmd=[dotnet, str(Path(tmp) / "out" / "app.dll")], cwd=tmp,
        cleanup=lambda: shutil.rmtree(tmp, ignore_errors=True),
    ), None


async def _prepare_go(source: str, timeout: float) -> tuple[PreparedProgram | None, LangRunResult | None]:
    # `run_go` below uses `go run` (compile+execute combined, no reusable
    # artifact) -- fine for Program Mode's single execution, but Function
    # Mode's up-to-40-cases-per-submission needs a real compile-once step.
    # `go build` gives exactly that: a standalone .exe reusable across every
    # case, same PreparedProgram pattern as every other compiled adapter.
    go = shutil.which("go") or "go"
    if "package " not in source:
        imports = 'import "fmt"' if "fmt." in source else ""
        body = "\n".join("    " + l for l in source.splitlines())
        source = f"package main\n{imports}\n\nfunc main() {{\n{body}\n}}"
    tmp = tempfile.mkdtemp()
    src = Path(tmp) / "main.go"
    src.write_text(source, encoding="utf-8")
    exe = Path(tmp) / "main.exe"
    build = await _run_subprocess([go, "build", "-o", str(exe), str(src)], timeout, cwd=tmp)
    if build.exit_code != 0:
        combined_err = (build.stderr or build.stdout).strip() or (
            f"Compilation failed (exit code {build.exit_code})"
        )
        shutil.rmtree(tmp, ignore_errors=True)
        return None, LangRunResult(
            stdout="", stderr=combined_err, duration_ms=build.duration_ms,
            exit_code=build.exit_code, compile_output=combined_err, compile_failed=True,
        )
    return PreparedProgram(
        run_cmd=[str(exe)], cwd=tmp,
        cleanup=lambda: shutil.rmtree(tmp, ignore_errors=True),
    ), None


async def run_go(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    go = shutil.which("go") or "go"
    with tempfile.TemporaryDirectory() as tmp:
        if "package " not in source:
            imports = 'import "fmt"' if "fmt." in source else ""
            body = "\n".join("    " + l for l in source.splitlines())
            source = f"package main\n{imports}\n\nfunc main() {{\n{body}\n}}"
        src = Path(tmp) / "main.go"
        src.write_text(source, encoding="utf-8")
        return _simple(await _run_subprocess([go, "run", str(src)], timeout, cwd=tmp, input_bytes=input_bytes))


def _rust_cmds():
    rustc = shutil.which("rustc") or "rustc"

    # Windows-only fix: this environment's rustc only has the
    # x86_64-pc-windows-MSVC target installed by default, which needs
    # Microsoft's link.exe (part of Visual Studio Build Tools) -- not
    # installed here, and a same-named `link.exe` from Git's usr/bin
    # (D:\Git\usr\bin\link.exe, an unrelated MSYS tool) gets picked up from
    # PATH instead, producing a confusing "linking failed" error that looks
    # like a code bug but is actually a toolchain-completeness gap (found
    # via a real compile attempt, not assumed). Fixed by installing the
    # x86_64-pc-windows-gnu target (`rustup target add`) and pointing rustc
    # at the ALREADY-installed MinGW-w64 gcc (used for the cpp/c adapters)
    # as its linker via an absolute path -- sidesteps PATH ambiguity
    # entirely rather than trying to reorder PATH for every subprocess.
    extra_flags: list[str] = []
    if os.name == "nt":
        mingw_gcc = shutil.which("gcc")
        if mingw_gcc:
            extra_flags = ["--target", "x86_64-pc-windows-gnu", "-C", f"linker={mingw_gcc}"]

    def build(src: Path, tmp: str):
        return [rustc, str(src), "-o", str(Path(tmp) / "main"), "-C", "opt-level=2", *extra_flags]

    def run(src: Path, tmp: str):
        return [str(Path(tmp) / "main")]

    return build, run


def _wrap_rust_source(source: str) -> str:
    if "fn main()" in source:
        return source
    body = "\n".join("    " + l for l in source.splitlines())
    return f"fn main() {{\n{body}\n}}"


async def run_rust(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    build, run = _rust_cmds()
    return await _compile_and_run(_wrap_rust_source(source), ".rs", timeout, build, run, input_bytes=input_bytes)


async def run_shell(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    # Previously passed `source` inline as a `cmd /c`/`sh -c` argument -- same
    # argv-length vulnerability class as the pre-fix run_python/run_javascript
    # (see _run_via_tempfile's docstring). Fixed by writing to a temp script
    # file and invoking the interpreter with the file path.
    if os.name == "nt":
        with tempfile.NamedTemporaryFile(suffix=".bat", mode="w", delete=False, encoding="utf-8") as f:
            f.write(source)
            path = f.name
        try:
            return _simple(await _run_subprocess(["cmd", "/c", path], timeout, input_bytes=input_bytes))
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
    sh = shutil.which("bash") or shutil.which("sh") or "sh"
    return await _run_via_tempfile(sh, ".sh", source, timeout, input_bytes)


async def run_ruby(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    # Previously `ruby -e <source>` -- same argv-length vulnerability class as
    # the pre-fix run_python/run_javascript. Fixed to temp-file transport.
    ruby = shutil.which("ruby") or "ruby"
    return await _run_via_tempfile(ruby, ".rb", source, timeout, input_bytes)


def _kotlin_cmds():
    kotlinc = shutil.which("kotlinc") or "kotlinc"
    java    = shutil.which("java")    or "java"

    def build(src: Path, tmp: str):
        return [kotlinc, str(src), "-include-runtime", "-d", str(Path(tmp) / "main.jar")]

    def run(src: Path, tmp: str):
        return [java, "-jar", str(Path(tmp) / "main.jar")]

    return build, run


async def run_kotlin(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    build, run = _kotlin_cmds()
    return await _compile_and_run(source, ".kt", timeout, build, run, input_bytes=input_bytes)


async def run_swift(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    swift = shutil.which("swift") or "swift"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "main.swift"
        src.write_text(source, encoding="utf-8")
        return _simple(await _run_subprocess([swift, str(src)], timeout, cwd=tmp, input_bytes=input_bytes))


async def run_r(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    # ignore_cleanup_errors=True: on Windows, Rscript can leave main.r's file handle
    # open for a brief window after the awaited subprocess reports exit
    # (observed reproducibly, not a one-off) -- the OS hasn't released the
    # lock yet when the context manager's rmtree runs immediately after,
    # raising PermissionError and crashing the whole judge run. This makes
    # cleanup best-effort instead: the run's actual result is already
    # captured by _run_subprocess before this point, so a leaked temp dir
    # (which the OS reclaims on its own) is a fully acceptable trade-off
    # for not crashing real judge traffic.
    rscript = shutil.which("Rscript") or shutil.which("rscript") or "Rscript"
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        src = Path(tmp) / "main.r"
        src.write_text(source, encoding="utf-8")
        return _simple(await _run_subprocess([rscript, str(src)], timeout, input_bytes=input_bytes))


async def run_csharp(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    mcs  = shutil.which("mcs") or shutil.which("csc")
    mono = shutil.which("mono")
    if mcs and mono:
        def build(src: Path, tmp: str):
            return [mcs, str(src), f"-out:{Path(tmp) / 'main.exe'}"]
        def run_fn(src: Path, tmp: str):
            return [mono, str(Path(tmp) / "main.exe")]
        return await _compile_and_run(source, ".cs", timeout, build, run_fn, input_bytes=input_bytes)

    # Fallback: dotnet run (no separate compile step to isolate — a build
    # failure surfaces as a nonzero exit_code with dotnet's own diagnostics in
    # stderr, not compile_failed=True; documented as a known limitation).
    dotnet = shutil.which("dotnet") or "dotnet"
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "Program.cs").write_text(source, encoding="utf-8")
        (Path(tmp) / "app.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
            "<OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>"
            "</PropertyGroup></Project>"
        )
        return _simple(await _run_subprocess(
            [dotnet, "run", "--project", tmp], timeout, cwd=tmp, input_bytes=input_bytes
        ))


async def run_php(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    php = shutil.which("php") or "php"
    with tempfile.NamedTemporaryFile(suffix=".php", mode="w", delete=False, encoding="utf-8") as f:
        f.write(source)
        path = f.name
    try:
        return _simple(await _run_subprocess([php, path], timeout, input_bytes=input_bytes))
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


async def run_scala(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    scala = shutil.which("scala-cli") or shutil.which("scala") or "scala-cli"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "main.scala"
        src.write_text(source, encoding="utf-8")
        return _simple(await _run_subprocess([scala, str(src)], timeout, cwd=tmp, input_bytes=input_bytes))


async def _prepare_scala(source: str, timeout: float) -> tuple[PreparedProgram | None, LangRunResult | None]:
    # Contradicts this codebase's prior documented assumption ("scala-cli
    # ... compile+run as one indivisible step") -- `scala-cli --power
    # package <src> -o <jar>` DOES have a real, isolable compile step
    # (confirmed directly: ~2-3 minutes the very first time ever run on
    # this machine, paying a one-time Maven dependency download for the
    # Scala 3 compiler/runtime itself, but ~1.5s on every build after that
    # cache is warm), then `java -jar <jar>` reruns the same artifact per
    # case -- same PreparedProgram pattern as every other compiled adapter.
    # `--power` is required for the `package` subcommand (scala-cli marks
    # it "restricted" behind that flag); this is a CLI feature flag, not a
    # privilege escalation of any kind.
    scala = shutil.which("scala-cli") or "scala-cli"
    tmp = tempfile.mkdtemp()
    src = Path(tmp) / "main.scala"
    src.write_text(source, encoding="utf-8")
    jar = Path(tmp) / "main.jar"
    build = await _run_subprocess(
        [scala, "--power", "package", str(src), "-o", str(jar), "-f"], timeout, cwd=tmp
    )
    if build.exit_code != 0 or not jar.exists():
        combined_err = (build.stderr or build.stdout).strip() or (
            f"Compilation failed (exit code {build.exit_code})"
        )
        shutil.rmtree(tmp, ignore_errors=True)
        return None, LangRunResult(
            stdout="", stderr=combined_err, duration_ms=build.duration_ms,
            exit_code=build.exit_code, compile_output=combined_err, compile_failed=True,
        )
    java = shutil.which("java") or "java"
    return PreparedProgram(
        run_cmd=[java, "-jar", str(jar)], cwd=tmp,
        cleanup=lambda: shutil.rmtree(tmp, ignore_errors=True),
    ), None


async def run_perl(source: str, timeout: float, input_bytes: bytes | None = None) -> LangRunResult:
    perl = shutil.which("perl") or "perl"
    with tempfile.NamedTemporaryFile(suffix=".pl", mode="w", delete=False, encoding="utf-8") as f:
        f.write(source)
        path = f.name
    try:
        return _simple(await _run_subprocess([perl, path], timeout, input_bytes=input_bytes))
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


RUNNERS = {
    "python":     run_python,
    "javascript": run_javascript,
    "typescript": run_typescript,
    "cpp":        run_cpp,
    "c":          run_c,
    "java":       run_java,
    "go":         run_go,
    "rust":       run_rust,
    "shell":      run_shell,
    "ruby":       run_ruby,
    "kotlin":     run_kotlin,
    "swift":      run_swift,
    "r":          run_r,
    "csharp":     run_csharp,
    "php":        run_php,
    "scala":      run_scala,
    "perl":       run_perl,
}


# ── Compile-once preparers (judge use only) ─────────────────────────────────────
# Only languages with a real, isolable compile step and a cheap re-run are
# included. NOTE: this comment previously claimed scala-cli and swift
# "compile+run as one indivisible step" -- that assumption turned out to be
# wrong for BOTH (see _prepare_scala's and _prepare_swift's docstrings for
# the direct experiments that disproved it), so both now have real preparers
# below. The mcs/mono csharp path is the one remaining exception: its
# run_csharp fallback genuinely conflates build+run with no isolable step
# when mcs/mono aren't present (dotnet build IS isolable and is what
# _prepare_csharp actually uses).

async def _prepare_cpp(source: str, timeout: float) -> tuple[PreparedProgram | None, LangRunResult | None]:
    suffix, build, run = _cpp_cmds()
    return await _prepare_compiled(source, suffix, timeout, build, run)


async def _prepare_c(source: str, timeout: float) -> tuple[PreparedProgram | None, LangRunResult | None]:
    suffix, build, run = _c_cmds()
    return await _prepare_compiled(source, suffix, timeout, build, run)


async def _prepare_rust(source: str, timeout: float) -> tuple[PreparedProgram | None, LangRunResult | None]:
    build, run = _rust_cmds()
    return await _prepare_compiled(_wrap_rust_source(source), ".rs", timeout, build, run)


async def _prepare_kotlin(source: str, timeout: float) -> tuple[PreparedProgram | None, LangRunResult | None]:
    build, run = _kotlin_cmds()
    return await _prepare_compiled(source, ".kt", timeout, build, run)


async def _prepare_swift(source: str, timeout: float) -> tuple[PreparedProgram | None, LangRunResult | None]:
    # `run_swift` above uses `swift main.swift` (JIT-compile-and-run as one
    # indivisible step) -- fine for Program Mode's single execution, but
    # Function Mode's up-to-40-cases-per-submission needs a real
    # compile-once step. `swiftc main.swift -o main.exe` gives exactly that
    # -- confirmed directly this session (needed SDKROOT pointed at the
    # Windows platform SDK, plus a Visual Studio Build Tools install for the
    # MSVC linker Swift's Windows target requires), same PreparedProgram
    # pattern as every other compiled adapter.
    swiftc = shutil.which("swiftc") or "swiftc"
    tmp = tempfile.mkdtemp()
    src = Path(tmp) / "main.swift"
    src.write_text(source, encoding="utf-8")
    exe = Path(tmp) / "main.exe"
    build = await _run_subprocess([swiftc, str(src), "-o", str(exe)], timeout, cwd=tmp)
    if build.exit_code != 0 or not exe.exists():
        combined_err = (build.stderr or build.stdout).strip() or (
            f"Compilation failed (exit code {build.exit_code})"
        )
        shutil.rmtree(tmp, ignore_errors=True)
        return None, LangRunResult(
            stdout="", stderr=combined_err, duration_ms=build.duration_ms,
            exit_code=build.exit_code, compile_output=combined_err, compile_failed=True,
        )
    return PreparedProgram(
        run_cmd=[str(exe)], cwd=tmp,
        cleanup=lambda: shutil.rmtree(tmp, ignore_errors=True),
    ), None


PREPARERS: dict[str, "Callable[[str, float], object]"] = {
    "cpp":    _prepare_cpp,
    "c":      _prepare_c,
    "rust":   _prepare_rust,
    "kotlin": _prepare_kotlin,
    "java":   _prepare_java,
    "csharp": _prepare_csharp,
    "go":     _prepare_go,
    "scala":  _prepare_scala,
    "swift":  _prepare_swift,
}


# ── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/run", response_model=RunResponse)
async def run_cell(body: RunRequest) -> RunResponse:
    runner = RUNNERS.get(body.language)
    if not runner:
        raise HTTPException(
            status_code=422,
            detail=f"Language '{body.language}' not supported. Supported: {', '.join(RUNNERS)}",
        )
    input_bytes = body.input_data.encode("utf-8") if body.input_data is not None else None
    r = await runner(body.source, body.timeout, input_bytes=input_bytes)
    return RunResponse(
        output=r.stdout, error=r.stderr, duration_ms=r.duration_ms, language=body.language,
        exit_code=r.exit_code, memory_kb=r.memory_kb, compile_output=r.compile_output,
    )


@router.post("/run-cell/{experiment_id}/{cell_id}", response_model=RunResponse)
async def run_saved_cell(
    experiment_id: str,
    cell_id: str,
    timeout: float = 10.0,
    db: AsyncSession = Depends(get_db),
) -> RunResponse:
    result = await db.execute(
        select(NotebookCell).where(
            NotebookCell.id == cell_id,
            NotebookCell.experiment_id == experiment_id,
        )
    )
    cell = result.scalar_one_or_none()
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")

    runner = RUNNERS.get(cell.language or "python")
    if not runner:
        raise HTTPException(status_code=422, detail=f"Language '{cell.language}' not supported")

    r = await runner(cell.source, min(timeout, MAX_TIMEOUT))
    cell.output = r.stdout
    cell.error = r.stderr
    cell.executed_at = datetime.now(timezone.utc)
    await db.flush()
    return RunResponse(
        output=r.stdout, error=r.stderr, duration_ms=r.duration_ms, language=cell.language or "python",
        exit_code=r.exit_code, memory_kb=r.memory_kb, compile_output=r.compile_output,
    )
