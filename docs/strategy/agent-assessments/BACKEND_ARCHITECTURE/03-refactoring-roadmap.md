______________________________________________________________________

## permalink: architecture/refactoring-roadmap-critical-path-to-real-time-multi-sport

______________________________________________________________________

## title: Refactoring Roadmap - Critical Path to Real-Time & Multi-Sport type: note permalink: architecture/refactoring-roadmap-critical-path-to-real-time-multi-sport

# Critical Path Refactoring Roadmap

**Quick Reference for Architecture Implementation**

______________________________________________________________________

## The Problem

Current api.py structure blocks real-time and multi-sport:

```python
# Current: 40% duplicate code between functions
def process_dropjump_video(...) -> DropJumpMetrics:  # 232 lines
    # Reads entire video into memory
    # Processes all frames sequentially
    # Calculates metrics at end
    # Cannot stream frames (WebSocket)

def process_cmj_video(...) -> CMJMetrics:  # 248 lines
    # ~90% duplicate of above
    # Different phase detection only

# With Task 4 (Running), would add 220+ more duplicate lines
# Duplication: 2.96% → 5.5%
```

## The Solution: 5-Day Refactoring Sprint

### Day 1: Extract Streaming Infrastructure

**File:** `/Users/feniix/src/personal/cursor/dropjump-claude/src/kinemotion/core/streaming.py`

```python
# NEW FILE (80 lines)
class RingBuffer:
    """Fixed-size buffer for temporal smoothing window."""
    def __init__(self, size: int):
        self.buffer = deque(maxlen=size)

    def append(self, item):
        self.buffer.append(item)

    def get_all(self) -> list:
        return list(self.buffer)

class StreamingPoseProcessor:
    """Process frames incrementally without loading entire video."""

    def __init__(self, fps: float, smoothing_window: int = 5):
        self.fps = fps
        self.landmark_buffer = RingBuffer(smoothing_window)
        self.tracker = PoseTracker()

    async def process_frame(self, frame: np.ndarray) -> dict | None:
        """Process single frame, return smoothed landmarks or None."""
        pose = self.tracker.process_frame(frame)
        self.landmark_buffer.append(pose)

        if len(self.landmark_buffer) >= self.smoothing_window:
            smoothed = smooth_landmarks(self.landmark_buffer.get_all())
            return smoothed[-1]
        return None
```

**Benefits:** Frame-by-frame processing, constant memory, WebSocket-ready

### Day 1-2: Extract MotionAnalyzer Base Class

**File:** `/Users/feniix/src/personal/cursor/dropjump-claude/src/kinemotion/core/analysis.py`

```python
# NEW FILE (150 lines)
from abc import ABC, abstractmethod
from typing import AsyncIterator
import numpy as np

class MotionAnalyzer(ABC):
    """Base class for all sport-specific motion analysis."""

    @abstractmethod
    async def detect_phases(
        self,
        landmarks_sequence: list[dict],
        fps: float,
        **kwargs
    ) -> List[dict]:  # [{phase_type, start_frame, end_frame, ...}]
        """Detect motion phases from landmarks."""
        pass

    @abstractmethod
    async def calculate_metrics(
        self,
        phases: list[dict],
        vertical_positions: np.ndarray,
        fps: float,
        **kwargs
    ) -> dict:  # Sport-specific metrics
        """Calculate metrics from phases."""
        pass

    async def analyze(
        self,
        processor: StreamingPoseProcessor,
        frame_source: AsyncIterator[np.ndarray],
        fps: float,
        **kwargs
    ) -> dict:
        """Generic analysis pipeline."""
        phases = []
        frame_num = 0
        positions = []

        async for frame in frame_source:
            landmarks = await processor.process_frame(frame)
            if landmarks:
                # Detect phases incrementally (if needed)
                positions.append(landmarks)
            frame_num += 1

        # Final phase detection on complete sequence
        phases = await self.detect_phases(positions, fps, **kwargs)
        metrics = await self.calculate_metrics(phases, np.array(positions), fps, **kwargs)

        return metrics

# Concrete implementations (move existing logic here):

class CMJAnalyzer(MotionAnalyzer):
    """Counter Movement Jump analysis."""

    async def detect_phases(self, landmarks_sequence, fps, **kwargs):
        # Reuse existing detect_cmj_phases() from cmj/analysis.py
        return detect_cmj_phases(
            vertical_positions=[...],  # extracted from landmarks
            fps=fps,
            **kwargs
        )

    async def calculate_metrics(self, phases, vertical_positions, fps, **kwargs):
        # Reuse existing calculate_cmj_metrics() from cmj/kinematics.py
        return calculate_cmj_metrics(
            vertical_positions=vertical_positions,
            phases=phases,
            fps=fps,
            **kwargs
        )

class DropJumpAnalyzer(MotionAnalyzer):
    """Drop Jump analysis (similar pattern)."""
    async def detect_phases(self, ...):
        # Reuse detect_ground_contact() from dropjump/analysis.py

    async def calculate_metrics(self, ...):
        # Reuse calculate_drop_jump_metrics() from dropjump/kinematics.py
```

**Benefits:** Eliminates process\_\*\_video duplication, enables Task 4

### Day 2: Consolidate api.py

**File:** `/Users/feniix/src/personal/cursor/dropjump-claude/src/kinemotion/api.py` (refactored)

**Before (1150 lines):**

```python
def process_dropjump_video(...) -> DropJumpMetrics:  # 232 lines
    # Video reading + smoothing + detection + metrics

def process_cmj_video(...) -> CMJMetrics:  # 248 lines
    # ~90% duplicate
```

**After (450 lines):**

```python
async def process_video_streaming(
    frame_source: AsyncIterator[np.ndarray],
    analyzer: MotionAnalyzer,
    fps: float,
    quality: str = "balanced",
    **kwargs
) -> dict:
    """Generic streaming video processor."""
    processor = StreamingPoseProcessor(fps)
    params = auto_tune_parameters(...)
    processor.update_smoothing(params.smoothing_window)

    return await analyzer.analyze(
        processor,
        frame_source,
        fps,
        **params
    )

# Backward-compatible batch API (uses streaming internally):
def process_dropjump_video(video_path: str, **kwargs) -> DropJumpMetrics:
    """Batch API (unchanged externally)."""
    async def frame_generator():
        with VideoProcessor(video_path) as video:
            while True:
                frame = video.read_frame()
                if frame is None:
                    break
                yield frame

    analyzer = DropJumpAnalyzer(**kwargs)
    return asyncio.run(
        process_video_streaming(
            frame_generator(),
            analyzer,
            video.fps,
            **kwargs
        )
    )

def process_cmj_video(video_path: str, **kwargs) -> CMJMetrics:
    """Similar to above."""
    async def frame_generator():
        with VideoProcessor(video_path) as video:
            while True:
                frame = video.read_frame()
                if frame is None:
                    break
                yield frame

    analyzer = CMJAnalyzer(**kwargs)
    return asyncio.run(process_video_streaming(...))

# NEW API for WebSocket/streaming:
async def process_video_realtime(
    frame_source: AsyncIterator[np.ndarray],
    sport_type: str,
    on_metric_update: Callable[[dict], Awaitable[None]],
    **kwargs
) -> dict:
    """Real-time streaming API (Task 3 uses this)."""
    analyzer = ANALYZERS[sport_type](**kwargs)

    # Process with callbacks for metrics
    processor = StreamingPoseProcessor(...)

    async for frame in frame_source:
        landmarks = await processor.process_frame(frame)
        if landmarks:
            metrics = await analyzer.calculate_metrics(...)
            await on_metric_update(metrics)

    return final_metrics
```

**Benefits:** Single processing logic, used by file/stream/WebSocket, 700 lines removed

### Days 3-4: Extract Phase Detection Abstraction

**File:** `/Users/feniix/src/personal/cursor/dropjump-claude/src/kinemotion/core/phase_detection.py`

```python
# NEW FILE (200 lines)
from abc import ABC, abstractmethod
from typing import TypedDict

class Phase(TypedDict):
    """Generic phase representation."""
    start_frame: int
    end_frame: int
    phase_type: str  # "contact", "flight", "stance", "swing", etc.
    confidence: float
    metadata: dict  # Sport-specific

class PhaseDetector(ABC):
    """Base class for phase detection."""

    @abstractmethod
    def detect_phases(
        self,
        landmarks_sequence: list[dict],
        fps: float,
        **kwargs
    ) -> List[Phase]:
        """Detect motion phases from landmarks."""
        pass

# Concrete implementations:

class JumpPhaseDetector(PhaseDetector):
    """Detects jump phases (contact/flight for drop jump, eccentric/concentric for CMJ)."""

    def detect_phases(self, landmarks_sequence, fps, **kwargs) -> List[Phase]:
        # Reuse detect_cmj_phases() and detect_ground_contact()
        # Return generic Phase objects instead of sport-specific

class RunningPhaseDetector(PhaseDetector):
    """NEW: Detects running phases (stance/swing)."""

    def detect_phases(self, landmarks_sequence, fps, **kwargs) -> List[Phase]:
        # Detect foot accelerations
        # Threshold crossing = phase boundary
        # Return Phase objects with confidence

        phases = []
        for i, landmarks in enumerate(landmarks_sequence):
            # Compute foot acceleration
            # Detect phase transitions
            # Append to phases

        return phases
```

**Benefits:** Running doesn't touch jump code, reusable for all sports

### Days 4-5: Consolidate Metrics Calculators & Integration Testing

**File:** `/Users/feniix/src/personal/cursor/dropjump-claude/src/kinemotion/core/metrics.py`

```python
# NEW FILE (100 lines)
from abc import ABC, abstractmethod

class MetricsCalculator(ABC):
    """Base class for metric calculation."""

    @abstractmethod
    def calculate_metrics(
        self,
        phases: List[Phase],
        vertical_positions: np.ndarray,
        fps: float,
        **kwargs
    ) -> dict:
        """Calculate metrics from phases."""
        pass

# Move existing implementations to sport modules:
# dropjump/kinematics.py: class DropJumpMetricsCalculator(MetricsCalculator)
# cmj/kinematics.py: class CMJMetricsCalculator(MetricsCalculator)
# running/kinematics.py: class RunningMetricsCalculator(MetricsCalculator)
```

## Testing Strategy

### Before Refactoring (Baseline)

```bash
uv run pytest  # Should pass all 261 tests
uv run ruff check  # 0 errors
uv run pyright  # 0 errors
npx jscpd src/kinemotion  # 2.96% duplication
```

### After Each Refactoring Phase

```bash
# Test specific module
uv run pytest tests/test_streaming.py -v

# Full regression
uv run pytest

# Check duplication didn't regress
npx jscpd src/kinemotion  # Must stay <3%

# Type safety
uv run pyright
```

### Final Validation

```bash
# Before Task 3 starts
uv run pytest --cov=kinemotion --cov-report=term-missing

# Performance baseline (new)
python -m pytest tests/perf/ -v --benchmark-only

# Single-stream latency should be <500ms (will optimize to <200ms in Task 3)
```

## Risk Mitigation

### If Refactoring Takes Longer

**Early Warning Signs:**

- Day 2 end: StreamingPoseProcessor NOT working with existing api.py
- Day 3 end: MotionAnalyzer tests failing
- Day 4 end: Duplication increased instead of decreased

**Fallback Plan:**

1. Pause refactoring
1. Revert changes, keep current api.py
1. Implement Task 3 with duplicate code (acceptable short-term)
1. Extract abstraction post-MVP

### If Type Safety Breaks

**Issue:** Mypy/Pyright strict mode fails after refactoring

**Solution:**

```python
# Use explicit typing for complex patterns
async def process_video_streaming(
    frame_source: AsyncIterator[np.ndarray],
    analyzer: MotionAnalyzer,
    fps: float,
    quality: str = "balanced",
    **kwargs: Any  # Be explicit about kwargs
) -> MotionMetrics:  # Use generic type
    ...
```

### If Tests Fail

**Pattern:** Test failures in dropjump/cmj modules after refactoring

**Solution:**

1. Identify failing test
1. Check if it uses private functions (now moved)
1. Update import: `from kinemotion.core.streaming import StreamingPoseProcessor`
1. Re-run: Should pass

## File Changes Summary

### New Files Created

- `src/kinemotion/core/streaming.py` (80 lines)
- `src/kinemotion/core/analysis.py` (150 lines)
- `src/kinemotion/core/phase_detection.py` (200 lines)
- `src/kinemotion/core/metrics.py` (100 lines)

### Files Modified

- `src/kinemotion/api.py` (1150 → 450 lines, net -700)
- `src/kinemotion/dropjump/kinematics.py` (wrap in DropJumpAnalyzer)
- `src/kinemotion/cmj/kinematics.py` (wrap in CMJAnalyzer)

### Files Unchanged

- All CLI modules (dropjump/cli.py, cmj/cli.py)
- All tests (add new tests for streaming components)
- Core algorithms (analysis.py functions stay)

## Backward Compatibility

**External API (unchanged):**

```python
# These work exactly as before
from kinemotion import process_dropjump_video, process_cmj_video

metrics = process_dropjump_video("video.mp4")
metrics = process_cmj_video("video.mp4", quality="accurate")
```

**Internal API (new):**

```python
# New streaming API (Task 3 uses this)
from kinemotion.core.streaming import StreamingPoseProcessor
from kinemotion.core.analysis import CMJAnalyzer

processor = StreamingPoseProcessor(fps=30)
analyzer = CMJAnalyzer()
metrics = await analyzer.analyze(processor, frame_source, fps=30)
```

## Success Criteria

- [ ] All 261 tests pass
- [ ] Duplication: still \<3% (target 2.5%)
- [ ] Coverage: >70% (currently 74%)
- [ ] Type errors: 0 (Pyright strict)
- [ ] Single-stream latency: \<500ms (target \<200ms in Task 3)
- [ ] Task 3 can use StreamingPoseProcessor + MotionAnalyzer
- [ ] Task 4 can add RunningGaitAnalyzer with \<400 lines, no duplication spike

______________________________________________________________________

**Total Effort: 5-6 days (1 senior developer)**
**Risk Level: LOW (well-scoped, reversible)**
**Payoff: Unblocks 3 tasks, maintains code quality**
