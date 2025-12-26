# Pose Estimator Comparison for Multi-Sport Analysis

## Research Summary - December 2025

This document compares pose estimation systems for kinemotion's multi-sport expansion (jumps, sprints, weightlifting, wall ball) based on December 2025 research.

______________________________________________________________________

## Executive Summary

**Key Finding:** For a multi-sport platform on Apple Silicon, **RTMLib (RTMPose)** is the recommended choice, offering best-in-class accuracy for athletic movements with trivial installation and native M1/M2/M3 support.

**Decision Matrix:**

| Scenario                     | Recommendation            |
| ---------------------------- | ------------------------- |
| Jump analysis only (current) | MediaPipe is adequate     |
| Multi-sport platform         | **RTMLib/RTMPose**        |
| Browser-side preview         | MediaPipe (TensorFlow.js) |
| Research-grade accuracy      | RTMPose + multi-camera    |

______________________________________________________________________

## 1. Systems Compared

### 1.1 MediaPipe (Current)

- **Developer:** Google
- **Architecture:** Top-down (detect person, then keypoints)
- **Keypoints:** 33 landmarks
- **Speed:** 30+ FPS on CPU
- **API:** Tasks API (PoseLandmarker) - **Solution API removed in 0.10.31**
- **Model:** `lite` model (matches Solution API's `model_complexity=1` behavior)
- **Strengths:** Easy setup, browser deployment, mobile-native
- **Weaknesses:** Motion blur sensitivity, occlusion handling, single-person optimized

**Important Migration Note (December 2025):**

- MediaPipe Tasks API is now used (Solution API removed in v0.10.31)
- The `lite` model produces results matching the previous Solution API validation
- `full` and `heavy` models produce significantly different metrics (17% error in jump height)

### 1.2 OpenPose

- **Developer:** Carnegie Mellon University
- **Architecture:** Bottom-up (detect parts, then assemble)
- **Keypoints:** 25 body + hands/face/feet
- **Speed:** GPU-dependent (seconds per frame without GPU)
- **Strengths:** Multi-person, academic gold standard
- **Weaknesses:** Stale (2021), complex setup, CUDA required

### 1.3 DWPose

- **Developer:** IDEA Research (ICCV 2023)
- **Architecture:** Two-stage distillation
- **Keypoints:** 133 whole-body (body, face, hands, feet)
- **Speed:** 0.5-10 GFLOPS depending on model
- **Strengths:** Best whole-body accuracy, active development
- **Weaknesses:** MMPose dependency, GPU recommended

### 1.4 RTMPose (via RTMLib)

- **Developer:** OpenMMLab / Tau-J
- **Architecture:** Real-time multi-person pose estimation
- **Keypoints:** 17 (body), 26 (body+feet), 133 (whole-body)
- **Speed:** 15-40 FPS on CPU
- **Strengths:** Best accuracy, lightweight deployment, Apple Silicon native
- **Weaknesses:** Newer ecosystem

______________________________________________________________________

## 2. Accuracy Benchmarks

### 2.1 Running/Sprint Analysis (2025 Study)

Source: "Comparison of Visual Trackers for Biomechanical Analysis of Running" (arXiv:2505.04713)

| Tracker     | RMSE (degrees) | Ranking |
| ----------- | -------------- | ------- |
| **RTMPose** | **5.62°**      | **#1**  |
| MoveNet     | 6.14°          | #2      |
| MediaPipe   | 6.33°          | #3      |
| CoTracker3  | 24.83°         | #4      |
| PoseNet     | 33.44°         | #5      |

**Conclusion:** RTMPose is 12% more accurate than MediaPipe for sprint biomechanics.

### 2.2 Vertical Jump Analysis (2024 Study)

Source: "Advancing Field-Based Vertical Jump Analysis" (PMC11677309)

Using MMPose/RTMPose:

- **Velocity correlation:** r = 0.992 (extremely high)
- **Jump height ICC:** 0.985
- **Propulsive phase ICC:** 0.974
- **Take-off phase ICC:** 0.971

**Conclusion:** RTMPose achieves excellent agreement with force plates for jump metrics.

### 2.3 Athletic Movement Dataset (2025)

Source: AthletePose3D (arXiv:2503.07499)

- Generic models MPJPE: 214mm on athletic movements
- After sport-specific fine-tuning: 65mm
- **Improvement: 69%**

**Conclusion:** Domain-specific training matters more than model architecture.

### 2.4 Motion Blur Robustness

Source: "Robustness Evaluation in Hand Pose Estimation" (arXiv:2303.04566)

- **MediaPipe:** 50%+ detection failures with diagonal motion blur
- **OpenPose:** More robust to motion blur
- **RTMPose:** Most robust (ONNX-optimized inference)

**Conclusion:** For fast movements (sprints, wall ball throws), RTMPose and OpenPose outperform MediaPipe.

______________________________________________________________________

## 3. Movement-Specific Analysis

### 3.1 Counter-Movement Jump (CMJ) & Drop Jump

| Factor                | MediaPipe | RTMPose   | Winner    |
| --------------------- | --------- | --------- | --------- |
| Single-plane analysis | Good      | Excellent | RTMPose   |
| Takeoff detection     | Good      | Excellent | RTMPose   |
| Flight time accuracy  | Good      | Excellent | RTMPose   |
| Setup complexity      | Trivial   | Easy      | MediaPipe |

**Recommendation:** Both work well; RTMPose for maximum accuracy.

### 3.2 Sprint Analysis

| Factor                   | MediaPipe          | RTMPose    | Winner      |
| ------------------------ | ------------------ | ---------- | ----------- |
| High-speed limb tracking | Weak (motion blur) | Strong     | **RTMPose** |
| Joint angle accuracy     | 6.33° RMSE         | 5.62° RMSE | **RTMPose** |
| Foot strike detection    | Moderate           | Good       | **RTMPose** |

**Recommendation:** RTMPose strongly preferred for sprint analysis.

### 3.3 Weightlifting (Squat, Deadlift, Bench)

| Factor                     | MediaPipe | RTMPose  | Winner      |
| -------------------------- | --------- | -------- | ----------- |
| Barbell occlusion handling | Weak      | Moderate | **RTMPose** |
| Depth changes (sagittal)   | Moderate  | Good     | **RTMPose** |
| Multi-view support         | Limited   | Native   | **RTMPose** |

**Research Context:** Multiple 2024-2025 studies use MediaPipe + YOLOv5 hybrid, but RTMPose offers unified solution.

**Recommendation:** RTMPose preferred; multi-camera setup ideal for depth.

### 3.4 Wall Ball (CrossFit/HYROX)

| Factor                   | MediaPipe | RTMPose  | Winner      |
| ------------------------ | --------- | -------- | ----------- |
| Overhead arm extension   | Weak      | Good     | **RTMPose** |
| Fast repetition counting | Moderate  | Good     | **RTMPose** |
| Ball occlusion           | Weak      | Moderate | **RTMPose** |

**Recommendation:** RTMPose preferred for explosive overhead movements.

______________________________________________________________________

## 4. Apple Silicon Compatibility

### 4.1 The Problem with MMPose

MMPose (full framework) has known issues on Apple Silicon:

- MMCV compilation errors (CUDA dependencies)
- No official ARM64 wheels
- Requires workarounds (pytorch-nightly)

GitHub Issues: #2250, #2218 on open-mmlab/mmcv

### 4.2 The Solution: RTMLib

**RTMLib** is a lightweight wrapper that runs RTMPose WITHOUT MMPose dependencies:

```bash
pip install rtmlib
```

**Dependencies (minimal):**

- numpy
- opencv-python
- opencv-contrib-python
- onnxruntime

**Tested on M1 Pro (December 2025):**

```
✅ RTMLib initialized successfully on CPU!
✅ Inference works! Output shape: keypoints=(1, 17, 2)
```

### 4.3 Performance on Apple Silicon

| Mode          | Expected FPS | Use Case            |
| ------------- | ------------ | ------------------- |
| `lightweight` | 25-40 FPS    | Real-time preview   |
| `balanced`    | 15-25 FPS    | Production analysis |
| `performance` | 8-15 FPS     | Maximum accuracy    |

Memory: ~20MB per model (16GB unified RAM is plenty)

______________________________________________________________________

## 5. Deployment Comparison

| Aspect                | MediaPipe  | OpenPose       | RTMLib     |
| --------------------- | ---------- | -------------- | ---------- |
| **pip install**       | ✅ Trivial | ❌ Complex     | ✅ Trivial |
| **Apple Silicon**     | ✅ Native  | ❌ Problematic | ✅ Native  |
| **Browser (TFJS)**    | ✅ Yes     | ❌ No          | ❌ No      |
| **Cloud Run**         | ✅ Easy    | ⚠️ GPU needed  | ✅ Easy    |
| **GPU required**      | No         | Yes            | No         |
| **Real-time capable** | Yes        | With GPU       | Yes        |

______________________________________________________________________

## 6. RTMLib Quick Start

### 6.1 Installation

```bash
pip install rtmlib
```

### 6.2 Basic Usage

```python
from rtmlib import Body, Wholebody, PoseTracker

# Body pose (17 keypoints) - for jumps, sprints
body = Body(
    mode='balanced',  # 'lightweight', 'balanced', 'performance'
    backend='onnxruntime',
    device='cpu'  # or 'cuda', 'mps'
)

# Process frame
keypoints, scores = body(frame)
# keypoints: (num_people, 17, 2)
# scores: (num_people, 17)
```

### 6.3 Available Models

| Model           | Keypoints | Use Case                |
| --------------- | --------- | ----------------------- |
| `Body`          | 17        | Jumps, sprints, general |
| `Body` (26-kpt) | 26        | Body + feet detail      |
| `Wholebody`     | 133       | Body + hands + face     |
| `RTMO`          | 17        | One-stage (faster)      |

### 6.4 Modes

| Mode          | Speed   | Accuracy | Recommended For   |
| ------------- | ------- | -------- | ----------------- |
| `lightweight` | Fastest | Good     | Real-time preview |
| `balanced`    | Medium  | Better   | Production        |
| `performance` | Slowest | Best     | Detailed analysis |

______________________________________________________________________

## 7. Architecture Recommendation

### 7.1 Hybrid Approach

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (Vercel)                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MediaPipe (TensorFlow.js)                      │   │
│  │  - Quick preview during upload                  │   │
│  │  - Low-latency real-time feedback               │   │
│  │  - Client-side, no server round-trip            │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend (Cloud Run)                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  RTMLib (RTMPose)                               │   │
│  │  - High-accuracy analysis                       │   │
│  │  - All sports: jumps, sprints, lifts, wallball  │   │
│  │  - Unified pipeline, same code as local dev    │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Implementation Example

```python
# kinemotion/core/pose_rtmpose.py
from rtmlib import Body
import numpy as np

class RTMPoseTracker:
    """RTMPose-based pose tracker for multi-sport analysis."""

    def __init__(self, mode: str = 'balanced'):
        self.tracker = Body(
            mode=mode,
            backend='onnxruntime',
            device='cpu'
        )

    def process_frame(self, frame: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Process single frame, return keypoints and scores."""
        return self.tracker(frame)

    def get_landmark_by_name(self, keypoints: np.ndarray, name: str) -> np.ndarray:
        """Get specific landmark by name (COCO format)."""
        COCO_KEYPOINTS = {
            'nose': 0, 'left_eye': 1, 'right_eye': 2,
            'left_ear': 3, 'right_ear': 4,
            'left_shoulder': 5, 'right_shoulder': 6,
            'left_elbow': 7, 'right_elbow': 8,
            'left_wrist': 9, 'right_wrist': 10,
            'left_hip': 11, 'right_hip': 12,
            'left_knee': 13, 'right_knee': 14,
            'left_ankle': 15, 'right_ankle': 16,
        }
        return keypoints[:, COCO_KEYPOINTS[name], :]
```

______________________________________________________________________

## 8. Migration Path

### Phase 1: Keep MediaPipe for MVP (Current)

- Validate jump analysis with real users
- Gather feedback on accuracy needs
- No code changes needed

### Phase 2: Add RTMLib Backend (Multi-Sport)

- Install RTMLib alongside MediaPipe
- Implement unified pose interface
- Route to RTMPose for detailed analysis

### Phase 3: Consolidate (Optional)

- RTMLib for all server-side analysis
- MediaPipe only for browser preview
- Single pipeline for all sports

______________________________________________________________________

## 9. Key Takeaways

1. **RTMPose wins for multi-sport:** Best accuracy across jumps, sprints, weightlifting, and wall ball

1. **RTMLib solves Apple Silicon:** No CUDA, no MMPose, just `pip install rtmlib`

1. **MediaPipe still valuable:** Browser deployment via TensorFlow.js for real-time preview

1. **OpenPose is deprecated:** Stale (2021), complex setup, no clear advantage

1. **Domain-specific training matters:** 69% improvement with athletic-specific fine-tuning

1. **Motion blur is real:** MediaPipe struggles with fast movements; RTMPose is more robust

______________________________________________________________________

## 10. References

### Validation Studies

1. **Running Biomechanics (2025):** Gomez et al. "Comparison of Visual Trackers for Biomechanical Analysis of Running" arXiv:2505.04713

1. **Vertical Jump (2024):** "Advancing Field-Based Vertical Jump Analysis" PMC11677309

1. **Athletic Movements (2025):** Yeung et al. "AthletePose3D" arXiv:2503.07499

1. **Motion Blur (2023):** Pu et al. "Robustness Evaluation in Hand Pose Estimation" arXiv:2303.04566

### Software

- **RTMLib:** https://github.com/Tau-J/rtmlib
- **MMPose:** https://github.com/open-mmlab/mmpose
- **MediaPipe:** https://github.com/google/mediapipe
- **DWPose:** https://github.com/IDEA-Research/DWPose

### Apple Silicon Issues

- MMCV M1 Issues: https://github.com/open-mmlab/mmcv/issues/2250
- ARM64 Installation: https://github.com/open-mmlab/mmcv/issues/2218

______________________________________________________________________

## Document History

- **Version 1.0** - December 21, 2025: Initial research and comparison
- **Tested On:** MacBook Pro M1 Pro, 16GB RAM
- **Research Sources:** December 2025 web search, validation studies 2023-2025
