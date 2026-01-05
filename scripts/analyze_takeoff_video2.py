#!/usr/bin/env python3
"""Analyze takeoff detection for Video 2 to understand the -2 frame error."""

import sys
from pathlib import Path

import numpy as np

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from kinemotion.core.pose import MediaPipePoseTracker
from kinemotion.core.smoothing import compute_acceleration_from_derivative
from kinemotion.core.video_io import VideoProcessor
from kinemotion.cmj.analysis import compute_signed_velocity

# Ground truth
MANUAL_TAKEOFF = 108
VIDEO_PATH = project_root / "samples/test-videos/cmj-45-IMG_6734.mp4"


def process_video():
    """Process video and return positions/velocities."""
    positions = []

    with VideoProcessor(str(VIDEO_PATH)) as video:
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


def analyze_takeoff():
    """Analyze takeoff region in detail."""
    positions, fps = process_video()
    velocities = compute_signed_velocity(positions)
    accelerations = compute_acceleration_from_derivative(positions)

    peak_height_frame = int(np.argmin(positions))

    # Current takeoff detection
    takeoff_search_start = max(0, peak_height_frame - int(fps * 0.35))
    takeoff_search_end = peak_height_frame - 2
    takeoff_velocities = velocities[takeoff_search_start:takeoff_search_end]
    peak_vel_idx = int(np.argmin(takeoff_velocities))
    detected_takeoff = takeoff_search_start + peak_vel_idx

    print(f"Peak height frame: {peak_height_frame}")
    print(f"Search window: {takeoff_search_start} - {takeoff_search_end}")
    print(f"Detected takeoff: {detected_takeoff}")
    print(f"Manual takeoff: {MANUAL_TAKEOFF}")
    print(f"Error: {detected_takeoff - MANUAL_TAKEOFF}")

    print("\n" + "=" * 60)
    print("VELOCITY ANALYSIS AROUND TAKEOFF")
    print("=" * 60)

    # Analyze frames around takeoff
    start = max(0, MANUAL_TAKEOFF - 10)
    end = min(len(velocities), MANUAL_TAKEOFF + 5)

    print(f"\n{'Frame':<8} | {'Position':<10} | {'Velocity':<12} | {'Accel':<12} | Note")
    print("-" * 70)

    for i in range(start, end):
        pos = positions[i]
        vel = velocities[i]
        acc = accelerations[i]

        note = ""
        if i == detected_takeoff:
            note = "<-- DETECTED (peak upward velocity)"
        elif i == MANUAL_TAKEOFF:
            note = "<-- MANUAL (ground truth)"
        elif i == peak_height_frame:
            note = "<-- PEAK HEIGHT"

        print(f"{i:<8} | {pos:<10.4f} | {vel:<12.6f} | {acc:<12.6f} | {note}")

    # Find where velocity first becomes negative (upward motion starts)
    print("\n" + "=" * 60)
    print("TAKEOFF APPROACHES")
    print("=" * 60)

    # Method 1: Peak velocity (current)
    print(f"\n1. Peak upward velocity: frame {detected_takeoff}")

    # Method 2: Zero crossing (velocity sign change)
    # In normalized coords, negative velocity = moving up
    for i in range(MANUAL_TAKEOFF - 15, MANUAL_TAKEOFF + 5):
        if i > 0 and velocities[i-1] > 0 and velocities[i] < 0:
            print(f"2. Velocity zero crossing (pos→neg): frame {i}")
            break

    # Method 3: Max upward acceleration
    acc_window = accelerations[MANUAL_TAKEOFF - 15:MANUAL_TAKEOFF + 5]
    max_up_acc_idx = MANUAL_TAKEOFF - 15 + int(np.argmin(acc_window))
    print(f"3. Max upward acceleration: frame {max_up_acc_idx}")

    # Method 4: Velocity just before deceleration starts
    # Find where velocity magnitude starts decreasing
    for i in range(detected_takeoff, peak_height_frame):
        if velocities[i] > velocities[i-1]:  # velocity becoming less negative
            print(f"4. Velocity deceleration onset: frame {i-1}")
            break


if __name__ == "__main__":
    analyze_takeoff()
