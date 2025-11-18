---
title: strategic-priority-tasks-current-roadmap
type: note
permalink: strategy/strategic-priority-tasks-current-roadmap
tags:
- strategy
- roadmap
- priorities
---

# Strategic Priority Tasks - Current Roadmap

**Goal**: Transform from jump-only to multi-sport, real-time capable platform in 6 months

**Window**: 6-12 months before market consolidates (sports analytics growing 22% CAGR)

## Top 5 Priority Tasks (ROI-ranked)

### Task 1: Fix Ankle Angle Calculation (IMMEDIATE - 2-3 days)
- **Impact**: HIGH | **Effort**: SMALL | **ROI**: 9.0
- **Owner**: Biomechanics Specialist + Backend Dev
- **What**: Use `foot_index` instead of heel for accurate plantarflexion
- **Why**: Establishes credibility for all downstream work
- **Start**: This week
- **Status**: 🟡 PENDING

### Task 2: Expand CMJ Testing (Week 1-2 - 3-4 days)
- **Impact**: MEDIUM | **Effort**: SMALL | **ROI**: 2.0
- **Owner**: QA Engineer + Biomechanics Specialist
- **What**: Add phase progression + physiological bounds validation
- **Why**: Prevent regressions as features added
- **Start**: Week 1
- **Status**: 🟡 PENDING

### Task 3: Real-Time Web Analysis (Week 3-6 - 3-4 weeks)
- **Impact**: VERY HIGH | **Effort**: LARGE | **ROI**: 3.2
- **Owner**: CV Engineer + Backend Dev
- **What**: WebSocket streaming, <200ms latency, live coaching feedback
- **Why**: Market differentiator (proven by Motion-IQ success)
- **Start**: Week 3
- **Architecture Decision**: Server-side MediaPipe (recommended) vs client-side
- **Status**: 🟡 PENDING

### Task 4: Running Gait Analysis (Week 5-7 - 2-3 weeks)
- **Impact**: HIGH | **Effort**: LARGE | **ROI**: 3.2
- **Owner**: Biomechanics Specialist + Backend Dev
- **What**: Core metrics (GCT, cadence, stride) + advanced metrics
- **Why**: 10x larger market than jump sports (25M+ runners in US)
- **Why**: Proves multi-sport architecture extensibility
- **Start**: Week 5 (parallel with Task 3)
- **Depends On**: Phase detection abstraction (must happen before Task 4)
- **Status**: 🟡 PENDING

### Task 5: API Documentation & Integrations (Week 2-7 - 2 weeks)
- **Impact**: HIGH | **Effort**: MEDIUM | **ROI**: 4.5
- **Owner**: Technical Writer + Backend Dev
- **What**: OpenAPI spec, 3 integration examples, webhooks
- **Why**: Enables partnership revenue model
- **Start**: Week 2 (parallel with other work)
- **Pricing Decision**: Freemium hybrid (recommended) vs per-request vs seat-based
- **Status**: 🟡 PENDING

## Execution Timeline

```
SPRINT 0 (Week 1)          FOUNDATION
├─ Task 1: Ankle fix
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
```

## 6-Month Success Criteria

✓ **Accuracy**: Fixed ankle calculation, validated against research
✓ **Scope**: 3+ sports (Drop Jump, CMJ, Running, +1-2 optional)
✓ **Capability**: Real-time web analysis, <200ms latency
✓ **Ecosystem**: Public APIs, SDKs, 3+ integration examples
✓ **Distribution**: Partnership agreements negotiated
✓ **Positioning**: "Accurate, extensible, developer-friendly athletic performance platform"

## Key Decisions Needed

1. Real-Time Architecture: Server-side MediaPipe (recommended) vs client-side
2. Running Metrics: Core 3 vs advanced
3. API Pricing: Freemium hybrid vs per-request vs seat-based
4. Multi-Sport Priority: Running → Throwing → Swimming

## Risk Mitigation

- **Real-time latency misses 200ms**: Early perf testing in week 1 of Task 3
- **Running gait reveals architecture limits**: Phase detection abstraction before Task 4
- **Competitor feature parity**: 3-4 month launch advantage, differentiate on accuracy
- **Coach adoption slow**: Beta program with 10-20 coaches, free tier
