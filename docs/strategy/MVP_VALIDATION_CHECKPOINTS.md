# MVP Validation Checkpoints & Phase 2 Decision Gates

**Purpose:** Track MVP progress and define explicit criteria for activating Phase 2 features (#13 and #14).

**Document Date:** November 26, 2025

______________________________________________________________________

## Checkpoint 1: Week 3 (MVP Shipped & Live)

**Go/No-Go Criteria for MVP Launch:**

- [ ] Issue #10 complete: Ankle angle fix validated on real CMJ video
- [ ] Issue #11 complete: Phase progression tests passing (3-5 tests)
- [ ] Issue #12 complete: Web UI deployed and publicly accessible
- [ ] Backend responds to analysis requests without errors
- [ ] Frontend displays metrics clearly and can export results
- [ ] Documentation: Setup guide for coaches using the MVP

**Deliverable:** MVP ready for coach testing

**Decision:** Go to Checkpoint 2 (market validation) or fix blockers

______________________________________________________________________

## Checkpoint 2: Week 4-5 (Market Validation & Feedback Collection)

**Objective:** Get 5-10 coaches using MVP and collecting structured feedback

**Activities:**

1. **Recruit Test Coaches**

   - [ ] Identify and contact 5-10 coaches
   - [ ] Get them using the MVP (send URL + short tutorial)
   - [ ] Encourage 3-5 test videos per coach

1. **Collect Structured Feedback**

   - [ ] Use feedback collection script (see: `MVP_FEEDBACK_COLLECTION.md`)
   - [ ] Record responses to 5 key questions
   - [ ] Document feature requests and pain points
   - [ ] Track: "Would you pay for this?"

1. **Monitor MVP Stability**

   - [ ] Track error rates and crashes
   - [ ] Monitor video upload success rate
   - [ ] Measure average analysis time
   - [ ] Fix any bugs discovered

**Deliverable:** Feedback data from 5-10 coaches

**Success Criteria:**

- Coaches provide actionable feedback
- MVP remains stable under real usage
- At least 3 coaches give clear feature requests

______________________________________________________________________

## Decision Gate 1: Phase 2 Feature Prioritization (End of Week 5)

**Based on MVP Feedback, Decide Which Phase 2 Feature to Build:**

### Option A: Real-Time Web Analysis (WebSockets, \<200ms latency)

**Unblock Criteria:**

- [ ] 3+ coaches explicitly say: "I need real-time feedback"
- [ ] Evidence: Live feedback would change their coaching decisions
- [ ] Market research: Motion-IQ success validates this market exists

**Timeline if Unblocked:** Weeks 6-9 (3-4 weeks)
**Issue:** #12v2 (Real-Time Web Analysis)
**Team:** Computer Vision Engineer + Backend Dev
**ROI:** 3.2 (market differentiator)

______________________________________________________________________

### Option B: Running Gait Analysis (GCT, cadence, stride length)

**Unblock Criteria:**

- [ ] 3+ coaches or runners explicitly say: "I need running analysis"
- [ ] Evidence: Willingness to use/test running features
- [ ] Market research: 25M+ runners in US validates TAM

**Timeline if Unblocked:** Weeks 6-8 (2-3 weeks)
**Issue:** #13 (Running Gait Analysis)
**Team:** Biomechanics Specialist + Backend Dev
**ROI:** 3.2 (10x market TAM)

______________________________________________________________________

### Option C: API & Integration Framework (OpenAPI, webhooks, SDKs)

**Unblock Criteria:**

- [ ] 2+ integration partners explicitly request: "Can we build on your API?"
- [ ] Evidence: Specific partnerships identified (e.g., Vimeo Coach, coaching app)
- [ ] Use case: Clear integration scenarios that drive adoption

**Timeline if Unblocked:** Weeks 6-8 (2 weeks)
**Issue:** #14 (API Documentation & Integration Framework)
**Team:** Technical Writer + Backend Dev
**ROI:** 4.5 (enables partnership revenue)

______________________________________________________________________

### Option D: Iterate on MVP (UI, UX, accuracy improvements)

**Criteria:**

- [ ] Coaches like the concept but found UX issues
- [ ] Metrics not trusted yet (need more validation)
- [ ] Better to polish MVP before building new features

**Timeline if Chosen:** Weeks 6-7 (1-2 weeks)
**Team:** Frontend Dev + Biomechanics Specialist
**ROI:** Ensures MVP success before expansion

______________________________________________________________________

## Decision Documentation

**Use this template to record the decision:**

```markdown
## Phase 2 Decision: [Date]

**Feedback Summary:**
- Coach 1: [Feature request / pain point]
- Coach 2: [Feature request / pain point]
- ...

**Feature Requests Frequency:**
- Real-Time: [X coaches requested]
- Running: [X coaches requested]
- API: [X coaches/partners requested]
- Other: [X coaches requested]

**Willingness to Pay:**
- Free tier only: [X coaches]
- Willing to pay $50-100/month: [X coaches]
- Willing to pay $500+/month: [X coaches]

**Recommendation:** Prioritize [Option A/B/C/D]

**Rationale:**
- [Why this option has strongest customer demand]
- [Which coaches/partners specifically requested it]

**Phase 2 Planning:**
- Assign team: [Names]
- Start date: Week 6
- Target launch: [Date]
```

______________________________________________________________________

## Long-Term Vision (Months 2-6, Informed by MVP)

**After Phase 2 Unblock Decision:**

**Month 2 Success State:**

- [ ] Phase 2 feature shipped and working
- [ ] 20+ coaches actively using MVP + Phase 2 feature
- [ ] Early revenue signals (if applicable)

**Month 3-4 Success State:**

- [ ] Phase 2 feature validated with real users
- [ ] Plan Phase 3 based on Phase 2 learnings
- [ ] Consider which sport to add next (or deepen CMJ/DJump)

**Month 5-6 Success State:**

- [ ] Platform expansion begins (if market shows demand)
- [ ] Revenue model finalized
- [ ] Partnerships discussed/signed

______________________________________________________________________

## Why This Approach?

**Traditional:** Build everything → ship comprehensive platform → hope people want it

- Risk: 6-8 weeks + 4-5 developers on features customers don't want
- Outcome: Wasted resources, unclear market fit

**MVP-First:** Ship MVP → learn from customers → build what they ask for

- Risk: Lower (3-week MVP sunk cost)
- Outcome: Phase 2 driven by real demand, not assumptions

**Result:** Better ROI, faster feedback loop, lower waste

______________________________________________________________________

**Document Status:** ACTIVE - Updated as feedback is collected

**Next Update:** After Week 4 coach testing (Week 5 decision gate)

**Maintained By:** Project Manager / Product Lead

______________________________________________________________________

## References

- GitHub Issues: #10, #11, #12, #13, #14
- MVP Feedback Collection: `MVP_FEEDBACK_COLLECTION.md`
- Strategic Summary: `1-STRATEGIC_SUMMARY.md`
- Market Analysis: `2-STRATEGIC_ANALYSIS.md`
