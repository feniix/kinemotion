---
title: Sprinting Analysis Biomechanics Research
type: note
permalink: research/sprinting-analysis-biomechanics-research
---

# Sprinting Analysis Biomechanics Research

## Executive Summary

Sprinting requires **different algorithms and metrics** than jump analysis due to cyclical nature, horizontal velocity dominance, and very short ground contact times (80-120ms at max velocity).

**Key Finding:** Max velocity phase (30-60m+) should be MVP focus - mechanics are more consistent, metrics more stable, and it's where performance differences are most pronounced.

---

## 1. Sprinting Phases

### Acceleration Phase (0-30m)

**Characteristics:**
- Forward body lean (45-60° from horizontal)
- Longer ground contact times (180-250ms)
- Emphasis on horizontal force production
- Step length increases, step frequency increases
- Center of mass starts low, rises gradually

**Key Metrics:**
- Ground contact time: 180-250ms (decreases throughout phase)
- Flight time: 80-120ms
- Step frequency: 3.5-4.5 Hz (increasing)
- Step length: 1.2-1.8m (increasing)
- Horizontal velocity: 0-8 m/s (rapid acceleration)

**Technical Challenges:**
- Forward lean makes hip tracking difficult (MediaPipe)
- Camera angle changes (frontal → sagittal plane)
- Different mechanics throughout phase (non-steady state)
- Requires longer video capture (0-30m distance)

### Max Velocity Phase (30-60m+)

**Characteristics:**
- Upright body position (0-5° forward lean)
- Shortest ground contact times (80-120ms)
- Flight time longer than contact time
- Consistent, cyclical mechanics
- Center of mass at near-constant height

**Key Metrics:**
- Ground contact time: 80-120ms (elite), 120-160ms (trained), 150-200ms (recreational)
- Flight time: 120-160ms (elite), 100-140ms (trained)
- Step frequency: 4.5-5.0 Hz (elite), 4.0-4.5 Hz (trained), 3.5-4.0 Hz (recreational)
- Step length: 2.2-2.7m (elite), 1.8-2.2m (trained), 1.5-1.8m (recreational)
- Velocity: 11.5-12.5 m/s (elite), 9-11 m/s (trained), 7-9 m/s (recreational)

**Technical Advantages:**
- Consistent mechanics (steady state)
- Easier to detect cycles (regular stride pattern)
- Upright body → better MediaPipe tracking
- Camera position stable (side view)

**MVP Recommendation:** Focus on max velocity phase - easier to implement, more stable metrics, clearer coaching applications.

---

## 2. Essential Metrics for 2D Video Analysis

### 2.1 Ground Contact Time (GCT)

**Definition:** Time from foot strike to toe-off (stance phase)

**Measurement:**
- Detect foot strike: Foot velocity becomes zero relative to ground
- Detect toe-off: Foot leaves ground, flight phase begins
- Use vertical foot displacement or ankle height

**Normative Values:**

| Level        | Max Velocity (ms) | Acceleration (ms) |
| ------------ | ----------------- | ----------------- |
| Elite        | 80-120            | 150-180           |
| College      | 100-140           | 170-210           |
| High School  | 120-160           | 190-230           |
| Recreational | 150-200           | 210-260           |

**Validation Bounds:**
- Absolute min: 60ms (physiological limit at max velocity)
- Absolute max: 350ms (beyond this, not sprinting)
- Elite flag: <90ms at max velocity (exceptional, verify)
- Error flag: >250ms at max velocity (likely jogging, not sprinting)

**Technical Notes:**
- **Very short!** At 30fps, only 2-4 frames in contact phase
- **High frame rate essential:** 60fps minimum, 120fps recommended
- MediaPipe struggles: Motion blur during foot strike/loss of tracking

### 2.2 Flight Time

**Definition:** Time from toe-off to next foot strike (aerial phase)

**Measurement:**
- Detect when foot leaves ground (ankle height increases rapidly)
- Detect when same foot contacts ground again
- Can measure from hip displacement pattern (oscillates)

**Normative Values:**

| Level        | Max Velocity (ms) |
| ------------ | ----------------- |
| Elite        | 120-160           |
| College      | 110-140           |
| High School  | 100-130           |
| Recreational | 90-120            |

**Formula:**
- Flight Ratio = Flight Time / (Contact Time + Flight Time)
- Elite: ~0.55-0.60 (spends more time in flight than contact)
- Recreational: ~0.40-0.50

**Technical Notes:**
- At max velocity, flight time > contact time (unlike acceleration)
- Hip position oscillates consistently (easier to detect than foot)
- Use hip displacement + foot strike detection together

### 2.3 Stride Length

**Definition:** Distance covered in one complete stride cycle (left foot strike to next left foot strike)

**Measurement:**
- Count frames between consecutive foot strikes of same foot
- Multiply by velocity (or use known distance calibration)
- Alternative: Measure from hip displacement if camera calibrated

**Normative Values:**

| Level        | Max Velocity (m) | Acceleration (m) |
| ------------ | ---------------- | ---------------- |
| Elite        | 2.2-2.7          | 1.6-2.0          |
| College      | 1.9-2.3          | 1.4-1.8          |
| High School  | 1.6-2.1          | 1.2-1.6          |
| Recreational | 1.4-1.8          | 1.0-1.4          |

**Formula:**
- Velocity = Stride Length × Stride Frequency
- Stride Length = Velocity / Stride Frequency

**Technical Notes:**
- Requires velocity measurement (pixels → meters conversion)
- Camera calibration needed (known distance in frame)
- Or use timing gates / known distance (e.g., 10m zone at 50m mark)

### 2.4 Stride Frequency

**Definition:** Number of strides per second (Hz)

**Measurement:**
- Count consecutive strides (left foot strike to next left foot strike)
- Calculate time for N strides: Frequency = N / Total Time
- Or: Frequency = 1 / Stride Duration

**Normative Values:**

| Level        | Max Velocity (Hz) | Acceleration (Hz) |
| ------------ | ----------------- | ----------------- |
| Elite        | 4.5-5.0           | 3.5-4.2           |
| College      | 4.2-4.7           | 3.2-3.9           |
| High School  | 3.8-4.4           | 2.9-3.6           |
| Recreational | 3.5-4.0           | 2.6-3.3           |

**Technical Notes:**
- Easiest metric to measure reliably (just count foot strikes)
- Detect foot strikes using ankle or hip velocity pattern
- Regular oscillation makes detection robust

### 2.5 Velocity

**Definition:** Horizontal speed of athlete's center of mass

**Measurement:**
- Displacement of hip or center of mass over time
- Requires calibration (known distance in frame)
- Or use timing gate data (if available)

**Normative Values:**

| Level        | Max Velocity (m/s) | Acceleration (m/s) |
| ------------ | ------------------ | ------------------ |
| Elite (Bolt) | 12.4               | 0-12.4             |
| Elite        | 11.5-12.0          | 0-11.5             |
| College      | 9.5-10.5           | 0-9.5              |
| High School  | 8.0-9.5            | 0-8.0              |
| Recreational | 6.5-8.0            | 0-6.5              |

**Technical Notes:**
- Camera calibration critical
- Side view essential (no perspective distortion)
- Parallax errors if athlete not in center of frame

### 2.6 Flight Ratio

**Definition:** Proportion of stride spent in flight vs contact

**Formula:**
```
Flight Ratio = Flight Time / (Contact Time + Flight Time)
```

**Normative Values:**

| Level        | Max Velocity |
| ------------ | ------------ |
| Elite        | 0.55-0.60    |
| College      | 0.50-0.55    |
| High School  | 0.45-0.50    |
| Recreational | 0.40-0.45    |

**Interpretation:**
- Higher ratio = more efficient elastic energy utilization
- Elite sprinters spend >55% of stride in flight phase
- Recreational runners spend more time on ground (less efficient)

---

## 3. Camera Setup for Sprinting

### 3.1 Optimal Camera Position

**Max Velocity Phase (MVP Focus):**

| Factor           | Recommendation           | Rationale                                    |
| ---------------- | ------------------------ | -------------------------------------------- |
| **View Angle**   | 90° lateral (side view)  | Clear sagittal plane mechanics                |
| **Distance**     | 5-10m perpendicular      | Minimize parallax, capture full stride       |
| **Height**       | 1-1.5m from ground       | Hip/knee level, not too high/low             |
| **Zone**         | 40-50m mark (100m sprint)| Max velocity phase, stable mechanics         |
| **Frame Rate**   | 60fps minimum, 120fps ideal | Capture short contact phase (80-120ms)     |

**Why 90° Lateral:**
- Full visibility of swing leg and stance leg
- Clear hip, knee, ankle angles
- Minimal occlusion
- Consistent with existing CMJ/Drop Jump validation (45° oblique for jumps, 90° for sprinting)

**Why Max Velocity Zone (40-50m):**
- Athlete at top speed (stable mechanics)
- Upright body position (easiest for MediaPipe tracking)
- Consistent stride-to-stride mechanics
- Performance differences most pronounced here

### 3.2 Acceleration Phase Setup (Future)

| Factor          | Recommendation            |
| --------------- | ------------------------- |
| **View Angle**  | 45° oblique or frontal (0-10m), transition to lateral (10-30m) |
| **Camera Setup**| Multiple cameras or panning |
| **Distance**    | 0-30m zone                |
| **Challenge**   | Changing body angle, camera parallax |

**Technical Challenge:** Athlete's body angle changes from 45° forward lean (start) to upright (max velocity). Single camera angle cannot optimally capture entire acceleration phase.

### 3.3 Calibration Requirements

**Essential:**
- Known distance in frame (e.g., track markings 1m apart)
- Or reference object of known height
- Camera height and distance from athlete

**Why:**
- Convert pixel displacement to meters (stride length, velocity)
- Without calibration, only relative metrics possible (stride frequency, contact/flight times)

**Calibration Method:**
1. Place markers 1m apart on track (use lane lines)
2. Capture video with markers visible
3. Calculate pixels-per-meter ratio
4. Apply to all displacement measurements

---

## 4. Algorithm Differences: Sprinting vs Jumping

### 4.1 Cyclical vs Discrete

| Aspect           | Sprinting                            | Jumping (CMJ/DJ/SJ)                |
| ---------------- | ------------------------------------ | ---------------------------------- |
| **Nature**       | Cyclical (repeating stride pattern)  | Discrete (single event)            |
| **Detection**    | Find stride cycles, count repeats    | Find start/end of single phase     |
| **Metrics**      | Averages across N strides            | Single values for entire movement  |
| **Algorithm**    | Peak detection, periodicity analysis | Forward/backward search            |

### 4.2 Velocity Calculation

| Aspect           | Sprinting                            | Jumping                    |
| ---------------- | ------------------------------------ | -------------------------- |
| **Primary Axis** | Horizontal (forward motion)          | Vertical (jump height)     |
| **Velocity Type**| Horizontal velocity dominates        | Vertical velocity (signed) |
| **Detection**    | Hip displacement over time           | Vertical hip velocity      |
| **Smoothing**    | Critical (high-frequency oscillation)| Moderate (single movement) |

### 4.3 Phase Detection

**Sprinting:**

```
Algorithm (Cyclical Detection):
1. Detect foot strikes (local minima in ankle height)
2. Group into stride cycles (left-left or right-right)
3. Calculate stride metrics (duration, length, frequency)
4. Average across N strides for stability
```

**Jumping:**

```
Algorithm (Single Event):
Drop Jump: Forward search for landing → takeoff
CMJ: Backward search from peak → takeoff → bottom → start
SJ: Detect squat hold → takeoff
```

### 4.4 MediaPipe Landmarks

**Sprinting Challenges:**

- **Motion blur:** Fast limb movement → landmark jitter
- **Foot strike:** Brief contact (80-120ms) → may be only 2-4 frames at 30fps
- **Occlusion:** Swing leg may be hidden by stance leg at 90° view
- **Perspective:** Side view essential (different from CMJ's 45° oblique)

**Solutions:**

- **Higher frame rate:** 60fps minimum, 120fps ideal
- **Temporal smoothing:** Critical for velocity/acceleration
- **Hip tracking:** Use hip instead of foot for cycle detection (more stable)
- **Multiple stride averaging:** Reduce noise by averaging 5-10 strides

---

## 5. Normative Values Database

### 5.1 Max Velocity Phase (MVP Focus)

**Elite Sprinters (World Class):**

| Metric               | Range        | Mean ± SD    |
| -------------------- | ------------ | ------------ |
| Velocity (m/s)       | 11.5-12.5    | 12.0 ± 0.4   |
| Ground Contact (ms)  | 80-120       | 100 ± 15     |
| Flight Time (ms)     | 120-160      | 140 ± 15     |
| Stride Frequency (Hz)| 4.5-5.0      | 4.7 ± 0.2    |
| Stride Length (m)    | 2.2-2.7      | 2.4 ± 0.2    |
| Flight Ratio         | 0.55-0.60    | 0.57 ± 0.02  |

**College Sprinters:**

| Metric               | Range        | Mean ± SD    |
| -------------------- | ------------ | ------------ |
| Velocity (m/s)       | 9.5-10.5     | 10.0 ± 0.4   |
| Ground Contact (ms)  | 100-140      | 120 ± 15     |
| Flight Time (ms)     | 110-140      | 125 ± 12     |
| Stride Frequency (Hz)| 4.2-4.7      | 4.4 ± 0.2    |
| Stride Length (m)    | 1.9-2.3      | 2.1 ± 0.2    |
| Flight Ratio         | 0.50-0.55    | 0.52 ± 0.02  |

**High School Sprinters:**

| Metric               | Range        | Mean ± SD    |
| -------------------- | ------------ | ------------ |
| Velocity (m/s)       | 8.0-9.5      | 8.7 ± 0.5    |
| Ground Contact (ms)  | 120-160      | 140 ± 15     |
| Flight Time (ms)     | 100-130      | 115 ± 12     |
| Stride Frequency (Hz)| 3.8-4.4      | 4.1 ± 0.2    |
| Stride Length (m)    | 1.6-2.1      | 1.9 ± 0.2    |
| Flight Ratio         | 0.45-0.50    | 0.48 ± 0.02  |

**Recreational Athletes:**

| Metric               | Range        | Mean ± SD    |
| -------------------- | ------------ | ------------ |
| Velocity (m/s)       | 6.5-8.0      | 7.2 ± 0.6    |
| Ground Contact (ms)  | 150-200      | 175 ± 20     |
| Flight Time (ms)     | 90-120       | 105 ± 12     |
| Stride Frequency (Hz)| 3.5-4.0      | 3.8 ± 0.2    |
| Stride Length (m)    | 1.4-1.8      | 1.6 ± 0.2    |
| Flight Ratio         | 0.40-0.45    | 0.42 ± 0.02  |

### 5.2 Acceleration Phase (Future Enhancement)

**First 10m (Block Acceleration):**

| Metric               | Elite        | College      | High School  |
| -------------------- | ------------ | ------------ | ------------ |
| Time (s)             | 1.7-1.9      | 1.9-2.1      | 2.1-2.4      |
| Ground Contact (ms)  | 200-250      | 220-270      | 240-290      |
| Step Frequency (Hz)  | 3.5-4.0      | 3.2-3.7      | 2.9-3.4      |
| Step Length (m)      | 1.2-1.5      | 1.0-1.3      | 0.9-1.2      |

**10-30m (Transition to Max Velocity):**

| Metric               | Elite        | College      | High School  |
| -------------------- | ------------ | ------------ | ------------ |
| Velocity (m/s)       | 9-11         | 8-9.5        | 7-8.5        |
| Ground Contact (ms)  | 150-180      | 170-200      | 190-220      |
| Step Frequency (Hz)  | 4.0-4.5      | 3.7-4.2      | 3.4-3.9      |
| Step Length (m)      | 1.6-2.0      | 1.4-1.8      | 1.2-1.6      |

---

## 6. Validation Bounds (Red Flags)

### 6.1 Physiological Impossibilities

| Metric               | Impossible If...          | Check                      |
| -------------------- | ------------------------- | -------------------------- |
| Ground Contact Time  | < 60ms                    | Below physiological limit  |
| Ground Contact Time  | > 350ms                   | Beyond sprinting (jogging) |
| Flight Time          | < 50ms                    | Too brief for sprinting    |
| Stride Frequency     | > 6.0 Hz                  | Beyond human capability    |
| Stride Frequency     | < 2.5 Hz                  | Too slow for sprinting     |
| Stride Length        | > 3.0m (max velocity)     | Exceeds world record       |
| Velocity             | > 13.0 m/s                | Exceeds Bolt's record      |

### 6.2 Technical Issue Flags

| Metric Pattern                   | Likely Issue                         | Action                                  |
| -------------------------------- | ------------------------------------ | --------------------------------------- |
| GCT varies wildly stride-to-stride| Tracking inconsistency               | Check video quality, lighting          |
| No clear foot strike pattern      | Camera angle wrong                   | Verify 90° lateral view                 |
| All contacts < 3 frames at 30fps  | Frame rate too low                   | Recommend 60fps+ recording             |
| Foot lost during swing phase      | Occlusion/MediaPipe limitation       | Use RTMPose or adjust camera position  |
| Contact/flight times inconsistent | Incorrect phase detection            | Adjust velocity thresholds             |

### 6.3 Athlete Profile Flags

**Elite Sprinter Indicators:**
- GCT < 100ms at max velocity
- Flight ratio > 0.55
- Stride frequency > 4.5 Hz
- Stride length > 2.2m at max velocity

**Recreational Level Indicators:**
- GCT > 160ms at max velocity
- Flight ratio < 0.45
- Stride frequency < 3.8 Hz
- Stride length < 1.6m

**Technique Issues:**
- GCT decreasing but velocity not increasing → poor force application
- High stride frequency but short stride length → overstriding
- Large vertical oscillation → excessive bounce (energy waste)
- Asymmetric stride times (left vs right) → imbalance/injury risk

---

## 7. MVP Implementation Recommendations

### 7.1 Phase Focus: Max Velocity (40-50m zone)

**Rationale:**
- Stable, consistent mechanics (steady-state)
- Easiest algorithms (regular cyclical pattern)
- Most performance differentiation between athletes
- Simplest camera setup (single position, 90° lateral)
- Best MediaPipe tracking (upright body)

### 7.2 Minimum Viable Metrics

**Tier 1 (MVP - Implement First):**

1. **Stride Frequency** (Hz)
   - Easiest to measure (count foot strikes)
   - No calibration needed
   - Robust to tracking issues

2. **Ground Contact Time** (ms)
   - Critical performance metric
   - Can measure from ankle or hip
   - Requires high frame rate (60fps+)

3. **Flight Time** (ms)
   - Complements contact time
   - Flight ratio = efficiency metric
   - Easier to detect than contact (hip oscillation)

4. **Flight Ratio** (unitless)
   - Efficiency indicator
   - No calibration needed
   - Clear normative bands

**Tier 2 (With Calibration):**

5. **Velocity** (m/s)
   - Requires camera calibration (known distance)
   - Most intuitive metric for coaches
   - Enables stride length calculation

6. **Stride Length** (m)
   - Derived from velocity and frequency
   - Key technical component
   - Coach-friendly metric

**Tier 3 (Advanced/Future):**

7. **Horizontal Force Production** (estimate)
   - Requires mass + velocity + contact time
   - Complex calculations
   - Research-grade analysis

8. **Joint Angles** (hip, knee, ankle)
   - Technical analysis
   - Requires very accurate tracking
   - For detailed coaching

### 7.3 Algorithm Design

**Stride Detection (Core Algorithm):**

```python
def detect_stride_cycles(ankle_height_y: np.ndarray, fps: float) -> list[dict]:
    """
    Detect stride cycles from ankle height oscillation.

    Args:
        ankle_height_y: Normalized vertical ankle position (0-1)
        fps: Video frame rate

    Returns:
        List of stride cycles with foot strike frames
    """
    # 1. Smooth ankle height trajectory
    smoothed = savgol_filter(ankle_height_y, window_length=11, polyorder=2)

    # 2. Compute vertical velocity
    velocity = np.gradient(smoothed)

    # 3. Find foot strikes (local minima with velocity crossing zero)
    # Ankle height is minimum when foot contacts ground
    from scipy.signal import find_peaks
    foot_strikes, _ = find_peaks(-smoothed, prominence=0.02)  # Invert for minima

    # 4. Group into strides (left-left or right-right)
    # Every other minimum is same foot
    left_strikes = foot_strikes[::2]
    right_strikes = foot_strikes[1::2]

    # 5. Calculate stride metrics
    strides = []
    for i in range(len(left_strikes) - 1):
        stride_duration_frames = left_strikes[i+1] - left_strikes[i]
        stride_duration_sec = stride_duration_frames / fps
        stride_frequency = 1.0 / stride_duration_sec

        strides.append({
            'start_frame': left_strikes[i],
            'end_frame': left_strikes[i+1],
            'duration_sec': stride_duration_sec,
            'frequency_hz': stride_frequency
        })

    return strides
```

**Contact/Flight Time Detection:**

```python
def detect_contact_flight_phases(
    ankle_height_y: np.ndarray,
    foot_strike_frames: list[int],
    fps: float
) -> list[dict]:
    """
    Detect ground contact and flight phases within each stride.

    Args:
        ankle_height_y: Normalized vertical ankle position
        foot_strike_frames: List of foot strike frame indices
        fps: Video frame rate

    Returns:
        List of phases with contact and flight times
    """
    phases = []

    for i, strike_frame in enumerate(foot_strike_frames[:-1]):
        # Contact phase: foot strike to next minimum (ankle lowest)
        # Flight phase: takeoff to next foot strike

        # Find takeoff (when ankle starts rising rapidly)
        # This is when ankle height reaches local maximum after contact
        search_window = range(strike_frame, min(strike_frame + 15, len(ankle_height_y)))
        contact_end = max(search_window, key=lambda f: ankle_height_y[f])

        # Calculate times
        contact_frames = contact_end - strike_frame
        contact_time_ms = (contact_frames / fps) * 1000

        # Flight time: from takeoff to next foot strike
        next_strike = foot_strike_frames[i + 1]
        flight_frames = next_strike - contact_end
        flight_time_ms = (flight_frames / fps) * 1000

        phases.append({
            'foot_strike_frame': strike_frame,
            'takeoff_frame': contact_end,
            'contact_time_ms': contact_time_ms,
            'flight_time_ms': flight_time_ms,
            'flight_ratio': flight_time_ms / (contact_time_ms + flight_time_ms)
        })

    return phases
```

### 7.4 Validation Framework

**Follow Existing Pattern:**

```python
class SprintingBounds(MetricBounds):
    """Validation bounds for sprinting metrics."""

    # Stride Frequency (Hz)
    absolute_min: float = 2.0
    absolute_max: float = 6.0
    practical_min: float = 2.5
    recreational_min: float = 3.0
    recreational_max: float = 4.2
    elite_min: float = 4.2
    elite_max: float = 5.2

    # Ground Contact Time (ms) - at max velocity
    absolute_min: float = 60
    absolute_max: float = 350
    practical_min: float = 80
    recreational_min: float = 140
    recreational_max: float = 200
    elite_min: float = 80
    elite_max: float = 120

    # Flight Time (ms)
    absolute_min: float = 50
    absolute_max: float = 250
    practical_min: float = 80
    recreational_min: float = 90
    recreational_max: float = 120
    elite_min: float = 120
    elite_max: float = 160

    # Flight Ratio
    absolute_min: float = 0.20
    absolute_max: float = 0.80
    practical_min: float = 0.30
    recreational_min: float = 0.35
    recreational_max: float = 0.48
    elite_min: float = 0.50
    elite_max: float = 0.62
```

### 7.5 Camera Setup Guide for Users

**Recommended Setup (Max Velocity Phase):**

```
1. Position camera 5-10m perpendicular to track at 40-50m mark
2. Set camera height 1-1.5m from ground (hip level)
3. Frame athlete from head to feet (full body visible)
4. Include lane markings or meter marks for calibration
5. Record at 60fps or higher (120fps ideal)
6. Capture 5-10 consecutive strides
```

**Validation Checks:**

- ✓ Athlete fully visible in frame
- ✓ 90° lateral view (side view)
- ✓ Lane markings visible (for calibration)
- ✓ Frame rate ≥ 60fps
- ✓ Athlete at max velocity (40-50m mark in 100m sprint)

---

## 8. Key Differences from Jump Analysis

| Aspect                | Sprinting                                  | Jumping (CMJ/DJ/SJ)                 |
| --------------------- | ------------------------------------------ | ----------------------------------- |
| **Movement Type**     | Cyclical (repeating)                       | Discrete (single event)             |
| **Primary Direction** | Horizontal                                 | Vertical                            |
| **Detection**         | Stride cycles, foot strike pattern          | Takeoff/landing events               |
| **Algorithm**         | Peak detection, periodicity, averaging      | Forward/backward search             |
| **Metrics**           | Frequency, contact/flight, stride length    | Height, RSI, power                  |
| **Camera Angle**      | 90° lateral (side view)                     | 45° oblique (CMJ/DJ)                |
| **Frame Rate**        | 60fps+ critical (80-120ms contact)          | 30fps acceptable (200ms+ contact)    |
| **Smoothing**         | Heavy smoothing needed (high-freq osc)      | Moderate smoothing                  |
| **Calibration**       | Required for velocity/length                | Not required for height/RSI          |

---

## 9. Research References

### Primary Sources

1. **Mattes & Wolff (2021)** - "Kinematic Stride Characteristics of Maximal Sprint Running"
   - Journal of Human Kinetics 77:15-24
   - Elite sprinter stride mechanics at max velocity
   - Ground contact times: 80-120ms (elite)
   - Stride length: 2.2-2.7m (elite)

2. **Miyashiro et al. (2019)** - "Kinematics of Maximal Speed Sprinting"
   - Frontiers in Sports and Active Living
   - Leg length effects on stride parameters
   - Step frequency vs step length trade-offs

3. **Čoh (2019)** - "Usain Bolt: Biomechanical Model of Sprint Technique"
   - FACTA UNIVERSITATIS
   - Bolt's max velocity: 12.42 m/s at 70-90m
   - Stride length: 2.70m, frequency: 4.6 Hz

4. **Seidl et al. (2021)** - "Assessment of Sprint Parameters in Top Speed Interval"
   - Frontiers in Sports and Active Living 3:689341
   - Field-based 2D video validation
   - Practical methodology for coaching

5. **Nagahara et al. (2014)** - "Kinematics of Transition During Accelerated Sprinting"
   - Biology Open 3:689-699
   - Acceleration to max velocity transition
   - Biomechanical changes across phases

### Normative Data

6. **McKay et al. (2020)** - "Normative Reference Values for High School Athletes"
   - JSCR 34(4)
   - High school sprinting benchmarks

7. **Selmi et al. (2020)** - "Normative Data and Determinants of Sprint Performance"
   - JSCR 34(2)
   - Multiple sprint tests, normative ranges

### 2D Video Analysis

8. **van der Meijden (2019)** - "Analyzing Sprint Features with 2D Human Pose Estimation"
   - Master's thesis, Tilburg University
   - Pose estimation for sprinting
   - Feature extraction methodology

9. **Garden et al. (2022)** - "Sprint Technique: Football Players vs Elite Sprinters"
   - ISBS Proceedings
   - 2D video comparison study
   - Technical differences between populations

### Pose Estimation

10. **Pose Estimator Comparison (2025)** - See: docs/research/pose-estimator-comparison-2025.md
    - RTMPose: 5.62° RMSE (best for sprinting)
    - MediaPipe: 6.33° RMSE
    - Motion blur challenges
    - Recommendation: RTMPose for sprint analysis

---

## 10. Implementation Roadmap

### Phase 1: MVP (Max Velocity Focus)

**Week 1-2: Core Algorithms**
- Implement stride cycle detection (ankle/hip oscillation)
- Foot strike detection (local minima)
- Contact/flight time measurement
- Stride frequency calculation

**Week 3: Validation & Bounds**
- Implement SprintingBounds class
- Add physiological checks
- Create validation tests

**Week 4: Testing**
- Test on real sprinting videos
- Validate against published norms
- Refine thresholds

**Deliverable:**
- Command: `kinemotion sprint-analyze video.mp4`
- Metrics: Stride frequency, contact time, flight time, flight ratio
- Output: JSON + optional debug video

### Phase 2: Calibration & Distance Metrics

**Week 5-6:**
- Camera calibration interface
- Velocity calculation (pixels → meters)
- Stride length derivation
- Enhanced debug overlay (trajectory plots)

**Deliverable:**
- Additional metrics: Velocity, stride length
- Calibration workflow for users

### Phase 3: Acceleration Phase (Optional)

**Week 7-8:**
- Acceleration-specific algorithms
- Multi-phase detection (acceleration → max velocity)
- Advanced metrics (force estimates, power)

**Deliverable:**
- Full 100m sprint analysis
- Phase-by-phase breakdown

---

## Summary of MVP Recommendations

### What to Build First

**Target Phase:** Max Velocity (40-50m zone)

**Minimum Metrics:**
1. Stride Frequency (Hz)
2. Ground Contact Time (ms)
3. Flight Time (ms)
4. Flight Ratio (unitless)

**Camera Setup:**
- 90° lateral view
- 5-10m distance from track
- 60fps minimum recording
- Calibrate with lane markings

**Algorithm Approach:**
- Detect foot strikes from ankle height minima
- Group into stride cycles (alternating left/right)
- Measure contact/flight within each stride
- Average across 5-10 strides for stability

**Validation Strategy:**
- Physiological bounds (60-350ms contact time)
- Profile-based norms (elite vs recreational)
- Technical issue flags (frame rate, tracking quality)

### Key Success Factors

1. **High frame rate:** 60fps minimum, 120fps ideal (contact phase only 80-120ms)
2. **Camera angle:** 90° lateral (not 45° like CMJ)
3. **Smoothing:** Heavy temporal smoothing needed (high-frequency oscillation)
4. **Calibration:** Required for velocity/length (not needed for frequency/times)
5. **Stride averaging:** Reduce noise by averaging multiple strides

### Red Flags to Watch

- Contact time < 3 frames at 30fps (frame rate too low)
- Inconsistent stride patterns (tracking issues)
- All contacts < 80ms for recreational athletes (unlikely)
- No clear foot strike oscillation (wrong phase or camera angle)

### Integration with Existing Codebase

**Follow Drop Jump Pattern:**
- `src/kinemotion/sprinting/` module
- `analysis.py` - stride detection algorithms
- `kinematics.py` - velocity, stride length calculations
- `metrics_validator.py` - SprintingMetricsValidator
- `validation_bounds.py` - SprintingBounds

**Reuse Core Components:**
- `smoothing.py` - temporal filtering (critical for sprinting)
- `validation.py` - MetricsValidator base class
- `pose.py` - MediaPipePoseTracker (or RTMPoseTracker)

**New Challenges:**
- Cyclical detection (vs discrete event detection)
- Horizontal velocity (vs vertical)
- Camera calibration (not needed for jumps)
- Higher frame rate requirements

---

**Document Status:** Initial research complete, ready for implementation planning

**Next Steps:** Review with project manager, prioritize MVP scope, begin algorithm development
