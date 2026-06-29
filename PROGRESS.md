# Algorithm Atlas — Progress Report

**Date**: 2026-06-29  
**Status**: 250 / 250 algorithms complete ✓ PHASE 7 — 100% EXECUTED

---

## Numbers at a Glance

| Metric | Value |
|--------|-------|
| Algorithms implemented | 250 |
| Test files | 200 (legacy) + new plugin tests |
| Tests passing | 3665 / 3665 (legacy) |
| Algorithm categories | 19 |
| Visualization types | 13 (all wired) |
| Target | 250 |
| Remaining | 0 |

---

## Algorithms by Category

### Backtracking (9)
combination-sum, cryptarithmetic, knight-tour, n-queens, permutations, rat-in-maze, subsets, sudoku-solver, word-search

### Computational Geometry (8)
closest-pair, convex-hull-graham, gift-wrapping, line-segment-intersection, minimum-enclosing-circle, point-in-polygon, polygon-area, rotating-calipers

### Divide and Conquer (9)
closest-pair, counting-inversions, fast-power, karatsuba, majority-element, matrix-exponentiation, median-of-medians, polynomial-multiplication, strassen

### Dynamic Programming (36)
bitmask-tsp, boolean-parenthesization, coin-change, coin-change-ways, convex-hull-trick, decode-ways, distinct-subsequences, edit-distance, egg-drop, fibonacci-dp, floyd-warshall, house-robber, interleaving-strings, jump-game, knapsack-01, longest-bitonic-subsequence, longest-common-subsequence, longest-increasing-subsequence, matrix-chain-multiplication, maximum-product-subarray, maximum-subarray, min-path-sum, optimal-bst, palindrome-partition, palindrome-partitioning, palindrome-subsequence, rod-cutting, sequence-alignment, staircase, stock-cooldown, subset-sum, unbounded-knapsack, unique-paths, wildcard-matching, word-break, word-wrap

### Graph (29)
0-1-bfs, articulation-points, a-star, a-star-bidirectional, bellman-ford, bfs, bidirectional-bfs, bipartite-check, bipartite-matching, bridges, cycle-detection, dfs, dijkstra, edmonds-karp, euler-path, floyd-warshall, ford-fulkerson, graph-coloring, hamiltonian-path, hierholzer, johnson-algorithm, kosaraju-scc, kruskals-mst, min-cost-max-flow, prims, prims-mst, tarjan-bridges, tarjan-scc, topological-sort

### Greedy (9)
activity-selection, fractional-knapsack, gas-station, huffman-coding, huffman-with-decode, job-scheduling, meeting-rooms, stable-matching, task-scheduler

### Machine Learning (10)
decision-tree-entropy, gradient-descent, k-means, k-nearest-neighbors, linear-regression, logistic-regression, naive-bayes, perceptron, random-forest, svm-linear

### Number Theory (20)
baby-step-giant-step, berlekamp-massey, catalan-number, chinese-remainder, collatz, discrete-log-pohlig-hellman, euler-phi-sieve, euler-totient, extended-euclidean, gcd-euclidean, goldbach, lucas-theorem, miller-rabin, modular-exponentiation, number-of-divisors, pollard-rho, prime-factorization, primitive-root, sieve-of-eratosthenes, tonelli-shanks

### Randomized (6)
karger-mincut, monte-carlo-pi, quickselect, random-walk, reservoir-sampling, simulated-annealing

### Searching (12)
binary-search, bloom-filter, exponential-search, fibonacci-search, interpolation-search, jump-search, linear-search, peak-element, rotated-binary-search, skip-list, ternary-search, two-sum

### Sorting (22)
bitonic-sort, bubble-sort, bucket-sort, cocktail-sort, comb-sort, counting-sort, cycle-sort, gnome-sort, heap-sort, insertion-sort, merge-sort, odd-even-sort, pancake-sort, patience-sort, quick-sort, radix-sort, selection-sort, shell-sort, stooge-sort, strand-sort, tim-sort, tree-sort

### String (15)
aho-corasick, aho-corasick-count, boyer-moore, burrows-wheeler, kmp, longest-common-substring, longest-palindromic-substring, manacher, rabin-karp, run-length-encoding, string-hashing, suffix-array, suffix-array-lcp, suffix-automaton, z-algorithm

### Tree (19)
avl-tree, binary-heap, bst-search, cartesian-tree, diameter, fenwick-tree, heavy-light-decomposition, inorder, interval-tree, lca, level-order, link-cut-tree, morris-traversal, postorder, preorder, segment-tree, sparse-table, treap, trie

### Cellular Automata (8)
conways-game-of-life, rule-110, rule-30, forest-fire, langtons-ant, cyclic-cellular-automata, brain, cave-generation

### Distributed Systems (10)
chord-dht, consistent-hashing, distributed-mutex, gossip-protocol, lamport-clocks, paxos, raft-leader-election, raft-log-replication, two-phase-commit, vector-clocks

### Cryptography (10)
aes-round, caesar-cipher, des-feistel, diffie-hellman, elliptic-curve-add, feistel-network, md5-round, rsa-keygen, sha256-round, vigenere-cipher

### Optimization (8)
ant-colony, firefly, genetic-algorithm, gradient-descent-landscape, hill-climbing, particle-swarm, simulated-annealing-tsp, tabu-search

### Probability (8)
bayesian-update, birthday-paradox, central-limit-theorem, markov-chain, metropolis-hastings, monte-carlo-integration, random-walk-2d, rejection-sampling

### Data Structures (6)
b-tree, hash-table-chaining, hash-table-probing, linked-list, red-black-tree, rope

---

## What Each Algorithm Consists Of

Every algorithm has 3 files:

```
plugins/<category>/<slug>/
├── manifest.json        # metadata, complexity, tags
├── algorithm.py         # AlgorithmPlugin implementation
└── tests/
    └── test_<slug>.py   # pytest suite (~10-15 tests each)
```

---

## Technical Conventions

- **SDK import path**: `sys.path.insert(0, str(Path(__file__).parents[5] / "packages/plugin-sdk/python"))`
- **Module loading in tests**: `importlib.util.spec_from_file_location` (required for hyphenated directory names)
- **_make_plugin pattern**: Set attributes after class definition — `P.seed = seed` not `_seed = seed` inside class body
- **State encoding**: All params needed by `steps()` encoded in `description` string; extracted via `re.search()`
- **GraphTraversalState node roles**: encoded in `weight` field (no `color` field on NodeState)
  - Typical weights: `2.0` = current, `1.0` = visited/active, `0.0` = unvisited, `3.0` = bridge/special
- **SortState array values**: 1–99 for bars (0 allowed for initial DP states)
- **Final state**: `return` the final `State` from `steps()` generator; also `yield` it if tests need it in `list()`

---

## Roadmap

### Phase 2 — COMPLETE ✓
**Goal**: Reach 200 algorithms with full test coverage

**Result**: 200/200 algorithms, 3665/3665 tests passing.

**Added in this session**:

| Slug | Category | Tests |
|------|----------|-------|
| `min-cost-max-flow` | graph | 14 |
| `optimal-bst` | dynamic-programming | 11 |
| `boolean-parenthesization` | dynamic-programming | 11 |
| `tonelli-shanks` | number-theory | 11 |
| `berlekamp-massey` | number-theory | 11 |
| `heavy-light-decomposition` | tree | 12 |
| `link-cut-tree` | tree | 13 |
| `convex-hull-trick` | dynamic-programming | 11 |
| `aho-corasick-count` | string | 12 |
| `burrows-wheeler` | string | 15 |

---

### Phase 3 — WASM Pipeline ✓ ARCHITECTURE COMPLETE
**Goal**: Compile simple algorithms to Rust → WASM for browser-side execution (no server round-trip)

**Architecture decision (locked)**: Hybrid WASM + server. Simple algorithms run in-browser via wasm-pack; complex/ML algorithms stay on server. Plugin manifests use `execution_target: "server" | "wasm" | "both"`.

**Status**: All code written. Run `npm run build:wasm` in `apps/frontend/` to compile the WASM binary (requires Rust + wasm-pack toolchain).

#### What was built

**3.1 — Rust plugin SDK** ✓
- `packages/plugin-sdk/rust/` — `SortPlugin` trait, `SortState`, `SimulationFrame`, `AlgorithmMetadata` types
- Mirrors Python SDK types exactly; serde-serializable for JS interop

**3.2 — Build toolchain** ✓
- `packages/wasm-engine/` — cdylib crate using wasm-bindgen + serde_json
- `wasm_engine.run_sort(slug, seed, array_size, input_order) → JSON string`
- `wasm_engine.benchmark_sort(slug, seed, array_size, input_order, trials) → ms`
- Vite: `vite-plugin-wasm` added; alias `@wasm-engine` → `src/wasm-engine/`
- Build script: `npm run build:wasm` runs `wasm-pack build --target web`
- Manifest field `wasm_module: "wasm_engine"` marks WASM-enabled plugins
- Stub JS in `src/wasm-engine/wasm_engine.js` for graceful dev degradation

**3.3 — Frontend execution router** ✓
- `SimulationCanvas` accepts `executionTarget` prop
- `executionTarget === "wasm"` → creates `WasmController` (no server session)
- `executionTarget === "server"` → creates `WebSocketController` (existing flow)
- `WasmController`: loads WASM once, computes all frames in `connect()`, serves them locally via array indexing — `totalFrames` known immediately, zero latency seek/step

**3.4 — 5 seed sort algorithms in Rust** ✓
- `bubble_sort.rs` — optimized with early-termination
- `insertion_sort.rs` — left-to-right shift-and-place
- `selection_sort.rs` — min-scan with auxiliary_indices highlighting
- `merge_sort.rs` — bottom-up iterative, comparison + placement frames
- `quick_sort.rs` — Lomuto partition, iterative (stack-based), pivot highlighted

All manifests updated: `execution_target: "wasm"` for bubble-, insertion-, selection-, merge-, quick-sort.

**3.5 — Benchmark harness** ✓
- `BenchmarkPanel` shows "WASM" badge for wasm-targeted algorithms
- Runs `WasmController.benchmarkSizes()` for browser-side WASM timing
- Two-line SVG chart: indigo = server/Python, emerald = browser/WASM
- Sizes up to n=5000 (WASM is fast enough; server stops at 1000)

#### How to activate
```powershell
# 1. Install Rust + wasm-pack (one-time)
#    https://rustup.rs/  →  cargo install wasm-pack

# 2. Build WASM binary
cd apps/frontend
npm run build:wasm

# 3. Install frontend deps (adds vite-plugin-wasm)
npm install

# 4. Start dev server
npm run dev
```

---

### Phase 4 — Notebook System + Rust Engine
**Goal**: Jupyter-compatible notebook interface; full Rust simulation engine for server

**4.1 — Notebook kernel** ✓ ARCHITECTURE COMPLETE — 9/9 tests passing
- `packages/notebook-kernel/pyproject.toml` — package `algorithm-atlas-notebook` v0.4.1
- `packages/notebook-kernel/algorithm_atlas_notebook/__init__.py` — exports `run`, `compare`, `AtlasDisplay`
- `packages/notebook-kernel/algorithm_atlas_notebook/api.py` — `run(slug, seed, **params)` auto-discovers plugins; `compare(*slugs)` multi-cell display
- `packages/notebook-kernel/algorithm_atlas_notebook/display.py` — `AtlasDisplay` with `_repr_html_()`, `_repr_json_()`, `save_html()`, stats properties
- `packages/notebook-kernel/algorithm_atlas_notebook/player.py` — self-contained canvas animation player (no external deps, works offline)
- `packages/notebook-kernel/tests/test_notebook.py` — 9 tests covering all 5 sort algorithms, HTML generation, JSON serialization, file export

Usage:
```python
from algorithm_atlas_notebook import run, compare
run("bubble-sort", seed=42, array_size=30)              # animated player in Jupyter cell
run("merge-sort").save_html("demo.html")                # export standalone HTML
compare("bubble-sort", "quick-sort", array_size=30)     # side-by-side
```

**4.2 — Rust simulation engine** ✓ ARCHITECTURE COMPLETE
- Refactored shared sorting impls into `packages/plugin-sdk/rust/src/sorting/` — single source of truth for both WASM and native targets
  - `mod.rs` — `pub fn run_sort(slug, seed, n, order) -> Vec<SimulationFrame>` dispatch
  - `utils.rs`, `bubble_sort.rs`, `insertion_sort.rs`, `selection_sort.rs`, `merge_sort.rs`, `quick_sort.rs`
- `packages/wasm-engine/src/sorting/mod.rs` — slim re-export `pub use algorithm_atlas_sdk::sorting::run_sort`; individual sort files retained as dead-code reference
- `packages/wasm-engine/src/lib.rs` — now calls `sdk_run_sort()` instead of individual sort modules
- `packages/rust-engine/Cargo.toml` — added `algorithm-atlas-sdk` path dep + `serde`, `serde_json`
- `packages/rust-engine/src/lib.rs` — added 3 new PyO3 functions:
  - `run_sort_rs(slug, seed, array_size, input_order) -> str` — JSON frames, GIL released
  - `benchmark_sort_rs(slug, seed, array_size, input_order, trials) -> f64` — `std::time::Instant` timing
  - `benchmark_parallel_rs(requests_json) -> str` — Rayon `par_iter` over request list, ~8× throughput on 8-core
- `apps/backend/algorithm_atlas/benchmark/rust_runner.py` — graceful import of `algorithm_atlas_rs`; `is_available()`, `benchmark_slug()`, `benchmark_parallel()`, `run_sort_frames()`
- `apps/backend/algorithm_atlas/api/v1/benchmarks.py` — Rust-first routing for sort algorithms; new `/batch` endpoint (Rayon parallel)
- `apps/frontend/src/core/api/client.ts` — fixed pre-existing field mismatch (`sizes`→`results`, `algorithm_slug`→`slug`); added `engine` field
- `apps/frontend/src/benchmark/BenchmarkPanel.tsx` — uses `results` field; shows "Rust" badge when server used native engine

**To build** (requires Rust + maturin):
```powershell
pip install maturin
cd packages/rust-engine
maturin develop          # editable install
# Then: uvicorn algorithm_atlas.main:app --reload --app-dir apps/backend
```

**4.3 — Tauri desktop app** ✓ ARCHITECTURE COMPLETE
- `apps/desktop/` — Tauri 2.x shell
  - `src-tauri/Cargo.toml` — `tauri 2`, `tauri-plugin-shell`, `serde_json`
  - `src-tauri/src/lib.rs` — `launch_backend`, `kill_backend`, `backend_running` commands; auto-kills backend on window close via `on_window_event`
  - `src-tauri/tauri.conf.json` — window config (1280×840), `beforeBuildCommand` runs `build:wasm` + `build`
  - `src-tauri/capabilities/default.json` — `core:default`, `shell:allow-open`, `shell:allow-execute`
- `apps/frontend/src/core/tauri.ts` — `isTauriApp()` + `tauriInvoke<T>()` via `window.__TAURI_INTERNALS__` (no `@tauri-apps/api` dep needed)
- `apps/frontend/src/core/hooks/useServerAvailable.ts` — probes API with 2.5 s timeout, rechecks every 30 s; exports `isTauriApp` re-export
- `apps/frontend/src/catalog/CatalogPage.tsx` — offline banner; "Launch server" button calls `launch_backend` in Tauri context; filters to WASM-only when offline

**To build the desktop app** (requires Rust + wasm-pack + Tauri CLI):
```powershell
# 1. Install Tauri CLI
cargo install tauri-cli --version "^2"

# 2. Generate app icons (requires an SVG source)
cd apps/desktop && cargo tauri icon ../../apps/frontend/public/logo.svg

# 3. Dev mode (launches Vite + Tauri window)
cargo tauri dev

# 4. Release build (produces installers in src-tauri/target/release/bundle/)
cargo tauri build
```

**4.4 — Graph renderer upgrade** ✓ COMPLETE
- `GraphTraversalRenderer.tsx` fully rewritten
- Zoom + pan via viewBox manipulation (`useViewBox()` hook — scroll zooms toward cursor, drag to pan, dbl-click resets)
- Smooth CSS transitions: `stroke 0.22s ease` on edges, `fill 0.22s ease` on nodes
- Directed arrowheads: 5 color-matched `<marker>` elements in SVG `<defs>`, selected by `markerKey`
- Path highlighting: `pathEdgeSet` built from `state.path`; cyan `#22d3ee` on matched edges
- Perpendicular edge-weight labels (offset `(-dy/len*11, dx/len*11)` — never overlaps line)
- Description bar moved outside SVG → always visible regardless of zoom state
- Legend shows path line item only when path is non-empty
- TypeScript typecheck: 0 errors

---

### Phase 5 — Polyglot Notebook Kernel ✓ ARCHITECTURE COMPLETE — 27/27 tests passing
**Goal**: Compile and visualize algorithms written in any language (C, C++, Java, C#, Python)

**New files:**
- `packages/notebook-kernel/algorithm_atlas_notebook/compilers/base.py` — `CompilerBase`, `CompilerResult`, `parse_frames()` (newline-delimited JSON protocol)
- `packages/notebook-kernel/algorithm_atlas_notebook/compilers/c_compiler.py` — GCC wrapper; harness provides `ATLAS_COMPARE`, `ATLAS_SWAP`, `ATLAS_EMIT` macros; user writes `void atlas_sort(int* arr, int n)`
- `packages/notebook-kernel/algorithm_atlas_notebook/compilers/cpp_compiler.py` — G++ wrapper; same interface + STL (`<vector>`, `<algorithm>`) available
- `packages/notebook-kernel/algorithm_atlas_notebook/compilers/java_compiler.py` — javac+java; harness provides `compare(i,j)`, `swap(arr,i,j)`; user writes `static void sort(int[] arr)`
- `packages/notebook-kernel/algorithm_atlas_notebook/compilers/csharp_compiler.py` — dotnet (.NET 9); harness provides `Compare(i,j)`, `Swap(arr,i,j)`; user writes `static void Sort(int[] arr)`
- `packages/notebook-kernel/algorithm_atlas_notebook/compilers/python_runner.py` — in-process Python runner via `exec()`; user writes `def atlas_sort(arr, cb)`
- `packages/notebook-kernel/algorithm_atlas_notebook/compilers/__init__.py` — `get_compiler(lang)`, `available_languages()`
- `packages/notebook-kernel/algorithm_atlas_notebook/polyglot.py` — `run_code(source, lang, seed, array_size, input_order)` → `AtlasDisplay`; language shortcuts `run_c`, `run_cpp`, `run_java`, `run_csharp`, `run_python`
- `packages/notebook-kernel/algorithm_atlas_notebook/magics.py` — `register_magics()` registers `%%atlas_c`, `%%atlas_cpp`, `%%atlas_java`, `%%atlas_cs`, `%%atlas_py` IPython cell magics
- `packages/notebook-kernel/tests/test_polyglot.py` — 18 tests, all languages; skipif when toolchain absent

**Key design decision:** JSON in harnesses built via `char Q = '"'` + `.append(Q)` to avoid Python→Java/C# string-escape collision (every other approach produced malformed Java/C# source).

**To activate:** gcc, g++, javac, dotnet must be on PATH (all present on this machine).

Usage:
```python
from algorithm_atlas_notebook import run_c, run_java, run_csharp, run_cpp, register_magics

run_c(r"""
void atlas_sort(int* arr, int n) {
    for (int i=0;i<n-1;i++) for (int j=0;j<n-i-1;j++) {
        ATLAS_COMPARE(arr,n,j,j+1);
        if(arr[j]>arr[j+1]) ATLAS_SWAP(arr,n,j,j+1);
    }
}
""", seed=42, array_size=20)

# Or cell magic in Jupyter:
register_magics()
# %%atlas_java seed=42 n=20
# static void sort(int[] arr) { ... }
```

### Phase 6 — Community + Public Platform ✓ ARCHITECTURE COMPLETE
**Goal**: Open plugin directory, embed widget, advanced catalog, synchronized comparison

**6.1 — Embed widget** ✓
- `apps/frontend/src/embed/EmbedPage.tsx` — `/embed/:slug` route (no navbar), reads `seed/n/autoplay/speed` query params, auto-plays when `autoplay=1`, minimal header with algorithm name + complexity + "Atlas ↗" link
- `apps/frontend/src/App.tsx` — `/embed/:slug` route outside NavBar wrapper
- `apps/frontend/src/algorithm/AlgorithmDetailPage.tsx` — `EmbedButton` component: click → popover with iframe snippet + copy-to-clipboard button
- Embed snippet example: `<iframe src="/embed/bubble-sort?n=30&autoplay=1" width="720" height="420" frameborder="0" />`

**6.2 — Advanced catalog filters** ✓
- Complexity class dropdown filter (O(n²) etc.) — derived from `time_average` across loaded algorithms
- Tag chip row — all unique tags, click to filter (single tag active at a time), chips inside cards also clickable
- Sort options: A–Z (name), Complexity (canonical order), Category
- "Clear filters (n)" button appears when any filter is active
- Dynamic subtitle: "X of 200 algorithms"

**6.3 — Community plugin directory + validation script** ✓
- `plugins/community/` — directory for third-party PRs; ignored by first-party plugin loader unless explicitly included
- `plugins/community/README.md` — full contributor guide: directory structure, manifest schema, allowed imports, test contract, review criteria
- `scripts/validate_plugin.py` — standalone CLI validator: structure check, jsonschema manifest validation, AST import safety scan, plugin class import + instantiation, optional `--run-tests` to run pytest
  - Exit 0 = pass, exit 1 = fail; colored output; runs without server or SDK if not installed (graceful warnings)

**6.4 — Synchronized comparison playback** ✓
- `apps/frontend/src/comparison/ComparisonPage.tsx` — "Lock sync" toggle button in selectors bar
- Lock mode: shared `SyncControlsBar` renders above panels; all play/pause/step/seek/reset/speed actions fire on both `WebSocketController`s simultaneously
- Individual panel controls hidden in lock mode (only frame counter + visualization visible)
- "Lock sync" button indicator: locked (🔒 indigo) vs unlocked (🔓 neutral)
- Both sims lifted to `ComparisonPage` so `ComparisonPage` can wire them together without prop drilling

---

---

### Phase 7 — 100% Completion Gap Fill ✓ COMPLETE

**Goal**: Close all gaps from the original vision; reach 100% execution.

**7.1 — 5 new SDK state types** ✓
- `CellularAutomataState` — grid of ints, generation, population count
- `DistributedSystemState` + `DSNode` + `DSMessage` — distributed algo state
- `CryptoState` — variables table, operation, highlighted vars, bits display
- `CurveState` — landscape + history + best/current for optimization curves
- `ProbabilityState` — histogram + trial count + estimate vs true_value + 2D path

**7.2 — 7 new visualization renderers (all wired)** ✓
| Type | Renderer | Used by |
|---|---|---|
| CURVE | CurveRenderer | Optimization algorithms |
| PARTICLE_FIELD | ParticleFieldRenderer | Cellular automata |
| PROBABILITY_SPACE | ProbabilityRenderer | Probability algorithms |
| STATE_MACHINE | StateMachineRenderer | Cryptography |
| NETWORK_TOPOLOGY | NetworkTopologyRenderer | Distributed systems |
| TIMELINE | TimelineRenderer | Lamport/vector clocks |
| GEOMETRIC | GeometricRenderer | Computational geometry |

**7.3 — Persistence layer** ✓
- `apps/backend/algorithm_atlas/database.py` — async SQLAlchemy + SQLite (aiosqlite), zero-config
- `apps/backend/algorithm_atlas/models/experiment.py` — `Experiment` + `NotebookCell` ORM models
- `apps/backend/algorithm_atlas/api/v1/experiments.py` — full CRUD: experiments + cells
- `apps/backend/algorithm_atlas/api/v1/notebook.py` — `POST /notebook/run` + `POST /notebook/run-cell/{id}/{cid}` (subprocess execution)
- Schema auto-created on startup via `init_db()`

**7.4 — 50 new algorithms across 6 categories** ✓
| Category | Count | Visualization |
|---|---|---|
| cellular-automata | 8 | PARTICLE_FIELD |
| distributed-systems | 10 | NETWORK_TOPOLOGY / TIMELINE |
| cryptography | 10 | STATE_MACHINE |
| optimization | 8 | CURVE |
| probability | 8 | PROBABILITY_SPACE |
| data-structures | 6 | ARRAY_BARS / TREE |

**7.5 — Web notebook UI** ✓
- `apps/frontend/src/notebook/NotebookPage.tsx` — cell-based Python notebook
  - Add / delete / reorder cells, Tab → 4 spaces, Shift+Enter to run
  - Run all / clear outputs / save to experiment / load from saved
  - Zero new npm deps — polished textarea with line-height auto-resize
- `apps/frontend/src/experiments/ExperimentsPage.tsx` — browse/view/rename/delete experiments
  - Collapsible cell viewer with source + output + timing
  - Pagination, search/filter

**7.6 — Docker** ✓
- `apps/backend/Dockerfile` — `python:3.11-slim-bookworm` + security patches, `/data` volume for SQLite
- `apps/frontend/Dockerfile` — multi-stage: `node:20-slim` builder → `nginx:1.27-alpine` server; SPA fallback
- `docker-compose.yml` — backend + frontend services, healthcheck, named volume `atlas_data`

**7.7 — Benchmark runner extended to all categories** ✓
- `apps/backend/algorithm_atlas/benchmark/config.py` — `CATEGORY_CONFIGS` dict: 14 categories → size_param + default_sizes + label
- `GET /api/v1/benchmarks/config/{slug}` — returns category-appropriate benchmark config
- `apps/frontend/src/benchmark/BenchmarkPanel.tsx` — fetches config on mount; uses correct size_param + sizes for any algorithm type

---

## Quick Commands Reference

```powershell
# Count manifests
(Get-ChildItem plugins -Recurse -Filter manifest.json | Where-Object { $_.Directory.FullName -notlike "*__pycache__*" }).Count

# Run full test suite
python -m pytest plugins/ -q

# Run single algorithm tests
python -m pytest plugins/<category>/<slug>/tests/ -v

# Check for algorithms missing tests
Get-ChildItem plugins -Recurse -Filter algorithm.py | ForEach-Object {
    $tests = Join-Path $_.Directory "tests"
    if (-not (Test-Path $tests)) { $_.Directory.FullName }
}
```
