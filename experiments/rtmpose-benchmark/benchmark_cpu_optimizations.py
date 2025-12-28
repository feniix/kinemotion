#!/usr/bin/env python3
"""Benchmark CPU optimization strategies for RTMPose.

Tests different configurations to identify the best optimization strategy:
- ONNX Runtime threading optimization
- Input size reduction
- Combined optimizations
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import optimized CPU tracker
from optimized_cpu_tracker import OptimizedCPUTracker
from rtmpose_tracker import RTMPoseTracker

from kinemotion.core.pose import PoseTracker

# Project root for relative paths
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Test videos (both DJ and CMJ)
TEST_VIDEOS = {
    "DJ": str(PROJECT_ROOT / "samples/test-videos/dj-45-IMG_6739.mp4"),
    "CMJ": str(PROJECT_ROOT / "samples/test-videos/cmj-45-IMG_6733.mp4"),
}

# Default video for quick testing
VIDEO_PATH = TEST_VIDEOS["DJ"]


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    config_name: str
    fps: float
    total_frames: int
    total_time: float
    avg_frame_time_ms: float
    min_frame_time_ms: float
    max_frame_time_ms: float
    init_time_ms: float
    frame_times: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "config": self.config_name,
            "fps": round(self.fps, 2),
            "total_frames": self.total_frames,
            "total_time": round(self.total_time, 3),
            "avg_frame_time_ms": round(self.avg_frame_time_ms, 2),
            "min_frame_time_ms": round(self.min_frame_time_ms, 2),
            "max_frame_time_ms": round(self.max_frame_time_ms, 2),
            "init_time_ms": round(self.init_time_ms, 2),
        }


def benchmark_config(
    config_name: str,
    tracker_factory,
    video_path: str,
    warmup_frames: int = 5,
) -> BenchmarkResult:
    """Benchmark a single tracker configuration.

    Args:
        config_name: Name of the configuration
        tracker_factory: Function that creates the tracker
        video_path: Path to test video
        warmup_frames: Number of frames to skip for warmup

    Returns:
        BenchmarkResult with metrics
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    # Measure initialization time
    init_start = perf_counter()
    tracker = tracker_factory()
    init_time = perf_counter() - init_start

    # Warmup
    for _ in range(warmup_frames):
        ret, frame = cap.read()
        if not ret:
            break
        tracker.process_frame(frame)

    # Reset for actual benchmark
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    tracker = tracker_factory()

    # Benchmark loop
    frame_times = []
    start_time = perf_counter()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_start = perf_counter()
        tracker.process_frame(frame)
        frame_time = perf_counter() - frame_start

        frame_times.append(frame_time)

    total_time = perf_counter() - start_time
    cap.release()
    tracker.close()

    # Calculate statistics
    avg_time = np.mean(frame_times) * 1000 if frame_times else 0
    min_time = np.min(frame_times) * 1000 if frame_times else 0
    max_time = np.max(frame_times) * 1000 if frame_times else 0
    fps = len(frame_times) / total_time if total_time > 0 else 0

    return BenchmarkResult(
        config_name=config_name,
        fps=fps,
        total_frames=len(frame_times),
        total_time=total_time,
        avg_frame_time_ms=avg_time,
        min_frame_time_ms=min_time,
        max_frame_time_ms=max_time,
        init_time_ms=init_time * 1000,
        frame_times=frame_times,
    )


def run_cpu_optimization_benchmark(output: str | None = None) -> dict[str, BenchmarkResult]:
    """Run comprehensive CPU optimization benchmark.

    Tests multiple optimization strategies:
    1. Baseline: Current RTMPoseTracker (default ONNX settings)
    2. MediaPipe baseline for comparison

    Args:
        output: Optional JSON output path

    Returns:
        Dictionary mapping config names to results
    """
    print("=" * 70)
    print("CPU Optimization Benchmark for RTMPose")
    print("=" * 70)
    print(f"Video: {Path(VIDEO_PATH).name}")
    print()

    results = {}

    # Configuration 1: Baseline - RTMPoseTracker with defaults
    print("Testing baseline RTMPoseTracker...")
    results["Baseline-RTMPose-Default"] = benchmark_config(
        "Baseline-RTMPose-Default",
        lambda: RTMPoseTracker(mode="lightweight", device="cpu"),
        VIDEO_PATH,
    )
    print(f"  FPS: {results['Baseline-RTMPose-Default'].fps:.1f}")

    # Configuration 2: MediaPipe baseline
    print("Testing MediaPipe baseline...")
    results["MediaPipe-Baseline"] = benchmark_config(
        "MediaPipe-Baseline",
        lambda: PoseTracker(strategy="image"),
        VIDEO_PATH,
    )
    print(f"  FPS: {results['MediaPipe-Baseline'].fps:.1f}")

    # Configuration 3: Optimized CPU - Sequential mode (8 intra, 1 inter)
    print("Testing Optimized CPU (Sequential mode)...")
    results["Optimized-Sequential-8x1"] = benchmark_config(
        "Optimized-Sequential-8x1",
        lambda: OptimizedCPUTracker(intra_threads=8, inter_threads=1),
        VIDEO_PATH,
    )
    print(f"  FPS: {results['Optimized-Sequential-8x1'].fps:.1f}")

    # Configuration 4: Optimized CPU - Reduced input size (160x160)
    print("Testing Optimized CPU (160x160)...")
    results["Optimized-InputSize-160x160"] = benchmark_config(
        "Optimized-InputSize-160x160",
        lambda: OptimizedCPUTracker(intra_threads=8, inter_threads=1, input_size=(160, 160)),
        VIDEO_PATH,
    )
    print(f"  FPS: {results['Optimized-InputSize-160x160'].fps:.1f}")

    # Configuration 5: Optimized CPU - Smaller input size (128x128)
    print("Testing Optimized CPU (128x128)...")
    results["Optimized-InputSize-128x128"] = benchmark_config(
        "Optimized-InputSize-128x128",
        lambda: OptimizedCPUTracker(intra_threads=8, inter_threads=1, input_size=(128, 128)),
        VIDEO_PATH,
    )
    print(f"  FPS: {results['Optimized-InputSize-128x128'].fps:.1f}")

    # Configuration 6: Optimized CPU - Parallel mode (4 intra, 2 inter)
    print("Testing Optimized CPU (Parallel mode)...")
    results["Optimized-Parallel-4x2"] = benchmark_config(
        "Optimized-Parallel-4x2",
        lambda: OptimizedCPUTracker(intra_threads=4, inter_threads=2),
        VIDEO_PATH,
    )
    print(f"  FPS: {results['Optimized-Parallel-4x2'].fps:.1f}")

    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print()

    # Sort by FPS
    sorted_results = sorted(results.items(), key=lambda x: x[1].fps, reverse=True)

    print(f"{'Configuration':<35} {'FPS':<10} {'vs Baseline':<15} {'Status'}")
    print("-" * 70)

    baseline_fps = results["Baseline-RTMPose-Default"].fps
    mediapipe_fps = results["MediaPipe-Baseline"].fps

    for name, result in sorted_results:
        vs_baseline = (result.fps / baseline_fps * 100) if baseline_fps > 0 else 0

        status = (
            "✅"
            if result.fps >= mediapipe_fps * 0.8
            else "⚠️"
            if result.fps >= mediapipe_fps * 0.5
            else "❌"
        )

        print(f"{name:<35} {result.fps:<10.1f} {vs_baseline:>6.1f}%        {status}")

    print()
    print("Key Findings:")
    print(f"  • MediaPipe achieves {mediapipe_fps:.1f} FPS")
    baseline_percent = baseline_fps / mediapipe_fps * 100
    print(f"  • Baseline RTMPose-CPU achieves {baseline_fps:.1f} FPS")
    print(f"    ({baseline_percent:.1f}% of MediaPipe)")

    # Output results
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = {name: result.to_dict() for name, result in results.items()}

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {output_path}")

    return results


def run_comprehensive_benchmark(
    videos: dict[str, str],
    output: str | None = None,
    include_cuda: bool = False,
) -> dict[str, dict[str, BenchmarkResult]]:
    """Run benchmark on multiple video types.

    Args:
        videos: Dict mapping video type to path
        output: Optional JSON output path
        include_cuda: Whether to include CUDA benchmarks

    Returns:
        Dict mapping video type to results dict
    """
    all_results = {}

    for video_type, video_path in videos.items():
        print()
        print("=" * 70)
        print(f"BENCHMARKING: {video_type} Video")
        print("=" * 70)

        # Update VIDEO_PATH for this run
        global VIDEO_PATH
        VIDEO_PATH = video_path

        results = run_single_benchmark(video_path, video_type, include_cuda=include_cuda)
        all_results[video_type] = results

    # Print comprehensive summary
    print()
    print("=" * 70)
    print("COMPREHENSIVE RESULTS SUMMARY (Both DJ and CMJ)")
    print("=" * 70)
    print()

    # Calculate averages across video types
    config_names = list(all_results.values())[0].keys()

    print(f"{'Configuration':<35} {'DJ FPS':<12} {'CMJ FPS':<12} {'Avg FPS':<12} {'vs MP'}")
    print("-" * 85)

    for config in config_names:
        dj_fps = all_results["DJ"][config].fps
        cmj_fps = all_results["CMJ"][config].fps
        avg_fps = (dj_fps + cmj_fps) / 2
        dj_mp = all_results["DJ"]["MediaPipe-Baseline"].fps
        cmj_mp = all_results["CMJ"]["MediaPipe-Baseline"].fps
        mp_avg = (dj_mp + cmj_mp) / 2
        vs_mp = (avg_fps / mp_avg * 100) if mp_avg > 0 else 0

        status = "✅" if avg_fps >= mp_avg * 0.8 else "⚠️" if avg_fps >= mp_avg * 0.5 else "❌"
        print(
            f"{config:<35} {dj_fps:<12.1f} {cmj_fps:<12.1f} {avg_fps:<12.1f} {vs_mp:.0f}% {status}"
        )

    # Save combined results
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Flatten results for JSON export
        combined_data = {}
        for video_type, results in all_results.items():
            for config, result in results.items():
                key = f"{video_type}_{config}"
                combined_data[key] = result.to_dict()

        with open(output_path, "w") as f:
            json.dump(combined_data, f, indent=2)
        print(f"\nResults saved to: {output_path}")

    return all_results


def run_single_benchmark(
    video_path: str,
    video_type: str,
    include_cuda: bool = False,
) -> dict[str, BenchmarkResult]:
    """Run benchmark for a single video type."""
    print(f"Video: {Path(video_path).name}")
    print()

    results = {}

    # Configuration 1: Baseline - RTMPoseTracker with defaults
    print("Testing baseline RTMPoseTracker...")
    results["Baseline-RTMPose-Default"] = benchmark_config(
        "Baseline-RTMPose-Default",
        lambda: RTMPoseTracker(mode="lightweight", device="cpu"),
        video_path,
    )
    print(f"  FPS: {results['Baseline-RTMPose-Default'].fps:.1f}")

    # Configuration 2: MediaPipe baseline
    print("Testing MediaPipe baseline...")
    results["MediaPipe-Baseline"] = benchmark_config(
        "MediaPipe-Baseline",
        lambda: PoseTracker(strategy="image"),
        video_path,
    )
    print(f"  FPS: {results['MediaPipe-Baseline'].fps:.1f}")

    # Configuration 3: Optimized CPU - Sequential mode (8 intra, 1 inter)
    print("Testing Optimized CPU (Sequential mode)...")
    results["Optimized-Sequential-8x1"] = benchmark_config(
        "Optimized-Sequential-8x1",
        lambda: OptimizedCPUTracker(intra_threads=8, inter_threads=1),
        video_path,
    )
    print(f"  FPS: {results['Optimized-Sequential-8x1'].fps:.1f}")

    # Configuration 4: Optimized CPU - Reduced input size (160x160)
    print("Testing Optimized CPU (160x160)...")
    results["Optimized-InputSize-160x160"] = benchmark_config(
        "Optimized-InputSize-160x160",
        lambda: OptimizedCPUTracker(intra_threads=8, inter_threads=1, input_size=(160, 160)),
        video_path,
    )
    print(f"  FPS: {results['Optimized-InputSize-160x160'].fps:.1f}")

    # Configuration 5: Optimized CPU - Smaller input size (128x128)
    print("Testing Optimized CPU (128x128)...")
    results["Optimized-InputSize-128x128"] = benchmark_config(
        "Optimized-InputSize-128x128",
        lambda: OptimizedCPUTracker(intra_threads=8, inter_threads=1, input_size=(128, 128)),
        video_path,
    )
    print(f"  FPS: {results['Optimized-InputSize-128x128'].fps:.1f}")

    # Configuration 6: Optimized CPU - Parallel mode (4 intra, 2 inter)
    print("Testing Optimized CPU (Parallel mode)...")
    results["Optimized-Parallel-4x2"] = benchmark_config(
        "Optimized-Parallel-4x2",
        lambda: OptimizedCPUTracker(intra_threads=4, inter_threads=2),
        video_path,
    )
    print(f"  FPS: {results['Optimized-Parallel-4x2'].fps:.1f}")

    # CUDA configurations (if requested)
    if include_cuda:
        # RTMPose-S CUDA
        print("Testing RTMPose-S CUDA...")
        results["RTMPose-S-CUDA"] = benchmark_config(
            "RTMPose-S-CUDA",
            lambda: RTMPoseTracker(mode="lightweight", device="cuda"),
            video_path,
        )
        print(f"  FPS: {results['RTMPose-S-CUDA'].fps:.1f}")

        # RTMPose-M CUDA
        print("Testing RTMPose-M CUDA...")
        results["RTMPose-M-CUDA"] = benchmark_config(
            "RTMPose-M-CUDA",
            lambda: RTMPoseTracker(mode="balanced", device="cuda"),
            video_path,
        )
        print(f"  FPS: {results['RTMPose-M-CUDA'].fps:.1f}")

    return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark CPU optimizations for RTMPose")
    parser.add_argument(
        "--output",
        "-o",
        default="cpu_optimization_results.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--comprehensive",
        "-c",
        action="store_true",
        help="Run benchmark on both DJ and CMJ videos",
    )
    parser.add_argument(
        "--video",
        "-v",
        choices=["DJ", "CMJ"],
        help="Run benchmark on specific video type only",
    )
    parser.add_argument(
        "--cuda",
        action="store_true",
        help="Include CUDA benchmarks (RTMPose-S/M)",
    )

    args = parser.parse_args()

    if args.comprehensive:
        run_comprehensive_benchmark(TEST_VIDEOS, output=args.output, include_cuda=args.cuda)
    elif args.video:
        run_single_benchmark(TEST_VIDEOS[args.video], args.video, include_cuda=args.cuda)
    else:
        run_cpu_optimization_benchmark(output=args.output)


if __name__ == "__main__":
    main()
