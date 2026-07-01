# ── Stage: full polyglot runtime ─────────────────────────────────────────────
# Ubuntu 22.04 so Swift's official tarballs match the platform.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.cargo/bin:/usr/local/dotnet:/usr/local/kotlinc/bin:${PATH}"

# ── 1. Base system packages ───────────────────────────────────────────────────
RUN apt-get update -q && apt-get install -y -q --no-install-recommends \
    # Python 3.11
    python3.11 python3.11-dev python3-pip \
    # C / C++ (GCC 11, c17/c++17 fully supported)
    build-essential gcc g++ \
    # Java (JDK for javac + java; also used by Kotlin & Scala)
    default-jdk \
    # Ruby
    ruby-full \
    # PHP
    php-cli \
    # R
    r-base \
    # Perl (usually pre-installed but be explicit)
    perl \
    # Go
    golang-go \
    # Mono C# compiler + runtime
    mono-mcs mono-runtime \
    # Utilities
    curl wget unzip ca-certificates xz-utils \
    && rm -rf /var/lib/apt/lists/*

# ── 2. Node.js 20 (apt default on 22.04 is 12 — too old for tsx) ─────────────
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y -q --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g tsx --quiet

# ── 3. Rust (minimal profile — rustc + cargo, no docs/clippy) ────────────────
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
    | sh -s -- -y --no-modify-path --profile minimal \
    && rustc --version

# ── 4. Kotlin 2.0.20 ─────────────────────────────────────────────────────────
RUN curl -fsSL \
    "https://github.com/JetBrains/kotlin/releases/download/v2.0.20/kotlin-compiler-2.0.20.zip" \
    -o /tmp/kotlin.zip \
    && unzip -q /tmp/kotlin.zip -d /usr/local/ \
    && ln -sf /usr/local/kotlinc/bin/kotlinc /usr/local/bin/kotlinc \
    && ln -sf /usr/local/kotlinc/bin/kotlin   /usr/local/bin/kotlin \
    && rm /tmp/kotlin.zip

# ── 5. Scala CLI ─────────────────────────────────────────────────────────────
RUN curl -fsSL \
    "https://github.com/VirtusLab/scala-cli/releases/latest/download/scala-cli-x86_64-pc-linux.gz" \
    | gunzip -c > /usr/local/bin/scala-cli \
    && chmod +x /usr/local/bin/scala-cli

# ── 6. .NET 8 (C# fallback if Mono has issues) ───────────────────────────────
RUN curl -fsSL https://dot.net/v1/dotnet-install.sh \
    | bash -s -- --channel 8.0 --install-dir /usr/local/dotnet \
    && ln -sf /usr/local/dotnet/dotnet /usr/local/bin/dotnet

# ── 7. Swift 5.10 for Ubuntu 22.04 ───────────────────────────────────────────
RUN apt-get update -q && apt-get install -y -q --no-install-recommends \
    binutils libcurl4-openssl-dev libedit2 libgcc-9-dev \
    libpython3-dev libsqlite3-dev libstdc++-9-dev \
    libxml2-dev libz3-dev pkg-config zlib1g-dev \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL \
    "https://download.swift.org/swift-5.10-release/ubuntu2204/swift-5.10-RELEASE/swift-5.10-RELEASE-ubuntu22.04.tar.gz" \
    | tar xz -C /opt/ \
    && ln -sf "/opt/swift-5.10-RELEASE-ubuntu22.04/usr/bin/swift" /usr/local/bin/swift \
    && swift --version

# ── 8. Verify all runtimes ────────────────────────────────────────────────────
RUN echo "=== Runtime check ===" \
    && python3.11 --version \
    && gcc --version | head -1 \
    && g++ --version | head -1 \
    && java -version 2>&1 | head -1 \
    && node --version \
    && tsx --version \
    && go version \
    && rustc --version \
    && ruby --version \
    && php --version | head -1 \
    && Rscript --version 2>&1 \
    && mcs --version \
    && kotlinc -version 2>&1 \
    && scala-cli --version \
    && swift --version 2>&1 | head -1 \
    && perl --version | head -2 \
    && echo "=== All runtimes OK ==="

# ── 9. Python application ─────────────────────────────────────────────────────
# Bootstrap a modern pip for Python 3.11 (system python3-pip on Ubuntu 22.04
# can't parse [project] table from pyproject.toml, so deps are silently skipped)
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 \
    && python3.11 -m pip install --upgrade --quiet pip setuptools wheel

WORKDIR /app

COPY packages/plugin-sdk/python /sdk
COPY apps/backend .
COPY plugins /plugins

# Install all backend dependencies explicitly so they land in Python 3.11's
# site-packages regardless of the pyproject.toml parsing issue above.
RUN python3.11 -m pip install --no-cache-dir \
    "fastapi>=0.111.0" \
    "uvicorn[standard]>=0.29.0" \
    "pydantic>=2.7.0" \
    "pydantic-settings>=2.3.0" \
    "loguru>=0.7.2" \
    "jsonschema>=4.22.0" \
    "numpy>=1.26.0" \
    "scipy>=1.13.0" \
    "networkx>=3.3" \
    "sympy>=1.12.0" \
    "sqlalchemy>=2.0.0" \
    "aiosqlite>=0.20.0" \
    "alembic>=1.13.0"

# Atlas AI dependency — separate layer so it doesn't invalidate the heavy install above
RUN python3.11 -m pip install --no-cache-dir "groq>=0.9.0"

# PYTHONPATH exposes algorithm_atlas (source) and algorithm_atlas_sdk (sdk source)
# without requiring pip to successfully install the local packages.
ENV PYTHONPATH=/app:/sdk \
    PLUGIN_ROOT=/plugins \
    PORT=8000 \
    LOG_LEVEL=INFO \
    SQLITE_URL=sqlite+aiosqlite:///./atlas.db

EXPOSE 8000

CMD ["python3.11", "-m", "uvicorn", "algorithm_atlas.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]
