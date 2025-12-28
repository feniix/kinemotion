#!/usr/bin/env python3
"""Profile memory consumption for different pose trackers.

Measures peak memory usage during initialization and inference.
"""

from __future__ import annotations

import gc
import sys
import tracemalloc
from dataclasses import dataclass
from pathlib import Path

import cv2

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from optimized_cpu_tracker import OptimizedCPUTracker
from rtmpose_tracker import RTMPoseTracker

from kinemotion.core.pose import PoseTracker

# Project root for relative paths
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Test video
VIDEO_PATH = str(PROJECT_ROOT / "samples/test-videos/dj-45-IMG_6739.mp4")


@dataclass
class MemoryProfile:
    """Memory profile results."""

    config_name: str
    init_peak_mb: float
    inference_peak_mb: float
    total_peak_mb: float
    init_time_ms: float


def profile_tracker_memory(
    config_name: str,
    tracker_factory,
    video_path: str,
    num_frames: int = 50,
) -> MemoryProfile:
    """Profile memory usage for a tracker.

    Args:
        config_name: Name of the configuration
        tracker_factory: Function that creates the tracker
        video_path: Path to test video
        num_frames: Number of frames to process for inference profiling

    Returns:
        MemoryProfile with memory usage in MB
    """
    gc.collect()

    # Profile initialization
    tracemalloc.start()
    tracker = tracker_factory()
    init_peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024  # MB
    tracemalloc.stop()

    # Profile inference
    tracemalloc.start()
    cap = cv2.VideoCapture(video_path)
    for _ in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        _ = tracker.process_frame(frame)
    cap.release()
    tracker.close()
    inference_peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024  # MB
    tracemalloc.stop()

    return MemoryProfile(
        config_name=config_name,
        init_peak_mb=init_peak,
        inference_peak_mb=inference_peak,
        total_peak_mb=max(init_peak, inference_peak),
        init_time_ms=0,  # Not measured here
    )


def main():
    """Run memory profiling for all tracker configurations."""
    print("=" * 70)
    print("Memory Profiling for Pose Trackers")
    print("=" * 70)
    print(f"Video: {Path(VIDEO_PATH).name}")
    print("Frames: 50 (for inference profiling)")
    print()

    results = {}

    # MediaPipe baseline
    print("Profiling MediaPipe...")
    results["MediaPipe"] = profile_tracker_memory(
        "MediaPipe",
        lambda: PoseTracker(strategy="image"),
        VIDEO_PATH,
    )
    print(f"  Init: {results['MediaPipe'].init_peak_mb:.1f} MB")
    print(f"  Peak: {results['MediaPipe'].total_peak_mb:.1f} MB")

    # RTMPose CPU (default)
    print("\nProfiling RTMPose-CPU (default)...")
    results["RTMPose-CPU-Default"] = profile_tracker_memory(
        "RTMPose-CPU-Default",
        lambda: RTMPoseTracker(mode="lightweight", device="cpu"),
        VIDEO_PATH,
    )
    print(f"  Init: {results['RTMPose-CPU-Default'].init_peak_mb:.1f} MB")
    print(f"  Peak: {results['RTMPose-CPU-Default'].total_peak_mb:.1f} MB")

    # RTMPose CPU (optimized - sequential 8x1)
    print("\nProfiling RTMPose-CPU (optimized, sequential)...")
    results["RTMPose-CPU-Optimized"] = profile_tracker_memory(
        "RTMPose-CPU-Optimized",
        lambda: OptimizedCPUTracker(intra_threads=8, inter_threads=1),
        VIDEO_PATH,
    )
    print(f"  Init: {results['RTMPose-CPU-Optimized'].init_peak_mb:.1f} MB")
    print(f"  Peak: {results['RTMPose-CPU-Optimized'].total_peak_mb:.1f} MB")

    # RTMPose CUDA
    print("\nProfiling RTMPose-CUDA...")
    results["RTMPose-CUDA"] = profile_tracker_memory(
        "RTMPose-CUDA",
        lambda: RTMPoseTracker(mode="lightweight", device="cuda"),
        VIDEO_PATH,
    )
    print(f"  Init: {results['RTMPose-CUDA'].init_peak_mb:.1f} MB")
    print(f"  Peak: {results['RTMPose-CUDA'].total_peak_mb:.1f} MB")

    # Print summary table
    print()
    print("=" * 70)
    print("MEMORY USAGE SUMMARY")
    print("=" * 70)
    print()
    print(f"{'Configuration':<30} {'Init (MB)':<12} {'Peak (MB)':<12} {'Status'}")
    print("-" * 70)

    for name, result in sorted(results.items(), key=lambda x: x[1].total_peak_mb):
        if result.total_peak_mb < 500:
            status = "✅"
        elif result.total_peak_mb < 1000:
            status = "⚠️"
        else:
            status = "❌"
        print(f"{name:<30} {result.init_peak_mb:<12.1f} {result.total_peak_mb:<12.1f} {status}")

    return results


if __name__ == "__main__":
    main()
