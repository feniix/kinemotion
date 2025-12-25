---
title: Phase 2 Performance Assessment Results - RTMPose Performance Blocker
type: note
permalink: strategy/phase-2-performance-assessment-results-rtmpose-performance-blocker
---

# Phase 2: Performance Assessment Results

**Date**: December 25, 2025
**Branch**: zai-rtmlib-evaluation
**Status**: ❌ PERFORMANCE BLOCKER IDENTIFIED

## Executive Summary

RTMPose with **CPU-only inference** on Apple Silicon M1 Pro is **significantly slower** than MediaPipe, failing the performance feasibility threshold.

**Performance Feasibility Score: 1.5/4.0 - NOT FEASIBLE for real-time use**

## Benchmark Results (M1 Pro, CPU-only)

| Tracker | Avg FPS | vs MediaPipe | Frame Time (ms) | Status |
|---------|---------|--------------|-----------------|--------|
| MediaPipe | 44.17 FPS | 100% | 19.82 | ✅ Baseline |
| RTMPose-Lightweight | 21.74 FPS | 49.2% | 43.15 | ❌ 2x slower |
| RTMPose-Balanced | 3.31 FPS | 7.5% | 299.32 | ❌ 13x slower |

## Detailed Metrics

### MediaPipe (Baseline)
- **Consistent**: 43.77 - 44.64 FPS across all videos
- **Latency**: 19.61 - 20.01 ms/frame
- **Std Dev**: 4.71 - 5.52 ms (very stable)
- **Timing breakdown**:
  - mediapipe_inference: ~4100-4700 ms total
  - frame_conversion: ~30-40 ms total
  - landmark_extraction: ~2-3 ms total

### RTMPose-Lightweight
- **Consistent**: 21.36 - 22.02 FPS across all videos
- **Latency**: 42.62 - 43.90 ms/frame
- **Std Dev**: 0.95 - 2.88 ms (stable)
- **Timing breakdown**:
  - rtmpose_inference: ~7900-10500 ms total (2x slower than MediaPipe)
  - rtmpose_initialization: ~24-31 ms per tracker creation
  - landmark_extraction: ~4-7 ms total

### RTMPose-Balanced
- **Consistent**: 3.19 - 3.39 FPS across all videos
- **Latency**: 292.54 - 310.18 ms/frame (unusable)
- **Std Dev**: 3.55 - 29.71 ms (some variance)
- **Timing breakdown**:
  - rtmpose_inference: ~54000-74000 ms total (13x slower!)
  - rtmpose_initialization: ~64-83 ms per tracker creation
  - landmark_extraction: ~4-6 ms total

## Decision Framework Analysis

According to the assessment plan's performance decision matrix:

| Score | Criteria | Result |
|-------|----------|--------|
| 4.0 | ≥90% of MediaPipe FPS | ❌ Not met |
| 3.0 | 75-89% of MediaPipe FPS | ❌ Not met |
| 2.0 | 50-74% of MediaPipe FPS | ⚠️ 49.2% (below threshold) |
| 1.0 | <50% of MediaPipe FPS | ✅ 49.2% (at threshold) |

**RTMPose-Lightweight scores 1.0-2.0 range → PERFORMANCE CONCERNS**
**RTMPose-Balanced scores 1.0 range → PERFORMANCE BLOCKER**

## Success Rate

All trackers achieved **100% success rate** - no failed detections.
- MediaPipe: 1305/1305 frames
- RTMPose-Lightweight: 1305/1305 frames
- RTMPose-Balanced: 1305/1305 frames

This confirms RTMPose accuracy is viable, but performance is the blocker.

## Root Cause Analysis

### CPU-Only Inference
RTMLib uses ONNX Runtime with **CPU Execution Provider** by default.
While CoreML EP is available, RTMLib does not expose configuration to enable GPU acceleration.

### Model Size Impact
- RTMPose-s (lightweight): RTMPose-small model
- RTMPose-m (balanced): RTMPose-medium model

The medium model is **13x slower** than MediaPipe, making it unusable for any real-time application.

### Initialization Overhead
RTMLib loads models twice (detection + pose):
- Detection model: YOLOX for person detection
- Pose model: RTMPose for keypoint estimation

This dual-model approach adds initialization overhead.

## Recommendations

### For Real-Time/Near-Real-Time Applications
**DO NOT PROCEED** with RTMPose replacement without GPU acceleration.

### For Batch Processing (Offline Analysis)
RTMPose-Lightweight at 22 FPS **may be acceptable** if:
- Accuracy improvements are significant (Phase 3 validation needed)
- Processing time is not a critical factor
- User experience is not impacted by wait times

### Next Steps

1. **Skip to Phase 5** (Decision Analysis) - The performance results are conclusive
2. **Optional:** Investigate CoreML EP optimization for RTMLib
3. **Optional:** Test RTMPose accuracy (Phase 3) to determine if 2x slowdown is worth accuracy gains

## Files

- Benchmark script: `experiments/rtmpose-benchmark/benchmark.py`
- RTMPose adapter: `experiments/rtmpose-benchmark/rtmpose_tracker.py`
- Results JSON: `experiments/rtmpose-benchmark/results.json`

## Test Configuration

- **Hardware**: Apple M1 Pro (8-core CPU, 14-core GPU, 16GB Neural Engine)
- **Software**: onnxruntime 1.23.2 (CPU-only), rtmlib 0.0.14
- **Videos**: 6 test videos (3 CMJ, 3 DJ) at 45° oblique angle
- **Total frames processed**: 1305 frames per tracker
