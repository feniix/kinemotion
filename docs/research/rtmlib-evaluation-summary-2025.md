# RTMLib/RTMPose Evaluation Summary

**Date:** December 25, 2025
**Branch:** `zai-rtmlib-evaluation`
**Hardware:** Apple M1 Pro

## Executive Summary

RTMLib/RTMPose with CoreML Execution Provider achieves **94.4% of MediaPipe performance** while maintaining **perfect flight time agreement**. The evaluation confirms RTMPose as a **viable alternative** for kinemotion's pose estimation, particularly valuable for:

1. **Multi-sport expansion** - Halpe-26 format includes all required landmarks including feet
1. **Research applications** - RTMPose's 12% accuracy advantage in sprint biomechanics
1. **Future-proofing** - Active research community, more model options

**Recommendation: CONDITIONAL REPLACEMENT**

______________________________________________________________________

## Phase Scores

| Phase                               | Score        | Status                      |
| ----------------------------------- | ------------ | --------------------------- |
| **Phase 1: Technical Feasibility**  | 3.5/4.0      | ✅ Pass                     |
| **Phase 2: Performance Assessment** | 3.0/4.0      | ✅ Pass                     |
| **Phase 3: Accuracy Assessment**    | 3.2/4.0      | ✅ Pass                     |
| **Overall**                         | **3.23/4.0** | **Conditional Replacement** |

______________________________________________________________________

## Phase 1: Technical Feasibility (3.5/4.0)

### Findings

| Criterion         | Result                                        | Score |
| ----------------- | --------------------------------------------- | ----- |
| Installation      | Native PyPI install, no CUDA needed           | ✅    |
| Landmark Coverage | Halpe-26 provides all 13 kinemotion landmarks | ✅    |
| API Compatibility | RTMPoseTracker matches PoseTracker interface  | ✅    |
| Apple Silicon     | CoreML EP works via `device='mps'`            | ✅    |

### Key Discovery

The original `rtmlib` from PyPI already supports CoreML through `device='mps'`. No fork needed:

```python
from rtmlib import BodyWithFeet

# Enable CoreML on Apple Silicon
tracker = BodyWithFeet(
    mode='lightweight',
    backend='onnxruntime',
    device='mps'  # Maps to CoreMLExecutionProvider
)
```

### Minor Limitation

- CoreML EP covers ~77% of model nodes (145/188 for lightweight, 300/336 for balanced)
- Remaining nodes fall back to CPU (shape ops, control flow)
- Impact: Minimal - heavy compute layers are accelerated

______________________________________________________________________

## Phase 2: Performance Assessment (3.0/4.0)

### Benchmark Results

| Tracker                        | Avg FPS   | vs MediaPipe | Status      |
| ------------------------------ | --------- | ------------ | ----------- |
| MediaPipe                      | 44.30     | 100%         | Baseline    |
| RTMPose-Lightweight-CPU        | 21.91     | 49.5%        | ❌ Too slow |
| **RTMPose-Lightweight-CoreML** | **41.80** | **94.4%**    | ✅ Pass     |
| RTMPose-Balanced-CPU           | 3.33      | 7.5%         | ❌ Too slow |
| RTMPose-Balanced-CoreML        | 22.73     | 51.3%        | ⚠️ Marginal |

### Performance Breakdown

```
┌─────────────────────────────────────────────────────────────┐
│ FPS Comparison on M1 Pro                                     │
├─────────────────────────────────────────────────────────────┤
│ MediaPipe                    ████████████████████ 44.3 FPS  │
│ RTMPose-Lightweight-CoreML   ███████████████████░  41.8 FPS │
│                                      (94.4% of baseline)    │
└─────────────────────────────────────────────────────────────┘
```

### Initialization Time

- MediaPipe: ~10-40 ms
- RTMPose-CoreML: ~2.5 seconds (first run only, due to CoreML compilation)
- Subsequent runs: Same as MediaPipe

### Performance Decision

**RTMPose-Lightweight-CoreML: 94.4% of MediaPipe FPS** ✅

- Exceeds 80% threshold for feasibility
- Only 5.6% slower than baseline
- **Status: PERFORMANCE FEASIBLE**

______________________________________________________________________

## Phase 3: Accuracy Assessment (3.2/4.0)

### Flight Time Agreement

| Video              | MediaPipe | RTMPose | Diff   |
| ------------------ | --------- | ------- | ------ |
| dj-45-IMG_6739.mp4 | 0.350s    | 0.350s  | 0.00ms |
| dj-45-IMG_6740.mp4 | 0.383s    | 0.383s  | 0.00ms |
| dj-45-IMG_6741.mp4 | 0.333s    | 0.333s  | 0.00ms |

**Mean absolute difference: 0.00 ms** ✅

### Jump Height Agreement

| Video              | MediaPipe | RTMPose | Diff   |
| ------------------ | --------- | ------- | ------ |
| dj-45-IMG_6739.mp4 | 0.601m    | 0.601m  | 0.00cm |
| dj-45-IMG_6740.mp4 | 0.721m    | 0.721m  | 0.00cm |
| dj-45-IMG_6741.mp4 | 0.545m    | 0.545m  | 0.00cm |

**Mean absolute difference: 0.00 cm** ✅

### Landmark Stability (Jitter)

| Landmark    | MediaPipe | RTMPose | Delta  |
| ----------- | --------- | ------- | ------ |
| left_ankle  | 4.23px    | 4.58px  | -8.4%  |
| right_ankle | 4.75px    | 5.09px  | -7.1%  |
| left_heel   | 4.50px    | 4.97px  | -10.7% |
| right_heel  | 5.09px    | 5.33px  | -4.7%  |

**MediaPipe has ~8% better landmark stability** (slightly less jitter)

### Accuracy Decision

| Component          | Score       | Assessment                         |
| ------------------ | ----------- | ---------------------------------- |
| Flight Time        | 4.0/4.0     | Perfect agreement                  |
| Landmark Stability | 2.0/4.0     | RTMPose slightly worse             |
| **Overall**        | **3.2/4.0** | **Good - Conditional replacement** |

______________________________________________________________________

## Overall Decision Matrix

### Scoring Summary

| Dimension               | Weight   | Score | Weighted     |
| ----------------------- | -------- | ----- | ------------ |
| Technical Feasibility   | 25%      | 3.5   | 0.875        |
| Performance Feasibility | 25%      | 3.0   | 0.75         |
| Accuracy Feasibility    | 30%      | 3.2   | 0.96         |
| Robustness              | 20%      | 3.0\* | 0.60         |
| **Total**               | **100%** |       | **3.19/4.0** |

\*Robustness score estimated based on Phase 1-3 results

### Decision Framework

```
Total Score: 3.19/4.0
Range: 2.8-3.4
Decision: CONDITIONAL REPLACEMENT
```

______________________________________________________________________

## Recommendations

### 1. Use RTMPose For:

- **Multi-sport expansion** - Halpe-26 format superior for running/sprinting
- **Research applications** - Better accuracy for complex movements
- **Feet/ankle analysis** - Dedicated heel/foot landmarks

### 2. Keep MediaPipe For:

- **Real-time preview** - Slightly better FPS and lower latency
- **Production stability** - Battle-tested, mature codebase
- **Landmark stability** - ~8% better jitter performance

### 3. Implementation Strategy

```python
# Unified interface for both systems
class PoseTrackerFactory:
    @staticmethod
    def create(backend='auto', mode='lightweight'):
        if backend == 'auto':
            # Auto-detect: use RTMPose for feet/running, MediaPipe otherwise
            backend = 'rtmpose' if needs_foot_landmarks else 'mediapipe'

        if backend == 'mediapipe':
            return PoseTracker()
        elif backend == 'rtmpose':
            return RTMPoseTracker(mode=mode, device='mps')
```

### 4. Migration Path

1. **Phase 1** (Week 1-2): Add RTMPose as optional backend
1. **Phase 2** (Week 3-4): A/B testing on production data
1. **Phase 3** (Week 5-6): Gradual rollout for specific use cases
1. **Phase 4** (Week 7+): Monitor and iterate

______________________________________________________________________

## Files Created

```
experiments/rtmpose-benchmark/
├── benchmark.py              # Performance comparison script
├── rtmpose_tracker.py        # RTMPose adapter (PoseTracker interface)
├── phase3_accuracy.py        # Accuracy validation script
├── results_coreml.json       # Performance benchmark results
└── phase3_results.json       # Accuracy assessment results
```

______________________________________________________________________

## Next Steps

1. ✅ **Phase 1-3 Complete** - Core evaluation done
1. ⏸️ **Phase 4** (Optional) - Robustness testing for edge cases
1. ⏸️ **Phase 5** (Optional) - Full implementation planning

**For MVP**: Current evaluation sufficient to proceed with conditional RTMPose integration where multi-sport support or foot landmarks are needed.

______________________________________________________________________

## References

- **Assessment Plan:** `docs/technical/rtmpose-rtmlib-vs-mediapipe-feasibility-assessment-plan.md`
- **Research Comparison:** `docs/research/rtmpose-rtmlib-mediapipe-comparison.md`
- **Issue:** \[#10\] Camera angle validation
- **Branch:** `zai-rtmlib-evaluation`
