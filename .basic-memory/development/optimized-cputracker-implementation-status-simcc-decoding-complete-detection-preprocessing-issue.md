---
title: OptimizedCPUTracker Implementation Status - SIMCC Decoding Complete, Detection
  Preprocessing Issue
type: note
permalink: development/optimized-cputracker-implementation-status-simcc-decoding-complete-detection-preprocessing-issue
---

# OptimizedCPUTracker Implementation Status

## Summary

Working on making OptimizedCPUTracker functional (currently returns empty landmarks despite 68 FPS).

## Completed

1. **SIMCC Decoding Implementation** ✅
   - Reverse-engineered rtmlib's SIMCC decoding logic
   - Implemented `get_simcc_maximum` equivalent in `_extract_landmarks_from_output`
   - Implemented affine transform preprocessing (`_get_warp_matrix`, `_rotate_point`, `_get_3rd_point`)
   - Implemented pose preprocessing with RTMPose's mean/std normalization

2. **Research Complete** ✅
   - Found all helper functions in rtmlib source code
   - Understood SIMCC format: dual 1-D heatmaps (simcc_x, simcc_y)
   - Identified key functions: `bbox_xyxy2cs`, `top_down_affine`, `get_simcc_maximum`

3. **Detection Model Issue Identified** ⚠️
   - YOLOX ONNX model output shape: `(1, 1, 5)` not `(1, 8400, 85)`
   - Model has NMS built-in (outputs `[x1, y1, x2, y2, score]`)
   - Current preprocessing returns all zeros: `[[0. 0. 0. 0. 0.]]`
   - rtmlib's YOLOX class works correctly (detects 1 person)

## Current Issue

Detection preprocessing returns all zeros from ONNX model. Possible causes:
1. Input format mismatch (BGR vs RGB, normalization, etc.)
2. Model expects different preprocessing than current implementation
3. Session options affecting model output

## Next Steps

**Option 1: Use rtmlib YOLOX + Optimized Pose Model**
- Use rtmlib's proven YOLOX for detection
- Apply ONNX optimization only to pose model
- Faster to implement, still shows CPU optimization benefit

**Option 2: Debug Detection Preprocessing**
- Compare rtmlib's YOLOX preprocessing line-by-line
- May need to examine ONNX model input/output metadata
- More complex but pure ONNX implementation

**Option 3: Hybrid Approach**
- Use rtmlib's BodyWithFeet as baseline
- Only optimize ONNX session options for pose estimation
- Document limitations

## Files Modified

- `experiments/rtmpose-benchmark/optimized_cpu_tracker.py`
  - Added SIMCC decoding in `_extract_landmarks_from_output`
  - Added affine transform helpers
  - Updated detection preprocessing (still has issues)
  - Updated pose preprocessing to match rtmlib

## Test Results

```
Frame shape: (1920, 1080, 3)
DEBUG: detections[0]: [[0. 0. 0. 0. 0.]]  # Should have non-zero values
DEBUG: scores before filter: [0.]  # Should be > 0.3
DEBUG: No detections passed threshold
Landmarks returned: 0  # Should return 13 landmarks
```

rtmlib YOLOX works:
```
YOLOX detected 1 persons
First bbox: [ 456.18536  484.72638  707.7193  1179.5068 ]
```

## Recommendation

Given the complexity and time spent, recommend **Option 1**: Use rtmlib's YOLOX for detection (proven to work) and only apply ONNX session optimizations to the pose model. This still demonstrates the CPU optimization benefit while using proven components for detection.
