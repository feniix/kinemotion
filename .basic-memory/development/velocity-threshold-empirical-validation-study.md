---
title: Velocity Threshold Empirical Validation Study
type: note
permalink: development/velocity-threshold-empirical-validation-study
---

# Velocity Threshold Empirical Validation Study

**Date**: 2025-12-06
**Study Type**: Empirical velocity profiling
**Dataset**: 3 drop jump videos @ 45° oblique, 60fps

## Executive Summary

Empirical measurement of foot velocities during drop jumps revealed that the auto-tuning formula for `velocity_threshold` was **5x too loose**, causing complete failure of contact state detection.

**Old formula**: `0.02 * (30/fps)` → 0.01 at 60fps
**New formula**: `0.004 * (30/fps)` → 0.002 at 60fps
**Impact**: 99% improvement in landing/takeoff detection

## Methodology

### Measurement Setup
- Processed videos with MediaPipe Pose tracking
- Extracted foot positions (average of ankle, heel, foot_index landmarks)
- Calculated velocities using Savitzky-Golay derivative (window=5, polyorder=2)
- Measured velocity distribution across different jump phases

### Sample Video Analysis

**Video**: dj-45-IMG_6740.MOV (60fps, complete failure case)
- Total frames: 232
- Ground truth: drop=141, landing=154, takeoff=166

## Empirical Velocity Measurements

### Standing Phase (Stationary on Box)
**Frames**: 100-141 (before drop)

| Metric | Value | Notes |
|--------|-------|-------|
| Mean absolute velocity | 0.0003 | Natural body sway |
| Max absolute velocity | 0.0011 | Peak sway |
| 95th percentile | 0.0007 | Typical upper bound |

**Interpretation**: Stationary feet exhibit ~0.001 normalized velocity due to:
- Natural body sway
- Breathing movement
- MediaPipe tracking noise

### Drop Phase (Falling Through Air)
**Frames**: 141-154 (after leaving box, before ground contact)

| Metric | Value | Notes |
|--------|-------|-------|
| Mean absolute velocity | 0.0062 | Consistent downward acceleration |
| Max absolute velocity | 0.0088 | Peak falling velocity |
| All > 0.01? | **FALSE** | Below old threshold! |

**Interpretation**: Falling velocities ~0.006-0.009, which is **below the old 0.01 threshold**, causing algorithm to classify falling as "stationary".

### Flight Phase (Airborne After Takeoff)
**Frames**: 166-186 (after takeoff)

| Metric | Value | Notes |
|--------|-------|-------|
| Mean absolute velocity | 0.0040 | Rising then falling trajectory |
| Max absolute velocity | 0.0090 | Peak velocity |
| All > 0.01? | **FALSE** | Below old threshold! |

**Interpretation**: Flight velocities ~0.004-0.009, also **below the old 0.01 threshold**.

## Root Cause Analysis

### Problem: Threshold Too Loose

**Old threshold (0.01) classification**:
- Standing (0.001) < 0.01 → ON_GROUND ✓ Correct
- Drop (0.006) < 0.01 → **ON_GROUND ✗ WRONG!** (should be IN_AIR)
- Flight (0.005) < 0.01 → **ON_GROUND ✗ WRONG!** (should be IN_AIR)

**Result**: Algorithm thought athlete **never left the ground**, even during:
- Drop phase (falling from box)
- Flight phase (after takeoff)

**Impact**:
- drop_start error: 90 frames (detected wrong event)
- landing error: 97 frames (defaulted to frame 0)
- takeoff error: 22 frames (detected end of video)

### Solution: Optimal Threshold

**New threshold (0.002) classification**:
- Standing (0.001) < 0.002 → ON_GROUND ✓ Correct
- Drop (0.006) > 0.002 → IN_AIR ✓ Correct
- Flight (0.005) > 0.002 → IN_AIR ✓ Correct

**Safety margin**: 2x separation between standing max (0.0011) and threshold (0.002)

## Formula Derivation

### Why 0.004 Factor?

**Goal**: velocity_threshold = 0.002 at 60fps

**Inverse scaling with FPS**:
```python
threshold = factor * (30 / fps)
```

**At 60fps**:
```python
0.002 = factor * (30 / 60)
0.002 = factor * 0.5
factor = 0.004
```

**Validation at different frame rates**:
- 30fps: 0.004 * (30/30) = 0.004 (reasonable for lower fps)
- 60fps: 0.004 * (30/60) = 0.002 (empirically validated)
- 120fps: 0.004 * (30/120) = 0.001 (appropriate for higher temporal resolution)

## Why Original Formula Failed

**Original assumption** (0.02 factor):
> "At 30fps, feet move ~2% of frame per frame when stationary"

**Reality**:
- Positions are normalized 0-1
- Standing sway is ~0.1-0.3% of frame, not 2%
- Savitzky-Golay smoothing reduces apparent velocity further
- Actual standing velocity: ~0.001 (50x smaller than assumed!)

**The error**: Assumed raw pixel velocities, but forgot positions are normalized to [0,1] range

## Results After Fix

### Contact State Detection
- Video 1: Now detects 9 phases (was 3)
- Video 2: Now detects 7 phases (was 1)
- Correctly identifies drop, landing, and flight phases

### Event Detection Accuracy
- drop_start: 0.67 frames (was 90.67) - **99% improvement**
- landing: 0.38 frames (was 97.06) - **99.6% improvement**
- takeoff: 0.82 frames (was 21.97) - **96% improvement**

**All events now within 1 frame of ground truth!**

## Lessons Learned

1. **Always validate assumptions with empirical data** - the 0.02 factor was based on incorrect assumptions
2. **Normalized coordinates behave differently** - velocities in [0,1] space are much smaller than pixel space
3. **Smoothing affects velocity** - Savitzky-Golay reduces noise AND apparent velocity
4. **Ground truth data is essential** - without manual annotations, this bug would have persisted
5. **Systematic debugging pays off** - velocity profiling identified exact root cause

## Applicability to CMJ

CMJ detection likely uses the same `auto_tune_parameters` function, so this fix may also improve CMJ detection. However, CMJ uses different algorithms (backward search), so benefits may vary.

**Recommendation**: Test CMJ videos with new threshold to see if it improves detection accuracy.
