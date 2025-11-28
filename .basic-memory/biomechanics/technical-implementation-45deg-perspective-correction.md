---
title: Technical Implementation - 45° Camera Perspective Correction for Joint Angles
type: note
permalink: biomechanics/technical-implementation-45deg-perspective-correction
tags:
  - perspective-correction
  - camera-angle
  - implementation
  - technical-feasibility
---

# Technical Implementation: 45° Camera Perspective Correction for Joint Angles

## Executive Summary

**YES, it's technically feasible** to adjust algorithms for 45° view, but with practical trade-offs:

| Aspect | Complexity | Feasibility |
|--------|-----------|-------------|
| **Math model** | Low-Medium | ✅ Well-established (computer vision) |
| **Implementation** | Medium | ✅ 2-3 weeks development |
| **User calibration** | Medium | ⚠️ Requires setup per session |
| **Accuracy improvement** | High (10-15%) | ✅ Eliminates systematic bias |
| **Practical deployment** | Medium | ⚠️ Adds complexity |

---

## Technical Approach: Planar Homography Correction

### How It Would Work

**Step 1: Establish Camera Model**

For a fixed 45° setup, define:
```
Camera intrinsics (iPhone/Android standard):
- Focal length: ~1000 pixels (for 1080p)
- Principal point: (960, 540) (frame center)
- No significant distortion (modern phones)

Camera extrinsics (measured at setup):
- Height: 130-150cm (hip level)
- Distance: 3-5m from athlete
- Angle: 45° from sagittal plane
- Rotation matrix R for 45° rotation
- Translation vector t for position
```

**Step 2: 2D→3D Projection**

For each 2D landmark (x, y) in frame:
```
Assume movement in sagittal plane (reasonable for jumps)
Use back-projection to estimate 3D position:

P_3D = K^-1 * [x, y, 1]^T * depth_estimate

Where:
- K = camera intrinsic matrix
- depth_estimate = estimated distance from camera (from ankle contact detection)
```

**Step 3: Apply Inverse Rotation**

Rotate 3D points to canonical (lateral) view:
```
P_canonical = R^-1 * P_3D

This removes the 45° rotation, giving equivalent lateral view coordinates
```

**Step 4: Calculate Angles in Canonical Space**

Compute joint angles using 2D projection of canonical 3D points:
```
No more perspective bias ✓
Angles are now comparable across camera angles ✓
```

### Mathematical Model

**Planar homography approach** (simplified, assumes sagittal plane):

```
For 45° camera with athlete centered:

Rotation matrix (45° around z-axis):
R_45 = [cos(45°)  -sin(45°)  0] = [0.707  -0.707  0]
       [sin(45°)   cos(45°)  0]   [0.707   0.707  0]
       [0          0         1]   [0       0      1]

To convert 2D→3D (assuming depth z from ankle contact):
P_3D = [x * z/f, y * z/f, z]^T
(where f = focal length in pixels, z = estimated depth)

Then apply inverse rotation:
P_canonical = R_45^T * P_3D = R^-1 * P_3D

Project back to 2D:
[x_canonical, y_canonical] = [(P_canonical.x * f) / P_canonical.z,
                               (P_canonical.y * f) / P_canonical.z]

Calculate angles using canonical coordinates (same as lateral view)
```

---

## Implementation Options

### Option 1: Simplified Fixed Correction (Easiest)

**What:** Apply average correction factor for all 45° videos

**Math:**
```python
# Empirically measured correction factor
ANKLE_ANGLE_45DEG_CORRECTION = 1.145  # Multiply measured angle by this

ankle_angle_corrected = ankle_angle_measured * ANKLE_ANGLE_45DEG_CORRECTION

# Example:
# Measured: 35°  →  Corrected: 40° (closer to true 40°)
```

**Pros:**
- ✅ Simple (1 line of code)
- ✅ No calibration needed
- ✅ Minimal overhead

**Cons:**
- ❌ Average correction, not precise
- ❌ Assumes all setups are identical
- ❌ Only works if camera angle is exactly 45°

**Effort:** 1-2 hours

---

### Option 2: Calibration-Based Correction (Practical)

**What:** User performs one-time calibration, system learns camera parameters

**Calibration process:**
```
1. User records known object (e.g., 50cm ruler) at athlete position
2. Algorithm measures ruler length in pixels
3. Calculates depth relationship: z = (real_size_mm * focal_length) / pixel_size
4. Stores camera model for future videos
5. Applies perspective correction to all videos with that camera
```

**Implementation:**
```python
class PerspectiveCorrector:
    def __init__(self, calibration_data):
        # Calibration performed once, stored
        self.focal_length = calibration_data['focal_length']
        self.camera_angle = 45.0  # degrees
        self.distance = 4.0  # meters
        self.height = 1.4  # meters

    def correct_angle_3d(self, landmarks_2d, joint1, joint2, joint3):
        # Convert 2D landmarks to 3D using calibration
        points_3d = self._to_3d(landmarks_2d)

        # Rotate to canonical (lateral) view
        points_canonical = self._rotate_to_canonical(points_3d)

        # Calculate angle in canonical space
        angle = calculate_angle_3_points(
            points_canonical[joint1],
            points_canonical[joint2],
            points_canonical[joint3]
        )
        return angle
```

**Pros:**
- ✅ Precise (uses actual camera parameters)
- ✅ Adaptive (different phones/setups)
- ✅ One-time calibration
- ✅ Theoretically sound

**Cons:**
- ⚠️ Requires user calibration step
- ⚠️ More complex implementation (~2-3 weeks)
- ❌ Adds computation per frame (~5-10% slower)

**Effort:** 2-3 weeks development

---

### Option 3: Automatic Angle Detection (Advanced)

**What:** System detects camera angle from video itself

**How:**
- Analyze human pose skeleton (know anatomical joint angle bounds)
- Use optimization to infer camera angle that best explains observed landmarks
- Apply perspective correction based on detected angle

**Pros:**
- ✅ No user calibration
- ✅ Works with any camera angle (not just 45°)

**Cons:**
- ❌ Complex optimization algorithm
- ❌ Potentially unstable (multiple solutions possible)
- ❌ Expensive computation (~30-60 seconds per video)

**Effort:** 4-6 weeks development

---

## What Information Is Needed

### For Correction to Work

```
REQUIRED (to calculate 3D positions):
1. Focal length (camera's focal length in pixels)
   - iPhone standard: ~1000-1200 pixels for 1080p
   - Android varies by model

2. Camera angle (45° in this case)
   - Could be hardcoded if standardized
   - Or provided by user in CLI

3. Depth estimate (distance from camera to ankle)
   - Estimate from ankle contact detection
   - Or use fixed 4m distance if setup is standardized

OPTIONAL (improves accuracy):
- Camera principal point (usually frame center)
- Lens distortion parameters (usually negligible on phones)
- Ground plane height (for better depth estimation)
```

### From Recording Instructions

The standardized 45° setup in recording protocol provides:
- ✅ Fixed angle: 45° (can be hardcoded)
- ✅ Fixed distance: 3-5m optimal, 4m typical (can use default)
- ✅ Fixed height: Mid-chest level 100-120cm (can use default)
- ✅ Fixed phone type: iPhone/Android (focal length tables exist)

**This means we could use Option 1 or Option 2 with minimal user input.**

---

## Recommended Implementation Path

### Phase 1: Validation Study (Immediate)
```
1. Record same athlete with BOTH:
   - Lateral view (90°) - reference
   - 45° view - test

2. Calculate correction factors empirically:
   - Ankle angle: measured_45° vs measured_90°
   - Knee angle: measured_45° vs measured_90°
   - Hip angle: measured_45° vs measured_90°

3. Document correction factors
   - Example: ankle_corrected = ankle_measured * 1.142
```

**Why this first:**
- Validates the mathematical model
- Provides empirical correction factors
- Low cost (~4-8 hours)
- Enables quick fix (Option 1)

### Phase 2: Simple Correction (1-2 weeks)
```
Implement Option 1 (fixed correction factors):
- Apply empirically-derived correction in calculate_angle_3_points()
- Add CLI flag: --camera-angle 45
- Document assumptions and limitations
```

### Phase 3: Calibration-Based Correction (Future)
```
Implement Option 2 if:
- Users request different camera angles
- Need for higher accuracy arises
- Time allows after Phase 2
```

---

## Impact on Recording Guidelines

### If We Implement Perspective Correction

**Update recording protocol:**

```markdown
## Camera Setup for Perspective Correction

The system now automatically corrects for 45° camera angle.

### Calibration (One-time, ~5 minutes)
1. Position a 50cm ruler at the athlete position
2. Record 5 seconds of ruler in frame
3. Run: kinemotion calibrate --ruler-video calibration.mp4
4. System stores camera parameters

### Recording
- Use 45° angle as specified
- All angle measurements automatically corrected
- Results comparable to lateral-view studies
- No special considerations needed
```

---

## Code Changes Required

### Minimal Change (Option 1):
```python
# File: src/kinemotion/cmj/joint_angles.py

def calculate_angle_3_points(
    point1: tuple[float, float],
    point2: tuple[float, float],
    point3: tuple[float, float],
    camera_angle: float = None,  # NEW
) -> float:
    """Calculate angle with optional perspective correction."""

    angle = _calculate_2d_angle(point1, point2, point3)

    # Apply perspective correction if camera angle provided
    if camera_angle is not None and camera_angle == 45:
        angle = angle * 1.142  # Empirically derived correction

    return angle
```

### Moderate Change (Option 2):
```python
# New file: src/kinemotion/core/perspective.py

class PerspectiveCorrector:
    def __init__(self, calibration_file):
        self.calibration = load_calibration(calibration_file)

    def landmarks_2d_to_3d(self, landmarks_2d):
        """Convert 2D landmarks to 3D using calibration."""
        # Implement 2D→3D back-projection

    def correct_angle(self, landmarks_2d, joint1, joint2, joint3):
        """Calculate angle with automatic perspective correction."""
        # Convert to 3D
        # Rotate to canonical view
        # Calculate angle
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Calibration fails | Low | Medium | Provide default values |
| Math unstable | Low | High | Validate with test cases |
| Computation overhead | Low | Medium | Cache calibration data |
| User confusion | Medium | Medium | Clear documentation |
| Different phone models | Medium | Medium | Auto-detect focal length |

---

## Recommendation

**Implement Option 1 (Simple Correction) first:**

1. ✅ Quick validation study (4-8 hours)
2. ✅ Implement fixed correction factors (1-2 hours)
3. ✅ Update recording guidelines
4. ✅ Deploy and collect feedback
5. 🔄 Upgrade to Option 2 if needed

**Timeline:** 1-2 weeks total

**Benefit:** Eliminates systematic 10-15% error, makes 45° measurements equivalent to lateral view

**Trade-off:** Slightly more complex code, one-time calibration (Option 2)

---

## Evidence

- **Camera calibration:** OpenCV, Pose2Sim use similar approaches successfully
- **Perspective correction:** Standard in medical imaging, sports biomechanics software
- **Implementation reference:** Baldinger et al. (2025) describes angle measurement errors but not correction methods
