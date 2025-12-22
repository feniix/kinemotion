---
title: RTMLib Pose Estimation Research Summary
type: note
permalink: research/rtmlib-pose-estimation-research-summary
---

# RTMLib Pose Estimation Research Summary

## Overview
Research conducted December 2025 comparing pose estimation systems for kinemotion's multi-sport expansion.

## Key Finding
**RTMLib (RTMPose)** is the recommended choice for multi-sport analysis on Apple Silicon.

## Accuracy Benchmarks
- RTMPose: 5.62° RMSE (running analysis)
- MediaPipe: 6.33° RMSE
- RTMPose is 12% more accurate than MediaPipe for sprint biomechanics

## Apple Silicon Compatibility
- RTMLib works natively on M1/M2/M3 via ONNX Runtime
- No CUDA or MMPose dependencies required
- Installation: `pip install rtmlib`

## Tested Configuration
- MacBook Pro M1 Pro, 16GB unified RAM
- RTMLib lightweight mode: 25-40 FPS
- RTMLib balanced mode: 15-25 FPS

## Recommendation Matrix
| Use Case | Recommendation |
|----------|----------------|
| Jump analysis only | MediaPipe adequate |
| Multi-sport platform | **RTMLib/RTMPose** |
| Browser preview | MediaPipe (TensorFlow.js) |
| Research-grade | RTMPose + multi-camera |

## Documentation Created
- `docs/research/pose-estimator-comparison-2025.md` - Full comparison
- `docs/reference/pose-systems.md` - Updated quick reference
- `CLAUDE.md` - Updated with RTMLib recommendation

## Related
- [RTMLib GitHub](https://github.com/Tau-J/rtmlib)
- [Pose Estimator Comparison](pose-estimator-comparison-2025)
- [Sports Biomechanics Research](sports-biomechanics-pose-estimation)
