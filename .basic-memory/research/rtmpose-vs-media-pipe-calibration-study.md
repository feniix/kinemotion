---
title: RTMPose vs MediaPipe Calibration Study
type: note
permalink: research/rtmpose-vs-media-pipe-calibration-study
tags:
- rtmpose
- mediapipe
- calibration
- cmj
- research
---

# RTMPose vs MediaPipe Calibration Study

## Problem
RTMPose (used by default on macOS via CoreML) produces different CMJ phase detection results than MediaPipe, resulting in ~4.1cm jump height underestimation.

## Root Cause Analysis
- RTMPose detects takeoff **+2 frames late** consistently across all test videos
- Landing detection is accurate (mean error: +0.3 frames)
- Position signals are highly correlated (0.996) - not a coordinate issue
- The difference is in velocity/acceleration micro-patterns affecting derivative-based takeoff detection

## Calibration Solution
Apply a **-2 frame offset** to RTMPose takeoff detection:

```python
# Calibration offsets by pose estimator
POSE_CALIBRATION = {
    "rtmpose": {"takeoff_offset": -2, "landing_offset": 0},
    "mediapipe": {"takeoff_offset": 0, "landing_offset": 0},
}
```

## Validation Results

| Estimator | Without Calibration | With Calibration |
|-----------|-------------------|------------------|
| MediaPipe | 0.83 cm MAE | 0.83 cm MAE |
| RTMPose | 4.12 cm MAE | **0.83 cm MAE** |

## Key Findings
1. Position-level calibration (linear transform) doesn't help
2. Frame offset is simple and effective
3. RTMPose has systematic +2 frame takeoff bias
4. Both estimators can achieve same accuracy with calibration

## Implementation
Add `pose_estimator` parameter to `detect_cmj_phases()` to apply estimator-specific calibration offsets.

## Related
- [Pose Estimator Comparison](docs/research/pose-estimator-comparison-2025.md)
- CMJ Analysis: `src/kinemotion/cmj/analysis.py`
