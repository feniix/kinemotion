---
title: Non-Deterministic Analysis Root Cause and Solution
type: note
permalink: development/non-deterministic-analysis-root-cause-and-solution
tags:
- reproducibility
- bug
- priority-0
- drop-jump
- threshold-detection
---

# Non-Deterministic Analysis Root Cause

## Problem
Same video analyzed 3 times produces 59% RSI variation:
- Run 1: Contact=181ms, RSI=3.17
- Run 2: Contact=169ms, RSI=3.90
- Run 3: Contact=135ms, RSI=5.03

## Root Cause
**Binary thresholds without temporal averaging or hysteresis**

MediaPipe pose landmarks have natural ±0.01-0.02 variation between runs. When values oscillate near detection thresholds, binary comparisons flip randomly.

### Critical Thresholds
1. `src/kinemotion/dropjump/analysis.py:379`
   ```python
   is_stationary = np.abs(velocities) < velocity_threshold  # Binary, no hysteresis
   ```

2. `src/kinemotion/dropjump/kinematics.py:250`
   ```python
   if second_ground_y - first_ground_y > 0.05:  # Drop jump classification
   ```

3. `src/kinemotion/dropjump/analysis.py:168`
   ```python
   position_change_threshold=0.01  # Drop start detection
   ```

### Why This Causes Large Variation
1. MediaPipe landmark Y position varies by ±0.015 between runs
2. When foot_y = 0.049 vs 0.051 (tiny difference), threshold comparison at 0.05 flips
3. Different drop jump classification → selects different contact phase → 50+ frame difference in detection
4. Frame differences get amplified: 10 frames at 60fps = 167ms difference in contact time

## Solutions (Ranked by Effectiveness)

### Solution 1: Temporal Averaging (RECOMMENDED)
**Status**: Highest impact, lowest risk

Replace single-frame comparisons with median/mean over N-frame window:
```python
# Before
if second_ground_y - first_ground_y > 0.05:

# After
window = 3  # frames
first_ground_y = np.median(foot_y_positions[start:end])
second_ground_y = np.median(foot_y_positions[start2:end2])
if second_ground_y - first_ground_y > 0.05:
```

**Benefits**:
- Smooths out MediaPipe noise
- No change to detection logic or sensitivity
- Already computing means (line 241-246), just need wider window

### Solution 2: Hysteresis Thresholds
Add different thresholds for state transitions:
```python
# Drop detection with hysteresis
UP_THRESHOLD = 0.055  # Require clear evidence
DOWN_THRESHOLD = 0.045  # But don't flip back easily
```

### Solution 3: Increase Threshold Margin
Move from 0.05 to 0.08 (further from noise level):
```python
if second_ground_y - first_ground_y > 0.08:  # More robust
```

**Risk**: May miss some borderline drop jumps

### Solution 4: Activate Adaptive Thresholds
Use existing `calculate_adaptive_threshold()` function (analysis.py:28-107):
- Currently marked `@unused`
- Analyzes video-specific noise floor
- Sets threshold as 1.5x noise level

## Implementation Plan
1. Implement temporal averaging (Solution 1) in `_identify_main_contact_phase`
2. Test reproducibility with same video 10 times
3. If still >5% variation, add hysteresis (Solution 2)
4. Document in validation guide

## MediaPipe Determinism Investigation
- No TensorFlow Lite seed/determinism controls found in MediaPipe API
- Model inference has inherent minor variation (GPU vs CPU, floating point)
- Must make detection algorithm robust to small input variations
