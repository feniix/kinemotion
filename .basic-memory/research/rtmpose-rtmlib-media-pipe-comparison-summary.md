---
title: RTMPose RTMLib MediaPipe Comparison Summary
type: note
permalink: research/rtmpose-rtmlib-media-pipe-comparison-summary
---

# RTMPose vs RTMLib vs MediaPipe - Quick Summary

## Key Distinction

**RTMPose** = Neural network architecture (the model)
**RTMLib** = Deployment wrapper for RTMPose (runs models without MMPose)
**MediaPipe** = Separate end-to-end solution from Google

RTMPose and RTMLib are complementary, not competitors!

## Accuracy Comparison

| Model | COCO AP | Joint Angle RMSE |
|-------|---------|------------------|
| RTMPose-m | 75.8% | 5.62° |
| RTMPose-s | 72.2% | - |
| MediaPipe Heavy | ~70-72% | 6.33° |
| MediaPipe Full | ~68-70% | - |

**RTMPose is 12% more accurate for running/sprint biomechanics.**

## Speed Comparison (CPU)

| System | FPS Range |
|--------|-----------|
| RTMLib balanced | 15-25 FPS |
| RTMLib lightweight | 25-40 FPS |
| MediaPipe Full | 30+ FPS |

## Platform Support

| Platform | RTMLib | MediaPipe |
|----------|--------|-----------|
| Apple Silicon | **Native** | Native |
| Browser | No | **Yes (TF.js)** |
| Mobile | No | **Yes** |
| Multi-person | **Yes** | Limited |

## Architecture Differences

**RTMPose:**
- Top-down (detect person, then pose)
- SimCC head (coordinate classification)
- CSPNeXt backbone
- 17 keypoints (COCO)

**MediaPipe:**
- Single-shot detector
- Heatmap regression
- BlazePose architecture
- 33 landmarks

## Recommendations

- **Backend analysis**: RTMLib (better accuracy, Apple Silicon native)
- **Browser preview**: MediaPipe (TensorFlow.js)
- **Mobile apps**: MediaPipe (native SDKs)
- **Multi-sport (jumps/sprints/lifts)**: RTMLib

## Installation

```bash
# RTMLib (recommended)
pip install rtmlib

# MediaPipe
pip install mediapipe
```

## Related Documents
- [Full Comparison](rtmpose-rtmlib-mediapipe-comparison)
- [Pose Estimator Comparison 2025](pose-estimator-comparison-2025)
- [RTMLib Research Summary](rtmlib-pose-estimation-research-summary)
