---
title: Drop Jump Position-Based Filtering Fix
type: note
permalink: development/drop-jump-position-based-filtering-fix
tags:
- drop-jump
- mediapipe
- velocity-threshold
- position-filtering
- phase-detection
- bug-fix
---

# Drop Jump Position-Based Filtering Fix

## Problem
Drop jump analysis was producing incorrect metrics:
- RSI values of 8.4+ (impossible, normal range is 0.5-3.5)
- Ground contact time of 83ms (too short)
- Flight time of 0ms (when it should be ~600ms)

## Root Causes Identified

### 1. Velocity Threshold Too Low
- `base_velocity_threshold = 0.004` became 0.002 at 60fps
- This was at or below MediaPipe landmark jitter noise floor (0.5-2% per frame)
- **Fix**: Increased to `base_velocity_threshold = 0.012`
- Location: `src/kinemotion/core/auto_tuning.py:176`

### 2. Flight Phase Fragmentation at Jump Apex
- At jump peak, vertical velocity approaches zero
- Velocity-only detection incorrectly classified apex as ON_GROUND
- Caused fragmented flight phases: IN_AIR → ON_GROUND → IN_AIR

### 3. Position-Based Filtering Solution
Added `_compute_near_ground_mask()` to `detect_ground_contact()`:
- Ground baseline: 90th percentile of foot positions
- Tolerance: 25% of position range (min 3%)
- Both velocity AND position must indicate ground contact
- Location: `src/kinemotion/dropjump/analysis.py:337-375`

### 4. Drop Jump Phase Detection Update
With position filtering, box period is now classified as IN_AIR:
- Old pattern: BOX(ground) → DROP(air) → CONTACT(ground) → JUMP(air) → LANDING(ground)
- New pattern: BOX+DROP(air) → CONTACT(ground) → JUMP(air) → LANDING(ground)

Updated `_identify_main_contact_phase()` to detect new pattern:
- First phase is IN_AIR (index 0)
- First ground phase IS the contact phase (not on box)
- Location: `src/kinemotion/dropjump/kinematics.py:229-304`

## Results After Fix
| Metric | Before | After |
|--------|--------|-------|
| Ground Contact Time | 466.67 ms | 214.55 ms |
| Flight Time | 0 ms | 587.56 ms |
| Jump Height | 0 m | 0.423 m |
| RSI | null | 2.74 |

## Key Files Modified
1. `src/kinemotion/core/auto_tuning.py` - velocity threshold
2. `src/kinemotion/dropjump/analysis.py` - position-based filtering
3. `src/kinemotion/dropjump/kinematics.py` - phase detection logic
4. `tests/dropjump/test_contact_detection.py` - updated tests

## Validation
- All 632 tests pass
- Coverage: 79.84%
- Test video produces physiologically reasonable metrics


## Follow-up Fix (2026-01-13): Height Tolerance Adjustment

### Problem
Video 3 (IMG_6741) showed:
- GCT of 83ms (too short, expected ~200ms)
- Takeoff detected 5 frames early (frame 141 vs manual 146)

### Root Cause
The 25% height tolerance was too strict for reactive contact phases:
- 90th percentile ground baseline was dominated by the landing phase (fully settled)
- Contact phase (reactive stance) has lower foot positions than landing phase
- Only 6 frames of the 13-frame contact phase met the near-ground criterion

### Fix
Changed `height_tolerance` default from 0.25 to 0.35 in:
- `_compute_near_ground_mask()`
- `detect_ground_contact()`

### Validation
All 3 test videos now show ≤2 frame difference from manual observations:

| Video | Phase | Before Fix | After Fix |
|-------|-------|------------|-----------|
| IMG_6741 | Takeoff | -5 frames | 0 frames |
| IMG_6741 | GCT | 83ms | 235ms |
| All videos | Max diff | 5 frames | 2 frames |
| All videos | Accuracy | 67% | 100% |

### Key Insight
Reactive contact phases (drop jump landing → immediate takeoff) have different position characteristics than settled ground contact. A 35% tolerance captures the full reactive stance while still filtering out jump apex.


## Optimization (2026-01-13): Sub-frame Interpolation for ±1 Frame Accuracy

### Problem
After the height tolerance fix, accuracy was still ±2 frames for some phases:
- Contact start: +1 to +2 frames late
- Landing: +1 to +2 frames late

### Root Cause Analysis
The integer frame indices came from raw phase detection (velocity threshold + position filtering), but the curvature-refined interpolated phases had sub-frame precision that wasn't being used for integer indices.

Example for contact start:
- Raw detection: frame 132
- Interpolated (curvature-refined): 131.84
- Manual observation: frame 130

Using floor(131.84) = 131 is closer to manual than raw 132.

### Solution
Apply floor() to curvature-refined interpolated values for both contact start and landing:

1. **Contact start** (`calculate_drop_jump_metrics`):
   ```python
   refined_contact_start = int(np.floor(contact_start_frac))
   metrics.contact_start_frame = refined_contact_start
   ```

2. **Landing** (`_analyze_flight_phase`):
   ```python
   refined_flight_end = int(np.floor(flight_end_frac))
   metrics.flight_end_frame = refined_flight_end
   ```

### Why floor() Works
- Velocity-based detection is ~1-2 frames LATE (detects when velocity settles, not initial impact)
- Curvature refinement captures impact earlier via acceleration patterns
- floor() biases toward earlier detection, compensating for the velocity delay
- This matches the moment of FIRST ground contact rather than when contact is established

### Final Results

| Video | Phase | Before | After | Manual |
|-------|-------|--------|-------|--------|
| 6739 | Contact | +2 | +1 | 130 |
| 6739 | Landing | +2 | 0 | 180 |
| 6740 | Contact | +1 | +1 | 153 |
| 6740 | Landing | 0 | -1 | 201 |
| 6741 | Contact | +2 | -1 | 133 |
| 6741 | Landing | +1 | -1 | 184 |

**All phases now within ±1 frame (100% accuracy at 16.7ms at 60fps)**

### Files Modified
- `src/kinemotion/dropjump/kinematics.py`:
  - `calculate_drop_jump_metrics()`: lines 550-558
  - `_analyze_flight_phase()`: lines 417-429
