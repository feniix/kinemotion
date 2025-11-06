# Counter Movement Jump (CMJ) Analysis Guide

## Overview

The CMJ (Counter Movement Jump) analysis module provides comprehensive biomechanical analysis of counter movement jumps performed at floor level. Unlike drop jumps which start from an elevated platform, CMJs begin with the athlete standing on the ground, performing a countermovement (downward squat), and then jumping upward.

## Quick Start

### Basic Analysis

```bash
# Simple analysis (JSON to stdout)
kinemotion cmj-analyze video.mp4

# With debug video overlay (includes triple extension)
kinemotion cmj-analyze video.mp4 --output debug.mp4 --json-output results.json
```

### Python API

```python
from kinemotion import process_cmj_video

# Analyze CMJ video
metrics = process_cmj_video(
    "athlete_cmj.mp4",
    quality="balanced",
    output_video="debug.mp4",
    verbose=True
)

print(f"Jump height: {metrics.jump_height:.3f}m")
print(f"Countermovement depth: {metrics.countermovement_depth:.3f}m")
print(f"Eccentric duration: {metrics.eccentric_duration*1000:.0f}ms")
```

## Why CMJ is Different from Drop Jumps

| Aspect                | Drop Jump               | CMJ                                        |
| --------------------- | ----------------------- | ------------------------------------------ |
| **Starting Position** | Elevated box (0.3-0.6m) | Floor level                                |
| **Drop Height**       | Required parameter      | Not applicable                             |
| **Key Phases**        | Drop → Contact → Jump   | Standing → Eccentric → Concentric → Flight |
| **Primary Focus**     | Reactive strength index | Neuromuscular coordination                 |
| **Key Metric**        | Ground contact time     | Jump height from flight time               |
| **Tracking Method**   | Foot tracking           | Foot tracking                              |
| **Use Case**          | Plyometric performance  | Power output, jump height                  |

## CMJ-Specific Metrics

### Performance Metrics

1. **Jump Height** (m) - Maximum vertical displacement calculated from flight time

   - Formula: h = (g × t²) / 8
   - Typical range: 0.20-0.60m for athletes

1. **Flight Time** (s) - Time spent airborne

   - Typical range: 300-600ms

### Movement Characteristics

1. **Countermovement Depth** (m) - Vertical distance during eccentric phase

   - Represents how deep the athlete squats
   - Typical range: 0.20-0.40m
   - Deeper ≠ always better (optimal depth varies by athlete)

1. **Eccentric Duration** (s) - Time from countermovement start to lowest point

   - Downward phase duration
   - Typical range: 300-800ms

1. **Concentric Duration** (s) - Time from lowest point to takeoff

   - Upward phase duration
   - Typical range: 200-500ms

1. **Total Movement Time** (s) - Full movement from countermovement to takeoff

   - Sum of eccentric + concentric durations
   - Typical range: 500-1200ms

1. **Transition Time** (s) - Duration at lowest point (amortization phase)

   - Brief pause at countermovement bottom
   - Shorter = better stretch-shortening cycle utilization
   - Typical range: 50-150ms

### Velocity Profile

1. **Peak Eccentric Velocity** (m/s) - Maximum downward speed

   - Indicates countermovement speed
   - Typical range: 0.5-1.5 m/s

1. **Peak Concentric Velocity** (m/s) - Maximum upward speed

   - Indicates propulsion force
   - Typical range: 1.5-3.0 m/s

### Triple Extension (in debug video)

1. **Ankle Angle** - Dorsiflexion/plantarflexion
1. **Knee Angle** - Flexion/extension
1. **Hip Angle** - Flexion/extension
1. **Trunk Tilt** - Forward/backward lean

**Note**: Ankle/knee angles have limited visibility in lateral view videos (~20-30% of frames). Trunk angle is available throughout. See docs/TRIPLE_EXTENSION.md for details.

## CMJ Phases Explained

### 1. Standing Phase (Optional)

- **Duration**: Variable (1-3 seconds typical)
- **Characteristics**: Near-zero velocity, stable position
- **Detection**: Velocity \< 0.01 normalized units
- **Note**: May not be present if athlete starts moving immediately

### 2. Eccentric Phase (Countermovement)

- **Duration**: 300-800ms typical
- **Characteristics**: Downward motion, positive velocity
- **Detection**: Velocity crosses countermovement threshold (+0.015 @ 30fps)
- **Purpose**: Store elastic energy in muscles and tendons
- **Color in Debug Video**: 🟠 Orange

### 3. Transition Phase (Amortization)

- **Duration**: 50-150ms typical
- **Characteristics**: Velocity near zero at lowest point
- **Detection**: Velocity crosses from positive to negative
- **Purpose**: Brief coupling between eccentric and concentric phases
- **Importance**: Shorter = better stretch-shortening cycle
- **Color in Debug Video**: 🟣 Purple

### 4. Concentric Phase (Propulsion)

- **Duration**: 200-500ms typical
- **Characteristics**: Upward motion, negative velocity
- **Detection**: From lowest point until takeoff
- **Purpose**: Generate upward force for jump
- **Color in Debug Video**: 🟢 Green

### 5. Flight Phase

- **Duration**: 300-600ms typical
- **Characteristics**: Airborne, no ground contact
- **Detection**: Peak negative velocity + acceleration analysis
- **Color in Debug Video**: 🔴 Red

### 6. Landing Phase

- **Duration**: Brief (1-2 frames)
- **Characteristics**: Impact deceleration
- **Detection**: Acceleration spike detection
- **Color in Debug Video**: ⚪ White

## Advanced Features

### Intelligent Auto-Tuning

Parameters automatically adjust based on:

- **Frame Rate**: Higher FPS → adjusted thresholds
  - `countermovement_threshold = 0.015 × (30 / fps)`
  - `min_contact_frames = round(3 × (fps / 30))`
- **Tracking Quality**: Lower visibility → more smoothing
- **Quality Preset**: fast/balanced/accurate

### Quality Presets

**Fast** - Quick analysis (~50% faster)

- Lower confidence thresholds
- Less smoothing
- Good for batch processing

**Balanced** (Default) - Best for most cases

- Optimal accuracy/speed tradeoff
- Recommended for general use

**Accurate** - Research-grade

- Higher confidence thresholds
- More aggressive smoothing
- Best for publication-quality data

### Sub-Frame Precision

- **Interpolation**: Linear interpolation of smooth velocity curves
- **Accuracy**: ±10ms at 30fps (vs ±33ms without interpolation)
- **Method**: Savitzky-Golay derivative-based velocity calculation
- **Improvement**: 60-70% reduction in timing error

### Backward Search Algorithm

The CMJ algorithm works backward from peak height for robust detection:

1. Find peak height (global minimum position)
1. Find takeoff (peak upward velocity before peak)
1. Find lowest point (maximum position before takeoff)
1. Find landing (acceleration spike after peak)

**Why this is better:**

- Peak height is unambiguous
- All events relative to peak (robust to artifacts)
- Avoids false detections from video start/end
- Matches physical reality

## CLI Reference

### Basic Options

```bash
kinemotion cmj-analyze VIDEO_PATH [OPTIONS]
```

**Required:**

- `VIDEO_PATH` - Path(s) to video file(s), supports glob patterns

**Recommended:**

- `--output PATH` - Generate debug video with triple extension visualization
- `--json-output PATH` - Save metrics to JSON file

**Quality:**

- `--quality [fast|balanced|accurate]` - Analysis preset (default: balanced)
- `--verbose` - Show auto-selected parameters

### Batch Processing

```bash
# Process multiple videos
kinemotion cmj-analyze videos/*.mp4 --batch --workers 4

# With output directories
kinemotion cmj-analyze videos/*.mp4 --batch \
  --json-output-dir results/ \
  --output-dir debug_videos/ \
  --csv-summary summary.csv
```

### Expert Mode

Override auto-tuned parameters (rarely needed):

```bash
kinemotion cmj-analyze video.mp4 \
  --countermovement-threshold 0.012 \
  --velocity-threshold 0.015 \
  --smoothing-window 7
```

**Expert Parameters:**

- `--smoothing-window` - Savitzky-Golay window size
- `--velocity-threshold` - Flight detection threshold (unused, kept for API)
- `--countermovement-threshold` - Eccentric phase threshold (positive value)
- `--min-contact-frames` - Minimum frames for valid phases
- `--visibility-threshold` - Landmark confidence threshold
- `--detection-confidence` - MediaPipe pose detection confidence
- `--tracking-confidence` - MediaPipe pose tracking confidence

## Python API Reference

### Single Video Processing

```python
from kinemotion import process_cmj_video, CMJMetrics

metrics: CMJMetrics = process_cmj_video(
    video_path="athlete.mp4",
    quality="balanced",           # "fast", "balanced", or "accurate"
    output_video="debug.mp4",     # Optional debug video with triple extension
    json_output="results.json",   # Optional JSON output
    smoothing_window=None,        # Expert override
    velocity_threshold=None,      # Expert override
    countermovement_threshold=None, # Expert override
    min_contact_frames=None,      # Expert override
    visibility_threshold=None,    # Expert override
    detection_confidence=None,    # Expert override
    tracking_confidence=None,     # Expert override
    verbose=False                 # Print progress
)

# Access metrics
print(f"Jump height: {metrics.jump_height:.3f}m")
print(f"Countermovement depth: {metrics.countermovement_depth:.3f}m")
print(f"Eccentric/Concentric ratio: {metrics.eccentric_duration / metrics.concentric_duration:.2f}")
```

### Bulk Processing

```python
from kinemotion import CMJVideoConfig, process_cmj_videos_bulk

# Configure multiple videos
configs = [
    CMJVideoConfig("video1.mp4"),
    CMJVideoConfig("video2.mp4", quality="accurate"),
    CMJVideoConfig("video3.mp4", output_video="debug3.mp4"),
]

# Process in parallel
results = process_cmj_videos_bulk(configs, max_workers=4)

# Handle results
for result in results:
    if result.success:
        m = result.metrics
        print(f"✓ {result.video_path}: {m.jump_height:.3f}m")
    else:
        print(f"✗ {result.video_path}: {result.error}")
```

## Camera Setup for CMJ

### Required Setup

1. **Lateral (Side) View** - Camera perpendicular to sagittal plane (90° angle)
1. **Distance** - 3-5 meters from athlete (optimal: ~4m)
1. **Height** - Camera at athlete's hip height (0.8-1.2m)
1. **Framing** - Full body visible (head to feet) throughout jump
1. **Orientation** - Landscape preferred (portrait works but less ideal)
1. **Stability** - Tripod required (no hand-held)
1. **Frame Rate** - 30+ fps minimum (60fps recommended)
1. **Resolution** - 1080p or higher

### Why Lateral View is Required

- CMJ is a vertical movement in the sagittal plane
- Direct measurement of vertical displacement
- Clear visualization of countermovement depth
- Accurate velocity calculations
- Validated in biomechanics research

### Front View Will Not Work

❌ **Do not use front view for CMJ**:

- Cannot measure vertical motion accurately
- Parallax errors from forward/backward movement
- Y-coordinate confounded by distance changes
- Results will be unreliable

See `docs/CAMERA_SETUP.md` for detailed setup guide.

## Interpreting Results

### Jump Height

- **Elite athletes**: 0.40-0.60m
- **Trained athletes**: 0.30-0.45m
- **Recreational**: 0.20-0.35m

### Countermovement Depth

- **Too shallow** (\< 0.15m): May not utilize full potential
- **Optimal** (0.20-0.35m): Good technique
- **Too deep** (> 0.40m): May slow down transition

### Eccentric/Concentric Ratio

- **\< 1.0**: Very fast transition (good for power)
- **1.0-2.0**: Normal range (good technique)
- **> 2.0**: Slow transition (may indicate fatigue)

### Transition Time

- **\< 50ms**: Excellent stretch-shortening cycle
- **50-100ms**: Good
- **100-150ms**: Average
- **> 150ms**: May indicate technique issues

## Troubleshooting

### "Could not detect CMJ phases"

**Solutions:**

- Verify video shows complete jump (from standing through landing)
- Use `--quality accurate` for better tracking
- Adjust `--countermovement-threshold` (try 0.010 or 0.020)
- Generate debug video to visually verify detection

### Unrealistic Jump Heights

**Causes:**

- Camera not level
- Athlete moves out of frame
- Poor tracking quality

**Solutions:**

- Ensure camera is level and stable
- Use `--quality accurate`
- Check that full body is visible in all frames

### Front View Video Gives Wrong Results

**Explanation:** Front view cannot measure vertical displacement accurately due to parallax and foreshortening.

**Solution:** Always use lateral (side) view as documented.

### Triple Extension Shows "N/A"

**Explanation:** MediaPipe has difficulty detecting ankle/knee in pure lateral view.

**Solutions:**

- Use slightly oblique camera angle (80-85° instead of 90°)
- Higher resolution (1080p+)
- Trunk angle always available (100% visibility)

See `docs/TRIPLE_EXTENSION.md` for detailed information on joint angle tracking.

## Validation

The CMJ module has been validated with:

✅ **Real video testing**: samples/cmjs/cmj.mp4
✅ **Jump height**: 50.6cm (±1 frame = 33ms precision)
✅ **Frame detection**: Takeoff 154 (known: 153), Landing 173 (known: 172)
✅ **Test coverage**: 9 CMJ-specific tests, all passing
✅ **Integration**: 70 total tests passing

## References & Further Reading

1. **Countermovement Jump Biomechanics**

   - Linthorne, N. P. (2001). Analysis of standing vertical jumps using a force platform

1. **Stretch-Shortening Cycle**

   - Komi, P. V. (2000). Stretch-shortening cycle: a powerful model to study muscle function

1. **Video-Based Motion Analysis**

   - Validated approach using flight time method (force plate standard)

______________________________________________________________________

*Kinemotion CMJ Analysis Module - Version 0.1.0*
*Floor-level counter movement jump analysis with intelligent auto-tuning*
