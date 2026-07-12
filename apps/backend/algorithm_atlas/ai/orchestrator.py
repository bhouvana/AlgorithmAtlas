"""
Orchestrator — intent detection → agent routing.

Pattern scoring is regex-based (no extra LLM call). The agent still receives the
full AtlasContext so context is an additional signal, not a constraint.
"""
from __future__ import annotations

import re

from .agents.atlascode import AtlasCodeAgent
from .agents.base import BaseAgent
from .agents.challenge import ChallengeAgent
from .agents.general import GeneralAgent
from .agents.interviewer import InterviewerAgent
from .agents.navigation import NavigationAgent
from .agents.notebook import NotebookAgent
from .agents.search import SearchAgent
from .agents.teaching import TeachingAgent
from .agents.visualization import VisualizationAgent
from .agents.whiteboard import WhiteboardAgent
from .context_builder import AtlasContext


def _patterns(*raw: str) -> list[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in raw]


_TEACHING = _patterns(
    r"\bexplain\b", r"\bwhy\b", r"\bhow does\b", r"\bwhat is\b", r"\bwhat are\b",
    r"\bteach\b", r"\bwalk me through\b", r"\bhelp me understand\b",
    r"\bwhat happens\b", r"\bwhen should\b", r"\bdifference between\b",
    r"\badvantage\b", r"\bbetter than\b", r"\btrade.?off\b",
    r"\bintuition\b", r"\bwhy does\b", r"\bprove\b",
)

_NOTEBOOK = _patterns(
    r"\bwrite\b", r"\bgenerate\b", r"\bdebug\b", r"\bfix\b", r"\boptimize\b",
    r"\bconvert\b", r"\btranslate\b", r"\bcode\b", r"\bimplement\b",
    r"\berror\b", r"\bexception\b", r"\brefactor\b", r"\btest case\b",
    r"\bdocument\b", r"\badd comments\b", r"\brewrite\b", r"\bsyntax\b",
    r"\bcompile\b", r"\brun\b", r"\bexecute\b",
)

_ATLASCODE = _patterns(
    r"\bhint\b", r"\bwrong answer\b", r"\bfailing\b", r"\bfailed\b", r"\btest case\b",
    r"\bwhy (is|did|does|isn't|doesn't)\b", r"\bverdict\b", r"\baccepted\b",
    r"\bcompile error\b", r"\bruntime error\b", r"\btime limit\b",
    r"\bwrite\b", r"\bgenerate\b", r"\bdebug\b", r"\bfix\b", r"\boptimize\b",
    r"\bcode\b", r"\bimplement\b", r"\berror\b", r"\bexception\b",
    r"\brefactor\b", r"\bsolve\b", r"\bapproach\b", r"\bsolution\b", r"\brun\b",
)

_VISUALIZATION = _patterns(
    r"\breplay\b", r"\bpause\b", r"\bplay\b", r"\bslow\b", r"\bfaster\b",
    r"\bspeed\b", r"\bjump to\b", r"\bframe\b", r"\bstep\b",
    r"\bgo back\b", r"\bstart over\b", r"\breset\b", r"\bstart from\b",
    r"\bwatch\b", r"\bshow.*step\b", r"\bstep by step\b",
)

_CHALLENGE = _patterns(
    r"\bchallenge\b", r"\bproblem\b", r"\bpractice\b", r"\bquiz me\b",
    r"\btest me\b", r"\bgive me.*problem\b", r"\bexercise\b",
    r"\bgenerate.*problem\b", r"\bcreate.*challenge\b", r"\bgive me a.*question\b",
)

_WHITEBOARD = _patterns(
    r"\bdraw\b", r"\bdiagram\b", r"\bwhiteboard\b", r"\bsketch\b",
    r"\billustrate\b", r"\bshow.*tree\b", r"\bshow.*graph\b",
    r"\brecursion tree\b", r"\bcall stack\b", r"\bmap out\b",
    r"\bvisualize\b(?!.*simulation)", r"\bplot\b",
)

_INTERVIEW = _patterns(
    r"\binterview\b", r"\bfaang\b", r"\bmock.*interview\b",
    r"\bstart.*interview\b", r"\binterview.*mode\b", r"\binterviewer\b",
    r"\bask me.*question\b", r"\bprepare.*interview\b",
)

_SEARCH = _patterns(
    r"\bfind\b", r"\bsearch\b", r"\blook for\b", r"\bshow me.*algorithm\b",
    r"\bwhat.*algorithm.*for\b", r"\brecommend\b", r"\bwhich algorithm\b",
    r"\bbest algorithm\b", r"\bsimilar to\b", r"\brelated to\b",
)

_NAVIGATE = _patterns(
    r"\btake me to\b", r"\bnavigate to\b",
    r"\bgo to\s+(the\s+)?(notebook|catalog|algorithms|learning|experiments|compare|atlas)\b",
    r"\bopen\s+(the\s+)?(notebook|catalog|algorithms?|learning|experiments|compare)\b",
    r"\bswitch to\s+(the\s+)?(notebook|catalog|algorithms?|learning|experiments|compare)\b",
    r"\bshow me\s+.+\s+page\b",
    r"\btake me\s+.+\s+page\b",
    # Compare two specific algorithms (e.g. "compare quicksort and mergesort")
    r"\bcompare\b.{2,60}\b(and|vs\.?|versus)\b",
)


def _score(message: str, patterns: list[re.Pattern]) -> int:
    return sum(1 for p in patterns if p.search(message))


def route(message: str, context: AtlasContext) -> BaseAgent:
    """Choose the best agent for this message + context combination."""
    m = message

    # Navigation always wins when explicit
    if _score(m, _NAVIGATE) >= 1:
        return NavigationAgent()

    # Hard overrides by page context
    if context.page == "notebook" and _score(m, _NOTEBOOK) > 0:
        return NotebookAgent()
    if context.page == "atlascode" and _score(m, _ATLASCODE) > 0:
        return AtlasCodeAgent()

    if context.simulation and context.simulation.status in ("paused", "running", "created"):
        if _score(m, _VISUALIZATION) >= 1:
            return VisualizationAgent()

    scores = {
        "teaching":      _score(m, _TEACHING),
        "notebook":      _score(m, _NOTEBOOK),
        "atlascode":     _score(m, _ATLASCODE),
        "visualization": _score(m, _VISUALIZATION),
        "challenge":     _score(m, _CHALLENGE),
        "whiteboard":    _score(m, _WHITEBOARD),
        "interview":     _score(m, _INTERVIEW),
        "search":        _score(m, _SEARCH),
    }

    best_key = max(scores, key=lambda k: scores[k])

    if scores[best_key] == 0:
        # Fall back on page context
        if context.page in ("algorithm", "lesson"):
            return TeachingAgent()
        if context.page == "notebook":
            return NotebookAgent()
        if context.page == "atlascode":
            return AtlasCodeAgent()
        if context.page in ("catalog", "atlascode-catalog", "learning"):
            return SearchAgent()
        return GeneralAgent()

    return {
        "teaching":      TeachingAgent,
        "notebook":      NotebookAgent,
        "atlascode":     AtlasCodeAgent,
        "visualization": VisualizationAgent,
        "challenge":     ChallengeAgent,
        "whiteboard":    WhiteboardAgent,
        "interview":     InterviewerAgent,
        "search":        SearchAgent,
    }[best_key]()
