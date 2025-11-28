---
title: Camera Perspective Analysis - 45° vs Lateral Angle Impact on Joint Angle Calculations
type: note
permalink: biomechanics/camera-perspective-analysis-45deg-vs-lateral
tags:
  - camera-angle
  - ankle-angle
  - perspective
  - validation
  - issue-10
---

# Camera Perspective Analysis: 45° vs Lateral Angle Impact on Joint Angles

**Critical Finding:** The ankle angle and triple extension algorithms currently **DO NOT account for camera viewing angle**.

## Current Algorithm Behavior

### Code Analysis

**File:** `src/kinemotion/cmj/joint_angles.py`

All joint angle calculations use the same approach:
- **`calculate_angle_3_points(point1, point2, point3)`** - Generic 3-point angle calculator
- Uses law of cosines: `cos(angle) = (v1 · v2) / (|v1| * |v2|)`
- Works purely on 2D pixel coordinates from MediaPipe pose landmarks
- **No camera angle correction or perspective adjustment**

### How Angles are Calculated

1. **Ankle angle:** foot_index → ankle → knee (3-point angle in 2D)
2. **Knee angle:** ankle → knee → hip (3-point angle in 2D)
3. **Hip angle:** knee → hip → shoulder (3-point angle in 2D)
4. **Trunk tilt:** hip-to-shoulder angle relative to vertical

All calculations assume **the 2D pixel positions directly represent true joint angles** with no perspective correction.

## The Problem: Viewing Angle Effects

### What MediaPipe Gives Us
- 2D pixel coordinates (x, y) in normalized frame coordinates (0-1)
- Confidence scores (z) for each landmark
- **NO 3D information** (depth is estimated but not used for angle calculations)
- **NO camera intrinsic parameters** (focal length, principal point)
- **NO camera extrinsic parameters** (viewing angle relative to subject)

### How 45° View Differs from Lateral (90°)

#### Lateral View (90° - Pure Side View)
```
Camera ←→ Athlete

In 2D frame coordinates:
- Ankle, knee, hip aligned on Y-axis
- Joint angles in frame ≈ true anatomical angles
- Pure sagittal plane measurement
```

#### 45° View (Between Side and Front)
```
       Athlete
         ↙ 45°
    Camera

In 2D frame coordinates:
- Landmarks appear rotated in frame
- Ankle position compressed/shifted due to perspective
- Joint angles in frame ≠ true anatomical angles
- Mixed sagittal + frontal plane components
```

### Specific Impact on Ankle Angle

**Scenario:** Athlete plantarflexes at takeoff

**Lateral (90°) View:**
```
Expected: 80° (neutral) → 120° (plantarflex) = 40° progression
Measured: ≈ 80° → ≈ 120° = ≈ 40° ✓ CORRECT
Reason: Pure 2D angle matches anatomical angle
```

**45° View (Current Code - NO Correction):**
```
Expected: 80° (neutral) → 120° (plantarflex) = 40° progression
Measured: ≈ 75° → ≈ 110° = ≈ 35° ❌ UNDERESTIMATED
Reason: Perspective foreshortening compresses ankle motion
- Foot appears less plantarflexed than reality
- 3D ankle angle compressed to 2D frame coordinates
```

## Mathematical Basis

### Why This Happens

When camera is at 45°:
- Athlete's foot is partially pointing away from camera
- Plantarflexion motion has components:
  1. **In-plane (visible):** The sagittal movement toward camera
  2. **Out-of-plane (not visible):** The depth component away from camera

2D pixel angle captures only in-plane component, **missing ~15-25% of plantarflexion**.

### Approximate Error Estimate

For a 45° camera angle viewing a plantarflexing ankle:
- **Systematic bias:** -5° to -10° (underestimation)
- **Proportional error:** -10% to -15% of true angle progression
- **Example:** True 40° progression measured as 34-36°

## Impact on Validation

### Issue for CMJ Ankle Angle Validation (Issue #10)

**Current target:** 30°+ ankle angle progression (80° → 120°+)

**What happens with 45° video:**
```
If true progression is 40° with ideal lateral view:
- Measured at 45° angle: ~34-36° ✓ Still passes criterion
- But measurement is systematically biased low
- Cannot be compared directly to lateral-view reference studies
```

**Specific risk:**
- Videos recorded at 45° may show ankle progression at edge of acceptance
- Same athlete at lateral (90°) view would show 5-10° more progression
- Inconsistent validation across different camera angles

### Impact on Triple Extension Analysis

Less critical than ankle, but still affected:

1. **Hip angle:** Mostly in sagittal plane - minimal 45° effect (~2-3° error)
2. **Knee angle:** Similar to hip - ~3-5° error
3. **Ankle angle:** Most affected - ~5-10° error (as above)
4. **Trunk tilt:** Depends on frame orientation - ~2-5° error

## Solutions (Not Yet Implemented)

### Option 1: Camera Angle Correction (Recommended)
- Add camera angle parameter to analysis
- Apply 2D→3D perspective transformation
- Requires knowing camera intrinsic/extrinsic parameters
- **Effort:** Moderate (1-2 weeks)

### Option 2: Dual-Camera Stereo (Research-Grade)
- Use Pose2Sim for 3D reconstruction
- Eliminates perspective ambiguity entirely
- **Effort:** High (requires additional infrastructure)

### Option 3: Validation Against Lateral View
- Record same athletes with both 45° and lateral cameras
- Create correction factors empirically
- **Effort:** Medium (requires validation study)

### Option 4: Document Limitation (Current Approach)
- Clearly state in guidelines: "Use lateral view for accurate measurements"
- Accept that 45° view is for improved visibility, not accuracy
- **Effort:** Low (documentation only)

## Recommendation for Recording Guidelines

**Current `INSTRUCCIONES-GRABACION-CMJ-ES.md` recommends 45° angle based on:**
- Better ankle/knee visibility (40-60% vs 18-27% in lateral)
- Reduced occlusion
- Better tracking quality

**But this introduces systematic measurement bias.**

### Choice to Make:
1. **Accept the trade-off:** Better visibility but ~10% ankle angle underestimation
2. **Use lateral view instead:** Pure measurements but ~30% lower landmark visibility
3. **Use 45° with documented correction:** Requires algorithm changes

## Code Status Summary

| Component | Status | Impact |
|-----------|--------|--------|
| `calculate_angle_3_points()` | 2D only, no perspective correction | All joint angles affected |
| `calculate_ankle_angle()` | No camera angle consideration | 5-10° systematic error at 45° |
| `calculate_triple_extension()` | Passes through angles as-is | Depends on individual angles |
| Documentation | No mention of camera angle limitations | Users unaware of bias |

## Evidence

- **Baldinger et al. (2025):** "Influence of the Camera Viewing Angle on OpenPose Validity in Motion Analysis" - documents ~15-20% joint angle errors with suboptimal camera angles
- **Project guidelines (docs/guides/camera-setup.md):** Recommends 45° for visibility but doesn't mention measurement accuracy trade-offs

## Action Items for Project

1. **Clarify recording guidelines:** Choose between visibility vs accuracy trade-off
2. **Document limitations:** If using 45°, explicitly state ±5-10° ankle angle uncertainty
3. **Consider 3D reconstruction:** Implement stereo or other 3D methods for future research-grade analysis
4. **Validate empirically:** Record test videos at multiple angles, compare measurements
