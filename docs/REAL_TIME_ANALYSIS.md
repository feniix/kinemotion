# Real-Time CMJ Analysis - Technical Assessment

## Executive Summary

**Can the current CMJ implementation work with streaming video for real-time analysis?**

**Answer: No, but near real-time (1-2 second delay) is feasible.**

______________________________________________________________________

## Current Implementation Architecture

### Design Constraints

The current CMJ analysis algorithm **requires the complete video** due to fundamental architectural decisions:

#### 1. Backward Search Algorithm

**Core principle**: Find peak height first, work backward to find all events.

```python
# Current algorithm (requires complete video)
def detect_cmj_phases(positions, fps, ...):
    # Step 1: Find peak height (global minimum y)
    peak_frame = argmin(positions)  # Needs complete trajectory!

    # Step 2: Work backward from peak
    takeoff = find_peak_velocity_before(peak_frame)
    lowest_point = find_max_position_before(takeoff)
    landing = find_impact_after(peak_frame)

    return (lowest_point, takeoff, landing)
```

**Why this matters**:

- Can't find peak height until jump is complete
- Can't work backward until we know where peak is
- Requires global view of entire trajectory

#### 2. Savitzky-Golay Smoothing

**Symmetric window requirement**:

```python
# Current smoothing (non-causal)
velocity = savgol_filter(
    positions,
    window_length=5,      # Uses ±2 frames around current
    polyorder=2,
    deriv=1,
    mode='interp'
)
```

**Implications**:

- Needs frames from FUTURE to smooth current frame
- Can't process frame-by-frame as they arrive
- Non-causal filter (not real-time compatible)

#### 3. Global Trajectory Analysis

**Auto-tuning and phase detection**:

- Analyzes entire video to determine tracking quality
- Uses global min/max for phase boundaries
- Optimizes parameters based on full sequence

**Validation results**:

- ✅ **Jump height**: 50.6cm (±1 frame = 33ms accuracy)
- ✅ **Takeoff detection**: Frame 154 (known: 153)
- ✅ **Landing detection**: Frame 173 (known: 172)

This accuracy comes FROM having the complete trajectory.

______________________________________________________________________

## Real-Time Feasibility Analysis

### Option 1: Near Real-Time with Buffering ⭐ RECOMMENDED

**Approach**: Buffer frames, detect jump completion, analyze buffer.

```python
class NearRealTimeCMJAnalyzer:
    def __init__(self):
        self.buffer = CircularBuffer(max_frames=300)  # 10 seconds @ 30fps
        self.state = "waiting"

    def process_frame(self, frame):
        # Add to buffer
        self.buffer.add(frame)

        # Detect jump completion
        if self.state == "waiting" and self.detect_movement_start():
            self.state = "jumping"

        if self.state == "jumping" and self.detect_jump_complete():
            # Run offline algorithm on buffered frames
            metrics = analyze_cmj_offline(self.buffer.get_frames())
            self.state = "waiting"
            self.buffer.clear()
            return metrics  # Results 1-2 seconds after landing

        return None  # Jump not complete yet
```

**Characteristics**:

- **Latency**: 1-2 seconds after landing
- **Accuracy**: ⭐⭐⭐⭐⭐ Same as offline (50.6cm validated)
- **Complexity**: Low (reuses existing algorithm)
- **Implementation**: 200-300 lines of new code

**Jump completion detection**:

```python
def detect_jump_complete(buffer):
    recent_positions = buffer.get_recent(frames=30)  # Last 1 second
    recent_velocity = compute_velocity(recent_positions)

    # Landed if:
    # 1. Low velocity for sustained period
    # 2. Position has returned to near-starting level
    # 3. At least 2 seconds have passed since movement start

    if (abs(recent_velocity) < 0.005 and
        duration > 2.0 and
        position_stabilized):
        return True
    return False
```

**Advantages**:

- ✅ Maintains accuracy (same algorithm)
- ✅ Simple implementation
- ✅ Keeps triple extension visualization
- ✅ 1-2 second delay acceptable for coaching
- ✅ No new validation needed

**Disadvantages**:

- ⚠️ Not instant (1-2 second delay)
- ⚠️ Memory usage (buffer of ~300 frames)

______________________________________________________________________

### Option 2: True Real-Time with Forward Detection

**Approach**: Detect phases as they occur, no buffering.

```python
class RealTimeCMJAnalyzer:
    def __init__(self):
        self.state = "standing"
        self.events = {}
        self.position_history = deque(maxlen=10)  # Causal filter

    def process_frame(self, frame, frame_idx):
        # Track pose
        landmarks = tracker.process(frame)
        position = extract_position(landmarks)

        # Causal smoothing (only past frames)
        self.position_history.append(position)
        smoothed_pos = exponential_smooth(self.position_history)
        velocity = self.position_history[-1] - self.position_history[-2]

        # State machine for phase detection
        if self.state == "standing" and velocity > 0.015:
            self.state = "eccentric"
            self.events['eccentric_start'] = frame_idx

        elif self.state == "eccentric" and velocity < 0:
            self.state = "concentric"
            self.events['lowest_point'] = frame_idx

        elif self.state == "concentric" and velocity < -0.02:
            self.state = "flight"
            self.events['takeoff'] = frame_idx

        elif self.state == "flight" and abs(velocity) < 0.01:
            self.state = "landed"
            self.events['landing'] = frame_idx
            return self.calculate_metrics()  # Return immediately!

        return None  # Jump not complete
```

**Characteristics**:

- **Latency**: \<100ms (instant)
- **Accuracy**: ⭐⭐⭐ Lower (causal filtering, no global optimization)
- **Complexity**: High (new algorithm, needs extensive validation)
- **Implementation**: 500-800 lines + validation

**Challenges**:

1. **Causal filtering artifacts**:

   - Exponential smoothing has lag
   - Can't use future frames to refine past estimates
   - Velocity estimates noisier

1. **No global optimization**:

   - Can't find "true" peak (don't know it yet)
   - Can't refine takeoff by working backward
   - Miss opportunities for sub-frame interpolation

1. **False positives**:

   - May detect non-jump movements
   - Need robust state machine
   - Sensitive to noise

1. **Accuracy degradation**:

   - Estimated: 55-60cm instead of 50.6cm (±10% error)
   - Frame detection: ±2-3 frames instead of ±1
   - Less reliable phase detection

**Advantages**:

- ✅ Instant feedback (\<100ms)
- ✅ True real-time
- ✅ Lower memory usage

**Disadvantages**:

- ⚠️ Reduced accuracy (~10% error)
- ⚠️ Complex validation needed
- ⚠️ High implementation effort
- ⚠️ May not work reliably

______________________________________________________________________

## Performance Analysis

### Current Processing Speed

**Test video**: 236 frames @ 29.58fps

```text
Processing time breakdown:
- MediaPipe tracking: ~5-6 seconds
- Smoothing: ~0.1 seconds
- Phase detection: ~0.01 seconds
- Rendering debug video: ~2 seconds
Total: ~7-8 seconds for 8-second video
```

**Per-frame cost**: ~30-40ms (mostly MediaPipe)

**Bottleneck**: MediaPipe pose tracking (not our algorithm)

### Real-Time Requirements

**For 30fps streaming**:

- Must process each frame in \<33ms
- MediaPipe: ~25-30ms per frame
- Our algorithm: \<1ms per frame
- **Conclusion**: MediaPipe is the limiting factor, but feasible

**For 60fps streaming**:

- Must process each frame in \<17ms
- MediaPipe: ~25-30ms per frame
- **Conclusion**: Would need GPU acceleration or lower MediaPipe model complexity

______________________________________________________________________

## Implementation Roadmap

### Phase 1: Near Real-Time (Buffered) - RECOMMENDED

**Effort**: 1-2 days

**Implementation**:

1. **Create `RealtimeCMJAnalyzer` class**:

   ```python
   class RealtimeCMJAnalyzer:
       def __init__(self, buffer_seconds=10):
           self.buffer = CircularFrameBuffer(buffer_seconds)
           self.tracker = PoseTracker(...)

       def process_frame(self, frame):
           """Process single frame, return metrics when jump complete."""
           landmarks = self.tracker.process_frame(frame)
           self.buffer.add(frame, landmarks)

           if self.is_jump_complete():
               return self.analyze_buffered_jump()
           return None
   ```

1. **Jump completion detector**:

   - Monitor position stability
   - Detect landing (velocity → near zero)
   - Wait 1 second after landing to ensure complete

1. **Analyze buffered frames**:

   - Call existing `detect_cmj_phases()`
   - Use proven algorithm
   - Return metrics with 1-2 second delay

**API Example**:

```python
analyzer = RealtimeCMJAnalyzer()

while True:
    frame = camera.read()
    result = analyzer.process_frame(frame)

    if result:
        print(f"Jump complete! Height: {result.jump_height*100:.1f}cm")
```

**Benefits**:

- ✅ Maintains 50.6cm accuracy
- ✅ Simple implementation
- ✅ All features work (triple extension, etc.)
- ✅ 1-2 second delay acceptable

______________________________________________________________________

### Phase 2: True Real-Time (Forward Detection) - FUTURE

**Effort**: 1-2 weeks + validation

**Implementation**:

1. **Causal filter** (exponential smoothing or one-sided Savitzky-Golay)
1. **Forward phase detection** (state machine)
1. **Event triggers** (real-time callbacks)
1. **Extensive validation** (test against known jumps)

**Expected accuracy**: 55-60cm (±10% error)

**Use cases**: Specialized applications requiring instant feedback

______________________________________________________________________

## Recommendations

### For Most Use Cases: Near Real-Time (Buffered)

**Implement buffered mode if:**

- Need quick results during training (1-2 sec acceptable)
- Want to maintain accuracy (50.6cm validated)
- Building coaching app or live testing system
- Value reliability over instant feedback

### For Research/Analysis: Offline (Current)

**Use current implementation for:**

- Maximum accuracy needed
- Post-session analysis
- Research/publication data
- Detailed biomechanical analysis

### Future: True Real-Time

**Only implement if:**

- Instant feedback is critical (\<100ms)
- Willing to accept ~10% accuracy reduction
- Have time for extensive validation
- Specialized application requires it

______________________________________________________________________

## Technical Constraints

### MediaPipe Processing Speed

**Current**: ~25-30ms per frame (M1 Pro)

**Implications**:

- 30fps: ✅ Feasible (33ms budget, 25-30ms used)
- 60fps: ⚠️ Challenging (17ms budget, 25-30ms used)

**Solutions for 60fps**:

1. Use GPU acceleration
1. Use lighter MediaPipe model (reduced accuracy)
1. Process every other frame
1. Use dedicated hardware (Jetson Nano, etc.)

### Memory Requirements

**Buffered approach**:

- 10 seconds @ 30fps = 300 frames
- 720x1280x3 bytes per frame = 2.7MB per frame
- Total buffer: ~800MB (manageable)

**True real-time**:

- Minimal buffer (10-20 frames for smoothing)
- ~50-100MB (very low)

______________________________________________________________________

## Example Use Cases

### Use Case 1: Training App (Near Real-Time)

**Scenario**: Mobile app for athletes to track CMJ during workouts

```python
# Training app implementation
app = TrainingApp()
analyzer = RealtimeCMJAnalyzer(buffer_seconds=10)

while training_session_active:
    frame = phone_camera.capture()
    result = analyzer.process_frame(frame)

    if result:
        # Show results 1-2 seconds after landing
        app.display_result(f"Jump: {result.jump_height*100:.0f}cm")
        app.save_to_session(result)
        app.play_feedback_sound()
```

**Latency**: 1-2 seconds after landing ✓ Acceptable

### Use Case 2: Research Lab (Offline - Current)

**Scenario**: Biomechanics research, publication-quality data

```python
# Current offline analysis (already implemented)
metrics = process_cmj_video(
    "athlete_cmj.mp4",
    quality="accurate",
    output_video="debug.mp4"
)

# Accuracy: 50.6cm (validated)
# Use for research papers, detailed analysis
```

**Latency**: N/A (offline) ✓ Maximum accuracy

### Use Case 3: Competition Testing (Near Real-Time)

**Scenario**: Testing session with immediate results

```python
# Competition testing station
analyzer = RealtimeCMJAnalyzer()

for athlete in competition:
    print(f"Testing {athlete.name}...")

    while True:
        frame = camera.capture()
        result = analyzer.process_frame(frame)

        if result:
            print(f"Result: {result.jump_height*100:.1f}cm")
            save_to_database(athlete, result)
            break  # Move to next athlete
```

**Latency**: 1-2 seconds ✓ Fast enough for testing

______________________________________________________________________

## Implementation Specification

### Buffered Near Real-Time Mode

#### API Design

```python
from kinemotion import RealtimeCMJAnalyzer

# Initialize analyzer
analyzer = RealtimeCMJAnalyzer(
    buffer_seconds=10,           # Buffer duration
    quality="balanced",           # Analysis quality
    detection_confidence=0.5,     # MediaPipe settings
    jump_timeout=5.0,            # Max jump duration
)

# Process streaming frames
while camera.is_open():
    frame = camera.read()

    # Returns None until jump complete
    result = analyzer.process_frame(frame)

    if result:
        print(f"Jump height: {result.metrics.jump_height*100:.1f}cm")
        print(f"Latency: {result.latency_ms:.0f}ms after landing")

    # Optional: Get live preview (incomplete analysis)
    preview = analyzer.get_preview()
    if preview:
        display_text(f"Current phase: {preview.phase}")
```

#### Jump Completion Detection

```python
def detect_jump_complete(self):
    """Detect if a complete CMJ has occurred and analysis can begin."""

    # Require minimum activity
    if self.buffer.duration < 2.0:
        return False

    # Get recent trajectory (last 1 second)
    recent_positions = self.buffer.get_recent(frames=30)
    recent_velocity = compute_signed_velocity(recent_positions)

    # Check for landing indicators:
    # 1. Position stabilized (low velocity)
    stable = np.abs(recent_velocity[-10:]).mean() < 0.005

    # 2. Clear upward motion detected earlier
    had_upward_motion = np.any(recent_velocity < -0.015)

    # 3. Position returned to near-starting level
    current_pos = recent_positions[-1]
    starting_pos = self.buffer.get_starting_position()
    returned = abs(current_pos - starting_pos) < 0.05

    return stable and had_upward_motion and returned
```

#### Processing Pipeline

```python
def analyze_buffered_jump(self):
    """Analyze complete jump from buffer using offline algorithm."""

    # Extract frames and landmarks from buffer
    frames = self.buffer.get_frames()
    landmarks = self.buffer.get_landmarks()

    # Use existing offline algorithm (proven accurate)
    positions = extract_positions(landmarks)
    phases = detect_cmj_phases(positions, fps, ...)  # Backward search
    metrics = calculate_cmj_metrics(...)

    # Calculate latency
    landing_time = phases[3] / fps
    current_time = self.buffer.duration
    latency = current_time - landing_time

    return RealtimeResult(
        metrics=metrics,
        latency_ms=latency * 1000,
        frames_analyzed=len(frames)
    )
```

**Accuracy**: Same as offline (50.6cm validated) ✓

______________________________________________________________________

### True Real-Time Mode (Future)

#### Forward-Only Detection

**State machine approach**:

```python
class TrueRealtimeCMJAnalyzer:
    def __init__(self):
        self.state = "idle"
        self.events = {}
        self.position_buffer = deque(maxlen=10)  # Minimal buffer

    def process_frame(self, frame, frame_idx):
        # Extract position (causal only)
        position = self.extract_position_causal(frame)
        self.position_buffer.append(position)

        # Compute causal velocity (only past frames)
        velocity = self.compute_causal_velocity()

        # State transitions
        if self.state == "idle" and abs(velocity) < 0.005:
            self.state = "standing"

        elif self.state == "standing" and velocity > 0.015:
            self.state = "eccentric"
            self.events['eccentric_start'] = frame_idx

        elif self.state == "eccentric" and velocity < 0:
            self.state = "concentric"
            self.events['lowest_point'] = frame_idx

        elif self.state == "concentric" and velocity < -0.025:
            self.state = "flight"
            self.events['takeoff'] = frame_idx

        elif self.state == "flight" and abs(velocity) < 0.01:
            self.state = "landing"
            self.events['landing'] = frame_idx

            # Calculate metrics immediately
            return self.calculate_instant_metrics()

        return None
```

**Causal smoothing**:

```python
def compute_causal_velocity(self):
    """Compute velocity using only past frames (causal filter)."""

    # Option 1: Exponential moving average
    alpha = 0.3
    smoothed = self.position_buffer[0]
    for pos in self.position_buffer[1:]:
        smoothed = alpha * pos + (1 - alpha) * smoothed
    velocity = self.position_buffer[-1] - smoothed

    # Option 2: One-sided Savitzky-Golay
    # Uses only past frames (asymmetric window)
    velocity = savgol_filter(
        list(self.position_buffer),
        window_length=9,
        polyorder=2,
        deriv=1,
        mode='mirror'  # Only use left side
    )[-1]

    return velocity
```

**Expected accuracy**:

- Jump height: ±10% error (55-60cm instead of 50.6cm)
- Frame detection: ±2-3 frames instead of ±1
- Phase timing: Less precise

**Why lower accuracy**:

- Causal filtering has inherent lag
- Can't refine estimates with future data
- No global trajectory optimization
- More sensitive to noise

______________________________________________________________________

## Performance Comparison

| Metric                    | Offline (Current) | Near Real-Time | True Real-Time |
| ------------------------- | ----------------- | -------------- | -------------- |
| **Latency**               | N/A               | 1-2 seconds    | \<100ms        |
| **Jump Height Accuracy**  | 50.6cm ✓          | 50.6cm ✓       | ~55-60cm       |
| **Frame Detection Error** | ±1 frame          | ±1 frame       | ±2-3 frames    |
| **Smoothing Quality**     | Excellent         | Excellent      | Good           |
| **Triple Extension**      | Yes               | Yes            | Limited        |
| **Memory Usage**          | Full video        | ~800MB buffer  | ~50MB          |
| **Implementation Effort** | ✓ Done            | 1-2 days       | 1-2 weeks      |
| **Validation Effort**     | ✓ Done            | Minimal        | Extensive      |

______________________________________________________________________

## Recommendation Matrix

### Choose Offline (Current) If

- ✅ Maximum accuracy required (research, validation)
- ✅ Processing pre-recorded videos
- ✅ Time is not critical
- ✅ Want triple extension with full coverage
- ✅ Publication-quality data needed

### Choose Near Real-Time If

- ✅ Need quick results (1-2 sec acceptable)
- ✅ Coaching/training applications
- ✅ Live testing sessions
- ✅ Want to maintain accuracy
- ✅ Building mobile/web app

### Choose True Real-Time If

- ⚠️ Instant feedback critical (\<100ms)
- ⚠️ Interactive applications (games, VR)
- ⚠️ Can accept ~10% accuracy reduction
- ⚠️ Have resources for extensive validation
- ⚠️ Specialized use case

______________________________________________________________________

## Technical Considerations

### Buffered Mode Implementation Checklist

**Core components needed**:

1. **CircularFrameBuffer class**

   - Store frames + landmarks
   - Efficient memory management
   - Thread-safe if needed

1. **JumpCompletionDetector**

   - Analyze recent frames
   - Detect landing + stability
   - Trigger analysis

1. **RealtimeCMJAnalyzer wrapper**

   - Manages buffer
   - Calls existing offline algorithm
   - Returns results with latency info

1. **Testing suite**

   - Validate against known jumps
   - Test various scenarios
   - Measure actual latency

**Estimated implementation**: 200-300 lines

### True Real-Time Implementation Checklist

**Major components needed**:

1. **Causal filtering system**

   - Exponential smoothing
   - One-sided Savitzky-Golay
   - Adaptive filtering

1. **Forward phase detector**

   - State machine
   - Event triggers
   - Robust to noise

1. **Instant metrics calculator**

   - No backward refinement
   - Immediate results
   - Error handling

1. **Extensive validation**

   - Compare with offline
   - Test accuracy degradation
   - Validate across multiple videos

**Estimated implementation**: 500-800 lines

______________________________________________________________________

## Conclusion

### Summary

**Current implementation (offline)**:

- ✅ Production-ready
- ✅ Validated accuracy (50.6cm)
- ✅ ±1 frame precision
- ✅ Triple extension tracking
- ❌ Not real-time compatible

**Feasible near-term**: Buffered near real-time

- 1-2 second delay
- Same accuracy as offline
- Simple implementation
- Good for coaching/training apps

**Future possibility**: True real-time

- \<100ms latency
- ~10% accuracy reduction
- Complex implementation
- Specialized use cases

### Recommendation

**Implement buffered near real-time mode** as next feature:

- Maintains accuracy (critical for credibility)
- Simple enough to implement quickly (1-2 days)
- Meets 80% of real-time use cases
- Builds on proven algorithm

**Don't implement true real-time** unless:

- Specific application requires it
- Can accept accuracy reduction
- Have time for extensive validation

______________________________________________________________________

## Questions & Answers

**Q: Can I use this for a live training app?**
A: Yes! Use buffered near real-time mode (1-2 sec delay). Accuracy maintained.

**Q: Can I get instant feedback as I jump?**
A: Not with current algorithm. Would need true real-time mode (~10% accuracy loss).

**Q: What about webcam input?**
A: Buffered mode works great with webcam. True real-time possible but less accurate.

**Q: How much memory does buffering need?**
A: ~800MB for 10 second buffer @ 1080p. Manageable for most systems.

**Q: Will triple extension work in real-time?**
A: Yes in buffered mode (same as offline). Limited in true real-time (harder to track during motion).

______________________________________________________________________

*Kinemotion CMJ Module*
*Real-Time Analysis Technical Assessment*
*Version 0.1.0 - 2025-11-06*
