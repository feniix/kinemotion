---
title: RTMPose Benchmark Code Review - Critical Issues Found
type: note
permalink: development/rtmpose-benchmark-code-review-critical-issues-found
---

# RTMPose Benchmark Code Review - December 27, 2025

## Critical Issue: OptimizedCPUTracker is Non-Functional

### Problem
The `OptimizedCPUTracker` in `optimized_cpu_tracker.py` returns empty pose landmarks:

```python
def _extract_landmarks_from_output(
    self,
    outputs: list,
    bbox: list,
    img_width: int,
    img_height: int,
) -> dict[str, tuple[float, float, float]]:
    """Extract landmarks from RTMPose output."""
    # TODO: Implement proper SIMCC output parsing
    # For now, return empty dict to avoid errors
    return {}  # <-- CRITICAL BUG: Returns empty dict!
```

### Impact
- **FPS benchmarks are VALID** - The 68 FPS result accurately measures inference speed
- **Tracker is NOT FUNCTIONAL** - Cannot be used for actual pose estimation
- **Research summary is misleading** - Doesn't mention this limitation

### Root Cause
RTMPose uses SIMCC (SimCC-based coordinate representation) output format which requires proper decoding. The OptimizedCPUTracker manually loads ONNX models but doesn't implement the complex SIMCC decoding logic that rtmlib handles internally.

## Other Issues Found

### Code Quality Issues
1. **Global variable usage** in `benchmark_cpu_optimizations.py`:
   ```python
   global VIDEO_PATH  # Code smell
   ```

2. **Duplicate code** - `BenchmarkResult` dataclass defined in multiple files:
   - `benchmark.py`
   - `benchmark_cpu_optimizations.py`
   - `optimized_cpu_tracker.py`

3. **File naming inconsistency** - `benchmark_cpu_optimizations.py` now includes CUDA tests

## Recommendation

To make CPU optimization usable in production, either:

**Option 1: Complete the OptimizedCPUTracker**
- Implement proper SIMCC decoding (complex, requires studying rtmlib internals)
- Reference: `rtmlib/backends/onnxruntime/rtmpose/body.py`

**Option 2: Modify rtmlib to expose session options**
- Fork rtmlib and add session_options parameter
- Submit PR upstream

**Option 3: Use environment variables** (quickest)
```python
import os
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['OMP_WAIT_POLICY'] = 'ACTIVE'
from rtmlib import BodyWithFeet
```

## Files Reviewed
- `benchmark.py` - ✅ OK
- `benchmark_cpu_optimizations.py` - ⚠️ Has global var, includes CUDA now
- `optimized_cpu_tracker.py` - ❌ Non-functional (no landmark extraction)
- `rtmpose_tracker.py` - ✅ OK (uses rtmlib correctly)
- `phase3_accuracy.py` - ✅ OK
- `profile_memory.py` - ✅ OK (for memory profiling only)

## Action Items
1. Document the OptimizedCPUTracker limitation in research summary
2. Consider implementing Option 3 (environment variables) for working CPU optimization
3. Refactor duplicate BenchmarkResult dataclass
