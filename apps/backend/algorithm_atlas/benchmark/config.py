"""
Category-aware benchmark configuration.

Each category has a canonical size_param and sensible default sizes.
Algorithms can override these via their manifest's `benchmark` key.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BenchmarkConfig:
    size_param: str
    default_sizes: tuple[int, ...] = field(default_factory=tuple)
    label: str = "n"


# Maps category slug → benchmark config
CATEGORY_CONFIGS: dict[str, BenchmarkConfig] = {
    "sorting": BenchmarkConfig(
        size_param="array_size",
        default_sizes=(10, 25, 50, 100, 200, 500, 1000),
        label="array size",
    ),
    "searching": BenchmarkConfig(
        size_param="array_size",
        default_sizes=(10, 25, 50, 100, 200, 500, 1000),
        label="array size",
    ),
    "graph": BenchmarkConfig(
        size_param="node_count",
        default_sizes=(5, 10, 20, 50, 100, 200),
        label="nodes",
    ),
    "tree": BenchmarkConfig(
        size_param="node_count",
        default_sizes=(5, 10, 20, 50, 100, 200),
        label="nodes",
    ),
    "dynamic-programming": BenchmarkConfig(
        size_param="n",
        default_sizes=(5, 10, 20, 50, 100, 200),
        label="n",
    ),
    "string": BenchmarkConfig(
        size_param="n",
        default_sizes=(10, 25, 50, 100, 200, 500),
        label="string length",
    ),
    "number-theory": BenchmarkConfig(
        size_param="n",
        default_sizes=(10, 50, 100, 500, 1000, 5000),
        label="n",
    ),
    "computational-geometry": BenchmarkConfig(
        size_param="n",
        default_sizes=(5, 10, 20, 50, 100, 200),
        label="points",
    ),
    "cellular-automata": BenchmarkConfig(
        size_param="n",
        default_sizes=(10, 15, 20, 25, 30, 40, 50),
        label="grid size",
    ),
    "distributed-systems": BenchmarkConfig(
        size_param="nodes",
        default_sizes=(3, 4, 5, 6, 7, 8, 10),
        label="nodes",
    ),
    "cryptography": BenchmarkConfig(
        size_param="rounds",
        default_sizes=(1, 2, 4, 8, 16, 32, 64),
        label="rounds",
    ),
    "optimization": BenchmarkConfig(
        size_param="steps",
        default_sizes=(10, 25, 50, 100, 200, 500),
        label="iterations",
    ),
    "probability": BenchmarkConfig(
        size_param="n",
        default_sizes=(100, 250, 500, 1000, 2000, 5000),
        label="trials",
    ),
    "data-structures": BenchmarkConfig(
        size_param="n",
        default_sizes=(10, 25, 50, 100, 200, 500, 1000),
        label="elements",
    ),
}

_DEFAULT_CONFIG = BenchmarkConfig(
    size_param="n",
    default_sizes=(10, 25, 50, 100, 200, 500),
    label="n",
)


def get_config(category: str) -> BenchmarkConfig:
    return CATEGORY_CONFIGS.get(category, _DEFAULT_CONFIG)
