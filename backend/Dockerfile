# Multi-stage build optimized for Fly.io free tier deployment
# Uses Python 3.12 for performance and uses uv for fast dependency installation

FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install system dependencies required for MediaPipe and OpenCV
# ffmpeg: Video processing
# libsm6, libxext6, libxrender-dev: OpenCV/MediaPipe GUI support
# libgomp1: OpenMP for NumPy optimization
# wget: For health check endpoint verification
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create app directory
WORKDIR /app

# Copy pyproject.toml and uv.lock (if exists) for dependency installation
COPY pyproject.toml ./
COPY uv.lock* ./

# Install Python dependencies using uv
# Using --frozen to ensure reproducible builds from lock file
# This includes kinemotion from PyPI (specified in pyproject.toml)
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/

# Create non-root user for security (prevents container escape privilege escalation)
RUN groupadd -r kinemotion && useradd -r -g kinemotion kinemotion \
    && mkdir -p /app /tmp \
    && chown -R kinemotion:kinemotion /app /tmp

# Switch to non-root user
USER kinemotion

# Expose port for Fly.io
EXPOSE 8000

# Health check to help Fly.io detect crashes
# Uses wget (installed in base) instead of requests
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Run the application with uvicorn
# Single worker for free tier stability (recommended for <50 req/s)
# Graceful shutdown timeout of 60 seconds for video processing
# Workers parameter can be adjusted via environment variable
CMD ["uv", "run", "uvicorn", "kinemotion_backend.app:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "${WORKERS:-1}", \
     "--timeout-graceful-shutdown", "60"]
