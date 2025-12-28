---
title: Multi-Backend Pose Tracking Architecture
type: note
permalink: development/multi-backend-pose-tracking-architecture
---

# Multi-Backend Pose Tracking Architecture

## Goal

Support multiple pose tracking backends with automatic selection:
- MediaPipe (baseline, always available)
- RTMPose-S with multiple acceleration options:
  - CPU optimized (68 FPS, 9-12px accuracy)
  - CUDA (133 FPS, GPU accelerated)
  - CoreML (42 FPS, Apple Silicon)

## Architecture Design

### Factory Pattern

```python
class PoseTrackerFactory:
    @staticmethod
    def create(backend='auto', mode='lightweight', **kwargs):
        """Create pose tracker with specified backend.

        Args:
            backend: 'auto', 'mediapipe', 'rtmpose-cpu', 'rtmpose-cuda', 'rtmpose-coreml'
            mode: 'lightweight' or 'balanced' (RTMPose only)
            **kwargs: Backend-specific parameters

        Returns:
            Pose tracker instance matching PoseTracker interface
        """
        if backend == 'auto':
            backend = PoseTrackerFactory._detect_best_backend()

        trackers = {
            'mediapipe': MediaPipePoseTracker,
            'rtmpose-cpu': OptimizedCPUTracker,
            'rtmpose-cuda': RTMPoseTrackerWrapper,  # device='cuda'
            'rtmpose-coreml': RTMPoseTrackerWrapper,  # device='mps'
        }

        return trackers[backend](mode=mode, **kwargs)

    @staticmethod
    def _detect_best_backend():
        """Auto-detect best available backend.

        Priority:
        1. CUDA (if available) - fastest
        2. CoreML (if macOS) - good performance
        3. Optimized CPU - fallback
        4. MediaPipe - guaranteed fallback
        """
        try:
            import torch
            if torch.cuda.is_available():
                return 'rtmpose-cuda'
        except ImportError:
            pass

        if sys.platform == 'darwin':
            return 'rtmpose-coreml'

        return 'rtmpose-cpu'
```

### Auto-Detection Priority

| Backend | Detection Method | Performance | Accuracy |
|---------|-----------------|-------------|----------|
| rtmpose-cuda | torch.cuda.is_available() | 133 FPS | 9-12px |
| rtmpose-coreml | sys.platform == 'darwin' | 42 FPS | 9-12px |
| rtmpose-cpu | Fallback | 68 FPS | 9-12px |
| mediapipe | Always available | 48 FPS | Baseline |

## File Structure

### Current
```
src/kinemotion/
├── core/
│   └── pose.py                    # MediaPipe only
experiments/rtmpose-benchmark/
├── optimized_cpu_tracker.py       # Needs to move
└── rtmpose_tracker.py             # Needs to move
```

### Proposed
```
src/kinemotion/
├── core/
│   ├── pose.py                    # MediaPipe + Factory
│   ├── rtmpose_cpu.py             # OptimizedCPUTracker
│   └── rtmpose_wrapper.py         # RTMPoseTracker (CUDA/CoreML)
├── cmj/
│   └── analysis.py                # Uses PoseTrackerFactory.create()
├── dropjump/
│   └── analysis.py                # Uses PoseTrackerFactory.create()
```

## Interface Compatibility

All trackers must implement:
```python
def process_frame(self, frame: np.ndarray, timestamp_ms: int = 0) -> dict[str, tuple[float, float, float]] | None:
    """Process frame and return landmarks.

    Returns:
        Dict mapping landmark names to (x, y, visibility) tuples,
        or None if no pose detected.
    """
```

## Usage Examples

```python
# Auto-detect best backend
tracker = PoseTrackerFactory.create()

# Force specific backend
tracker = PoseTrackerFactory.create(backend='rtmpose-cuda')

# Use in analysis
tracker = PoseTrackerFactory.create(backend='auto')
landmarks = tracker.process_frame(frame)
```

## Implementation Notes

1. **OptimizedCPUTracker**: ONNX Runtime with intra_threads=8, inter_threads=1
2. **RTMPoseTrackerWrapper**: Wraps rtmlib.BodyWithFeet for CUDA/MPS
3. **MediaPipePoseTracker**: Existing PoseTracker (renamed)
4. **Fallback chain**: Ensures graceful degradation

## Migration Path

1. Create new files in core/
2. Add PoseTrackerFactory to pose.py
3. Update imports in cmj/ and dropjump/
4. Add environment variable override (POSE_TRACKER_BACKEND)
5. Test all backends
