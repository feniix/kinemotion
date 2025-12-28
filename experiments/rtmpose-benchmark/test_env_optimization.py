#!/usr/bin/env python3
"""Test environment variable optimization for RTMPose CPU performance.

This tests if setting ONNX Runtime environment variables before importing
rtmlib can improve CPU performance without modifying the library.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

# CRITICAL: Set environment variables BEFORE importing rtmlib or anything that uses it
os.environ["OMP_NUM_THREADS"] = "8"  # Physical cores of Ryzen 7 7800X3D
os.environ["MKL_NUM_THREADS"] = "8"  # MKL threading
os.environ["OMP_WAIT_POLICY"] = "ACTIVE"  # Reduce thread spawn overhead
os.environ["OPENBLAS_NUM_THREADS"] = "8"  # OpenBLAS threading
os.environ["VECLIB_MAXIMUM_THREADS"] = "8"  # macOS Accelerate framework
os.environ["NUMEXPR_NUM_THREADS"] = "8"  # NumExpr threading

# Now safe to import kinemotion modules
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from rtmpose_tracker import RTMPoseTracker

from kinemotion.core.pose import PoseTracker

# Project root for relative paths
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Test videos
TEST_VIDEOS = {
    "DJ": str(PROJECT_ROOT / "samples/test-videos/dj-45-IMG_6739.mp4"),
    "CMJ": str(PROJECT_ROOT / "samples/test-videos/cmj-45-IMG_6733.mp4"),
}


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


def benchmark_tracker(
    config_name: str,
    tracker_factory,
    video_path: str,
    warmup_frames: int = 5,
) -> BenchmarkResult:
    """Benchmark a single tracker configuration."""
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
        result = tracker.process_frame(frame)
        frame_time = perf_counter() - frame_start

        # Verify we got actual landmarks
        if result is None:
            print(f"    Warning: Frame {len(frame_times)} returned None")

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
    )


def main():
    """Run environment variable optimization test."""
    print("=" * 70)
    print("Environment Variable Optimization Test for RTMPose")
    print("=" * 70)
    print()
    print("Environment variables set:")
    print(f"  OMP_NUM_THREADS={os.environ.get('OMP_NUM_THREADS')}")
    print(f"  MKL_NUM_THREADS={os.environ.get('MKL_NUM_THREADS')}")
    print(f"  OMP_WAIT_POLICY={os.environ.get('OMP_WAIT_POLICY')}")
    print()

    results = {}

    for video_type, video_path in TEST_VIDEOS.items():
        print(f"Testing {video_type} video: {Path(video_path).name}")
        print("-" * 70)

        # MediaPipe baseline
        print("  Testing MediaPipe baseline...")
        key = f"{video_type}_MediaPipe"
        results[key] = benchmark_tracker(
            f"{video_type}_MediaPipe",
            lambda: PoseTracker(strategy="image"),
            video_path,
        )
        print(f"    FPS: {results[key].fps:.1f}")

        # RTMPose with environment variables
        print("  Testing RTMPose (with env vars)...")
        key = f"{video_type}_RTMPose-EnvVars"
        results[key] = benchmark_tracker(
            f"{video_type}_RTMPose-EnvVars",
            lambda: RTMPoseTracker(mode="lightweight", device="cpu"),
            video_path,
        )
        print(f"    FPS: {results[key].fps:.1f}")
        print()

    # Summary
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print()

    print(f"{'Video':<8} {'MediaPipe':<15} {'RTMPose-EnvVars':<20} {'Improvement':<12}")
    print("-" * 70)

    for video_type in ["DJ", "CMJ"]:
        mp_key = f"{video_type}_MediaPipe"
        rt_key = f"{video_type}_RTMPose-EnvVars"

        mp_fps = results[mp_key].fps
        rt_fps = results[rt_key].fps
        improvement = (rt_fps / mp_fps * 100) if mp_fps > 0 else 0

        status = "✅" if improvement >= 80 else "⚠️" if improvement >= 50 else "❌"
        print(f"{video_type:<8} {mp_fps:<15.1f} {rt_fps:<20.1f} {improvement:>6.1f}% {status}")

    # Compare with known baseline (without env vars)
    print()
    print("Comparison with known baseline (no env vars, default rtmlib settings):")
    print("  Baseline (no env vars): 19.2 FPS (39% of MediaPipe)")
    print()

    dj_mp = results["DJ_MediaPipe"].fps
    dj_rt = results["DJ_RTMPose-EnvVars"].fps
    dj_improvement = (dj_rt / dj_mp * 100) if dj_mp > 0 else 0

    print(f"Environment variable results: {dj_rt:.1f} FPS ({dj_improvement:.1f}% of MediaPipe)")

    if dj_rt > 25:
        print("  ✅ Environment variables HELPED significantly!")
    elif dj_rt > 20:
        print("  ⚠️  Environment variables helped somewhat")
    else:
        print("  ❌ Environment variables did NOT help - need ONNX session options")


if __name__ == "__main__":
    main()
