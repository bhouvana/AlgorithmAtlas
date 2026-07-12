"""
Progress API

GET /api/v1/progress/:user_id   user progress summary
GET /api/v1/challenges/today    today's daily challenge
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...models.atlas_code import DailyChallenge, Problem, UserProgress

router = APIRouter(tags=["atlas-code"])


# ── Response schemas ──────────────────────────────────────────────────────────

class ProgressOut(BaseModel):
    user_id: str
    solved_problems: list[str]
    attempted_problems: list[str]
    current_streak: int
    longest_streak: int
    xp: int
    language_stats: dict
    achievements: list

    class Config:
        from_attributes = True


class DailyChallengeOut(BaseModel):
    date: date
    problem_id: str
    bonus_xp: int
    problem_title: str
    problem_difficulty: str
    problem_category: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/progress/{user_id}", response_model=ProgressOut)
async def get_progress(user_id: str, db: AsyncSession = Depends(get_db)) -> ProgressOut:
    result = await db.execute(select(UserProgress).where(UserProgress.user_id == user_id))
    progress = result.scalar_one_or_none()
    if not progress:
        # Return empty progress rather than 404 — first-time users are valid
        return ProgressOut(
            user_id=user_id,
            solved_problems=[],
            attempted_problems=[],
            current_streak=0,
            longest_streak=0,
            xp=0,
            language_stats={},
            achievements=[],
        )
    return ProgressOut.model_validate(progress)


@router.get("/challenges/today", response_model=DailyChallengeOut)
async def get_today_challenge(db: AsyncSession = Depends(get_db)) -> DailyChallengeOut:
    today = datetime.now(timezone.utc).date()
    result = await db.execute(
        select(DailyChallenge).where(DailyChallenge.date == today)
    )
    challenge = result.scalar_one_or_none()
    if not challenge:
        raise HTTPException(status_code=404, detail="No daily challenge set for today")

    prob_result = await db.execute(select(Problem).where(Problem.id == challenge.problem_id))
    problem = prob_result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Daily challenge problem not found")

    return DailyChallengeOut(
        date=challenge.date,
        problem_id=challenge.problem_id,
        bonus_xp=challenge.bonus_xp,
        problem_title=problem.title,
        problem_difficulty=problem.difficulty,
        problem_category=problem.category,
    )
