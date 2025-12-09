---
title: Drop Jump Fix - Drop Start Successful, Landing and Takeoff Remain
type: note
permalink: development/drop-jump-fix-drop-start-successful-landing-and-takeoff-remain
---

# Drop Jump Detection Fix - Progress Update

**Date**: 2025-12-06
**Status**: Partial success - drop_start fixed, landing/takeoff still broken

## Fixes Implemented

### ✅ Fix 1: Add drop_start_frame field to DropJumpMetrics
- **File**: `src/kinemotion/dropjump/kinematics.py` line 60
- **Change**: Added `self.drop_start_frame: int | None = None`

### ✅ Fix 2: Store drop_start in calculate_drop_jump_metrics
- **File**: `src/kinemotion/dropjump/kinematics.py` line 417
- **Change**: `metrics.drop_start_frame = drop_start_frame_value if drop_start_frame_value > 0 else None`

### ✅ Fix 3: Fix metadata storage in process_dropjump_video
- **File**: `src/kinemotion/api.py` lines 551-556
- **Change**: Use `metrics.drop_start_frame` instead of `metrics.contact_start_frame`
- **Before**: Was storing landing frame as drop_frame
- **After**: Correctly stores actual drop_start

### ✅ Fix 4: Improve position_change_threshold
- **File**: `src/kinemotion/dropjump/kinematics.py` line 168
- **Change**: `position_change_threshold=0.01` (was 0.005)
- **Result**: Better accuracy, especially on video 3

## Results After Fix

### Overall Performance
- **Before**: 36.15 frames MAE (602.5ms)
- **After**: 23.12 frames MAE (385.3ms)
- **Improvement**: **36% reduction in error!**

### Drop Start Detection (FIXED!)
| Video | Ground Truth | Detected | Error | Status |
|-------|--------------|----------|-------|--------|
| Video 1 | 118 | 119 | 1 frame | ✅ Excellent |
| Video 2 | 141 | 141 | 0 frames | ✅ **Perfect!** |
| Video 3 | 119 | 120 | 1 frame | ✅ Excellent |

**Mean error**: 0.67 frames (11ms at 60fps)
**Before**: 90.67 frames (broken)
**Improvement**: **99%!**

### Landing Detection (STILL BROKEN)
| Video | Ground Truth | Detected | Error | Issue |
|-------|--------------|----------|-------|-------|
| Video 1 | 131 | 130.0 | 1 frame | ✅ Works! |
| Video 2 | 154 | 0.0 | NULL | ❌ Returns 0 |
| Video 3 | 134 | 0.7 | 133 frames | ❌ Returns start of video |

**Mean error**: 96.12 frames (still broken)

### Takeoff Detection (STILL BROKEN)
| Video | Ground Truth | Detected | Error | Issue |
|-------|--------------|----------|-------|-------|
| Video 1 | 144 | 211.0 | 67 frames | ❌ End of video |
| Video 2 | 166 | 231.0 | 65 frames | ❌ End of video |
| Video 3 | 146 | 146.1 | 0.1 frame | ✅ Accidentally correct |

**Mean error**: 21.71 frames

## Remaining Issues

### Issue 1: Landing Detection Cascade Failure

**Problem**: When drop_start detection puts athlete already near or past landing, landing detection fails.

**Hypothesis**:
- Video 2: drop_start=141, landing_GT=154 (only 13 frames apart)
- Algorithm may be filtering out landing as "too soon after drop"
- Returns 0 as fallback

**Next steps**: Investigate `_filter_phases_after_drop` and contact phase detection logic

### Issue 2: Takeoff "End of Video" Default

**Problem**: Takeoff consistently detected at last frame of video on 2/3 videos.

**Hypothesis**:
- Contact phase detection thinks athlete stays on ground until end
- Never detects takeoff → defaults to last frame
- Ground contact time shows 1350ms and 3852ms (way too long!)

**Root cause**: `find_contact_phases` or contact state detection failing to identify end of ground contact

**Next steps**:
1. Debug contact_states for videos 1 & 2
2. Check if velocity/acceleration thresholds for liftoff are too strict
3. May need to adjust `detect_ground_contact` parameters

## Summary

**Wins**:
- ✅ drop_start detection now excellent (0.67 frame error)
- ✅ Overall error reduced by 36%
- ✅ Proper metadata storage implemented

**Still Broken**:
- ❌ Landing detection (96 frame error)
- ❌ Takeoff detection (22 frame error)

**Next Priority**: Fix takeoff detection (contact phase end detection)
