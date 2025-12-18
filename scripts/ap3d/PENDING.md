# AthletePose3D Scripts - Pending Tasks & Status

These scripts were remade on Dec 18, 2025, after being lost from the workspace. While structurally complete, they require scientific refinement once the dataset is downloaded.

## 🎯 Current Status: **Phase 1 (Infrastructure Ready)**

The scripts can scan directories, generate manifests, and perform basic MPJPE calculations. However, they are currently in **Image Space (Pixels)**, not **World Space (MM)**.

## 🚀 Pending Work (High Priority)

### 1. Coordinate Normalization

- [ ] **Problem:** MediaPipe is normalized \[0,1\], AP3D Ground Truth is likely in mm or centralized camera coordinates.
- [ ] **Task:** Implement a scaling/normalization factor (e.g., using torso length) to make MPJPE meaningful.
- [ ] **Task:** Add Procrustes Alignment (Kabsch Algorithm) to handle translation/rotation offsets between models.

### 2. 3D Kinematics

- [ ] **Task:** Implement 3D joint angle calculations for Hip, Knee, and Ankle.
- [ ] **Task:** Compare Kinemotion's 2D-derived angles vs AP3D's 3D ground truth angles.

### 3. Data Integration

- [ ] **Task:** Verify `.pkl` / `.npy` loading logic against actual AP3D files (once downloaded).
- [ ] **Task:** Handle multi-view data (if present) - current scripts assume single view per video.
- [ ] **Task:** Add regex-based mapping for complex filenames (e.g., `S01_Run_V1.mp4` -> `S01_Run.pkl`).

### 4. Robustness & Presets

- [ ] **Task:** Use results to validate the "athletic" preset (smoothing/filtering optimization).
- [ ] **Task:** Handle detection failures (frames where MediaPipe returns no landmarks).

## 📊 Evaluation Summary (Code Reasoning)

| Script                 | Purpose           | Confidence | Primary Risk                   |
| ---------------------- | ----------------- | ---------- | ------------------------------ |
| `prepare_ap3d_data.py` | Data indexing     | High       | Naive filename mapping         |
| `ap3d_validator.py`    | Error calculation | Medium     | Lacks 3D coordinate projection |
| `validate_baseline.py` | Execution         | High       | None                           |

______________________________________________________________________

**Note:** Do not use MPJPE values from the current version for scientific reports until **Coordinate Normalization** is implemented.
