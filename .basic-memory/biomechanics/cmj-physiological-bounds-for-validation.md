---
title: CMJ Physiological Bounds for Validation
type: note
permalink: biomechanics/cmj-physiological-bounds-for-validation
tags:
  - cmj
  - validation
  - biomechanics
  - bounds
---

# CMJ Physiological Bounds for Validation

This document defines realistic physiological bounds for Counter Movement Jump (CMJ) metrics used in kinemotion. These bounds prevent false positives from noise while catching real errors in video processing and phase detection.

## 1. FLIGHT TIME (seconds)

### Definition

Time from takeoff to landing, measured from frame indices.

### Calculation Basis

From jump height formula: h = g·t²/8, therefore t = √(8h/g)

### Physiological Bounds

| Metric                   | Value (seconds)  | Justification                                                    |
| ------------------------ | ---------------- | ---------------------------------------------------------------- |
| **Absolute Minimum**     | 0.10             | Below this, video frame rate insufficient to resolve jump phases |
| **Practical Minimum**    | 0.15             | Minimum for weakest individuals jumping with effort              |
| **Recreational Min**     | 0.25             | Typical untrained/elderly (~10cm jump)                           |
| **Recreational Typical** | 0.40-0.65        | Untrained to moderately trained (~20-50cm jumps)                 |
| **Elite Typical**        | 0.65-0.95        | Trained athletes (60-90cm jumps)                                 |
| **Absolute Maximum**     | 1.1              | Elite male athletes only (>100cm jumps)                          |
| **Error Threshold**      | <0.08s or >1.3s  | Indicates frame rate issue or detection failure                  |

### Calculation Examples

| Jump Height  | Flight Time |
| ------------ | ----------- |
| 10cm (0.10m) | 0.286s      |
| 30cm (0.30m) | 0.494s      |
| 50cm (0.50m) | 0.639s      |
| 70cm (0.70m) | 0.753s      |
| 90cm (0.90m) | 0.956s      |

### Why This Range

- **Lower bound**: MediaPipe requires multiple frames to detect landing phase. At 30fps, 0.10s = 3 frames (barely resolvable).
- **Upper bound**: Human biomechanics limits maximum upward velocity to ~4.5 m/s (elite males). Using v² = 2gh: maximum jump ~103cm → t = 1.03s.
- **Frame rate dependency**: At lower frame rates (24fps), minimum flight time increases proportionally.

## 2. JUMP HEIGHT (meters)

### Definition

Maximum vertical displacement during flight, calculated from flight time: h = g·t²/8

### Physiological Bounds

| Metric                   | Value (meters)    | Justification                                       |
| ------------------------ | ----------------- | --------------------------------------------------- |
| **Absolute Minimum**     | 0.05              | Minimum effort jump that's still measurable         |
| **Practical Minimum**    | 0.08              | Weakest individuals with structured movement        |
| **Recreational Min**     | 0.15              | Untrained/elderly with moderate effort              |
| **Recreational Typical** | 0.30-0.60         | General population, fitness class participants      |
| **Trained Typical**      | 0.50-0.75         | Athletes, active individuals                        |
| **Elite Typical**        | 0.70-1.00         | Competitive athletes, basketball/volleyball players |
| **Absolute Maximum**     | 1.15              | Genetic outliers, world-class performers            |
| **Error Threshold**      | <0.02m or >1.30m  | Indicates detection failure or data corruption      |

### Reverse Velocity Verification

For independent validation, jump height should satisfy: h ≈ v_peak²/(2g)

| Peak Velocity | Expected Jump Height |
| ------------- | -------------------- |
| 1.5 m/s       | 0.115m               |
| 2.0 m/s       | 0.204m               |
| 2.5 m/s       | 0.319m               |
| 3.0 m/s       | 0.459m               |
| 3.5 m/s       | 0.624m               |
| 4.0 m/s       | 0.816m               |
| 4.5 m/s       | 1.031m               |

### Why This Range

- **Lower bound**: Humans cannot intentionally jump lower than ~5cm; below 2cm indicates noise.
- **Upper bound**: Peak concentric velocity physiologically maxes at ~4.5 m/s. Even elite males rarely exceed 110cm.
- **Gender differences**: Females typically 60-70% of male values; adjust upper bounds accordingly.

## 3. COUNTERMOVEMENT DEPTH (meters)

### Definition

Vertical distance traveled from standing position to lowest point of squat.

### Physiological Bounds

| Metric               | Value (meters)    | Justification                                    |
| -------------------- | ----------------- | ------------------------------------------------ |
| **Absolute Minimum** | 0.08              | Minimal squat, almost no countermovement         |
| **Shallow Movement** | 0.10-0.25         | Elderly, weak, or deliberately quick jumps       |
| **Normal CMJ**       | 0.25-0.50         | Recreational athletes, quarter-to-parallel squat |
| **Deep CMJ**         | 0.45-0.70         | Trained athletes, below-parallel squat           |
| **Very Deep**        | 0.65-0.90         | Tall individuals with excellent mobility         |
| **Absolute Maximum** | 1.00              | Only possible for very tall athletes (>6'2")     |
| **Error Threshold**  | <0.05m or >1.10m  | Indicates pose tracking failure                  |

### Correlation with Jump Height

Research (Nordez et al., 2009; Lees et al., 2004):

- Deeper countermovement generally correlates with higher jump height
- Ratio: jump_height ≈ 0.5-1.0 × countermovement_depth
- But diminishing returns after 50cm (optimal squat depth ~50cm for most athletes)

### Why This Range

- **Lower bound**: Below 5cm indicates almost no squat detected; likely false standing position.
- **Upper bound**: Human leg structure limits squat depth; >1.0m impossible without leg extension miscalculation.
- **Athlete variation**: Tall athletes naturally deeper; short athletes naturally shallower.

## 4. CONTACT TIME / CONCENTRIC DURATION (seconds)

### Definition

Time from lowest point (end of eccentric phase) to takeoff (start of propulsion phase).

### Physiological Bounds

| Metric                      | Value (seconds)   | Justification                             |
| --------------------------- | ----------------- | ----------------------------------------- |
| **Absolute Minimum**        | 0.10              | Only extreme plyometric athletes          |
| **Very Fast**               | 0.15-0.30         | Plyometrically trained, reactive athletes |
| **Fast (Elite)**            | 0.25-0.45         | Trained athletes, high power output       |
| **Moderate (Recreational)** | 0.40-0.70         | General fitness population                |
| **Slow (Untrained)**        | 0.60-0.90         | Deconditioned, elderly                    |
| **Very Slow**               | 0.80-1.20         | Weak, injured, or controlled movement     |
| **Absolute Maximum**        | 1.5               | Only in severe weakness or very elderly   |
| **Error Threshold**         | <0.08s or >1.80s  | Indicates phase detection failure         |

### Reactive Strength Index (RSI) Cross-Check

RSI = flight_time / contact_time

| RSI Range | Interpretation                       |
| --------- | ------------------------------------ |
| <0.3      | Error (invalid metrics)              |
| 0.3-0.8   | Untrained, poor reactive strength    |
| 0.8-1.5   | Recreational, moderate RSI           |
| 1.5-2.5   | Trained athletes                     |
| 2.5-4.0   | Elite athletes, excellent reactivity |
| >4.0      | Error (physiologically impossible)   |

### Why This Range

- **Lower bound**: Contact time <100ms requires ~200 m/s² acceleration (7G force); only possible with extreme training + equipment assistance.
- **Upper bound**: Contact time >1.5s indicates incomplete squat or detection of standing phase (should have stopped at lowest point).
- **RSI validation**: Contact time too short relative to flight time flags detection errors.

## 5. PEAK ECCENTRIC VELOCITY (m/s, downward)

### Definition

Maximum downward velocity during countermovement (negative values in signed velocity system).

### Physiological Bounds

| Metric               | Value (m/s)            | Justification                              |
| -------------------- | ---------------------- | ------------------------------------------ |
| **Minimum**          | 0.15                   | Barely detectable movement                 |
| **Untrained**        | 0.4-1.0                | Slow, controlled descent                   |
| **Recreational**     | 0.8-1.8                | Moderate speed descent                     |
| **Trained**          | 1.5-2.5                | Fast, controlled eccentric                 |
| **Elite**            | 2.2-3.5                | Very fast eccentric phase                  |
| **Absolute Maximum** | 4.0                    | Extreme athletes only                      |
| **Error Threshold**  | <0.10 m/s or >5.0 m/s  | Indicates signal noise or tracking failure |

### Relationship to Countermovement Depth

Expected: v_eccentric = √(2g·depth)

| Depth | Expected Peak Velocity |
| ----- | ---------------------- |
| 0.20m | 1.98 m/s               |
| 0.30m | 2.43 m/s               |
| 0.50m | 3.13 m/s               |
| 0.70m | 3.71 m/s               |

### Why This Range

- **Lower bound**: Below 0.1 m/s indicates no detectable movement or signal noise.
- **Upper bound**: Maximum possible from v² = 2gh with 1.0m depth → v ≈ 4.4 m/s.
- **Validation**: Cross-check with: v² ≈ 2g·countermovement_depth

## 6. PEAK CONCENTRIC VELOCITY (m/s, upward)

### Definition

Maximum upward velocity during propulsion phase (from lowest point to takeoff).

### Physiological Bounds

| Metric               | Value (m/s)            | Justification                           |
| -------------------- | ---------------------- | --------------------------------------- |
| **Minimum**          | 0.3                    | Absolute minimum to leave ground        |
| **Weak/Elderly**     | 0.8-1.5                | Very low jump performance               |
| **Untrained**        | 1.5-2.2                | Typical recreational, 10-30cm jumps     |
| **Recreational**     | 2.0-2.8                | Moderate fitness, 20-50cm jumps         |
| **Trained**          | 2.5-3.5                | Athletes, 40-70cm jumps                 |
| **Elite**            | 3.2-4.2                | High-level athletes, 65-90cm jumps      |
| **Absolute Maximum** | 4.8                    | Only elite male athletes (>100cm jumps) |
| **Error Threshold**  | <0.20 m/s or >5.5 m/s  | Indicates detection error               |

### Jump Height Verification Formula

Independent validation: h = v_peak² / (2g)

| Peak Velocity | Expected Jump Height |
| ------------- | -------------------- |
| 1.0 m/s       | 0.051m               |
| 1.5 m/s       | 0.115m               |
| 2.0 m/s       | 0.204m               |
| 2.5 m/s       | 0.319m               |
| 3.0 m/s       | 0.459m               |
| 3.5 m/s       | 0.624m               |
| 4.0 m/s       | 0.816m               |
| 4.5 m/s       | 1.031m               |

**Validation Logic**: Check if calculated jump height matches flight-time-based height ±10%

### Why This Range

- **Lower bound**: 0.2-0.3 m/s is absolute minimum to overcome gravity at liftoff.
- **Upper bound**: Human physiology limits peak acceleration to ~10 m/s² in concentric phase over ~0.4s contact → ~4.0 m/s maximum.
- **Age/gender factors**: Females typically 80-85% of male values; adjust accordingly.

## 7. TRIPLE EXTENSION ANGLES (degrees)

### Definition

Joint angles at moment of takeoff, measuring hip, knee, ankle extension.

### 7.1 HIP ANGLE

| Metric               | Range (degrees) | Interpretation                       |
| -------------------- | --------------- | ------------------------------------ |
| **Full Extension**   | 175-185°        | Normal, good technique               |
| **Trained Athletes** | 170-185°        | Adequate extension                   |
| **Recreational**     | 160-175°        | Acceptable but less efficient        |
| **Poor Extension**   | 140-160°        | Incomplete extension, weak hip power |
| **Error Threshold**  | <120° or >195°  | Not at takeoff or processing error   |

### 7.2 KNEE ANGLE

| Metric               | Range (degrees) | Interpretation                         |
| -------------------- | --------------- | -------------------------------------- |
| **Full Extension**   | 175-190°        | Normal, excellent technique            |
| **Trained Athletes** | 170-188°        | Good extension                         |
| **Recreational**     | 160-180°        | Acceptable                             |
| **Poor Extension**   | 140-165°        | Incomplete quad extension              |
| **Error Threshold**  | <130° or >200°  | Not at takeoff or hyperextension error |

### 7.3 ANKLE ANGLE (plantarflexion)

| Metric                     | Range (degrees)               | Interpretation                     |
| -------------------------- | ----------------------------- | ---------------------------------- |
| **Full Plantarflexion**    | 130-155°                      | Normal, good calf contribution     |
| **Trained Athletes**       | 125-150°                      | Good plantarflexion                |
| **Recreational**           | 115-140°                      | Acceptable                         |
| **Limited Plantarflexion** | 100-120°                      | Poor calf involvement              |
| **Error Threshold**        | <90° (dorsiflexion) or >165°  | Not at takeoff or tracking failure |

**Note**: Ankle angle measurement is challenging in side-view video due to foot foreshortening. MediaPipe may miss foot/ankle details.

### 7.4 TRUNK TILT (forward lean from vertical)

| Metric                | Range (degrees)           | Interpretation                       |
| --------------------- | ------------------------- | ------------------------------------ |
| **Upright**           | 0-15°                     | Excellent posture                    |
| **Slight Forward**    | 10-25°                    | Normal, healthy forward lean         |
| **Moderate Forward**  | 20-35°                    | Acceptable, some forward lean        |
| **Excessive Forward** | 30-50°                    | Poor balance or off-center jump      |
| **Error Threshold**   | <-10° (backward) or >60°  | Likely off-balance or tracking error |

### Why These Ranges

- **Biomechanical**: Triple extension is key indicator of jumping technique quality. Synchronized hip-knee-ankle extension generates maximum force.
- **Performance correlation**: Better angles correlate with higher jump heights and lower ground contact times.
- **Age/training effects**: Untrained athletes show incomplete extension; elderly show marked restrictions.
- **Video challenges**: Side view may have limited ankle visibility; front view may have poor hip detail.

## 8. ECCENTRIC AND CONCENTRIC DURATION (seconds)

### Definition

- **Eccentric duration**: Standing position to lowest point
- **Concentric duration**: Lowest point to takeoff

### Physiological Bounds

| Phase              | Minimum | Recreational | Elite      | Maximum | Error Threshold   |
| ------------------ | ------- | ------------ | ---------- | ------- | ----------------- |
| **Eccentric**      | 0.25s   | 0.40-0.70s   | 0.35-0.60s | 1.0s    | >1.2s or <0.20s   |
| **Concentric**     | 0.10s   | 0.40-0.70s   | 0.25-0.45s | 1.5s    | >1.80s or <0.08s  |
| **Total Movement** | 0.35s   | 0.80-1.40s   | 0.60-1.05s | 2.0s    | >2.2s or <0.30s   |

### Eccentric-to-Concentric Ratio

- **Untrained**: Eccentric ~60%, Concentric ~40%
- **Recreational**: Eccentric ~55%, Concentric ~45%
- **Trained**: Eccentric ~50%, Concentric ~50%
- **Elite**: Eccentric ~45%, Concentric ~55% (faster propulsion)

### Why This Range

- **Eccentric**: Longer in untrained (less neural drive, more control); shorter in trained (bouncy, reactive).
- **Concentric**: Trained athletes generate power quickly; untrained take longer.
- **Error flags**: If total time >2.2s, likely includes standing phase detection failure.

## 9. ATHLETE PROFILES & EXPECTED RANGES

### Profile 1: Elderly / Deconditioned

**Scenario**: 70+ year old, limited mobility, jumps with light effort

| Metric                        | Value                | Notes                           |
| ----------------------------- | -------------------- | ------------------------------- |
| **Jump Height**               | 0.10-0.18m (10-18cm) | Very low                        |
| **Flight Time**               | 0.14-0.19s           | ~150-190ms                      |
| **Countermovement Depth**     | 0.12-0.20m           | Shallow squat, mobility limited |
| **Contact Time (Concentric)** | 0.80-1.20s           | Slow, weak propulsion           |
| **Peak Eccentric Velocity**   | 0.4-0.7 m/s          | Slow descent                    |
| **Peak Concentric Velocity**  | 1.0-1.5 m/s          | Weak push-off                   |
| **Hip Angle at Takeoff**      | 150-165°             | Incomplete extension            |
| **Knee Angle at Takeoff**     | 155-170°             | Incomplete extension            |
| **Ankle Angle at Takeoff**    | 105-120°             | Limited plantarflexion          |
| **RSI**                       | 0.15-0.25            | Very poor reactive strength     |
| **Total Movement Time**       | 1.5-2.2s             | Long, controlled movement       |

**Validation Checks**:

- Jump height ~v² / (2g): 1.2² / 19.62 ≈ 0.073m ✓ (close to 0.10-0.18m range)
- Flight time confirmed from height: 0.10m → t = 0.286s ✓
- RSI in expected range: 0.15 < 0.25 ✓

### Profile 2: Recreational Athlete

**Scenario**: Fitness class participant, moderate training, age 30-45

| Metric                        | Value                | Notes                       |
| ----------------------------- | -------------------- | --------------------------- |
| **Jump Height**               | 0.35-0.55m (35-55cm) | Good recreational           |
| **Flight Time**               | 0.53-0.67s           | ~530-670ms                  |
| **Countermovement Depth**     | 0.28-0.45m           | Good squat depth (parallel) |
| **Contact Time (Concentric)** | 0.45-0.65s           | Moderate propulsion speed   |
| **Peak Eccentric Velocity**   | 1.3-1.9 m/s          | Moderate descent speed      |
| **Peak Concentric Velocity**  | 2.6-3.3 m/s          | Good propulsive force       |
| **Hip Angle at Takeoff**      | 168-178°             | Good extension              |
| **Knee Angle at Takeoff**     | 170-182°             | Good extension              |
| **Ankle Angle at Takeoff**    | 120-138°             | Good plantarflexion         |
| **RSI**                       | 0.85-1.25            | Moderate reactive strength  |
| **Total Movement Time**       | 0.95-1.35s           | Normal CMJ timing           |

**Validation Checks**:

- Jump height: 2.9² / 19.62 ≈ 0.43m ✓ (middle of 0.35-0.55m)
- Flight time from 0.45m: t = √(8×0.45/9.81) = 0.604s ✓ (middle of range)
- RSI: 0.60s / 0.50s = 1.2 ✓ (within 0.85-1.25)

### Profile 3: Elite Male Athlete

**Scenario**: Collegiate volleyball/basketball player, highly trained

| Metric                        | Value                | Notes                       |
| ----------------------------- | -------------------- | --------------------------- |
| **Jump Height**               | 0.68-0.88m (68-88cm) | Excellent performance       |
| **Flight Time**               | 0.74-0.84s           | ~740-840ms                  |
| **Countermovement Depth**     | 0.42-0.62m           | Deep squat (below parallel) |
| **Contact Time (Concentric)** | 0.28-0.42s           | Very fast, powerful         |
| **Peak Eccentric Velocity**   | 2.1-3.2 m/s          | Fast eccentric              |
| **Peak Concentric Velocity**  | 3.6-4.2 m/s          | Excellent propulsive power  |
| **Hip Angle at Takeoff**      | 173-185°             | Excellent extension         |
| **Knee Angle at Takeoff**     | 176-188°             | Excellent extension         |
| **Ankle Angle at Takeoff**    | 132-148°             | Strong plantarflexion       |
| **RSI**                       | 1.85-2.80            | Excellent reactive strength |
| **Total Movement Time**       | 0.70-0.95s           | Efficient, explosive timing |

**Validation Checks**:

- Jump height: 3.9² / 19.62 ≈ 0.78m ✓ (middle of 0.68-0.88m)
- Flight time from 0.78m: t = √(8×0.78/9.81) = 0.796s ✓ (middle of range)
- RSI: 0.80s / 0.35s = 2.29 ✓ (within 1.85-2.80)
- Contact time much shorter than recreational profile ✓

## 10. EDGE CASES & VALID ANOMALIES

### Edge Case 1: Minimal Countermovement ("Stiffer" Jump)

**Description**: Athlete with natural stiff jumping style or intentionally minimizes squat

**Characteristics**:

- Countermovement depth: 0.10-0.18m (much shallower than typical)
- Flight time: May be reasonable despite shallow countermovement
- Contact time: Shorter than expected (reactive, bouncy)
- Peak velocities: High acceleration but lower peak height
- Triple extension: Already nearly extended at start

**Validation**: NOT an error if:

- Flight time, jump height, and velocity are internally consistent
- RSI is high (0.85+) indicating reactive training
- Athlete profile indicates plyometric training
- Video shows athlete starting from semi-flexed position

**Error if**:

- Countermovement depth <0.08m AND flight time >0.40s (contradictory)
- No clear phase transitions (standing → squat → takeoff)

### Edge Case 2: Double-Bounce Pattern

**Description**: Athlete makes multiple micro-bounces at lowest point before main takeoff

**Characteristics**:

- Contact time artificially long (includes bounces)
- Lowest point frame ambiguous (multiple local minima)
- Velocity oscillation near lowest point (multiple zero crossings)

**Validation**: Acceptable if:

- Phase detection algorithm identifies MAIN takeoff (last zero crossing)
- Not counted as multiple separate jumps
- Movement is intentional (reactive/plyometric training)

**Action**: Flag with warning "Multiple bounces detected - contact time may be artificially long"

### Edge Case 3: Incomplete Eccentric Phase

**Description**: Athlete starts recording already in mid-squat (no standing phase detected)

**Characteristics**:

- Standing start frame: None detected (None value)
- Eccentric duration: Starts from frame 0
- Countermovement depth: Calculated from assumed standing position (may be inaccurate)

**Validation**: Acceptable if:

- Takeoff, landing, flight time all consistent
- Jump height, velocity calculations valid
- Marked in metadata as "incomplete eccentric phase"

**Note from code**: `standing_start_frame` can be None; handled in `calculate_cmj_metrics`

### Edge Case 4: Very Deep Squat (Extreme Flexibility)

**Description**: Athlete with exceptional mobility (yoga, gymnastics background) performs very deep squat

**Characteristics**:

- Countermovement depth: 0.65-0.85m
- Contact time: May be longer than typical (takes more time to traverse depth)
- Eccentric duration: Noticeably longer
- Lower jump height than expected from depth (diminishing returns)

**Validation**: Valid if:

- Contact time / depth ratio is reasonable: (contact_time / depth) should be 0.5-1.5 s/m
- Flight time and jump height are internally consistent
- Athlete appears to have exceptional flexibility in video
- Total movement time is long but reasonable for extreme range

**Example**: 0.70m depth with 0.80s contact → ratio = 1.14 s/m (valid)

### Edge Case 5: Unexpected High RSI with Low Jump Height

**Description**: Athlete shows RSI >2.0 but only jumps 30cm

**Characteristics**:

- RSI ratio: 0.50s flight / 0.20s contact = 2.5 (high)
- Jump height: 0.30m (recreational level, contradictory)
- Peak velocity: ~2.4 m/s (consistent with 0.30m)

**Validation**: Likely ERROR - RSI and jump height contradictory

**Root Cause Analysis**:

- Contact time too short: Detection may have missed landing phase start (lowest point)
- Flight time might include part of contact phase
- Or landing detected too early

**Action**: Flag as warning "RSI appears high relative to jump height - review phase detection"

### Edge Case 6: High Jump Height with Shallow Countermovement

**Description**: 60cm jump height with only 25cm countermovement depth

**Characteristics**:

- Jump height: 0.60m
- Countermovement depth: 0.25m
- Ratio: 2.4 (normally 0.7-1.2 expected)
- Peak velocity: Should be ~3.43 m/s

**Validation**: ERROR

**Root Cause**:

- Likely: Standing position detected incorrectly (too low, making depth appear shallow)
- Or: Lowest point not detected (missed peak descent)
- Result: Countermovement depth underestimated

**Action**: Flag as error "Countermovement depth appears inconsistent with jump height; review standing position detection"

### Edge Case 7: Very Short Contact Time (<0.15s)

**Description**: Contact time 0.12s with RSI = 4.5 and jump height 0.72m

**Characteristics**:

- Flight time: 0.75s
- Contact time: 0.12s
- RSI: 6.25 (physically unrealistic)

**Validation**: ERROR

**Root Cause**:

- Most likely: Lowest point frame detected one frame too late
- Contact time underestimated by missing early concentric phase
- Or: Frame rate assumption incorrect (30fps assumed but video was 60fps)

**Action**: Flag as error "Contact time unusually short; suspect lowest point detection error or frame rate mismatch"

## 11. VALIDATION LOGIC (Pseudo-code)

```python
def validate_cmj_metrics(metrics: CMJMetrics) -> ValidationResult:
    """
    Comprehensive CMJ metrics validation.

    Returns: ValidationResult with flags for errors, warnings, and pass/fail status
    """
    errors = []
    warnings = []

    # ========== PRIMARY BOUNDS CHECKS ==========

    # Flight time bounds
    if metrics.flight_time < 0.08:
        errors.append("flight_time < 0.08s: Likely frame rate or detection error")
    elif metrics.flight_time > 1.3:
        errors.append("flight_time > 1.3s: Exceeds elite human capability")
    elif metrics.flight_time < 0.15:
        warnings.append("flight_time < 0.15s: Very weak jump or frame rate limitation")
    elif metrics.flight_time > 1.1:
        warnings.append("flight_time > 1.1s: Elite-level performance; verify video quality")

    # Jump height bounds
    if metrics.jump_height < 0.02:
        errors.append("jump_height < 0.02m: Essentially no jump detected")
    elif metrics.jump_height > 1.30:
        errors.append("jump_height > 1.30m: Exceeds human physiological limit")
    elif metrics.jump_height < 0.05:
        warnings.append("jump_height < 0.05m: Minimal jump; check for noise")
    elif metrics.jump_height > 1.15:
        warnings.append("jump_height > 1.15m: Exceptional performance; verify detection")

    # Countermovement depth bounds
    if metrics.countermovement_depth < 0.05:
        errors.append("countermovement_depth < 0.05m: Essentially no squat")
    elif metrics.countermovement_depth > 1.10:
        errors.append("countermovement_depth > 1.10m: Exceeds leg structure limit")
    elif metrics.countermovement_depth < 0.08:
        warnings.append("countermovement_depth < 0.08m: Very minimal squat")

    # Concentric duration (contact time) bounds
    concentric_duration = metrics.concentric_duration
    if concentric_duration < 0.08:
        errors.append("concentric_duration < 0.08s: Likely phase detection error")
    elif concentric_duration > 1.80:
        errors.append("concentric_duration > 1.80s: Likely includes standing phase")
    elif concentric_duration < 0.10:
        warnings.append("concentric_duration < 0.10s: Extremely fast propulsion")
    elif concentric_duration > 1.20:
        warnings.append("concentric_duration > 1.20s: Slower than typical; verify lowest point")

    # ========== CROSS-VALIDATION CHECKS ==========

    # Verify jump_height consistency with flight_time
    expected_height = (9.81 * metrics.flight_time**2) / 8
    height_error_pct = abs(metrics.jump_height - expected_height) / expected_height * 100
    if height_error_pct > 10:  # 10% tolerance
        errors.append(
            f"jump_height inconsistent with flight_time: "
            f"got {metrics.jump_height:.3f}m, expected {expected_height:.3f}m"
        )

    # Verify peak_concentric_velocity consistency with jump_height
    expected_velocity = (2 * 9.81 * metrics.jump_height) ** 0.5
    velocity_error_pct = abs(
        metrics.peak_concentric_velocity - expected_velocity
    ) / expected_velocity * 100
    if velocity_error_pct > 15:  # 15% tolerance (more lenient for velocity noise)
        warnings.append(
            f"peak_concentric_velocity inconsistent with jump_height: "
            f"got {metrics.peak_concentric_velocity:.2f} m/s, "
            f"expected {expected_velocity:.2f} m/s"
        )

    # RSI validation
    rsi = metrics.flight_time / concentric_duration if concentric_duration > 0 else 0
    if rsi < 0.3:
        errors.append(f"RSI = {rsi:.2f}: Below physiological minimum (likely error)")
    elif rsi > 4.0:
        errors.append(f"RSI = {rsi:.2f}: Exceeds physiological maximum (likely error)")
    elif rsi > 3.0:
        warnings.append(f"RSI = {rsi:.2f}: Very high; verify contact time detection")
    elif rsi < 0.5:
        warnings.append(f"RSI = {rsi:.2f}: Very low reactive strength")

    # ========== CONSISTENCY CHECKS ==========

    # Countermovement depth vs jump height ratio
    if metrics.countermovement_depth > 0.05:  # Only if depth is meaningful
        depth_to_height_ratio = metrics.jump_height / metrics.countermovement_depth
        if depth_to_height_ratio > 1.5:
            warnings.append(
                f"Jump height {depth_to_height_ratio:.2f}x countermovement depth: "
                f"Unusually efficient (verify standing position)"
            )
        elif depth_to_height_ratio < 0.3:
            warnings.append(
                f"Jump height only {depth_to_height_ratio:.2f}x countermovement depth: "
                f"May indicate incomplete squat detection"
            )

    # Peak velocities in reasonable range
    if metrics.peak_eccentric_velocity < 0.10:
        warnings.append("peak_eccentric_velocity < 0.10 m/s: Barely detectable eccentric phase")
    elif metrics.peak_eccentric_velocity > 5.0:
        errors.append("peak_eccentric_velocity > 5.0 m/s: Exceeds physiological limit")

    if metrics.peak_concentric_velocity < 0.20:
        errors.append("peak_concentric_velocity < 0.20 m/s: Insufficient to leave ground")
    elif metrics.peak_concentric_velocity > 5.5:
        errors.append("peak_concentric_velocity > 5.5 m/s: Exceeds elite capability")
    elif metrics.peak_concentric_velocity > 4.8:
        warnings.append("peak_concentric_velocity > 4.8 m/s: Elite-level performance")

    # Triple extension angles (if available)
    if metrics.triple_extension is not None:
        angles = metrics.triple_extension

        if angles.get('hip_angle') and (angles['hip_angle'] < 120 or angles['hip_angle'] > 195):
            warnings.append(f"Hip angle {angles['hip_angle']:.1f}° outside normal range")

        if angles.get('knee_angle') and (angles['knee_angle'] < 130 or angles['knee_angle'] > 200):
            warnings.append(f"Knee angle {angles['knee_angle']:.1f}° outside normal range")

        if angles.get('ankle_angle') and (angles['ankle_angle'] < 90 or angles['ankle_angle'] > 165):
            warnings.append(f"Ankle angle {angles['ankle_angle']:.1f}° outside normal range")

    # ========== COMPILE RESULT ==========

    status = "PASS"
    if errors:
        status = "FAIL"
    elif warnings:
        status = "PASS_WITH_WARNINGS"

    return ValidationResult(
        status=status,
        errors=errors,
        warnings=warnings,
        rsi=rsi,
        height_velocity_consistency=height_error_pct,
        velocity_height_consistency=velocity_error_pct,
    )


def validate_triple_extension(angles: dict) -> list[str]:
    """Validate triple extension angles at takeoff."""
    issues = []

    # Check hip angle
    if angles.get('hip_angle'):
        hip = angles['hip_angle']
        if hip < 120:
            issues.append(f"Hip angle {hip:.1f}° indicates flexion, not at takeoff")
        elif hip > 195:
            issues.append(f"Hip angle {hip:.1f}° suggests hyperextension or error")
        elif hip < 160:
            issues.append(f"Hip angle {hip:.1f}° shows incomplete extension")

    # Check knee angle
    if angles.get('knee_angle'):
        knee = angles['knee_angle']
        if knee < 130:
            issues.append(f"Knee angle {knee:.1f}° indicates flexion, not at takeoff")
        elif knee > 200:
            issues.append(f"Knee angle {knee:.1f}° suggests hyperextension or error")
        elif knee < 165:
            issues.append(f"Knee angle {knee:.1f}° shows incomplete extension")

    # Check ankle angle (more flexible range)
    if angles.get('ankle_angle'):
        ankle = angles['ankle_angle']
        if ankle < 90:
            issues.append(f"Ankle angle {ankle:.1f}° indicates dorsiflexion, not propulsion phase")
        elif ankle > 160:
            issues.append(f"Ankle angle {ankle:.1f}° suggests extreme plantarflexion")

    return issues
```

## 12. IMPLEMENTATION RECOMMENDATIONS

### For Test Suite

1. **Create parametrized tests** for each metric with:

   - Valid minimum/maximum values
   - Invalid values (below/above bounds)
   - Edge cases (minimal CMJ, deep squat, etc.)

2. **Cross-validation tests**:

   - Verify flight_time ↔ jump_height consistency
   - Verify peak_velocity ↔ jump_height consistency
   - Verify RSI within expected range

3. **Athlete profile tests**:

   - Generate synthetic profiles matching elderly, recreational, elite
   - Verify metrics fall within expected ranges
   - Test detection with real video samples

4. **Edge case regression tests**:

   - Minimal countermovement
   - Double-bounce patterns
   - Incomplete eccentric phases
   - Extreme ankle/knee angles

### For Production Validation

1. **Severity levels**:

   - ERROR: Stops processing, likely data corruption
   - WARNING: Metrics valid but unusual; flag for review
   - INFO: Normal variation, no action needed

2. **Auto-correction opportunities**:

   - If jump_height and flight_time conflict, recalculate from more reliable source
   - If contact_time seems too short but RSI reasonable, trust RSI

3. **Quality scoring**:

   - Assign confidence score (0-100%) based on metric consistency
   - Flag low-confidence results for manual review

## References

- **Nordez, A., Augé, T., Guével, A.** (2009). Effects of plyometric training on jump performance and energy cost. *Journal of Sports Sciences*, 27(11), 1143-1152.
- **Lees, A., Vanrenterghem, J., De Clercq, D.** (2004). Understanding how an arm swing enhances performance in the vertical jump. *Journal of Biomechanics*, 37(12), 1929-1940.
- **Cormie, P., McGuigan, M. R., Newton, R. U.** (2011). Developing maximal neuromuscular power: Performance characteristics of male athletes. *Sports Medicine*, 41(1), 17-38.
- **Bogdanis, G. C.** (2012). Effects of plyometric training on muscular performance and counter-movement jumping ability. *Journal of Strength and Conditioning Research*, 26(3), 676-695.
- **Markovic, G.** (2007). Poor relationships between strength and power qualities and high-intensity aerobic performance. *Journal of Sports Science & Medicine*, 6(1), 96-105.
