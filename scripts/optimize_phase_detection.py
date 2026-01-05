#!/usr/bin/env python3
"""Optimize phase detection thresholds against manual ground truth."""

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


def find_landing_contact_tuned(
    velocities: np.ndarray,
    peak_height_frame: int,
    fps: float,
    onset_threshold: float = 0.3,
) -> float:
    """Landing detection with tunable threshold."""
    search_start = peak_height_frame
    search_end = min(len(velocities), peak_height_frame + int(fps * 1.0))

    if search_end <= search_start:
        return float(peak_height_frame + int(fps * 0.3))

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

    threshold = min_deriv * onset_threshold
    below_threshold = np.where(vel_derivative[: min_deriv_idx + 1] < threshold)[0]

    if len(below_threshold) > 0:
        landing_frame = search_start + below_threshold[0]
    else:
        landing_frame = search_start + min_deriv_idx

    return float(landing_frame)


def find_takeoff_frame_tuned(
    velocities: np.ndarray,
    peak_height_frame: int,
    fps: float,
    search_window: float = 0.35,
    offset_frames: int = 2,
) -> float:
    """Takeoff detection with tunable parameters."""
    takeoff_search_start = max(0, peak_height_frame - int(fps * search_window))
    takeoff_search_end = peak_height_frame - offset_frames

    takeoff_velocities = velocities[takeoff_search_start:takeoff_search_end]

    if len(takeoff_velocities) == 0:
        return float(peak_height_frame - int(fps * 0.3))

    vel_min = np.min(takeoff_velocities)
    vel_max = np.max(takeoff_velocities)
    vel_range = vel_max - vel_min

    if vel_range < 1e-6:
        return float((takeoff_search_start + takeoff_search_end) / 2.0)
    else:
        peak_vel_idx = int(np.argmin(takeoff_velocities))
        return float(takeoff_search_start + peak_vel_idx)


def find_takeoff_with_offset(
    velocities: np.ndarray,
    peak_height_frame: int,
    fps: float,
    frame_offset: int = 0,
) -> float:
    """Find takeoff then apply offset."""
    base_takeoff = find_takeoff_frame_tuned(velocities, peak_height_frame, fps)
    return base_takeoff + frame_offset


def process_video(video_path: Path):
    """Process video and return positions/velocities."""
    positions = []

    with VideoProcessor(str(video_path)) as video:
        fps = video.fps
        tracker = MediaPipePoseTracker()

        for frame_idx, frame in enumerate(video):
            # Ensure timestamp is always positive and increasing
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

    positions = np.array(positions)
    velocities = compute_signed_velocity(positions)
    accelerations = compute_acceleration_from_derivative(positions)

    return positions, velocities, accelerations, fps


def evaluate_thresholds():
    """Test different threshold values."""
    video_dir = project_root / "samples/test-videos"

    # Process all videos once
    video_data = {}
    for video_name in GROUND_TRUTH.keys():
        video_path = video_dir / video_name
        if video_path.exists():
            print(f"Processing {video_name}...")
            positions, velocities, accelerations, fps = process_video(video_path)

            # Find peak height (doesn't depend on thresholds)
            peak_height_frame = int(np.argmin(positions))

            video_data[video_name] = {
                "positions": positions,
                "velocities": velocities,
                "accelerations": accelerations,
                "fps": fps,
                "peak_height_frame": peak_height_frame,
            }

    print("\n" + "=" * 80)
    print("LANDING THRESHOLD OPTIMIZATION")
    print("=" * 80)

    # Test landing thresholds
    thresholds = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]

    print(f"\n{'Threshold':<12} | {'Video 1':<10} | {'Video 2':<10} | {'Video 3':<10} | {'MAE':<8} | {'Max Err':<8}")
    print("-" * 75)

    best_landing_threshold = 0.3
    best_landing_mae = float('inf')

    for threshold in thresholds:
        errors = []
        error_strs = []

        for video_name, gt in GROUND_TRUTH.items():
            if video_name not in video_data:
                continue

            data = video_data[video_name]
            detected = find_landing_contact_tuned(
                data["velocities"],
                data["peak_height_frame"],
                data["fps"],
                onset_threshold=threshold,
            )
            error = detected - gt["landing"]
            errors.append(error)
            error_strs.append(f"{error:+.0f}")

        mae = np.mean(np.abs(errors))
        max_err = np.max(np.abs(errors))

        if mae < best_landing_mae:
            best_landing_mae = mae
            best_landing_threshold = threshold

        marker = " <-- BEST" if mae == best_landing_mae else ""
        print(f"{threshold:<12.2f} | {error_strs[0]:<10} | {error_strs[1]:<10} | {error_strs[2]:<10} | {mae:<8.2f} | {max_err:<8.0f}{marker}")

    print(f"\nBest landing threshold: {best_landing_threshold} (MAE: {best_landing_mae:.2f} frames)")

    print("\n" + "=" * 80)
    print("TAKEOFF OFFSET OPTIMIZATION")
    print("=" * 80)

    # Test takeoff offsets
    offsets = [-3, -2, -1, 0, 1, 2, 3]

    print(f"\n{'Offset':<12} | {'Video 1':<10} | {'Video 2':<10} | {'Video 3':<10} | {'MAE':<8} | {'Max Err':<8}")
    print("-" * 75)

    best_takeoff_offset = 0
    best_takeoff_mae = float('inf')

    for offset in offsets:
        errors = []
        error_strs = []

        for video_name, gt in GROUND_TRUTH.items():
            if video_name not in video_data:
                continue

            data = video_data[video_name]
            detected = find_takeoff_with_offset(
                data["velocities"],
                data["peak_height_frame"],
                data["fps"],
                frame_offset=offset,
            )
            error = detected - gt["takeoff"]
            errors.append(error)
            error_strs.append(f"{error:+.0f}")

        mae = np.mean(np.abs(errors))
        max_err = np.max(np.abs(errors))

        if mae < best_takeoff_mae:
            best_takeoff_mae = mae
            best_takeoff_offset = offset

        marker = " <-- BEST" if mae == best_takeoff_mae else ""
        print(f"{offset:<12} | {error_strs[0]:<10} | {error_strs[1]:<10} | {error_strs[2]:<10} | {mae:<8.2f} | {max_err:<8.0f}{marker}")

    print(f"\nBest takeoff offset: {best_takeoff_offset} (MAE: {best_takeoff_mae:.2f} frames)")

    # Final comparison
    print("\n" + "=" * 80)
    print("FINAL COMPARISON: CURRENT vs OPTIMIZED")
    print("=" * 80)

    print("\nJump Height Results:")
    print(f"{'Video':<20} | {'Manual':<12} | {'Current':<12} | {'Optimized':<12} | {'Curr Err':<10} | {'Opt Err':<10}")
    print("-" * 90)

    current_errors = []
    optimized_errors = []

    for video_name, gt in GROUND_TRUTH.items():
        if video_name not in video_data:
            continue

        data = video_data[video_name]
        fps = data["fps"]

        # Manual
        manual_flight = (gt["landing"] - gt["takeoff"]) / fps
        manual_height = 9.81 * manual_flight**2 / 8 * 100

        # Current (threshold=0.3, offset=0)
        current_landing = find_landing_contact_tuned(
            data["velocities"], data["peak_height_frame"], fps, onset_threshold=0.3
        )
        current_takeoff = find_takeoff_with_offset(
            data["velocities"], data["peak_height_frame"], fps, frame_offset=0
        )
        current_flight = (current_landing - current_takeoff) / fps
        current_height = 9.81 * current_flight**2 / 8 * 100

        # Optimized
        opt_landing = find_landing_contact_tuned(
            data["velocities"], data["peak_height_frame"], fps, onset_threshold=best_landing_threshold
        )
        opt_takeoff = find_takeoff_with_offset(
            data["velocities"], data["peak_height_frame"], fps, frame_offset=best_takeoff_offset
        )
        opt_flight = (opt_landing - opt_takeoff) / fps
        opt_height = 9.81 * opt_flight**2 / 8 * 100

        current_err = current_height - manual_height
        opt_err = opt_height - manual_height

        current_errors.append(abs(current_err))
        optimized_errors.append(abs(opt_err))

        print(f"{video_name:<20} | {manual_height:<12.1f} | {current_height:<12.1f} | {opt_height:<12.1f} | {current_err:+10.1f} | {opt_err:+10.1f}")

    print("-" * 90)
    print(f"{'MAE':<20} | {'':<12} | {'':<12} | {'':<12} | {np.mean(current_errors):<10.1f} | {np.mean(optimized_errors):<10.1f}")

    improvement = (1 - np.mean(optimized_errors) / np.mean(current_errors)) * 100
    print(f"\nImprovement: {improvement:.1f}%")

    return best_landing_threshold, best_takeoff_offset


if __name__ == "__main__":
    evaluate_thresholds()
