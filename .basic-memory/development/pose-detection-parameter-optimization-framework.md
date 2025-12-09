---
title: Pose Detection Parameter Optimization Framework
type: note
permalink: development/pose-detection-parameter-optimization-framework
---

# Pose Detection Parameter Optimization Framework

## Overview

Framework for optimizing CMJ and drop jump detection parameters using ground truth annotations from validation videos.

## Files Created

### Ground Truth Templates
- `samples/validation/ground_truth_template.json` - Original template with null values
- `samples/validation/ground_truth.json` - Working file with FPS metadata pre-filled

### Scripts
- `scripts/prepare_ground_truth.py` - Extract video metadata (FPS, frame count)
- `scripts/optimize_detection_params.py` - Evaluation and optimization framework

## Ground Truth Data Format

```json
{
  "video_file": "samples/validation/cmj-45-IMG_6733.MOV",
  "jump_type": "cmj",
  "camera_angle": "45",
  "fps": 60.0,
  "frame_count": 215,
  "duration_seconds": 3.6,
  "notes": "",
  "ground_truth": {
    "standing_end": null,
    "lowest_point": null,
    "takeoff": null,
    "landing": null
  }
}
```

### Event Definitions

**CMJ:**
- `standing_end`: Last frame where athlete is stationary before starting downward movement
- `lowest_point`: Frame where center of mass reaches lowest position (deepest squat)
- `takeoff`: Frame where feet leave the ground (start of flight phase)
- `landing`: Frame where feet make first contact with ground after flight

**Drop Jump:**
- `drop_start`: Frame where athlete's feet leave the box
- `landing`: Frame where feet make first contact with ground after dropping
- `takeoff`: Frame where feet leave the ground after ground contact

## Annotation Workflow

### Step 1: Analyze Videos and Generate Debug Videos
```bash
# CMJ videos
uv run kinemotion cmj-analyze samples/validation/cmj-45-IMG_6733.MOV -o debug/cmj-45-1.mp4
uv run kinemotion cmj-analyze samples/validation/cmj-45-IMG_6734.MOV -o debug/cmj-45-2.mp4
# ... repeat for all videos

# Drop jump videos
uv run kinemotion dropjump-analyze samples/validation/dj-45-IMG_6739.MOV -o debug/dj-45-1.mp4
# ... repeat for all videos
```

### Step 2: Watch Debug Videos and Note Frame Numbers
- Open debug videos in a video player that shows frame numbers
- Pause at each key event
- Note the frame number
- Use slow-motion or frame-by-frame stepping for precision

### Step 3: Fill in Ground Truth File
Edit `samples/validation/ground_truth.json` and replace null values with frame numbers:

```json
{
  "ground_truth": {
    "standing_end": 45.5,
    "lowest_point": 67.0,
    "takeoff": 72.3,
    "landing": 88.7
  }
}
```

## Evaluation

### Evaluate Current Parameters
```bash
uv run python scripts/optimize_detection_params.py evaluate \
  --ground-truth samples/validation/ground_truth.json \
  --output results/baseline_evaluation.json
```

Output shows MAE (mean absolute error) for each event:
- Mean ± Std
- Max error
- Median error
- Overall MAE in frames and milliseconds

### Target Accuracy
- Goal: **Within 5 frames** (~83ms at 60fps, ~42ms at 120fps)

## Parameter Optimization

### Current Parameters

**CMJ (src/kinemotion/cmj/analysis.py):**
- Takeoff search window: 0.35s before peak height
- Lowest point search: 0.4s before takeoff
- Landing search window: 1.0s after peak height
- Velocity flatness threshold: 1e-6
- Landing skip frames: 2

**Drop Jump (src/kinemotion/dropjump/analysis.py):**
- `velocity_threshold`: 0.02
- `min_contact_frames`: 3
- `visibility_threshold`: 0.5
- `min_stationary_duration`: 1.0s
- `position_change_threshold`: 0.02
- `smoothing_window`: 5

### Optimization Methods

**Grid Search** (systematic exploration):
```bash
uv run python scripts/optimize_detection_params.py optimize \
  --ground-truth samples/validation/ground_truth.json \
  --method grid \
  --output results/optimized_params.json
```

**Scipy Optimize** (efficient continuous optimization):
```bash
uv run python scripts/optimize_detection_params.py optimize \
  --ground-truth samples/validation/ground_truth.json \
  --method scipy \
  --output results/optimized_params.json
```

**Manual Testing**:
1. Create params.json with custom values
2. Test: `uv run python scripts/optimize_detection_params.py test --ground-truth samples/validation/ground_truth.json --params params.json`
3. Iterate based on results

## Video Dataset

Using **only 45° oblique videos** based on empirical validation (Issue #10) showing 45° provides superior MediaPipe tracking vs 90° lateral.

### CMJ Videos (3 total)
- 45° angle: 3 videos @ 60fps (3.2-4.0s)

### Drop Jump Videos (3 total)
- 45° angle: 3 videos @ 60fps (3.5-4.1s)

**Total: 6 videos for optimization**

## Implementation Status

- [x] Ground truth template with annotation guide
- [x] Metadata extraction script
- [x] Evaluation framework with MAE computation
- [ ] Grid search implementation
- [ ] Scipy optimization implementation
- [ ] Parameter update integration

## Next Steps

1. User annotates ground truth frames by watching debug videos
2. Run baseline evaluation to quantify current accuracy
3. Implement grid search over parameter ranges
4. Validate optimized parameters
5. Update default parameters in codebase
6. Document optimization results
