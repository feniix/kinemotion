______________________________________________________________________

title: Infrastructure & Deployment Assessment - Roadmap
type: note
permalink: assessments/infrastructure-deployment-assessment-roadmap
tags:

- infrastructure
- devops
- roadmap
- assessment
- deployment

______________________________________________________________________

# Kinemotion Infrastructure & Deployment Assessment

**Date:** November 17, 2025
**Prepared by:** DevOps/CI-CD Engineer
**Status:** Comprehensive Infrastructure Review for 6-Month Roadmap
**Classification:** Technical Assessment

______________________________________________________________________

## Executive Summary

The strategic roadmap introduces a **fundamental architectural shift** from single-machine CLI tool to distributed real-time platform. Current CI/CD infrastructure is **adequate for initial tasks (1-2)** but has **critical gaps for real-time service (Task 3)** and **moderate gaps for multi-sport expansion (Tasks 4-5)**.

**Key Finding:** Task 3 (Real-Time Web Analysis) requires significant infrastructure investment. Without addressing gaps, project risks latency failures and deployment issues.

### Infrastructure Readiness Score

| Component                | Current | Required | Gap          |
| ------------------------ | ------- | -------- | ------------ |
| CI/CD Testing            | 8/10    | 9/10     | Low          |
| Build Automation         | 6/10    | 9/10     | **Medium**   |
| Containerization         | 0/10    | 9/10     | **CRITICAL** |
| Deployment Pipeline      | 0/10    | 9/10     | **CRITICAL** |
| Load Testing             | 0/10    | 8/10     | **HIGH**     |
| Monitoring/Observability | 0/10    | 9/10     | **CRITICAL** |
| Performance Profiling    | 0/10    | 8/10     | **HIGH**     |
| Release Automation       | 7/10    | 8/10     | Low          |

**Overall Readiness:** 3/10 (Adequate for CLI, Insufficient for platform)

______________________________________________________________________

## 1. CI/CD Pipeline Assessment

### Current State (v0.28.0)

**File:** `.github/workflows/test.yml`

```yaml
Trigger:     On PR and push to main
Runner:      ubuntu-latest (single)
Python:      3.12.7 (via asdf)
Package Mgr: uv
Tests:       261 tests, 74.27% coverage
Time:        ~5 minutes per run
Coverage:    pytest-cov → coverage.xml → SonarCloud
Quality:     SonarCloud Cloud integration enabled
```

**Strengths:**

- Solid pytest configuration with coverage reporting
- SonarCloud integration working well
- Semantic release automation for versioning
- Good dependency management (uv)
- Coverage branch analysis enabled

### Assessment: Current Adequacy by Task

**Task 1 (Ankle Fix) - ADEQUATE**

- Single function change
- Existing test infrastructure handles this
- No new tools needed

**Task 2 (CMJ Testing) - ADEQUATE**

- Expands test count to 300+ tests
- All new tests are unit/integration (pytest native)
- Coverage reporting works fine
- SonarQube gates can enforce new coverage targets

**Task 3 (Real-Time WebSocket) - INADEQUATE**

- No load testing infrastructure
- No performance profiling in CI
- No WebSocket testing framework
- No Docker image building
- No deployment pipeline
- No latency benchmarking

**Task 4 (Running Gait) - PARTIALLY ADEQUATE**

- Unit tests work fine (existing pytest)
- **Missing:** Performance regression testing (ensure new sport doesn't slow pipeline)
- **Missing:** Integration tests for multi-sport API

**Task 5 (API/SDKs) - PARTIALLY ADEQUATE**

- Unit tests work fine
- **Missing:** API/HTTP testing framework
- **Missing:** Integration test for webhook delivery
- **Missing:** SDK testing across versions

### Recommendations

**Keep & Enhance (Low Effort):**

- Maintain existing pytest configuration
- Keep SonarCloud integration
- Expand coverage gates to 80% for new code
- Add code duplication enforcement (\<3% maintained)

**Must Add (Medium Effort):**

- Load testing framework (locust)
- Performance regression testing
- WebSocket testing library (pytest-asyncio, websockets)
- Docker build stage in workflow
- Integration test framework

**Timeline to Implement:**

- Week 1: Load testing setup
- Week 2-3: Docker build integration
- Week 4: Performance regression tests
- By Task 3 start (week 3): All infrastructure in place

______________________________________________________________________

## 2. Containerization Strategy

### Why Containerization is Critical

Real-time platform requires:

- **Consistent environment:** Ensure latency is reproducible
- **Deployment automation:** Docker enables CI/CD deployment
- **Scaling:** Container orchestration (Kubernetes, ECS) requires images
- **Development:** Developers test exact production environment
- **Storage:** Docker registries (Docker Hub, ECR, GCR) enable version tracking

### Dockerfile Architecture

**Target Image Size:** \<500MB (MediaPipe + OpenCV are heavy)

```dockerfile
# Multi-stage build to minimize final image

# Stage 1: Dependencies build
FROM python:3.12-slim as builder

WORKDIR /build
COPY pyproject.toml uv.lock ./

# Install uv and build dependencies
RUN pip install uv
RUN uv export --no-header > requirements.txt

# Stage 2: Runtime image
FROM python:3.12-slim

WORKDIR /app

# Install OpenCV system dependencies (slim base has minimal libs)
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy built requirements
COPY --from=builder /build/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/kinemotion ./kinemotion

# Health check for orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; socket.create_connection(('localhost', 8000), timeout=5)"

# Run FastAPI app (Task 3)
CMD ["uvicorn", "kinemotion.realtime.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Size Optimization:**

- Multi-stage build: ~250MB (dependencies only in final image)
- Slim base image: Not full ubuntu base
- Remove apt caches: -20MB
- Target: 400-500MB (acceptable for frequent deploys)

### Docker Registry Strategy

**Development/Staging:** Docker Hub or private registry
**Production:** Automated builds on releases

```yaml
# GitHub Actions: Build & Push on Release

on:
  release:
    types: [published]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t kinemotion:${{ github.ref_name }} .
          docker build -t kinemotion:latest .

      - name: Push to registry
        run: |
          docker push kinemotion:${{ github.ref_name }}
          docker push kinemotion:latest
```

### Timeline

- **Week 1 (Task 3 planning):** Dockerfile finalized, tested locally
- **Week 2:** GitHub Actions build integration
- **Week 3:** Docker Compose setup for local development
- **Week 4:** Registry setup and automated pushes

______________________________________________________________________

## 3. Deployment Architecture

### Target Architecture (Production)

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Browser (React/Next.js)                              │  │
│  │  - Video capture (WebRTC)                             │  │
│  │  - Live metrics display                               │  │
│  │  - Connection status indicator                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ WebSocket (50ms)
┌─────────────────────────────────────────────────────────────┐
│                  INGRESS LAYER                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Load Balancer (Nginx/HAProxy)                        │  │
│  │  - Sticky session routing (WebSocket affinity)        │  │
│  │  - TLS termination                                    │  │
│  │  - Rate limiting                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              APPLICATION LAYER (Auto-scaling)               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  FastAPI + Uvicorn Replicas (N instances)            │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │  │
│  │  │ Instance 1   │ │ Instance 2   │ │ Instance N   │ │  │
│  │  │ MediaPipe    │ │ MediaPipe    │ │ MediaPipe    │ │  │
│  │  │ WebSocket    │ │ WebSocket    │ │ WebSocket    │ │  │
│  │  │ Handler      │ │ Handler      │ │ Handler      │ │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           CACHE & MESSAGE LAYER                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Redis (metrics cache, pub/sub, session store)        │  │
│  │  - Stores live metrics (latency <5ms)                 │  │
│  │  - Cross-instance pub/sub for broadcasts              │  │
│  │  - Session affinity helper                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              PERSISTENCE & MONITORING                       │
│  ┌────────────────────┐ ┌────────────────────────────────┐ │
│  │ PostgreSQL         │ │ Prometheus + Grafana           │ │
│  │ - Analysis history │ │ - Metrics collection           │ │
│  │ - User data        │ │ - Alerting                     │ │
│  │ - Audit logs       │ │ - Dashboard                    │ │
│  │ - Webhooks         │ │                                │ │
│  └────────────────────┘ └────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ S3 / Cloud Storage                                      │ │
│  │ - Video files (analysis input)                          │ │
│  │ - Output videos (with debug overlay)                    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Latency Budget (Target: \<200ms E2E)

```
Client → Capture: 33ms (30fps)
Client → Network: 20ms (LAN) / 50ms (Internet)
Network → Server: 50ms (internet typical)
Server → Process: 50ms (MediaPipe pose detection)
Server → Calculate: 20ms (kinematics)
Server → Transmit: 20ms (network)
Browser → Render: 33ms (30fps)
────────────────────────────────────
TOTAL: ~170-250ms

Acceptable range: <200ms (elite), 200-300ms (competitive)
Fallback: 250ms still competitive vs Motion-IQ (200-250ms)
```

### Deployment Targets

**Development (Local):**

- Docker Compose with services
- File: `docker-compose.dev.yml`
- Services: FastAPI, Redis, PostgreSQL, Prometheus
- Purpose: Exact reproduction of prod locally

**Staging (Cloud):**

- Kubernetes cluster (managed: EKS, GKE, AKS)
- OR: Fargate (serverless containers)
- OR: Cloud Run (Google) or similar
- Auto-scaling: 2-4 replicas based on CPU
- Purpose: Pre-production testing, load testing
- Cost: ~$100-200/month

**Production (Cloud):**

- Same as staging with higher resource limits
- Auto-scaling: 4-8+ replicas
- Blue-green or canary deployment strategy
- Backup/redundancy: Multi-zone deployment
- Cost: ~$500-1000/month (depends on load)

### Recommended Cloud Platform

**AWS ECS + Fargate (Recommended):**

- Native integration with GitHub Actions
- Pay-per-use pricing (lower than reserved instances)
- Load balancer (ALB) built-in
- Auto-scaling based on metrics
- Ecosystem: S3 (videos), RDS (postgres), CloudWatch (monitoring)

**Alternative: Google Cloud Run**

- Simpler deployment (git-to-prod)
- Good for initial MVP
- Limits: 1 concurrent request per instance (not ideal for WebSocket)

**Alternative: Kubernetes (self-hosted or managed)**

- More complex but very flexible
- Better for 100+ concurrent users at scale
- Steeper learning curve

______________________________________________________________________

## 4. Testing Infrastructure

### Current Testing (Working Well)

```
261 tests (74.27% coverage)
├─ Unit tests: 180 tests (core algorithms, kinematics)
├─ Integration: 60 tests (API, video I/O)
└─ E2E: 21 tests (real video files)

Execution: ~5 minutes
Coverage: pytest-cov, branch coverage enabled
Quality: SonarCloud gates (current passing)
```

### Testing Gaps to Close

#### 1. Load Testing (NEW - Required for Task 3)

**Tool:** Locust (Python-based, easy to write tests)

```python
# tests/load_test_realtime.py
from locust import HttpUser, task, between
import websocket
import json

class RealtimeUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def analyze_video_stream(self):
        # Simulate WebSocket connection
        # Send frame stream for 10 seconds
        # Measure latency and error rate
        pass

# Run: locust -f tests/load_test_realtime.py --host=http://localhost:8000
```

**Scenarios:**

- 25 concurrent users (baseline)
- 100 concurrent users (peak)
- Ramp-up: 1 user/sec for 100 sec
- Measure: p50, p95, p99 latencies, error rate

**Integration:** GitHub Actions workflow on PRs

```yaml
# .github/workflows/load-test.yml
on: pull_request

jobs:
  load-test:
    runs-on: ubuntu-latest
    services:
      app:
        image: kinemotion:latest
        ports:
          - 8000:8000

    steps:
      - name: Run load test (25 concurrent)
        run: |
          locust -f tests/load_test_realtime.py \
            --headless \
            -u 25 -r 5 --run-time 2m \
            --csv results

      - name: Check SLO
        run: |
          python scripts/check_load_test_slo.py results
          # Fail if p95 > 200ms or error rate > 1%
```

#### 2. Performance Profiling (NEW - Required for Task 3)

**Tools:** py-spy, cProfile, memory_profiler

```python
# tests/performance_profile.py
import cProfile
import pstats
from kinemotion.realtime.pipeline import RealtimePipeline

def profile_pipeline():
    pipeline = RealtimePipeline(quality="balanced")

    # Load sample video frames
    frames = load_test_frames(100)

    # Profile
    profiler = cProfile.Profile()
    profiler.enable()

    for frame in frames:
        pipeline.process_frame(frame)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 slowest functions
```

**Bottleneck Targets:**

- MediaPipe detection: should be \<40ms
- Kinematics calculation: should be \<10ms
- WebSocket encoding: should be \<5ms
- Total frame-to-metrics: should be \<50ms

#### 3. WebSocket Testing (NEW - Required for Task 3)

```python
# tests/test_websocket_realtime.py
import pytest
from fastapi.testclient import TestClient
from kinemotion.realtime.server import app

@pytest.mark.asyncio
async def test_websocket_connection():
    client = TestClient(app)
    with client.websocket_connect("/ws/analyze") as websocket:
        # Send video frame
        websocket.send_json({"frame": b64encode(frame).decode()})

        # Receive metrics
        data = websocket.receive_json()
        assert "metrics" in data
        assert data["metrics"]["cmj_height"] > 0

@pytest.mark.asyncio
async def test_concurrent_connections():
    # Test 10+ concurrent WebSocket connections
    # Verify isolation (one user's analysis doesn't affect others)
    pass
```

#### 4. API Testing (NEW - Required for Task 5)

```python
# tests/test_api_integration.py
def test_api_analysis_endpoint():
    response = client.post("/api/v1/analyses/dropjump",
        json={"video_url": "s3://videos/test.mp4"})
    assert response.status_code == 202  # Accepted
    analysis_id = response.json()["id"]

    # Poll for completion
    for _ in range(30):  # 30 seconds timeout
        result = client.get(f"/api/v1/analyses/{analysis_id}")
        if result.status_code == 200:
            assert result.json()["status"] == "completed"
            break

def test_webhook_delivery():
    # Verify webhook is called on analysis completion
    # Mock webhook receiver
    pass

def test_rate_limiting():
    # Verify 1000 calls/month limit enforced
    pass
```

#### 5. Regression Testing (NEW - Performance)

```yaml
# Automatic performance regression detection
on: pull_request

jobs:
  regression-test:
    steps:
      - name: Benchmark new code
        run: pytest --benchmark-only

      - name: Compare to baseline
        run: pytest-benchmark compare
```

### Test Execution Timeline

**Week 1-2 (immediate):**

- Add load testing scaffold
- Add WebSocket testing framework
- Integrate with CI/CD

**Week 3-4 (Task 3 active):**

- Run full load tests
- Performance profiling on real streams
- Identify bottlenecks

**Week 5+ (ongoing):**

- Regression tests on every PR
- Performance benchmarking suite

______________________________________________________________________

## 5. Monitoring & Observability Strategy

### Current Monitoring: ZERO

No infrastructure for tracking real-time system health.

### Required Monitoring Architecture

#### Prometheus Metrics Collection

```python
# kinemotion/realtime/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Connection metrics
ws_active_connections = Gauge('ws_active_connections',
    'Active WebSocket connections')

# Analysis metrics
analyses_total = Counter('analyses_total',
    'Total analyses completed', ['sport'])
analyses_failed = Counter('analyses_failed',
    'Failed analyses', ['error_type'])

# Latency metrics (track percentiles)
frame_latency = Histogram('frame_latency_ms',
    'End-to-end frame processing latency',
    buckets=[50, 100, 150, 200, 250, 300, 500, 1000])

# Resource metrics
mediapipe_time = Histogram('mediapipe_process_ms',
    'MediaPipe detection time')
memory_usage = Gauge('memory_usage_mb',
    'Memory usage in MB')
```

**FastAPI Integration:**

```python
# Add Prometheus endpoint to FastAPI
from prometheus_client import make_asgi_app
from fastapi import FastAPI

app = FastAPI()

# Add /metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

#### Grafana Dashboards

**Key Dashboards to Create:**

1. **System Health Dashboard:**

   - Active connections (gauge)
   - Error rate (counter)
   - p95 latency (histogram)
   - CPU/Memory usage

1. **Analysis Dashboard:**

   - Analyses by sport (pie chart)
   - Completion rate (gauge)
   - Average latency by sport
   - Failed analyses by error type

1. **Infrastructure Dashboard:**

   - Container restarts
   - Scaling events (replicas added/removed)
   - Deployment timeline
   - Resource utilization

#### Alert Rules (SLO Enforcement)

```yaml
# prometheus-rules.yml
groups:
  - name: kinemotion-slos
    rules:
      # Latency SLO: p95 < 200ms
      - alert: HighLatencySLO
        expr: histogram_quantile(0.95, rate(frame_latency_ms_bucket[5m])) > 200
        for: 5m
        annotations:
          summary: "P95 latency exceeds 200ms"

      # Error rate SLO: <1%
      - alert: HighErrorRate
        expr: rate(analyses_failed_total[5m]) / rate(analyses_total[5m]) > 0.01
        for: 5m
        annotations:
          summary: "Error rate exceeds 1%"

      # Resource SLO: CPU <80%
      - alert: HighCPUUsage
        expr: (100 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        annotations:
          summary: "CPU usage exceeds 80%, triggering auto-scale"
```

#### Log Aggregation

**Structured Logging Setup:**

```python
# kinemotion/realtime/logging.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "event": record.__dict__.get("event"),
            "sport": record.__dict__.get("sport"),
            "user_id": record.__dict__.get("user_id"),
            "latency_ms": record.__dict__.get("latency_ms"),
        }
        return json.dumps(log_obj)

# Usage
logger.info("analysis_started", extra={
    "event": "analysis_started",
    "sport": "cmj",
    "user_id": "user123"
})
```

**Log Aggregation Options:**

- Cloud: CloudWatch (AWS), Stackdriver (GCP), Application Insights (Azure)
- Self-hosted: ELK Stack (Elasticsearch, Logstash, Kibana)
- Recommended: Cloud provider for simplicity

#### SLO Thresholds

| Metric       | Threshold | Action               |
| ------------ | --------- | -------------------- |
| p95 Latency  | \<200ms   | Alert if exceeded 5m |
| Error Rate   | \<1%      | Alert if exceeded 5m |
| Availability | >99%      | Alert if degraded    |
| CPU Usage    | \<80%     | Scale up if exceeded |
| Memory       | \<85%     | Alert if exceeded    |

### Monitoring Timeline

**Week 1 (Task 3 planning):**

- Set up Prometheus + Grafana (local docker-compose)
- Define metrics collection points

**Week 2-3 (Task 3 active):**

- Integrate Prometheus client into FastAPI app
- Build monitoring dashboards
- Deploy to staging

**Week 4+:**

- Validate SLOs in production
- Tune alerting rules
- Set up on-call rotation

______________________________________________________________________

## 6. Release & Versioning Strategy

### Current State

```
Semantic Release: ✓ Working
Version bumping: ✓ Automated
CLI packaging: ✓ Releases on GitHub
```

### Required for Roadmap

Multi-artifact releases:

1. **CLI Tool** (Python package) → PyPI + GitHub Releases
1. **Real-Time Service** (Docker image) → Registry
1. **Python SDK** (Python package) → PyPI
1. **JavaScript SDK** (npm package) → npm registry
1. **API Documentation** → GitHub Pages

### Unified Release Workflow

```yaml
# .github/workflows/release.yml
on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      # 1. Determine version (semantic-release)
      - name: Run semantic release
        uses: cycjimmy/semantic-release-action@v3
        with:
          semantic_version: 19
          extra_plugins: |
            @semantic-release/changelog
            @semantic-release/git
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      # 2. Build CLI package
      - name: Build Python package
        run: |
          pip install build
          python -m build

      # 3. Publish CLI to PyPI
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

      # 4. Build & Push Docker image
      - name: Build Docker image
        run: |
          VERSION=$(cat pyproject.toml | grep version | head -1 | awk -F'"' '{print $2}')
          docker build -t kinemotion:$VERSION -t kinemotion:latest .

      - name: Push Docker image
        run: |
          docker push kinemotion:$VERSION
          docker push kinemotion:latest

      # 5. Build & Publish SDKs
      - name: Build Python SDK
        run: python scripts/build_sdk_python.py

      - name: Publish Python SDK
        run: twine upload dist/kinemotion-sdk-python-*.whl

      - name: Build JavaScript SDK
        run: npm run build

      - name: Publish JavaScript SDK
        run: npm publish

      # 6. Deploy to Staging
      - name: Deploy to Staging
        run: |
          aws ecs update-service \
            --cluster kinemotion-staging \
            --service realtime-api \
            --force-new-deployment

      # 7. Update API Documentation
      - name: Deploy API docs
        run: |
          npm run docs:build
          aws s3 sync docs/_build/html s3://kinemotion-docs/
```

### Release Checklist

- [ ] All tests passing (261+ tests, 80%+ coverage)
- [ ] Code review approved
- [ ] No critical SonarCloud issues
- [ ] Performance benchmarks acceptable
- [ ] Changelog updated
- [ ] Documentation updated
- [ ] BREAKING_CHANGE if needed

### Version Progression (6 Months)

```
v0.28.0 (current, CLI only)
  ↓
v0.29.0 (Tasks 1-2: Accuracy + Testing)
  - Ankle angle fix
  - CMJ phase progression tests

v0.30.0 (Task 3: Real-Time)
  - WebSocket service
  - Real-time analysis API
  - Docker image published

v0.31.0 (Task 4: Running Gait)
  - Running gait analysis
  - Multi-sport platform

v0.32.0 (Task 5: APIs/SDKs)
  - Public API documentation
  - Python SDK
  - JavaScript SDK
  - Webhook system

v1.0.0 (Release candidate)
  - Production-ready
  - All features stable
  - Enterprise-ready
```

______________________________________________________________________

## 7. SonarQube Integration for New Features

### Current SonarQube Setup

```
Project: feniix_kinemotion
Coverage: 74.27% (261 tests)
Branch coverage: Enabled
Quality gate: Default (passing)
```

### Quality Gates for Roadmap Features

**New Code Quality Requirements:**

```properties
# sonar-project.properties (updated)

# Code Coverage
sonar.newCode.coverageComparison=PROJECT

# New code must have 80%+ coverage
sonar.qualitygate.new_coverage=80

# No new critical issues
sonar.qualitygate.new_critical_issues=0

# Branch coverage enabled
sonar.python.coverage.branchCoverage=true

# Duplication < 3%
sonar.cpd.exclusions=**/test_**,**/*_test.py
sonar.qualitygate.duplicated_lines_density=3

# Type safety (pyright strict)
sonar.python.mypy_path=/usr/local/bin/pyright
```

### WebSocket Code Quality Focus

**Task 3 (Real-Time WebSocket) must have:**

- Unit tests: All functions covered (>90%)
- Integration tests: WebSocket scenarios covered (>85%)
- Type hints: 100% coverage (pyright strict)
- Error handling: All exceptions tested
- Performance tests: Latency benchmarks documented

**Example: WebSocket handler quality standards**

```python
# kinemotion/realtime/websocket_handler.py
# Line 1: Must have type hints on all parameters/returns
async def handle_analysis_websocket(
    websocket: WebSocket,
    quality: str = "balanced"
) -> None:
    """WebSocket handler for real-time analysis.

    Args:
        websocket: WebSocket connection
        quality: Analysis quality preset

    Raises:
        WebSocketDisconnect: Connection closed
        ValidationError: Invalid quality preset
    """
    # Every code path must be tested
```

**SonarQube Dashboard for Task 3:**

- Coverage: Target 85%+ (real-time code)
- Duplication: \<2%
- Bugs: 0
- Vulnerabilities: 0
- Code smells: \<10
- Hotspots: All reviewed

______________________________________________________________________

## 8. Performance Testing Framework

### Performance Test Suite

**Scope:** Ensure real-time service meets latency SLOs

```python
# tests/test_performance.py
import pytest
from kinemotion.realtime.pipeline import RealtimePipeline

class TestPerformance:

    @pytest.mark.performance
    def test_frame_processing_latency(self):
        """Assert frame-to-metrics latency < 50ms"""
        pipeline = RealtimePipeline(quality="balanced")

        latencies = []
        for frame in load_test_frames(100):
            start = time.perf_counter()
            metrics = pipeline.process_frame(frame)
            latencies.append((time.perf_counter() - start) * 1000)

        p95_latency = np.percentile(latencies, 95)
        assert p95_latency < 50, f"p95 latency {p95_latency}ms > 50ms"

    @pytest.mark.performance
    def test_mediapipe_latency(self):
        """Assert MediaPipe detection < 40ms"""
        # Measure just pose detection time
        pass

    @pytest.mark.performance
    def test_memory_under_load(self):
        """Assert memory usage < 500MB under sustained load"""
        # Run 1000 frames, monitor memory
        pass

    @pytest.mark.performance
    def test_cpu_efficiency(self):
        """Assert CPU usage < 80% with 25 concurrent connections"""
        # Simulate concurrent load
        pass
```

**Run in CI:**

```bash
# Run performance tests on PR
pytest tests/test_performance.py -v

# Generate performance report
pytest --benchmark-only --benchmark-json=results.json

# Compare to baseline
pytest-benchmark compare results.json baseline.json --fail-if-slower=5
```

### Latency Budget Tracking

**Document in repository:**

```markdown
# Performance Budget

## Frame-to-Metrics Latency

| Component | Budget | Actual | Status |
|-----------|--------|--------|--------|
| Capture (client) | 33ms | 30ms | OK |
| Network (client→server) | 50ms | 45ms | OK |
| MediaPipe detection | 40ms | 38ms | OK |
| Kinematics calc | 10ms | 8ms | OK |
| Network (server→client) | 20ms | 18ms | OK |
| Render (browser) | 33ms | 30ms | OK |
| **TOTAL** | **200ms** | **169ms** | **OK** |

## Headroom

- 31ms buffer (16% headroom)
- Fallback: Can accept 250ms for amateur coaches
```

______________________________________________________________________

## 9. Risk Assessment & Mitigation

### Critical Risks

#### RISK 1: Latency Misses Target (HIGH PROBABILITY, HIGH IMPACT)

**Problem:** Real-time service requires \<200ms latency, but MediaPipe may not support this with concurrent streams.

**Probability:** MEDIUM (55%)

- MediaPipe detection: 25-53ms on modern hardware
- Variable depending on model and video resolution
- Unknown with concurrent loads

**Impact:** HIGH

- Market positioning lost (Motion-IQ also ~200ms)
- Invalidates primary market differentiation

**Mitigation (MANDATORY):**

1. **Performance testing in Week 1 of Task 3** (non-negotiable)
1. Measure latency with realistic video resolution
1. Load test with 25 concurrent streams
1. If latency > 250ms: Plan fallback architecture
   - Client-side MediaPipe lite model (lower accuracy, faster)
   - Queue-based architecture with delayed feedback (coaching mode)
   - Async processing (not real-time, but still fast)

**Fallback Latency Goals:**

- Elite: \<200ms (current target)
- Acceptable: 200-300ms (still competitive)
- Fallback: 250ms + cached results (not ideal, but deployable)

**Decision Point:** End of Week 2, Task 3

- If \<200ms: Proceed with real-time
- If 200-250ms: Document trade-offs, proceed
- If >250ms: Pivot to deferred feedback model

#### RISK 2: Scaling Bottleneck (MEDIUM PROBABILITY, MEDIUM IMPACT)

**Problem:** MediaPipe is CPU-bound; 100 concurrent users require 4+ GPU-accelerated instances.

**Probability:** MEDIUM (60%)

- MediaPipe can't be easily parallelized
- GPU instances are expensive
- Cost may not justify early scaling

**Impact:** MEDIUM

- Higher infrastructure costs
- May delay profitability

**Mitigation:**

1. Start with CPU instances (cheaper)
1. Monitor CPU usage and latency correlation
1. Scale to GPU only if needed (Week 4+)
1. Alternative: Model optimization (quantization, pruning)

#### RISK 3: Deployment Failures (LOW PROBABILITY, HIGH IMPACT)

**Problem:** No deployment experience; rolling out new code breaks live coaching sessions.

**Probability:** LOW (30%)

- Staged rollout (staging first)
- Automated testing prevents most failures
- Blue-green deployment reduces risk

**Impact:** HIGH

- Coaches can't use service during outage
- Loss of trust/revenue

**Mitigation:**

1. **Staging-only for first 2 weeks** (Week 3-4)
1. Canary deployment: 10% traffic → 50% → 100% (Week 5+)
1. Automated rollback: If error rate > 5% → rollback
1. Monitoring alerts: Page on-call for critical metrics
1. Runbook: documented procedures for common failures

#### RISK 4: Testing Gaps on Real-Time Code (MEDIUM PROBABILITY, MEDIUM IMPACT)

**Problem:** WebSocket code is complex; bugs cause latency issues or connection losses.

**Probability:** MEDIUM (50%)

- WebSocket testing is less common than HTTP
- Complex state management
- Concurrent connections add complexity

**Impact:** MEDIUM

- Sporadic failures hard to debug
- Coverage-based SonarQube gates don't catch concurrency bugs

**Mitigation:**

1. WebSocket testing library in place (pytest-asyncio, websockets)
1. Chaos engineering tests (simulate network failures)
1. Stress tests: 100+ concurrent connections, hold 10 minutes
1. Code review focus: All async/await code requires review

#### RISK 5: Monitoring Gap (MEDIUM PROBABILITY, MEDIUM IMPACT)

**Problem:** Production issues invisible; no alerting for SLO violations.

**Probability:** MEDIUM (50%)

- Prometheus/Grafana not set up initially
- Metrics added later

**Impact:** MEDIUM

- Slow incident response
- Customer impact not detected immediately

**Mitigation:**

1. **Prometheus + Grafana mandatory by Week 2 of Task 3**
1. Alert rules in place before production deploy
1. Simulated alerts during staging
1. On-call rotation established

### Medium Risks

**RISK 6: Container Image Size (LOW PROBABILITY, LOW IMPACT)**

- Mitigation: Multi-stage build, test image size on Week 1

**RISK 7: Semantic Release Versioning Confusion (LOW PROBABILITY, LOW IMPACT)**

- Mitigation: Clear commit message standards (already in place)

**RISK 8: SonarQube Quality Gate False Positives (LOW PROBABILITY, LOW IMPACT)**

- Mitigation: Regularly review gate rules, tune thresholds

### Risk Summary

| Risk                     | Probability | Impact | Status   | Mitigation          |
| ------------------------ | ----------- | ------ | -------- | ------------------- |
| Latency misses target    | MEDIUM      | HIGH   | CRITICAL | Perf testing Week 1 |
| Scaling bottleneck       | MEDIUM      | MEDIUM | HIGH     | Monitor CPU/latency |
| Deployment failures      | LOW         | HIGH   | HIGH     | Staging → canary    |
| Testing gaps (WebSocket) | MEDIUM      | MEDIUM | MEDIUM   | Advanced testing    |
| Monitoring blind spot    | MEDIUM      | MEDIUM | MEDIUM   | Prometheus Week 2   |

______________________________________________________________________

## 10. Infrastructure Recommendations to Roadmap

### Immediate Changes (Before Task 3 Starts)

1. **Add Load Testing to CI/CD** (Week 1-2)

   - Locust framework
   - 25-concurrent baseline test
   - Latency assertion: p95 \< 200ms
   - Error rate assertion: \<1%

1. **Build Dockerfile** (Week 1-2)

   - Multi-stage build
   - Size target: \<500MB
   - Health check endpoint

1. **Docker Compose for Development** (Week 1-2)

   - FastAPI + Redis + PostgreSQL
   - Enables local testing of full system
   - Matches production environment

### Before Production Deploy (Week 4-5)

1. **Prometheus + Grafana Setup** (Week 2-3)

   - Metrics collection points in code
   - Dashboards for health monitoring
   - Alert rules for SLOs

1. **Deployment Pipeline** (Week 3-4)

   - GitHub Actions workflow for staging
   - Manual approval for production
   - Automated rollback capability

1. **Performance Profiling Automation** (Week 3-4)

   - py-spy integration in CI
   - Bottleneck identification
   - Regression detection

### Ongoing (Months 2-6)

1. **Multi-Registry Strategy** (Month 2+)

   - Docker Hub for public images
   - Private registry for staging
   - ECR/GCR for production

1. **Integration Testing Framework** (Month 2+)

   - API endpoint testing (Task 5)
   - Webhook testing
   - SDK testing

1. **Database Migration Infrastructure** (Month 2+)

   - Alembic for PostgreSQL migrations
   - Versioned schemas
   - Rollback procedures

1. **API Documentation Automation** (Month 2+)

   - OpenAPI/Swagger generation
   - Multi-version API docs
   - SDK generation from OpenAPI spec

______________________________________________________________________

## 11. Detailed Implementation Timeline

### Week 1 (Task 1 - Ankle Fix + Infrastructure Planning)

**DevOps Actions:**

- [ ] Finalize Dockerfile design
- [ ] Review Latency budget calculations
- [ ] Load testing tool selection (Locust)
- [ ] Estimate infrastructure costs (staging + prod)

**No blocking changes** - Task 1 doesn't require infrastructure

### Week 2 (Task 1 Complete, Task 2 Starting + Task 5 API Docs Starting)

**DevOps Actions:**

- [ ] Build and test Dockerfile locally
- [ ] Set up Docker Compose for dev
- [ ] Integrate Locust load tests into CI
- [ ] Create GitHub Actions workflow for load testing
- [ ] Add performance benchmarking to pytest
- [ ] Set up Prometheus + Grafana locally

**CI/CD Changes:**

- Add load-test.yml workflow
- Add performance-regression.yml workflow

### Week 3 (Task 2 Complete + Task 3 Real-Time Starting)

**DevOps Actions:**

- [ ] Performance testing on real video streams (CRITICAL)
- [ ] Identify latency bottlenecks
- [ ] Select cloud platform (AWS ECS recommended)
- [ ] Provision staging environment
- [ ] Deploy Prometheus to staging
- [ ] WebSocket testing framework ready
- [ ] Begin FastAPI + Uvicorn integration

**Decision Point:** Latency acceptable? (target \<200ms)

- YES: Proceed with real-time architecture
- NO: Plan fallback (async processing or client-side)

### Week 4-5 (Task 3 Active - Real-Time Implementation)

**DevOps Actions:**

- [ ] Deploy real-time service to staging
- [ ] Run 25-concurrent load test on staging
- [ ] Measure end-to-end latency (target \<200ms)
- [ ] Optimize bottlenecks
- [ ] Set up canary deployment pipeline
- [ ] Deploy monitoring to staging
- [ ] Test rollback procedures

**Deliverable:** Sub-200ms latency achieved on staging

### Week 6-7 (Task 3 Complete, Task 4 & 5 Active)

**DevOps Actions:**

- [ ] Real-time service to production (canary)
- [ ] Monitor production metrics
- [ ] Set up alerting on-call rotation
- [ ] Auto-scale policies tuned
- [ ] Multi-sport architecture validated (Task 4)
- [ ] API endpoint testing (Task 5)

**Deliverable:** Production real-time service live

### Week 8+ (Task 4 & 5 Complete + Month 6 Preview)

**DevOps Actions:**

- [ ] Multi-registry strategy (Docker Hub + ECR)
- [ ] Database migration tools (Alembic)
- [ ] SDK testing automation
- [ ] Performance SLO dashboard
- [ ] Cost optimization review

**Deliverable:** Platform infrastructure ready for scale

______________________________________________________________________

## 12. Cost Estimation

### Development (Local)

- **Docker:** Free
- **GitHub:** Free
- **SonarCloud:** Free (open source)
- **Total:** $0/month

### Staging (Cloud)

- **Compute (2-4 instances):** $50-150/month
- **Data transfer:** $10-20/month
- **Storage (PostgreSQL, Redis):** $20-50/month
- **Total:** $100-200/month

### Production (Year 1)

- **Compute (4-8 instances):** $200-400/month
- **Data transfer:** $50-100/month
- **Storage (PostgreSQL, Redis):** $50-100/month
- **Monitoring (Datadog/New Relic alternative):** $50-100/month
- **Total:** $500-1000/month (scales with users)

### CI/CD & DevOps Tools

- **GitHub Actions:** Free (for open source)
- **Docker Hub (private):** $5-30/month
- **Monitoring (Prometheus/Grafana):** Free (self-hosted)
- **Total:** $0-50/month

______________________________________________________________________

## 13. Rollback & Disaster Recovery

### Deployment Rollback Procedures

**Automated Rollback (Production):**

```yaml
# Triggered if error rate > 5% within 5 minutes
on: error_rate_spike

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - name: Get previous deployment
        run: |
          PREVIOUS_VERSION=$(aws ecs describe-services \
            --cluster kinemotion-prod \
            --service realtime-api | jq -r '.services[0].deployments[1].taskDefinition')

      - name: Rollback to previous
        run: |
          aws ecs update-service \
            --cluster kinemotion-prod \
            --service realtime-api \
            --task-definition $PREVIOUS_VERSION

      - name: Send alert
        run: |
          slack-notify "Production rolled back to previous version"
```

**Manual Rollback Runbook:**

```markdown
## Production Rollback Procedure

1. SSH to bastion host
2. Identify current problematic version:
   `kubectl get deployment kinemotion-realtime -o jsonpath='{.spec.template.spec.containers[0].image}'`
3. Rollback to previous stable version:
   `kubectl rollout undo deployment/kinemotion-realtime`
4. Verify new pods are healthy:
   `kubectl get pods -l app=kinemotion-realtime`
5. Monitor metrics for 5 minutes
6. If stable, close incident
7. Document incident post-mortem
```

### Data Backup Strategy

**PostgreSQL (Analysis history):**

- Daily automated backup to S3
- 30-day retention
- Test restore monthly

**Configuration:**

- Docker images tagged in registry
- Infrastructure-as-Code in git
- All configs versioned

______________________________________________________________________

## 14. SonarQube Quality Gates - Updated

### Current Quality Gate (Passing)

```
Coverage: >= 50%
New coverage: >= 80%
Duplication: < 3%
Bugs: 0
Vulnerabilities: 0
```

### Updated for Roadmap

**Task 3 (Real-Time WebSocket):**

```
New code coverage: >= 85%  (WebSocket code more critical)
Branch coverage: >= 80%    (Async code branches important)
Duplication: < 2%          (Stricter for platform)
Bugs: 0
Critical issues: 0
Hotspots: <= 5 new
```

**Task 4 (Running Gait):**

```
New code coverage: >= 80%
Duplicated lines: < 1% (reuse previous sport modules)
Type safety: 100% (pyright strict)
```

**Task 5 (API/SDKs):**

```
New code coverage: >= 80%
API stability: All endpoints backwards compatible
Documentation: >= 90% of endpoints documented
```

______________________________________________________________________

## 15. Action Items & Owners

### Immediate (This Week)

- [ ] **DevOps:** Finalize Dockerfile design
- [ ] **DevOps:** Review latency budget calculations
- [ ] **Backend Dev:** Prepare FastAPI skeleton
- [ ] **Project Manager:** Confirm infrastructure budget/approvals

### Week 1-2

- [ ] **DevOps:** Build + test Dockerfile
- [ ] **DevOps:** Integrate Locust into CI/CD
- [ ] **DevOps:** Add Docker Compose
- [ ] **Backend Dev:** Add prometheus-client to dependencies
- [ ] **Backend Dev:** Implement WebSocket scaffold

### Week 2-3

- [ ] **DevOps:** Provision staging cloud environment
- [ ] **DevOps:** Deploy Prometheus + Grafana
- [ ] **Backend Dev:** Real-time pipeline implementation
- [ ] **QA:** WebSocket testing framework ready

### Week 3-4 (CRITICAL)

- [ ] **DevOps:** Performance testing on real streams (DECISION POINT)
- [ ] **Backend Dev:** Optimize bottlenecks
- [ ] **DevOps:** Canary deployment pipeline

### Week 4+

- [ ] **DevOps:** Production deployment
- [ ] **DevOps:** Alert/monitoring tuning
- [ ] **Ops:** On-call rotation established

______________________________________________________________________

## Conclusion & Recommendations

### Infrastructure Readiness: 3/10 Currently → 9/10 Required

**Current gaps are NOT blockers for Tasks 1-2**, but **CRITICAL for Task 3**.

### Recommended Actions Before Task 3 Starts

1. **Mandatory:** Performance testing infrastructure (Week 1)
1. **Mandatory:** Containerization and deployment pipeline (Week 1-2)
1. **Mandatory:** Monitoring infrastructure (Week 2-3)
1. **High Priority:** Load testing framework (Week 1)
1. **High Priority:** WebSocket testing (Week 2)

### Critical Success Factors

- **Sub-200ms latency:** Must validate in Week 1 of Task 3, or pivot architecture
- **Horizontal scaling:** Prepare for 100+ concurrent users by Week 4
- **Production readiness:** Monitoring, alerting, rollback must exist before deploy

### Resource Requirements

- **DevOps/Platform Engineer:** 60% FTE (Weeks 1-6, then 20% ongoing)
- **Backend Developer:** 40% FTE (Weeks 2-6)
- **QA Engineer:** 30% FTE (Weeks 2-6 for testing infrastructure)

### Risk: Insufficient Infrastructure Investment

If infrastructure gaps not addressed:

- Latency failures discovered in production → Major credibility loss
- Deployment failures → Service outages → Revenue impact
- Scaling issues → Can't support paying customers
- No observability → Slow incident response

### Upside: Proper Infrastructure Investment

With recommended infrastructure:

- Sub-200ms latency validated before launch
- Automated rollback prevents outages
- Monitoring provides early warning of issues
- Scalable from day 1 (handles 100+ concurrent)
- Clear deployment strategy enables rapid iteration

______________________________________________________________________

## Appendix A: Infrastructure Checklist

### Pre-Task 3 Checklist

- [ ] Dockerfile built and tested locally (\<500MB)
- [ ] Docker Compose with full stack working locally
- [ ] Load testing framework in CI (25 concurrent baseline)
- [ ] Performance profiling integrated into pytest
- [ ] Latency budget validated (\<200ms, p95)
- [ ] Prometheus + Grafana running in staging
- [ ] Metrics collection points in code
- [ ] WebSocket testing framework ready
- [ ] Cloud staging environment provisioned
- [ ] Automated rollback tested
- [ ] On-call rotation procedure documented
- [ ] SLO thresholds defined and validated
- [ ] Monitoring alerts configured
- [ ] Deployment runbook created
- [ ] Incident response procedure defined

### Pre-Production Deploy Checklist

- [ ] All staging tests passing
- [ ] Load testing: 25-concurrent successful
- [ ] Latency: p95 \< 200ms validated
- [ ] Error rate: \< 1% under load
- [ ] Monitoring: All dashboards healthy
- [ ] Alerts: Tested and tuned
- [ ] Rollback: Tested and documented
- [ ] On-call: Team trained and rotated
- [ ] Documentation: Updated and published
- [ ] Security: TLS/HTTPS enabled, rate limiting active
- [ ] Backup: Automatic backups tested, restore verified
- [ ] Cost: Budget approved and monitored

______________________________________________________________________

**Document Status:** Ready for Implementation
**Last Updated:** November 17, 2025
**Next Review:** Weekly during execution, monthly thereafter
**Owner:** DevOps/CI-CD Engineer
