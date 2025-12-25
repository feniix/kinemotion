---
title: Phase 2 Performance Assessment - RTMPose Performance Blocker
type: note
permalink: strategy/phase-2-performance-assessment-rtmpose-performance-blocker
---

# Phase 2: Performance Assessment - RTMPose Performance Blocker

**Status:** ❌ DO NOT PROCEED for real-time use

## Executive Summary

After comprehensive performance testing and optimization attempts, RTMPose on Apple Silicon M1 Pro (CPU-only) cannot match MediaPipe's performance for real-time video analysis.

## Benchmark Results

| Configuration | FPS | vs MediaPipe | Avg Frame Time (ms) |
|--------------|-----|--------------|---------------------|
| **MediaPipe (Baseline)** | 44.17 | 100% | 19.7 |
| RTMPose-Lightweight | 21.74 | 49.2% | 42.6 |
| RTMPose-Balanced | 3.31 | 7.5% | 294.4 |

**Success Criteria Check:**
- Target: ≥80% of MediaPipe FPS
- Actual: 49.2% (lightweight), 7.5% (balanced)
- Result: ❌ FAILED

## Optimization Attempts

### 1. OpenCV DNN Backend
**Result:** FAILED
- RTMPose uses TopK operator not supported by OpenCV DNN
- Error: "ERROR during processing node with 2 inputs and 2 outputs: [TopK]"

### 2. Threading Optimizations
**Result:** NO IMPROVEMENT
- Single-threaded: 21.95 FPS
- Multi-threaded (default): 21.97 FPS
- Difference: Within margin of error (0.2%)

### 3. CoreML Execution Provider
**Result:** NOT APPLICABLE
- ONNX Runtime 1.23.2 includes CoreMLExecutionProvider
- rtmlib-coreml fork supports `device='coreml'`
- However: Fork doesn't have BodyWithFeet class (needed for Halpe-26 with feet)
- Only has Body class (COCO 17 keypoints, no feet)

## Root Cause Analysis

**Primary Bottleneck:** CPU-only inference

RTMPose models require:
- YOLOX detector (person detection)
- RTMPose pose estimator (keypoint prediction)

Both running on ONNX Runtime CPU EP. GPU acceleration via CoreML would require:
1. The rtmlib-coreml fork (for CoreML EP support)
2. A BodyWithFeet implementation (doesn't exist in fork)

## Decision Framework

**Performance Feasibility Score: 1.5/4.0**

| Criterion | Score | Notes |
|-----------|-------|-------|
| FPS Target (≥80% MediaPipe) | 0.5/1 | Achieved 49.2% |
| Latency (≤50ms avg) | 0.5/1 | 42.6ms (passes, but 2x slower) |
| Optimization Potential | 0.0/1 | ExHAUSTED: OpenCV failed, threading no help, CoreML requires missing class |
| Production Readiness | 0.5/1 | Not viable for real-time |

## Recommendation

**For Real-Time Analysis:** STAY WITH MediaPipe
- 2x faster performance
- Validated for jump analysis
- All 13 landmarks supported

**For Offline/Batch Analysis:** MAYBE consider RTMPose
- If accuracy improvements are critical
- If processing time is not a constraint
- Would need custom BodyWithFeet implementation with CoreML

## Next Steps

1. **Continue with MediaPipe** for MVP
2. **Re-evaluate RTMPose** if:
   - rtmlib-coreml adds BodyWithFeet support
   - Apple Silicon GPU acceleration becomes plug-and-play
   - Accuracy benefits are proven significant for jump metrics

## Files Created

- `experiments/rtmpose-benchmark/benchmark.py` - Main benchmark script
- `experiments/rtmpose-benchmark/rtmpose_tracker.py` - RTMPose adapter
- `experiments/rtmpose-benchmark/results.json` - Complete benchmark data
- `experiments/rtmpose-benchmark/optimization_test.py` - Optimization tests
- `experiments/rtmpose-benchmark/coreml_tracker.py` - CoreML attempt (incomplete)
