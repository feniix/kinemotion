# RTMPose vs RTMLib vs MediaPipe: Detailed Technical Comparison

**Last Updated:** December 2025

This document provides a comprehensive technical comparison between RTMPose, RTMLib, and MediaPipe for pose estimation, specifically focused on kinemotion's multi-sport analysis use case.

______________________________________________________________________

## Executive Summary

| Aspect          | RTMPose                     | RTMLib                          | MediaPipe                 |
| --------------- | --------------------------- | ------------------------------- | ------------------------- |
| **What it is**  | Neural network architecture | Deployment wrapper for RTMPose  | End-to-end pose solution  |
| **Developer**   | OpenMMLab (Shanghai AI Lab) | Tau-J (community)               | Google                    |
| **Primary Use** | Research & training         | Production deployment           | Mobile/browser apps       |
| **Best For**    | Maximum accuracy            | Apple Silicon / easy deployment | Cross-platform simplicity |

**Key Insight:** RTMPose is the *model architecture*, RTMLib is a *deployment tool* that runs RTMPose models. They're complementary, not competitors. MediaPipe is a completely separate solution.

______________________________________________________________________

## 1. Understanding the Relationship

### RTMPose (The Model)

- **Full name:** Real-Time Models for Multi-Person Pose Estimation
- **Paper:** arXiv:2303.07399 (March 2023)
- **Framework:** Part of MMPose (OpenMMLab ecosystem)
- **Purpose:** Train and develop pose estimation models
- **Dependencies:** MMPose, MMCV, PyTorch

### RTMLib (The Deployment Tool)

- **Full name:** RTMLib - Lightweight RTMPose wrapper
- **Repository:** github.com/Tau-J/rtmlib
- **Purpose:** Run pre-trained RTMPose models WITHOUT MMPose dependencies
- **Dependencies:** numpy, opencv, onnxruntime (minimal)

### MediaPipe (The Alternative)

- **Full name:** MediaPipe Pose Landmarker
- **Developer:** Google
- **Purpose:** Cross-platform pose estimation (mobile, browser, desktop)
- **Dependencies:** mediapipe package

```
┌─────────────────────────────────────────────────────────────┐
│                    POSE ESTIMATION LANDSCAPE                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐     exports      ┌─────────────┐          │
│  │   RTMPose   │ ──────────────▶  │   RTMLib    │          │
│  │  (MMPose)   │   ONNX models    │ (Deployer)  │          │
│  └─────────────┘                  └─────────────┘          │
│        │                                │                   │
│        │ Training                       │ Inference         │
│        │ Research                       │ Production        │
│        ▼                                ▼                   │
│  ┌─────────────────────────────────────────────────┐       │
│  │              YOUR APPLICATION                    │       │
│  └─────────────────────────────────────────────────┘       │
│                          ▲                                  │
│                          │ Alternative                      │
│                          │                                  │
│                   ┌─────────────┐                          │
│                   │  MediaPipe  │                          │
│                   │  (Google)   │                          │
│                   └─────────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

______________________________________________________________________

## 2. Architecture Comparison

### 2.1 RTMPose Architecture

```
Input Image
     │
     ▼
┌─────────────────┐
│  Person Detector │  ◄── RTMDet-nano (optional)
│  (Top-Down)      │
└────────┬────────┘
         │ Crop each person
         ▼
┌─────────────────┐
│  CSPNeXt        │  ◄── Backbone (designed for detection tasks)
│  Backbone       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SimCC Head     │  ◄── Coordinate classification (not heatmap)
│  + GAU Attention│      X and Y predicted separately
└────────┬────────┘
         │
         ▼
   17 Keypoints (COCO format)
```

**Key Innovations:**

1. **SimCC (Simple Coordinate Classification):** Treats localization as classification, not regression
2. **CSPNeXt Backbone:** Optimized for detection tasks, not ImageNet classification
3. **GAU (Gated Attention Unit):** Lightweight transformer for keypoint refinement
4. **Top-Down Paradigm:** Detect person first, then estimate pose

### 2.2 MediaPipe Architecture

```
Input Image
     │
     ▼
┌─────────────────┐
│  BlazePose      │  ◄── Single-shot detector + pose
│  Detector       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Pose Landmark  │  ◄── Heatmap-based regression
│  Model          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ROI Tracking   │  ◄── Temporal smoothing for video
│  (for video)    │
└────────┬────────┘
         │
         ▼
   33 Landmarks (MediaPipe format)
```

**Key Features:**

1. **BlazePose:** Optimized for mobile inference
2. **Heatmap Regression:** Traditional approach with upsampling
3. **ROI Tracking:** Reduces computation in video by tracking previous detection
4. **Single-Person Optimized:** Best performance with one subject

______________________________________________________________________

## 3. Accuracy Benchmarks

### 3.1 COCO Keypoint Detection (AP @ IoU 0.50:0.95)

| Model               | Input Size | AP       | AP50  | AP75  | AR   | Params | GFLOPs |
| ------------------- | ---------- | -------- | ----- | ----- | ---- | ------ | ------ |
| **RTMPose-t**       | 256×192    | 68.5     | 89.2  | 75.8  | 73.3 | 3.3M   | 0.36   |
| **RTMPose-s**       | 256×192    | 72.2     | 89.9  | 78.6  | 77.1 | 5.5M   | 0.68   |
| **RTMPose-m**       | 256×192    | 75.8     | 90.6  | 81.8  | 80.5 | 13.6M  | 1.93   |
| **RTMPose-l**       | 256×192    | 76.5     | 90.7  | 82.8  | 81.2 | 27.7M  | 4.16   |
| **RTMPose-x**       | 384×288    | 79.2     | 92.2  | 85.7  | 83.3 | 49.4M  | 17.3   |
| **MediaPipe Heavy** | 256×256    | ~70-72\* | ~88\* | ~76\* | -    | ~6M    | ~1.5   |
| **MediaPipe Full**  | 256×256    | ~68-70\* | ~87\* | ~74\* | -    | ~3M    | ~0.8   |
| **MediaPipe Lite**  | 256×256    | ~62-65\* | ~84\* | ~70\* | -    | ~1M    | ~0.3   |

\*MediaPipe values are estimated from various benchmarks as Google doesn't publish official COCO AP scores.

### 3.2 Sports/Athletic Movement Accuracy

From "Comparison of Visual Trackers for Biomechanical Analysis of Running" (arXiv:2505.04713):

| Tracker       | Joint Angle RMSE (degrees) | Ranking |
| ------------- | -------------------------- | ------- |
| **RTMPose**   | **5.62°**                  | **#1**  |
| MoveNet       | 6.14°                      | #2      |
| **MediaPipe** | 6.33°                      | #3      |
| CoTracker3    | 24.83°                     | #4      |
| PoseNet       | 33.44°                     | #5      |

**Key Finding:** RTMPose is **12% more accurate** than MediaPipe for running/sprint biomechanics.

### 3.3 Vertical Jump Analysis

From "Advancing Field-Based Vertical Jump Analysis" (PMC11677309):

| Metric               | RTMPose/MMPose | Interpretation |
| -------------------- | -------------- | -------------- |
| Velocity correlation | r = 0.992      | Excellent      |
| Jump height ICC      | 0.985          | Excellent      |
| Propulsive phase ICC | 0.974          | Excellent      |
| Take-off phase ICC   | 0.971          | Excellent      |

______________________________________________________________________

## 4. Speed Benchmarks

### 4.1 RTMPose Speed (from official paper)

| Model     | CPU (i7-11700) | GPU (GTX 1660 Ti) | Mobile (SD865) |
| --------- | -------------- | ----------------- | -------------- |
| RTMPose-t | 150+ FPS       | 800+ FPS          | 90+ FPS        |
| RTMPose-s | 120+ FPS       | 600+ FPS          | 70+ FPS        |
| RTMPose-m | 90+ FPS        | 430+ FPS          | 35+ FPS        |
| RTMPose-l | 50+ FPS        | 300+ FPS          | 20+ FPS        |

### 4.2 RTMLib Speed (Apple Silicon - tested)

| Mode          | M1 Pro CPU | Use Case            |
| ------------- | ---------- | ------------------- |
| `lightweight` | 25-40 FPS  | Real-time preview   |
| `balanced`    | 15-25 FPS  | Production analysis |
| `performance` | 8-15 FPS   | Maximum accuracy    |

### 4.3 MediaPipe Speed

| Model | CPU     | Mobile  | Browser |
| ----- | ------- | ------- | ------- |
| Lite  | 50+ FPS | 30+ FPS | 30+ FPS |
| Full  | 30+ FPS | 25+ FPS | 20+ FPS |
| Heavy | 15+ FPS | 15+ FPS | 10+ FPS |

______________________________________________________________________

## 5. Keypoint Comparison

### 5.1 Keypoint Count and Format

| System                | Keypoints | Format         | Notes                    |
| --------------------- | --------- | -------------- | ------------------------ |
| **RTMPose Body**      | 17        | COCO           | Standard body joints     |
| **RTMPose Body (26)** | 26        | Halpe          | Includes toe/heel detail |
| **RTMPose Wholebody** | 133       | COCO-WholeBody | Body + hands + face      |
| **MediaPipe Pose**    | 33        | MediaPipe      | Body + basic hands/feet  |

### 5.2 COCO 17 Keypoints (RTMPose Default)

```
      0: nose
     / \
    1   2  (left/right eye)
   /     \
  3       4  (left/right ear)
   \     /
    5   6  (left/right shoulder)
    |   |
    7   8  (left/right elbow)
    |   |
    9  10  (left/right wrist)
    |   |
   11  12  (left/right hip)
    |   |
   13  14  (left/right knee)
    |   |
   15  16  (left/right ankle)
```

### 5.3 MediaPipe 33 Landmarks

```
MediaPipe includes additional landmarks:
- Face: nose, eyes (inner/outer), ears, mouth
- Body: shoulders, elbows, wrists, hips, knees, ankles
- Hands: thumb, index, pinky (tips only)
- Feet: heel, foot index (big toe tip)
```

### 5.4 Keypoint Mapping (RTMLib COCO → MediaPipe)

```python
# If you need to convert between formats:
COCO_TO_MEDIAPIPE = {
    0: 0,    # nose
    1: 2,    # left_eye → left_eye_outer (approximate)
    2: 5,    # right_eye → right_eye_outer
    3: 7,    # left_ear
    4: 8,    # right_ear
    5: 11,   # left_shoulder
    6: 12,   # right_shoulder
    7: 13,   # left_elbow
    8: 14,   # right_elbow
    9: 15,   # left_wrist
    10: 16,  # right_wrist
    11: 23,  # left_hip
    12: 24,  # right_hip
    13: 25,  # left_knee
    14: 26,  # right_knee
    15: 27,  # left_ankle
    16: 28,  # right_ankle
}
```

______________________________________________________________________

## 6. Installation & Setup

### 6.1 RTMLib (Recommended for Production)

```bash
# Simple installation - works on Apple Silicon!
pip install rtmlib

# Dependencies (automatically installed):
# - numpy
# - opencv-python
# - onnxruntime
```

**Usage:**

```python
from rtmlib import Body, Wholebody, PoseTracker
import cv2

# Initialize (downloads models automatically on first use)
body = Body(
    mode='balanced',       # 'lightweight', 'balanced', 'performance'
    backend='onnxruntime', # 'onnxruntime', 'openvino', 'opencv'
    device='cpu'           # 'cpu', 'cuda', 'mps'
)

# Process frame
frame = cv2.imread('image.jpg')
keypoints, scores = body(frame)
# keypoints: (num_people, 17, 2) - x, y coordinates
# scores: (num_people, 17) - confidence per keypoint
```

### 6.2 RTMPose (Full MMPose - for training/research)

```bash
# Requires MMPose ecosystem
pip install openmim
mim install mmengine
mim install "mmcv>=2.0.0"
mim install "mmdet>=3.0.0"
mim install "mmpose>=1.0.0"

# Note: May have issues on Apple Silicon due to MMCV
```

**Usage:**

```python
from mmpose.apis import inference_topdown, init_model
from mmdet.apis import inference_detector, init_detector

# Initialize models
det_model = init_detector(det_config, det_checkpoint, device='cuda:0')
pose_model = init_model(pose_config, pose_checkpoint, device='cuda:0')

# Detect persons
det_results = inference_detector(det_model, image)

# Estimate poses
pose_results = inference_topdown(pose_model, image, det_results)
```

### 6.3 MediaPipe

```bash
pip install mediapipe
```

**Usage:**

```python
import mediapipe as mp
import cv2

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Initialize
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,      # 0=Lite, 1=Full, 2=Heavy
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Process frame
image = cv2.imread('image.jpg')
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
results = pose.process(image_rgb)

# Access landmarks
if results.pose_landmarks:
    for landmark in results.pose_landmarks.landmark:
        x, y, z = landmark.x, landmark.y, landmark.z
        visibility = landmark.visibility
```

______________________________________________________________________

## 7. Platform Support

| Feature                 | RTMLib        | RTMPose (MMPose) | MediaPipe        |
| ----------------------- | ------------- | ---------------- | ---------------- |
| **Linux x86**           | ✅ Native     | ✅ Native        | ✅ Native        |
| **Windows**             | ✅ Native     | ✅ Native        | ✅ Native        |
| **macOS Intel**         | ✅ Native     | ⚠️ Partial       | ✅ Native        |
| **macOS Apple Silicon** | ✅ **Native** | ❌ MMCV issues   | ✅ Native        |
| **iOS**                 | ❌            | ❌               | ✅ Native SDK    |
| **Android**             | ❌            | ❌               | ✅ Native SDK    |
| **Browser (JS)**        | ❌            | ❌               | ✅ TensorFlow.js |
| **Raspberry Pi**        | ✅ (ARM64)    | ⚠️ Slow          | ✅ Native        |
| **NVIDIA Jetson**       | ✅ CUDA       | ✅ CUDA          | ✅ Native        |
| **GPU (CUDA)**          | ✅            | ✅               | ⚠️ Limited       |
| **GPU (MPS)**           | ✅            | ❌               | ❌               |

______________________________________________________________________

## 8. Feature Comparison

| Feature                    | RTMLib            | RTMPose (MMPose) | MediaPipe                  |
| -------------------------- | ----------------- | ---------------- | -------------------------- |
| **Multi-person detection** | ✅ Native         | ✅ Native        | ⚠️ Single-person optimized |
| **Real-time video**        | ✅                | ✅               | ✅                         |
| **3D pose estimation**     | ✅ (RTMW3D)       | ✅               | ✅ (world landmarks)       |
| **Whole-body (133 kpts)**  | ✅                | ✅               | ❌ (33 only)               |
| **Temporal smoothing**     | ❌ Manual         | ❌ Manual        | ✅ Built-in                |
| **Segmentation mask**      | ❌                | ❌               | ✅ Optional                |
| **Custom training**        | ❌ Inference only | ✅ Full training | ❌                         |
| **Model fine-tuning**      | ❌                | ✅               | ❌                         |
| **ONNX export**            | ✅ Pre-exported   | ✅               | ⚠️ Limited                 |
| **TensorRT support**       | ✅                | ✅               | ⚠️ Limited                 |
| **OpenVINO support**       | ✅                | ✅               | ❌                         |

______________________________________________________________________

## 9. Motion Blur & Fast Movement Handling

### 9.1 Robustness Comparison

From "Robustness Evaluation in Hand Pose Estimation" (arXiv:2303.04566):

| System        | Motion Blur Handling                | Fast Movement | Occlusion   |
| ------------- | ----------------------------------- | ------------- | ----------- |
| **RTMPose**   | ✅ Excellent                        | ✅ Robust     | ✅ Good     |
| **MediaPipe** | ⚠️ 50%+ failures with diagonal blur | ⚠️ Struggles  | ⚠️ Moderate |
| **OpenPose**  | ✅ Good                             | ✅ Good       | ✅ Good     |

### 9.2 Why RTMPose Handles Motion Better

1. **SimCC vs Heatmap:** SimCC's coordinate classification is more robust to spatial noise
2. **CSPNeXt Backbone:** Designed for detection, better feature extraction
3. **GAU Attention:** Global context helps with partial occlusion
4. **Top-Down Approach:** Person detection isolates subjects

### 9.3 Why MediaPipe Struggles

1. **Heatmap Regression:** Sensitive to spatial blur
2. **Mobile-Optimized:** Accuracy sacrificed for speed
3. **Single-Person Focus:** Less robust multi-person handling
4. **ROI Tracking:** Can lose track during fast movements

______________________________________________________________________

## 10. Use Case Recommendations

### 10.1 When to Use RTMLib

✅ **Best for:**

- Multi-sport analysis (jumps, sprints, lifts, wall ball)
- Apple Silicon development (M1/M2/M3)
- Production backends (Cloud Run, AWS Lambda)
- Maximum accuracy requirements
- Multi-person scenarios

❌ **Not ideal for:**

- Browser-based applications
- Mobile apps (iOS/Android native)
- Custom model training

### 10.2 When to Use RTMPose (Full MMPose)

✅ **Best for:**

- Research and development
- Custom model training
- Fine-tuning on domain-specific data
- Exploring architectural modifications

❌ **Not ideal for:**

- Apple Silicon deployment
- Quick prototyping
- Production without GPU

### 10.3 When to Use MediaPipe

✅ **Best for:**

- Browser-based applications (TensorFlow.js)
- Mobile apps (iOS/Android)
- Quick prototypes
- Single-person tracking
- Cross-platform consistency

❌ **Not ideal for:**

- Research-grade accuracy
- Fast movement analysis (sprints, throws)
- Multi-person scenarios
- Detailed biomechanical analysis

______________________________________________________________________

## 11. Integration Examples

### 11.1 RTMLib for kinemotion

```python
"""RTMLib-based pose tracker for kinemotion multi-sport analysis."""
from rtmlib import Body
import numpy as np
from typing import NamedTuple

class PoseResult(NamedTuple):
    keypoints: np.ndarray  # (17, 2) - x, y
    scores: np.ndarray     # (17,) - confidence

class RTMPoseTracker:
    """RTMPose-based tracker using RTMLib for deployment."""

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

    def __init__(self, mode: str = 'balanced'):
        """Initialize RTMPose tracker.

        Args:
            mode: 'lightweight', 'balanced', or 'performance'
        """
        self.tracker = Body(
            mode=mode,
            backend='onnxruntime',
            device='cpu'  # or 'cuda', 'mps'
        )

    def process_frame(self, frame: np.ndarray) -> list[PoseResult]:
        """Process single frame, return list of poses."""
        keypoints, scores = self.tracker(frame)

        results = []
        for i in range(len(keypoints)):
            results.append(PoseResult(
                keypoints=keypoints[i],
                scores=scores[i]
            ))
        return results

    def get_joint(self, result: PoseResult, name: str) -> tuple[float, float, float]:
        """Get specific joint coordinates and confidence."""
        idx = self.COCO_KEYPOINTS[name]
        x, y = result.keypoints[idx]
        conf = result.scores[idx]
        return x, y, conf

    def calculate_angle(self, result: PoseResult,
                       joint1: str, joint2: str, joint3: str) -> float:
        """Calculate angle at joint2 formed by joint1-joint2-joint3."""
        p1 = result.keypoints[self.COCO_KEYPOINTS[joint1]]
        p2 = result.keypoints[self.COCO_KEYPOINTS[joint2]]
        p3 = result.keypoints[self.COCO_KEYPOINTS[joint3]]

        v1 = p1 - p2
        v2 = p3 - p2

        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1, 1))
        return np.degrees(angle)
```

### 11.2 MediaPipe for Browser Preview

```typescript
// Browser-side preview using MediaPipe TensorFlow.js
import { Pose } from '@mediapipe/pose';

const pose = new Pose({
  locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
});

pose.setOptions({
  modelComplexity: 1,
  smoothLandmarks: true,
  enableSegmentation: false,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});

pose.onResults((results) => {
  if (results.poseLandmarks) {
    // Draw landmarks on canvas
    drawLandmarks(results.poseLandmarks);
  }
});

// Process video frame
async function processFrame(videoElement: HTMLVideoElement) {
  await pose.send({ image: videoElement });
}
```

______________________________________________________________________

## 12. Migration Path: MediaPipe → RTMLib

### 12.1 Code Changes

```python
# BEFORE: MediaPipe
import mediapipe as mp
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=1)

results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
if results.pose_landmarks:
    landmarks = results.pose_landmarks.landmark
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    x, y = left_hip.x * width, left_hip.y * height

# AFTER: RTMLib
from rtmlib import Body
body = Body(mode='balanced')

keypoints, scores = body(frame)
if len(keypoints) > 0:
    left_hip = keypoints[0][11]  # COCO index 11 = left_hip
    x, y = left_hip[0], left_hip[1]  # Already in pixel coordinates
```

### 12.2 Key Differences

| Aspect             | MediaPipe               | RTMLib                  |
| ------------------ | ----------------------- | ----------------------- |
| Input format       | RGB                     | BGR (OpenCV default) ✅ |
| Output coordinates | Normalized (0-1)        | Pixel coordinates       |
| Multi-person       | First person only       | All detected persons    |
| Keypoint indices   | MediaPipe enum          | COCO indices            |
| Confidence         | Per-landmark visibility | Per-keypoint score      |

______________________________________________________________________

## 13. Summary Table

| Criteria               | RTMLib    | RTMPose (MMPose) | MediaPipe    |
| ---------------------- | --------- | ---------------- | ------------ |
| **Accuracy (COCO AP)** | 72-79%    | 72-79%           | ~65-72%      |
| **Speed (CPU)**        | 15-40 FPS | 50-150 FPS       | 15-50 FPS    |
| **Apple Silicon**      | ✅ Native | ❌ Issues        | ✅ Native    |
| **Browser Support**    | ❌        | ❌               | ✅           |
| **Mobile Native**      | ❌        | ❌               | ✅           |
| **Multi-Person**       | ✅        | ✅               | ⚠️ Limited   |
| **Motion Blur**        | ✅ Robust | ✅ Robust        | ⚠️ Struggles |
| **Setup Complexity**   | Very Low  | High             | Low          |
| **Custom Training**    | ❌        | ✅               | ❌           |
| **Dependencies**       | Minimal   | Heavy            | Moderate     |

______________________________________________________________________

## 14. Conclusion

For kinemotion's multi-sport analysis platform:

1. **Use RTMLib** for:

   - Backend analysis (Cloud Run)
   - Local development (Apple Silicon)
   - All sports: jumps, sprints, lifts, wall ball

2. **Use MediaPipe** for:

   - Browser-based real-time preview
   - Mobile app development (future)

3. **Avoid full MMPose** unless:

   - Training custom models
   - Research/experimentation
   - Have CUDA-capable hardware

**Recommended Architecture:**

```
Frontend (Browser) ──► MediaPipe (TensorFlow.js) ──► Quick preview
        │
        ▼
Backend (Cloud Run) ──► RTMLib (RTMPose) ──► Detailed analysis
```

______________________________________________________________________

## 15. Kinemotion Keypoint Compatibility Analysis

This section analyzes keypoint compatibility between RTMPose and kinemotion's current MediaPipe implementation for CMJ and drop jump analysis.

### 15.1 Keypoints Currently Used in Kinemotion

From `src/kinemotion/core/pose.py`, kinemotion tracks these landmarks:

| Landmark           | Used For                       | In COCO 17? | In Halpe 26? |
| ------------------ | ------------------------------ | ----------- | ------------ |
| `nose`             | Center of Mass estimation      | ✅ Yes      | ✅ Yes       |
| `left_shoulder`    | Hip angle, CoM                 | ✅ Yes      | ✅ Yes       |
| `right_shoulder`   | Hip angle, CoM                 | ✅ Yes      | ✅ Yes       |
| `left_hip`         | Triple extension, CoM          | ✅ Yes      | ✅ Yes       |
| `right_hip`        | Triple extension, CoM          | ✅ Yes      | ✅ Yes       |
| `left_knee`        | Triple extension, CoM          | ✅ Yes      | ✅ Yes       |
| `right_knee`       | Triple extension, CoM          | ✅ Yes      | ✅ Yes       |
| `left_ankle`       | Triple extension, CoM          | ✅ Yes      | ✅ Yes       |
| `right_ankle`      | Triple extension, CoM          | ✅ Yes      | ✅ Yes       |
| `left_heel`        | Ankle angle (fallback)         | ❌ **No**   | ✅ Yes       |
| `right_heel`       | Ankle angle (fallback)         | ❌ **No**   | ✅ Yes       |
| `left_foot_index`  | Ankle angle (primary, toe tip) | ❌ **No**   | ✅ Yes       |
| `right_foot_index` | Ankle angle (primary, toe tip) | ❌ **No**   | ✅ Yes       |

### 15.2 The Gap: Foot Landmarks

**RTMPose Body (17 keypoints, COCO format)** includes:

- nose, eyes, ears
- shoulders, elbows, wrists
- hips, knees, ankles

**NOT included in COCO 17:**

- `heel` - used by kinemotion for ankle angle fallback calculation
- `foot_index` / toe - used by kinemotion for accurate plantarflexion measurement

### 15.3 Solution: RTMPose Halpe 26-Keypoint Model

RTMLib offers a **Halpe 26-keypoint model** (from AlphaPose) that adds detailed foot landmarks:

```
Halpe 26 Keypoints:
├── 0-16: Same as COCO 17 (nose through ankles)
├── 17: Head (top)
├── 18: Neck
├── 19: Hip (center/pelvis)
└── 20-25: Foot detail
    ├── 20: left_big_toe
    ├── 21: right_big_toe
    ├── 22: left_small_toe
    ├── 23: right_small_toe
    ├── 24: left_heel
    └── 25: right_heel
```

**Note:** "COCO 26" is not a standard - the correct name is **Halpe 26** (from Halpe-FullBody dataset).

**Mapping to kinemotion:**

- `foot_index` → `big_toe` (functionally equivalent - toe tip)
- `heel` → `heel` (direct match)

### 15.4 Migration Mapping

```python
# Kinemotion landmark mapping: MediaPipe → RTMPose Halpe-26
KINEMOTION_TO_HALPE26 = {
    # Core body (same as COCO 17)
    'nose': 0,
    'left_shoulder': 5,
    'right_shoulder': 6,
    'left_hip': 11,
    'right_hip': 12,
    'left_knee': 13,
    'right_knee': 14,
    'left_ankle': 15,
    'right_ankle': 16,

    # Foot landmarks (Halpe 26 additions)
    'left_heel': 24,
    'right_heel': 25,
    'left_foot_index': 20,   # big_toe = foot_index equivalent
    'right_foot_index': 21,  # big_toe = foot_index equivalent
}
```

### 15.5 Joint Angle Calculation Compatibility

Kinemotion's joint angle calculations (from `src/kinemotion/countermovement_jump/joint_angles.py`):

| Calculation     | Required Landmarks                           | RTMPose 26 Support |
| --------------- | -------------------------------------------- | ------------------ |
| **Ankle Angle** | foot_index → ankle → knee (or heel fallback) | ✅ Full support    |
| **Knee Angle**  | ankle → knee → hip                           | ✅ Full support    |
| **Hip Angle**   | knee → hip → shoulder                        | ✅ Full support    |
| **Trunk Tilt**  | hip, shoulder                                | ✅ Full support    |

### 15.6 What About COCO 17 Only?

If using standard COCO 17 keypoints (without foot detail):

**Option A: Modified ankle angle calculation**

- Use only the ankle-knee line with geometric approximation
- Less accurate for plantarflexion measurement
- Acceptable for basic analysis

**Option B: Skip ankle angle**

- Focus on knee and hip angles for triple extension
- These are the primary indicators anyway
- Ankle angle is supplementary

### 15.7 Recommendation for Kinemotion

**Use RTMPose Halpe 26-keypoint model via RTMLib:**

```python
from rtmlib import Body

# Use Halpe 26 for foot landmarks
# Check RTMLib docs for exact parameter name
body = Body(
    mode='balanced',
    backend='onnxruntime',
    device='cpu',
    to_openpose=False,  # Use native format
)
```

**Note:** Verify the exact RTMLib API for selecting Halpe 26 vs COCO 17 models. The library may auto-download different model variants.

This provides:

- All keypoints currently used for CMJ/drop jump analysis
- Better accuracy than MediaPipe (5.6° vs 6.3° RMSE)
- Native Apple Silicon support
- No loss of functionality

### 15.8 Summary

| Question                                       | Answer                                |
| ---------------------------------------------- | ------------------------------------- |
| Does RTMPose support all kinemotion keypoints? | ✅ Yes, with Halpe 26-keypoint model  |
| Can we migrate without algorithm changes?      | ✅ Yes, only index mapping needed     |
| Is COCO 17 sufficient?                         | ⚠️ Partial - loses ankle angle detail |
| Do we need face/hand keypoints?                | ❌ No - not used in jump analysis     |

### 15.9 Keypoint Format Reference

| Format             | Keypoints | Source                     | Foot Detail |
| ------------------ | --------- | -------------------------- | ----------- |
| **COCO**           | 17        | MS COCO dataset            | ❌ No       |
| **Halpe**          | 26        | AlphaPose / Halpe-FullBody | ✅ Yes      |
| **COCO-WholeBody** | 133       | COCO-WholeBody extension   | ✅ Yes      |

**Important:** "COCO 26" does not exist as a standard. Use "Halpe 26" for the 26-keypoint format with foot landmarks.

______________________________________________________________________

## 16. References

1. Jiang, T., et al. (2023). "RTMPose: Real-Time Multi-Person Pose Estimation based on MMPose." arXiv:2303.07399
2. Bazarevsky, V., et al. (2020). "BlazePose: On-device Real-time Body Pose Tracking." arXiv:2006.10204
3. Gomez, et al. (2025). "Comparison of Visual Trackers for Biomechanical Analysis of Running." arXiv:2505.04713
4. RTMLib Repository: https://github.com/Tau-J/rtmlib
5. MMPose Documentation: https://mmpose.readthedocs.io/
6. MediaPipe Pose: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker

______________________________________________________________________

**Document History:**

- December 21, 2025: Added kinemotion keypoint compatibility analysis (Section 15)
- December 21, 2025: Initial comprehensive comparison
