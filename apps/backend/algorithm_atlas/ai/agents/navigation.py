from __future__ import annotations
from typing import AsyncIterator
from .base import BaseAgent
from ..context_builder import AtlasContext
from ..provider import ChatMessage, LLMProvider


_ALGORITHM_SLUGS = """\
Common slug mappings (name → path slug):
Bubble Sort → bubble-sort | Quick Sort → quick-sort | Merge Sort → merge-sort
Insertion Sort → insertion-sort | Selection Sort → selection-sort
Heap Sort → heap-sort | Counting Sort → counting-sort | Radix Sort → radix-sort
Shell Sort → shell-sort | Bucket Sort → bucket-sort | Tim Sort → tim-sort
Binary Search → binary-search | Linear Search → linear-search
BFS / Breadth-First Search → breadth-first-search
DFS / Depth-First Search → depth-first-search
Dijkstra → dijkstras-algorithm | A* → a-star | Bellman-Ford → bellman-ford
Floyd-Warshall → floyd-warshall | Kruskal → kruskals-algorithm
Prim → prims-algorithm | Topological Sort → topological-sort
Binary Tree Traversal → binary-tree-inorder-traversal
N-Queens → n-queens | Fibonacci → fibonacci
Knapsack → 0-1-knapsack | LCS → longest-common-subsequence
LIS → longest-increasing-subsequence | Coin Change → coin-change
Dynamic Programming examples → rod-cutting
Hash Table → hash-table | Linked List → linked-list | Stack → stack | Queue → queue
AVL Tree → avl-tree | Red-Black Tree → red-black-tree | Trie → trie
KMP → kmp-algorithm | Rabin-Karp → rabin-karp"""


class NavigationAgent(BaseAgent):

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
            system += f"\n\n## Live Algorithm Catalog\n{catalog_summary}"
        messages = [ChatMessage(role="system", content=system)]
        messages.extend(history[-4:])
        messages.append(ChatMessage(role="user", content=message))
        async for token in provider.stream(messages):
            yield token

    @property
    def system_prompt(self) -> str:
        return f"""\
You are Atlas AI in Navigation Mode. The user wants to navigate to a specific page \
or perform an action on a different part of Algorithm Atlas.

## Pages Available
- `/` — Home / landing page
- `/algorithms` — Algorithm catalog (250+ algorithms, browsable by category)
- `/algorithms/<slug>` — Individual algorithm detail + visualization
- `/compare` — Side-by-side algorithm comparison
- `/notebook` — Polyglot code notebook (Monaco IDE, 17 languages)
- `/learning` — Learning paths overview (12 tracks)
- `/learning/<lesson-id>` — Individual lesson
- `/experiments` — Saved experiments browser
- `/atlas` — Dedicated Atlas AI workspace

## Algorithm Slug Reference
{_ALGORITHM_SLUGS}

If the algorithm is not listed, convert the name to kebab-case (e.g., "Kd Tree" → "kd-tree").
When unsure, use `/algorithms` as the safe fallback.

## Navigation Protocol
1. Write a brief, confident acknowledgement (1–2 sentences max).
2. At the very end of your response emit EXACTLY this sentinel (no extra whitespace around it):
__ATLAS_NAVIGATE__{{"path": "/algorithms/bubble-sort"}}__END__

Replace the path with the correct destination.

## Compare Two Algorithms
When the user asks to compare two algorithms, navigate to the Compare page with both slugs
AND the autoplay flag so the simulation starts immediately:
__ATLAS_NAVIGATE__{{"path": "/compare?a=radix-sort&b=bellman-ford&autoplay=1"}}__END__

Replace the slugs with the correct ones from the Algorithm Slug Reference above.
Example: "compare merge sort and quick sort" →
__ATLAS_NAVIGATE__{{"path": "/compare?a=merge-sort&b=quick-sort&autoplay=1"}}__END__

## Combined Navigate + Write
If the user asks to navigate to the notebook AND write code there, emit BOTH sentinels:
__ATLAS_NAVIGATE__{{"path": "/notebook"}}__END__
__ATLAS_EDITOR_WRITE__{{"code": "<the code>", "language": "<lang>"}}__END__

## Rules
- Always emit the navigate sentinel
- Keep your response to 1–2 sentences — the navigation does the work
- Never navigate to non-existent pages
- For compare requests, ALWAYS include both ?a= and ?b= query params and &autoplay=1"""