# Critical Decision Points

**Date:** November 17, 2025 | **Decisions Needed:** This Week | **Status:** Ready for Leadership

______________________________________________________________________

## 🎯 3 CRITICAL DECISIONS

### DECISION #1: Real-Time Architecture

**Timeline:** Week 1 of Task 3 (end of first sprint)

**Question:** Can we achieve \<200ms end-to-end latency?

**Context:**

- Strategic plan assumes server-side MediaPipe → 250-350ms (too slow)
- Market expects \<200ms for coaching feedback to feel natural
- Two technical approaches with different trade-offs

______________________________________________________________________

#### Option A: Pure Server-Side MediaPipe

**Architecture:**

- Client browser → WebSocket → Server (MediaPipe + Python analysis) → Response
- Network latency: 80-120ms (real-world WiFi/4G)
- Server processing: 50-100ms (MediaPipe 40ms + metrics 10-60ms)
- **Total: 250-350ms**

**Pros:**

- Simpler implementation (1 architecture, 2-3 weeks)
- Easier to optimize on server
- Better for older browsers

**Cons:**

- 🔴 Misses \<200ms target
- Poor UX for coaching feedback
- Network latency is bottleneck

**Cost:** 2-3 weeks development

______________________________________________________________________

#### Option B: Hybrid (Recommended) ✅

**Architecture:**

- Primary: Client-side TensorFlow.js (browser-native WebGL)
- Fallback: Server-side MediaPipe (for older browsers)
- Network: Only metrics sent back (not video frames)
- **Total Client-Side: \<150ms**
- **Total Fallback: \<250ms**

**Pros:**

- ✅ \<200ms on modern browsers (Safari, Chrome, Edge)
- ✅ Enables offline capability (premium feature)
- ✅ Monetization path (free tier local, premium server)
- Better UX, more responsive
- Works on older browsers (fallback)

**Cons:**

- ⚠️ More complex implementation
- +1 week development (hybrid + fallback logic)
- Client-side limitations (GPU/battery on mobile)

**Cost:** 3-4 weeks development (1 week extra for hybrid)

______________________________________________________________________

#### DECISION CRITERIA

**Measure:** Build latency profiler Week 1

- Empirical test of both approaches
- Measure actual network latency (not assume 50ms)
- Test on target browsers/devices
- Go/No-Go: Can we hit \<200ms?

**If Yes (\<200ms achievable):**

- ✅ Proceed with hybrid approach
- ✅ Enables competitive positioning
- ✅ Opens monetization paths

**If No (only 250-350ms possible):**

- ⚠️ Proceed with server-side
- ⚠️ Document as "responsive coaching feedback (250ms)"
- ⚠️ Position as "adequate for amateur coaches, professional athletes use premium server setup"

**Recommendation:** Option B (Hybrid) - Better market position + enablement

**Owner:** Computer Vision Engineer + DevOps
**Deadline:** End of Week 1 of Task 3
**Impact:** Affects all remaining real-time work

______________________________________________________________________

### DECISION #2: Project Timeline

**Timeline:** This Week (before Sprint 0 starts)

**Question:** Should we extend to 10-12 weeks for full validation, or compress to 6 weeks?

**Context:**

- Original plan: 6 weeks (high risk, tight)
- Adjusted plan: 10-12 weeks (lower risk, full validation)
- Market window: 12-18 months before consolidation
- Timeline is gate for partnerships

______________________________________________________________________

#### Option A: Compressed 6-Week Timeline

**Scope:**

- Task 1: Ankle fix (no extra validation)
- Task 2: CMJ tests (basic coverage)
- Task 3: Real-time (server-side OR hybrid, no optimization)
- Task 4: Running (basic implementation, no lab validation)
- Task 5: APIs (minimal scope, no full examples)
- ❌ Skip: Validation study, parameter testing, infrastructure hardening

**Pros:**

- Faster to market (2-4 months earlier)
- First-mover advantage
- Reduced cost

**Cons:**

- 🔴 High technical risk (no parameter testing)
- 🔴 Running accuracy may be poor (±100ms instead of ±30-50ms)
- 🔴 No validation study (partnerships difficult)
- 🔴 Technical debt not addressed
- 🔴 Real-time latency not validated
- Higher failure probability (50-60%)

**Timeline:**

```
Week 1-2: Task 1 + Task 2
Week 3-6: Task 3 + Task 4 + Task 5
Month 2: Production launch
Month 3+: Crisis mode (fixing accuracy issues)
```

______________________________________________________________________

#### Option B: Full 10-12 Week Timeline (Recommended) ✅

**Scope:**

- Week 0: Refactoring + parameter definition + infrastructure prep
- Weeks 1-2: Task 1 (validated) + Task 2 (80%+) + latency profiling
- Weeks 2-3: Platform foundation (Task 3/5 start)
- Weeks 4-5: Multi-sport proof (Task 3/4 running parallel)
- Weeks 6-7: Release with validated metrics
- Weeks 8-9: Beta + hardening
- Weeks 10-11: Validation study (force plate comparison)
- Week 12: Credibility launch (validation paper published)

**Pros:**

- ✅ Low risk (all components validated)
- ✅ Validation study (partnerships enabled)
- ✅ Running parameters tested (accuracy proven)
- ✅ Technical debt eliminated
- ✅ Real-time latency validated
- ✅ Premium positioning ("validated accuracy platform")
- Higher success probability (85-90%)

**Cons:**

- 4-6 weeks longer to market
- Higher development cost
- Competitors may launch first

**Timeline:**

```
Week 0-7: Platform launch (validated, ready for partnerships)
Month 2: Production launch + partnerships begin
Weeks 10-11: Validation study results
Month 3+: "Validated accuracy" marketing + licensing pipeline
```

______________________________________________________________________

#### DECISION CRITERIA

**Market Window Analysis:**

- Now → 12 months: Market consolidation happening
- Competitive threat: Motion-IQ, FormPro expanding
- Partnership value: Validation study worth $X in deals
- Revenue model: Licensing requires validation

**Timeline Risk-Reward:**

- 6 weeks: Fast launch, high accuracy risk, hard partnerships
- 10-12 weeks: Slower launch, validated accuracy, easy partnerships

**Success Probability:**

- 6 weeks: 50-60% (likely accuracy issues)
- 10-12 weeks: 85-90% (validated platform)

**Financial Impact:**

- 6 weeks: Earlier revenue, but high support cost (accuracy fixing)
- 10-12 weeks: Later revenue, but premium positioning + partnerships

**Recommendation:** Option B (10-12 weeks) - Better ROI through partnerships + validation

**Owner:** Project Manager + Stakeholders
**Deadline:** THIS WEEK
**Impact:** Cascades to all other decisions

______________________________________________________________________

### DECISION #3: Running Gait Scope

**Timeline:** Weeks 1-2 (parameter definition phase)

**Question:** What running metrics should we support in MVP?

**Context:**

- Market expects GCT, cadence, landing pattern
- Stride length and vertical oscillation are "nice to have"
- Parameter testing will validate feasibility
- Scope affects complexity + implementation time

______________________________________________________________________

#### Option A: Core 3 Metrics (Recommended) ✅

**Metrics:**

- Ground Contact Time (GCT)
- Cadence (steps/minute)
- Landing Pattern (heel/midfoot/forefoot classification)

**Pros:**

- ✅ MVP ready Month 2
- ✅ Enough for injury prevention guidance
- ✅ Simpler to validate (3 instead of 5 metrics)
- ✅ Less prone to accuracy issues
- ✅ Leaves room for Phase 2 expansion

**Cons:**

- Customers ask "where's stride length?"
- Advanced athletes disappointed
- Positioning limited to "fitness" vs "performance"

**Accuracy Expectations:**

- GCT: ±30-50ms (recreational grade)
- Cadence: ±2-3 steps/min
- Landing: 80-90% classification accuracy

**Timeline:** 2-3 weeks (Weeks 5-7)

______________________________________________________________________

#### Option B: Core + Advanced (5 Metrics)

**Metrics:**

- Ground Contact Time ✅
- Cadence ✅
- Landing Pattern ✅
- Stride Length ❓
- Vertical Oscillation ❓

**Pros:**

- More complete analysis
- Better for performance-focused athletes
- Premium positioning

**Cons:**

- 🔴 Stride length requires camera calibration
- 🔴 Vertical oscillation accuracy difficult without calibration
- 🔴 Adds 1-2 weeks implementation
- 🔴 Higher accuracy risk (→ credibility loss)
- Complex validation

**Accuracy Expectations:**

- GCT: ±30-50ms
- Cadence: ±2-3 steps/min
- Landing: 80-90%
- Stride length: ±10-20% (without calibration)
- Vertical oscillation: ±5-15cm (high uncertainty)

**Timeline:** 3-4 weeks (1-2 weeks extra)

______________________________________________________________________

#### DECISION CRITERIA

**MVP vs Premium:**

- MVP (Core 3): Fitness focus, MVP ready, risk low
- Premium (Core + Advanced): Performance focus, delayed launch, risk higher

**Market Positioning:**

- Core 3: "Fitness app for injury prevention" 🎯 Good for coaches
- Core + Advanced: "Performance analysis platform" 🎯 Good for athletes

**Recommendation:** Option A (Core 3) - MVP scope, Phase 2 expansion

**Owner:** Biomechanics Specialist + ML Data Scientist
**Deadline:** Weeks 1-2 (parameter definition)
**Impact:** Task 4 implementation scope

**Phase 2 Plan:** Add stride length + vertical oscillation once camera calibration ready

______________________________________________________________________

## 📊 Decision Matrix

| Decision             | Option          | Timeline  | Risk   | Effort      | Confidence | Recommendation   |
| -------------------- | --------------- | --------- | ------ | ----------- | ---------- | ---------------- |
| **Real-Time Arch**   | Pure Server     | Week 3    | MEDIUM | 2 weeks     | 70%        | ❌ No            |
|                      | Hybrid          | Week 3    | LOW    | 3 weeks     | 90%        | ✅ YES           |
| **Project Timeline** | 6 weeks         | Month 2   | HIGH   | Low cost    | 50%        | ❌ No            |
|                      | 10-12 weeks     | Month 3   | LOW    | Higher cost | 85%        | ✅ YES           |
| **Running Scope**    | Core 3          | Weeks 5-7 | LOW    | 2 weeks     | 85%        | ✅ YES           |
|                      | Core + Advanced | Weeks 6-8 | MEDIUM | 3-4 weeks   | 70%        | ❌ Maybe Phase 2 |

______________________________________________________________________

## 🚀 DECISION PACKAGE FOR LEADERSHIP

### What Needs to Be Decided

1. **By Friday:** Approve 10-12 week timeline (or negotiate timeline)
1. **By Friday:** Approve hybrid real-time architecture as plan A
1. **By Friday:** Approve core 3 running metrics for MVP
1. **By Friday:** Commit resources (DevOps, ML, Biomechanics)
1. **By Friday:** Approve infrastructure budget ($100-200K Year 1)

### What's Already Decided

- ✅ Ankle fix approach (approved by all agents)
- ✅ CMJ testing scope (approved by QA + Biomechanics)
- ✅ API documentation approach (approved by Tech Writer)
- ✅ Validation study need (approved by all agents)

### Who Should Decide

- **Project Timeline:** CEO/Product/Finance
- **Real-Time Architecture:** CTO/Technical Leadership
- **Running Scope:** Product Manager/Biomechanics Lead
- **Resource Approval:** Department Heads
- **Budget Approval:** CFO/Finance

### Decision Timeline

- **This Week (Thursday):** Leadership review + decisions
- **Friday:** Owner assignments + sprint kickoff meeting
- **Monday (Week 1):** Execution begins

______________________________________________________________________

## 📋 Decision Tracker

| Decision                                | Status     | Owner        | Deadline  | Approved |
| --------------------------------------- | ---------- | ------------ | --------- | -------- |
| Project Timeline (6 vs 10-12 weeks)     | 🟡 PENDING | CEO/Product  | THIS WEEK | ☐        |
| Real-Time Architecture (pure vs hybrid) | 🟡 PENDING | CTO          | THIS WEEK | ☐        |
| Running Scope (3 vs 5 metrics)          | 🟡 PENDING | Product Mgmt | THIS WEEK | ☐        |
| Infrastructure Budget                   | 🟡 PENDING | CFO          | THIS WEEK | ☐        |
| Resource Commitments                    | 🟡 PENDING | Dept Heads   | THIS WEEK | ☐        |

______________________________________________________________________

## 🎯 If Decisions Are Delayed

**Risk of Non-Decision:**

- 🔴 Sprint 0 (refactoring) cannot start without timeline approval
- 🔴 Week 1 latency testing cannot start without real-time architecture approval
- 🔴 Running parameter definition cannot start without scope approval
- 🔴 Infrastructure build cannot start without budget approval

**Cascade Effect:**

- Timeline delays → Project delays → Market window closes → Competitive disadvantage

**Recommendation:** Decide by EOB Friday to avoid Monday delays

______________________________________________________________________

## 📞 Questions for Leadership

**"Is 10-12 weeks too long?"**

- Market consolidation timeframe: 12-18 months (we have time)
- Competitor pace: Motion-IQ took 2+ years to validation
- Partnership value: Validation study enables licensing revenue
- Risk: Rushing (6 weeks) → accuracy issues → credibility loss

**"What if we can't hit \<200ms latency?"**

- Fallback: Server-side (250-350ms) still adequate for amateur coaches
- Positioning: "Responsive coaching feedback" instead of "real-time"
- Market: Satisfies 80% of coaches (not elite athletes)

**"Why core 3 running metrics instead of 5?"**

- Stride length + vertical oscillation require calibration (not ready)
- MVP: Achieve 85% accuracy with 3 metrics vs 70% with 5
- Phase 2: Add advanced metrics once calibration ready
- Market: Core 3 sufficient for injury prevention positioning

**"What's the budget impact of 10-12 weeks?"**

- Development cost: +4-6 weeks of team time
- Infrastructure cost: +$5-10K (validation study lab access)
- BUT: Licensing revenue from validation study = ROI in first partnership
- Bottom line: Higher upfront cost, better long-term ROI

______________________________________________________________________

**Status:** Ready for leadership decision

**Last Updated:** November 17, 2025
**Next Step:** Schedule leadership decision meeting
