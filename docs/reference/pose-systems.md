# Pose Estimation Systems - Quick Reference

**Last Updated:** December 2025 (Sources through December 2025)

## TL;DR - Best Choice by Use Case

| Use Case                              | Recommended System    | Accuracy     | Setup Effort | Cost     |
| ------------------------------------- | --------------------- | ------------ | ------------ | -------- |
| **Multi-Sport (Jumps/Sprints/Lifts)** | **RTMLib (RTMPose)**  | ★★★★★ (5.6°) | **Very Low** | Free     |
| **Research Lab**                      | Pose2Sim              | ★★★★★ (3-4°) | Medium       | Free     |
| **Field Testing**                     | OpenCap               | ★★★★☆        | Low          | Free     |
| **Clinical/Rehab**                    | Stereo MediaPipe      | ★★★☆☆        | Low          | Free     |
| **Elite Sports**                      | Pose2Sim + Sport Data | ★★★★★        | Medium-High  | Free-$$$ |
| **Browser/Mobile**                    | MediaPipe             | ★★★☆☆        | Very Low     | Free     |
| **Apple Silicon Dev**                 | **RTMLib**            | ★★★★★        | **Very Low** | Free     |
| **Commercial**                        | Theia3D               | ★★★★☆        | Low          | $$$      |

> **New (Dec 2025):** RTMLib provides RTMPose accuracy without MMPose dependencies. Native Apple Silicon support, trivial installation (`pip install rtmlib`).

______________________________________________________________________

## System Comparison Table

| System               | Joint Angle Error | Position RMSE | Validation     | Cameras   | Open Source | Apple Silicon |
| -------------------- | ----------------- | ------------- | -------------- | --------- | ----------- | ------------- |
| **RTMLib (RTMPose)** | **5.6°**          | ~30mm         | Running/Jump ✓ | 1+        | Yes         | **Native ✓**  |
| **Pose2Sim**         | 3-4°              | 30-40mm       | Qualisys ✓     | 4-8       | Yes         | Problematic   |
| **OpenCap**          | TBD               | TBD           | Emerging       | 2+ phones | Yes         | Yes           |
| **Stereo MediaPipe** | ~5-7°             | 30mm          | Qualisys ✓     | 2         | Yes         | Yes           |
| **Theia3D**          | 2.6-13.2°         | -             | Published      | Multi     | No          | N/A           |
| **MediaPipe (mono)** | ~6-10°            | 56mm          | Limited        | 1         | Yes         | Yes           |
| **OpenPose**         | ~5-8°             | -             | Academic       | 1+        | Yes         | **No (CUDA)** |
| **Marker-Based**     | \<2°              | 1-15mm        | Gold Std       | 8+        | No          | N/A           |

> **Note:** RTMLib wraps RTMPose models for deployment without MMPose/MMCV dependencies.

______________________________________________________________________

## Quick Decision Tree

```text
What's your primary constraint?
├─ Apple Silicon / No GPU
│  └─ Use RTMLib (pip install rtmlib)
├─ Browser deployment needed
│  └─ Use MediaPipe (TensorFlow.js)
├─ Multi-sport analysis (jumps/sprints/lifts/wallball)
│  └─ Use RTMLib (best accuracy + easy setup)
├─ Research-grade accuracy required
│  ├─ Have multi-camera setup?
│  │  └─ Yes → Use Pose2Sim (3-4° accuracy)
│  └─ Smartphone-only?
│     └─ Use OpenCap
└─ Quick prototype / exercise assessment
   └─ Use MediaPipe (simplest)
```

______________________________________________________________________

## RTMLib Quick Setup (Recommended for Multi-Sport)

```bash
# Install (works on Apple Silicon, Linux, Windows)
pip install rtmlib
```

```python
from rtmlib import Body

# Initialize (downloads models automatically)
pose_tracker = Body(
    mode='balanced',      # 'lightweight', 'balanced', 'performance'
    backend='onnxruntime',
    device='cpu'          # or 'cuda', 'mps'
)

# Process frame
keypoints, scores = pose_tracker(frame)
# keypoints: (num_people, 17, 2) - COCO format
# scores: (num_people, 17)
```

**Models Available:**

| Model           | Keypoints | Use Case                |
| --------------- | --------- | ----------------------- |
| `Body`          | 17        | Jumps, sprints, general |
| `Body` (26-kpt) | 26        | Body + feet detail      |
| `Wholebody`     | 133       | Body + hands + face     |
| `RTMO`          | 17        | One-stage (faster)      |

**Performance Modes:**

| Mode          | Speed     | Accuracy | Best For          |
| ------------- | --------- | -------- | ----------------- |
| `lightweight` | 25-40 FPS | Good     | Real-time preview |
| `balanced`    | 15-25 FPS | Better   | Production        |
| `performance` | 8-15 FPS  | Best     | Detailed analysis |

**Repository:** <https://github.com/Tau-J/rtmlib>

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

**Q: What's the best choice for multi-sport analysis (jumps, sprints, lifts)?**
A: **RTMLib (RTMPose)**. Best accuracy (5.6° RMSE for running), works on Apple Silicon, trivial setup.

**Q: Can I use OpenPose/MediaPipe alone for biomechanics?**
A: For field/training use, RTMLib or MediaPipe are sufficient. For research-grade accuracy, use Pose2Sim or OpenCap with multi-camera setup.

**Q: Does RTMPose work on Mac M1/M2/M3?**
A: Yes! Use RTMLib (`pip install rtmlib`), which runs via ONNX Runtime without CUDA dependencies. Tested and confirmed working.

**Q: Why RTMLib instead of full MMPose?**
A: MMPose has MMCV dependency issues on Apple Silicon (CUDA compilation errors). RTMLib provides the same models without those dependencies.

**Q: How many cameras do I need?**
A: Single camera works for field use (5-10° accuracy). For research (3-4° accuracy), use 4-8 cameras with Pose2Sim.

**Q: Will DWPose or newer models help?**
A: For single-camera use, RTMPose/DWPose are ~10-15% more accurate than MediaPipe. The bigger gains come from multi-view setups.

**Q: MediaPipe vs RTMPose for sprint analysis?**
A: RTMPose (5.62° RMSE) beats MediaPipe (6.33° RMSE) and is more robust to motion blur in fast movements.

**Q: What about browser deployment?**
A: Use MediaPipe (TensorFlow.js) for browser. RTMLib is Python/server-side only.

**Q: Can I process in real-time?**
A: Yes. RTMLib `lightweight` mode: 25-40 FPS. MediaPipe: 30+ FPS. Both work on CPU.

**Q: How do I validate my setup?**
A: Compare against marker-based system (Vicon/Qualisys). Calculate CMC, RMSE, ROM errors, Bland-Altman plots \[1,2\].

______________________________________________________________________

## Contact & Updates

This is a living document based on research as of December 2025. The field is rapidly advancing.

For kinemotion project-specific questions, see:

- Detailed comparison: [`docs/research/pose-estimator-comparison-2025.md`](../research/pose-estimator-comparison-2025.md)
- Sports biomechanics research: [`docs/research/sports-biomechanics-pose-estimation.md`](../research/sports-biomechanics-pose-estimation.md)
- Project: <https://github.com/feniix/kinemotion>

**Check for updates:** Research landscape changes quickly. New validations and systems emerge regularly.

______________________________________________________________________

## Additional Resources

- **RTMLib:** <https://github.com/Tau-J/rtmlib>
- **RTMPose Paper:** <https://arxiv.org/abs/2303.07399>
- **Running Biomechanics Comparison:** arXiv:2505.04713
- **AthletePose3D:** <https://arxiv.org/abs/2503.07499>
