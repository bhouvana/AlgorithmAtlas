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

**[🌐 Live Demo →](https://algorithm-atlas.onrender.com)**

</div>

---

## What is Algorithm Atlas?

Algorithm Atlas is a full-stack, real-time algorithm visualization platform built for students, engineers, and the algorithmically curious. Every algorithm is a live, interactive experience — not a static diagram.

- **Learn through 53 guided lessons** across 9 curriculum tracks — from Big O fundamentals to advanced graph algorithms, each with interactive visualizations, code examples, complexity analysis, and 6-question quizzes
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

### Structured Learning Paths (New)
53 guided lessons across 9 tracks — Foundations, Sorting, Searching, Trees, Graphs, Dynamic Programming, Greedy, Backtracking, and Advanced Topics. Every lesson follows a consistent 5-tab layout:

| Tab | Content |
|-----|---------|
| Concept | Overview + key-point cards |
| Visualization | Live `SimulationCanvas` using the catalog plugin for the algorithm — full playback controls |
| Examples | Annotated code examples with complexity badges |
| Complexity | Big O table + real-world applications + common mistakes |
| Quiz | 6 interactive questions with instant feedback and explanations |

Progress is tracked locally with XP, level-ups, bookmarks, and per-lesson completion state.

### Structured Algorithm Catalog
- 250+ algorithms across 20 categories
- Filterable by category, time complexity, and tags
- Paginated (24 per page) for smooth performance
- Every algorithm card shows: name, category accent, description, complexity badge, and tags
- Full detail page: complexity table (best/avg/worst/space), intuition, tags, references, source code, and live visualization

### Experiments & Persistence
Save algorithm runs as named experiments. Each experiment stores its parameters, seed, and a set of notebook cells (code + output). Cells can be re-executed at any time. SQLite-backed, zero-config.

### Higgsfield-Style Grid Background
All pages feature an animated grid background with a cursor-following indigo spotlight — dim rounded-square grid always visible, bright indigo tiles revealed via CSS `mask-image` radial gradient, lerped with `requestAnimationFrame` for buttery smooth trailing.

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
│   │   │   ├── learning/           # 53-lesson curriculum (9 tracks, 5-tab GenericLesson)
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
│       │   ├── config.py           # Pydantic settings
│       │   ├── database.py         # Async SQLAlchemy engine
│       │   ├── api/v1/             # REST + WebSocket routers
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

Built with React, FastAPI, and a love for algorithms.

**[⬡ Algorithm Atlas](https://github.com/bhouvana/AlgorithmAtlas)**

</div>
