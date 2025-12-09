---
title: AthletePose3D Final Strategy - Accuracy and Robustness
type: note
permalink: development/athlete-pose3-d-final-strategy-accuracy-and-robustness
tags:
- athletepose3d
- accuracy
- robustness
- strategy
---

# AthletePose3D Final Strategy: Accuracy & Robustness

**Date:** 2025-12-08
**Status:** Determinism verified ✅, Now testing Accuracy + Robustness in parallel

---

## Key Discovery: Determinism Already Perfect

Tested drop jump analysis on 3 videos × 3 runs = **100% deterministic**:

```
dj-45-IMG_6739.MOV: RSI = 3.7186533116576643 (identical across 3 runs)
dj-45-IMG_6740.MOV: RSI = 3.1705635822212423 (identical across 3 runs)
dj-45-IMG_6741.MOV: RSI = 4.016533853743156 (identical across 3 runs)
```

**Conclusion:** AthletePose3D is NOT needed for determinism - already working perfectly.

---

## Revised Strategy: Focus on What Matters

### Track A: Accuracy Validation (In Progress)
**Agent:** Computer Vision Engineer
**Goal:** Measure absolute accuracy using camera projection
**Method:**
- Use `camera_projection.py` (Track 2 solution)
- Calculate pixel-level MPJPE on AP3D videos
- Compare with research benchmarks

**Deliverables:**
- `validator_mpjpe.py` - Working MPJPE calculator
- `reports/ap3d_accuracy_baseline.md` - Accuracy report
- Baseline: 78px MPJPE (from Track 2 test)

**Value:** Know if MediaPipe is "good enough" or needs improvement

---

### Track B: Robustness Analysis (In Progress)
**Agent:** ML Data Scientist
**Goal:** Understand parameter sensitivity
**Method:**
- Test quality presets on 3 drop jump videos
- Vary smoothing/filtering parameters
- Measure RSI variance

**Deliverables:**
- `test_parameter_sensitivity.py` - Parameter testing script
- `reports/parameter_sensitivity_analysis.md` - Findings
- Identification of most stable parameters

**Value:** Know which parameters minimize unwanted variance

---

## Why This Makes Sense

### Accuracy tells us:
- **"Are we close to ground truth?"**
- MediaPipe detects ankle at (512, 384)
- Ground truth is (489, 401)
- MPJPE = 28 pixels = good!

### Robustness tells us:
- **"Do small changes break things?"**
- smoothing_window=5 → RSI=3.2
- smoothing_window=7 → RSI=3.2 (stable ✅)
- smoothing_window=11 → RSI=2.9 (sensitive ⚠️)

### Combined:
**"MediaPipe is X% accurate AND parameters should be set to Y for lowest variance"**

---

## Expected Outcomes

### Best Case (Both Succeed):
✅ **Accuracy:** "MediaPipe achieves 60-90px MPJPE on athletic jumps (good baseline)"
✅ **Robustness:** "smoothing_window=7, filter_cutoff=8Hz minimizes variance"
✅ **Action:** Create "athletic" preset with robust parameters

### Likely Case:
✅ **Accuracy:** "MPJPE varies: 50px (Axel) to 120px (Running)"
✅ **Robustness:** "balanced preset already near-optimal, minor tuning possible"
✅ **Action:** Decide if improvement worth Phase 2 effort

---

## Integration Plan

When both tracks complete:

1. **Accuracy Report:**
   - "MediaPipe baseline: X pixels MPJPE"
   - "Movement-specific: Axel=Y, Running=Z"

2. **Robustness Report:**
   - "Current variance: ±W% across similar videos"
   - "Optimal parameters: [smoothing=X, filter=Y]"
   - "Expected variance reduction: V%"

3. **Combined Recommendation:**
   - If accuracy good + low variance → Phase 1 complete, use for marketing
   - If accuracy good + high variance → Tune parameters (Phase 2a only)
   - If accuracy poor → Full Phase 2-3 needed

---

## Timeline

**Accuracy Track:** 2-3 hours (camera projection + validation run)
**Robustness Track:** 1-2 hours (parameter testing on 3 videos)

**Parallel completion:** ~3 hours total (vs 5 hours sequential)

---

## Current Status

- ✅ Determinism: Verified perfect
- 🔄 Accuracy: Agent working on MPJPE validation
- 🔄 Robustness: Agent testing parameter sensitivity
- ⏳ Results: Expected in 1-3 hours

---

**Next:** Wait for agents to complete, then integrate findings into final Phase 1 report.
