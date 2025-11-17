# Risk Register

**Date:** November 17, 2025 | **Total Risks:** 13 | **Critical:** 5 | **Medium:** 8

______________________________________________________________________

## 🔴 CRITICAL RISKS (Must Address Immediately)

### RISK C1: Code Refactoring Not Completed on Time

| Element         | Value                            |
| --------------- | -------------------------------- |
| **Probability** | 40% (MEDIUM)                     |
| **Impact**      | CRITICAL (blocks Task 3 cleanly) |
| **Priority**    | 🔴 P0 - IMMEDIATE                |
| **Owner**       | Backend Developer                |

**Description:**
Refactoring sprint (extracting abstractions, eliminating duplication) is critical path item. If not completed Week 0, Task 3 proceeds with poor architecture, making multi-sport addition difficult.

**Trigger:**

- Backend dev unavailable
- Scope underestimated
- Complications during extraction

**Impact If Occurs:**

- Technical debt compounds (2.96% → 8%+ duplication)
- Task 3 harder to implement cleanly
- Task 4 running becomes complexity nightmare
- Future sports impossible to add

**Mitigation Strategies:**

1. **Schedule this week** - Lock in backend dev's calendar NOW
1. **Define scope clearly** - List exact files/functions to refactor
1. **Time-box strictly** - 5-6 days max, strict scope boundaries
1. **Test first** - Ensure existing tests pass before refactoring
1. **Pair programming** - Backend dev + another dev for continuity
1. **Daily standups** - Track progress daily, catch issues early

**Contingency:**

- If refactoring slips: Proceed with Task 3 server-side only (no multi-sport abstraction)
- May need to refactor Task 3 and Task 4 together later (more expensive)

**Success Criteria:**

- [ ] Sprint completed on time (5-6 days)
- [ ] 700 lines duplication eliminated
- [ ] All tests still passing
- [ ] Duplication: 2.96% → 2.5%
- [ ] `PhaseDetector` abstraction ready for running

______________________________________________________________________

### RISK C2: Real-Time Latency Target Not Achievable

| Element         | Value                         |
| --------------- | ----------------------------- |
| **Probability** | 50% (MEDIUM-HIGH)             |
| **Impact**      | CRITICAL (market positioning) |
| **Priority**    | 🔴 P0 - WEEK 1 GO/NO-GO       |
| **Owner**       | CV Engineer + DevOps          |

**Description:**
Strategic plan assumes \<200ms E2E latency achievable with server-side MediaPipe. Actual latency is 250-350ms due to network overhead. If we can't hit \<200ms, competitive positioning damaged.

**Trigger:**

- Network latency higher than assumed
- MediaPipe processing slower than expected
- Profiler shows limitations

**Impact If Occurs:**

- Cannot claim "real-time coaching feedback"
- Market differentiator lost (Motion-IQ has \<200ms)
- Coaches compare unfavorably to competitors
- Premium pricing harder to justify

**Mitigation Strategies:**

1. **Week 1 profiling** - Build empirical latency profiler ASAP
1. **Hybrid architecture** - Client-side TensorFlow.js (primary) + server fallback
1. **Network optimization** - WebSocket compression, delta updates only
1. **Processing optimization** - Lite model for speed vs accuracy trade-off
1. **Cache aggressively** - Pre-compute what we can
1. **Early decision** - End of Week 1, decide server-only vs hybrid

**Contingency:**

- If \<200ms not achievable: Use hybrid (client-side): \<150ms achievable
- If hybrid impossible: Proceed with 250-350ms positioning ("responsive feedback")
- Fall back to offline demo for \<50ms showing power

**Success Criteria:**

- [ ] Latency profiler built and working
- [ ] Actual latencies measured (not theoretical)
- [ ] \<200ms achieved (hybrid) OR \<250ms documented (server)
- [ ] Decision made by end of Week 1
- [ ] Architecture finalized for remaining Task 3 work

______________________________________________________________________

### RISK C3: Running Parameters Undefined (Accuracy Risk)

| Element         | Value                            |
| --------------- | -------------------------------- |
| **Probability** | 45% (MEDIUM)                     |
| **Impact**      | CRITICAL (credibility loss)      |
| **Priority**    | 🔴 P0 - WEEKS 1-2 DEFINITION     |
| **Owner**       | ML Data Scientist + Biomechanics |

**Description:**
Running gait parameters (detection confidence, Butterworth cutoff, etc.) are fundamentally different from jumping. If not defined correctly before Task 4, implementation will produce poor accuracy results.

**Trigger:**

- Parameters not defined before Week 5 Task 4 starts
- Parameter assumptions wrong (tested too late)
- Field testing reveals poor accuracy

**Impact If Occurs:**

- Running analysis unreliable (±50-100ms GCT instead of ±30-50ms)
- Cannot claim "multi-sport platform" with credibility
- Coaches distrust metrics
- Partnerships fall apart (accuracy claims not validated)

**Mitigation Strategies:**

1. **Week 1-2 definition** - Define parameters immediately with ML + Biomechanics
1. **Prototype testing** - 1-week prototype validation (test on real videos)
1. **Sensitivity analysis** - Understand which parameters most affect accuracy
1. **Ground truth** - Compare prototype output to known-good 120fps video
1. **Safety margins** - Conservative thresholds for accuracy first
1. **Documentation** - Record parameter rationale for future reference

**Contingency:**

- If parameters wrong: Pivot to Weeks 4-5 (instead of 5-7) for parameter tuning
- May delay running launch 1-2 weeks if major issues found
- Fall back to core metrics only (defer landing pattern to Phase 2)

**Success Criteria:**

- [ ] Running parameters documented and ratified
- [ ] 1-week prototype test shows acceptable accuracy
- [ ] ±30-50ms GCT achievable on benchmark videos
- [ ] Cadence detection accurate to ±3 steps/min
- [ ] Landing pattern classifier 80%+ accurate
- [ ] Decision: Proceed with Task 4 or adjust scope

______________________________________________________________________

### RISK C4: Infrastructure Not Ready by Week 3

| Element         | Value                                |
| --------------- | ------------------------------------ |
| **Probability** | 40% (MEDIUM)                         |
| **Impact**      | CRITICAL (blocks Task 3 deployment)  |
| **Priority**    | 🔴 P0 - INFRASTRUCTURE CRITICAL PATH |
| **Owner**       | DevOps Engineer                      |

**Description:**
Infrastructure build (Dockerfile, GitHub Actions, monitoring, AWS setup) MUST complete by Week 3 to enable Task 3 deployment. If delayed, real-time service cannot go to staging.

**Trigger:**

- DevOps engineer unavailable
- AWS setup complications
- Container image optimization needed
- Monitoring setup underestimated

**Impact If Occurs:**

- Task 3 cannot deploy (stuck in development)
- Real-time launch delayed 2-4 weeks
- Timeline slips to Month 3+ (instead of Month 2)
- Market window closes

**Mitigation Strategies:**

1. **Assign DevOps this week** - Lock calendar NOW
1. **Prioritize critical path** - Dockerfile → CI/CD → monitoring → optional enhancements
1. **Early AWS setup** - Account, IAM roles, networking ready Week 1
1. **Container optimization** - Start with simple, optimize later
1. **Monitoring baseline** - Prometheus + basic alerting (advanced tuning later)
1. **Daily standups** - Track progress vs Week 3 deadline

**Contingency:**

- If infrastructure delayed: Deploy to simple staging (single server) for testing
- Optimize infrastructure in parallel with Task 3 implementation
- Move full deployment to Week 4+ if necessary

**Success Criteria:**

- [ ] Dockerfile built and \<500MB
- [ ] Docker Compose working locally (dev stack)
- [ ] GitHub Actions build + push working
- [ ] AWS ECS staging environment ready
- [ ] Prometheus + Grafana collecting metrics
- [ ] Load testing framework (Locust) ready
- [ ] Deployment runbook complete

______________________________________________________________________

### RISK C5: Validation Study Lab Access Not Available

| Element                                              | Value                   |
| ---------------------------------------------------- | ----------------------- |
| **Probability**                                      | 25% (LOW-MEDIUM)        |
| **Impact**                                           | CRITICAL (partnerships) |
| **Priority**                                         | 🔴 P0 - MUST PLAN EARLY |
| **Owner:** Biomechanics Specialist + Project Manager |                         |

**Description:**
Validation study (force plate comparison) is critical for partnership credibility. If lab access not available Month 3-4, study delayed or impossible. Must contact labs NOW for availability.

**Trigger:**

- No lab space available Month 3-4
- Lab access costs prohibitive
- Academic partner unavailable
- Alternative validation method needed

**Impact If Occurs:**

- Cannot publish validation study Month 3
- Partnership negotiations delayed
- Licensing revenue delayed (1-2 years)
- Competitors with validated studies get partnerships first

**Mitigation Strategies:**

1. **Contact labs this week** - Identify 3 potential partners (university, sports science center, PT clinic)
1. **Negotiate access** - Budget $5-10K for lab time + equipment
1. **Lock dates now** - Reserve Month 3-4 slots before they fill
1. **Prepare protocol** - Draft validation study protocol (sharing criteria, data collection, analysis plan)
1. **Backup plan** - Consider alternative validation methods (IMU comparison, optical marker tracking)
1. **Academic partnership** - Explore co-publishing opportunities (free lab access in exchange for co-authorship)

**Contingency:**

- If lab not available: Use alternative validation (IMU comparison, force plate-lite setup)
- Crowdsourced validation (athlete community feedback) as interim credibility
- Publish case studies instead of formal study

**Success Criteria:**

- [ ] 3 potential labs identified and contacted
- [ ] Month 3-4 slots reserved with deposit
- [ ] Validation protocol drafted (ready for lab review)
- [ ] Budget approved ($5-10K lab time)
- [ ] Academic partner identified (co-authorship agreement in progress)

______________________________________________________________________

## 🟡 MEDIUM RISKS (Monitor & Mitigate)

### RISK M1: Running GCT Accuracy Insufficient

| Element         | Value                        |
| --------------- | ---------------------------- |
| **Probability** | 35% (MEDIUM)                 |
| **Impact**      | MEDIUM (scope, not critical) |
| **Priority**    | 🟡 P1 - Monitor              |
| **Owner**       | Biomechanics + ML            |

**Description:**
Running ground contact time achieves ±30-50ms (recreational grade) instead of elite ±5-10ms. Acceptable for fitness/injury prevention but not elite training.

**Mitigation:**

- Accept recreational scope in marketing
- Disclose accuracy limits in documentation
- Position as "form feedback for injury prevention"
- Plan Phase 2 advanced metrics for elite athletes

______________________________________________________________________

### RISK M2: Multi-Person Detection Deferred

| Element         | Value                      |
| --------------- | -------------------------- |
| **Probability** | 60% (MEDIUM-HIGH)          |
| **Impact**      | MEDIUM (feature, not core) |
| **Priority**    | 🟡 P1 - Track for Task 3B  |
| **Owner**       | CV Engineer                |

**Description:**
Multi-person detection requires temporal tracking (2 weeks work). Not achievable in Task 3; deferred to Task 3B (Month 3).

**Mitigation:**

- Separate multi-person as Task 3B planning in Week 1
- Document approach for future implementation
- Communicate delay to stakeholders early
- Offer workaround (sequential single-person recordings)

______________________________________________________________________

### RISK M3: Foot_Index Visibility Loss

| Element         | Value                              |
| --------------- | ---------------------------------- |
| **Probability** | 30% (LOW-MEDIUM)                   |
| **Impact**      | MEDIUM (running landing detection) |
| **Priority**    | 🟡 P1 - Task 1 Validation          |
| **Owner**       | CV + Biomechanics                  |

**Description:**
Running analysis depends on foot_index (toe) visibility for landing pattern classification. May lose visibility during aggressive plantarflexion motion.

**Mitigation:**

- Task 1 validates foot_index on 10 real CMJ videos (2 hours)
- Implement fallback to heel if visibility issues detected
- Additional testing with running videos before Task 4
- Train ML model to infer foot_index when not visible

______________________________________________________________________

### RISK M4: CMJ Test Coverage 80% Not Achievable

| Element         | Value                 |
| --------------- | --------------------- |
| **Probability** | 20% (LOW)             |
| **Impact**      | MEDIUM (quality gate) |
| **Priority**    | 🟡 P1 - Monitor       |
| **Owner**       | QA Engineer           |

**Description:**
Target of 62% → 80%+ test coverage may not be achievable if existing code is harder to test than expected.

**Mitigation:**

- Task 2 defines specific test cases first (40-50 tests identified)
- Early assessment (Week 1) of coverage achievability
- Adjust target if needed (→ 75% acceptable minimum)
- Refactoring (Task 0) makes tests easier

______________________________________________________________________

### RISK M5: Real-Time Load Testing Issues

| Element         | Value                            |
| --------------- | -------------------------------- |
| **Probability** | 40% (MEDIUM)                     |
| **Impact**      | MEDIUM (performance, not launch) |
| **Priority**    | 🟡 P1 - Week 1 Testing Build     |
| **Owner**       | QA + DevOps                      |

**Description:**
Load testing infrastructure (Locust) may have issues at scale (100+ concurrent streams). Could reveal performance problems late in Task 3.

**Mitigation:**

- Build Locust framework Week 1 (not Week 4)
- Early performance profiling (Week 1-2)
- Gradual load increase (10 → 50 → 100 concurrent)
- Identify bottlenecks early for optimization

______________________________________________________________________

### RISK M6: API Documentation Scope Creep

| Element         | Value                        |
| --------------- | ---------------------------- |
| **Probability** | 50% (MEDIUM-HIGH)            |
| **Impact**      | LOW (timeline, not critical) |
| **Priority**    | 🟡 P1 - Scope Lock           |
| **Owner**       | Tech Writer + Backend        |

**Description:**
Task 5 (2 weeks) could expand with advanced integrations, multiple examples, additional SDKs. Could blow timeline if not scoped strictly.

**Mitigation:**

- Scope lock Week 1: MVP = OpenAPI + 1 example + Python SDK (core 80%)
- Defer to Phase 2: Advanced integrations, JavaScript SDK, webhook examples
- Track scope creep weekly

______________________________________________________________________

### RISK M7: Real-Time Deployment Issues

| Element         | Value                 |
| --------------- | --------------------- |
| **Probability** | 40% (MEDIUM)          |
| **Impact**      | MEDIUM (launch delay) |
| **Priority**    | 🟡 P1 - Early Testing |
| **Owner**       | DevOps + Backend      |

**Description:**
Moving from development (single instance) to production (scaling) may reveal unforeseen issues (WebSocket session management, state handling, etc.).

**Mitigation:**

- Early staging testing (Week 4-5 during Task 3 implementation)
- Load testing in staging before production
- Canary deployment strategy (5% → 25% → 100%)
- Rollback plan ready

______________________________________________________________________

### RISK M8: Adoption Slower Than Expected

| Element         | Value                          |
| --------------- | ------------------------------ |
| **Probability** | 40% (MEDIUM)                   |
| **Impact**      | MEDIUM (revenue/partnerships)  |
| **Priority**    | 🟡 P1 - Ongoing                |
| **Owner**       | Product Manager + Business Dev |

**Description:**
Even with good product, coach adoption may be slow (incumbent relationships strong, free tier cannibalization, etc.).

**Mitigation:**

- Beta program with influential coaches Month 2
- Free tier (1000 analyses/month) to drive adoption
- Partner integrations to reduce switching cost
- Case studies showing ROI to coaches

______________________________________________________________________

## 📊 Risk Heat Map (Ranked by Priority × Impact)

```
CRITICAL ZONE (Act Immediately)
┌─────────────────────────────────┐
│ C1: Refactoring (40% × HIGH)    │ → CRITICAL
│ C2: Latency (50% × HIGH)        │ → CRITICAL
│ C3: Parameters (45% × HIGH)     │ → CRITICAL
│ C4: Infrastructure (40% × HIGH) │ → CRITICAL
│ C5: Lab Access (25% × CRITICAL) │ → CRITICAL
└─────────────────────────────────┘

HIGH ZONE (Monitor Closely)
┌─────────────────────────────────┐
│ M6: API Scope Creep (50% × LOW) │ → HIGH
│ M2: Multi-Person (60% × MED)    │ → HIGH
│ M5: Load Testing (40% × MED)    │ → HIGH
└─────────────────────────────────┘

MEDIUM ZONE (Manage)
┌─────────────────────────────────┐
│ M8: Adoption (40% × MED)        │ → MEDIUM
│ M7: Deployment (40% × MED)      │ → MEDIUM
│ M1: GCT Accuracy (35% × MED)    │ → MEDIUM
│ M3: Foot_Index (30% × MED)      │ → MEDIUM
└─────────────────────────────────┘

LOW ZONE (Track)
┌─────────────────────────────────┐
│ M4: Coverage (20% × MED)        │ → LOW
└─────────────────────────────────┘
```

______________________________________________________________________

## 🚨 Risk Escalation Triggers

**If Any of These Happen, Escalate Immediately:**

1. **Refactoring not started by Monday (Week 0)**

   - Escalate to CTO
   - Consider contract resource
   - May slip timeline by 1 week

1. **Latency profiler not complete by Thursday of Week 1**

   - Escalate to CTO
   - Architecture decision will miss Friday deadline
   - Real-time feature delayed

1. **Running parameters not defined by end of Week 2**

   - Escalate to VP Engineering
   - Task 4 cannot start Week 5
   - Timeline slips 1-2 weeks

1. **Infrastructure not at 50% by end of Week 1**

   - Escalate to DevOps Lead
   - Week 3 deadline at risk
   - May need additional resources

1. **Lab partner not locked by Friday**

   - Escalate to Project Manager
   - Validation study timeline at risk
   - Partnership pipeline delayed

______________________________________________________________________

## 📋 Weekly Risk Review Template

**Every Friday, review:**

| Risk               | Status       | Probability | Impact | Mitigation | Owner |
| ------------------ | ------------ | ----------- | ------ | ---------- | ----- |
| C1: Refactoring    | 🟢 / 🟡 / 🔴 | %           | Level  | Action?    | Name  |
| C2: Latency        | 🟢 / 🟡 / 🔴 | %           | Level  | Action?    | Name  |
| C3: Parameters     | 🟢 / 🟡 / 🔴 | %           | Level  | Action?    | Name  |
| C4: Infrastructure | 🟢 / 🟡 / 🔴 | %           | Level  | Action?    | Name  |
| C5: Lab Access     | 🟢 / 🟡 / 🔴 | %           | Level  | Action?    | Name  |

______________________________________________________________________

**Status:** Risk register complete. Ready for weekly reviews.

**Last Updated:** November 17, 2025
**Review Schedule:** Every Friday + escalation if triggers hit
