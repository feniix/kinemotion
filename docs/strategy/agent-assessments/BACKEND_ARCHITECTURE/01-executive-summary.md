# Backend Architecture Assessment - Real-Time & Multi-Sport

**Date:** November 17, 2025 | **Owner:** Python Backend Developer | **Status:** Complete

______________________________________________________________________

## Executive Summary

### Verdict: ARCHITECTURE IS SOUND AND EXECUTABLE

The proposed WebSocket + FastAPI architecture for real-time analysis is production-ready and proven by industry patterns. However, the current codebase requires strategic refactoring **before** implementing new features to maintain code quality (\<3% duplication target) and enable extensibility to multiple sports.

### Key Findings

- **Real-Time Feasibility:** YES - \<200ms E2E latency achievable with server-side MediaPipe
- **Multi-Sport Extensibility:** YES - Requires phase detection abstraction layer
- **Scale Capacity (MVP):** 5-10 concurrent streams with single GPU server
- **Scale Capacity (Enterprise):** 100+ concurrent with distributed inference tier
- **Code Quality Risk:** MEDIUM - Must refactor before Task 4 to prevent duplication spike
- **Timeline:** Realistic with disciplined execution (6 weeks MVP to real-time + running + APIs)

______________________________________________________________________

## Part 1: Architecture Assessment

### 1.1 Real-Time WebSocket + FastAPI Architecture

#### Assessment: SOUND FOR PRODUCTION USE

#### Why WebSocket + FastAPI is Ideal

1. **Proven Patterns in Industry**

   - Redis Pub/Sub for multi-worker coordination
   - Connection managers for state tracking
   - Heartbeat mechanisms for connection health

1. **Latency Budget (achievable \<200ms)**

   - Capture: 33ms (30fps camera)
   - Network: 50ms (LAN)
   - MediaPipe inference: 50ms (GPU-accelerated)
   - Metrics calc: 10ms (NumPy vectorized)
   - Render: 33ms (browser)
   - **Total: ~166ms (within budget)**

1. **FastAPI Advantages**

   - Native async/await support
   - Built-in OpenAPI documentation
   - Type safety with Pydantic
   - WebSocket support with connection management

#### Architecture Diagram

```text
Client (Browser/Mobile)
  └─ WebRTC/H.264 capture (30fps, 360p = 2Mbps)
     └─ WebSocket connection (JSON updates)

API Tier (FastAPI, scales horizontally)
  ├─ Connection manager (tracks active streams)
  ├─ Frame queue → Redis
  ├─ Receives poses from inference tier
  ├─ Metric calculation (lightweight, NumPy)
  ├─ State storage → Redis
  ├─ Pub/Sub → Redis (broadcast to dashboards)
  └─ Webhook delivery (metric updates)

Inference Tier (separate GPU workers)
  ├─ MediaPipe pose detection (frame → pose)
  ├─ Consumes from Redis queue
  ├─ Publishes results back to API
  └─ Auto-scales on queue depth

Data Tier
  ├─ Redis (state, queue, Pub/Sub)
  ├─ TimescaleDB (metrics history, optional)
  └─ S3 (video recordings, optional)
```

### 1.2 Performance Analysis at Scale

#### Single-Server Capacity (MVP Phase)

| Configuration        | Concurrent Streams | Latency (P95) | Bottleneck           |
| -------------------- | ------------------ | ------------- | -------------------- |
| CPU only (modern i9) | 1-2                | 800ms+        | MediaPipe inference  |
| GPU (RTX 3080)       | 5-10               | 150-200ms     | GPU memory           |
| GPU (RTX A100)       | 15-20              | 100-150ms     | CPU → GPU throughput |

**Practical MVP:** 5 concurrent streams with single GPU server

#### Bottleneck Hierarchy

1. **INFERENCE (Critical - 50-80% of latency)**

   - MediaPipe per-frame: 25-50ms
   - Solution: Frame batching (4-8 frames) or separate GPU tier
   - Optimization: TensorRT (3-5x speedup), Lite model (2x faster, lower accuracy)

1. **MEMORY (High - OOM at 100+ concurrent)**

   - Per connection: ~80MB (frame buffer + pose cache)
   - 100 streams: ~8GB buffers + 2GB MediaPipe + 2GB OS = 12GB total
   - Solution: Ring buffers (fixed size), stream poses to database

1. **NETWORK (Medium - depends on bandwidth)**

   - Per stream: 4-8 Mbps (720p uncompressed)
   - 100 streams: 400-800 Mbps aggregate
   - Solution: H.264 compression (25x reduction), client-side preprocessing

1. **STATE MANAGEMENT (Medium - naive implementation)**

   - 100 in-memory dicts = O(n) lookups
   - Solution: Redis-backed state (fast, automatic persistence)

#### Scaling Strategy

**MVP (Week 3-6, Task 3):**

- Single API instance + single GPU worker
- Frame queuing via Redis (ready for scale)
- Capacity: 5-10 concurrent streams
- Designed for growth, not scaled yet

**Growth Phase (Month 6-9):**

- API: 2-4 instances (stateless, behind load balancer)
- Inference: 4-8 GPU workers (auto-scaling based on queue)
- Capacity: 50-100 concurrent streams
- Architecture: Full horizontal scaling

**Enterprise Phase (Year 1+):**

- Multi-region with geo-routing
- 10-20 GPU workers per region
- Capacity: 1000+ concurrent streams
- SLA: \<100ms P95 latency

### 1.3 Existing Codebase: Readiness for Real-Time

#### Strengths

- Modular architecture (core + domain-specific modules)
- High code quality (74% coverage, 2.96% duplication, Pyright strict)
- Type-safe foundations (TypedDict, NDArray types)
- ProcessPoolExecutor pattern scales to batch processing

#### Weaknesses (Blocking Real-Time)

1. **Tightly Coupled Video I/O**

   - `VideoProcessor` reads entire file at once
   - Can't accept frame iterator (WebSocket stream)
   - Must decouple for streaming use

1. **No Streaming Pose Processor**

   - Landmarks stored in-memory array (entire video)
   - Requires frame-by-frame model for WebSocket intake
   - Needs ring buffer for smoothing window

1. **Synchronous Processing Pipeline**

   - api.py functions are blocking (video read → inference → output)
   - WebSocket needs async/await throughout
   - Must refactor to async

1. **Metrics Calculation Tightly Bound to Video Format**

   - calculate_cmj_metrics() expects complete vertical_positions array
   - Can't calculate partial metrics incrementally
   - Need to split into: partial calculation + final aggregation

#### Risk Assessment: **MEDIUM (Well-scoped, 4-5 days work)**

______________________________________________________________________

## Part 2: Refactoring Strategy (Critical Path)

### 2.1 Must Refactor BEFORE Task 3 (Real-Time)

#### Refactoring 1: Extract StreamingPoseProcessor

**Current Problem:**

```python
# api.py: Everything in one function
with VideoProcessor(video_path) as video:
    frames, landmarks = _process_all_frames(video, tracker, verbose)
    smoothed = smooth_landmarks(landmarks)
    # All data in memory
```

**Refactored Design:**

```python
# core/streaming.py
class StreamingPoseProcessor:
    """Processes frame stream incrementally, no file I/O required."""

    def __init__(self, fps: float, smoothing_window: int = 5):
        self.fps = fps
        self.smoothing_window = smoothing_window
        self.landmark_buffer = RingBuffer(smoothing_window)  # Fixed memory
        self.tracker = PoseTracker()

    async def process_frame(self, frame: np.ndarray) -> dict | None:
        """Process single frame, return smoothed landmarks or None."""
        pose = self.tracker.process_frame(frame)
        self.landmark_buffer.append(pose)

        if len(self.landmark_buffer) >= self.smoothing_window:
            smoothed = smooth_landmarks(self.landmark_buffer.get_all())
            return smoothed[-1]  # Return latest smoothed
        return None
```

**Benefits:**

- Works with any frame source (file, WebSocket, camera)
- Constant memory (ring buffer doesn't grow)
- Async-ready for integration
- **Implementation: 80 lines, 1-2 hours**

#### Refactoring 2: Extract MotionAnalyzer Abstraction

**Current Problem:**

```python
# api.py: Separate functions for each sport
def process_dropjump_video(...) -> DropJumpMetrics:
def process_cmj_video(...) -> CMJMetrics:
# 40% duplicate code (parameter handling, smoothing, output)
```

**Refactored Design:**

```python
# core/analysis.py
class MotionAnalyzer(ABC):
    """Base class for sport-specific analysis."""

    @abstractmethod
    async def detect_phases(self, landmarks: list) -> List[Phase]:
        """Detect motion phases from landmarks."""
        pass

    @abstractmethod
    async def calculate_metrics(self, phases: List[Phase]) -> Metrics:
        """Calculate sport-specific metrics from phases."""
        pass

    async def analyze(self,
        processor: StreamingPoseProcessor,
        frame_source: AsyncIterator
    ) -> Metrics:
        """Generic analysis pipeline."""
        phases = []
        async for frame in frame_source:
            landmarks = await processor.process_frame(frame)
            if landmarks:
                detected = await self.detect_phases([landmarks])
                phases.extend(detected)

        return await self.calculate_metrics(phases)

# Concrete implementations:
class CMJAnalyzer(MotionAnalyzer):
    async def detect_phases(self, landmarks):
        # Reuse existing detect_cmj_phases logic

class DropJumpAnalyzer(MotionAnalyzer):
    # Similar for dropjump
```

**Benefits:**

- Eliminates duplicate process\_\*\_video() logic
- Enables Task 4 (running) without code duplication
- Testable independently
- **Implementation: 150 lines, 2-3 hours**

#### Refactoring 3: Consolidate api.py

**Current Code Structure:**

- `process_dropjump_video()`: 232 lines
- `process_cmj_video()`: 248 lines
- `_apply_expert_overrides()`, `_print_verbose_parameters()`, etc. (helpers)
- ~40% code overlap between functions

**Refactored Structure:**

```python
# api.py (simplified)
async def process_video_streaming(
    frame_source: AsyncIterator[np.ndarray],
    analyzer: MotionAnalyzer,
    fps: float,
    quality: str = "balanced",
    verbose: bool = False
) -> Metrics:
    """Generic video processing pipeline."""
    processor = StreamingPoseProcessor(fps)
    return await analyzer.analyze(processor, frame_source)

# Backward compatible API:
def process_cmj_video(video_path: str, ...) -> CMJMetrics:
    """Batch API (unchanged from outside)."""
    with VideoProcessor(video_path) as video:
        async def frame_generator():
            while True:
                frame = video.read_frame()
                if frame is None:
                    break
                yield frame

        analyzer = CMJAnalyzer(...)
        return asyncio.run(
            process_video_streaming(
                frame_generator(),
                analyzer,
                video.fps
            )
        )
```

**Benefits:**

- Reduces api.py from 1150 lines to ~450 lines
- Single processing logic, used by file/stream/WebSocket
- **Implementation: 200 lines, 2-3 hours**

### 2.2 Must Refactor BEFORE Task 4 (Running Gait)

#### Refactoring 4: Phase Detection Abstraction

**Why Critical:**

- Current: Jump-specific phase detection (forward/backward search)
- Running: Cyclic phase detection (stance/swing alternation)
- Without abstraction: Running module will duplicate 30% of code

**Design:**

```python
# core/phase_detection.py
class Phase(TypedDict):
    start_frame: int
    end_frame: int
    phase_type: str  # e.g., "contact", "flight", "stance", "swing"
    confidence: float
    metadata: dict  # Sport-specific data

class PhaseDetector(ABC):
    @abstractmethod
    def detect_phases(
        self,
        landmarks_sequence: list[dict],
        fps: float,
        window_length: int = None
    ) -> List[Phase]:
        """Detect phases from landmark sequence."""
        pass

# Concrete implementations:
class JumpPhaseDetector(PhaseDetector):
    """Wraps existing detect_cmj_phases/detect_ground_contact."""

class RunningPhaseDetector(PhaseDetector):
    """New: Detects stance/swing from foot acceleration."""
    def detect_phases(self, landmarks, fps, **kwargs):
        # Compute foot accelerations
        # Threshold crossing = phase boundary
        # Return phases with confidence
```

**Benefits:**

- Running module doesn't touch jump code
- Each detector independently testable
- 3rd sport (throwing) adds new detector, no existing changes
- **Implementation: 200 lines, 2-3 hours**

#### Refactoring 5: Consolidate Metrics Calculators

**Current Pattern:**

```python
# dropjump/kinematics.py
def calculate_drop_jump_metrics(contact_states, vertical_positions, fps, ...) -> DropJumpMetrics:

# cmj/kinematics.py
def calculate_cmj_metrics(vertical_positions, velocities, ...) -> CMJMetrics:

# These will triple with running/kinematics.py
```

**Refactored Design:**

```python
# core/metrics.py
class MetricsCalculator(ABC):
    @abstractmethod
    def calculate_metrics(self, phases: List[Phase], **kwargs) -> Metrics:
        """Calculate metrics from phases."""
        pass

# Concrete implementations in sport modules:
# dropjump/kinematics.py:
class DropJumpMetricsCalculator(MetricsCalculator):
    def calculate_metrics(self, phases, vertical_positions, fps):
        # Existing logic
        return DropJumpMetrics(...)

# running/kinematics.py:
class RunningMetricsCalculator(MetricsCalculator):
    def calculate_metrics(self, phases, vertical_positions, fps):
        # New logic
        return RunningMetrics(...)
```

**Benefits:**

- Metrics calculators follow consistent interface
- MotionAnalyzer doesn't need to know implementation details
- **Implementation: 100 lines, 1-2 hours**

### 2.3 Refactoring Timeline

**Total Effort: 5-6 days (4 developers parallel, 1.5 days sequentially)**

```
Day 1: Refactor 1-3 (StreamingPoseProcessor, MotionAnalyzer, api.py consolidation)
       - 200 lines StreamingPoseProcessor
       - 150 lines MotionAnalyzer abstraction
       - 200 lines api.py consolidation
       - Total: ~550 lines new + refactored

Day 2: Tests for refactored code
       - Async test fixtures
       - Mock frame streams
       - Coverage verification

Days 3-4: Refactor 4-5 (Phase detection, metrics calculator abstractions)
       - 200 lines phase detection abstraction
       - 100 lines metrics calculator abstraction
       - Move existing logic to concrete classes

Day 5: Integration testing + verification
       - Ensure existing CLI works unchanged
       - Run full test suite
       - Duplication check (must stay <3%)
       - Performance baseline (no regression)

Risk: LOW if done sequentially, can parallelize with integration testing
```

### 2.4 Code Quality Impact

**Before Refactoring:**

- Duplication: 2.96% (excellent)
- Coverage: 74.27% (good)
- Type errors: 0 (Pyright strict)

**After Refactoring:**

- Duplication: ~2.5% (improved - eliminated process\_\*\_video duplication)
- Coverage: 73-75% (maintained with new tests)
- Type errors: 0 (maintained)

**Impact on Tasks 3-5:**

- Task 3 (Real-Time): Can reuse refactored streaming components
- Task 4 (Running): Add ~400 lines, duplication stays \<3%
- Task 5 (APIs): New code, doesn't touch existing modules

______________________________________________________________________

## Part 3: Technical Debt & Blockers

### 3.1 Critical Blockers (Must Fix Before Task 3)

| Issue                          | Severity | Fix                            | Effort    | Timeline |
| ------------------------------ | -------- | ------------------------------ | --------- | -------- |
| Video I/O coupling             | CRITICAL | Extract StreamingPoseProcessor | 80 lines  | 2 hours  |
| No async support               | CRITICAL | Async refactor + lifespan      | 100 lines | 2 hours  |
| In-memory frame storage        | CRITICAL | Implement ring buffer          | 50 lines  | 1 hour   |
| Process\_\*\_video duplication | HIGH     | Extract generic pattern        | 200 lines | 2 hours  |
| No WebSocket infrastructure    | CRITICAL | FastAPI WebSocket module       | 200 lines | 3 hours  |

#### Total: 10 hours (1.25 days)

### 3.2 High Priority (Should Fix Before Task 4)

| Issue                    | Severity | Fix                       | Effort    | Timeline |
| ------------------------ | -------- | ------------------------- | --------- | -------- |
| Phase detection coupling | HIGH     | Extract PhaseDetector ABC | 200 lines | 3 hours  |
| Metrics calc isolation   | HIGH     | Generic MetricsCalculator | 100 lines | 2 hours  |
| CLI pattern duplication  | MEDIUM   | Extract CLI generator     | 150 lines | 2 hours  |
| No rate limiting         | MEDIUM   | Redis middleware          | 100 lines | 2 hours  |

**Total: 9 hours (1.1 days)**

### 3.3 Current Architectural Strengths (Preserve)

- Modular structure (core + sports modules): KEEP
- Type safety (Pyright strict): MAINTAIN
- Test coverage (74%): MAINTAIN >70%
- Batch processing (ProcessPoolExecutor): KEEP for compatibility

______________________________________________________________________

## Part 4: API Design for Extensibility

### 4.1 RESTful API Structure (Sport-Agnostic)

**Design Principle:** Sport is a parameter, not a path

```
POST /api/v1/analyses
  Create batch or real-time analysis
  {
    "sport_type": "cmj|dropjump|running",
    "input": {
      "video_path": "s3://...", OR
      "streaming": true  # WebSocket upgrade
    },
    "quality": "fast|balanced|accurate",
    "config": {
      "smoothing_window": 5,
      "velocity_threshold": 0.05
    },
    "webhook_url": "https://..."  # optional
  }
  Response: {
    "analysis_id": "uuid-123",
    "status": "queued",
    "sport_type": "cmj",
    "rtc_url": "wss://..."  # if streaming=true
  }

GET /api/v1/analyses/{analysis_id}
  Get analysis results
  Response: {
    "analysis_id": "uuid-123",
    "status": "completed",
    "metrics": {...},
    "metadata": {...}
  }

GET /api/v1/analyses/{analysis_id}/stream
  WebSocket upgrade for live updates
  Message format: {
    "type": "metric_update|analysis_complete|error",
    "timestamp_ms": 12345,
    "data": {...}
  }

GET /api/v1/sports
  List supported sports
  Response: [{
    "name": "cmj",
    "display_name": "Counter Movement Jump",
    "metrics": ["jump_height", "flight_time", ...],
    "model_version": "v0.28.0",
    "requires_lateral_view": true
  }]

POST /api/v1/webhooks/register
  Register webhook listener
  {
    "url": "https://myapp.com/webhooks",
    "events": ["analysis_complete", "metric_update"],
    "sport_types": ["cmj", "running"]  # filter
  }
```

### 4.2 Webhook Event Schema (Standardized)

```python
class WebhookEvent(TypedDict):
    """Standardized webhook payload."""
    event_id: str  # UUID for idempotency
    timestamp_iso: str  # ISO 8601
    event_type: str  # "metric_update", "analysis_complete", "error"
    analysis_id: str
    sport_type: str

class MetricUpdateEvent(WebhookEvent):
    """Real-time metric updates."""
    frame_number: int
    metrics: dict  # Current frame metrics
    confidence: float

class AnalysisCompleteEvent(WebhookEvent):
    """Final analysis results."""
    metrics: dict  # Aggregated
    metadata: dict
    duration_ms: float
```

**Delivery Guarantees:**

- At-least-once delivery with exponential backoff (up to 24 hours)
- Event idempotency: Third-party deduplicates on event_id
- Retry: 1s → 2s → 4s → 8s → 15m → hourly → daily

### 4.3 SDK Examples (Python)

```python
from kinemotion import KinomotioncClient

# Initialize client
client = KinomotioncClient(
    api_key="sk_live_...",
    base_url="https://api.kinemotion.io"
)

# Batch analysis
analysis = client.create_analysis(
    video_path="s3://my-bucket/athlete.mp4",
    sport_type="cmj",
    quality="balanced",
    webhook_url="https://myapp.com/webhooks/cmj"
)

# Poll for completion
while True:
    status = client.get_analysis(analysis.analysis_id)
    if status.status == "completed":
        print(f"Jump height: {status.metrics['jump_height']:.3f}m")
        break
    time.sleep(1)

# Real-time streaming
async def on_metric_update(metrics):
    print(f"Live: {metrics['jump_height']:.3f}m at frame {metrics['frame_number']}")

async with client.stream_analysis(
    video_path="video.mp4",
    sport_type="cmj",
    on_update=on_metric_update
) as stream:
    results = await stream.wait()
```

### 4.4 Integration Examples (Task 5 Deliverables)

#### Integration 1: Coaching App (Vimeo Coach)

```python
# Webhook receives CMJ metrics
@app.post("/webhooks/kinemotion")
async def on_analysis_complete(event: AnalysisCompleteEvent):
    # Extract jump height, RSI, etc.
    athlete_id = extract_from_video_path(event.metadata["source"])

    # Store in Vimeo Coach
    vimeo_coach_api.update_athlete_metrics(
        athlete_id=athlete_id,
        metrics={
            "jump_height_m": event.metrics["jump_height"],
            "reactive_strength_index": event.metrics["rsi"],
            "test_date": event.timestamp_iso
        }
    )
```

**Integration 2: Wearable Sync (Oura)**

```python
# Combine kinemotion metrics with Oura recovery data
async def correlate_jump_recovery():
    cmj_metrics = await kinemotion_client.get_analysis(analysis_id)

    oura_data = oura_api.get_recovery(
        date=cmj_metrics.metadata["timestamp"],
        metrics=["heart_rate_variability", "recovery_index"]
    )

    # Store correlation for coaching
    store_athlete_profile({
        "jump_metrics": cmj_metrics.metrics,
        "recovery_metrics": oura_data,
        "recommended_action": determine_training_load(
            cmj_metrics, oura_data
        )
    })
```

#### Integration 3: Team Dashboard (TeamSnap)

```python
# Batch analyze team roster
team_members = teamsnap_api.get_roster(team_id)

tasks = [
    kinemotion_client.create_analysis(
        video_path=f"s3://team-videos/{member.id}.mp4",
        sport_type="cmj",
        webhook_url=f"https://myapp.com/webhooks/cmj/{member.id}"
    )
    for member in team_members
]

await asyncio.gather(*tasks)
# Results aggregated and displayed on team dashboard
```

### 4.5 Rate Limiting Strategy

**Freemium Tier:**

- 1,000 analyses/month
- 1 concurrent stream
- 1 integration (webhook)
- Free

**Pro Tier ($99/month):**

- 50,000 analyses/month
- 5 concurrent streams
- 5 integrations
- Priority support

**Enterprise (Custom):**

- Unlimited
- Custom SLA
- Dedicated inference tier
- Custom integration support

**Implementation:**

```python
# Redis-backed sliding window counter
async def check_rate_limit(api_key: str, limit: int, window_s: int = 3600):
    """Check if request within rate limit."""
    key = f"rate_limit:{api_key}"
    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, window_s)
    return current <= limit
```

______________________________________________________________________

## Part 5: Risk Assessment & Mitigation

### 5.1 Architectural Risks

| Risk                                        | Likelihood | Impact                        | Mitigation                                          |
| ------------------------------------------- | ---------- | ----------------------------- | --------------------------------------------------- |
| Real-time latency exceeds 200ms             | MEDIUM     | Loss of coaching feature      | Performance profiling Week 1 Task 3; fallback 250ms |
| Multi-sport abstraction too restrictive     | LOW        | Refactoring pain for sport 4+ | Phase detector well-designed; can extend if needed  |
| Scale to 100+ requires unexpected resources | HIGH       | Higher infra costs            | MVP single-server, add tier on demand               |
| Code duplication spirals to 5%+             | MEDIUM     | Technical debt                | Enforce refactor before Task 4; budget 1 week       |
| Async/streaming code untestable             | MEDIUM     | Regression bugs               | Invest in async fixtures early; min 70% coverage    |
| Third-party API contracts break             | MEDIUM     | Integration failures          | Semantic versioning, early partner testing          |

### 5.2 Execution Risks

| Risk                                         | Likelihood | Impact                | Mitigation                                        |
| -------------------------------------------- | ---------- | --------------------- | ------------------------------------------------- |
| Real-time adds scope creep                   | MEDIUM     | Timeline slips        | Scope to Drop Jump only; add CMJ in Month 2       |
| Refactoring takes longer than estimated      | MEDIUM     | Delays Task 3         | 1-2 days buffer; refactor iteratively             |
| MediaPipe GPU bottleneck worse than expected | MEDIUM     | Scale timeline pushed | Early testing Week 1 Task 3; have fallback plans  |
| Redis dependency adds operational complexity | MEDIUM     | DevOps burden         | Docker Compose for dev; managed Redis for prod    |
| Team unfamiliar with async patterns          | MEDIUM     | Code quality issues   | Early training; pair programming first async code |

### 5.3 Market Risks

| Risk                                    | Likelihood | Impact               | Mitigation                                                 |
| --------------------------------------- | ---------- | -------------------- | ---------------------------------------------------------- |
| Competitor releases similar feature     | MEDIUM     | Differentiation lost | First-mover advantage; 3-4 month launch window             |
| Coach adoption slower than expected     | MEDIUM     | Revenue delay        | Beta program with 10-20 coaches; free tier                 |
| Running gait analysis proves inaccurate | MEDIUM     | Product credibility  | Validation against published research; conservative launch |

______________________________________________________________________

## Part 6: Recommendations & Next Steps

### 6.1 IMMEDIATE (This Week)

1. **Create Refactoring Design Document**

   - Detailed specs for StreamingPoseProcessor, MotionAnalyzer abstractions
   - Sequence refactorings to minimize risk
   - Assign code reviewers

1. **Set Up Performance Profiling Infrastructure**

   - Benchmark: Single-stream latency baseline (should be \<500ms current)
   - Profiling: Frame-by-frame timing breakdown
   - Target: \<200ms E2E after refactoring

1. **Reserve 5-6 Days for Refactoring**

   - Before Task 3 starts, complete critical refactorings
   - Schedule: Weeks 1-2 (parallel with Task 2 CMJ tests)
   - Budget: 1 senior developer full-time

### 6.2 BEFORE TASK 3 (Weeks 1-2)

1. **Execute Critical Refactorings (4-5 days)**

   - ✓ Extract StreamingPoseProcessor
   - ✓ Create MotionAnalyzer abstraction
   - ✓ Consolidate api.py
   - ✓ Add ring buffer implementation
   - ✓ Basic WebSocket infrastructure module

1. **Performance Validation**

   - Single-stream latency: Target \<200ms
   - Memory usage: \<300MB per stream
   - CPU usage: \<50% on single core (room for scaling)

1. **API Design Finalization**

   - OpenAPI spec for Task 5 kickoff
   - Webhook schema definition
   - SDK interface design

### 6.3 BEFORE TASK 4 (Week 4)

1. **Extract Phase Detection Abstraction**

   - PhaseDetector ABC with concrete implementations
   - Move jump phase logic to JumpPhaseDetector
   - Create RunningPhaseDetector stub

1. **Consolidate Metrics Calculators**

   - MetricsCalculator ABC
   - Move existing logic to concrete classes
   - Generic interface for Task 4 use

1. **Verify Duplication**

   - Run npx jscpd: Target \<3%
   - Should be ~2.5% after refactoring

### 6.4 Code Quality Standards (Maintain Throughout)

- **Type Safety:** Pyright strict (0 errors)
- **Coverage:** >70% (currently 74%)
- **Duplication:** \<3% (currently 2.96%)
- **Linting:** Ruff (0 errors)
- **Documentation:** Docstrings for public APIs

### 6.5 Build Strategy (Preserve Quality as Scope Grows)

1. **Limit MVP Scope**

   - Real-time for Drop Jump only (CMJ in Month 2)
   - Reduces complexity, enables faster iteration

1. **Aggressive Refactoring**

   - Extract early, often
   - Don't wait for duplication to hit 5%

1. **Testing Discipline**

   - Async code especially needs coverage
   - Mock external dependencies (Redis, WebSocket)
   - Integration tests for critical paths

1. **Type Safety**

   - Keep Pyright strict
   - Catches interface mismatches early

______________________________________________________________________

## Part 7: Success Criteria

### 7.1 Architecture Validation

- [ ] WebSocket connection established \<1s
- [ ] Single-stream E2E latency \<200ms (P95)
- [ ] Frame buffer memory constant (ring buffer working)
- [ ] 5+ concurrent streams stable on single GPU

### 7.2 Code Quality Validation

- [ ] Duplication: \<3% (no regression from 2.96%)
- [ ] Coverage: >70% (maintain 74%)
- [ ] Type errors: 0 (Pyright strict)
- [ ] All tests passing (261 tests)

### 7.3 Extensibility Validation

- [ ] Running gait analyzer added with \<400 lines
- [ ] Duplication stays \<3% with 3 sports
- [ ] Phase detection abstraction reusable

### 7.4 API Validation

- [ ] OpenAPI spec generated automatically
- [ ] 3 integration examples working
- [ ] Rate limiting enforced
- [ ] Webhook delivery verified

______________________________________________________________________

## Conclusion

**The architecture is SOUND and EXECUTABLE.** The roadmap is ambitious but realistic. The main challenge is not technical complexity but maintaining code quality discipline as scope expands.

### Key Takeaways

1. **WebSocket + FastAPI:** Production-ready for real-time analysis
1. **Refactoring First:** 5-6 days upfront saves 2-3 weeks downstream
1. **Phase Detection Abstraction:** Enables multi-sport without duplication
1. **Scaling Strategy:** MVP single-server, grow incrementally as demand requires
1. **Code Quality:** Must enforce \<3% duplication before Task 4

With disciplined execution of planned refactorings and architectural abstractions, Kinemotion can achieve:

- ✓ Real-time capability without sacrificing accuracy
- ✓ Multi-sport extensibility without code duplication
- ✓ Scalability from 5 to 100+ concurrent streams
- ✓ Third-party integrations through clean APIs
- ✓ Code quality maintenance (\<3% duplication, >70% coverage)

**Timeline: 6 weeks to MVP (real-time + running + APIs) achievable with 4-5 developers and disciplined execution.**

______________________________________________________________________

**Document Status:** Ready for Review
**Recommended Next Action:** Stakeholder Sign-off on Refactoring Plan
**Timeline to Execution:** This Week
