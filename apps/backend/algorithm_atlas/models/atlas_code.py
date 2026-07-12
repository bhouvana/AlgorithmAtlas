"""
AtlasCode ORM models.

Tables:
  problems         — problem catalog (seeded from algorithm manifests)
  test_cases       — per-problem test cases (stdin → expected stdout)
  submissions      — user code submissions with verdicts
  user_progress    — aggregated progress per anonymous user
  daily_challenges — one featured problem per calendar day
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

try:
    from sqlalchemy import JSON
except ImportError:
    from sqlalchemy.types import JSON  # type: ignore[no-redef]

from ..database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


# ──────────────────────────────────────────────────────────────────────────────
# Problem
# ──────────────────────────────────────────────────────────────────────────────

class Problem(Base):
    """
    A coding problem. The id is its slug and maps 1-to-1 to an algorithm
    plugin slug so the visualization bridge works automatically.
    """
    __tablename__ = "problems"

    id                 = Column(String(255), primary_key=True)   # e.g. "binary-search"
    title              = Column(String(255), nullable=False)
    difficulty         = Column(String(10),  nullable=False)     # Easy | Medium | Hard
    category           = Column(String(100), nullable=False, index=True)
    problem_statement  = Column(Text, nullable=False)
    examples           = Column(JSON, default=list)   # [{input, output, explanation}]
    constraints        = Column(JSON, default=list)   # [str]
    hints              = Column(JSON, default=list)   # [{level: 1..7, text: str}]
    companies          = Column(JSON, default=list)   # ["Google", "Meta", ...]
    acceptance_rate    = Column(Float, default=0.0)
    estimated_minutes  = Column(Integer, default=30)
    algorithm_slug     = Column(String(255), nullable=True)  # link to visualization
    starter_code       = Column(JSON, default=dict)           # {python: "...", cpp: "...", ...} -- Program Mode
    # Function Mode support (see atlascode/function_mode/). NULL means this
    # problem has no Function Mode support yet -- Program Mode is always
    # available regardless, this column never affects it.
    function_contract     = Column(JSON, nullable=True)   # FunctionContract dict (see function_mode/contracts.py)
    starter_code_function = Column(JSON, default=dict)    # {python: "...", ...} -- Function Mode starters, per language
    total_submissions  = Column(Integer, default=0)
    total_accepted     = Column(Integer, default=0)
    # Bumped whenever this problem's test_cases change in a way that would
    # invalidate cross-submission runtime/memory percentile comparisons
    # (e.g. bad test data fixed, cases added/removed). Submissions snapshot
    # this value at submit time so percentiles only ever compare
    # same-suite-version submissions.
    test_suite_version = Column(String(20), default="1.0")
    created_at         = Column(DateTime(timezone=True), default=_now)

    test_cases  = relationship("TestCase",  back_populates="problem",
                               cascade="all, delete-orphan", order_by="TestCase.order")
    submissions = relationship("Submission", back_populates="problem")


# ──────────────────────────────────────────────────────────────────────────────
# TestCase
# ──────────────────────────────────────────────────────────────────────────────

class TestCase(Base):
    """
    A single evaluation case.  input_data is piped to stdin; expected_output
    is compared (stripped) against stdout produced by the user's program.
    """
    __tablename__ = "test_cases"

    id            = Column(String(36), primary_key=True, default=_uuid)
    problem_id    = Column(String(255), ForeignKey("problems.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    input_data    = Column(Text, nullable=False)      # Program Mode: what goes into stdin
    expected_output = Column(Text, nullable=False)    # Program Mode: expected stripped stdout
    is_hidden     = Column(Boolean, default=False)    # hidden = only evaluated on Submit
    explanation   = Column(Text, nullable=True)
    order         = Column(Integer, default=0)

    # Function Mode: the SAME underlying case, captured as typed arguments +
    # typed return instead of a stdin/stdout string pair. Populated only when
    # the parent Problem has a function_contract; NULL otherwise. Never a
    # second test corpus -- same `order`, same case, two representations.
    function_args     = Column(JSON, nullable=True)   # {param_name: value, ...}
    function_expected = Column(JSON, nullable=True)   # the oracle's raw return value

    problem = relationship("Problem", back_populates="test_cases")


# ──────────────────────────────────────────────────────────────────────────────
# Submission
# ──────────────────────────────────────────────────────────────────────────────

class Submission(Base):
    """
    One code submission by a user for a problem.  ai_review is populated
    asynchronously after the verdict is determined.
    """
    __tablename__ = "submissions"

    id                 = Column(String(36),  primary_key=True, default=_uuid)
    problem_id         = Column(String(255), ForeignKey("problems.id"), nullable=False, index=True)
    user_id            = Column(String(255), default="anonymous", index=True)
    language           = Column(String(50),  nullable=False)
    code               = Column(Text,        nullable=False)
    verdict            = Column(String(50),  nullable=False)   # Accepted | Wrong Answer | etc.
    runtime_ms         = Column(Float,       nullable=True)
    memory_kb          = Column(Float,       nullable=True)    # peak measured memory; None if unmeasured
    test_cases_passed  = Column(Integer,     default=0)
    test_cases_total   = Column(Integer,     default=0)
    compile_output     = Column(Text,        nullable=True)    # populated only on Compilation Error
    # Per-case results, ALREADY hidden-redacted before storage (same redaction
    # as the live API response) -- lets the Submission Detail view show case
    # outcomes later without re-running the code. A plain JSON column rather
    # than a new table: this project's established pattern for per-submission
    # structured data that's never queried/filtered on directly (see examples,
    # constraints, hints, achievements, language_stats above).
    test_results_json  = Column(JSON,        nullable=True)
    # Snapshots of the judge/test-suite versions ACTIVE AT SUBMIT TIME — so a
    # later test-suite fix (e.g. correcting bad test data) doesn't silently
    # make an old submission's percentile/history comparisons misleading.
    judge_version      = Column(String(20),  nullable=True)
    test_suite_version = Column(String(20),  nullable=True)
    ai_review          = Column(JSON,        nullable=True)    # structured review dict
    created_at         = Column(DateTime(timezone=True), default=_now)

    problem = relationship("Problem", back_populates="submissions")


# ──────────────────────────────────────────────────────────────────────────────
# UserProgress
# ──────────────────────────────────────────────────────────────────────────────

class UserProgress(Base):
    """
    Aggregated progress for one user_id.  Updated after every accepted submission.
    """
    __tablename__ = "user_progress"

    user_id          = Column(String(255), primary_key=True)
    solved_problems  = Column(JSON, default=list)   # [problem_id, ...]
    attempted_problems = Column(JSON, default=list) # [problem_id, ...]
    current_streak   = Column(Integer, default=0)
    longest_streak   = Column(Integer, default=0)
    last_active      = Column(Date,    nullable=True)
    xp               = Column(Integer, default=0)
    language_stats   = Column(JSON, default=dict)   # {python: 5, javascript: 2}
    achievements     = Column(JSON, default=list)   # ["binary-search-master", ...]
    updated_at       = Column(DateTime(timezone=True), default=_now, onupdate=_now)


# ──────────────────────────────────────────────────────────────────────────────
# DailyChallenge
# ──────────────────────────────────────────────────────────────────────────────

class DailyChallenge(Base):
    """One problem highlighted per calendar day."""
    __tablename__ = "daily_challenges"

    date       = Column(Date,        primary_key=True)
    problem_id = Column(String(255), ForeignKey("problems.id"), nullable=False)
    bonus_xp   = Column(Integer,     default=50)
