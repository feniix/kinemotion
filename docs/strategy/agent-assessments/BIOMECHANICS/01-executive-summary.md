# Biomechanics Specialist Executive Summary

**Roadmap Status:** APPROVE WITH MODIFICATIONS
**Date:** November 17, 2025

______________________________________________________________________

## Quick Verdict

| Task                  | Status           | Risk   | Notes                                       |
| --------------------- | ---------------- | ------ | ------------------------------------------- |
| **Task 1: Ankle Fix** | APPROVE          | MEDIUM | Correct fix but needs visibility validation |
| **Task 2: CMJ Tests** | APPROVE          | LOW    | Straightforward expansion to 80%+ coverage  |
| **Task 3: Real-Time** | APPROVE          | LOW    | No biomechanics blocker                     |
| **Task 4: Running**   | APPROVE + MODIFY | HIGH   | Prototype first; defer stride length        |
| **Task 5: API Docs**  | APPROVE          | LOW    | Add accuracy statements                     |

______________________________________________________________________

## Critical Findings

### 1. ANKLE ANGLE FIX - CORRECT BUT NEEDS VALIDATION

**What's happening:** Current system measures ankle angle from heel (static). Proposal: switch to foot_index (toes, active plantarflexion).

**Biomechanics verdict:** CORRECT - foot_index is proper landmark for plantarflexion.

**Risk:** foot_index can lose visibility when toes point down during push-off.

**Action needed:** Test on 10 real CMJ videos before deployment. If visibility adequate, proceed. If not, use weighted blend of foot_index + heel.

**Timeline impact:** +1 day for visibility validation (already in roadmap estimate).

______________________________________________________________________

### 2. CMJ METRICS - VALIDATED

**Jump height:** Biomechanically valid, ±2-3cm accuracy (acceptable for coaching)

**Countermovement depth:** Valid ICC 0.60-0.92 per research; useful for form feedback

**Triple Extension (after fix):**

- Hip & Knee: Already validated ✓
- Ankle: Pending fix validation

**Action:** Task 2 (testing expansion) will catch any issues. Coverage target 80%+ is achievable.

______________________________________________________________________

### 3. RUNNING METRICS - FEASIBLE WITH CAVEATS

| Metric              | Feasibility | Accuracy | Caveats                                 |
| ------------------- | ----------- | -------- | --------------------------------------- |
| **GCT**             | Yes         | ±30-50ms | Good for form feedback; not elite-grade |
| **Cadence**         | Yes         | ±1-2%    | Straightforward                         |
| **Stride Length**   | DEFER       | ±10-20%  | Needs calibration; recommend Phase 2    |
| **Landing Pattern** | Yes         | 80-90%   | Train classifier; good coaching value   |

**Critical issue:** No published study validates running GCT from video using MediaPipe (only force plate/IMU validation exists).

**Recommendation:** Prototype GCT detection on real videos first (1 week) before full Task 4 sprint. This de-risks the timeline.

______________________________________________________________________

### 4. VALIDATION STUDY - CRITICAL BUT MISSING

**What's needed:** Compare Kinemotion metrics against gold-standard (force plate or marker system) to prove accuracy.

**Why needed:** Coaches/medical professionals demand proof. Competitors cite validation studies. Partnership agreements require accuracy claims.

**Current roadmap:** No validation study planned.

**Recommendation:** Schedule for Month 3-4 (after MVP features). Plan now, execute later.

**Expected outcome:** Publish technical report showing CMJ metrics ±2-3cm accurate, running GCT ±30-50ms accurate.

______________________________________________________________________

## Biomechanical Risks (Ranked by Severity)

### Risk 1: Running GCT Accuracy Insufficient (HIGH)

- **Probability:** 40%
- **Impact:** Market positioning, elite athlete appeal
- **Mitigation:** Start with recreational runner scope; prototype first
- **Timeline:** +1 week for prototype validation

### Risk 2: Stride Length Not Feasible (HIGH)

- **Probability:** 60%
- **Impact:** Running feature completeness
- **Mitigation:** Defer to Phase 2; use normalized metrics initially
- **Timeline:** No delay if deferred; +1-2 weeks if attempted now

### Risk 3: Foot_Index Visibility Loss (MEDIUM)

- **Probability:** 30%
- **Impact:** Ankle angle accuracy after fix
- **Mitigation:** Implement fallback to heel; test on real videos
- **Timeline:** +1 day investigation

### Risk 4: Ground Contact Detection Fails (MEDIUM)

- **Probability:** 35%
- **Impact:** Running GCT reliability
- **Mitigation:** Prototype on various surfaces/lighting
- **Timeline:** +1-2 weeks if robustness issues found

______________________________________________________________________

## Key Recommendations

### IMMEDIATE (This Week)

1. **Approve Task 1 with investigation:**

   - 2-hour review: Why was heel originally chosen?
   - Once confirmed: proceed with foot_index fix
   - Add fallback strategy to spec

1. **Approve Task 2 (CMJ testing):**

   - Standard expansion; no biomechanics concerns
   - Ensure ankle angle progression test included

### NEAR-TERM (Weeks 2-3)

1. **Prototype Task 4 before full sprint:**

   - Run GCT detection on 5-10 real running videos
   - Document accuracy achieved
   - Decide: proceed full Task 4 or adjust scope
   - Timeline: 1 week parallel with other work

1. **Document physiological bounds:**

   - All metrics should have warning thresholds
   - Publish in API documentation
   - Prevents "garbage in, garbage out"

### STRATEGIC (Month 3-4)

1. **Plan validation study:**
   - Budget: ~$5-10K lab time
   - Timeline: 3-4 weeks conduct, 1-2 weeks write
   - Outcome: Technical report for partnerships
   - Not blocking MVP but critical for market credibility

______________________________________________________________________

## Accuracy Statements (For Marketing/API)

### CMJ Analysis

**Currently Deployable:**

> "Kinemotion provides video-based CMJ analysis with ±2-3cm accuracy for jump height and ±20-30ms accuracy for flight time, comparable to consumer fitness wearables. Best performance with 60fps+ video, lateral view, good lighting."

**After Ankle Fix + Validation:**

> "Triple extension analysis with ±5-10° accuracy for hip and knee angles, ±8-12° for ankle plantarflexion. Validated against force plate analysis."

### Running Analysis

**Cautious (Recommended):**

> "Running metrics including ground contact time (±30-50ms), cadence (±2%), and landing pattern classification (80% accuracy). Suitable for form feedback and injury prevention guidance."

**Avoid (Too Strong):**

> "Laboratory-grade running biomechanics" (not validated)
> "99% accurate metrics" (impossible)

______________________________________________________________________

## Modified 6-Month Timeline

```
SPRINT 0 (Week 1)
├─ Task 1: Ankle fix (2-3 days + 2-hour investigation)
└─ Task 2: CMJ tests (start)

SPRINT 1 (Weeks 2-3)
├─ Task 2: CMJ tests (complete)
├─ Task 3: Real-time (start)
└─ Task 5: API docs (start)

SPRINT 2 (Weeks 4-5) - MODIFIED
├─ Task 3: Real-time (continue)
├─ Task 4: Running PROTOTYPE (1 week validation)
│  └─ Test GCT on real videos
│  └─ Defer stride length to Phase 2
└─ Task 5: API docs (continue)

SPRINT 3 (Weeks 6-7)
├─ Task 3: Real-time (complete)
├─ Task 4: Running (complete, modified scope)
└─ Task 5: API (complete)

MONTH 4+ (Optional, Critical for Credibility)
└─ VALIDATION STUDY: CMJ/Running accuracy vs gold-standard

OUTCOME: 3-sport platform, real-time capable, APIs ready
         With documented accuracy and physiological validation
```

______________________________________________________________________

## Decision Points Required

### Decision 1: Ankle Angle Investigation

- **Question:** Why was heel originally chosen?
- **Timeline:** 2 hours
- **Outcome:** Confirm fix is correct direction OR investigate alternative

### Decision 2: Running Scope

- **Question:** Accept ±30-50ms GCT accuracy or delay for better algorithm?
- **Timeline:** Prototype result (1 week)
- **Outcome:** Proceed full task or defer stride length + add algorithmic work

### Decision 3: Validation Study

- **Question:** Budget for Month 3-4 accuracy validation study?
- **Timeline:** Decide now, execute Month 3-4
- **Outcome:** Technical report for partnership credibility

### Decision 4: Stride Length

- **Question:** Include stride length measurement in Task 4?
- **Timeline:** Decide before Task 4 starts (Week 5)
- **Options:**
  - A: Defer to Phase 2 (recommended, no timeline impact)
  - B: Include normalized stride (1 extra week)
  - C: Include calibrated stride (2-3 extra weeks)

______________________________________________________________________

## Research Basis

**Studies Reviewed (2024-2025):**

- Barzyk et al. (2024): MediaPipe CMJ validation, r > 0.85 hip/knee
- Aleksic et al. (2024): MMPose CMJ temporal accuracy, r > 0.90
- Diamond et al. (2024): OpenCap ankle angles ICC 0.60-0.93
- Weber et al. (2024): Running GCT validation via IMU
- OpenCapBench (2025): Pose estimation keypoint sparsity warning

**Key Finding:** MediaPipe can measure CMJ accurately but running GCT is harder (no published video-based validation exists).

______________________________________________________________________

## Bottom Line

**PROCEED with modifications:**

1. Ankle fix is correct; prototype validation first
1. CMJ testing expansion is low-risk
1. Running metrics feasible but less accurate than jump metrics
1. Recommend prototype validation for running (1 week, low risk)
1. Plan validation study for Month 3-4 (credibility)
1. Defer stride length to Phase 2 (reduces scope complexity)

**Expected 6-month state:** Multi-sport platform with documented accuracy, ready for partnership conversations backed by validation study.

______________________________________________________________________

**Prepared by:** Biomechanics Specialist
**For:** Technical Leadership Review
**Full Analysis:** See BIOMECHANICS_ASSESSMENT.md
