"""
LLM provider abstraction.

Multiple providers/keys can be pooled behind `RotatingProvider`, which
round-robins across them and falls forward to the next one on failure (rate
limit, timeout, outage) -- spreads load so no single key gets hammered, and
degrades gracefully instead of hard-failing when one key/provider is down.

Swap or add a provider by subclassing LLMProvider and wiring it into
get_provider() -- no agent code changes required.
"""
from __future__ import annotations

import json
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


class OllamaCloudProvider(LLMProvider):
    """Ollama Cloud (ollama.com) via its OpenAI-compatible endpoint
    (POST {base_url}/chat/completions, Bearer auth). Implemented as a plain
    HTTP client rather than the `openai` SDK to avoid adding a second LLM SDK
    dependency for one OpenAI-compatible endpoint."""

    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        import httpx
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60.0,
        )
        self._model = model

    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        body = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }
        async with self._client.stream("POST", "/chat/completions", json=body) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line[len("data:"):].strip()
                if payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                if delta:
                    yield delta

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> str:
        body = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        response = await self._client.post("/chat/completions", json=body)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"].get("content") or ""


class RotatingProvider(LLMProvider):
    """Round-robins across multiple underlying (label, provider) pairs --
    which may be different keys for the same provider, different providers
    entirely, or a mix. Each call starts from the next provider in sequence
    and falls forward through the rest on failure, so a single rate-limited
    or briefly-down key doesn't fail the whole request."""

    def __init__(self, providers: list[tuple[str, LLMProvider]]) -> None:
        if not providers:
            raise ValueError("RotatingProvider needs at least one underlying provider")
        self._providers = providers
        self._next_index = 0

    def _rotation_order(self) -> list[tuple[str, LLMProvider]]:
        n = len(self._providers)
        start = self._next_index
        self._next_index = (self._next_index + 1) % n
        return [self._providers[(start + i) % n] for i in range(n)]

    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        errors: list[str] = []
        for label, provider in self._rotation_order():
            started = False
            try:
                async for chunk in provider.stream(messages, max_tokens=max_tokens, temperature=temperature):
                    started = True
                    yield chunk
                return
            except Exception as exc:
                logger.warning(f"Atlas AI provider '{label}' failed: {exc}")
                errors.append(f"{label}: {exc}")
                if started:
                    # Already yielded partial output to the caller -- can't
                    # silently restart on a different provider without
                    # duplicating text, so the failure has to surface now.
                    raise
                continue
        raise RuntimeError(f"All Atlas AI providers failed: {'; '.join(errors)}")

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> str:
        errors: list[str] = []
        for label, provider in self._rotation_order():
            try:
                return await provider.complete(messages, max_tokens=max_tokens, temperature=temperature)
            except Exception as exc:
                logger.warning(f"Atlas AI provider '{label}' failed: {exc}")
                errors.append(f"{label}: {exc}")
        raise RuntimeError(f"All Atlas AI providers failed: {'; '.join(errors)}")


# ── Singleton factory ──────────────────────────────────────────────────────────

_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        from ..config import get_settings
        s = get_settings()

        pool: list[tuple[str, LLMProvider]] = []
        if s.GROQ_API_KEY:
            pool.append(("groq", GroqProvider(api_key=s.GROQ_API_KEY, model=s.GROQ_MODEL)))
        if s.OLLAMA_API_KEY_1:
            pool.append(("ollama-1", OllamaCloudProvider(
                api_key=s.OLLAMA_API_KEY_1, model=s.OLLAMA_MODEL, base_url=s.OLLAMA_BASE_URL,
            )))
        if s.OLLAMA_API_KEY_2:
            pool.append(("ollama-2", OllamaCloudProvider(
                api_key=s.OLLAMA_API_KEY_2, model=s.OLLAMA_MODEL, base_url=s.OLLAMA_BASE_URL,
            )))

        if not pool:
            raise RuntimeError(
                "Atlas AI requires at least one LLM provider key. "
                "Set GROQ_API_KEY and/or OLLAMA_API_KEY_1/OLLAMA_API_KEY_2 in your .env file."
            )

        _provider = pool[0][1] if len(pool) == 1 else RotatingProvider(pool)
        logger.info(f"Atlas AI provider initialised: {[label for label, _ in pool]}")
    return _provider
