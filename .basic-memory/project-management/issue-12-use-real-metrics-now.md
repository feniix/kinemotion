---
title: Issue #12 - Use Real Metrics NOW (Not Mocked)
type: note
permalink: project-management/issue-12-use-real-metrics-now
tags:
  - issue-12
  - web-ui
  - mvp-strategy
  - real-data
---

# Issue #12: Use Real Metrics NOW (Not Mocked)

## Key Decision

**Use the current CMJ/Drop Jump implementation immediately. Don't mock.**

This means:
- ✅ MVP ships with real metrics from day 1
- ✅ Coaches test with real data (not fake numbers)
- ✅ Full stack testable without waiting for #10
- ✅ Feedback based on actual performance
- ✅ Fix/refine metrics later when #10 is complete

---

## Why This Is Better Than Mocking

| Approach | Timeline | Data Quality | Feedback Value |
|----------|----------|---|---|
| **Mock metrics** | ~6 days | Fake | "UI looks nice" (not valuable) |
| **Real metrics NOW** | ~6 days | Real (current) | "Metrics seem off" or "This is useful!" (valuable) |
| **Real metrics (wait for #10)** | ~3+ weeks | Perfect (future) | Too late, MVP stalled |

**We choose:** Real metrics NOW ✅

---

## Implementation

### Backend Uses Real Functions

```python
from kinemotion import process_cmj_video, process_dropjump_video

# NOT mocked - uses actual implementation
metrics = process_cmj_video(video_path, quality="balanced")
# OR
metrics = process_dropjump_video(video_path, quality="balanced")
```

---

## Future Updates (Decoupled)

When #10 is complete (CMJ ankle angle fix):

1. **Update** `backend/pyproject.toml` with new kinemotion version
2. **Redeploy** backend (30 minutes)
3. **Metrics automatically improve** - no code changes

---

## Advantages of This Approach

✅ **Faster MVP**: No waiting for #10 to complete
✅ **Real data**: Coaches test with actual analysis
✅ **Better feedback**: "Metrics seem off" is actionable
✅ **Decoupled**: #12 doesn't block on #10
✅ **Flexible**: Can iterate quickly based on feedback
✅ **Low risk**: Current implementation works, just not perfect

---

## What Coaches Will See

**Real metrics today:**
- CMJ: Jump height, flight time, countermovement depth, triple extension
- Drop Jump: Ground contact time, flight time, reactive strength index
- Joint angles: Ankle, knee, hip (ankle angle may be 5-10° off - will be fixed with #10)

**Feedback we'll get:**
- "Are these numbers reasonable?"
- "What do the angles mean?"
- "This is useful for my coaching!"

---

## When Metrics Improve (#10 Complete)

Coach sees:
- Better ankle angle calculation
- More accurate triple extension analysis
- Same UI/API (seamless upgrade)
- "Wow, the metrics improved!"

---

## Risk Assessment

**Risk: Metrics are "wrong" and hurt credibility**

Mitigation:
- Include in UI: "MVP metrics for testing - expect refinements"
- When #10 fixes it, show: "Improved accuracy with recent update"

**Actual risk is LOW** because:
- Current implementation is validated (Issue #11 tests it)
- Only ankle angle is known to be ~5-10° off
- Other metrics are accurate
- Coaches understand "MVP" = works but refining
