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
# ffmpeg: Video processing (includes libx264 for H.264 encoding)
# libsm6, libxext6, libxrender-dev: OpenCV/MediaPipe GUI support
# libgomp1: OpenMP for NumPy optimization
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libx264-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create app directory
WORKDIR /app

# Copy workspace files
COPY uv.lock pyproject.toml README.md ./
COPY src/ ./src/

# Copy backend files
COPY backend/pyproject.toml backend/README.md ./backend/
COPY backend/src/ ./backend/src/

# Sync workspace from root (installs kinemotion)
RUN uv sync --frozen --no-dev

# Sync backend dependencies (uvicorn, fastapi, etc)
RUN cd backend && uv sync --frozen --no-dev

# Add venv to PATH for static execution
ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv"

# Expose port (Cloud Run expects $PORT environment variable, defaults to 8080)
EXPOSE 8080

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8080}/health').read()" || exit 1

# Run uvicorn directly (venv is in PATH, no wrapper needed)
# Cloud Run: use PORT env var (defaults to 8080)
# Graceful shutdown timeout of 60 seconds for video processing
CMD ["sh", "-c", "exec uvicorn kinemotion_backend.app:app --host 0.0.0.0 --port ${PORT:-8080} --workers ${WORKERS:-1} --timeout-graceful-shutdown 60"]
