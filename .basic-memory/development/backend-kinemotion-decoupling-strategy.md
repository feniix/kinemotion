---
title: Backend Kinemotion Decoupling Strategy
type: note
permalink: development/backend-kinemotion-decoupling-strategy
tags:
- backend
- decoupling
- adapter-pattern
- architecture
- kinemotion
- cli
- subprocess
---

# Backend-Kinemotion Decoupling Strategy

**Created**: 2025-12-02
**Purpose**: Complete guide for decoupling backend from kinemotion Python API
**Status**: Recommended approach with implementation examples

## Executive Summary

**Problem**: Backend currently imports `from kinemotion.api import process_cmj_video, process_dropjump_video` which creates:
- Dependency on kinemotion PyPI package (≥0.30.0)
- Deployment coupling (must wait for PyPI publish)
- Breaking changes in kinemotion.api break backend
- Hard to test without kinemotion installed

**Recommended Solution**: Adapter Pattern with CLI Subprocess
- Backend calls kinemotion CLI instead of importing Python package
- Complete decoupling - no PyPI dependency
- Version independence - Docker installs kinemotion CLI
- Clean architecture with testable interfaces

**Result**: Backend can update kinemotion version without code changes, repositories can split cleanly.

## Current Coupling Analysis

### Coupling Points

```python
# backend/src/kinemotion_backend/app.py line 25
from kinemotion.api import process_cmj_video, process_dropjump_video

# backend/pyproject.toml line 35
dependencies = [
    "kinemotion>=0.30.0",  # PyPI dependency
    ...
]

# Usage in app.py (simplified)
@app.post("/api/analyze")
async def analyze_video(video: UploadFile, jump_type: str):
    if jump_type == "cmj":
        metrics = process_cmj_video(video_path, quality="balanced")
    else:
        metrics = process_dropjump_video(video_path, quality="balanced")
    return metrics.to_dict()
```

### Problems with Current Approach

| Problem | Impact |
|---------|--------|
| **PyPI Dependency** | Backend must wait for kinemotion to be published |
| **Version Coupling** | Breaking API changes break backend |
| **Testing** | Hard to mock kinemotion functions |
| **Repository Split** | Can't cleanly separate repos (shared Python dependency) |
| **Deployment** | Must rebuild backend when kinemotion updates |

## Decoupling Strategies Evaluated

### Strategy 1: Adapter Pattern with CLI Subprocess ✅ RECOMMENDED

**Description**: Backend calls kinemotion CLI as subprocess, parses JSON output

**Architecture**:
```
Backend FastAPI → VideoAnalyzer (interface) → KinemotionCLIAdapter → kinemotion CLI
                                           → MockAdapter (for tests)
```

**Pros**:
- ✅ Complete decoupling - no kinemotion package needed
- ✅ Version independence - update CLI without code changes
- ✅ Testable - easy to mock
- ✅ Repository split friendly
- ✅ Type-safe via adapter interface
- ✅ Performance acceptable (~100ms subprocess overhead vs seconds for video processing)

**Cons**:
- ⚠️ Subprocess overhead (~100ms per call)
- ⚠️ JSON parsing instead of Python objects
- ⚠️ Must ensure CLI is in Docker PATH

**Verdict**: Best solution for repository split scenario

### Strategy 2: Adapter Pattern with Python API

**Description**: Create adapter layer but still use kinemotion.api

```python
class KinemotionPythonAdapter(VideoAnalyzer):
    def analyze_cmj(self, video_path: str, quality: str):
        from kinemotion.api import process_cmj_video
        return process_cmj_video(video_path, quality)
```

**Pros**:
- ✅ Keeps Python types
- ✅ No subprocess overhead
- ✅ Testable via mocking

**Cons**:
- ❌ Still depends on PyPI
- ❌ Still coupled to kinemotion versions
- ❌ Doesn't solve deployment coupling

**Verdict**: Good for code organization, doesn't solve PyPI dependency

### Strategy 3: REST Microservice

**Description**: Run kinemotion as separate HTTP service

```
Backend → HTTP call → Kinemotion Service (FastAPI) → kinemotion.api
```

**Pros**:
- ✅ Complete decoupling
- ✅ Language-agnostic
- ✅ Independently scalable

**Cons**:
- ❌ Infrastructure complexity (another service)
- ❌ Network overhead
- ❌ Large video file transfers
- ❌ More deployment complexity

**Verdict**: Overkill for current needs

### Strategy 4: Message Queue (Async)

**Description**: Backend publishes video to queue, worker processes it

**Pros**:
- ✅ Async processing
- ✅ Scalable workers
- ✅ Resilient

**Cons**:
- ❌ Most complex
- ❌ Requires message broker (RabbitMQ, Redis)
- ❌ Overkill for current scale

**Verdict**: Future consideration for scale

## Recommended Implementation: CLI Adapter

### Phase 1: Create Adapter Interface

**File**: `backend/src/kinemotion_backend/video_analyzer.py`

```python
"""Video analysis adapter interface for decoupling from kinemotion implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

JumpType = Literal["cmj", "dropjump"]
QualityPreset = Literal["fast", "balanced", "accurate"]


@dataclass
class VideoAnalysisResult:
    """Standardized result from video analysis.

    This interface is what the backend needs, independent of implementation.
    """
    # Core metrics (all jump types)
    jump_height_m: float
    flight_time_ms: float

    # CMJ-specific (None for drop jump)
    countermovement_depth_m: float | None = None
    eccentric_duration_ms: float | None = None
    concentric_duration_ms: float | None = None
    peak_eccentric_velocity_m_s: float | None = None
    peak_concentric_velocity_m_s: float | None = None

    # Drop jump-specific (None for CMJ)
    ground_contact_time_ms: float | None = None
    reactive_strength_index: float | None = None

    # Metadata
    processing_time_s: float | None = None
    quality_warnings: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        result: dict[str, Any] = {
            "jump_height_m": self.jump_height_m,
            "flight_time_ms": self.flight_time_ms,
        }

        # Add non-None optional fields
        if self.countermovement_depth_m is not None:
            result["countermovement_depth_m"] = self.countermovement_depth_m
        if self.eccentric_duration_ms is not None:
            result["eccentric_duration_ms"] = self.eccentric_duration_ms
        if self.concentric_duration_ms is not None:
            result["concentric_duration_ms"] = self.concentric_duration_ms
        if self.ground_contact_time_ms is not None:
            result["ground_contact_time_ms"] = self.ground_contact_time_ms
        if self.reactive_strength_index is not None:
            result["reactive_strength_index"] = self.reactive_strength_index

        return result


class VideoAnalyzer(ABC):
    """Abstract interface for video analysis.

    This allows swapping implementations (CLI, Python API, HTTP service, mock).
    """

    @abstractmethod
    def analyze(
        self,
        video_path: str,
        jump_type: JumpType,
        quality: QualityPreset = "balanced",
    ) -> VideoAnalysisResult:
        """Analyze a video and return metrics.

        Args:
            video_path: Path to video file
            jump_type: Type of jump ("cmj" or "dropjump")
            quality: Analysis quality preset

        Returns:
            VideoAnalysisResult with metrics

        Raises:
            ValueError: If analysis fails or invalid parameters
            FileNotFoundError: If video file doesn't exist
        """
        pass
```

### Phase 2: Implement CLI Adapter

**File**: `backend/src/kinemotion_backend/adapters/cli_adapter.py`

```python
"""Kinemotion CLI adapter - calls kinemotion via subprocess."""

import json
import subprocess
import tempfile
from pathlib import Path

from kinemotion_backend.logging_config import get_logger
from kinemotion_backend.video_analyzer import (
    JumpType,
    QualityPreset,
    VideoAnalysisResult,
    VideoAnalyzer,
)

logger = get_logger(__name__)


class KinemotionCLIAdapter(VideoAnalyzer):
    """Production adapter that calls kinemotion CLI via subprocess."""

    def __init__(self, cli_path: str = "kinemotion"):
        """Initialize CLI adapter.

        Args:
            cli_path: Path to kinemotion CLI executable (default: "kinemotion")
        """
        self.cli_path = cli_path
        self._verify_cli_available()

    def _verify_cli_available(self) -> None:
        """Verify kinemotion CLI is available."""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise RuntimeError(f"kinemotion CLI not working: {result.stderr}")
            logger.info(f"kinemotion CLI found: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError(
                f"kinemotion CLI not found at '{self.cli_path}'. "
                "Ensure it's installed and in PATH."
            )

    def analyze(
        self,
        video_path: str,
        jump_type: JumpType,
        quality: QualityPreset = "balanced",
    ) -> VideoAnalysisResult:
        """Analyze video using kinemotion CLI.

        Calls: kinemotion {jump_type}-analyze video.mp4 --quality {quality} --json output.json
        """
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        # Create temporary file for JSON output
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp:
            json_output_path = tmp.name

        try:
            # Build CLI command
            cmd = [
                self.cli_path,
                f"{jump_type}-analyze",
                str(video_path),
                "--quality",
                quality,
                "--json",
                json_output_path,
            ]

            logger.info(f"Running kinemotion CLI: {' '.join(cmd)}")

            # Execute CLI
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout for video processing
            )

            if result.returncode != 0:
                logger.error(f"CLI failed: {result.stderr}")
                raise ValueError(f"Analysis failed: {result.stderr}")

            # Parse JSON output
            with open(json_output_path, "r") as f:
                raw_result = json.load(f)

            # Map to VideoAnalysisResult
            return self._parse_cli_output(raw_result, jump_type)

        finally:
            # Clean up temp file
            Path(json_output_path).unlink(missing_ok=True)

    def _parse_cli_output(
        self, raw_result: dict, jump_type: JumpType
    ) -> VideoAnalysisResult:
        """Parse kinemotion CLI JSON output to VideoAnalysisResult."""
        data = raw_result.get("data", {})
        metadata = raw_result.get("metadata", {})

        # Extract common metrics
        jump_height = data.get("jump_height_m")
        flight_time = data.get("flight_time_ms")

        if jump_height is None or flight_time is None:
            raise ValueError("Missing required metrics in CLI output")

        # Extract quality warnings
        quality_info = metadata.get("quality", {})
        warnings = quality_info.get("warnings", [])

        # Extract processing time
        processing_info = metadata.get("processing", {})
        processing_time = processing_info.get("processing_time_s")

        if jump_type == "cmj":
            return VideoAnalysisResult(
                jump_height_m=float(jump_height),
                flight_time_ms=float(flight_time),
                countermovement_depth_m=data.get("countermovement_depth_m"),
                eccentric_duration_ms=data.get("eccentric_duration_ms"),
                concentric_duration_ms=data.get("concentric_duration_ms"),
                peak_eccentric_velocity_m_s=data.get("peak_eccentric_velocity_m_s"),
                peak_concentric_velocity_m_s=data.get("peak_concentric_velocity_m_s"),
                processing_time_s=processing_time,
                quality_warnings=warnings if warnings else None,
            )
        else:  # dropjump
            return VideoAnalysisResult(
                jump_height_m=float(jump_height),
                flight_time_ms=float(flight_time),
                ground_contact_time_ms=data.get("ground_contact_time_ms"),
                reactive_strength_index=data.get("reactive_strength_index"),
                processing_time_s=processing_time,
                quality_warnings=warnings if warnings else None,
            )
```

### Phase 3: Create Mock Adapter for Testing

**File**: `backend/src/kinemotion_backend/adapters/mock_adapter.py`

```python
"""Mock adapter for testing without kinemotion dependency."""

from kinemotion_backend.video_analyzer import (
    JumpType,
    QualityPreset,
    VideoAnalysisResult,
    VideoAnalyzer,
)


class MockVideoAnalyzer(VideoAnalyzer):
    """Mock adapter that returns fake data for testing."""

    def analyze(
        self,
        video_path: str,
        jump_type: JumpType,
        quality: QualityPreset = "balanced",
    ) -> VideoAnalysisResult:
        """Return mock analysis result."""
        if jump_type == "cmj":
            return VideoAnalysisResult(
                jump_height_m=0.506,
                flight_time_ms=640.0,
                countermovement_depth_m=0.32,
                eccentric_duration_ms=450.0,
                concentric_duration_ms=320.0,
                peak_eccentric_velocity_m_s=-1.8,
                peak_concentric_velocity_m_s=2.5,
                processing_time_s=2.5,
                quality_warnings=None,
            )
        else:  # dropjump
            return VideoAnalysisResult(
                jump_height_m=0.45,
                flight_time_ms=600.0,
                ground_contact_time_ms=180.0,
                reactive_strength_index=2.5,
                processing_time_s=2.0,
                quality_warnings=None,
            )


class ConfigurableMockAnalyzer(VideoAnalyzer):
    """Mock adapter with configurable responses for testing edge cases."""

    def __init__(self, result: VideoAnalysisResult | None = None, should_fail: bool = False):
        """Initialize with custom result or failure mode."""
        self.result = result
        self.should_fail = should_fail

    def analyze(
        self,
        video_path: str,
        jump_type: JumpType,
        quality: QualityPreset = "balanced",
    ) -> VideoAnalysisResult:
        """Return configured result or raise error."""
        if self.should_fail:
            raise ValueError("Simulated analysis failure")

        if self.result:
            return self.result

        # Default mock result
        return VideoAnalysisResult(
            jump_height_m=0.5,
            flight_time_ms=600.0,
            processing_time_s=1.0,
        )
```

### Phase 4: Update Backend Application

**File**: `backend/src/kinemotion_backend/app.py` (updated)

```python
"""FastAPI application with decoupled video analysis."""

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from kinemotion_backend.adapters.cli_adapter import KinemotionCLIAdapter
from kinemotion_backend.adapters.mock_adapter import MockVideoAnalyzer
from kinemotion_backend.logging_config import get_logger, setup_logging
from kinemotion_backend.video_analyzer import JumpType, QualityPreset, VideoAnalyzer

# Initialize logging
setup_logging(
    json_logs=os.getenv("JSON_LOGS", "false").lower() == "true",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
)

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(title="Kinemotion Backend API")

# Initialize video analyzer (production uses CLI, tests use mock)
def get_video_analyzer() -> VideoAnalyzer:
    """Factory function for video analyzer.

    Returns CLI adapter in production, mock in test mode.
    """
    if os.getenv("USE_MOCK_ANALYZER", "false").lower() == "true":
        logger.info("Using mock video analyzer")
        return MockVideoAnalyzer()
    else:
        logger.info("Using kinemotion CLI adapter")
        return KinemotionCLIAdapter()

# Global analyzer instance
video_analyzer = get_video_analyzer()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "kinemotion-backend"}


@app.post("/api/analyze")
async def analyze_video(
    video: UploadFile = File(...),
    jump_type: JumpType = Form("cmj"),
    quality: QualityPreset = Form("balanced"),
):
    """Analyze video and return metrics.

    This endpoint is now decoupled from kinemotion.api!
    """
    logger.info(f"Analyzing {jump_type} video with {quality} quality")

    # Save uploaded video to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(await video.read())
        video_path = tmp.name

    try:
        # Call analyzer (could be CLI or mock)
        result = video_analyzer.analyze(video_path, jump_type, quality)

        logger.info(f"Analysis complete: jump_height={result.jump_height_m}m")

        return {
            "status": "success",
            "metrics": result.to_dict(),
            "jump_type": jump_type,
            "quality": quality,
        }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temp file
        Path(video_path).unlink(missing_ok=True)
```

### Phase 5: Update Dockerfile

**File**: `backend/Dockerfile` (updated)

```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy backend dependencies
COPY pyproject.toml README.md ./
COPY uv.lock ./

# Install backend dependencies (NO kinemotion package!)
RUN uv sync --frozen --no-dev

# Install kinemotion CLI from PyPI
# This is separate from backend dependencies
RUN uv pip install kinemotion>=0.34.0

# Verify kinemotion CLI is available
RUN uv run kinemotion --version

# Copy application code
COPY src/ ./src/

EXPOSE 8080

CMD ["sh", "-c", "exec uv run uvicorn kinemotion_backend.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

### Phase 6: Update pyproject.toml

**File**: `backend/pyproject.toml` (updated)

```toml
[project]
name = "kinemotion-backend"
version = "0.1.0"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "python-multipart>=0.0.6",
    "boto3>=1.34.0",
    "slowapi>=0.1.9",
    "structlog>=24.1.0",
    "supabase>=2.10.0",
    "pyjwt>=2.8.0",
    "httpx>=0.27.0",
    # REMOVED: "kinemotion>=0.30.0"
    # kinemotion is now installed separately in Docker as CLI tool
]
```

### Phase 7: Add Tests

**File**: `backend/tests/test_adapters.py`

```python
"""Tests for video analyzer adapters."""

import pytest
from kinemotion_backend.adapters.mock_adapter import (
    ConfigurableMockAnalyzer,
    MockVideoAnalyzer,
)
from kinemotion_backend.video_analyzer import VideoAnalysisResult


def test_mock_analyzer_cmj():
    """Test mock analyzer returns CMJ metrics."""
    analyzer = MockVideoAnalyzer()
    result = analyzer.analyze("test.mp4", "cmj", "balanced")

    assert result.jump_height_m > 0
    assert result.flight_time_ms > 0
    assert result.countermovement_depth_m is not None
    assert result.ground_contact_time_ms is None  # CMJ doesn't have GCT


def test_mock_analyzer_dropjump():
    """Test mock analyzer returns drop jump metrics."""
    analyzer = MockVideoAnalyzer()
    result = analyzer.analyze("test.mp4", "dropjump", "balanced")

    assert result.jump_height_m > 0
    assert result.flight_time_ms > 0
    assert result.ground_contact_time_ms is not None
    assert result.countermovement_depth_m is None  # Drop jump doesn't have CM depth


def test_configurable_mock_failure():
    """Test configurable mock can simulate failures."""
    analyzer = ConfigurableMockAnalyzer(should_fail=True)

    with pytest.raises(ValueError, match="Simulated analysis failure"):
        analyzer.analyze("test.mp4", "cmj", "balanced")


def test_configurable_mock_custom_result():
    """Test configurable mock returns custom result."""
    custom_result = VideoAnalysisResult(
        jump_height_m=1.0,
        flight_time_ms=900.0,
    )
    analyzer = ConfigurableMockAnalyzer(result=custom_result)

    result = analyzer.analyze("test.mp4", "cmj", "balanced")
    assert result.jump_height_m == 1.0
    assert result.flight_time_ms == 900.0
```

**File**: `backend/tests/test_app.py` (updated)

```python
"""Tests for FastAPI app with mocked analyzer."""

import os
from fastapi.testclient import TestClient

# Set mock analyzer before importing app
os.environ["USE_MOCK_ANALYZER"] = "true"

from kinemotion_backend.app import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_cmj():
    """Test CMJ analysis endpoint with mock."""
    # Create fake video file
    video_content = b"fake video data"

    response = client.post(
        "/api/analyze",
        files={"video": ("test.mp4", video_content, "video/mp4")},
        data={"jump_type": "cmj", "quality": "balanced"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "metrics" in data
    assert data["metrics"]["jump_height_m"] > 0
```

## Migration Plan

### Timeline: 1-2 days

### Step 1: Create Adapter Infrastructure (2 hours)
- [ ] Create `backend/src/kinemotion_backend/video_analyzer.py`
- [ ] Create `backend/src/kinemotion_backend/adapters/__init__.py`
- [ ] Create `backend/src/kinemotion_backend/adapters/cli_adapter.py`
- [ ] Create `backend/src/kinemotion_backend/adapters/mock_adapter.py`
- [ ] Run: `uv run pyright` to verify types

### Step 2: Update Application Code (1 hour)
- [ ] Update `backend/src/kinemotion_backend/app.py`
- [ ] Add `get_video_analyzer()` factory function
- [ ] Replace direct `process_cmj_video` / `process_dropjump_video` calls
- [ ] Add `USE_MOCK_ANALYZER` environment variable support

### Step 3: Add Tests (2 hours)
- [ ] Create `backend/tests/test_adapters.py`
- [ ] Update `backend/tests/test_app.py` to use mock
- [ ] Run: `uv run pytest` to verify all tests pass

### Step 4: Update Docker Configuration (1 hour)
- [ ] Update `backend/Dockerfile` to install kinemotion CLI separately
- [ ] Remove `kinemotion>=0.30.0` from `pyproject.toml` dependencies
- [ ] Test Docker build: `docker build -t backend-test ./backend`
- [ ] Test Docker run with CLI: `docker run backend-test uv run kinemotion --version`

### Step 5: Deploy and Verify (2 hours)
- [ ] Deploy to Cloud Run staging environment
- [ ] Test with real video upload
- [ ] Verify kinemotion CLI works in container
- [ ] Check logs for any errors
- [ ] Deploy to production

### Step 6: Update Documentation
- [ ] Update `backend/README.md` with new architecture
- [ ] Document environment variables (`USE_MOCK_ANALYZER`)
- [ ] Update deployment guide

## Rollback Plan

If issues arise:

1. **Keep both implementations temporarily**:
   ```python
   # app.py
   USE_CLI_ADAPTER = os.getenv("USE_CLI_ADAPTER", "false").lower() == "true"

   if USE_CLI_ADAPTER:
       video_analyzer = KinemotionCLIAdapter()
   else:
       # Old way - direct import
       from kinemotion.api import process_cmj_video
   ```

2. **Toggle via environment variable** in Cloud Run
3. **Gradually migrate** one endpoint at a time

## Verification Checklist

### Development
- [ ] Adapter interface compiles without errors
- [ ] Mock adapter returns correct data structure
- [ ] Unit tests pass with mock adapter
- [ ] Type checking passes (`uv run pyright`)

### Docker
- [ ] Docker builds successfully
- [ ] kinemotion CLI available in container: `docker run <image> kinemotion --version`
- [ ] CLI adapter can call kinemotion: `docker run <image> uv run python -c "from kinemotion_backend.adapters.cli_adapter import KinemotionCLIAdapter; a = KinemotionCLIAdapter()"`

### Integration
- [ ] Health check responds
- [ ] Video upload works
- [ ] Analysis completes successfully
- [ ] JSON output matches expected format
- [ ] Quality warnings are captured
- [ ] Error handling works (invalid video, etc.)

### Performance
- [ ] Video processing time < 10 seconds for 30s video
- [ ] Subprocess overhead < 200ms
- [ ] Memory usage stable

## Benefits Summary

| Before | After |
|--------|-------|
| Backend imports kinemotion.api | Backend calls kinemotion CLI |
| Dependencies: kinemotion>=0.30.0 | Dependencies: (none) |
| Deploy coupling: Wait for PyPI | Deploy independence: Update Docker |
| Testing: Requires kinemotion | Testing: Use mock adapter |
| Repository: Shared Python code | Repository: Clean separation |
| Breaking changes: Break backend | Breaking changes: CLI contract stable |

## Next Steps

1. **Implement adapter pattern** (this guide)
2. **Test in staging environment**
3. **Deploy to production**
4. **Monitor for issues**
5. **Consider repository split** (now unblocked!)

## Alternative: Keep Python API with Version Pinning

If CLI approach has issues, alternative is to keep using kinemotion.api but with better version management:

```toml
# pyproject.toml
dependencies = [
    "kinemotion==0.34.0",  # Pin exact version, not >=
]
```

Then coordinate releases:
1. Release kinemotion v0.35.0 to PyPI
2. Update backend pyproject.toml to kinemotion==0.35.0
3. Deploy backend

This is simpler but doesn't solve deployment coupling.

---

**Status**: Ready for implementation
**Recommendation**: Use CLI adapter approach for clean decoupling
