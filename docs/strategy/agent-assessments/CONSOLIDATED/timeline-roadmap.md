# Timeline & Roadmap Visualization

**Date:** November 17, 2025 | **Status:** Ready for Execution | **Duration:** 10-12 weeks

______________________________________________________________________

## 📅 RECOMMENDED TIMELINE (10-12 Weeks)

### High-Level Sprint Map

```
SPRINT -1: WEEK 0 (This Week)
├─ Refactoring Sprint (5-6 days)
├─ Parameter Definition (3-4 days)
├─ Infrastructure Planning (2-3 days)
└─ Validation Study Planning (2 days)
   GATE: Week 0 complete → Proceed to Week 1

SPRINT 0: WEEK 1 (Foundation + Go/No-Go)
├─ Task 1: Ankle Fix (2-3 days)
├─ Task 2: CMJ Tests (Start, 3-4 days)
├─ Latency Profiler Build (3 days) 🎯 GO/NO-GO DECISION
├─ Infrastructure Week 1 (5 days, parallel)
└─ Parameter Testing (3 days, parallel)
   GATE: Latency decision made → Week 2+ direction decided

SPRINT 1: WEEKS 2-3 (Platform Foundation)
├─ Task 2: CMJ Testing (Complete)
├─ Task 3: Real-Time (Start - architecture confirmed)
├─ Task 5: API Docs (Start)
└─ Infrastructure Weeks 2-3 (parallel)
   GATE: CMJ tests at 80%+, real-time architecture clear

SPRINT 2: WEEKS 4-5 (Multi-Sport Proof)
├─ Task 3: Real-Time (Continue)
├─ Task 4: Running Gait (Start - if parameters passed)
├─ Task 5: API Docs (Continue)
└─ Robustness Testing (parallel)
   GATE: Real-time latency validation, running parameters confirmed

SPRINT 3: WEEKS 6-7 (Release & Demo)
├─ Task 3: Real-Time (Complete)
├─ Task 4: Running (Complete)
├─ Task 5: APIs (Complete)
└─ Staging Deployment Complete
   GATE: All tests passing, staging ready for Month 2 production

SPRINT 4: WEEKS 8-9 (Beta & Hardening)
├─ Production Deployment
├─ Beta Program (10-20 coaches)
├─ Multi-Person Detection (Optional Task 3B)
└─ Performance Optimization
   GATE: Production stable, <1% error rate

SPRINT 5: WEEKS 10-11 (Validation Study)
├─ Lab: Force Plate Comparison Testing
├─ Data Collection & Analysis
└─ Case Studies Development
   GATE: Validation paper ready for review

SPRINT 6: WEEK 12 (Credibility Launch)
├─ Validation Paper Publication
├─ Marketing Launch
└─ Partnership Negotiations
   GATE: "Validated accuracy" positioning live

TOTAL: 12 weeks
```

______________________________________________________________________

## 📊 DETAILED WEEK-BY-WEEK BREAKDOWN

### WEEK 0 (CRITICAL PREP - THIS WEEK)

**Monday-Wednesday: Refactoring Sprint**

- Backend Developer: Extract MotionAnalyzer base class
- Extract PhaseDetector abstraction
- Extract StreamingPoseProcessor (80 lines)
- Extract MetricsCalculator interface
- All existing tests passing
- **Deadline:** Refactoring complete by COB Wednesday
- **Success:** 700 lines duplication eliminated, 2.96% → 2.5%

**Monday-Thursday: Parameter Definition Sprint** (Parallel)

- ML + Biomechanics: Define running quality presets
- Create validation framework
- Design benchmark dataset
- Build 1-week prototype test plan
- **Deadline:** Parameters documented by EOD Thursday
- **Success:** All running parameters specified (confidence, thresholds, filters)

**Monday-Wednesday: Infrastructure Planning** (Parallel)

- DevOps: Identify tools (Docker, Locust, Prometheus, Grafana)
- Design AWS ECS Fargate architecture
- Create deployment plan
- Identify resource needs
- **Deadline:** Plan finalized by Wednesday
- **Success:** Infrastructure Week 1 sprint ready to go

**Tuesday: Validation Study Planning**

- Biomechanics + Project Manager: Contact 3 potential labs
- Draft validation study protocol
- Budget validation ($5-10K lab time)
- Reserve Month 3-4 lab slots
- **Deadline:** Labs contacted, slots reserved by Friday
- **Success:** Lab partnership in progress

**Friday: LEADERSHIP DECISIONS**

- Stakeholder review of strategic documents
- Approve 3 decisions (timeline, real-time arch, running scope)
- Assign all task owners
- Approve budgets
- **Deadline:** Decisions by EOB Friday
- **Success:** All approvals locked for Monday kickoff

______________________________________________________________________

### WEEK 1 (FOUNDATION + GO/NO-GO DECISIONS)

**Daily Standup:** 15 min sync, track progress vs milestones

**Task 1: Ankle Fix & Validation** (2-3 days)

- Biomechanics + Backend Dev
- Fix ankle calculation (heel → foot_index)
- Test foot_index visibility on 10 real CMJ videos (2 hours)
- Deploy with fallback to heel
- All tests passing
- **Deadline:** Wednesday EOD
- **Success:** Ankle angles increase 30°+ during concentric

**Task 2: CMJ Testing (Start)** (3-4 days)

- QA Engineer + Biomechanics
- Create 40-50 new test cases
- Phase progression tests
- Physiological bounds tests
- Ankle angle progression tests
- Real video sample validation
- **Deadline:** Thursday EOD (25% of tests done, momentum clear)
- **Success:** 20+ tests written and passing

**Latency Profiler Build** (3 days) 🎯 **GO/NO-GO DECISION**

- CV Engineer + DevOps
- Monday-Tuesday: Build profiler (measure empirical latency)
- Tuesday-Wednesday: Test server vs client vs hybrid
- Thursday: Analysis + presentation
- **Thursday EOD:** GO/NO-GO DECISION
  - Option A (Server-only): 250-350ms → Proceed with server
  - Option B (Hybrid): \<150ms → Proceed with hybrid
  - Go/No-Go: \<200ms achievable? YES → proceed, NO → document 250ms
- **Deadline:** Decision finalized Thursday
- **Success:** Latency measured empirically, architecture chosen

**Infrastructure Week 1** (Parallel, 5 days)

- DevOps Engineer (60% FTE)
- Monday-Tuesday: Dockerfile + Docker Compose (local dev stack)
- Tuesday-Wednesday: GitHub Actions build workflow
- Wednesday-Thursday: AWS ECS initial setup (IAM, VPC, networking)
- Thursday: Basic Locust load testing framework scaffolded
- **Deadline:** Thursday EOD
- **Success:** Docker image builds, CI/CD build step works

**Parameter Testing Week 1** (Parallel, 3 days)

- ML + Biomechanics
- Monday: Define running presets (confidence, thresholds)
- Tuesday-Wednesday: Build 1-week prototype test
- Thursday: Prototype validation test starts
- **Deadline:** Thursday EOD (prototype test starting)
- **Success:** Parameters defined, 1-week test in progress

**WEEK 1 GATE CHECK:**

- ✅ Task 1 complete (ankle fix validated)
- ✅ Task 2 momentum clear (25% tests done)
- ✅ Latency profiler decision made (architecture chosen)
- ✅ Infrastructure Week 1 complete (Docker + CI/CD + AWS started)
- ✅ Parameters defined and 1-week test started

______________________________________________________________________

### WEEKS 2-3 (PLATFORM FOUNDATION)

**Task 2: CMJ Testing (Complete)**

- QA Engineer + Biomechanics
- Weeks 2-3: Write remaining 20-30 tests
- Phase progression validation
- Physiological bounds testing
- Integration with ankle fix validation
- **Target:** 62% → 80%+ coverage
- **Deadline:** Friday Week 3 EOD
- **Success:** 80%+ coverage, all tests passing

**Task 3: Real-Time (Start)**

- CV Engineer + Backend Dev + DevOps
- Week 2: Architecture implementation based on Week 1 decision
  - If Server-only: Start WebSocket handler + server processing
  - If Hybrid: Start TensorFlow.js + server fallback
- Week 3: Continue implementation + testing
- **Deadline:** Week 3 EOD (50% implementation)
- **Success:** Basic real-time metrics updating (CMJ height in browser)

**Task 5: API Docs (Start)**

- Tech Writer + Backend Dev
- Week 2: OpenAPI 3.1 spec drafted + reviewed
- Week 3: 1 integration example started (coaching app)
- **Deadline:** Week 3 EOD (OpenAPI spec + example scaffolded)
- **Success:** OpenAPI published, example in progress

**Infrastructure Weeks 2-3** (Parallel)

- DevOps Engineer (60% FTE)
- Week 2: GitHub Actions deployment pipeline (build → push to ECR)
- Week 3: AWS ECS staging environment deployed
- Prometheus + Grafana setup started
- **Deadline:** Week 3 EOD (staging environment ready)
- **Success:** Deploy button works from GitHub Actions

**Parameter Testing Weeks 2-3** (Parallel)

- ML + Biomechanics
- Week 2: Continue 1-week prototype test
- Week 3: Results analyzed, parameters validated or adjusted
- **Deadline:** Week 3 EOD (parameters confirmed or adjusted)
- **Success:** Running parameters ready for Week 5 Task 4

**WEEKS 2-3 GATE CHECK:**

- ✅ Task 2 at 50%+ (CMJ tests halfway)
- ✅ Task 3 started (real-time prototype working)
- ✅ Task 5 started (OpenAPI spec done)
- ✅ Infrastructure staging ready (can deploy)
- ✅ Parameters tested and validated

______________________________________________________________________

### WEEKS 4-5 (MULTI-SPORT PROOF)

**Task 2: CMJ Testing (Complete)**

- Complete by Week 4 Monday
- **Success:** 80%+ coverage locked

**Task 3: Real-Time (Continue)**

- CV Engineer + Backend Dev + DevOps
- Week 4: Full real-time implementation, load testing
- Week 5: Performance optimization, bug fixes
- Latency profiling in staging (measure actual performance)
- Load test: 10 → 50 → 100 concurrent streams
- **Deadline:** Week 5 EOD (implementation feature-complete)
- **Success:** \<200ms latency validated (or 250ms documented)

**Task 4: Running Gait (Start)** (If parameters passed Week 3)

- Biomechanics + Backend Dev + ML
- Week 4: Build running phase detection
- Week 5: Build landing pattern classifier + cadence metrics
- **Deadline:** Week 5 EOD (basic implementation)
- **Success:** Core 3 metrics (GCT, cadence, landing) working

**Task 5: API Docs (Continue)**

- Tech Writer + Backend Dev
- Week 4: Complete 1 integration example (coaching app)
- Week 5: Python SDK completed, API reference updated
- **Deadline:** Week 5 EOD (MVP scope, optional examples deferred)
- **Success:** OpenAPI + Python SDK + 1 example working

**Robustness Testing** (Parallel weeks 4-5)

- QA Engineer + ML
- Test multi-person scenarios (not detecting, OK for MVP)
- Test occlusion handling (hands occluding legs)
- Test lighting variations
- Test camera angles (30-45° lateral, ideal)
- **Deadline:** Week 5 EOD (robustness report)
- **Success:** Known issues documented

**Infrastructure Weeks 4-5** (Parallel)

- DevOps Engineer (60% FTE)
- Week 4: Prometheus + Grafana fully operational
- Week 4-5: Performance tuning + monitoring dashboards
- **Deadline:** Week 5 EOD (monitoring live)
- **Success:** Real-time service metrics tracked

**WEEKS 4-5 GATE CHECK:**

- ✅ Task 3 performance validated (\<200ms or documented)
- ✅ Task 4 basic implementation complete (if parameters OK)
- ✅ Task 5 MVP scope complete (OpenAPI + SDK + 1 example)
- ✅ Robustness testing complete
- ✅ Monitoring live in staging

______________________________________________________________________

### WEEKS 6-7 (RELEASE & DEMO)

**Task 3: Real-Time (Complete)**

- Final testing + bug fixes
- E2E testing (video capture → metrics display → live updates)
- Performance benchmarks finalized
- Demo video recorded (real-time showing \<200ms)
- **Deadline:** Week 6 EOD (ready for staging → production)
- **Success:** All tests passing, \<1% error rate, latency documented

**Task 4: Running (Complete)**

- Final validation tests
- Edge case testing (stairs, hills, sprinting)
- Accuracy benchmarks documented (GCT ±30-50ms, cadence ±3)
- **Deadline:** Week 6 EOD (ready for validation)
- **Success:** All running tests passing

**Task 5: APIs (Complete)**

- Final OpenAPI review
- Python SDK documentation complete
- 1 integration example fully working
- Webhooks tested with multiple clients
- Rate limiting + API key management working
- **Deadline:** Week 6 EOD (APIs live)
- **Success:** Public API documentation published

**Staging Deployment**

- DevOps + Backend + CV
- Week 6: All 3 sports deployed to staging
- Week 7: Production deployment dry run (staging → production)
- **Deadline:** Week 7 EOD (ready to flip switch)
- **Success:** Production environment configured, rollback plan ready

**WEEKS 6-7 GATE CHECK:**

- ✅ All 3 tasks (1/2/3/4/5) feature-complete
- ✅ All tests passing (CMJ 80%+, real-time validated, running tested)
- ✅ APIs live and responding
- ✅ Staging deployment successful
- ✅ Ready for Month 2 production launch

______________________________________________________________________

### WEEKS 8-9 (BETA & HARDENING)

**Production Deployment** (Week 8)

- DevOps: Execute production deployment
- Canary: 5% traffic → 25% → 100%
- Monitoring: Real-time dashboards active
- **Deadline:** Week 8 Wednesday (production live)
- **Success:** Zero downtime deployment, \<1% error rate

**Beta Program** (Weeks 8-9)

- Project Manager: 10-20 coaches testing real-time feature
- Feedback collection (usability, accuracy, feature requests)
- Bug triage + hotfix
- **Deadline:** Week 9 Friday (beta feedback collected)
- **Success:** Major issues found + fixed, feedback documented

**Optional: Multi-Person Detection (Task 3B)**

- CV Engineer: Begin if resources available
- Temporal tracking implementation (Hungarian algorithm)
- Track multiple athletes in frame
- **Deadline:** Week 9 EOD (architecture + prototype)
- **Success:** Multi-person working in dev environment

**Performance Optimization** (Weeks 8-9)

- Backend + DevOps: Production performance tuning
- Query optimization
- Caching strategies
- Latency profiling in production
- **Deadline:** Week 9 EOD (p95 latency \<200ms or documented)
- **Success:** Performance meets or exceeds expectations

______________________________________________________________________

### WEEKS 10-11 (VALIDATION STUDY)

**Lab: Force Plate Comparison** (Weeks 10-11)

- Biomechanics: Conduct testing with lab partner
- CMJ data collection (10+ subjects)
- Running data collection (20+ subjects)
- Ground truth comparison (Kinemotion vs force plate)
- **Deadline:** Week 10 EOD (data collection complete)
- **Success:** Raw data collected, no issues

**Analysis & Reporting** (Week 11)

- ML + Biomechanics: Statistical analysis
- Calculate accuracy metrics (MAE, ICC, Bland-Altman plots)
- Case studies development
- Paper draft writing
- **Deadline:** Week 11 Friday (draft paper ready)
- **Success:** 4-6 page technical report with findings

______________________________________________________________________

### WEEK 12 (CREDIBILITY LAUNCH)

**Validation Paper Publication**

- Tech Writer + Biomechanics: Final review + publication
- Publish technical report
- Case studies shared
- Press release / marketing announcement
- **Deadline:** Week 12 Wednesday (live)
- **Success:** "Validated accuracy" positioning launched

**Partnership Negotiations**

- Business Development: Begin partnerships
- Coaching platforms (Vimeo Coach, Synq, Catalyst)
- Wearables (Oura, Whoop, Apple Health)
- Team management (TeamSnap, Hudl)
- **Deadline:** Week 12+ (ongoing)
- **Success:** 2-3 partnerships in negotiations

**Phase 2 Planning**

- Project Manager: Plan next phase
- Additional sports (kicking, throwing, swimming)
- Mobile app (iOS/Android)
- Advanced running metrics
- Cloud infrastructure scaling
- **Deadline:** Week 12 Friday (Phase 2 roadmap)
- **Success:** Clear product roadmap next 6 months

______________________________________________________________________

## 📊 MILESTONE SUMMARY

| Week      | Sprint | Key Milestone                 | Gate                | Owner        |
| --------- | ------ | ----------------------------- | ------------------- | ------------ |
| **0**     | Prep   | Decisions approved            | Leadership sign-off | PM           |
| **1**     | S0     | Latency profiler decision     | Architecture locked | CV + DevOps  |
| **2-3**   | S1     | CMJ 80%+, real-time started   | Platform foundation | QA + Backend |
| **4-5**   | S2     | Running parameters validated  | Multi-sport proof   | ML + Bio     |
| **6-7**   | S3     | All 3 sports complete         | Production ready    | All          |
| **8-9**   | S4     | Production live, beta started | Hardening phase     | DevOps + PM  |
| **10-11** | S5     | Validation study complete     | Credibility         | Bio + ML     |
| **12**    | S6     | Partnerships launched         | Long-term success   | All          |

______________________________________________________________________

## 🎯 COMPRESSED TIMELINE ALTERNATIVE (6 Weeks - Higher Risk)

If timeline must be 6 weeks:

```
WEEK 0: Skip refactoring, parameter testing, validation planning
  - Risk: Technical debt compounds (2.96% → 8%+)
  - Risk: Running parameters undefined (accuracy?)
  - Risk: No validation study planned

WEEK 1: Task 1 + Task 2 (no latency profiling)
  - Risk: Latency target not validated
  - Risk: Architecture guess instead of measure

WEEKS 2-4: Task 3 + Task 4 + Task 5 (parallel)
  - Risk: Too much in parallel, quality at risk
  - Risk: Testing infrastructure underestimated

WEEKS 5-6: Finish + deploy
  - Risk: Deployment under-tested
  - Risk: No hardening time

OUTCOME:
  - Faster market launch (1 month sooner)
  - BUT: Accuracy issues likely (running parameters undefined)
  - BUT: No validation study (partnerships hard)
  - BUT: Technical debt (multi-sport hard to add)
  - Success probability: 50-60% (high risk)
```

**Recommendation:** Stick with 10-12 week timeline for credibility + sustainability

______________________________________________________________________

## 📈 Success Metrics by Period

### Month 1 (Weeks 1-4)

- ✅ Ankle fix deployed (accuracy improved 5-10° → 30°+)
- ✅ CMJ tests 80%+ coverage
- ✅ Running parameters defined + tested
- ✅ Real-time latency validated (\<200ms or \<250ms documented)
- ✅ Infrastructure Weeks 1-2 complete

### Month 2 (Weeks 5-8)

- ✅ Real-time running gait analysis working
- ✅ APIs live and responding
- ✅ 3-sport platform operational
- ✅ Staging → Production deployment successful
- ✅ Beta program (10-20 coaches) started

### Month 3 (Weeks 9-12)

- ✅ Production stable (\<1% error rate, 99%+ uptime)
- ✅ Validation study published (force plate comparison)
- ✅ "Validated accuracy" positioning live
- ✅ Partnerships in negotiations (coaching, wearables, team mgmt)
- ✅ Phase 2 roadmap clear (additional sports, mobile app)

______________________________________________________________________

## 📞 Questions?

- **"Why does it take 12 weeks?"** → Proper refactoring (Week 0), parameter testing (Weeks 1-2), validation study (Weeks 10-11)
- **"Can we do it in 6 weeks?"** → Yes, but skip validation → partnerships harder
- **"What's the critical path?"** → Refactoring (Week 0) → Latency decision (Week 1) → Infrastructure (Weeks 1-3) → Validation (Weeks 10-11)
- **"What could delay us?"** → See risk register

______________________________________________________________________

**Status:** Timeline finalized and ready for execution.

**Last Updated:** November 17, 2025
**Next Step:** Kickoff meeting Week 0 (this week)
