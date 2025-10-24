# Configuration Parameters Guide

This document explains each configuration parameter available in `dropjump-analyze` and how to tune them for different scenarios.

## Overview

The tool has 6 main configuration parameters divided into 3 categories:

1. **Smoothing** (1 parameter): Reduces jitter in tracked landmarks
2. **Contact Detection** (3 parameters): Determines when feet are on/off ground
3. **Pose Tracking** (2 parameters): Controls MediaPipe's pose detection quality

---

## Smoothing Parameters

### `--smoothing-window` (default: 5)

**What it does:**
Controls the window size for the Savitzky-Golay filter that smooths landmark trajectories over time.

**How it works:**
- Applies a polynomial smoothing filter across N consecutive frames
- Must be an odd number (3, 5, 7, 9, etc.)
- Larger window = smoother trajectories but less responsive to quick movements
- Smaller window = more responsive but potentially noisier

**Technical details:**
- Uses polynomial order 2 (quadratic fit)
- Applied to x and y coordinates of all foot landmarks
- Smoothing happens AFTER all frames are tracked, not in real-time

**When to increase (7, 9, 11):**
- Video has significant camera shake
- Tracking is jittery/noisy
- Athlete moves slowly (long ground contact times)
- Low-quality video or poor lighting
- False contact detections due to landmark jitter

**When to decrease (3):**
- High-quality, stable video
- Very fast movements (reactive jumps)
- Need to capture brief contact phases
- High frame rate video (60+ fps)

**Example:**
```bash
# Noisy video with camera shake
dropjump-analyze video.mp4 --smoothing-window 9

# High-quality 60fps video
dropjump-analyze video.mp4 --smoothing-window 3
```

**Visual effect:**
- Before smoothing: Foot position jumps between frames
- After smoothing: Smooth trajectory curve through the jump

---

## Contact Detection Parameters

### `--velocity-threshold` (default: 0.02)

**What it does:**
The vertical velocity threshold (in normalized coordinates) below which feet are considered stationary/on ground.

**How it works:**
- Velocity is calculated as change in y-position per frame
- Units are in normalized coordinates (0-1, where 1 = full frame height)
- Velocity < threshold = potentially on ground
- Velocity > threshold = in motion (flight)

**Technical details:**
- Calculated: `velocity = abs(y_position[frame] - y_position[frame-1])`
- Applied to average foot position (mean of all visible foot landmarks)
- Works in combination with `min-contact-frames`

**When to decrease (0.01, 0.005):**
- Missing flight phases (everything detected as ground contact)
- Very reactive jumps with minimal ground time
- High frame rate video (motion per frame is smaller)
- Athlete has minimal vertical movement during contact

**When to increase (0.03, 0.05):**
- Detecting false contacts during flight
- Video has significant jitter/noise
- Low frame rate video (larger motion per frame)
- Athlete bounces during ground contact

**Math example:**
```
Video: 1080p (height = 1 in normalized coords)
Frame rate: 30 fps
Threshold: 0.02

0.02 * 1080 pixels = 21.6 pixels per frame
21.6 pixels * 30 fps = 648 pixels/second

So feet moving < 648 pixels/sec vertically = on ground
```

**Example:**
```bash
# Missing short flight phases
dropjump-analyze video.mp4 --velocity-threshold 0.01

# Too many false contacts detected
dropjump-analyze video.mp4 --velocity-threshold 0.03
```

---

### `--min-contact-frames` (default: 3)

**What it does:**
Minimum number of consecutive frames with low velocity required to confirm ground contact.

**How it works:**
- Acts as a temporal filter to remove spurious detections
- If feet are stationary for < N frames, contact is ignored
- Prevents single-frame tracking glitches from being labeled as contact

**Technical details:**
- Applied after velocity thresholding
- Works on consecutive frames only (not total count)
- Example: [1, 1, 0, 1, 1] with min=3 → no valid contact (broken sequence)

**When to increase (5, 7, 10):**
- Video has significant tracking noise/jitter
- Many false brief contacts detected
- Athlete has long ground contact times (>200ms)
- Low confidence in tracking quality

**When to decrease (1, 2):**
- Missing very brief ground contacts
- High-quality tracking with minimal noise
- Very reactive/plyometric jumps
- High frame rate video (60+ fps)

**Frame rate consideration:**
```
30 fps video:
  3 frames = 100ms minimum contact time
  5 frames = 167ms minimum contact time
  10 frames = 333ms minimum contact time

60 fps video:
  3 frames = 50ms minimum contact time
  6 frames = 100ms minimum contact time
```

**Example:**
```bash
# Noisy tracking with false contacts
dropjump-analyze video.mp4 --min-contact-frames 5

# Missing brief contacts in 60fps video
dropjump-analyze video.mp4 --min-contact-frames 2
```

---

### `--visibility-threshold` (default: 0.5)

**What it does:**
Minimum MediaPipe visibility score (0-1) required to trust a landmark for contact detection.

**How it works:**
- MediaPipe assigns each landmark a "visibility" score (0 = not visible, 1 = clearly visible)
- Landmarks below threshold are ignored in contact detection
- Average visibility of foot landmarks determines if frame is valid

**Technical details:**
- Applied to: left/right ankle, left/right heel, left/right foot index
- If average foot visibility < threshold → frame marked as UNKNOWN contact state
- Does NOT affect pose tracking itself, only contact detection logic

**When to decrease (0.3, 0.4):**
- Feet frequently occluded (e.g., long grass, obstacles)
- Side view not perfectly aligned
- Baggy clothing covering feet/ankles
- Many frames marked as UNKNOWN in debug video

**When to increase (0.6, 0.7):**
- Require high confidence in tracking
- Front/back view where feet visibility varies greatly
- Multiple people in frame (need clear foot separation)
- Suspicious tracking results

**MediaPipe visibility score meaning:**
- 0.0-0.3: Landmark likely occluded or outside frame
- 0.3-0.5: Low confidence, possibly visible
- 0.5-0.7: Moderate confidence, probably visible
- 0.7-1.0: High confidence, clearly visible

**Example:**
```bash
# Feet often occluded by equipment
dropjump-analyze video.mp4 --visibility-threshold 0.3

# Need high confidence tracking only
dropjump-analyze video.mp4 --visibility-threshold 0.7
```

---

## Pose Tracking Parameters (MediaPipe)

### `--detection-confidence` (default: 0.5)

**What it does:**
Minimum confidence score (0-1) for MediaPipe to detect a pose in a frame.

**How it works:**
- First stage of MediaPipe Pose: "Is there a person in this frame?"
- If confidence < threshold → no pose detected for that frame
- Higher threshold = fewer false detections but may miss valid poses
- Only applied when MediaPipe needs to detect a NEW pose

**Technical details:**
- Used during initial detection and when tracking is lost
- Once tracking starts, `tracking-confidence` takes over
- Trade-off between false positives (detecting non-humans) and false negatives (missing real poses)

**When to increase (0.6, 0.7, 0.8):**
- Multiple people in frame
- Background objects look like people
- Getting false pose detections
- Need very reliable pose initialization

**When to decrease (0.3, 0.4):**
- Person is far from camera
- Poor lighting conditions
- Unusual camera angle
- Athlete wearing bulky equipment
- Getting "no pose detected" errors

**Example:**
```bash
# Multiple athletes in frame
dropjump-analyze video.mp4 --detection-confidence 0.7

# Poor lighting, distant athlete
dropjump-analyze video.mp4 --detection-confidence 0.3
```

---

### `--tracking-confidence` (default: 0.5)

**What it does:**
Minimum confidence score (0-1) for MediaPipe to continue tracking an existing pose across frames.

**How it works:**
- Second stage of MediaPipe Pose: "Is this still the same person as last frame?"
- If confidence < threshold → tracking is lost, must re-detect pose
- Higher threshold = more likely to re-detect if person moves quickly
- Lower threshold = more persistent tracking even with occlusions

**Technical details:**
- Only used after initial pose detection succeeds
- If tracking fails, falls back to detection stage (using `detection-confidence`)
- Balance between tracking stability and false tracking

**When to increase (0.6, 0.7, 0.8):**
- Tracking jumps between different people/objects
- Tracking continues when person leaves frame
- Need to force re-detection frequently
- Multiple moving objects in scene

**When to decrease (0.3, 0.4):**
- Tracking frequently lost during movement
- Athlete moves very quickly
- Temporary occlusions (e.g., arm passes in front of body)
- Need more stable, persistent tracking

**Relationship with detection-confidence:**
```
High detection + High tracking = Very conservative, frequent re-detection
High detection + Low tracking = Strict initialization, persistent tracking
Low detection + High tracking = Easy initialization, frequent re-detection
Low detection + Low tracking = Lenient overall, stable but risky
```

**Example:**
```bash
# Tracking jumps to wrong person
dropjump-analyze video.mp4 --tracking-confidence 0.7

# Tracking frequently lost during jump
dropjump-analyze video.mp4 --tracking-confidence 0.3
```

---

## Common Scenarios and Recommended Settings

### Scenario 1: High-Quality Studio Video
- 60fps, stable camera, good lighting, clear side view
```bash
dropjump-analyze video.mp4 \
  --smoothing-window 3 \
  --velocity-threshold 0.015 \
  --min-contact-frames 2 \
  --visibility-threshold 0.6 \
  --detection-confidence 0.5 \
  --tracking-confidence 0.5
```

### Scenario 2: Outdoor Handheld Video
- 30fps, camera shake, variable lighting, somewhat noisy
```bash
dropjump-analyze video.mp4 \
  --smoothing-window 7 \
  --velocity-threshold 0.025 \
  --min-contact-frames 4 \
  --visibility-threshold 0.4 \
  --detection-confidence 0.4 \
  --tracking-confidence 0.4
```

### Scenario 3: Low-Quality Smartphone Video
- 30fps, distant view, poor lighting, compression artifacts
```bash
dropjump-analyze video.mp4 \
  --smoothing-window 9 \
  --velocity-threshold 0.03 \
  --min-contact-frames 5 \
  --visibility-threshold 0.3 \
  --detection-confidence 0.3 \
  --tracking-confidence 0.3
```

### Scenario 4: Very Reactive/Fast Jumps
- Need to capture brief flight times and contacts
```bash
dropjump-analyze video.mp4 \
  --smoothing-window 3 \
  --velocity-threshold 0.01 \
  --min-contact-frames 2 \
  --visibility-threshold 0.5 \
  --detection-confidence 0.5 \
  --tracking-confidence 0.5
```

### Scenario 5: Multiple People in Frame
- Need to avoid tracking wrong person
```bash
dropjump-analyze video.mp4 \
  --smoothing-window 5 \
  --velocity-threshold 0.02 \
  --min-contact-frames 3 \
  --visibility-threshold 0.6 \
  --detection-confidence 0.7 \
  --tracking-confidence 0.7
```

---

## Debugging Workflow

### Step 1: Generate Debug Video
Always start with a debug video to visualize what's happening:

```bash
dropjump-analyze video.mp4 --output debug.mp4
```

### Step 2: Identify the Problem

Watch `debug.mp4` and look for:

| Problem | Visual Indication | Parameter to Adjust |
|---------|------------------|---------------------|
| Foot position jumps around | Circle/landmarks jittery | ↑ smoothing-window |
| False flight phases | Red circle during ground contact | ↑ velocity-threshold or ↑ min-contact-frames |
| Missing flight phases | Green circle during jump | ↓ velocity-threshold |
| "UNKNOWN" states everywhere | Frequent state changes | ↓ visibility-threshold |
| No pose detected | No landmarks visible | ↓ detection-confidence |
| Tracking wrong person | Landmarks jump to other person | ↑ tracking-confidence |

### Step 3: Adjust One Parameter at a Time

```bash
# Test hypothesis: missing contacts due to high velocity threshold
dropjump-analyze video.mp4 --output debug2.mp4 --velocity-threshold 0.01

# Compare debug.mp4 vs debug2.mp4
```

### Step 4: Verify with JSON Output

```bash
dropjump-analyze video.mp4 \
  --json-output results.json \
  --smoothing-window 7 \
  --velocity-threshold 0.015

# Check metrics make sense
cat results.json
```

---

## Parameter Interactions

### Smoothing affects velocity calculation
```
High smoothing → smoother velocity → may need lower velocity-threshold
Low smoothing → noisier velocity → may need higher velocity-threshold
```

### Velocity + min-contact-frames work together
```
Strict velocity (low) + lenient frames (low) = sensitive to brief contacts
Lenient velocity (high) + strict frames (high) = only long, clear contacts
```

### Detection + tracking confidence relationship
```
If detection-confidence > tracking-confidence:
  → Will re-detect frequently (less stable tracking)

If tracking-confidence > detection-confidence:
  → Will maintain tracking longer (more stable)
```

---

## Performance Impact

| Parameter | Performance Impact |
|-----------|-------------------|
| smoothing-window | Negligible (post-processing) |
| velocity-threshold | None (simple comparison) |
| min-contact-frames | None (simple counting) |
| visibility-threshold | None (simple comparison) |
| detection-confidence | Medium (affects MediaPipe workload) |
| tracking-confidence | Medium (affects MediaPipe workload) |

**Note:** Higher confidence thresholds can actually improve performance by reducing unnecessary pose detection/tracking attempts.

---

## Advanced Tips

### 1. Frame Rate Matters
Scale velocity-threshold and min-contact-frames based on FPS:
```
30 fps: velocity-threshold = 0.02, min-contact-frames = 3
60 fps: velocity-threshold = 0.01, min-contact-frames = 6
```

### 2. Aspect Ratio Considerations
Velocity threshold is in normalized coordinates:
- Tall videos (9:16 portrait): threshold has more "room" vertically
- Wide videos (16:9 landscape): threshold has less relative space
- Generally doesn't require adjustment, but good to be aware

### 3. Use Debug Video's Frame Numbers
The debug video shows frame numbers. Use these with JSON output:
```json
{
  "contact_start_frame": 10,
  "contact_end_frame": 35,
  "flight_start_frame": 36,
  "flight_end_frame": 45
}
```
Jump to these frames in debug video to verify detection accuracy.

### 4. Iterate Systematically
```bash
# Baseline
dropjump-analyze video.mp4 --output v1.mp4 --json-output v1.json

# Test smoothing
dropjump-analyze video.mp4 --output v2.mp4 --json-output v2.json --smoothing-window 7

# Test velocity
dropjump-analyze video.mp4 --output v3.mp4 --json-output v3.json --smoothing-window 7 --velocity-threshold 0.015

# Compare v1, v2, v3 side-by-side
```

---

## Summary Table

| Parameter | Default | Range | Primary Effect | Adjust When |
|-----------|---------|-------|----------------|-------------|
| `smoothing-window` | 5 | 3-11 (odd) | Trajectory smoothness | Video is jittery or too smooth |
| `velocity-threshold` | 0.02 | 0.005-0.05 | Contact sensitivity | Missing contacts or false detections |
| `min-contact-frames` | 3 | 1-10 | Contact duration filter | Brief false contacts or missing short contacts |
| `visibility-threshold` | 0.5 | 0.3-0.8 | Landmark trust level | Occlusions or need high confidence |
| `detection-confidence` | 0.5 | 0.1-0.9 | Initial pose detection | Multiple people or poor visibility |
| `tracking-confidence` | 0.5 | 0.1-0.9 | Tracking persistence | Tracking lost or wrong person tracked |
