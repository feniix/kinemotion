# Google Cloud Run optimized build for Kinemotion Backend
# Uses Python 3.12 with uv for fast dependency installation
# Cloud Run containers run as root, so no need for non-root user complications

FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app/src

# Install system dependencies required for MediaPipe and OpenCV
# ffmpeg: Video processing
# libsm6, libxext6, libxrender-dev: OpenCV/MediaPipe GUI support
# libgomp1: OpenMP for NumPy optimization
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create app directory
WORKDIR /app

# Copy project files for dependency installation
COPY pyproject.toml README.md ./
# Copy uv.lock (workspace lock file, kept in sync with root uv.lock)
COPY uv.lock ./

# Install Python dependencies using uv
# Using --frozen to ensure reproducible builds from lock file
# This includes kinemotion from PyPI (specified in pyproject.toml)
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/

# Expose port (Cloud Run expects $PORT environment variable, defaults to 8080)
EXPOSE 8000

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Run the application with uvicorn
# Cloud Run: use PORT env var (defaults to 8000)
# Graceful shutdown timeout of 60 seconds for video processing
# Using exec form with sh -c for proper signal handling and env var expansion
CMD ["sh", "-c", "exec .venv/bin/uvicorn kinemotion_backend.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-1} --timeout-graceful-shutdown 60"]
