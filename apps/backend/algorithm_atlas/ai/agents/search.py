"""
Search agent — semantic search over the algorithm catalog and lesson curriculum.

The orchestrator injects a catalog summary so the LLM can reason over real data.
"""
from __future__ import annotations

from typing import AsyncIterator

from .base import BaseAgent
from ..context_builder import AtlasContext, context_to_text
from ..provider import ChatMessage, LLMProvider


class SearchAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return """\
You are Atlas AI in Search Mode — a semantic search engine for Algorithm Atlas.

Help users find algorithms, lessons, and concepts using natural language.

## Response Format
1. **Direct answer** — What you found that matches the query
2. **Primary results** — 3–5 most relevant items, each with:
   - **Algorithm/Lesson name** — one-sentence description — complexity if applicable
   - Link hint: "View it at /algorithms/{slug}" or "Learn it at /learning/{id}"
3. **Related concepts** — 2–3 adjacent topics worth exploring
4. **Recommendation** — Where to start if they're new to this area

## Available Categories
Dynamic Programming · Sorting · Searching · Graph · Tree · String · Number Theory ·
Cryptography · Divide & Conquer · Distributed Systems · Backtracking · Machine Learning ·
Greedy · Cellular Automata · Optimization · Computational Geometry · Probability ·
Randomized · Data Structures

## Formatting
- Bold algorithm names: **Dijkstra's Algorithm**
- Show complexity inline: $O(E \\log V)$
- Group by category when returning multiple results
- Always explain WHY each result matches the query — not just the name"""

    async def stream(
        self,
        message: str,
        context: AtlasContext,
        history: list[ChatMessage],
        provider: LLMProvider,
        memories: dict[str, str],
        catalog_summary: str = "",
    ) -> AsyncIterator[str]:
        system = self._build_system(context, memories)
        if catalog_summary:
            system += f"\n\n## Algorithm Catalog (current data)\n{catalog_summary}"

        messages = [ChatMessage(role="system", content=system)]
        messages.extend(history[-6:])
        messages.append(ChatMessage(role="user", content=message))

        async for token in provider.stream(messages):
            yield token
