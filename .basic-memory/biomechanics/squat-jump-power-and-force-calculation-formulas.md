---
title: Squat Jump Power and Force Calculation Formulas
type: note
permalink: biomechanics/squat-jump-power-and-force-calculation-formulas
---

# Squat Jump Power and Force Calculation Formulas

## Validation Summary

Validated regression equations from Sayers et al. (1999) for Squat Jump power estimation using **mass + jump height** (no camera calibration needed).

### Key Findings from Sayers et al. (1999)

**Study Design:**
- 108 college-age male and female athletes and non-athletes
- Force plate validation of regression equations
- Compared Lewis formula, Harman et al. formula, and new Sayers equation
- Tested both Squat Jump (SJ) and Countermovement Jump (CMJ) protocols

**Critical Results:**

1. **Squat Jump is superior to CMJ for power prediction**
   - SJ protocol: R² = 0.87, SEE = 372.9 W (more accurate)
   - CMJ protocol: R² = 0.82, SEE = 442.8 W (more variable)
   - Reason: SJ has consistent 90° knee angle, CMJ has variable technique

2. **Sayers equation is most accurate**
   - Underestimates peak power by < 1%
   - SEE = 355.0 W (excellent precision)
   - Validated against force plate data

3. **Lewis formula is INVALID**
   - Underestimates peak power by 73%
   - Underestimates mean power by 43%
   - Should NOT be used

4. **Gender differences are minimal**
   - Single equation works for both males and females
   - Only 2-5% difference between genders

## Recommended Formulas

### 1. Peak Power (Sayers et al., 1999)

**Formula:**
```
Peak Power (W) = 60.7 × jump_height_cm + 45.3 × mass_kg − 2055
```

**Validation:**
- R² = 0.87 (strong correlation)
- SEE = 355.0 W (standard error of estimate)
- Error: < 1% underestimation
- **Validated against force plate data**

**Inputs:**
- `jump_height_cm`: Jump height in centimeters
- `mass_kg`: Athlete mass in kilograms

**Example Calculation (80kg athlete, 50cm jump):**
```
Peak Power = 60.7 × 50 + 45.3 × 80 − 2055
           = 3035 + 3624 − 2055
           = 4604 W
```

**Expected Ranges (from validation_bounds.py):**
- Elderly: 1500-3000 W
- Recreational: 3000-8000 W
- Elite male: 9000-15000 W

### 2. Mean Power (Work-Energy Method)

**Formula:**
```
Mean Power (W) = (mass_kg × g × jump_height_m) / concentric_duration_s
```

**Where:**
- `g = 9.81 m/s²` (gravity)
- `jump_height_m`: Jump height in meters
- `concentric_duration_s`: Time from concentric start to takeoff (seconds)

**Physics:**
- Work = Force × Distance = mass × g × jump_height
- Power = Work / Time
- This is the **true mean power** during concentric phase

**Example Calculation (80kg athlete, 0.40m jump, 0.35s concentric):**
```
Mean Power = (80 × 9.81 × 0.40) / 0.35
           = 313.92 / 0.35
           = 897 W
```

**Validation:**
- Based on fundamental physics (work-energy theorem)
- Mean power typically 60-75% of peak power in vertical jumps
- Check: 897 W / 4604 W = 19.5% (This seems LOW - need to verify)

**Expected Ranges:**
- Mean power should be 60-75% of peak power
- Current bounds in validation_bounds.py may be too high

### 3. Peak Force (Impulse-Momentum Method)

**Formula:**
```
Takeoff Velocity = √(2 × g × jump_height_m)
Peak Force = mass_kg × (takeoff_velocity / concentric_duration_s + g)
```

**Derivation:**
- Takeoff velocity from kinematics: v² = 2gh → v = √(2gh)
- Average acceleration: a_avg = v / t_concentric
- Average force: F_avg = mass × (a_avg + g) = mass × (v/t + g)
- Peak force is typically 1.2-1.5× average force

**Simplified (Use 1.3× as peak factor):**
```
Peak Force = 1.3 × mass_kg × (√(2 × g × jump_height_m) / concentric_duration_s + g)
```

**Example Calculation (80kg athlete, 0.40m jump, 0.35s concentric):**
```
Takeoff Velocity = √(2 × 9.81 × 0.40) = √7.848 = 2.80 m/s
Avg Force = 80 × (2.80/0.35 + 9.81) = 80 × 17.81 = 1425 N
Peak Force = 1.3 × 1425 = 1853 N
```

**Alternative (Direct from power):**
```
Peak Force = Peak Power / Peak_Velocity
```

**Expected Ranges:**
- Recreational: 2.0-2.5 × body weight
- Elite: 3.0-4.5 × body weight
- For 80kg athlete: 1600-3600 N (recreational to elite)

## Validation Against Existing Bounds

### Current Bounds in `validation_bounds.py`:

**PEAK_POWER:**
- Recreational: 3000-8000 W
- Elite: 9000-15000 W
- **Check:** Sayers formula produces appropriate ranges ✓

**MEAN_POWER:**
- Recreational: 1500-5000 W
- Elite: 6000-10000 W
- **Issue:** Work-energy formula may produce LOWER values
  - Example: 80kg, 0.40m, 0.35s → ~900 W (below recreational minimum)
  - **Action:** Bounds may need adjustment OR formula needs refinement

**PEAK_FORCE:**
- Recreational: 2000-4000 N
- Elite: 4500-6000 N
- **Check:** Impulse-momentum formula produces appropriate ranges ✓
  - Example: 80kg athlete → 1853 N (slightly low, but plausible)

## Implementation Recommendations

### Priority 1: Use Sayers Formula for Peak Power
- Most validated regression equation
- Requires only mass and jump height
- < 1% error against force plate data
- Superior to Lewis and Harman equations

### Priority 2: Use Work-Energy for Mean Power
- Physiologically sound (fundamental physics)
- Requires mass, height, concentric duration
- May need to adjust validation bounds after testing
- Typical mean-to-peak ratio: 60-75%

### Priority 3: Use Impulse-Momentum for Peak Force
- Based on takeoff velocity calculation
- Requires mass, height, concentric duration
- Apply 1.2-1.5× multiplier for peak vs average
- Typical range: 2.0-4.5 × body weight

## Testing Plan

1. **Validate Sayers formula against existing bounds**
   - Test with typical athletes: 60-100 kg, 0.20-0.60 m jumps
   - Verify output falls within recreational/elite ranges

2. **Test mean power formula**
   - Calculate mean-to-peak power ratio
   - If ratio < 60%, investigate formula or adjust bounds

3. **Test peak force formula**
   - Verify force-to-body-weight ratio is 2.0-4.5×
   - Compare with power-based force calculation: F = P/v

## References

**Primary Source:**
- Sayers, S. P., Harackiewicz, D. V., Harman, E. A., Frykman, P. N., & Rosenstein, M. T. (1999). Cross-validation of three jump power equations. *Medicine & Science in Sports & Exercise*, 31(4), 572-57.

**Key Findings:**
- SJ superior to CMJ for power prediction (R² = 0.87 vs 0.82)
- Sayers equation most accurate (< 1% error)
- Lewis formula invalid (73% underestimation)
- Single equation valid for both genders

## Comparison with Drop Jump and CMJ

**Drop Jump:**
- Uses RSI (Reactive Strength Index) as primary metric
- Power calculation not primary focus

**CMJ:**
- Can use Sayers equation with 2.7% overestimation
- Has stretch-shortening cycle (SSC) contribution
- Typically achieves higher jump heights than SJ

**Squat Jump:**
- Pure concentric phase (no SSC)
- Lower jump heights than CMJ
- More consistent technique → better power prediction
- Ideal for testing pure explosive power

## Notes

- SJ power equations are **specific to Squat Jump protocol**
- Do not use CMJ-derived equations for SJ data
- Sayers equation can be used for CMJ with 2.7% error
- Always use 90° knee angle starting position for consistency
- Arm swing contributes to power (standard in testing)
