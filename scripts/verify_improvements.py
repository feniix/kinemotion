#!/usr/bin/env python3
"""Verify the production code improvements against manual ground truth."""

import sys
from pathlib import Path

import numpy as np

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from kinemotion.core.pose import MediaPipePoseTracker
from kinemotion.core.smoothing import compute_acceleration_from_derivative
from kinemotion.core.video_io import VideoProcessor
from kinemotion.cmj.analysis import (
    LandingMethod,
    compute_signed_velocity,
    detect_cmj_phases,
)

# Ground truth from manual observations
GROUND_TRUTH = {
    "cmj-45-IMG_6733.mp4": {
        "standing_end": 64,
        "lowest_point": 88,
        "takeoff": 104,
        "landing": 142,
    },
    "cmj-45-IMG_6734.mp4": {
        "standing_end": 69,
        "lowest_point": 90,
        "takeoff": 108,
        "landing": 144,
    },
    "cmj-45-IMG_6735.mp4": {
        "standing_end": 58,
        "lowest_point": 78,
        "takeoff": 93,
        "landing": 130,
    },
}


def process_video(video_path: Path):
    """Process video and extract hip positions."""
    positions = []

    with VideoProcessor(str(video_path)) as video:
        fps = video.fps
        tracker = MediaPipePoseTracker()

        for frame_idx, frame in enumerate(video):
            timestamp_ms = int((frame_idx + 1) * 1000 / fps)
            result = tracker.process_frame(frame, timestamp_ms=timestamp_ms)
            if result:
                left_hip = result.get("left_hip")
                right_hip = result.get("right_hip")
                if left_hip is not None and right_hip is not None:
                    hip_y = (left_hip[1] + right_hip[1]) / 2
                    positions.append(hip_y)
                else:
                    positions.append(positions[-1] if positions else 0.5)
            else:
                positions.append(positions[-1] if positions else 0.5)

    return np.array(positions), fps


def compute_jump_height(takeoff, landing, fps):
    """Compute jump height from flight time."""
    flight_time = (landing - takeoff) / fps
    return 9.81 * flight_time**2 / 8 * 100


def verify():
    """Verify production code against ground truth."""
    video_dir = project_root / "samples/test-videos"

    print("Processing videos with production code...")
    print("=" * 90)

    all_phase_errors = {"standing_end": [], "lowest_point": [], "takeoff": [], "landing": []}
    height_errors = []

    print(f"\n{'Video':<20} | {'Phase':<12} | {'Detected':<10} | {'Manual':<10} | {'Error':<8}")
    print("-" * 70)

    for video_name, gt in GROUND_TRUTH.items():
        video_path = video_dir / video_name
        if not video_path.exists():
            print(f"{video_name}: NOT FOUND")
            continue

        positions, fps = process_video(video_path)

        # Use production detect_cmj_phases with CONTACT method
        result = detect_cmj_phases(positions, fps, landing_method=LandingMethod.CONTACT)

        if result is None:
            print(f"{video_name}: DETECTION FAILED")
            continue

        standing_end, lowest_point, takeoff, landing = result

        short_name = video_name.replace("cmj-45-", "").replace(".mp4", "")

        phases = [
            ("standing_end", standing_end, gt["standing_end"]),
            ("lowest_point", lowest_point, gt["lowest_point"]),
            ("takeoff", takeoff, gt["takeoff"]),
            ("landing", landing, gt["landing"]),
        ]

        for phase_name, detected, manual in phases:
            error = detected - manual
            all_phase_errors[phase_name].append(abs(error))
            print(f"{short_name:<20} | {phase_name:<12} | {detected:<10.0f} | {manual:<10} | {error:+.0f}")

        # Compute jump height
        manual_height = compute_jump_height(gt["takeoff"], gt["landing"], fps)
        detected_height = compute_jump_height(takeoff, landing, fps)
        height_error = detected_height - manual_height
        height_errors.append(abs(height_error))

        print(f"{short_name:<20} | {'JUMP HEIGHT':<12} | {detected_height:<10.1f} | {manual_height:<10.1f} | {height_error:+.1f} cm")
        print("-" * 70)

    # Summary
    print("\n" + "=" * 90)
    print("SUMMARY: Phase Detection MAE (frames)")
    print("=" * 90)

    for phase_name, errors in all_phase_errors.items():
        mae = np.mean(errors) if errors else 0
        print(f"{phase_name:<15}: {mae:.2f} frames")

    print(f"\n{'JUMP HEIGHT MAE':<15}: {np.mean(height_errors):.2f} cm")

    # Comparison with original
    print("\n" + "=" * 90)
    print("IMPROVEMENT SUMMARY")
    print("=" * 90)
    print(f"Original MAE:  5.18 cm")
    print(f"Improved MAE:  {np.mean(height_errors):.2f} cm")
    improvement = (1 - np.mean(height_errors) / 5.18) * 100
    print(f"Improvement:   {improvement:.1f}%")


if __name__ == "__main__":
    verify()
