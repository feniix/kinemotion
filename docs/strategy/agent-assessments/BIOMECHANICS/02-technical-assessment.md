# Expert Biomechanics Assessment: Kinemotion Strategic Roadmap

**Date:** November 17, 2025
**Prepared by:** Biomechanics Specialist
**Status:** Comprehensive Analysis for Technical Leadership

______________________________________________________________________

## Executive Summary

The Kinemotion strategic roadmap is **technically sound for CMJ metrics** but faces **significant biomechanics risks for running implementation** and requires a **validation study before market credibility claims**. The documented ankle angle issue is correctly identified but requires careful implementation validation. Running metrics have known research gaps that may impact timeline.

**Key Findings:**

- CMJ metrics (jump height, countermovement depth): Biomechanically valid, supported by 2024 research
- Ankle angle fix (heel → foot_index): Directionally correct but requires visibility validation
- Running GCT measurement: Feasible but harder than jump analysis; no published MediaPipe validation exists
- Critical gap: No gold-standard validation study yet (needed for coaching/medical credibility)

**Recommendation:** Proceed with Tasks 1-3 as planned, but allocate 2-3 weeks for running algorithm validation (Task 4) before committing to timeline.

______________________________________________________________________

## Section 1: Ankle Angle Issue Assessment

### 1.1 Problem Identification - CORRECT

**Current State:** Using heel landmark (MediaPipe #29) for ankle angle measurement
**Proposed Fix:** Switch to foot_index landmark (MediaPipe #32)

**Biomechanical Justification:**

| Aspect                       | Heel Landmark                                                  | Foot_Index Landmark                                       | Winner     |
| ---------------------------- | -------------------------------------------------------------- | --------------------------------------------------------- | ---------- |
| **Plantarflexion Movement**  | Static during takeoff (heel lifting off)                       | Active (toes extend/plantarflex)                          | foot_index |
| **Defines Ankle Angle**      | Distance from ankle to heel (measures ankle height, not angle) | Distance from ankle to toes (measures plantarflexion ROM) | foot_index |
| **Physiological Accuracy**   | Misses plantarflexion impulse                                  | Captures full push-off motion                             | foot_index |
| **Expected CMJ Progression** | 80° → 85° (insufficient change)                                | 80° → 130°+ (realistic progression)                       | foot_index |

**Research Support:**

- Barzyk et al. (2024): Validated MediaPipe CMJ joint angles using proper landmarks achieved r=0.85+ vs marker-based systems
- Diamond et al. (2024): OpenCap (similar markerless approach) achieved ankle angle ICC 0.60-0.93, confirming MediaPipe-class systems can measure ankle angles if proper landmarks used
- Plantarflexion biomechanics: Toes (foot_index) move during plantarflexion; heel is relatively static during push-off phase

**Verdict:** CORRECT FIX - foot_index is biomechanically proper landmark for plantarflexion measurement.

### 1.2 Implementation Risk - MEDIUM

**Potential Issue: Foot_Index Visibility**

During plantarflexion in CMJ takeoff, toes point downward (away from camera). This can cause:

- MediaPipe visibility confidence dropping below threshold
- NaN/null values in landmark output
- Higher noise in ankle angle calculations

**Severity:** MEDIUM

- Jump phase is brief (~300ms), so missing frames are localized
- Heel is backup that could be used when foot_index confidence \< threshold
- Smoothing filters can fill small gaps

**Validation Required Before Deployment:**

1. Test on 5-10 real CMJ videos with current code
1. Compare foot_index vs heel visibility confidence during concentric phase
1. Measure ankle angle range with both landmarks
1. Verify: 30°+ increase during concentric (current likely shows 5-10°)

**Fix Approach:**

```
1. Primary: Use foot_index (ankle-to-toes angle)
2. Fallback: Use heel if foot_index visibility < 0.5
3. Smooth: Apply Savitzky-Golay filter (5-frame window)
4. Validate: Ankle angle 80° minimum, 130° maximum during takeoff
```

**Effort Estimate:** 2-3 days (including validation)

______________________________________________________________________

## Section 2: CMJ Metrics Validation

### 2.1 Jump Height - VALIDATED

**Metric Definition:** Maximum vertical distance center-of-mass reaches above standing position

**Calculation:** h = 0.5 *g* (t/2)² where t = flight time (seconds)

- Assumes symmetric flight parabola (takeoff velocity = landing velocity)
- Typical range: 20-80cm (recreational-elite)
- Elite athletes: 50-80cm

**Research Validation:**

- **Gold Standard:** Force plate analysis (Aleksic et al. 2024)
- **MediaPipe Accuracy:** r > 0.90 with force plate data
- **Error Range:** ±2-3cm typical for markerless systems (acceptable for coaching)
- **Key Dependency:** Takeoff/landing detection accuracy

**Critical Parameter: Flight Time Detection**

- Must identify exact frame of takeoff (when foot leaves ground)
- Must identify exact frame of landing (when foot returns)
- Current implementation: Uses backward search from peak hip height
- Accuracy: Video frame rate dependent (±33ms at 30fps = ±2cm height error)

**Verdict:** VALID and ACCURATE for coaching feedback

- Jump height ±2-3cm is acceptable for athlete trending
- Not precise enough for laboratory research but adequate for field assessment
- Must maintain >50% test coverage on flight time detection

### 2.2 Countermovement Depth - RESEARCH SUPPORTED

**Metric Definition:** Vertical displacement from standing to lowest hip position during eccentric phase

**Measurement Approach:**

- Standing hip height: Recorded at start of movement
- Lowest hip height: During deepest squat position
- Depth = Standing height - Lowest height

**Research Validation:**

- **OpenCap System:** ICC 0.60-0.92 for countermovement depth (Diamond et al. 2024)
- **Variability:** Depends heavily on hip tracking stability
- **Typical Range:** 30-60cm (varies by athlete anthropometry)

**Accuracy Considerations:**

- ICC 0.60-0.92 means moderate-to-good reliability
- Lower end (0.60) when movement is fast/jerky
- Higher end (0.92) when athlete moves smoothly
- Hip visibility can be compromised if athlete bends forward

**Physiological Bounds:**

- Minimum: 15cm (very shallow countermovement)
- Maximum: 100cm (would be unrealistic for most athletes)
- Flag for review: Depth > 80cm (possible camera/tracking error)
- Expected range: 30-60cm for most trained athletes

**Verdict:** VALID but with caveats

- Useful for athlete trending
- Not appropriate for comparing athletes (anthropometry-dependent)
- Requires human review of extreme values

### 2.3 Triple Extension - PARTIALLY VALIDATED

**Metric Definition:** Simultaneous extension of hip, knee, and ankle joints during takeoff

**Component Analysis:**

#### Hip Extension

- Normal range: 180° (full extension from ~90-120° flexion)
- MediaPipe accuracy: r > 0.85 (Barzyk 2024)
- Biomechanical validity: High
- Status: VALIDATED

#### Knee Extension

- Normal range: 180° (full extension from ~90-110° flexion)
- MediaPipe accuracy: r > 0.85 (Barzyk 2024)
- Biomechanical validity: High
- Status: VALIDATED

#### Ankle Plantarflexion

- Normal range: 80° → 130°+ (dorsiflexed → plantarflexed)
- MediaPipe accuracy: NOT YET VALIDATED with foot_index
- Current implementation uses heel: Likely shows only 80° → 90°
- After fix: Should show full 50°+ range
- Status: AWAITING VALIDATION (see Section 1.2)

**Triple Extension Timing:**

- All three joints should extend nearly simultaneously
- Peak velocity: ~100-150ms before takeoff
- Duration: ~200-300ms total (eccentric + concentric)

**Physiological Bounds (Elite Athletes):**

```
Hip angle at takeoff:     175-180°
Knee angle at takeoff:    175-180°
Ankle angle at takeoff:   120-130°

Poor form would show:
Hip angle < 160° OR
Knee angle < 160° OR
Ankle angle < 100° (or > 140°)
```

**Verdict:** HIP and KNEE validated; ANKLE requires fix

- Ankle fix is critical for credible "triple extension" analysis
- Once fixed, entire metric becomes valuable for coaching feedback on technique

### 2.4 CMJ Test Coverage - ROADMAP TARGET ACHIEVABLE

Current: 62% CMJ module coverage
Roadmap Target: 80%+

**Gap Analysis:**

- Current tests: Basic metric calculation
- Missing: Phase progression validation (0% coverage)
- Missing: Physiological bounds validation (0% coverage)
- Missing: Real video sample validation (0% coverage)

**Recommended Test Additions:**

```
1. Phase Progression Tests (10% coverage gain)
   - Eccentric phase: Angles decrease, velocity increases downward
   - Inflection point: Velocity crosses zero
   - Concentric phase: Angles increase, velocity increases upward

2. Physiological Bounds Tests (8% coverage gain)
   - Flag RSI > 4.0 (impossible)
   - Flag jump height > 150cm (unlikely)
   - Flag GCT < 50ms (unrealistic)
   - Flag countermovement depth > 80cm (review needed)

3. Real Video Validation Tests (5% coverage gain)
   - Process 3-5 curated CMJ videos
   - Validate metrics fall within expected ranges
   - Compare output between frames for continuity
```

**Effort:** 3-4 days (Task 2 in roadmap)

______________________________________________________________________

## Section 3: Running Metrics - FEASIBILITY & ACCURACY

### 3.1 Ground Contact Time (GCT) - CHALLENGING

**Metric Definition:** Duration foot is in contact with ground during running step

**Measurement Principle:**

- Detect foot contact with ground
- Measure duration from contact to liftoff
- Typical range: Elite runners 0.15-0.25s, recreational 0.25-0.35s

**Research Validation:**

- **Weber et al. (2024):** GCT measurement validated using IMU sensors (r > 0.95 vs force plate)
- **Challenge:** No published studies validate GCT from VIDEO using MediaPipe
- **Reason:** Detecting subtle foot contact from 2D video is harder than detecting jump landing

**Technical Difficulty: MEDIUM-HIGH**

Why running GCT is harder than jump GCT:

1. Jump has clear acceleration spike (impact on ground)
1. Running has subtle, repetitive ground contacts
1. Horizontal velocity is dominant (harder to detect from side view)
1. Foot may not be clearly visible if ground plane has similar color/texture

**Approaches for Detection:**

| Approach                              | Accuracy | Complexity | Notes                                                  |
| ------------------------------------- | -------- | ---------- | ------------------------------------------------------ |
| **Vertical velocity zero-crossing**   | ±30-50ms | Medium     | Foot contact when vertical velocity crosses zero       |
| **Foot landmark proximity to ground** | ±20-40ms | High       | Requires camera calibration & depth estimation         |
| **ML contact classifier**             | ±10-20ms | Very High  | Train model on force plate data; not yet in Kinemotion |
| **Foot acceleration (IMU hybrid)**    | ±5-10ms  | Medium     | If wearable integration added                          |

**Expected Accuracy (Vision-Only):** ±30-50ms

- Acceptable for recreational runners (stride error ~1-2%)
- NOT acceptable for elite runners (demands ±5ms precision)
- Sufficient for injury prevention feedback ("too long contact")

**Critical Requirement: Camera Setup Specification**

- Must be lateral view (sagittal plane)
- Adequate lighting to see foot-ground contact
- Known camera height for calibration
- Frame rate ≥ 60fps (30fps insufficient for GCT)

**Verdict:** FEASIBLE but with accuracy caveats

- Can achieve ±30-50ms from video alone
- Better with calibration markers or IMU integration
- Must set customer expectations correctly

### 3.2 Cadence - STRAIGHTFORWARD

**Metric Definition:** Steps per minute (frequency of ground contact)

**Measurement:** Count ground contacts over time duration

- Typical range: 160-180 steps/min (optimal)
- Elite/distance runners: 170-180
- Recreational/heavy runners: 160-170

**Technical Difficulty:** LOW

Why easy:

- Depends only on accurate step counting
- Less sensitive to absolute timing accuracy
- Frame rate ≥ 30fps sufficient

**Accuracy:** ±2-3% (frame rate dependent)

**Verdict:** VALID and STRAIGHTFORWARD

- No biomechanical concerns
- Works reliably once GCT detection works

### 3.3 Stride Length - PROBLEMATIC

**Metric Definition:** Horizontal distance traveled during one complete gait cycle (two steps)

**Measurement Challenge:** Estimating absolute horizontal distance from 2D video without depth information

**Technical Problem: SIGNIFICANT**

Single-camera video captures:

- Pixel distances (relative scale)
- NOT absolute meters (needs camera calibration or known reference object)

To measure stride length absolutely requires:

1. Camera height & distance calibration, OR
1. Multi-camera stereo setup, OR
1. Known reference object in frame, OR
1. IMU integration with step counting

**Research Gap:** No published validated stride length extraction from 2D smartphone video

**Accuracy Without Calibration:** ±10-20% error

- Acceptable for form feedback ("longer stride = more power")
- NOT acceptable for performance tracking ("my stride improved 2%")

**Recommended Approach:**

Option A (Simple): Report normalized stride length

- Example: "Stride = 1.8x your leg length"
- Requires manual anthropometry input
- No camera calibration needed
- Useful for form feedback

Option B (Medium): Request calibration markers

- Place reference object (e.g., 1m stick) in frame
- System auto-calibrates
- Then stride length accurate to ±3-5%

Option C (Advanced): Integrate IMU accelerometer

- Use step counting from accelerometer (accurate to ±1-2%)
- Use video for form analysis
- Combine for best accuracy

**Verdict:** STRIDE LENGTH MEASUREMENT NOT RECOMMENDED (yet)

- Option A (normalized) safe for release
- Option B (calibration) viable if implemented carefully
- Option C requires additional hardware integration

### 3.4 Landing Pattern Classification - VIABLE

**Metric Definition:** Heel, midfoot, or forefoot strike classification

**Classification Task:** Binary/Ternary classification on foot strike type

**Technical Approach:**

- Extract foot region image during ground contact
- Classify which part of foot hits first
- No absolute distance needed (only image classification)

**Accuracy:** 80-90% possible with trained model

**Biomechanical Significance:**

- Heel strike: More impact shock, common in recreational runners
- Midfoot strike: Balanced, efficient
- Forefoot strike: Sprint/elite runners, higher calf load

**Requirements:**

- Labeled training data (20-50 samples each class)
- Can create from existing running video samples
- Moderate development effort (~1 week)

**Verdict:** VIABLE

- Good coaching feedback value
- Reasonable accuracy achievable
- Should be included in running module

### 3.5 Running Metrics Summary

**Go/No-Go Decision:**

| Metric              | Status               | Timeline Impact                             | Notes                          |
| ------------------- | -------------------- | ------------------------------------------- | ------------------------------ |
| **GCT**             | PROCEED with caveats | No delay if ±30-50ms acceptable             | Requires camera setup spec     |
| **Cadence**         | PROCEED              | No delay                                    | Straightforward once GCT works |
| **Stride Length**   | CONDITIONAL          | +1-2 weeks for calibration or normalization | Requires design decision first |
| **Landing Pattern** | PROCEED              | +1 week for model training                  | Good coaching value            |

**Recommendation:**

- Task 4 estimate: 2-3 weeks (reasonable)
- RISK: May be 3-4 weeks if stride length requires calibration implementation
- Suggest starting with GCT + Cadence + Landing Pattern (omit stride initially)
- Add stride length as Phase 2 after running release

______________________________________________________________________

## Section 4: Physiological Bounds & Validation

### 4.1 Critical Bounds for Quality Assurance

These bounds should trigger automatic warnings or manual review:

**Drop Jump Metrics:**

```
Ground Contact Time:
  - Warning if < 100ms (unrealistic, check foot detection)
  - Warning if > 500ms (not reactive, check for detection error)
  - Alert if > 1000ms (definitely wrong)

Flight Time:
  - Warning if < 200ms (unrealistic jump)
  - Warning if > 800ms (unrealistic for humans)

RSI (Reactive Strength Index):
  - Warning if < 0.1 (poor reactivity)
  - Warning if > 4.0 (impossible, check for error)
  - Expected range: 0.5-3.5
```

**CMJ Metrics:**

```
Jump Height:
  - Warning if < 10cm (very poor)
  - Warning if > 150cm (check for error)
  - Alert if > 200cm (definitely wrong)

Countermovement Depth:
  - Warning if < 15cm (very shallow)
  - Warning if > 80cm (check for error)
  - Expected range: 30-60cm

Triple Extension Angles (at takeoff):
  - Hip angle: 160-180° (flag if < 150° or > 190°)
  - Knee angle: 160-180° (flag if < 150° or > 190°)
  - Ankle angle: 110-135° (flag if < 100° or > 145°)

Angle Progression (concentric phase):
  - Hip: Must increase ≥ 20°
  - Knee: Must increase ≥ 20°
  - Ankle: Must increase ≥ 30° (after fix)
  - Alert if any joint < 15° increase
```

**Running Metrics:**

```
Ground Contact Time:
  - Warning if < 0.10s (unrealistic elite)
  - Warning if > 0.60s (check detection)
  - Expected: 0.15-0.40s

Cadence:
  - Warning if < 120 steps/min (too slow)
  - Warning if > 220 steps/min (unrealistic)
  - Expected: 160-180 steps/min

Landing Pattern Confidence:
  - Warning if < 70% confidence (ambiguous strike)
  - Should require human review
```

### 4.2 Implementation Strategy

**In Code:**

```python
# Example structure
class PhysiologicalBounds:
    cmj_ankle_angle_min = 100  # degrees
    cmj_ankle_angle_max = 145
    cmj_jump_height_max = 150  # cm
    running_gct_min = 0.10  # seconds
    running_gct_max = 0.60

def validate_metrics(metrics_dict):
    warnings = []
    for metric, value in metrics_dict.items():
        if value < bounds[metric]['min']:
            warnings.append(f"{metric} below expected: {value}")
        if value > bounds[metric]['max']:
            warnings.append(f"{metric} above expected: {value}")
    return warnings

# Output example:
# "ankle_angle": 95°  → warning: "Ankle plantarflexion low (95°), check visibility"
# "jump_height": 175cm → error: "Jump height impossible, check flight time detection"
```

**Documentation Output:**

- Every metric should include: value ± confidence interval
- Example: "Jump Height: 52cm ± 3cm (95% confidence)"
- Include warning flags in JSON output

______________________________________________________________________

## Section 5: Testing Strategy for Credibility

### 5.1 Current Testing (Roadmap Task 2)

**Scope:** Phase progression, physiological bounds, real video validation
**Estimated Coverage Gain:** 62% → 80%+
**Estimated Effort:** 3-4 days

**Limitation:** Tests unit metrics in isolation; doesn't validate against gold-standard

### 5.2 CRITICAL GAP: Validation Study Not in Roadmap

**Why Needed:**

- Coaches/medical professionals demand accuracy proof
- Competitors (Motion-IQ, Dartfish) cite validation studies
- Licensing/partnership agreements require accuracy claims
- Liability protection for coaching recommendations

**Recommended Study:**
**Title:** "Validation of Video-Based Kinematic Analysis Using MediaPipe: CMJ and Running Gait"

**Scope:**

- 15-25 participants
- Record simultaneously with:
  - 2x MediaPipe (Kinemotion lateral views)
  - Force plate (CMJ landing GRF)
  - Marker-based motion capture (optional but preferred)
- Analyze: CMJ flight time, GCT, ankle angles; Running GCT, cadence

**Analysis:**

- Bland-Altman plots (agreement analysis)
- Intraclass correlation (ICC) for each metric
- Root-mean-square error (RMSE)
- Publish findings as technical report

**Effort & Cost:**

- Research effort: 3-4 weeks (data collection + analysis)
- Lab cost: ~$5-10K (if academic partnership)
- Could be conducted as thesis/capstone project
- Timeline: Best completed BEFORE major marketing push

**Publication Venue:**

- Conference: ACSM (American College of Sports Medicine)
- Journal: Journal of Sports Sciences (2-3 month review)
- Minimum: Internal technical report (1-2 weeks to write)

**Expected Outcome:**

- CMJ metrics: ±2-3cm (jump height), ±20-30ms (flight time)
- Running GCT: ±30-50ms (current limitation)
- Ankle angles: ±5-10° (after foot_index fix)
- Report credibility for partnerships

### 5.3 Phase Progression Testing

**What to Validate:**

**CMJ Phase Progression:**

```
Standing Phase:
- Hip angle: 180° (full extension)
- Knee angle: 180° (full extension)
- Ankle angle: ~110° (neutral)
- Hip velocity: 0
- Knee velocity: 0

Eccentric Phase (countermovement down):
- Hip angle: decreases 180° → 90-100°
- Knee angle: decreases 180° → 90-100°
- Ankle angle: decreases 110° → 80-90° (dorsiflexion)
- Hip velocity: negative (downward)
- Knee velocity: negative (downward)

Inflection Point:
- Vertical velocity crosses zero
- Joint velocities at maximum magnitude (downward)

Concentric Phase (push-up):
- Hip angle: increases 90-100° → 170-180°
- Knee angle: increases 90-100° → 170-180°
- Ankle angle: increases 80-90° → 120-130°
- Hip velocity: positive (upward, increasing)
- Knee velocity: positive (upward, increasing)

Flight Phase:
- All joints extended
- Hip/knee/ankle angles constant at ~180°/~180°/~130°
- Vertical velocity decreases (due to gravity)

Landing Phase:
- Reverse of eccentric (angles decrease again)
```

**Test Implementation:**

```python
def test_cmj_phase_progression():
    # Parse a real CMJ video
    phases = detect_cmj_phases(video)

    # Eccentric phase validation
    assert phases['eccentric']['hip_angle_start'] > 160
    assert phases['eccentric']['hip_angle_end'] < 110
    assert phases['eccentric']['hip_angle_change'] > 50

    # Concentric phase validation
    assert phases['concentric']['hip_angle_start'] < 110
    assert phases['concentric']['hip_angle_end'] > 160
    assert phases['concentric']['ankle_angle_change'] > 30  # KEY: Ankle must change ±30°

    # Takeoff validation
    assert phases['takeoff']['hip_angle'] > 160
    assert phases['takeoff']['knee_angle'] > 160
    assert phases['takeoff']['ankle_angle'] > 110
```

### 5.4 Real Video Sample Library

**Recommended Curation:**

- 5-10 CMJ videos: Various skill levels
- 5-10 Running videos: Different cadences/form
- Metadata: Athlete info, ground truth metrics if available

**Documentation:**

- Expected metric ranges for each sample
- Video quality indicators (lighting, camera stability, athlete position)
- Known limitations (e.g., "ankle angle partially occluded, 0.7 visibility")

**Use Case:**

- Regression testing (ensure algorithm changes don't break these)
- Performance benchmarking
- Coach training ("here's what good form looks like")

______________________________________________________________________

## Section 6: Biomechanics-Specific Risks to Roadmap

### 6.1 Task 1 (Ankle Angle Fix) - Risk Level: MEDIUM

**Risk Factors:**

1. **Foot_Index Visibility Loss** (Probability: 30%, Impact: High)

   - During aggressive plantarflexion, foot_index may drop out of frame
   - Results in NaN values or high noise
   - Mitigation: Implement fallback to heel + smoothing filter
   - Detection: Run on 10 test videos before deployment

1. **Heel Was Intentional** (Probability: 10%, Impact: Critical)

   - Original designers may have chosen heel for specific reason
   - Fix could be wrong direction
   - Mitigation: Review original design rationale first
   - Timeline impact: +1 day investigation

1. **Validation Failure** (Probability: 15%, Impact: Medium)

   - After fix, ankle angles may still not increase 30°+
   - Could indicate MediaPipe accuracy limit for ankle
   - Mitigation: Prepare to accept 20-25° range if 30° not achievable
   - Risk: Diminishes "triple extension" credibility

**Contingency Plan:**

- If foot_index visibility \< 70%: Use weighted blend of foot_index + heel
- If ankle angle increase \< 20°: Document limitation, adjust bounds
- If >50% confidence values low: Label as "requires high-quality video"

### 6.2 Task 4 (Running Metrics) - Risk Level: HIGH

**Risk Factors:**

1. **GCT Accuracy Insufficient** (Probability: 40%, Impact: High)

   - Current approach may yield ±50ms error
   - Elite runners need ±10ms precision
   - Market expectation: "accurate as wearables"
   - Mitigation: Start with recreational runner scope only
   - Timeline impact: +2 weeks for algorithm optimization

1. **Ground Plane Detection Failure** (Probability: 35%, Impact: High)

   - Detecting foot contact from 2D requires ground plane knowledge
   - May fail with variable lighting, ground surfaces
   - Mitigation: Restrict to controlled environments initially
   - Timeline impact: +1-2 weeks for robust detection

1. **Stride Length Accuracy Unacceptable** (Probability: 60%, Impact: Medium)

   - Without calibration, stride error 10-20%
   - Affects credibility of running metrics
   - Mitigation: Publish stride as "relative to body" not absolute distance
   - Timeline impact: +1 week for design decision

1. **MediaPipe Pose Drops During Running** (Probability: 25%, Impact: Medium)

   - Fast limb motion can cause detection gaps
   - Affects phase continuity
   - Mitigation: Early prototype testing on running videos
   - Timeline impact: +1 week if robustness issues found

**Risk Severity Summary:**

- 40% chance running GCT accuracy is 2-3x worse than claimed
- 60% chance stride length unacceptable without calibration
- Recommend: De-risk with 1-2 week prototype before full sprint commitment

### 6.3 OpenCapBench Critical Finding (2025)

**Recent Publication:** "OpenCapBench: A Benchmark to Bridge Pose Estimation and Biomechanics"

**Key Finding:** Current pose estimation models use keypoints that are TOO SPARSE for accurate biomechanics

**Implications for Kinemotion:**

- MediaPipe has 33 keypoints (reasonable but limited)
- Accuracy for joint angles: ±5-10° typical
- OpenCapBench shows 2x error reduction with denser keypoints
- Recommendation: Not actionable now, but indicates accuracy ceiling

**Mitigation:**

- Document known accuracy limits: ±5-10° for joint angles
- Don't claim "laboratory-grade" accuracy
- Position as "coaching feedback" not "research grade"

______________________________________________________________________

## Section 7: Recommendations

### 7.1 Task-Specific Biomechanics Guidance

**TASK 1: Ankle Angle Fix**

```
APPROVAL: Proceed as planned
CRITICAL PATH:
  1. Review original design rationale (investigate why heel chosen) - 2 hours
  2. Test foot_index visibility on 10 CMJ videos - 2 hours
  3. Implement fallback strategy (heel if visibility < 0.5) - 4 hours
  4. Validate ankle angle increases 30°+ in concentric phase - 2 hours
  5. Update tests to verify 30°+ increase - 2 hours
EXPECTED OUTCOME: Ankle angles 80° → 130°, triple extension credible
RISK MITIGATION: Accept 25° minimum if 30° unrealistic
```

**TASK 2: CMJ Testing Expansion**

```
APPROVAL: Proceed as planned
RECOMMENDED TESTS TO ADD:
  1. Phase progression: Eccentric/inflection/concentric angle progressions
  2. Physiological bounds: Validate all metrics in expected ranges
  3. Real video: Process 5 curated CMJ videos, validate outputs
COVERAGE TARGET: 80%+
TIMELINE: 3-4 days
CRITICAL: Include ankle angle progression test (after Task 1 fix)
```

**TASK 3: Real-Time Web Analysis**

```
APPROVAL: Proceed as planned (no biomechanics blocker)
BIOMECHANICS CONSIDERATION:
  - Latency <200ms is achievable (not biomechanics concern)
  - Use same phase detection algorithms as batch mode
  - Must validate metrics accuracy same as offline (no latency penalty)
TIMELINE: 3-4 weeks (no changes needed)
```

**TASK 4: Running Gait Analysis**

```
APPROVAL: PROCEED WITH MODIFICATIONS
MODIFIED SCOPE:
  1. GCT: Proceed with ±30-50ms accuracy disclaimer
  2. Cadence: Proceed (straightforward)
  3. Stride Length: DEFER (add to Phase 2)
  4. Landing Pattern: Proceed (good feedback value)
CRITICAL WORK:
  - Week 1: Prototype GCT detection on 5-10 running videos
  - Week 1: Document GCT accuracy limits before commitment
  - Week 2-3: Implement landing pattern classifier
  - Week 2-3: Implement cadence counter
TIMELINE: 2-3 weeks (feasible with scope modification)
RISK REDUCTION: Test on real videos first before full sprint
RECOMMENDATION: Start immediately with prototype validation
```

**TASK 5: API Documentation**

```
APPROVAL: Proceed as planned (no biomechanics impact)
INCLUDE IN DOCS:
  - Accuracy statements for each metric (±cm, ±ms, ±degrees)
  - Known limitations (e.g., "ankle angle requires high-quality video")
  - Physiological bounds and warning thresholds
  - Interpretation guide for coaches
```

### 7.2 Credibility & Market Positioning

**DO IMMEDIATELY:**

1. Start validation study planning (even if low priority for now)
1. Document accuracy limits in API (±2-3cm jump height, ±5-10° angles)
1. Add physiological bounds validation to all metrics
1. Prepare "accuracy statement" document for partnerships

**DO BEFORE MAJOR MARKETING:**

1. Complete validation study (vs force plate or marker system)
1. Publish results as technical report/white paper
1. Partner with 2-3 biomechanics researchers for credibility
1. Include accuracy statements in all marketing claims

**EXAMPLE ACCURATE MARKETING CLAIM:**

> "Kinemotion provides video-based CMJ analysis with ±2-3cm accuracy for jump height, comparable to consumer wearables. Validated against force plate analysis. Suitable for coaching feedback and performance trending."

**EXAMPLE INACCURATE CLAIM (AVOID):**

> "Laboratory-grade biomechanics analysis" (too strong, not validated)
> "99% accurate ankle angle measurement" (impossible, not validated)

### 7.3 Key Decision Points for Technical Leadership

**Decision 1: Ankle Angle - Proceed or Investigate?**

- **Recommendation: INVESTIGATE FIRST** (2 hours)
- Reason: Need to confirm original design intent
- Risk: Fix could be wrong direction
- Decision point: After investigation, approve fix

**Decision 2: Running GCT - Accept ±30-50ms or Delay?**

- **Recommendation: ACCEPT WITH DISCLAIMER**
- Reason: Good enough for injury prevention feedback
- Timeline: Allows Task 4 to complete on schedule
- Decision point: Set customer expectation correctly

**Decision 3: Validation Study - Priority?**

- **Recommendation: SCHEDULE FOR MONTH 3-4**
- Reason: Essential for partnerships, but not blocking MVP
- Timeline: Can be conducted during mobile app development
- Decision point: Budget and partner identification needed

**Decision 4: Stride Length - Include or Defer?**

- **Recommendation: DEFER TO PHASE 2**
- Reason: Requires calibration or normalization; adds complexity
- Timeline: Can be added in Month 4-6 when running validated
- Decision point: Clear scope before Task 4 starts

______________________________________________________________________

## Section 8: Summary Matrix

| Aspect                              | Status          | Confidence | Risk   | Action                            |
| ----------------------------------- | --------------- | ---------- | ------ | --------------------------------- |
| **CMJ Jump Height**                 | Valid           | High       | Low    | Proceed, document ±2-3cm          |
| **CMJ Flight Time**                 | Valid           | High       | Low    | Ensure robust phase detection     |
| **CMJ Countermovement Depth**       | Valid           | Medium     | Medium | Document anthropometry dependency |
| **CMJ Triple Extension (Hip/Knee)** | Valid           | High       | Low    | Proceed as planned                |
| **CMJ Ankle Angle (Current)**       | Invalid         | High       | High   | MUST FIX before marketing         |
| **CMJ Ankle Angle (After Fix)**     | Valid (pending) | Medium     | Medium | Validate foot_index visibility    |
| **Running GCT**                     | Feasible        | Medium     | Medium | Accept ±30-50ms, document limit   |
| **Running Cadence**                 | Valid           | High       | Low    | Straightforward implementation    |
| **Running Stride Length**           | Problematic     | Low        | High   | DEFER to Phase 2                  |
| **Running Landing Pattern**         | Valid           | Medium     | Low    | Proceed, train classifier         |
| **Real-Time Capability**            | Feasible        | High       | Low    | No biomechanics blocker           |
| **API Ecosystem**                   | Valid           | High       | Low    | Include accuracy statements       |
| **Overall Roadmap**                 | Achievable      | Medium     | Medium | Proceed with modifications below  |

______________________________________________________________________

## Section 9: Roadmap Modifications (Recommended)

### Current Roadmap (6-Month Plan)

- Sprint 0: Ankle fix + CMJ tests
- Sprint 1: CMJ tests (complete) + Real-time (start) + API docs (start)
- Sprint 2: Real-time (continue) + Running (start) + API (continue)
- Sprint 3: Real-time (complete) + Running (complete) + API (complete)

### RECOMMENDED Modified Roadmap

**Sprint 0 (Week 1)** - UNCHANGED

- Task 1: Ankle fix (with investigation phase)
- Task 2: CMJ tests (start)

**Sprint 1 (Weeks 2-3)** - UNCHANGED

- Task 2: CMJ tests (complete)
- Task 3: Real-time (start)
- Task 5: API docs (start)

**Sprint 2 (Weeks 4-5)** - MODIFIED

- Task 3: Real-time (continue)
- **Task 4 (Modified): Running prototype validation**
  - Prototype GCT detection on 5-10 real running videos
  - Document accuracy achieved (±ms)
  - Validate ground contact detection works
  - Implement landing pattern classifier
  - Defer stride length to Phase 2
- Task 5: API docs (continue)

**Sprint 3 (Weeks 6-7)** - MODIFIED

- Task 3: Real-time (complete)
- Task 4: Running (complete, scope-modified: no stride length)
- Task 5: API (complete, includes accuracy statements)

**Sprint 4+ (Weeks 8+)** - PLANNING ADDITION

- **VALIDATION STUDY:** Conduct CMJ/Running accuracy validation
  - Month 3-4 timeline
  - Compare vs force plate / marker system
  - Publish results for partnership credibility

______________________________________________________________________

## Section 10: Conclusion

**Overall Assessment:** ROADMAP IS SOUND WITH MODIFICATIONS

**Key Strengths:**

- CMJ metrics are biomechanically valid and well-researched
- Ankle angle fix is directionally correct
- Running metrics are feasible within stated scope
- Timeline is realistic with proposed changes

**Key Concerns:**

- Ankle angle fix requires validation before deployment
- Running GCT accuracy (±30-50ms) not ideal for elite athletes
- Validation study essential for market credibility (not in current roadmap)
- Stride length should be deferred (complexity unjustified for MVP)

**Critical Success Factors:**

1. Validate ankle angle fix on real videos (2 hours)
1. Document physiological bounds for all metrics
1. Conduct running prototype validation before full sprint (1 week)
1. Plan validation study for Month 3-4
1. Include accuracy statements in all API documentation

**Expected 6-Month Outcome:**

- 3-sport platform (Drop Jump, CMJ, Running)
- Real-time web analysis capability
- Public APIs with documented accuracy limits
- CMJ metrics: ±2-3cm accuracy
- Running GCT: ±30-50ms accuracy (with caveats)
- Foundation for partnership/licensing based on validation study

**Recommendation:**
**PROCEED WITH MODIFICATIONS** - Allocate 1-2 weeks for running prototype validation and 2 hours for ankle angle investigation before committing to full Task 4 sprint.

______________________________________________________________________

**Prepared by:** Biomechanics Specialist
**Review Date:** November 17, 2025
**Next Review:** Upon completion of Task 1 (ankle fix validation)
