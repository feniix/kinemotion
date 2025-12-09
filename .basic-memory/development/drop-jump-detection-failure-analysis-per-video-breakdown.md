---
title: Drop Jump Detection Failure Analysis - Per Video Breakdown
type: note
permalink: development/drop-jump-detection-failure-analysis-per-video-breakdown
---

# Drop Jump Detection Failure Analysis

**Date**: 2025-12-06
**Analysis Type**: Per-video debugging
**Dataset**: 3 drop jump videos @ 45° oblique

## Critical Findings

### Video 1: dj-45-IMG_6739.MOV ⚠️ PARTIAL SUCCESS

| Event | Ground Truth | Detected | Error | Status |
|-------|--------------|----------|-------|--------|
| drop_start | 118 | 130 | 12 frames (200ms) | ⚠️ Moderate error |
| landing | 131 | 130.0 | 1 frame (17ms) | ✅ **Excellent!** |
| takeoff | 144 | 211 | 67 frames (1117ms) | ❌ **Broken** |

**Detected contact duration**: 1350ms vs **GT: 217ms** (6x too long!)

**Analysis:**
- `detect_drop_start`: Working but 12 frames late
- Landing detection: **Works excellently when drop_start succeeds**
- Takeoff detection: **Detected end of video (frame 211/212)** instead of actual takeoff

### Video 2: dj-45-IMG_6740.MOV ❌ CATASTROPHIC FAILURE

| Event | Ground Truth | Detected | Error | Status |
|-------|--------------|----------|-------|--------|
| drop_start | 141 | **0** | NULL | ❌ **Failed completely** |
| landing | 154 | **0.0** | NULL | ❌ **Failed completely** |
| takeoff | 166 | 231 | 65 frames (1084ms) | ❌ **End of video** |

**Detected contact duration**: 3852ms (entire video!)

**Analysis:**
- `detect_drop_start`: **Returned 0 or None** (complete failure)
- Landing: Defaulted to frame 0 when drop_start failed
- Takeoff: Detected near end of video (frame 231/232)

### Video 3: dj-45-IMG_6741.MOV ❌ CATASTROPHIC FAILURE (with lucky takeoff)

| Event | Ground Truth | Detected | Error | Status |
|-------|--------------|----------|-------|--------|
| drop_start | 119 | **0** | NULL | ❌ **Failed completely** |
| landing | 134 | **0.7** | 133 frames (2223ms) | ❌ **Start of video** |
| takeoff | 146 | 146.1 | 0.1 frame (1ms) | ✅ **Accidentally perfect!** |

**Detected contact duration**: 2424ms vs **GT: 200ms** (12x too long!)

**Analysis:**
- `detect_drop_start`: **Returned 0 or None** (complete failure)
- Landing: Detected at **frame 0.7 (start of video!)** when drop_start failed
- Takeoff: **Accidentally correct** - probably a fluke

## Root Cause Analysis

### 1. `detect_drop_start` is Fundamentally Broken

**Success Rate**: 1/3 videos (33%)

**Failure Mode**: Returns 0 or None on 2/3 videos

**Impact**: When `detect_drop_start` fails, all downstream detection fails catastrophically

**Hypothesis**: The stable baseline detection algorithm is too sensitive or looking for wrong signal

### 2. Landing Detection CASCADE FAILURE

**When drop_start works** (Video 1): Landing detection is **excellent** (1 frame error)

**When drop_start fails** (Videos 2 & 3): Landing defaults to frame 0 or fails completely

**Conclusion**: Landing detection algorithm is actually GOOD, but depends on correct drop_start

### 3. Takeoff Detection: "End of Video" Bug

**Pattern**: Takeoff consistently detected near end of video:
- Video 1: Frame 211/212 (end)
- Video 2: Frame 231/232 (end)
- Video 3: Frame 146/244 (accidentally correct)

**Hypothesis**: Algorithm can't find proper takeoff (velocity threshold too sensitive?) so defaults to last frame

## Priority Fixes

### P0 - CRITICAL: Fix `detect_drop_start`

**Current behavior**: Fails 2/3 times, returns 0/None

**Investigation needed**:
1. Check stable baseline detection thresholds
2. Verify position change detection
3. Look at video-specific characteristics that cause failure

**Location**: `src/kinemotion/dropjump/analysis.py:detect_drop_start`

### P1 - HIGH: Fix Takeoff Detection

**Current behavior**: Defaults to end of video when can't find takeoff

**Investigation needed**:
1. Check contact state transitions
2. Verify velocity/acceleration thresholds for liftoff
3. Ensure proper search window after landing

**Location**: `src/kinemotion/dropjump/analysis.py:find_contact_phases`

### P2 - VERIFY: Landing Detection

**Current behavior**: Works when drop_start succeeds, fails when it doesn't

**Action**: Likely no fix needed - will work once drop_start is fixed

## Next Steps

1. **Examine `detect_drop_start` algorithm** in detail
2. **Plot position/velocity traces** for all 3 videos to see what's different
3. **Fix stable baseline detection** (videos 2 & 3)
4. **Fix takeoff detection** "end of video" default behavior
5. **Re-evaluate after fixes**

## Expected Improvement

If we fix `detect_drop_start` and takeoff detection:
- **Drop start error**: Should drop from 90 frames → <10 frames
- **Landing error**: Already good (1 frame), should stay good
- **Takeoff error**: Should drop from 22 frames → <5 frames
- **Overall MAE**: Could improve from 36 frames → ~5-10 frames
