# 📋 RTMLib/RTMPose Feasibility Evaluation Plan

**Goal**: Determine if RTMLib/RTMPose can replace MediaPipe for kinemotion's pose estimation needs with equal or better **performance** and **accuracy**.

**Created**: December 23, 2025
**Status**: Planning
**Estimated Duration**: 11-17 days

______________________________________________________________________

## Executive Summary

This document outlines a rigorous, phased approach to evaluate whether RTMLib/RTMPose is a viable replacement for MediaPipe in kinemotion's pose estimation pipeline. The evaluation focuses on two primary dimensions:

1. **Performance**: Landmark extraction speed and efficiency
1. **Accuracy**: Landmark detection accuracy and downstream metric reliability

**Key Finding**: RTMLib's `BodyWithFeet` class using **Halpe26** format provides **all 13 landmarks** kinemotion requires, including the critical heel and foot_index (big_toe) landmarks.

______________________________________________________________________

## 🔑 Critical Technical Discovery

### Keypoint Mapping (Verified from mmpose source)

| Kinemotion Landmark | MediaPipe Index | RTMLib Halpe26 Index   |
| ------------------- | --------------- | ---------------------- |
| `nose`              | 0               | **0**                  |
| `left_shoulder`     | 11              | **5**                  |
| `right_shoulder`    | 12              | **6**                  |
| `left_hip`          | 23              | **11**                 |
| `right_hip`         | 24              | **12**                 |
| `left_knee`         | 25              | **13**                 |
| `right_knee`        | 26              | **14**                 |
| `left_ankle`        | 27              | **15**                 |
| `right_ankle`       | 28              | **16**                 |
| `left_heel`         | 29              | **24**                 |
| `right_heel`        | 30              | **25**                 |
| `left_foot_index`   | 31              | **20** (left_big_toe)  |
| `right_foot_index`  | 32              | **21** (right_big_toe) |

**✅ All 13 landmarks available in Halpe26 format**

### RTMLib Usage Pattern

```python
from rtmlib import BodyWithFeet, PoseTracker

tracker = PoseTracker(
    BodyWithFeet,
    det_frequency=7,      # Run detector every 7 frames
    mode='balanced',      # 'lightweight', 'balanced', 'performance'
    backend='onnxruntime',
    device='cpu'          # or 'cuda', 'mps'
)

keypoints, scores = tracker(frame)
# keypoints: (N, 23, 2) - N people, 23 keypoints, x/y pixel coordinates
# scores: (N, 23) - confidence per keypoint
```

______________________________________________________________________

## 📊 Current MediaPipe Performance Baseline

From performance analysis (see [pose-estimator-comparison-2025.md](./pose-estimator-comparison-2025.md)):

```
Total pose tracking: 7097ms (93% of total processing)
├─ Frame read:           2052ms (26.3%) - CONSTANT (regardless of estimator)
├─ Frame rotation:        631ms (8.1%)  - CONSTANT (regardless of estimator)
├─ MediaPipe inference:  4251ms (54.5%) - THIS IS WHAT WE'RE BENCHMARKING
└─ Landmark extraction:     3ms (0.0%)  - NEGLIGIBLE
```

**The only variable in this evaluation**: MediaPipe inference (4.25s) vs RTMLib inference

______________________________________________________________________

## 🗓️ Phased Evaluation Plan

### Phase 0: Proof of Concept

**Duration**: 1-2 days
**Goal**: Verify RTMLib works with kinemotion's requirements

#### Tasks

1. **Install dependencies**

   ```bash
   # Add to pyproject.toml (optional dependency group)
   uv add --optional benchmark rtmlib
   uv add --optional benchmark onnxruntime-silicon  # macOS ARM64
   # OR
   uv add --optional benchmark onnxruntime          # other platforms
   ```

1. **Write minimal test script** (`scripts/benchmark/test_rtmpose_poc.py`)

   ```python
   """Proof of concept: RTMLib landmark extraction."""
   import cv2
   import numpy as np
   from rtmlib import BodyWithFeet, PoseTracker

   # Initialize tracker
   tracker = PoseTracker(
       BodyWithFeet,
       det_frequency=7,
       mode='balanced',
       backend='onnxruntime',
       device='cpu'
   )

   # Load test frame
   frame = cv2.imread("samples/validation/test_frame.jpg")

   # Extract keypoints
   keypoints, scores = tracker(frame)

   # Verify output shape
   print(f"Detected {keypoints.shape[0]} people")
   print(f"Keypoints shape: {keypoints.shape}")  # Expected: (N, 23, 2)
   print(f"Scores shape: {scores.shape}")        # Expected: (N, 23)

   # Verify specific landmarks exist
   HALPE26_MAPPING = {
       'nose': 0, 'left_shoulder': 5, 'right_shoulder': 6,
       'left_hip': 11, 'right_hip': 12, 'left_knee': 13, 'right_knee': 14,
       'left_ankle': 15, 'right_ankle': 16,
       'left_heel': 24, 'right_heel': 25,
       'left_foot_index': 20, 'right_foot_index': 21,  # big_toe
   }

   if keypoints.shape[0] > 0:
       person = keypoints[0]  # First detected person
       for name, idx in HALPE26_MAPPING.items():
           x, y = person[idx]
           conf = scores[0][idx]
           print(f"  {name}: ({x:.1f}, {y:.1f}) confidence={conf:.3f}")
   ```

1. **Visual verification**: Overlay both systems' landmarks on same frame

   - Create side-by-side comparison image
   - Verify landmarks align visually

1. **Coordinate normalization test**

   - RTMLib returns pixel coordinates
   - Verify normalization: `x_norm = x / frame_width`, `y_norm = y / frame_height`

#### Decision Gate

| Outcome   | Criteria                                    | Action                             |
| --------- | ------------------------------------------- | ---------------------------------- |
| ✅ Pass   | All 13 landmarks detected, visually correct | Continue to Phase 1                |
| ⚠️ Issues | Some landmarks missing or incorrect         | Investigate, adjust mapping        |
| ❌ Fail   | Fundamental incompatibility                 | Stop evaluation, document findings |

#### Deliverables

- [ ] `scripts/benchmark/test_rtmpose_poc.py` - PoC script
- [ ] Visual comparison screenshots (MediaPipe vs RTMLib)
- [ ] Phase 0 status report (pass/fail with notes)

______________________________________________________________________

### Phase 1: Performance Benchmarking

**Duration**: 2-3 days
**Goal**: Quantify speed difference between MediaPipe and RTMLib

#### Methodology

Use kinemotion's existing `PerformanceTimer` infrastructure:

```python
"""Performance benchmark: MediaPipe vs RTMLib."""
from kinemotion.core.timing import PerformanceTimer
from kinemotion.core.pose import PoseTracker as MediaPipePoseTracker

# Setup timers
mp_timer = PerformanceTimer()
rtm_timer = PerformanceTimer()

# Benchmark MediaPipe
for frame in frames:
    with mp_timer.measure("inference"):
        mp_tracker.process_frame(frame)

# Benchmark RTMLib
for frame in frames:
    with rtm_timer.measure("inference"):
        rtm_tracker(frame)

# Compare
mp_fps = len(frames) / mp_timer.get_metrics()["inference"]
rtm_fps = len(frames) / rtm_timer.get_metrics()["inference"]
print(f"MediaPipe: {mp_fps:.1f} FPS")
print(f"RTMLib: {rtm_fps:.1f} FPS")
```

#### Test Matrix

| Video             | Duration | Resolution | Frames | MediaPipe (ms) | RTMLib (ms) | Ratio |
| ----------------- | -------- | ---------- | ------ | -------------- | ----------- | ----- |
| cmj_sample_1      | 10s      | 1080p      | ~300   | ?              | ?           | ?     |
| cmj_sample_2      | 30s      | 720p       | ~900   | ?              | ?           | ?     |
| dropjump_sample_1 | 60s      | 1080p      | ~1800  | ?              | ?           | ?     |

#### RTMLib Modes to Test

| Mode          | Expected Speed | Expected Accuracy | Use Case           |
| ------------- | -------------- | ----------------- | ------------------ |
| `lightweight` | Fastest        | Lower             | Real-time preview  |
| `balanced`    | Medium         | Medium            | Production default |
| `performance` | Slowest        | Highest           | Maximum accuracy   |

#### Additional Parameters to Test

- `det_frequency`: 1, 3, 7, 15 (detector runs every N frames)
- Higher = faster but may lose tracking on fast movements

#### Metrics to Collect

1. **Inference FPS** (frames per second, inference only)
1. **Total processing time** (including frame I/O)
1. **Memory usage** (via `tracemalloc`)
1. **Model initialization time** (cold start, first frame)
1. **Warm inference time** (subsequent frames)

#### Deliverables

- [ ] `scripts/benchmark/performance_benchmark.py` - Benchmark script
- [ ] `results/benchmark/performance_comparison.csv` - Raw data
- [ ] `docs/research/rtmpose-performance-results.md` - Analysis report

______________________________________________________________________

### Phase 2: Accuracy Benchmarking - Physics Validation

**Duration**: 3-5 days
**Goal**: Compare timing accuracy using physics ground truth

#### Why Physics Validation Works

For a freely falling object dropped from height `h`:

- Flight time: `t = √(2h/g)` where `g = 9.81 m/s²`
- This is **known physics** - it IS the ground truth

| Drop Height | Theoretical Flight Time |
| ----------- | ----------------------- |
| 0.5m        | 0.319s (319ms)          |
| 1.0m        | 0.452s (452ms)          |
| 1.5m        | 0.553s (553ms)          |

#### Test Setup

1. **Create/collect test videos**

   - Record object drops from known heights: 0.5m, 1.0m, 1.5m
   - 3 trials each = 9 videos minimum
   - 60fps recording recommended
   - Store in `samples/validation/physics/`

1. **Extend validation script**

   Modify `scripts/validate_known_heights.py`:

   ```python
   parser.add_argument(
       "--pose-estimator",
       choices=["mediapipe", "rtmpose-lightweight", "rtmpose-balanced", "rtmpose-performance"],
       default="mediapipe",
       help="Pose estimator to use for analysis"
   )
   ```

1. **Run validation for both systems**

   ```bash
   # MediaPipe baseline
   python scripts/validate_known_heights.py \
       --videos-dir samples/validation/physics/ \
       --pose-estimator mediapipe \
       --output results/benchmark/physics_mediapipe.json

   # RTMLib variants
   python scripts/validate_known_heights.py \
       --videos-dir samples/validation/physics/ \
       --pose-estimator rtmpose-balanced \
       --output results/benchmark/physics_rtmpose.json
   ```

#### Metrics

| Metric      | Formula                              | Target | Deal-Breaker |
| ----------- | ------------------------------------ | ------ | ------------ |
| MAE         | `mean(\|measured - theoretical\|)`   | ≤20ms  | >30ms        |
| RMSE        | `√(mean((measured - theoretical)²))` | ≤30ms  | >50ms        |
| Correlation | R² with theoretical                  | ≥0.99  | \<0.95       |
| Bias        | `mean(measured - theoretical)`       | ±10ms  | >±20ms       |

#### Analysis Script

```python
"""Analyze physics validation results."""
import json
import numpy as np
from scipy import stats

def analyze_results(results_path: str):
    with open(results_path) as f:
        results = json.load(f)

    measured = np.array([r['measured_flight_time_s'] for r in results])
    theoretical = np.array([r['theoretical_flight_time_s'] for r in results])

    errors = measured - theoretical

    return {
        'mae_ms': np.mean(np.abs(errors)) * 1000,
        'rmse_ms': np.sqrt(np.mean(errors**2)) * 1000,
        'bias_ms': np.mean(errors) * 1000,
        'r_squared': stats.pearsonr(measured, theoretical)[0]**2,
    }
```

#### Deliverables

- [ ] Test videos in `samples/validation/physics/`
- [ ] Extended `scripts/validate_known_heights.py`
- [ ] `results/benchmark/physics_mediapipe.json`
- [ ] `results/benchmark/physics_rtmpose.json`
- [ ] `docs/research/rtmpose-physics-validation.md` - Comparison report

______________________________________________________________________

### Phase 3: Accuracy Benchmarking - Metric Agreement

**Duration**: 2-3 days
**Goal**: Ensure downstream metrics agree between systems

#### Methodology

Run BOTH estimators on identical videos, compare derived metrics:

```python
"""Compare downstream metrics between pose estimators."""
from kinemotion import process_cmj_video

# Same video, different estimators
mp_metrics = process_cmj_video("video.mp4", pose_estimator="mediapipe")
rtm_metrics = process_cmj_video("video.mp4", pose_estimator="rtmpose")

# Compare key metrics
metrics_to_compare = [
    'flight_time_s',
    'jump_height_m',
    'ground_contact_time_s',
    'rsi',
]
```

#### Test Dataset

Use existing samples:

- `samples/cmjs/` - CMJ videos
- `samples/dropjumps/` - Drop jump videos
- `samples/validation/` - Validation videos

#### Agreement Analysis

```python
"""Statistical agreement analysis."""
import numpy as np
from scipy import stats

def compute_agreement(mp_values, rtm_values):
    """Compute agreement statistics between two measurement sets."""
    return {
        # Correlation
        'pearson_r': stats.pearsonr(mp_values, rtm_values)[0],
        'r_squared': stats.pearsonr(mp_values, rtm_values)[0]**2,

        # Differences
        'mean_diff': np.mean(mp_values - rtm_values),
        'std_diff': np.std(mp_values - rtm_values),
        'max_abs_diff': np.max(np.abs(mp_values - rtm_values)),

        # Agreement rate (within threshold)
        'agreement_10ms': np.mean(np.abs(mp_values - rtm_values) < 0.010),
        'agreement_20ms': np.mean(np.abs(mp_values - rtm_values) < 0.020),
    }
```

#### Success Criteria

| Metric         | Target Agreement        | Acceptable              | Deal-Breaker |
| -------------- | ----------------------- | ----------------------- | ------------ |
| Flight time    | R² ≥ 0.99, diff \< 10ms | R² ≥ 0.95, diff \< 20ms | R² \< 0.90   |
| Jump height    | R² ≥ 0.99, diff \< 1cm  | R² ≥ 0.95, diff \< 2cm  | R² \< 0.90   |
| Ground contact | R² ≥ 0.98, diff \< 15ms | R² ≥ 0.95, diff \< 25ms | R² \< 0.90   |
| RSI            | R² ≥ 0.98               | R² ≥ 0.95               | R² \< 0.90   |

#### Discrepancy Investigation

For videos where systems disagree significantly (>2 std deviations):

1. Visual inspection of debug videos from both systems
1. Frame-by-frame landmark comparison
1. Identify root cause (detection failure, jitter, occlusion, etc.)

#### Deliverables

- [ ] `scripts/benchmark/metric_agreement.py` - Analysis script
- [ ] `results/benchmark/metric_agreement.csv` - Per-video comparison
- [ ] `docs/research/rtmpose-metric-agreement.md` - Analysis report
- [ ] List of discrepancy videos with root cause analysis

______________________________________________________________________

### Phase 4: Robustness Testing

**Duration**: 2-3 days
**Goal**: Compare edge case handling between systems

#### Test 1: Camera Angle Sensitivity

MediaPipe known issue: Confuses left/right feet at 90° lateral view.

**Test Setup**:

- Record same jump from 3 angles: 45° oblique, 90° lateral, frontal
- Run both systems on all angles
- Compare detection rate and accuracy per angle

**Metrics**:

| Angle       | MediaPipe Detection Rate | RTMLib Detection Rate | Accuracy |
| ----------- | ------------------------ | --------------------- | -------- |
| 45° oblique | ?                        | ?                     | ?        |
| 90° lateral | ?                        | ?                     | ?        |
| Frontal     | ?                        | ?                     | ?        |

#### Test 2: Temporal Stability (Jitter Analysis)

**Methodology**:

1. Identify stationary frames (athlete standing still before jump)
1. Extract landmark positions over N consecutive stationary frames
1. Compute standard deviation of each landmark position
1. Lower std = more stable tracking

```python
"""Jitter analysis on stationary frames."""
import numpy as np

def compute_jitter(landmarks_over_frames: np.ndarray) -> dict:
    """
    Args:
        landmarks_over_frames: (N_frames, 13, 2) array of landmark positions
    Returns:
        Jitter statistics per landmark
    """
    # Compute std of each landmark across frames
    std_per_landmark = np.std(landmarks_over_frames, axis=0)  # (13, 2)

    return {
        'mean_jitter_px': np.mean(std_per_landmark),
        'max_jitter_px': np.max(std_per_landmark),
        'per_landmark': {name: std_per_landmark[i] for i, name in enumerate(LANDMARK_NAMES)},
    }
```

**Success Criteria**:

- Mean jitter \< 2px (normalized: \< 0.002)
- RTMLib jitter ≤ MediaPipe jitter

#### Test 3: Confidence Score Analysis

**Questions to Answer**:

1. Do high-confidence detections agree between systems?
1. Do low-confidence detections correlate with errors?
1. Which system has more reliable confidence estimation?

**Methodology**:

```python
"""Confidence score correlation analysis."""
# For frames where both systems detect the same person
mp_conf = [frame['visibility'] for frame in mp_results]
rtm_conf = [frame['scores'] for frame in rtm_results]

# Correlation between confidence scores
conf_correlation = np.corrcoef(mp_conf, rtm_conf)[0,1]

# Agreement by confidence tier
high_conf_agreement = agreement_when(mp_conf > 0.8, rtm_conf > 0.8)
low_conf_agreement = agreement_when(mp_conf < 0.5, rtm_conf < 0.5)
```

#### Test 4: Failure Mode Analysis

For videos where systems produce significantly different results:

1. Manual frame-by-frame inspection
1. Categorize failure modes:
   - Detection failure (no person detected)
   - Wrong person selected (multi-person scene)
   - Landmark jitter/jump
   - Left/right confusion
   - Occlusion handling
1. Count failures per category per system

#### Deliverables

- [ ] Multi-angle test videos
- [ ] `scripts/benchmark/robustness_tests.py` - Test suite
- [ ] `results/benchmark/angle_sensitivity.csv`
- [ ] `results/benchmark/jitter_analysis.csv`
- [ ] `results/benchmark/failure_modes.csv`
- [ ] `docs/research/rtmpose-robustness-report.md`

______________________________________________________________________

### Phase 5: Decision

**Duration**: 1 day
**Goal**: Make go/no-go recommendation based on all evidence

#### Decision Matrix

| Outcome                 | Criteria                                       | Recommendation                         |
| ----------------------- | ---------------------------------------------- | -------------------------------------- |
| **Full Replace**        | RTMLib ≥ MediaPipe on ALL metrics              | Migrate entirely to RTMLib             |
| **Hybrid Approach**     | RTMLib better on some metrics, worse on others | Offer both via `--pose-estimator` flag |
| **Stay with MediaPipe** | MediaPipe clearly better overall               | Keep MediaPipe, archive findings       |
| **Conditional Replace** | RTMLib better but needs work                   | Create improvement roadmap             |

#### Summary Report Template

```markdown
# RTMLib/RTMPose Evaluation Summary

## Executive Decision: [REPLACE / HYBRID / STAY / CONDITIONAL]

## Key Findings

### Performance
- MediaPipe: X FPS
- RTMLib (balanced): Y FPS
- Winner: [MediaPipe/RTMLib] by Z%

### Accuracy (Physics Validation)
- MediaPipe MAE: Xms, RMSE: Yms
- RTMLib MAE: Xms, RMSE: Yms
- Winner: [MediaPipe/RTMLib]

### Metric Agreement
- Flight time R²: X
- Jump height R²: X
- Overall agreement: X%

### Robustness
- Camera angle winner: [MediaPipe/RTMLib]
- Jitter winner: [MediaPipe/RTMLib]
- Failure rate: MediaPipe X%, RTMLib Y%

## Recommendation
[Detailed recommendation with rationale]

## Next Steps
1. ...
2. ...
3. ...
```

#### Deliverables

- [ ] `docs/research/rtmpose-evaluation-summary.md` - Final report
- [ ] Presentation slides (if needed)
- [ ] Implementation roadmap (if proceeding)

______________________________________________________________________

## ⚠️ Risk Assessment

### High-Risk Items

| Risk                     | Impact                     | Likelihood | Mitigation                        |
| ------------------------ | -------------------------- | ---------- | --------------------------------- |
| Keypoint mapping errors  | Completely wrong landmarks | Medium     | Visual verification in Phase 0    |
| Multi-person handling    | Wrong person tracked       | Medium     | Largest bounding box selection    |
| Coordinate normalization | Incorrect positions        | Low        | Explicit normalization in adapter |

### Medium-Risk Items

| Risk                        | Impact                     | Likelihood | Mitigation                       |
| --------------------------- | -------------------------- | ---------- | -------------------------------- |
| Model download on first use | Slow cold start            | High       | Pre-download in setup/deployment |
| det_frequency tuning        | Speed vs accuracy tradeoff | Medium     | Benchmark multiple settings      |
| Apple Silicon compatibility | Platform issues            | Low        | Use onnxruntime-silicon          |

### Low-Risk Items

| Risk                  | Impact           | Likelihood | Mitigation             |
| --------------------- | ---------------- | ---------- | ---------------------- |
| API stability         | Breaking changes | Low        | Pin rtmlib version     |
| License compatibility | Legal issues     | Very Low   | Apache 2.0, compatible |

______________________________________________________________________

## 🎯 Success Criteria Summary

| Category              | Minimum Acceptable    | Target       | Deal-Breaker |
| --------------------- | --------------------- | ------------ | ------------ |
| **Performance**       | ≥80% of MediaPipe FPS | ≥100% FPS    | \<50% FPS    |
| **Flight time MAE**   | ≤25ms                 | ≤20ms        | >30ms        |
| **Metric agreement**  | R² ≥0.95              | R² ≥0.99     | R² \<0.90    |
| **Memory usage**      | ≤300MB                | ≤200MB       | >500MB       |
| **Landmark coverage** | All 13                | All 13       | Missing any  |
| **Jitter**            | ≤ MediaPipe           | \< MediaPipe | >> MediaPipe |

______________________________________________________________________

## 📁 Complete Deliverables Checklist

### Phase 0: Proof of Concept

- [ ] `scripts/benchmark/test_rtmpose_poc.py`
- [ ] Visual comparison screenshots
- [ ] Phase 0 status report

### Phase 1: Performance

- [ ] `scripts/benchmark/performance_benchmark.py`
- [ ] `results/benchmark/performance_comparison.csv`
- [ ] `docs/research/rtmpose-performance-results.md`

### Phase 2: Physics Validation

- [ ] Test videos in `samples/validation/physics/`
- [ ] Extended `scripts/validate_known_heights.py`
- [ ] `results/benchmark/physics_*.json`
- [ ] `docs/research/rtmpose-physics-validation.md`

### Phase 3: Metric Agreement

- [ ] `scripts/benchmark/metric_agreement.py`
- [ ] `results/benchmark/metric_agreement.csv`
- [ ] `docs/research/rtmpose-metric-agreement.md`

### Phase 4: Robustness

- [ ] Multi-angle test videos
- [ ] `scripts/benchmark/robustness_tests.py`
- [ ] `results/benchmark/*.csv` (multiple)
- [ ] `docs/research/rtmpose-robustness-report.md`

### Phase 5: Decision

- [ ] `docs/research/rtmpose-evaluation-summary.md`

______________________________________________________________________

## ⏱️ Timeline

| Phase     | Duration       | Start  | End    | Dependencies                  |
| --------- | -------------- | ------ | ------ | ----------------------------- |
| Phase 0   | 1-2 days       | Day 1  | Day 2  | None                          |
| Phase 1   | 2-3 days       | Day 3  | Day 5  | Phase 0 ✓                     |
| Phase 2   | 3-5 days       | Day 3  | Day 8  | Phase 0 ✓, test videos        |
| Phase 3   | 2-3 days       | Day 6  | Day 8  | Phase 0 ✓                     |
| Phase 4   | 2-3 days       | Day 9  | Day 11 | Phase 0 ✓, multi-angle videos |
| Phase 5   | 1 day          | Day 12 | Day 12 | All phases ✓                  |
| **Total** | **11-17 days** |        |        |                               |

Note: Phases 1-3 can run partially in parallel after Phase 0 completion.

______________________________________________________________________

## References

- [RTMLib GitHub](https://github.com/Tau-J/rtmlib)
- [RTMPose Paper](https://arxiv.org/abs/2303.07399)
- [Halpe26 Keypoint Format](https://github.com/open-mmlab/mmpose/blob/main/configs/_base_/datasets/halpe26.py)
- [Pose Estimator Comparison 2025](./pose-estimator-comparison-2025.md)
- [Camera Setup Guide](../guides/camera-setup.md)
