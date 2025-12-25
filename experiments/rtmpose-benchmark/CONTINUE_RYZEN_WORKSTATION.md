# RTMLib Evaluation: Continuation Guide for Ryzen 7 7800X3D Workstation

**Branch:** `zai-rtmlib-evaluation`
**Commit:** `e1cba4f` - "feat(experiments): complete RTMLib/RTMPose evaluation Phase 1-3"

## Status Summary

Phases 1-3 completed on Apple M1 Pro:

| Phase                           | Score   | Status  |
| ------------------------------- | ------- | ------- |
| Phase 1: Technical Feasibility  | 3.5/4.0 | ✅ Pass |
| Phase 2: Performance Assessment | 3.0/4.0 | ✅ Pass |
| Phase 3: Accuracy Assessment    | 3.2/4.0 | ✅ Pass |

**Key Finding:** RTMPose-S-160x160 with CoreML: 42.9 FPS (96.9% of MediaPipe)

## Next Steps on Ryzen 7 7800X3D

### 1. Setup Environment

```bash
# Clone and checkout branch
git clone https://github.com/feniix/kinemotion.git
cd kinemotion
git checkout zai-rtmlib-evaluation

# Install dependencies (requires Python 3.10-3.12)
uv sync

# Verify RTMLib installation
uv run python -c "from rtmlib import Body; print('RTMLib ready')"
```

### 2. Expected Performance on Ryzen 7 7800X3D

Based on official benchmarks (i7-11700: 223 FPS model-only) and CPU comparison:

| Config              | Expected FPS (full pipeline) | vs MediaPipe |
| ------------------- | ---------------------------- | ------------ |
| RTMPose-S (256×192) | 40-60 FPS                    | 90-135%      |
| RTMPose-S (160×160) | 50-70 FPS                    | 113-158%     |

**The Ryzen should OUTPERFORM MediaPipe** for RTMPose!

### 3. Run Benchmarks

```bash
cd experiments/rtmpose-benchmark

# Update video paths for your system
# Edit benchmark.py to use local video paths

# Run full performance benchmark
uv run python benchmark.py --categories dj --output results_ryzen.json

# Run extended benchmark (RTMO + custom sizes)
uv run python benchmark_extended.py

# Run accuracy validation
uv run python phase3_accuracy.py --output phase3_results_ryzen.json
```

### 4. Key Files Reference

| File                    | Purpose                                     |
| ----------------------- | ------------------------------------------- |
| `benchmark.py`          | Full performance comparison (6 videos)      |
| `benchmark_extended.py` | RTMO + custom input size tests (1 video)    |
| `rtmpose_tracker.py`    | RTMPose adapter with PoseTracker interface  |
| `phase3_accuracy.py`    | Flight time/jump height accuracy validation |

### 5. Modifying for Ryzen (CPU-only)

Change `device='mps'` to `device='cpu'` in benchmark scripts:

```python
# Apple M1 Pro (CoreML)
tracker = RTMPoseTracker(mode="lightweight", device="mps")

# Ryzen 7 7800X3D (CPU-only)
tracker = RTMPoseTracker(mode="lightweight", device="cpu")
```

### 6. GPU Acceleration Options

If you have an NVIDIA GPU:

```bash
# Install TensorRT for ONNX Runtime
# See: https://onnxruntime.ai/docs/execution-providers/TensorRT-ExecutionProvider.html

# Use TensorRT EP
tracker = RTMPoseTracker(
    mode="lightweight",
    backend="onnxruntime",
    device="cuda",  # Requires onnxruntime-gpu + TensorRT
)
```

### 7. Results to Collect

1. **FPS Comparison**: RTMPose-S CPU vs MediaPipe baseline
1. **Input Size Optimization**: Test 128×128, 160×160, 192×192, 256×192
1. **Accuracy**: Flight time agreement with MediaPipe
1. **Landmark Stability**: Jitter comparison (px/frame)

### 8. Quick Start Command

```bash
# Single video quick test
cd experiments/rtmpose-benchmark
uv run python benchmark_extended.py
```

## Reference Data

### Intel i7-11700 Benchmarks (ONNX CPU)

| Model     | Input   | Latency | FPS (model-only) |
| --------- | ------- | ------- | ---------------- |
| RTMPose-s | 256×192 | 4.48ms  | **223 FPS**      |

### Ryzen 7 7800X3D vs i7-11700

| Metric        | 7800X3D | i7-11700 | Difference |
| ------------- | ------- | -------- | ---------- |
| Single-thread | 1817    | 1595     | **+14%**   |
| Multi-thread  | 17762   | ~15000   | **+18%**   |

### Sources

- [RTMPose Official Benchmarks](https://github.com/open-mmlab/mmpose/blob/main/projects/rtmpose/benchmark/README.md)
- [CPU Benchmark Comparison](https://www.cpubenchmark.net/compare/4234vs5299/)
- [RTMLib GitHub](https://github.com/Tau-J/rtmlib)

______________________________________________________________________

**Created:** December 25, 2025
**Workstation:** AMD Ryzen 7 7800X3D, 32GB RAM
**Branch:** `zai-rtmlib-evaluation`
