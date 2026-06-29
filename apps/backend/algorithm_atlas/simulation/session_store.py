"""
In-memory simulation session store.

Phase 0: simple dict. This is intentionally behind an interface so that
Phase 1 can swap in a Redis-backed store without touching any call sites.
"""
from __future__ import annotations

import time
from typing import Dict, Iterator, Optional

from loguru import logger

from .engine import SimulationController


class SessionStore:
    """
    Tracks active SimulationController instances by session_id.

    TTL cleanup runs on access — no background task required.
    """

    DEFAULT_TTL_SECONDS = 3600  # 1 hour

    def __init__(self) -> None:
        self._sessions: Dict[str, tuple[SimulationController, float]] = {}
        # (controller, created_at_timestamp)

    def put(self, controller: SimulationController) -> None:
        self._sessions[controller.session_id] = (controller, time.monotonic())
        logger.debug(f"Session created: {controller.session_id}")

    def get(self, session_id: str) -> Optional[SimulationController]:
        entry = self._sessions.get(session_id)
        if entry is None:
            return None
        controller, created_at = entry
        if time.monotonic() - created_at > self.DEFAULT_TTL_SECONDS:
            self.delete(session_id)
            return None
        return controller

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
        logger.debug(f"Session deleted: {session_id}")

    def cleanup_expired(self) -> int:
        now = time.monotonic()
        expired = [
            sid
            for sid, (_, created_at) in self._sessions.items()
            if now - created_at > self.DEFAULT_TTL_SECONDS
        ]
        for sid in expired:
            self.delete(sid)
        return len(expired)

    def __len__(self) -> int:
        return len(self._sessions)

    def __iter__(self) -> Iterator[str]:
        return iter(self._sessions)


# Module-level singleton — replaced with dependency injection in Phase 1
_store = SessionStore()


def get_session_store() -> SessionStore:
    return _store
