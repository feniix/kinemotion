# MVP-First Strategy - Current Direction

**Date Updated**: November 26, 2025
**Status**: ACTIVE - Guides all development decisions

______________________________________________________________________

## Strategic Pivot

**Changed from:** 6-month comprehensive platform (real-time + running + API in parallel)
**Changed to:** 3-week MVP validation + market-driven Phase 2

______________________________________________________________________

## Phase 1: MVP Validation (Weeks 1-3)

**Three GitHub Issues Only:**

1. **Issue #10 (P0)**: Fix CMJ ankle angle calculation

   - Validate on real video
   - Establish accuracy credibility

1. **Issue #11 (P0)**: Validate CMJ metrics with phase progression tests

   - Add phase progression tests
   - Prove metrics are reproducible

1. **Issue #12 (P0)**: Build simple web UI MVP

   - Upload video → see metrics → export results
   - Get product in coaches' hands
   - Deploy to Vercel/Heroku

**Team**: 1-2 developers
**Timeline**: 3 weeks
**Goal**: Ship MVP, gather customer feedback

______________________________________________________________________

## Phase 2: Market-Driven Development (Week 4+)

**Features unblock ONLY when customers request them:**

### Option A: Real-Time Analysis

- **Unblock if**: 3+ coaches ask for live feedback
- **Timeline**: 3-4 weeks
- **ROI**: 3.2 (market differentiator)

### Option B: Running Gait Analysis

- **Unblock if**: 3+ coaches/runners ask for it
- **Timeline**: 2-3 weeks
- **ROI**: 3.2 (10x market)

### Option C: API & Integrations

- **Unblock if**: 2+ partners ask for API
- **Timeline**: 2 weeks
- **ROI**: 4.5 (partnerships)

### Option D: Iterate MVP

- **Unblock if**: MVP liked but needs UX fixes
- **Timeline**: 1-2 weeks

______________________________________________________________________

## GitHub Issues Status

| Issue | Priority | Phase   | Status             |
| ----- | -------- | ------- | ------------------ |
| #10   | P0       | Phase 1 | Fix ankle angle    |
| #11   | P0       | Phase 1 | Validate metrics   |
| #12   | P0       | Phase 1 | Web UI MVP         |
| #13   | P2       | Phase 2 | DEFERRED - Running |
| #14   | P2       | Phase 2 | DEFERRED - API     |

______________________________________________________________________

## Key Documents

- **Strategic Summary**: `docs/strategy/1-STRATEGIC_SUMMARY.md`
- **Market Analysis**: `docs/strategy/2-STRATEGIC_ANALYSIS.md`
- **MVP Checkpoints**: `docs/strategy/MVP_VALIDATION_CHECKPOINTS.md`
- **Feedback Collection**: `docs/strategy/MVP_FEEDBACK_COLLECTION.md`

______________________________________________________________________

## Why This Approach

| Metric     | Traditional          | MVP-First   |
| ---------- | -------------------- | ----------- |
| Timeline   | 6-8 weeks            | 3 weeks     |
| Developers | 4-5                  | 1-2         |
| Risk       | Build wrong features | Learn first |
| Cost       | High                 | Low         |

______________________________________________________________________

## Success Criteria

**Phase 1 (Week 3)**:

- MVP deployed and live
- Accurate metrics validated
- Ready for coach testing

**Phase 2 Decision (Week 4-5)**:

- 5-10 coaches tested MVP
- Clear market feedback
- Decide next priority with data

______________________________________________________________________

## Next Immediate Actions

1. Start Issue #10 (ankle angle fix + validation)
1. Start Issue #11 (metrics tests)
1. Start Issue #12 (web UI)
1. Week 4: Recruit coaches for MVP testing
1. Week 5: Gather feedback, make Phase 2 decision
