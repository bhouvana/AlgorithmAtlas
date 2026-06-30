"""
LLM provider abstraction.

GroqProvider is the default implementation. Swap by subclassing LLMProvider
and updating get_provider() — no agent code changes required.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

from loguru import logger


@dataclass
class ChatMessage:
    role: str   # "system" | "user" | "assistant"
    content: str


class LLMProvider(ABC):
    @abstractmethod
    def stream(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]: ...

    @abstractmethod
    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> str: ...


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        from groq import AsyncGroq   # deferred — not imported if key is absent
        self._client = AsyncGroq(api_key=api_key)
        self._model = model

    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False,
        )
        return response.choices[0].message.content or ""


# ── Singleton factory ──────────────────────────────────────────────────────────

_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        from ..config import get_settings
        s = get_settings()
        if not s.GROQ_API_KEY:
            raise RuntimeError(
                "Atlas AI requires a Groq API key. "
                "Set GROQ_API_KEY in your .env file."
            )
        _provider = GroqProvider(api_key=s.GROQ_API_KEY, model=s.GROQ_MODEL)
        logger.info(f"Atlas AI provider initialised (model: {s.GROQ_MODEL})")
    return _provider
