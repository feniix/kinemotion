# Configuration Parameters Guide

**⚠️ NOTICE:** **This document is mostly DEPRECATED as of November 2025.**

Kinemotion now features **intelligent auto-tuning** that automatically optimizes all parameters based on video characteristics (FPS, tracking quality). Most users no longer need to manually adjust parameters.

**For current usage, see:**

- README.md - Simplified interface with auto-tuning
- CLAUDE.md - Auto-tuning system documentation

**This document is preserved for:**

- Expert users who need to override auto-tuned values (use `--expert` mode)
- Understanding what each parameter does internally
- Debugging when auto-tuning doesn't work as expected

______________________________________________________________________

## Quick Reference (Auto-Tuned Values)

**You don't need to set these manually!** The tool auto-detects:

| Parameter            | 30fps Auto | 60fps Auto | 120fps Auto | Formula                      |
| -------------------- | ---------- | ---------- | ----------- | ---------------------------- |
| `velocity-threshold` | 0.020      | 0.010      | 0.005       | 0.02 × (30/fps)              |
| `min-contact-frames` | 3          | 6          | 12          | round(3 × (fps/30))          |
| `smoothing-window`   | 5          | 3          | 3           | 5 if fps≤30 else 3           |
| `outlier-rejection`  | ✅         | ✅         | ✅          | Always enabled               |
| `use-curvature`      | ✅         | ✅         | ✅          | Always enabled               |
| `polyorder`          | 2          | 2          | 2           | Always 2 (optimal for jumps) |

**Quality adjustments** (based on MediaPipe visibility):

- High quality (visibility > 0.7): Minimal smoothing, no bilateral filter
- Medium quality (0.4-0.7): +1 smoothing adjustment, enable bilateral
- Low quality (\< 0.4): +2 smoothing adjustment, enable bilateral, lower confidence

**Use `--verbose` to see what was auto-selected for your video!**

______________________________________________________________________

## Batch Processing Parameters

These parameters control batch processing mode when analyzing multiple videos:

| Parameter           | Type | Default | Description                                                       |
| ------------------- | ---- | ------- | ----------------------------------------------------------------- |
| `--batch`           | flag | auto    | Explicitly enable batch mode (auto-enabled with multiple files)   |
| `--workers`         | int  | 4       | Number of parallel workers for ProcessPoolExecutor                |
| `--output-dir`      | path | -       | Directory for debug videos (auto-named: `{video_name}_debug.mp4`) |
| `--json-output-dir` | path | -       | Directory for JSON metrics (auto-named: `{video_name}.json`)      |
| `--csv-summary`     | path | -       | Export aggregated results to CSV file                             |

**Usage:**

```bash
# Batch process with all outputs
kinemotion dropjump-analyze videos/*.mp4 --batch \
  --workers 4 \
  --json-output-dir results/ \
  --output-dir debug_videos/ \
  --csv-summary summary.csv
```

**Notes:**

- Batch mode is automatically enabled when multiple video paths are provided
- All analysis parameters (quality, smoothing-window, etc.) apply to all videos in batch
- Progress is shown in real-time: `[3/10] ✓ athlete3.mp4 (2.1s)`
- Summary statistics are calculated across successful videos
- CSV includes all videos (successful and failed)

**Python API Alternative:**

For more control, use the Python API:

```python
from kinemotion import DropJumpVideoConfig, process_dropjump_videos_bulk

configs = [
    DropJumpVideoConfig("video1.mp4", quality="fast"),
    DropJumpVideoConfig("video2.mp4", quality="accurate"),  # Different settings per video
]

results = process_dropjump_videos_bulk(configs, max_workers=4)
```

See `examples/bulk/README.md` for complete API documentation.

______________________________________________________________________

## Legacy Manual Parameter Reference

**⚠️ Important:** **kinemotion accuracy is currently unvalidated**. These parameter recommendations are based on theoretical considerations and industry best practices, not empirically verified performance.

This section explains each parameter for expert users who need manual control.

**Note**: Drop jump analysis uses foot-based tracking. The `--use-com` and `--adaptive-threshold` features (available in `core/` modules) require longer videos (~5+ seconds) with a 3-second standing baseline, making them unsuitable for typical drop jump videos (~3 seconds total).

**Accuracy Disclaimer**: All parameter tuning recommendations assume kinemotion provides accurate measurements. Actual accuracy performance is currently unknown and requires validation against gold standards (force plates, 3D motion capture).

______________________________________________________________________

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

````bash
# Noisy video with camera shake
kinemotion dropjump-analyze video.mp4 --smoothing-window 9

# High-quality 60fps video
kinemotion dropjump-analyze video.mp4 --smoothing-window 3
```text

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

**Performance comparison:**

```text
polyorder=2 (typical):
- Baseline performance for jump motion
- Robust to noise and tracking errors
- Ideal for parabolic trajectories

polyorder=3 (advanced):
- Theoretically better for complex motion (⚠️ unvalidated)
- Better captures non-parabolic adjustments
- More sensitive to noise
- Requires high-quality video

polyorder=4+ (expert):
- Minimal practical benefit
- Risk of overfitting to noise
- Not recommended for general use
```text

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
  --smoothing-window 9
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
```text

**Physical interpretation:**

```text
Gravity causes constant downward acceleration
→ Velocity changes linearly with time
→ Position follows quadratic (parabolic) path
→ polyorder=2 is theoretically optimal

Non-ideal factors:
→ Air resistance (higher order needed)
→ Athlete adjustments mid-flight (higher order needed)
→ But these effects are usually small vs measurement noise
→ So polyorder=2 works best in practice
```text

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

## Advanced Filtering Parameters

### `--outlier-rejection` / `--no-outlier-rejection` (default: --outlier-rejection)

**What it does:**
Detects and removes MediaPipe tracking glitches (outliers) before smoothing, replacing them with interpolated values.

**How it works:**

- Applies two complementary outlier detection methods:
  1. **RANSAC-based polynomial fitting**: Fits a polynomial to sliding windows of data and identifies points that deviate significantly from the fit
  2. **Median filtering**: Detects points that differ significantly from the local median
- Outliers are replaced with linear interpolation from neighboring valid points
- Applied to each landmark coordinate (x, y) independently
- Runs BEFORE Savitzky-Golay smoothing in the processing pipeline

**Technical details:**

- RANSAC parameters:
  - Window size: 15 frames
  - Threshold: 0.02 (normalized coordinates)
  - Min inliers: 70% of window must fit the model
- Median filter parameters:
  - Window size: 5 frames
  - Threshold: 0.03 (normalized coordinates)
- Combines both methods (marks as outlier if either detects it)
- Interpolation method: Linear between nearest valid neighbors

**When to use --outlier-rejection (default, recommended):**

- All typical use cases (enabled by default for good reason)
- Videos with occasional tracking glitches or jumps
- Medium to low quality video
- Camera shake or motion blur
- Partially occluded landmarks
- Athlete wearing loose clothing
- Improves robustness across varying video quality

**When to use --no-outlier-rejection:**

- Debugging or testing raw MediaPipe output
- Perfect tracking quality (rare in real-world videos)
- Academic comparison studies
- Performance-critical applications (saves ~5-10% processing time)
- When you want to see unfiltered tracking errors

**Example:**

```bash
# Standard usage (outlier rejection enabled by default)
kinemotion dropjump-analyze video.mp4

# Explicitly enable outlier rejection
kinemotion dropjump-analyze video.mp4 --outlier-rejection

# Disable for debugging
kinemotion dropjump-analyze video.mp4 --no-outlier-rejection --output debug.mp4
```text

**Visual effect:**

- Without outlier rejection: Occasional position "jumps" in debug video (landmark suddenly shifts 5-10cm then returns)
- With outlier rejection: Smooth trajectory throughout the jump, glitches removed

**Effect:**

- Removes tracking glitches for more consistent measurements
- Most beneficial for videos with tracking issues
- Minimal effect on perfect tracking (no glitches to remove)

**Common scenarios:**

- **Scenario 1: Loose clothing**
  - Problem: Ankle landmark occasionally jumps to clothing edge
  - Solution: RANSAC detects deviation from smooth trajectory, replaces with interpolation
- **Scenario 2: Motion blur**
  - Problem: Landing causes blur, landmark position uncertainty
  - Solution: Median filter catches brief spikes, smooths transition
- **Scenario 3: Occlusion**
  - Problem: One foot temporarily hidden behind other
  - Solution: Both methods detect inconsistent position, use valid frames for interpolation

**Troubleshooting:**

- If trajectories look "too smooth" (missing real motion):
  - Outlier rejection is not the cause (operates at 0.02-0.03 threshold, small deviations)
  - Check --smoothing-window instead (probably too large)
- If still seeing tracking glitches in output:
  - Outlier rejection may be too conservative for your video
  - This is rare; glitches might be in velocity calculation instead
  - Try increasing --smoothing-window to further reduce noise
- If metrics seem unrealistic:
  - Outlier rejection is likely helping, not hurting
  - Check other parameters (velocity-threshold, min-contact-frames)

**Performance impact:**

- Adds ~5-10% to processing time
- O(n × window_size) complexity per landmark
- Negligible impact on overall analysis time (most time spent in MediaPipe tracking)

---

### `--bilateral-filter` / `--no-bilateral-filter` (default: --no-bilateral-filter)

**What it does:**
Uses bilateral temporal filtering instead of Savitzky-Golay smoothing to preserve sharp transitions (landing/takeoff) while smoothing noise.

**How it works:**

- **Standard Savitzky-Golay** (default): Uniform smoothing across all frames
  - Smooths based only on temporal distance
  - Treats all frames equally regardless of motion
  - May blur sharp transitions like landing impact

- **Bilateral filtering** (--bilateral-filter): Edge-preserving smoothing
  - Weights each neighbor by TWO factors:
    1. **Spatial weight**: Temporal distance (like standard smoothing)
    2. **Intensity weight**: Position similarity (preserves edges)
  - Frames with similar positions get high weight (smooth together)
  - Frames with different positions get low weight (preserve transition)
  - Landing/takeoff edges remain sharp, noise in smooth regions is reduced

**Technical details:**

- Bilateral filter parameters:
  - Window size: 9 frames (automatically adjusted to odd)
  - Sigma spatial: 3.0 (controls temporal weighting)
  - Sigma intensity: 0.02 (controls position difference weighting)
- Replaces Savitzky-Golay smoothing when enabled (not additive)
- Applied to landmark positions before velocity/acceleration calculation
- More computationally expensive than Savitzky-Golay (~2x time)

**Mathematical formulation:**

```text
For each frame i:
  For each neighbor j in window:
    spatial_weight[j] = exp(-(i-j)² / (2 × sigma_spatial²))
    intensity_weight[j] = exp(-(pos[j]-pos[i])² / (2 × sigma_intensity²))
    combined_weight[j] = spatial_weight[j] × intensity_weight[j]

  smoothed_pos[i] = Σ(combined_weight[j] × pos[j]) / Σ(combined_weight[j])
```text

**When to use --bilateral-filter:**

- Videos with rapid state transitions (landing, takeoff)
- High-quality video where preserving timing precision is critical
- Research scenarios requiring maximum event timing accuracy
- When Savitzky-Golay smoothing blurs important transitions
- Drop jumps with very brief ground contact times
- Reactive jumps with explosive movements

**When to use --no-bilateral-filter (default):**

- Most typical use cases
- Standard video quality
- When processing speed matters
- Proven baseline method (Savitzky-Golay)
- When results are already good with default settings
- Lower-quality videos (bilateral may amplify noise)

**Example:**

```bash
# Use bilateral filter for high-quality video
kinemotion dropjump-analyze studio_video.mp4 \
  --bilateral-filter \
  --outlier-rejection \
  --output debug.mp4

# Compare bilateral vs standard smoothing
kinemotion dropjump-analyze video.mp4 --output standard.mp4
kinemotion dropjump-analyze video.mp4 --bilateral-filter --output bilateral.mp4
```text

**Visual effect:**

- Standard smoothing: Landing transition spread over 2-3 frames, smooth curve
- Bilateral filtering: Landing transition sharp at 1-2 frames, preserves impact timing

**Effect:**

- Preserves timing precision for rapid transitions
- Most beneficial for high-quality videos with sharp state changes
- May amplify noise in low-quality videos

**Trade-offs:**

- **Advantages:**
  - Preserves sharp transitions (landing, takeoff)
  - More accurate event timing
  - Better for rapid movements
  - Physics-aware (respects motion discontinuities)

- **Disadvantages:**
  - Experimental feature (less tested than Savitzky-Golay)
  - ~2x slower processing
  - May preserve noise in low-quality videos
  - More parameters to tune (sigma_spatial, sigma_intensity)
  - Less predictable behavior across varying video quality

**Interaction with other parameters:**

- **Compatible with:**
  - --outlier-rejection: Apply together for best results (outlier removal → bilateral smoothing)
  - --use-curvature: Bilateral preserves transitions for accurate timing refinement

- **Replaces:**
  - --smoothing-window and --polyorder have no effect when bilateral filter is enabled
  - Bilateral uses its own window size (9 frames) and weighting scheme

**Common scenarios:**

- **Scenario 1: Explosive reactive jump**
  - Problem: Takeoff happens in <2 frames, Savitzky-Golay smooths it to 4 frames
  - Solution: Bilateral preserves sharp takeoff, accurate flight time measurement

- **Scenario 2: Hard landing impact**
  - Problem: Landing deceleration spread over 3 frames, timing imprecise
  - Solution: Bilateral maintains sharp landing transition, better contact time

- **Scenario 3: Noisy low-quality video**
  - Problem: Bilateral amplifies frame-to-frame noise
  - Solution: Use standard Savitzky-Golay instead (more robust to noise)

**Troubleshooting:**

- If results are noisier with --bilateral-filter:
  - Video quality may not be high enough
  - Revert to standard smoothing (--no-bilateral-filter)
  - Or use --outlier-rejection to clean data first
- If transitions still seem blurred:
  - Bilateral sigma_intensity may be too large (currently 0.02)
  - This is a fixed parameter; file an issue for configurability
- If processing is too slow:
  - Bilateral adds ~2x time to smoothing step
  - Use standard Savitzky-Golay for faster processing

**Performance impact:**

- Adds ~50-100% to smoothing step time
- Smoothing is ~10-20% of total pipeline
- Overall impact: ~10-20% slower total processing
- O(n × window_size) complexity (same as Savitzky-Golay)
- Slower per-frame due to exponential calculations

**Recommendation:**

- Start with default (--no-bilateral-filter)
- If timing precision seems off, try --bilateral-filter
- Always use with --outlier-rejection for best results
- Consider experimental feature; may become default in future versions

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

```text
Video: 1080p (height = 1 in normalized coords)
Frame rate: 30 fps
Threshold: 0.02

0.02 * 1080 pixels = 21.6 pixels per frame
21.6 pixels * 30 fps = 648 pixels/second

So feet moving < 648 pixels/sec vertically = on ground
```text

**Example:**

```bash
# Missing short flight phases
kinemotion dropjump-analyze video.mp4 --velocity-threshold 0.01

# Too many false contacts detected
kinemotion dropjump-analyze video.mp4 --velocity-threshold 0.03
```text

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

```text
30 fps video:
  3 frames = 100ms minimum contact time
  5 frames = 167ms minimum contact time
  10 frames = 333ms minimum contact time

60 fps video:
  3 frames = 50ms minimum contact time
  6 frames = 100ms minimum contact time
```text

**Example:**

```bash
# Noisy tracking with false contacts
kinemotion dropjump-analyze video.mp4 --min-contact-frames 5

# Missing brief contacts in 60fps video
kinemotion dropjump-analyze video.mp4 --min-contact-frames 2
```text

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
```text

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
```text

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

```text
High detection + High tracking = Very conservative, frequent re-detection
High detection + Low tracking = Strict initialization, persistent tracking
Low detection + High tracking = Easy initialization, frequent re-detection
Low detection + Low tracking = Lenient overall, stable but risky
```text

**Example:**

```bash
# Tracking jumps to wrong person
kinemotion dropjump-analyze video.mp4 --tracking-confidence 0.7

# Tracking frequently lost during jump
kinemotion dropjump-analyze video.mp4 --tracking-confidence 0.3
```text

---

## Auto-Tuning System

Kinemotion uses an intelligent auto-tuning system that automatically optimizes analysis parameters based on video characteristics. This eliminates the need for manual calibration and makes the tool accessible to users without technical expertise.

### How Auto-Tuning Works

The system analyzes:

- **Video frame rate** - Adjusts smoothing windows and thresholds
- **Tracking quality** - Adapts confidence levels and filtering
- **Landmark visibility** - Determines outlier rejection needs
- **Quality preset** - Balances speed vs accuracy based on user selection

### Quality Presets

All analysis functions accept a `quality` parameter:

- **`"fast"`** - Quick processing, good for batch operations (50% faster)
- **`"balanced"`** - Default, optimal for most use cases
- **`"accurate"`** - Research-grade, maximum precision (slower)

**Example:**

```bash
# Fast processing for batch
kinemotion dropjump-analyze videos/*.mp4 --batch --quality fast

# Accurate for research
kinemotion dropjump-analyze video.mp4 --quality accurate --verbose
```

**Python API:**

```python
from kinemotion import process_dropjump_video

metrics = process_dropjump_video(
    "video.mp4",
    quality="accurate",
    verbose=True  # Shows selected parameters
)
```text

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

**Timing precision comparison:**

```text
Without curvature (velocity only):
- Uses smooth Savitzky-Golay velocity with sub-frame interpolation
- Effective for most use cases
- Theoretical timing precision: ±10ms at 30fps (⚠️ unvalidated)

With curvature (velocity + acceleration):
- Refines timing using physics-based acceleration patterns
- Theoretically more precise for rapid transitions
- Theoretical timing precision: ±5-8ms at 30fps (⚠️ unvalidated)
- Especially effective for landing detection (impact spike)
```text

**Physical basis:**

```text
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
```text

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
  --output debug_max.mp4 \
  --json-output metrics.json
```

**Effect on timing:**

```text
Example landing detection at 30fps:

Velocity-based estimate: frame 49.0
  → Velocity drops below threshold at this point

Curvature refinement: frame 46.9
  → Acceleration spike occurs earlier (impact moment)

Blended result: 0.7 × 46.9 + 0.3 × 49.0 = 47.43
  → 2.1 frames (70ms) more accurate timing
```text

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
  --velocity-threshold 0.015 \
  --min-contact-frames 2 \
  --visibility-threshold 0.6 \
  --detection-confidence 0.5 \
  --tracking-confidence 0.5
```text

### Scenario 2: Outdoor Handheld Video

- 30fps, camera shake, variable lighting, somewhat noisy

```bash
kinemotion dropjump-analyze video.mp4 \
  --smoothing-window 7 \
  --velocity-threshold 0.02 \
  --min-contact-frames 4 \
  --visibility-threshold 0.4 \
  --detection-confidence 0.4 \
  --tracking-confidence 0.4
```text

**Note:** Higher smoothing compensates for camera shake.

### Scenario 3: Low-Quality Smartphone Video

- 30fps, distant view, poor lighting, compression artifacts

```bash
kinemotion dropjump-analyze video.mp4 \
  --smoothing-window 9 \
  --velocity-threshold 0.025 \
  --min-contact-frames 5 \
  --visibility-threshold 0.3 \
  --detection-confidence 0.3 \
  --tracking-confidence 0.3
```text

**Note:** High smoothing filters out jitter from compression artifacts.

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
```text

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
```text

### Scenario 6: Drop Jump with Expert Parameter Tuning

- Drop jump analysis with manually tuned parameters for specific conditions

```bash
kinemotion dropjump-analyze video.mp4 \
  --quality accurate \
  --smoothing-window 5 \
  --velocity-threshold 0.02 \
  --min-contact-frames 3 \
  --visibility-threshold 0.5 \
  --detection-confidence 0.5 \
  --tracking-confidence 0.5 \
  --output debug.mp4 \
  --json-output metrics.json
```

**Note:** Expert parameters should only be adjusted when the automatic tuning doesn't work for your specific video conditions. The `--verbose` flag shows auto-selected parameters for comparison.

### Scenario 7: High-Performance Drop Jump Analysis (Maximum Accuracy)

- Research-grade analysis with all accuracy features enabled

```bash
kinemotion dropjump-analyze video.mp4 \
  --quality accurate \
  --use-curvature \
  --outlier-rejection \
  --output debug_max.mp4 \
  --json-output metrics.json \
  --smoothing-window 5 \
  --velocity-threshold 0.02 \
  --min-contact-frames 3 \
  --visibility-threshold 0.6 \
  --detection-confidence 0.5 \
  --tracking-confidence 0.5
```

**Note:** This uses maximum accuracy settings with advanced filtering:

- Curvature analysis: Enhanced timing precision
- Outlier rejection: Removes tracking glitches
- Fine-tuned expert parameters: Optimized for clean, high-quality videos

---

## Debugging Workflow

### Step 1: Generate Debug Video

Always start with a debug video to visualize what's happening:

```bash
kinemotion dropjump-analyze video.mp4 --output debug.mp4
```text

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
```text

### Step 4: Verify with JSON Output

```bash
kinemotion dropjump-analyze video.mp4 \
  --json-output results.json \
  --smoothing-window 7 \
  --velocity-threshold 0.015

# Check metrics make sense
cat results.json
```text

---

## Parameter Interactions

### Smoothing affects velocity calculation

```text
High smoothing → smoother velocity → may need lower velocity-threshold
Low smoothing → noisier velocity → may need higher velocity-threshold
```text

### Velocity + min-contact-frames work together

```text
Strict velocity (low) + lenient frames (low) = sensitive to brief contacts
Lenient velocity (high) + strict frames (high) = only long, clear contacts
```text

### Detection + tracking confidence relationship

```text
If detection-confidence > tracking-confidence:
  → Will re-detect frequently (less stable tracking)

If tracking-confidence > detection-confidence:
  → Will maintain tracking longer (more stable)
```text

### Frame rate affects velocity threshold

```text
30 fps:
→ More motion per frame
→ May need higher velocity-threshold (e.g., 0.02)
→ Adjust min-contact-frames based on expected contact duration

60 fps:
→ Less motion per frame
→ May need lower velocity-threshold (e.g., 0.01)
→ Can use smaller min-contact-frames for brief contacts
```text

### Curvature + sub-frame interpolation work together

```text
Both enabled (default):
→ Velocity interpolation gives sub-frame precision
→ Curvature refines based on acceleration patterns
→ Blended result combines both methods
→ Best timing accuracy

Curvature disabled:
→ Pure velocity-based interpolation
→ Still highly accurate with smooth derivatives
→ Useful for debugging or comparison
```text

### Outlier rejection + bilateral filter pipeline

```text
Outlier rejection first (when enabled):
→ Removes tracking glitches (jumps, spikes)
→ Replaces with interpolated values
→ Cleans data for subsequent smoothing

Then bilateral filter (if enabled) OR Savitzky-Golay (default):
→ Bilateral: edge-preserving, replaces Savitzky-Golay
→ Savitzky-Golay: uniform smoothing (default)

Best practice:
→ Keep outlier-rejection enabled (default)
→ Use bilateral for high-quality videos with rapid transitions
→ Use Savitzky-Golay (default) for most cases
```text

### Bilateral filter replaces smoothing-window/polyorder

```text
When bilateral-filter enabled:
→ Ignores --smoothing-window parameter
→ Ignores --polyorder parameter
→ Uses its own window size (9 frames) and weighting

When bilateral-filter disabled (default):
→ Uses --smoothing-window and --polyorder
→ Standard Savitzky-Golay smoothing
```text

---

## Performance Impact

| Parameter | Performance Impact |
|-----------|-------------------|
| smoothing-window | Negligible (post-processing) |
| polyorder | Negligible (same algorithm complexity) |
| outlier-rejection | Low (~5-10% total time increase) |
| bilateral-filter | Medium (~10-20% total time increase when enabled) |
| velocity-threshold | None (simple comparison) |
| min-contact-frames | None (simple counting) |
| visibility-threshold | None (simple comparison) |
| detection-confidence | Medium (affects MediaPipe workload) |
| tracking-confidence | Medium (affects MediaPipe workload) |
| use-curvature | Negligible (reuses smoothed trajectory) |

**Notes:**

- Higher confidence thresholds can actually improve performance by reducing unnecessary pose detection/tracking attempts
- Curvature analysis reuses existing derivatives, effectively free
- Polyorder has no performance impact (polynomial fit complexity is O(window_size), independent of order)

---

## Advanced Tips

### 1. Frame Rate Matters

Scale velocity-threshold and min-contact-frames based on FPS:

```text
30 fps: velocity-threshold = 0.02, min-contact-frames = 3
60 fps: velocity-threshold = 0.01, min-contact-frames = 6
```text

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
```text

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
```text

---

## Summary Table

| Parameter | Default | Range | Primary Effect | Adjust When |
|-----------|---------|-------|----------------|-------------|
| `smoothing-window` | 5 | 3-11 (odd) | Trajectory smoothness | Video is jittery or too smooth |
| `polyorder` | 2 | 1-4 | Polynomial fit complexity | High-quality video with complex motion (+1-2%) |
| `outlier-rejection` | enabled | enabled/disabled | Removes tracking glitches | Keep enabled unless debugging (+1-2%) |
| `bilateral-filter` | disabled | enabled/disabled | Edge-preserving smoothing | High-quality video with rapid transitions (+1-2%) |
| `velocity-threshold` | 0.02 | 0.005-0.05 | Contact sensitivity | Missing contacts or false detections |
| `min-contact-frames` | 3 | 1-10 | Contact duration filter | Brief false contacts or missing short contacts |
| `visibility-threshold` | 0.5 | 0.3-0.8 | Landmark trust level | Occlusions or need high confidence |
| `detection-confidence` | 0.5 | 0.1-0.9 | Initial pose detection | Multiple people or poor visibility |
| `tracking-confidence` | 0.5 | 0.1-0.9 | Tracking persistence | Tracking lost or wrong person tracked |
| `use-curvature` | enabled | enabled/disabled | Timing refinement | Default: keep enabled for best accuracy |
| `quality` | balanced | fast/balanced/accurate | Analysis speed vs accuracy | Use fast for batch, accurate for research |
```
````
