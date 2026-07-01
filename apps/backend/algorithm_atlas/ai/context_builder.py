"""
AtlasContext — the full platform state sent by the frontend with every request.

context_to_text() converts it to a concise natural-language paragraph injected
into every agent's system prompt so agents never need to ask for context.
"""
from __future__ import annotations

import json
from typing import Optional

from pydantic import BaseModel


# ── Sub-models ────────────────────────────────────────────────────────────────

class ComplexityInfo(BaseModel):
    time_best: str = ""
    time_average: str = ""
    time_worst: str = ""
    space: str = ""


class AlgorithmContext(BaseModel):
    slug: str
    name: str
    category: str
    visualization_type: str
    complexity: Optional[ComplexityInfo] = None
    description: str = ""


class SimulationContext(BaseModel):
    status: str                          # created | paused | running | completed | error
    currentFrameIndex: int = 0
    totalFrames: Optional[int] = None
    playbackSpeed: float = 1.0
    currentFrame: Optional[dict] = None  # raw frame.state
    eventLabel: Optional[str] = None


class NotebookContext(BaseModel):
    language: str = "python"
    source: str = ""
    lastOutput: str = ""
    lastError: str = ""


class LessonContext(BaseModel):
    id: str
    title: str
    track: str
    difficulty: str
    activeSection: str  # concept | visualization | examples | complexity | quiz


class LearningProgressContext(BaseModel):
    xp: int = 0
    level: int = 1
    completedLessons: list[str] = []
    currentStreak: int = 0


class ComparisonContext(BaseModel):
    algorithmA: Optional[str] = None
    algorithmB: Optional[str] = None


# ── Root context model ────────────────────────────────────────────────────────

class AtlasContext(BaseModel):
    page: str = "landing"   # landing | catalog | algorithm | compare | notebook | experiments | learning | lesson
    userId: str = "anonymous"

    algorithm: Optional[AlgorithmContext] = None
    simulation: Optional[SimulationContext] = None
    notebook: Optional[NotebookContext] = None
    lesson: Optional[LessonContext] = None
    learningProgress: Optional[LearningProgressContext] = None
    comparison: Optional[ComparisonContext] = None


# ── Serialiser ────────────────────────────────────────────────────────────────

_PAGE_LABELS: dict[str, str] = {
    "landing":     "the home / landing page",
    "catalog":     "the algorithm catalog (250+ algorithms, browsable)",
    "algorithm":   "an algorithm detail page",
    "compare":     "the side-by-side algorithm comparison page",
    "notebook":    "the Polyglot Notebook (Monaco IDE, 17 languages)",
    "experiments": "the saved experiments browser",
    "learning":    "the learning path overview (12 curriculum tracks)",
    "lesson":      "an individual lesson",
}


def context_to_text(ctx: AtlasContext) -> str:
    """Compact natural-language summary of the full platform state."""
    parts: list[str] = []

    parts.append(f"The user is on {_PAGE_LABELS.get(ctx.page, ctx.page)}.")

    if ctx.algorithm:
        a = ctx.algorithm
        cplx = ""
        if a.complexity:
            cplx = (
                f" Complexity: best={a.complexity.time_best}, "
                f"avg={a.complexity.time_average}, worst={a.complexity.time_worst}, "
                f"space={a.complexity.space}."
            )
        parts.append(
            f"They are viewing '{a.name}' (category: {a.category}, "
            f"viz type: {a.visualization_type}).{cplx}"
        )

    if ctx.simulation:
        s = ctx.simulation
        total = f"/{s.totalFrames}" if s.totalFrames else ""
        parts.append(
            f"The simulation is {s.status} at frame {s.currentFrameIndex}{total}, "
            f"speed {s.playbackSpeed}×."
        )
        if s.eventLabel:
            parts.append(f"Current step: '{s.eventLabel}'.")
        if s.currentFrame:
            frame_snippet = json.dumps(s.currentFrame)[:600]
            parts.append(f"Frame state: {frame_snippet}")

    if ctx.notebook:
        n = ctx.notebook
        line_count = len(n.source.splitlines()) if n.source else 0
        parts.append(f"Notebook language: {n.language} ({line_count} lines of code).")
        if n.source:
            parts.append(f"Current code:\n```{n.language}\n{n.source[:3000]}\n```")
        if n.lastError:
            parts.append(f"Last execution error:\n{n.lastError[:1500]}")
        elif n.lastOutput:
            parts.append(f"Last output: {n.lastOutput[:500]}")

    if ctx.lesson:
        l = ctx.lesson
        parts.append(
            f"Lesson: '{l.title}' (track: {l.track}, difficulty: {l.difficulty}, "
            f"active section: {l.activeSection})."
        )

    if ctx.learningProgress:
        p = ctx.learningProgress
        parts.append(
            f"User progress: Level {p.level}, {p.xp} XP, "
            f"{len(p.completedLessons)} lessons completed"
            + (f", {p.currentStreak}-day streak." if p.currentStreak else ".")
        )

    if ctx.comparison:
        c = ctx.comparison
        if c.algorithmA or c.algorithmB:
            parts.append(
                f"Comparing: {c.algorithmA or '(none)'} vs {c.algorithmB or '(none)'}."
            )

    return " ".join(parts)
