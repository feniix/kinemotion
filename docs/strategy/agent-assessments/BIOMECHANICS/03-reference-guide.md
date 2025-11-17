# Biomechanics Reference Guide for Developers

Quick reference for metric definitions, accuracy expectations, and validation requirements.

______________________________________________________________________

## CMJ Metrics Reference

### Jump Height

- **Definition:** Maximum vertical displacement of center-of-mass above standing position

- **Formula:** h = 0.5 *g* (t/2)² where t = flight time (seconds)

- **Accuracy:** ±2-3cm (markerless video)

- **Range:** 10-150cm (10cm = poor, 150cm = elite)

- **Unit:** Centimeters

- **Validation:** Force plate comparison shows r > 0.90

- **Key Dependency:** Accurate takeoff/landing detection

- **Code Validation:**

  ```python
  assert 10 < jump_height < 150, f"Jump height {jump_height}cm outside realistic range"
  ```

### Flight Time

- **Definition:** Duration from takeoff (toe leaves ground) to landing (foot returns)

- **Accuracy:** ±30ms (frame rate dependent, 30fps = ±33ms)

- **Range:** 0.2-0.8 seconds (typical: 0.4-0.6s)

- **Unit:** Seconds (milliseconds in output)

- **Validation:** Compare takeoff/landing frame consistency

- **Code Validation:**

  ```python
  assert 0.2 < flight_time < 0.8, f"Flight time {flight_time}s unrealistic"
  ```

### Ground Contact Time (CMJ)

- **Definition:** Duration from landing impact to takeoff

- **Accuracy:** ±20-30ms

- **Range:** 0.3-0.7 seconds

- **Unit:** Seconds

- **Validation:** Detect landing acceleration spike, verify takeoff velocity

- **Code Validation:**

  ```python
  assert 0.1 < gct < 1.0, f"CMJ GCT {gct}s outside realistic range"
  ```

### Countermovement Depth

- **Definition:** Vertical distance hip descends from standing to lowest squat point

- **Accuracy:** ±3-5cm (ICC 0.60-0.92 per research)

- **Range:** 15-100cm (15cm = very shallow, >80cm = check for error)

- **Unit:** Centimeters

- **Typical:** 30-60cm for trained athletes

- **Validation:** Anthropometry-dependent; compare to leg length

- **Code Validation:**

  ```python
  assert 15 < depth < 80, f"Depth {depth}cm; check for tracking error if >80cm"
  ```

### RSI (Reactive Strength Index)

- **Definition:** Flight time / Ground contact time (upper body only or total body variant)

- **Accuracy:** ±0.1 (relative, error propagates from GCT)

- **Range:** 0.1-4.0 (0.1 = poor, 4.0+ = impossible, flag error)

- **Typical:** 0.5-3.5 for trained athletes

- **Unit:** Dimensionless ratio

- **Validation:** Physical bounds check

- **Code Validation:**

  ```python
  rsi = flight_time / gct
  assert 0.1 < rsi < 4.0, f"RSI {rsi} outside realistic range"
  ```

______________________________________________________________________

## Triple Extension Angles Reference

### Hip Extension

- **Definition:** Angle from vertical to line connecting hip-to-knee

- **Range at Standing:** 180° (fully extended)

- **Range at Squat:** 90-100° (flexed)

- **Range at Takeoff:** 170-180° (nearly full extension)

- **Expected Change (Concentric):** ≥20° increase from squat to takeoff

- **Accuracy:** ±5° typical

- **Validation:** r > 0.85 vs marker-based systems

- **Code Validation:**

  ```python
  assert 150 < hip_angle_takeoff < 190, f"Hip angle {hip_angle_takeoff}° outside bounds"
  assert (hip_angle_takeoff - hip_angle_squat) > 20, "Hip extension < 20°, check for error"
  ```

### Knee Extension

- **Definition:** Angle at knee joint (ankle-knee-hip)

- **Range at Standing:** 180° (fully extended)

- **Range at Squat:** 90-110° (flexed)

- **Range at Takeoff:** 170-180° (nearly full extension)

- **Expected Change (Concentric):** ≥20° increase

- **Accuracy:** ±5° typical

- **Validation:** r > 0.85 vs marker-based systems

- **Code Validation:**

  ```python
  assert 150 < knee_angle_takeoff < 190, f"Knee angle {knee_angle_takeoff}° outside bounds"
  assert (knee_angle_takeoff - knee_angle_squat) > 20, "Knee extension < 20°"
  ```

### Ankle Plantarflexion (AFTER FIX)

- **Definition:** Angle at ankle joint (heel-ankle-foot_index)

- **Range at Standing/Neutral:** ~110-120° (heel elevated)

- **Range at Landing:** 80-90° (dorsiflexed, toes up)

- **Range at Takeoff:** 120-135° (plantarflexed, toes down)

- **Expected Change (Concentric):** ≥30° increase (currently 5-10°, shows bug)

- **Accuracy:** ±8-10° after fix (pending validation)

- **Validation:** PENDING foot_index visibility check

- **Code Validation (After Fix):**

  ```python
  assert 70 < ankle_angle_landing < 100, f"Landing ankle {ankle_angle_landing}° odd"
  assert 110 < ankle_angle_takeoff < 145, f"Takeoff ankle {ankle_angle_takeoff}° outside bounds"
  assert (ankle_angle_takeoff - ankle_angle_landing) > 30, "Ankle plantarflexion < 30°, check fix"
  ```

### Triple Extension Progression

- **Eccentric Phase:** All angles decrease (flexion)

- **Inflection Point:** Velocity crosses zero

- **Concentric Phase:** All angles increase (extension)

  - Hip increases ≥20°
  - Knee increases ≥20°
  - Ankle increases ≥30° (after fix)

- **Takeoff:** All angles near maximal extension

- **Test Example:**

  ```python
  def test_triple_extension_progression():
      eccentric = get_phase(video, 'eccentric')
      concentric = get_phase(video, 'concentric')

      # All angles should increase ≥20° during concentric
      assert concentric['hip_change'] >= 20, "Hip extension < 20°"
      assert concentric['knee_change'] >= 20, "Knee extension < 20°"
      assert concentric['ankle_change'] >= 30, "Ankle plantarflexion < 30°"
  ```

______________________________________________________________________

## Running Metrics Reference

### Ground Contact Time (GCT)

- **Definition:** Duration foot is in contact with ground during running step

- **Accuracy:** ±30-50ms (video-based, no published validation yet)

- **Range:** 0.10-0.60 seconds

- **Typical - Elite:** 0.15-0.25s

- **Typical - Recreational:** 0.25-0.35s

- **Typical - Heavy Runner:** 0.35-0.50s

- **Unit:** Seconds (milliseconds in output)

- **Warning Thresholds:**

  - \<0.10s: Unrealistic (elite only), check for detection error
  - > 0.60s: Definitely wrong, check algorithm

- **Accuracy Note:** ±30-50ms good for form feedback, NOT for elite performance quantification

- **Code Validation:**

  ```python
  assert 0.10 < gct < 0.60, f"GCT {gct}s outside realistic range"
  if gct < 0.15:
      warnings.append("Unusually low GCT; verify detection on video")
  ```

### Cadence

- **Definition:** Steps per minute (frequency of ground contacts)

- **Accuracy:** ±2-3 steps/min (frame rate dependent)

- **Range:** 120-220 steps/min

- **Typical - Optimal:** 160-180 steps/min

- **Typical - Elite/Distance:** 170-180+ steps/min

- **Typical - Recreational:** 160-170 steps/min

- **Unit:** Steps per minute

- **Warning Thresholds:**

  - \<120 steps/min: Too slow, unusual
  - > 220 steps/min: Unrealistic for sustained running

- **Code Validation:**

  ```python
  assert 120 < cadence < 220, f"Cadence {cadence} steps/min outside realistic range"
  if cadence < 160:
      warnings.append("Low cadence increases injury risk; consider form correction")
  ```

### Stride Length

- **Definition:** Horizontal distance traveled in one complete gait cycle (right foot to right foot contact)

- **Accuracy:** ±10-20% (without camera calibration)

- **Range:** 1.0-2.5 meters (varies by height, speed)

- **Unit:** Meters or normalized (as ratio to body height)

- **Status:** NOT RECOMMENDED for MVP (defer to Phase 2)

- **Reason:** Requires camera calibration or known reference object

- **Alternative:** Report as "relative stride" (pixels or body-length-based)

- **Code Validation (When Added):**

  ```python
  if camera_calibrated:
      assert 1.0 < stride_length < 2.5, f"Stride {stride_length}m outside typical range"
  else:
      stride_relative = stride_length / height  # Report as multiplier
  ```

### Landing Pattern Classification

- **Definition:** Classification of foot strike type

- **Categories:** Heel strike, Midfoot strike, Forefoot strike

- **Accuracy:** 80-90% with trained classifier

- **Unit:** Categorical label + confidence percentage

- **Biomechanical Significance:**

  - Heel strike: More impact shock, common in recreational runners
  - Midfoot strike: Balanced, efficient
  - Forefoot strike: Sprint/elite runners, higher calf load

- **Warning Thresholds:**

  - Confidence \<70%: Mark as "ambiguous", requires human review

- **Code Validation:**

  ```python
  landing_type, confidence = classify_landing_pattern(frame)
  if confidence < 0.70:
      warnings.append(f"Landing pattern ambiguous ({confidence:.0%}), manual review recommended")
  ```

______________________________________________________________________

## Phase Detection Reference

### CMJ Phases (Backward Search Algorithm)

**Phase 1: Peak (Starting Point)**

- Highest hip position
- Velocity = 0 (or near-zero)
- All joints extended

**Phase 2: Takeoff (Search Backward)**

- Point where vertical velocity crosses zero going upward
- Occurs during concentric phase
- All joints nearly at maximum extension
- GCT window: 300-400ms before peak

**Phase 3: Lowest Point (Continue Backward)**

- Lowest hip position during countermovement
- Vertical velocity = 0 (inflection point)
- Hip/knee/ankle at minimum angles (maximum flexion)
- Occurs 300-600ms before takeoff

**Phase 4: Start (Continue Backward)**

- Movement starts from standing position
- Hip height stable
- All joints at standing extension
- Looking for first change in hip position

**Phase 5: Landing (Search Forward from Peak)**

- Point where hip returns to near standing height
- Vertical velocity crosses zero going downward
- Used to detect landing impact

**Code Reference:**

```python
def detect_cmj_phases(video_frames, hip_positions):
    """
    Returns: {
        'start': frame_index,           # Standing ready
        'lowest': frame_index,          # Lowest squat point
        'takeoff': frame_index,         # Push-off point
        'peak': frame_index,            # Highest point
        'landing': frame_index,         # Return to ground
        'eccentric_duration': ms,
        'flight_duration': ms,
        'gct': ms
    }
    """
```

### Running Phases (Forward Detection)

**Phase 1: Stance (Foot in Contact)**

- Foot on ground
- Vertical position descending then ascending
- Force production phase

**Phase 2: Flight (Foot in Air)**

- Foot off ground
- Both feet in air briefly
- Recovery phase

**Phase 3: Ground Contact Detection**

- Typically: Peak downward velocity + vertical position minimum
- Alternative: Acceleration spike during landing

**Code Reference:**

```python
def detect_gait_phases(video_frames, foot_positions, vertical_velocity):
    """
    Returns: [
        {'stance_start': frame, 'stance_end': frame, 'duration_ms': ms},
        {'flight_start': frame, 'flight_end': frame, 'duration_ms': ms},
        ...
    ]
    GCT = duration of stance phases
    Flight time = duration of flight phases
    Cadence = frequency of stance starts per minute
    """
```

______________________________________________________________________

## Physiological Bounds (Quality Control)

### CMJ Metric Bounds

```python
PHYSIOLOGICAL_BOUNDS = {
    'jump_height': {'min': 10, 'max': 150, 'unit': 'cm', 'warning': 'Flag if >80cm'},
    'flight_time': {'min': 0.2, 'max': 0.8, 'unit': 's'},
    'gct': {'min': 0.1, 'max': 1.0, 'unit': 's'},
    'rsi': {'min': 0.1, 'max': 4.0, 'unit': 'ratio'},
    'countermovement_depth': {'min': 15, 'max': 80, 'unit': 'cm', 'warning': 'Flag if >80cm'},
    'hip_angle': {'min': 150, 'max': 190, 'unit': 'degrees'},
    'knee_angle': {'min': 150, 'max': 190, 'unit': 'degrees'},
    'ankle_angle': {'min': 70, 'max': 145, 'unit': 'degrees'},
    'hip_extension_change': {'min': 20, 'max': 100, 'unit': 'degrees', 'phase': 'concentric'},
    'knee_extension_change': {'min': 20, 'max': 100, 'unit': 'degrees', 'phase': 'concentric'},
    'ankle_plantarflexion_change': {'min': 30, 'max': 100, 'unit': 'degrees', 'phase': 'concentric'},
}
```

### Running Metric Bounds

```python
RUNNING_BOUNDS = {
    'gct': {'min': 0.10, 'max': 0.60, 'unit': 's', 'warning': 'Video-only accuracy ±30-50ms'},
    'cadence': {'min': 120, 'max': 220, 'unit': 'steps/min'},
    'landing_confidence': {'min': 0.70, 'max': 1.0, 'unit': 'fraction', 'warning': '<0.70 review recommended'},
}
```

______________________________________________________________________

## Accuracy Statement Template

**For CMJ Analysis:**

```
"Kinemotion provides video-based countermovement jump (CMJ) analysis with
±2-3cm accuracy for jump height, ±30ms accuracy for flight time, and ±5-10°
accuracy for joint angles (hip, knee, ankle). Best performance with 60fps+
video, clear lateral view, and good lighting. Suitable for coaching feedback
and performance trending, not for laboratory research requiring marker-based
motion capture accuracy."
```

**For Running Analysis:**

```
"Kinemotion provides running gait analysis including ground contact time
(±30-50ms), cadence (±2-3 steps/min), and landing pattern classification
(80-90% accuracy). Video-based measurements are suitable for form feedback
and injury prevention guidance. Ground contact time accuracy is 2-3x less
precise than force-plate or IMU methods; use for trending and coaching
feedback, not for elite performance quantification."
```

**For Full Platform:**

```
"Kinemotion is an accessible, video-based biomechanics platform providing
coaching-grade analysis of athletic movements. Metrics are validated for
accuracy and appropriate for form feedback, performance trending, and
injury prevention guidance. All metrics include confidence bounds and
warning thresholds to flag suspicious data."
```

______________________________________________________________________

## Development Checklist

### Before Deploying Ankle Angle Fix

- [ ] Test on 10 real CMJ videos
- [ ] Verify foot_index visibility > 70% during plantarflexion
- [ ] Confirm ankle angle increases ≥30° during concentric
- [ ] Update tests for 30°+ angle change validation
- [ ] Document fallback strategy if visibility drops

### Before Deploying Running GCT

- [ ] Test on 5-10 real running videos (various cadences)
- [ ] Document accuracy achieved (±ms)
- [ ] Test on different ground surfaces (treadmill, track, outdoor)
- [ ] Publish accuracy statement in API docs
- [ ] Set customer expectation (±30-50ms, not force plate grade)

### Before Market Launch

- [ ] All metrics have physiological bounds implemented
- [ ] All outputs include accuracy/confidence information
- [ ] Documentation includes accuracy statements
- [ ] Test coverage on core algorithms >85%
- [ ] Real video samples validated for each sport

### Before Partnership/Licensing

- [ ] Validation study completed (vs force plate or marker system)
- [ ] Technical report published with accuracy findings
- [ ] Biomechanics expert review of all metrics
- [ ] Accuracy statements reviewed by independent party

______________________________________________________________________

**Last Updated:** November 17, 2025
**For Questions:** Contact Biomechanics Specialist
