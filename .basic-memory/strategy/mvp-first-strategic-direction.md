---
title: MVP-First Strategic Direction
type: note
permalink: strategy/mvp-first-strategic-direction
tags:
- strategy
- mvp
- roadmap
- pivot
- product-direction
---

# MVP-First Strategic Direction

**Status:** ACTIVE - Adopted November 26, 2025

**Change:** Pivoted from 6-month comprehensive platform roadmap to 3-week MVP-first validation approach.

---

## Why This Matters

The original strategic roadmap (#10-14) planned to build real-time, running analysis, and API integrations in parallel over 6-8 weeks. **Risk:** You might build features customers don't want.

**New approach:** Ship MVP in 3 weeks, gather customer feedback, then decide Phase 2 based on what they actually ask for.

---

## Phase 1: MVP Validation (Weeks 1-3)

**Three Issues Only:**
- Issue #10 (P0): Fix CMJ ankle angle calculation
- Issue #11 (P0): Validate CMJ metrics with phase progression tests
- Issue #12 (P0): Build simple web UI MVP (upload → analyze → export)

**Goal:** Get product in coaches' hands to gather real feedback

**Resources:** 1-2 developers, 3 weeks

---

## Phase 2: Market-Driven Development (Week 4+)

**Features unblock ONLY if customers request them:**

1. **Real-Time Analysis** - IF 3+ coaches ask for live feedback
2. **Running Gait Analysis** - IF 3+ coaches/runners ask for it
3. **API & Integrations** - IF 2+ partners ask for API access

**See:** `MVP_VALIDATION_CHECKPOINTS.md` for explicit unblock criteria

---

## Key Documents

- **Strategic Summary:** `docs/strategy/1-STRATEGIC_SUMMARY.md`
- **Strategic Analysis:** `docs/strategy/2-STRATEGIC_ANALYSIS.md` (market research, still valid)
- **MVP Validation Gates:** `docs/strategy/MVP_VALIDATION_CHECKPOINTS.md`
- **Feedback Collection:** `docs/strategy/MVP_FEEDBACK_COLLECTION.md`

---

## Success Criteria

**Phase 1 Success (Week 3):**
- Accurate, validated CMJ metrics
- Simple web UI deployed and live
- Ready for coach testing

**Phase 2 Decision (Week 4-5):**
- 5-10 coaches using MVP
- Clear market feedback on priorities
- Data to drive Phase 2 decisions

---

## GitHub Issues Status

| Issue | Priority | Phase | Status |
|-------|----------|-------|--------|
| #10 | P0 | Phase 1 | MVP - Fix ankle angle |
| #11 | P0 | Phase 1 | MVP - Validate metrics |
| #12 | P0 | Phase 1 | MVP - Web UI |
| #13 | P2 | Phase 2 | DEFERRED - Unblock if requested |
| #14 | P2 | Phase 2 | DEFERRED - Unblock if requested |

---

## Why MVP-First Is Better

| Aspect | Traditional | MVP-First |
|--------|-----------|-----------|
| Timeline | 6-8 weeks | 3 weeks |
| Dev Cost | 4-5 developers | 1-2 developers |
| Risk | Build wrong features | Learn before investing |
| Feedback | After launch | Week 4 |
| Flexibility | Hard to pivot | Easy to adjust Phase 2 |

---

**Decision Date:** November 26, 2025
**Updated By:** Project Strategic Pivot
**Next Review:** After Week 3 MVP launch
