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
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...models.experiment import NotebookCell

router = APIRouter(prefix="/notebook", tags=["notebook"])

MAX_TIMEOUT = 30


class RunRequest(BaseModel):
    source: str = Field(..., max_length=65_536)
    language: str = "python"
    timeout: float = Field(10.0, gt=0, le=MAX_TIMEOUT)


class RunResponse(BaseModel):
    output: str
    error: str
    duration_ms: float
    language: str


# ── Language executors ──────────────────────────────────────────────────────────
#
# asyncio.create_subprocess_exec is unreliable on Windows under uvicorn's event
# loop. Use a thread-pool executor with synchronous subprocess.run instead.

_executor = ThreadPoolExecutor(max_workers=8)


def _run_sync(cmd: list[str], timeout: float, cwd: str | None = None) -> tuple[str, str, float]:
    """Synchronous subprocess run — safe on all platforms."""
    t0 = time.perf_counter()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
            cwd=cwd,
        )
        out = result.stdout.decode("utf-8", errors="replace")
        err = result.stderr.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return "", f"TimeoutError: exceeded {timeout}s", (time.perf_counter() - t0) * 1000
    except FileNotFoundError as exc:
        return "", f"Runtime not found: {exc.filename}", (time.perf_counter() - t0) * 1000
    except Exception as exc:
        return "", str(exc), (time.perf_counter() - t0) * 1000
    return out, err, (time.perf_counter() - t0) * 1000


async def _run_subprocess(cmd: list[str], timeout: float, cwd: str | None = None) -> tuple[str, str, float]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _run_sync, cmd, timeout, cwd)


async def _with_tempfile(source: str, suffix: str, timeout: float, build_cmd_fn, run_cmd_fn=None) -> tuple[str, str, float]:
    """Write source to temp file, optionally compile, then run."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / f"main{suffix}"
        src.write_text(source, encoding="utf-8")

        if build_cmd_fn:
            build_cmd = build_cmd_fn(src, tmp)
            out, err, ms = await _run_subprocess(build_cmd, timeout, cwd=tmp)
            if err.strip() and not out.strip():
                return out, err, ms
            timeout = max(1.0, timeout - ms / 1000)

        run_cmd = run_cmd_fn(src, tmp) if run_cmd_fn else build_cmd_fn(src, tmp)
        return await _run_subprocess(run_cmd, timeout, cwd=tmp)


# ── Per-language runners ────────────────────────────────────────────────────────

async def run_python(source: str, timeout: float) -> tuple[str, str, float]:
    return await _run_subprocess([sys.executable, "-c", source], timeout)


async def run_javascript(source: str, timeout: float) -> tuple[str, str, float]:
    node = shutil.which("node") or "node"
    return await _run_subprocess([node, "-e", source], timeout)


async def run_typescript(source: str, timeout: float) -> tuple[str, str, float]:
    # Use npx tsx for zero-install TypeScript execution
    npx = shutil.which("npx") or "npx"
    with tempfile.NamedTemporaryFile(suffix=".ts", mode="w", delete=False, encoding="utf-8") as f:
        f.write(source)
        path = f.name
    try:
        out, err, ms = await _run_subprocess([npx, "tsx", path], timeout)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    return out, err, ms


async def run_cpp(source: str, timeout: float) -> tuple[str, str, float]:
    compiler = shutil.which("g++") or shutil.which("c++") or "g++"
    def build(src: Path, tmp: str):
        return [compiler, str(src), "-o", str(Path(tmp) / "main"), "-std=c++17", "-O1"]
    def run(src: Path, tmp: str):
        exe = str(Path(tmp) / "main")
        return [exe] if os.name != "nt" else [exe + ".exe" if Path(exe + ".exe").exists() else exe]
    return await _with_tempfile(source, ".cpp", timeout, build, run)


async def run_c(source: str, timeout: float) -> tuple[str, str, float]:
    compiler = shutil.which("gcc") or "gcc"
    def build(src: Path, tmp: str):
        return [compiler, str(src), "-o", str(Path(tmp) / "main"), "-std=c17"]
    def run(src: Path, tmp: str):
        exe = str(Path(tmp) / "main")
        return [exe] if os.name != "nt" else [exe + ".exe" if Path(exe + ".exe").exists() else exe]
    return await _with_tempfile(source, ".c", timeout, build, run)


async def run_java(source: str, timeout: float) -> tuple[str, str, float]:
    javac = shutil.which("javac") or "javac"
    java  = shutil.which("java")  or "java"
    with tempfile.TemporaryDirectory() as tmp:
        # Java requires public class name to match filename
        class_name = "Main"
        src = Path(tmp) / f"{class_name}.java"
        # Wrap in class Main if no class definition detected
        if "class " not in source:
            source = f"public class Main {{\n    public static void main(String[] args) {{\n{chr(10).join('        ' + l for l in source.splitlines())}\n    }}\n}}"
        src.write_text(source, encoding="utf-8")
        out, err, ms = await _run_subprocess([javac, str(src)], timeout, cwd=tmp)
        if err.strip() and ".class" not in "".join(os.listdir(tmp)):
            return out, err, ms
        remaining = max(1.0, timeout - ms / 1000)
        o2, e2, ms2 = await _run_subprocess([java, "-cp", tmp, class_name], remaining, cwd=tmp)
        return o2, e2, ms + ms2


async def run_go(source: str, timeout: float) -> tuple[str, str, float]:
    go = shutil.which("go") or "go"
    async def _run(src: Path, tmp: str):
        return await _run_subprocess([go, "run", str(src)], timeout, cwd=tmp)
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "main.go"
        if "package " not in source:
            source = "package main\nimport \"fmt\"\n\nfunc main() {\n" + "\n".join("    " + l for l in source.splitlines()) + "\n}"
        src.write_text(source, encoding="utf-8")
        return await _run_subprocess([go, "run", str(src)], timeout, cwd=tmp)


async def run_rust(source: str, timeout: float) -> tuple[str, str, float]:
    rustc = shutil.which("rustc") or "rustc"
    def build(src: Path, tmp: str):
        out_name = "main" + (".exe" if os.name == "nt" else "")
        return [rustc, str(src), "-o", str(Path(tmp) / out_name)]
    def run(src: Path, tmp: str):
        out_name = "main" + (".exe" if os.name == "nt" else "")
        return [str(Path(tmp) / out_name)]
    wrapped = source
    if "fn main()" not in source:
        wrapped = f"fn main() {{\n{chr(10).join('    ' + l for l in source.splitlines())}\n}}"
    return await _with_tempfile(wrapped, ".rs", timeout, build, run)


async def run_shell(source: str, timeout: float) -> tuple[str, str, float]:
    if os.name == "nt":
        return await _run_subprocess(["cmd", "/c", source], timeout)
    sh = shutil.which("bash") or shutil.which("sh") or "sh"
    return await _run_subprocess([sh, "-c", source], timeout)


async def run_ruby(source: str, timeout: float) -> tuple[str, str, float]:
    ruby = shutil.which("ruby") or "ruby"
    return await _run_subprocess([ruby, "-e", source], timeout)


async def run_kotlin(source: str, timeout: float) -> tuple[str, str, float]:
    kotlinc = shutil.which("kotlinc") or "kotlinc"
    java = shutil.which("java") or "java"
    def build(src: Path, tmp: str):
        return [kotlinc, str(src), "-include-runtime", "-d", str(Path(tmp) / "main.jar")]
    def run(src: Path, tmp: str):
        return [java, "-jar", str(Path(tmp) / "main.jar")]
    return await _with_tempfile(source, ".kt", timeout, build, run)


async def run_swift(source: str, timeout: float) -> tuple[str, str, float]:
    swift = shutil.which("swift") or "swift"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "main.swift"
        src.write_text(source, encoding="utf-8")
        return await _run_subprocess([swift, str(src)], timeout, cwd=tmp)


async def run_r(source: str, timeout: float) -> tuple[str, str, float]:
    rscript = shutil.which("Rscript") or shutil.which("rscript") or "Rscript"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "main.r"
        src.write_text(source, encoding="utf-8")
        return await _run_subprocess([rscript, str(src)], timeout, cwd=tmp)


async def run_csharp(source: str, timeout: float) -> tuple[str, str, float]:
    # Try mcs (Mono C# compiler) first — fast, widely available
    mcs = shutil.which("mcs") or shutil.which("csc")
    if mcs:
        mono = shutil.which("mono") or "mono"
        def build(src: Path, tmp: str):
            return [mcs, str(src), f"-out:{Path(tmp) / 'main.exe'}"]
        def run_fn(src: Path, tmp: str):
            return [mono, str(Path(tmp) / "main.exe")]
        return await _with_tempfile(source, ".cs", timeout, build, run_fn)
    # Fall back to dotnet run with an ephemeral project
    dotnet = shutil.which("dotnet") or "dotnet"
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "Program.cs").write_text(source, encoding="utf-8")
        (Path(tmp) / "app.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
            "<OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>"
            "</PropertyGroup></Project>",
        )
        return await _run_subprocess([dotnet, "run", "--project", tmp], timeout, cwd=tmp)


async def run_php(source: str, timeout: float) -> tuple[str, str, float]:
    php = shutil.which("php") or "php"
    with tempfile.NamedTemporaryFile(suffix=".php", mode="w", delete=False, encoding="utf-8") as f:
        f.write(source)
        path = f.name
    try:
        return await _run_subprocess([php, path], timeout)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


async def run_scala(source: str, timeout: float) -> tuple[str, str, float]:
    # Prefer scala-cli (modern), fall back to scala (classic)
    scala = shutil.which("scala-cli") or shutil.which("scala") or "scala"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "main.scala"
        src.write_text(source, encoding="utf-8")
        return await _run_subprocess([scala, str(src)], timeout, cwd=tmp)


async def run_perl(source: str, timeout: float) -> tuple[str, str, float]:
    perl = shutil.which("perl") or "perl"
    with tempfile.NamedTemporaryFile(suffix=".pl", mode="w", delete=False, encoding="utf-8") as f:
        f.write(source)
        path = f.name
    try:
        return await _run_subprocess([perl, path], timeout)
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


# ── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/run", response_model=RunResponse)
async def run_cell(body: RunRequest) -> RunResponse:
    runner = RUNNERS.get(body.language)
    if not runner:
        raise HTTPException(status_code=422, detail=f"Language '{body.language}' not supported. Supported: {', '.join(RUNNERS)}")
    output, error, duration_ms = await runner(body.source, body.timeout)
    return RunResponse(output=output, error=error, duration_ms=duration_ms, language=body.language)


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

    output, error, duration_ms = await runner(cell.source, min(timeout, MAX_TIMEOUT))
    cell.output = output
    cell.error = error
    cell.executed_at = datetime.now(timezone.utc)
    await db.flush()
    return RunResponse(output=output, error=error, duration_ms=duration_ms, language=cell.language or "python")
