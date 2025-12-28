#!/usr/bin/env python3
"""Quick benchmark of RTMO and custom input size configurations.

Tests:
1. RTMO-S (one-stage lightweight)
2. RTMPose-S custom input sizes (160x160, 128x128)
3. RTMO-M (one-stage balanced)

Uses single video for fast iteration.
"""

# Add parent directory for rtmpose_tracker import
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from rtmlib import Body

from kinemotion.core.pose import PoseTracker

sys.path.insert(0, str(Path(__file__).parent))

from rtmpose_tracker import RTMPoseTracker

# Project root for relative paths
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Single video for quick testing
VIDEO_PATH = str(PROJECT_ROOT / "samples/test-videos/dj-45-IMG_6739.mp4")


def benchmark_config(
    tracker_name: str,
    tracker_factory,
    video_path: str = VIDEO_PATH,
    warmup_frames: int = 3,
) -> dict:
    """Benchmark a single tracker configuration.

    Returns dict with fps, frame times, etc.
    """
    print(f"  Testing {tracker_name}...", end="", flush=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    # Warmup
    tracker = tracker_factory()
    for _ in range(warmup_frames):
        ret, frame = cap.read()
        if not ret:
            break
        tracker.process_frame(frame)
    tracker.close()

    # Benchmark
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    tracker = tracker_factory()
    frame_times = []
    successful = 0

    start = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        t0 = time.time()
        result = tracker.process_frame(frame)
        frame_time = time.time() - t0
        frame_times.append(frame_time)
        if result is not None:
            successful += 1

    total_time = time.time() - start
    cap.release()
    tracker.close()

    fps = len(frame_times) / total_time if total_time > 0 else 0
    avg_ms = np.mean(frame_times) * 1000

    print(f" {fps:.1f} FPS ({avg_ms:.1f} ms/frame)")
    return {
        "fps": fps,
        "avg_ms": avg_ms,
        "min_ms": np.min(frame_times) * 1000,
        "max_ms": np.max(frame_times) * 1000,
        "success_rate": successful / len(frame_times) if frame_times else 0,
    }


def main():
    print("=" * 70)
    print("EXTENDED BENCHMARK: RTMO + Custom Input Sizes")
    print("=" * 70)
    print(f"Video: {Path(VIDEO_PATH).name}")
    print()

    results = {}

    # Baseline: MediaPipe (use image mode to avoid timestamp issues)
    print("--- Baseline ---")
    results["MediaPipe"] = benchmark_config(
        "MediaPipe",
        lambda: PoseTracker(strategy="image"),
    )

    # Baseline: RTMPose-S lightweight (standard 192x256)
    print("\n--- RTMPose Two-Stage (Baseline) ---")
    results["RTMPose-S-192x256"] = benchmark_config(
        "RTMPose-S (192x256)",
        lambda: RTMPoseTracker(mode="lightweight", device="mps"),
    )

    # Test 1: RTMPose-S with smaller input sizes
    print("\n--- RTMPose-S: Custom Input Sizes ---")
    for size in [(160, 160), (128, 128)]:
        name = f"RTMPose-S-{size[0]}x{size[1]}"

        def make_tracker(size=size):
            return RTMPoseTracker(
                mode="lightweight",
                device="mps",
                pose_input_size=size,
            )

        results[name] = benchmark_config(name, make_tracker)

    # Test 2: RTMO-S (one-stage lightweight)
    print("\n--- RTMO One-Stage ---")

    class RTMOWrapper:
        """Wrapper to make RTMO Body compatible with benchmark."""

        def __init__(self, model_name, input_size):
            self.estimator = Body(
                pose=model_name,
                pose_input_size=input_size,
                backend="onnxruntime",
                device="mps",
                to_openpose=False,
            )

        def process_frame(self, frame):
            # RTMO returns keypoints, scores directly
            result = self.estimator(frame)
            if result and len(result) > 0:
                # Return non-None to indicate success
                return result[0]  # First person
            return None

        def close(self):
            pass

    def make_rtmo_s():
        return RTMOWrapper("rtmo-s_8xb32-600e_body7-640x640", (640, 640))

    results["RTMO-S"] = benchmark_config("RTMO-S (640x640)", make_rtmo_s)

    # Test 3: RTMO-M (one-stage balanced)
    def make_rtmo_m():
        return RTMOWrapper("rtmo-m_16xb16-600e_body7-640x640", (640, 640))

    results["RTMO-M"] = benchmark_config("RTMO-M (640x640)", make_rtmo_m)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Config':<25} {'FPS':<10} {'Frame (ms)':<12} {'vs MP':<10}")
    print("-" * 70)

    mp_fps = results["MediaPipe"]["fps"]

    for name, metrics in sorted(results.items(), key=lambda x: -x[1]["fps"]):
        vs_mp = (metrics["fps"] / mp_fps * 100) if mp_fps > 0 else 0
        status = "✅" if vs_mp >= 90 else "⚠️" if vs_mp >= 70 else "❌"
        print(
            f"{name:<25} {metrics['fps']:<10.1f} {metrics['avg_ms']:<12.1f} {vs_mp:<.1f}% {status}"
        )

    # Find best non-MediaPipe option
    best = max(
        [(n, m) for n, m in results.items() if n != "MediaPipe"],
        key=lambda x: x[1]["fps"],
    )
    print()
    print(f"🏆 Best RTMPose/RTMO: {best[0]} @ {best[1]['fps']:.1f} FPS")

    return results


if __name__ == "__main__":
    main()
