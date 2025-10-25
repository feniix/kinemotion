# Configuration Parameters Guide

This document explains each configuration parameter available in `kinemotion dropjump-analyze` and how to tune them for different scenarios.

## Overview

The tool has 11 main configuration parameters divided into 7 categories:

1. **Smoothing** (2 parameters): Reduces jitter in tracked landmarks
2. **Contact Detection** (3 parameters): Determines when feet are on/off ground
3. **Pose Tracking** (2 parameters): Controls MediaPipe's pose detection quality
4. **Calibration** (1 parameter): Enables accurate jump height measurement
5. **Tracking Method** (1 parameter): Choose between CoM or foot-based tracking
6. **Velocity Threshold Mode** (1 parameter): Auto-calibrate or use fixed threshold
7. **Trajectory Analysis** (1 parameter): Enable/disable curvature-based refinement

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
- Uses polynomial order specified by `--polyorder` (default: 2, quadratic fit)
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
kinemotion dropjump-analyze video.mp4 --smoothing-window 9

# High-quality 60fps video
kinemotion dropjump-analyze video.mp4 --smoothing-window 3
```

**Visual effect:**
- Before smoothing: Foot position jumps between frames
- After smoothing: Smooth trajectory curve through the jump

---

### `--polyorder` (default: 2)

**What it does:**
Controls the polynomial order used in the Savitzky-Golay filter for smoothing and derivative calculations.

**How it works:**
- Fits a polynomial of order N to data points in the smoothing window
- Order 2 (quadratic): y = a + bx + cx² - fits parabolas
- Order 3 (cubic): y = a + bx + cx² + dx³ - fits S-curves
- Order 4+ (quartic, quintic): captures more complex patterns
- Higher order polynomials can fit more complex motion but are more sensitive to noise
- Must satisfy: polyorder < smoothing-window (e.g., polyorder=3 requires window≥5)

**Technical details:**
- Applied to landmark smoothing, velocity calculation, and acceleration calculation
- Affects all three: position smoothing, first derivative (velocity), second derivative (acceleration)
- Jump motion is fundamentally parabolic (constant acceleration), so polyorder=2 is mathematically ideal
- Higher orders useful when motion deviates from ideal parabola (e.g., athlete adjusting mid-air)
- Same polyorder used throughout entire analysis pipeline for consistency

**When to use polyorder=2 (quadratic, default):**
- Most jump scenarios (motion follows gravity's parabola)
- Noisy videos (lower orders more robust to noise)
- Standard drop jumps and reactive jumps
- When in doubt - this is the safest choice
- **Recommended for 95% of use cases**

**When to use polyorder=3 (cubic):**
- High-quality studio videos with stable tracking
- Complex motion patterns (athlete adjusting posture mid-flight)
- Very smooth, low-noise tracking data
- Research scenarios requiring maximum precision
- When motion appears to deviate from simple parabola
- Requires larger smoothing window (7+ recommended)

**When to use polyorder=4+ (advanced):**
- Rarely needed in practice
- May overfit to noise rather than capture real motion
- Only for special research cases with very high-quality data
- Requires smoothing-window ≥ polyorder + 2

**Accuracy comparison:**
```
polyorder=2 (typical):
- Baseline accuracy for jump motion
- Robust to noise and tracking errors
- Ideal for parabolic trajectories

polyorder=3 (advanced):
- Accuracy improvement: +1-2% for complex motion
- Better captures non-parabolic adjustments
- More sensitive to noise
- Requires high-quality video

polyorder=4+ (expert):
- Minimal accuracy gain in practice
- Risk of overfitting to noise
- Not recommended for general use
```

**Examples:**
```bash
# Default: polyorder=2 (recommended for most cases)
kinemotion dropjump-analyze video.mp4

# High-quality video with complex motion
kinemotion dropjump-analyze studio.mp4 \
  --polyorder 3 \
  --smoothing-window 7

# Maximum accuracy setup
kinemotion dropjump-analyze video.mp4 \
  --polyorder 3 \
  --smoothing-window 9 \
  --adaptive-threshold \
  --use-com \
  --drop-height 0.40
```

**Validation rules:**
```bash
# Valid combinations
--smoothing-window 5 --polyorder 2  ✓ (2 < 5)
--smoothing-window 7 --polyorder 3  ✓ (3 < 7)
--smoothing-window 9 --polyorder 4  ✓ (4 < 9)

# Invalid combinations
--smoothing-window 5 --polyorder 5  ✗ (5 ≮ 5)
--smoothing-window 3 --polyorder 3  ✗ (3 ≮ 3)
```

**Physical interpretation:**
```
Gravity causes constant downward acceleration
→ Velocity changes linearly with time
→ Position follows quadratic (parabolic) path
→ polyorder=2 is theoretically optimal

Non-ideal factors:
→ Air resistance (higher order needed)
→ Athlete adjustments mid-flight (higher order needed)
→ But these effects are usually small vs measurement noise
→ So polyorder=2 works best in practice
```

**Troubleshooting:**
- If smoothing seems too aggressive with polyorder=3:
  - Reduce to polyorder=2
  - Or increase smoothing-window
- If validation error "polyorder must be < smoothing-window":
  - Increase smoothing-window (e.g., from 5 to 7)
  - Or decrease polyorder
- If results look noisier with polyorder=3:
  - Video quality may not support higher order
  - Revert to polyorder=2
  - Or increase smoothing-window to compensate

**Performance impact:**
- Negligible computational difference between polyorder values
- Same post-processing time regardless of order
- No runtime performance reason to prefer lower orders
- Choose based on accuracy/noise tradeoff only

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
kinemotion dropjump-analyze video.mp4 --velocity-threshold 0.01

# Too many false contacts detected
kinemotion dropjump-analyze video.mp4 --velocity-threshold 0.03
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
kinemotion dropjump-analyze video.mp4 --min-contact-frames 5

# Missing brief contacts in 60fps video
kinemotion dropjump-analyze video.mp4 --min-contact-frames 2
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
kinemotion dropjump-analyze video.mp4 --visibility-threshold 0.3

# Need high confidence tracking only
kinemotion dropjump-analyze video.mp4 --visibility-threshold 0.7
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
kinemotion dropjump-analyze video.mp4 --detection-confidence 0.7

# Poor lighting, distant athlete
kinemotion dropjump-analyze video.mp4 --detection-confidence 0.3
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
kinemotion dropjump-analyze video.mp4 --tracking-confidence 0.7

# Tracking frequently lost during jump
kinemotion dropjump-analyze video.mp4 --tracking-confidence 0.3
```

---

## Calibration Parameters

### `--drop-height` (optional, no default)

**What it does:**
Specifies the height of the drop box/platform in meters to enable calibrated jump height measurement.

**How it works:**
- Measures the actual drop distance from the box to the ground in the video
- Calculates a scale factor to convert normalized coordinates (0-1) to real-world meters
- Applies this scale factor to the jump height measurement
- Significantly improves jump height accuracy from ~71% to ~88%

**Technical details:**
- Only applicable for drop jumps (box → drop → landing → jump)
- Automatically detects drop jump pattern by comparing ground phase elevations
- Uses the initial drop phase to establish the calibration scale factor
- Formula: `scale_factor = drop_height_m / drop_distance_normalized`
- Applied to position-based jump height measurement (not kinematic)

**When to use:**
- Any drop jump where you know the box height
- When accuracy of jump height is important
- When comparing athletes or tracking progress over time
- For research or performance analysis

**When NOT to use:**
- Regular jumps without a drop box (no calibration reference available)
- Unknown drop box height (will calculate but results won't be accurate)
- Video doesn't show the full drop from box to ground

**How to measure your drop box:**
1. Use a tape measure or ruler
2. Measure from top of box surface to ground
3. Convert to meters (divide cm by 100)
4. Examples:
   - 30cm box = 0.30
   - 40cm box = 0.40
   - 60cm box = 0.60

**Accuracy comparison:**
```
Without calibration:
- Uses kinematic method with empirical correction factor
- Accuracy: ~71% (±29% error)
- Example: 38.4cm actual → 27.2cm measured (11.2cm short)

With calibration (--drop-height 0.40):
- Uses position-based measurement with scale factor
- Accuracy: ~88% (±12% error)
- Example: 38.4cm actual → 33.9cm measured (4.5cm short)
```

**Example:**
```bash
# 40cm drop box
kinemotion dropjump-analyze video.mp4 --drop-height 0.40

# 60cm drop box with outputs
kinemotion dropjump-analyze video.mp4 \
  --drop-height 0.60 \
  --json-output metrics.json \
  --output debug.mp4

# Compare calibrated vs uncalibrated
# Without calibration
kinemotion dropjump-analyze video.mp4 --json-output uncalibrated.json

# With calibration
kinemotion dropjump-analyze video.mp4 --drop-height 0.40 --json-output calibrated.json
```

**JSON output with calibration:**
```json
{
  "jump_height_m": 0.339,                      // Primary (calibrated)
  "jump_height_kinematic_m": 0.256,            // Kinematic-only (fallback)
  "jump_height_trajectory_normalized": 0.0845  // Normalized measurement
}
```

**Troubleshooting:**
- If jump height still seems wrong:
  1. Verify box height measurement is accurate
  2. Check that entire drop is visible in video
  3. Ensure camera is stationary (not panning/zooming)
  4. Generate debug video to verify drop phase detection
- If automatic drop jump detection fails:
  - First ground phase must be >5% higher than second ground phase
  - Try adjusting contact detection parameters
  - Check that athlete starts clearly on the box

---

## Tracking Method Parameters

### `--use-com / --use-feet` (default: --use-feet)

**What it does:**
Chooses whether to track the body's center of mass (CoM) or average foot position for vertical motion analysis.

**How it works:**
- **Foot tracking** (`--use-feet`, default): Averages positions of ankle, heel, and foot index landmarks
  - Simple, fast, well-tested baseline method
  - Directly tracks contact points with ground
  - Subject to errors from foot dorsiflexion/plantarflexion during flight

- **CoM tracking** (`--use-com`): Calculates biomechanical center of mass using Dempster's body segment parameters
  - Tracks weighted average of body segments: Head (8%), Trunk (50%), Thighs (20%), Legs (10%), Feet (3%)
  - Represents true body movement according to physics
  - Reduces error from foot movement artifacts during flight
  - More accurate for calculating flight time and jump height

**Technical details:**
- CoM calculation uses 13 body landmarks: nose, shoulders, hips, knees, ankles, heels, feet
- Falls back to hip midpoint if insufficient landmarks visible
- Visibility threshold applied to each landmark (default: 0.5)
- CoM position smoothed using same Savitzky-Golay filter as foot tracking
- Debug video shows CoM as large colored circle with white border

**When to use CoM (`--use-com`):**
- Drop jumps where maximum accuracy is critical
- When foot dorsiflexion/plantarflexion is pronounced during flight
- Research or performance analysis requiring precise measurements
- When comparing against force plate data
- When combined with calibration (`--drop-height`) for maximum accuracy

**When to use feet (`--use-feet`):**
- Quick analysis or exploratory work
- When baseline method is sufficient
- When foot landmarks are more visible than body landmarks
- Troubleshooting or comparison with previous results

**Accuracy comparison:**
```
Foot-based tracking:
- Baseline accuracy: ~88% with calibration
- Affected by foot movement during flight
- Simple, fast, reliable

CoM-based tracking:
- Accuracy improvement: +3-5% over foot tracking
- With calibration: ~91-93% accuracy
- More physically accurate representation
- Slightly more computation
```

**Example:**
```bash
# Use CoM tracking
kinemotion dropjump-analyze video.mp4 --use-com

# CoM with calibration for maximum accuracy
kinemotion dropjump-analyze video.mp4 \
  --use-com \
  --drop-height 0.40 \
  --output debug_com.mp4 \
  --json-output metrics.json

# Compare foot vs CoM tracking
kinemotion dropjump-analyze video.mp4 --use-feet --json-output feet.json
kinemotion dropjump-analyze video.mp4 --use-com --json-output com.json
```

**Debug video visualization:**
- **Feet tracking**: Yellow circles on individual foot landmarks, averaged position colored by state
- **CoM tracking**: Large colored circle at CoM, orange circle at hip midpoint, orange line connecting them

**Troubleshooting:**
- If CoM tracking gives poor results:
  1. Check that body landmarks (shoulders, hips, knees) are visible in video
  2. Lower `--visibility-threshold` if landmarks are partially occluded
  3. Generate debug video to verify CoM position looks reasonable
  4. Try adjusting `--smoothing-window` if CoM trajectory is jittery
- Falls back to feet tracking if insufficient body landmarks visible

---

## Velocity Threshold Mode Parameters

### `--adaptive-threshold / --fixed-threshold` (default: --fixed-threshold)

**What it does:**
Chooses whether to automatically calibrate the velocity threshold from the video or use a fixed value.

**How it works:**
- **Fixed threshold** (`--fixed-threshold`, default): Uses the value specified by `--velocity-threshold` parameter (default: 0.02)
  - Consistent, predictable behavior across videos
  - Requires manual tuning for optimal results
  - Same threshold used for entire video

- **Adaptive threshold** (`--adaptive-threshold`): Automatically calibrates threshold from video baseline
  - Analyzes first 3 seconds of video (assumed athlete standing relatively still on box)
  - Computes velocity for this "stationary" period using Savitzky-Golay derivative
  - Sets threshold as 1.5× the 95th percentile of baseline velocity (noise floor)
  - Bounded between 0.005 (minimum sensitivity) and 0.05 (maximum sensitivity)
  - Adapts to video-specific conditions: camera distance, lighting, frame rate, compression

**Technical details:**
- Baseline duration: 3 seconds (configurable in code)
- Noise floor: 95th percentile of absolute velocity values (robust to outliers)
- Multiplier: 1.5× noise floor (configurable in code)
- Safety bounds: max(1.5 × noise, 0.005), then min(result, 0.05)
- Falls back to 0.02 if video too short (< smoothing window frames)

**When to use adaptive (`--adaptive-threshold`):**
- Videos with varying quality or lighting conditions
- Different camera distances or zoom levels
- Unknown optimal threshold for specific video
- Batch processing multiple videos with different characteristics
- When combined with CoM tracking for maximum accuracy
- First-time analysis of a new video setup

**When to use fixed (`--fixed-threshold`):**
- Consistent video setup (same camera, distance, lighting)
- You've already determined optimal threshold for your setup
- Need reproducible results with same threshold
- Debugging or comparison with previous results
- Baseline motion in video is not stationary (athlete moving)

**Accuracy comparison:**
```
Fixed threshold (manual tuning):
- Requires trial and error to find optimal value
- May be suboptimal for varying conditions
- Consistent across runs

Adaptive threshold (auto-calibration):
- Accuracy improvement: +2-3% by eliminating tuning errors
- Automatically adapts to video conditions
- No manual tuning required
- May vary slightly between runs if baseline motion varies
```

**Example:**
```bash
# Use adaptive threshold
kinemotion dropjump-analyze video.mp4 --adaptive-threshold

# Adaptive + CoM for maximum accuracy
kinemotion dropjump-analyze video.mp4 \
  --adaptive-threshold \
  --use-com \
  --drop-height 0.40 \
  --output debug.mp4 \
  --json-output metrics.json

# Compare fixed vs adaptive
kinemotion dropjump-analyze video.mp4 --fixed-threshold --velocity-threshold 0.02 --json-output fixed.json
kinemotion dropjump-analyze video.mp4 --adaptive-threshold --json-output adaptive.json
```

**Console output with adaptive threshold:**
```
Calculating adaptive velocity threshold...
Adaptive threshold: 0.0178 (auto-calibrated from baseline)
```

**How adaptive threshold adapts:**
```
Scenario 1: Close camera, high resolution
- More pixel movement for same physical motion
- Higher baseline velocity → higher threshold (e.g., 0.025)

Scenario 2: Distant camera, low resolution
- Less pixel movement for same physical motion
- Lower baseline velocity → lower threshold (e.g., 0.012)

Scenario 3: Poor lighting, noisy tracking
- Jittery landmarks → higher baseline velocity
- Higher threshold (e.g., 0.030) filters out noise

Scenario 4: Studio quality, stable tracking
- Smooth landmarks → lower baseline velocity
- Lower threshold (e.g., 0.008) detects subtle motion
```

**Troubleshooting:**
- If adaptive threshold gives poor contact detection:
  1. Verify first 3 seconds show athlete relatively stationary (standing on box)
  2. If athlete is moving during baseline, use `--fixed-threshold` instead
  3. Generate debug video to see where contacts are detected
  4. Check console output to see what threshold was calculated
- If threshold seems too high/low:
  - Threshold bounds: 0.005 ≤ threshold ≤ 0.05
  - Contact detection may need different `--min-contact-frames` setting
  - Try manual `--fixed-threshold` with custom value for comparison

---

## Trajectory Analysis Parameters

### `--use-curvature / --no-curvature` (default: --use-curvature)

**What it does:**
Enables or disables trajectory curvature analysis for refining phase transition timing.

**How it works:**
- **With curvature** (`--use-curvature`, default): Uses acceleration patterns to refine event timing
  - Step 1: Velocity-based detection finds approximate transitions (sub-frame interpolation)
  - Step 2: Acceleration analysis searches ±3 frames for characteristic patterns
  - Step 3: Blends curvature-based refinement (70%) with velocity estimate (30%)
  - Landing detection: Finds maximum acceleration spike (impact deceleration)
  - Takeoff detection: Finds maximum acceleration change (static → upward motion)

- **Without curvature** (`--no-curvature`): Pure velocity-based detection
  - Uses only velocity threshold crossings with sub-frame interpolation
  - Simpler, faster algorithm
  - Still highly accurate with smooth Savitzky-Golay velocity curves

**Technical details:**
- Acceleration computed using Savitzky-Golay second derivative (deriv=2)
- Search window: ±3 frames around velocity-based estimate
- Blending factor: 70% curvature + 30% velocity
- No performance penalty (reuses smoothed trajectory from velocity calculation)
- Independent validation based on physics (Newton's laws)

**When to keep enabled (`--use-curvature`, default):**
- Maximum accuracy desired
- Rapid transitions (reactive jumps, short contact times)
- Noisy velocity estimates need refinement
- When combined with other accuracy features (CoM, adaptive threshold, calibration)
- General use cases (recommended default)

**When to disable (`--no-curvature`):**
- Debugging: isolate velocity-based detection
- Comparison with simpler algorithms
- Extremely smooth, high-quality videos where velocity alone is sufficient
- Research on pure velocity-based methods
- Troubleshooting unexpected transition timing

**Accuracy comparison:**
```
Without curvature (velocity only):
- Uses smooth Savitzky-Golay velocity with sub-frame interpolation
- Highly accurate for most use cases
- Timing precision: ±10ms at 30fps

With curvature (velocity + acceleration):
- Refines timing using physics-based acceleration patterns
- More precise for rapid transitions
- Timing precision: ±5-8ms at 30fps
- Especially effective for landing detection (impact spike)
```

**Physical basis:**
```
Landing impact:
- Large acceleration spike as feet decelerate body on contact
- Peak acceleration marks exact landing moment
- More precise than velocity threshold crossing

Takeoff event:
- Acceleration changes from ~0 (static) to positive (upward)
- Maximum acceleration change marks exact takeoff
- Validates velocity-based estimate

During flight:
- Constant acceleration (gravity ≈ -9.81 m/s²)
- Smooth trajectory, no spikes

On ground (static):
- Near-zero acceleration
- Stationary position
```

**Example:**
```bash
# Default: curvature enabled
kinemotion dropjump-analyze video.mp4

# Explicitly enable curvature
kinemotion dropjump-analyze video.mp4 --use-curvature

# Disable for comparison
kinemotion dropjump-analyze video.mp4 --no-curvature --json-output no_curve.json

# Maximum accuracy: all features enabled
kinemotion dropjump-analyze video.mp4 \
  --use-curvature \
  --adaptive-threshold \
  --use-com \
  --drop-height 0.40 \
  --output debug_max.mp4 \
  --json-output metrics.json
```

**Effect on timing:**
```
Example landing detection at 30fps:

Velocity-based estimate: frame 49.0
  → Velocity drops below threshold at this point

Curvature refinement: frame 46.9
  → Acceleration spike occurs earlier (impact moment)

Blended result: 0.7 × 46.9 + 0.3 × 49.0 = 47.43
  → 2.1 frames (70ms) more accurate timing
```

**Troubleshooting:**
- If curvature refinement gives unexpected results:
  1. Disable with `--no-curvature` to see velocity-only timing
  2. Generate debug video to verify transition points
  3. Check if acceleration patterns are unusual (e.g., soft landing, gradual takeoff)
  4. Try adjusting `--smoothing-window` (affects derivative quality)
- If timing seems off:
  - Curvature only refines by ±3 frames maximum
  - Blending prevents large deviations from velocity estimate
  - Core velocity detection may need parameter tuning

---

## Common Scenarios and Recommended Settings

### Scenario 1: High-Quality Studio Video
- 60fps, stable camera, good lighting, clear side view
```bash
kinemotion dropjump-analyze video.mp4 \
  --smoothing-window 3 \
  --adaptive-threshold \
  --min-contact-frames 2 \
  --visibility-threshold 0.6 \
  --detection-confidence 0.5 \
  --tracking-confidence 0.5
```
**Note:** Using `--adaptive-threshold` instead of manual threshold - will auto-calibrate optimally for this setup.

### Scenario 2: Outdoor Handheld Video
- 30fps, camera shake, variable lighting, somewhat noisy
```bash
kinemotion dropjump-analyze video.mp4 \
  --smoothing-window 7 \
  --adaptive-threshold \
  --min-contact-frames 4 \
  --visibility-threshold 0.4 \
  --detection-confidence 0.4 \
  --tracking-confidence 0.4
```
**Note:** Adaptive threshold handles variable lighting automatically. Higher smoothing compensates for camera shake.

### Scenario 3: Low-Quality Smartphone Video
- 30fps, distant view, poor lighting, compression artifacts
```bash
kinemotion dropjump-analyze video.mp4 \
  --smoothing-window 9 \
  --adaptive-threshold \
  --min-contact-frames 5 \
  --visibility-threshold 0.3 \
  --detection-confidence 0.3 \
  --tracking-confidence 0.3
```
**Note:** Adaptive threshold will automatically adjust to compression noise. High smoothing filters out jitter.

### Scenario 4: Very Reactive/Fast Jumps
- Need to capture brief flight times and contacts
```bash
kinemotion dropjump-analyze video.mp4 \
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
kinemotion dropjump-analyze video.mp4 \
  --smoothing-window 5 \
  --velocity-threshold 0.02 \
  --min-contact-frames 3 \
  --visibility-threshold 0.6 \
  --detection-confidence 0.7 \
  --tracking-confidence 0.7
```

### Scenario 6: Drop Jump with Calibration
- Standard drop jump analysis with 40cm box for accurate jump height
```bash
kinemotion dropjump-analyze video.mp4 \
  --drop-height 0.40 \
  --adaptive-threshold \
  --use-com \
  --smoothing-window 5 \
  --min-contact-frames 3 \
  --visibility-threshold 0.5 \
  --detection-confidence 0.5 \
  --tracking-confidence 0.5 \
  --output debug.mp4 \
  --json-output metrics.json
```
**Note:** Using CoM tracking + adaptive threshold + calibration achieves ~91-93% accuracy.

### Scenario 7: High-Performance Drop Jump Analysis (Maximum Accuracy)
- Research-grade analysis with all accuracy features enabled (~93-96% accuracy)
```bash
kinemotion dropjump-analyze video.mp4 \
  --drop-height 0.40 \
  --adaptive-threshold \
  --use-com \
  --use-curvature \
  --output debug_max.mp4 \
  --json-output metrics.json \
  --smoothing-window 5 \
  --min-contact-frames 3 \
  --visibility-threshold 0.6 \
  --detection-confidence 0.5 \
  --tracking-confidence 0.5
```
**Note:** This combines all accuracy improvements:
- CoM tracking: +3-5% accuracy
- Adaptive threshold: +2-3% accuracy
- Calibration: ~88% baseline → 93-96% total
- Curvature analysis: Enhanced timing precision (enabled by default)

---

## Debugging Workflow

### Step 1: Generate Debug Video
Always start with a debug video to visualize what's happening:

```bash
kinemotion dropjump-analyze video.mp4 --output debug.mp4
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
kinemotion dropjump-analyze video.mp4 --output debug2.mp4 --velocity-threshold 0.01

# Compare debug.mp4 vs debug2.mp4
```

### Step 4: Verify with JSON Output

```bash
kinemotion dropjump-analyze video.mp4 \
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

### CoM tracking works best with adaptive threshold
```
CoM tracking + adaptive threshold:
→ CoM reduces foot movement artifacts
→ Adaptive threshold accounts for smoother CoM trajectories
→ Optimal combination for maximum accuracy
```

### Adaptive threshold makes manual tuning unnecessary
```
With adaptive-threshold:
→ Ignores --velocity-threshold parameter
→ Automatically adapts to video conditions
→ Eliminates need for FPS-based threshold scaling

With fixed-threshold:
→ Uses --velocity-threshold value
→ Requires manual tuning per video setup
→ May need adjustment for different FPS
```

### Curvature + sub-frame interpolation work together
```
Both enabled (default):
→ Velocity interpolation gives sub-frame precision
→ Curvature refines based on acceleration patterns
→ Blended result combines both methods
→ Best timing accuracy

Curvature disabled:
→ Pure velocity-based interpolation
→ Still highly accurate with smooth derivatives
→ Useful for debugging or comparison
```

---

## Performance Impact

| Parameter | Performance Impact |
|-----------|-------------------|
| smoothing-window | Negligible (post-processing) |
| polyorder | Negligible (same algorithm complexity) |
| velocity-threshold | None (simple comparison) |
| min-contact-frames | None (simple counting) |
| visibility-threshold | None (simple comparison) |
| detection-confidence | Medium (affects MediaPipe workload) |
| tracking-confidence | Medium (affects MediaPipe workload) |
| drop-height | None (scaling calculation only) |
| use-com | Negligible (weighted average) |
| adaptive-threshold | Very low (one-time baseline analysis) |
| use-curvature | Negligible (reuses smoothed trajectory) |

**Notes:**
- Higher confidence thresholds can actually improve performance by reducing unnecessary pose detection/tracking attempts
- CoM tracking adds minimal overhead (~5% vs foot tracking) but provides 3-5% accuracy gain
- Adaptive threshold computed once at start, no runtime overhead
- Curvature analysis reuses existing derivatives, effectively free
- Polyorder has no performance impact (polynomial fit complexity is O(window_size), independent of order)

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
kinemotion dropjump-analyze video.mp4 --output v1.mp4 --json-output v1.json

# Test smoothing
kinemotion dropjump-analyze video.mp4 --output v2.mp4 --json-output v2.json --smoothing-window 7

# Test velocity
kinemotion dropjump-analyze video.mp4 --output v3.mp4 --json-output v3.json --smoothing-window 7 --velocity-threshold 0.015

# Compare v1, v2, v3 side-by-side
```

---

## Summary Table

| Parameter | Default | Range | Primary Effect | Adjust When |
|-----------|---------|-------|----------------|-------------|
| `smoothing-window` | 5 | 3-11 (odd) | Trajectory smoothness | Video is jittery or too smooth |
| `polyorder` | 2 | 1-4 | Polynomial fit complexity | High-quality video with complex motion (+1-2%) |
| `velocity-threshold` | 0.02 | 0.005-0.05 | Contact sensitivity | Missing contacts or false detections (ignored if adaptive-threshold enabled) |
| `min-contact-frames` | 3 | 1-10 | Contact duration filter | Brief false contacts or missing short contacts |
| `visibility-threshold` | 0.5 | 0.3-0.8 | Landmark trust level | Occlusions or need high confidence |
| `detection-confidence` | 0.5 | 0.1-0.9 | Initial pose detection | Multiple people or poor visibility |
| `tracking-confidence` | 0.5 | 0.1-0.9 | Tracking persistence | Tracking lost or wrong person tracked |
| `drop-height` | None | 0.1-2.0 | Jump height calibration | Drop jump with known box height |
| `use-com` | feet | com/feet | Tracking method | Want maximum accuracy (+3-5%) |
| `adaptive-threshold` | fixed | adaptive/fixed | Threshold mode | Varying video conditions, unknown optimal threshold |
| `use-curvature` | enabled | enabled/disabled | Timing refinement | Default: keep enabled for best accuracy |
