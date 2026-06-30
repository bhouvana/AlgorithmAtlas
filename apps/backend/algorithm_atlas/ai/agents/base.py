"""Base agent — all agents inherit from this."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..context_builder import AtlasContext, context_to_text
from ..provider import ChatMessage, LLMProvider


class BaseAgent(ABC):
    @property
    @abstractmethod
    def system_prompt(self) -> str: ...

    async def stream(
        self,
        message: str,
        context: AtlasContext,
        history: list[ChatMessage],
        provider: LLMProvider,
        memories: dict[str, str],
    ) -> AsyncIterator[str]:
        system = self._build_system(context, memories)
        messages = [ChatMessage(role="system", content=system)]
        messages.extend(history[-10:])
        messages.append(ChatMessage(role="user", content=message))
        async for token in provider.stream(messages):
            yield token

    def _build_system(self, context: AtlasContext, memories: dict[str, str]) -> str:
        system = self.system_prompt
        ctx_text = context_to_text(context)
        if ctx_text:
            system += f"\n\n## Current Platform Context\n{ctx_text}"
        if memories:
            mem_lines = "\n".join(f"- {k}: {v}" for k, v in memories.items())
            system += f"\n\n## What You Remember About This User\n{mem_lines}"
        return system
