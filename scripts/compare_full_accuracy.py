#!/usr/bin/env python3
"""Compare full jump height accuracy with different algorithm combinations."""

import sys
from pathlib import Path

import numpy as np
from scipy.signal import savgol_filter

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from kinemotion.core.pose import MediaPipePoseTracker
from kinemotion.core.smoothing import compute_acceleration_from_derivative
from kinemotion.core.video_io import VideoProcessor
from kinemotion.cmj.analysis import compute_signed_velocity

# Ground truth from manual observations
GROUND_TRUTH = {
    "cmj-45-IMG_6733.mp4": {"takeoff": 104, "landing": 142},
    "cmj-45-IMG_6734.mp4": {"takeoff": 108, "landing": 144},
    "cmj-45-IMG_6735.mp4": {"takeoff": 93, "landing": 130},
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


# Takeoff methods
def takeoff_peak_velocity(velocities, peak_height_frame, fps):
    """Current method: peak upward velocity."""
    takeoff_search_start = max(0, peak_height_frame - int(fps * 0.35))
    takeoff_search_end = peak_height_frame - 2
    takeoff_velocities = velocities[takeoff_search_start:takeoff_search_end]
    if len(takeoff_velocities) == 0:
        return peak_height_frame - int(fps * 0.3)
    peak_vel_idx = int(np.argmin(takeoff_velocities))
    return takeoff_search_start + peak_vel_idx


def takeoff_decel_onset(velocities, accelerations, peak_height_frame, fps):
    """Find when deceleration starts after peak velocity."""
    peak_vel_frame = takeoff_peak_velocity(velocities, peak_height_frame, fps)
    for i in range(peak_vel_frame, peak_height_frame):
        if accelerations[i] > 0:
            return i
    return peak_vel_frame


# Landing methods
def landing_contact(velocities, peak_height_frame, fps, threshold=0.10):
    """Landing using deceleration onset."""
    search_start = peak_height_frame
    search_end = min(len(velocities), peak_height_frame + int(fps * 1.0))

    if search_end <= search_start:
        return peak_height_frame + int(fps * 0.3)

    window_length = 5
    search_velocities = velocities[search_start:search_end]

    if len(search_velocities) < window_length:
        vel_derivative = np.diff(search_velocities, prepend=search_velocities[0])
    else:
        vel_derivative = savgol_filter(
            search_velocities, window_length, 2, deriv=1, delta=1.0, mode="interp"
        )

    min_deriv_idx = int(np.argmin(vel_derivative))
    min_deriv = vel_derivative[min_deriv_idx]

    threshold_val = min_deriv * threshold
    below_threshold = np.where(vel_derivative[: min_deriv_idx + 1] < threshold_val)[0]

    if len(below_threshold) > 0:
        return search_start + below_threshold[0]
    return search_start + min_deriv_idx


def compute_jump_height(takeoff, landing, fps):
    """Compute jump height from flight time."""
    flight_time = (landing - takeoff) / fps
    return 9.81 * flight_time**2 / 8 * 100


def analyze_combinations():
    """Compare different algorithm combinations."""
    video_dir = project_root / "samples/test-videos"

    print("Processing videos...")
    video_data = {}
    for video_name in GROUND_TRUTH.keys():
        video_path = video_dir / video_name
        if video_path.exists():
            positions, fps = process_video(video_path)
            velocities = compute_signed_velocity(positions)
            accelerations = compute_acceleration_from_derivative(positions)
            peak_height_frame = int(np.argmin(positions))
            video_data[video_name] = {
                "velocities": velocities,
                "accelerations": accelerations,
                "fps": fps,
                "peak": peak_height_frame,
            }

    print("\n" + "=" * 100)
    print("ALGORITHM COMBINATIONS COMPARISON")
    print("=" * 100)

    combinations = [
        ("PeakVel + 0.30", "peak_velocity", 0.30),  # Original
        ("PeakVel + 0.10", "peak_velocity", 0.10),  # Improved landing only
        ("DecelOnset + 0.10", "decel_onset", 0.10),  # Both improved
    ]

    print(f"\n{'Configuration':<20} | {'Video 1':<20} | {'Video 2':<20} | {'Video 3':<20} | {'MAE (cm)':<10}")
    print("-" * 100)

    for name, takeoff_method, landing_thresh in combinations:
        errors = []
        results = []

        for video_name, gt in GROUND_TRUTH.items():
            data = video_data[video_name]
            fps = data["fps"]

            # Manual height
            manual_height = compute_jump_height(gt["takeoff"], gt["landing"], fps)

            # Detected
            if takeoff_method == "peak_velocity":
                takeoff = takeoff_peak_velocity(data["velocities"], data["peak"], fps)
            else:
                takeoff = takeoff_decel_onset(
                    data["velocities"], data["accelerations"], data["peak"], fps
                )

            landing = landing_contact(data["velocities"], data["peak"], fps, landing_thresh)

            detected_height = compute_jump_height(takeoff, landing, fps)
            error = detected_height - manual_height
            errors.append(abs(error))

            results.append(f"{detected_height:.1f} ({error:+.1f})")

        mae = np.mean(errors)
        print(f"{name:<20} | {results[0]:<20} | {results[1]:<20} | {results[2]:<20} | {mae:<10.2f}")

    # Manual reference
    print("-" * 100)
    manual_heights = []
    for video_name, gt in GROUND_TRUTH.items():
        fps = video_data[video_name]["fps"]
        height = compute_jump_height(gt["takeoff"], gt["landing"], fps)
        manual_heights.append(f"{height:.1f}")
    print(f"{'Manual (reference)':<20} | {manual_heights[0]:<20} | {manual_heights[1]:<20} | {manual_heights[2]:<20} |")


if __name__ == "__main__":
    analyze_combinations()
