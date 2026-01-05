#!/usr/bin/env python3
"""Analyze takeoff detection pattern across all videos."""

import sys
from pathlib import Path

import numpy as np

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from kinemotion.core.pose import MediaPipePoseTracker
from kinemotion.core.smoothing import compute_acceleration_from_derivative
from kinemotion.core.video_io import VideoProcessor
from kinemotion.cmj.analysis import compute_signed_velocity

# Ground truth from manual observations
GROUND_TRUTH = {
    "cmj-45-IMG_6733.mp4": {"takeoff": 104},
    "cmj-45-IMG_6734.mp4": {"takeoff": 108},
    "cmj-45-IMG_6735.mp4": {"takeoff": 93},
}


def process_video(video_path: Path):
    """Process video and return positions/velocities."""
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


def find_takeoff_peak_velocity(velocities, peak_height_frame, fps):
    """Current method: peak upward velocity."""
    takeoff_search_start = max(0, peak_height_frame - int(fps * 0.35))
    takeoff_search_end = peak_height_frame - 2
    takeoff_velocities = velocities[takeoff_search_start:takeoff_search_end]
    peak_vel_idx = int(np.argmin(takeoff_velocities))
    return takeoff_search_start + peak_vel_idx


def find_takeoff_decel_onset(velocities, accelerations, peak_height_frame, fps):
    """New method: find when deceleration starts after peak velocity."""
    # First find peak velocity
    peak_vel_frame = find_takeoff_peak_velocity(velocities, peak_height_frame, fps)

    # Look forward from peak velocity to find deceleration onset
    # Deceleration = positive acceleration (in normalized coords)
    for i in range(peak_vel_frame, peak_height_frame):
        if accelerations[i] > 0:
            return i
    return peak_vel_frame


def find_takeoff_velocity_decrease(velocities, peak_height_frame, fps):
    """Alternative: find when velocity magnitude starts decreasing."""
    peak_vel_frame = find_takeoff_peak_velocity(velocities, peak_height_frame, fps)

    for i in range(peak_vel_frame + 1, peak_height_frame):
        # Velocity becoming less negative = slowing down
        if velocities[i] > velocities[i-1]:
            return i
    return peak_vel_frame


def analyze_videos():
    """Analyze all videos."""
    video_dir = project_root / "samples/test-videos"

    print("=" * 90)
    print("TAKEOFF DETECTION METHOD COMPARISON")
    print("=" * 90)
    print(f"\n{'Video':<20} | {'Manual':<8} | {'PeakVel':<8} | {'Err':<6} | {'DecelOnset':<10} | {'Err':<6} | {'VelDecr':<8} | {'Err':<6}")
    print("-" * 90)

    for video_name, gt in GROUND_TRUTH.items():
        video_path = video_dir / video_name
        if not video_path.exists():
            continue

        positions, fps = process_video(video_path)
        velocities = compute_signed_velocity(positions)
        accelerations = compute_acceleration_from_derivative(positions)
        peak_height_frame = int(np.argmin(positions))

        manual = gt["takeoff"]
        peak_vel = find_takeoff_peak_velocity(velocities, peak_height_frame, fps)
        decel_onset = find_takeoff_decel_onset(velocities, accelerations, peak_height_frame, fps)
        vel_decr = find_takeoff_velocity_decrease(velocities, peak_height_frame, fps)

        short_name = video_name.replace("cmj-45-", "").replace(".mp4", "")
        print(f"{short_name:<20} | {manual:<8} | {peak_vel:<8} | {peak_vel - manual:+6} | {decel_onset:<10} | {decel_onset - manual:+6} | {vel_decr:<8} | {vel_decr - manual:+6}")

    print("-" * 90)


if __name__ == "__main__":
    analyze_videos()
