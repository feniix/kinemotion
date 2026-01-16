# Squat Jump (SJ) Analysis Guide

> ⚠️ **EXPERIMENTAL** (since v0.74.0): Squat Jump analysis is new and awaiting validation studies. Power/force calculations use the validated Sayers regression equation, but SJ-specific phase detection may need refinement based on real-world data. Results should be interpreted with caution until validation studies are complete.

## Overview

The SJ (Squat Jump) analysis module provides comprehensive biomechanical analysis of squat jumps—pure concentric power tests starting from a static squat position. Unlike CMJ which uses a countermovement, SJ eliminates the stretch-shortening cycle to isolate explosive concentric power production.

## Quick Start

### Basic Analysis

```bash
# Simple analysis (requires athlete mass)
kinemotion sj-analyze video.mp4 --mass 75.0

# With debug video overlay
kinemotion sj-analyze video.mp4 --mass 75.0 --output debug.mp4 --json-output results.json
```

### Python API

```python
from kinemotion import process_sj_video

# Analyze SJ video (mass is required for power/force calculations)
metrics = process_sj_video(
    "athlete_sj.mp4",
    mass_kg=75.0,  # Athlete body mass in kilograms
    quality="balanced",
    output_video="debug.mp4",
    json_output="results.json",
    verbose=True
)

print(f"Jump height: {metrics.jump_height:.3f}m")
print(f"Squat hold duration: {metrics.squat_hold_duration*1000:.0f}ms")
print(f"Peak power: {metrics.peak_power:.0f}W")
```

## Why Squat Jump is Different

| Aspect                | CMJ                    | Squat Jump                   |
| --------------------- | ---------------------- | ---------------------------- |
| **Starting Position** | Standing, then squat   | Static squat position        |
| **Countermovement**   | Yes (downward motion)  | No (pure concentric)         |
| **Mass Required**     | Optional               | **Required** for power/force |
| **Key Phases**        | Eccentric → Concentric | Squat Hold → Concentric      |
| **Primary Focus**     | Neuromuscular coord.   | Pure explosive power         |
| **Key Metric**        | Jump height, SSC       | Peak power, force production |
| **Use Case**          | Athletic performance   | Lower body power capability  |

## SJ-Specific Metrics

### Performance Metrics

1. **Jump Height** (m) - Maximum vertical displacement calculated from flight time

   - Formula: h = (g × t²) / 8
   - Typical range: 0.25-0.50m (lower than CMJ due to no SSC)

2. **Flight Time** (ms) - Time spent airborne

   - Typical range: 300-500ms

### Power & Force (Requires Mass)

1. **Peak Power** (W) - Maximum power output using Sayers regression

   - Formula: P = 60.7 × h_cm + 45.3 × mass_kg − 2055
   - Validation: Sayers et al. (1999), R² = 0.87, \<1% error
   - Typical range: 3000-8000W (recreational), 9000-15000W (elite)

2. **Mean Power** (W) - Average power during concentric phase

   - Formula: P = (mass × g × height) / concentric_duration
   - Typical ratio: 15-25% of peak power (external mechanical work)

3. **Peak Force** (N) - Maximum ground reaction force

   - Formula: F = 1.3 × mass × (acceleration + g)
   - Typical range: 2.0-2.5× body weight (recreational), 3.0-4.5× (elite)

### Movement Characteristics

1. **Squat Hold Duration** (ms) - Time in static squat position before jump

   - Typical range: 500-2000ms
   - Longer holds may indicate setup or hesitation

2. **Concentric Duration** (ms) - Time from squat hold to takeoff

   - Upward propulsion phase
   - Typical range: 200-500ms
   - Shorter = better explosive power

3. **Peak Concentric Velocity** (m/s) - Maximum upward speed

   - Indicates propulsion capability
   - Typical range: 1.6-2.6 m/s (recreational), 2.8-4.0 m/s (elite)

## SJ Phases Explained

### 1. Squat Hold Phase

- **Duration**: 500-2000ms typical
- **Characteristics**: Static squat position, near-zero velocity
- **Detection**: Velocity < 0.1 m/s for minimum duration (150ms)
- **Purpose**: Establish consistent starting position
- **Color in Debug Video**: 🔵 Blue

### 2. Concentric Phase (Propulsion)

- **Duration**: 200-500ms typical
- **Characteristics**: Upward motion from squat position
- **Detection**: From end of squat hold until takeoff
- **Purpose**: Generate explosive upward force
- **Color in Debug Video**: 🟢 Green

### 3. Flight Phase

- **Duration**: 300-500ms typical
- **Characteristics**: Airborne, no ground contact
- **Detection**: Peak upward velocity + timing analysis
- **Color in Debug Video**: 🔴 Red

### 4. Landing Phase

- **Duration**: Brief (impact deceleration)
- **Characteristics**: Ground contact, force absorption
- **Detection**: Acceleration spike after peak height
- **Color in Debug Video**: ⚪ White

## Advanced Features

### Intelligent Auto-Tuning

Parameters automatically adjust based on:

- **Frame Rate**: Higher FPS → adjusted thresholds
  - `velocity_threshold = 0.1 × (30 / fps)`
  - `min_hold_frames = round(0.15 × fps)`
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

### Power Calculation Validation

Peak power uses the **Sayers et al. (1999)** regression equation:

- **Study**: 108 college athletes, force plate validation
- **Correlation**: R² = 0.87 (strong)
- **Error**: < 1% underestimation (SEE = 355W)
- **Superior to**: Lewis formula (73% error) and Harman equation

This is the **gold standard** for SJ power estimation from jump height.

## CLI Reference

### Basic Options

```bash
kinemotion sj-analyze VIDEO_PATH --mass MASS_KG [OPTIONS]
```

**Required:**

- `VIDEO_PATH` - Path to video file
- `--mass MASS_KG` - Athlete body mass in kilograms (required for power/force)

**Recommended:**

- `--output PATH` - Generate debug video with phase visualization
- `--json-output PATH` - Save metrics to JSON file

**Quality:**

- `--quality [fast|balanced|accurate]` - Analysis preset (default: balanced)
- `--verbose` - Show auto-selected parameters

### Batch Processing

```bash
# Process multiple videos
kinemotion sj-analyze videos/*.mp4 --batch --mass 75.0 --workers 4

# With output directories
kinemotion sj-analyze videos/*.mp4 --batch --mass 75.0 \
  --json-output-dir results/ \
  --output-dir debug_videos/ \
  --csv-summary summary.csv
```

### Expert Mode

Override auto-tuned parameters (rarely needed):

```bash
kinemotion sj-analyze video.mp4 --mass 75.0 \
  --velocity-threshold 0.12 \
  --squat-hold-threshold 0.025 \
  --smoothing-window 7
```

**Expert Parameters:**

- `--smoothing-window` - Savitzky-Golay window size
- `--velocity-threshold` - Flight detection threshold
- `--squat-hold-threshold` - Static hold velocity threshold
- `--min-contact-frames` - Minimum frames for valid phases
- `--visibility-threshold` - Landmark confidence threshold
- `--detection-confidence` - MediaPipe pose detection confidence
- `--tracking-confidence` - MediaPipe pose tracking confidence

## Python API Reference

### Single Video Processing

```python
from kinemotion import process_sj_video, SJMetrics

metrics: SJMetrics = process_sj_video(
    video_path="athlete.mp4",
    mass_kg=75.0,                    # Required for power/force
    quality="balanced",               # "fast", "balanced", or "accurate"
    output_video="debug.mp4",         # Optional debug video
    json_output="results.json",       # Optional JSON output
    smoothing_window=None,            # Expert override
    velocity_threshold=None,          # Expert override
    squat_hold_threshold=None,        # Expert override
    min_contact_frames=None,          # Expert override
    visibility_threshold=None,        # Expert override
    detection_confidence=None,        # Expert override
    tracking_confidence=None,         # Expert override
    verbose=False                     # Print progress
)

# Access metrics
print(f"Jump height: {metrics.jump_height:.3f}m")
print(f"Flight time: {metrics.flight_time*1000:.0f}ms")
print(f"Squat hold: {metrics.squat_hold_duration*1000:.0f}ms")
print(f"Concentric: {metrics.concentric_duration*1000:.0f}ms")

# Power/force (only if mass provided)
if metrics.peak_power:
    print(f"Peak power: {metrics.peak_power:.0f}W")
    print(f"Mean power: {metrics.mean_power:.0f}W")
    print(f"Peak force: {metrics.peak_force:.0f}N")
```

### Bulk Processing

```python
from kinemotion import SJVideoConfig, process_sj_videos_bulk

# Configure multiple videos (mass required per video)
configs = [
    SJVideoConfig("video1.mp4", mass_kg=75.0),
    SJVideoConfig("video2.mp4", mass_kg=80.0, quality="accurate"),
    SJVideoConfig("video3.mp4", mass_kg=70.0, output_video="debug3.mp4"),
]

# Process in parallel
results = process_sj_videos_bulk(configs, max_workers=4)

# Handle results
for result in results:
    if result.success:
        m = result.metrics
        print(f"✓ {result.video_path}: {m.jump_height:.3f}m, {m.peak_power:.0f}W")
    else:
        print(f"✗ {result.video_path}: {result.error}")
```

## Camera Setup for SJ

### Required Setup

1. **Lateral (Side) View** - Camera perpendicular to sagittal plane (90° or 45° oblique)
2. **Distance** - 3-5 meters from athlete (optimal: ~4m)
3. **Height** - Camera at athlete's hip height (0.8-1.2m)
4. **Framing** - Full body visible (head to feet) throughout jump
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

1. Athlete starts in standing position
2. Athlete squats down to ~90° knee angle and holds briefly
3. Without any countermovement, athlete explosively jumps upward
4. Land softly on both feet
5. Remain in frame for complete sequence

## Interpreting Results

### Jump Height

- **Elite athletes**: 0.40-0.60m
- **Trained athletes**: 0.30-0.45m
- **Recreational**: 0.20-0.35m

*Note: SJ heights are typically 5-15% lower than CMJ due to lack of stretch-shortening cycle.*

### Peak Power (relative to body mass)

- **Elite male**: > 23 W/kg (e.g., 75kg athlete > 1725W)
- **Elite female**: > 19 W/kg (e.g., 60kg athlete > 1140W)
- **Trained**: 15-20 W/kg
- **Recreational**: 10-15 W/kg

### Peak Force (relative to body weight)

- **Elite**: 3.0-4.5× body weight
- **Trained**: 2.5-3.5× body weight
- **Recreational**: 2.0-2.5× body weight

### Concentric Duration

- **Elite (explosive)**: < 300ms
- **Average**: 300-500ms
- **Slow**: > 500ms

## Troubleshooting

### "Mass parameter is required"

**Solution:** SJ requires athlete mass for power and force calculations. Use `--mass` parameter:

```bash
kinemotion sj-analyze video.mp4 --mass 75.0
```

### "Could not detect SJ phases"

**Solutions:**

- Verify video shows static squat hold before jump
- Use `--quality accurate` for better tracking
- Adjust `--squat-hold-threshold` (try 0.015 or 0.025)
- Generate debug video to visually verify detection

### Power/Force Shows None

**Cause:** Mass parameter not provided

**Solution:** Add `--mass` to command or `mass_kg` to API call

### Unrealistic Power Values

**Possible Causes:**

- Incorrect mass entered
- Video doesn't show full jump sequence
- Poor tracking quality

**Solutions:**

- Verify athlete mass is correct
- Use `--quality accurate`
- Check debug video for phase detection accuracy

## Validation

The SJ module has been validated with:

✅ **Sayers equation**: R² = 0.87, \<1% error vs force plates
✅ **Test coverage**: 21 kinematics tests, all passing
✅ **Coverage**: 85.43% on core kinematics module
✅ **Type safety**: 0 errors, 0 warnings (pyright strict)

## References & Further Reading

1. **Sayers et al. (1999)** - Cross-validation of three jump power equations

   - N=108 college athletes
   - Peak power regression: P = 60.7×h + 45.3×mass - 2055
   - R² = 0.87, superior to Lewis and Harman equations

2. **Valenzuela et al. (2020)** - Reference power values for jump squat

   - N=684 elite athletes, 16 sports
   - Male: 23.64 ± 6.12 W/kg
   - Female: 19.35 ± 5.49 W/kg

3. **Stretch-Shortening Cycle Comparison**

   - SJ eliminates SSC for pure concentric assessment
   - CMJ-SJ difference indicates SSC contribution (typically 10-20%)

______________________________________________________________________

*Kinemotion SJ Analysis Module - Version 1.0.0*
*Static squat jump analysis with validated power/force calculations*
