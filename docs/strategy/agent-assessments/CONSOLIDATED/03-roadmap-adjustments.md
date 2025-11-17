# Roadmap Adjustments Based on Agent Review

**Date:** November 17, 2025 | **Status:** Ready for Approval

______________________________________________________________________

## 📋 Summary of Changes

**Original Plan:** 5 tasks, 6 weeks

**Adjusted Plan:** 5 tasks + prep work, 10-12 weeks (OR compress scope for 6 weeks)

**Key Changes:**

1. Add refactoring sprint (Week 0)
1. Add parameter definition work (Weeks 1-2)
1. Add infrastructure build (Weeks 1-3)
1. Add validation study planning (Week 0)
1. Adjust Task 3 to include latency decision point (Week 1)
1. Defer multi-person detection to Task 3B
1. Add validation study (Month 3-4, not concurrent)

______________________________________________________________________

## 🔄 Original vs Adjusted Roadmap

### ORIGINAL ROADMAP (From Strategic Analysis)

```
SPRINT 0 (Week 1)          FOUNDATION
├─ Task 1: Ankle fix ✓
└─ Task 2: CMJ tests (start)

SPRINT 1 (Weeks 2-3)       PLATFORM FOUNDATION
├─ Task 2: CMJ tests (complete)
├─ Task 3: Real-time (start)
└─ Task 5: API docs (start)

SPRINT 2 (Weeks 4-5)       MULTI-SPORT PROOF
├─ Task 3: Real-time (continue)
├─ Task 4: Running (start)
└─ Task 5: API docs (continue)

SPRINT 3 (Weeks 6-7)       RELEASE & DEMO
├─ Task 3: Real-time (complete)
├─ Task 4: Running (complete)
└─ Task 5: APIs (complete)

TIMELINE: 6 weeks
```

______________________________________________________________________

### ADJUSTED ROADMAP (Recommended)

```
SPRINT -1 (Week 0)         CRITICAL PREP
├─ Refactoring: Extract abstractions (5-6 days) 🔴 CRITICAL
├─ Parameter definition: Define running specs (3-4 days)
├─ Infrastructure prep: Identify tools + architecture
└─ Validation planning: Contact labs for Month 3-4

SPRINT 0 (Week 1)          FOUNDATION + GO/NO-GO DECISIONS
├─ Task 1: Ankle fix ✓
├─ Task 2: CMJ tests (start)
├─ Latency profiler: Build + measure (go/no-go decision) 🎯
├─ Infrastructure: Weeks 1 critical path (Dockerfile, CI/CD)
└─ Parameter tuning: 1-week running prototype test

SPRINT 1 (Weeks 2-3)       PLATFORM FOUNDATION
├─ Task 2: CMJ tests (complete) → 80%+ coverage
├─ Task 3: Real-time (start architecture based on latency decision)
├─ Task 5: API docs (OpenAPI spec + examples)
└─ Infrastructure: Weeks 2-3 (deployment, monitoring)

SPRINT 2 (Weeks 4-5)       MULTI-SPORT PROOF + VALIDATION
├─ Task 3: Real-time (continue implementation)
├─ Task 4: Running (start) → if parameter test passed
├─ Task 5: API docs (continue + integrate examples)
└─ Robustness testing: Multi-person, occlusion, lighting

SPRINT 3 (Weeks 6-7)       RELEASE & DEMO
├─ Task 3: Real-time (complete + performance validation)
├─ Task 4: Running (complete + validation tests)
├─ Task 5: APIs (complete + SDKs published)
└─ Staging deployment ready

SPRINT 4 (Weeks 8-9)       BETA & HARDENING
├─ Production deployment
├─ Multi-person detection (Task 3B, if started)
├─ Performance optimization
└─ Beta coach feedback integration

SPRINT 5 (Weeks 10-11)     VALIDATION STUDY CONDUCT
├─ Lab: Force plate comparison tests
├─ Data: Collect CMJ + running metrics
└─ Analysis: Statistical validation

SPRINT 6 (Weeks 12)        CREDIBILITY LAUNCH
├─ Study: Publish validation paper + case studies
├─ Marketing: Launch with "validated accuracy" positioning
├─ Partnerships: Begin partner negotiations
└─ Month 3-4 target: Partnerships + licensing pipeline

TIMELINE: 10-12 weeks (recommended) OR 6 weeks (compressed scope)
```

______________________________________________________________________

## 📝 Task-by-Task Changes

### TASK 1: Fix CMJ Ankle Joint Angle

**Original Plan:**

- Fix ankle calculation (heel → foot_index)
- Deploy immediately

**Adjusted Plan:**

- ✅ Fix ankle calculation (same)
- ⚠️ **ADD:** Validate foot_index visibility on 10 real CMJ videos (2 hours)
- ⚠️ **ADD:** Document fallback to heel if visibility issues detected
- ⚠️ **ADD:** This validation unblocks Task 4 (running analysis)

**Changes:**

- Timeline: Same (2-3 days)
- Risk reduction: Validates foot_index before Task 4 depends on it
- Success criteria: Ankle angle increases 30°+ during concentric phase

**Owner:** Biomechanics Specialist + Backend Developer

______________________________________________________________________

### TASK 2: Expand CMJ Testing

**Original Plan:**

- Expand from 62% → 80% test coverage
- 40-50 new tests

**Adjusted Plan:**

- ✅ Same scope (40-50 new tests)
- ⚠️ **ADD:** Phase progression tests (eccentric → concentric → takeoff)
- ⚠️ **ADD:** Physiological bounds validation
- ⚠️ **ADD:** Real video sample validation
- ⚠️ **ADD:** Ankle angle progression tests (validates Task 1 fix)

**Changes:**

- Timeline: Same (3-4 days)
- Coverage target: 62% → 80%+
- Added: Ankle angle progression tests (validates Task 1)

**Owner:** QA Engineer + Biomechanics Specialist

______________________________________________________________________

### TASK 3: Implement Real-Time Web-Based Analysis

**Original Plan:**

- WebSocket streaming, \<200ms E2E latency, live metrics
- Server-side MediaPipe

**Adjusted Plan:**

**WEEK 1 - DECISION SPRINT:**

- ⚠️ **ADD:** Build latency profiler (empirical measurement)
- ⚠️ **ADD:** Test server-side vs client-side vs hybrid performance
- 🎯 **ADD:** Go/No-Go decision: Which architecture?
  - Option A: Pure server-side (250-350ms) - simpler, slower
  - Option B: Hybrid (client TensorFlow.js + server) - better UX, 1 week extra
- Recommended: Hybrid for \<200ms target

**WEEKS 2-6 - IMPLEMENTATION (based on Week 1 decision):**

- ✅ Same metrics (CMJ height, GCT, RSI updating live)
- ⚠️ **CHANGE:** Architecture based on latency profiling decision
- ⚠️ **REMOVE:** Multi-person detection (moved to Task 3B, post-MVP)

**Changes:**

- +3 days Week 1 for latency profiling + decision
- Timeline: 3-4 weeks → 4-5 weeks (includes latency validation)
- Architecture: Server-only → Hybrid (likely recommendation)
- Multi-person: Task 3 → Task 3B (post-MVP, Month 3)

**Owner:** Computer Vision Engineer + Python Backend + DevOps

**Critical Dependency:** Week 1 latency profiler is go/no-go for \<200ms target

______________________________________________________________________

### TASK 4: Add Running Gait Analysis

**Original Plan:**

- Ground contact time, cadence, stride length, landing pattern
- Start Week 5

**Adjusted Plan:**

**WEEKS 1-2 (PARALLEL WITH OTHER WORK):**

- ⚠️ **ADD:** Parameter definition sprint (ML + Biomechanics)
  - Define confidence thresholds, Butterworth cutoff, Savgol window, velocity thresholds
- ⚠️ **ADD:** 1-week prototype validation test
- ⚠️ **ADD:** Benchmark dataset design

**WEEKS 5-7 (IMPLEMENTATION):**

- ✅ Same scope (GCT, cadence, landing pattern)
- ⚠️ **REMOVE:** Stride length (defer to Phase 2 - too complex for MVP)
- ⚠️ **CHANGE:** Only if Weeks 1-2 parameter test succeeds

**Dependencies:**

- Task 1: Foot_index validation must complete (enables landing pattern detection)
- Weeks 1-2: Running parameters must be defined and prototyped

**Changes:**

- +1 week (Weeks 1-2) for parameter definition and testing
- Timeline: 2-3 weeks → 3-4 weeks (includes early validation)
- Scope: Core 3 metrics (GCT, cadence, landing) instead of 4
- Success criteria: 80%+ landing pattern accuracy, ±30-50ms GCT

**Owner:** Biomechanics Specialist + ML Data Scientist + Backend Developer

______________________________________________________________________

### TASK 5: Build API Documentation & Integration Framework

**Original Plan:**

- OpenAPI spec, 3 integration examples, SDK (Python + JavaScript)
- Webhooks for real-time metric delivery
- Rate limiting / API key management

**Adjusted Plan:**

**SCOPE ADJUSTMENT:**

- ✅ OpenAPI 3.1 spec (same)
- ⚠️ **REDUCE:** 1 integration example MVP + 2 more in Phase 2 (reduce scope 33%)
- ✅ **KEEP:** Python SDK (core requirement)
- ⚠️ **DEFER:** JavaScript SDK to Phase 2 (can be auto-generated)
- ✅ **KEEP:** Webhooks (essential for real-time partnerships)
- ✅ **KEEP:** Rate limiting / API key management

**Changes:**

- Timeline: 2 weeks → 2 weeks (reduced scope matches timeline)
- MVP scope: OpenAPI + Python SDK + 1 example + webhooks
- Phase 2: Add 2 more examples + JavaScript SDK + additional integrations

**Owner:** Technical Writer + Backend Developer

**Rationale:** Faster to market while maintaining core ecosystem capability

______________________________________________________________________

## ⏰ NEW TIMELINE

### Week 0 (This Week) - CRITICAL PREP

**Refactoring Sprint (5-6 days)**

- Extract abstractions (MotionAnalyzer, PhaseDetector, StreamingPoseProcessor, MetricsCalculator)
- Result: Eliminates 700 lines duplication, enables clean multi-sport extension
- Owner: Backend Developer
- Timeline: THIS WEEK

**Parameter Definition Sprint (3-4 days)**

- Define running quality presets
- Create validation framework
- Design benchmark dataset
- Owner: ML + Biomechanics
- Timeline: Parallel with refactoring

**Infrastructure Planning (2-3 days)**

- Identify tools (Docker, Locust, Prometheus, Grafana)
- Design AWS ECS architecture
- Plan deployment strategy
- Owner: DevOps
- Timeline: Parallel with refactoring

**Validation Study Planning (2 days)**

- Contact potential labs for Month 3-4 slots
- Define study parameters (CMJ vs force plate, running vs 120fps video)
- Budget validation study ($5-10K lab time)
- Owner: Biomechanics + Project Manager
- Timeline: This week

______________________________________________________________________

### Week 1 (Sprint 0) - FOUNDATION + GO/NO-GO DECISIONS

**Task 1: Ankle Fix + Validation (2-3 days)**

- Fix ankle calculation
- Validate foot_index visibility on 10 real videos
- Deploy with fallback strategy
- Owner: Biomechanics + Backend

**Task 2: CMJ Testing (Start, 3-4 days)**

- Create 40-50 new tests
- Phase progression tests
- Physiological bounds tests
- Owner: QA + Biomechanics

**Latency Profiler (3 days) - GO/NO-GO DECISION**

- Build empirical measurement tool
- Test server vs client vs hybrid
- Decide architecture: Pure server (slower) vs Hybrid (\<150ms)
- Owner: CV + DevOps

**Infrastructure Week 1 (5 days - parallel)**

- Dockerfile + Docker Compose
- GitHub Actions build workflow
- Begin AWS ECS setup
- Owner: DevOps

**Parameter Testing Week 1 (3 days - parallel)**

- Define running presets
- Build prototype validation
- Owner: ML + Biomechanics

______________________________________________________________________

### Weeks 2-3 (Sprint 1) - PLATFORM FOUNDATION

**Task 2: CMJ Testing (Complete)**

- 80%+ coverage achieved
- All tests passing
- Owner: QA + Biomechanics

**Task 3: Real-Time (Start)**

- Architecture selected (based on Week 1 latency profiler)
- Begin implementation
- Owner: CV + Backend + DevOps

**Task 5: API Docs (Start)**

- OpenAPI spec drafted
- 1 integration example started
- Python SDK scaffolded
- Owner: Tech Writer + Backend

**Infrastructure Weeks 2-3 (5 days - parallel)**

- GitHub Actions deployment pipeline
- Prometheus + Grafana setup
- AWS ECS staging environment
- Owner: DevOps

______________________________________________________________________

### Weeks 4-5 (Sprint 2) - MULTI-SPORT PROOF

**Task 3: Real-Time (Continue)**

- Implementation continues
- Performance optimization
- Load testing with 100+ concurrent streams
- Owner: CV + Backend + DevOps

**Task 4: Running (Start) - IF PARAMETER TEST PASSED**

- Implementation based on Week 1-2 parameter definition
- Build running gait detection
- Landing pattern classifier
- Owner: Biomechanics + Backend

**Task 5: API Docs (Continue)**

- OpenAPI spec finalized
- Python SDK complete
- 1 integration example published
- Webhooks documented
- Owner: Tech Writer + Backend

**Robustness Testing**

- Multi-person scenarios
- Occlusion handling
- Lighting variations
- Owner: QA

______________________________________________________________________

### Weeks 6-7 (Sprint 3) - RELEASE & DEMO

**Task 3: Real-Time (Complete)**

- E2E testing complete
- Performance validated (\<200ms p95)
- Production deployment ready
- Owner: CV + Backend + DevOps

**Task 4: Running (Complete)**

- All validation tests passing
- Landing pattern accuracy >80%
- GCT ±30-50ms documented
- Owner: Biomechanics + Backend + QA

**Task 5: APIs (Complete)**

- OpenAPI spec published
- Python SDK released
- 1 integration example working
- Webhooks tested with multiple clients
- Owner: Tech Writer + Backend

**Staging Deployment**

- All 3 sports deployed to staging
- All APIs functional
- Ready for Month 2 production launch
- Owner: DevOps

______________________________________________________________________

### Weeks 8-9 (Sprint 4) - BETA & HARDENING

**Production Deployment**

- Real-time service live
- API endpoints serving requests
- Monitoring dashboards active
- Owner: DevOps

**Multi-Person Detection (Task 3B - Optional)**

- If resources available, begin Task 3B
- Temporal tracking implementation
- Owner: CV + Backend

**Performance Optimization**

- Latency profiling in production
- Query optimization
- Caching strategies
- Owner: Backend + DevOps

**Beta Program**

- 10-20 coaches testing
- Feedback collection
- Bug fixes
- Owner: Product Manager

______________________________________________________________________

### Weeks 10-11 (Sprint 5) - VALIDATION STUDY

**Lab Validation Study**

- Conduct force plate comparison tests
- Collect CMJ metrics (10+ subjects)
- Collect running metrics (20+ subjects)
- Perform statistical analysis
- Owner: Biomechanics + ML

**Quality Assurance**

- Publish case studies
- Document methodology
- Prepare paper for journal submission
- Owner: Tech Writer + Biomechanics

______________________________________________________________________

### Week 12 (Sprint 6) - CREDIBILITY LAUNCH

**Validation Paper Publication**

- Technical report published
- Case studies shared
- Marketing highlights credibility
- Owner: Tech Writer + Biomechanics

**Partnership Negotiations**

- Begin coaching platform partnerships
- Wearable integrations
- Team management platform integrations
- Owner: Product Manager + Business Dev

**Phase 2 Planning**

- Additional sports (kicking, throwing, swimming)
- Mobile app (iOS/Android)
- Advanced running metrics (stride length, vertical oscillation)
- Cloud infrastructure scaling
- Owner: Project Manager

______________________________________________________________________

## 🎯 Timeline Comparison

| Metric                     | Original | Adjusted (Recommended) | Adjusted (Compressed)     |
| -------------------------- | -------- | ---------------------- | ------------------------- |
| **Total Duration**         | 6 weeks  | 10-12 weeks            | 6 weeks                   |
| **Prep Work**              | None     | Week 0 (critical)      | Skip (risk)               |
| **Go/No-Go Decision**      | No       | Week 1 (latency)       | Week 1 (same)             |
| **Parameter Testing**      | N/A      | Weeks 1-2              | Skip (risk)               |
| **Validation Study**       | N/A      | Weeks 10-11            | Skip (risk)               |
| **Multi-Person Detection** | Task 3   | Task 3B (deferred)     | Task 3 (scope creep risk) |
| **Confidence Level**       | 70%      | 85-90%                 | 50-60%                    |

______________________________________________________________________

## 📋 Success Criteria Changes

### Month 1 (Week 4)

**Original:** Ankle fix + CMJ tests + real-time started
**Adjusted:**

- ✅ Ankle angle: 30°+ increase during concentric
- ✅ Foot_index validated for running use
- ✅ CMJ coverage: 62% → 80%+
- ✅ Running parameters defined + 1-week test complete
- ✅ Infrastructure Week 1-2 complete (Dockerfile, CI/CD)
- ✅ Latency profiling decision made
- ✅ Real-time architecture selected

### Month 2 (Week 8)

**Original:** 3-sport platform, real-time + APIs
**Adjusted:**

- ✅ Real-time: \<200ms latency achieved (or documented as 250ms)
- ✅ Running gait: GCT + cadence + landing pattern working
- ✅ APIs: OpenAPI spec published, Python SDK released, 1 integration example
- ✅ Staging: All 3 sports deployed and tested
- ✅ Infrastructure: Production deployment ready

### Month 3 (Week 12)

**Original:** Production launch ready
**Adjusted:**

- ✅ Production launched (same)
- ✅ Validation study: Lab comparison started
- ✅ Beta: 10-20 coaches testing
- ✅ Partnerships: Discussions underway

### Month 6

**Original:** 3-sport platform, real-time, APIs, partnerships
**Adjusted:**

- ✅ 3-sport platform with validated metrics
- ✅ Real-time capability proven
- ✅ Public APIs accepting requests
- ✅ **NEW:** Validation study published (credibility advantage)
- ✅ **NEW:** Partnership agreements signed
- ✅ **NEW:** "Validated accuracy" positioning

______________________________________________________________________

## 🚀 Decision Points

### Decision 1: Compressed vs Full Timeline

- **Compressed (6 weeks):** Skip prep work, parameter testing, validation study
- **Full (10-12 weeks):** All prep work, parameter testing, credibility study
- **Recommendation:** FULL (credibility enables partnerships + licensing)

### Decision 2: Real-Time Architecture

- **Week 1:** Choose server-only vs hybrid based on latency profiler
- **Recommendation:** Hybrid (\<150ms client-side + fallback server)

### Decision 3: Running Scope

- **Core 3 metrics (MVP):** GCT, cadence, landing pattern
- **Deferred to Phase 2:** Stride length, vertical oscillation
- **Recommendation:** Core 3 for faster Phase 2 launch

______________________________________________________________________

## ⚠️ Risks of Not Making Adjustments

If proceeding with original 6-week timeline:

- 🔴 Technical debt (duplication) compounds (→ 8%+ by Month 3)
- 🔴 Running parameters undefined → accuracy fails at launch
- 🔴 Latency target not validated → may miss \<200ms
- 🔴 No validation study → partnerships difficult
- 🔴 Infrastructure not ready → deployment delayed
- 🔴 Multi-person detection underestimated (cut at last minute)

______________________________________________________________________

## ✅ Benefits of Adjustments

With recommended adjustments:

- ✅ Technical debt eliminated (2.96% → 2.5%)
- ✅ Running parameters defined + tested before implementation
- ✅ Latency validated Week 1 (empirical, not theoretical)
- ✅ Validation study basis for partnership advantage
- ✅ Infrastructure ready Week 3 (no deployment delays)
- ✅ Multi-person detection realistically scoped (Task 3B)
- ✅ Higher confidence (85-90% vs 70%)

______________________________________________________________________

## 📞 Questions?

- **"Why extend timeline?"** → Better credibility, no technical debt, validated accuracy
- **"Can we do it in 6 weeks?"** → Yes, but skip prep work + validation (higher risk)
- **"What's the cost of 10-12 weeks?"** → 4-6 weeks additional development cost
- **"What's the benefit of 10-12 weeks?"** → Partnerships, licensing, premium positioning

______________________________________________________________________

**Status:** Adjustments identified and ready for approval.

**Last Updated:** November 17, 2025
**Requires:** Leadership decision on timeline + scope
