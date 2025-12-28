#!/usr/bin/env python3
"""Compare analysis metrics between MediaPipe and OptimizedCPUTracker.

This script processes a video with both trackers and compares the resulting
pose landmarks to determine if the analysis metrics would be the same.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

# Add parent directory for kinemotion imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from optimized_cpu_tracker import OptimizedCPUTracker

from kinemotion.core.pose import PoseTracker

# Project root for video paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
VIDEO_PATH = str(PROJECT_ROOT / "samples/test-videos/dj-45-IMG_6739.mp4")

# Key landmarks for jump analysis (ankles and heels)
JUMP_LANDMARKS = [
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
]


def process_video_with_tracker(tracker, video_path: str, tracker_name: str) -> list:
    """Process entire video with given tracker.

    Returns:
        List of landmark dictionaries for each frame with valid pose.
    """
    print(f"  Processing with {tracker_name}...")
    cap = cv2.VideoCapture(video_path)
    landmarks = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        result = tracker.process_frame(frame)
        if result:
            landmarks.append(result)
        frame_count += 1

    cap.release()
    tracker.close()
    print(f"    Processed {frame_count} frames, {len(landmarks)} valid poses")
    return landmarks


def compare_landmarks(mp_landmarks: list, opt_landmarks: list) -> dict:
    """Compare landmarks between MediaPipe and OptimizedCPUTracker.

    Returns:
        Dictionary with comparison statistics.
    """
    # Estimate video dimensions (will normalize for comparison)
    video_w, video_h = 640, 480

    # Find overlapping frames
    n_frames = min(len(mp_landmarks), len(opt_landmarks))

    if n_frames == 0:
        return {
            "overlap_frames": 0,
            "landmark_stats": {},
        }

    # Track per-landmark statistics
    landmark_stats = {name: [] for name in JUMP_LANDMARKS}

    for i in range(n_frames):
        mp_frame = mp_landmarks[i]
        opt_frame = opt_landmarks[i]

        for name in JUMP_LANDMARKS:
            if name in mp_frame and name in opt_frame:
                mp_x, mp_y, _ = mp_frame[name]
                opt_x, opt_y, _ = opt_frame[name]

                # Calculate pixel difference
                dx = abs(mp_x - opt_x) * video_w
                dy = abs(mp_y - opt_y) * video_h
                dist = (dx**2 + dy**2) ** 0.5

                landmark_stats[name].append(dist)

    # Calculate summary statistics
    summary = {}
    for name, distances in landmark_stats.items():
        if distances:
            summary[name] = {
                "mean_px": np.mean(distances),
                "max_px": np.max(distances),
                "std_px": np.std(distances),
                "samples": len(distances),
            }

    return {
        "overlap_frames": n_frames,
        "landmark_stats": summary,
    }


def print_comparison(stats: dict):
    """Print comparison results."""
    print()
    print("=" * 70)
    print("LANDMARK POSITION COMPARISON")
    print("=" * 70)
    print("Measuring difference in landmark positions (in pixels)")
    print("Video dimensions assumed: 640x480")
    print()

    print(f"{'Landmark':<15} {'Mean Δ':<12} {'Max Δ':<12} {'Std Δ':<12} {'Frames':<10} {'Status'}")
    print("-" * 80)

    for name, data in stats["landmark_stats"].items():
        mean_delta = data["mean_px"]
        max_delta = data["max_px"]
        std_delta = data["std_px"]

        # Status based on mean difference
        if mean_delta < 5:
            status = "✅ Excellent"
        elif mean_delta < 10:
            status = "✅ Good"
        elif mean_delta < 20:
            status = "⚠️ Acceptable"
        else:
            status = "❌ Poor"

        # Format: name mean max std samples status
        print(f"{name:<15} {mean_delta:<12.1f} {max_delta:<12.1f} ", end="")
        print(f"{std_delta:<12.1f} {data['samples']:<10} {status}")

    print()
    print("INTERPRETATION:")
    print("  • Excellent (< 5px): Landmarks nearly identical")
    print("  • Good (< 10px): Minor differences, unlikely to affect metrics")
    print("  • Acceptable (< 20px): Moderate differences, may affect edge cases")
    print("  • Poor (> 20px): Significant differences, metrics may differ")
    print()


def analyze_metric_implications(stats: dict):
    """Analyze how landmark differences might affect jump metrics."""
    print("=" * 70)
    print("METRIC IMPLICATIONS")
    print("=" * 70)
    print()

    # Get mean differences across all landmarks
    all_means = [s["mean_px"] for s in stats["landmark_stats"].values()]
    overall_mean = np.mean(all_means)
    overall_max = np.max([s["max_px"] for s in stats["landmark_stats"].values()])

    # For drop jump analysis, the critical metrics are:
    # 1. Flight time (based on vertical position of feet)
    # 2. Ground contact time (based on when feet leave/touch ground)
    # 3. RSI (calculated from flight time / ground contact time)

    print(f"Overall mean landmark difference: {overall_mean:.1f} pixels")
    print(f"Overall max landmark difference: {overall_max:.1f} pixels")
    print()

    if overall_mean < 10:
        print("✅ METRIC EQUIVALENCE EXPECTED")
        print("   Landmark differences are small enough that:")
        print("   • Flight time should be nearly identical")
        print("   • Ground contact time should be nearly identical")
        print("   • RSI should be nearly identical")
        print("   • Differences < 1-2ms (negligible for practical purposes)")
    elif overall_mean < 20:
        print("⚠️  MINOR METRIC DIFFERENCES POSSIBLE")
        print("   Landmark differences may cause:")
        print("   • Flight time differences of ~1-5ms")
        print("   • Ground contact time differences of ~1-5ms")
        print("   • RSI differences of ~1-2%")
        print("   • Still within acceptable tolerances for most use cases")
    else:
        print("❌ SIGNIFICANT METRIC DIFFERENCES LIKELY")
        print("   Landmark differences may cause:")
        print("   • Flight time differences of > 5ms")
        print("   • Ground contact time differences of > 5ms")
        print("   • RSI differences of > 2-5%")
        print("   • May affect coaching decisions in edge cases")

    print()


def main():
    """Run metric comparison test."""
    print("=" * 70)
    print("METRIC COMPARISON: MediaPipe vs OptimizedCPUTracker")
    print("=" * 70)
    print(f"Video: {Path(VIDEO_PATH).name}")
    print()

    # Process with MediaPipe
    print("Step 1: Processing with MediaPipe baseline")
    mp_tracker = PoseTracker(strategy="image")
    mp_landmarks = process_video_with_tracker(mp_tracker, VIDEO_PATH, "MediaPipe")

    # Process with OptimizedCPUTracker
    print()
    print("Step 2: Processing with OptimizedCPUTracker")
    opt_tracker = OptimizedCPUTracker(intra_threads=8, inter_threads=1)
    opt_landmarks = process_video_with_tracker(opt_tracker, VIDEO_PATH, "OptimizedCPUTracker")

    # Compare
    print()
    print("Step 3: Comparing landmarks...")
    stats = compare_landmarks(mp_landmarks, opt_landmarks)

    # Print results
    print_comparison(stats)
    analyze_metric_implications(stats)

    # Final summary
    print("=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    print()
    print(f"MediaPipe valid frames: {len(mp_landmarks)}")
    print(f"OptimizedCPUTracker valid frames: {len(opt_landmarks)}")
    print(f"Overlap for comparison: {stats['overlap_frames']} frames")
    print()

    # Calculate overall mean difference
    if stats["landmark_stats"]:
        all_means = [s["mean_px"] for s in stats["landmark_stats"].values()]
        overall_mean = np.mean(all_means)

        if overall_mean < 10:
            print("✅ YES - The metrics should be ESSENTIALLY THE SAME")
            print(f"   (Mean landmark difference: {overall_mean:.1f}px < 10px threshold)")
        elif overall_mean < 20:
            print("⚠️  MOSTLY - The metrics should be SIMILAR with minor differences")
            print(f"   (Mean landmark difference: {overall_mean:.1f}px < 20px threshold)")
        else:
            print("❌ NO - The metrics may DIFFER significantly")
            print(f"   (Mean landmark difference: {overall_mean:.1f}px > 20px threshold)")


if __name__ == "__main__":
    main()
