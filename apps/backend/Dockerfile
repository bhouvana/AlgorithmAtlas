FROM python:3.11-slim-bookworm

WORKDIR /app

# Apply OS security patches, then install build deps
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

# Install plugin SDK first (changes less often)
COPY packages/plugin-sdk/python /sdk
RUN pip install --no-cache-dir /sdk

# Install backend
COPY apps/backend/pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

COPY apps/backend .
COPY plugins /plugins

ENV PLUGIN_ROOT=/plugins
ENV PORT=8000
ENV HOST=0.0.0.0
ENV LOG_LEVEL=INFO
ENV SQLITE_URL=sqlite+aiosqlite:////data/atlas.db

# Persist the SQLite database across container restarts
VOLUME ["/data"]

EXPOSE 8000

CMD ["uvicorn", "algorithm_atlas.main:app", "--host", "0.0.0.0", "--port", "8000"]
