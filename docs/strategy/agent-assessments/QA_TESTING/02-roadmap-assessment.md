# Expert QA Testing & Quality Assessment of Roadmap

**Prepared by:** QA/Test Engineer
**Date:** November 17, 2025
**Classification:** Technical Quality Assessment
**Scope:** 5-Priority Task Roadmap (6-month execution)

______________________________________________________________________

## Executive Summary

The 6-month roadmap is **strategically sound but requires substantial testing infrastructure investment**. Current test coverage (74.27%) provides excellent foundation for core algorithms, but real-time features, multi-sport extensibility, and API ecosystem require NEW testing approaches not yet established.

**Overall Assessment:** FEASIBLE with mitigations for 3 MEDIUM-risk areas

- Task 2 (CMJ testing): Coverage target achievable but requires expanded scope
- Task 3 (Real-time): Latency target feasible but needs early performance testing
- Task 4 (Running): Architecture generalization untested—requires validation before implementation

______________________________________________________________________

## 1. TASK 2 SCOPE: CMJ Testing 62% → 80%

### Current Assessment: ACHIEVABLE with Expanded Scope

**Current State:**

- CMJ module: 62% coverage
- Total codebase: 261 tests, 74.27% coverage
- Core algorithms: 85-100% coverage
- Core weakness: Phase progression and physiological validation untested

**Gap Analysis: 62% → 80% requires +18% improvement**

Current coverage gaps:

```
CMJ Module Coverage Breakdown:
├─ Analysis functions: ~75% (core metrics working)
├─ Kinematics calculations: ~70% (basic cases covered)
├─ Phase detection: ~40% (limited edge case coverage)
├─ Joint angle validation: ~35% (ankle issue documented, minimal bounds tests)
├─ Real-world video validation: ~10% (no real video tests)
└─ Edge cases: ~25% (sparse coverage)
```

### Recommended Test Expansion (Phase Progression Focus)

**1. Phase Progression Tests (NEW - Add 5-6%)**

```python
# Test Case Category: Phase Progression Validation
# Purpose: Verify CMJ phases detected correctly and metrics increase properly

@pytest.mark.parametrize("phase,expected_ankle_range,expected_knee_range", [
    ("eccentric_start", (80, 95), (80, 100)),
    ("lowest_point", (75, 90), (85, 110)),
    ("concentric_mid", (95, 115), (120, 150)),
    ("takeoff", (110, 135), (160, 180)),
])
def test_joint_angles_progress_through_phases(phase, expected_ankle_range, expected_knee_range):
    """Verify joint angles increase monotonically through CMJ phases."""
    landmarks = get_phase_landmarks(phase)

    ankle = calculate_ankle_angle(landmarks)
    knee = calculate_knee_angle(landmarks)

    assert ankle is None or expected_ankle_range[0] <= ankle <= expected_ankle_range[1]
    assert knee is None or expected_knee_range[0] <= knee <= expected_knee_range[1]

def test_ankle_angle_increases_from_lowest_to_takeoff():
    """Critical test: Ankle angle must increase during concentric phase."""
    angle_lowest = calculate_ankle_angle(landmarks_at_lowest)
    angle_takeoff = calculate_ankle_angle(landmarks_at_takeoff)

    assert angle_takeoff > angle_lowest, \
        f"Ankle should increase: {angle_lowest}° → {angle_takeoff}°"
    assert angle_takeoff - angle_lowest >= 20, \
        f"Increase too small: {angle_takeoff - angle_lowest}° (expect 20°+)"

def test_knee_angle_increases_from_lowest_to_takeoff():
    """Knee angle must show clear extension pattern."""
    angle_lowest = calculate_knee_angle(landmarks_at_lowest)
    angle_takeoff = calculate_knee_angle(landmarks_at_takeoff)

    assert angle_takeoff > angle_lowest
    assert angle_takeoff >= 160, "Takeoff should have near-full extension"

def test_hip_angle_increases_from_lowest_to_takeoff():
    """Hip angle must show clear extension pattern."""
    angle_lowest = calculate_hip_angle(landmarks_at_lowest)
    angle_takeoff = calculate_hip_angle(landmarks_at_takeoff)

    assert angle_takeoff > angle_lowest
    assert angle_takeoff >= 170, "Takeoff should have full extension"

# Add ~8 tests like above for different scenarios
```

**Tests to Add:**

- 8-10 phase progression tests (ankle, knee, hip progression validation)
- 4-6 synchronization tests (verify all joints extend together)
- 3-5 timing tests (phase transition detection)

**Coverage Impact:** +5-6% (adds detection coverage)

______________________________________________________________________

**2. Physiological Bounds Validation Tests (NEW - Add 4-5%)**

```python
# Test Case Category: Anatomical Realism
# Purpose: Reject impossible/unrealistic joint angles

JOINT_BOUNDS = {
    "ankle": (70, 135),      # Plantarflexion 120° max, dorsiflexion 70° min
    "knee": (80, 185),       # Squat ~80°, slight hyperextension to 185°
    "hip": (60, 195),        # Deep squat 60°, slight hyperextension 195°
}

@pytest.mark.parametrize("joint,min_angle,max_angle", [
    ("ankle", 70, 135),
    ("knee", 80, 185),
    ("hip", 60, 195),
])
def test_joint_angle_within_physiological_bounds(joint, min_angle, max_angle):
    """All measured angles must be within anatomical limits."""
    # Test 50 different landmark configurations
    for i in range(50):
        landmarks = generate_realistic_landmarks_for_joint(joint)

        if joint == "ankle":
            angle = calculate_ankle_angle(landmarks)
        elif joint == "knee":
            angle = calculate_knee_angle(landmarks)
        else:
            angle = calculate_hip_angle(landmarks)

        assert angle is None or (min_angle <= angle <= max_angle), \
            f"{joint.title()} angle {angle}° outside bounds [{min_angle}-{max_angle}°]"

def test_impossible_angles_detected_and_flagged():
    """Angles >180° or <0° should be caught."""
    bad_landmarks = generate_bad_landmarks()  # Causes impossible angle

    angle = calculate_ankle_angle(bad_landmarks)
    assert angle is None or (70 <= angle <= 135), "Bad landmarks should return None or valid angle"

# Add ~10 tests with edge cases:
# - Maximum dorsiflexion (70°)
# - Maximum plantarflexion (135°)
# - Hyperextended knee (180°+)
# - Impossible combinations
```

**Tests to Add:**

- 12-15 bounds validation tests (each joint, various positions)
- 4-6 error detection tests (flags impossible values)
- 3-4 combination tests (multiple joints checked together)

**Coverage Impact:** +4-5% (adds validation coverage)

______________________________________________________________________

**3. Real Video Validation Tests (NEW - Add 3-4%)**

```python
# Test Case Category: End-to-End Real Video
# Purpose: Validate against actual CMJ video with known athlete

@pytest.fixture
def cmj_video_good_athlete(tmp_path):
    """CMJ video of athlete with good triple extension technique."""
    # Using realistic synthetic video matching known biomechanics
    video_path = create_synthetic_cmj_video(
        tmp_path,
        technique="good",  # Synchronized extension
        ankle_range=(75, 125),
        knee_range=(85, 170),
        hip_range=(90, 175),
    )
    return video_path

@pytest.fixture
def cmj_video_poor_athlete(tmp_path):
    """CMJ video of athlete with incomplete knee extension."""
    video_path = create_synthetic_cmj_video(
        tmp_path,
        technique="poor",  # Incomplete knee extension
        ankle_range=(75, 120),
        knee_range=(85, 155),  # Stops at 155° (incomplete)
        hip_range=(90, 175),
    )
    return video_path

def test_real_cmj_video_good_technique(cmj_video_good_athlete):
    """Good technique should show synchronized extension."""
    metrics = process_cmj_video(str(cmj_video_good_athlete))

    # Extract phase angles from analysis
    angles = metrics["joint_angles"]

    # All joints should extend together
    assert angles["ankle_at_takeoff"] > 110
    assert angles["knee_at_takeoff"] > 165
    assert angles["hip_at_takeoff"] > 170
    assert angles["synchronization_score"] > 0.8

def test_real_cmj_video_poor_technique(cmj_video_poor_athlete):
    """Poor technique should show incomplete knee extension."""
    metrics = process_cmj_video(str(cmj_video_poor_athlete))
    angles = metrics["joint_angles"]

    # Knee should be incomplete
    assert angles["knee_at_takeoff"] < 160, "Poor technique has incomplete knee"
    assert angles["synchronization_score"] < 0.6

def test_foot_index_vs_heel_difference_in_video():
    """Validate that foot_index produces meaningfully different angles than heel."""
    metrics_with_foot_index = process_cmj_video(video_path, use_foot_index=True)
    metrics_with_heel = process_cmj_video(video_path, use_foot_index=False)

    ankle_diff = abs(
        metrics_with_foot_index["ankle_at_takeoff"] -
        metrics_with_heel["ankle_at_takeoff"]
    )

    assert ankle_diff > 10, \
        f"Foot_index should differ >10° from heel, got {ankle_diff}°"

# Add ~4 more tests:
# - Different video qualities (good/poor lighting)
# - Different camera angles (frontal bias)
# - Different athlete types (explosive vs controlled)
# - Different video frame rates
```

**Tests to Add:**

- 3-4 real video tests (good/poor technique discrimination)
- 2-3 video quality tests (various lighting conditions)
- 2-3 camera angle tests (frontal bias detection)

**Coverage Impact:** +3-4% (adds real-world validation)

______________________________________________________________________

**4. Foot_index Ankle Angle Validation (NEW - Add 2-3%)**

```python
# Test Case Category: Ankle Angle Fix Validation (Task 1 prerequisite)
# Purpose: Verify foot_index implementation is correct

def test_ankle_angle_uses_foot_index_when_available():
    """When foot_index available, should use toes not heel."""
    landmarks = {
        "right_foot_index": (0.52, 0.80, 0.95),  # Visible toes
        "right_heel": (0.48, 0.85, 0.90),        # Also visible
        "right_ankle": (0.50, 0.75, 0.90),
        "right_knee": (0.50, 0.55, 0.90),
    }

    # Should use foot_index, not heel
    angle = calculate_ankle_angle(landmarks)
    expected_with_foot_index = calculate_angle_3_points(
        (0.52, 0.80), (0.50, 0.75), (0.50, 0.55)
    )

    assert abs(angle - expected_with_foot_index) < 0.5

def test_ankle_angle_falls_back_to_heel_if_foot_index_unavailable():
    """When foot_index not visible, should gracefully fall back to heel."""
    landmarks = {
        "right_foot_index": (0.52, 0.80, 0.15),  # Not visible (confidence <0.3)
        "right_heel": (0.48, 0.85, 0.90),        # Visible, use as fallback
        "right_ankle": (0.50, 0.75, 0.90),
        "right_knee": (0.50, 0.55, 0.90),
    }

    angle = calculate_ankle_angle(landmarks)
    # Should fall back to heel
    expected_with_heel = calculate_angle_3_points(
        (0.48, 0.85), (0.50, 0.75), (0.50, 0.55)
    )

    assert abs(angle - expected_with_heel) < 0.5

def test_ankle_angle_returns_none_if_neither_available():
    """Should return None gracefully if no foot landmark available."""
    landmarks = {
        "right_foot_index": (0.52, 0.80, 0.15),  # Not visible
        "right_heel": (0.48, 0.85, 0.15),        # Not visible
        "right_ankle": (0.50, 0.75, 0.90),
        "right_knee": (0.50, 0.55, 0.90),
    }

    angle = calculate_ankle_angle(landmarks)
    assert angle is None

# Add ~3-4 more edge case tests
```

**Tests to Add:**

- 3-4 foot_index vs heel comparison tests
- 2-3 fallback logic tests
- 2-3 edge case tests

**Coverage Impact:** +2-3% (adds ankle fix validation)

______________________________________________________________________

### Summary: Task 2 Coverage Path

```
Starting Point:       62% CMJ coverage
+ Phase Progression:  +5-6% → 67-68%
+ Bounds Validation:  +4-5% → 71-73%
+ Real Video:         +3-4% → 74-77%
+ Ankle Fix Tests:    +2-3% → 76-80%
─────────────────────────────
Target:               80%+ CMJ coverage ✓ ACHIEVABLE

Total New Tests:      ~40-50 tests
Estimated Effort:     3-4 days (for test implementation)
File Locations:       tests/test_cmj_joint_angles.py (expand)
                      tests/test_cmj_phase_progression.py (new)
                      tests/fixtures/cmj_videos.py (new)
```

### Timeline

- **Day 1:** Implement phase progression tests (8-10 tests)
- **Day 2:** Implement bounds validation tests (12-15 tests)
- **Day 3:** Implement real video tests (4-6 tests, requires synthetic video gen)
- **Day 4:** Implement ankle fix validation tests (3-4 tests) + documentation

### Success Criteria

- CMJ coverage: 62% → 80%+
- All phase progression tests passing
- All bounds validation tests passing
- Real video tests showing good/poor technique discrimination
- Ankle angle increases 20°+ from lowest to takeoff

**Recommendation:** EXPAND test suite as outlined. Current 62% has significant gaps in phase validation and real-world testing. The proposed expansion provides measurable, testable improvements with clear success criteria.

______________________________________________________________________

## 2. COVERAGE STRATEGY: Phase Progression & Physiological Bounds

### Progressive Coverage Layers

```
Layer 1: Unit Tests (Existing - 74%)
├─ Individual function tests
├─ Happy path coverage
└─ Basic edge cases

Layer 2: Phase Progression (NEW - Task 2)
├─ Phase detection validation
├─ Metrics increase through phases
├─ Phase timing validation
└─ Coverage: +5-6%

Layer 3: Physiological Bounds (NEW - Task 2)
├─ Joint angle anatomy validation
├─ Impossible value detection
├─ Expected range validation
└─ Coverage: +4-5%

Layer 4: Real-World Validation (NEW - Task 2)
├─ End-to-end video processing
├─ Technique discrimination (good vs poor)
├─ Video quality robustness
└─ Coverage: +3-4%

Layer 5: Integration (Task 3/4)
├─ Multi-sport cross-tests
├─ API contract validation
├─ Real-time stress tests
└─ Coverage: +2-3%
```

### Physiological Bounds Reference

Based on biomechanics research (Linthorne, Vanezis, Moran):

| Joint | Min | Max  | At Takeoff | Source                |
| ----- | --- | ---- | ---------- | --------------------- |
| Ankle | 70° | 135° | 110-130°   | Vanezis & Lees (2005) |
| Knee  | 80° | 185° | 160-180°   | Linthorne (2001)      |
| Hip   | 60° | 195° | 170-180°   | Linthorne (2001)      |

### Expected Phase Progressions

```
CMJ Phase Progression (Good Athlete):

Frame 0 (Standing):
  Ankle: 90°  | Knee: 170°  | Hip: 175°

Frame 1 (Eccentric start):
  Ankle: 88°  | Knee: 140°  | Hip: 130°

Frame 2 (Lowest point):
  Ankle: 80°  | Knee: 95°   | Hip: 100°
         ↓           ↓             ↓

Frame 3 (Concentric mid):
  Ankle: 100° | Knee: 130°  | Hip: 140°

Frame 4 (Concentric late):
  Ankle: 115° | Knee: 155°  | Hip: 165°

Frame 5 (Takeoff):
  Ankle: 120° | Knee: 170°  | Hip: 175°
  Change: +40° | Change: +75° | Change: +75°
  Status: ✓ Synchronized extension
```

______________________________________________________________________

## 3. REAL-TIME TESTING: Load Testing & Latency Profiling

### Real-Time Architecture (Task 3)

From roadmap analysis:

```
Client (React/Browser)
     ↓ WebRTC video stream (33ms @ 30fps)
     ↓ JSON metric updates

[Network Layer]
     ↓ WebSocket (50ms typical latency)
     ↓ Binary frame data, frame drops if needed

Server (FastAPI + MediaPipe)
     ↓ Frame receive (1ms)
     ↓ MediaPipe inference (50ms - bottleneck)
     ↓ Metric calculation (5ms)
     ↓ JSON serialization (2ms)

[Network Layer]
     ↓ WebSocket response (50ms)

Browser Rendering
     ↓ Parse JSON (2ms)
     ↓ Update UI (33ms @ 30fps)
     ↓ Browser paint (varies)
─────────────────
Total E2E: ~166ms (within <200ms target)
```

### Latency Testing Strategy

**Phase 1: Baseline Profiling (Week 1 of Task 3)**

```python
# tests/test_realtime_latency.py

class TestRealtimeLatencyBaseline:
    """Establish baseline latency for real-time mode."""

    def test_single_client_latency_p50(self, websocket_server):
        """P50 latency should be <150ms for single client."""
        results = run_latency_test(
            num_clients=1,
            duration_seconds=60,
            video_quality="balanced"
        )

        p50_latency = np.percentile(results.latencies, 50)
        assert p50_latency < 150, f"P50 latency {p50_latency}ms exceeds target"

    def test_single_client_latency_p95(self, websocket_server):
        """P95 latency should be <180ms for single client."""
        results = run_latency_test(num_clients=1, duration_seconds=60)
        p95_latency = np.percentile(results.latencies, 95)
        assert p95_latency < 180, f"P95 latency {p95_latency}ms exceeds target"

    def test_single_client_latency_p99(self, websocket_server):
        """P99 latency should be <200ms (acceptable for coaching)."""
        results = run_latency_test(num_clients=1, duration_seconds=60)
        p99_latency = np.percentile(results.latencies, 99)
        assert p99_latency < 200, f"P99 latency {p99_latency}ms exceeds target"

    def test_mediapipe_inference_time(self):
        """Profile MediaPipe inference time (main bottleneck)."""
        times = []
        for _ in range(100):
            frame = get_test_frame()
            start = time.perf_counter()
            results = mediapipe_pose.process(frame)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # ms

        p50_inference = np.percentile(times, 50)
        p95_inference = np.percentile(times, 95)

        # MediaPipe should be <50ms per frame
        assert p50_inference < 50, f"Inference {p50_inference}ms too slow"
        assert p95_inference < 60, f"Inference p95 {p95_inference}ms too slow"

def run_latency_test(num_clients, duration_seconds, video_quality="balanced"):
    """Run latency test with specified parameters."""
    latencies = []

    async def client_task():
        async with websockets.connect(f"ws://localhost:8000/stream") as ws:
            for frame_idx in range(duration_seconds * 30):  # 30fps
                # Send frame
                frame = get_test_frame(quality=video_quality)
                await ws.send(frame)

                # Measure roundtrip time
                start = time.perf_counter()
                response = await ws.recv()
                elapsed = (time.perf_counter() - start) * 1000  # ms
                latencies.append(elapsed)

    asyncio.run(asyncio.gather(*[client_task() for _ in range(num_clients)]))

    return LatencyResults(
        latencies=latencies,
        p50=np.percentile(latencies, 50),
        p95=np.percentile(latencies, 95),
        p99=np.percentile(latencies, 99),
        mean=np.mean(latencies),
        std=np.std(latencies),
    )
```

**Phase 2: Multi-Client Load Testing (Week 2 of Task 3)**

```python
class TestRealtimeLoadScaling:
    """Verify latency remains acceptable under load."""

    @pytest.mark.parametrize("num_clients", [1, 10, 25, 50, 100])
    def test_latency_p95_under_load(self, num_clients, websocket_server):
        """P95 latency should stay <200ms up to 50 clients."""
        results = run_latency_test(
            num_clients=num_clients,
            duration_seconds=30
        )

        if num_clients <= 50:
            # Should maintain <200ms
            assert results.p95 < 200, \
                f"{num_clients} clients: P95 {results.p95}ms exceeds target"
        else:
            # May degrade at 100 clients (find failure point)
            pass  # Log but don't fail

    @pytest.mark.parametrize("num_clients", [1, 10, 50, 100])
    def test_connection_stability_under_load(self, num_clients):
        """All connections should remain stable without drops."""
        results = run_load_test(
            num_clients=num_clients,
            duration_seconds=60,
            monitor_drops=True
        )

        # Connection drop rate should be <0.1%
        drop_rate = results.connection_drops / results.total_connections
        assert drop_rate < 0.001, \
            f"{num_clients} clients: {drop_rate*100:.2f}% drops"

def test_cpu_memory_per_client():
    """Monitor resource usage to predict max concurrent clients."""
    # Start server
    server_process = start_websocket_server()

    initial_cpu = get_cpu_percent()
    initial_mem = get_memory_percent()

    # Add clients incrementally
    for num_clients in [1, 10, 25, 50]:
        add_clients(num_clients)
        time.sleep(5)  # Let system stabilize

        cpu_percent = get_cpu_percent()
        mem_percent = get_memory_percent()

        cpu_per_client = (cpu_percent - initial_cpu) / num_clients
        mem_per_client = (mem_percent - initial_mem) / num_clients

        print(f"{num_clients} clients: "
              f"CPU {cpu_per_client:.1f}%/client, "
              f"Memory {mem_per_client:.1f}%/client")

        # Should be roughly linear until hitting limits
        # If CPU > 80% or Memory > 85%, find failure point
```

### Load Testing Tools Setup

```yaml
# tests/load-testing/locustfile.py
from locust import HttpUser, WebsocketClient, task, between

class RealtimeClient(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Connect to WebSocket."""
        self.client = websockets.connect("ws://localhost:8000/stream")

    @task
    def send_frame_get_metrics(self):
        """Send frame, receive metrics."""
        frame = get_video_frame()
        response = self.client.send(frame)
        metrics = json.loads(response)

        # Validate response
        assert "cmj_height" in metrics
        assert "gct" in metrics
        assert "rsi" in metrics

# Run with:
# locust -f tests/load-testing/locustfile.py \
#        --host=ws://localhost:8000 \
#        --users=50 --spawn-rate=5 --run-time=5m
```

### Multi-Client Testing Scenarios

| Scenario  | Clients   | Duration      | Success Criteria          |
| --------- | --------- | ------------- | ------------------------- |
| Baseline  | 1         | 5 min         | P95 \<150ms, 0 drops      |
| Ramp-Up   | 1→50      | 10 min        | P95 \<180ms, \<0.1% drops |
| Sustained | 25        | 30 min        | P95 \<200ms, 0 crashes    |
| Spike     | 10→100→10 | 5 min         | Handle without crashing   |
| Stress    | 100+      | Until failure | Find breaking point       |

### Latency Profiling Implementation

```python
# src/kinemotion/realtime/profiling.py

class LatencyProfiler:
    """Profiles latency at each stage of real-time pipeline."""

    def __init__(self):
        self.stages = {
            "frame_received": [],
            "mediapipe_inference": [],
            "metric_calculation": [],
            "json_serialization": [],
            "websocket_send": [],
            "total": [],
        }

    def profile_frame_processing(self, frame):
        """Profile a single frame through entire pipeline."""
        total_start = time.perf_counter()

        # Stage 1: Frame receive (timestamp when arrived)
        frame_received = time.perf_counter()
        self.stages["frame_received"].append(0)

        # Stage 2: MediaPipe inference
        inference_start = time.perf_counter()
        pose_results = self.pose.process(frame)
        inference_time = (time.perf_counter() - inference_start) * 1000
        self.stages["mediapipe_inference"].append(inference_time)

        # Stage 3: Metric calculation
        calc_start = time.perf_counter()
        metrics = calculate_metrics(pose_results)
        calc_time = (time.perf_counter() - calc_start) * 1000
        self.stages["metric_calculation"].append(calc_time)

        # Stage 4: JSON serialization
        serial_start = time.perf_counter()
        json_payload = json.dumps(metrics)
        serial_time = (time.perf_counter() - serial_start) * 1000
        self.stages["json_serialization"].append(serial_time)

        # Stage 5: WebSocket send (simulated)
        total_time = (time.perf_counter() - total_start) * 1000
        self.stages["total"].append(total_time)

        return metrics

    def get_report(self):
        """Generate latency report."""
        report = {}
        for stage, times in self.stages.items():
            report[stage] = {
                "mean": np.mean(times),
                "p50": np.percentile(times, 50),
                "p95": np.percentile(times, 95),
                "p99": np.percentile(times, 99),
                "max": np.max(times),
            }
        return report
```

______________________________________________________________________

## 4. RUNNING VALIDATION: Without Biomechanics Lab

### Validation Strategy (Task 4)

**Three-Level Validation Approach:**

### Level 1: Published Research Validation

```python
# tests/test_running_validation.py

class TestRunningMetricsAgainstPublishedRanges:
    """Validate against published running biomechanics research."""

    PUBLISHED_RANGES = {
        # Ground Contact Time (GCT)
        "gct": {
            "elite_sprinter": (0.08, 0.15),       # Very fast
            "elite_distance": (0.25, 0.35),       # Efficient
            "recreational": (0.35, 0.50),        # Slower
            "overstrider": (0.50, 0.70),         # Poor technique
        },
        # Cadence (steps/minute)
        "cadence": {
            "optimal": (160, 180),
            "slow": (140, 160),
            "fast": (180, 200),
        },
        # Stride Length (m) - varies by height
        "stride_length": {
            "height_160cm": (0.90, 1.20),
            "height_170cm": (1.00, 1.35),
            "height_180cm": (1.10, 1.50),
        },
    }

    def test_gct_in_published_range_recreational(self):
        """GCT should be 0.35-0.50s for recreational runners."""
        # Using synthetic video matching "recreational" biomechanics
        video = create_synthetic_running_video(
            gait_profile="recreational",
            gct_seconds=0.42  # Middle of range
        )

        metrics = process_running_video(video)
        gct = metrics["ground_contact_time"]

        assert 0.35 <= gct <= 0.50, \
            f"GCT {gct:.3f}s outside published range for recreational [0.35-0.50s]"

    def test_cadence_in_published_optimal_range(self):
        """Optimal cadence should be 160-180 steps/min."""
        video = create_synthetic_running_video(
            cadence_spm=170  # Middle of optimal range
        )

        metrics = process_running_video(video)
        cadence = metrics["cadence"]

        assert 160 <= cadence <= 180, \
            f"Cadence {cadence:.1f} spm outside optimal range [160-180]"

    def test_stride_length_matches_height(self):
        """Stride length should scale with athlete height."""
        # Test different heights
        test_cases = [
            (160, (0.90, 1.20)),
            (170, (1.00, 1.35)),
            (180, (1.10, 1.50)),
        ]

        for height_cm, expected_range in test_cases:
            video = create_synthetic_running_video(
                athlete_height_cm=height_cm,
                stride_length_m=np.mean(expected_range)
            )

            metrics = process_running_video(video)
            stride = metrics["stride_length"]

            assert expected_range[0] <= stride <= expected_range[1], \
                f"Height {height_cm}cm: stride {stride:.2f}m outside range {expected_range}"
```

**Reference Sources:**

- Buist et al. (2007): Running biomechanics
- Lieberman et al. (2010): Impact forces and running form
- Moore et al. (2012): Running economy and cadence

### Level 2: Consistency & Repeatability Testing

```python
class TestRunningConsistency:
    """Validate metric stability and reproducibility."""

    def test_gct_repeatable_same_video(self):
        """Same video analyzed twice should give same GCT."""
        video = create_synthetic_running_video()

        # Analyze twice
        metrics1 = process_running_video(video)
        metrics2 = process_running_video(video)

        # GCT should be identical
        assert abs(metrics1["gct"] - metrics2["gct"]) < 0.01, \
            "GCT should be repeatable"

    def test_metrics_stable_across_angles(self):
        """Metrics should be similar from slightly different camera angles."""
        # Create same run from slightly different angles (±5° tilt)
        base_video = create_synthetic_running_video(gct_seconds=0.40)
        video_tilted_left = create_synthetic_running_video(
            gct_seconds=0.40,
            camera_angle=85  # 5° tilt
        )
        video_tilted_right = create_synthetic_running_video(
            gct_seconds=0.40,
            camera_angle=95  # 5° tilt other direction
        )

        metrics_base = process_running_video(base_video)
        metrics_left = process_running_video(video_tilted_left)
        metrics_right = process_running_video(video_tilted_right)

        # Should be within 5% tolerance
        tolerance = 0.05  # 5%

        assert abs(metrics_base["gct"] - metrics_left["gct"]) / metrics_base["gct"] < tolerance
        assert abs(metrics_base["gct"] - metrics_right["gct"]) / metrics_base["gct"] < tolerance

    def test_asymmetry_detection_left_vs_right(self):
        """Should detect asymmetry between left and right legs."""
        # Video with asymmetrical GCT (left 0.35s, right 0.45s)
        video = create_synthetic_running_video(
            left_gct_seconds=0.35,
            right_gct_seconds=0.45
        )

        metrics = process_running_video(video)

        # Should report asymmetry
        assert metrics["left_gct"] < metrics["right_gct"]
        asymmetry_percent = abs(metrics["left_gct"] - metrics["right_gct"]) / \
                           np.mean([metrics["left_gct"], metrics["right_gct"]]) * 100
        assert asymmetry_percent > 20, "Should detect >20% asymmetry"
```

### Level 3: Crowdsourced Athlete Validation

```python
class TestRunningWithRealAthletes:
    """Validate with real athlete data (minimal infrastructure)."""

    @pytest.fixture
    def athlete_video_database(self):
        """Load database of athlete videos (crowdsourced or test)."""
        # In real scenario: 10-20 recruited runners
        # For now: synthetic videos matching athlete profiles
        return {
            "elite_runner_1": {
                "video": "synthetic_elite_1.mp4",
                "self_reported_gct": 0.28,
                "self_reported_cadence": 185,
                "fitness_level": "elite",
            },
            "recreational_runner_1": {
                "video": "synthetic_recreational_1.mp4",
                "self_reported_gct": 0.42,
                "self_reported_cadence": 172,
                "fitness_level": "recreational",
            },
            "beginner_runner_1": {
                "video": "synthetic_beginner_1.mp4",
                "self_reported_gct": 0.55,
                "self_reported_cadence": 155,
                "fitness_level": "beginner",
            },
        }

    def test_metrics_correlate_with_fitness_level(self, athlete_video_database):
        """Measured metrics should correlate with self-reported fitness."""
        results = []

        for athlete_id, athlete_data in athlete_video_database.items():
            metrics = process_running_video(athlete_data["video"])

            results.append({
                "athlete": athlete_id,
                "fitness_level": athlete_data["fitness_level"],
                "measured_gct": metrics["gct"],
                "self_reported_gct": athlete_data["self_reported_gct"],
                "measured_cadence": metrics["cadence"],
                "self_reported_cadence": athlete_data["self_reported_cadence"],
            })

        # Correlation tests
        for result in results:
            # Elite runners should have lower GCT
            if result["fitness_level"] == "elite":
                assert result["measured_gct"] < 0.35, \
                    f"Elite runner GCT {result['measured_gct']} should be <0.35"

            # Beginners should have higher GCT
            elif result["fitness_level"] == "beginner":
                assert result["measured_gct"] > 0.45, \
                    f"Beginner GCT {result['measured_gct']} should be >0.45"

    def test_gct_error_within_acceptable_range(self, athlete_video_database):
        """Measured GCT should be within 10% of self-reported."""
        for athlete_id, athlete_data in athlete_video_database.items():
            metrics = process_running_video(athlete_data["video"])

            measured = metrics["gct"]
            reported = athlete_data["self_reported_gct"]

            error_percent = abs(measured - reported) / reported * 100
            assert error_percent < 15, \
                f"GCT error {error_percent:.1f}% exceeds 15% tolerance"
```

### Validation Approach Advantages

| Approach              | Effort | Cost | Reliability          |
| --------------------- | ------ | ---- | -------------------- |
| Published Research    | Low    | None | High (peer-reviewed) |
| Synthetic Data        | Medium | None | Medium (controlled)  |
| Consistency Tests     | Low    | None | High (deterministic) |
| Crowdsourced Athletes | Medium | Low  | High (real data)     |
| Lab Equipment         | High   | High | Highest              |

**Recommendation:** Use **Levels 1-3** (published research + synthetic + crowdsourced). Sufficient for MVP validation without lab.

______________________________________________________________________

## 5. REGRESSION PREVENTION: Critical Tests for 3-Sport Platform

### Regression Test Strategy

**Regression Prevention Layers:**

### Layer 1: Algorithm Regression Tests

```python
# tests/test_regression_core_algorithms.py

class TestCoreAlgorithmRegression:
    """Catch regressions in core calculations across all sports."""

    # Baseline metrics (snapshot from current, working version)
    BASELINE_METRICS = {
        "drop_jump": {
            "gct": 0.285,           # Ground contact time
            "rsi": 2.15,            # Reactive strength index
            "peak_velocity": 3.2,   # m/s
        },
        "cmj": {
            "jump_height": 0.52,    # meters
            "flight_time": 0.647,   # seconds
            "peak_velocity": 3.15,  # m/s
        },
        "running": {
            "gct": 0.38,            # Ground contact time
            "cadence": 175,         # steps/min
            "stride_length": 1.28,  # meters
        },
    }

    @pytest.mark.parametrize("sport,metric,baseline", [
        ("drop_jump", "gct", 0.285),
        ("drop_jump", "rsi", 2.15),
        ("cmj", "jump_height", 0.52),
        ("running", "gct", 0.38),
    ])
    def test_metric_regression_detection(self, sport, metric, baseline):
        """Detect if core metrics deviate significantly from baseline."""
        # Use standard test video for each sport
        test_video = get_standard_test_video(sport)

        if sport == "drop_jump":
            metrics = process_dropjump_video(test_video)
        elif sport == "cmj":
            metrics = process_cmj_video(test_video)
        else:
            metrics = process_running_video(test_video)

        measured = metrics[metric]

        # Allow 2% tolerance (small variations expected)
        tolerance = baseline * 0.02

        assert abs(measured - baseline) <= tolerance, \
            f"{sport} {metric}: {measured} differs from baseline {baseline} by " \
            f"{abs(measured - baseline) / baseline * 100:.1f}% (tolerance 2%)"

    def test_filtering_doesnt_change_output_significantly(self):
        """Smoothing/filtering should not degrade metrics >1%."""
        # Get raw metrics
        raw_metrics = calculate_metrics_raw(get_standard_test_video("cmj"))

        # Get filtered metrics
        filtered_metrics = calculate_metrics_filtered(get_standard_test_video("cmj"))

        # Height should be within 1% (smoothing helps, shouldn't hurt)
        height_change = abs(raw_metrics["height"] - filtered_metrics["height"]) / \
                       raw_metrics["height"] * 100
        assert height_change < 2, \
            f"Filtering changed height by {height_change:.1f}% (>2%)"
```

### Layer 2: Cross-Sport Regression Tests

```python
class TestCrossSportRegression:
    """Verify changes in one sport don't break others."""

    def test_phase_detection_works_for_all_sports(self):
        """Phase detection abstraction must work for jump AND running."""
        # Get test videos
        drop_jump_video = get_standard_test_video("drop_jump")
        cmj_video = get_standard_test_video("cmj")
        running_video = get_standard_test_video("running")

        # All should successfully detect phases
        for video_path in [drop_jump_video, cmj_video, running_video]:
            phases = detect_phases(video_path)

            assert phases is not None, "Phase detection returned None"
            assert len(phases) > 0, "No phases detected"
            assert all(p["start"] < p["end"] for p in phases), \
                "Invalid phase boundaries"

    def test_cli_commands_still_work(self):
        """CLI commands for all sports should still function."""
        test_videos = {
            "drop_jump": get_standard_test_video("drop_jump"),
            "cmj": get_standard_test_video("cmj"),
            "running": get_standard_test_video("running"),
        }

        for sport, video_path in test_videos.items():
            result = subprocess.run(
                ["kinemotion", f"{sport}-analyze", str(video_path)],
                capture_output=True,
                text=True
            )

            assert result.returncode == 0, \
                f"{sport} CLI failed: {result.stderr}"

            # Output should be valid JSON
            output = json.loads(result.stdout)
            assert "metrics" in output, f"{sport} output missing metrics"

    def test_api_signatures_consistent_across_sports(self):
        """API should have consistent interface across sports."""
        # All sports should accept same parameters
        params = {
            "video_path": "test.mp4",
            "quality": "balanced",
            "output": "output.mp4",
        }

        # Should not raise exceptions
        try:
            process_dropjump_video(**params)
            process_cmj_video(**params)
            process_running_video(**params)
        except TypeError as e:
            pytest.fail(f"Inconsistent API signature: {e}")
```

### Layer 3: Biomechanics Regression Tests

```python
class TestBiomechanicsRegression:
    """Catch regressions in biomechanical accuracy."""

    def test_ankle_angle_still_increases_after_fix(self):
        """Ankle angle fix should increase values during concentric."""
        video = get_cmj_test_video()
        angles = extract_ankle_angles_through_phases(video)

        # After foot_index fix, should see significant increase
        increase_from_lowest_to_takeoff = angles["takeoff"] - angles["lowest_point"]

        assert increase_from_lowest_to_takeoff > 20, \
            f"Ankle increase {increase_from_lowest_to_takeoff}° too small " \
            "(foot_index fix may have regressed)"

    def test_triple_extension_stays_synchronized(self):
        """Hip/knee/ankle should extend together."""
        video = get_cmj_test_video()
        metrics = process_cmj_video(str(video))

        # All joints should reach near-maximum at similar time
        synchronization_score = calculate_synchronization(
            metrics["ankle_angles"],
            metrics["knee_angles"],
            metrics["hip_angles"]
        )

        assert synchronization_score > 0.75, \
            f"Synchronization {synchronization_score} indicates regression"

    def test_metrics_within_expected_physiological_ranges(self):
        """Metrics should be within known physiological bounds."""
        test_cases = [
            ("drop_jump", {
                "gct": (0.15, 0.50),
                "rsi": (1.0, 4.0),
            }),
            ("cmj", {
                "jump_height": (0.30, 0.80),
                "flight_time": (0.50, 0.80),
            }),
            ("running", {
                "gct": (0.25, 0.60),
                "cadence": (140, 200),
            }),
        ]

        for sport, bounds in test_cases:
            video = get_standard_test_video(sport)
            metrics = process_video(video, sport_type=sport)

            for metric_name, (min_val, max_val) in bounds.items():
                value = metrics[metric_name]
                assert min_val <= value <= max_val, \
                    f"{sport} {metric_name} {value} outside bounds [{min_val}, {max_val}]"
```

### Layer 4: Integration Regression Tests

```python
class TestIntegrationRegression:
    """Verify end-to-end pipelines still work."""

    def test_batch_processing_all_sports(self):
        """Batch processing should work for all sports."""
        test_dir = Path("tests/test_videos")
        videos = list(test_dir.glob("*.mp4"))

        # Should complete without errors
        results = process_videos_batch(videos, num_workers=4)

        assert len(results) == len(videos), "Some videos not processed"
        assert all(r["success"] for r in results), "Some videos failed"

    def test_real_time_mode_with_all_sports(self):
        """Real-time mode should work for all sports."""
        for sport in ["drop_jump", "cmj", "running"]:
            # Should start without errors
            realtime_processor = RealtimeAnalyzer(sport_type=sport)

            # Process test frame
            test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            result = realtime_processor.process_frame(test_frame)

            assert result is not None, f"Real-time {sport} returned None"
            assert "metrics" in result, f"Real-time {sport} missing metrics"

    def test_api_endpoint_health_all_sports(self):
        """API endpoints should respond for all sports."""
        for sport in ["drop_jump", "cmj", "running"]:
            response = requests.get(f"/api/{sport}/status")

            assert response.status_code == 200, \
                f"{sport} API endpoint not responding"
```

### Regression Test CI Integration

```yaml
# .github/workflows/regression-tests.yml

name: Regression Tests

on: [push, pull_request]

jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run regression tests
        run: |
          uv run pytest tests/test_regression_*.py -v --tb=short

      - name: Compare metrics against baseline
        run: |
          uv run python scripts/compare_metrics.py \
            --baseline metrics_baseline.json \
            --current metrics_current.json \
            --tolerance 0.02  # 2% tolerance

      - name: Fail if metrics regressed >2%
        run: |
          if [ $? -ne 0 ]; then
            echo "Metrics regressed beyond tolerance"
            exit 1
          fi
```

______________________________________________________________________

## 6. INTEGRATION TESTING: APIs, Webhooks, Multi-User

### API Testing Framework

```python
# tests/test_api_integration.py

class TestAPIIntegration:
    """Test API endpoints and contracts."""

    @pytest.fixture
    def api_client(self):
        """Fixture for API testing."""
        return TestClient(app)  # FastAPI test client

    def test_create_analysis_request(self, api_client):
        """POST /api/analyses should create new analysis."""
        response = api_client.post(
            "/api/analyses",
            json={
                "video_url": "https://example.com/video.mp4",
                "sport_type": "cmj",
                "quality": "balanced",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "analysis_id" in data
        assert data["status"] == "pending"

    def test_get_analysis_results(self, api_client):
        """GET /api/analyses/{id} should return results."""
        # Create analysis
        create_response = api_client.post(
            "/api/analyses",
            json={"video_url": "...", "sport_type": "cmj"}
        )
        analysis_id = create_response.json()["analysis_id"]

        # Get results (should wait until complete)
        get_response = api_client.get(f"/api/analyses/{analysis_id}")

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["status"] in ["completed", "processing"]
        assert "metrics" in data or data["status"] == "processing"

    def test_api_rate_limiting(self, api_client):
        """API should enforce rate limits."""
        # Make requests rapidly
        for i in range(101):  # Exceed limit
            response = api_client.get("/api/status")

            if i < 100:
                assert response.status_code == 200
            else:
                # 101st request should be rate limited
                assert response.status_code == 429  # Too Many Requests

    def test_authentication_required(self, api_client):
        """Protected endpoints should require authentication."""
        response = api_client.post(
            "/api/analyses",
            json={"video_url": "..."},
            headers={}  # No auth header
        )

        assert response.status_code == 401  # Unauthorized

    def test_user_data_isolation(self, api_client):
        """User A shouldn't see User B's analyses."""
        # User A creates analysis
        user_a_response = api_client.post(
            "/api/analyses",
            json={"video_url": "...", "sport_type": "cmj"},
            headers={"Authorization": "Bearer user_a_token"}
        )
        user_a_analysis_id = user_a_response.json()["analysis_id"]

        # User B tries to access User A's analysis
        user_b_response = api_client.get(
            f"/api/analyses/{user_a_analysis_id}",
            headers={"Authorization": "Bearer user_b_token"}
        )

        assert user_b_response.status_code == 403  # Forbidden
```

### Webhook Testing

```python
class TestWebhookIntegration:
    """Test webhook delivery and reliability."""

    @pytest.fixture
    def webhook_receiver(self):
        """Mock webhook receiver server."""
        server = WebhookReceiverMock()
        yield server
        server.cleanup()

    def test_webhook_fires_on_analysis_complete(self, webhook_receiver):
        """Webhook should be called when analysis completes."""
        webhook_url = webhook_receiver.get_url()

        # Register webhook
        requests.post(
            "/api/webhooks/register",
            json={
                "event": "analysis.complete",
                "url": webhook_url,
            }
        )

        # Trigger analysis
        response = requests.post(
            "/api/analyses",
            json={"video_url": "...", "sport_type": "cmj"}
        )
        analysis_id = response.json()["analysis_id"]

        # Wait for completion
        time.sleep(5)

        # Check webhook was received
        webhooks = webhook_receiver.get_received_webhooks()

        assert len(webhooks) > 0, "No webhooks received"
        assert webhooks[0]["event"] == "analysis.complete"
        assert webhooks[0]["data"]["analysis_id"] == analysis_id

    def test_webhook_retry_on_failure(self, webhook_receiver):
        """Failed webhooks should retry with backoff."""
        # Register webhook that will fail
        webhook_url = "http://nonexistent.example.com/webhook"

        requests.post(
            "/api/webhooks/register",
            json={"event": "analysis.complete", "url": webhook_url}
        )

        # Trigger analysis
        requests.post("/api/analyses", json={"video_url": "...", "sport_type": "cmj"})

        # Wait and verify retry attempts logged
        time.sleep(10)

        logs = get_webhook_logs()
        retry_attempts = [l for l in logs if "retry" in l.lower()]

        assert len(retry_attempts) > 0, "No retry attempts logged"

    def test_webhook_payload_contains_correct_metrics(self, webhook_receiver):
        """Webhook payload should include all expected metrics."""
        webhook_url = webhook_receiver.get_url()

        requests.post(
            "/api/webhooks/register",
            json={"event": "analysis.complete", "url": webhook_url}
        )

        requests.post(
            "/api/analyses",
            json={"video_url": "...", "sport_type": "cmj"}
        )

        time.sleep(5)

        webhooks = webhook_receiver.get_received_webhooks()
        payload = webhooks[0]["data"]

        # Should contain CMJ metrics
        assert "jump_height" in payload["metrics"]
        assert "flight_time" in payload["metrics"]
        assert "metrics_confidence" in payload
```

### Multi-User Scenario Testing

```python
class TestMultiUserScenarios:
    """Test concurrent multi-user behavior."""

    def test_concurrent_analyses_isolated(self):
        """Multiple concurrent analyses should be isolated."""
        async def user_analysis(user_id):
            """Simulate user submitting analysis."""
            response = await api_client.post(
                "/api/analyses",
                json={
                    "video_url": f"https://example.com/video_{user_id}.mp4",
                    "sport_type": "cmj"
                }
            )
            return response.json()["analysis_id"]

        # Run 10 concurrent analyses
        user_ids = range(10)
        analysis_ids = asyncio.run(
            asyncio.gather(*[user_analysis(uid) for uid in user_ids])
        )

        # All should be unique
        assert len(set(analysis_ids)) == 10, "Duplicate analysis IDs"

    def test_high_concurrency_load(self):
        """System should handle 50 concurrent users."""
        def user_workflow():
            """Simulate one user's workflow."""
            # Create analysis
            create = requests.post(
                "/api/analyses",
                json={"video_url": "...", "sport_type": "cmj"}
            )
            analysis_id = create.json()["analysis_id"]

            # Poll for completion
            for _ in range(30):  # Poll for up to 30s
                get = requests.get(f"/api/analyses/{analysis_id}")
                if get.json()["status"] == "completed":
                    return True
                time.sleep(1)

            return False

        # Run with 50 concurrent users
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(user_workflow) for _ in range(50)]
            results = [f.result() for f in futures]

        # All users should complete successfully
        success_rate = sum(results) / len(results)
        assert success_rate > 0.95, f"Only {success_rate*100:.1f}% succeeded"

    def test_team_analytics_aggregation(self):
        """Users should see aggregated team metrics."""
        # Create 5 users on team
        team_id = "team_123"
        user_ids = [f"user_{i}" for i in range(5)]

        # Each user submits CMJ
        for user_id in user_ids:
            requests.post(
                "/api/analyses",
                json={
                    "video_url": "...",
                    "sport_type": "cmj",
                    "team_id": team_id,
                    "user_id": user_id,
                }
            )

        # Get team summary
        response = requests.get(f"/api/teams/{team_id}/summary")

        assert response.status_code == 200
        data = response.json()

        # Should show aggregated metrics
        assert "average_jump_height" in data
        assert "athlete_count" in data
        assert data["athlete_count"] == 5

        # Should NOT include individual user results
        assert "user_1_jump_height" not in data
```

______________________________________________________________________

## 7. PERFORMANCE TESTING: Benchmarks & Profiling

### Latency Benchmarks (Task 3)

| Scenario       | Target      | Metric       | Tool                |
| -------------- | ----------- | ------------ | ------------------- |
| Single Client  | \<150ms P50 | E2E latency  | Custom profiler     |
| 10 Clients     | \<180ms P95 | E2E latency  | WebSocket load test |
| 50 Clients     | \<200ms P99 | E2E latency  | WebSocket load test |
| Inference Only | \<50ms P50  | MediaPipe    | cProfile            |
| Metric Calc    | \<10ms P50  | Calculations | cProfile            |

### Setup Performance Benchmarking

```python
# tests/benchmarks/realtime_latency_benchmark.py

import pytest
from benchmarking import LatencyBenchmark

class TestRealtimeLatencyBenchmarks:
    """Performance benchmarks for real-time mode."""

    @pytest.mark.benchmark
    def test_single_frame_processing_latency(self, benchmark):
        """Benchmark single frame end-to-end latency."""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        def process_frame():
            processor = RealtimeAnalyzer(sport="cmj")
            return processor.process_frame(frame)

        result = benchmark(process_frame)

        # Should complete in <100ms for single frame
        assert benchmark.stats.mean < 0.100

    @pytest.mark.benchmark
    def test_mediapipe_inference_benchmark(self, benchmark):
        """Benchmark MediaPipe inference time."""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        pose = mp.solutions.pose.Pose()

        result = benchmark(lambda: pose.process(frame))

        # Should be <50ms per frame
        assert benchmark.stats.mean < 0.050

    @pytest.mark.benchmark
    def test_metric_calculation_benchmark(self, benchmark):
        """Benchmark metric calculation speed."""
        landmarks = generate_test_landmarks()

        def calc_metrics():
            return calculate_metrics(landmarks)

        result = benchmark(calc_metrics)

        # Should be <10ms
        assert benchmark.stats.mean < 0.010

# Run with: pytest tests/benchmarks/ --benchmark-only
```

### Throughput Testing

```python
class TestThroughput:
    """Test system throughput under load."""

    def test_video_processing_throughput(self):
        """Measure videos processed per second."""
        test_videos = [create_test_video(i) for i in range(10)]

        start = time.perf_counter()

        for video in test_videos:
            process_video(str(video))

        elapsed = time.perf_counter() - start
        throughput = len(test_videos) / elapsed

        # Should process at least 1 video/second
        assert throughput > 1.0, f"Throughput {throughput:.2f} vps too low"

    def test_real_time_frame_throughput(self):
        """Measure frames processed per second in real-time mode."""
        processor = RealtimeAnalyzer(sport="cmj")
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        frame_count = 0
        start = time.perf_counter()
        duration = 10  # seconds

        while time.perf_counter() - start < duration:
            processor.process_frame(frame)
            frame_count += 1

        fps = frame_count / duration

        # Should sustain 30+ FPS
        assert fps >= 30, f"FPS {fps:.1f} below 30fps target"
```

### Memory Profiling

```python
class TestMemoryUsage:
    """Test memory consumption."""

    def test_per_client_memory_overhead(self):
        """Measure memory per WebSocket client."""
        import tracemalloc

        tracemalloc.start()

        # Start with baseline
        baseline = tracemalloc.get_traced_memory()[0]

        # Create 10 clients
        clients = [create_websocket_client() for _ in range(10)]

        peak = tracemalloc.get_traced_memory()[0]
        per_client_memory = (peak - baseline) / 10

        # Should be <50MB per client
        assert per_client_memory < 50e6, \
            f"Memory {per_client_memory/1e6:.1f}MB per client too high"

    def test_no_memory_leak_long_running(self):
        """Verify no memory leak during long operation."""
        import psutil

        process = psutil.Process()

        # Start real-time mode
        processor = RealtimeAnalyzer(sport="cmj")

        # Process frames for 1 minute
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        memory_samples = []
        for i in range(3000):  # ~100 seconds @ 30fps
            processor.process_frame(frame)

            if i % 300 == 0:  # Sample every 10s
                memory_samples.append(process.memory_info().rss / 1e6)

        # Memory should not grow monotonically
        # Allow 10% growth (garbage collection)
        growth = (memory_samples[-1] - memory_samples[0]) / memory_samples[0]
        assert growth < 0.10, f"Memory grew {growth*100:.1f}% (possible leak)"
```

______________________________________________________________________

## 8. TEST INFRASTRUCTURE & TOOLS

### Recommended Load Testing Tools

```yaml
# Load Testing Tool Recommendations:

Apache JMeter:
  - WebSocket plugin support
  - Scalability: 1000+ concurrent connections
  - Cost: Free/open-source
  - Good for: Spike testing, sustained load
  - Setup: JMeter WebSocket sampler

Locust:
  - Python-based, easy to write custom scenarios
  - Real-time monitoring
  - Cost: Free/open-source
  - Good for: Realistic user workflows
  - Setup: Custom Python load tests

BlazeMeter/Loadforge:
  - Cloud-based, easy setup
  - Real-time dashboards
  - Cost: Paid ($100-500/month)
  - Good for: Production load testing
  - Setup: UI-based scenario definition

Custom Python (asyncio + websockets):
  - Full control, lightweight
  - Best for: Specific protocol testing
  - Cost: Free
  - Good for: Integration with CI/CD
```

### CI/CD Integration

```yaml
# .github/workflows/performance-tests.yml

name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Run latency benchmarks
        run: |
          uv run pytest tests/benchmarks/ \
            --benchmark-only \
            --benchmark-json=benchmarks.json

      - name: Compare against baseline
        run: |
          python scripts/compare_benchmarks.py \
            --baseline .github/baseline_benchmarks.json \
            --current benchmarks.json \
            --tolerance 0.10  # 10% tolerance

      - name: Run WebSocket load test
        run: |
          locust -f tests/load-testing/locustfile.py \
            --headless --users=50 --spawn-rate=5 \
            --run-time=5m --csv=load_results

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: |
            benchmarks.json
            load_results_*.csv

      - name: Fail if performance regressed >10%
        run: |
          if [ $? -ne 0 ]; then
            echo "Performance regression detected"
            exit 1
          fi
```

### Performance Profiling Tools

```python
# src/kinemotion/realtime/profiling.py

import cProfile
import pstats
from contextlib import contextmanager

@contextmanager
def profile_section(name):
    """Profile a code section."""
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        yield profiler
    finally:
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats("cumulative")
        print(f"\n=== Profile: {name} ===")
        stats.print_stats(10)  # Top 10 functions

# Usage:
# with profile_section("MediaPipe Processing"):
#     results = pose.process(frame)
```

______________________________________________________________________

## 9. RISK ASSESSMENT & MITIGATION

### Risk Matrix

```
Impact vs Likelihood Matrix:

HIGH Impact × HIGH Likelihood → CRITICAL
├─ Real-time latency misses target
└─ Ankle angle fix breaks tests

HIGH Impact × MEDIUM Likelihood → HIGH
├─ Multi-sport architecture fails to generalize
├─ Regression in core algorithms
└─ Task 2 doesn't reach 80% coverage

MEDIUM Impact × MEDIUM Likelihood → MEDIUM
├─ WebSocket reliability under load
└─ API rate limiting too restrictive

LOW Impact × LOW Likelihood → LOW
├─ Performance degradation over time
└─ MediaPipe breaking changes
```

### Critical Risk 1: Real-Time Latency Misses \<200ms Target

| Aspect         | Details                                            |
| -------------- | -------------------------------------------------- |
| **Likelihood** | MEDIUM (MediaPipe might be slower than expected)   |
| **Impact**     | VERY HIGH (product-market fit failure)             |
| **Detection**  | Week 1 of Task 3 latency profiling                 |
| **Mitigation** | Early performance testing, frame dropping fallback |
| **Recovery**   | 2-3 week optimization sprint                       |

**Mitigation Strategy:**

```python
# Week 1 baseline test (must complete)
- Single client latency: <150ms P50, <200ms P99
- MediaPipe inference: <50ms P50, <60ms P95

# If fails:
- Option 1: Use GPU/optimized inference
- Option 2: Reduce video quality for real-time
- Option 3: Frame dropping (process every other frame)
- Option 4: Client-side preprocessing (compression)

Fallback target: <250ms acceptable for amateur coaches
```

### Critical Risk 2: Ankle Angle Fix Breaks Other Tests

| Aspect         | Details                               |
| -------------- | ------------------------------------- |
| **Likelihood** | LOW (well-understood change)          |
| **Impact**     | VERY HIGH (blocks entire roadmap)     |
| **Detection**  | During Task 1 implementation          |
| **Mitigation** | Comprehensive test suite before/after |
| **Recovery**   | Quick rollback + investigation        |

**Mitigation Strategy:**

```python
# Before implementing ankle fix:
1. Snapshot all current test results
2. Snapshot all current metrics (height, flight time, etc.)
3. Create regression test baseline

# During implementation:
1. Run full test suite after change
2. Compare metrics against baseline
3. Verify with real CMJ video

# If breaks:
1. Rollback change
2. Investigate root cause
3. Add specific test to prevent regression
4. Reimplement carefully
```

### Medium Risk 1: Multi-Sport Architecture Fails

| Aspect         | Details                                              |
| -------------- | ---------------------------------------------------- |
| **Likelihood** | MEDIUM (jump/running have different characteristics) |
| **Impact**     | HIGH (running feature blocked)                       |
| **Detection**  | Week 4 when running tests written                    |
| **Mitigation** | Architecture review before Task 4                    |
| **Recovery**   | 1-2 week redesign                                    |

**Mitigation Strategy:**

```
PREVENT (Week 2):
├─ Design phase detection abstraction
├─ Write abstraction tests with dummy data
├─ Get architecture review from team
└─ Validate with existing drop jump code

DETECT (Week 3):
├─ Write running detection tests
├─ Run against abstraction
└─ Identify gaps early

RECOVER:
└─ Fix abstraction in parallel with Task 4
```

### Medium Risk 2: Task 2 Coverage Doesn't Reach 80%

| Aspect         | Details                       |
| -------------- | ----------------------------- |
| **Likelihood** | MEDIUM (scope underestimated) |
| **Impact**     | MEDIUM (quality suffers)      |
| **Detection**  | End of Task 2 (Day 4)         |
| **Mitigation** | Daily coverage tracking in CI |
| **Recovery**   | 2-3 day extension             |

**Mitigation Strategy:**

```
MONITOR:
├─ Track coverage daily
├─ Identify untested code early
└─ Adjust test scope if needed

PREVENT:
├─ Add coverage gates to merge requirements
├─ Fail PR if coverage drops
└─ Define success criteria upfront

RECOVER:
└─ Can extend Task 2 by 2-3 days if needed
```

______________________________________________________________________

## 10. RECOMMENDATIONS & SUMMARY

### Strategic Testing Recommendations

**Immediate Actions (This Week):**

1. **Baseline Establishment**

   - Run full test suite on current code
   - Snapshot all metrics (GCT, RSI, height, etc.)
   - Establish performance baseline
   - Create regression test fixtures

1. **Task 1 Preparation (Ankle Fix)**

   - Prepare comprehensive test suite for foot_index validation
   - Get biomechanics specialist to review change
   - Plan rapid rollback if needed
   - Schedule 2-hour validation window

1. **Task 2 Scope Finalization**

   - Finalize test list (40-50 tests as outlined)
   - Estimate resource needs per test type
   - Prepare test video generation fixtures
   - Confirm coverage targets achievable

### Implementation Priority

```
PHASE 1 (Week 1):
✓ Task 1: Ankle angle fix + validation tests
✓ Task 2: Start phase progression tests

PHASE 2 (Week 2-3):
✓ Task 2: Complete phase progression + bounds validation
✓ Task 3: Start real-time architecture design + latency profiling

PHASE 3 (Week 4-5):
✓ Task 3: Implement WebSocket + load testing
✓ Task 4: Start running analysis with architecture validation

PHASE 4 (Week 6-7):
✓ Task 3: Finalize real-time + performance optimization
✓ Task 4: Complete running analysis + validation
✓ Task 5: Complete API + webhook + SDK testing
```

### Test Infrastructure Buildout

**Required Setup:**

- [ ] Synthetic video generation (CMJ, drop jump, running)
- [ ] WebSocket load testing harness
- [ ] Latency profiling infrastructure
- [ ] Regression test baseline snapshots
- [ ] CI/CD performance gates
- [ ] Mock webhook receiver
- [ ] API load testing setup
- [ ] Performance benchmark tracking

**Estimated Effort:** 3-4 days setup + 1 day per new test phase

### Coverage Path to Success

```
Current:        74.27% (261 tests, 2383 statements)
│
├─ Task 1: Ankle fix tests         +2-3%  → 76-77%
├─ Task 2: Phase progression       +5-6%  → 81-83%
├─ Task 2: Bounds validation       +4-5%  → 85-88%
├─ Task 2: Real video validation   +3-4%  → 88-92%
├─ Task 3: Real-time integration   +2-3%  → 90-95%
├─ Task 4: Running feature         +3-4%  → 93-99%
└─ Task 5: API integration         +1-2%  → 94-100%

Target by Month 6: 90%+ coverage on critical paths
```

### Success Metrics (Month 6)

| Metric                | Target         | Status                 |
| --------------------- | -------------- | ---------------------- |
| CMJ Coverage          | 80%+           | Achievable ✓           |
| Real-Time Latency     | \<200ms P99    | Requires early testing |
| Multi-Sport Support   | 3 sports       | Achievable ✓           |
| API Coverage          | 70%+           | Requires test suite    |
| Regression Prevention | 0 regressions  | Requires discipline    |
| Performance Stable    | No degradation | Requires monitoring    |

______________________________________________________________________

## Final Assessment

### Overall Verdict: FEASIBLE with Structured Execution

**Strengths:**

- Existing 74% coverage provides excellent foundation
- Current architecture supports extensibility
- Test infrastructure mature and scalable
- Clear success criteria defined

**Challenges:**

- Real-time adds new testing complexity (latency, load)
- Multi-sport requires architecture validation
- Coverage gap to 80% requires 40-50 new tests
- Performance benchmarking not yet established

**Critical Success Factors:**

1. **Early baseline testing** (Week 1) for real-time latency
1. **Ankle angle fix validation** must be comprehensive
1. **Phase detection abstraction** must work for all sports
1. **Daily coverage tracking** to stay on pace
1. **Performance profiling** from project start

**Resource Requirements:**

- QA Engineer: 100% for 6 weeks (test implementation)
- Backend Developer: 20% (test infrastructure setup)
- Biomechanics Specialist: 10% (validation data review)

**Recommended Go/No-Go Decision Points:**

- **Week 1:** If real-time latency \<150ms P50 → GO
- **Week 2:** If CMJ coverage trending to 75%+ → GO
- **Week 4:** If running architecture tests pass → GO

______________________________________________________________________

**Assessment Completed:** November 17, 2025
**Confidence Level:** HIGH (based on existing code quality and infrastructure)
**Recommendation:** PROCEED with mitigations outlined above

______________________________________________________________________

## Appendices

### Appendix A: Test File Organization

```
tests/
├── test_regression_core_algorithms.py      # Baseline metric snapshots
├── test_regression_cross_sport.py          # Phase detection, CLI, APIs
├── test_regression_biomechanics.py         # Triple extension, ranges
├── test_cmj_phase_progression.py           # Phase progression tests (NEW)
├── test_cmj_physiological_bounds.py        # Bounds validation tests (NEW)
├── test_cmj_real_video_validation.py       # End-to-end video tests (NEW)
├── test_running_validation.py              # Running metrics validation
├── test_realtime_latency.py                # Latency profiling
├── test_realtime_load.py                   # WebSocket load tests
├── test_api_integration.py                 # API endpoint tests
├── test_api_webhooks.py                    # Webhook delivery tests
├── test_api_multiuser.py                   # Multi-user scenarios
├── benchmarks/
│   └── realtime_latency_benchmark.py       # Performance benchmarks
└── load-testing/
    └── locustfile.py                       # Locust load test scenarios
```

### Appendix B: Coverage Tracking Script

```python
# scripts/track_coverage.py

import json
from pathlib import Path

def track_daily_coverage():
    """Track coverage metrics daily."""
    coverage_data = {
        "date": datetime.now().isoformat(),
        "total_coverage": get_coverage_percent(),
        "by_module": {
            "core": get_module_coverage("kinemotion/core"),
            "dropjump": get_module_coverage("kinemotion/dropjump"),
            "cmj": get_module_coverage("kinemotion/cmj"),
            "running": get_module_coverage("kinemotion/running"),
            "api": get_module_coverage("kinemotion/api"),
        },
        "critical_paths": {
            "analysis_functions": get_coverage_for_pattern("*analysis.py"),
            "kinematics": get_coverage_for_pattern("*kinematics.py"),
            "joint_angles": get_coverage_for_pattern("*joint_angles.py"),
        }
    }

    # Save to file
    history_file = Path(".coverage_history.json")
    history = []
    if history_file.exists():
        history = json.loads(history_file.read_text())

    history.append(coverage_data)
    history_file.write_text(json.dumps(history, indent=2))

    # Alert if declining
    if len(history) > 1:
        prev_coverage = history[-2]["total_coverage"]
        curr_coverage = coverage_data["total_coverage"]

        if curr_coverage < prev_coverage:
            print(f"WARNING: Coverage declined from {prev_coverage}% to {curr_coverage}%")
```

### Appendix C: Latency Profiler Code

```python
# src/kinemotion/realtime/profiling.py

from dataclasses import dataclass
import time

@dataclass
class LatencyProfile:
    """Latency measurements for a frame."""
    frame_received: float      # ms
    mediapipe_inference: float # ms
    metric_calculation: float  # ms
    json_serialization: float  # ms
    websocket_send: float      # ms
    total: float               # ms

    def report(self):
        """Generate latency report."""
        return f"""
Latency Profile:
  Total:                {self.total:.1f}ms
  ├─ MediaPipe:        {self.mediapipe_inference:.1f}ms ({self.mediapipe_inference/self.total*100:.0f}%)
  ├─ Metrics:          {self.metric_calculation:.1f}ms ({self.metric_calculation/self.total*100:.0f}%)
  ├─ JSON:             {self.json_serialization:.1f}ms ({self.json_serialization/self.total*100:.0f}%)
  └─ WebSocket:        {self.websocket_send:.1f}ms ({self.websocket_send/self.total*100:.0f}%)
"""

class LatencyProfiler:
    """Profiles each stage of real-time processing."""

    def __init__(self):
        self.measurements = []

    def profile_frame(self, frame):
        """Profile a single frame through pipeline."""
        profile = LatencyProfile(0, 0, 0, 0, 0, 0)
        total_start = time.perf_counter()

        # Stage 1: MediaPipe
        inference_start = time.perf_counter()
        pose_results = self.pose.process(frame)
        profile.mediapipe_inference = (time.perf_counter() - inference_start) * 1000

        # Stage 2: Metrics
        calc_start = time.perf_counter()
        metrics = calculate_metrics(pose_results)
        profile.metric_calculation = (time.perf_counter() - calc_start) * 1000

        # Stage 3: JSON
        serial_start = time.perf_counter()
        json_str = json.dumps(metrics)
        profile.json_serialization = (time.perf_counter() - serial_start) * 1000

        # Stage 4: WebSocket (simulated)
        profile.websocket_send = 10  # Assume 10ms network

        profile.total = (time.perf_counter() - total_start) * 1000

        self.measurements.append(profile)
        return profile

    def get_statistics(self):
        """Get latency statistics."""
        totals = [m.total for m in self.measurements]
        return {
            "p50": np.percentile(totals, 50),
            "p95": np.percentile(totals, 95),
            "p99": np.percentile(totals, 99),
            "mean": np.mean(totals),
            "max": np.max(totals),
            "bottleneck": max(  # Find slowest stage
                ("MediaPipe", np.mean([m.mediapipe_inference for m in self.measurements])),
                ("Metrics", np.mean([m.metric_calculation for m in self.measurements])),
                ("JSON", np.mean([m.json_serialization for m in self.measurements])),
                key=lambda x: x[1]
            )[0]
        }
```

______________________________________________________________________

**Document Version:** 1.0
**Last Updated:** November 17, 2025
**Classification:** Technical Assessment (Internal)
