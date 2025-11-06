# Pose Estimation Systems - Quick Reference

**Last Updated:** November 2025 (Sources through July 2025)

## TL;DR - Best Choice by Use Case

| Use Case           | Recommended System    | Accuracy     | Setup Effort | Cost     |
| ------------------ | --------------------- | ------------ | ------------ | -------- |
| **Research Lab**   | Pose2Sim              | ★★★★★ (3-4°) | Medium       | Free     |
| **Field Testing**  | OpenCap               | ★★★★☆        | Low          | Free     |
| **Clinical/Rehab** | Stereo MediaPipe      | ★★★☆☆        | Low          | Free     |
| **Elite Sports**   | Pose2Sim + Sport Data | ★★★★★        | Medium-High  | Free-$$$ |
| **Commercial**     | Theia3D               | ★★★★☆        | Low          | $$$      |

______________________________________________________________________

## System Comparison Table

| System                | Joint Angle Error | Position RMSE | Validation | Cameras   | Open Source |
| --------------------- | ----------------- | ------------- | ---------- | --------- | ----------- |
| **Pose2Sim**          | 3-4°              | 30-40mm       | Qualisys ✓ | 4-8       | Yes         |
| **OpenCap**           | TBD               | TBD           | Emerging   | 2+ phones | Yes         |
| **Stereo MediaPipe**  | ~5-7°             | 30mm          | Qualisys ✓ | 2         | Yes         |
| **Theia3D**           | 2.6-13.2°         | -             | Published  | Multi     | No          |
| **Current MediaPipe** | ~10-15°           | 56mm          | Limited    | 1         | Yes         |
| **Marker-Based**      | \<2°              | 1-15mm        | Gold Std   | 8+        | No          |

______________________________________________________________________

## Quick Decision Tree

```text
Need sports biomechanics accuracy?
├─ Yes
│  ├─ Have budget/time for multi-camera setup?
│  │  ├─ Yes → Use Pose2Sim
│  │  └─ No → Use OpenCap (smartphones)
│  └─ Just need exercise assessment?
│     └─ Use Stereo MediaPipe OR OpenCap
└─ No (general pose detection)
   └─ Stay with current MediaPipe/OpenPose
```

______________________________________________________________________

## Pose2Sim Quick Setup

```bash
# 1. Install
pip install pose2sim

# 2. Setup project
pose2sim-project setup

# 3. Run pipeline
pose2sim calibration      # Camera calibration
pose2sim poseEstimation   # 2D pose detection
pose2sim triangulation    # 3D reconstruction
pose2sim filtering        # Smooth trajectories
pose2sim kinematics       # OpenSim IK → joint angles
```

**Hardware Needed:**

- 4-8 RGB cameras (1080p+, 60 Hz+)
- Calibration board (ChArUco)
- Sync (hardware or software)

**Output:**

- 3D joint coordinates (.trc)
- Joint angles (.mot)
- Velocities, accelerations
- OpenSim model

______________________________________________________________________

## OpenCap Quick Setup

```bash
# 1. Record with 2+ smartphones
# 2. Upload to opencap.ai
# 3. Download results
# 4. Parse OpenSim output
```

**Hardware Needed:**

- 2+ smartphones
- Internet connection

**Output:**

- OpenSim results
- Joint angles
- Video with overlay

______________________________________________________________________

## Stereo MediaPipe Quick Setup

```python
import mediapipe as mp
import cv2

# Process two camera views
pose = mp.solutions.pose.Pose()
results1 = pose.process(frame1)  # Camera 1
results2 = pose.process(frame2)  # Camera 2

# Triangulate (need calibration)
point_3d = triangulate(results1, results2, calib)
```

**Hardware Needed:**

- 2 cameras at 90° angle
- Camera calibration

**Output:**

- 3D joint coordinates
- MediaPipe landmarks (33 points)

______________________________________________________________________

## Kinemotion Upgrade Options

### Option 1: Pose2Sim (Best Accuracy)

- **Effort:** Medium (2-4 weeks)
- **Benefit:** Research-grade (3-4° errors)
- **Changes:** Add 3-4 cameras, implement full pipeline

### Option 2: Stereo MediaPipe (Simple)

- **Effort:** Low (1-2 weeks)
- **Benefit:** ~50% error reduction
- **Changes:** Add 1 camera, implement triangulation

### Option 3: OpenCap (Easiest)

- **Effort:** Very Low (days)
- **Benefit:** Biomechanical constraints
- **Changes:** Record with phones, parse output

______________________________________________________________________

## Key Metrics Explained

**CMC (Coefficient of Multiple Correlation):**

>

- > 0.95: Excellent
- 0.85-0.94: Very good
- 0.75-0.84: Good
- \<0.75: Poor

**Joint Angle Error:**

- \<2°: Gold standard (marker-based)
- 3-5°: Excellent (research-grade markerless)
- 5-10°: Good (clinical use)
- > 10°: Limited use

**Position RMSE:**

- \<15mm: Gold standard
- 30-40mm: Good markerless
- 50-60mm: Acceptable for exercises
- > 100mm: Poor

______________________________________________________________________

## Critical Success Factors

For sports biomechanics markerless systems:

1. ✅ **Multi-camera** (≥2, ideally 4-8)
1. ✅ **90° camera separation** (optimal triangulation)
1. ✅ **Biomechanical constraints** (OpenSim skeletal model)
1. ✅ **Proper calibration** (intrinsic + extrinsic)
1. ✅ **Temporal filtering** (Butterworth 4th order, 6 Hz)
1. ✅ **Sport-specific training** (fine-tune on athletic data)
1. ✅ **Gold standard validation** (compare to Vicon/Qualisys)

______________________________________________________________________

## Common Pitfalls

❌ **Using monocular for biomechanics** → depth ambiguity, noisy
❌ **No biomechanical constraints** → physically inconsistent
❌ **Lateral view only** → occlusion (kinemotion's issue)
❌ **Poor calibration** → 3D reconstruction errors
❌ **Generic training data for sports** → 69% worse accuracy
❌ **No validation** → unknown accuracy
❌ **Low frame rate for fast movements** → temporal aliasing

______________________________________________________________________

## Resources

**Documentation:**

- Pose2Sim: <https://pose2sim.readthedocs.io/>
- OpenCap: <https://www.opencap.ai/>
- OpenSim: <https://opensim.stanford.edu/>

**Datasets:**

- AthletePose3D: <https://github.com/calvinyeungck/athletepose3d>
- BioCV: <https://doi.org/10.1038/s41597-024-04077-3>

**Key Papers (Full citations in main documentation):**

- **\[1\]** Pagnon et al. (2022) - Pose2Sim validation: <https://doi.org/10.3390/s22072712>
- **\[2\]** Dill et al. (2024) - Stereo MediaPipe validation: <https://doi.org/10.3390/s24237772>
- **\[3\]** Yeung et al. (2025) - AthletePose3D dataset: <https://arxiv.org/abs/2503.07499>
- **\[4\]** Bazarevsky et al. (2020) - MediaPipe Pose: <https://arxiv.org/abs/2006.10204>
- **\[5\]** Cao et al. (2019) - OpenPose: <https://doi.org/10.1109/TPAMI.2019.2929257>
- **\[11\]** Delp et al. (2007) - OpenSim: <https://doi.org/10.1109/TBME.2007.901024>

______________________________________________________________________

## FAQ

**Q: Can I use OpenPose/MediaPipe alone for biomechanics?**
A: No. They provide 2D/noisy 3D keypoints but lack biomechanical constraints and multi-view accuracy \[1\]. Use Pose2Sim or OpenCap.

**Q: How many cameras do I need?**
A: Minimum 2 (stereo), recommended 4-8 (full 3D).

**Q: Will DWpose or newer models help?**
A: Not significantly. The bottleneck is multi-view triangulation and biomechanical modeling, not the 2D detector.

**Q: What about IMUs (Xsens)?**
A: Comparable accuracy (2-5° errors) but requires wearable sensors \[1\]. Video-based is more natural.

**Q: Can I process in real-time?**
A: Most systems are batch processing. Real-time requires optimization and GPU acceleration.

**Q: How do I validate my setup?**
A: Compare against marker-based system (Vicon/Qualisys). Calculate CMC, RMSE, ROM errors, Bland-Altman plots \[1,2\].

______________________________________________________________________

## Contact & Updates

This is a living document based on research as of November 2025 (sources through July 2025). The field is rapidly advancing.

For kinemotion project-specific questions, see:

- Main documentation: `SPORTS_BIOMECHANICS_POSE_ESTIMATION.md`
- Project: <https://github.com/feniix/kinemotion> (or your repo)

**Check for updates:** Research landscape changes quickly. New validations and systems emerge regularly.
