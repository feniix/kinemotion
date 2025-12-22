---
title: Real-Time Pose Estimation Summary
type: note
permalink: research/real-time-pose-estimation-summary
---

# Real-Time Pose Estimation Summary

## Key Systems

### RTMO (One-Stage) - Best for Real-Time
- **Paper:** CVPR 2024
- **Speed:** 141 FPS (V100), 20-40 FPS (CPU)
- **Accuracy:** 74.8% AP on COCO
- **Key advantage:** Constant time regardless of people count
- **Available in RTMLib:** `from rtmlib import RTMO`

### RTMPose (Two-Stage) - Best for Accuracy
- **Speed:** 430 FPS (GPU), 90 FPS (CPU)
- **Accuracy:** 75.8% AP on COCO
- **Limitation:** Slows down with more people (N × inference time)

### MediaPipe - Best for Browser
- **Speed:** 30+ FPS (browser/CPU)
- **Accuracy:** ~70% AP
- **Key advantage:** TensorFlow.js, no server needed

## One-Stage vs Two-Stage

```
Two-Stage: Detect → Crop → Pose (per person)
  1 person:  ~15ms
  6 people:  ~65ms  ← Slows down!

One-Stage: Single pass for all
  1 person:  ~10ms
  6 people:  ~10ms  ← Constant!
```

## Architecture Options

### Option A: Browser-Only (MediaPipe)
- Latency: ~30-50ms
- No server costs
- Good for: Camera preview, basic feedback

### Option B: Hybrid (Recommended)
- MediaPipe preview in browser
- RTMO analysis on server (periodic)
- Best accuracy + instant feedback

### Option C: Full Server-Side (WebSocket)
- Latency: ~50-100ms
- Maximum accuracy
- Requires good internet

## Latency Budget

```
Browser-only: ~35ms total
  Capture: 3ms + Process: 30ms + Render: 2ms

Server-side: ~78ms total
  Capture: 3ms + Upload: 20ms + Process: 25ms + Download: 20ms + Render: 5ms
```

## Recommended Strategy

1. **Phase 1 (MVP):** Upload video → analyze → results
2. **Phase 2:** MediaPipe browser preview (camera setup)
3. **Phase 3:** Hybrid real-time (if coaches request it)

## Code Quick Reference

```python
# RTMO (one-stage, fast)
from rtmlib import RTMO
rtmo = RTMO(backend='onnxruntime', device='cpu')
keypoints, scores = rtmo(frame)

# RTMPose (two-stage, accurate)
from rtmlib import Body
body = Body(mode='balanced', backend='onnxruntime', device='cpu')
keypoints, scores = body(frame)
```

## Related Documents
- [Real-Time Pose Estimation Guide](real-time-pose-estimation)
- [RTMPose vs RTMLib vs MediaPipe](rtmpose-rtmlib-mediapipe-comparison)
- [Pose Estimator Comparison 2025](pose-estimator-comparison-2025)
