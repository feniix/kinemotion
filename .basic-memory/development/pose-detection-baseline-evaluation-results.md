---
title: Pose Detection Baseline Evaluation Results
type: note
permalink: development/pose-detection-baseline-evaluation-results
---

# Pose Detection Baseline Evaluation Results

**Date**: 2025-12-06
**Dataset**: 6 videos @ 45° oblique (3 CMJ + 3 Drop Jump)
**Target Accuracy**: Within 5 frames (~83ms at 60fps)
**Overall MAE**: **36.15 frames** (602.5ms at 60fps) ❌

## CMJ Detection Performance

| Event | Mean Error | Std Dev | Max Error | Median | Status |
|-------|-----------|---------|-----------|--------|--------|
| **standing_end** | 29.67 | 1.25 | 31.00 | 30.00 | ❌ POOR |
| **lowest_point** | 9.00 | 1.41 | 11.00 | 8.00 | ⚠️ NEEDS WORK |
| **takeoff** | 1.33 | 0.47 | 2.00 | 1.00 | ✅ EXCELLENT |
| **landing** | 3.33 | 3.30 | 8.00 | 1.00 | ✅ GOOD |

### Analysis

**✅ Working Well:**
- **Takeoff detection**: 1.33 frames (~22ms) - EXCEEDS target!
- **Landing detection**: 3.33 frames (~56ms) - Within acceptable range

**❌ Critical Issues:**
- **standing_end detection**: 29.67 frames (~495ms) - **CONSISTENTLY OFF BY ~30 FRAMES**
  - Very low variance (±1.25) suggests systematic bias
  - Algorithm likely detecting wrong phase transition
  - **Root cause**: Probably detecting countermovement start too early

- **lowest_point detection**: 9.00 frames (~150ms) - Moderate error
  - Needs refinement but not critical
  - May improve when standing_end is fixed

## Drop Jump Detection Performance

| Event | Mean Error | Std Dev | Max Error | Median | Status |
|-------|-----------|---------|-----------|--------|--------|
| **drop_start** | 90.67 | 56.35 | 141.00 | 119.00 | ❌ BROKEN |
| **landing** | 97.06 | 66.43 | 154.00 | 133.30 | ❌ BROKEN |
| **takeoff** | 21.97 | 30.43 | 65.00 | 0.85 | ⚠️ INCONSISTENT |

### Analysis

**❌ CRITICAL FAILURES:**
- **drop_start**: 90.67 frames (~1511ms) - **COMPLETELY BROKEN**
  - High variance (±56 frames) - inconsistent detection
  - Algorithm detecting drop WAY too early (standing on box phase)
  - **Root cause**: `detect_drop_start` baseline detection failing

- **landing**: 97.06 frames (~1618ms) - **COMPLETELY BROKEN**
  - Massive systematic error
  - Algorithm thinks landing happens way before actual contact
  - **Root cause**: Contact detection algorithm failing

- **takeoff**: 21.97 frames (~366ms) - INCONSISTENT
  - Median is actually good (0.85 frames)
  - But one video has 65 frame error → algorithm works sometimes, fails catastrophically other times
  - Needs investigation of failure case

## Priority Fixes

### P0 - Critical (Must Fix)

1. **Drop jump `detect_drop_start`** (90 frame error)
   - Current algorithm searching for stable baseline + drop
   - Appears to be detecting wrong event (too early)
   - Need to examine individual video results to understand failure mode

2. **Drop jump `landing` detection** (97 frame error)
   - Contact detection algorithm (`detect_ground_contact`) failing
   - `velocity_threshold=0.02` may be too sensitive
   - Need to check if feet are being tracked correctly at 45° angle

3. **CMJ `standing_end` detection** (30 frame error)
   - Systematic ~30 frame early detection
   - Algorithm detecting something consistently wrong
   - Need to examine velocity/position traces

### P1 - Improvement

4. **CMJ `lowest_point` detection** (9 frame error)
   - Moderate improvement needed
   - May auto-improve when standing_end is fixed

5. **Drop jump `takeoff` detection** (22 frame error)
   - Works well on 2/3 videos
   - One catastrophic failure case needs investigation

## Next Steps

1. **Debug drop jump videos individually**
   - Watch debug videos with detected vs ground truth overlays
   - Examine position/velocity traces
   - Identify why `detect_drop_start` fails

2. **Debug CMJ standing_end**
   - Plot velocity/position for standing phase
   - Check if algorithm is using wrong threshold/window

3. **Implement fixes**
   - Adjust parameters based on findings
   - Re-evaluate after each fix

4. **Grid search optimization** (AFTER fixes)
   - Once algorithms work correctly, optimize parameters
   - Grid search won't help if algorithm logic is fundamentally wrong

## Ground Truth Data Quality

All 6 videos successfully annotated:
- CMJ: cmj-45-IMG_6733, 6734, 6735
- Drop Jump: dj-45-IMG_6739, 6740, 6741

Annotations appear consistent and reasonable based on frame numbers.
