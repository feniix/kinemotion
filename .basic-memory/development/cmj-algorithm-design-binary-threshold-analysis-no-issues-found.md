---
title: CMJ Algorithm Design - Binary Threshold Analysis (No Issues Found)
type: note
permalink: development/cmj-algorithm-design-binary-threshold-analysis-no-issues-found
tags:
- CMJ
- binary-thresholds
- event-detection
- algorithm-analysis
- validation
- robustness
---

# CMJ Algorithm Design - Binary Threshold Analysis

**Date:** 2026-01-06
**Investigation:** Event detection amplification from algorithm design
**Status:** COMPLETE - No issues found

## Executive Summary

**Finding:** Binary thresholds exist in CMJ code but **are NOT causing problems**.

**Evidence:**
- Standing End: Perfect consistency (0.0 frame std deviation)
- Takeoff: Excellent accuracy (0.33 frame MAE = 5.6ms)
- Landing: Good accuracy (0.67 frame MAE = 11ms with IMPACT)

**Conclusion:** The algorithm is working excellently. No changes needed.

---

## Binary Threshold Locations

### Issue #1: Standing End Detection

**Location:** `src/kinemotion/cmj/analysis.py:658`

```python
for i in range(baseline_end, int(lowest_point)):
    if accelerations[i] > accel_threshold:  # Binary threshold
        return float(i)
```

**Theoretical Problem:**
- Single-frame comparison: `accel[i] > threshold`
- No temporal averaging
- No hysteresis

**Theoretical Impact:** ±2-3 frames (33-50ms)

**Actual Performance:**
- **0.0 frame std deviation** across 3 videos (PERFECT)
- All videos detected at same frame in repeated runs

**Why It Works:**
1. **Strong signal:** Acceleration spike is clearly above 3σ threshold
2. **Smoothing:** Savitzky-Golay filter (window=5) reduces noise
3. **Unambiguous transition:** Standing → Countermovement is distinct

### Issue #2: Takeoff Detection

**Location:** `src/kinemotion/cmj/analysis.py:398`

```python
for i in range(peak_vel_frame, peak_height_frame):
    if accelerations[i] > 0:  # Binary zero crossing
        return float(i)
```

**Theoretical Problem:**
- Binary zero crossing: `accel > 0`
- No hysteresis around transition

**Theoretical Impact:** ±1-2 frames (17-33ms)

**Actual Performance:**
- **0.33 frame MAE** = 5.6ms (EXCELLENT)
- 2/3 videos perfectly matched ground truth
- 1/3 videos off by 1 frame

**Why It Works:**
1. **Sharp transition:** Deceleration onset is clear
2. **Velocity-based:** Uses peak velocity as anchor
3. **Good validation:** 5.6ms error is negligible

### Issue #3: Legacy Velocity Detection

**Location:** `src/kinemotion/cmj/analysis.py:666`

```python
low_vel = np.abs(standing_search) < 0.005  # Binary threshold
```

**Status:** Fallback code (not currently used)

**Primary method:** Acceleration-based detection (above)

---

## Why Binary Thresholds Work in CMJ

### 1. Strong Signal-to-Noise Ratio

**Acceleration signal characteristics:**
- Standing phase: Mean ≈ 0.000, Std ≈ 0.001 (baseline)
- Movement onset: Spike to 0.005-0.010 (5-10× baseline)
- Detection threshold: mean + 3×std ≈ 0.003
- **Margin:** 2-3× above threshold (clear separation)

**Result:** No oscillation around threshold

### 2. Savitzky-Golay Smoothing

**Applied before velocity/acceleration calculation:**
```python
window_length = 5  # frames
polyorder = 2
positions = savgol_filter(positions, window_length, polyorder)
```

**Effect:**
- Reduces high-frequency noise
- Smooths single-frame spikes
- Preserves signal shape

**Impact:** 0.048% landmark variance → minimal after smoothing

### 3. Validation Results Prove It Works

| Metric | Accuracy | Assessment |
|--------|----------|------------|
| Standing End | 0.0 frame std | PERFECT |
| Takeoff | 0.33 frame MAE (5.6ms) | EXCELLENT |
| Landing (IMPACT) | 0.67 frame MAE (11ms) | GOOD |

**Conclusion:** Binary thresholds are NOT causing practical issues

---

## Comparison: Drop Jump vs CMJ

### Drop Jump (The Problem Case)

**From our previous study:**
- 59% RSI variation across runs
- Binary thresholds on position comparisons
- Multiple phase classifications (single vs double contact)
- Small position differences (0.049 vs 0.051) → flip classification

**Solution implemented:**
- Temporal averaging (median over 3 frames)
- Hysteresis thresholds
- Adaptive thresholds

### CMJ (The Good Case)

**Current validation:**
- 0% variation in standing end
- 5.6ms error in takeoff
- 11ms error in landing
- Single, clear movement pattern
- Strong acceleration spikes

**No changes needed:**
- Signal is unambiguous
- Smoothing is sufficient
- Transitions are clear

---

## The 14% Jump Height Difference

### Not from Binary Thresholds!

**Root cause:** Semantic difference between CONTACT and IMPACT methods

**CONTACT method:**
- Detects: Deceleration onset (10% of max deceleration)
- Frame: 140, 142, 127 (example)
- Flight time: 600ms
- Jump height: 0.44m

**IMPACT method:**
- Detects: Maximum deceleration spike (impact)
- Frame: 142, 145, 129 (2-3 frames later)
- Flight time: 633ms (+33ms = +5.6%)
- Jump height: 0.49m (+0.05m = +11.6%)

**Why the difference:**
- IMPACT detects later event (impact vs onset)
- Later landing = longer flight = higher jump
- This is BY DESIGN, not noise

**Both methods valid:**
- IMPACT: Matches visual annotation (coaching use)
- CONTACT: Force-plate equivalent (research use)

---

## Recommendations

### For CMJ (Current Code)

**✅ LEAVE AS-IS**

**Rationale:**
1. Excellent validation results
2. No practical issues from binary thresholds
3. Signal-to-noise ratio is sufficient
4. Smoothing provides robustness

### If Future Improvements Desired

**Optional enhancements** (not currently needed):

**Option 1: Temporal Averaging**
```python
# Replace single-frame check
if accelerations[i] > threshold:

# With 3-frame median
if np.median(accelerations[i-1:i+2]) > threshold:
```

**Pros:** More robust to single-frame noise
**Cons:** More complex, may not help (already working)

**Option 2: Hysteresis**
```python
# Add two thresholds
THRESHOLD_ENTER = 0.005  # Trigger on
THRESHOLD_EXIT = 0.003   # Trigger off

if accel > THRESHOLD_ENTER and not triggered:
    triggered = True
    return frame
elif accel < THRESHOLD_EXIT and triggered:
    triggered = False
```

**Pros:** Prevents flipping
**Cons:** More parameters, harder to tune

**Option 3: Sub-frame Interpolation**
```python
# Instead of integer frames
if accelerations[i] > threshold:
    return float(i)

# Use interpolation
if accelerations[i] > threshold:
    # Linear interpolation between frames
    fraction = (threshold - accel[i-1]) / (accel[i] - accel[i-1])
    return float(i - 1 + fraction)
```

**Pros:** Theoretically more precise
**Cons:** More complex, validation unclear

---

## Action Items

### Immediate (None Required)

**✅ No changes needed for CMJ**

**Rationale:**
- Algorithm is working excellently
- Binary thresholds are not causing issues
- Validation proves robustness

### Documentation

**✅ Document current state:**
- Binary thresholds exist but work well
- Validation results demonstrate robustness
- Drop jump was the problematic case (already fixed)

### Future Considerations

**If validation shows issues:**
1. Add temporal averaging to standing end detection
2. Add hysteresis to takeoff zero crossing
3. Increase smoothing window if needed

**Trigger:** Validation shows >2 frame MAE in any phase

---

## Conclusion

**Binary thresholds are NOT the problem.**

**Evidence:**
1. Perfect standing end consistency (0.0 std)
2. Excellent takeoff accuracy (0.33 frame MAE)
3. Good landing accuracy (0.67 frame MAE)
4. Strong signal-to-noise ratio
5. Effective smoothing

**The 14% metric difference:**
- From CONTACT vs IMPACT semantic difference
- By design (different events detected)
- Not a bug or algorithm issue

**Recommendation:**
- Accept current implementation as robust
- Focus on IMPACT method adoption
- Document landing method choice
- No algorithm changes needed

---

**Tags:** CMJ, binary-thresholds, event-detection, algorithm-analysis, validation, robustness
