#!/usr/bin/env python3
"""
Validation script for foot velocity landing detection.

Compares the current acceleration-based landing detection with a new
foot velocity-based approach that should detect landing 1-4 frames earlier.

Research basis:
- FootNet (2021): 5ms RMSE using foot velocity for contact detection
- Force plates define landing at 10-50N (initial touch)
- Current algorithm detects maximum deceleration (full impact)
"""

import sys
from pathlib import Path

import numpy as np
from scipy.signal import savgol_filter

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from kinemotion.cmj.analysis import (
    compute_signed_velocity,
    detect_cmj_phases,
    find_landing_frame,
)
from kinemotion.core.pipeline_utils import extract_vertical_positions
from kinemotion.core.pose import PoseTrackerFactory
from kinemotion.core.smoothing import (
    compute_acceleration_from_derivative,
    smooth_landmarks,
)
from kinemotion.core.video_io import VideoProcessor


def find_landing_frame_foot_position_minimum(
    positions: np.ndarray,
    peak_height_frame: int,
    fps: float,
    window_length: int = 3,
) -> tuple[float, dict]:
    """
    Find landing by detecting when foot position reaches local minimum.

    Force-plate equivalent: At initial contact (10-50N), the foot STOPS descending.
    This is the earliest detectable signal - before any deceleration is visible.

    In normalized coordinates (y increases downward):
    - During descent: foot y is INCREASING (moving down)
    - At contact: foot y reaches LOCAL MAXIMUM (lowest point physically)
    - After contact: foot y may decrease slightly (rebound) or stabilize

    Args:
        positions: Foot vertical positions (normalized, y increases downward)
        peak_height_frame: Frame index of peak jump height
        fps: Video frame rate
        window_length: Window for local maximum detection

    Returns:
        Tuple of (landing_frame, debug_info)
    """
    debug_info = {}

    # Search window: after peak height
    search_start = peak_height_frame + 5  # Skip a few frames after peak
    search_end = min(len(positions), peak_height_frame + int(fps * 0.5))

    if search_end <= search_start:
        return float(peak_height_frame + int(fps * 0.3)), {"error": "empty_window"}

    search_positions = positions[search_start:search_end]

    # Find local maxima (foot at lowest physical point = highest y value)
    # Use simple approach: find where position stops increasing
    for i in range(1, len(search_positions) - 1):
        # Check if this is a local maximum (foot stopped descending)
        if search_positions[i] >= search_positions[i-1] and search_positions[i] >= search_positions[i+1]:
            # Verify it's significant (not just noise)
            if search_positions[i] > search_positions[0]:  # Higher than start of search
                landing_frame = search_start + i
                debug_info["detection_method"] = "position_local_max"
                debug_info["landing_position"] = float(positions[landing_frame])
                return float(landing_frame), debug_info

    # Fallback: find global maximum in search window
    max_idx = int(np.argmax(search_positions))
    landing_frame = search_start + max_idx
    debug_info["detection_method"] = "position_global_max"
    debug_info["landing_position"] = float(positions[landing_frame])

    return float(landing_frame), debug_info


def find_landing_frame_velocity_zero_crossing(
    velocities: np.ndarray,
    peak_height_frame: int,
    fps: float,
) -> tuple[float, dict]:
    """
    Find landing by detecting when foot velocity crosses zero.

    Force-plate equivalent: At initial contact, foot transitions from
    "falling" (positive velocity in normalized coords) to "stopped" (zero).

    This is more precise than waiting for velocity to drop below a threshold.

    Args:
        velocities: Signed foot velocities (positive = falling in norm coords)
        peak_height_frame: Frame index of peak jump height
        fps: Video frame rate

    Returns:
        Tuple of (landing_frame, debug_info)
    """
    debug_info = {}

    # Search window
    search_start = peak_height_frame + 5
    search_end = min(len(velocities), peak_height_frame + int(fps * 0.5))

    if search_end <= search_start:
        return float(peak_height_frame + int(fps * 0.3)), {"error": "empty_window"}

    search_velocities = velocities[search_start:search_end]

    # Find peak falling velocity first
    max_falling_idx = int(np.argmax(search_velocities))
    max_falling_vel = search_velocities[max_falling_idx]
    debug_info["max_falling_velocity"] = float(max_falling_vel)
    debug_info["max_falling_frame"] = search_start + max_falling_idx

    # Search for zero crossing AFTER peak falling velocity
    post_peak_velocities = search_velocities[max_falling_idx:]

    # Find first frame where velocity <= 0 (stopped or rebounding)
    zero_crossing = np.where(post_peak_velocities <= 0)[0]

    if len(zero_crossing) > 0:
        landing_rel_idx = zero_crossing[0]
        landing_frame = search_start + max_falling_idx + landing_rel_idx
        debug_info["detection_method"] = "velocity_zero_crossing"
        debug_info["landing_velocity"] = float(velocities[int(landing_frame)])
    else:
        # Fallback: find minimum velocity (closest to zero)
        min_vel_idx = int(np.argmin(np.abs(post_peak_velocities)))
        landing_frame = search_start + max_falling_idx + min_vel_idx
        debug_info["detection_method"] = "min_abs_velocity"
        debug_info["landing_velocity"] = float(velocities[int(landing_frame)])

    return float(landing_frame), debug_info


def find_landing_frame_combined_early(
    positions: np.ndarray,
    velocities: np.ndarray,
    peak_height_frame: int,
    fps: float,
) -> tuple[float, dict]:
    """
    Combined approach: earliest detection from multiple signals.

    Takes the EARLIEST landing frame detected by:
    1. Foot position minimum (local max in normalized coords)
    2. Velocity zero crossing
    3. Velocity derivative onset

    This mimics force plate behavior which detects the very first moment
    of contact, regardless of which signal shows it first.

    Args:
        positions: Foot vertical positions
        velocities: Foot vertical velocities
        peak_height_frame: Frame index of peak jump height
        fps: Video frame rate

    Returns:
        Tuple of (landing_frame, debug_info)
    """
    debug_info = {}

    # Get all candidate detections
    pos_landing, pos_debug = find_landing_frame_foot_position_minimum(
        positions, peak_height_frame, fps
    )
    vel_landing, vel_debug = find_landing_frame_velocity_zero_crossing(
        velocities, peak_height_frame, fps
    )
    deriv_landing, deriv_debug = find_landing_frame_velocity_derivative(
        velocities, peak_height_frame, fps
    )

    candidates = {
        "position_min": pos_landing,
        "velocity_zero": vel_landing,
        "velocity_deriv": deriv_landing,
    }

    debug_info["candidates"] = {k: float(v) for k, v in candidates.items()}

    # Take earliest (minimum frame number)
    best_method = min(candidates, key=candidates.get)
    landing_frame = candidates[best_method]

    debug_info["detection_method"] = f"combined_early ({best_method})"
    debug_info["selected_method"] = best_method

    return float(landing_frame), debug_info


def find_landing_frame_foot_velocity(
    velocities: np.ndarray,
    peak_height_frame: int,
    fps: float,
    velocity_threshold_ratio: float = 0.15,
) -> tuple[float, dict]:
    """
    Find landing frame using foot velocity zero-crossing.

    Detects initial ground contact by finding where foot vertical velocity
    transitions from "falling fast" (high positive) to "near zero" (stopped).

    This should detect landing 1-4 frames EARLIER than acceleration-based
    detection because:
    - Foot stops moving when it touches ground (physics-based)
    - Hip/COM deceleration happens AFTER foot contact (kinematic chain delay)

    Args:
        velocities: Signed foot vertical velocities (positive = downward)
        peak_height_frame: Frame index of peak jump height
        fps: Video frame rate
        velocity_threshold_ratio: Threshold as ratio of max falling velocity

    Returns:
        Tuple of (landing_frame, debug_info)
    """
    debug_info = {}

    # Search window: peak height to +0.6s (typical flight is 0.3-0.5s)
    search_start = peak_height_frame
    search_end = min(len(velocities), peak_height_frame + int(fps * 0.6))

    if search_end <= search_start:
        return float(peak_height_frame + int(fps * 0.3)), {"error": "empty_window"}

    search_velocities = velocities[search_start:search_end]

    # Find peak falling velocity (max positive velocity during descent)
    max_falling_vel = np.max(search_velocities)
    max_falling_idx = int(np.argmax(search_velocities))
    debug_info["max_falling_velocity"] = float(max_falling_vel)
    debug_info["max_falling_frame"] = search_start + max_falling_idx

    if max_falling_vel <= 0:
        # No falling detected, fallback
        return float(peak_height_frame + int(fps * 0.3)), {"error": "no_falling"}

    # Threshold: velocity drops below X% of max falling velocity
    threshold = max_falling_vel * velocity_threshold_ratio
    debug_info["velocity_threshold"] = float(threshold)

    # Search for threshold crossing AFTER peak falling velocity
    post_peak_start = max_falling_idx
    post_peak_velocities = search_velocities[post_peak_start:]

    # Find first frame where velocity drops below threshold
    below_threshold = np.where(post_peak_velocities < threshold)[0]

    if len(below_threshold) > 0:
        landing_rel_idx = below_threshold[0]
        landing_frame = search_start + post_peak_start + landing_rel_idx
        debug_info["detection_method"] = "velocity_threshold"
    else:
        # Fallback: find minimum velocity (closest to zero or negative)
        min_vel_idx = int(np.argmin(post_peak_velocities))
        landing_frame = search_start + post_peak_start + min_vel_idx
        debug_info["detection_method"] = "min_velocity_fallback"

    debug_info["landing_velocity"] = float(velocities[int(landing_frame)])

    return float(landing_frame), debug_info


def find_landing_frame_foot_deceleration(
    positions: np.ndarray,
    peak_height_frame: int,
    fps: float,
    window_length: int = 5,
) -> tuple[float, dict]:
    """
    Find landing using foot deceleration (acceleration of foot landmark).

    Key insight: At landing, the FOOT experiences maximum deceleration BEFORE
    the hip does (kinematic chain). So foot acceleration spike should be earlier.

    Args:
        positions: Foot vertical positions
        peak_height_frame: Frame index of peak jump height
        fps: Video frame rate
        window_length: Smoothing window

    Returns:
        Tuple of (landing_frame, debug_info)
    """
    debug_info = {}

    # Compute foot acceleration
    if len(positions) < window_length:
        vel = np.diff(positions, prepend=positions[0])
        acc = np.diff(vel, prepend=vel[0])
    else:
        if window_length % 2 == 0:
            window_length += 1
        acc = savgol_filter(positions, window_length, 2, deriv=2, delta=1.0, mode="interp")

    # Search window
    search_start = peak_height_frame
    search_end = min(len(acc), peak_height_frame + int(fps * 0.6))

    if search_end <= search_start:
        return float(peak_height_frame + int(fps * 0.3)), {"error": "empty_window"}

    search_acc = acc[search_start:search_end]

    # At landing: foot experiences NEGATIVE acceleration (deceleration)
    # This is the impact spike - find minimum acceleration
    min_acc_idx = int(np.argmin(search_acc))
    min_acc = search_acc[min_acc_idx]

    debug_info["min_acceleration"] = float(min_acc)
    debug_info["detection_method"] = "foot_deceleration_spike"

    landing_frame = search_start + min_acc_idx
    debug_info["landing_acceleration"] = float(acc[int(landing_frame)])

    return float(landing_frame), debug_info


def find_landing_frame_velocity_derivative(
    velocities: np.ndarray,
    peak_height_frame: int,
    fps: float,
    window_length: int = 5,
) -> tuple[float, dict]:
    """
    Find landing by detecting when foot velocity STARTS to decrease rapidly.

    Instead of waiting for velocity to reach near-zero, detect the onset of
    rapid deceleration (where d(velocity)/dt becomes most negative).

    This approach finds the BEGINNING of the landing impact, not the end.

    Args:
        velocities: Foot vertical velocities
        peak_height_frame: Frame index of peak jump height
        fps: Video frame rate
        window_length: Smoothing window for derivative

    Returns:
        Tuple of (landing_frame, debug_info)
    """
    debug_info = {}

    # Compute velocity derivative (= acceleration, but directly from velocity)
    if len(velocities) < window_length:
        vel_derivative = np.diff(velocities, prepend=velocities[0])
    else:
        if window_length % 2 == 0:
            window_length += 1
        vel_derivative = savgol_filter(
            velocities, window_length, 2, deriv=1, delta=1.0, mode="interp"
        )

    # Search window: from peak height to typical landing time
    search_start = peak_height_frame
    search_end = min(len(vel_derivative), peak_height_frame + int(fps * 0.6))

    if search_end <= search_start:
        return float(peak_height_frame + int(fps * 0.3)), {"error": "empty_window"}

    search_derivative = vel_derivative[search_start:search_end]

    # Find where velocity is decreasing most rapidly (most negative derivative)
    # This is the START of the deceleration (impact onset)
    min_deriv_idx = int(np.argmin(search_derivative))
    min_deriv = search_derivative[min_deriv_idx]

    debug_info["min_velocity_derivative"] = float(min_deriv)
    debug_info["min_derivative_frame"] = search_start + min_deriv_idx

    # To find onset, look for where derivative drops below threshold
    # before the minimum point
    threshold = min_deriv * 0.3  # 30% of max deceleration rate
    below_threshold = np.where(search_derivative[:min_deriv_idx + 1] < threshold)[0]

    if len(below_threshold) > 0:
        # First frame where deceleration exceeds threshold
        landing_frame = search_start + below_threshold[0]
        debug_info["detection_method"] = "deceleration_onset"
    else:
        # Fallback to minimum derivative point
        landing_frame = search_start + min_deriv_idx
        debug_info["detection_method"] = "max_deceleration"

    return float(landing_frame), debug_info


def find_landing_frame_foot_hip_divergence(
    foot_positions: np.ndarray,
    hip_positions: np.ndarray,
    peak_height_frame: int,
    fps: float,
    window_length: int = 5,
) -> tuple[float, dict]:
    """
    Find landing using foot-hip divergence rate.

    During flight, foot and hip move together (same velocity).
    At landing, foot stops but hip continues briefly, causing divergence.

    Args:
        foot_positions: Foot vertical positions
        hip_positions: Hip vertical positions
        peak_height_frame: Frame index of peak jump height
        fps: Video frame rate
        window_length: Smoothing window

    Returns:
        Tuple of (landing_frame, debug_info)
    """
    debug_info = {}

    # Compute leg extension (gap between hip and foot)
    gap = hip_positions - foot_positions

    # Compute rate of change of gap (divergence velocity)
    if len(gap) < window_length:
        gap_velocity = np.diff(gap, prepend=gap[0])
    else:
        if window_length % 2 == 0:
            window_length += 1
        gap_velocity = savgol_filter(gap, window_length, 2, deriv=1, delta=1.0, mode="interp")

    # Search window
    search_start = peak_height_frame
    search_end = min(len(gap_velocity), peak_height_frame + int(fps * 0.6))

    if search_end <= search_start:
        return float(peak_height_frame + int(fps * 0.3)), {"error": "empty_window"}

    search_gap_vel = gap_velocity[search_start:search_end]

    # At landing: gap_velocity spikes POSITIVE (hip continues, foot stops)
    # This creates leg compression as hip catches up to stopped foot
    max_divergence_idx = int(np.argmax(search_gap_vel))
    max_divergence = search_gap_vel[max_divergence_idx]

    debug_info["max_divergence"] = float(max_divergence)
    debug_info["max_divergence_frame"] = search_start + max_divergence_idx

    # Use threshold to find onset of divergence
    threshold = max_divergence * 0.3
    above_threshold = np.where(search_gap_vel > threshold)[0]

    if len(above_threshold) > 0:
        landing_frame = search_start + above_threshold[0]
        debug_info["detection_method"] = "divergence_onset"
    else:
        landing_frame = search_start + max_divergence_idx
        debug_info["detection_method"] = "max_divergence"

    return float(landing_frame), debug_info


def analyze_video(video_path: str, ground_truth: dict | None = None) -> dict:
    """
    Analyze a video and compare landing detection methods.

    Args:
        video_path: Path to video file
        ground_truth: Optional dict with 'landing' frame number

    Returns:
        Dict with comparison results
    """
    print(f"\n{'='*60}")
    print(f"Analyzing: {Path(video_path).name}")
    print(f"{'='*60}")

    # Process video
    with VideoProcessor(video_path) as video:
        fps = video.fps
        print(f"FPS: {fps:.1f}")

        # Create pose tracker
        tracker = PoseTrackerFactory.create()

        # Extract landmarks (VideoProcessor is iterable)
        landmarks_sequence = []
        for frame in video:
            result = tracker.process_frame(frame)
            landmarks_sequence.append(result)

        tracker.close()

        # Smooth landmarks
        smoothed_landmarks = smooth_landmarks(landmarks_sequence, window_length=5, polyorder=2)

        # Extract positions
        hip_positions, _ = extract_vertical_positions(smoothed_landmarks, target="hip")
        foot_positions, _ = extract_vertical_positions(smoothed_landmarks, target="foot")

        # Compute derivatives for hip (current method)
        hip_velocities = compute_signed_velocity(hip_positions, window_length=5, polyorder=2)
        hip_accelerations = compute_acceleration_from_derivative(hip_positions, window_length=5, polyorder=2)

        # Compute derivatives for foot (new method)
        foot_velocities = compute_signed_velocity(foot_positions, window_length=5, polyorder=2)

        # Find peak height
        peak_height_frame = int(np.argmin(hip_positions))
        print(f"Peak height frame: {peak_height_frame}")

        # Method 1: Current (acceleration-based on foot positions)
        current_landing = find_landing_frame(
            compute_acceleration_from_derivative(foot_positions),
            compute_signed_velocity(foot_positions),
            peak_height_frame,
            fps,
        )

        # Method 2: Foot velocity threshold
        fv_landing, fv_debug = find_landing_frame_foot_velocity(
            foot_velocities,
            peak_height_frame,
            fps,
        )

        # Method 3: Foot-hip divergence
        div_landing, div_debug = find_landing_frame_foot_hip_divergence(
            foot_positions,
            hip_positions,
            peak_height_frame,
            fps,
        )

        # Method 4: Foot deceleration spike
        foot_decel_landing, foot_decel_debug = find_landing_frame_foot_deceleration(
            foot_positions,
            peak_height_frame,
            fps,
        )

        # Method 5: Velocity derivative (deceleration onset)
        vel_deriv_landing, vel_deriv_debug = find_landing_frame_velocity_derivative(
            foot_velocities,
            peak_height_frame,
            fps,
        )

        # Method 6: Foot position minimum (force-plate equivalent)
        pos_min_landing, pos_min_debug = find_landing_frame_foot_position_minimum(
            foot_positions,
            peak_height_frame,
            fps,
        )

        # Method 7: Velocity zero crossing (force-plate equivalent)
        vel_zero_landing, vel_zero_debug = find_landing_frame_velocity_zero_crossing(
            foot_velocities,
            peak_height_frame,
            fps,
        )

        # Method 8: Combined early (takes earliest of multiple signals)
        combined_landing, combined_debug = find_landing_frame_combined_early(
            foot_positions,
            foot_velocities,
            peak_height_frame,
            fps,
        )

        # Results
        results = {
            "video": Path(video_path).name,
            "fps": fps,
            "peak_height_frame": peak_height_frame,
            "current_landing": current_landing,
            "foot_velocity_landing": fv_landing,
            "divergence_landing": div_landing,
            "foot_decel_landing": foot_decel_landing,
            "vel_deriv_landing": vel_deriv_landing,
            "pos_min_landing": pos_min_landing,
            "vel_zero_landing": vel_zero_landing,
            "combined_landing": combined_landing,
            "fv_debug": fv_debug,
            "div_debug": div_debug,
            "foot_decel_debug": foot_decel_debug,
            "vel_deriv_debug": vel_deriv_debug,
            "pos_min_debug": pos_min_debug,
            "vel_zero_debug": vel_zero_debug,
            "combined_debug": combined_debug,
        }

        # Comparison
        print(f"\n--- Landing Detection Comparison ---")
        print(f"{'Method':<25} {'Frame':>8} {'Time':>10}")
        print("-" * 45)
        print(f"{'Current (foot accel)':<25} {current_landing:>8.1f} {(current_landing/fps)*1000:>8.0f}ms")
        print(f"{'Foot velocity threshold':<25} {fv_landing:>8.1f} {(fv_landing/fps)*1000:>8.0f}ms")
        print(f"{'Foot-hip divergence':<25} {div_landing:>8.1f} {(div_landing/fps)*1000:>8.0f}ms")
        print(f"{'Foot decel spike':<25} {foot_decel_landing:>8.1f} {(foot_decel_landing/fps)*1000:>8.0f}ms")
        print(f"{'Vel deriv onset':<25} {vel_deriv_landing:>8.1f} {(vel_deriv_landing/fps)*1000:>8.0f}ms")
        print("-" * 45)
        print(f"{'★ Position minimum':<25} {pos_min_landing:>8.1f} {(pos_min_landing/fps)*1000:>8.0f}ms")
        print(f"{'★ Velocity zero-cross':<25} {vel_zero_landing:>8.1f} {(vel_zero_landing/fps)*1000:>8.0f}ms")
        print(f"{'★ Combined early':<25} {combined_landing:>8.1f} {(combined_landing/fps)*1000:>8.0f}ms")

        # Delta from current
        print(f"\nDelta from current (negative = earlier):")
        deltas = [
            ("Position minimum", pos_min_landing - current_landing),
            ("Velocity zero-cross", vel_zero_landing - current_landing),
            ("Combined early", combined_landing - current_landing),
            ("Vel deriv onset", vel_deriv_landing - current_landing),
        ]
        for name, delta in deltas:
            print(f"  {name:<20}: {delta:+.1f} frames ({delta/fps*1000:+.0f}ms)")

        if ground_truth and "landing" in ground_truth:
            gt = ground_truth["landing"]
            results["ground_truth"] = gt
            print(f"\nGround truth: Frame {gt}")
            print(f"  Current error:       {current_landing - gt:+.1f} frames ({(current_landing-gt)/fps*1000:+.0f}ms)")
            print(f"  Foot velocity:       {fv_landing - gt:+.1f} frames ({(fv_landing-gt)/fps*1000:+.0f}ms)")
            print(f"  Foot-hip div:        {div_landing - gt:+.1f} frames ({(div_landing-gt)/fps*1000:+.0f}ms)")
            print(f"  Foot decel spike:    {foot_decel_landing - gt:+.1f} frames ({(foot_decel_landing-gt)/fps*1000:+.0f}ms)")
            print(f"  Vel deriv onset:     {vel_deriv_landing - gt:+.1f} frames ({(vel_deriv_landing-gt)/fps*1000:+.0f}ms)")

            # Find best method
            errors = {
                "Current": abs(current_landing - gt),
                "Foot velocity": abs(fv_landing - gt),
                "Foot-hip div": abs(div_landing - gt),
                "Foot decel": abs(foot_decel_landing - gt),
                "Vel deriv": abs(vel_deriv_landing - gt),
            }
            best_method = min(errors, key=errors.get)
            print(f"\n  ★ Best method: {best_method} (error: {errors[best_method]:.1f} frames)")

        # Debug info
        print(f"\nDebug info:")
        print(f"  Foot velocity: {fv_debug}")
        print(f"  Divergence: {div_debug}")
        print(f"  Foot decel: {foot_decel_debug}")
        print(f"  Vel deriv: {vel_deriv_debug}")

        return results


def load_ground_truth(project_root: Path) -> dict:
    """Load ground truth from JSON file."""
    gt_file = project_root / "samples" / "validation" / "ground_truth.json"
    if gt_file.exists():
        import json
        with open(gt_file) as f:
            data = json.load(f)
        # Convert to lookup dict by video path
        return {
            ann["video_file"]: ann["ground_truth"]
            for ann in data["annotations"]
        }
    return {}


def main():
    """Main validation script."""
    # Load ground truth
    gt_data = load_ground_truth(project_root)

    # Default: test all CMJ videos at 45 degrees
    validation_videos = [
        {
            "path": "samples/validation/cmj-45-IMG_6733.MOV",
            "ground_truth": gt_data.get("samples/validation/cmj-45-IMG_6733.MOV"),
        },
        {
            "path": "samples/validation/cmj-45-IMG_6734.MOV",
            "ground_truth": gt_data.get("samples/validation/cmj-45-IMG_6734.MOV"),
        },
        {
            "path": "samples/validation/cmj-45-IMG_6735.MOV",
            "ground_truth": gt_data.get("samples/validation/cmj-45-IMG_6735.MOV"),
        },
    ]

    # Check if custom path provided
    if len(sys.argv) > 1:
        custom_path = sys.argv[1]
        if Path(custom_path).exists():
            # Try to find ground truth for custom path
            gt_key = str(Path(custom_path).relative_to(project_root)) if project_root in Path(custom_path).parents else custom_path
            validation_videos = [{"path": custom_path, "ground_truth": gt_data.get(gt_key)}]
        else:
            print(f"Error: Video not found: {custom_path}")
            sys.exit(1)

    all_results = []
    for video_info in validation_videos:
        video_path = project_root / video_info["path"]
        if not video_path.exists():
            print(f"Warning: Video not found: {video_path}")
            continue

        results = analyze_video(str(video_path), video_info.get("ground_truth"))
        all_results.append(results)

    # Summary
    if all_results:
        print(f"\n{'='*60}")
        print("SUMMARY ACROSS ALL VIDEOS")
        print(f"{'='*60}")

        # Collect errors for each method
        method_errors = {
            "Current": [],
            "Foot velocity": [],
            "Foot-hip div": [],
            "Foot decel": [],
            "Vel deriv": [],
        }

        for r in all_results:
            print(f"\n{r['video']}:")

            if "ground_truth" in r and r["ground_truth"]:
                gt_data = r["ground_truth"]
                gt = gt_data["landing"] if isinstance(gt_data, dict) else gt_data
                errors = {
                    "Current": r["current_landing"] - gt,
                    "Foot velocity": r["foot_velocity_landing"] - gt,
                    "Foot-hip div": r["divergence_landing"] - gt,
                    "Foot decel": r["foot_decel_landing"] - gt,
                    "Vel deriv": r["vel_deriv_landing"] - gt,
                }

                for method, err in errors.items():
                    method_errors[method].append(err)
                    print(f"  {method:15s}: {err:+.1f} frames ({err/r['fps']*1000:+.0f}ms)")

                # Find best for this video
                abs_errors = {k: abs(v) for k, v in errors.items()}
                best = min(abs_errors, key=abs_errors.get)
                print(f"  ★ Best: {best}")

        # Overall summary
        print(f"\n{'='*60}")
        print("AGGREGATE STATISTICS")
        print(f"{'='*60}")
        print(f"\n{'Method':15s} {'Mean Error':>12s} {'Abs Mean':>10s} {'Std Dev':>10s}")
        print("-" * 50)

        for method, errors in method_errors.items():
            if errors:
                mean_err = np.mean(errors)
                abs_mean = np.mean(np.abs(errors))
                std_err = np.std(errors)
                print(f"{method:15s} {mean_err:+10.2f}fr {abs_mean:8.2f}fr {std_err:8.2f}fr")

        # Find overall best method
        avg_abs_errors = {k: np.mean(np.abs(v)) for k, v in method_errors.items() if v}
        best_overall = min(avg_abs_errors, key=avg_abs_errors.get)
        print(f"\n★ BEST OVERALL: {best_overall} (avg absolute error: {avg_abs_errors[best_overall]:.2f} frames)")


if __name__ == "__main__":
    main()
