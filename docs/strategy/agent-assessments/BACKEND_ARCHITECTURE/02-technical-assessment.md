# Backend Architecture Assessment

## Real-Time, Multi-Sport, & API Scalability

**Date:** November 17, 2025
**Assessment Scope:** Tasks 3, 4, 5 (Real-Time Web, Running Gait, API Integration)
**Prepared by:** Python Backend Developer

______________________________________________________________________

## Executive Summary

**Verdict: ARCHITECTURE IS SOUND AND EXECUTABLE**

The proposed roadmap (real-time WebSocket analysis, multi-sport support, ecosystem APIs) is technically feasible and strategically sound. However, **critical refactoring is required before implementation** to maintain code quality and enable extensibility.

### Key Findings

| Finding                           | Status                  | Impact                                              |
| --------------------------------- | ----------------------- | --------------------------------------------------- |
| WebSocket + FastAPI for real-time | ✅ APPROVED             | Proven patterns, \<200ms latency achievable         |
| Single-server capacity (MVP)      | ✅ 5-10 streams         | Sufficient for Q1 launch                            |
| Multi-sport abstraction design    | ✅ SOUND                | Enables running + future sports without duplication |
| Code quality preservation         | ⚠️ REQUIRES REFACTORING | Must extract abstractions before Task 4             |
| Scaling to 100+ concurrent        | ✅ VIABLE               | Requires distributed inference tier (Month 6+)      |

### Recommendations (Prioritized)

1. **IMMEDIATE:** Execute 5-6 day refactoring sprint (BEFORE Task 3)

   - Extract streaming infrastructure (StreamingPoseProcessor)
   - Create MotionAnalyzer abstraction base class
   - Consolidate api.py (eliminate 40% duplication)
   - **Payoff:** Unblocks real-time, running, APIs without quality regression

1. **BEFORE Task 4:** Extract phase detection abstraction

   - Running gait will add new PhaseDetector implementation
   - Prevents duplication spike (2.96% → 5.5%)

1. **PARALLEL with Task 3:** Design API surface (OpenAPI spec, webhooks)

   - Sport-agnostic endpoints (sport_type parameter, not path)
   - Standardized webhook events
   - Rate limiting strategy

### Risk Assessment

| Risk                      | Likelihood | Mitigation                                               |
| ------------------------- | ---------- | -------------------------------------------------------- |
| Latency exceeds 200ms     | MEDIUM     | Early profiling Week 1; fallback 250ms acceptable        |
| Code duplication spirals  | MEDIUM     | Enforce refactoring before Task 4 (mandatory)            |
| Scale bottleneck appears  | MEDIUM     | MVP single-server; add infrastructure as demand requires |
| Async code quality issues | MEDIUM     | Invest in async fixtures + min 70% coverage              |

______________________________________________________________________

## Architectural Assessment

### 1. Real-Time WebSocket Architecture

**Status: PRODUCTION-READY**

#### Why This Architecture Works

**Proven Patterns:**

- Redis Pub/Sub for multi-instance coordination (distributed)
- Connection managers for state tracking (reliable)
- Heartbeat mechanisms for stale detection (maintainable)
- Async/await throughout (modern Python)

**Latency Budget (\<200ms achievable):**

```
Capture:      33ms (30fps camera)
Network:      50ms (LAN/5G)
Processing:   50ms (MediaPipe GPU-accelerated)
Metrics:      10ms (NumPy vectorized)
Render:       33ms (browser)
─────────────────────────────
TOTAL:       ~166ms ✓ (within budget)
```

#### Architecture Components

```
Client (Browser)
  ├─ WebRTC capture (H.264, 30fps, 360p = 2Mbps)
  ├─ WebSocket to API tier
  └─ Real-time metric updates

API Tier (FastAPI, stateless, scales horizontally)
  ├─ WebSocket connection manager
  ├─ Frame queuing → Redis
  ├─ Metrics calculation (lightweight)
  ├─ State management → Redis
  ├─ Pub/Sub → Redis for dashboards
  └─ Webhook delivery

Inference Tier (separate GPU workers)
  ├─ MediaPipe pose detection
  ├─ Frame queue consumption from Redis
  ├─ Result publishing back to API tier
  └─ Auto-scaling on queue depth

Data Tier
  ├─ Redis (connection state, queues, Pub/Sub)
  ├─ TimescaleDB (optional, metrics history)
  └─ S3 (optional, video recordings)
```

### 2. Performance at Scale

#### Single-Server Capacity (MVP Phase)

| Hardware     | Concurrent Streams | Latency P95 | Bottleneck          |
| ------------ | ------------------ | ----------- | ------------------- |
| CPU only     | 1-2                | 800ms+      | MediaPipe inference |
| GPU RTX 3080 | 5-10               | 150-200ms   | GPU memory          |
| GPU RTX A100 | 15-20              | 100-150ms   | CPU→GPU throughput  |

**MVP Target:** 5-10 concurrent streams, single GPU server

#### Performance Bottleneck Hierarchy

1. **INFERENCE (50-80% of latency)**

   - MediaPipe: 25-50ms per frame
   - Solution: Frame batching OR separate inference tier
   - Optimization: TensorRT (3-5x faster), Lite model (2x faster)

1. **MEMORY (prevents scaling beyond 20-30 concurrent)**

   - Per connection: ~80MB (frame buffer + poses)
   - Solution: Ring buffers (fixed size), stream to database

1. **NETWORK (10-50ms, depends on bandwidth)**

   - Per stream: 4-8 Mbps uncompressed
   - Solution: H.264 compression (25x reduction)

1. **STATE MANAGEMENT (operational at scale)**

   - 100 in-memory dicts = slow lookups
   - Solution: Redis (fast, distributed)

#### Scaling Timeline

**MVP (Weeks 3-6):** Single server, 5-10 concurrent
**Growth (Month 6-9):** Distributed inference, 50-100 concurrent
**Enterprise (Year 1+):** Multi-region, 1000+ concurrent

### 3. Current Codebase: Readiness Assessment

#### Strengths

✅ Modular architecture (core + sport-specific)
✅ High code quality (74% coverage, 2.96% duplication, Pyright strict)
✅ Type-safe foundations (TypedDict, NDArray types)
✅ Batch processing pattern proven (ProcessPoolExecutor)

#### Weaknesses (BLOCKING Real-Time)

❌ Tightly coupled video I/O (can't accept frame stream)
❌ No streaming pose processor (frame-by-frame)
❌ No async/await support (WebSocket requires)
❌ Metrics calculation requires entire array in memory
❌ 40% code duplication between process_dropjump and process_cmj

#### Refactoring Priority: **CRITICAL (Must do BEFORE Task 3)**

______________________________________________________________________

## Refactoring Strategy (Critical Path)

### Why Refactoring First?

**If we don't refactor:**

- Task 3 (real-time): Blocked by tight coupling, 2-3 week delay
- Task 4 (running): Code duplication spikes to 5%+, technical debt
- Task 5 (APIs): Multiple code paths to maintain, brittleness

**With refactoring:**

- Task 3: Unblocked, can reuse streaming components
- Task 4: Clean addition, duplication stays \<3%
- Task 5: Single API path, maintainable integrations

### Five-Day Refactoring Roadmap

**Total Effort:** 5-6 days (1 senior developer, could parallelize with Task 2)

#### Day 1: Extract Streaming Infrastructure

**New File:** `core/streaming.py` (80 lines)

- RingBuffer class (fixed-size, reusable for any smoothing)
- StreamingPoseProcessor class (frame-by-frame, no file I/O)

**Benefit:** Enables WebSocket intake, constant memory

#### Days 1-2: Extract MotionAnalyzer Base Class

**New File:** `core/analysis.py` (150 lines)

- MotionAnalyzer ABC (generic pipeline)
- CMJAnalyzer, DropJumpAnalyzer concrete implementations

**Benefit:** Eliminates process_dropjump_video / process_cmj_video duplication (700+ lines)

#### Day 2: Consolidate api.py

**Refactored:** `api.py` (1150 → 450 lines)

- Single processing logic: process_video_streaming()
- Backward-compatible batch API (unchanged externally)
- New real-time API for Task 3

**Benefit:** 700 lines eliminated, single code path

#### Days 3-4: Extract Phase Detection Abstraction

**New File:** `core/phase_detection.py` (200 lines)

- Phase TypedDict (generic representation)
- PhaseDetector ABC (framework for all sports)
- JumpPhaseDetector, RunningPhaseDetector implementations

**Benefit:** Running doesn't touch jump code, future-proof

#### Days 4-5: Consolidate Metrics Calculators & Testing

**New File:** `core/metrics.py` (100 lines)

- MetricsCalculator ABC
- Move existing implementations to concrete classes

**Benefit:** Enables Task 4 without quality regression

### Code Quality Impact

**Before Refactoring:**

- Duplication: 2.96% (excellent)
- Coverage: 74.27% (good)
- Type errors: 0 (excellent)

**After Refactoring:**

- Duplication: ~2.5% (improved)
- Coverage: 73-75% (maintained)
- Type errors: 0 (maintained)

______________________________________________________________________

## Multi-Sport Extensibility Design

### Phase Detection Abstraction

**Problem:** Each sport has different phase patterns

- Jump: Contact/flight (event-based)
- Running: Stance/swing (cyclic)
- Throwing: Windup/acceleration/deceleration (kinetic chain)

**Solution:** Generic PhaseDetector interface, sport-specific implementations

```python
class PhaseDetector(ABC):
    def detect_phases(self, landmarks, fps, **kwargs) -> List[Phase]:
        """Detect motion phases from landmarks."""
        pass

class Phase(TypedDict):
    start_frame: int
    end_frame: int
    phase_type: str  # "contact", "flight", "stance", etc.
    confidence: float
```

**Benefits:**

- Running adds new PhaseDetector, doesn't touch jump code
- Each detector independently testable
- Future sport (throwing) adds detector, not changes
- Duplication stays \<3%

### Metrics Calculator Pattern

Similar abstraction:

```python
class MetricsCalculator(ABC):
    def calculate_metrics(self, phases, vertical_positions, fps, **kwargs) -> dict:
        """Calculate sport-specific metrics."""
        pass
```

**Benefits:**

- Consistent interface across sports
- MotionAnalyzer doesn't need sport-specific logic
- Easy to add new sports

______________________________________________________________________

## API Design for Extensibility

### RESTful Endpoints (Sport-Agnostic)

**Design Principle:** Sport is a parameter, not a path

```
POST /api/v1/analyses
  Create batch or real-time analysis
  Body: {sport_type: "cmj|dropjump|running", ...}

GET /api/v1/analyses/{analysis_id}
  Get results

GET /api/v1/analyses/{analysis_id}/stream
  WebSocket upgrade for live metrics

GET /api/v1/sports
  List supported sports with capabilities

POST /api/v1/webhooks/register
  Register webhook listener
```

### Webhook Events (Standardized)

```python
# MetricUpdate event (real-time)
{
  "event_id": "evt_123",
  "timestamp_iso": "2025-11-17T10:30:45Z",
  "event_type": "metric_update",
  "analysis_id": "ana_456",
  "sport_type": "cmj",
  "frame_number": 45,
  "metrics": {"jump_height": 0.42, ...},
  "confidence": 0.95
}

# AnalysisComplete event (final results)
{
  "event_id": "evt_789",
  "timestamp_iso": "...",
  "event_type": "analysis_complete",
  "analysis_id": "ana_456",
  "sport_type": "cmj",
  "metrics": {...},  # Aggregated
  "duration_ms": 2450
}
```

### Integration Examples (Task 5 Deliverables)

1. **Coaching App Integration (Vimeo Coach)**

   - Webhook receives CMJ metrics
   - Post to Vimeo Coach athlete dashboard
   - Store metrics + trends

1. **Wearable Sync (Oura + Kinemotion)**

   - Combine jump metrics with recovery data
   - Correlate performance with HRV
   - Coaching recommendations

1. **Team Dashboard (TeamSnap Integration)**

   - Batch analyze team roster
   - Compare athlete metrics
   - Export reports

### Rate Limiting & SDKs

**Pricing Tiers:**

- Free: 1,000 analyses/month, 1 concurrent stream
- Pro: 50,000/month, 5 concurrent streams, $99/month
- Enterprise: Unlimited, custom SLA

**SDKs (Python + JavaScript):**

```python
client = KinomotioncClient(api_key="sk_...", base_url="https://api.kinemotion.io")
analysis = await client.analyze_video("video.mp4", sport_type="cmj")
```

______________________________________________________________________

## Risk Assessment & Mitigation

### Architectural Risks

| Risk                                    | Likelihood | Impact                   | Mitigation                                       |
| --------------------------------------- | ---------- | ------------------------ | ------------------------------------------------ |
| Latency exceeds 200ms                   | MEDIUM     | Loss of coaching feature | Performance profiling Week 1; fallback 250ms     |
| Multi-sport abstraction too restrictive | LOW        | Refactoring pain         | Design well-proven; can extend if needed         |
| Scale to 100+ requires more resources   | HIGH       | Infra costs              | MVP single-server, scale incrementally           |
| Code duplication spirals to 5%+         | MEDIUM     | Technical debt           | ENFORCE refactoring before Task 4                |
| Async code untestable                   | MEDIUM     | Regression bugs          | Invest in async fixtures early; min 70% coverage |

### Execution Risks

| Risk                              | Likelihood | Impact         | Mitigation                               |
| --------------------------------- | ---------- | -------------- | ---------------------------------------- |
| Refactoring takes longer          | MEDIUM     | Task 3 delays  | 1-2 day buffer; refactor iteratively     |
| MediaPipe bottleneck worse        | MEDIUM     | Scale timeline | Early testing Week 1 Task 3              |
| Redis adds operational complexity | MEDIUM     | DevOps burden  | Docker Compose local; managed Redis prod |
| Team unfamiliar with async        | MEDIUM     | Code quality   | Early training; pair programming         |
| Real-time scope creep             | MEDIUM     | Timeline slips | Limit to Drop Jump MVP; CMJ Month 2      |

______________________________________________________________________

## Timeline & Success Criteria

### Refactoring Phase (This Week - Days 1-2 Week 1)

- ✓ Extract StreamingPoseProcessor + MotionAnalyzer
- ✓ Consolidate api.py
- ✓ All tests passing, duplication \<3%
- ✓ Performance baseline established

### Task 3 Phase (Weeks 3-6)

- ✓ WebSocket infrastructure
- ✓ Real-time metric streaming
- ✓ \<200ms E2E latency achieved
- ✓ 5+ concurrent streams stable

### Task 4 Phase (Week 5-7, parallel)

- ✓ Phase detection abstraction extracted
- ✓ Running gait analyzer implemented
- ✓ Duplication stays \<3%
- ✓ 3 sports (CMJ, DJump, Running) supported

### Task 5 Phase (Weeks 2-7, parallel)

- ✓ OpenAPI spec auto-generated
- ✓ 3 integration examples working
- ✓ Rate limiting enforced
- ✓ Webhook delivery verified

### Success Criteria

**Architecture:**

- [ ] WebSocket connection \<1s
- [ ] Single-stream latency \<200ms (P95)
- [ ] 5+ concurrent streams stable
- [ ] Ring buffer memory constant

**Code Quality:**

- [ ] Duplication: \<3%
- [ ] Coverage: >70%
- [ ] Type errors: 0
- [ ] All 261 tests passing

**Extensibility:**

- [ ] Running gait added with \<400 lines
- [ ] New sport doesn't increase duplication
- [ ] Phase detection reusable across sports

______________________________________________________________________

## Conclusion

**The architecture is SOUND and EXECUTABLE.**

### Key Takeaways

1. **WebSocket + FastAPI:** Production-ready for real-time (\<200ms latency)
1. **Refactoring First:** 5-6 days upfront saves 2-3 weeks downstream and maintains code quality
1. **Phase Detection Abstraction:** Enables multi-sport without duplication
1. **Scaling Strategy:** MVP single-server (5-10 concurrent), grow incrementally to 100+
1. **Code Quality:** Must enforce \<3% duplication discipline before Task 4

### Recommended Next Steps

**THIS WEEK:**

1. Stakeholder sign-off on refactoring plan
1. Reserve 5-6 days for refactoring sprint
1. Start performance profiling infrastructure

**WEEK 1:**

1. Execute critical refactorings (Days 1-2)
1. Performance validation (Day 3)
1. API design finalization (parallel)

**BEFORE TASK 3:**

1. All refactorings complete
1. WebSocket infrastructure ready
1. Real-time demo working

______________________________________________________________________

**Prepared by:** Python Backend Developer
**Date:** November 17, 2025
**Status:** Ready for Review & Execution
**Next Action:** Stakeholder Sign-off on Refactoring Plan

**Detailed Analysis:** See `architecture/Backend Architecture Assessment - Real-Time & Multi-Sport.md`
**Implementation Roadmap:** See `architecture/Refactoring Roadmap - Critical Path to Real-Time & Multi-Sport.md`
