---
title: Sprinting Analysis Validation Strategy
type: note
permalink: testing/sprinting-analysis-validation-strategy
---

# Sprinting Analysis Validation Strategy

**Status:** Design Document (Pre-Implementation)
**Created:** January 17, 2026
**Type:** Cyclical analysis validation (vs discrete jumps)

## Executive Summary

Sprinting analysis is fundamentally different from existing jump analysis (CMJ, Drop Jump, SJ):

| Aspect | Jump Analysis | Sprinting Analysis |
|--------|---------------|-------------------|
| Movement Type | Discrete (single event) | Cyclical (repeated strides) |
| Key Metrics | Flight time, contact time, RSI | Ground contact time (GCT), flight time, step frequency, step length |
| Challenge | Single takeoff/landing detection | Consistent stride detection across 10-30 strides |
| Frame Rate | 30-60fps acceptable | 120fps+ recommended for accuracy |

## 1. Ground Truth Data Strategy

### Option A: Marker-Based Motion Capture (Gold Standard - Deferred)
**Status:** NOT RECOMMENDED for MVP

**Why Deferred:**
- Cost: $50,000+ for Vicon/Qualisys system
- Access: Requires laboratory partnership
- Timeline: 3-6 months to establish partnership
- Complexity: Requires specialized expertise

**Use Case:** Research publication, post-MVP validation

### Option B: Force Plate / Instrumented Treadmill (Recommended for Phase 2)
**Status:** RECOMMENDED after MVP

**Setup:**
- Instrumented treadmill with 1000Hz optoelectronic sensing (e.g., Optojump Next)
- Validated in Balsalobre-Fernandez (2016) with r=0.94-0.99 correlation
- Cost: $10,000-20,000 for treadmill + sensors
- Access: University performance labs, high-performance centers

**Protocol:**
1. Record 8 consecutive strides at each running speed
2. Speeds: 2.77, 3.33, 3.88, 4.44, 5.0, 5.55 m/s
3. Simultaneous kinemotion + Optojump recording
4. Compare GCT and flight time measurements

### Option C: Known-Height Physics Validation (RECOMMENDED for MVP)
**Status:** PRIMARY MVP VALIDATION METHOD

**Rationale:**
- Cost: ~$100 (measuring tape, ball, smartphone)
- Accessible: Can be done anywhere
- Physics-based: Uses t = sqrt(2h/g) formula
- Proven: Already validated for jump analysis in kinemotion

**Adaptation for Sprinting:**
Cannot directly apply (sprinting is horizontal, not vertical motion).

### Option D: Manual Frame Counting (RECOMMENDED for MVP)
**Status:** PRACTICAL MVP VALIDATION

**Protocol:**
1. Record sprint at 240fps (iPhone 13+ Pro)
2. Use frame-by-frame playback in Kinovea/VLC
3. Manually identify contact frames for each stride
4. Calculate expected GCT = (frame_count / fps)
5. Compare to kinemotion automated detection

**Requirements:**
- High-speed camera (240fps recommended, 120fps minimum)
- Frame-by-frame playback software
- Trained rater (2-hour training session per Bramah 2024)

**Validation Metrics:**
- Mean Absolute Error (MAE): Target < 10ms
- Systematic bias: Target < 5ms
- Correlation: Target r > 0.95

## 2. Test Video Specifications

### Minimum Viable Set (MVP)

| Category | Specification |
|----------|---------------|
| **Athlete Levels** | 2 athletes (1 recreational, 1 trained) |
| **Distances** | 10m, 20m, 30m sprints |
| **Speeds** | Submaximal, maximal effort |
| **Camera Angles** | 90 degrees lateral (perpendicular to running direction) |
| **Frame Rates** | 60fps minimum, 120fps preferred |
| **Resolution** | 720p minimum, 1080p preferred |
| **Lighting** | Consistent, diffuse lighting (no shadows) |
| **Background** | High contrast (uniform color) |

### Recommended Full Validation Set

| Category | Specifications |
|----------|---------------|
| **Athlete Levels** | 3 levels x 2 athletes = 6 athletes (recreational, college, elite) |
| **Distances** | 10m, 20m, 30m, 40m (acceleration to max speed) |
| **Speeds** | Jog (3 m/s), tempo (5 m/s), sprint (7-9 m/s) |
| **Camera Angles** | 90 degrees lateral, 45 degrees oblique |
| **Frame Rates** | 60fps, 120fps, 240fps versions |
| **Trials** | 3 trials per condition |
| **Total Videos** | ~100-150 videos |

### Video Filename Convention

```
sprint_[LEVEL]_[DISTANCE]m_speed[SPEED]_run[NUMBER].mp4

Examples:
- sprint_recreational_10m_speed5_run1.mp4
- sprint_elite_30m_speed8_run2.mp4
- sprint_college_20m_speed6_run1.mp4
```

## 3. Acceptance Criteria Matrix

### Primary Metrics

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| **MAE (GCT)** | < 10ms | 1 frame at 120fps = 8.3ms |
| **RMSE (GCT)** | < 15ms | Accounts for outliers |
| **Systematic Bias** | < 5ms | No consistent under/over-measurement |
| **Correlation (r)** | > 0.95 | Strong linear relationship |
| **Stride Detection** | > 90% | Must detect at least 9 of 10 strides |
| **Consistent Detection** | CV < 5% | Low variability across strides |

### Secondary Metrics

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| **Step Frequency Accuracy** | < 3% error | Calculated from GCT + flight time |
| **Flight Time MAE** | < 15ms | Shorter duration, harder to measure |
| **Inter-stride CV** | < 8% | Consistency across strides |

### Failure Modes

| Issue | Detection | Action |
|-------|-----------|--------|
| **MAE > 20ms** | Automated test | Algorithm parameter tuning |
| **Detection rate < 70%** | Automated test | Check pose tracking quality |
| **High bias (>10ms)** | Statistical check | Frame rate verification |
| **Correlation < 0.90** | Statistical check | Review detection algorithm |

## 4. Edge Cases

### What Breaks Stride Detection

| Edge Case | Impact | Mitigation |
|-----------|--------|------------|
| **Partial body in frame** | Missed detections | Camera positioning guidelines |
| **Variable lighting** | Tracking failures | Consistent lighting requirements |
| **Multiple runners** | Wrong person tracked | Single-subject requirement for MVP |
| **Diagonal camera angle** | Perspective distortion | 90 degrees lateral recommended |
| **Low frame rate (<30fps)** | Insufficient temporal resolution | Minimum 60fps requirement |
| **Motion blur** | Unclear contact/flight | Shutter speed guidelines |
| **Occluded foot** | False GCT values | Camera angle guidelines |
| **Starting/stopping** | Irregular strides | Analyze middle strides only |
| **Turns/curves** | Changed mechanics | Straight-line sprinting only |

### Edge Case Testing Protocol

**Priority 1 (Critical):**
1. Partial foot occlusion (10%, 25%, 50%)
2. Variable lighting (bright to dark transition)
3. Low frame rate (30fps vs 60fps vs 120fps)
4. Diagonal camera angles (30, 45, 60 degrees)

**Priority 2 (Important):**
1. Motion blur at different speeds
2. Starting phase (acceleration irregular strides)
3. Deceleration phase (irregular strides)
4. Different running surfaces (turf, track, grass)

**Priority 3 (Nice to have):**
1. Left vs right leg asymmetry
2. Footwear differences (spikes vs trainers)
3. Clothing contrast with background

## 5. Validation Bounds Testing

### Proposed Sprinting Bounds (Physiological)

**Ground Contact Time (GCT):**
- Elite sprinters: 0.08-0.12s (80-120ms)
- College athletes: 0.12-0.18s (120-180ms)
- Recreational: 0.18-0.25s (180-250ms)
- Absolute limits: 0.06-0.35s

**Flight Time:**
- Elite sprinters: 0.10-0.14s
- College athletes: 0.08-0.12s
- Recreational: 0.06-0.10s
- Absolute limits: 0.04-0.20s

**Step Frequency:**
- Elite sprinters: 4.5-5.5 Hz (270-330 steps/min)
- College athletes: 3.5-4.5 Hz (210-270 steps/min)
- Recreational: 2.5-3.5 Hz (150-210 steps/min)
- Absolute limits: 2.0-6.0 Hz

**Step Length:**
- Elite sprinters: 2.0-2.5m
- College athletes: 1.5-2.0m
- Recreational: 1.0-1.5m
- Absolute limits: 0.5-3.0m

### Bound Verification Testing

**Test Structure:**
```python
class TestSprintingBounds:
    def test_gct_elite_in_bounds()
    def test_gct_recreational_in_bounds()
    def test_flight_time_elite_in_bounds()
    def test_step_frequency_calculated_correctly()
    def test_gct_below_absolute_minimum_fails()
    def test_gct_above_absolute_maximum_fails()
    def test_flight_time_physically_possible()
```

### Warning vs Error Logic

**ERROR (Data Corruption):**
- GCT < 0.06s or > 0.35s
- Flight time < 0.04s or > 0.20s
- Step frequency < 2.0Hz or > 6.0Hz
- Negative time values
- Zero strides detected

**WARNING (Unusual but Possible):**
- GCT exceeds profile range by >20%
- CV > 10% across strides (high variability)
- Missing >20% of strides in analysis window
- Left-right asymmetry >30%

**INFO (Normal Variation):**
- GCT within profile range
- Consistent step frequency
- Minor asymmetry (<20%)

## 6. Risk Assessment

### High Risk Areas

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Frame rate inaccuracy** | Timing bias | Medium | Verify with ffprobe, document actual fps |
| **Camera positioning** | Detection failures | High | Clear guidelines, visual guide overlay |
| **Pose tracking at high speed** | Missing landmarks | Medium | Use 120fps+, test at each speed |
| **Stride segmentation** | Wrong stride count | High | Robust algorithm, manual verification |
| **Lighting changes** | Tracking inconsistency | Low | Controlled environment requirement |

### Medium Risk Areas

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Athlete variability** | Wide metric ranges | High | Profile-based bounds |
| **Surface differences** | GCT variations | Medium | Document surface type |
| **Fatigue effects** | GCT increase during trial | Low | Analyze middle strides only |

### Low Risk Areas

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Clothing contrast** | Minor tracking issues | Low | Recommend high-contrast clothing |
| **Footwear type** | Minor GCT differences | Low | Document in metadata |

## 7. Implementation Timeline

**Phase 1 (MVP Validation - 2-3 weeks):**
1. Create manual frame counting protocol
2. Record 20 test videos (2 athletes x 5 conditions x 2 trials)
3. Manually verify GCT for all strides
4. Compare kinemotion output to manual counts
5. Establish MAE, bias, correlation metrics
6. Create validation bounds

**Phase 2 (Extended Validation - 4-6 weeks):**
1. Record 100+ test videos per full specification
2. Test across all athlete levels
3. Test edge cases systematically
4. Refine bounds and thresholds
5. Create normative data tables

**Phase 3 (Gold Standard Validation - 3-6 months):**
1. Establish partnership with motion capture lab
2. Record simultaneous marker-based and video data
3. Compare against force plate/treadmill data
4. Research publication (optional)

## 8. Test Plan Template

```python
# tests/sprinting/test_sprinting_validation.py

class TestSprintingGroundTruth:
    """Manual frame counting validation."""

    def test_gct_accuracy_vs_manual_count()
        """Compare kinemotion GCT to manual frame counting."""

    def test_flight_time_accuracy_vs_manual_count()
        """Compare kinemotion flight time to manual counting."""

    def test_stride_detection_count()
        """Verify correct number of strides detected."""

class TestSprintingBounds:
    """Physiological bounds testing."""

    def test_gct_elite_bounds()
    def test_gct_college_bounds()
    def test_gct_recreational_bounds()
    def test_flight_time_physically_possible()
    def test_step_frequency_in_range()

class TestSprintingEdgeCases:
    """Edge case testing."""

    def test_partial_occlusion_handling()
    def test_low_framerate_detection()
    def test_acceleration_phase_irregular_strides()
    def test_multiple_runners_in_frame()
    def test_diagonal_camera_angle()

class TestSprintingMetrics:
    """Derived metrics testing."""

    def test_step_frequency_calculation()
    def test_step_length_calculation()
    def test_stride_variability_cv()
    def test_left_right_asymmetry_detection()
```

## References

- Bramah et al. (2024). Sprint Mechanics Assessment Score (S-MAS). AJSM.
- Balsalobre-Fernandez et al. (2016). iPhone app validity for running mechanics. J Appl Biomech.
- Morin et al. (2005). Simple method for measuring running stiffness. J Appl Biomech.
- Existing kinemotion validation patterns: docs/validation/known-height-validation.md
