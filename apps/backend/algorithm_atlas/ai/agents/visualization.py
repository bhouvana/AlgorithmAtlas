"""
Visualization agent — explains the current frame and returns simulation control
commands the frontend executes via SimulationProxy.

Command JSON block detected by orchestrator → emitted as type:commands SSE event.
"""
from __future__ import annotations

import json
import re
from typing import AsyncIterator

from .base import BaseAgent
from ..context_builder import AtlasContext
from ..provider import ChatMessage, LLMProvider


_CMD_BLOCK_RE = re.compile(
    r"```json\s*(\{[\s\S]*?\"commands\"\s*:[\s\S]*?\})\s*```",
    re.IGNORECASE,
)


class VisualizationAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return """\
You are Atlas AI in Visualization Mode — a simulation controller for Algorithm Atlas.

You can both explain what's happening in the visualization AND control it.

## Simulation Commands
When you want to control the simulation, include EXACTLY ONE JSON block like this:

```json
{"commands": [
  {"action": "play"},
  {"action": "pause"},
  {"action": "seek", "frame": 0},
  {"action": "set_speed", "value": 0.5},
  {"action": "reset"},
  {"action": "step_forward"},
  {"action": "step_backward"}
]}
```

You can chain multiple commands in one array (they execute in order).

## Common Mappings
- "replay" / "start over"     → [seek(0), play()]
- "slow down"                 → [set_speed(0.3)]
- "speed up"                  → [set_speed(2.0)]
- "normal speed"              → [set_speed(1.0)]
- "pause"                     → [pause()]
- "jump to frame N"           → [seek(N)]
- "explain step by step"      → [seek(0), set_speed(0.3), play()]
- "next step"                 → [step_forward()]

## Response Structure
1. One sentence: what you're about to do
2. (Optional) The commands JSON block
3. Explanation of what the simulation will show after the command

Always describe the exact algorithm state visible at the current frame before issuing
any commands. Never guess what a frame shows — read it from context."""

    async def stream(
        self,
        message: str,
        context: AtlasContext,
        history: list[ChatMessage],
        provider: LLMProvider,
        memories: dict[str, str],
    ) -> AsyncIterator[str]:
        buffer = ""
        commands_emitted = False
        async for token in super().stream(message, context, history, provider, memories):
            buffer += token
            yield token

        # After full response is buffered, extract and emit commands as a
        # special JSON line the SSE layer will convert to type:commands.
        if not commands_emitted:
            match = _CMD_BLOCK_RE.search(buffer)
            if match:
                try:
                    data = json.loads(match.group(1))
                    cmds = data.get("commands", [])
                    if cmds:
                        # Sentinel the orchestrator/endpoint layer listens for.
                        yield f"\n__ATLAS_COMMANDS__{json.dumps(cmds)}__END__"
                except (json.JSONDecodeError, KeyError):
                    pass
