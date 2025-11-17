# Computer Vision Implementation Checklist

**For:** Task 3 Real-Time Analysis & Task 4 Running Gait
**Prepared by:** Computer Vision Engineer
**Date:** November 17, 2025

______________________________________________________________________

## TASK 3: Real-Time Web Analysis - Week 1 Critical Actions

### Week 1: Latency Profiling & Architecture Decision (3 days)

- [ ] **Create latency profiler module**

  - File: `src/kinemotion/core/latency_profiler.py`
  - Measure: capture → inference → metrics → network
  - Report format: Per-component breakdown + waterfall chart
  - Integration: Can be used in all tasks for ongoing monitoring

- [ ] **Set up dual-architecture test environment**

  - Client-side: Create minimal React component with MediaPipe TensorFlow.js
  - Server-side: FastAPI endpoint with server-side MediaPipe
  - Network: Simulate real latency with `tc` (traffic control) on mac/linux

- [ ] **Measure actual latencies with profiler**

  - Client-side inference: \_\_\_\_\_ ms (target: \<50ms)
  - Server-side inference: \_\_\_\_\_ ms (target: \<50ms)
  - Network round-trip: \_\_\_\_\_ ms (baseline measurement)
  - Total client path: \_\_\_\_\_ ms (should be \<150ms)
  - Total server path: \_\_\_\_\_ ms (should be \<300ms)

- [ ] **Record decision: Client-side primary vs server-side only**

  - Decision: \[ \] Client-side primary + server fallback | \[ \] Server-side only
  - Rationale: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
  - Sign-off: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

- [ ] **Create task summary for steering committee**

  - Document actual latencies achieved
  - Explain any deviations from assumptions
  - Confirm go-ahead for full implementation

**Output:** Latency profiler tool + architecture decision document

______________________________________________________________________

### Week 2-3: Client-Side Implementation (if chosen)

#### Client Component (React)

- [ ] **WebGL MediaPipe setup (TensorFlow.js)**

  - [ ] Install: `@mediapipe/pose`, `@tensorflow/tfjs-core`, `@tensorflow/tfjs-backend-webgl`
  - [ ] Create: `src/components/PoseDetectionCanvas.tsx`
  - [ ] Load model in worker thread to avoid blocking render
  - [ ] Implement confidence threshold: `min_detection_confidence=0.5`, `min_tracking_confidence=0.45`

- [ ] **Real-time metric calculation in browser**

  - [ ] Move metric functions to TypeScript: `src/utils/metrics.ts`
  - [ ] Implement: vertical velocity, phase detection (for jump types)
  - [ ] Add: Ground contact detection (for running)
  - [ ] Test: Metrics match Python implementation

- [ ] **WebRTC video streaming setup**

  - [ ] WebRTC offer/answer handshake
  - [ ] Data channel for metrics transmission
  - [ ] Connection status indicator
  - [ ] Graceful fallback to server if WebRTC unavailable

- [ ] **UI/UX implementation**

  - [ ] Live pose overlay with landmarks
  - [ ] Real-time metrics display (updating every frame)
  - [ ] Confidence score indicator
  - [ ] Start/stop recording
  - [ ] Download session data

#### Server Component (Python/FastAPI)

- [ ] **WebRTC signaling server**

  - [ ] STUN/TURN configuration for NAT traversal
  - [ ] Offer/answer handshake via WebSocket
  - [ ] ICE candidate handling

- [ ] **Server-side fallback MediaPipe**

  - [ ] FastAPI endpoint: `POST /api/detect-pose`
  - [ ] Accept video frames (base64 or binary)
  - [ ] Return pose landmarks + metrics
  - [ ] Rate limiting: Max 30fps per client

- [ ] **Metric storage & retrieval**

  - [ ] Store session data: person_id, timestamp, metrics, confidence
  - [ ] Retrieve: Full session timeline for comparison
  - [ ] API: `GET /api/session/{session_id}`

- [ ] **Testing & benchmarking**

  - [ ] Latency profile: Client-side path with real network
  - [ ] Load test: 10 simultaneous connections
  - [ ] Edge cases: Network dropout, reconnection, low confidence frames

**Output:** Working real-time demo, latency profile report

______________________________________________________________________

### Week 4-5: Optimization & Hardening

- [ ] **Performance optimization**

  - [ ] Canvas resolution: Test 480p, 720p, 1080p trade-offs
  - [ ] Frame skipping: Only calculate metrics if confidence > threshold
  - [ ] Model caching: LocalStorage/IndexedDB for faster loads
  - [ ] WebWorker: Offload metrics calculation to separate thread

- [ ] **Network optimization**

  - [ ] Metric compression: Send only changed values (delta encoding)
  - [ ] Jitter buffer: Test 1-2 frame buffer vs 3+ for latency
  - [ ] Connection pooling: Reuse WebSocket for multiple streams

- [ ] **Error handling & resilience**

  - [ ] Graceful degradation: Fall back to server if client-side fails
  - [ ] Reconnection: Auto-retry with exponential backoff
  - [ ] Timeouts: Detect stale connections, clean up resources
  - [ ] User feedback: Status messages for connection issues

- [ ] **Security & privacy**

  - [ ] HTTPS/WSS only (no plaintext WebSocket)
  - [ ] CORS configuration: Restrict to expected origins
  - [ ] Authentication: API key or JWT for server access
  - [ ] Video retention: Auto-delete after session (no persistent storage default)

- [ ] **Documentation**

  - [ ] Latency profiling guide
  - [ ] Browser compatibility matrix
  - [ ] Network requirement recommendations
  - [ ] Troubleshooting guide

**Success criteria:**

- [ ] \<200ms E2E latency on modern browsers (Chrome/Firefox/Safari)
- [ ] Graceful fallback to server-side (250-350ms) on older browsers
- [ ] 10 concurrent connections without degradation
- [ ] Load test report documented

______________________________________________________________________

## TASK 4: Running Gait Analysis - Pre-Work & Implementation

### Pre-Work (Dependency on Task 1)

**BLOCKING:** Task 1 must be complete and validated before starting Task 4

- [ ] **Task 1 (Ankle Fix) validation**

  - [ ] Verify: Ankle angle uses foot_index (toe), not heel
  - [ ] Test: Ankle angle increases 30°+ during concentric
  - [ ] Confirm: foot_index visibility is consistently high (>0.6)
  - [ ] Extract: Confidence profiles that foot_index tracking is reliable

- [ ] **Review foot_index usage patterns**

  - [ ] When is foot_index visibility low? (speed, blur, occlusion)
  - [ ] What confidence threshold is safe? (0.5? 0.6? 0.7?)
  - [ ] Document: Reliability characteristics for running application

______________________________________________________________________

### Week 5-6: Gait Cycle Detection (Foundation)

#### Core Algorithm: Gait Cycle Detection

- [ ] **Create `src/kinemotion/running/gait_cycles.py`**

  - [ ] Define: `Cycle` dataclass with contact_frame, flight_start, flight_end
  - [ ] Implement: `detect_ground_contacts(poses) -> List[int]`
    - [ ] Multi-factor detection: height + velocity + acceleration
    - [ ] Height: Heel at minimum Y position
    - [ ] Velocity: Hip vertical velocity approaches zero
    - [ ] Acceleration: Large upward spike on landing
    - [ ] Voting: Landmark must satisfy 2/3 factors
  - [ ] Implement: `group_contacts_to_cycles(contacts) -> List[Cycle]`
  - [ ] Handle: Partial cycles at frame boundaries

- [ ] **Validation against running data**

  - [ ] Test videos: >=3, various running styles (slow/fast, heel/midfoot)
  - [ ] Manual frame-by-frame validation: Do detected contacts match actual footfalls?
  - [ ] Tolerance: ±2 frames acceptable (67ms at 30fps)
  - [ ] Metric: Cycle detection accuracy >= 90%

#### Core Metrics: Cadence & Stride

- [ ] **Implement: Cadence calculation**

  - [ ] File: `src/kinemotion/running/kinematics.py`
  - [ ] Signature: `calculate_cadence(cycles, fps=30) -> float`
  - [ ] Returns: Steps per minute (normal range: 160-180 for optimal)
  - [ ] Handle: Variable FPS across different videos
  - [ ] Test: Cadence calculation against manual count

- [ ] **Implement: Stride length calculation**

  - [ ] Option A (simple): Use pixel-space with height calibration
    - [ ] User inputs height at start
    - [ ] Calibrate: pixels per meter from known height
    - [ ] Calculate: Hip horizontal distance per cycle
  - [ ] Option B (better): Use MediaPipe world_landmarks (3D meters)
    - [ ] Convert: Image coordinates to 3D world coordinates
    - [ ] Advantage: No height input needed, more accurate
    - [ ] Complexity: Requires camera calibration (focal length)
  - [ ] Recommendation: Start with Option A (simpler), add Option B in iteration 2
  - [ ] Test: Stride length plausible for runner (height/2 to height)

______________________________________________________________________

### Week 6-7: Landing Classification & Advanced Metrics

#### Landing Pattern Classification

- [ ] **Create: Landing pattern detector**

  - [ ] File: `src/kinemotion/running/landing_detection.py`

  - [ ] Landmarks needed: heel (29, 30), foot_index (31, 32), ankle (27, 28)

  - [ ] At ground contact frame, compare Y positions (vertical)

  - [ ] Classification logic:

    ```
    heel_y = pose.landmarks[HEEL].y
    toe_y = pose.landmarks[TOE].y
    diff = toe_y - heel_y

    if diff < threshold_heel:
        return 'heel_strike'
    elif diff < threshold_midfoot:
        return 'midfoot_strike'
    else:
        return 'forefoot_strike'
    ```

  - [ ] Determine: Thresholds by running video analysis (typical values: 0.02-0.05 pixels)

  - [ ] Visibility gate: Both landmarks must have visibility > 0.6

- [ ] **Validation dataset**

  - [ ] Collect: 3+ videos with known landing patterns
  - [ ] Manual classification: What landing is actually used?
  - [ ] Test: Does detector match manual classification?
  - [ ] Accuracy target: >= 85%

#### Advanced Metrics (Phase Progression)

- [ ] **Flight time calculation**

  - [ ] From cycle: flight_start frame to flight_end frame
  - [ ] Calculate: Duration in seconds
  - [ ] Metric: Flight time (indicator of vertical power)

- [ ] **Ground contact time (GCT)**

  - [ ] From cycle: contact_frame to flight_start
  - [ ] Calculate: Duration in seconds
  - [ ] Metric: GCT (indicator of loading efficiency)

- [ ] **Vertical velocity at takeoff**

  - [ ] Measure: Hip vertical velocity at flight_start
  - [ ] Use: Signed velocity (direction matters)
  - [ ] Metric: Takeoff velocity (indicator of power)

- [ ] **Knee angle progression**

  - [ ] At contact: Knee angle (bent on impact)
  - [ ] At midstance: Knee angle (extended for stability)
  - [ ] At takeoff: Knee angle (extension for push-off)
  - [ ] Metric: Knee flexion range (should be 40-60° typically)

______________________________________________________________________

### Week 7: Integration & Testing

#### File Structure

- [ ] **New module structure created**

  ```
  src/kinemotion/running/
  ├── __init__.py
  ├── cli.py                 # CLI command: kinemotion running-analyze
  ├── analysis.py            # Main analysis orchestration
  ├── kinematics.py          # Metric calculations
  ├── gait_cycles.py         # Cycle detection
  ├── landing_detection.py   # Landing classification
  ├── debug_overlay.py       # Visualization
  └── phase_detector.py      # Generic phase detection interface
  ```

#### CLI Integration

- [ ] **Register new subcommand**

  - [ ] File: `src/kinemotion/cli.py`
  - [ ] Command: `kinemotion running-analyze video.mp4 [options]`
  - [ ] Options: --quality, --output, --batch
  - [ ] Output: JSON with metrics + video annotation

- [ ] **Parallel processing support**

  - [ ] Batch mode: `kinemotion running-analyze *.mp4 --batch --workers 4`
  - [ ] Uses: Existing batch processing infrastructure

#### Testing

- [ ] **Unit tests**

  - [ ] File: `tests/test_running_gait_cycles.py`
  - [ ] Tests: Cycle detection, cadence, stride, landing classification
  - [ ] Fixtures: Pre-recorded running videos with known metrics
  - [ ] Coverage target: >75% of running module

- [ ] **Integration tests**

  - [ ] End-to-end: Video input → JSON metrics output
  - [ ] Compare: Output format matches drop-jump/CMJ JSON structure
  - [ ] Validation: Metrics are plausible for real runners

- [ ] **Real video validation**

  - [ ] File: `tests/fixtures/running_samples.py`
  - [ ] Sample 1: Elite runner (high cadence, forefoot strike)
  - [ ] Sample 2: Recreational runner (medium cadence, heel strike)
  - [ ] Sample 3: Slow/recovery run (low cadence, long GCT)
  - [ ] Manual validation: Expected metrics recorded, automation checks against them

#### Documentation

- [ ] **Running Biomechanics Guide**
  - [ ] File: `docs/guides/RUNNING_ANALYSIS.md`
  - [ ] Explain: Each metric (cadence, stride, GCT, landing)
  - [ ] Ranges: Typical values for different runner types
  - [ ] Interpretation: What metrics indicate (speed, efficiency, injury risk)
  - [ ] Limitations: What MediaPipe can't detect (internal forces, shoe wear)

______________________________________________________________________

## Architecture & Abstraction Tasks (Supporting Both Task 3 & 4)

### Generic Phase Detection Interface

- [ ] **Create: `src/kinemotion/core/phase_detector.py`**

  ```python
  class PhaseDetector(ABC):
      @abstractmethod
      def detect_phases(self, pose_timeline) -> List[Phase]:
          """Find activity phases in pose timeline"""

  class JumpPhaseDetector(PhaseDetector):
      # Existing CMJ/DropJump logic

  class GaitPhaseDetector(PhaseDetector):
      # New running gait logic
  ```

- [ ] **Benefit:** Enables future sports (rowing, swimming, cycling) to plug in

______________________________________________________________________

### Sport-Specific Confidence Profiles

- [ ] **Create: `src/kinemotion/core/quality_profiles.py`**

  ```python
  QUALITY_PROFILES = {
      'dropjump': {
          'balanced': {
              'detection_confidence': 0.6,
              'tracking_confidence': 0.6,
              'description': 'Stationary, high-quality single event'
          }
      },
      'cmj': {
          'balanced': {
              'detection_confidence': 0.6,
              'tracking_confidence': 0.6,
              'description': 'Stationary, high-quality single event'
          }
      },
      'running': {
          'balanced': {
              'detection_confidence': 0.5,
              'tracking_confidence': 0.45,
              'description': 'Continuous motion, accept jitter'
          }
      }
  }
  ```

- [ ] **Usage:** `process_video(video_path, sport='running', quality='balanced')`

- [ ] **Tests:** Verify profiles load correctly, apply to MediaPipe

______________________________________________________________________

### Visibility Filtering

- [ ] **Create: Enhanced filtering in `src/kinemotion/core/filtering.py`**

  ```python
  def filter_landmarks_by_visibility(
      pose: Pose,
      min_visibility: float = 0.5
  ) -> Pose:
      """Only use high-confidence landmarks"""
      # Update phase detection to use only visible landmarks
      # Skip frames where critical landmarks are occluded
  ```

- [ ] **Integration:** Update phase detection to respect visibility

- [ ] **Tests:** Verify robustness when landmarks are low-confidence

______________________________________________________________________

## Testing & Validation Checklist

### MediaPipe Integration Tests

- [ ] **Confidence threshold testing**
  - [ ] For each sport, verify chosen thresholds work on sample videos
  - [ ] Too strict: Missed detections
  - [ ] Too loose: False positives or jitter
  - [ ] Document final thresholds in code comments

### Running Gait Specific Tests

- [ ] **Gait cycle detection accuracy**

  - [ ] Manual validation: >=90% of cycles detected correctly
  - [ ] Boundary cases: Cycles starting/ending at frame boundaries
  - [ ] Edge cases: Sudden speed changes, turns

- [ ] **Metric plausibility**

  - [ ] Cadence: 160-180 spm for typical run (verify against known runners)
  - [ ] Stride: Height / 2 to height (runner-dependent)
  - [ ] GCT: 0.2-0.5 seconds depending on speed
  - [ ] Landing: Classify heel vs midfoot vs forefoot correctly

### Real-Time Task 3 Tests

- [ ] **Latency benchmarks**

  - [ ] Document E2E latency for client-side path: \_\_\_\_\_ ms
  - [ ] Document E2E latency for server-side fallback: \_\_\_\_\_ ms
  - [ ] Test with 10 concurrent connections
  - [ ] Measure under network constraints (100ms latency injection)

- [ ] **Browser compatibility**

  - [ ] Chrome (latest): \_\_\_\_\_ ms latency
  - [ ] Firefox (latest): \_\_\_\_\_ ms latency
  - [ ] Safari (latest): \_\_\_\_\_ ms latency
  - [ ] Mobile (iOS Safari): \_\_\_\_\_ ms latency

______________________________________________________________________

## Sign-Off Checklist (Before Deployment)

### Task 3 Real-Time Analysis

- [ ] Code review: Architecture approved by tech lead
- [ ] Test coverage: >70% of real-time module
- [ ] Performance: \<200ms on modern browsers, \<300ms fallback
- [ ] Security: HTTPS, CORS, auth configured
- [ ] Documentation: Latency profiling guide, troubleshooting
- [ ] Demo: Working live video analysis demo available

### Task 4 Running Gait Analysis

- [ ] Code review: Gait algorithm approved by biomechanics specialist
- [ ] Test coverage: >75% of running module
- [ ] Validation: 3 real videos with known metrics validated
- [ ] Documentation: Running biomechanics guide published
- [ ] Metrics: Cadence, stride, GCT, landing classification working
- [ ] Error handling: Graceful degradation when confidence is low

______________________________________________________________________

## Dependency Chain Summary

```
Task 1 (Ankle Fix)
    ↓ Validates foot_index reliability
Task 4 (Running Gait) - Landing classification requires foot_index
    ↓
Task 3 (Real-Time) - Can proceed independently
    ├─ Week 1: Latency profiling, architecture decision
    ├─ Week 2-5: Client-side + server implementation
    └─ Result: <200ms on modern browsers

Timeline: All can proceed in parallel after Task 1 validation
```

______________________________________________________________________

**Document:** CV_IMPLEMENTATION_CHECKLIST.md
**Purpose:** Detailed implementation guide for CV engineer
**Status:** Ready for use
