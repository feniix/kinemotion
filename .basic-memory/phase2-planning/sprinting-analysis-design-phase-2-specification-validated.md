---
title: Sprinting Analysis Design - Phase 2 Specification (Validated)
type: note
permalink: phase2-planning/sprinting-analysis-design-phase-2-specification-validated
tags:
- sprinting
- phase2
- biomechanics
- validated
- design-specification
---

# Sprinting Analysis Design - Phase 2 Specification

**Status:** Multi-source validated (Jan 2025)
**Phase:** Phase 2 (Post-MVP, pending market validation)
**Last Updated:** 2025-01-17

---

## Executive Summary

Comprehensive sprinting analysis design validated through:
- Biomechanics specialist (literature review)
- Computer vision engineer (MediaPipe feasibility)
- QA test engineer (validation strategy)
- 2024-2025 research papers (Exa, Ref search)
- Sequential reasoning analysis

**Result:** Design is TECHNICALLY VALIDATED with 6 corrections applied.

---

## Corrected Validation Bounds

All bounds validated against 2024-2025 research literature.

### Ground Contact Time (GCT)

| Tier | Range (ms) | Confidence | Source |
|------|------------|------------|--------|
| **Elite** | 85-120 | HIGH | Blauberger 2021: 104.8±6.71ms; Weyand 2010: 108ms minimum |
| **College/Trained** | 100-140 | HIGH | NCAA Division I intermediate |
| **High School** | 120-160 | MEDIUM | Developmental progression |
| **Recreational** | 160-240 | HIGH | Jogging pace ~200ms+ |

**Key Corrections:**
- Elite minimum: 85ms (not 80ms) - 80ms below physiological minimum
- Recreational: 160-240ms (not 130-200ms) - 200ms is average jogging pace

### Stride Frequency

| Tier | Range (Hz) | Confidence | Source |
|------|------------|------------|--------|
| **Elite** | 4.2-4.6 | HIGH | Bolt world records: 4.24-4.29 Hz |
| **College/Trained** | 4.0-4.4 | HIGH | NCAA Division I |
| **High School** | 3.8-4.2 | MEDIUM | Developing athletes |
| **Recreational** | 3.0-3.8 | HIGH | Distance running range |

**Key Correction:**
- Elite maximum: 4.6 Hz (not 5.2 Hz) - Physiological limit based on Usain Bolt analysis (4.24-4.29 Hz). Elite athletes achieve speed through stride LENGTH, not frequency.

### Flight Time and Ratio

| Tier | Flight Time (ms) | Flight Ratio | Confidence |
|------|-----------------|--------------|------------|
| **Elite** | 120-160 | 0.50-0.60 | HIGH (calculated) |
| **Recreational** | 60-100 | 0.30-0.40 | HIGH (calculated) |

---

## Technical Specifications

### Frame Rate Requirements

| FPS | Frames per GCT (85ms) | Viability | User Availability |
|-----|----------------------|-----------|-------------------|
| 240fps | 18.4 frames | ✅ Optimal | ~5-10% (latest Pro) |
| 120fps | 9.2 frames | ✅ Viable | ~15-25% (flagship) |
| 60fps | 4.6 frames | ⚠️ Marginal | ~70-80% (mid-range+) |
| 30fps | 2.3 frames | ❌ Not usable | ~100% (default) |

**Frame Rate Policy:**
```python
def validate_sprinting_fps(fps: float, target_level: str = "college") -> tuple[bool, str]:
    if fps >= 120:
        return True, "Ideal frame rate for sprinting analysis"
    elif fps >= 60:
        if target_level == "elite":
            return True, "WARNING: 60fps marginal for elite (4-6 frames per contact phase)"
        return True, "60fps acceptable for recreational/trained athletes"
    else:
        return False, "ERROR: Frame rate below 60fps not supported for sprinting"
```

### Adaptive Smoothing

Fixed smoothing windows over-smooth short GCT phases. Use adaptive approach:

```python
def get_smoothing_window(fps: float) -> int:
    """Return adaptive smoothing window based on frame rate."""
    if fps >= 240:
        return 7  # 29ms smoothing - 24-34% of elite GCT
    elif fps >= 120:
        return 5  # 42ms smoothing - 35-49% of elite GCT
    elif fps >= 60:
        return 3  # 50ms smoothing - 42-59% of elite GCT
    else:
        raise ValueError("Frame rate below 60fps not supported")
```

### Camera Setup

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Angle** | 90° lateral (side view) | Validated for max velocity phase |
| **Alternative** | 45-60° posterior-anterior oblique | If occlusion issues at 90° |
| **Distance** | 5-10m perpendicular | Minimize parallax |
| **Height** | 1-1.5m from ground | Hip/knee level |
| **Zone** | 40-50m mark (100m sprint) | Max velocity phase |

**Critical:** At max velocity (40-60m), sprinters are nearly UPRIGHT (0-5° forward lean). The 45° lean is only during acceleration phase (0-30m).

---

## Module Structure

```
src/kinemotion/sprinting/
├── __init__.py              # Public exports
├── cli.py                   # kinemotion sprint-analyze
├── api.py                   # process_sprinting_video()
├── analysis.py              # Stride detection (merged gait_cycles)
├── kinematics.py            # Metrics calculation
├── metrics_validator.py     # SprintingMetricsValidator
├── validation_bounds.py     # SprintingBounds (with College tier)
└── debug_overlay.py         # Visualization

tests/sprinting/
├── test_analysis.py         # Stride detection tests
├── test_kinematics.py       # Metrics calculation tests
├── test_validation_bounds.py # Bounds validation tests
├── test_api.py              # API tests
└── test_cli.py              # CLI tests
```

---

## Data Structures

```python
@dataclass
class SprintStrideMetrics:
    """Metrics for a SINGLE stride."""
    stride_index: int
    ground_contact_time_ms: float
    flight_time_ms: float
    stride_frequency_hz: float
    flight_ratio: float
    step_length_m: float | None = None  # Requires calibration

@dataclass
class SprintingMetrics:
    """Aggregated metrics across 5-15 strides."""
    mean_ground_contact_time_ms: float
    std_ground_contact_time_ms: float
    mean_flight_time_ms: float
    std_flight_time_ms: float
    mean_stride_frequency_hz: float
    std_stride_frequency_hz: float
    mean_flight_ratio: float
    std_flight_ratio: float
    # Spatial metrics (require calibration)
    mean_velocity_m_s: float | None = None
    mean_stride_length_m: float | None = None
    mean_step_length_m: float | None = None
    # Metadata
    num_strides_analyzed: int = 0
    stride_metrics: list[SprintStrideMetrics] | None = None
```

---

## Validation Bounds Code

```python
# src/kinemotion/sprinting/validation_bounds.py

class SprintingBounds:
    """Physiological bounds for sprinting metrics (max velocity phase)."""

    # Ground Contact Time (milliseconds)
    ELITE_GCT = MetricBounds(absolute_min=60, practical_min=85, elite_min=85, elite_max=120,
                            recreational_min=160, recreational_max=240, absolute_max=300, unit="ms")
    COLLEGE_GCT = MetricBounds(absolute_min=60, practical_min=100, elite_min=100, elite_max=140,
                             recreational_min=130, recreational_max=170, absolute_max=250, unit="ms")
    HIGH_SCHOOL_GCT = MetricBounds(absolute_min=60, practical_min=120, elite_min=120, elite_max=160,
                                  recreational_min=140, recreational_max=200, absolute_max=250, unit="ms")
    RECREATIONAL_GCT = MetricBounds(absolute_min=100, practical_min=160, elite_min=160, elite_max=200,
                                    recreational_min=180, recreational_max=280, absolute_max=350, unit="ms")

    # Stride Frequency (Hz - strides per second)
    ELITE_FREQUENCY = MetricBounds(absolute_min=3.5, practical_min=4.0, elite_min=4.2, elite_max=4.6,
                                  recreational_min=3.8, recreational_max=4.5, absolute_max=5.5, unit="Hz")
    COLLEGE_FREQUENCY = MetricBounds(absolute_min=3.0, practical_min=3.5, elite_min=4.0, elite_max=4.4,
                                   recreational_min=3.5, recreational_max=4.2, absolute_max=5.0, unit="Hz")
    HIGH_SCHOOL_FREQUENCY = MetricBounds(absolute_min=2.5, practical_min=3.0, elite_min=3.8, elite_max=4.2,
                                      recreational_min=3.2, recreational_max=4.0, absolute_max=4.5, unit="Hz")
    RECREATIONAL_FREQUENCY = MetricBounds(absolute_min=2.0, practical_min=2.5, elite_min=3.0, elite_max=3.8,
                                        recreational_min=2.8, recreational_max=3.8, absolute_max=4.5, unit="Hz")

    # Flight Time (milliseconds)
    ELITE_FLIGHT = MetricBounds(absolute_min=80, practical_min=100, elite_min=120, elite_max=160,
                               recreational_min=100, recreational_max=140, absolute_max=200, unit="ms")
    RECREATIONAL_FLIGHT = MetricBounds(absolute_min=40, practical_min=60, elite_min=80, elite_max=120,
                                       recreational_min=90, recreational_max=150, absolute_max=180, unit="ms")

    # Flight Ratio (dimensionless: flight / total_time)
    ELITE_FLIGHT_RATIO = MetricBounds(absolute_min=0.35, practical_min=0.45, elite_min=0.50, elite_max=0.60,
                                      recreational_min=0.45, recreational_max=0.55, absolute_max=0.70, unit="ratio")
    RECREATIONAL_FLIGHT_RATIO = MetricBounds(absolute_min=0.20, practical_min=0.25, elite_min=0.30, elite_max=0.40,
                                            recreational_min=0.35, recreational_max=0.45, absolute_max=0.55, unit="ratio")
```

---

## Algorithm Design

### Stride Detection (Cyclical Pattern)

```python
def detect_stride_contacts(
    foot_positions: FloatArray,
    fps: float,
    smoothing_window: int | None = None,
) -> list[int]:
    """
    Detect foot strikes from ankle height oscillation.

    Key insight: Foot strikes occur at local MAXIMA in normalized y-coordinate
    (y increases downward, so lowest physical position = highest y value).

    Args:
        foot_positions: Ankle vertical positions (normalized 0-1)
        fps: Video frame rate (60fps minimum)
        smoothing_window: Adaptive if None, or use provided value

    Returns:
        List of contact frame indices
    """
    # Apply adaptive smoothing
    if smoothing_window is None:
        smoothing_window = get_smoothing_window(fps)

    # Heavy smoothing for cyclical motion
    smoothed = savgol_filter(foot_positions, smoothing_window, polyorder=2)

    # Find peaks (local maxima = foot closest to ground)
    peaks, properties = find_peaks(
        smoothed,
        distance=int(fps * 0.25),  # Minimum 0.25s between strides
        prominence=0.02,
        width=int(fps * 0.05),
    )

    return peaks.tolist()
```

### Contact/Flight Phase Detection

```python
def detect_contact_flight_phases(
    ankle_y: FloatArray,
    foot_strikes: list[int],
    fps: float,
) -> list[ContactFlightPhase]:
    """
    Detect ground contact and flight phases within each stride.

    Contact phase: Foot strike to takeoff (ankle at max height)
    Flight phase: Takeoff to next foot strike

    Args:
        ankle_y: Ankle vertical positions
        foot_strikes: Contact frame indices
        fps: Frame rate

    Returns:
        List of contact/flight phases
    """
    phases = []

    for i, strike_frame in enumerate(foot_strikes[:-1]):
        next_strike = foot_strikes[i + 1]

        # Find takeoff (local minimum y = max height) between strikes
        stride_segment = ankle_y[strike_frame:next_strike]
        takeoff_relative = int(np.argmin(stride_segment))
        takeoff_frame = strike_frame + takeoff_relative

        # Calculate times
        contact_ms = ((takeoff_frame - strike_frame) / fps) * 1000
        flight_ms = ((next_strike - takeoff_frame) / fps) * 1000
        flight_ratio = flight_ms / (contact_ms + flight_ms)

        phases.append(ContactFlightPhase(
            contact_start_frame=strike_frame,
            contact_end_frame=takeoff_frame,
            flight_end_frame=next_strike,
            contact_time_ms=contact_ms,
            flight_time_ms=flight_ms,
            flight_ratio=flight_ratio,
        ))

    return phases
```

---

## CLI Interface

```bash
# Basic analysis (temporal metrics only)
kinemotion sprint-analyze sprint.mp4

# With calibration for velocity/stride length
kinemotion sprint-analyze sprint.mp4 --calibration 245

# Analyze specific time window (40-50m mark)
kinemotion sprint-analyze sprint.mp4 --start-time 3.5 --duration 2.0

# Specify athlete level for appropriate bounds
kinemotion sprint-analyze sprint.mp4 --athlete-level college

# Batch processing
kinemotion sprint-analyze sprints/*.mp4 --batch --workers 3
```

---

## Implementation Triggers (Phase 2)

Implement sprinting analysis when ALL of the following are met:

1. ✅ **Market Validation:** 5+ coaches request sprinting analysis
2. ✅ **RTMPose Integration:** RTMPose integrated and tested
3. ✅ **Hardware Confirmed:** User base has 120fps+ capability
4. ✅ **Web UI Complete:** Issue #12 delivered and deployed

---

## Key Research References

1. **Blauberger et al. 2021** - "Detection of Ground Contact Times with Inertial Sensors in Elite 100-m Sprints" (Sensors 21:7331)
   - Elite GCT: 104.8 ± 6.71ms (steps 46-50 at max velocity)
   - Steps 16-45: 107-109ms

2. **Weyand et al. 2010** - "The biological limits to running speed are imposed from the ground up" (J Appl Physiol 108:950-961)
   - Physiological minimum: 108ms for forward running

3. **Maćkała & Mero 2013** - "A Kinematics Analysis Of Three Best 100 M Performances Ever" (J Hum Kinet 36:149-160)
   - Usain Bolt stride frequency: 4.24 ± 0.03 Hz
   - Beijing: 4.24 Hz, Berlin: 4.23 Hz, London: 4.29 Hz

4. **Balsalobre-Fernandez et al. 2016** - "Validation of iPhone app for running mechanics"
   - Manual frame counting validation: r=0.94-0.99

5. **VideoRun2D 2024** - Cost-effective markerless motion capture for sprint biomechanics
   - Validated 90° lateral camera angle for sprinting

---

## Risk Mitigation Strategies

| Risk | Mitigation |
|------|------------|
| 60fps marginal for elite | Strong 120fps recommendation, frame rate warnings |
| MediaPipe motion blur | Confidence filtering, heavy smoothing, RTMPose path |
| Occlusion at 90° lateral | Document 45-60° oblique alternative |
| Over-smoothing GCT | Adaptive window size (3-7 frames based on fps) |
| User hardware limitations | Clear documentation, tier support (elite requires 120fps) |

---

## Next Steps When Implementing

1. Review this design against any new research (post-2025)
2. Create test video dataset with manual frame counting validation
3. Implement with MediaPipe first (MVP)
4. Validate against RTMPose comparison
5. Consider RTMPose migration if MediaPipe insufficient
6. Update bounds based on validation data

---

**Document Owner:** kinemotion project
**Review Date:** 2025-01-17
**Next Review:** When triggering Phase 2 implementation
