# Multi-stage Dockerfile for kinemotion
# Optimized for Python 3.12, uv, OpenCV, and MediaPipe
# Note: Only linux/amd64 platform supported (MediaPipe lacks ARM64 Linux wheels)

# ============================================================================
# Stage 1: Builder - Install dependencies with uv
# ============================================================================
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Optimization: Compile Python bytecode at build time for faster startup
# Optimization: Copy mode for dependencies to work across build stages
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies FIRST (cached layer - only invalidated when dependencies change)
# Use bind mounts to avoid copying files into the image
# Use cache mount to reuse uv downloads across builds
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy source code AFTER dependencies (source changes don't invalidate dependency cache)
COPY . /app

# Install the project itself as a non-editable package (fast since dependencies are already installed)
# --no-editable ensures the package is properly installed, not as editable
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.12-slim-bookworm AS runtime

# OCI annotations for image metadata
LABEL org.opencontainers.image.title="kinemotion" \
      org.opencontainers.image.description="Video-based kinematic analysis for athletic performance. Analyzes drop-jump videos using MediaPipe pose tracking." \
      org.opencontainers.image.authors="Sebastian Otaegui <feniix@gmail.com>" \
      org.opencontainers.image.vendor="kinemotion" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.url="https://github.com/feniix/kinemotion" \
      org.opencontainers.image.source="https://github.com/feniix/kinemotion" \
      org.opencontainers.image.documentation="https://github.com/feniix/kinemotion#readme" \
      org.opencontainers.image.base.name="docker.io/library/python:3.12-slim-bookworm"

# Install system dependencies required by OpenCV and MediaPipe
# - libgl1: OpenGL library for OpenCV
# - libglib2.0-0: GLib library for MediaPipe
# - libgomp1: GNU OpenMP library for multi-threading
# - ffmpeg: Video codec support for OpenCV
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder (contains installed package)
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
# PATH: Use virtual environment binaries
# PYTHONUNBUFFERED: Force stdout/stderr to be unbuffered for real-time logging
# PYTHONDONTWRITEBYTECODE: Don't create .pyc files (saves space)
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user for security
RUN useradd -m -u 1000 kinemotion && \
    chown -R kinemotion:kinemotion /app

USER kinemotion

# Verify installation
RUN python -c "import kinemotion; print('kinemotion installed successfully')"

# Set entrypoint to kinemotion CLI
ENTRYPOINT ["kinemotion"]

# Default command: show help
CMD ["--help"]

# ============================================================================
# Usage examples:
#
# Build:
#   docker build -t kinemotion:latest .
#
# Run with help:
#   docker run --rm kinemotion:latest --help
#
# Analyze video:
#   docker run --rm -v $(pwd):/data kinemotion:latest \
#     dropjump-analyze /data/video.mp4 --drop-height 0.40 \
#     --output /data/debug.mp4 --json-output /data/metrics.json
#
# Interactive shell:
#   docker run --rm -it --entrypoint /bin/bash kinemotion:latest
# ============================================================================
