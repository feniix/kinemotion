---
title: Pose2Sim Migration Evaluation and Strategy
type: note
permalink: strategy/pose2-sim-migration-evaluation-and-strategy
tags:
- pose2sim
- migration-strategy
- mvp-first
- cost-benefit-analysis
- phased-approach
---

# Pose2Sim Migration Evaluation and Strategy

**Date:** 2025-12-08
**Analysis Method:** Sequential thinking + Multi-tool research (exa, ref, serena, basic-memory)
**Decision:** DEFER to Phase 2+ (post-MVP)

---

## Executive Summary

**Recommendation: DO NOT migrate to Pose2Sim during MVP phase (Weeks 1-3)**

Pose2Sim would provide 67-73% accuracy improvement but requires:
- 2-4 weeks integration time (delays MVP launch)
- $2,000-5,000 hardware investment (premature before market validation)
- Multi-camera setup (adds complexity for users)
- Batch processing only (may conflict with real-time needs)

**Strategic timing is wrong.** Focus on MVP launch, gather user feedback, then reassess based on validated market needs.

---

## Current State Analysis

### MediaPipe Monocular (Kinemotion Current)
- **Joint angle error:** ~10-15°
- **Position RMSE:** 56mm
- **Ankle/knee visibility:** 18-27% (lateral view, occlusion issues)
- **Cost:** $0 (single camera/smartphone)
- **Setup time:** Minutes
- **Processing:** Real-time capable
- **Architecture:** PoseTracker class wraps MediaPipe, processes frames sequentially

### Recent Optimizations (Dec 2025)
- 92% improvement in detection accuracy (within 5 frames target)
- Fixed non-deterministic analysis (temporal averaging)
- 45° oblique angle validated as optimal for MediaPipe

---

## Pose2Sim Technical Analysis

### Accuracy Improvements
| Metric | Current (MediaPipe) | Pose2Sim | Improvement |
|--------|-------------------|----------|-------------|
| Joint angle error | ~10-15° | 3-4° | **67-73%** ↓ |
| Position RMSE | 56mm | 30-40mm | **29-46%** ↓ |
| Ankle/knee visibility | 18-27% | 80-95% | **3-5x** ↑ |
| CMC correlation | Not available | 0.90-0.98 | Research-grade |

### Technical Requirements
- **Hardware:** 4-8 RGB cameras (1080p+, 60-240 Hz)
- **Sync:** Hardware preferred, software acceptable
- **Calibration:** ChArUco board, intrinsic + extrinsic
- **Compute:** GPU recommended but NOT required (CPU works, 2-3x slower)
- **Software:** Python, OpenSim, pose2sim package

### Integration Architecture

**Pose2Sim Pipeline:**
```python
from Pose2Sim import Pose2Sim

Pose2Sim.calibration()      # Camera calibration
Pose2Sim.poseEstimation()   # 2D pose (uses OpenPose/MediaPipe/AlphaPose)
Pose2Sim.triangulation()    # 3D reconstruction
Pose2Sim.filtering()        # Butterworth smoothing (6 Hz)
Pose2Sim.kinematics()       # OpenSim inverse kinematics
```

**Kinemotion Integration Points:**
1. Replace `PoseTracker` class (src/kinemotion/core/pose.py)
2. Modify `process_dropjump_video()` / `process_cmj_video()` (src/kinemotion/api.py)
3. Keep existing: smoothing, signed velocity, backward search, analysis logic
4. Add: multi-camera input handling, calibration management, OpenSim output parsing

---

## Cost-Benefit Analysis

### Investment Required
| Item | Cost | Time |
|------|------|------|
| 4-8 RGB cameras (1080p, 60-120 Hz) | $2,000-3,000 | 1 week |
| Optional GPU for faster 2D pose | $1,000-2,000 | N/A |
| Integration development | $0 (internal) | 2-4 weeks |
| Testing & validation | $0 (internal) | 1 week |
| **Total** | **$2,000-5,000** | **3-5 weeks** |

### Benefits
- **Accuracy:** Research-grade (publishable validation studies)
- **Credibility:** Gold-standard validation vs Vicon/Qualisys
- **Market differentiation:** Can claim highest accuracy in market
- **Biomechanical validity:** OpenSim constraints ensure physically plausible poses
- **Multi-view:** Eliminates occlusion problems (45° + frontal + lateral)

### Risks
- **Complexity:** Multi-camera setup increases user friction
- **Cost barrier:** $2-5k hardware may limit adoption
- **No real-time:** Batch processing only (if real-time needed, Pose2Sim won't work)
- **Integration delay:** 3-5 weeks delays MVP launch and market feedback
- **Premature optimization:** Unknown if accuracy is validated user pain point

---

## Migration Strategy Options

### Option A: Full Replacement (NOT RECOMMENDED NOW)
**Timeline:** 3-5 weeks
**Cost:** $2,000-5,000
**Risk:** High (delays MVP, unknown market need)

Replace PoseTracker entirely with Pose2Sim pipeline. Requires multi-camera for all users.

### Option B: Hybrid Architecture (RECOMMENDED IF MIGRATING)
**Timeline:** 4-6 weeks
**Cost:** $2,000-5,000
**Risk:** Medium (backward compatible)

- Keep MediaPipe for single-camera/real-time path
- Add Pose2Sim for research-grade offline analysis
- Both paths converge at analysis stage (shared smoothing, metrics)
- Users can choose based on accuracy vs convenience needs

### Option C: OpenCap Integration (LOW-RISK TEST)
**Timeline:** Days to 1 week
**Cost:** $0 (use smartphones)
**Risk:** Low (easy to test, no commitment)

- Keep MediaPipe as primary
- Add OpenCap offline processing option
- Parse OpenCap output → feed to existing analysis
- Test accuracy improvement before committing to Pose2Sim

---

## Go/No-Go Decision Framework

**Phase 1 (MVP - Weeks 1-3): GO = 0/5 ❌**

| Criteria | Status | Weight |
|----------|--------|--------|
| Is MediaPipe accuracy blocking adoption? | ❌ NO (no users yet) | Critical |
| User feedback demanding better accuracy? | ❌ NO (pre-launch) | Critical |
| Research publication planned? | ⚠️ TBD (not immediate) | High |
| Can afford 3-5 week delay? | ❌ NO (Week 3 of MVP) | Critical |
| $2-5k justified by revenue? | ❌ NO (pre-revenue) | High |

**Recommendation: DEFER**

**Phase 2+ (Post-MVP): Reassess when GO ≥ 3/5**

Wait for:
1. MVP launch (Week 3)
2. User feedback (Weeks 4-8)
3. Market validation (revenue/engagement)
4. Feature prioritization from actual users

---

## Phased Migration Roadmap (IF NEEDED)

### Immediate (Week 4 - Post-MVP Launch)
**Action:** Test OpenCap as low-risk validation
- Record sample videos with 2 smartphones
- Upload to opencap.ai, download results
- Compare accuracy vs MediaPipe on validation dataset
- Assess if improvement justifies complexity
- **Cost:** $0, **Time:** 2-3 days

### Short-term (Weeks 5-8 - IF accuracy validated as pain point)
**Action:** Implement hybrid architecture
- Create `Pose2SimAdapter` class alongside `PoseTracker`
- Add `--multi-camera` flag to CLI
- Keep MediaPipe for single-camera (backward compatible)
- Add Pose2Sim for research-grade offline analysis
- Share analysis logic (smoothing, metrics calculation)
- **Cost:** $2-3k (cameras), **Time:** 2-4 weeks

### Long-term (Months 2-3 - IF market demands it)
**Action:** Full Pose2Sim integration
- Multi-camera calibration UI
- Batch processing optimization
- OpenSim biomechanical constraints
- Validation study publication (if academic goals)
- Market as "research-grade" premium tier
- **Cost:** $2-5k, **Time:** 4-6 weeks

---

## Alternative: OpenCap Comparison

### OpenCap Advantages vs Pose2Sim
- **Cost:** $0 (use existing smartphones)
- **Setup:** Minutes (no calibration needed)
- **Processing:** Cloud-based (no local compute)
- **Accuracy:** ~4-6° joint angle errors (vs 3-4° for Pose2Sim)
- **Biomechanics:** Automatic OpenSim constraints

### OpenCap Disadvantages
- **Internet required:** Cloud processing dependency
- **Less control:** Can't customize pipeline
- **Validation:** Still emerging (fewer published studies than Pose2Sim)
- **Output format:** May require parsing/conversion

### Recommendation
**Test OpenCap first** (Week 4) before committing to Pose2Sim hardware investment.

---

## Key Technical Insights

### GPU Requirements
- **OpenCap:** NO GPU needed (cloud processing)
- **Pose2Sim:** GPU only speeds up 2D pose step (3-5x faster)
  - With GPU: ~2-5 min per camera (1000 frames)
  - With CPU: ~10-30 min per camera (1000 frames)
- **Recommendation:** CPU-only Pose2Sim acceptable for research use

### Current Architecture (Kinemotion)
- **PoseTracker:** Wraps MediaPipe, processes frames sequentially
- **API entry points:** `process_dropjump_video()`, `process_cmj_video()` (376-628 lines)
- **Data flow:** Video → PoseTracker.process_frame() → landmarks → smoothing → analysis → metrics
- **Integration points:** Replace PoseTracker or add parallel Pose2Sim path

### Integration Complexity
- **Low:** OpenCap (parse output, feed to existing analysis)
- **Medium:** Hybrid Pose2Sim (new code path, keep MediaPipe)
- **High:** Full Pose2Sim replacement (breaking change)

---

## Strategic Recommendation

### Phase 1 (NOW): Ship MVP with MediaPipe
**Focus:** Get product in coaches' hands, gather feedback
- Current accuracy sufficient for initial validation
- Real-time capability preserved (may be needed)
- No hardware barriers for early adopters
- Fast time-to-market

### Phase 2 (Week 4+): Market-Driven Decision
**If users say:** "Accuracy is not good enough" → Pose2Sim migration
**If users say:** "Real-time feedback is critical" → Stay with MediaPipe
**If users say:** "Both accuracy and real-time needed" → Hybrid architecture

### Key Principle
**Optimize for learning, not accuracy.** Ship fast, validate with real users, then invest based on validated needs rather than technical possibilities.

---

## References

- **Pose2Sim validation:** Pagnon et al. (2022), Sensors 22(7), 2712
- **Stereo MediaPipe:** Dill et al. (2024), Sensors 24(23), 7772
- **AthletePose3D dataset:** Yeung et al. (2025), arXiv:2503.07499
- **Kinemotion docs:** docs/reference/pose-systems.md, docs/research/sports-biomechanics-pose-estimation.md
- **Current architecture:** src/kinemotion/core/pose.py, src/kinemotion/api.py

---

## Conclusion

Pose2Sim migration is **technically feasible** (2-4 weeks, $2-5k) and would provide **67-73% accuracy improvement**, but **strategic timing is wrong**.

**Action:** Focus on MVP launch (Phase 1), gather real market feedback, then decide based on validated user needs rather than technical possibilities.

**Next steps:**
1. Complete MVP launch (Week 3)
2. Collect user feedback (Weeks 4-8)
3. Test OpenCap if accuracy emerges as pain point (Week 4)
4. Reassess Pose2Sim decision when GO score ≥ 3/5
