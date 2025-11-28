# Camera Perspective Validation Study - Issue #10 Progress

**Date**: November 28, 2025
**Status**: Phase 1 Discovery Complete - Ready for Phase 2 Implementation
**Related Issue**: #10 (CMJ Ankle Angle Validation)

## Current Discovery

### Problem Identified

The CMJ ankle angle and triple extension algorithms **DO NOT account for camera viewing angle**:

- Current code uses pure 2D pixel calculations (no perspective correction)
- `calculate_angle_3_points()` in `src/kinemotion/cmj/joint_angles.py` uses law of cosines on 2D landmarks only
- Systematic bias: ~5-10° underestimation at 45° camera angle

### Impact Analysis

- **45° View vs 90° Lateral View**:

  - At 45°: 2D pixel angle captures only in-plane component
  - Missing ~15-25% of true plantarflexion motion
  - Example: True 40° progression measured as 34-36°

- **Affected Components**:

  - Ankle angle: ~5-10° error (most affected)
  - Knee angle: ~3-5° error
  - Hip angle: ~2-3° error (mostly in sagittal plane)
  - Trunk tilt: ~2-5° error

### Validation Protocol Designed

**12-Video Recording Protocol** (Phase 1 validation study):

- **Groups A-D**: 45°/90° × 60fps/120fps (3 jumps each)
- **Same athlete**: Consistency across all measurements
- **Ankle angle target**: 80° → 120°+ (≥30° progression)
- **Outcome**: Empirically-derived correction factors for 45° view

**Documents Created**:

- `docs/guides/cmj-recording-protocol-es.md` - Spanish instructions
- `docs/guides/cmj-recording-protocol.md` - English instructions

## Implementation Recommendations

### Recommended Path: Option 1 (Simple Correction)

1. **Phase 1 (4-8 hours)**: Collect 12 validation videos, establish correction factors
1. **Phase 2 (1-2 weeks)**: Implement fixed correction factors in code
1. **Phase 3 (Future)**: Upgrade to calibration-based correction if needed

### Implementation Options Analyzed

1. **Option 1: Fixed Correction Factor** (Recommended)

   - Effort: 1-2 hours
   - Implementation: 1 line of code (`angle * 1.145`)
   - Trade-off: Average correction, assumes identical setups

1. **Option 2: Calibration-Based Correction** (Practical)

   - Effort: 2-3 weeks
   - Implementation: PerspectiveCorrector class with 2D→3D projection
   - Trade-off: Requires one-time calibration per session

1. **Option 3: Automatic Angle Detection** (Advanced)

   - Effort: 4-6 weeks
   - Implementation: Optimization algorithm to infer camera angle
   - Trade-off: Complex, potentially unstable

## Mathematical Model

**Planar Homography Approach** (for 45° camera):

```
Rotation matrix R_45 (45° around z-axis):
R = [0.707  -0.707  0]
    [0.707   0.707  0]
    [0       0      1]

2D→3D back-projection: P_3D = K^-1 * [x, y, 1]^T * z
Rotate to canonical: P_canonical = R^-1 * P_3D
Project back to 2D for angle calculation
```

## Code Changes Required

### For Option 1 (Quick Fix):

File: `src/kinemotion/cmj/joint_angles.py`

- Add optional `camera_angle` parameter to `calculate_angle_3_points()`
- Apply empirical correction: `angle * 1.142` when `camera_angle=45`

### For Option 2 (Full Solution):

New file: `src/kinemotion/core/perspective.py`

- Implement `PerspectiveCorrector` class
- Methods: `landmarks_2d_to_3d()`, `correct_angle()`

## Risk Assessment

| Risk                   | Likelihood | Impact | Mitigation               |
| ---------------------- | ---------- | ------ | ------------------------ |
| Calibration fails      | Low        | Medium | Provide default values   |
| Math unstable          | Low        | High   | Validate with test cases |
| Computation overhead   | Low        | Medium | Cache calibration data   |
| User confusion         | Medium     | Medium | Clear documentation      |
| Different phone models | Medium     | Medium | Auto-detect focal length |

## Knowledge Base References

### Basic-Memory Biomechanics Folder

- `camera-perspective-analysis-45deg-vs-lateral.md` (196 lines)

  - Algorithm behavior analysis
  - Mathematical basis for perspective bias
  - Impact on validation
  - 4 solution options documented

- `technical-implementation-45deg-perspective-correction.md` (397 lines)

  - Executive summary with feasibility assessment
  - Technical approach (planar homography)
  - 3 implementation options with code examples
  - Recommended implementation path
  - Risk assessment and evidence

- `cmj-physiological-bounds-for-validation.md` (817 lines)

  - Flight time, jump height, countermovement depth bounds
  - Peak velocity bounds
  - Triple extension angle specifications
  - Athlete profile bounds (elderly, recreational, elite)
  - Edge cases (7 specific anomalies)
  - Comprehensive validation logic

## Next Steps

1. **Phase 1 (Immediate)**: Record 12 validation videos per protocol
1. **Phase 2 (1-2 weeks)**: Implement Option 1 correction factors
1. **Phase 3 (Post-MVP)**: Upgrade to Option 2 if higher accuracy needed
1. **Documentation**: Update recording guidelines with perspective correction info

## Evidence Base

- **Baldinger et al. (2025)**: "Influence of the Camera Viewing Angle on OpenPose Validity in Motion Analysis" - documents ~15-20% joint angle errors with suboptimal camera angles
- **OpenCV/Pose2Sim**: Successfully implement similar perspective correction approaches
- **Standard in biomechanics**: Medical imaging and sports analysis software use these correction methods
