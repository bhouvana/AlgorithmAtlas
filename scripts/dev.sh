#!/usr/bin/env bash
# Start the full development environment.
# Prerequisites: Python 3.11+, Node 20+, Docker

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Starting infrastructure (Postgres + Redis)"
docker compose -f docker/docker-compose.dev.yml up -d --wait

echo "==> Installing Plugin SDK"
pip install -e packages/plugin-sdk/python --quiet

echo "==> Installing backend"
pip install -e apps/backend --quiet

echo "==> Installing frontend"
cd apps/frontend && npm install --silent && cd "$REPO_ROOT"

echo "==> Checking for Rust engine"
if command -v cargo &>/dev/null && command -v maturin &>/dev/null; then
  echo "     Building Rust engine..."
  cd packages/rust-engine && maturin develop --quiet && cd "$REPO_ROOT"
else
  echo "     Rust/maturin not found — Rust engine disabled (Python fallbacks active)"
fi

echo "==> Starting services"
# Backend in background
uvicorn algorithm_atlas.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000 \
  --app-dir apps/backend \
  --log-level info &
BACKEND_PID=$!

# Frontend in background
(cd apps/frontend && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "  Backend:  http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:5173"
echo ""
echo "  Press Ctrl+C to stop all services"

cleanup() {
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
  docker compose -f docker/docker-compose.dev.yml stop
}
trap cleanup INT TERM

wait
