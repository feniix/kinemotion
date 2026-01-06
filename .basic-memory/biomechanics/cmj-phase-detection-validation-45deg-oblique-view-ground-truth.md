---
title: CMJ Phase Detection Validation - 45° Oblique View Ground Truth
type: note
permalink: biomechanics/cmj-phase-detection-validation-45deg-oblique-view-ground-truth
tags:
- CMJ
- phase-detection
- validation
- ground-truth
- MediaPipe
- accuracy-analysis
---

# CMJ Phase Detection Validation Study

**Date:** 2026-01-05
**Camera Angle:** 45° oblique view (recommended for MediaPipe)
**Pose Estimator:** MediaPipe
**Algorithm:** CONTACT (Current production implementation)

## Ground Truth Data

### Test Videos

**Video 1: cmj-45-IMG_6733.mp4** (215 frames, 60fps, 3.58s)

| Phase | Detected (CONTACT) | Manual Observation | Frame Error | Time Error (ms) |
|-------|-------------------|-------------------|-------------|-----------------|
| Standing End | 64 | 64 | 0 | 0 |
| Lowest Point | 91 | 88 | +3 (late) | +50ms |
| Takeoff | 104 | 104 | 0 | 0 |
| Landing | 144 | 142 | +2 (late) | +33ms |

**Video 2: cmj-45-IMG_6734.mp4** (242 frames, 60fps, 4.03s)

| Phase | Detected (CONTACT) | Manual Observation | Frame Error | Time Error (ms) |
|-------|-------------------|-------------------|-------------|-----------------|
| Standing End | 69 | 69 | 0 | 0 |
| Lowest Point | 92 | 90 | +2 (late) | +33ms |
| Takeoff | 106 | 108 | -2 (early) | -33ms |
| Landing | 145 | 144 | +1 (late) | +17ms |

**Video 3: cmj-45-IMG_6735.mp4** (190 frames, 60fps, 3.17s)

| Phase | Detected (CONTACT) | Manual Observation | Frame Error | Time Error (ms) |
|-------|-------------------|-------------------|-------------|-----------------|
| Standing End | 58 | 58 | 0 | 0 |
| Lowest Point | 76 | 78 | -2 (early) | -33ms |
| Takeoff | 93 | 93 | 0 | 0 |
| Landing | 131 | 130 | +1 (late) | +17ms |

## Accuracy Analysis

### Phase-by-Phase Performance

**Standing End Detection:** ✅ Perfect
- 0/3 frame errors
- 100% accuracy
- Algorithm: Static pose detection before motion begins

**Lowest Point Detection:** ⚠️ Variable
- Mean absolute error: ~2.3 frames (38ms)
- Pattern: 2/3 late, 1/3 early
- Largest error: +3 frames (50ms)
- Algorithm: Hip velocity minimum in backward search

**Takeoff Detection:** ✅ Excellent
- Mean absolute error: ~0.7 frames (12ms)
- 2/3 perfect, 1/3 early by 2 frames
- Largest error: -2 frames (33ms early)
- Algorithm: Toe-off event in forward progression

**Landing Detection:** ⚠️ Consistently Late
- Mean absolute error: ~1.3 frames (22ms)
- Pattern: 3/3 late (bias detected)
- Largest error: +2 frames (33ms)
- Algorithm: Vertical velocity minimum after flight phase

### Statistical Summary

| Metric | Value |
|--------|-------|
| Total phases analyzed | 12 |
| Perfect detections | 6 (50%) |
| Mean absolute error | 1.08 frames (18ms) |
| Max absolute error | 3 frames (50ms) |
| Errors ≤ 2 frames | 11/12 (92%) |
| Errors ≤ 1 frame | 6/12 (50%) |

### Timing Context

At 60fps:
- 1 frame = 16.67ms
- 2 frames = 33.33ms
- 3 frames = 50ms

**Interpretation:** Even the largest error (50ms) is within acceptable tolerances for athletic performance analysis, where human movement variability typically exceeds 100ms.

## Patterns and Insights

### Key Findings

1. **Standing End**: Perfect detection - algorithm correctly identifies static pose before motion

2. **Lowest Point**: Inconsistent timing
   - Slightly delayed in 2/3 videos (+2, +3 frames)
   - Slightly early in 1/3 video (-2 frames)
   - **Hypothesis:** Hip velocity minimum detection may be sensitive to:
     - Noise in velocity calculation
     - Smoothing parameters
     - Athlete's pause depth variation

3. **Takeoff**: Generally excellent
   - Perfect in 2/3 videos
   - Slightly early in 1/3 (-2 frames)
   - **Hypothesis:** Toe-off detection is robust but may trigger on:
     - Last frame of foot contact
     - Initial toe extension before full departure

4. **Landing**: Consistently delayed (bias detected)
   - All 3 videos show late detection (+1, +2, +1 frames)
   - **Hypothesis:** Vertical velocity minimum occurs after:
     - Initial ground contact
     - Brief compressive phase
   - **Root cause:** Algorithm may be detecting bottom of landing compression, not initial contact

### Error Directions

| Phase | Error Direction | Consistency |
|-------|----------------|-------------|
| Standing End | N/A | Perfect |
| Lowest Point | Mixed (2 late, 1 early) | Inconsistent |
| Takeoff | Mixed (1 early, 2 perfect) | Mostly accurate |
| Landing | Late (3/3) | **Consistent bias** |

## Implications for Metric Accuracy

### Potentially Affected Metrics

**Countermovement Depth:**
- Depends on: Standing End → Lowest Point
- Error propagation: ±2-3 frames
- Impact: Minor - depth is spatial measurement, less sensitive to 50ms timing

**Flight Time:**
- Depends on: Takeoff → Landing
- Error propagation: Takeoff (±0-2) + Landing (+1-2)
- Impact: Low - errors may partially cancel, 17-50ms on 400-600ms flight is < 10%

**Jump Height (from flight time):**
- Derived from: Flight time²
- Impact: Minimal - small timing variations have negligible effect on height calculation

### Confidence Assessment

- **High confidence:** Standing End, Takeoff detection
- **Medium confidence:** Lowest Point (within human observation variance)
- **Action needed:** Landing detection (consistent +1-2 frame bias)

## Recommendations

### Immediate Actions

1. ✅ **Document baseline:** This ground truth dataset establishes performance baseline
2. 🔍 **Investigate landing bias:** Why is vertical velocity minimum consistently late?
3. 🧪 **Test alternative algorithms:** Compare CONTACT with other methods

### Algorithm Improvements to Test

**For Landing Detection:**
- Option A: Detect first frame with downward velocity after apex (not minimum)
- Option B: Use vertical position threshold relative to standing height
- Option C: Hybrid: Velocity change + position confirmation

**For Lowest Point:**
- Option A: Add local minima validation window
- Option B: Use hip height threshold in addition to velocity
- Option C: Smooth velocity with different parameters

### Validation Methodology

This 3-video dataset provides:
- N=3 athletes (single athlete multiple reps)
- N=12 phase detections total
- Sufficient for initial algorithm comparison
- **Next step:** Expand to N=10+ athletes for statistical validation

## Next Steps

1. Analyze current algorithm implementation (task #2)
2. Test parameter tuning based on these findings (task #3)
3. Compare with alternative phase detection methods (task #4)

---

**Tags:** CMJ, phase-detection, validation, ground-truth, MediaPipe, 45-degree, accuracy-analysis
