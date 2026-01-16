# Drop Jump (DJ) Analysis Guide

## Overview

The Drop Jump (DJ) analysis module provides comprehensive biomechanical analysis of drop jumps—plyometric exercises where an athlete drops from an elevated platform and immediately jumps upward. This test measures reactive strength and the stretch-shortening cycle (SSC), which are critical for athletic performance in sports requiring explosive movements.

**Key Metric:** Reactive Strength Index (RSI) = Flight Time / Ground Contact Time

## Quick Start

### Basic Analysis

```bash
# Simple analysis (JSON to stdout)
kinemotion dropjump-analyze video.mp4

# With debug video overlay
kinemotion dropjump-analyze video.mp4 --output debug.mp4 --json-output results.json
```

### Python API

```python
from kinemotion import process_dropjump_video

# Analyze DJ video
metrics = process_dropjump_video(
    "athlete_dj.mp4",
    quality="balanced",
    output_video="debug.mp4",
    verbose=True
)

print(f"Ground contact time: {metrics.ground_contact_time*1000:.0f}ms")
print(f"Flight time: {metrics.flight_time*1000:.0f}ms")
print(f"Jump height: {metrics.jump_height:.3f}m")
print(f"RSI: {metrics.jump_height_kinematic / metrics.ground_contact_time:.2f}")
```

## Why Drop Jump is Different

| Aspect                | Drop Jump                | CMJ                         | SJ                    |
| --------------------- | ------------------------ | --------------------------- | --------------------- |
| **Starting Position** | Elevated box (0.3-0.6m)  | Floor level                 | Static squat position |
| **Drop Height**       | Required for context     | Not applicable              | Not applicable        |
| **Key Phases**        | Drop → Contact → Jump    | Standing → Eccentric → Conc | Squat Hold → Conc     |
| **Algorithm**         | Forward search from drop | Backward search from peak   | Squat hold detection  |
| **Primary Focus**     | Reactive strength (RSI)  | Neuromuscular coordination  | Pure concentric power |
| **Key Metric**        | Ground contact time      | Jump height                 | Peak power            |
| **Use Case**          | Plyometric performance   | Athletic performance        | Lower body power      |

## Drop Jump-Specific Metrics

### Performance Metrics

1. **Ground Contact Time (GCT)** (s) - Time from landing to takeoff

   - Represents reactive ability and SSC utilization
   - Formula: contact_end_frame - contact_start_frame
   - Typical range: 150-500ms (shorter = better)

2. **Flight Time** (s) - Time spent airborne after jump

   - Represents explosive power output
   - Formula: (flight_end_frame - flight_start_frame)
   - Typical range: 400-850ms

3. **Jump Height** (m) - Maximum vertical displacement

   - Calculated from flight time: h = (g × t²) / 8
   - Typical range: 0.25-0.65m (recreational), 0.50-1.00m (elite)

4. **Reactive Strength Index (RSI)** - Ratio of flight time to ground contact time

   - Formula: RSI = Flight Time / Ground Contact Time
   - Typical range: 0.70-1.80 (recreational), 1.50-3.50 (elite)
   - **Higher RSI = Better reactive strength**

### Jump Height Variants

The module provides three jump height measurements:

1. **Jump Height (Kinematic)** - Primary metric from flight time

   - Most reliable, validated against force plates
   - Formula: h = (g × t²) / 8

2. **Jump Height (Trajectory)** - From position tracking

   - Calculated from peak vertical position in video
   - Available in `jump_height_trajectory_m`

3. **Jump Height (Normalized)** - Trajectory height in normalized coordinates

   - Useful for relative comparisons across videos

## Drop Jump Phases Explained

### 1. Drop Phase

- **Duration**: Free fall from box (~300-600ms depending on drop height)
- **Characteristics**: Athlete leaves box, falls downward
- **Detection**: Auto-detected from frame where vertical position starts decreasing
- **Manual override**: Use `--drop-start-frame` if auto-detection fails
- **Color in Debug Video**: 🟠 Orange

### 2. Ground Contact Phase

- **Duration**: 150-500ms typical (shorter = better)
- **Characteristics**: Athlete lands on ground, absorbs impact, generates force
- **Detection**: From foot contact (position plateau) until takeoff
- **Purpose**: Eccentric deceleration + concentric propulsion (SSC)
- **Key Metric**: Ground Contact Time (lower = better RSI)
- **Color in Debug Video**: 🟢 Green

### 3. Flight Phase

- **Duration**: 400-850ms typical
- **Characteristics**: Airborne, ascending to peak then descending
- **Detection**: Peak upward velocity + acceleration analysis
- **Purpose**: Measure jump height via flight time
- **Color in Debug Video**: 🔴 Red

### 4. Landing Phase

- **Duration**: Brief (impact deceleration)
- **Characteristics**: Ground contact after jump, force absorption
- **Detection**: Acceleration spike after peak height
- **Color in Debug Video**: ⚪ White

## Interpreting Reactive Strength Index (RSI)

RSI is the gold standard for assessing plyometric ability and reactive strength:

### RSI Values by Athlete Level

| Level             | RSI Range    | Interpretation                  |
| ----------------- | ------------ | ------------------------------- |
| **Elite**         | 2.50 - 3.50+ | Exceptional reactive ability    |
| **Well-Trained**  | 2.00 - 2.50  | Very good plyometric capacity   |
| **Trained**       | 1.50 - 2.00  | Above average reactive strength |
| **Average**       | 1.00 - 1.50  | Normal SSC utilization          |
| **Below Average** | 0.70 - 1.00  | Room for improvement            |
| **Poor**          | < 0.70       | Limited reactive ability        |

### What RSI Measures

**High RSI** indicates:

- Efficient stretch-shortening cycle
- Fast ground contact times
- Good explosive power output
- Strong plyometric ability

**Low RSI** may indicate:

- Slow ground contact (poor SSC)
- Weak explosive power
- Inefficient landing mechanics
- Need for plyometric training

### Ground Contact Time Interpretation

| GCT Range | Interpretation             |
| --------- | -------------------------- |
| < 150ms   | Extreme plyometric ability |
| 150-200ms | Excellent (elite level)    |
| 200-250ms | Very good                  |
| 250-350ms | Good (trained athletes)    |
| 350-500ms | Average                    |
| > 500ms   | Below average              |

## Advanced Features

### Intelligent Auto-Tuning

Parameters automatically adjust based on:

- **Frame Rate**: Higher FPS → adjusted thresholds
  - `velocity_threshold = 0.015 × (30 / fps)`
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

### Forward Search Algorithm

The DJ algorithm works forward from the drop for robust detection:

1. Detect drop start (position begins decreasing)
2. Find ground contact (position plateau/foot contact)
3. Find takeoff (peak upward velocity)
4. Find landing (acceleration spike after peak)

**Why this is better for DJ:**

- Drop start is unambiguous
- Ground contact is distinct from flight
- Minimizes false detections from video artifacts
- Optimized for plyometric movement pattern

### Sub-Frame Precision

- **Interpolation**: Linear interpolation of smooth velocity curves
- **Accuracy**: ±10ms at 30fps (vs ±33ms without interpolation)
- **Method**: Savitzky-Golay derivative-based velocity calculation
- **Benefit**: Precise GCT measurement critical for RSI accuracy

## CLI Reference

### Basic Options

```bash
kinemotion dropjump-analyze VIDEO_PATH [OPTIONS]
```

**Required:**

- `VIDEO_PATH` - Path(s) to video file(s), supports glob patterns

**Recommended:**

- `--output PATH` - Generate debug video with phase visualization
- `--json-output PATH` - Save metrics to JSON file

**Quality:**

- `--quality [fast|balanced|accurate]` - Analysis preset (default: balanced)
- `--verbose` - Show auto-selected parameters

### Expert Mode

Override auto-tuned parameters (rarely needed):

```bash
kinemotion dropjump-analyze video.mp4 \
  --drop-start-frame 45 \
  --velocity-threshold 0.012 \
  --smoothing-window 7
```

**Expert Parameters:**

- `--drop-start-frame` - Manually specify frame where drop begins
- `--smoothing-window` - Savitzky-Golay window size
- `--velocity-threshold` - Flight detection threshold
- `--min-contact-frames` - Minimum frames for valid contact phase
- `--visibility-threshold` - Landmark confidence threshold
- `--detection-confidence` - MediaPipe pose detection confidence
- `--tracking-confidence` - MediaPipe pose tracking confidence

### Batch Processing

```bash
# Process multiple videos
kinemotion dropjump-analyze videos/*.mp4 --batch --workers 4

# With output directories
kinemotion dropjump-analyze videos/*.mp4 --batch \
  --json-output-dir results/ \
  --output-dir debug_videos/ \
  --csv-summary summary.csv
```

## Python API Reference

### Single Video Processing

```python
from kinemotion import process_dropjump_video, DropJumpMetrics

metrics: DropJumpMetrics = process_dropjump_video(
    video_path="athlete.mp4",
    quality="balanced",           # "fast", "balanced", or "accurate"
    output_video="debug.mp4",     # Optional debug video
    json_output="results.json",   # Optional JSON output
    drop_start_frame=None,        # Expert override
    overrides=None,               # Expert parameter overrides
    detection_confidence=None,    # Expert override
    tracking_confidence=None,     # Expert override
    verbose=False                 # Print progress
)

# Access metrics
print(f"Ground contact time: {metrics.ground_contact_time*1000:.0f}ms")
print(f"Flight time: {metrics.flight_time*1000:.0f}ms")
print(f"Jump height: {metrics.jump_height:.3f}m")

# Calculate RSI
if metrics.ground_contact_time and metrics.flight_time:
    rsi = metrics.flight_time / metrics.ground_contact_time
    print(f"RSI: {rsi:.2f}")
```

### Bulk Processing

```python
from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk

# Configure multiple videos
configs = [
    DropJumpVideoConfig("video1.mp4"),
    DropJumpVideoConfig("video2.mp4", quality="accurate"),
    DropJumpVideoConfig("video3.mp4", output_video="debug3.mp4"),
]

# Process in parallel
results = process_dropjump_videos_bulk(configs, max_workers=4)

# Handle results
for result in results:
    if result.success:
        m = result.metrics
        rsi = m.flight_time / m.ground_contact_time if m.ground_contact_time else None
        print(f"✓ {result.video_path}: GCT={m.ground_contact_time*1000:.0f}ms, RSI={rsi:.2f}")
    else:
        print(f"✗ {result.video_path}: {result.error}")
```

## Camera Setup for Drop Jump

### Required Setup

1. **Lateral (Side) View** - Camera perpendicular to sagittal plane
2. **Distance** - 3-5 meters from athlete (optimal: ~4m)
3. **Height** - Camera at athlete's hip height (0.8-1.2m)
4. **Framing** - Full body visible (head to feet) including drop box
5. **Orientation** - Landscape preferred
6. **Stability** - Tripod required (no hand-held)
7. **Frame Rate** - 30+ fps minimum (60fps recommended)
8. **Resolution** - 1080p or higher

### Recommended Camera Angle

**45° Oblique View** (preferred over pure lateral):

- Better separation of left/right feet for MediaPipe tracking
- Clear visibility of hip, knee, and ankle joints
- Reduces occlusion issues during movement
- Validated for accurate jump detection

Pure lateral (90°) may cause MediaPipe to confuse left/right feet due to occlusion.

### Recording Protocol

1. Position camera perpendicular to athlete's sagittal plane
2. Ensure drop box and landing area are clearly visible
3. Athlete stands on elevated box (0.3-0.6m height)
4. Athlete steps off box (not jumps off)
5. Upon landing, immediately jump upward maximally
6. Land softly and remain in frame
7. Video should capture: box → drop → landing → jump → landing

### Drop Height Guidelines

| Drop Height | Use Case                     | Athlete Level          |
| ----------- | ---------------------------- | ---------------------- |
| 0.15m (6")  | Beginners, technique focus   | Novice                 |
| 0.30m (12") | Standard assessment          | Recreational → Trained |
| 0.45m (18") | Advanced plyometric training | Well-trained → Elite   |
| 0.60m (24") | Elite athletes only          | Elite only             |

**Note**: Higher drop heights don't always mean better RSI. Use appropriate height for athlete level.

## Interpreting Results

### Ground Contact Time

- **Elite athletes**: 150-250ms
- **Trained athletes**: 200-350ms
- **Recreational**: 300-500ms

Shorter GCT = better reactive strength and SSC utilization.

### Flight Time

- **Elite athletes**: 650-850ms
- **Trained athletes**: 550-700ms
- **Recreational**: 450-600ms

Longer flight time = better explosive power.

### Jump Height

- **Elite athletes**: 0.50-0.80m
- **Trained athletes**: 0.35-0.55m
- **Recreational**: 0.25-0.45m

### Reactive Strength Index (RSI)

See "Interpreting RSI" section above for detailed interpretation.

## Troubleshooting

### "Could not detect DJ phases"

**Solutions:**

- Verify video shows complete sequence (box → drop → contact → jump → landing)
- Use `--quality accurate` for better tracking
- Manually specify `--drop-start-frame` if auto-detection fails
- Generate debug video to visually verify detection

### Unrealistic Ground Contact Times

**Possible Causes:**

- Video doesn't show clear foot contact
- Poor tracking quality during landing
- Camera angle causing occlusion

**Solutions:**

- Ensure 45° oblique view for better foot visibility
- Use `--quality accurate`
- Check debug video for contact detection

### RSI Seems Too High/Low

**Possible Causes:**

- Incorrect phase detection (contact or flight boundaries)
- Drop height not appropriate for athlete level
- Athlete not performing true drop jump (e.g., stepping down slowly)

**Solutions:**

- Verify athlete drops off box (doesn't step down)
- Check debug video for phase accuracy
- Ensure immediate jump upon landing

### Drop Start Detection Fails

**Cause:** Algorithm can't identify when athlete leaves the box

**Solution:** Use `--drop-start-frame` to manually specify:

```bash
kinemotion dropjump-analyze video.mp4 --drop-start-frame 42
```

Find the frame by opening the video and counting to when the athlete leaves the box.

## Validation

The Drop Jump module has been validated with:

✅ **Physiological bounds**: Comprehensive RSI, GCT, flight time ranges
✅ **Test coverage**: Comprehensive kinematics tests
✅ **Coverage**: 93.03% on kinematics module
✅ **Type safety**: 0 errors, 0 warnings (pyright strict)
✅ **Algorithm**: Forward search optimized for drop jump pattern

## References & Further Reading

1. **Young, W. B. (1995)** - Drop jump performance and plyometric training

   - Validation of RSI as reactive strength measure
   - Ground contact time as key performance indicator

2. **Flanagan, E. P., & Comyns, T. M. (2008)** - The use of contact time and the reactive strength index

   - RSI = Jump Height / Ground Contact Time
   - Alternative formula: RSI = Flight Time / Ground Contact Time

3. **Stretch-Shortening Cycle in Drop Jumps**

   - DJ emphasizes eccentric-concentric coupling
   - Short GCT indicates efficient SSC utilization
   - RSI correlates with explosive sport performance

______________________________________________________________________

*Kinemotion Drop Jump Analysis Module - Version 1.0.0*
*Elevated box drop jump analysis with RSI calculation*
