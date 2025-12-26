---
title: MediaPipe Tasks API Migration Complete
type: note
permalink: development/media-pipe-tasks-api-migration-complete
---

# MediaPipe Tasks API Migration Complete

**Date:** 2025-12-26
**Status:** ✅ Complete - All 626 tests passing, 80.18% coverage

---

## Summary

Successfully migrated from MediaPipe Solution API (deprecated) to MediaPipe Tasks API.

## Changes Made

### New Files

1. **`src/kinemotion/core/pose_landmarks.py`**
   - Defines `LANDMARK_INDICES` mapping landmark names to indices (0-32)
   - Defines `KINEMOTION_LANDMARKS` - subset used in kinemotion analysis

2. **`src/kinemotion/core/model_downloader.py`**
   - `get_model_path()` - Downloads and caches model files
   - `get_model_cache_dir()` - Platform-specific cache directory
   - Supports "lite", "full", and "heavy" model variants
   - Model URL: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task`

### Modified Files

1. **`src/kinemotion/core/pose.py`**
   - Replaced `mp.solutions.pose.Pose` with `mp.tasks.vision.PoseLandmarker`
   - Uses `PoseLandmarker.create_from_options()` with VIDEO mode
   - `process_frame()` now takes `timestamp_ms` parameter
   - Wraps numpy array in `mp.Image` for Tasks API
   - Index-based landmark access instead of enum

2. **`src/kinemotion/core/video_io.py`**
   - Added `_frame_index` tracking
   - Added `current_timestamp_ms` property
   - Added `frame_index` property

3. **`src/kinemotion/core/pipeline_utils.py`**
   - Updated `_process_frames_loop()` to pass timestamps to `process_frame()`

4. **`src/kinemotion/core/__init__.py`**
   - Exported new modules: `LANDMARK_INDICES`, `KINEMOTION_LANDMARKS`, `get_model_path`, `get_model_cache_dir`

5. **`pyproject.toml`**
   - Added `platformdirs>=4.0.0` dependency

## Key API Changes

| Aspect | Solution API (Old) | Tasks API (New) |
|--------|-------------------|-----------------|
| Import | `mp.solutions.pose.Pose` | `mp.tasks.vision.PoseLandmarker` |
| Constructor | `Pose(...)` | `PoseLandmarker.create_from_options()` |
| Input | `numpy.ndarray` | `mp.Image(image_format=mp.ImageFormat.SRGB, data=array)` |
| Process method | `pose.process(rgb_frame)` | `landmarker.detect_for_video(mp_image, timestamp_ms)` |
| Landmark access | `results.pose_landmarks.landmark[enum]` | `result.pose_landmarks[0][idx]` |
| Model | Bundled | Download `.task` file |

## Quality Checks

- ✅ **pyright**: 0 errors, 0 warnings (strict mode)
- ✅ **ruff**: All checks passed
- ✅ **pytest**: 626 tests passed
- ✅ **Coverage**: 80.18% (above 50% threshold)

## Model File

The model is downloaded on first use to:
- macOS: `~/Library/Caches/kinemotion/models/pose_landmarker_heavy.task`
- Linux: `~/.cache/kinemotion/models/pose_landmarker_heavy.task`
- Windows: `%LOCALAPPDATA%\kinemotion\models\pose_landmarker_heavy.task`
