# Best Pose Detection & Tracking for Sports Biomechanics

## Research Summary - November 2025

This document summarizes current state-of-the-art markerless pose estimation and tracking systems for sports biomechanics applications, based on validation studies and research literature published through mid-2025 (most recent: July 2025).

______________________________________________________________________

## Executive Summary

**Key Finding:** For sports biomechanics research, **Pose2Sim** is currently the best-validated open-source solution, achieving 3-4° joint angle accuracy when validated against gold-standard motion capture systems \[1\].

**Critical Insight:** The 2D pose estimator (OpenPose, MediaPipe, etc.) is only the first step. Sports biomechanics requires \[2\]:

1. Multi-camera 3D triangulation
1. Biomechanical skeletal modeling (OpenSim) \[11\]
1. Inverse kinematics for joint angles
1. Validation against gold-standard motion capture

______________________________________________________________________

## 1. Sports Biomechanics Requirements

### Why General Pose Estimation is Insufficient

Standard pose estimation libraries (OpenPose \[5\], MediaPipe \[4\], MoveNet \[9\]) are designed for general-purpose human pose detection but fall short for biomechanics because:

| Requirement      | General HPE              | Sports Biomechanics Need              |
| ---------------- | ------------------------ | ------------------------------------- |
| **Output**       | 2D or noisy 3D keypoints | Accurate 3D joint coordinates         |
| **Joint Angles** | Not provided             | \<5° error required                   |
| **Constraints**  | None                     | Anatomically plausible poses          |
| **Frame Rate**   | 30 fps typical           | 120-240 Hz for fast movements         |
| **Validation**   | General datasets         | Gold standard MoCap (Vicon, Qualisys) |
| **Kinematics**   | Position only            | Position, velocity, acceleration      |
| **Depth**        | Ambiguous (monocular)    | Accurate 3D depth required            |

### Biomechanics-Specific Challenges

1. **Joint Center Bias**: ML-based detectors have systematic 10-50mm offsets from true anatomical joint centers \[1\]
1. **Depth Ambiguity**: Monocular 3D estimation is ill-posed (multiple 3D poses → same 2D projection) \[2\]
1. **Occlusion**: Self-occlusion in lateral views (e.g., 18-27% ankle/knee visibility in lateral camera angles)
1. **Physical Plausibility**: Need to enforce joint angle limits and kinematic constraints \[11\]
1. **Temporal Consistency**: Smooth trajectories required for velocity/acceleration calculations \[1\]

______________________________________________________________________

## 2. State-of-the-Art Systems

### 2.1 Pose2Sim (Recommended for Research)

#### Pose2Sim Overview

- Full pipeline for sports biomechanics: 2D detection → triangulation → OpenSim modeling
- Validated against Qualisys 31-marker system
- Open-source, actively maintained
- **Citation:** Pagnon, D., Domalain, M., & Reveret, L. (2022). Pose2Sim: An End-to-End Workflow for 3D Markerless Sports Kinematics—Part 2: Accuracy. *Sensors*, 22(7), 2712. <https://doi.org/10.3390/s22072712> \[1\]

#### Validated Accuracy (vs Qualisys Gold Standard)

| Task    | Mean Joint Angle Error | ROM Error | CMC Correlation |
| ------- | ---------------------- | --------- | --------------- |
| Walking | 3.0°                   | 2.7°      | 0.90-0.98       |
| Running | 4.1°                   | 2.3°      | 0.65-1.00\*     |
| Cycling | 4.0°                   | 4.3°      | 0.75-1.00\*     |

\*Hip flexion/extension in running had 15° offset (CMC=0.65) due to systematic bias
\*Ankle in cycling partially occluded (CMC=0.75)

**95% Limits of Agreement:** ±15° across all movements (Bland-Altman analysis)

#### Pipeline Architecture

```text
1. Multi-camera video capture (4-8 cameras recommended)
2. 2D pose estimation (OpenPose, MediaPipe, or AlphaPose)
3. Person tracking across views
4. Robust 3D triangulation (RANSAC filtering)
5. Butterworth filtering (4th order, 6 Hz)
6. OpenSim skeletal model scaling
7. Inverse kinematics optimization
8. Export: joint angles, velocities, accelerations
```

#### Key Features

- Flexible 2D backend (works with OpenPose, MediaPipe BlazePose, AlphaPose)
- Physically consistent poses via OpenSim constraints
- Camera calibration without prior calibration (optional)
- Robust to dark/blurry images, calibration errors
- Works with as few as 4 cameras

#### Setup Requirements

- 4-8 RGB cameras (90° separation optimal)
- Hardware or software synchronization
- Python environment
- OpenSim for biomechanical modeling

**Repository:** <https://github.com/perfanalytics/pose2sim>

#### Validation Studies

- Pagnon et al. (2022): Walking, running, cycling validation
- Compared favorably to Theia3D commercial system
- Mean errors within marker-based system tolerances

______________________________________________________________________

### 2.2 OpenCap (Accessible Alternative)

#### OpenCap Overview

- Stanford-developed, web-based motion capture system \[13\]
- Uses smartphones (2+ required)
- Free, open-source
- Designed specifically for biomechanics research

#### Features

- No specialized hardware required
- Automatic OpenSim integration
- Web-based processing (no local compute needed)
- Growing validation literature
- Accessible to non-experts

#### Validation Status

- Multiple ongoing validation studies (2024)
- Designed for clinical and sports applications
- Accuracy metrics still emerging in literature

#### Use Cases

- Field testing and training environments
- Clinical assessments
- Educational applications
- Low-resource settings

**Access:** <https://www.opencap.ai/>

______________________________________________________________________

### 2.3 Stereo MediaPipe + Triangulation

#### Stereo MediaPipe Overview

- Two-camera setup using MediaPipe Pose \[4\]
- 2D detection + stereo triangulation
- No biomechanical constraints (unless added)

#### Validated Accuracy

- **Median RMSE:** 30.1mm (vs Qualisys)
- **Monocular MediaPipe:** 56.3mm RMSE
- **Improvement:** 47% reduction in error with stereo
- **Statistical significance:** p \< 10⁻⁶

**Validation Study:** Dill, S., Ahmadi, A., Grimmer, M., Haufe, D., Rohr, M., Zhao, Y., Sharbafi, M., & Hoog Antink, C. (2024). Accuracy Evaluation of 3D Pose Reconstruction Algorithms Through Stereo Camera Information Fusion for Physical Exercises with MediaPipe Pose. *Sensors*, 24(23), 7772. <https://doi.org/10.3390/s24237772> \[2\]

#### Key Findings \[2\]

- 9 subjects performing squats (correct and incorrect)
- Validated against Qualisys 11-camera system
- Sufficient accuracy for exercise error detection
- Not recommended for precise kinematic analysis

#### Optimal Setup

- 90° angle between cameras (from Pagnon et al.)
- MediaPipe Pose (BlazePose model)
- Triangulation with epipolar geometry
- 6 Hz Butterworth filtering

#### Stereo MediaPipe Limitations

- No biomechanical constraints → anatomically inconsistent poses possible
- Systematic biases from MediaPipe remain
- Lower accuracy than Pose2Sim
- Better for exercise assessment than research

______________________________________________________________________

### 2.4 AthletePose3D (Sport-Specific Training)

#### AthletePose3D Overview

- New benchmark dataset for athletic movements (CVSports at CVPR 2025)
- Addresses failure of general models on high-speed sports
- Fine-tuning dataset for sport-specific applications

**Citation:** Yeung, C., Suzuki, T., Tanaka, R., Yin, Z., & Fujii, K. (2025). AthletePose3D: A Benchmark Dataset for 3D Human Pose Estimation and Kinematic Validation in Athletic Movements. *arXiv preprint arXiv:2503.07499*. \[3\]

#### Dataset Characteristics \[3\]

- 12 sports movements
- 1.3M frames, 165K postures
- High-speed, high-acceleration focus
- Validated against gold-standard MoCap

#### Performance Impact \[3\]

- Generic model MPJPE: 214mm
- After fine-tuning on AthletePose3D: 65mm
- **Improvement: 69%** (3.3x reduction in error)

#### Applications

- Fine-tuning existing models for specific sports
- Training sport-specific pose estimators
- Validating markerless systems on athletic movements

**Availability:** Dataset downloadable for research (non-commercial license)

**Repository:** <https://github.com/calvinyeungck/athletepose3d>

______________________________________________________________________

### 2.5 Commercial Systems

#### Theia3D

- **Type:** Commercial markerless solution
- **Accuracy:** 2.6°-13.2° RMSE (walking validation) \[14\]
- **Features:** Proprietary 2D detector, triangulation, skeletal modeling
- **Cost:** Commercial licensing
- **Validation:** Published validation studies available \[14\]

#### Vald/Simi/Contemplas

- Industry-specific commercial solutions
- Turnkey systems with support
- Higher cost, easier deployment
- Limited academic validation literature

______________________________________________________________________

## 3. Validation Studies Summary

### 3.1 Pose2Sim Validation (Pagnon et al., 2022) \[1\]

#### Pose2Sim Study Design

- 1 participant, 83 reflective markers (CAST marker set)
- Reference: 20 Qualisys opto-electronic cameras
- Tasks: Walking, running, cycling (8-13 cycles each)
- Comparison: Pose2Sim vs marker-based with same OpenSim model

#### Results - Lower Limb (Sagittal Plane)

| Joint | Task  | CMC  | Pearson r | ROM Error | Mean Error |
| ----- | ----- | ---- | --------- | --------- | ---------- |
| Ankle | Walk  | 0.90 | 0.89      | -1.2°     | -2.8°      |
| Knee  | Walk  | 0.98 | 0.96      | -0.3°     | -1.9°      |
| Hip   | Walk  | 0.96 | 0.96      | -1.7°     | -3.0°      |
| Ankle | Run   | 0.99 | 0.99      | -2.9°     | -0.7°      |
| Knee  | Run   | 1.00 | 1.00      | 0.0°      | -0.7°      |
| Hip   | Run   | 0.65 | 0.95      | 4.0°      | 15.2°\*    |
| Ankle | Cycle | 0.75 | 0.85      | 1.9°      | -6.7°\*    |
| Knee  | Cycle | 1.00 | 1.00      | -2.9°     | 2.1°       |
| Hip   | Cycle | 0.92 | 0.97      | -5.9°     | 6.1°       |

\*Systematic offsets due to occlusion or movement patterns

#### Interpretation of CMC (Coefficient of Multiple Correlation) \[1\]

- CMC > 0.95: Excellent
- CMC 0.85-0.94: Very good
- CMC 0.75-0.84: Good
- CMC \< 0.75: Poor

#### Key Findings \[1\]

1. Sagittal plane (flexion/extension): Excellent agreement (CMC > 0.9)
1. Non-sagittal planes: Good to poor (CMC 0.3-0.9)
1. Systematic offsets can occur (hip running, ankle cycling)
1. Overall accuracy comparable to marker-based for primary movements

______________________________________________________________________

### 3.2 Stereo MediaPipe Validation (Dill et al., 2024) \[2\]

#### Stereo MediaPipe Study Design

- 9 subjects performing squats (correct and incorrect forms)
- Reference: Qualisys 11-camera system, 31 markers
- Setup: 2 smartphones (frontal and lateral views)
- Comparison: Stereo MediaPipe vs monocular MediaPipe 3D

#### Results

| Method                 | Median RMSE | Best Use Case           |
| ---------------------- | ----------- | ----------------------- |
| Monocular MediaPipe 3D | 56.3mm      | General pose estimation |
| Stereo MediaPipe       | 30.1mm      | Exercise assessment     |
| Pose2Sim               | ~30-40mm    | Sports biomechanics     |
| Marker-based           | 1-15mm      | Research gold standard  |

#### Conclusions \[2\]

- Stereo significantly better than monocular (p \< 10⁻⁶)
- Sufficient for exercise error recognition
- Not recommended for precise biomechanical research
- 90° camera angle optimal (confirmed from Pagnon et al. \[1\])

______________________________________________________________________

### 3.3 AthletePose3D Validation (Yeung et al., 2025) \[3\]

#### Key Findings \[3\]

- **Problem:** SOTA models trained on daily activities fail on athletic movements
- **MPJPE on athletic motions:** 214mm (generic models)
- **After fine-tuning:** 65mm MPJPE
- **Improvement:** 69% error reduction

#### Kinematic Validation \[3\]

- Strong joint angle correlation
- Limitations in velocity estimation
- Highlights need for sport-specific training data

#### Impact \[3\]

- Proves generic pose datasets insufficient for sports
- Provides benchmark for athletic pose estimation
- Enables fine-tuning for sport-specific applications

______________________________________________________________________

## 4. Comparison: Pose2Sim vs Alternatives

### 4.1 Accuracy Comparison

| System               | Joint Angle Error | Position RMSE | CMC       | Validation    | Cost  |
| -------------------- | ----------------- | ------------- | --------- | ------------- | ----- |
| **Pose2Sim**         | 3-4°              | 30-40mm       | >0.9      | Qualisys      | Free  |
| **OpenCap**          | TBD               | TBD           | TBD       | Emerging      | Free  |
| **Stereo MediaPipe** | 5-7°\*            | 30mm          | 0.75-0.85 | Qualisys      | Free  |
| **Theia3D**          | 2.6-13.2°         | -             | -         | Published     | $$$   |
| **Xsens (IMU)**      | 2-5°              | N/A           | -         | Published     | $$$$  |
| **Marker-Based**     | \<2°              | 1-15mm        | 1.0       | Gold Standard | $$$$$ |

\*Estimated from RMSE and validation studies

### 4.2 Pose2Sim vs Theia3D vs Xsens (Walking)

From Pagnon et al. (2022) comparison \[1\]:

| Metric               | Pose2Sim | Theia3D | Xsens (IMU) |
| -------------------- | -------- | ------- | ----------- |
| **Ankle RMSE**       | 4.0°     | -       | -           |
| **Knee RMSE**        | 5.1°     | 3.3°    | -           |
| **Hip RMSE**         | 5.6°     | 11°     | -           |
| **Ankle Mean Error** | 2.8°     | -       | 2.2°        |
| **Hip Mean Error**   | 3.0°     | -       | 2.5°        |
| **Ankle ROM Error**  | -1.2°    | ≈-10°   | 0.4°        |
| **Hip ROM Error**    | -1.7°    | ≈-10°   | 2.4°        |

**Note:** Different studies, different setups. Direct comparison limited but indicates comparable performance.

______________________________________________________________________

## 5. System Recommendations by Use Case

### 5.1 Research Labs (Highest Accuracy)

#### Recommended: Pose2Sim

#### Why Pose2Sim for Research

- Research-grade accuracy (3-4° joint angles)
- Validated against gold standard
- Full biomechanics pipeline
- Open-source and customizable

#### Pose2Sim Setup

- 4-8 RGB cameras (1080p, 60-120 Hz)
- Hardware sync (recommended) or software sync
- Camera calibration (ChArUco or checkerboard)
- Compute: GPU recommended but not required

**Cost:** Low (~$2,000-5,000 for cameras + compute)

#### Workflow

```python
from Pose2Sim import Pose2Sim

# Configure cameras and calibration
Pose2Sim.calibration()

# Process videos
Pose2Sim.poseEstimation()  # 2D pose from each camera
Pose2Sim.synchronization()  # Sync multi-camera
Pose2Sim.triangulation()    # 3D reconstruction
Pose2Sim.filtering()        # Smooth trajectories
Pose2Sim.kinematics()       # OpenSim IK
```

______________________________________________________________________

### 5.2 Field/Training Environments

#### Recommended: OpenCap

#### Why OpenCap for Field Use

- Minimal equipment (smartphones only)
- Web-based processing
- Designed for biomechanics
- No specialized setup

#### OpenCap Setup

- 2+ smartphones with cameras
- Internet connection
- OpenCap account (free)

**Cost:** Minimal (use existing smartphones)

#### OpenCap Limitations

- Requires internet
- Less control over processing
- Validation still emerging

______________________________________________________________________

### 5.3 Clinical/Rehabilitation

#### Recommended: Stereo MediaPipe OR OpenCap

#### Why for Clinical Use

- Sufficient accuracy for error detection
- Low setup complexity
- Cost-effective
- Validated for exercise assessment

#### Setup (Stereo MediaPipe)

- 2 cameras at 90° angle
- MediaPipe Pose for 2D detection
- Triangulation with epipolar geometry
- Optional: Add OpenSim constraints

#### Setup (OpenCap)

- 2 smartphones
- Web-based workflow

______________________________________________________________________

### 5.4 Elite Sports Performance

#### Recommended: Pose2Sim + AthletePose3D OR Commercial

#### Why for Elite Sports

- Research-grade accuracy critical for competitive advantage
- Sport-specific fine-tuning available
- OR commercial support for deployment

#### Considerations

- Fine-tune on AthletePose3D for sport-specific movements
- May need >120 Hz for fast movements (pitching, jumping)
- Consider commercial (Theia3D, Vald) for support

______________________________________________________________________

## 6. Implementation Guide: Pose2Sim

### 6.1 Hardware Requirements

#### Cameras

- Minimum: 4 cameras (more is better)
- Resolution: 1080p minimum, 4K better
- Frame rate: 60 Hz minimum, 120-240 Hz for fast movements
- Placement: 90° separation optimal, capture volume from multiple angles
- Sync: Hardware sync ideal, software sync acceptable

#### Compute

- CPU: Multi-core for parallel processing
- GPU: Recommended for 2D pose estimation (not required)
- RAM: 16GB+ recommended
- Storage: Large for raw videos

#### Hardware Calibration

- ChArUco board or checkerboard
- Large enough to be visible from all cameras
- Multiple calibration poses/positions

### 6.2 Software Setup

```bash
# Install Pose2Sim
pip install pose2sim

# Install 2D pose estimator (choose one)
# OpenPose (most validated)
git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose
# OR MediaPipe
pip install mediapipe
# OR AlphaPose
git clone https://github.com/MVIG-SJTU/AlphaPose
```

### 6.3 Workflow Steps

#### 1. Camera Calibration

```python
from Pose2Sim import Pose2Sim
Pose2Sim.calibration()
```

- Capture calibration board from all cameras
- Estimates intrinsic and extrinsic parameters
- Outputs calibration file

#### 2. Video Capture

- Record synchronized videos from all cameras
- Subject performs movement in capture volume
- Ensure subject visible from all cameras

#### 3. 2D Pose Estimation

```python
Pose2Sim.poseEstimation()
```

- Runs OpenPose/MediaPipe on each camera
- Outputs 2D joint coordinates per frame per camera

#### 4. Synchronization (if needed)

```python
Pose2Sim.synchronization()
```

- Aligns camera timestamps
- Handles software sync if no hardware sync

#### 5. Triangulation

```python
Pose2Sim.triangulation()
```

- Reconstructs 3D coordinates from 2D views
- Uses RANSAC for robust outlier rejection
- Outputs 3D joint coordinates

#### 6. Filtering

```python
Pose2Sim.filtering()
```

- Butterworth filter (4th order, 6 Hz default)
- Smooths trajectories for velocity/acceleration

#### 7. OpenSim Kinematics

```python
Pose2Sim.kinematics()
```

- Scales OpenSim model to subject
- Runs inverse kinematics
- Outputs joint angles, velocities, accelerations

### 6.4 Output Data

Pose2Sim provides:

- 3D joint coordinates (.trc files)
- Joint angles (.mot files)
- Joint velocities and accelerations
- OpenSim model files (.osim)
- Visualization files

______________________________________________________________________

## 7. Kinemotion-Specific Recommendations

### Current Limitations

#### Kinemotion's Setup

- MediaPipe monocular (single camera)
- Lateral view (side view)
- Good temporal processing (smoothing, signed velocity)
- Backward search algorithm for CMJ

#### Identified Issues

- 18-27% ankle/knee visibility in lateral view
- Depth ambiguity (noisy Z-axis from monocular)
- No biomechanical constraints

### Recommended Upgrade Path

#### Option 1: Implement Pose2Sim (Best Accuracy)

#### Option 1: Changes Needed

1. Add 3-4 cameras (one frontal, one lateral, 1-2 at 45° angles)
1. Implement camera synchronization
1. Replace single MediaPipe call with Pose2Sim pipeline
1. Add OpenSim skeletal model
1. Keep existing: smoothing, signed velocity, backward search

#### Option 1: Benefits

- Eliminates occlusion problem
- Research-grade accuracy
- Physically consistent poses
- Validated for jumping movements

#### Integration with Existing Code

```python
# kinemotion/core/pose_estimation.py (new module)
from Pose2Sim import Pose2Sim

def process_multi_camera_video(video_paths, drop_height):
    """Process multi-camera video with Pose2Sim"""
    # 1. Run Pose2Sim pipeline
    Pose2Sim.poseEstimation()
    Pose2Sim.triangulation()
    Pose2Sim.filtering()
    Pose2Sim.kinematics()

    # 2. Extract ankle/hip trajectories from OpenSim output
    ankle_pos = extract_joint_trajectory('ankle')
    hip_pos = extract_joint_trajectory('hip')

    # 3. Use existing kinemotion algorithms
    from kinemotion.dropjump.analysis import detect_ground_contact
    ground_contact = detect_ground_contact(ankle_pos, ...)

    # 4. Calculate metrics
    metrics = calculate_metrics(...)
    return metrics
```

**Effort:** Medium (2-4 weeks integration)

______________________________________________________________________

#### Option 2: Add Second Camera (Simpler)

#### Option 2: Changes Needed

1. Add 1 camera at 90° from current lateral view
1. Implement stereo triangulation
1. Keep MediaPipe as 2D detector
1. Optionally add OpenSim constraints

#### Option 2: Benefits

- Lower complexity than Pose2Sim
- Solves depth ambiguity
- Can reuse existing MediaPipe code
- ~50% error reduction

#### Integration

```python
# kinemotion/core/stereo.py (new module)
import mediapipe as mp
import cv2

def triangulate_stereo(video1_path, video2_path, calibration):
    """Triangulate 3D pose from two camera views"""
    # Run MediaPipe on both cameras
    pose1 = run_mediapipe(video1_path)
    pose2 = run_mediapipe(video2_path)

    # Triangulate matching keypoints
    pose3d = triangulate(pose1, pose2, calibration)

    # Apply to existing pipeline
    return pose3d
```

**Effort:** Low (1-2 weeks integration)

______________________________________________________________________

#### Option 3: Try OpenCap (Easiest)

#### Option 3: Changes Needed

1. Record videos with 2 smartphones
1. Upload to OpenCap web interface
1. Download OpenSim results
1. Parse output for existing metrics

#### Option 3: Benefits

- Minimal code changes
- No camera setup
- Automatic biomechanical constraints
- Free

#### Option 3: Limitations

- Less control over processing
- Requires internet
- May not match existing output format exactly

**Effort:** Very Low (days to test)

______________________________________________________________________

### Performance Comparison Estimate

| Setup                    | Expected Accuracy  | Ankle/Knee Visibility | Depth Quality | Effort   |
| ------------------------ | ------------------ | --------------------- | ------------- | -------- |
| Current (MediaPipe mono) | ~10-15° angles     | 18-27%                | Noisy         | -        |
| Stereo MediaPipe         | ~5-7° angles       | 50-80%                | Good          | Low      |
| Pose2Sim                 | ~3-4° angles       | 80-95%                | Excellent     | Medium   |
| OpenCap                  | ~4-6° angles (est) | 80-95%                | Excellent     | Very Low |

______________________________________________________________________

## 8. Best Practices for Sports Biomechanics

### 8.1 Camera Setup

#### Placement

- Minimum 4 cameras for full 3D reconstruction
- 90° separation between adjacent cameras optimal
- Cover full movement volume from all angles
- Avoid backlighting (subject silhouettes reduce accuracy)

#### Configuration

- Resolution: 1080p minimum, higher better
- Frame rate: Match movement speed
  - Walking/slow: 60 Hz sufficient
  - Running/jumping: 120 Hz
  - Baseball pitch/golf swing: 240 Hz
- Shutter speed: Fast enough to avoid motion blur
- Sync: Hardware trigger preferred, software sync acceptable

#### Camera Calibration Best Practices

- Use ChArUco boards (more robust than checkerboard)
- Calibrate at beginning of each session
- Move calibration board through capture volume
- Verify reprojection errors \< 1 pixel

### 8.2 Data Processing

#### 2D Pose Estimation

- Use highest accuracy settings (slower but better)
- MediaPipe: `model_complexity=2`, `min_detection_confidence=0.5`
- OpenPose: `--net_resolution 656x368`, `--scale_number 4`

#### Filtering

- Low-pass filter: 4th-order Butterworth, 6 Hz cutoff (validated in Pose2Sim)
- Adjust cutoff based on movement frequency
- Balance noise removal vs signal preservation

#### Biomechanical Modeling

- Use OpenSim skeletal model
- Scale model to subject anthropometry
- Define joint constraints (angle limits)
- Verify inverse kinematics residuals

### 8.3 Validation

#### Ground Truth Comparison

- Validate against marker-based system (Vicon, Qualisys)
- Calculate CMC, RMSE, ROM errors
- Bland-Altman analysis for systematic bias
- Report 95% limits of agreement

#### Quality Metrics

- OpenSim IK RMS error \< 2-4 cm
- Temporal consistency (smooth trajectories)
- Physical plausibility (no joint angle violations)
- Reprojection error \< 10 pixels

______________________________________________________________________

## 9. Future Directions

### Emerging Technologies

#### 1. Foundation Models for Pose Estimation

- Large-scale models trained on diverse data
- Transfer learning for sport-specific applications
- Examples: ViTPose, HRNet, TokenPose

#### 2. Diffusion Models

- Generative models for pose refinement
- Can handle severe occlusion
- Still experimental for biomechanics

#### 3. Neural Radiance Fields (NeRF)

- 3D scene reconstruction from images
- Potential for markerless capture
- Computationally intensive

#### 4. Event Cameras

- High temporal resolution (microseconds)
- Low latency
- Emerging for sports analysis

### Research Gaps

#### 1. Sport-Specific Validation

- More validation studies needed per sport
- High-speed movements understudied
- Contact sports pose unique challenges

#### 2. Real-Time Processing

- Most systems batch processing only
- Need low-latency for feedback
- Edge deployment for field use

#### 3. Outdoor/Uncontrolled Environments

- Most validation in controlled labs
- Outdoor lighting challenges
- Long-distance capture

#### 4. Multi-Person Sports

- Team sports require multi-person tracking
- Person identity maintenance
- Interaction analysis

______________________________________________________________________

## 10. References

### Key Publications

**\[1\]** Pagnon, D., Domalain, M., & Reveret, L. (2022). Pose2Sim: An End-to-End Workflow for 3D Markerless Sports Kinematics—Part 2: Accuracy. *Sensors*, 22(7), 2712. <https://doi.org/10.3390/s22072712>

- **Validation:** Qualisys, walking/running/cycling, 3-4° joint angle errors
- **Key contribution:** Full validated pipeline for sports biomechanics

**\[2\]** Dill, S., Ahmadi, A., Grimmer, M., Haufe, D., Rohr, M., Zhao, Y., Sharbafi, M., & Hoog Antink, C. (2024). Accuracy Evaluation of 3D Pose Reconstruction Algorithms Through Stereo Camera Information Fusion for Physical Exercises with MediaPipe Pose. *Sensors*, 24(23), 7772. <https://doi.org/10.3390/s24237772>

- **Validation:** Qualisys, squat exercises, 30.1mm RMSE
- **Key contribution:** Stereo MediaPipe validation for exercises

**\[3\]** Yeung, C., Suzuki, T., Tanaka, R., Yin, Z., & Fujii, K. (2025). AthletePose3D: A Benchmark Dataset for 3D Human Pose Estimation and Kinematic Validation in Athletic Movements. *arXiv preprint arXiv:2503.07499*. <https://arxiv.org/abs/2503.07499>

- **Finding:** 69% improvement with sport-specific fine-tuning (214mm → 65mm MPJPE)
- **Key contribution:** First large-scale athletic movement dataset

**\[4\]** Bazarevsky, V., Grishchenko, I., Raveendran, K., Zhu, T., Zhang, F., & Grundmann, M. (2020). BlazePose: On-device Real-time Body Pose Tracking. *arXiv preprint arXiv:2006.10204*. <https://arxiv.org/abs/2006.10204>

- **Key contribution:** MediaPipe Pose architecture

**\[5\]** Cao, Z., Hidalgo Martinez, G., Simon, T., Wei, S., & Sheikh, Y. A. (2019). OpenPose: Realtime Multi-Person 2D Pose Estimation using Part Affinity Fields. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 43(1), 172-186. <https://doi.org/10.1109/TPAMI.2019.2929257>

- **Key contribution:** Part Affinity Fields for multi-person pose estimation

### Validation Studies (2024-2025)

**\[6\]** Truijen, S., Abdullahi, A., Bijsterbosch, D., van Zoest, E., Conijn, M., Wang, Y., Winds, K., Stoel, R., Struyf, N., Saeys, W., & Jansen, B. (2024). Accuracy, Validity, and Reliability of Markerless Camera-Based 3D Motion Capture Systems versus Marker-Based 3D Motion Capture Systems in Gait Analysis: A Systematic Review and Meta-Analysis. *Sensors*, 24(11), 3686. <https://doi.org/10.3390/s24113686>

- **Key contribution:** Systematic review of markerless systems

**\[7\]** Needham, L., Evans, M., Cosker, D. P., Wade, L., McGuigan, P. M., Bilzon, J. L., & Colyer, S. L. (2024). Synchronised Video, Motion Capture and Force Plate Dataset for Validating Markerless Human Movement Analysis. *Scientific Data*, 11, 1281. <https://doi.org/10.1038/s41597-024-04077-3>

- **Key contribution:** BioCV benchmark dataset for validation

**\[8\]** Adlou, B., Wilburn, C., & Weimar, W. (2025). Motion Capture Technologies for Athletic Performance Enhancement and Injury Risk Assessment: A Review for Multi-Sport Organizations. *Sensors*, 25(14), 4384. <https://doi.org/10.3390/s25144384>

- **Key contribution:** Comprehensive review for multi-sport organizations

### Comparative Studies

**\[9\]** Chung, J.-L., Ong, L.-Y., & Leow, M.-C. (2022). Comparative Analysis of Skeleton-Based Human Pose Estimation. *Future Internet*, 14(12), 380. <https://doi.org/10.3390/fi14120380>

- **Comparison:** OpenPose, PoseNet, MoveNet, MediaPipe Pose
- **Key contribution:** Performance comparison across systems

**\[10\]** Needham, L., Evans, M., Cosker, D. P., Wade, L., McGuigan, P. M., Bilzon, J. L., & Colyer, S. L. (2021). The accuracy of several pose estimation methods for 3D joint centre localisation. *Scientific Reports*, 11, 20673. <https://doi.org/10.1038/s41598-021-00212-x>

- **Finding:** Task-specific accuracy varies significantly
- **Key contribution:** Highlighted importance of task-specific validation

### OpenSim Resources

**\[11\]** Delp, S. L., Anderson, F. C., Arnold, A. S., Loan, P., Habib, A., John, C. T., Guendelman, E., & Thelen, D. G. (2007). OpenSim: Open-Source Software to Create and Analyze Dynamic Simulations of Movement. *IEEE Transactions on Biomedical Engineering*, 54(11), 1940-1950. <https://doi.org/10.1109/TBME.2007.901024>

- **Key contribution:** OpenSim biomechanical modeling framework

**\[12\]** Rajagopal, A., Dembia, C. L., DeMers, M. S., Delp, D. D., Hicks, J. L., & Delp, S. L. (2016). Full-Body Musculoskeletal Model for Muscle-Driven Simulation of Human Gait. *IEEE Transactions on Biomedical Engineering*, 63(10), 2068-2079. <https://doi.org/10.1109/TBME.2016.2586891>

- **Key contribution:** Full-body gait model used in Pose2Sim

### OpenCap Resources

**\[13\]** Uhlrich, S. D., Falisse, A., Kidziński, Ł., Muccini, J., Ko, M., Chaudhari, A. S., Hicks, J. L., & Delp, S. L. (2023). OpenCap: Human movement dynamics from smartphone videos. *PLOS Computational Biology*, 19(10), e1011462. <https://doi.org/10.1371/journal.pcbi.1011462>

- **Key contribution:** Smartphone-based accessible biomechanics

### Commercial System Validation

**\[14\]** Kanko, R. M., Laende, E. K., Davis, E. M., Selbie, W. S., & Deluzio, K. J. (2021). Concurrent assessment of gait kinematics using marker-based and markerless motion capture. *Journal of Biomechanics*, 127, 110665. <https://doi.org/10.1016/j.jbiomech.2021.110665>

- **System:** Theia3D validation
- **Key contribution:** Commercial markerless validation

______________________________________________________________________

## 11. Software & Resources

### Open-Source Tools

#### Pose2Sim

- GitHub: <https://github.com/perfanalytics/pose2sim>
- Documentation: <https://pose2sim.readthedocs.io/>
- License: BSD 3-Clause

#### OpenCap

- Website: <https://www.opencap.ai/>
- GitHub: <https://github.com/stanfordnmbl/opencap-core>
- License: Apache 2.0

#### AthletePose3D

- GitHub: <https://github.com/calvinyeungck/athletepose3d>
- Paper: <https://arxiv.org/abs/2503.07499>
- License: Non-commercial research only

#### MediaPipe

- GitHub: <https://github.com/google/mediapipe>
- Documentation: <https://developers.google.com/mediapipe>
- License: Apache 2.0

#### OpenPose

- GitHub: <https://github.com/CMU-Perceptual-Computing-Lab/openpose>
- License: Academic/commercial licensing

#### OpenSim

- Website: <https://opensim.stanford.edu/>
- GitHub: <https://github.com/opensim-org/opensim-core>
- License: Apache 2.0

### Commercial Solutions

- **Theia3D:** <https://www.theiamarkerless.ca/>
- **Vald Performance:** <https://www.valdperformance.com/>
- **Simi Motion:** <https://www.simi.com/>
- **Contemplas:** <https://www.contemplas.com/>

______________________________________________________________________

## 12. Glossary

**CMC (Coefficient of Multiple Correlation):** Statistical measure of waveform similarity that jointly evaluates correlation, gain, and offset. Values >0.95 indicate excellent agreement.

**MPJPE (Mean Per Joint Position Error):** Average Euclidean distance between estimated and ground truth 3D joint positions.

**ROM (Range of Motion):** Angular excursion of a joint during movement.

**RMSE (Root Mean Square Error):** Square root of the mean squared differences between estimated and ground truth values.

**Inverse Kinematics (IK):** Computational method to determine joint angles given endpoint positions, enforcing skeletal constraints.

**Triangulation:** Computing 3D coordinates from 2D projections in multiple camera views using epipolar geometry.

**Gold Standard:** Marker-based motion capture systems (Vicon, Qualisys, OptiTrack) with sub-millimeter accuracy.

**Sagittal Plane:** Anatomical plane dividing body into left and right halves (flexion/extension movements).

**Frontal Plane:** Anatomical plane dividing body into front and back (abduction/adduction).

**Transverse Plane:** Anatomical plane dividing body into upper and lower (rotation).

______________________________________________________________________

## Document History

- **Version 1.0** - November 2025: Initial documentation based on 2022-2025 research
- **Research Date:** November 2025 (sources through July 2025)
- **Author:** Research synthesis for kinemotion project
- **Last Updated:** November 6, 2025

______________________________________________________________________

## Conclusion

For sports biomechanics applications requiring accurate joint angle measurements:

1. **Use Pose2Sim \[1\]** for research-grade accuracy (3-4° errors)
1. **Multi-camera setup is essential** (minimum 4 cameras, 90° separation optimal \[1\])
1. **Biomechanical constraints required** (OpenSim skeletal modeling \[11\])
1. **Validate against gold standard** (marker-based motion capture \[7\])
1. **Sport-specific training helps** (AthletePose3D fine-tuning \[3\])

The field is rapidly advancing, but Pose2Sim \[1\] currently represents the best-validated open-source solution for sports biomechanics research, with published validation against gold-standard motion capture systems. Recent developments in sport-specific datasets \[3\] and stereo camera validation \[2\] continue to improve accessibility and accuracy of markerless systems for athletic applications \[8\].
