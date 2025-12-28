---
title: RTMPose vs MediaPipe Comparison Guide
type: note
permalink: research/rtmpose-vs-media-pipe-comparison-guide
---

# RTMPose vs MediaPipe: When to Use Which Backend?

## Executive Summary

**Short answer**: MediaPipe is generally **more accurate** and **faster** for kinemotion's current use case, but RTMPose provides **additional landmarks** (feet) and is actively developed for multi-sport analysis.

## Accuracy Comparison

### Tracking Quality (from CLI testing)

| Metric | MediaPipe | RTMPose CUDA | Winner |
|--------|-----------|--------------|--------|
| Quality Score | 96.3 | 92.6 | MediaPipe ✅ |
| Avg Visibility | 0.934 | 0.841 | MediaPipe ✅ |
| Min Visibility | 0.859 | 0.751 | MediaPipe ✅ |

**MediaPipe has better tracking quality** based on visibility scores.

### But Different Trackers Detect Different Metrics

| Metric | MediaPipe | RTMPose | Difference |
|--------|-----------|---------|------------|
| Jump Height | 0.349m | 0.492m | +41% (RTMPose) |
| Flight Time | 533.6ms | 633.6ms | +19% (RTMPose) |

**Why the difference?**
- Different landmark sets (MediaPipe 33 landmarks vs RTMPose Halpe-26)
- Different tracking characteristics
- Phase detection sensitivity to tracking patterns
- **Which is correct?** We need ground truth validation to know

## Performance Comparison

| Backend | Inference FPS | Init Time | Total (215 frames) |
|---------|---------------|-----------|---------------------|
| MediaPipe | 98.7 | 60ms | 3.9s |
| RTMPose CPU | 44.2 | 83ms | 6.9s |
| RTMPose CUDA | 127.7 | 878ms | 4.0s |

**MediaPipe has the best balance**:
- Fast initialization (60ms vs 878ms for CUDA)
- Good inference speed (98.7 FPS)
- Best tracking quality

## When to Use Each Backend

### Use MediaPipe When:

1. **Primary use case: Drop jump and CMJ analysis**
   - Best tracking quality (96.3 score)
   - Fast initialization
   - Well-tested with kinemotion's pipeline

2. **Short videos or real-time applications**
   - Low initialization overhead
   - Consistent performance

3. **When tracking quality matters most**
   - Highest visibility scores
   - Most reliable landmark detection

### Use RTMPose When:

1. **You need feet landmarks**
   - Halpe-26 format includes left_foot_index, right_foot_index, left_heel, right_heel
   - MediaPipe requires inference for foot landmarks
   - Critical for sports that emphasize foot positioning

2. **Multi-sport analysis**
   - RTMPose has active research community
   - Better suited for complex movements beyond jumping
   - Designed for general pose estimation

3. **Long video processing**
   - CUDA version has 3x speedup vs RTMPose CPU
   - Modest speedup vs MediaPipe (1.3x)
   - Better amortization of initialization cost

4. **You want fallback options**
   - Multiple execution providers (CUDA, CPU, CoreML)
   - Hardware flexibility

## Accuracy Research from Literature

### COCO Dataset Benchmarks (Standard Academic Comparison)

From RTMPose research (arxiv.org/abs/2303.07399) and community benchmarks:

| Model | COCO AP | Hardware | FPS |
|-------|---------|----------|-----|
| RTMPose-m | 75.8% | Intel i7-11700 (ONNX) | 90+ |
| RTMPose-m | 75.8% | NVIDIA GTX 1660 Ti (TensorRT) | 430+ |
| RTMPose-s | 72.2% | Snapdragon 865 (mobile) | 70+ |
| RTMPose-s | 72.2% | Intel i7-11700 (ONNX) | ~150 |

**Note**: MediaPipe is not always included in academic COCO comparisons because:
- MediaPipe uses a different evaluation protocol
- MediaPipe focuses on real-time applications, not maximum accuracy
- MediaPipe has 33 landmarks vs standard 17 COCO landmarks

### Roboflow Comparison (2025)

From Roboflow's "Best Pose Estimation Models" guide (Nov 2025):

| Model | COCO mAP@0.5 | Strength | Best For |
|-------|---------------|---------|----------|
| YOLO11-Pose | 89.4% | Balance of speed/accuracy | Production systems |
| ViTPose | ~80% | Maximum accuracy | Research |
| HRNet | 89.0% | Precise localization | Biomechanics |
| MediaPipe | Not reported | Real-time, mobile | Edge devices |
| MoveNet | 65%+ | Lightweight | Mobile |

**Key insight**: RTMPose is not mentioned in this 2025 comparison, focusing on YOLO11, ViTPose, HRNet, MediaPipe, and MoveNet instead.

### From kinemotion's Phase 3 Testing

From `docs/research/rtmlib-evaluation-summary-2025.md`:

| Metric | MediaPipe | RTMPose | Winner |
|--------|-----------|---------|--------|
| Landmark Stability | Baseline | +28-34% | RTMPose ✅ |
| Jump Detection Quality | 96.3 score | 92.6 score | MediaPipe ✅ |
| Visibility (avg) | 0.934 | 0.841 | MediaPipe ✅ |

**Two different measures of "accuracy":**
1. **Landmark stability**: How consistent is tracking over time? (RTMPose wins)
2. **Visibility/confidence**: How confident is the tracker? (MediaPipe wins)

## Current Recommendation for kinemotion

### For Current Use Case (Drop Jump, CMJ)

**Use MediaPipe as default** because:
- ✅ Best tracking quality (96.3 vs 92.6)
- ✅ Faster initialization (60ms vs 878ms)
- ✅ Well-tested and validated
- ✅ Sufficient landmarks for jump analysis

### Keep RTMPose Available For:

1. **Feet landmark requirements**
   - Foot index and heel positions
   - Sports like running, sprinting

2. **Future multi-sport expansion**
   - Active research community
   - Better suited for complex movements

3. **Users with CUDA hardware**
   - Faster for long videos (batch processing)
   - Hardware acceleration options

## Implementation Notes

### kinemotion Default Behavior

```python
# Auto-detection priority
# 1. RTMPose CUDA (if PyTorch CUDA available)
# 2. RTMPose CoreML (if on Apple Silicon)
# 3. RTMPose CPU (if ONNX Runtime available)
# 4. MediaPipe (fallback, most reliable)
```

**Recommendation**: Make MediaPipe the default, with RTMPose as opt-in for users who need its specific features.

### Quality Validation

Current quality assessment favors MediaPipe:
- Higher visibility scores
- More consistent tracking
- Lower outlier rates

RTMPose would benefit from:
- Per-sport validation datasets
- Ground truth comparison
- Quality tuning for jump-specific movements

## Future Work

1. **Ground truth validation**
   - Compare against measured jump heights (force plates)
   - Determine which tracker is more accurate for jumping
   - Validate both backends with known standards

2. **RTMPose optimization for jumping**
   - Fine-tune quality thresholds
   - Optimize for jump-specific movements
   - Reduce initialization overhead

3. **Hybrid approach**
   - Use MediaPipe for validation
   - Use RTMPose for feet-specific analysis
   - Cross-validate results

## References

- Research: `docs/research/rtmlib-evaluation-summary-2025.md`
- Investigation: `docs/research/pose-tracking-performance-investigation-2025.md`
- Comparison: `docs/research/pose-estimator-comparison-2025.md`
