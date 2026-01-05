#!/usr/bin/env python3
"""Validate ankle angle signal for landing detection.

This script extracts and visualizes ankle angles around the landing phase
to determine if ankle dorsiflexion can be used as an early landing signal.

Ground truth: Landing at frame 141
Current detection: Landing at frame 142

Expected pattern:
- Flight: Constant plantarflexed angle (~120-140°)
- Landing: Rapid dorsiflexion (angle decreases)
- Angular velocity spike should precede hip deceleration
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter

from kinemotion.core.pose import MediaPipePoseTracker
from kinemotion.core.pose_landmarks import LANDMARK_INDICES


def compute_ankle_angle(
    landmarks: dict[str, tuple[float, float, float]],
    side: str = "left",
) -> float:
    """Compute ankle dorsiflexion angle.

    Angle between shin (knee-ankle) and foot (ankle-heel) vectors.
    Returns angle in degrees.

    Args:
        landmarks: Landmark dict from pose tracker
        side: "left" or "right"

    Returns:
        Ankle angle in degrees, or np.nan if landmarks not visible
    """
    prefix = f"{side}_"

    # Get landmark coordinates
    knee_name = f"{prefix}knee"
    ankle_name = f"{prefix}ankle"
    heel_name = f"{prefix}heel"

    if knee_name not in landmarks or ankle_name not in landmarks or heel_name not in landmarks:
        return np.nan

    knee = landmarks[knee_name]
    ankle = landmarks[ankle_name]
    heel = landmarks[heel_name]

    # Check visibility
    if ankle[2] < 0.5 or knee[2] < 0.5 or heel[2] < 0.5:
        return np.nan

    # Convert to numpy arrays (using x, y coordinates)
    knee_pos = np.array([knee[0], knee[1]])
    ankle_pos = np.array([ankle[0], ankle[1]])
    heel_pos = np.array([heel[0], heel[1]])

    # Compute vectors
    # shin_vector: knee → ankle (pointing down)
    shin_vector = ankle_pos - knee_pos
    # foot_vector: ankle → heel (pointing back)
    foot_vector = heel_pos - ankle_pos

    # Compute angle between vectors
    shin_norm = np.linalg.norm(shin_vector)
    foot_norm = np.linalg.norm(foot_vector)

    if shin_norm < 1e-6 or foot_norm < 1e-6:
        return np.nan

    cos_angle = np.dot(shin_vector, foot_vector) / (shin_norm * foot_norm)
    # Clamp to valid range for arccos
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    angle_rad = np.arccos(cos_angle)
    angle_deg = np.degrees(angle_rad)

    return angle_deg


def extract_landmarks_around_landing(
    video_path: Path,
    landing_frame: int = 141,
    window_frames: int = 20,
) -> tuple[dict[int, dict], float]:
    """Extract landmarks for frames around landing.

    Args:
        video_path: Path to video file
        landing_frame: Ground truth landing frame
        window_frames: Frames before/after landing to extract

    Returns:
        Tuple of (landmarks dict, fps)
    """
    tracker = MediaPipePoseTracker(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)

    start_frame = max(0, landing_frame - window_frames)
    end_frame = min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), landing_frame + window_frames)

    landmarks: dict[int, dict] = {}

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    for frame_idx in range(start_frame, end_frame):
        ret, frame = cap.read()
        if not ret:
            break

        timestamp_ms = int(frame_idx * 1000 / fps)
        frame_landmarks = tracker.process_frame(frame, timestamp_ms)

        if frame_landmarks:
            landmarks[frame_idx] = frame_landmarks

    cap.release()
    tracker.close()

    return landmarks, fps


def analyze_ankle_angles(
    landmarks: dict[int, dict],
    landing_frame: int = 141,
) -> dict[str, dict]:
    """Analyze ankle angles for both sides.

    Args:
        landmarks: Dict mapping frame_idx to landmarks
        landing_frame: Ground truth landing frame

    Returns:
        Dict with analysis results for each side
    """
    results = {}

    for side in ["left", "right"]:
        # Compute raw angles
        angles = []
        frames = []
        visibilities = []

        for frame_idx in sorted(landmarks.keys()):
            angle = compute_ankle_angle(landmarks[frame_idx], side)
            if not np.isnan(angle):
                angles.append(angle)
                frames.append(frame_idx)

                # Track ankle visibility
                ankle_name = f"{side}_ankle"
                if ankle_name in landmarks[frame_idx]:
                    visibilities.append(landmarks[frame_idx][ankle_name][2])

        if len(angles) < 5:
            results[side] = {"error": "Insufficient data"}
            continue

        angles = np.array(angles)
        frames = np.array(frames)

        # Smooth the angle signal
        if len(angles) >= 5:
            smoothed = savgol_filter(angles, window_length=5, polyorder=2)
        else:
            smoothed = angles

        # Compute angular velocity (degrees per frame)
        angular_velocity = np.diff(smoothed)

        # Find peak angular velocity (maximum dorsiflexion rate)
        # Negative velocity = dorsiflexion (angle decreasing)
        min_vel_idx = np.argmin(angular_velocity)
        peak_velocity_frame = frames[min_vel_idx + 1]
        peak_velocity = angular_velocity[min_vel_idx]

        # Find when angle change starts (velocity crosses threshold)
        # Threshold: 2 degrees/frame change
        threshold = -2.0
        change_frames = frames[1:][angular_velocity < threshold]

        first_change_frame = change_frames[0] if len(change_frames) > 0 else frames[0]

        results[side] = {
            "frames": frames,
            "angles": angles,
            "smoothed": smoothed,
            "angular_velocity": angular_velocity,
            "avg_visibility": np.mean(visibilities) if visibilities else 0,
            "peak_velocity_frame": peak_velocity_frame,
            "peak_velocity": peak_velocity,
            "first_change_frame": first_change_frame,
            "landing_frame_offset": first_change_frame - landing_frame if len(change_frames) > 0 else None,
        }

    return results


def plot_results(
    results: dict[str, dict],
    landing_frame: int = 141,
    output_path: Path | None = None,
) -> None:
    """Plot ankle angle analysis results.

    Args:
        results: Analysis results from analyze_ankle_angles
        landing_frame: Ground truth landing frame
        output_path: Optional path to save plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"Ankle Angle Analysis Around Landing (Frame {landing_frame})", fontsize=14)

    colors = {"left": "blue", "right": "red"}

    for idx, side in enumerate(["left", "right"]):
        if "error" in results[side]:
            continue

        data = results[side]
        color = colors[side]
        frames = data["frames"]

        # Plot 1: Raw vs smoothed angles
        ax = axes[0, 0]
        ax.plot(frames, data["angles"], "o-", color=color, alpha=0.5, label=f"{side} raw")
        ax.plot(frames, data["smoothed"], "-", color=color, linewidth=2, label=f"{side} smoothed")
        ax.axvline(landing_frame, color="green", linestyle="--", label="Ground truth landing")
        ax.axvline(data["first_change_frame"], color=color, linestyle=":", label=f"{side} first change")
        ax.set_ylabel("Ankle Angle (degrees)")
        ax.set_title("Ankle Angle Over Time")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 2: Angular velocity
        ax = axes[0, 1]
        vel_frames = frames[1:]
        ax.plot(vel_frames, data["angular_velocity"], "o-", color=color, label=f"{side} ang. vel")
        ax.axhline(-2, color="gray", linestyle="--", alpha=0.5, label="Threshold (-2°/frame)")
        ax.axvline(landing_frame, color="green", linestyle="--", label="Ground truth landing")
        ax.axvline(data["peak_velocity_frame"], color=color, linestyle=":", label=f"{side} peak vel")
        ax.set_ylabel("Angular Velocity (°/frame)")
        ax.set_title("Angular Velocity (Dorsiflexion Rate)")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 3: Zoom around landing
        ax = axes[1, 0]
        window_start = landing_frame - 5
        window_end = landing_frame + 5
        mask = (frames >= window_start) & (frames <= window_end)
        ax.plot(frames[mask], data["angles"][mask], "o-", color=color, linewidth=2)
        ax.axvline(landing_frame, color="green", linestyle="--", linewidth=2, label="Ground truth")
        ax.axvline(data["first_change_frame"], color=color, linestyle=":", linewidth=2, label=f"{side} change")
        ax.set_xlabel("Frame Number")
        ax.set_ylabel("Ankle Angle (degrees)")
        ax.set_title(f"{side.capitalize()} Ankle: Zoom Around Landing")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 4: Summary stats
        ax = axes[1, 1]
        ax.axis("off")

        stats_text = f"""
{side.upper()} ANKLE STATISTICS:
{'─' * 30}
Average visibility: {data['avg_visibility']:.3f}
Peak angular velocity: {data['peak_velocity']:.2f}°/frame
Peak velocity frame: {data['peak_velocity_frame']}
First change frame: {data['first_change_frame']}
Frame offset from landing: {data['landing_frame_offset']:+.0f} frames

Smoothing window: 5 frames
Detection threshold: -2.0°/frame
        """
        ax.text(0.1, 0.5, stats_text, fontsize=10, family="monospace", verticalalignment="center")

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Plot saved to: {output_path}")

    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate ankle angle signal for landing detection"
    )
    parser.add_argument("video", type=Path, help="Path to video file")
    parser.add_argument("--landing-frame", type=int, default=141, help="Ground truth landing frame")
    parser.add_argument("--output", type=Path, help="Output path for plot")
    args = parser.parse_args()

    print(f"Analyzing: {args.video}")
    print(f"Ground truth landing: frame {args.landing_frame}")
    print("Extracting landmarks...")

    landmarks, fps = extract_landmarks_around_landing(args.video, args.landing_frame)

    print(f"Extracted {len(landmarks)} frames at {fps:.2f} fps")
    print("Analyzing ankle angles...")

    results = analyze_ankle_angles(landmarks, args.landing_frame)

    for side in ["left", "right"]:
        if "error" not in results[side]:
            data = results[side]
            print(f"\n{side.upper()} ankle:")
            print(f"  Avg visibility: {data['avg_visibility']:.3f}")
            print(f"  Peak angular velocity: {data['peak_velocity']:.2f}°/frame at frame {data['peak_velocity_frame']}")
            print(f"  First change frame: {data['first_change_frame']}")
            print(f"  Offset from landing: {data['landing_frame_offset']:+.0f} frames")
        else:
            print(f"\n{side.upper()} ankle: {results[side]['error']}")

    print("\nGenerating plot...")
    plot_results(results, args.landing_frame, args.output)


if __name__ == "__main__":
    main()
