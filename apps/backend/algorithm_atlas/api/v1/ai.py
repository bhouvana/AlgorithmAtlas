"""
Atlas AI endpoints.

POST /api/v1/ai/chat     — streaming SSE chat (main conversation)
POST /api/v1/ai/complete — synchronous inline code completion (notebook)
GET  /api/v1/ai/memory   — read user memory
POST /api/v1/ai/memory   — write / update user memory
"""
from __future__ import annotations

import json
import re
from typing import AsyncIterator, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...ai.context_builder import AtlasContext
from ...ai.memory import delete_memory, get_user_memories, upsert_memory
from ...ai.orchestrator import route
from ...ai.provider import ChatMessage, get_provider
from ...database import get_db
from ...plugins.registry import get_registry

router = APIRouter(prefix="/ai", tags=["atlas-ai"])


# ── Request / response models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    context: AtlasContext
    history: list[dict] = []   # [{"role": "user"|"assistant", "content": "..."}]


class CompleteRequest(BaseModel):
    prefix: str
    language: str = "python"
    context: Optional[AtlasContext] = None


class CompleteResponse(BaseModel):
    completion: str


class MemoryWriteRequest(BaseModel):
    user_id: str
    key: str
    value: str


class MemoryDeleteRequest(BaseModel):
    user_id: str
    key: str


# ── Helpers ────────────────────────────────────────────────────────────────────

_CMD_SENTINEL_RE = re.compile(r"__ATLAS_COMMANDS__(.*?)__END__", re.DOTALL)
_INTERVIEW_SENTINEL_RE = re.compile(r"__ATLAS_INTERVIEW_START__(.*?)__END__", re.DOTALL)
_EDITOR_WRITE_RE = re.compile(r"__ATLAS_EDITOR_WRITE__(.*?)__END__", re.DOTALL)
_NAVIGATE_RE = re.compile(r"__ATLAS_NAVIGATE__(.*?)__END__", re.DOTALL)
_SENTINEL_ANCHOR = "__ATLAS_"


def _split_at_sentinel(buf: str) -> tuple[str, str]:
    """Split buf into (safe_to_emit, keep_buffered).

    The safe part contains no complete or partial sentinel prefix, so it can
    be streamed to the client immediately without risk of leaking sentinel text.
    """
    idx = buf.find(_SENTINEL_ANCHOR)
    if idx >= 0:
        return buf[:idx], buf[idx:]
    # Check whether the tail of buf is a partial prefix of _SENTINEL_ANCHOR
    anchor = _SENTINEL_ANCHOR
    for n in range(min(len(anchor) - 1, len(buf)), 0, -1):
        if buf.endswith(anchor[:n]):
            return buf[:-n], buf[-n:]
    return buf, ""


def _build_history(raw: list[dict]) -> list[ChatMessage]:
    messages = []
    for item in raw[-10:]:
        role = item.get("role", "user")
        content = item.get("content", "")
        if role in ("user", "assistant", "system") and content:
            messages.append(ChatMessage(role=role, content=content))
    return messages


def _build_catalog_summary(limit: int = 60) -> str:
    """Compact catalog text for SearchAgent context injection."""
    try:
        registry = get_registry()
        lines = []
        for alg in list(registry.list_all())[:limit]:
            m = alg.manifest
            cplx = m.get("complexity", {})
            avg = cplx.get("time_average", "?")
            lines.append(
                f"- {m['name']} [{m['category']}] avg={avg} | {m.get('description','')[:80]}"
            )
        return "\n".join(lines)
    except Exception:
        return ""


def _flush_sentinels(buf: str) -> tuple[list[str], str]:
    """Extract all complete sentinels from buf. Returns (sse_events, cleaned_buf)."""
    events: list[str] = []

    cmd_match = _CMD_SENTINEL_RE.search(buf)
    if cmd_match:
        try:
            cmds = json.loads(cmd_match.group(1))
            events.append(json.dumps({"type": "commands", "commands": cmds}))
        except (json.JSONDecodeError, ValueError):
            pass
        buf = _CMD_SENTINEL_RE.sub("", buf)

    iv_match = _INTERVIEW_SENTINEL_RE.search(buf)
    if iv_match:
        try:
            problem = json.loads(iv_match.group(1))
            events.append(json.dumps({"type": "interview_start", "problem": problem}))
        except (json.JSONDecodeError, ValueError):
            pass
        buf = _INTERVIEW_SENTINEL_RE.sub("", buf)

    ew_match = _EDITOR_WRITE_RE.search(buf)
    if ew_match:
        try:
            payload = json.loads(ew_match.group(1))
            events.append(json.dumps({"type": "editor_write", **payload}))
        except (json.JSONDecodeError, ValueError):
            pass
        buf = _EDITOR_WRITE_RE.sub("", buf)

    nav_match = _NAVIGATE_RE.search(buf)
    if nav_match:
        try:
            payload = json.loads(nav_match.group(1))
            events.append(json.dumps({"type": "navigate", **payload}))
        except (json.JSONDecodeError, ValueError):
            pass
        buf = _NAVIGATE_RE.sub("", buf)

    return events, buf


async def _event_stream(
    message: str,
    context: AtlasContext,
    history: list[ChatMessage],
    memories: dict[str, str],
) -> AsyncIterator[str]:
    try:
        provider = get_provider()
    except Exception as exc:
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return

    agent = route(message, context)

    # Inject catalog for SearchAgent and NavigationAgent
    from ...ai.agents.search import SearchAgent
    from ...ai.agents.navigation import NavigationAgent
    kwargs: dict = {}
    if isinstance(agent, (SearchAgent, NavigationAgent)):
        kwargs["catalog_summary"] = _build_catalog_summary()

    try:
        token_buffer = ""
        async for token in agent.stream(message, context, history, provider, memories, **kwargs):
            token_buffer += token

            # Flush any complete sentinels first
            sse_events, token_buffer = _flush_sentinels(token_buffer)
            for ev in sse_events:
                yield f"data: {ev}\n\n"

            # Emit the safe prefix — text that cannot be the start of any sentinel
            safe, token_buffer = _split_at_sentinel(token_buffer)
            if safe:
                yield f"data: {json.dumps({'type': 'token', 'content': safe})}\n\n"

        # End of stream — flush any sentinels still in buffer, then remaining text
        sse_events, token_buffer = _flush_sentinels(token_buffer)
        for ev in sse_events:
            yield f"data: {ev}\n\n"
        token_buffer = token_buffer.strip()
        if token_buffer:
            yield f"data: {json.dumps({'type': 'token', 'content': token_buffer})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except RuntimeError as exc:
        event = json.dumps({"type": "error", "message": str(exc)})
        yield f"data: {event}\n\n"
    except Exception as exc:
        event = json.dumps({"type": "error", "message": f"Atlas AI error: {exc}"})
        yield f"data: {event}\n\n"


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/chat")
async def chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    memories = await get_user_memories(db, body.context.userId)
    history = _build_history(body.history)

    return StreamingResponse(
        _event_stream(body.message, body.context, history, memories),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/complete", response_model=CompleteResponse)
async def complete(body: CompleteRequest):
    """
    Inline code completion for the notebook editor.
    Returns a short continuation of the code prefix.
    """
    try:
        provider = get_provider()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    algo_context = ""
    if body.context and body.context.algorithm:
        a = body.context.algorithm
        algo_context = (
            f"The user is implementing or studying {a.name} "
            f"({a.category}). Completions should be relevant to this algorithm."
        )

    system = (
        f"You are an expert {body.language} programmer. "
        "Complete the code prefix provided by the user. "
        "Return ONLY the completion text — no explanation, no markdown, no code fences. "
        "The completion should be at most 3–5 lines and flow naturally from the prefix. "
        f"{algo_context}"
    )

    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(
            role="user",
            content=f"Complete this {body.language} code:\n{body.prefix}",
        ),
    ]

    completion = await provider.complete(messages, max_tokens=200, temperature=0.2)
    return CompleteResponse(completion=completion.strip())


@router.get("/memory")
async def read_memory(user_id: str, db: AsyncSession = Depends(get_db)):
    memories = await get_user_memories(db, user_id)
    return {"user_id": user_id, "memories": memories}


@router.post("/memory")
async def write_memory(body: MemoryWriteRequest, db: AsyncSession = Depends(get_db)):
    await upsert_memory(db, body.user_id, body.key, body.value)
    return {"status": "ok", "key": body.key}


@router.delete("/memory")
async def remove_memory(body: MemoryDeleteRequest, db: AsyncSession = Depends(get_db)):
    deleted = await delete_memory(db, body.user_id, body.key)
    return {"status": "ok" if deleted else "not_found", "key": body.key}
