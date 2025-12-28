"""Detailed performance benchmark for pose tracking backends.

Measures:
- Per-frame pose tracking latency (isolated from video I/O)
- Initialization time
- Actual ONNX Runtime execution providers in use
- GPU memory allocation
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2

from kinemotion.core.pose import PoseTrackerFactory
from kinemotion.core.timing import PerformanceTimer

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Test video
TEST_VIDEO = str(PROJECT_ROOT / "samples/test-videos/cmj-45-IMG_6733.mp4")


@dataclass
class BackendBenchmarkResult:
    """Results from benchmarking a single backend."""

    backend: str
    tracker_class: str
    execution_providers: list[str]
    device_info: str
    total_frames: int
    successful_frames: int
    # Timing metrics
    initialization_time_ms: float
    total_time: float
    avg_frame_time_ms: float
    min_frame_time_ms: float
    max_frame_time_ms: float
    std_frame_time_ms: float
    p50_frame_time_ms: float
    p95_frame_time_ms: float
    p99_frame_time_ms: float
    fps: float
    # Raw data
    frame_times_ms: list[float] = field(default_factory=list)
    timing_breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "backend": self.backend,
            "tracker_class": self.tracker_class,
            "execution_providers": self.execution_providers,
            "device_info": self.device_info,
            "total_frames": self.total_frames,
            "successful_frames": self.successful_frames,
            "success_rate": self.successful_frames / self.total_frames
            if self.total_frames > 0
            else 0,
            "initialization_time_ms": round(self.initialization_time_ms, 2),
            "total_time_s": round(self.total_time, 3),
            "avg_frame_time_ms": round(self.avg_frame_time_ms, 2),
            "min_frame_time_ms": round(self.min_frame_time_ms, 2),
            "max_frame_time_ms": round(self.max_frame_time_ms, 2),
            "std_frame_time_ms": round(self.std_frame_time_ms, 2),
            "p50_frame_time_ms": round(self.p50_frame_time_ms, 2),
            "p95_frame_time_ms": round(self.p95_frame_time_ms, 2),
            "p99_frame_time_ms": round(self.p99_frame_time_ms, 2),
            "fps": round(self.fps, 2),
            "timing_breakdown_ms": {
                k: round(v * 1000, 2) for k, v in self.timing_breakdown.items()
            },
        }


def get_execution_providers(tracker: Any) -> list[str]:
    """Extract actual ONNX Runtime execution providers from tracker."""
    tracker_class = type(tracker).__name__

    if tracker_class == "MediaPipePoseTracker":
        return ["MediaPipe Tasks API (CPU/GPU auto)"]

    if tracker_class == "OptimizedCPUTracker":
        # Check ONNX Runtime sessions
        det_session = getattr(tracker, "det_session", None)
        pose_session = getattr(tracker, "pose_session", None)

        providers = set()
        for session in [det_session, pose_session]:
            if session is not None:
                providers.update(session.get_providers())
        return sorted(providers)

    if tracker_class == "RTMPoseWrapper":
        # Check rtmlib's BodyWithFeet estimator
        estimator = getattr(tracker, "estimator", None)
        if estimator is not None:
            # Check if it has pose_model and det_model (YOLOX + RTMPose)
            for model_name in ["pose_model", "det_model"]:
                model = getattr(estimator, model_name, None)
                if model is not None:
                    session = getattr(model, "session", None)
                    if session is not None:
                        return list(session.get_providers())
            # Check single-stage model (RTMO)
            for model_name in ["model"]:
                model = getattr(estimator, model_name, None)
                if model is not None:
                    session = getattr(model, "session", None)
                    if session is not None:
                        return list(session.get_providers())

    return ["Unknown"]


def get_device_info(tracker: Any) -> str:
    """Get detailed device information from tracker."""
    tracker_class = type(tracker).__name__

    if tracker_class == "MediaPipePoseTracker":
        return "MediaPipe (auto-detect)"

    if tracker_class == "OptimizedCPUTracker":
        try:
            import onnxruntime as ort

            providers = ort.get_available_providers()
            if "CUDAExecutionProvider" in providers:
                return f"ONNX Runtime (CUDA available: {providers})"
            return f"ONNX Runtime (CPU only: {providers})"
        except ImportError:
            return "ONNX Runtime"

    if tracker_class == "RTMPoseWrapper":
        device = getattr(tracker, "device", None)
        backend = getattr(tracker, "backend", None)
        return f"RTMLib device={device}, backend={backend}"

    return "Unknown"


def benchmark_backend(
    backend: str,
    video_path: str,
    warmup_frames: int = 10,
) -> BackendBenchmarkResult:
    """Benchmark a single pose tracking backend.

    Isolates pose tracking from video I/O by pre-loading all frames.
    """
    # Load all frames into memory (eliminates video I/O overhead)
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    print(f"  Loaded {len(frames)} frames from video")

    # Measure initialization time
    init_start = time.perf_counter()
    timer = PerformanceTimer()
    tracker = PoseTrackerFactory.create(backend=backend, timer=timer)
    init_time = time.perf_counter() - init_start

    tracker_class = type(tracker).__name__
    execution_providers = get_execution_providers(tracker)
    device_info = get_device_info(tracker)

    print(f"  Tracker: {tracker_class}")
    print(f"  Execution providers: {execution_providers}")
    print(f"  Device info: {device_info}")
    print(f"  Initialization: {init_time * 1000:.1f} ms")

    # Warmup
    print(f"  Warming up with {warmup_frames} frames...")
    for _, frame in enumerate(frames[:warmup_frames]):
        tracker.process_frame(frame)

    # Reset timer for actual benchmark
    timer = PerformanceTimer()
    tracker = PoseTrackerFactory.create(backend=backend, timer=timer)

    # Benchmark loop - measure per-frame pose tracking only
    frame_times = []
    successful_frames = 0
    start_time = time.perf_counter()

    for frame in frames:
        frame_start = time.perf_counter()
        result = tracker.process_frame(frame)
        frame_time = time.perf_counter() - frame_start

        frame_times.append(frame_time * 1000)  # Convert to ms
        if result is not None:
            successful_frames += 1

    total_time = time.perf_counter() - start_time
    tracker.close()

    # Calculate statistics
    avg_time = statistics.mean(frame_times) if frame_times else 0
    min_time = min(frame_times) if frame_times else 0
    max_time = max(frame_times) if frame_times else 0
    std_time = statistics.stdev(frame_times) if len(frame_times) > 1 else 0

    # Percentiles
    sorted_times = sorted(frame_times)
    p50 = sorted_times[len(sorted_times) // 2] if sorted_times else 0
    p95 = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
    p99 = sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0

    fps = len(frame_times) / total_time if total_time > 0 else 0

    # Get timing breakdown
    timing_metrics = timer.get_metrics()

    return BackendBenchmarkResult(
        backend=backend,
        tracker_class=tracker_class,
        execution_providers=execution_providers,
        device_info=device_info,
        total_frames=len(frame_times),
        successful_frames=successful_frames,
        initialization_time_ms=init_time * 1000,
        total_time=total_time,
        avg_frame_time_ms=avg_time,
        min_frame_time_ms=min_time,
        max_frame_time_ms=max_time,
        std_frame_time_ms=std_time,
        p50_frame_time_ms=p50,
        p95_frame_time_ms=p95,
        p99_frame_time_ms=p99,
        fps=fps,
        frame_times_ms=frame_times,
        timing_breakdown=timing_metrics,
    )


def run_comparative_benchmark(
    backends: list[str] | None = None,
    output: str | None = None,
) -> dict[str, BackendBenchmarkResult]:
    """Run comparative benchmark across all backends."""
    if backends is None:
        backends = ["mediapipe", "rtmpose-cpu", "rtmpose-cuda"]

    results: dict[str, BackendBenchmarkResult] = {}

    print("=== Pose Tracking Backend Benchmark ===")
    print(f"Video: {Path(TEST_VIDEO).name}")
    print(f"Backends: {', '.join(backends)}")
    print()

    for backend in backends:
        print(f"--- {backend} ---")
        try:
            result = benchmark_backend(backend, TEST_VIDEO)
            results[backend] = result
            print(f"  Results: {result.fps:.1f} FPS, {result.avg_frame_time_ms:.1f} ms/frame")
            print()
        except Exception as e:
            print(f"  ERROR: {e}")
            print()
            continue

    # Output results
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = {backend: result.to_dict() for backend, result in results.items()}

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to: {output_path}")

    return results


def print_summary(results: dict[str, BackendBenchmarkResult]) -> None:
    """Print summary statistics."""
    print()
    print("=== Performance Summary ===")
    print()
    print(
        f"{'Backend':<20} {'FPS':<10} {'Avg (ms)':<10} "
        f"{'P50 (ms)':<10} {'P95 (ms)':<10} {'Init (ms)':<10}"
    )
    print("-" * 80)

    for backend, result in results.items():
        print(
            f"{backend:<20} {result.fps:<10.1f} "
            f"{result.avg_frame_time_ms:<10.1f} {result.p50_frame_time_ms:<10.1f} "
            f"{result.p95_frame_time_ms:<10.1f} {result.initialization_time_ms:<10.1f}"
        )

    print()
    print("=== Execution Providers ===")
    print()
    for backend, result in results.items():
        providers = ", ".join(result.execution_providers)
        print(f"{backend:<20} {providers}")

    print()
    print("=== Device Info ===")
    print()
    for backend, result in results.items():
        print(f"{backend:<20} {result.device_info}")

    # Compare to MediaPipe
    if "mediapipe" in results:
        mp_fps = results["mediapipe"].fps
        print()
        print("=== Performance vs MediaPipe ===")
        print()
        for backend, result in results.items():
            if backend == "mediapipe":
                continue
            ratio = (result.fps / mp_fps * 100) if mp_fps > 0 else 0
            print(f"{backend:<20} {ratio:.1f}% of MediaPipe FPS")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Detailed benchmark of pose tracking backends")
    parser.add_argument(
        "--backends",
        nargs="+",
        default=["mediapipe", "rtmpose-cpu", "rtmpose-cuda"],
        choices=["mediapipe", "rtmpose-cpu", "rtmpose-cuda", "rtmpose-coreml"],
        help="Backends to benchmark",
    )
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument(
        "--video",
        default=TEST_VIDEO,
        help="Path to test video",
    )

    args = parser.parse_args()

    results = run_comparative_benchmark(
        backends=args.backends,
        output=args.output,
    )

    if results:
        print_summary(results)


if __name__ == "__main__":
    main()
