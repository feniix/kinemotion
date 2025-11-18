# Critical Findings & Top Risks

**Date:** November 17, 2025 | **Agent Review:** Complete | **Priority:** IMMEDIATE ACTION

______________________________________________________________________

## 🚨 5 CRITICAL ISSUES (Must Address This Week)

### 🔴 CRITICAL #1: Code Refactoring is Execution Blocker

**Issue:** Backend code duplication prevents clean multi-sport extension

**Evidence:**

- Current duplication: 2.96% of codebase
- After adding running without refactoring: 8%+ duplication (maintainability crisis)
- 700+ lines of duplicated logic between jump types
- Adding more sports multiplies the problem

**What's Blocked:** Task 3 cannot proceed cleanly without this

**Required Refactoring (5-6 days):**

```
- Extract MotionAnalyzer base class (eliminates 700 lines)
- Extract PhaseDetector abstraction (for jump/running/other sports)
- Extract StreamingPoseProcessor (80 lines)
- Extract MetricsCalculator interface (100 lines)
- Consolidate api.py (1150 → 450 lines)
```

**Result:** Net -170 lines, 2.96% → 2.5% duplication, scalable architecture

**Decision:** Must complete this week (Sprint 0) BEFORE Task 1 starts

**Owner:** Python Backend Developer

**Timeline:** THIS WEEK (5-6 day sprint)

**Risk if delayed:** Technical debt compounds; each new sport gets harder to add

______________________________________________________________________

### 🔴 CRITICAL #2: \<200ms Latency Requires Hybrid Architecture

**Issue:** Strategic plan claims \<200ms with server-side MediaPipe only; NOT feasible

**Evidence:**

- Server-side MediaPipe latency: 250-350ms (too slow for coaching feedback)
- Network latency: 80-120ms real-world (not 50ms assumed)
- Budget breakdown shows 50ms alone to network overhead

**What's Required:** Client-side + server-side hybrid

- Client: TensorFlow.js via WebGL (browser-native)
- Server: MediaPipe (fallback for older browsers)
- Result: \<150ms on modern browsers, \<250ms fallback

**Decision Point:** Week 1 of Task 3

- Build latency profiler (empirical measurement)
- Test actual client vs server vs hybrid performance
- Go/No-Go: Can we hit \<200ms?

**Owner:** Computer Vision Engineer + DevOps

**Timeline:** Week 1 of Task 3 (critical decision)

**Risk if missed:** Deploy slow system → coaches reject → market loss

**Mitigation:** Early performance testing, hybrid architecture backup

______________________________________________________________________

### 🔴 CRITICAL #3: Running Parameters Undefined

**Issue:** Running gait parameters fundamentally different from jumping; NOT auto-compatible

**Evidence:**

- Detection confidence: 0.70 (vs 0.5 for jumps)
- Tracking confidence: 0.65 (vs 0.5)
- Butterworth cutoff: 5 Hz (vs 8 Hz for jumps)
- Savgol window: 9 frames (vs 11 for jumps)
- Velocity threshold: 0.05 m/s (vs 0.10 for jumps)

**Impact:** Wrong parameters = poor running accuracy = credibility loss

**What's Required (Weeks 1-2):**

1. Define running quality presets with ML + Biomechanics
1. Create validation framework (vs ground-truth force plate)
1. Design benchmark dataset
1. 1-week prototype validation before full Task 4 sprint

**Decision Point:** Must complete BEFORE Week 5 Task 4 starts

**Owner:** ML Data Scientist + Biomechanics Specialist

**Timeline:** Weeks 1-2 (IMMEDIATE)

**Risk if missed:** Running analysis unreliable → cannot claim "multi-sport platform"

**Mitigation:** Parameter sensitivity analysis, early prototype testing

______________________________________________________________________

### 🔴 CRITICAL #4: Infrastructure Investment Required by Week 3

**Issue:** Current infrastructure 3/10 for platform needs; gaps gate Task 3 deployment

**Missing Infrastructure:**

1. Dockerfile + Docker Compose (5-8 days)
1. GitHub Actions deployment pipeline (5-7 days)
1. Locust load testing framework (3-4 days)
1. Prometheus + Grafana monitoring (4-5 days)
1. AWS ECS staging environment

**Timeline:** MUST COMPLETE BY WEEK 3 (gates Task 3 start)

**Resource:** 60% FTE DevOps engineer, 6 weeks

**Cost:** $100-200/mo staging, $500-1000/mo production (Year 1)

**Owner:** DevOps/CI-CD Engineer

**Decision:** Approve budget + assign DevOps lead THIS WEEK

**Risk if delayed:** Task 3 (real-time) blocked Week 3 → cascading timeline delays

**Mitigation:** Start Week 1, prioritize critical path components

______________________________________________________________________

### 🔴 CRITICAL #5: Validation Study Not in Roadmap

**Issue:** No validation study planned; domain experts say this is CRITICAL for partnerships

**Why This Matters:**

- Coaches/medical professionals demand accuracy proof
- Competitors cite validation studies in marketing
- Partnerships require validated accuracy claims
- Liability protection for coaching recommendations
- Enables premium positioning, licensing revenue

**What's Required (Month 3-4):**

- Compare Kinemotion vs gold-standard (force plate or marker system)
- CMJ accuracy: GCT \<20ms MAE, ICC >0.90
- Running accuracy: GCT \<15ms MAE, cadence \<3 spm
- 4-6 page technical report with statistical analysis
- Bland-Altman plots, confidence intervals

**Timeline:** Month 3-4 (not this month, but plan NOW)

- 3-4 weeks conduct (need lab access)
- 1-2 weeks write and publish

**Cost:** ~$5-10K lab time (potential academic partnership)

**Owner:** Biomechanics Specialist + ML Data Scientist

**Decision:** Contact potential lab partners THIS WEEK for Month 3-4 slots

**Risk if missed:** Cannot claim "validated accuracy" → partnerships fall through

**Mitigation:** Identify and contact labs this week, plan contingencies

______________________________________________________________________

## ⚠️ 8 MEDIUM-RISK ISSUES (Action Required)

### Issue M1: Running GCT Accuracy Limited

**Problem:** Running ground contact time achieves ±30-50ms (recreational scope, not elite)

**Evidence:** No published research validates running GCT from video using MediaPipe (only force plate/IMU)

**Impact:** Cannot market as elite athlete grade; suitable for recreational runners and injury prevention

**Action:** Accept recreational scope in marketing; disclose accuracy limits

**Timeline:** Before Task 4 launch (Month 2)

______________________________________________________________________

### Issue M2: Multi-Person Detection Deferred

**Problem:** Strategic plan lists multi-person as "immediately feasible"; actually requires 2 weeks work

**Evidence:** Needs temporal tracking layer (Hungarian algorithm) not currently implemented

**Action:** Separate as Task 3B (post-MVP, after real-time baseline)

**Timeline:** Month 3+ (not Month 2)

______________________________________________________________________

### Issue M3: Foot_Index Visibility Risk

**Problem:** Running gait landing classification depends on foot_index (toe) landmark; may lose visibility during aggressive motion

**Impact:** Could affect landing pattern detection accuracy

**Action:** Task 1 must validate foot_index visibility on real CMJ videos before assuming it works for running

**Timeline:** Task 1 validation (Week 1)

______________________________________________________________________

### Issue M4: Test Coverage Target (62% → 80%)

**Problem:** CMJ testing coverage 62% → 80% (18% improvement) is achievable but requires 40-50 new tests

**Action:** Define test cases: phase progression, physiological bounds, edge cases

**Timeline:** Task 2 (Weeks 1-2)

______________________________________________________________________

### Issue M5: Real-Time Testing Infrastructure Missing

**Problem:** No load testing framework, latency profiler, or multi-client testing tools

**Action:** Build Locust framework + latency profiler Week 1 (QA + DevOps)

**Timeline:** Week 1 (gates Task 3 go/no-go decision)

______________________________________________________________________

### Issue M6: API Documentation Scope Creep Risk

**Problem:** Task 5 (2 weeks) could expand: OpenAPI, 3 integrations, SDKs, webhooks

**Action:** Scope lock: MVP = OpenAPI + 1 integration example + Python SDK (core 80%, saves 1 week)

**Timeline:** Weeks 2-3 for MVP; defer advanced integrations to Phase 2

______________________________________________________________________

### Issue M7: Validation Study Lab Access Risk

**Problem:** May not have lab access available Month 3-4 when needed

**Action:** Contact potential academic/lab partners NOW for availability

**Timeline:** This week (secure slots for Month 3-4)

______________________________________________________________________

### Issue M8: DevOps Resource Constraint

**Problem:** Need 60% FTE DevOps engineer for 6 weeks; may not be available

**Action:** Secure commitment this week; consider contract resource if needed

**Timeline:** This week (resource planning)

______________________________________________________________________

## 📊 Risk Heat Map

| Risk                                  | Probability  | Impact   | Priority | Owner             |
| ------------------------------------- | ------------ | -------- | -------- | ----------------- |
| Refactoring not done on time          | MEDIUM (40%) | CRITICAL | 🔴 P0    | Backend Dev       |
| Latency target missed                 | MEDIUM (50%) | CRITICAL | 🔴 P0    | CV Eng + DevOps   |
| Running parameters undefined          | MEDIUM (45%) | CRITICAL | 🔴 P0    | ML + Biomechanics |
| Infrastructure not ready Week 3       | MEDIUM (40%) | CRITICAL | 🔴 P0    | DevOps            |
| Validation study lab access denied    | LOW (20%)    | HIGH     | 🟡 P1    | Biomechanics      |
| Multi-person detection underestimated | MEDIUM (60%) | MEDIUM   | 🟡 P1    | CV Engineer       |
| Running GCT accuracy insufficient     | MEDIUM (35%) | MEDIUM   | 🟡 P1    | Biomechanics + ML |
| Test coverage 80% not achievable      | LOW (20%)    | MEDIUM   | 🟡 P1    | QA Engineer       |
| Real-time load testing issues         | MEDIUM (40%) | MEDIUM   | 🟡 P1    | QA + DevOps       |
| API scope creep                       | MEDIUM (50%) | LOW      | 🟢 P2    | Tech Writer       |
| Foot_index visibility lost            | LOW (30%)    | MEDIUM   | 🟡 P1    | CV + Biomechanics |
| Timeline extension rejection          | LOW (25%)    | HIGH     | 🟡 P1    | Project Manager   |
| Adoption slower than expected         | MEDIUM (40%) | HIGH     | 🟡 P1    | Project Manager   |

______________________________________________________________________

## 🎯 Dependency Bottlenecks

### Bottleneck #1: Task 1 Blocks Task 4

- Task 1 (ankle fix) validates foot_index visibility
- Task 4 (running) depends on reliable foot_index
- **Timeline impact:** If Task 1 validation fails, running launch delayed 1-2 weeks

**Mitigation:** Early validation on real videos (2 hours)

______________________________________________________________________

### Bottleneck #2: Latency Profiling Blocks Task 3

- Week 1 latency profiler (empirical measurement)
- Go/no-go decision: Pure server (250-350ms) vs Hybrid (\<150ms)
- Architecture decision affects remaining 4 weeks of work

**Mitigation:** Build profiler immediately, decide by end of Week 1

______________________________________________________________________

### Bottleneck #3: Infrastructure Blocks Task 3 Deployment

- Weeks 1-3: Infrastructure build (Dockerfile, CI/CD, monitoring)
- Week 3: Real-time deployment gates to staging
- If delayed, Task 3 cannot deploy on schedule

**Mitigation:** Start Week 1, prioritize critical path

______________________________________________________________________

### Bottleneck #4: Running Parameters Block Task 4 Quality

- Weeks 1-2: Parameter definition + 1-week prototype test
- If parameters wrong, running accuracy fails at launch
- If delayed, Task 4 implementation delayed

**Mitigation:** Parallel work with Task 1-2, early prototype testing

______________________________________________________________________

## 📋 Pre-Execution Checklist

**Must Complete This Week:**

- [ ] **Refactoring Decision:** Assign backend developer, schedule sprint
- [ ] **Latency Decision:** Approve hybrid architecture as plan A
- [ ] **Infrastructure Decision:** Approve budget ($100-200K Year 1), assign DevOps
- [ ] **Parameters Decision:** Assign ML + Biomechanics team to Week 1-2 work
- [ ] **Validation Decision:** Contact potential labs for Month 3-4 slots
- [ ] **Resource Planning:** Confirm all owner assignments
- [ ] **Timeline Decision:** Approve 10-12 week timeline (or compress scope)
- [ ] **Success Metrics:** Agree on Month 1-2-3 milestones
- [ ] **Communication:** Brief all teams on roadmap + critical issues
- [ ] **Risk Management:** Establish weekly risk review cadence

______________________________________________________________________

## 🚀 This Week's Actions

### Priority 1 (Must Do By Friday)

1. Stakeholder review of this document
1. Decision on 5 critical issues (refactoring, latency, parameters, infrastructure, validation)
1. Assign all task owners
1. Approve budget for infrastructure

### Priority 2 (Start This Week)

1. Schedule refactoring sprint kickoff
1. Build latency profiler design (CV + DevOps)
1. Schedule parameter definition meeting (ML + Biomechanics)
1. Contact lab partners for Month 3-4 availability
1. Brief all teams on roadmap

### Priority 3 (Complete By End of Week 1)

1. Refactoring sprint complete
1. Latency profiler built and ready
1. Running parameters defined
1. Infrastructure Week 1 work started

______________________________________________________________________

## 📞 Questions?

- **"What's the impact on timeline?"** → [timeline-roadmap.md](./timeline-roadmap.md)
- **"What are the decision criteria?"** → [04-decision-points.md](./04-decision-points.md)
- **"How are these issues connected?"** → [04-decision-points.md](./04-decision-points.md)
- **"What's the full risk assessment?"** → [risk-register.md](./risk-register.md)

______________________________________________________________________

**Status:** Critical issues identified. Ready for leadership action.

**Last Updated:** November 17, 2025
**Next Review:** Weekly during execution
