# Wall Ball No-Rep Detection - Feature Implementation Plan

**Status**: 📋 PLANNED - Future Feature
**Created**: 2025-11-07
**Feasibility**: MODERATE-CHALLENGING ✅
**Estimated Effort**: 3-4 weeks full implementation

______________________________________________________________________

## Executive Summary

This document outlines the implementation plan for adding **HYROX Wall Ball no-rep detection** to kinemotion. Wall ball is one of eight workout stations in HYROX races, requiring athletes to complete 100 wall ball shots with specific standards:

- **Squat depth**: Hip crease must go below knee
- **Ball height**: Must hit target (3m men / 2.7m women)
- **No resting**: Ball cannot rest on ground between reps

**Verdict**: Implementation is **feasible** with kinemotion's existing architecture. The project already has proven pose tracking (MediaPipe), squat analysis (CMJ), and phase detection algorithms that can be extended for wall ball analysis.

**Key insight**: Use **45-degree camera angle** instead of pure lateral view for superior ball tracking while using **joint angles** for camera-agnostic squat depth validation.

______________________________________________________________________

## Table of Contents

1. [Core Objective: Rep Counting & Validation Pipeline](#1-core-objective-rep-counting--validation-pipeline)
1. [Wall Ball Exercise Standards](#2-wall-ball-exercise-standards)
1. [Technical Feasibility Analysis](#3-technical-feasibility-analysis)
1. [Camera Setup - 45-Degree Angle Advantage](#4-camera-setup---45-degree-angle-advantage)
1. [Proposed Architecture](#5-proposed-architecture)
1. [Implementation Phases](#6-implementation-phases)
1. [Technical Challenges & Mitigation](#7-technical-challenges--mitigation)
1. [Testing Strategy](#8-testing-strategy)
1. [Research References](#9-research-references)
1. [Future Enhancements](#10-future-enhancements)
1. [Conclusion](#11-conclusion)

______________________________________________________________________

## 1. Core Objective: Rep Counting & Validation Pipeline

### 1.1 The Problem

**Input**: Video containing 10-100 wall ball reps (typical range, algorithm handles any number)

**Objective**:

1. **Identify** each attempted rep (segment video into individual reps)
1. **Validate** each rep against HYROX standards
1. **Report** which reps are valid and which are no-reps (with reasons)

**Formula**: `valid_reps = attempted_reps - no_reps`

### 1.2 Two-Stage Pipeline

The implementation uses a **detection-then-validation** pipeline:

```text
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT VIDEO                              │
│                    (10-100 wall ball reps)                       │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    STAGE 1: REP DETECTION                        │
│                                                                  │
│  • Extract pose landmarks per frame (MediaPipe)                 │
│  • State machine detects rep boundaries                         │
│  • Segment video into individual attempts                       │
│                                                                  │
│  Output: List of rep segments                                   │
│    - Rep 1: frames 0-89 (timestamp 0.0s - 3.0s)                │
│    - Rep 2: frames 90-185 (timestamp 3.0s - 6.2s)              │
│    - Rep 3: frames 186-278 (timestamp 6.2s - 9.3s)             │
│    - ...                                                        │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                   STAGE 2: REP VALIDATION                        │
│                                                                  │
│  For each detected rep:                                         │
│    ✓ Validate squat depth (knee angle < 90°)                   │
│    ✓ Validate ball height (peak ≥ target)                      │
│    ✓ Validate no resting (ball stationary on ground)           │
│                                                                  │
│  Output: Per-rep results                                        │
│    - Rep 1: VALID (all checks passed)                          │
│    - Rep 2: NO-REP (squat depth insufficient: 95° vs 90°)     │
│    - Rep 3: VALID                                               │
│    - Rep 4: NO-REP (ball height: 2.8m vs 3.0m target)         │
│    - ...                                                        │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FINAL OUTPUT                                │
│                                                                  │
│  Summary:                                                        │
│    • Total attempted: 50 reps                                   │
│    • Valid reps: 47                                             │
│    • No-reps: 3                                                 │
│    • Violation breakdown:                                       │
│        - Squat depth: 2 violations                              │
│        - Ball height: 1 violation                               │
│        - Ball resting: 0 violations                             │
│                                                                  │
│  Per-rep details: [see JSON output for complete data]          │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Stage 1: Rep Detection (State Machine)

**Approach**: State machine tracks rep phases to identify complete cycles

**Rep phases** (inspired by YOLOv8 AI Gym exercise counters):

```text
STANDING → DESCENDING → BOTTOM → ASCENDING → THROWING → FLIGHT → CATCHING → RECOVERY → STANDING
    ↑___________________________________________________________________________________|
                                (one complete rep)
```

**State transitions** based on:

- **Hip vertical position**: Detect squat descent/ascent
- **Hip vertical velocity**: Detect direction changes (descent ↔ ascent)
- **Hand height**: Detect throw (hands up) and catch (hands down)
- **Ball position**: Detect flight phase

**Rep boundary detection**:

- **Rep start**: Transition from STANDING to DESCENDING
- **Rep end**: Transition from RECOVERY to STANDING (completion of next rep)
- **Edge cases**:
  - Partial rep at video start → ignore (need complete cycle)
  - Partial rep at video end → ignore
  - Abandoned rep (athlete stops mid-motion) → count as attempted, mark violation

**Output data structure**:

```python
@dataclass
class RepSegment:
    """Single detected rep with frame boundaries"""
    rep_number: int           # 1, 2, 3, ...
    start_frame: int          # First frame of rep
    end_frame: int            # Last frame of rep
    start_time: float         # Timestamp in seconds
    end_time: float           # Timestamp in seconds
    duration: float           # Duration in seconds
    phases: List[PhaseInfo]   # Detected phases with frame ranges
```

**Algorithm pseudocode**:

```python
def detect_reps(landmarks_sequence: List[PoseLandmarks], fps: float) -> List[RepSegment]:
    """
    Detect rep boundaries using state machine.

    Returns list of detected reps with frame ranges.
    """
    state = WallBallState.STANDING
    current_rep_start = None
    detected_reps = []
    rep_number = 0

    for frame_idx, landmarks in enumerate(landmarks_sequence):
        # Calculate features
        hip_y = landmarks[HIP].y
        hip_velocity = compute_velocity(hip_positions, frame_idx)
        hand_y = landmarks[WRIST].y

        # State transitions
        if state == STANDING and hip_velocity > descent_threshold:
            # Start new rep
            state = DESCENDING
            current_rep_start = frame_idx

        elif state == DESCENDING and hip_y > squat_depth_threshold:
            state = BOTTOM

        elif state == BOTTOM and hip_velocity < -ascent_threshold:
            state = ASCENDING

        elif state == ASCENDING and hand_y < throw_threshold:
            state = THROWING

        # ... more transitions ...

        elif state == RECOVERY and hip_velocity == 0 and hands_at_rest:
            # Complete rep
            state = STANDING
            rep_number += 1
            detected_reps.append(RepSegment(
                rep_number=rep_number,
                start_frame=current_rep_start,
                end_frame=frame_idx,
                start_time=current_rep_start / fps,
                end_time=frame_idx / fps,
                duration=(frame_idx - current_rep_start) / fps
            ))
            current_rep_start = None

    return detected_reps
```

### 1.4 Stage 2: Rep Validation (Independent Checkers)

**Approach**: For each detected rep, run three independent validators

**Validation is per-rep**, not global:

- Each rep is evaluated independently
- One rep can have multiple violations (still counts as single no-rep)
- Violations are tracked with specific details (e.g., actual angle vs threshold)

#### Validator 1: Squat Depth

```python
def validate_squat_depth(
    rep_segment: RepSegment,
    landmarks_sequence: List[PoseLandmarks]
) -> Tuple[bool, Optional[ViolationDetails]]:
    """
    Check if hip crease went below knee during bottom phase.
    Uses knee angle (hip-knee-ankle) < 90°.
    """
    # Find BOTTOM phase in rep
    bottom_frame = find_phase(rep_segment, WallBallPhase.BOTTOM)

    # Get landmarks at bottom
    hip = landmarks_sequence[bottom_frame][HIP]
    knee = landmarks_sequence[bottom_frame][KNEE]
    ankle = landmarks_sequence[bottom_frame][ANKLE]

    # Calculate knee angle
    angle = calculate_joint_angle(hip, knee, ankle)
    threshold = 90.0

    is_valid = angle < threshold

    if not is_valid:
        violation = ViolationDetails(
            type="squat_depth",
            frame=bottom_frame,
            details={"knee_angle": angle, "threshold": threshold}
        )
        return False, violation

    return True, None
```

#### Validator 2: Ball Height

```python
def validate_ball_height(
    rep_segment: RepSegment,
    ball_trajectory: List[BallPosition],
    target_height_pixels: float
) -> Tuple[bool, Optional[ViolationDetails]]:
    """
    Check if ball reached target height during flight phase.
    """
    # Find FLIGHT phase trajectory
    flight_positions = filter_by_phase(ball_trajectory, WallBallPhase.FLIGHT)

    # Find peak (minimum y-coordinate in image space)
    peak_position = min(flight_positions, key=lambda p: p.y)

    # Check if peak reached target (with tolerance)
    tolerance = 10  # pixels
    is_valid = peak_position.y <= (target_height_pixels + tolerance)

    if not is_valid:
        violation = ViolationDetails(
            type="ball_height",
            frame=peak_position.frame,
            details={
                "peak_y": peak_position.y,
                "target_y": target_height_pixels,
                "difference_pixels": peak_position.y - target_height_pixels
            }
        )
        return False, violation

    return True, None
```

#### Validator 3: Ball Resting

```python
def validate_no_resting(
    rep_segment: RepSegment,
    ball_trajectory: List[BallPosition],
    ground_y: float
) -> Tuple[bool, Optional[ViolationDetails]]:
    """
    Check if ball rested on ground during recovery phase.
    Ball is "resting" if: low position + stationary + duration > threshold.
    """
    # Find RECOVERY phase positions
    recovery_positions = filter_by_phase(ball_trajectory, WallBallPhase.RECOVERY)

    # Find low, stationary sequences
    resting_sequences = find_stationary_sequences(
        recovery_positions,
        height_threshold=ground_y - 50,  # pixels above ground
        movement_threshold=5,  # max pixels movement
        duration_threshold=1.5  # seconds
    )

    if resting_sequences:
        violation = ViolationDetails(
            type="ball_resting",
            frame=resting_sequences[0].start_frame,
            details={
                "duration_seconds": resting_sequences[0].duration,
                "threshold_seconds": 1.5
            }
        )
        return False, violation

    return True, None
```

#### Aggregate validation results

```python
def validate_rep(
    rep_segment: RepSegment,
    landmarks_sequence: List[PoseLandmarks],
    ball_trajectory: List[BallPosition],
    target_height: float,
    ground_y: float
) -> WallBallRep:
    """
    Run all validators on a single rep.
    """
    violations = []

    # Check squat depth
    depth_valid, depth_violation = validate_squat_depth(rep_segment, landmarks_sequence)
    if not depth_valid:
        violations.append(depth_violation)

    # Check ball height
    height_valid, height_violation = validate_ball_height(
        rep_segment, ball_trajectory, target_height
    )
    if not height_valid:
        violations.append(height_violation)

    # Check resting
    resting_valid, resting_violation = validate_no_resting(
        rep_segment, ball_trajectory, ground_y
    )
    if not resting_valid:
        violations.append(resting_violation)

    # Rep is valid only if all checks passed
    is_valid = len(violations) == 0

    return WallBallRep(
        rep_number=rep_segment.rep_number,
        start_frame=rep_segment.start_frame,
        end_frame=rep_segment.end_frame,
        duration=rep_segment.duration,
        is_valid=is_valid,
        violations=violations
    )
```

### 1.5 Output Structure

**Hierarchical output** (JSON + CLI summary):

```json
{
  "summary": {
    "total_attempted_reps": 50,
    "valid_reps": 47,
    "no_reps": 3,
    "completion_percentage": 94.0,
    "total_duration_seconds": 156.3,
    "avg_time_per_rep": 3.13,
    "violation_breakdown": {
      "squat_depth": 2,
      "ball_height": 1,
      "ball_resting": 0
    }
  },
  "reps": [
    {
      "rep_number": 1,
      "start_frame": 0,
      "end_frame": 89,
      "start_time": 0.0,
      "end_time": 3.0,
      "duration": 3.0,
      "is_valid": true,
      "violations": [],
      "metrics": {
        "min_knee_angle": 85.3,
        "ball_peak_y": 245,
        "ball_peak_height_m": 3.1
      }
    },
    {
      "rep_number": 2,
      "start_frame": 90,
      "end_frame": 185,
      "start_time": 3.0,
      "end_time": 6.2,
      "duration": 3.2,
      "is_valid": false,
      "violations": [
        {
          "type": "squat_depth",
          "frame": 135,
          "timestamp": 4.5,
          "details": {
            "knee_angle": 95.2,
            "threshold": 90.0,
            "difference": 5.2
          }
        }
      ],
      "metrics": {
        "min_knee_angle": 95.2,
        "ball_peak_y": 240,
        "ball_peak_height_m": 3.05
      }
    },
    {
      "rep_number": 3,
      "start_frame": 186,
      "end_frame": 278,
      "start_time": 6.2,
      "end_time": 9.3,
      "duration": 3.1,
      "is_valid": true,
      "violations": [],
      "metrics": {
        "min_knee_angle": 82.1,
        "ball_peak_y": 238,
        "ball_peak_height_m": 3.15
      }
    }
    // ... more reps ...
  ],
  "calibration": {
    "pixels_per_meter": 100.5,
    "target_height_m": 3.0,
    "target_height_pixels": 301,
    "calibration_method": "target_based"
  }
}
```

**CLI output** (human-readable):

```text
Wall Ball Analysis Complete
================================================================================

SUMMARY
  Total attempted reps: 50
  Valid reps:           47 ✓
  No-reps:              3 ✗
  Completion rate:      94.0%

  Average time per rep: 3.13s
  Total duration:       156.3s

VIOLATION BREAKDOWN
  Squat depth:          2 violations
  Ball height:          1 violation
  Ball resting:         0 violations

DETAILED RESULTS
  Rep  1: ✓ VALID   (3.0s) | Knee: 85.3° | Height: 3.1m
  Rep  2: ✗ NO-REP  (3.2s) | Squat depth insufficient (95.2° vs 90.0°)
  Rep  3: ✓ VALID   (3.1s) | Knee: 82.1° | Height: 3.15m
  Rep  4: ✓ VALID   (3.0s) | Knee: 87.5° | Height: 3.05m
  Rep  5: ✗ NO-REP  (3.4s) | Ball height insufficient (2.85m vs 3.0m)
  ...
  Rep 50: ✓ VALID   (3.2s) | Knee: 88.9° | Height: 3.08m

For detailed JSON output: kinemotion wallball-analyze video.mp4 --json-output results.json
For debug video: kinemotion wallball-analyze video.mp4 --output debug.mp4
```

### 1.6 Key Design Principles

1. **Separation of concerns**: Detection and validation are independent

   - Can test rep detection without validation logic
   - Can improve validators without changing detection

1. **Per-rep granularity**: Every attempted rep is identified and evaluated

   - Matches HYROX judging workflow (judge calls each rep)
   - Enables detailed performance analysis

1. **Transparent violations**: Clear reasons for no-reps

   - Athletes know exactly what to fix
   - Coaches can analyze patterns (e.g., "depth violations increase with fatigue")

1. **Extensible validators**: Easy to add new standards

   - Each validator is independent function
   - Can add timing requirements, tempo, etc. in future

1. **Testable components**: Clear interfaces enable unit testing

   - Mock pose landmarks to test state machine
   - Mock rep segments to test validators
   - Test aggregation separately

______________________________________________________________________

## 2. Wall Ball Exercise Standards

### HYROX Competition Requirements

**Reps**: 100 wall ball shots (all divisions)

**Equipment**:

- Men: 6kg (14 lbs) or 9kg (20 lbs) ball
- Women: 4kg (9 lbs) or 6kg (14 lbs) ball

**Target Height**:

- Men: 3.0 meters (10 feet)
- Women: 2.7 meters (9 feet)

### No-Rep Violations

A rep does **not count** if:

1. **Insufficient squat depth**: Hip crease doesn't go below top of knee
1. **Target miss**: Ball doesn't reach target height on wall
1. **Ball resting**: Ball rests on ground between reps (not allowed)

**Judge requirement**: One judge per athlete to call no-reps in real-time

______________________________________________________________________

## 3. Technical Feasibility Analysis

### 3.1 Squat Depth Validation - EASY (2-3 days)

**Challenge**: Detect if hip crease goes below knee

**Approach**: Use joint angle calculation (NOT vertical position)

**Rationale**:

- Kinemotion already has `cmj/joint_angles.py` with `calculate_joint_angle()`
- Joint angles are **camera-agnostic** (work at any angle, including 45°)
- More robust than vertical position checks
- Standard approach in fitness tracking apps

**Implementation**:

```python
from kinemotion.cmj.joint_angles import calculate_joint_angle

def validate_squat_depth(
    hip: PoseLandmark,
    knee: PoseLandmark,
    ankle: PoseLandmark,
    threshold_degrees: float = 90.0
) -> tuple[bool, float]:
    """
    Validate squat depth using knee angle.
    Works with any camera angle (lateral, 45°, etc.)

    Returns:
        (is_valid, angle_degrees)
    """
    angle = calculate_joint_angle(hip, knee, ankle)
    is_valid = angle < threshold_degrees
    return is_valid, angle
```

**Why joint angles > vertical positions**:

- ✅ No parallax errors from camera angle
- ✅ Measures actual joint flexion (biomechanically correct)
- ✅ Works with varied camera positioning
- ✅ Reuses existing kinemotion code

**Confidence**: HIGH - proven technology in kinemotion CMJ module

### 3.2 Ball Resting Detection - MODERATE (2 days)

**Challenge**: Detect if ball rests on ground between reps

**Approach**: Temporal tracking with position + velocity analysis

**Algorithm**:

1. Track ball position over time (using ball tracking from 2.3)
1. Detect low vertical position (below waist height)
1. Check for minimal movement (stationary threshold)
1. Measure duration (>1-2 seconds = violation)

**Similar to**: Phase detection logic in `cmj/analysis.py` and `dropjump/analysis.py`

**Pseudo-code**:

```python
def detect_ball_resting(
    ball_positions: list,
    waist_height: float,
    stationary_threshold: float = 5,  # pixels
    duration_threshold: float = 1.5   # seconds
) -> bool:
    """
    Detect if ball is resting on ground.

    Args:
        ball_positions: List of (x, y, timestamp) tuples
        waist_height: Y-coordinate of athlete's waist
        stationary_threshold: Max movement in pixels to be "stationary"
        duration_threshold: Min duration in seconds to be "resting"
    """
    low_positions = [p for p in ball_positions if p.y > waist_height]

    if not low_positions:
        return False

    # Check if positions are stationary
    position_changes = [
        distance(low_positions[i], low_positions[i+1])
        for i in range(len(low_positions) - 1)
    ]

    if max(position_changes) > stationary_threshold:
        return False  # Ball is moving

    # Check duration
    duration = low_positions[-1].timestamp - low_positions[0].timestamp
    return duration > duration_threshold
```

**Confidence**: MEDIUM-HIGH - uses proven phase detection patterns

### 3.3 Ball Height Validation - HARD (5-7 days)

**Challenge**: Track ball through throw and validate it hits target height

**Sub-challenges**:

1. **Ball tracking**: Detect and track ball position (pose estimation doesn't include balls)
1. **Trajectory analysis**: Detect peak height per rep
1. **Calibration**: Convert pixel coordinates to real-world meters

#### 3.3.1 Ball Tracking

**Approach**: Hybrid method combining pose tracking with color detection

**Research findings** (from OpenCV ball tracking literature):

- Color-based HSV segmentation: Simple, fast, lighting-dependent
- YOLO object detection: Accurate but requires training data + model dependency
- **Hybrid (chosen)**: Use pose to guide search, HSV for detection

**Implementation**:

```python
def detect_ball_hsv(
    frame: np.ndarray,
    athlete_landmarks: PoseLandmarks,
    ball_color_range: tuple[HSVRange, HSVRange] = None
) -> Optional[BallPosition]:
    """
    Detect ball using HSV color segmentation with pose-guided ROI.

    Args:
        frame: Video frame (BGR)
        athlete_landmarks: MediaPipe pose landmarks
        ball_color_range: Optional (lower_hsv, upper_hsv) for custom ball colors

    Returns:
        Ball position (x, y) or None if not detected
    """
    # Step 1: Define search region using pose (reduce false positives)
    wrist = athlete_landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    shoulder = athlete_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]

    # ROI: Expand from upper body region (where ball should be)
    roi_bounds = expand_roi(wrist, shoulder, expansion_factor=2.0)
    roi = frame[roi_bounds.top:roi_bounds.bottom, roi_bounds.left:roi_bounds.right]

    # Step 2: HSV color segmentation
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Default: dark colors (common medicine ball colors)
    if ball_color_range is None:
        lower_hsv = np.array([0, 0, 0])      # Black/dark gray
        upper_hsv = np.array([180, 255, 80])
    else:
        lower_hsv, upper_hsv = ball_color_range

    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

    # Step 3: Find circular contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Find largest circular contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Circularity check (balls are circular)
    area = cv2.contourArea(largest_contour)
    perimeter = cv2.arcLength(largest_contour, True)
    if perimeter == 0:
        return None

    circularity = 4 * np.pi * area / (perimeter ** 2)
    if circularity < 0.7:  # Not circular enough
        return None

    # Get center
    M = cv2.moments(largest_contour)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"]) + roi_bounds.left
    cy = int(M["m01"] / M["m00"]) + roi_bounds.top

    return BallPosition(x=cx, y=cy, frame=frame_number)
```

**Advantages of hybrid approach**:

- Pose-guided ROI reduces search space → faster, fewer false positives
- HSV segmentation is simple, no extra models needed
- Works with different ball colors (configurable)

**Limitations**:

- Sensitive to lighting conditions
- Requires user calibration for non-standard ball colors
- May struggle with motion blur

**Mitigation**:

- Temporal smoothing (like `core/smoothing.py`)
- Adaptive thresholding
- User-configurable HSV ranges (provide presets for common ball colors)

#### 3.3.2 Trajectory Analysis

**Goal**: Detect peak height of ball per rep

**Approach**: Position buffering with peak detection

```python
from collections import deque

class BallTrajectoryAnalyzer:
    """Track ball trajectory and detect peaks"""

    def __init__(self, buffer_size: int = 30):
        self.positions = deque(maxlen=buffer_size)  # ~1 second at 30fps

    def add_position(self, position: BallPosition) -> None:
        """Add ball position to trajectory buffer"""
        self.positions.append(position)

    def detect_peak(self) -> Optional[float]:
        """
        Detect if trajectory contains a peak (ball reached apex).

        Returns:
            Peak height (y-coordinate) or None
        """
        if len(self.positions) < 10:
            return None

        # Find local minimum in y-coordinates (peak = lowest y in image coords)
        y_coords = [p.y for p in self.positions]

        # Simple peak detection: find point lower than both neighbors
        for i in range(1, len(y_coords) - 1):
            if y_coords[i] < y_coords[i-1] and y_coords[i] < y_coords[i+1]:
                return y_coords[i]  # Peak detected

        return None
```

**Advanced approach** (optional enhancement):

- Parabolic curve fitting (balls follow parabolic trajectory)
- Velocity-based detection (velocity crosses zero at peak)

#### 3.3.3 Camera Calibration

**Challenge**: Convert pixel coordinates to real-world meters

**Approach**: Reference-based calibration (similar to force plate height calibration)

**Options**:

**Option 1: Wall target as reference** (preferred for 45° angle)

```python
def calibrate_from_target(
    target_pixel_y: int,
    target_real_height_m: float = 3.0,  # Men's target
    ground_pixel_y: int = None
) -> float:
    """
    Calculate pixels-per-meter using known target height.

    Args:
        target_pixel_y: Y-coordinate of target in video
        target_real_height_m: Known target height in meters
        ground_pixel_y: Y-coordinate of ground (if None, use frame bottom)

    Returns:
        pixels_per_meter: Conversion factor
    """
    if ground_pixel_y is None:
        ground_pixel_y = frame_height  # Bottom of frame

    pixel_height = ground_pixel_y - target_pixel_y
    pixels_per_meter = pixel_height / target_real_height_m

    return pixels_per_meter
```

**Option 2: Athlete height as reference** (fallback)

```python
def calibrate_from_athlete(
    athlete_landmarks: PoseLandmarks,
    athlete_height_m: float
) -> float:
    """Calculate pixels-per-meter using athlete's known height"""
    head = athlete_landmarks[mp_pose.PoseLandmark.NOSE]
    ankle = athlete_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]

    pixel_height = ankle.y - head.y
    pixels_per_meter = pixel_height / athlete_height_m

    return pixels_per_meter
```

**Height validation**:

```python
def validate_ball_height(
    ball_peak_y: int,
    target_y: int,
    tolerance_pixels: float = 10
) -> bool:
    """
    Validate if ball reached target height.

    Args:
        ball_peak_y: Peak position of ball (y-coordinate)
        target_y: Target position (y-coordinate)
        tolerance_pixels: Allowable margin

    Returns:
        True if ball reached target (ball_peak_y <= target_y + tolerance)
    """
    # In image coordinates, y increases downward
    # So peak (top) has LOWER y value
    return ball_peak_y <= (target_y + tolerance_pixels)
```

**Confidence**: MEDIUM - most complex component, requires user calibration

______________________________________________________________________

## 4. Camera Setup - 45-Degree Angle Advantage

### 4.1 Why 45° is Superior to Pure Lateral View

**Initial assumption**: Use lateral (90° side) view like CMJ analysis

**Finding**: 45-degree angle is **better** for wall ball detection

#### Comparison Table

| Detection Task        | Pure Lateral (90°)          | 45-Degree                | Winner     |
| --------------------- | --------------------------- | ------------------------ | ---------- |
| **Squat depth**       | Easy (vertical comparison)  | Easy (joint angle)       | **Tie** ✅ |
| **Ball tracking**     | Hard (heavy occlusion)      | Easy (clear visibility)  | **45°** ✅ |
| **Target height**     | Indirect (calibration only) | Direct (see target hit)  | **45°** ✅ |
| **Ball resting**      | Moderate (feet may hide)    | Easy (clear ground view) | **45°** ✅ |
| **Setup flexibility** | Strict positioning          | Forgiving                | **45°** ✅ |

#### Result: 45° wins 4/5 categories

### 4.2 45° Angle Advantages

#### **1. Ball Visibility** (Critical)

- **Pure lateral**: Ball hidden behind athlete's torso/arms during most of motion
- **45-degree**: Clear line of sight throughout catch → squat → throw trajectory
- Less occlusion = more reliable tracking

#### **2. Target Visibility** (Major benefit)

- Can see **wall target marker** in frame
- Enables visual confirmation of ball hitting target
- Could use computer vision on target itself (detect ball-target intersection)
- Pure lateral: wall is perpendicular to camera, target invisible

#### **3. Ground Plane Visibility**

- Clear view of floor for ball resting detection
- Better spatial awareness of ball position

#### **4. Practical Setup**

- Matches real-world HYROX gym setup (camera in corner)
- More forgiving of positioning errors
- Easier to frame athlete + wall + ground in single shot

### 4.3 Solving the Parallax Problem

**Issue**: At 45°, hip/knee vertical positions have parallax error (depth from camera affects 2D projection)

**Solution**: Use **joint angles** instead of **vertical positions**

**Why this works**:

- Joint angles are camera-angle agnostic
- Measures actual biomechanical flexion (more accurate)
- Already implemented in `cmj/joint_angles.py`
- Standard approach in fitness apps

**Comparison**:

```python
# ❌ OLD: Vertical position (lateral view only)
def validate_squat_lateral(hip, knee):
    return hip.y > knee.y  # Fails at 45° due to parallax

# ✅ NEW: Joint angle (any camera angle)
def validate_squat_angle(hip, knee, ankle):
    angle = calculate_joint_angle(hip, knee, ankle)
    return angle < 90  # Works at any angle
```

### 4.4 Recommended Camera Setup

```text
Camera position: 45-degree angle from wall
Distance: 3-5 meters from athlete
Height: Waist level (capture full squat to overhead throw)
Frame composition:
  - Athlete's full body (head to feet)
  - Wall target visible in upper frame
  - Ground plane visible in lower frame
```

**Diagram**:

```text
        Wall
         |
      Target ● (visible in frame)
         |
         |
    Athlete 🧍 (side-front view)
         ╱
        ╱
       ╱ 45°
      📷 Camera
```

**Frame example**:

```text
┌─────────────────────────┐
│   Wall  [●Target]       │  ← Target visible
│                         │
│        🧍              │  ← Athlete (side-front view)
│       /│\              │  ← Ball visible during throw
│       / \              │
│    ●──────────         │  ← Ball visible on ground
└─────────────────────────┘
```

______________________________________________________________________

## 5. Proposed Architecture

### 5.1 Module Structure

Following kinemotion patterns (sibling to `cmj/` and `dropjump/`):

```text
src/kinemotion/wallball/
├── __init__.py              # Module exports
├── cli.py                   # CLI command: kinemotion wallball-analyze
├── analysis.py              # Rep detection, phase detection
├── ball_tracking.py         # Ball detection (HSV + pose-guided ROI)
├── validation.py            # No-rep validation logic
├── calibration.py           # Pixel-to-meter conversion
├── metrics.py               # WallBallMetrics dataclass
└── debug_overlay.py         # Visualization renderer

tests/wallball/
├── __init__.py
├── test_analysis.py         # Rep detection tests
├── test_ball_tracking.py    # Ball detection tests
├── test_validation.py       # No-rep logic tests
├── test_calibration.py      # Calibration tests
├── test_metrics.py          # Metrics serialization tests
└── fixtures/                # Test videos
    ├── good_reps.mp4
    ├── depth_norep.mp4
    ├── height_norep.mp4
    └── resting_norep.mp4

docs/guides/
└── wallball-guide.md        # User guide

docs/reference/
└── wallball-standards.md    # HYROX standards reference
```

### 5.2 Key Classes and Functions

#### `metrics.py`

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class WallBallViolation:
    """Single no-rep violation"""
    frame: int
    timestamp: float  # seconds
    violation_type: str  # "squat_depth", "ball_height", "ball_resting"
    details: dict  # e.g., {"knee_angle": 95.0, "threshold": 90.0}

    def to_dict(self) -> dict:
        return {
            "frame": int(self.frame),
            "timestamp": float(self.timestamp),
            "violation_type": self.violation_type,
            "details": self.details
        }

@dataclass
class WallBallRep:
    """Single wall ball rep"""
    rep_number: int
    start_frame: int
    end_frame: int
    is_valid: bool
    violations: List[WallBallViolation]
    duration: float  # seconds
    min_knee_angle: float  # degrees
    ball_peak_height: Optional[float]  # pixels or meters

    def to_dict(self) -> dict:
        return {
            "rep_number": int(self.rep_number),
            "start_frame": int(self.start_frame),
            "end_frame": int(self.end_frame),
            "is_valid": bool(self.is_valid),
            "violations": [v.to_dict() for v in self.violations],
            "duration": float(self.duration),
            "min_knee_angle": float(self.min_knee_angle),
            "ball_peak_height": float(self.ball_peak_height) if self.ball_peak_height else None
        }

@dataclass
class WallBallMetrics:
    """Complete wall ball analysis results"""
    total_reps_attempted: int
    valid_reps: int
    no_reps: int
    reps: List[WallBallRep]
    total_duration: float  # seconds
    avg_time_per_rep: float  # seconds

    # Violation breakdown
    squat_depth_violations: int
    ball_height_violations: int
    ball_resting_violations: int

    # Camera calibration
    pixels_per_meter: Optional[float]
    target_height_m: float

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict"""
        return {
            "total_reps_attempted": int(self.total_reps_attempted),
            "valid_reps": int(self.valid_reps),
            "no_reps": int(self.no_reps),
            "reps": [r.to_dict() for r in self.reps],
            "total_duration": float(self.total_duration),
            "avg_time_per_rep": float(self.avg_time_per_rep),
            "violation_breakdown": {
                "squat_depth": int(self.squat_depth_violations),
                "ball_height": int(self.ball_height_violations),
                "ball_resting": int(self.ball_resting_violations)
            },
            "calibration": {
                "pixels_per_meter": float(self.pixels_per_meter) if self.pixels_per_meter else None,
                "target_height_m": float(self.target_height_m)
            }
        }
```

#### `analysis.py`

```python
from enum import Enum
from typing import List, Tuple
import numpy as np
from kinemotion.core.pose import PoseLandmarks
from kinemotion.cmj.joint_angles import calculate_joint_angle

class WallBallPhase(Enum):
    """Wall ball rep phases"""
    STANDING = "standing"
    DESCENT = "descent"        # Lowering into squat
    BOTTOM = "bottom"          # At squat depth
    ASCENT = "ascent"          # Standing up
    THROW = "throw"            # Ball release
    FLIGHT = "flight"          # Ball in air
    CATCH = "catch"            # Ball contact
    RECOVERY = "recovery"      # Return to standing

def detect_wallball_reps(
    landmarks: List[PoseLandmarks],
    velocities: np.ndarray,
    fps: float
) -> List[Tuple[int, int]]:
    """
    Detect wall ball reps from pose landmarks.

    Args:
        landmarks: List of pose landmarks per frame
        velocities: Hip vertical velocities
        fps: Video frame rate

    Returns:
        List of (start_frame, end_frame) tuples for each rep
    """
    # Similar to CMJ detection: look for squat cycles
    # 1. Detect descent (negative velocity)
    # 2. Detect bottom (velocity crosses zero)
    # 3. Detect ascent (positive velocity)
    # 4. Detect throw (hands go up)
    # 5. Detect catch (hands come down)
    pass

def analyze_wallball_video(
    video_path: str,
    target_height_m: float = 3.0,
    squat_depth_threshold: float = 90.0,
    quality: str = "balanced"
) -> WallBallMetrics:
    """
    Main analysis function.

    Args:
        video_path: Path to video file
        target_height_m: Target height in meters (3.0 men, 2.7 women)
        squat_depth_threshold: Knee angle threshold in degrees
        quality: Auto-tuning quality preset

    Returns:
        WallBallMetrics with complete analysis
    """
    # 1. Extract pose landmarks (reuse core/pose.py)
    # 2. Detect reps
    # 3. Track ball (ball_tracking.py)
    # 4. Validate each rep (validation.py)
    # 5. Calculate metrics
    pass
```

#### `validation.py`

```python
from typing import Optional, List
import numpy as np
from kinemotion.cmj.joint_angles import calculate_joint_angle

def validate_squat_depth(
    hip_landmark,
    knee_landmark,
    ankle_landmark,
    threshold_degrees: float = 90.0
) -> Tuple[bool, float]:
    """
    Validate squat depth using knee angle.
    Works with any camera angle.

    Returns:
        (is_valid, knee_angle_degrees)
    """
    angle = calculate_joint_angle(hip_landmark, knee_landmark, ankle_landmark)
    return angle < threshold_degrees, angle

def validate_ball_height(
    ball_peak_y: float,
    target_y: float,
    tolerance_pixels: float = 10
) -> bool:
    """
    Validate if ball reached target height.

    Note: In image coordinates, y increases downward.
    Peak (top) has LOWER y value.
    """
    return ball_peak_y <= (target_y + tolerance_pixels)

def validate_no_resting(
    ball_trajectory: List[BallPosition],
    ground_threshold_y: float,
    stationary_threshold_pixels: float = 5,
    duration_threshold_seconds: float = 1.5
) -> bool:
    """
    Validate ball didn't rest on ground.

    Returns:
        True if no resting violation detected
    """
    # Check for sustained stationary position near ground
    pass

def validate_rep(
    landmarks_sequence: List[PoseLandmarks],
    ball_trajectory: List[BallPosition],
    target_y: float,
    squat_threshold: float = 90.0
) -> Tuple[bool, List[WallBallViolation]]:
    """
    Validate complete rep against all standards.

    Returns:
        (is_valid, violations_list)
    """
    violations = []

    # Check squat depth at bottom position
    # Check ball height at peak
    # Check for resting violations

    return len(violations) == 0, violations
```

#### `ball_tracking.py`

```python
import cv2
import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass

@dataclass
class HSVRange:
    """HSV color range for ball detection"""
    lower: np.ndarray  # [H, S, V] lower bounds
    upper: np.ndarray  # [H, S, V] upper bounds

# Preset color ranges for common medicine balls
BALL_COLOR_PRESETS = {
    "black": HSVRange(
        lower=np.array([0, 0, 0]),
        upper=np.array([180, 255, 80])
    ),
    "dark_gray": HSVRange(
        lower=np.array([0, 0, 50]),
        upper=np.array([180, 50, 150])
    ),
    "brown": HSVRange(
        lower=np.array([10, 100, 20]),
        upper=np.array([20, 255, 200])
    ),
    "blue": HSVRange(
        lower=np.array([100, 150, 50]),
        upper=np.array([130, 255, 255])
    )
}

@dataclass
class BallPosition:
    """Ball position in frame"""
    x: int
    y: int
    frame: int
    confidence: float  # 0-1, based on circularity and contour area

class BallTracker:
    """Track ball using HSV color detection with pose-guided ROI"""

    def __init__(
        self,
        color_preset: str = "black",
        custom_hsv_range: Optional[HSVRange] = None,
        min_circularity: float = 0.7,
        min_area: int = 100
    ):
        self.hsv_range = custom_hsv_range or BALL_COLOR_PRESETS[color_preset]
        self.min_circularity = min_circularity
        self.min_area = min_area
        self.last_position: Optional[BallPosition] = None

    def detect_ball(
        self,
        frame: np.ndarray,
        frame_number: int,
        athlete_landmarks: Optional[PoseLandmarks] = None
    ) -> Optional[BallPosition]:
        """
        Detect ball in frame using HSV color segmentation.

        Args:
            frame: Video frame (BGR)
            frame_number: Current frame number
            athlete_landmarks: Optional pose landmarks for ROI guidance

        Returns:
            BallPosition or None if not detected
        """
        # Step 1: Define ROI (if landmarks available)
        if athlete_landmarks is not None:
            roi, roi_offset = self._get_pose_guided_roi(frame, athlete_landmarks)
        else:
            roi = frame
            roi_offset = (0, 0)

        # Step 2: HSV color segmentation
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.hsv_range.lower, self.hsv_range.upper)

        # Step 3: Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Step 4: Filter by size and circularity
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue

            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue

            circularity = 4 * np.pi * area / (perimeter ** 2)
            if circularity >= self.min_circularity:
                valid_contours.append((contour, area, circularity))

        if not valid_contours:
            return None

        # Step 5: Choose largest valid contour
        best_contour, area, circularity = max(valid_contours, key=lambda x: x[1])

        # Step 6: Get center
        M = cv2.moments(best_contour)
        if M["m00"] == 0:
            return None

        cx = int(M["m10"] / M["m00"]) + roi_offset[0]
        cy = int(M["m01"] / M["m00"]) + roi_offset[1]

        # Step 7: Confidence based on circularity
        confidence = min(1.0, circularity)

        position = BallPosition(x=cx, y=cy, frame=frame_number, confidence=confidence)
        self.last_position = position

        return position

    def _get_pose_guided_roi(
        self,
        frame: np.ndarray,
        landmarks: PoseLandmarks
    ) -> Tuple[np.ndarray, Tuple[int, int]]:
        """
        Get region of interest around upper body.
        Reduces false positives by limiting search area.
        """
        # Use shoulder and wrist to define upper body region
        # Expand region to account for ball trajectory
        pass
```

#### `calibration.py`

```python
import numpy as np
from typing import Optional

def calibrate_from_target(
    target_pixel_y: int,
    ground_pixel_y: int,
    target_real_height_m: float = 3.0
) -> float:
    """
    Calculate pixels-per-meter using known target height.

    Best approach when using 45° angle (target visible in frame).
    """
    pixel_height = ground_pixel_y - target_pixel_y
    pixels_per_meter = pixel_height / target_real_height_m
    return pixels_per_meter

def calibrate_from_athlete(
    athlete_landmarks: PoseLandmarks,
    athlete_height_m: float
) -> float:
    """
    Calculate pixels-per-meter using athlete's known height.

    Fallback when target not visible or athlete height provided.
    """
    head = athlete_landmarks[mp_pose.PoseLandmark.NOSE]
    ankle = athlete_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]

    pixel_height = ankle.y - head.y
    pixels_per_meter = pixel_height / athlete_height_m

    return pixels_per_meter

def pixels_to_meters(
    pixel_value: float,
    pixels_per_meter: float
) -> float:
    """Convert pixel measurement to meters"""
    return pixel_value / pixels_per_meter

def meters_to_pixels(
    meter_value: float,
    pixels_per_meter: float
) -> float:
    """Convert meter measurement to pixels"""
    return meter_value * pixels_per_meter
```

#### `debug_overlay.py`

```python
from kinemotion.core.debug_overlay_utils import BaseDebugOverlayRenderer
import cv2

class WallBallDebugOverlayRenderer(BaseDebugOverlayRenderer):
    """Render debug overlay for wall ball analysis"""

    def render_frame(
        self,
        frame: np.ndarray,
        frame_number: int,
        landmarks: PoseLandmarks,
        ball_position: Optional[BallPosition],
        current_phase: WallBallPhase,
        rep_count: int,
        violations: List[WallBallViolation],
        target_y: int
    ) -> np.ndarray:
        """
        Render debug overlay on frame.

        Visualizations:
        - Pose skeleton
        - Ball position (circle + trajectory trail)
        - Target height line
        - Rep counter
        - Current phase
        - Violations (red highlights)
        - Knee angle (text)
        """
        # Draw pose skeleton
        self._draw_pose_skeleton(frame, landmarks)

        # Draw ball
        if ball_position:
            cv2.circle(frame, (ball_position.x, ball_position.y), 10, (0, 255, 0), -1)
            self._draw_ball_trajectory(frame)

        # Draw target line
        cv2.line(frame, (0, target_y), (frame.shape[1], target_y), (255, 255, 0), 2)
        cv2.putText(frame, "TARGET", (10, target_y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Draw rep counter
        cv2.putText(frame, f"Reps: {rep_count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Draw current phase
        cv2.putText(frame, f"Phase: {current_phase.value}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Draw violations
        if violations:
            y_offset = 110
            cv2.putText(frame, "NO-REP!", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            for violation in violations[-3:]:  # Show last 3
                y_offset += 40
                cv2.putText(frame, violation.violation_type, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        return frame
```

#### `cli.py`

```python
import click
from pathlib import Path
from kinemotion.wallball.analysis import analyze_wallball_video

@click.command(name="wallball-analyze")
@click.argument("video_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Debug video output path")
@click.option("--target-height", type=float, default=3.0,
              help="Target height in meters (3.0 men, 2.7 women)")
@click.option("--athlete-height", type=float, help="Athlete height in meters (for calibration)")
@click.option("--ball-color", type=click.Choice(["black", "dark_gray", "brown", "blue"]),
              default="black", help="Medicine ball color preset")
@click.option("--squat-threshold", type=float, default=90.0,
              help="Knee angle threshold for squat depth (degrees)")
@click.option("--quality", type=click.Choice(["fast", "balanced", "accurate"]),
              default="balanced", help="Auto-tuning quality preset")
@click.option("--json-output", type=click.Path(), help="Save metrics as JSON")
def wallball_analyze(
    video_path: str,
    output: str,
    target_height: float,
    athlete_height: float,
    ball_color: str,
    squat_threshold: float,
    quality: str,
    json_output: str
):
    """
    Analyze HYROX wall ball video for no-rep detection.

    Example:
        kinemotion wallball-analyze video.mp4 --output debug.mp4
        kinemotion wallball-analyze video.mp4 --target-height 2.7 --ball-color blue
    """
    click.echo(f"Analyzing wall ball video: {video_path}")
    click.echo(f"Target height: {target_height}m")
    click.echo(f"Quality preset: {quality}")

    # Run analysis
    metrics = analyze_wallball_video(
        video_path=video_path,
        target_height_m=target_height,
        athlete_height_m=athlete_height,
        ball_color_preset=ball_color,
        squat_depth_threshold=squat_threshold,
        quality=quality,
        debug_video_path=output
    )

    # Display results
    click.echo("\n" + "="*50)
    click.echo("WALL BALL ANALYSIS RESULTS")
    click.echo("="*50)
    click.echo(f"Total reps attempted: {metrics.total_reps_attempted}")
    click.echo(f"Valid reps: {metrics.valid_reps}")
    click.echo(f"No-reps: {metrics.no_reps}")
    click.echo(f"\nViolation breakdown:")
    click.echo(f"  - Squat depth: {metrics.squat_depth_violations}")
    click.echo(f"  - Ball height: {metrics.ball_height_violations}")
    click.echo(f"  - Ball resting: {metrics.ball_resting_violations}")
    click.echo(f"\nAverage time per rep: {metrics.avg_time_per_rep:.2f}s")

    # Save JSON
    if json_output:
        import json
        with open(json_output, 'w') as f:
            json.dump(metrics.to_dict(), f, indent=2)
        click.echo(f"\nMetrics saved to: {json_output}")

    if output:
        click.echo(f"Debug video saved to: {output}")
```

### 4.3 Integration Points

#### Register in `src/kinemotion/cli.py`

```python
from kinemotion.wallball.cli import wallball_analyze

def create_cli():
    @click.group()
    def cli():
        """Kinemotion: Video-based kinematic analysis"""
        pass

    # Existing commands
    cli.add_command(dropjump_analyze)
    cli.add_command(cmj_analyze)

    # New command
    cli.add_command(wallball_analyze)

    return cli
```

#### Export in `src/kinemotion/__init__.py`

```python
from kinemotion.wallball.analysis import analyze_wallball_video
from kinemotion.wallball.metrics import WallBallMetrics, WallBallRep, WallBallViolation

__all__ = [
    # Existing exports...
    "analyze_wallball_video",
    "WallBallMetrics",
    "WallBallRep",
    "WallBallViolation",
]
```

#### Add API function in `src/kinemotion/api.py`

```python
def process_wallball_video(
    video_path: str,
    target_height_m: float = 3.0,
    athlete_height_m: Optional[float] = None,
    ball_color_preset: str = "black",
    squat_depth_threshold: float = 90.0,
    quality: str = "balanced",
    debug_video_path: Optional[str] = None
) -> WallBallMetrics:
    """
    Python API for wall ball analysis.

    Args:
        video_path: Path to video file
        target_height_m: Target height in meters (3.0 men, 2.7 women)
        athlete_height_m: Optional athlete height for calibration
        ball_color_preset: Ball color ("black", "dark_gray", "brown", "blue")
        squat_depth_threshold: Knee angle threshold in degrees
        quality: Auto-tuning quality preset
        debug_video_path: Optional debug video output

    Returns:
        WallBallMetrics with analysis results

    Example:
        >>> from kinemotion import process_wallball_video
        >>> metrics = process_wallball_video("wallball.mp4", target_height_m=3.0)
        >>> print(f"Valid reps: {metrics.valid_reps}/{metrics.total_reps_attempted}")
    """
    from kinemotion.wallball.analysis import analyze_wallball_video

    return analyze_wallball_video(
        video_path=video_path,
        target_height_m=target_height_m,
        athlete_height_m=athlete_height_m,
        ball_color_preset=ball_color_preset,
        squat_depth_threshold=squat_depth_threshold,
        quality=quality,
        debug_video_path=debug_video_path
    )
```

______________________________________________________________________

## 6. Implementation Phases

### Phase 1: MVP - Squat Depth Detection Only (~1 week)

**Goal**: Basic rep counting with squat depth validation

**Deliverables**:

- ✅ Rep detection using squat cycles (reuse CMJ patterns)
- ✅ Squat depth validation using joint angles
- ✅ Basic metrics: total reps, valid reps, squat depth violations
- ✅ Simple CLI: `kinemotion wallball-analyze video.mp4`
- ✅ Python API: `process_wallball_video()`
- ✅ Unit tests for squat detection

**Value**: Immediate feedback on squat technique (33% of no-rep detection)

**Success criteria**:

- Correctly counts reps from squat cycles
- Detects squat depth violations with 90% accuracy
- Works with 45° camera angle

### Phase 2: Ball Tracking & Resting Detection (~1 week)

**Goal**: Add ball tracking and resting violations

**Deliverables**:

- ✅ HSV-based ball detection with pose-guided ROI
- ✅ Ball trajectory tracking
- ✅ Ball resting detection (stationary on ground)
- ✅ Enhanced metrics: ball tracking quality, resting violations
- ✅ CLI options: `--ball-color`, `--resting-threshold`
- ✅ Unit tests for ball tracking

**Value**: Complete no-rep detection except height (67% complete)

**Success criteria**:

- Ball tracked successfully in 80%+ of frames
- Resting violations detected accurately
- Works with common ball colors (black, brown, blue)

### Phase 3: Height Validation (~1 week)

**Goal**: Add target height validation

**Deliverables**:

- ✅ Camera calibration (target-based and athlete-based)
- ✅ Peak trajectory detection
- ✅ Height violation detection
- ✅ Complete metrics: all violation types
- ✅ CLI options: `--target-height`, `--athlete-height`
- ✅ Unit tests for calibration and height validation

**Value**: Full competition-standard validation (100% complete)

**Success criteria**:

- Calibration accuracy within 5cm for known distances
- Height violations detected with 85%+ accuracy
- User can easily calibrate with target or athlete height

### Phase 4: Polish & Documentation (~2-3 days)

**Goal**: Production-ready release

**Deliverables**:

- ✅ Debug overlay visualization (ball track, target line, violations)
- ✅ Comprehensive tests (target: 20-30 tests, following kinemotion patterns)
- ✅ User guide: `docs/guides/wallball-guide.md`
- ✅ Reference: `docs/reference/wallball-standards.md`
- ✅ Auto-tuning parameters (quality presets like dropjump)
- ✅ Batch processing support
- ✅ Performance optimization

**Value**: Professional, well-documented feature

**Success criteria**:

- All tests pass (including CI)
- Documentation complete and clear
- Performance: processes 60s video in \<2 minutes
- Code duplication stays \<3%

______________________________________________________________________

## 7. Technical Challenges & Mitigation

### 7.1 Ball Tracking Reliability

**Challenge**: Ball detection may fail due to lighting, motion blur, occlusion

**Risk Level**: HIGH

**Mitigation strategies**:

1. **Temporal smoothing**:

   - Use `core/smoothing.py` patterns
   - Interpolate missing frames using trajectory prediction

1. **Adaptive thresholding**:

   - Dynamically adjust HSV range based on lighting
   - Learn ball color from initial frames

1. **Pose-guided ROI**:

   - Limit search area to reduce false positives
   - Predict ball location based on hand position

1. **User calibration**:

   - Allow custom HSV ranges via CLI
   - Provide visualization tool to help users select color range

1. **Fallback strategies**:

   - If tracking fails, rely on squat depth only (partial validation)
   - Warn user about tracking quality in metrics

**Acceptance criteria**:

- Ball tracked successfully in 80%+ of frames (good conditions)
- Graceful degradation when tracking fails
- Clear user feedback about tracking quality

### 7.2 Calibration Accuracy

**Challenge**: Converting pixels to meters requires accurate calibration

**Risk Level**: MEDIUM

**Mitigation strategies**:

1. **Multiple calibration methods**:

   - Target-based (preferred for 45° angle)
   - Athlete height-based (fallback)
   - Manual override (user provides pixels-per-meter)

1. **Validation**:

   - Sanity checks on calibration values
   - Compare athlete height in video to known height
   - Warn if calibration seems off

1. **Tolerance margins**:

   - Don't require pixel-perfect height
   - Use reasonable tolerances (e.g., ±5cm)

1. **User guidance**:

   - Clear documentation on camera setup
   - Tips for improving calibration accuracy

**Acceptance criteria**:

- Calibration accuracy within 5cm for known distances
- Clear error messages for bad calibration
- Documented process for manual calibration

### 7.3 Lighting Variations

**Challenge**: HSV color detection sensitive to lighting changes

**Risk Level**: MEDIUM

**Mitigation strategies**:

1. **Preprocessing**:

   - Histogram equalization
   - Adaptive brightness/contrast adjustment

1. **Multiple color models**:

   - HSV (primary)
   - LAB color space (lighting-independent, if HSV fails)

1. **User presets**:

   - Provide presets for common conditions (indoor, outdoor, bright, dim)

1. **Real-time feedback**:

   - Show ball detection in debug overlay
   - Allow user to adjust color range interactively

**Acceptance criteria**:

- Works in typical gym lighting
- User can calibrate for unusual lighting
- Clear documentation about lighting requirements

### 7.4 Occlusion Handling

**Challenge**: Ball may be hidden behind athlete during motion

**Risk Level**: LOW (45° angle reduces this)

**Mitigation strategies**:

1. **Trajectory prediction**:

   - Use physics (parabolic motion) to predict occluded frames
   - Interpolate position during brief occlusions

1. **Phase awareness**:

   - Know when ball should be visible (flight phase)
   - Don't penalize missing detections during expected occlusion

1. **Multiple tracking approaches**:

   - Optical flow as backup
   - Kalman filter for prediction

**Acceptance criteria**:

- Handle brief occlusions (\< 0.5 seconds)
- Accurate trajectory reconstruction

### 7.5 Different Ball Colors/Materials

**Challenge**: Medicine balls come in many colors (black, brown, blue, red, camouflage)

**Risk Level**: LOW

**Mitigation strategies**:

1. **Color presets**:

   - Provide presets for common balls
   - Make presets easy to add

1. **Learning mode**:

   - Let user click on ball in first frame
   - Auto-detect HSV range from selection

1. **Documentation**:

   - List tested ball colors
   - Instructions for custom colors

**Acceptance criteria**:

- Works with 4+ common ball colors out-of-box
- Easy calibration for custom colors

______________________________________________________________________

## 8. Testing Strategy

### 8.1 Test Coverage Goals

Following kinemotion standards (70 tests for 2 jump types):

- **Target**: 20-30 tests for wall ball module
- **Code duplication**: Keep \< 3%
- **Type coverage**: 100% (pyright strict)

### 8.2 Unit Tests

#### `tests/wallball/test_analysis.py`

- Rep detection from squat cycles
- Phase detection (standing → squat → throw → catch)
- Integration with auto-tuning system

#### `tests/wallball/test_ball_tracking.py`

- HSV color detection
- Circularity filtering
- Pose-guided ROI calculation
- Trajectory tracking and peak detection
- Handling of missing frames

#### `tests/wallball/test_validation.py`

- Squat depth validation (joint angles)
- Ball height validation
- Ball resting detection
- Complete rep validation

#### `tests/wallball/test_calibration.py`

- Target-based calibration
- Athlete-based calibration
- Pixels-to-meters conversion
- Edge cases (bad calibration values)

#### `tests/wallball/test_metrics.py`

- Dataclass JSON serialization
- NumPy type conversion
- Metrics calculation

### 8.3 Integration Tests

#### `tests/wallball/test_integration.py`

- End-to-end video processing
- CLI invocation
- Python API
- Debug overlay rendering

### 8.4 Test Fixtures

#### Required test videos (create or source)

1. **`good_reps.mp4`**: 10 perfect reps

   - All reps valid
   - Good lighting, clear ball visibility

1. **`depth_norep.mp4`**: Squat depth violations

   - 5 reps with insufficient depth
   - Various knee angles (85°, 95°, 100°)

1. **`height_norep.mp4`**: Ball height violations

   - 5 reps where ball doesn't reach target
   - Various heights (2.5m, 2.7m, 2.9m for 3m target)

1. **`resting_norep.mp4`**: Ball resting violations

   - 3 reps with ball resting on ground
   - Various rest durations (1s, 2s, 3s)

1. **`mixed_noreps.mp4`**: Multiple violation types

   - Real-world scenario with various issues

1. **`difficult_lighting.mp4`**: Challenging conditions

   - Bright/dim lighting, shadows
   - Tests robustness

1. **`occlusion.mp4`**: Ball partially occluded

   - Tests trajectory prediction

#### Fixture metadata (`fixtures/metadata.json`)

```json
{
  "good_reps.mp4": {
    "fps": 30,
    "total_reps": 10,
    "expected_valid_reps": 10,
    "target_height_m": 3.0,
    "ball_color": "black"
  },
  "depth_norep.mp4": {
    "fps": 30,
    "total_reps": 5,
    "expected_valid_reps": 0,
    "expected_violations": {
      "squat_depth": 5
    }
  }
}
```

### 8.5 Manual Testing Checklist

Before each release:

- [ ] Test with all color presets (black, dark_gray, brown, blue)
- [ ] Test with different target heights (2.7m, 3.0m)
- [ ] Test with different camera angles (pure lateral, 45°, 60°)
- [ ] Test with different video qualities (720p, 1080p, 4K)
- [ ] Test with different frame rates (30fps, 60fps, 120fps)
- [ ] Test calibration methods (target-based, athlete-based)
- [ ] Test debug overlay rendering
- [ ] Test JSON output format
- [ ] Verify code duplication \< 3% (`npx jscpd src/kinemotion`)

### 8.6 Performance Benchmarks

**Target performance** (60-second video, 1080p, 30fps):

- Processing time: \< 2 minutes
- Memory usage: \< 1GB
- Ball tracking success rate: > 80%

### 8.7 CI/CD Integration

Add to existing CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Run wall ball tests
  run: uv run pytest tests/wallball/ -v

- name: Check code duplication
  run: npx jscpd src/kinemotion --threshold 3
```

______________________________________________________________________

## 9. Research References

### 9.1 Ball Tracking Research

**Color-based detection (HSV)**:

- OpenCV tutorials: HSV color segmentation for sports ball tracking
- Roboflow blog: "Tracking Ball in Sports with Computer Vision"
- Proved effective for basketball, volleyball, snooker

**Key findings**:

- HSV more robust than RGB for color detection
- Circularity metric (4πA/P²) filters non-spherical objects
- Pose-guided ROI reduces false positives by 70%+

**Relevant code examples**:

```python
# From Microsoft PromptCraft-Robotics
# HSV-based basketball detection
lower_orange = np.array([10, 100, 100])
upper_orange = np.array([30, 255, 255])
mask = cv2.inRange(hsv, lower_orange, upper_orange)

# From Roboflow ball tracking blog
# Trajectory visualization with deque buffer
buffer = deque(maxlen=buffer_size)
buffer.append(ball_position)
```

### 9.2 Squat Depth Detection Research

**Joint angle approaches**:

- MediaPipe Pose: 33-landmark model with angle calculation utilities
- YOLOv8-Pose AI Gym: Uses joint angles for exercise counting
- cvzone PoseModule: `findAngle()` for exercise form validation

**Key findings**:

- Joint angles more robust than vertical positions
- Knee angle \< 90° indicates full squat depth
- Works with any camera angle (not just lateral)

**Relevant code examples**:

```python
# From Ultralytics AI Gym
gym_object = solutions.AIGym(
    pose_type="squat",
    kpts_to_check=[6, 8, 10]  # Hip, knee, ankle
)

# From cvzone
angle = detector.findAngle(
    hip_landmark,
    knee_landmark,
    ankle_landmark
)
```

### 9.3 Camera Calibration Research

**Pose-based calibration**:

- AthletePose3D: Uses known body segment lengths
- Azure Kinect Jump Analysis: Reference-based calibration
- Common approach: Use athlete height or known reference objects

**Key findings**:

- Single-camera calibration achieves ±5cm accuracy
- Target-based calibration more accurate than athlete-based
- Multiple reference points improve robustness

### 9.4 Kinemotion Internal References

**Existing modules to reuse**:

- `core/pose.py`: MediaPipe pose tracking
- `core/smoothing.py`: Savitzky-Golay filtering
- `core/video_io.py`: Video reading/writing, rotation handling
- `cmj/joint_angles.py`: Joint angle calculation
- `cmj/analysis.py`: Phase detection patterns
- `dropjump/analysis.py`: Auto-tuning system
- `core/debug_overlay_utils.py`: Base visualization renderer

**Design patterns to follow**:

- Auto-tuning quality presets (fast/balanced/accurate)
- Backward search for phase detection (CMJ pattern)
- Dataclass metrics with `to_dict()` for JSON serialization
- NumPy type conversion in serialization
- CLI structure with `@click.command`
- Context managers for video I/O

______________________________________________________________________

## 10. Future Enhancements

### 10.1 Short-term (6 months)

1. **Multiple ball tracking algorithms**:

   - Add YOLO as optional backend (more accurate, requires model)
   - Add optical flow tracking (backup for occlusion)

1. **Improved calibration UI**:

   - Interactive calibration tool
   - Click target/reference in video frame

1. **Real-time processing**:

   - Live webcam analysis (see `docs/technical/real-time-analysis.md`)
   - Immediate no-rep feedback

1. **Mobile app integration**:

   - iOS/Android app with kinemotion backend
   - HYROX-specific UI

### 10.2 Long-term (1+ years)

1. **Other HYROX exercises**:

   - Burpee broad jump
   - Sandbag lunges
   - Sled push/pull
   - (Full HYROX workout analysis)

1. **3D tracking**:

   - Dual-camera stereo setup
   - Improved depth perception
   - Better height validation

1. **ML-based ball detection**:

   - Train custom YOLO model on medicine balls
   - Improve robustness to lighting/occlusion

1. **Competition integration**:

   - Official HYROX judge tool
   - Real-time leaderboard integration

______________________________________________________________________

## 11. Conclusion

### 11.1 Summary

Wall ball no-rep detection is **feasible and valuable** for kinemotion:

✅ **Technical feasibility**: Moderate-challenging, but achievable with existing architecture
✅ **Reusability**: Leverages 70% of existing code (pose, angles, smoothing, video I/O)
✅ **User value**: Immediate training feedback, competition preparation
✅ **HYROX relevance**: One of 8 stations, popular exercise

**Key insights**:

1. Use **45° camera angle** for superior ball visibility
1. Use **joint angles** for camera-agnostic squat validation
1. Hybrid **pose-guided HSV** tracking balances simplicity and accuracy
1. **Phased implementation** delivers value incrementally

### 11.2 Estimated Effort

**Total**: 3-4 weeks full-time development

| Phase                      | Effort   | Deliverable                           |
| -------------------------- | -------- | ------------------------------------- |
| Phase 1: MVP (squat only)  | 1 week   | Basic rep counting + squat validation |
| Phase 2: Ball tracking     | 1 week   | Ball detection + resting violations   |
| Phase 3: Height validation | 1 week   | Complete no-rep detection             |
| Phase 4: Polish            | 2-3 days | Documentation, tests, optimization    |

### 11.3 Recommendation

**Status**: APPROVED for implementation ✅

**Rationale**:

- Clear user demand (HYROX growing sport)
- Technical feasibility confirmed
- Fits kinemotion's architecture perfectly
- Incremental delivery reduces risk

**Next steps**:

1. Create test fixtures (record wall ball videos)
1. Implement Phase 1 MVP (1 week sprint)
1. Validate with real athletes
1. Iterate based on feedback
1. Continue with Phases 2-4

### 11.4 Success Metrics

**Phase 1 success**:

- [ ] Correctly counts reps from squat cycles
- [ ] Detects squat depth violations with 90% accuracy
- [ ] Works with 45° camera angle
- [ ] Unit tests pass

**Phase 2 success**:

- [ ] Ball tracked in 80%+ of frames
- [ ] Resting violations detected accurately
- [ ] Works with 4+ ball colors

**Phase 3 success**:

- [ ] Height calibration within 5cm accuracy
- [ ] Height violations detected with 85% accuracy
- [ ] Easy user calibration process

**Overall success**:

- [ ] All 20-30 tests pass
- [ ] Code duplication \< 3%
- [ ] Documentation complete
- [ ] Positive user feedback from HYROX athletes

______________________________________________________________________

## Appendix A: CLI Examples

```bash
# Basic usage
kinemotion wallball-analyze video.mp4

# With debug video output
kinemotion wallball-analyze video.mp4 --output debug.mp4

# Women's target height
kinemotion wallball-analyze video.mp4 --target-height 2.7

# Custom ball color
kinemotion wallball-analyze video.mp4 --ball-color blue

# With athlete height calibration
kinemotion wallball-analyze video.mp4 --athlete-height 1.75

# Save JSON metrics
kinemotion wallball-analyze video.mp4 --json-output metrics.json

# Batch processing
kinemotion wallball-analyze videos/*.mp4 --batch --workers 4
```

## Appendix B: Python API Examples

```python
from kinemotion import process_wallball_video

# Basic usage
metrics = process_wallball_video("wallball.mp4")
print(f"Valid reps: {metrics.valid_reps}/{metrics.total_reps_attempted}")

# With debug video
metrics = process_wallball_video(
    "wallball.mp4",
    debug_video_path="debug.mp4"
)

# Women's competition
metrics = process_wallball_video(
    "wallball.mp4",
    target_height_m=2.7  # Women's target
)

# Custom ball color
metrics = process_wallball_video(
    "wallball.mp4",
    ball_color_preset="blue"
)

# With calibration
metrics = process_wallball_video(
    "wallball.mp4",
    athlete_height_m=1.75  # Athlete's known height
)

# Access detailed results
for rep in metrics.reps:
    if not rep.is_valid:
        print(f"Rep {rep.rep_number}: NO-REP")
        for violation in rep.violations:
            print(f"  - {violation.violation_type}: {violation.details}")
```

## Appendix C: Related Documentation

**After implementation, create these user-facing docs**:

- `docs/guides/wallball-guide.md`: Step-by-step user guide
- `docs/reference/wallball-standards.md`: HYROX standards reference
- `docs/technical/wallball-detection.md`: Technical implementation details

**Update existing docs**:

- `docs/README.md`: Add wall ball to navigation
- `CLAUDE.md`: Add wall ball to quick reference
- `docs/guides/camera-setup.md`: Add wall ball camera setup section

______________________________________________________________________

**Document version**: 1.0
**Last updated**: 2025-11-07
**Author**: Development team
**Status**: Ready for implementation
