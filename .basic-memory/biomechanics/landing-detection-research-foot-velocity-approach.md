---
title: Landing Detection Research - Foot Velocity Approach
type: note
permalink: biomechanics/landing-detection-research-foot-velocity-approach
tags:
- landing-detection
- foot-velocity
- research
- algorithm-design
---

# Landing Detection Research - Foot Velocity Approach

## Context
- Date: 2026-01-05
- Problem: Current landing detection uses hip deceleration, detecting 1-4 frames AFTER initial contact
- Previous attempt: Ankle angle detection failed due to landing style variability (-12 to +3 frames)

## Key Research Papers

### PMC11057390 - VGRF from 2D Video
- Uses OpenPose + COM acceleration to estimate VGRF
- Formula: VGRF = m(aCOM + g)
- Landing defined as VGRF > 10N (initial touch)
- Achieved R=0.835 correlation with force plates

### FootNet (PLOS ONE 2021)
- Uses Bi-LSTM with foot COM velocity + ankle angle + tibia velocity
- Achieved **5ms RMSE** for foot-strike detection
- Ground truth: vGRF >= 50N

### UnderPressure (SIGGRAPH 2022)
- Deep learning for foot contact from motion capture
- Uses pressure insoles as ground truth

## Why Ankle Angle Failed but Foot Velocity Should Work

| Approach | Signal Type | Problem |
|----------|-------------|---------|
| Ankle Angle | Geometric (absolute) | Varies by landing style (forefoot vs heel-first) |
| Foot Velocity | Physics-based (kinematic) | Foot MUST stop when it hits ground, regardless of style |

## Proposed Algorithms

### Algorithm 1: Foot Velocity Landing Detection (FVLD)
1. Extract foot_index_y positions (MediaPipe landmarks 31, 32)
2. Compute SIGNED velocity using Savitzky-Golay deriv=1
3. Find where velocity drops from "high positive" to "near zero"
4. Threshold: foot_velocity < 0.1 * max_falling_velocity

### Algorithm 2: Foot-Hip Divergence Detection (FHDD)
1. Compute gap = hip_y - foot_y (leg extension)
2. Compute gap_velocity = d(gap)/dt
3. During flight: gap_velocity ≈ 0
4. At landing: gap_velocity spikes (hip continues, foot stops)

**Advantages of FHDD:**
- Cancels tracking noise
- No absolute threshold tuning
- Handles different body proportions

## Implementation Notes

Existing code in `src/kinemotion/core/smoothing.py`:
- `compute_velocity_from_derivative()` - uses savgol_filter but returns ABSOLUTE velocity
- Need to modify to return SIGNED velocity for landing detection

MediaPipe landmarks needed:
- LEFT_FOOT_INDEX (31), RIGHT_FOOT_INDEX (32) - toe/forefoot
- LEFT_HEEL (29), RIGHT_HEEL (30) - heel backup
- LEFT_HIP (23), RIGHT_HIP (24) - for FHDD approach

## Expected Improvement

Current detection is 1-4 frames late. Foot-based detection should:
- Detect landing 1-4 frames EARLIER
- At 60fps: improvement of 17-67ms
- Better match force plate "initial contact" definition

## Validation Strategy

1. Compare foot-based vs hip-based detection on existing test videos
2. Foot detection should be EARLIER (not later)
3. If foot detection is later → fallback to hip-based


## Validation Results (2026-01-05)

### Test Setup
- 3 CMJ videos at 45° camera angle
- Ground truth from manual annotation in `ground_truth.json`
- 60 FPS video

### Results by Method

| Method | Mean Error | Abs Mean | Std Dev |
|--------|-----------|----------|---------|
| **Current (foot accel)** | +0.00fr | **0.00fr** | 0.00fr |
| **Foot decel spike** | +0.00fr | **0.00fr** | 0.00fr |
| Foot-hip divergence | -0.33fr | 0.33fr | 0.47fr |
| Vel deriv onset | -1.67fr | 1.67fr | 0.47fr |
| Foot velocity threshold | +2.67fr | 2.67fr | 0.47fr |

### Key Findings

1. **Current algorithm is already excellent** - 0 error across all test videos
2. **Foot velocity threshold FAILED** - detected 2-3 frames LATE (opposite of expectation)
3. **Velocity derivative onset** - detects 1-2 frames EARLIER than visible contact
4. **Foot decel spike** - identical to current (both use acceleration signal)

### Why Foot Velocity Threshold Failed

The original hypothesis was that foot velocity would drop to zero AT contact. Instead:
- Savitzky-Golay smoothing adds phase lag
- The velocity signal remains non-zero due to settling/bouncing
- Threshold crossing happens AFTER the actual impact

### Why Current Algorithm Works So Well

The current algorithm detects **maximum deceleration (impact spike)**, which aligns perfectly with human-observable "first contact" moment. The ground truth annotations were made by humans looking for "Frame where feet make first contact" - and this matches the deceleration spike.

### Recommendations

1. **Keep current algorithm** - it matches human-annotated ground truth perfectly
2. **Velocity derivative onset** could be useful if force-plate-equivalent "initial touch" is needed (detects ~1-2 frames/17-33ms earlier)
3. **Do NOT use foot velocity threshold** - it detects landing too late

### Force Plate vs Video Context

| Detection Type | Algorithm | When Detected |
|---------------|-----------|---------------|
| Force plate (10-50N) | Vel deriv onset | ~1-2 frames before visible contact |
| Visible contact | Current (foot accel) | Exact match with human annotation |
| Full impact | Foot velocity threshold | 2-3 frames after visible contact |

The current algorithm is optimal for matching human-observable landing.
