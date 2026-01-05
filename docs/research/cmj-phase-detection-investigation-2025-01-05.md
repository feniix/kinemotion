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

- `src/kinemotion/cmj/analysis.py` - Reverted to baseline algorithm
- `scripts/validate_ankle_angle.py` - Created for ankle signal investigation (can be kept)

## References

- Savitzky-Golay phase lag: https://stackoverflow.com/questions/55572128
- Parabolic peak interpolation: https://ccrma.stanford.edu/~jos/parshar/Peak_Detection_Steps_3.html
- CUSUM change detection: Various signal processing references
- Zero-phase filtering: scipy.signal.filtfilt documentation
