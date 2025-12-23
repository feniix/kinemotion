---
title: RTMPose Feasibility Evaluation Plan
type: note
permalink: strategy/rtmpose-feasibility-evaluation-plan
tags:
- rtmpose
- rtmlib
- mediapipe
- benchmark
- evaluation
- plan
---

# RTMPose Feasibility Evaluation Plan

## Summary
Comprehensive 5-phase plan to evaluate RTMLib/RTMPose as MediaPipe replacement.

## Key Findings
- [RTMLib BodyWithFeet] [provides] [all 13 kinemotion landmarks via Halpe26 format]
- [Halpe26 indices] [maps] [0=nose, 5/6=shoulders, 11/12=hips, 13/14=knees, 15/16=ankles, 20/21=big_toe, 24/25=heels]
- [MediaPipe inference] [takes] [54.5% of pose tracking time (~4.25s)]

## Phases
1. **Phase 0** (1-2 days): Proof of concept - verify landmark extraction
2. **Phase 1** (2-3 days): Performance benchmarking - FPS, memory, latency
3. **Phase 2** (3-5 days): Physics validation - flight time accuracy using t=√(2h/g)
4. **Phase 3** (2-3 days): Metric agreement - compare downstream metrics
5. **Phase 4** (2-3 days): Robustness - camera angles, jitter, failure modes
6. **Phase 5** (1 day): Decision - replace, hybrid, or stay

## Success Criteria
- Performance: ≥80% of MediaPipe FPS (target: 100%+)
- Flight time MAE: ≤25ms (target: ≤20ms)
- Metric agreement: R² ≥0.95 (target: ≥0.99)

## Timeline
Total: 11-17 days

## Document
Full plan: `docs/research/rtmpose-feasibility-evaluation-plan.md`
