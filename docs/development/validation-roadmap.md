# Kinemotion Validation & Improvement Roadmap

**Document Version:** 1.0
**Last Updated:** 2025-01-13
**Status:** Planning Phase

## Executive Summary

This document outlines a practical 3-month validation roadmap for kinemotion that does not require laboratory equipment (force plates, motion capture, jump mats). Items are ranked by ROI (Return on Investment) and implementation difficulty to prioritize high-impact work.

**Current Status:** Pre-validation - technically sound implementation lacking empirical validation

**Goal:** Establish measurement reliability, compare against accessible benchmarks, and transparently document limitations

______________________________________________________________________

## Ranking System

- **ROI:** ⭐⭐⭐⭐⭐ (High) to ⭐☆☆☆☆ (Low)
- **Difficulty:** ⭐☆☆☆☆ (Easy) to ⭐⭐⭐⭐⭐ (Very Hard)
- **Time Estimate:** Hours required

______________________________________________________________________

## Priority 1: HIGH ROI + LOW DIFFICULTY (Do First)

### 1.1 Documentation of Known Limitations

**ROI:** ⭐⭐⭐⭐⭐ | **Difficulty:** ⭐☆☆☆☆ | **Time:** 2-4 hours

**Description:**
Add clear validation status warnings to README, API docs, and user-facing output.

**Deliverables:**

- Update `README.md` with validation status section
- Add limitations to API documentation
- Create `docs/validation-status.md`

**Content to include:**

```markdown
## ⚠️ Validation Status

**Current Status:** Pre-validation (not validated against force plates)

**Suitable for:**
- ✅ Training monitoring (relative changes within athlete)
- ✅ Educational purposes
- ✅ Exploratory analysis
- ✅ Proof-of-concept research

**NOT suitable for:**
- ❌ Research publications (as measurement tool)
- ❌ Clinical decision-making
- ❌ Talent identification (absolute comparisons)
- ❌ Legal/insurance assessments

**Known Limitations:**
- No force plate validation
- MediaPipe accuracy affected by: lighting, clothing, occlusion
- Lower sampling rate (30-60fps) vs validated apps (120-240Hz)
- Indirect measurement (landmarks → CoM) introduces error
```

**Files to modify:**

- `README.md`
- `docs/validation-status.md` (new)
- `docs/README.md` (add link)

**Success Criteria:**

- Clear warnings visible before use
- Legal/ethical protection established
- User expectations appropriately set

______________________________________________________________________

### 1.2 Add Confidence Scores to Output

**ROI:** ⭐⭐⭐⭐⭐ | **Difficulty:** ⭐⭐☆☆☆ | **Time:** 4-8 hours

**Description:**
Automatically flag low-confidence detections based on tracking quality indicators.

**Output Format:**

```json
{
  "jump_height": 0.35,
  "flight_time": 0.532,
  "confidence": "high",
  "quality_indicators": {
    "avg_visibility": 0.89,
    "tracking_stable": true,
    "phase_detection_clear": true,
    "outliers_detected": 2
  },
  "warnings": []
}
```

**Confidence Rules:**

- **High:** avg_visibility > 0.8, stable tracking, clear phases
- **Medium:** avg_visibility 0.6-0.8, OR minor tracking issues
- **Low:** avg_visibility \< 0.6, OR significant tracking gaps, OR unclear phases

**Warning Triggers:**

- `"Poor lighting or occlusion detected"`
- `"Unstable landmark tracking"`
- `"Unclear phase transitions"`
- `"High measurement uncertainty"`

**Files to modify:**

- `src/kinemotion/dropjump/analysis.py`
- `src/kinemotion/cmj/analysis.py`
- `src/kinemotion/api.py`
- Add `src/kinemotion/core/quality.py` (new module)

**Implementation:**

```python
# src/kinemotion/core/quality.py
from dataclasses import dataclass
from typing import Literal

@dataclass
class QualityAssessment:
    confidence: Literal["high", "medium", "low"]
    avg_visibility: float
    tracking_stable: bool
    phase_detection_clear: bool
    outliers_detected: int
    warnings: list[str]

def assess_quality(
    visibilities: np.ndarray,
    positions: np.ndarray,
    outlier_mask: np.ndarray,
    phases: list[tuple]
) -> QualityAssessment:
    """Calculate quality indicators and confidence score."""
    ...
```

**Testing:**

- Unit tests for quality assessment logic
- Integration tests with known good/bad videos
- Manual verification of confidence scores

**Success Criteria:**

- Confidence scores correlate with actual accuracy
- Users can filter low-quality detections
- System demonstrates self-awareness of limitations

______________________________________________________________________

### 1.3 Test-Retest Reliability (Determinism Test)

**ROI:** ⭐⭐⭐⭐⭐ | **Difficulty:** ⭐☆☆☆☆ | **Time:** 1-2 hours

**Description:**
Verify algorithm produces identical results on repeated runs of same video (deterministic behavior).

**Test Protocol:**

```bash
# Run same video 100 times
for i in {1..100}; do
    uv run kinemotion dropjump-analyze test.mp4 --output results_${i}.json
done

# Compare all outputs - should be IDENTICAL
python scripts/compare_results.py results_*.json
```

**Expected Result:**

- All 100 outputs byte-identical
- No random variation
- Proves fundamental reliability

**If Results Vary:**

- Investigate random seed issues
- Check for uninitialized variables
- Look for system-dependent behavior (timestamps, etc.)
- Fix non-deterministic components

**Script to create:**

```python
# scripts/compare_results.py
import json
import sys
from pathlib import Path

def compare_results(result_files: list[Path]) -> bool:
    """Compare multiple result files for identity."""
    baseline = json.loads(result_files[0].read_text())

    for i, file in enumerate(result_files[1:], start=2):
        current = json.loads(file.read_text())
        if current != baseline:
            print(f"Mismatch at run {i}")
            print(f"Baseline: {baseline}")
            print(f"Current: {current}")
            return False

    print(f"✅ All {len(result_files)} runs produced identical results")
    return True
```

**Success Criteria:**

- 100/100 runs produce identical results
- Algorithm proven deterministic
- Foundation for reliability established

______________________________________________________________________

### 1.4 Known Height Validation (Dropped Objects)

**ROI:** ⭐⭐⭐⭐☆ | **Difficulty:** ⭐⭐☆☆☆ | **Time:** 2-4 hours

**Description:**
Validate timing accuracy using physics with dropped objects from measured heights.

**Test Protocol:**

```text
Equipment:
- Basketball or medicine ball
- Measuring tape
- Camera at 60fps
- Tripod

Heights to test:
- 0.50m → expected flight_time = 0.319s
- 1.00m → expected flight_time = 0.452s
- 1.50m → expected flight_time = 0.553s

Formula: t = sqrt(2h/g) where g = 9.81 m/s²

Repetitions: 10 drops per height × 3 heights = 30 videos
```

**Data Collection:**

1. Mark heights on wall with tape
1. Drop object from each height
1. Record with camera capturing full drop
1. Measure actual height with tape measure
1. Record video filename with true height

**Analysis:**

```python
# scripts/validate_known_heights.py
import numpy as np
from kinemotion import process_dropjump_video

def validate_physics(video_path: str, true_height_m: float):
    """Compare measured vs theoretical flight time."""
    result = process_dropjump_video(video_path)

    measured_time = result['flight_time']
    expected_time = np.sqrt(2 * true_height_m / 9.81)

    error = measured_time - expected_time
    percent_error = (error / expected_time) * 100

    return {
        'measured': measured_time,
        'expected': expected_time,
        'error': error,
        'percent_error': percent_error
    }
```

**Validation Metrics:**

- Mean absolute error (MAE)
- Root mean square error (RMSE)
- Systematic bias
- Correlation coefficient

**Success Criteria:**

- MAE \< 20ms (reasonable for 30-60fps video)
- RMSE \< 30ms
- Systematic bias identified and documented
- r > 0.99 correlation with theoretical values

**Deliverable:**

- `docs/validation/known-height-validation.md` with results
- Scatter plot: measured vs expected
- Residual plot showing error distribution

______________________________________________________________________

### 1.5 Parameter Sensitivity Report

**ROI:** ⭐⭐⭐⭐☆ | **Difficulty:** ⭐⭐☆☆☆ | **Time:** 4-8 hours

**Description:**
Systematically test how tunable parameters affect output metrics.

**Parameters to Test:**

```python
test_matrix = {
    'smoothing_window': [3, 5, 7, 9, 11],
    'polyorder': [2, 3, 4],
    'velocity_threshold': [0.01, 0.015, 0.02, 0.025, 0.03],
    'model_complexity': [0, 1, 2],
    'min_contact_frames': [2, 3, 4, 5],
    'use_curvature': [True, False],
    'use_ransac': [True, False],
}
```

**Test Videos:**

- 10 representative videos (5 drop jump, 5 CMJ)
- Mix of quality levels (good, medium, poor tracking)
- Different athletes and conditions

**Analysis Script:**

```python
# scripts/parameter_sensitivity.py
import itertools
import pandas as pd
from kinemotion import process_video

def run_sensitivity_analysis(videos, param_grid):
    """Test all parameter combinations."""
    results = []

    for params in itertools.product(*param_grid.values()):
        param_dict = dict(zip(param_grid.keys(), params))

        for video in videos:
            result = process_video(video, **param_dict)
            results.append({
                **param_dict,
                'video': video,
                'jump_height': result['jump_height'],
                'flight_time': result['flight_time'],
                # ... other metrics
            })

    return pd.DataFrame(results)
```

**Visualization:**

- Heatmaps showing parameter impact
- Sensitivity indices (which parameters matter most)
- Interaction effects
- Recommended ranges

**Success Criteria:**

- Identify parameters with high sensitivity
- Document robust vs fragile parameters
- Justify default parameter choices
- Provide user guidance for tuning

**Deliverable:**

- `docs/validation/parameter-sensitivity.md`
- Interactive plots in `docs/validation/sensitivity-plots/`
- Updated parameter documentation with justification

______________________________________________________________________

## Priority 2: HIGH ROI + MEDIUM DIFFICULTY

### 2.1 Manual Frame Selection Comparison (MyJump Method)

**ROI:** ⭐⭐⭐⭐⭐ | **Difficulty:** ⭐⭐⭐☆☆ | **Time:** 8-16 hours

**Description:**
Compare kinemotion's automated detection against manual frame selection (MyJump's validated method).

**Why This Matters:**

- MyJump validated against force plates (ICC=0.997)
- If kinemotion matches MyJump, indirect validation achieved
- Most accessible "gold standard" without lab equipment

**Test Protocol:**

```text
Sample Size: 50 jumps (25 drop jump, 25 CMJ)
Athletes: 5 athletes × 10 jumps each
Video: 60fps, lateral view, 2-3m distance

For each jump:
1. Record video
2. Process with kinemotion (automated)
3. Manually identify takeoff/landing frames (blind to automated result)
4. Calculate flight time: (landing_frame - takeoff_frame) / fps
5. Calculate jump height: h = g × t² / 8
6. Compare automated vs manual
```

**Manual Frame Selection Guidelines:**

```text
Takeoff Frame: Last frame where feet are in contact with ground
Landing Frame: First frame where feet contact ground after flight

Tips for consistency:
- Use frame-by-frame playback
- Look for foot-ground contact/separation
- Mark frame numbers in spreadsheet
- Have 2 independent raters for reliability
```

**Statistical Analysis:**

```python
# scripts/validate_vs_manual.py
import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import mean_absolute_error

def calculate_icc(automated, manual):
    """Calculate ICC(2,1) - two-way random effects model."""
    # Implementation following McGraw & Wong (1996)
    ...

def bland_altman_analysis(automated, manual):
    """Calculate bias and 95% limits of agreement."""
    mean_diff = np.mean(automated - manual)
    std_diff = np.std(automated - manual)

    loa_upper = mean_diff + 1.96 * std_diff
    loa_lower = mean_diff - 1.96 * std_diff

    return {
        'bias': mean_diff,
        'loa_upper': loa_upper,
        'loa_lower': loa_lower,
        'std_diff': std_diff
    }
```

**Target Metrics:**

- **ICC > 0.90:** Excellent reliability
- **Bias \< 2cm:** Acceptable per Balsalobre 2015
- **r > 0.95:** Strong correlation
- **95% of differences within ±5cm:** Clinical acceptability

**Deliverables:**

- Dataset: `data/validation/manual_comparison.csv`
- Analysis notebook: `notebooks/manual_comparison_analysis.ipynb`
- Report: `docs/validation/manual-comparison-study.md`
- Bland-Altman plots
- ICC calculations with 95% CI

**Success Criteria:**

- Published as preprint (OSF, arXiv, SportRxiv)
- Demonstrates acceptable agreement with validated method
- Systematic bias identified (if any) for correction factor

______________________________________________________________________

### 2.2 Inter-Device Reliability Study

**ROI:** ⭐⭐⭐⭐☆ | **Difficulty:** ⭐⭐⭐☆☆ | **Time:** 4-8 hours

**Description:**
Test measurement consistency across different cameras/devices.

**Test Protocol:**

```text
Devices to test:
1. iPhone 12 Pro (60fps, 1920×1080)
2. Samsung Galaxy S21 (30fps, 1920×1080)
3. GoPro Hero 10 (60fps, 2.7K)
4. Laptop webcam (30fps, 720p)

Setup:
- Record same jumps simultaneously with all devices
- Side-by-side camera positions (same view angle)
- 10 jumps per session × 3 sessions = 30 jumps
- Process each video independently with kinemotion
```

**Analysis:**

```python
# Calculate ICC across devices
def inter_device_icc(devices: dict[str, list[float]]) -> float:
    """
    ICC(2,k) - two-way random effects, consistency definition.
    Tests if devices produce consistent relative measurements.
    """
    ...

# Mean differences between devices
def pairwise_device_comparison(device_a, device_b):
    """Compare each device pair."""
    return {
        'mean_diff': np.mean(device_a - device_b),
        'std_diff': np.std(device_a - device_b),
        'correlation': pearsonr(device_a, device_b)[0]
    }
```

**Expected Findings:**

- Higher fps devices (60fps) likely more accurate
- Higher resolution may improve landmark detection
- Webcams may have lower quality

**Deliverables:**

- `docs/validation/inter-device-reliability.md`
- ICC table across devices
- Recommended device specifications
- Known device-specific issues

**Success Criteria:**

- ICC > 0.85 across devices (acceptable)
- Identify best-performing device types
- Document device-specific corrections if needed

______________________________________________________________________

### 2.3 Frame Rate Sensitivity Study

**ROI:** ⭐⭐⭐⭐☆ | **Difficulty:** ⭐⭐☆☆☆ | **Time:** 4-6 hours

**Description:**
Quantify impact of video frame rate on measurement accuracy.

**Critical Question:**
Can 30fps video match accuracy of 120-240Hz validated apps?

**Test Protocol:**

```bash
# Record at highest fps available (60-120fps)
# Downsample to test lower rates

for fps in 60 48 30 24 15; do
    ffmpeg -i original_60fps.mp4 -r $fps downsampled_${fps}fps.mp4
    kinemotion dropjump-analyze downsampled_${fps}fps.mp4 > result_${fps}.json
done

# Compare metrics across frame rates
python scripts/analyze_fps_sensitivity.py
```

**Videos to Test:**

- 20 jumps recorded at 60fps (or 120fps if available)
- Mix of jump heights (low, medium, high)
- Mix of athletes (different speeds)

**Analysis:**

```python
def fps_sensitivity_analysis(results_by_fps):
    """Analyze how frame rate affects accuracy."""
    baseline = results_by_fps[60]  # 60fps as baseline

    for fps, results in results_by_fps.items():
        mae = mean_absolute_error(baseline, results)
        correlation = pearsonr(baseline, results)[0]

        print(f"{fps}fps: MAE={mae:.3f}m, r={correlation:.3f}")
```

**Expected Results:**

- Accuracy degrades with lower fps
- Quantify error vs frame rate relationship
- Determine minimum acceptable fps

**Deliverables:**

- `docs/validation/frame-rate-sensitivity.md`
- Plot: Accuracy vs Frame Rate
- Recommendation: Minimum fps for acceptable accuracy
- Update documentation with fps requirements

**Success Criteria:**

- Clear recommendation on minimum fps
- Quantified accuracy loss at lower fps
- User guidance updated

______________________________________________________________________

### 2.4 Add Validation Module to Codebase

**ROI:** ⭐⭐⭐⭐☆ | **Difficulty:** ⭐⭐⭐☆☆ | **Time:** 8-12 hours

**Description:**
Create reusable validation utilities for systematic testing.

**Module Structure:**

```python
# src/kinemotion/validation/__init__.py
from .reliability import calculate_icc, calculate_sem, calculate_mdl
from .agreement import bland_altman_analysis, calculate_bias
from .physics import check_energy_conservation, check_trajectory_validity
from .comparison import compare_to_manual, compare_devices
from .quality import assess_measurement_quality

# src/kinemotion/validation/reliability.py
def calculate_icc(
    measurements: list[list[float]],
    icc_type: str = "ICC(2,1)"
) -> tuple[float, tuple[float, float]]:
    """
    Calculate Intraclass Correlation Coefficient.

    Args:
        measurements: List of measurement sets (e.g., different sessions)
        icc_type: Type of ICC to calculate
            - ICC(1,1): One-way random effects
            - ICC(2,1): Two-way random effects, absolute agreement
            - ICC(3,1): Two-way mixed effects, consistency

    Returns:
        Tuple of (ICC value, 95% confidence interval)

    Reference:
        McGraw & Wong (1996). Forming inferences about some
        intraclass correlation coefficients.
    """
    ...

def calculate_sem(icc: float, sd: float) -> float:
    """
    Calculate Standard Error of Measurement.

    SEM = SD × sqrt(1 - ICC)

    Represents measurement precision.
    """
    return sd * np.sqrt(1 - icc)

def calculate_mdl(sem: float, confidence: float = 0.95) -> float:
    """
    Calculate Minimal Detectable Change.

    MDC = SEM × sqrt(2) × Z_score

    Smallest change that exceeds measurement error.
    """
    z_score = 1.96 if confidence == 0.95 else 2.576  # 99% CI
    return sem * np.sqrt(2) * z_score

# src/kinemotion/validation/agreement.py
def bland_altman_analysis(
    method_a: np.ndarray,
    method_b: np.ndarray,
    method_a_name: str = "Method A",
    method_b_name: str = "Method B"
) -> dict:
    """
    Perform Bland-Altman analysis for method comparison.

    Returns bias, limits of agreement, and plot data.

    Reference:
        Bland & Altman (1986). Statistical methods for assessing
        agreement between two methods of clinical measurement.
    """
    differences = method_a - method_b
    mean_values = (method_a + method_b) / 2

    bias = np.mean(differences)
    std_diff = np.std(differences, ddof=1)

    loa_upper = bias + 1.96 * std_diff
    loa_lower = bias - 1.96 * std_diff

    return {
        'bias': float(bias),
        'std_diff': float(std_diff),
        'loa_upper': float(loa_upper),
        'loa_lower': float(loa_lower),
        'differences': differences,
        'mean_values': mean_values,
        'n': len(differences)
    }

# src/kinemotion/validation/physics.py
def check_energy_conservation(
    takeoff_velocity: float,
    peak_height: float,
    tolerance: float = 0.05
) -> tuple[bool, float]:
    """
    Verify energy conservation: KE at takeoff → PE at peak.

    h_calculated = v² / (2g)

    Returns (is_valid, percent_error)
    """
    g = 9.81
    h_calculated = (takeoff_velocity ** 2) / (2 * g)
    error = abs(h_calculated - peak_height) / peak_height

    return (error < tolerance, error * 100)

def check_trajectory_validity(
    positions: np.ndarray,
    velocities: np.ndarray,
    accelerations: np.ndarray
) -> dict[str, bool]:
    """
    Check physics consistency of trajectory.

    Tests:
    1. Acceleration near -g during flight
    2. Velocity integrates to position
    3. Symmetric flight trajectory
    """
    ...
```

**Testing:**

```python
# tests/validation/test_reliability.py
def test_icc_perfect_agreement():
    """ICC should be 1.0 for identical measurements."""
    measurements = [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
    icc, ci = calculate_icc(measurements)
    assert icc == 1.0

def test_icc_no_agreement():
    """ICC should be near 0 for random measurements."""
    measurements = [[1.0, 2.0, 3.0], [3.0, 1.0, 2.0]]
    icc, ci = calculate_icc(measurements)
    assert icc < 0.5

def test_bland_altman():
    """Test Bland-Altman analysis calculation."""
    a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    b = np.array([1.1, 2.1, 2.9, 4.1, 4.9])

    result = bland_altman_analysis(a, b)

    assert 'bias' in result
    assert 'loa_upper' in result
    assert 'loa_lower' in result
```

**Deliverables:**

- New module: `src/kinemotion/validation/`
- Comprehensive tests
- Documentation: `docs/api/validation.md`
- Example notebooks in `notebooks/validation-examples/`

**Success Criteria:**

- All statistical methods validated against known results
- Easy to use for future validation studies
- Well-documented with references

______________________________________________________________________

## Priority 3: HIGH ROI + HIGH DIFFICULTY

### 3.1 Add Systematic Bias Correction Factors

**ROI:** ⭐⭐⭐⭐⭐ | **Difficulty:** ⭐⭐⭐⭐☆ | **Time:** 16-24 hours

**Description:**
Derive and apply correction equations for systematic bias (like Bishop 2022 for TTTO).

**Prerequisites:**

- Manual comparison study completed (#2.1)
- Sufficient data to establish correction relationship

**Methodology:**

```python
# 1. Collect paired data (automated vs manual)
automated = []  # kinemotion measurements
manual = []     # manual frame selection (gold standard)

# 2. Check for systematic bias
bias = np.mean(automated - manual)
if abs(bias) > 0.01:  # > 1cm systematic error
    print("Systematic bias detected")

# 3. Linear regression to find correction
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(automated.reshape(-1, 1), manual)

# Correction equation: y = ax + b
a = model.coef_[0]
b = model.intercept_

print(f"Correction: manual = {a:.4f} × automated + {b:.4f}")

# 4. Validate correction
corrected = a * automated + b
new_bias = np.mean(corrected - manual)
assert abs(new_bias) < 0.001  # Should eliminate bias
```

**Example from Bishop 2022:**

```python
# Time-to-take-off correction
# y = 0.8947x + 0.1507
# where y = force plate TTTO, x = manual TTTO

def apply_ttto_correction(raw_ttto: float) -> float:
    """Apply validated correction factor."""
    return 0.8947 * raw_ttto + 0.1507
```

**Implementation:**

```python
# src/kinemotion/correction.py
from dataclasses import dataclass
from typing import Literal

@dataclass
class CorrectionFactor:
    metric: str
    slope: float
    intercept: float
    r_squared: float
    n_samples: int
    validation_date: str
    reference: str

# Correction factors (to be determined from validation)
CORRECTION_FACTORS = {
    'jump_height': CorrectionFactor(
        metric='jump_height',
        slope=1.0,  # TBD from validation
        intercept=0.0,  # TBD from validation
        r_squared=0.0,  # TBD from validation
        n_samples=0,
        validation_date='TBD',
        reference='Internal validation study'
    ),
    'time_to_takeoff': CorrectionFactor(
        metric='time_to_takeoff',
        slope=1.0,  # TBD
        intercept=0.0,  # TBD
        r_squared=0.0,  # TBD
        n_samples=0,
        validation_date='TBD',
        reference='Internal validation study'
    )
}

def apply_correction(
    value: float,
    metric: str,
    apply: bool = True
) -> float:
    """Apply validated correction factor to measurement."""
    if not apply:
        return value

    factor = CORRECTION_FACTORS.get(metric)
    if factor is None:
        return value

    return factor.slope * value + factor.intercept
```

**Validation of Correction:**

```python
# Must validate on INDEPENDENT dataset
# - Training set: derive correction (n=30)
# - Test set: validate correction (n=20)

def validate_correction(test_automated, test_manual, correction_func):
    """Validate correction on independent dataset."""
    corrected = correction_func(test_automated)

    # Should eliminate bias
    bias_before = np.mean(test_automated - test_manual)
    bias_after = np.mean(corrected - test_manual)

    # Should improve agreement
    mae_before = mean_absolute_error(test_automated, test_manual)
    mae_after = mean_absolute_error(corrected, test_manual)

    return {
        'bias_before': bias_before,
        'bias_after': bias_after,
        'mae_before': mae_before,
        'mae_after': mae_after,
        'improvement': (mae_before - mae_after) / mae_before * 100
    }
```

**Deliverables:**

- Correction factors in `src/kinemotion/correction.py`
- Validation report: `docs/validation/correction-factors.md`
- Option to apply/disable corrections in API
- Updated accuracy claims with corrections applied

**Success Criteria:**

- Systematic bias reduced to \<0.5cm
- Correction validated on independent test set
- Improvement documented and published

______________________________________________________________________

### 3.2 Multi-Session Reliability Study

**ROI:** ⭐⭐⭐⭐☆ | **Difficulty:** ⭐⭐⭐⭐☆ | **Time:** 20-40 hours (data collection)

**Description:**
Establish test-retest reliability over multiple sessions (ecological validity).

**Study Design:**

```text
Participants: 10 athletes (recreationally trained)
Sessions: 5 sessions per athlete (2 weeks, every 3-4 days)
Jumps per session: 3 CMJ + 3 drop jump = 6 jumps
Total: 10 athletes × 5 sessions × 6 jumps = 300 jumps

Standardization:
- Same time of day (±2 hours)
- No training 24h before testing
- Same camera setup (distance, height, angle)
- Same warm-up protocol (5 min)
- Same environment (gym, lighting)
```

**Data Collection Protocol:**

```markdown
Session Protocol:
1. 5-minute standardized warm-up
   - Light jogging
   - Dynamic stretches
   - 3 practice jumps (submaximal)

2. Rest 2 minutes

3. Testing (randomized order):
   - 3 × CMJ (90s rest between)
   - 3 × Drop jump from 40cm box (90s rest)

4. Video recording:
   - Lateral view, 2.5m distance
   - 60fps, 1920×1080
   - Tripod-mounted, fixed position
   - Ensure full body in frame

5. Record:
   - Session date/time
   - Athlete ID (anonymized)
   - Jump order
   - Video filename
   - Any notes (fatigue, injury, etc.)
```

**Statistical Analysis:**

```python
# Within-session reliability
def calculate_within_session_icc(session_data):
    """ICC for 3 jumps within each session."""
    # ICC(3,1) - consistency within session
    ...

# Between-session reliability
def calculate_between_session_icc(athlete_data):
    """ICC across 5 sessions for each athlete."""
    # ICC(2,1) - absolute agreement across sessions
    ...

# Coefficient of Variation
def calculate_cv(measurements):
    """CV = (SD / Mean) × 100"""
    return (np.std(measurements) / np.mean(measurements)) * 100

# Minimal Detectable Change
def calculate_mdc(sem, confidence=0.95):
    """Smallest change exceeding measurement error."""
    z = 1.96 if confidence == 0.95 else 2.576
    return sem * np.sqrt(2) * z
```

**Expected Results:**

- **Within-session ICC:** > 0.90 (excellent)
- **Between-session ICC:** > 0.85 (good to excellent)
- **CV:** \< 10% (acceptable variability)
- **MDC:** Establishes meaningful change threshold

**Deliverables:**

- Raw data: `data/reliability-study/`
- Analysis notebook: `notebooks/reliability-analysis.ipynb`
- Report: `docs/validation/test-retest-reliability.md`
- Publication: Preprint on SportRxiv

**Success Criteria:**

- ICC values demonstrate acceptable reliability
- MDC values useful for practitioners
- Published validation data available
- Can claim "test-retest reliability established"

______________________________________________________________________

### 3.3 Implement Loaded Jump Support (F-v Profiling)

**ROI:** ⭐⭐⭐⭐☆ | **Difficulty:** ⭐⭐⭐⭐⭐ | **Time:** 24-40 hours

**Description:**
Enable force-velocity profiling (Samozino 2014) with loaded jumps.

**Theoretical Background:**

- Perform jumps at multiple loads (0%, 25%, 50%, 75%, 100% body mass)
- Plot force-velocity relationship
- Calculate Pmax, optimal F-v profile, F-v imbalance
- Identify if athlete is force- or velocity-oriented

**API Design:**

```python
# Single loaded jump
result = process_cmj_video(
    video_path="jump_50kg.mp4",
    additional_load_kg=50,
    athlete_mass_kg=75
)
# Returns: velocity, force (both normalized to body mass)

# Full F-v profile from multiple loads
fv_profile = calculate_fv_profile(
    jumps=[
        {"video": "jump_0kg.mp4", "load_kg": 0},
        {"video": "jump_20kg.mp4", "load_kg": 20},
        {"video": "jump_40kg.mp4", "load_kg": 40},
        {"video": "jump_60kg.mp4", "load_kg": 60},
        {"video": "jump_75kg.mp4", "load_kg": 75},
    ],
    athlete_mass_kg=75
)

print(fv_profile)
# {
#     'F0': 35.2,  # Theoretical max force (N/kg)
#     'v0': 3.1,   # Theoretical max velocity (m/s)
#     'Pmax': 27.3,  # Max power (W/kg)
#     'Sfv': -11.4,  # F-v slope (N.s.kg⁻¹.m⁻¹)
#     'Sfv_opt': -13.5,  # Optimal slope
#     'FvIMB': 15.6,  # F-v imbalance (%)
#     'profile_type': 'velocity_oriented'
# }
```

**Implementation:**

```python
# src/kinemotion/fv_profile.py
from dataclasses import dataclass
import numpy as np

@dataclass
class LoadedJumpResult:
    load_kg: float
    total_mass_kg: float
    velocity: float  # Mean velocity during push-off (m/s)
    force: float     # Mean force during push-off (N)
    power: float     # Mean power (W)

def calculate_loaded_jump_metrics(
    video_path: str,
    athlete_mass_kg: float,
    additional_load_kg: float,
    hpo: float  # Push-off distance (m)
) -> LoadedJumpResult:
    """
    Calculate force, velocity, power for loaded jump.

    Following Samozino et al. (2008) methodology:
    - Force = mg(h/hpo + 1) [normalized to body mass]
    - Velocity = sqrt(2gh) [mean during push-off]
    - Power = Force × Velocity
    """
    # Get jump height from video
    result = process_cmj_video(video_path)
    h = result['jump_height']

    # Total mass being moved
    total_mass = athlete_mass_kg + additional_load_kg

    # Calculate force (normalized to athlete body mass)
    g = 9.81
    F_abs = total_mass * g * (h / hpo + 1)  # Absolute force (N)
    F_norm = F_abs / athlete_mass_kg  # Normalized (N/kg)

    # Calculate velocity (mean during push-off)
    v = np.sqrt(2 * g * h)

    # Calculate power (normalized)
    P_norm = F_norm * v  # W/kg

    return LoadedJumpResult(
        load_kg=additional_load_kg,
        total_mass_kg=total_mass,
        velocity=v,
        force=F_norm,
        power=P_norm
    )

def fit_fv_relationship(jumps: list[LoadedJumpResult]) -> dict:
    """
    Fit linear F-v relationship and calculate profile.

    F = F0 - (F0/v0) × v
    where F0 = force intercept, v0 = velocity intercept

    Pmax = F0 × v0 / 4
    Sfv = -F0/v0 (slope)
    """
    forces = np.array([j.force for j in jumps])
    velocities = np.array([j.velocity for j in jumps])

    # Linear regression
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(velocities.reshape(-1, 1), forces)

    F0 = model.intercept_  # Force at zero velocity
    slope = model.coef_[0]
    v0 = -F0 / slope  # Velocity at zero force

    Sfv = slope  # F-v slope
    Pmax = F0 * v0 / 4  # Max power

    # Calculate optimal Sfv (Samozino 2012 equation)
    # Sfv_opt depends on Pmax and hpo
    # Simplified: Sfv_opt ≈ -sqrt(Pmax / (hpo × g))

    return {
        'F0': float(F0),
        'v0': float(v0),
        'Pmax': float(Pmax),
        'Sfv': float(Sfv),
        'Sfv_opt': float(Sfv_opt),  # TBD: implement Samozino equation
        'FvIMB': float(abs((Sfv - Sfv_opt) / Sfv_opt) * 100),
        'r_squared': float(model.score(velocities.reshape(-1, 1), forces))
    }
```

**Validation Requirements:**

- Must validate loaded jump calculations against force plate
- Complex biomechanics (additional load affects push-off)
- Requires careful testing

**Deliverables:**

- `src/kinemotion/fv_profile.py` module
- Documentation: `docs/guides/force-velocity-profiling.md`
- Example notebook: `notebooks/fv-profiling-example.ipynb`
- Tests with known F-v relationships

**Success Criteria:**

- Mathematically correct implementation
- Matches Samozino equations
- Validated against published data
- User-friendly API

______________________________________________________________________

## Priority 4: MEDIUM ROI + LOW DIFFICULTY

### 4.1 Improved Debug Visualizations

**ROI:** ⭐⭐⭐☆☆ | **Difficulty:** ⭐⭐☆☆☆ | **Time:** 4-8 hours

**Description:**
Enhanced debug video output with on-screen indicators.

**Features:**

- Confidence score displayed
- Phase labels (standing, eccentric, concentric, flight)
- Velocity/acceleration graphs overlaid
- Warnings when quality drops
- Timeline showing detected events

**Example Output:**

```text
[Video Frame]
┌─────────────────────────────────┐
│ Confidence: HIGH (0.89)         │
│ Phase: FLIGHT                   │
│ Jump Height: 0.35m              │
│ Flight Time: 0.532s             │
├─────────────────────────────────┤
│ ⚠ Warning: Low visibility 0.65  │
└─────────────────────────────────┘

[Velocity Graph Below]
  ▲
  │     ╱╲
v │    ╱  ╲
  │   ╱    ╲___
  │  ╱
  └──────────────► time
     ^    ^  ^
     |    |  |
    start|  land
     takeoff
```

**Implementation:**

```python
# src/kinemotion/visualization/enhanced_debug.py
def create_enhanced_debug_overlay(
    frame: np.ndarray,
    metrics: dict,
    quality: QualityAssessment,
    current_phase: str,
    velocity_history: list[float],
    time_ms: int
) -> np.ndarray:
    """Create informative debug overlay."""
    ...
```

**Success Criteria:**

- Users can understand what system is detecting
- Helps debug false detections
- Educational value

______________________________________________________________________

### 4.2 Batch Analysis Dashboard

**ROI:** ⭐⭐⭐☆☆ | **Difficulty:** ⭐⭐☆☆☆ | **Time:** 8-12 hours

**Description:**
HTML report for batch processing results.

**Features:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Kinemotion Batch Analysis</title>
</head>
<body>
    <h1>Jump Analysis Report</h1>

    <section id="summary">
        <h2>Summary Statistics</h2>
        <table>
            <tr><td>Total Jumps:</td><td>50</td></tr>
            <tr><td>Mean Height:</td><td>0.35 ± 0.08m</td></tr>
            <tr><td>High Confidence:</td><td>45/50 (90%)</td></tr>
        </table>
    </section>

    <section id="trends">
        <h2>Trend Analysis</h2>
        <canvas id="heightChart"></canvas>
    </section>

    <section id="outliers">
        <h2>Flagged Jumps</h2>
        <ul>
            <li>jump_12.mp4: Low confidence (visibility)</li>
            <li>jump_37.mp4: Unusually low height</li>
        </ul>
    </section>
</body>
</html>
```

**Usage:**

```bash
kinemotion cmj-analyze videos/*.mp4 --batch --report dashboard.html
open dashboard.html
```

**Success Criteria:**

- Professional-looking reports
- Useful for coaches/researchers
- Easy to share results

______________________________________________________________________

### 4.3 Environmental Condition Documentation

**ROI:** ⭐⭐⭐☆☆ | **Difficulty:** ⭐⭐☆☆☆ | **Time:** 4-8 hours

**Description:**
Test and document optimal recording conditions.

**Conditions to Test:**

1. **Lighting:**

   - Indoor gym (bright)
   - Indoor gym (dim)
   - Outdoor sunny
   - Outdoor cloudy
   - Outdoor dusk

1. **Camera Distance:**

   - 1m (close)
   - 2m (optimal?)
   - 3m (far)
   - 5m (very far)

1. **Camera Angle:**

   - 90° lateral (frontal plane)
   - 60° diagonal
   - 45° diagonal

1. **Background:**

   - Plain wall
   - Cluttered (equipment)
   - Outdoor (trees, buildings)

**Data Collection:**

- Same athlete performs 3 jumps in each condition
- Record video
- Process with kinemotion
- Note: visibility scores, tracking quality, detection success

**Deliverable:**

- `docs/guides/recording-guidelines.md`
- Best practices for video capture
- Common failure modes
- Troubleshooting guide

**Success Criteria:**

- Users know how to set up for best results
- Failure modes documented
- Realistic expectations set

______________________________________________________________________

## Priority 5: MEDIUM ROI + MEDIUM DIFFICULTY

### 5.1 Clothing Effect Study

**ROI:** ⭐⭐⭐☆☆ | **Difficulty:** ⭐⭐⭐☆☆ | **Time:** 4-8 hours

**Description:**
Quantify impact of clothing on landmark detection accuracy.

**Test Protocol:**

- Same athlete, 3 clothing conditions:

  1. Compression tights + fitted shirt (best case)
  1. Basketball shorts + t-shirt (typical)
  1. Loose sweatpants + hoodie (worst case)

- 10 jumps per condition

- Compare: visibility scores, tracking stability, metric consistency

**Expected Result:**

- Tight clothing → better tracking
- Loose clothing → more jitter, lower visibility
- Quantify degradation

**Deliverable:**

- Documentation with recommendations
- Photos showing good/bad examples

______________________________________________________________________

### 5.2 Physics-Based Sanity Checks

**ROI:** ⭐⭐⭐☆☆ | **Difficulty:** ⭐⭐⭐☆☆ | **Time:** 8-12 hours

**Description:**
Automatic validation using physics laws.

**Checks to Implement:**

```python
# Energy conservation
def check_energy_conservation(v_takeoff, h_peak):
    """h_calculated = v²/(2g) should match h_measured"""
    h_calc = v_takeoff**2 / (2 * 9.81)
    error = abs(h_calc - h_peak) / h_peak
    if error > 0.1:  # >10% error
        return False, f"Energy mismatch: {error*100:.1f}%"
    return True, "OK"

# Biological plausibility
def check_plausibility(metrics):
    """Flag implausible values."""
    warnings = []

    if metrics['jump_height'] > 0.80:
        warnings.append("Unusually high jump (world-class)")
    if metrics['jump_height'] < 0.10:
        warnings.append("Unusually low jump")
    if metrics.get('gct', 1.0) < 0.10:
        warnings.append("Impossibly short ground contact")
    if metrics.get('gct', 0.0) > 2.0:
        warnings.append("Unusually long ground contact")

    return warnings

# Trajectory consistency
def check_trajectory(positions, velocities):
    """Velocity should integrate to position."""
    # Numerical integration
    integrated_pos = np.cumsum(velocities)
    correlation = pearsonr(positions, integrated_pos)[0]

    if correlation < 0.9:
        return False, f"Trajectory inconsistent (r={correlation:.2f})"
    return True, "OK"
```

**Success Criteria:**

- Catches obvious errors automatically
- Builds user confidence
- Reduces false positives

______________________________________________________________________

### 5.3 Web Interface for Video Upload

**ROI:** ⭐⭐⭐☆☆ | **Difficulty:** ⭐⭐⭐☆☆ | **Time:** 16-24 hours

**Description:**
Simple web UI for video analysis.

**Stack:**

- Backend: FastAPI (Python)
- Frontend: React or vanilla HTML/JS
- Video processing: Async tasks with Celery

**Features:**

- Upload video
- Select jump type (drop jump / CMJ)
- View results
- Download JSON + debug video
- History of previous analyses

**Deployment:**

- Docker container
- Can run locally or deploy to cloud
- Optional: host demo at kinemotion.app

**Success Criteria:**

- Easy for non-technical users
- No CLI knowledge required
- Good for demos and education

______________________________________________________________________

## Priority 6: LOW ROI (Nice to Have)

### 6.1 Real-Time Analysis Mode

**ROI:** ⭐⭐☆☆☆ | **Difficulty:** ⭐⭐⭐⭐☆ | **Time:** 24-40 hours

Live webcam analysis with immediate feedback.

**Challenges:**

- Real-time performance (need GPU)
- Latency issues
- Not needed for validation

______________________________________________________________________

### 6.2 Mobile App

**ROI:** ⭐⭐☆☆☆ | **Difficulty:** ⭐⭐⭐⭐⭐ | **Time:** 100+ hours

Native iOS/Android app.

**Why Low ROI:**

- Massive effort
- Maintenance burden
- Python CLI + smartphone video already works
- Commercial apps already exist (MyJump)

______________________________________________________________________

### 6.3 3D Pose Integration

**ROI:** ⭐⭐☆☆☆ | **Difficulty:** ⭐⭐⭐⭐⭐ | **Time:** 60+ hours

Use MediaPipe 3D world coordinates.

**Why Low ROI:**

- 2D sufficient for sagittal plane
- Adds complexity
- Also unvalidated

______________________________________________________________________

### 6.4 Integration with Training Platforms

**ROI:** ⭐⭐☆☆☆ | **Difficulty:** ⭐⭐⭐⭐☆ | **Time:** 40+ hours

Export to TrainingPeaks, Strava, etc.

**Why Low ROI:**

- Feature creep
- API maintenance
- Users can export JSON themselves

______________________________________________________________________

### 6.5 Longitudinal Database & Tracking

**ROI:** ⭐⭐☆☆☆ | **Difficulty:** ⭐⭐⭐⭐☆ | **Time:** 40+ hours

Database for tracking progress over time.

**Why Low ROI:**

- Not core validation work
- Users can manage their own data
- Adds complexity and maintenance

______________________________________________________________________

## 3-Month Implementation Plan

### Month 1: Foundation & Quick Wins

**Weeks 1-2:**

1. Documentation of limitations (2h) ✅
1. Test-retest determinism test (2h) ✅
1. Add confidence scores (8h) ✅
1. Known height validation (4h) ✅

**Weeks 3-4:**
5\. Parameter sensitivity report (8h) ✅
6\. Start manual comparison study (data collection) ✅

**Deliverable:**

- Updated documentation with limitations
- Confidence scores in output
- Known height validation report
- Parameter sensitivity analysis

______________________________________________________________________

### Month 2: Comparative Validation

**Weeks 5-6:**
7\. Complete manual comparison study (16h) ✅
8\. Inter-device reliability study (8h) ✅

**Weeks 7-8:**
9\. Frame rate sensitivity study (6h) ✅
10\. Add validation module to code (12h) ✅

**Deliverable:**

- Manual comparison report with ICC, Bland-Altman
- Inter-device reliability data
- Frame rate recommendations
- Validation utilities in codebase

______________________________________________________________________

### Month 3: Polish & Publication

**Weeks 9-10:**
11\. Physics-based sanity checks (12h) ✅
12\. Environmental condition testing (8h) ✅

**Weeks 11-12:**
13\. Improved debug visualizations (8h) ✅
14\. Write technical validation report ✅
15\. Prepare preprint for publication ✅

**Deliverable:**

- Comprehensive technical report
- Published preprint (OSF/SportRxiv)
- Updated documentation
- Validated open-source tool

______________________________________________________________________

## Success Metrics

**After 3 Months:**

**Quantitative:**

- [ ] Test-retest ICC calculated (target: >0.90)
- [ ] Inter-device ICC calculated (target: >0.85)
- [ ] Correlation with manual method (target: r>0.95)
- [ ] Bias vs manual method (target: \<2cm)
- [ ] Known height MAE (target: \<20ms)

**Qualitative:**

- [ ] Technical report published as preprint
- [ ] Limitations clearly documented
- [ ] Optimal recording conditions established
- [ ] Confidence scoring implemented
- [ ] Physics validation completed

**Claims We CAN Make:**

- ✅ "Test-retest reliability established (ICC=X.XX)"
- ✅ "Strong correlation with manual frame selection (r=X.XX)"
- ✅ "Suitable for training monitoring"
- ✅ "Best results at 60fps, 2-3m distance, good lighting"

**Claims We CANNOT Make:**

- ❌ "Validated against force plates"
- ❌ "Suitable for research publications"
- ❌ "Clinically validated"
- ❌ "Equivalent to MyJump" (MyJump has force plate validation)

______________________________________________________________________

## Future Work (Beyond 3 Months)

**When Lab Equipment Becomes Available:**

1. Force plate validation study (gold standard)
1. Derive correction factors if needed
1. Publish in peer-reviewed journal
1. Claim "validated for research use"

**Advanced Features:**

1. Loaded jump support (F-v profiling)
1. Multi-session longitudinal tracking
1. Alternative pose models comparison
1. Machine learning for phase detection

**User-Facing:**

1. Web interface
1. Mobile app
1. Training platform integrations
1. Real-time analysis mode

______________________________________________________________________

## Appendix: References

### Key Validation Papers

- Balsalobre-Fernández et al. (2015) - MyJump validation
- Bishop et al. (2022) - MyJumpLab validation with corrections
- Samozino et al. (2014) - F-v imbalance theory
- Armstrong et al. (2025) - MediaPipe Pose clinical validation
- Bland & Altman (1986) - Agreement analysis methods
- McGraw & Wong (1996) - ICC calculation guidelines

### Biomechanics Theory

- Bosco et al. (1983) - Flight time method
- Samozino et al. (2012) - Optimal F-v profile
- Dempster (1955) - Body segment parameters
- Ebben & Petushek (2010) - RSI_mod definition

______________________________________________________________________

## Document Changelog

**Version 1.0 (2025-01-13):**

- Initial roadmap created
- Items ranked by ROI and difficulty
- 3-month plan established
- Success metrics defined
