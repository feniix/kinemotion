# Known Height Validation

**Status:** Protocol Documentation (Pre-testing)
**Updated:** 2025-11-14
**Type:** Physics-based validation without laboratory equipment

## Overview

This validation protocol tests kinemotion's timing accuracy by comparing measured flight times against theoretical predictions from physics equations. By dropping objects from measured heights, we can validate the algorithm's ability to measure flight time correctly without access to force plates or motion capture systems.

**Key Principle:** For a freely falling object, theoretical flight time can be calculated precisely:

```text
t = √(2h/g)

where:
  t = flight time (seconds)
  h = drop height (meters)
  g = gravitational acceleration (9.81 m/s²)
```

## Test Protocol

### Equipment Required

- Basketball, medicine ball, or similar object
- Measuring tape (minimum 2m)
- Camera capable of 60fps recording (smartphone acceptable)
- Tripod or stable mount
- Markers/tape for marking heights

### Test Setup

1. **Select drop heights:** 0.5m, 1.0m, 1.5m

   - Recommended: Create test rig with marked heights on wall
   - Use measuring tape to verify exact heights

1. **Camera positioning:**

   - Mount camera on tripod at 60fps or higher
   - Position to capture full drop trajectory
   - Ensure consistent distance and angle for all drops
   - Adequate lighting (consistent throughout)

1. **Drop execution:**

   - Position ball at marked height
   - Release (don't throw) from rest
   - Ball should drop vertically
   - Ensure complete capture from release to landing

### Video Filename Format

Videos must follow this naming convention for automatic height extraction:

```text
drop_[HEIGHT]m_run[NUMBER].mp4
```

**Examples:**

- `drop_0.5m_run1.mp4` - 0.5m drop, first repetition
- `drop_1.0m_run2.mp4` - 1.0m drop, second repetition
- `drop_1.5m_run3.mp4` - 1.5m drop, third repetition

Minimum: 10 drops per height (30 total videos)
Recommended: 15 drops per height (45 total videos)

### Expected Theoretical Values

| Height (m) | Theoretical Flight Time (s) |
| ---------- | --------------------------- |
| 0.50       | 0.319                       |
| 1.00       | 0.452                       |
| 1.50       | 0.553                       |

## Analysis

### Running Validation Script

```bash
# Validate all videos in default directory
python scripts/validate_known_heights.py

# Validate custom directory
python scripts/validate_known_heights.py --videos-dir data/my_drops

# Save results as JSON
python scripts/validate_known_heights.py --output results.json

# Create visualizations
python scripts/plot_validation_results.py results.json --output-dir plots/
```

### Script Outputs

**Console Output:**

- Per-video: measured vs theoretical flight times
- Error in milliseconds and percent
- Confidence assessment per video
- Summary statistics

**JSON Output** (with `--output`):

```json
{
  "summary": {
    "total_videos": 30,
    "mae_ms": 8.45,
    "rmse_ms": 10.2,
    "bias_ms": 2.1,
    "correlation": 0.9987,
    "pass_mae": true,
    "pass_rmse": true,
    "pass_correlation": true
  },
  "results": [
    {
      "video": "drop_0.5m_run1.mp4",
      "true_height_m": 0.5,
      "measured_flight_time_s": 0.321,
      "theoretical_flight_time_s": 0.319,
      "absolute_error_ms": 2.0,
      "percent_error": 0.63,
      "confidence": "high"
    }
  ]
}
```

**Visualization Output:**

- `validation_measured_vs_theoretical.png` - Scatter plot with fit line
- `validation_residuals.png` - Residual distribution
- `validation_bland_altman.png` - Agreement analysis

## Success Criteria

### Primary Metrics

| Metric                        | Threshold | Rationale                            |
| ----------------------------- | --------- | ------------------------------------ |
| Mean Absolute Error (MAE)     | \< 20ms   | Acceptable for 30-60fps video        |
| Root Mean Square Error (RMSE) | \< 30ms   | Accounts for larger outliers         |
| Correlation (r)               | > 0.99    | Strong linear relationship           |
| Systematic Bias               | \< 5ms    | No consistent under/over-measurement |

### Confidence Levels

- **High:** Error \< 10ms → reliable measurement
- **Medium:** Error 10-20ms → acceptable, note in results
- **Low:** Error > 20ms → investigate cause

## Interpretation

### What This Validates

✅ **Validates:**

- Kinemotion accurately measures flight time
- Algorithm correctly identifies takeoff and landing frames
- Timing accuracy at different heights
- Consistency across multiple runs
- Algorithm determinism (no random variation)

❌ **Does NOT validate:**

- Absolute accuracy against force plates (gold standard)
- Jump height calculations (depends on flight time + other factors)
- Countermovement or landing dynamics
- Performance suitability for research publications

### Common Causes of Error

**Systematic Bias (consistent over/under-measurement):**

- Incorrect frame rate in video file metadata
- Systematic tracking delay from MediaPipe
- Lighting artifacts affecting frame detection

**Random Error (variable error across videos):**

- Inconsistent lighting conditions
- Ball not dropping vertically
- Video compression artifacts
- Poor tracking on landing frame

**Large Errors (> 20ms):**

- Low frame rate (\< 30fps) - insufficient temporal resolution
- Video recording at different frame rate than specified
- Ball bouncing or multiple contact points
- Occlusion during flight

## Data Collection Recommendations

### Best Practices

1. **Lighting:**

   - Use consistent, diffuse lighting
   - Avoid shadows on ball or background
   - Avoid reflective backgrounds

1. **Camera Setup:**

   - Use 60fps or higher
   - Verify actual frame rate in recording properties
   - Use manual focus (avoid autofocus hunting)
   - High contrast background (ball visibility)

1. **Drop Execution:**

   - Release from rest (no initial velocity)
   - Ensure ball falls vertically (no rotation)
   - Allow complete impact capture (don't cut short)
   - Repeat consistently across all heights

1. **Quality Control:**

   - Check each video for:
     - Clear ball visibility throughout
     - No compression artifacts
     - Complete trajectory capture
     - Adequate lighting

### Problematic Videos

Exclude videos with:

- Ball not visible for portion of flight
- Multiple bounces before landing
- Partial frame capture
- Extreme motion blur
- Inconsistent lighting changes

## Expected Results

### Typical Performance

For properly conducted testing with 60fps video:

```text
Sample Results (30 drops):
- MAE: 6-12ms
- RMSE: 8-15ms
- Bias: -2 to +3ms
- Correlation: > 0.998
- 90% of measurements: high confidence
```

### Pass/Fail Criteria

**PASS:** All three criteria met:

- ✅ MAE \< 20ms
- ✅ RMSE \< 30ms
- ✅ Correlation > 0.99

**FAIL:** Any criterion not met

- ❌ Investigate cause
- ❌ Check video quality
- ❌ Verify frame rate
- ❌ Review setup

## Troubleshooting

### High Error Rate

**Problem:** Most measurements have errors > 20ms

**Possible Causes:**

1. **Low frame rate** - Most common

   - Solution: Use 60fps minimum (120fps ideal)
   - Verify: Check video properties

1. **Landing detection issues** - Ball bounces or unclear contact

   - Solution: Ensure ball lands on dark/uniform background
   - Solution: Check for motion blur

1. **Lighting problems** - Poor ball visibility

   - Solution: Increase lighting consistency
   - Solution: Use high-contrast background

**Diagnostic Steps:**

- Manually verify 1-2 videos with frame counter
- Check if error is systematic (always early/late) or random
- Compare high-error vs low-error videos for differences

### Bias Present (Consistent Offset)

**Problem:** Errors consistently positive or negative

**Examples:**

- Always 8ms too fast → bias = -8ms
- Always 5ms too slow → bias = +5ms

**Causes:**

1. Frame rate metadata incorrect (camera reports 60fps, actually 59.7fps)
1. Systematic delay in takeoff/landing detection
1. Video processing lag

**Solutions:**

- Verify actual frame rate with: `ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1:separator=/ video.mp4`
- If bias > 5ms, investigate algorithm parameters
- Document bias for future corrections

### Correlation Low (\< 0.99)

**Problem:** Error increases with height (or height-independent outliers)

**Causes:**

1. Tracking degradation at different heights
1. Height-dependent lighting changes
1. Camera angle effects
1. Incomplete test data

**Solutions:**

- Verify even lighting across all heights
- Check that camera angle is perpendicular to drop
- Review and potentially exclude outlier videos
- Ensure minimum 30 videos per condition

## Next Steps

### After Validation

If validation **PASSES**:

- Document results in project
- Update validation status with "Known Height Validation: PASSED"
- Reference in README
- Use as baseline for future algorithm changes

If validation **FAILS**:

1. Investigate specific cause (see Troubleshooting)
1. Collect additional test videos addressing identified issue
1. Retest with improvements
1. Document what was changed and why

### Integration with Broader Validation

This test is **Task 1.4** in the validation roadmap.

**Next Task (1.5):** Parameter Sensitivity Report

- Systematic testing of algorithm parameters
- Identify which parameters affect timing measurement
- Provide tuning guidance for different use cases

**Future Tasks:**

- Manual frame selection comparison (vs smartphone app)
- Multi-session reliability study
- Environmental condition testing

## References

### Physics Formulas

**Free fall from rest:**

- Position: `h = 0.5 * g * t²`
- Velocity: `v = g * t`
- Time to fall height h: `t = √(2h/g)`

**Constants:**

- g = 9.81 m/s² (use 9.8 m/s² if more precision needed: 9.807 m/s²)

### Related Documentation

- `docs/validation-status.md` - Overall validation status
- `docs/development/validation-roadmap.md` - Full validation roadmap
- `scripts/validate_known_heights.py` - Main validation script
- `scripts/plot_validation_results.py` - Visualization script

## Appendix: Manual Frame Analysis

### Verifying Results Manually

If you want to manually verify a video:

1. Open video in frame-by-frame capable player (VLC, FFmpeg)
1. Find first frame where ball is in motion (takeoff)
1. Find first frame where ball contacts ground (landing)
1. Count frames between takeoff and landing
1. Divide by frame rate: `flight_time = frame_count / fps`

**Example:**

- Takeoff frame: 120
- Landing frame: 147
- Frame count: 147 - 120 = 27 frames
- At 60fps: 27 / 60 = 0.45 seconds

**Compare to kinemotion output:**

- If kinemotion reports 0.45s → correct ✅
- If kinemotion reports 0.48s → investigate (28 frames detected)
- If kinemotion reports 0.42s → investigate (25 frames detected)

This manual verification is valuable for:

- Understanding algorithm behavior
- Identifying systematic detection errors
- Training eye for frame-level accuracy

## Questions & Feedback

For issues, questions, or suggestions:

- Check `docs/validation/known-height-validation.md` (this file)
- Review script output and logs
- See `docs/validation-status.md` for current validation state
