"""Binary Heap Operations plugin for Algorithm Atlas."""
from __future__ import annotations

import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    EdgeState,
    GraphTraversalState,
    NodeState,
    SimulationParams,
)


def _heap_to_graph(heap: list):
    """Convert heap array to tree nodes/edges for visualization."""
    import math
    n = len(heap)
    nodes = []
    edges = []
    for i, val in enumerate(heap):
        depth = int(math.log2(i + 1)) if i > 0 else 0
        pos_in_level = i - (2 ** depth - 1)
        level_count = 2 ** depth
        x = (pos_in_level + 0.5) / level_count
        y = depth * 0.18
        nodes.append(NodeState(node_id=str(i), label=str(val), x=x, y=y))
        if i > 0:
            parent = (i - 1) // 2
            edges.append(EdgeState(
                edge_id=f"{parent}-{i}", source=str(parent), target=str(i),
                weight=float(val), directed=True
            ))
    return tuple(nodes), tuple(edges)


class BinaryHeapSimulation(AlgorithmPlugin):
    """Binary Min-Heap: insert elements one by one."""

    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="binary-heap",
            name="Binary Heap Operations",
            category="tree",
            visualization_type="TREE",
            description="Build a min-heap by inserting elements one by one with sift-up.",
            intuition=(
                "Insert at end of array, then sift-up: while parent > child, swap them. "
                "After all insertions, extract-min by swapping root and last, sifting down."
            ),
            complexity_time_best="O(1)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(n)",
            tags=("tree", "heap", "priority-queue", "sift"),
        )

    def initialize(self, params: SimulationParams) -> GraphTraversalState:
        rng = random.Random(params.seed)
        n = int(params.inputs.get("array_size", 7))
        vals = rng.sample(range(1, n * 5 + 1), n)
        nodes, edges = _heap_to_graph([vals[0]])
        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(),
            frontier=tuple(str(v) for v in vals[1:]),
            current=None,
            distances={"size": 1.0},
            path=tuple(),
            description=f"Build min-heap from {vals}",
        )

    def steps(
        self, initial_state: GraphTraversalState
    ) -> Generator[GraphTraversalState, None, GraphTraversalState]:
        desc = initial_state.description
        vals_str = desc.split("[")[1].rstrip("]")
        vals = list(map(int, vals_str.split(", ")))

        heap: list = [vals[0]]

        for val in vals[1:]:
            heap.append(val)
            i = len(heap) - 1

            # Sift up
            while i > 0:
                parent = (i - 1) // 2
                if heap[parent] > heap[i]:
                    heap[parent], heap[i] = heap[i], heap[parent]
                    nodes, edges = _heap_to_graph(heap)
                    yield GraphTraversalState(
                        nodes=nodes,
                        edges=edges,
                        visited=frozenset([str(parent), str(i)]),
                        frontier=tuple(),
                        current=str(i),
                        distances={"size": float(len(heap))},
                        path=tuple(),
                        description=f"Insert {val}: swap [{i}]={heap[i]} with parent [{parent}]={heap[parent]}",
                    )
                    i = parent
                else:
                    break

            nodes, edges = _heap_to_graph(heap)
            yield GraphTraversalState(
                nodes=nodes,
                edges=edges,
                visited=frozenset([str(len(heap) - 1)]),
                frontier=tuple(),
                current=str(len(heap) - 1),
                distances={"size": float(len(heap))},
                path=tuple(),
                description=f"Inserted {val}, heap size={len(heap)}, min={heap[0]}",
            )

        return GraphTraversalState(
            nodes=nodes,
            edges=edges,
            visited=frozenset(str(i) for i in range(len(heap))),
            frontier=tuple(),
            current="0",
            distances={"size": float(len(heap)), "min": float(heap[0])},
            path=tuple(),
            description=f"Heap built: min={heap[0]} size={len(heap)}",
        )
