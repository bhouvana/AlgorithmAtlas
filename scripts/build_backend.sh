#!/usr/bin/env bash
# Backend build script — installs all 17 language runtimes then the Python app.
set -euo pipefail

echo "==> Updating apt..."
apt-get update -q

echo "==> Installing system language runtimes..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -q \
    build-essential \
    gcc g++ \
    default-jdk \
    ruby-full \
    php-cli \
    r-base \
    mono-mcs mono-runtime \
    perl \
    golang-go \
    curl unzip

# Node.js 20 via NodeSource (Ubuntu default is too old)
echo "==> Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash - 2>/dev/null
apt-get install -y -q nodejs

# tsx — zero-install TypeScript runner
echo "==> Installing tsx..."
npm install -g tsx --quiet

# Rust via apt (simpler than rustup in a build environment)
echo "==> Installing Rust..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -q rustc cargo || true
# Fallback: rustup if apt rust is missing
if ! command -v rustc &>/dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --no-modify-path --profile minimal
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Kotlin compiler
if ! command -v kotlinc &>/dev/null; then
    echo "==> Installing Kotlin..."
    KOTLIN_VER="2.0.20"
    curl -fsSL \
        "https://github.com/JetBrains/kotlin/releases/download/v${KOTLIN_VER}/kotlin-compiler-${KOTLIN_VER}.zip" \
        -o /tmp/kotlin.zip
    unzip -q /tmp/kotlin.zip -d /opt/
    ln -sf /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc
    ln -sf /opt/kotlinc/bin/kotlin   /usr/local/bin/kotlin
    rm /tmp/kotlin.zip
fi

# Scala CLI
if ! command -v scala-cli &>/dev/null && ! command -v scala &>/dev/null; then
    echo "==> Installing Scala CLI..."
    curl -fsSL \
        "https://github.com/VirtusLab/scala-cli/releases/latest/download/scala-cli-x86_64-pc-linux.gz" \
        | gunzip -c > /usr/local/bin/scala-cli
    chmod +x /usr/local/bin/scala-cli
fi

# Swift (Ubuntu 22.04 build)
if ! command -v swift &>/dev/null; then
    echo "==> Installing Swift 5.10..."
    DEBIAN_FRONTEND=noninteractive apt-get install -y -q \
        binutils libcurl4-openssl-dev libedit2 \
        libgcc-9-dev libpython3-dev libsqlite3-dev libstdc++-9-dev \
        libxml2-dev libz3-dev pkg-config tzdata zlib1g-dev 2>/dev/null || true
    SWIFT_VER="swift-5.10-RELEASE"
    SWIFT_PLAT="ubuntu2204"
    curl -fsSL \
        "https://download.swift.org/${SWIFT_VER}/${SWIFT_PLAT}/${SWIFT_VER}-${SWIFT_PLAT}.tar.gz" \
        | tar xz -C /opt/ 2>/dev/null || echo "Swift download failed — skipping"
    SWIFT_BIN="/opt/${SWIFT_VER}-${SWIFT_PLAT}/usr/bin/swift"
    if [ -f "$SWIFT_BIN" ]; then
        ln -sf "$SWIFT_BIN" /usr/local/bin/swift
        echo "Swift installed."
    fi
fi

echo "==> Installing Python packages..."
pip install -e ./packages/plugin-sdk/python
pip install -e ./apps/backend

echo ""
echo "==> Runtime availability:"
for cmd in python3 node tsx gcc g++ java go rustc ruby php Rscript mcs perl kotlinc swift; do
    command -v "$cmd" &>/dev/null && echo "  ✓ $cmd" || echo "  ✗ $cmd (not found)"
done
command -v scala-cli &>/dev/null && echo "  ✓ scala-cli" || echo "  ✗ scala-cli (not found)"
echo "==> Done."
