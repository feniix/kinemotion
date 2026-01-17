---
title: MediaPipe Sprinting Analysis Feasibility Assessment
type: note
permalink: video-processing/media-pipe-sprinting-analysis-feasibility-assessment
---

# MediaPipe Sprinting Analysis Feasibility Assessment

**Date:** 2025-01-17
**Assessor:** Computer Vision Engineer
**Purpose:** Validate MediaPipe capability for sprinting analysis at max velocity

## Executive Summary

**Assessment: NEEDS WORK with significant caveats**

MediaPipe can handle sprinting analysis BUT with critical limitations:
- **30fps**: Marginally viable (elite GCT = ~80-90ms, 1 frame = 33ms)
- **60fps**: Viable with careful smoothing design
- **120fps**: Recommended for elite sprinting analysis

**Key Finding:** Elite sprinter ground contact times (80-90ms at max velocity) are perilously close to single-frame durations at common frame rates. This creates fundamental sampling challenges.

---

## 1. MediaPipe Performance at High Speed

### Motion Blur Handling
- MediaPipe has documented issues with motion blur (GitHub issue #221)
- Fast-moving limbs at 12 m/s create significant inter-frame displacement
- Motion blur degrades keypoint detection accuracy, especially for extremities

### Tracking Accuracy for Fast Movements
- MediaPipe excels at **30+ FPS on CPU** (Roboflow benchmark)
- Uses temporal smoothing (`smoothLandmarks: true`) for stable video tracking
- Two-stage pipeline: person detection → keypoint localization

### Documented Sprinting/Running Performance
- RTMPose-based systems validated for sprinting (MDPI 2025 study)
- Multi-camera setups achieved centimeter-level accuracy at 60fps
- **MediaPipe specifically** lacks validation data for elite sprinting

### Occlusion Issues at 90 deg Lateral
- **Known problem**: GitHub issue #4868 - "Improve accuracy of detecting poses where limbs are occluded"
- At 90 deg lateral, limbs frequently occlude each other during sprinting
- During flight phase, tracking may be lost
- Left/right confusion documented for rapid movements

---

## 2. Frame Rate Reality Analysis

### Elite Sprinter Temporal Constraints

| Metric | Value | Frames at 30fps | Frames at 60fps | Frames at 120fps |
|--------|-------|-----------------|-----------------|------------------|
| Elite GCT (max velocity) | 80-90ms | 2.4-2.7 frames | 4.8-5.4 frames | 9.6-10.8 frames |
| Acceleration GCT | 140-200ms | 4.2-6 frames | 8.4-12 frames | 16.8-24 frames |
| Flight time | ~100-120ms | 3-3.6 frames | 6-7.2 frames | 12-14.4 frames |

### Smartphone Frame Rate Distribution (2024-2025)

| Frame Rate | Availability | Market Estimate |
|------------|--------------|------------------|
| 30fps (default) | ~100% of phones | All users |
| 60fps | ~70-80% of phones | Most mid-range+ |
| 120fps | ~15-25% of phones | Flagship only (iPhone Pro, Galaxy S/Ultra, Xperia) |
| 240fps | ~5-10% of phones | Premium flagships |

**Critical insight:** Only ~1 in 5 users have phones capable of 120fps recording.

---

## 3. Occlusion Issues

### 90 deg Lateral View Problems
- **Proven Issue**: MediaPipe struggles with limb occlusion (#4868)
- During swing phase, trailing leg often occluded by forward leg
- Arm swing creates frequent self-occlusion of torso
- Foot placement detection unreliable during crossover

### Flight Phase Tracking
- MediaPipe's temporal smoothing helps but doesn't eliminate tracking loss
- Confidence scores drop significantly during flight phase
- May require higher tracking confidence thresholds (sacrificing detection sensitivity)

### Left/Right Ankle Crossover
- MediaPipe can confuse left/right limbs during rapid movements
- Issue compounded by motion blur at high velocities
- 45 deg oblique view (validated for CMJ) also problematic for sprinting due to perspective

---

## 4. RTMPose vs MediaPipe Comparison

| Metric | MediaPipe | RTMPose | Advantage |
|--------|-----------|---------|-----------|
| COCO mAP | ~65-70% (est.) | 75.8% (RTMPose-m) | RTMPose +10-15% |
| CPU FPS | 30+ | 90+ (i7-11700) | RTMPose 3x faster |
| Mobile FPS | 30+ | 70+ (Snapdragon 865) | RTMPose 2x faster |
| Sprinting validation | None | 3x3 basketball study | RTMPose validated |
| Production maturity | Excellent | Good | MediaPipe easier |
| Cross-platform | Web, mobile, desktop | Python, C++, mobile | MediaPipe broader |

### RTMPose for Sprinting
- **Validated** in 3x3 basketball with linear sprints (MDPI 2025)
- Multi-camera 60fps achieved centimeter-level accuracy
- Speed estimates ICC = 0.97-1.00 vs time-motion analysis
- **Production-ready** for deployment

### Recommendation
RTMPose is **significantly better** for sprinting analysis but requires:
- Python backend integration (no web SDK)
- More complex deployment than MediaPipe
- Multi-camera setup for optimal accuracy

---

## 5. Smoothing Parameters Analysis

### The Over-Smoothing Problem

**At 60fps with 5-frame window:**
- Smoothing window = 5 frames / 60fps = 83.3ms
- Elite GCT = 80-90ms
- **Smoothing window APPROACHES or EQUALS entire ground contact phase**

**At 60fps with 3-frame window:**
- Smoothing window = 3 frames / 60fps = 50ms
- Still covers 56-63% of elite GCT

**At 120fps with 5-frame window:**
- Smoothing window = 5 frames / 120fps = 41.7ms
- Covers 46-52% of elite GCT (more acceptable)

### Recommended Smoothing Strategy
```python
# Frame-rate adaptive smoothing
if fps >= 120:
    window = 5  # 42ms smoothing
elif fps >= 60:
    window = 3  # 50ms smoothing
else:
    window = 2  # 67ms smoothing - minimum viable
```

### Alternative: One-Euro Filter
- Adaptive smoothing based on velocity
- Reduces lag during high-velocity movements
- Better preserves rapid transitions (ground contact → flight)

---

## 6. Technical Risks & Mitigations

### Risk 1: Undersampling at 30fps
**Risk:** 2.4-2.7 frames during elite GCT means missing critical events

**Mitigation:**
- Require minimum 60fps for sprinting analysis
- Implement frame interpolation (AI-based upscaling) as fallback
- Warn users about accuracy limitations at 30fps

### Risk 2: Motion Blur at High Velocity
**Risk:** 12 m/s limb movement creates severe motion blur

**Mitigation:**
- Require good lighting conditions
- Recommend shutter speed priority mode if available
- Implement confidence-based filtering (drop low-confidence frames)

### Risk 3: Occlusion-Induced Tracking Loss
**Risk:** Limb occlusion during swing phase causes tracking errors

**Mitigation:**
- Use 45-45 degree oblique views (not pure lateral)
- Implement Kalman filtering for limb trajectory prediction
- Multi-camera setup if accuracy critical

### Risk 4: Smoothing Lag Masking True GCT
**Risk:** Temporal smoothing obscures the exact contact moment

**Mitigation:**
- Use adaptive window size based on detected velocity
- Implement event-based detection (unfiltered for contact events)
- Separate detection and analysis pipelines

### Risk 5: Left/Right Confusion
**Risk:** MediaPipe swaps left/right limbs during crossover

**Mitigation:**
- Track limb trajectories across frames (temporal consistency)
- Use velocity direction to resolve ambiguities
- Confidence scores + voting across frame sequence

---

## 7. Recommended Frame Rate Policy

```python
def validate_sprinting_video(fps, target_level="elite"):
    """
    Validate video for sprinting analysis.

    Returns: (is_valid, warning_message, recommended_action)
    """

    if fps >= 120:
        return True, None, None
    elif fps >= 60:
        if target_level == "elite":
            return (True,
                   "60fps acceptable for elite analysis but 120fps recommended",
                   "Consider higher frame rate for peak velocity phases")
        return True, None, None
    elif fps >= 30:
        return (False,
               "30fps insufficient for reliable sprinting analysis",
               "Re-record at minimum 60fps (120fps for elite athletes)")
    else:
        return (False,
               f"{fps}fps below minimum threshold",
               "Re-record at minimum 60fps")
```

---

## 8. Alternative Approaches

### If MediaPipe Insufficient

1. **RTMPose** (Recommended alternative)
   - 10-15% better accuracy
   - Validated for sprinting movements
   - Requires Python backend

2. **YOLO11 Pose**
   - 89.4% mAP@0.5 (vs MediaPipe ~65-70%)
   - Real-time performance
   - Better occlusion handling

3. **Multi-Camera Setup**
   - 3+ cameras for 3D reconstruction
   - DLT algorithm for triangulation
   - Validated in 3x3 basketball study

4. **Frame Interpolation**
   - AI-based upscaling (30fps → 60fps)
   - RIFE, FILM, or similar models
   - Adds ~50-100ms processing latency

5. **Hybrid Approach**
   - MediaPipe for real-time feedback
   - RTMPose for post-analysis
   - Progressive accuracy enhancement

---

## 9. Validation Protocol

### Required Testing
1. Record elite sprinter at 120fps
2. Establish ground truth with force plates
3. Compare MediaPipe GCT detection vs actual
4. Measure error margin by frame rate
5. Validate smoothing parameter impact

### Success Criteria
- GCT detection within +/- 10ms at 60fps
- GCT detection within +/- 5ms at 120fps
- Step length accuracy within 5cm
- No tracking loss during >90% of strides

---

## 10. Final Recommendations

### For MVP Sprinting Analysis
1. **Require minimum 60fps** (hard requirement)
2. **Recommend 120fps** for elite athletes
3. **Use adaptive smoothing** based on velocity
4. **Implement confidence filtering** for motion blur frames
5. **Validate against ground truth** before production

### For Production-Grade Analysis
1. **Switch to RTMPose** for 10-15% accuracy gain
2. **Multi-camera setup** for critical applications
3. **Custom training** on sprinting-specific dataset
4. **Kalman/One-Euro filtering** for trajectory smoothing
5. **Real-time + post-processing** pipeline architecture

### User Communication
- Be transparent about frame rate requirements
- Explain why 30fps is insufficient for sprinting
- Provide clear recording guidelines
- Offer frame interpolation as fallback (with caveats)

---

## Conclusion

**MediaPipe is marginally viable for sprinting analysis at 60fps, but NOT recommended for elite-level analysis at 30fps.** The fundamental constraint is temporal resolution: elite ground contact times (80-90ms) are too close to single-frame durations for reliable detection at common frame rates.

**Recommended path forward:**
1. Short-term: Require 60fps minimum, implement adaptive smoothing
2. Medium-term: Evaluate RTMPose integration
3. Long-term: Multi-camera setup with custom training for sprinting-specific patterns

**Critical success factor:** User education on recording requirements. Most phones default to 30fps - users must manually enable higher frame rates.
