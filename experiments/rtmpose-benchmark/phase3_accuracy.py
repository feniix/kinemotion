#!/usr/bin/env python3
"""Phase 3: Accuracy Assessment - MediaPipe vs RTMPose comparison.

Compares flight time measurements and landmark stability between
MediaPipe and RTMPose-CUDA on the same drop jump videos.

Assessment Dimensions:
1. Metric Consistency: Agreement on flight time, jump height
2. Landmark Stability: Jitter/smoothness of keypoint tracking
3. Temporal Consistency: Frame-to-frame landmark variance
"""

from __future__ import annotations

import argparse
import json

# Add parent directory for rtmpose_tracker import
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from kinemotion.core.pose import PoseTracker
from kinemotion.core.timing import PerformanceTimer

sys.path.insert(0, str(Path(__file__).parent))

from rtmpose_tracker import RTMPoseTracker

# Project root for relative paths
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Test videos
TEST_VIDEOS = [
    str(PROJECT_ROOT / "samples/test-videos/dj-45-IMG_6739.mp4"),
    str(PROJECT_ROOT / "samples/test-videos/dj-45-IMG_6740.mp4"),
    str(PROJECT_ROOT / "samples/test-videos/dj-45-IMG_6741.mp4"),
]


@dataclass
class LandmarkMetrics:
    """Landmark stability metrics."""

    jitter_mean: float  # Average pixel distance between consecutive frames
    jitter_std: float
    jitter_max: float
    visibility_mean: float  # Average confidence score
    invisible_frames: int


@dataclass
class AccuracyResult:
    """Accuracy comparison result for a single video."""

    video_name: str
    tracker_mediapipe: dict[str, Any]
    tracker_rtmpose: dict[str, Any]

    # Flight time comparison
    flight_time_mp: float
    flight_time_rt: float
    flight_time_diff_ms: float
    flight_time_pct_diff: float

    # Jump height comparison
    jump_height_mp: float | None
    jump_height_rt: float | None
    jump_height_diff_cm: float | None

    # Landmark stability
    landmark_stability_mp: dict[str, LandmarkMetrics]
    landmark_stability_rt: dict[str, LandmarkMetrics]

    # Raw landmarks for analysis
    landmarks_mp: list[dict[str, tuple[float, float, float]]]
    landmarks_rt: list[dict[str, tuple[float, float, float]]]


def calculate_landmark_stability(
    landmarks_sequence: list[dict[str, tuple[float, float, float]]],
    frame_width: int,
    frame_height: int,
) -> dict[str, LandmarkMetrics]:
    """Calculate landmark stability metrics.

    Args:
        landmarks_sequence: List of frame landmarks
        frame_width: Video frame width
        frame_height: Video frame height

    Returns:
        Dict mapping landmark names to stability metrics
    """
    if len(landmarks_sequence) < 2:
        return {}

    # Convert normalized coordinates to pixels
    landmark_names = list(landmarks_sequence[0].keys())

    stability = {}

    for name in landmark_names:
        # Extract coordinates for this landmark across all frames
        positions = []
        visibilities = []

        for frame_landmarks in landmarks_sequence:
            if name in frame_landmarks:
                x, y, v = frame_landmarks[name]
                if v > 0:  # Only count visible landmarks
                    positions.append((x * frame_width, y * frame_height))
                    visibilities.append(v)

        if len(positions) < 2:
            stability[name] = LandmarkMetrics(
                jitter_mean=0,
                jitter_std=0,
                jitter_max=0,
                visibility_mean=np.mean(visibilities) if visibilities else 0,
                invisible_frames=len(landmarks_sequence) - len(positions),
            )
            continue

        # Calculate jitter (frame-to-frame movement)
        jitter_values = []
        for i in range(1, len(positions)):
            x1, y1 = positions[i - 1]
            x2, y2 = positions[i]
            distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            jitter_values.append(distance)

        stability[name] = LandmarkMetrics(
            jitter_mean=float(np.mean(jitter_values)),
            jitter_std=float(np.std(jitter_values)),
            jitter_max=float(np.max(jitter_values)),
            visibility_mean=float(np.mean(visibilities)),
            invisible_frames=len(landmarks_sequence) - len(positions),
        )

    return stability


def extract_drop_jump_metrics(
    video_path: str,
    tracker_name: str,
    tracker_factory,
) -> dict[str, Any]:
    """Extract drop jump metrics using specified tracker.

    Args:
        video_path: Path to video file
        tracker_name: Name of tracker for logging
        tracker_factory: Function that creates tracker instance

    Returns:
        Dict with metrics and raw landmarks
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    timer = PerformanceTimer()
    tracker = tracker_factory(timer=timer)

    # Collect all landmarks
    landmarks_sequence = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result = tracker.process_frame(frame)
        if result is not None:
            landmarks_sequence.append(result)
            frame_count += 1

    cap.release()
    tracker.close()

    # Calculate flight time from lowest to highest foot position
    # This is a simplified detection - full algorithm would use the complete
    # drop jump analysis with phase detection

    if landmarks_sequence:
        flight_time = calculate_flight_time_from_landmarks(landmarks_sequence, fps)
    else:
        flight_time = 0

    return {
        "tracker": tracker_name,
        "frame_count": frame_count,
        "flight_time_s": flight_time,
        "fps": fps,
        "frame_width": frame_width,
        "frame_height": frame_height,
        "landmarks_sequence": landmarks_sequence,
    }


def calculate_flight_time_from_landmarks(
    landmarks: list[dict[str, tuple[float, float, float]]],
    video_fps: float,
) -> float:
    """Calculate flight time from foot landmarks.

    Uses a simplified version of the drop jump algorithm:
    - Find takeoff: foot y-velocity becomes positive (moving up)
    - Find landing: foot y-velocity becomes negative (moving down)
    - Flight time = frames between / fps

    Args:
        landmarks: Sequence of landmark dictionaries
        video_fps: Video frame rate

    Returns:
        Flight time in seconds
    """
    if len(landmarks) < 10:
        return 0.0

    # Use lowest ankle/foot point for each frame
    foot_y_positions = []

    for frame_landmarks in landmarks:
        # Check for foot landmarks (prefer heels/ankles)
        foot_points = []
        for name in ["left_heel", "right_heel", "left_ankle", "right_ankle"]:
            if name in frame_landmarks:
                x, y, v = frame_landmarks[name]
                if v > 0.5:
                    foot_points.append(y)
                    break

        if foot_points:
            foot_y_positions.append(min(foot_points))  # Lowest point (largest y)

    if len(foot_y_positions) < 10:
        return 0.0

    # Calculate velocity (change in y position)
    # In normalized coords, smaller y = higher position
    positions = np.array(foot_y_positions)
    velocity = np.diff(positions)

    # Find takeoff: first positive velocity peak (moving up)
    # Smooth velocity first
    window_size = max(3, len(velocity) // 10)
    if window_size % 2 == 0:
        window_size += 1

    from scipy.ndimage import uniform_filter1d

    velocity_smooth = uniform_filter1d(velocity, size=window_size)

    # Takeoff: significant positive velocity
    takeoff_threshold = np.std(velocity_smooth) * 2
    takeoff_idx = None

    for i in range(len(velocity_smooth) // 3, 2 * len(velocity_smooth) // 3):
        if velocity_smooth[i] > takeoff_threshold:
            takeoff_idx = i
            break

    # Landing: significant negative velocity after takeoff
    landing_idx = None
    if takeoff_idx is not None:
        for i in range(takeoff_idx + 10, min(takeoff_idx + 60, len(velocity_smooth))):
            if velocity_smooth[i] < -takeoff_threshold:
                landing_idx = i
                break

    if takeoff_idx and landing_idx:
        flight_frames = landing_idx - takeoff_idx
        return max(0, flight_frames / video_fps)

    return 0.0


def compare_accuracy(video_path: str) -> AccuracyResult:
    """Compare accuracy between MediaPipe and RTMPose on a video.

    Args:
        video_path: Path to video file

    Returns:
        AccuracyResult with comparison metrics
    """
    video_name = Path(video_path).name

    print(f"  Processing {video_name}...")

    # Extract MediaPipe metrics (use image mode to avoid timestamp issues)
    result_mp = extract_drop_jump_metrics(
        video_path,
        "MediaPipe",
        lambda timer: PoseTracker(timer=timer, strategy="image"),
    )

    # Extract RTMPose metrics
    result_rt = extract_drop_jump_metrics(
        video_path,
        "RTMPose-CUDA",
        lambda timer: RTMPoseTracker(mode="lightweight", device="cuda", timer=timer),
    )

    # Flight time comparison
    ft_mp = result_mp["flight_time_s"]
    ft_rt = result_rt["flight_time_s"]
    ft_diff_ms = (ft_rt - ft_mp) * 1000
    ft_pct = (ft_rt / ft_mp - 1) * 100 if ft_mp > 0 else 0

    # Jump height from flight time: h = 0.5 * g * t^2
    g = 9.81
    jh_mp = 0.5 * g * ft_mp**2 if ft_mp > 0 else None
    jh_rt = 0.5 * g * ft_rt**2 if ft_rt > 0 else None
    jh_diff_cm = ((jh_rt - jh_mp) * 100) if (jh_mp and jh_rt) else None

    # Landmark stability
    stability_mp = calculate_landmark_stability(
        result_mp["landmarks_sequence"],
        result_mp["frame_width"],
        result_mp["frame_height"],
    )
    stability_rt = calculate_landmark_stability(
        result_rt["landmarks_sequence"],
        result_rt["frame_width"],
        result_rt["frame_height"],
    )

    return AccuracyResult(
        video_name=video_name,
        tracker_mediapipe=result_mp,
        tracker_rtmpose=result_rt,
        flight_time_mp=ft_mp,
        flight_time_rt=ft_rt,
        flight_time_diff_ms=ft_diff_ms,
        flight_time_pct_diff=ft_pct,
        jump_height_mp=jh_mp,
        jump_height_rt=jh_rt,
        jump_height_diff_cm=jh_diff_cm,
        landmark_stability_mp=stability_mp,
        landmark_stability_rt=stability_rt,
        landmarks_mp=result_mp["landmarks_sequence"],
        landmarks_rt=result_rt["landmarks_sequence"],
    )


def print_accuracy_summary(results: list[AccuracyResult]) -> dict:
    """Print and return accuracy assessment summary.

    Args:
        results: List of accuracy comparison results

    Returns:
        Summary dict with key metrics
    """
    print()
    print("=" * 70)
    print("PHASE 3: ACCURACY ASSESSMENT RESULTS")
    print("=" * 70)

    # Flight time comparison
    print("\n--- Flight Time Comparison ---")
    print(f"{'Video':<30} {'MediaPipe':<12} {'RTMPose':<12} {'Diff (ms)':<12}")
    print("-" * 70)

    ft_diffs = []
    ft_pct_diffs = []

    for r in results:
        sign = "+" if r.flight_time_diff_ms >= 0 else ""
        print(
            f"{r.video_name:<30} {r.flight_time_mp:.4f}s     {r.flight_time_rt:.4f}s     "
            f"{sign}{r.flight_time_diff_ms:.2f}"
        )
        ft_diffs.append(abs(r.flight_time_diff_ms))
        ft_pct_diffs.append(abs(r.flight_time_pct_diff))

    # Summary statistics
    print()
    print("Flight Time Agreement:")
    print(f"  Mean absolute difference: {np.mean(ft_diffs):.2f} ms")
    print(f"  Std deviation:            {np.std(ft_diffs):.2f} ms")
    print(f"  Max difference:            {np.max(ft_diffs):.2f} ms")
    print(f"  Mean % difference:         {np.mean(ft_pct_diffs):.2f}%")

    # Jump height comparison
    print("\n--- Jump Height Comparison ---")
    print(f"{'Video':<30} {'MediaPipe':<12} {'RTMPose':<12} {'Diff (cm)':<12}")
    print("-" * 70)

    jh_diffs = []
    for r in results:
        if r.jump_height_diff_cm is not None:
            sign = "+" if r.jump_height_diff_cm >= 0 else ""
            print(
                f"{r.video_name:<30} {r.jump_height_mp:.3f}m     "
                f"{r.jump_height_rt:.3f}m     {sign}{r.jump_height_diff_cm:.2f}"
            )
            jh_diffs.append(abs(r.jump_height_diff_cm))

    if jh_diffs:
        print()
        print("Jump Height Agreement:")
        print(f"  Mean absolute difference: {np.mean(jh_diffs):.2f} cm")
        print(f"  Std deviation:            {np.std(jh_diffs):.2f} cm")

    # Landmark stability comparison
    print("\n--- Landmark Stability (Jitter) ---")
    print("Lower jitter = more stable tracking")
    print()
    print(f"{'Landmark':<20} {'MP Jitter':<12} {'RT Jitter':<12} {'Improvement':<12}")
    print("-" * 70)

    # Average jitter across all videos for key landmarks
    key_landmarks = ["left_ankle", "right_ankle", "left_heel", "right_heel"]

    improvements = {}

    for lm in key_landmarks:
        mp_jitters = []
        rt_jitters = []

        for r in results:
            if lm in r.landmark_stability_mp and lm in r.landmark_stability_rt:
                mp_jitters.append(r.landmark_stability_mp[lm].jitter_mean)
                rt_jitters.append(r.landmark_stability_rt[lm].jitter_mean)

        if mp_jitters and rt_jitters:
            mp_mean = np.mean(mp_jitters)
            rt_mean = np.mean(rt_jitters)
            improvement = ((mp_mean - rt_mean) / mp_mean * 100) if mp_mean > 0 else 0

            improvements[lm] = improvement

            status = "✅" if improvement > 0 else "⚠️" if improvement > -10 else "❌"
            print(f"{lm:<20} {mp_mean:<12.2f} {rt_mean:<12.2f} {improvement:+.1f}% {status}")

    # Overall assessment
    print()
    print("=" * 70)
    print("ACCURACY ASSESSMENT")
    print("=" * 70)

    # Calculate scores based on the decision framework
    mean_ft_diff_ms = np.mean(ft_diffs)
    mean_ft_pct = np.mean(ft_pct_diffs)

    # Flight time agreement score
    if mean_ft_pct < 2:
        ft_score = 4.0
        ft_assessment = "Excellent agreement (<2% difference)"
    elif mean_ft_pct < 5:
        ft_score = 3.0
        ft_assessment = "Good agreement (2-5% difference)"
    elif mean_ft_pct < 10:
        ft_score = 2.0
        ft_assessment = "Moderate agreement (5-10% difference)"
    else:
        ft_score = 1.0
        ft_assessment = "Poor agreement (>10% difference)"

    print(f"\nFlight Time Accuracy: {ft_score}/4.0")
    print(f"  {ft_assessment}")

    # Landmark stability score
    if improvements:
        avg_improvement = np.mean(list(improvements.values()))
        if avg_improvement > 10:
            stability_score = 4.0
            stability_assessment = "RTMPose significantly more stable"
        elif avg_improvement > 0:
            stability_score = 3.0
            stability_assessment = "RTMPose moderately more stable"
        elif avg_improvement > -10:
            stability_score = 2.0
            stability_assessment = "Similar stability (±10%)"
        else:
            stability_score = 1.0
            stability_assessment = "MediaPipe more stable"

        print(f"\nLandmark Stability: {stability_score}/4.0")
        print(f"  {stability_assessment}")

    # Overall accuracy score (weighted average)
    # Flight time: 60%, Stability: 40%
    overall_score = ft_score * 0.6 + stability_score * 0.4

    print()
    print("-" * 70)
    print(f"OVERALL ACCURACY SCORE: {overall_score:.2f}/4.0")

    # Decision based on the framework
    if overall_score >= 3.5:
        decision = "✅ EXCELLENT - RTMPose shows clear accuracy benefits"
        recommendation = "Strong case for replacement"
    elif overall_score >= 2.8:
        decision = "⚠️  GOOD - RTMPose shows moderate accuracy benefits"
        recommendation = "Conditional replacement recommended"
    elif overall_score >= 2.0:
        decision = "⚠️  NEUTRAL - RTMPose accuracy similar to MediaPipe"
        recommendation = "Consider other factors (performance, robustness)"
    else:
        decision = "❌ CONCERNS - RTMPose less accurate than MediaPipe"
        recommendation = "Maintain MediaPipe for accuracy-critical tasks"

    print(f"\n{decision}")
    print(f"Recommendation: {recommendation}")

    return {
        "ft_score": ft_score,
        "stability_score": stability_score if improvements else 0,
        "overall_score": overall_score,
        "mean_flight_time_diff_ms": mean_ft_diff_ms,
        "mean_flight_time_pct": mean_ft_pct,
        "landmark_improvements": improvements,
        "assessment": ft_assessment,
        "recommendation": recommendation,
    }


def main():
    """Run Phase 3 accuracy assessment."""
    parser = argparse.ArgumentParser(
        description="Phase 3: Accuracy Assessment - MediaPipe vs RTMPose"
    )
    parser.add_argument(
        "--videos",
        nargs="+",
        default=TEST_VIDEOS,
        help="Video files to analyze",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output JSON file path",
    )

    args = parser.parse_args()

    print("=== Phase 3: Accuracy Feasibility Assessment ===")
    print(f"Analyzing {len(args.videos)} videos")
    print()

    results = []
    for video_path in args.videos:
        try:
            result = compare_accuracy(video_path)
            results.append(result)
        except Exception as e:
            print(f"  Error processing {video_path}: {e}")
            import traceback

            traceback.print_exc()

    # Print summary
    summary = print_accuracy_summary(results)

    # Save results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            "summary": summary,
            "results": [
                {
                    "video": r.video_name,
                    "flight_time_mediapipe_s": r.flight_time_mp,
                    "flight_time_rtmpose_s": r.flight_time_rt,
                    "flight_time_diff_ms": r.flight_time_diff_ms,
                    "flight_time_pct_diff": r.flight_time_pct_diff,
                    "jump_height_mediapipe_m": r.jump_height_mp,
                    "jump_height_rtmpose_m": r.jump_height_rt,
                    "jump_height_diff_cm": r.jump_height_diff_cm,
                    "landmark_stability_mp": {
                        k: {
                            "jitter_mean": v.jitter_mean,
                            "visibility_mean": v.visibility_mean,
                        }
                        for k, v in r.landmark_stability_mp.items()
                    },
                    "landmark_stability_rt": {
                        k: {
                            "jitter_mean": v.jitter_mean,
                            "visibility_mean": v.visibility_mean,
                        }
                        for k, v in r.landmark_stability_rt.items()
                    },
                }
                for r in results
            ],
        }

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
