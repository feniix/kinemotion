---
title: Sprinting Analysis Go/No-Go Decision
type: note
permalink: strategy/sprinting-analysis-go-no-go-decision
tags:
- roadmap
- feature-decision
- sprinting
- mvp
- roi-analysis
---

# Sprinting Analysis Feature Evaluation (2026-01-17)

## Decision: NO-GO for MVP Phase - DEFER to Post-MVP

### Complexity Assessment

**Comparison to Existing Features:**
- Drop Jump: ~2 weeks (Low complexity)
- CMJ: ~3 weeks (Medium complexity)
- Squat Jump: ~2 weeks (Low complexity)
- **Sprinting: 6-8 weeks (Very High complexity)** - 2-3x any jump feature

**Highest-Risk Components:**

1. **Frame Rate Dependency (Very High)**
   - Elite sprinters: 80-120ms contact times
   - At 60fps: 5-7 frames per ground contact (marginal)
   - At 30fps: 2-3 frames (unusable)

2. **Cyclical Movement Analysis (Very High)**
   - Fundamental shift from discrete movements
   - No event-based start/end phases
   - State machine redesign required

3. **Pose Detection Accuracy (High)**
   - 90° lateral view = occlusion issues
   - Arms cross body, blocking leg visibility
   - MediaPipe only validated for jumps at 45°

4. **Smoothing Trade-offs (Medium)**
   - Heavy smoothing needed for oscillation
   - Lag affects contact time accuracy
   - Different parameters for 60fps vs 120fps

### ROI Analysis

**ROI Score: 0.75 (Poor)**

```
ROI = (Impact × Strategic Value) / Complexity
Impact = 3 (medium feature, niche market)
Strategic Value = 2 (enables some running analysis)
Complexity = 8 (very high)
```

**Market Validation:** Unknown - no coach interviews, untested demand

**Opportunity Cost:** 6-8 weeks could fund 3-4 quick-win features

### Recommendations

**For MVP:**
1. Defer sprinting analysis
2. Prioritize: Web UI, export formatting, RTMPose integration
3. Focus on jump analysis validation with coaches

**For Post-MVP (if validated):**
1. Customer discovery: 10-15 coach interviews
2. Research spike: prototype cycle detection
3. Implement with RTMPose (better for running)

**Triggers for Reconsideration:**
- 5+ coaches explicitly request sprinting
- RTMPose integration completed
- 120fps camera ownership confirmed in market
- Competitive analysis shows differentiation value

### Risk Mitigation (If Proceeding)

**Validation Strategy:**
- Ground truth dataset with manual annotation
- Camera angle testing (45° vs 90°)
- Frame rate floor test (30/60/120fps comparison)

**Exit Criteria (Rollback Triggers):**
- Contact time CV >15% vs ground truth
- Step detection accuracy <90%
- Beta users report metrics don't match timing gates
- <5 coaches request feature in first month
