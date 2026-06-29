# Community Plugins

This directory hosts third-party algorithm plugins contributed via pull request.

## How to contribute

1. **Fork** the repository and create a branch: `plugin/<your-algorithm-name>`.
2. **Create** your plugin directory at `plugins/community/<category>/<algorithm-slug>/`.
3. **Implement** the required files (see structure below).
4. **Validate** your plugin locally: `python scripts/validate_plugin.py plugins/community/<category>/<algorithm-slug>/`.
5. **Open a PR** — CI will run the validator automatically.

## Required directory structure

```
plugins/community/<category>/<algorithm-slug>/
├── manifest.json      # metadata (see schema below)
├── algorithm.py       # plugin implementation
└── tests/
    └── test_plugin.py # at least one test
```

## manifest.json schema

```json
{
  "schema_version": "1.0",
  "id": "my-algorithm",         // lowercase, hyphens only
  "name": "My Algorithm",
  "version": "1.0.0",
  "category": "sorting",        // must match parent directory name
  "visualization_type": "ARRAY_BARS",
  "execution_target": "server", // "server" | "wasm" | "both"
  "entry_point": "algorithm.py",
  "description": "One paragraph explaining what this algorithm does.",
  "intuition": "Optional: plain-language mental model.",
  "complexity": {
    "time_best":    "O(n log n)",
    "time_average": "O(n log n)",
    "time_worst":   "O(n²)",
    "space":        "O(log n)"
  },
  "references": [
    { "title": "...", "type": "paper|book|video|article", "url": "..." }
  ],
  "tags": ["sorting", "comparison", "in-place"],
  "params_schema": { ... },     // optional, JSON Schema for user parameters
  "benchmark_enabled": false
}
```

### Allowed `visualization_type` values

`ARRAY_BARS` · `ARRAY_BARS_SEARCH` · `GRAPH` · `TREE` · `MATRIX` · `GRID` ·
`CURVE` · `PARTICLE_FIELD` · `NETWORK_TOPOLOGY` · `GEOMETRIC` ·
`STATE_MACHINE` · `PROBABILITY_SPACE` · `TIMELINE`

## algorithm.py contract

```python
from algorithm_atlas_sdk.protocols import AlgorithmPlugin
from algorithm_atlas_sdk.types import SortState  # or other state type

class MyAlgorithmPlugin(AlgorithmPlugin):
    def metadata(self):
        return { ... }  # mirrors manifest fields

    def initialize(self, params):
        return SortState(array=[...], ...)

    def steps(self, initial_state):
        # yield successive states
        yield ...
```

### Allowed imports

- `algorithm_atlas_sdk.*`
- Standard library: `math`, `random`, `heapq`, `bisect`, `collections`, `itertools`, `functools`, `enum`, `dataclasses`, `typing`, `typing_extensions`
- Approved scientific packages: `numpy`, `scipy`, `networkx`, `sympy`, `pandas`, `polars`

Internal packages (`algorithm_atlas`, `fastapi`, `sqlalchemy`, etc.) are **forbidden** and will fail CI validation.

## tests/test_plugin.py contract

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))
# ... load your plugin ...

def test_produces_frames():
    plugin = MyAlgorithmPlugin()
    state = plugin.initialize({"array_size": 10})
    frames = list(plugin.steps(state))
    assert len(frames) > 0

def test_sorted_result():
    ...
```

Run locally with `pytest plugins/community/<category>/<slug>/tests/`.

## Review criteria

- [ ] `validate_plugin.py` exits 0
- [ ] Algorithm is not already in the catalog
- [ ] At least 2 tests covering frames produced and final state correctness
- [ ] No forbidden imports
- [ ] `description` is ≥ 2 sentences and explains the algorithm
- [ ] `complexity` values are correct and sourced

## Maintainer notes

- Community plugins live in `plugins/community/` and are loaded alongside first-party plugins at server startup.
- The validator is authoritative — if it passes, the plugin structure is correct.
- Category slug in `manifest.json` must match the parent folder name exactly.
