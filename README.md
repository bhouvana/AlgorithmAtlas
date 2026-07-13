<div align="center">

# ⬡ Algorithm Atlas

**An interactive algorithmic encyclopedia — visualize, compare, learn, and run 250+ algorithms in real time**

[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=white)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=flat-square&logo=groq&logoColor=white)](https://groq.com)

**[🌐 Live Demo →](https://algorithm-atlas.onrender.com)**

</div>

---

## What is Algorithm Atlas?

Algorithm Atlas is a full-stack, real-time algorithm visualization platform built for students, engineers, and the algorithmically curious. Every algorithm is a live, interactive experience — not a static diagram.

- **Learn through 73 guided lessons** across 12 curriculum tracks — from Big O fundamentals to cache locality and real-world applications, each with interactive visualizations, code examples, complexity analysis, and 6-question quizzes
- **Step through 250+ algorithms** frame by frame via WebSocket-driven animations
- **Compare two algorithms side by side** with synchronized playback controls
- **Execute code in 17 languages** from a Monaco-powered in-browser IDE (Polyglot Notebook)
- **Save and revisit experiments** with persistent notebook cells backed by SQLite
- **Browse a structured catalog** of 250+ algorithms across 20 categories with full complexity analysis, references, and source code

---

## Feature Highlights

### Real-Time Algorithm Visualizations
Every algorithm streams execution frames over a WebSocket connection. The frontend renders each frame through a purpose-built renderer — bar charts for sorting, graph traversals with highlighted edges, DP tables filling cell by cell, probability distributions, particle fields, and more.

Playback controls: **Play / Pause / Step Forward / Step Backward / Seek / Speed ×0.5–×4 / Reset**

### Side-by-Side Comparison
The Compare page runs two independent algorithm sessions simultaneously. Lock sync mode drives both simulations from a single control bar — play, seek, and step in perfect unison.

### Polyglot Notebook (17 Languages)
A full Programiz-style split-pane IDE with Monaco Editor on the left and output on the right. Supports:

| Language | Language | Language |
|----------|----------|----------|
| Python | JavaScript | TypeScript |
| C++ | C | Java |
| Go | Rust | Shell |
| Ruby | Kotlin | Swift |
| R | C# | PHP |
| Scala | Perl | |

Each language runs in an isolated subprocess with a 10-second timeout. Compiled languages (C++, Java, Rust, Kotlin) go through a compile → run pipeline. TypeScript runs via `npx tsx` with zero-install.

### AtlasCode — Practice by Building
A LeetCode-style judge workspace: a resizable problem statement pane, a Monaco editor, and a bottom console with **Testcase**, **Test Result**, and **Console** tabs. All 216 problems are complete and solvable today — each ships a canonical implementation, a working judge, and at least one verified reference solution. Language support is tracked as a separate, ongoing metric (currently 48.81% of the 17-language × 2-mode matrix; see `docs/atlascode-complete-matrix.md`) rather than a completion gate — a problem is never "incomplete" just because a given language isn't verified for it yet. The **Problem Catalog** surfaces both metrics per row: a completion dot (Complete / In Progress) plus **LeetCode X/17** and **Codeforces X/17** language-coverage pills, so you can see at a glance which languages are verified for a given problem without it ever reading as unfinished.

Every problem supports two ways of solving it, named after the platforms they resemble:
- **LeetCode Mode** — write only the requested function; AtlasCode generates the driver, invokes it with typed arguments, and compares the typed return value.
- **Codeforces Mode** — write a complete program that reads from stdin and writes to stdout, exactly like a competitive-programming judge.

(Internally these are still the `function`/`program` execution modes in the API and database — the LeetCode/Codeforces names are a display-only convention introduced to make the distinction legible to newcomers.)

**Run** executes the problem's visible test cases (or a selected subset, or your own custom scratch cases) against the real judge and shows per-case results immediately — pass/fail, actual vs. expected output, runtime, and measured peak memory. It never persists anything.

The judge itself supports a full authoritative **Submit** path — all hidden test cases, persisted submission history, hidden-test redaction, and a runtime/memory quality analysis (`/api/v1/submissions`, see API Reference) — but it isn't wired into this workspace's UI yet, since a submission history has no real audience without a broader multi-user base. It's a backend-complete, frontend-deferred feature.

Atlas AI is available in this workspace too (see below) and defaults to hints and pointers rather than full solutions unless you explicitly ask for one.

### Structured Learning Paths (New)
73 guided lessons across 12 tracks — Foundations, Sorting, Searching, Trees, Graphs, Dynamic Programming, Greedy, Backtracking, Advanced Topics, Algorithms in the Wild, Algorithmic Thinking, and Practical Patterns. Every lesson follows a consistent 6-tab layout:

| Tab | Content |
|-----|---------|
| Concept | Overview + key-point cards |
| Visualization | Live `SimulationCanvas` using the catalog plugin for the algorithm — full playback controls |
| Video | A curated YouTube lesson for the topic, played in an embedded player — every one of the 73 lessons has a real, individually-picked video (not autogenerated), sourced from channels like HackerRank, CS Dojo, NeetCode, Computerphile, and TED-Ed |
| Examples | Annotated code examples with complexity badges |
| Complexity | Big O table + real-world applications + common mistakes |
| Quiz | 6 interactive questions with instant feedback and explanations |

Progress is tracked locally with XP, level-ups, bookmarks, and per-lesson completion state.

Three new tracks connect algorithms to daily life: **Algorithms in the Wild** (how Google, GPS, Netflix, ZIP, passwords, and autocomplete work), **Algorithmic Thinking** (recursion, divide & conquer, two pointers, sliding window, greedy, prefix sums), and **Practical Patterns** (bit manipulation, monotonic stack, intervals, amortized analysis, cache locality).

### Atlas AI — Your Algorithmic Co-pilot
A full conversational AI assistant that lives inside the workspace, backed by a rotating pool of LLM providers (**Groq · Llama 3.3 70B**, plus **Ollama Cloud · gpt-oss:120b** across two keys) — requests round-robin across whichever keys are configured and fall forward to the next one on a rate limit or outage, instead of hard-failing on a single key. Atlas understands your current context (which page you're on, the code in the notebook or AtlasCode editor, your learning progress) and acts on it:

| Capability | Example |
|------------|---------|
| **Navigate** | "Open Dijkstra" → takes you directly to the algorithm page |
| **Write code** | "Write N-Queens in Perl in the notebook" → switches language, writes code, navigates to Notebook |
| **Explain** | "Explain how Quicksort's partition step works" |
| **Debug** | "Why is my recursion hitting a stack overflow?" |
| **Teach** | "Walk me through this algorithm like I'm new to graphs" |
| **Interview** | "Give me a mock FAANG interview problem on trees" |
| **Search** | "What sorting algorithm is best for nearly-sorted data?" |
| **Coach (AtlasCode)** | "Why is my code failing this case?" → defaults to a hint or a pointer at the bug; gives the full solution only if you explicitly ask for it |

Atlas streams responses token by token (SSE) and embeds structured action events in the stream — navigation, editor writes, terminal commands — executed silently on the client without breaking the conversation flow.

### Structured Algorithm Catalog
- 250+ algorithms across 20 categories
- Filterable by category, time complexity, and tags
- Paginated (24 per page) for smooth performance
- Every algorithm card shows: name, category accent, description, complexity badge, and tags
- Full detail page: complexity table (best/avg/worst/space), intuition, tags, references, source code, and live visualization

### Experiments & Persistence
Save algorithm runs as named experiments. Each experiment stores its parameters, seed, and a set of notebook cells (code + output). Cells can be re-executed at any time. SQLite-backed, zero-config.

---

## Architecture

```
algorithm-atlas/
├── apps/
│   ├── frontend/          # React 18 + TypeScript + Vite
│   └── backend/           # FastAPI + Python 3.11
├── plugins/               # 220 algorithm plugins (manifest.json + algorithm.py)
├── sdk/                   # algorithm-atlas-sdk (shared Python package)
├── docker-compose.yml
└── README.md
```

### Frontend Stack
| Tool | Purpose |
|------|---------|
| React 18 + TypeScript | UI framework |
| Vite 5 | Build tool & dev server |
| Tailwind CSS 3 | Utility-first styling |
| Framer Motion | Animations & transitions |
| Monaco Editor | VS Code-quality code editor |
| React Router v6 | Client-side routing |
| WebSocketController | Custom simulation streaming client |

### Backend Stack
| Tool | Purpose |
|------|---------|
| FastAPI 0.111 | REST + WebSocket API |
| Python 3.11 | Runtime |
| SQLAlchemy 2 + aiosqlite | Async ORM + SQLite |
| Alembic | Database migrations |
| NumPy / SciPy / NetworkX / SymPy | Algorithm computation |
| Uvicorn | ASGI server |
| Groq SDK + LLaMA 3.3 70B | Atlas AI language model |

---

## Algorithm Categories

| Category | Count | Category | Count |
|----------|-------|----------|-------|
| Dynamic Programming | 36 | Sorting | 21 |
| Graph | 28 | String | 14 |
| Number Theory | 19 | Searching | 12 |
| Tree | 19 | Cryptography | 10 |
| Divide & Conquer | 9 | Distributed Systems | 10 |
| Backtracking | 9 | Machine Learning | 10 |
| Greedy | 9 | Cellular Automata | 8 |
| Optimization | 8 | Computational Geometry | 8 |
| Probability | 8 | Randomized | 6 |
| Data Structures | 6 | — | — |

---

## Visualization Renderers

Each algorithm declares a `visualization_type` in its manifest. The frontend picks the correct renderer automatically:

| Type | Used By |
|------|---------|
| `ARRAY_BARS` | Sorting, searching algorithms |
| `ARRAY_SEARCH` | Binary search, linear search |
| `GRAPH` | BFS, DFS, Dijkstra, A*, Bellman-Ford |
| `TREE` | BST, AVL, segment trees, heaps |
| `DP_TABLE` | Knapsack, LCS, edit distance |
| `GRID` | Maze generation, pathfinding, cellular automata |
| `CURVE` | Mathematical curves, number theory |
| `PARTICLE_FIELD` | Simulated annealing, particle swarm |
| `PROBABILITY_SPACE` | Random walks, Monte Carlo |
| `STATE_MACHINE` | Aho-Corasick, KMP, regex engines |
| `NETWORK_TOPOLOGY` | Distributed systems, consensus |
| `GEOMETRIC` | Convex hull, Voronoi, line sweep |
| `TIMELINE` | Interval scheduling, event-driven |

---

## API Reference

**Base URL**: `https://your-backend.onrender.com/api/v1`

### Algorithms
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/algorithms` | List all algorithms (filter: category, search, execution_target) |
| `GET` | `/algorithms/categories` | Category tree with counts |
| `GET` | `/algorithms/{slug}` | Full algorithm detail |
| `GET` | `/algorithms/{slug}/source` | Algorithm source code |

### Simulations
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/simulations` | Create simulation session → `session_id` |
| `GET` | `/simulations/{id}` | Session status |
| `DELETE` | `/simulations/{id}` | Destroy session |
| `WS` | `/ws/v1/simulations/{id}` | Real-time frame stream |

WebSocket messages: `play`, `pause`, `step_forward`, `step_backward`, `seek`, `reset`, `set_speed`, `ping`

### Notebook
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/notebook/run` | Execute code snippet (17 languages) |
| `POST` | `/notebook/run-cell/{exp_id}/{cell_id}` | Execute saved cell |

### AtlasCode
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/problems` | List problems (filter: category, difficulty, search; paginated — total count in `X-Total-Count` header). Each item includes `is_complete` plus `leetcode_languages`/`codeforces_languages` (verified-language arrays), computed live from the `atlascode_matrix_ledger` table — see `docs/atlascode-complete-matrix.md` |
| `GET` | `/problems/{slug}` | Problem detail + visible test cases + the same completion/coverage fields as above |
| `GET` | `/problems/{slug}/hints` | Progressive hints (`?max_level=`) |
| `POST` | `/problems/{slug}/run` | Fast iteration — visible/selected/custom cases only, never persisted, never touches hidden tests. `execution_mode: "function" \| "program"` selects LeetCode Mode / Codeforces Mode (see AtlasCode feature section above) |
| `POST` | `/submissions` | Authoritative judge run against all persisted test cases (visible + hidden), redacts hidden case content, updates progress. Backend-complete; not called by the current workspace UI (see AtlasCode feature section above) |
| `GET` | `/submissions/{id}` | Fetch a persisted submission (full per-case results) |
| `GET` | `/submissions/{id}/quality` | Real correctness/runtime/memory stats; runtime percentile only when ≥5 comparable accepted submissions exist |
| `GET` | `/progress/{user_id}` | Solved/attempted problems, XP, streak |

### Atlas AI
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/ai/chat` | Streaming SSE chat — request body `{message, context, history}` |
| `POST` | `/ai/complete` | Synchronous inline code completion for the notebook editor |
| `GET` | `/ai/memory` | Read user memory entries (`?user_id=…`) |
| `POST` | `/ai/memory` | Write / update a memory key |
| `DELETE` | `/ai/memory` | Delete a memory key |

### Experiments
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/experiments` | Create experiment |
| `GET` | `/experiments` | List experiments (paginated) |
| `GET` | `/experiments/{id}` | Experiment detail + cells |
| `PATCH` | `/experiments/{id}` | Update name/notes |
| `DELETE` | `/experiments/{id}` | Delete experiment |
| `POST` | `/experiments/{id}/cells` | Add notebook cell |
| `PATCH` | `/experiments/{id}/cells/{cell_id}` | Update cell |
| `DELETE` | `/experiments/{id}/cells/{cell_id}` | Delete cell |

---

## Plugin System

Every algorithm is a self-contained plugin: a folder with a `manifest.json` and an `algorithm.py` that implements the `AlgorithmPlugin` protocol from the SDK.

```
plugins/
└── sorting/
    └── bubble-sort/
        ├── manifest.json    # metadata, complexity, params, visualization_type
        └── algorithm.py     # yields SimulationFrame objects
```

**Manifest fields**: `id`, `name`, `version`, `category`, `visualization_type`, `execution_target`, `complexity` (best/avg/worst/space), `tags`, `references`, `parameters` (JSON Schema), `intuition`, `description`

**Security**: Plugins are statically validated via AST before import. Only approved imports are allowed (`algorithm_atlas_sdk`, standard library, numpy/scipy/networkx/sympy). Backend internals are explicitly forbidden.

---

## Local Development

### Prerequisites
- Node.js 20+
- Python 3.11+
- Git

### 1. Clone
```bash
git clone https://github.com/bhouvana/AlgorithmAtlas.git
cd AlgorithmAtlas
```

### 2. Backend
```bash
cd apps/backend

# Install SDK first
pip install -e ../../sdk

# Install backend
pip install -e ".[dev]"

# Run
uvicorn algorithm_atlas.main:app --reload --port 8000
```

Backend available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### 3. Frontend
```bash
cd apps/frontend

npm install
npm run dev
```

Frontend available at `http://localhost:5173`

### 4. Docker (full stack)
```bash
# From project root
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

---

## Environment Variables

### Backend
| Variable | Default | Description |
|----------|---------|-------------|
| `PLUGIN_ROOT` | `../../plugins` | Path to algorithm plugins directory |
| `SQLITE_URL` | `sqlite+aiosqlite:///./atlas.db` | Database connection string |
| `HOST` | `0.0.0.0` | Server bind host |
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `DEBUG` | Logging level |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |
| `GROQ_API_KEY` | *(optional\*)* | Groq API key for Atlas AI — get one free at [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model ID used by Atlas AI |
| `OLLAMA_API_KEY_1` | *(optional\*)* | Ollama Cloud API key — get one at [ollama.com/settings/keys](https://ollama.com/settings/keys) |
| `OLLAMA_API_KEY_2` | *(optional\*)* | A second Ollama Cloud key, rotated alongside the first to spread load across keys |
| `OLLAMA_MODEL` | `gpt-oss:120b` | Ollama Cloud model ID used by Atlas AI |
| `OLLAMA_BASE_URL` | `https://ollama.com/v1` | Ollama Cloud's OpenAI-compatible endpoint |

\* Atlas AI needs at least one of `GROQ_API_KEY` / `OLLAMA_API_KEY_1` / `OLLAMA_API_KEY_2` set. Configuring more than one lets Atlas AI round-robin across providers/keys and fall forward on a rate limit instead of failing outright.

### Frontend
| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## Project Structure

```
algorithm-atlas/
├── apps/
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── algorithm/          # Algorithm detail page
│   │   │   ├── catalog/            # Browsable algorithm catalog (paginated)
│   │   │   ├── comparison/         # Side-by-side compare page
│   │   │   ├── notebook/           # Polyglot IDE (17 languages)
│   │   │   ├── experiments/        # Saved experiment runs
│   │   │   ├── landing/            # Home page
│   │   │   ├── learning/           # 73-lesson curriculum (12 tracks, 6-tab GenericLesson incl. Video)
│   │   │   ├── simulation/         # WebSocket simulation controller
│   │   │   ├── visualization/      # 13 algorithm renderers
│   │   │   ├── components/
│   │   │   │   ├── layout/         # NavBar
│   │   │   │   └── ui/             # GridBackground, AnimateIn, SpotlightCard
│   │   │   ├── core/api/           # Typed API client
│   │   │   └── App.tsx             # Router + global layout
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   └── backend/
│       ├── algorithm_atlas/
│       │   ├── main.py             # FastAPI app factory
│       │   ├── config.py           # Pydantic settings (reads GROQ_API_KEY)
│       │   ├── database.py         # Async SQLAlchemy engine
│       │   ├── api/v1/             # REST + WebSocket routers
│       │   │   └── ai.py           # SSE chat, inline completion, memory endpoints
│       │   ├── ai/                 # Atlas AI subsystem
│       │   │   ├── agents/         # GeneralAgent, NotebookAgent, SearchAgent, …
│       │   │   ├── orchestrator.py # Routes messages to the right agent
│       │   │   ├── provider.py     # Groq SDK wrapper (streaming + sync)
│       │   │   ├── memory.py       # Per-user persistent memory (SQLite)
│       │   │   └── context_builder.py
│       │   ├── models/             # SQLAlchemy ORM models
│       │   ├── plugins/            # Plugin loader + registry
│       │   ├── simulation/         # FrameBuffer + SimulationController
│       │   └── benchmark/          # Benchmark runner (Python + Rust)
│       ├── tests/
│       └── pyproject.toml
│
├── plugins/                        # 220 algorithm plugins
│   ├── sorting/                    # 21 algorithms
│   ├── graph/                      # 28 algorithms
│   ├── dynamic-programming/        # 36 algorithms
│   └── ...                         # 17 more categories
│
├── sdk/                            # algorithm-atlas-sdk (shared protocol)
├── docker-compose.yml
└── README.md
```

---

## Running Tests

```bash
cd apps/backend
pytest tests/ -v
```

---

## Contributing

Contributions are welcome, especially new algorithm plugins.

### Adding a New Algorithm

1. Create a folder under `plugins/<category>/<algorithm-slug>/`
2. Add `manifest.json` with the required fields (see Plugin System above)
3. Add `algorithm.py` implementing `AlgorithmPlugin` from `algorithm_atlas_sdk`
4. Your `step()` generator should `yield` `SimulationFrame` objects
5. Restart the backend — the plugin is auto-discovered

```python
from algorithm_atlas_sdk import AlgorithmPlugin, SimulationFrame

class MyAlgorithm(AlgorithmPlugin):
    def initialize(self, params: dict) -> SimulationFrame:
        # set up initial state, return frame 0
        ...

    def step(self) -> Generator[SimulationFrame, None, None]:
        # yield one frame per meaningful step
        yield SimulationFrame(state={...}, event_label="...")
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with React, FastAPI, Groq AI, and a love for algorithms.

**[⬡ Algorithm Atlas](https://github.com/bhouvana/AlgorithmAtlas)**

</div>
