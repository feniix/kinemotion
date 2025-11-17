# ML/Data Science Assessment - Executive Summary

**Date:** November 17, 2025
**Status:** Ready for Review
**Overall Grade:** 7/10 (Good strategy, significant execution gaps)

______________________________________________________________________

## Key Findings at a Glance

### What's Working Well

✓ Clear 6-month roadmap with well-prioritized tasks
✓ Ankle angle fix identified as P0 credibility issue
✓ Real-time capability recognized as market differentiator
✓ Multi-sport extensibility (jump → running → other sports)
✓ Modular architecture supports new features

### Critical Gaps

✗ **Quality Presets:** One-size-fits-all for jumping; running needs sport-specific tuning (12 parameters differ)
✗ **Parameter Tuning:** Running parameters completely undefined; relies on guesswork not data
✗ **Validation Strategy:** Mentioned but not structured; no published accuracy metrics
✗ **Benchmark Datasets:** Missing entirely; credibility requires reproducible test data
✗ **Multi-Person:** Architectural gap; not even designed yet
✗ **Real-Time Latency:** Budget optimistic (166ms theoretical vs 190-300ms realistic)
✗ **Robustness Testing:** Zero specification; algorithm may fail silently in field
✗ **Ablation Studies:** Mentioned but not structured; rigor gap for credibility

______________________________________________________________________

## Critical ML/Data Science Recommendations

### Priority 1: Weeks 1-2 (4 Actions, 13-16 Days)

| Task                           | Why Now                                                | Owner             | Time     |
| ------------------------------ | ------------------------------------------------------ | ----------------- | -------- |
| Define running quality presets | Prevents wrong parameters before week 5 implementation | ML + Biomechanics | 3-4 days |
| Create validation framework    | Foundation for all downstream validation               | ML + QA           | 2 days   |
| Design benchmark dataset       | Establishes credibility, guides test strategy          | ML + QA           | 3-4 days |
| Build latency profiler tool    | Identify real-time bottlenecks immediately             | CV Engineer       | 3 days   |

**Deliverable:** Running parameter specification, validation protocol, latency baseline

### Priority 2: Weeks 3-5 (4 Actions, 38-49 Days)

| Task                            | Why Now                                      | Owner             | Time       |
| ------------------------------- | -------------------------------------------- | ----------------- | ---------- |
| Parameter optimization pipeline | Data-driven tuning, not guesswork            | ML + Backend      | 5-7 days   |
| Run robustness testing matrix   | Identify failure modes before launch         | QA + ML           | 10-15 days |
| Execute validation studies      | Ground truth comparison (jump + running)     | ML + Biomechanics | 10-15 days |
| Ablation studies (4 studies)    | Quantify parameter impacts, scientific rigor | ML + QA           | 20 days    |

**Deliverable:** Validation reports, robustness matrix, ablation study findings

### Priority 3: Optional Phase 2 (Multi-Person, Month 4+)

| Task                             | Why Later                        | Owner       | Time     |
| -------------------------------- | -------------------------------- | ----------- | -------- |
| Multi-person architecture design | Design now, implement month 4    | CV Engineer | 3-4 days |
| Multi-person implementation      | Requires latency profiling first | CV Engineer | 5-7 days |

______________________________________________________________________

## Running Gait Parameters - Specific Tuning Needed

**Critical:** These differ significantly from jump parameters

```
PARAMETER              JUMP BALANCED    RUNNING BALANCED    RATIONALE
─────────────────────────────────────────────────────────────────────
detection_confidence   0.5              0.70                Higher needed for foot tracking during swing
tracking_confidence    0.5              0.65                Harder to maintain ID during occlusion
model_complexity       1 (Full)         0 (Lite, faster)    Real-time priority for running
butterworth_cutoff     8 Hz             5 Hz (lower body)   Lower body moves slower in running
savgol_window          11 frames        9 frames            Stride cycle ~0.33s at 180 spm
velocity_threshold     0.1 m/s          0.05 m/s            Running has continuous velocity signal

→ None of these transfer directly. Running needs custom presets.
```

______________________________________________________________________

## Validation & Credibility Strategy

### Current State: Insufficient

- CMJ validated against published research, but no accuracy metrics published
- Drop Jump GCT documented, but no force plate comparison
- Running: Zero validation

### Required for Credibility

**Phase 1 (Jump):**

- GCT accuracy: MAE \<20ms (compare to force plate)
- CMJ height: MAE \<3cm (compare to viamark/video)
- Report: Bland-Altman plots, ICC >0.90, confidence intervals

**Phase 2 (Running - Before Public Launch):**

- GCT accuracy: MAE \<15ms (compare to force plate or 120fps video)
- Cadence accuracy: MAE \<3 spm
- Landing pattern: 85%+ classification accuracy
- Report: Same statistical rigor as jump validation

**Deliverable:** 4-6 page validation study paper (month 3)

______________________________________________________________________

## Benchmark Dataset Strategy

### Why It Matters

- Third-party verification of claims
- Academic credibility (publications)
- Competitive benchmarking
- Reproducible test environment

### Recommended Scope

**Jump Dataset v1.0 (Publish Immediately):**

- 40-50 videos (drop jump + CMJ)
- GitHub release with ground truth annotations
- 1-2 pages methods documentation

**Running Dataset v1.0 (Create for Roadmap Testing):**

- 45-60 videos (multiple speeds, conditions)
- Tiered quality (ideal/good/challenging)
- Ground truth: Force plate (15 videos) + manual annotation (35 videos)
- Publish on Zenodo (academic standard)

**Hosting:** GitHub (MVP, free), Zenodo (academic, permanent)

______________________________________________________________________

## Real-Time Latency - Reality Check

### Theoretical Budget: 166ms

### Actual Expectations: 190-300ms depending on scenario

| Scenario                                    | Realistic Latency | Target Met? |
| ------------------------------------------- | ----------------- | ----------- |
| Single person, Lite model, LAN, fast preset | 120-150ms         | Yes ✓       |
| Single person, Full model, WiFi, balanced   | 190-220ms         | Marginal ✓  |
| Multi-person, Full model, 4G, balanced      | 300-400ms         | No ✗        |

**Action:** Empirical profiling Week 1 of Task 3 (high priority)

**Realistic expectation:** "\<200ms on LAN with balanced preset, \<250ms on WiFi" not universal \<200ms

______________________________________________________________________

## Multi-Person Detection - Architectural Decision

### Current Status: Completely Skipped

**Market Gap:** Competitors (Motion-IQ, Dartfish) support multi-person. Kinemotion does not.

**Recommendation:** Design now (3-4 days), defer implementation to month 4

**Architecture Needed:**

- Person ID tracking (Hungarian algorithm)
- Per-person metric calculation
- Confidence threshold adjustments (0.70+ for multi-person)
- Latency scaling: 2 people = 100ms (10fps, acceptable for batch)

______________________________________________________________________

## Robustness Testing - Silent Failure Risk

### Critical Gap: Zero Robustness Specification

Algorithm may fail silently under:

- Poor lighting: Accuracy drops 2-3% per 20% brightness decrease
- Video quality: 720p vs 480p = 5% difference
- Camera angle: Beyond ±30° from lateral = 10%+ accuracy loss
- Subject variation: Overweight subjects = 15-20% accuracy loss
- Occlusion: Leg occlusion more critical than arm

**Recommendation:** Create 35-40 video test matrix covering all dimensions (2-3 weeks effort)

______________________________________________________________________

## Ablation Studies - Scientific Rigor

### Current Status: Mentioned, Not Structured

Needed for:

- Academic credibility
- Parameter optimization justification
- Regression testing
- Publication

### Recommended Studies (4 total, 5 days each)

1. **Ankle angle fix impact** (Week 2): Confirm fix improves angle, not height
1. **Savgol window optimization** (Week 2): Find best window size for jump
1. **Running confidence threshold** (Week 4): Find optimal threshold for GCT
1. **Filter strategy comparison** (Week 5): Butterworth vs Savgol vs adaptive

______________________________________________________________________

## Timeline Impact

### Current Roadmap: 6 weeks

### With ML additions (recommended): 10-12 weeks

### With full robustness: 14 weeks

**Mitigation:** Either extend timeline or reduce scope (defer multi-person + advanced ablations)

______________________________________________________________________

## Risk Assessment

| Risk                                   | Likelihood  | Impact   | Mitigation                                        |
| -------------------------------------- | ----------- | -------- | ------------------------------------------------- |
| Running parameters wrong               | MEDIUM-HIGH | CRITICAL | Validate week 4 vs ground truth                   |
| Real-time latency misses target        | MEDIUM      | HIGH     | Profile immediately, set realistic expectations   |
| Validation study shows poor accuracy   | MEDIUM-HIGH | CRITICAL | Run early (week 2-3), publish transparent results |
| Robustness issues in field             | MEDIUM-HIGH | MEDIUM   | Allocate 2-3 weeks testing, document limitations  |
| Multi-person reveals major refactoring | MEDIUM      | MEDIUM   | Design architecture first, prototype early        |

______________________________________________________________________

## One-Page Action Plan

### Week 1-2: Foundation (13-16 days)

1. Define running parameters (ML + Biomechanics) → 3-4 days
1. Create validation framework (ML + QA) → 2 days
1. Design benchmark dataset (ML + QA) → 3-4 days
1. Build latency profiler (CV Engineer) → 3 days

**Deliverable:** Parameter spec + validation protocol + latency baseline

### Week 3-5: Validation (38-49 days)

1. Run parameter sweeps (ML + Backend) → 5-7 days
1. Execute validation studies (ML + Biomechanics) → 10-15 days
1. Robustness testing (QA + ML) → 10-15 days
1. Ablation studies (ML + QA) → 20 days

**Deliverable:** Validation reports + robustness matrix + ablation findings

### Month 2+: Refinement

1. Publish validation study paper
1. Release benchmark datasets
1. Implement multi-person (if desired)
1. Launch real-time demo

______________________________________________________________________

## Success Metrics

**Month 1:**

- Running parameters validated (documented, tested)
- Drop Jump validation study in progress
- Latency profiler showing realistic performance

**Month 2:**

- All jump metrics validated (published accuracy)
- Running metrics validated (ground truth comparison)
- Robustness matrix complete (knows failure modes)

**Month 3:**

- 3-sport platform with validated metrics
- Public benchmark datasets released
- Validation study paper published
- APIs accepting requests

______________________________________________________________________

## Final Assessment

**Strategic Vision:** 9/10 (Excellent market positioning)
**Execution Plan:** 6/10 (Missing ML detail)
**Risk Mitigation:** 4/10 (Validation gaps)
**Overall Grade:** 7/10 (Good direction, execution gaps)

**Recommendation:** Implement all Priority 1 and Priority 2 recommendations. Estimated additional effort: 48-60 days spread across 12-week roadmap. Expected ROI: High credibility + competitive advantage.
