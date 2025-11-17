# Kinemotion Quality Presets & Parameter Specifications

**Date:** November 17, 2025
**Version:** 1.0 (For Implementation)
**Owner:** ML Data Scientist + Biomechanics Specialist

______________________________________________________________________

## Overview

This document specifies all quality presets and parameters for Kinemotion, organized by:

1. Jump metrics (Drop Jump, CMJ) - VALIDATED
1. Running gait - RECOMMENDED (needs validation)
1. Real-time optimization - PROFILING NEEDED
1. Multi-person detection - DESIGN PHASE

______________________________________________________________________

## Part 1: Jump Quality Presets (Drop Jump & CMJ)

### Current Implementation Status

✓ Validated against published CMJ research
✓ 74.27% test coverage
✓ Used in production

### Drop Jump Presets

**Fast Preset** (Fastest processing, acceptable accuracy)

```yaml
model_complexity: 0  # Lite model (fastest)
detection_confidence: 0.30
tracking_confidence: 0.30
butterworth_order: 2
butterworth_cutoff_hz: 10
savgol_window_length: 15  # Larger window (more smoothing)
savgol_polyorder: 2
velocity_threshold_ms: 0.15  # More forgiving

estimated_latency_ms: 35-45
estimated_accuracy: 85-90%
use_case: Real-time feedback (lower accuracy acceptable)
```

**Balanced Preset** (Recommended default)

```yaml
model_complexity: 1  # Full model (standard)
detection_confidence: 0.50
tracking_confidence: 0.50
butterworth_order: 2
butterworth_cutoff_hz: 8
savgol_window_length: 11  # Medium window
savgol_polyorder: 2
velocity_threshold_ms: 0.10

estimated_latency_ms: 50-70
estimated_accuracy: 92-95%
use_case: Standard analysis (coaching, research)
```

**Accurate Preset** (Maximum accuracy)

```yaml
model_complexity: 1  # Full model
detection_confidence: 0.70
tracking_confidence: 0.70
butterworth_order: 3
butterworth_cutoff_hz: 6
savgol_window_length: 7  # Smaller window (less smoothing)
savgol_polyorder: 3  # Higher order (capture derivatives)
velocity_threshold_ms: 0.05  # Strict

estimated_latency_ms: 80-110
estimated_accuracy: 95-98%
use_case: Research, precision measurement
```

### CMJ Presets

**Identical to Drop Jump presets above.** CMJ analysis uses same confidence thresholds and filtering parameters as drop jump, with following differences:

```yaml
# CMJ-specific additions (same base presets)
phase_detection_mode: backward_search  # Search from peak downward
triple_extension_enabled: true  # CMJ-specific metric
ankle_angle_calculation: foot_index  # Use toes for plantarflexion

# All other parameters identical to drop jump presets
```

______________________________________________________________________

## Part 2: Running Gait Quality Presets (RECOMMENDED)

### Status: NEEDS VALIDATION

These presets are based on published running biomechanics research but need empirical validation (Week 4-5, before public launch).

### Running Fast Preset (Real-time coaching)

```yaml
model_complexity: 0  # Lite model (critical for real-time performance)
detection_confidence: 0.65  # Higher than jump (foot swing occlusion risk)
tracking_confidence: 0.60
butterworth_order: 2
butterworth_cutoff_hz_lower_body: 4.0  # Slower lower body motion
butterworth_cutoff_hz_upper_body: 10.0  # Arms move faster
savgol_window_length: 11  # Stride cycle at 180 spm ≈ 0.67s
savgol_polyorder: 2
velocity_threshold_ms: 0.08  # More forgiving (noise tolerance)
foot_contact_threshold: 0.2  # Vertical acceleration threshold
zero_crossing_tolerance_ms: 0.05  # Noise window

phase_detection_mode: continuous_gait  # Different from jump
gct_algorithm: foot_velocity_crossing  # Detects foot acceleration/deceleration
cadence_detection: contact_event_counting  # Count foot strikes

estimated_latency_ms: 35-45
estimated_accuracy: 85-90%
gct_precision_ms: ±20-30
cadence_precision_spm: ±4-5
use_case: Real-time coaching feedback
```

### Running Balanced Preset (Recommended default)

```yaml
model_complexity: 1  # Full model
detection_confidence: 0.70  # Balanced between noise/accuracy
tracking_confidence: 0.65
butterworth_order: 2
butterworth_cutoff_hz_lower_body: 5.0
butterworth_cutoff_hz_upper_body: 12.0
savgol_window_length: 9  # Shorter window (less lag)
savgol_polyorder: 2
velocity_threshold_ms: 0.05
foot_contact_threshold: 0.15
zero_crossing_tolerance_ms: 0.03

phase_detection_mode: continuous_gait
gct_algorithm: foot_velocity_crossing
cadence_detection: contact_event_counting

estimated_latency_ms: 55-70
estimated_accuracy: 92-95%
gct_precision_ms: ±10-15
cadence_precision_spm: ±2-3
use_case: Standard running analysis (coaching, research)
```

### Running Accurate Preset (Research-grade)

```yaml
model_complexity: 1  # Full model
detection_confidence: 0.75  # High precision, fewer false positives
tracking_confidence: 0.70
butterworth_order: 3  # Steeper rolloff
butterworth_cutoff_hz_lower_body: 6.0
butterworth_cutoff_hz_upper_body: 15.0
savgol_window_length: 7  # Minimal smoothing (preserve signal)
savgol_polyorder: 3  # Higher order polynomial
velocity_threshold_ms: 0.01  # Very strict
foot_contact_threshold: 0.10
zero_crossing_tolerance_ms: 0.01

phase_detection_mode: continuous_gait
gct_algorithm: foot_velocity_crossing_with_acceleration_confirmation
cadence_detection: contact_event_counting_with_validation

estimated_latency_ms: 80-100
estimated_accuracy: 96-98%
gct_precision_ms: ±5-10
cadence_precision_spm: ±1-2
use_case: Research, clinical analysis, publication-quality metrics
```

______________________________________________________________________

## Part 3: Running-Specific Metrics Parameters

### Ground Contact Time (GCT) Detection

```yaml
# GCT definition: Time from foot strike to toe-off (entire stance phase)

# Algorithm: Detect foot vertical velocity zero-crossings

phase_one_strike_detection:
  - Method: Detect upward-to-downward velocity crossing (foot landing)
  - Signal: Ankle vertical velocity
  - Threshold: foot_contact_threshold (varies by preset)
  - Confirmation: Knee flexion increase + hip position drop
  - Latency_to_full_detection: 1-2 frames after contact

phase_toe_off_detection:
  - Method: Detect downward-to-upward velocity crossing (foot leaving ground)
  - Signal: Ankle vertical velocity
  - Threshold: foot_contact_threshold
  - Confirmation: Ankle plantarflexion, hip extension
  - Latency_to_full_detection: 1 frame before liftoff (predictive)

gct_calculation: frame_count_between_strike_and_toe_off / fps

accuracy_validation:
  - Compare to force plate: Target MAE <15ms
  - Compare to high-speed video (120fps manual): Target MAE <20ms
  - Acceptable precision at 30fps: ±1-2 frames (33-66ms)
```

### Cadence Detection

```yaml
# Cadence: Steps per minute (spm)

# Algorithm 1: Contact event counting
stride_cycle:
  - Left contact at frame 0
  - Right contact at frame ~30 (180 spm at 30fps = 0.33s stride)
  - Left contact again at frame ~60
  - Full stride cycle = ~60 frames (2 seconds at 30fps)

cadence_calculation:
  - Count foot contacts over 60-second window
  - Formula: (contact_count / 2) * 60 = spm
  - Running at 180 spm: ~180 foot contacts per 60 seconds

# Algorithm 2: Stride length-based (derivative)
cadence_from_stride_frequency:
  - Detect contact peaks in hip vertical position
  - Calculate interval between peaks
  - cadence = (1 / stride_period) * 60

accuracy_validation:
  - Compare to manual frame counting: Target accuracy >95%
  - Compare to force plate: Target MAE <3 spm
  - Acceptable precision: ±2-3 spm at balanced preset
```

### Landing Pattern Classification

```yaml
# Landing pattern: Heel-strike vs midfoot vs forefoot

# Detection: Foot strike position relative to body center

heel_strike_definition:
  - Initial contact with heel (back of foot)
  - Ankle angle: plantarflexed (toe up)
  - Example athlete: 60-80% of recreational runners
  - Cadence: Typically 160-170 spm

midfoot_strike_definition:
  - Initial contact with middle of foot
  - Ankle angle: neutral (~90°)
  - Example athlete: Elite distance runners, some beginners
  - Cadence: Typically 175-185 spm

forefoot_strike_definition:
  - Initial contact with ball of foot (toes)
  - Ankle angle: dorsiflexed (toe down)
  - Example athlete: Sprinters, track athletes
  - Cadence: Typically 180-200+ spm

classification_algorithm:
  - Extract foot_index and heel landmarks at first contact
  - Calculate vertical position at contact: foot_index.y vs heel.y
  - If foot_index.y < heel.y at contact: Forefoot-strike
  - If foot_index.y ≈ heel.y at contact: Midfoot-strike
  - If foot_index.y > heel.y at contact: Heel-strike

accuracy_validation:
  - Manual reviewer classification: Target >85% agreement
  - Cohen's kappa: Target >0.80 (excellent inter-rater)
  - Confusion matrix reporting: Per-class sensitivity >80%
```

### Stride Length Calculation

```yaml
# Stride length: Distance from one foot strike to next same-foot strike

stride_length_calculation:
  # Method 1: Hip horizontal displacement (most reliable)
  - hip_displacement_meters = hip.x[toe_off] - hip.x[contact]
  # (multiplied by calibration factor from video perspective)

  # Method 2: GCT × velocity (indirect)
  - horizontal_velocity = hip.x[next_strike] - hip.x[last_strike] / stride_duration
  - stride_length = horizontal_velocity × stride_duration

stride_length_reference_values:
  male_elite: 1.8-2.0m
  male_recreational: 1.5-1.8m
  female_elite: 1.6-1.9m
  female_recreational: 1.3-1.6m

accuracy_validation:
  - Compare to ground truth distance: Target ±5% error
  - Method 1 (hip displacement) preferred over Method 2
  - Requires camera calibration (known reference distance in frame)
```

______________________________________________________________________

## Part 4: Real-Time Optimization Parameters

### Latency Profiling Targets (Week 1, Task 3)

```yaml
profiling_matrix:
  model_complexity: [0, 1]  # Lite, Full
  video_resolution: [480, 720, 1080]  # pixels
  quality_preset: [Fast, Balanced, Accurate]
  network_condition: [LAN, WiFi, 4G]  # Simulated latency
  body_count: [1, 2, 3]  # Single vs multi-person

total_test_scenarios: 3 × 3 × 3 × 3 × 3 = 405 conditions

priority_scenarios:
  - Single person, Balanced preset, 720p, WiFi → Target <200ms
  - Single person, Lite model, 720p, LAN → Target <150ms
  - Multi-person (2), Lite model, 720p, WiFi → Target <150ms (acceptable for batch)
```

### Progressive Enhancement Strategy

```yaml
# Phase 1 (MVP): Metrics + video only
feature_set_1:
  - Live video stream (minimal overlay)
  - Metrics update (1/sec)
  - Latency target: <250ms acceptable

# Phase 2 (Enhanced): Add pose visualization
feature_set_2:
  - Live video with pose skeleton
  - Metrics update (2-3/sec)
  - Latency target: <150ms required

# Phase 3 (Advanced): Real-time feedback
feature_set_3:
  - Multi-person tracking
  - Per-person metrics
  - Coaching alerts
  - Latency target: <100ms required
```

______________________________________________________________________

## Part 5: Multi-Person Detection Parameters (Design Phase)

### Status: ARCHITECTURAL DESIGN ONLY (implementation Month 4)

```yaml
multi_person_confidence_adjustments:
  single_person:
    detection_confidence: 0.50
    tracking_confidence: 0.50
    max_people: 1

  two_people:
    detection_confidence: 0.65  # Higher to maintain separate IDs
    tracking_confidence: 0.60
    max_people: 2
    occlusion_tolerance_frames: 3  # Interpolate if occluded <3 frames

  three_to_five_people:
    detection_confidence: 0.70  # Even higher
    tracking_confidence: 0.65
    max_people: 5
    occlusion_tolerance_frames: 2  # Stricter (more crowding)

  six_plus_people:
    status: not_recommended  # Accuracy unreliable at crowd scale

multi_person_latency_scaling:
  single_person: 50ms  # Baseline
  two_people: ~100ms  # +50ms per person (linear scaling)
  three_people: ~150ms
  five_people: ~250ms  # Unacceptable for real-time

mitigation_strategies:
  - Use Lite model for multi-person (brings 2-person to 70ms)
  - Accept batch processing mode (10fps acceptable for team analysis)
  - Process subset of joints (lower body only) to reduce load
```

______________________________________________________________________

## Part 6: Parameter Validation Requirements

### Validation Study Specifications

```yaml
# All parameters above require validation studies

jump_metrics_validation:
  ground_truth: Force plate (ideal) OR high-speed 120fps video
  sample_size: 30-45 trials minimum
  athletes: 10-15, diverse (gender, body type, fitness)
  success_criteria:
    gct_mae: <20ms
    cmj_height_mae: <3cm
    icc_threshold: >0.90

running_metrics_validation:
  ground_truth: Force plate OR high-speed 120fps with manual annotation
  sample_size: 75-200+ stride cycles minimum
  athletes: 15-20, diverse speeds (easy jog to hard run)
  success_criteria:
    gct_mae: <15ms
    cadence_mae: <3spm
    landing_pattern_accuracy: >85%
    icc_threshold: >0.90

reporting_requirements:
  - Bland-Altman plots (difference vs average)
  - 95% confidence intervals
  - Effect sizes (Cohen's d)
  - Correlation coefficients
  - Per-preset accuracy breakdown
  - Per-population accuracy breakdown
```

______________________________________________________________________

## Part 7: Implementation Checklist

### Pre-Implementation Validation

- [ ] Running presets defined and documented (this file)
- [ ] Parameter sweep designed for running (Week 4)
- [ ] Latency profiler tool created and run (Week 1)
- [ ] Benchmark dataset specification complete (Week 2)

### Implementation Phase

- [ ] Drop Jump validation study in progress (Week 1-2)
- [ ] Running parameter optimization (Week 4)
- [ ] Running validation study (Week 4-5)
- [ ] Real-time latency optimization (Week 3-5)

### Pre-Launch Validation

- [ ] All jump metrics published accuracy data
- [ ] All running metrics published accuracy data
- [ ] Robustness testing matrix complete
- [ ] Ablation studies quantifying parameter impacts
- [ ] Benchmark datasets published

______________________________________________________________________

## Part 8: Reference: Parameter Sensitivity Analysis

### How Each Parameter Affects Output

```yaml
detection_confidence:
  effect: Controls probability threshold for detecting pose
  increase: More confident detections, fewer false positives, more missed frames
  decrease: More detections, more noise, more false positives
  typical_range: 0.3-0.8
  running_vs_jump: Running needs higher (0.65-0.75 vs 0.5-0.7)

butterworth_cutoff:
  effect: Filter frequency for smoothing high-frequency noise
  increase: Less smoothing, preserves faster movements, noisier
  decrease: More smoothing, loses detail, introduces lag
  typical_range: 4-12 Hz
  running_vs_jump: Running needs lower lower-body (5Hz vs 8Hz)

savgol_window:
  effect: Sliding window size for polynomial smoothing
  increase: More smoothing, more lag, faster processing
  decrease: Less smoothing, less lag, slower processing
  typical_range: 5-15 frames (odd numbers only)
  running_vs_jump: Running needs smaller (9 vs 11 frames at 30fps)

velocity_threshold:
  effect: Sensitivity for detecting phase transitions (zero-crossings)
  increase: Less sensitive, misses events, fewer false positives
  decrease: More sensitive, detects more, more false positives
  typical_range: 0.01-0.2 m/s
  running_vs_jump: Running needs lower (0.05 vs 0.1)
```

______________________________________________________________________

## Summary: Key Differences Running vs Jump

| Parameter            | Jump Balanced | Running Balanced | Why Different                               |
| -------------------- | ------------- | ---------------- | ------------------------------------------- |
| Detection confidence | 0.5           | 0.70             | Foot visibility critical during swing phase |
| Tracking confidence  | 0.5           | 0.65             | Harder to maintain ID during occlusion      |
| Model                | Full (1)      | Lite (0)         | Real-time priority for running              |
| Lower body cutoff    | 8 Hz          | 5 Hz             | Slower hip/ankle motion in running          |
| Savgol window        | 11 frames     | 9 frames         | Shorter stride cycles at running cadence    |
| Velocity threshold   | 0.10 m/s      | 0.05 m/s         | Running continuous velocity, not discrete   |

**Bottom line:** Running requires different parameters. One-size-fits-all approach will fail.

______________________________________________________________________

**Document Version:** 1.0
**Status:** Ready for Implementation
**Last Updated:** November 17, 2025
**Next Review:** After Week 1 latency profiling results
