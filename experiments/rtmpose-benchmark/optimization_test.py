"""Performance optimization tests for RTMPose on Apple Silicon.

Tests multiple optimization strategies:
1. OpenCV DNN backend (vs ONNX Runtime)
2. ONNX Runtime with threading optimizations
3. ONNX Runtime with CoreML Execution Provider (manual configuration)
4. Baseline comparisons
"""

from __future__ import annotations

import json

# Import the standard RTMPoseTracker
import sys
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

import cv2

from kinemotion.core.timing import PerformanceTimer

sys.path.insert(0, str(Path(__file__).parent))
from rtmpose_tracker import RTMPoseTracker


@dataclass
class OptimizationResult:
    """Results from a single optimization test."""

    config_name: str
    video_path: str
    total_frames: int
    successful_frames: int
    total_time: float
    fps: float
    avg_frame_time_ms: float
    min_frame_time_ms: float
    max_frame_time_ms: float
    std_frame_time_ms: float
    initialization_time_ms: float
    timing_breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "config": self.config_name,
            "video": Path(self.video_path).name,
            "total_frames": self.total_frames,
            "successful_frames": self.successful_frames,
            "success_rate": self.successful_frames / self.total_frames
            if self.total_frames > 0
            else 0,
            "total_time": round(self.total_time, 3),
            "fps": round(self.fps, 2),
            "avg_frame_time_ms": round(self.avg_frame_time_ms, 2),
            "min_frame_time_ms": round(self.min_frame_time_ms, 2),
            "max_frame_time_ms": round(self.max_frame_time_ms, 2),
            "std_frame_time_ms": round(self.std_frame_time_ms, 2),
            "initialization_time_ms": round(self.initialization_time_ms, 2),
            "timing_breakdown": {k: round(v * 1000, 2) for k, v in self.timing_breakdown.items()},
        }


def test_configuration(
    config_name: str,
    tracker_factory,
    video_path: str,
    warmup_frames: int = 5,
) -> OptimizationResult:
    """Test a specific configuration on a video.

    Args:
        config_name: Name of the configuration (for reporting)
        tracker_factory: Function that creates the tracker instance
        video_path: Path to test video
        warmup_frames: Number of frames to skip for warmup

    Returns:
        OptimizationResult with metrics
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    # Measure initialization time
    init_start = perf_counter()
    timer = PerformanceTimer()
    tracker = tracker_factory(timer=timer)
    init_time = perf_counter() - init_start

    # Warmup
    for _ in range(warmup_frames):
        ret, frame = cap.read()
        if not ret:
            break
        tracker.process_frame(frame)

    # Reset for actual benchmark
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    timer = PerformanceTimer()
    tracker = tracker_factory(timer=timer)

    # Benchmark loop
    successful_frames = 0
    start_time = perf_counter()
    frame_times_raw = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_start = perf_counter()
        result = tracker.process_frame(frame)
        frame_time = perf_counter() - frame_start

        frame_times_raw.append(frame_time)
        if result is not None:
            successful_frames += 1

    total_time = perf_counter() - start_time
    cap.release()
    tracker.close()

    # Calculate statistics
    import statistics

    avg_time = statistics.mean(frame_times_raw) if frame_times_raw else 0
    min_time = min(frame_times_raw) if frame_times_raw else 0
    max_time = max(frame_times_raw) if frame_times_raw else 0
    std_time = statistics.stdev(frame_times_raw) if len(frame_times_raw) > 1 else 0
    fps = len(frame_times_raw) / total_time if total_time > 0 else 0

    # Get timing breakdown
    metrics = timer.get_metrics()

    return OptimizationResult(
        config_name=config_name,
        video_path=video_path,
        total_frames=len(frame_times_raw),
        successful_frames=successful_frames,
        total_time=total_time,
        fps=fps,
        avg_frame_time_ms=avg_time * 1000,
        min_frame_time_ms=min_time * 1000,
        max_frame_time_ms=max_time * 1000,
        std_frame_time_ms=std_time * 1000,
        initialization_time_ms=init_time * 1000,
        timing_breakdown=metrics,
    )


def run_optimization_benchmark(
    video_path: str,
    output: str | None = None,
) -> list[OptimizationResult]:
    """Run optimization benchmark across all configurations.

    Args:
        video_path: Path to test video
        output: Optional JSON output path

    Returns:
        List of OptimizationResult for each configuration
    """
    results = []

    print("=== RTMPose Optimization Benchmark ===")
    print(f"Video: {Path(video_path).name}")
    print(f"ONNX Runtime version: {cv2.getBuildInformation().count('ONNX') > 0}")
    print()

    # Configuration 1: Baseline (ONNX Runtime, CPU, default settings)
    print("1. Baseline (ONNX Runtime CPU, default)...")
    results.append(
        test_configuration(
            "Baseline: ONNX CPU Default",
            lambda timer: RTMPoseTracker(mode="lightweight", timer=timer),
            video_path,
        )
    )
    print(f"   FPS: {results[-1].fps:.2f}")

    # Configuration 2: OpenCV DNN backend
    print("2. OpenCV DNN backend...")
    try:
        results.append(
            test_configuration(
                "OpenCV DNN Backend",
                lambda timer: RTMPoseTracker(mode="lightweight", backend="opencv", timer=timer),
                video_path,
            )
        )
        print(f"   FPS: {results[-1].fps:.2f}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Configuration 3: ONNX Runtime with minimal threads (for comparison)
    print("3. ONNX Runtime (single-threaded)...")
    try:
        # Set environment variable before importing
        import os

        old_env = os.environ.get("OMP_NUM_THREADS")
        os.environ["OMP_NUM_THREADS"] = "1"

        results.append(
            test_configuration(
                "ONNX Runtime Single-Threaded",
                lambda timer: RTMPoseTracker(mode="lightweight", timer=timer),
                video_path,
            )
        )
        print(f"   FPS: {results[-1].fps:.2f}")

        if old_env is not None:
            os.environ["OMP_NUM_THREADS"] = old_env
        else:
            os.environ.pop("OMP_NUM_THREADS", None)
    except Exception as e:
        print(f"   ERROR: {e}")

    # Configuration 4: CoreML Execution Provider
    print("4. ONNX Runtime CoreML EP...")
    try:
        results.append(
            test_configuration(
                "ONNX Runtime CoreML EP",
                lambda timer: RTMPoseTracker(
                    mode="lightweight", backend="onnxruntime", device="coreml", timer=timer
                ),
                video_path,
            )
        )
        print(f"   FPS: {results[-1].fps:.2f}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Output results
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            "video": Path(video_path).name,
            "results": [r.to_dict() for r in results],
        }

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {output_path}")

    return results


def print_summary(
    results: list[OptimizationResult], baseline_name: str = "Baseline: ONNX CPU Default"
) -> None:
    """Print summary statistics for all configurations."""
    print()
    print("=== Optimization Results Summary ===")
    print()

    # Find baseline
    baseline = next((r for r in results if r.config_name == baseline_name), None)
    if not baseline:
        baseline = results[0]

    print(f"{'Configuration':<35} {'FPS':<10} {'vs Baseline':<15} {'Avg (ms)':<12}")
    print("-" * 75)

    for r in results:
        ratio = (r.fps / baseline.fps * 100) if baseline.fps > 0 else 0
        diff = ratio - 100
        indicator = "+" if diff > 0 else ""
        print(
            f"{r.config_name:<35} {r.fps:<10.2f} "
            f"{indicator}{diff:<+14.1f}% {r.avg_frame_time_ms:<12.2f}"
        )

    print()
    print("=== Recommendations ===")
    print()

    best = max(results, key=lambda r: r.fps)
    print(f"Best performance: {best.config_name} ({best.fps:.2f} FPS)")

    if best.fps > baseline.fps * 1.1:
        improvement = ((best.fps - baseline.fps) / baseline.fps) * 100
        print(f"Improvement over baseline: {improvement:.1f}%")
    elif best.fps < baseline.fps * 0.9:
        regression = ((baseline.fps - best.fps) / baseline.fps) * 100
        print(f"Note: Best config is {regression:.1f}% SLOWER than baseline")


def main():
    """Main entry point for optimization test script."""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark RTMPose optimization strategies")
    parser.add_argument(
        "video",
        help="Path to test video",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output JSON file path",
        default="experiments/rtmpose-benchmark/optimization_results.json",
    )

    args = parser.parse_args()

    results = run_optimization_benchmark(
        video_path=args.video,
        output=args.output,
    )

    print_summary(results)


if __name__ == "__main__":
    main()
