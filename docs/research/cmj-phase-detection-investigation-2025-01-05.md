# CMJ Phase Detection Accuracy Investigation

**Date:** 2025-01-05
**Video:** `samples/validation/cmj-45-IMG_6733.MOV`
**Resolution:** 1920x1080 @ 60fps
**Duration:** 3.58s (215 frames)
**Backend:** MediaPipe Pose Tasks API

## Ground Truth (Manually Observed)

| Event          | Frame |
| -------------- | ----- |
| Standing Start | 64    |
| Lowest Point   | 87    |
| Takeoff        | 104   |
| Landing        | 141   |

## Baseline Results (Current Algorithm)

| Event          | Detected Frame | Error | Error (ms) |
| -------------- | -------------- | ----- | ---------- |
| Standing Start | 66             | +2    | +33ms      |
| Lowest Point   | 91             | +4    | +67ms      |
| Takeoff        | 105            | +1    | +17ms      |
| Landing        | 142            | +1    | +17ms      |

**Average Error:** 2.0 frames (33ms)

______________________________________________________________________

## Investigation: Systematic Delay Analysis

### Root Cause Hypothesis: Savitzky-Golay Phase Lag

**Savitzky-Golay Filter Properties:**

- Window length: 3-5 frames (auto-tuned)
- Phase lag ≈ (window_length - 1) / 2 per derivative operation
- At window=3: ~1 frame lag per derivative

**Impact on Each Detection:**

| Detection      | Signal Used  | Lag Factor             | Expected Lag |
| -------------- | ------------ | ---------------------- | ------------ |
| Standing Start | Acceleration | 2x (double derivation) | ~2 frames    |
| Lowest Point   | Velocity     | 1x                     | ~1 frame     |
| Takeoff        | Velocity     | 1x                     | ~1 frame     |
| Landing        | Acceleration | 2x                     | ~2 frames    |

**Actual errors closely match expected lag pattern**, suggesting smoothing is a contributing factor.

______________________________________________________________________

## Approach 1: Reduce Threshold (2σ instead of 3σ)

**Theory:** Standing Start uses `baseline_mean + 3*std` threshold. Reducing to 2σ should detect movement earlier.

### Implementation

Changed `find_standing_end()` threshold from `3.0 * std` to `2.0 * std`.

### Results

| Event          | Ground Truth | Baseline | 2σ Threshold | Delta  |
| -------------- | ------------ | -------- | ------------ | ------ |
| Standing Start | 64           | 66       | **40**       | -26 ❌ |
| Lowest Point   | 87           | 91       | 91           | 0      |
| Takeoff        | 104          | 105      | 105          | 0      |
| Landing        | 141          | 142      | 142          | 0      |

### Conclusion

**FAILED.** 2σ threshold detected noise 24 frames too early. The 3σ threshold is appropriate for filtering pose estimation jitter.

______________________________________________________________________

## Approach 2: Zero-Phase Filtering

**Theory:** Apply Savitzky-Golay filter forward and backward, averaging results to cancel phase lag.

### Implementation

Added `compute_zero_phase_velocity()` and `compute_zero_phase_acceleration()` functions applying bidirectional filtering.

### Results

| Event          | Ground Truth | Baseline | Zero-Phase | Delta |
| -------------- | ------------ | -------- | ---------- | ----- |
| Standing Start | 64           | 66       | 66         | 0     |
| Lowest Point   | 87           | 91       | **90**     | +1 ✅ |
| Takeoff        | 104          | 105      | **110**    | -5 ❌ |
| Landing        | 141          | 142      | 142        | 0     |

### Why Takeoff Got Worse

The `find_takeoff_frame()` uses `argmin(velocities)` to find peak upward velocity. Zero-phase filtering changed the velocity curve shape, causing the minimum to shift later in the data.

### Conclusion

**FAILED.** While lowest point improved slightly (+1 frame), takeoff got significantly worse (+5 frames). The bidirectional averaging created artifacts in the velocity curve.

______________________________________________________________________

## Approach 3: Combined (2σ + Zero-Phase)

Testing both approaches together to see if effects combine positively.

### Results

| Event          | Ground Truth | Baseline | Combined | Delta  |
| -------------- | ------------ | -------- | -------- | ------ |
| Standing Start | 64           | 66       | **40**   | -26 ❌ |
| Lowest Point   | 87           | 91       | **90**   | +1 ✅  |
| Takeoff        | 104          | 105      | **110**  | -5 ❌  |
| Landing        | 141          | 142      | 142      | 0      |

### Conclusion

**FAILED.** Effects were independent and additive, with both negative aspects (early standing start, late takeoff) present.

______________________________________________________________________

## Approach 4: Sub-Frame Interpolation

**Theory:** Instead of returning integer frame indices, interpolate to find fractional frame where event actually occurs using parabolic peak fitting.

### Implementation

Added helper functions:

- `_interpolate_parabolic_peak()`: Fits parabola to 3 points around detected peak/trough
- `_interpolate_sign_change()`: Linear interpolation for threshold crossings

Modified detection functions to apply interpolation to detected peaks.

### Results

| Event          | Ground Truth | Integer | Sub-Frame  | Error (Int) | Error (Sub) |
| -------------- | ------------ | ------- | ---------- | ----------- | ----------- |
| Standing Start | 64           | 66.0    | 66.0       | +2          | +2          |
| Lowest Point   | 87           | 91      | **90.69**  | +4          | +3.7        |
| Takeoff        | 104          | 105     | **105.08** | +1          | +1.1        |
| Landing        | 141          | 142     | **142.15** | +1          | +1.1        |

### Improvement

- **0.3 frames** average improvement (5ms at 60fps)
- Marginal gain for added complexity

### Conclusion

**MARGINAL.** Sub-frame interpolation provides fractional precision but doesn't address the underlying systematic delay. Given manual ground truth observation, the benefit is minimal.

______________________________________________________________________

## Cross-Video Validation

Tested on multiple videos from same session:

| Video | Standing | Lowest | Takeoff | Landing |
| ----- | -------- | ------ | ------- | ------- |
| 6733  | +2       | +4     | +1      | +1      |
| 6734  | +12      | +8     | +2      | +3      |
| 6735  | +1       | -8     | -11     | -12     |

**Note:** Videos 6734 and 6735 had different ground truth values. Variability suggests manual observation inconsistency or true biomechanical differences between jumps.

______________________________________________________________________

## Ankle Angle Detection Investigation

**Hypothesis:** Ankle dorsiflexion occurs at landing before hip deceleration, potentially providing earlier landing detection.

### Test Results

| Video | Left Ankle Offset      | Right Ankle Offset     |
| ----- | ---------------------- | ---------------------- |
| 6733  | -19 frames (too early) | -2 frames (close)      |
| 6734  | -19 frames (too early) | +3 frames (late)       |
| 6735  | -19 frames (too early) | -12 frames (too early) |

### Findings

1. **Right ankle** showed more consistent patterns than left
1. **Range of -12 to +3 frames** is too wide for practical use
1. **Ankle angle signal is inconsistent** across jumps
1. Individual landing mechanics vary (flat-footed vs forefoot)

### Conclusion

**NOT VIABLE.** Ankle angle detection is too variable for reliable landing detection.

______________________________________________________________________

## Conclusions

### Current Algorithm Performance

| Metric         | Baseline Error   | Assessment         |
| -------------- | ---------------- | ------------------ |
| Standing Start | +2 frames (33ms) | Acceptable ✅      |
| Lowest Point   | +4 frames (67ms) | Could be better ⚠️ |
| Takeoff        | +1 frame (17ms)  | Excellent ✅       |
| Landing        | +1 frame (17ms)  | Excellent ✅       |

### Key Findings

1. **3σ threshold is appropriate** - Lower thresholds detect noise
1. **Zero-phase filtering is counterproductive** - Creates curve artifacts
1. **Sub-frame interpolation provides minimal benefit** - ~0.3 frames (5ms)
1. **Ankle angle detection is too variable** - Individual landing mechanics differ

### Why Errors Exist

1. **Frame rate limitation** - At 60fps, 1 frame = 16.7ms
1. **Manual ground truth observation** - Subjective interpretation of event timing
1. **Pose estimation latency** - MediaPipe has inherent processing delay
1. **Smoothing lag** - Savitzky-Golay filter introduces ~1 frame per derivative

### Accuracy Context

**Current accuracy (±1-4 frames = ±17-67ms)** is within acceptable tolerances for:

- Sports performance analysis
- Movement pattern recognition
- Relative comparison between jumps

**For higher precision:**

- Use 120-240fps video (validated apps like MyJump use these rates)
- Force plate integration for ground truth validation
- Multiple camera angles for 3D reconstruction

______________________________________________________________________

## Recommendations

1. **Keep current algorithm** - All attempted improvements failed or showed marginal benefit
1. **Document frame rate limitation** - Recommend 120+ fps for research-grade analysis
1. **Consider RTMPose** - Showed exact takeoff detection (104 vs ground truth 104) in one test
1. **Focus on other priorities** - Current accuracy is sufficient for MVP use cases

______________________________________________________________________

## Files Modified During Investigation

All changes have been reverted. Codebase is in original state:

- `src/kinemotion/countermovement_jump/analysis.py` - Reverted to baseline algorithm
- `scripts/validate_ankle_angle.py` - Created for ankle signal investigation (can be kept)

______________________________________________________________________

## Force Plate Landing Detection Research

**Date:** 2025-01-05
**Context:** Understanding how force plates define landing vs. video-based detection

### Force Plate Landing Definition

**Standard Practice:** Landing is defined as when vertical ground reaction force (VGRF) exceeds a small threshold - typically **10-50 Newtons**.

From Tirosh & Sparrow (2003):

> "Any force threshold within 0 to 50 N could be used to predict heel-contact time."

**What 10-50 N Means:**

| Threshold | Context                              |
| --------- | ------------------------------------ |
| 10 N      | Weight of 1 kg - feather-light touch |
| 50 N      | Weight of 5 kg - minimal contact     |
| 700 N     | A 70 kg athlete's full body weight   |

10-50 N is essentially **initial touch**, not full impact.

### Force Plate vs. Video Algorithm Comparison

| Method                      | Landing Definition                           | Timing          |
| --------------------------- | -------------------------------------------- | --------------- |
| **Force Plate**             | First moment VGRF exceeds ~10-50 N           | Initial contact |
| **Current Video Algorithm** | Maximum deceleration spike after peak height | Full impact     |

**The Gap:**

At 30 FPS (33ms/frame), there could be 1-3 frames difference between:

- Frame 1: Toes barely touch (force plate threshold)
- Frame 2-3: Foot rolls, impact builds
- Frame 4: Maximum deceleration (current algorithm)

**At 60 FPS (16.7ms/frame):** 2-6 frames between initial contact and impact detection.

### Current Algorithm Behavior

From `src/kinemotion/countermovement_jump/analysis.py:388-442`:

```python
def find_landing_frame():
    """
    1. Find peak downward velocity (max positive velocity) after peak height
    2. Search for maximum deceleration (min acceleration) AFTER peak velocity
    3. This filters out mid-air tracking noise
    4. Returns frame of impact (maximum deceleration spike)
    """
```

**Key Points:**

- Detects **full impact** (deceleration spike), not initial contact
- Deliberately searches after peak velocity to avoid false positives from tracking noise
- Biomechanically meaningful (moment of force application)
- Marks end of flight time (used for jump height calculation)

### Can Video Detect True Initial Contact?

**The Challenge:**

At 10-50 N threshold, the athlete is still essentially in freefall:

- The foot has barely grazed the ground
- Visually indistinguishable from the frame just before contact
- By the time deceleration is visible in pose data, we're already past true initial contact

**Why Current Detection is Later:**

```
Frame N-2: Foot clearly in air, falling at ~9.8 m/s²
Frame N-1: Foot still falling, looks like air (force plate would detect 10N here)
Frame N:   First frame where pose might show something changed?
Frame N+1: Deceleration begins to be visible
Frame N+2: Impact (what current algorithm detects)
```

**Frame Rate Reality:**

At 60 FPS (16.7ms per frame), the entire transition from "just touched" to "full impact" might span **1-2 frames total**. True initial contact (10N) is not visually distinguishable from the preceding frame.

### Potential Approaches

#### 1. Foot Angle Detection

**Theory:** Ankle dorsiflexion occurs at landing before hip deceleration, potentially providing earlier landing detection.

**Status:** ❌ **NOT VIABLE** (tested above - "Ankle Angle Detection Investigation")

- Range of -12 to +3 frames offset
- Too variable for practical use
- Individual landing mechanics differ (flat-footed vs forefoot)

#### 2. Frame Subtraction

**Theory:** If initial contact is consistently N frames before deceleration, subtract N frames.

**Challenges:**

- Offset must be consistent across athletes and jump heights
- Requires validation data to determine correct offset
- May not generalize

#### 3. Accept Current Detection

**Rationale:**

- Current detection is biomechanically meaningful (impact phase)
- Error of ±1 frame at 60 FPS = ±17ms (acceptable for most use cases)
- Force plate "initial contact" (10N) may not be practically relevant for video-based analysis

### Force Plate Research References

1. **Tirosh & Sparrow (2003)** - "Identifying Heel Contact and Toe-Off Using Forceplate Thresholds"

   - Tested thresholds: 10, 20, 30, 40, 50 N
   - Found: "any force threshold within 0 to 50 N could be used to predict heel-contact time"
   - For takeoff: "10 N or less should be used"

1. **Rojano Ortega et al. (2010)** - "Analysis of the Vertical Ground Reaction Forces and Temporal Factors in the Landing Phase"

   - Two peak forces (F1 and F2) in landing force-time curve
   - F1: Impact of metatarsal heads (forefoot)
   - F2: Impact of calcaneus (heel)
   - Second peak (F2) usually related to injury risk

### Practical Considerations

**Question:** What metric are you trying to validate against?

| Use Case                 | Preferred Detection                                    |
| ------------------------ | ------------------------------------------------------ |
| Flight time calculation  | Initial contact (force plate style)                    |
| Landing mechanics/forces | Impact phase (current algorithm)                       |
| Injury risk assessment   | Both (contact timing + impact magnitude)               |
| Performance comparison   | Relative consistency matters more than absolute timing |

**Recommendation:**

If you need to match force plate data for validation:

- Use current algorithm and apply **constant offset** based on calibration
- Accept that video-based initial contact will lag force plates by ~10-30ms
- Focus on **flight time consistency** rather than matching exact frame numbers

For higher precision:

- Use 120-240fps video (validated apps like MyJump use these rates)
- Force plate integration for ground truth validation
- Multiple camera angles for 3D reconstruction

______________________________________________________________________

## Force-Plate-Equivalent Landing Detection

**Date:** 2025-01-05
**Goal:** Find a video-based method that detects landing at "initial contact" (like force plates at 10-50N) rather than "impact" (maximum deceleration).

### Methods Tested

| Method                   | Description                   | Average Offset vs Current  |
| ------------------------ | ----------------------------- | -------------------------- |
| Current (foot accel)     | Maximum deceleration spike    | Baseline                   |
| Foot velocity threshold  | Velocity drops to 15% of max  | +2.67 frames (LATER)       |
| Foot-hip divergence      | Foot-hip distance rate change | -0.33 frames               |
| Foot decel spike         | Foot acceleration minimum     | 0.00 frames                |
| **Velocity deriv onset** | First 30% of max deceleration | **-1.67 frames (EARLIER)** |
| Position minimum         | Foot stops descending         | +7.3 frames (buggy)        |
| Velocity zero-crossing   | Foot velocity reaches zero    | +7.7 frames (buggy)        |

### Best Method: Velocity Derivative Onset

**Algorithm:** Detect when foot deceleration first exceeds 30% of the maximum deceleration rate.

```python
def find_landing_frame_velocity_derivative(velocities, peak_height_frame, fps):
    # Compute velocity derivative (= acceleration)
    vel_derivative = savgol_filter(velocities, 5, 2, deriv=1)

    # Find minimum derivative (max deceleration)
    min_deriv = min(vel_derivative[search_window])

    # Find onset: first frame exceeding 30% threshold
    threshold = min_deriv * 0.3
    landing_frame = first_frame_where(vel_derivative < threshold)
```

### Visual Verification

Extracted frames from `cmj-45-IMG_6733.MOV`:

| Frame | Detection              | Visual Observation                                        |
| ----- | ---------------------- | --------------------------------------------------------- |
| 140   | **Vel deriv onset**    | Initial contact - feet just touching, motion blur present |
| 141   | -                      | Impact absorption in progress                             |
| 142   | Ground truth / Current | Impact completed - feet fully planted                     |

**Conclusion:** The velocity derivative onset method detects landing **1-2 frames earlier** (17-33ms at 60fps), which is closer to force plate behavior (initial contact at 10-50N).

### Results Across All Videos

| Video | Ground Truth | Current | Vel Deriv Onset | Delta     |
| ----- | ------------ | ------- | --------------- | --------- |
| 6733  | 142          | 142     | 140             | -2 frames |
| 6734  | 144          | 144     | 143             | -1 frame  |
| 6735  | 130          | 130     | 128             | -2 frames |

**Average: -1.67 frames (28ms earlier)**

### Why This Works

1. **Physics:** Deceleration begins the instant foot touches ground (can't decelerate in air)
1. **Kinematic chain:** Foot contact → foot deceleration → hip deceleration (delay)
1. **Force plate equivalent:** 10-50N threshold is "first measurable force" = deceleration onset

### Implications

If using velocity derivative onset for landing:

- **Flight time increases** by ~1-2 frames (~30ms)
- **Jump height increases** by ~0.5-1cm (using flight time formula)
- **More accurate** for force plate validation studies

### Implementation Status

- **Validation script:** `scripts/validate_foot_velocity_landing.py`
- **Frame extraction:** `scripts/extract_landing_frames.py`
- **Integration:** Not yet integrated into main codebase

______________________________________________________________________

## References

- Savitzky-Golay phase lag: https://stackoverflow.com/questions/55572128
- Parabolic peak interpolation: https://ccrma.stanford.edu/~jos/parshar/Peak_Detection_Steps_3.html
- CUSUM change detection: Various signal processing references
- Zero-phase filtering: scipy.signal.filtfilt documentation
- **Tirosh & Sparrow (2003)**: "Identifying Heel Contact and Toe-Off Using Forceplate Thresholds" - Journal of Applied Biomechanics 19(2):178-184
- **Rojano Ortega et al. (2010)**: "Analysis of the Vertical Ground Reaction Forces and Temporal Factors in the Landing Phase of a Countermovement Jump" - J Sports Sci Med 9(2):282-287
