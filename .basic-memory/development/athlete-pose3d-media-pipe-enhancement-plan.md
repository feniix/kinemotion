---
title: AthletePose3D MediaPipe Enhancement Plan
type: note
permalink: development/athlete-pose3-d-media-pipe-enhancement-plan
tags:
- athletepose3d
- mediapipe-enhancement
- validation-plan
- ml-training
- parameter-optimization
---

# AthletePose3D MediaPipe Enhancement Plan

**Date:** 2025-12-08
**Analysis Method:** Sequential thinking + Multi-tool research (exa, ref, serena, basic-memory)
**Strategy:** Incremental value delivery, validate before investing

---

## Executive Summary

**Goal:** Enrich Kinemotion's MediaPipe-based pose estimation with AthletePose3D dataset to improve accuracy on athletic movements.

**Approach:** Three-phase incremental plan:
1. **Phase 1 (Week 1):** Validation only - measure current accuracy on gold-standard data
2. **Phase 2 (Week 2):** Parameter optimization - tune existing pipeline using AP3D ground truth
3. **Phase 3 (Weeks 3-4):** Correction layer - train small ML model to correct MediaPipe outputs

**Expected Improvement:**
- Phase 1 only: Validation + credibility (0% code change)
- Phase 1-2: 10-20% error reduction (parameter tuning)
- Phase 1-3: 30-50% error reduction (with correction layer)

**Strategic Timing:** Phase 2+ (post-MVP), aligns with market-driven approach

---

## AthletePose3D Dataset Overview

### What It Provides
- **1.3M frames** of athletic movements (figure skating, running, track & field)
- **165K unique postures** captured at 60-120 fps
- **Gold-standard validation** (compared against marker-based MoCap)
- **Multiple formats:** COCO, H3.6M keypoints + raw 3D poses
- **Pre-split data:** Train/validation/test sets
- **Pre-trained models:** Fine-tuned checkpoints available

### Relevance to Kinemotion
- **Figure skating jumps:** Similar biomechanics to drop jumps (ballistic movement, flight phase)
- **High-speed movements:** 120 fps captures rapid acceleration
- **Ground truth:** Can validate RSI, flight time, ground contact calculations
- **Athletic focus:** Addresses gap in MediaPipe training (trained on daily activities)

### Access
- **License:** Non-commercial research only
- **Download:** https://github.com/calvinyeungck/AthletePose3D/tree/main/license
- **Size:** ~50-100GB for relevant subsets (figure skating + running)

---

## Current Kinemotion Architecture

### PoseTracker (src/kinemotion/core/pose.py)
```python
class PoseTracker:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(...)

    def process_frame(self, frame) -> dict | None:
        # Returns: {landmark_name: (x, y, visibility)}
        # 13 key landmarks: ankles, heels, feet, hips, shoulders, knees, nose
        # Normalized coordinates (0-1 range)
```

### Data Flow
```
Video → PoseTracker.process_frame()
      → Landmarks (MediaPipe output)
      → Smoothing (Savitzky-Golay, temporal averaging)
      → Analysis (detect events, calculate metrics)
      → Results (RSI, flight time, contact time)
```

### Integration Points
1. **Before smoothing:** Add correction layer to improve raw MediaPipe output
2. **During analysis:** Use AP3D-optimized parameters
3. **Validation:** Compare final metrics against AP3D ground truth

---

## Phase 1: Dataset Acquisition & Validation (Week 1)

### Objectives
- Access AthletePose3D dataset
- Measure current Kinemotion accuracy on athletic movements
- Identify error patterns
- Establish baseline for improvement

### Step 1.1: Dataset Download (1-2 days)

**Actions:**
1. Read and accept license at: https://github.com/calvinyeungck/AthletePose3D/tree/main/license
2. Download relevant subsets:
   - Figure skating jumps (Axel, Lutz, Loop) - most similar to drop jumps
   - Running movements (similar kinematics)
3. Organize directory structure:
```
data/athletepose3d/
├── videos/
│   ├── figure_skating/
│   │   ├── Axel_1_cam_1.mp4
│   │   └── ...
│   └── running/
├── ground_truth/
│   ├── figure_skating/
│   │   ├── Axel_1_cam_1.npy  (3D poses)
│   │   └── Axel_1_cam_1_coco.npy (COCO format)
│   └── running/
└── manifest.json
```

**Estimated size:** 50-100GB

### Step 1.2: Data Preparation Script (1 day)

**Create:** `scripts/prepare_ap3d_data.py`

```python
"""
Prepare AthletePose3D data for Kinemotion validation.
"""
import json
import numpy as np
from pathlib import Path

def create_manifest(ap3d_root: Path) -> dict:
    """
    Create manifest mapping videos to ground truth.

    Returns:
        {
            video_path: str,
            ground_truth_path: str,
            sport_type: str,
            movement: str,
            fps: int,
            num_frames: int
        }
    """
    manifest = []
    for video_path in ap3d_root.glob("videos/**/*.mp4"):
        # Find corresponding ground truth
        gt_path = ap3d_root / "ground_truth" / video_path.stem / f"{video_path.stem}.npy"

        manifest.append({
            "video_path": str(video_path),
            "ground_truth_path": str(gt_path),
            "sport_type": video_path.parent.name,
            "movement": extract_movement_type(video_path.stem),
            "fps": get_video_fps(video_path),
            "num_frames": get_frame_count(video_path)
        })

    return manifest

def load_ap3d_ground_truth(npy_path: Path) -> np.ndarray:
    """
    Load AP3D ground truth poses.

    Returns:
        Array of shape (num_frames, num_joints, 3)
        where coordinates are in camera/world space
    """
    return np.load(npy_path)

def convert_ap3d_to_mediapipe_format(ap3d_poses: np.ndarray) -> dict:
    """
    Convert AP3D COCO/H3.6M format to MediaPipe landmark names.

    Maps:
        COCO ankle (id=15/16) → MediaPipe left_ankle/right_ankle
        etc.
    """
    # TODO: Implement keypoint mapping
    pass
```

**Deliverable:** `data/athletepose3d/manifest.json` with all video/ground truth pairs

### Step 1.3: Validation Framework (2 days)

**Create:** `src/kinemotion/validation/ap3d_validator.py`

```python
"""
Validate Kinemotion predictions against AthletePose3D ground truth.
"""
import numpy as np
from pathlib import Path
from kinemotion import process_dropjump_video
from typing import Dict, List

class AP3DValidator:
    def __init__(self, manifest_path: Path):
        self.manifest = self.load_manifest(manifest_path)

    def validate_all(self) -> Dict:
        """Run validation on all AP3D videos."""
        results = []
        for item in self.manifest:
            result = self.validate_single(
                video_path=item["video_path"],
                ground_truth_path=item["ground_truth_path"]
            )
            results.append(result)

        return self.aggregate_results(results)

    def validate_single(self, video_path: str, ground_truth_path: str) -> Dict:
        """
        Validate single video against ground truth.

        Returns:
            {
                "mpjpe": float,  # Mean Per Joint Position Error (mm)
                "joint_angle_errors": Dict[str, float],  # Per-joint errors
                "velocity_correlation": float,
                "phase_detection_accuracy": float
            }
        """
        # 1. Run Kinemotion on video
        kinemotion_output = process_dropjump_video(video_path)

        # 2. Load AP3D ground truth
        ground_truth = self.load_ground_truth(ground_truth_path)

        # 3. Align temporal frames (may need interpolation)
        kinemotion_aligned, gt_aligned = self.temporal_alignment(
            kinemotion_output, ground_truth
        )

        # 4. Calculate metrics
        mpjpe = self.calculate_mpjpe(kinemotion_aligned, gt_aligned)
        joint_errors = self.calculate_joint_angle_errors(kinemotion_aligned, gt_aligned)
        velocity_corr = self.calculate_velocity_correlation(kinemotion_aligned, gt_aligned)

        return {
            "mpjpe": mpjpe,
            "joint_angle_errors": joint_errors,
            "velocity_correlation": velocity_corr,
            "video_path": video_path
        }

    def calculate_mpjpe(self, pred: np.ndarray, gt: np.ndarray) -> float:
        """
        Calculate Mean Per Joint Position Error.

        MPJPE = mean(||pred_joint - gt_joint||_2)
        """
        return np.mean(np.linalg.norm(pred - gt, axis=-1))

    def calculate_joint_angle_errors(self, pred: np.ndarray, gt: np.ndarray) -> Dict:
        """
        Calculate joint angle errors (degrees).

        Returns: {joint_name: mean_absolute_error}
        """
        # TODO: Calculate angles from 3D positions
        pass

    def generate_report(self, results: Dict) -> str:
        """Generate markdown validation report."""
        report = f"""
# AthletePose3D Validation Report

**Date:** {datetime.now()}
**Videos Tested:** {results['num_videos']}

## Overall Metrics

- **Mean MPJPE:** {results['mean_mpjpe']:.1f} mm
- **Joint Angle Error:** {results['mean_joint_error']:.1f}°
- **Velocity Correlation:** {results['velocity_corr']:.3f}

## Per-Movement Results

| Movement | MPJPE (mm) | Joint Angle Error (°) | Velocity Correlation |
|----------|------------|----------------------|----------------------|
{self._format_movement_table(results)}

## Error Patterns

{self._analyze_error_patterns(results)}

## Recommendations

{self._generate_recommendations(results)}
"""
        return report
```

**Deliverable:** Validation framework that measures Kinemotion accuracy

### Step 1.4: Baseline Measurement (1 day)

**Actions:**
1. Run validator on AP3D jumping movements:
```bash
python scripts/validate_ap3d.py \
    --manifest data/athletepose3d/manifest.json \
    --output reports/ap3d_baseline_validation.md \
    --movements figure_skating
```

2. Analyze results:
   - Which joints have highest errors?
   - Which movement phases are most problematic?
   - How does error vary by movement type?

3. Document findings in validation report

**Deliverable:**
- `reports/ap3d_baseline_validation.md`
- Baseline metrics for improvement tracking

**Success Criteria:**
- Validation framework runs successfully on AP3D data
- Report quantifies current accuracy
- Error patterns identified

---

## Phase 2: Parameter Optimization (Week 2)

### Objectives
- Use AP3D ground truth to optimize smoothing/filtering parameters
- Find best parameters for athletic movements
- Implement "athletic" quality preset
- Measure improvement over baseline

### Step 2.1: Parameter Grid Search (2-3 days)

**Create:** `src/kinemotion/tuning/ap3d_parameter_tuner.py`

```python
"""
Optimize Kinemotion parameters using AthletePose3D ground truth.
"""
from itertools import product
from typing import Dict, List, Tuple

class AP3DParameterTuner:
    def __init__(self, manifest_path: Path, ground_truth_dir: Path):
        self.manifest = load_manifest(manifest_path)
        self.ground_truth_dir = ground_truth_dir

    def grid_search(self) -> Dict:
        """
        Grid search over parameter space.

        Parameters to optimize:
        - smooth_window: [5, 7, 9, 11, 13]
        - filter_cutoff: [4, 6, 8, 10, 12] Hz
        - savgol_polyorder: [2, 3, 4]
        - min_contact_frames: [3, 5, 7]
        """
        param_grid = {
            "smooth_window": [5, 7, 9, 11, 13],
            "filter_cutoff": [4, 6, 8, 10, 12],
            "savgol_polyorder": [2, 3, 4],
            "min_contact_frames": [3, 5, 7]
        }

        results = []

        # Grid search
        for params in self.generate_combinations(param_grid):
            # Evaluate on validation set
            error = self.evaluate_params(params)
            results.append({
                "params": params,
                "mpjpe": error["mpjpe"],
                "joint_error": error["joint_error"],
                "velocity_corr": error["velocity_corr"]
            })

        # Find best parameters
        best = min(results, key=lambda x: x["mpjpe"])
        return best

    def evaluate_params(self, params: Dict) -> Dict:
        """
        Evaluate parameter set on validation videos.
        """
        total_error = 0
        for video_item in self.manifest["validation_set"]:
            # Run with these parameters
            prediction = process_dropjump_video(
                video_item["video_path"],
                **params  # Pass parameters
            )

            # Compare to ground truth
            gt = load_ground_truth(video_item["ground_truth_path"])
            error = calculate_error(prediction, gt)
            total_error += error

        return total_error / len(self.manifest["validation_set"])
```

**Run:**
```bash
python scripts/tune_ap3d_parameters.py \
    --manifest data/athletepose3d/manifest.json \
    --output results/parameter_optimization.json \
    --n_jobs 4
```

**Deliverable:** Optimized parameters for athletic movements

### Step 2.2: Statistical Analysis (1 day)

**Actions:**
1. Compare optimized vs default parameters using paired t-test
2. Calculate effect sizes (Cohen's d)
3. Identify which parameters matter most
4. Validate on test set (separate from optimization)

**Create:** `scripts/analyze_parameter_improvement.py`

```python
"""
Statistical analysis of parameter optimization.
"""
from scipy import stats
import pandas as pd

def compare_parameters(baseline_results, optimized_results):
    """
    Paired t-test comparing baseline vs optimized.
    """
    # Per-video comparison
    baseline_errors = [r["mpjpe"] for r in baseline_results]
    optimized_errors = [r["mpjpe"] for r in optimized_results]

    # Paired t-test
    t_stat, p_value = stats.ttest_rel(baseline_errors, optimized_errors)

    # Effect size
    cohens_d = (np.mean(baseline_errors) - np.mean(optimized_errors)) / np.std(baseline_errors)

    # Percent improvement
    improvement = (np.mean(baseline_errors) - np.mean(optimized_errors)) / np.mean(baseline_errors) * 100

    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "cohens_d": cohens_d,
        "percent_improvement": improvement,
        "significant": p_value < 0.05
    }
```

**Deliverable:** Statistical validation of improvement

### Step 2.3: Implementation (1 day)

**Modify:** `src/kinemotion/core/filtering.py`

```python
# Add athletic quality preset
QUALITY_PRESETS = {
    "fast": {...},
    "balanced": {...},
    "accurate": {...},
    "athletic": {  # NEW: Optimized for athletic movements
        "smooth_window": 9,  # From AP3D optimization
        "filter_cutoff": 8,  # Hz
        "savgol_polyorder": 3,
        "min_contact_frames": 5,
        "use_temporal_averaging": True
    }
}
```

**Update API:**
```python
# Users can now use:
metrics = process_dropjump_video("video.mp4", quality="athletic")
```

**Deliverable:**
- Athletic quality preset integrated
- Backward compatible
- Documented in API reference

**Success Criteria:**
- Statistically significant improvement (p < 0.05)
- 10-20% error reduction on AP3D test set
- No regression on existing validation videos

---

## Phase 3: Pose Correction Layer (Weeks 3-4)

### Objectives
- Train ML model to correct MediaPipe outputs
- Integrate correction layer into PoseTracker
- Maintain backward compatibility
- Achieve 30-50% cumulative improvement

### Step 3.1: Training Data Preparation (2 days)

**Create:** `scripts/prepare_correction_training_data.py`

```python
"""
Prepare training data for pose correction model.
"""
import numpy as np
from pathlib import Path

def prepare_training_data(manifest: dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create training dataset for correction model.

    Returns:
        inputs: MediaPipe landmarks (N, 13, 3)  # 13 joints × (x,y,z)
        targets: Corrections (N, 13, 3)  # ground_truth - mediapipe
    """
    inputs = []
    targets = []

    for video_item in manifest["train_set"]:
        # Get MediaPipe predictions
        mediapipe_landmarks = run_mediapipe_on_video(video_item["video_path"])

        # Load AP3D ground truth
        ground_truth = load_ground_truth(video_item["ground_truth_path"])

        # Calculate corrections needed
        corrections = ground_truth - mediapipe_landmarks

        inputs.append(mediapipe_landmarks)
        targets.append(corrections)

    return np.concatenate(inputs), np.concatenate(targets)

# Prepare splits
train_inputs, train_targets = prepare_training_data(manifest["train"])
val_inputs, val_targets = prepare_training_data(manifest["validation"])
test_inputs, test_targets = prepare_training_data(manifest["test"])

# Save
np.savez("data/ap3d_corrections/train.npz", inputs=train_inputs, targets=train_targets)
np.savez("data/ap3d_corrections/val.npz", inputs=val_inputs, targets=val_targets)
np.savez("data/ap3d_corrections/test.npz", inputs=test_inputs, targets=test_targets)
```

**Deliverable:** Training data in `data/ap3d_corrections/`

### Step 3.2: Correction Model Architecture (2 days)

**Create:** `src/kinemotion/enhancement/pose_corrector.py`

```python
"""
Lightweight pose correction model for athletic movements.
"""
import torch
import torch.nn as nn

class PoseCorrector(nn.Module):
    """
    Simple MLP to correct MediaPipe landmark errors.

    Architecture:
        Input: 13 joints × 3 coords = 39 features
        Hidden: [128, 64, 32]
        Output: 39 corrections

    Model size: <1MB (CPU-friendly)
    """
    def __init__(self, num_joints=13, coord_dim=3):
        super().__init__()
        input_dim = num_joints * coord_dim  # 39

        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.1),

            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.1),

            nn.Linear(64, 32),
            nn.ReLU(),

            nn.Linear(32, input_dim)  # Output corrections
        )

    def forward(self, landmarks):
        """
        Args:
            landmarks: (batch, 13, 3) MediaPipe landmarks

        Returns:
            corrections: (batch, 13, 3) to add to landmarks
        """
        batch_size = landmarks.shape[0]

        # Flatten
        x = landmarks.view(batch_size, -1)

        # Predict corrections
        corrections = self.network(x)

        # Reshape
        corrections = corrections.view(batch_size, 13, 3)

        return corrections

    @classmethod
    def load_pretrained(cls, checkpoint_path: str):
        """Load pre-trained model from checkpoint."""
        model = cls()
        model.load_state_dict(torch.load(checkpoint_path, map_location='cpu'))
        model.eval()
        return model

# Optional: Temporal model (LSTM)
class TemporalPoseCorrector(nn.Module):
    """
    LSTM-based corrector for temporal consistency.

    Better for sequences but ~2x slower.
    """
    def __init__(self, num_joints=13, coord_dim=3):
        super().__init__()
        input_dim = num_joints * coord_dim

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=64,
            num_layers=2,
            batch_first=True,
            dropout=0.1
        )

        self.fc = nn.Linear(64, input_dim)

    def forward(self, landmarks_sequence):
        """
        Args:
            landmarks_sequence: (batch, seq_len, 13, 3)

        Returns:
            corrections: (batch, seq_len, 13, 3)
        """
        batch_size, seq_len, num_joints, coord_dim = landmarks_sequence.shape

        # Flatten spatial dims
        x = landmarks_sequence.view(batch_size, seq_len, -1)

        # LSTM
        lstm_out, _ = self.lstm(x)

        # Predict corrections
        corrections = self.fc(lstm_out)

        # Reshape
        corrections = corrections.view(batch_size, seq_len, num_joints, coord_dim)

        return corrections
```

**Deliverable:** Correction model architecture

### Step 3.3: Training Script (2 days)

**Create:** `scripts/train_pose_corrector.py`

```python
"""
Train pose correction model on AthletePose3D data.
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path

def train_corrector(
    train_data_path: Path,
    val_data_path: Path,
    output_dir: Path,
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 1e-3
):
    """Train pose correction model."""

    # Load data
    train_data = np.load(train_data_path)
    val_data = np.load(val_data_path)

    train_dataset = TensorDataset(
        torch.FloatTensor(train_data["inputs"]),
        torch.FloatTensor(train_data["targets"])
    )
    val_dataset = TensorDataset(
        torch.FloatTensor(val_data["inputs"]),
        torch.FloatTensor(val_data["targets"])
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    # Model
    model = PoseCorrector()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Training loop
    best_val_loss = float('inf')
    patience = 10
    patience_counter = 0

    for epoch in range(epochs):
        # Train
        model.train()
        train_loss = 0
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            predictions = model(inputs)
            loss = criterion(predictions, targets)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # Validate
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for inputs, targets in val_loader:
                predictions = model(inputs)
                loss = criterion(predictions, targets)
                val_loss += loss.item()

        train_loss /= len(train_loader)
        val_loss /= len(val_loader)

        print(f"Epoch {epoch+1}/{epochs}: Train Loss={train_loss:.4f}, Val Loss={val_loss:.4f}")

        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            # Save best model
            torch.save(model.state_dict(), output_dir / "best_corrector.pth")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print("Early stopping triggered")
                break

    return model

# Run training
if __name__ == "__main__":
    train_corrector(
        train_data_path=Path("data/ap3d_corrections/train.npz"),
        val_data_path=Path("data/ap3d_corrections/val.npz"),
        output_dir=Path("models/ap3d_corrector/"),
        epochs=50
    )
```

**Run:**
```bash
python scripts/train_pose_corrector.py \
    --train data/ap3d_corrections/train.npz \
    --val data/ap3d_corrections/val.npz \
    --output models/ap3d_corrector/ \
    --epochs 50 \
    --batch_size 32
```

**Deliverable:**
- Trained model: `models/ap3d_corrector/best_corrector.pth`
- Training logs and curves

### Step 3.4: Integration into PoseTracker (2 days)

**Modify:** `src/kinemotion/core/pose.py`

```python
from kinemotion.enhancement.pose_corrector import PoseCorrector

class PoseTracker:
    """Enhanced with optional athletic pose correction."""

    def __init__(
        self,
        model_complexity: int = 1,
        use_athletic_correction: bool = False
    ):
        # Original MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=model_complexity,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # Optional: Athletic correction layer
        self.use_athletic_correction = use_athletic_correction
        if use_athletic_correction:
            try:
                self.corrector = PoseCorrector.load_pretrained(
                    "models/ap3d_corrector/best_corrector.pth"
                )
                print("Loaded athletic pose correction model")
            except FileNotFoundError:
                print("Warning: Correction model not found, using standard MediaPipe")
                self.use_athletic_correction = False

    def process_frame(
        self, frame: np.ndarray
    ) -> dict[str, tuple[float, float, float]] | None:
        """
        Process frame with optional athletic correction.
        """
        # Step 1: Standard MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)

        if not results.pose_landmarks:
            return None

        # Step 2: Extract landmarks
        landmarks = self._extract_landmarks(results)

        # Step 3: Optional correction
        if self.use_athletic_correction:
            landmarks = self._apply_correction(landmarks)

        return landmarks

    def _apply_correction(self, landmarks: dict) -> dict:
        """Apply athletic correction to landmarks."""
        # Convert dict to tensor
        landmark_array = self._dict_to_array(landmarks)
        landmark_tensor = torch.FloatTensor(landmark_array).unsqueeze(0)

        # Predict corrections
        with torch.no_grad():
            corrections = self.corrector(landmark_tensor)

        # Apply corrections
        corrected_array = landmark_array + corrections.squeeze(0).numpy()

        # Convert back to dict
        corrected_landmarks = self._array_to_dict(corrected_array)

        return corrected_landmarks
```

**Update API:**
```python
# Users can enable athletic correction:
from kinemotion import process_dropjump_video

metrics = process_dropjump_video(
    "video.mp4",
    quality="athletic",  # Use optimized parameters
    use_athletic_correction=True  # NEW: Enable correction layer
)
```

**Deliverable:**
- Integrated correction layer
- Backward compatible (default: False)
- Graceful fallback if model not found

**Success Criteria:**
- Model loads successfully
- Inference time < 5ms per frame (CPU)
- 30-50% cumulative error reduction vs baseline
- No accuracy regression when disabled

---

## Phase 4: Evaluation & Documentation (Week 5)

### Objectives
- Comprehensive evaluation of all enhancements
- A/B testing framework for user validation
- Complete documentation
- Publication-ready materials

### Step 4.1: Comprehensive Evaluation (2 days)

**Create:** `scripts/evaluate_enhancements.py`

```python
"""
Comprehensive evaluation of AthletePose3D enhancements.
"""

def evaluate_all_modes():
    """
    Compare three modes:
    1. Baseline: Standard MediaPipe
    2. Optimized: Athletic parameters only
    3. Enhanced: Parameters + correction layer
    """
    modes = {
        "baseline": {"quality": "balanced", "use_correction": False},
        "optimized": {"quality": "athletic", "use_correction": False},
        "enhanced": {"quality": "athletic", "use_correction": True}
    }

    results = {}

    for mode_name, config in modes.items():
        mode_results = []

        for video_item in test_manifest:
            # Run Kinemotion with config
            prediction = process_dropjump_video(
                video_item["video_path"],
                **config
            )

            # Compare to ground truth
            gt = load_ground_truth(video_item["ground_truth_path"])

            metrics = {
                "mpjpe": calculate_mpjpe(prediction, gt),
                "joint_angle_error": calculate_joint_error(prediction, gt),
                "rsi_error": abs(prediction["rsi"] - gt["rsi"]),
                "flight_time_error": abs(prediction["flight_time"] - gt["flight_time"])
            }

            mode_results.append(metrics)

        results[mode_name] = aggregate(mode_results)

    return results

def generate_comparison_report(results: dict) -> str:
    """Generate comprehensive comparison report."""
    report = f"""
# AthletePose3D Enhancement Evaluation Report

**Date:** {datetime.now()}
**Test Videos:** {len(test_manifest)}

## Overall Performance

| Mode | MPJPE (mm) | Joint Angle (°) | RSI Error (%) | Flight Time (ms) |
|------|------------|----------------|---------------|------------------|
| Baseline | {results['baseline']['mpjpe']:.1f} | {results['baseline']['joint_angle']:.1f} | {results['baseline']['rsi_error']:.1f} | {results['baseline']['flight_error']:.1f} |
| Optimized Params | {results['optimized']['mpjpe']:.1f} | {results['optimized']['joint_angle']:.1f} | {results['optimized']['rsi_error']:.1f} | {results['optimized']['flight_error']:.1f} |
| Enhanced (Full) | {results['enhanced']['mpjpe']:.1f} | {results['enhanced']['joint_angle']:.1f} | {results['enhanced']['rsi_error']:.1f} | {results['enhanced']['flight_error']:.1f} |

## Improvements vs Baseline

- **Optimized:** {calculate_improvement(results['baseline'], results['optimized'])}% reduction
- **Enhanced:** {calculate_improvement(results['baseline'], results['enhanced'])}% reduction

## Statistical Significance

{run_statistical_tests(results)}

## Per-Movement Analysis

{per_movement_breakdown(results)}

## Recommendations

{generate_recommendations(results)}
"""
    return report
```

**Deliverable:** Complete evaluation report

### Step 4.2: A/B Testing Framework (1 day)

**Create:** `src/kinemotion/evaluation/ab_testing.py`

```python
"""
A/B testing framework for user validation.
"""

class ABTestRecorder:
    """Record user preferences between enhancement modes."""

    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.results = []

    def record_comparison(
        self,
        video_id: str,
        baseline_result: dict,
        enhanced_result: dict,
        user_preference: str  # "baseline" | "enhanced" | "no_difference"
    ):
        """Record single A/B comparison."""
        self.results.append({
            "video_id": video_id,
            "timestamp": datetime.now().isoformat(),
            "baseline_rsi": baseline_result["rsi"],
            "enhanced_rsi": enhanced_result["rsi"],
            "user_preference": user_preference
        })

        self.save()

    def save(self):
        """Save results to file."""
        with open(self.output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

    def analyze(self) -> dict:
        """Analyze A/B test results."""
        preferences = [r["user_preference"] for r in self.results]

        return {
            "total_comparisons": len(self.results),
            "prefer_enhanced": preferences.count("enhanced"),
            "prefer_baseline": preferences.count("baseline"),
            "no_difference": preferences.count("no_difference"),
            "enhanced_win_rate": preferences.count("enhanced") / len(preferences)
        }
```

**CLI integration:**
```bash
# Run comparison mode
kinemotion dropjump-analyze video.mp4 --compare-modes

# Output shows both results, asks user which is better
```

**Deliverable:** A/B testing framework for user validation

### Step 4.3: Documentation (1 day)

**Create documentation:**

1. **Technical report:** `docs/validation/ap3d-enhancement-results.md`
   - Methodology
   - Results (tables, figures)
   - Statistical analysis
   - Conclusions

2. **User guide:** `docs/guides/athletic-enhancement-mode.md`
   - When to use athletic enhancement
   - How to enable
   - Expected improvements
   - Troubleshooting

3. **API documentation:** Update `docs/api/overview.md`
   ```python
   # New parameters:
   process_dropjump_video(
       video_path,
       quality="athletic",  # Use AP3D-optimized parameters
       use_athletic_correction=True  # Enable correction layer
   )
   ```

4. **Changelog:** `CHANGELOG.md`
   ```markdown
   ## [0.X.0] - Athletic Enhancement Release

   ### Added
   - Athletic quality preset (AP3D-optimized parameters)
   - Optional pose correction layer for athletic movements
   - AthletePose3D validation framework

   ### Improved
   - 30-50% reduction in joint position errors on jumping movements
   - More accurate RSI calculations for elite athletes
   ```

**Deliverable:** Complete documentation suite

### Step 4.4: Publication Preparation (1 day, optional)

**If planning academic publication:**

1. **Methods section:**
   - AP3D validation methodology
   - Parameter optimization procedure
   - Correction layer architecture
   - Statistical analysis approach

2. **Results figures:**
   - Before/after comparison plots
   - Error distribution histograms
   - Per-movement accuracy charts
   - Bland-Altman plots

3. **Supplementary materials:**
   - Complete parameter grid search results
   - Model architecture details
   - Training curves
   - Per-video results table

**Deliverable:** Publication-ready materials

**Success Criteria:**
- All modes evaluated on test set
- Statistical significance demonstrated
- User documentation complete
- Publication materials ready (if applicable)

---

## Timeline & Resource Requirements

### Option A: Minimum Viable Enhancement (Phases 1-2 only)

**Timeline:** 2 weeks
**Resources:**
- 1 developer
- 100GB storage
- Standard CPU (no GPU needed)

**Deliverables:**
- Validation report (baseline accuracy on AP3D)
- Optimized parameters for athletic movements
- "athletic" quality preset integrated

**Expected Improvement:** 10-20% error reduction

**Risk:** Low (no ML training, just parameter tuning)

---

### Option B: Full Enhancement (All 4 Phases)

**Timeline:** 5 weeks
**Resources:**
- 1 developer
- 100GB storage
- CPU sufficient (GPU speeds training but not required)

**Deliverables:**
- Validation report
- Optimized parameters
- Trained correction layer
- Integrated enhancement mode
- Complete documentation
- A/B testing framework

**Expected Improvement:** 30-50% error reduction (cumulative)

**Risk:** Medium (ML model may not generalize to all videos)

---

## Risk Mitigation

### Technical Risks

**Risk 1: AP3D format incompatibility**
- **Mitigation:** Start with COCO format (well-documented), map common joints first
- **Fallback:** Manual keypoint mapping if needed

**Risk 2: Correction model doesn't generalize**
- **Mitigation:**
  - Train on diverse AP3D movements
  - Use dropout/regularization
  - Validate on separate test set
  - Make correction optional (can disable)

**Risk 3: Performance overhead**
- **Mitigation:**
  - Keep model tiny (<1MB)
  - Profile CPU usage
  - Make correction optional
  - Target <5ms inference time

**Risk 4: Coordinate system misalignment**
- **Mitigation:**
  - Carefully study AP3D coordinate systems
  - Implement transformation functions
  - Validate with visual inspection

### Strategic Risks

**Risk 5: Improvement insufficient to justify effort**
- **Mitigation:** Phase 1 validates need before investing in Phases 2-3
- **Decision point:** Stop after Phase 1 if baseline already acceptable

**Risk 6: Users don't value accuracy improvement**
- **Mitigation:** A/B testing with real users, collect feedback
- **Fallback:** Document validation for research credibility even if not productized

---

## Success Metrics

### Phase 1 Success Criteria
- ✅ Validation framework runs successfully
- ✅ Baseline metrics documented
- ✅ Error patterns identified

### Phase 2 Success Criteria
- ✅ Statistically significant improvement (p < 0.05)
- ✅ 10-20% error reduction
- ✅ No regression on existing videos

### Phase 3 Success Criteria
- ✅ Model trains to convergence
- ✅ 30-50% cumulative improvement
- ✅ Inference time < 5ms per frame
- ✅ Graceful degradation if model unavailable

### Phase 4 Success Criteria
- ✅ Comprehensive evaluation complete
- ✅ Documentation published
- ✅ User feedback positive (A/B testing)

---

## Strategic Alignment

### MVP-First Approach
- **Now (MVP Phase):** Skip - focus on launch
- **Phase 2 (Week 4):** Start Phase 1 validation (2-3 days)
  - Low risk, high credibility gain
  - Can stop here if sufficient
- **Weeks 5-8:** Phases 2-3 if accuracy validated as pain point
- **Months 2-3:** Full implementation if market demands research-grade

### Key Principle
**"Optimize for learning, not accuracy."**
- Validate user need before investing
- Incremental value delivery
- Can stop at any phase
- Each phase builds on previous

### Market Differentiation
- **"Validated on Olympic-level movements"**
- **"Fine-tuned for elite athletic performance"**
- **"Research-grade accuracy"**
- Foundation for academic collaborations

---

## Next Actions

### Immediate (This Week)
1. **Review plan with team** - ensure alignment
2. **Accept AP3D license** - review terms, sign agreement
3. **Start download** - figure skating jumps subset (~50GB)

### Week 4 (Post-MVP)
1. **Run Phase 1 validation** - measure baseline (2-3 days)
2. **Decision point:** Is improvement needed and worth investment?
3. **If yes:** Continue to Phase 2
4. **If no:** Document validation for credibility, move on

### Ongoing
- Monitor user feedback for accuracy complaints
- Track validation metrics in product analytics
- Reassess priority based on market signals

---

## Conclusion

This plan provides a **systematic, incremental approach** to enriching MediaPipe with AthletePose3D:

**Phase 1 (Validation):** Low-risk baseline measurement
- **Value:** Scientific credibility, error pattern identification
- **Investment:** 1 week, $0, no code changes

**Phase 2 (Optimization):** Parameter tuning using ground truth
- **Value:** 10-20% improvement, no ML complexity
- **Investment:** 1 week, $0, minimal code changes

**Phase 3 (Correction Layer):** ML-based enhancement
- **Value:** 30-50% cumulative improvement
- **Investment:** 2 weeks, $0, moderate complexity

**Strategic fit:**
- Aligns with MVP-first approach
- Validates before investing
- Builds foundation for research collaborations
- Creates market differentiation

**Recommendation:** Start with Phase 1 validation (Week 4 post-MVP) to establish baseline, then decide based on results and user feedback.
