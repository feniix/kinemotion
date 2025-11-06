"""Example of using drop-jump analysis programmatically (low-level API)."""

from typing import Any

from kinemotion.core.pose import PoseTracker
from kinemotion.core.smoothing import smooth_landmarks
from kinemotion.core.video_io import VideoProcessor
from kinemotion.dropjump.analysis import (
    detect_ground_contact,
    extract_foot_positions_and_visibilities,
)
from kinemotion.dropjump.kinematics import calculate_drop_jump_metrics


def analyze_video(video_path: str) -> dict[str, Any]:
    """
    Analyze a drop-jump video and return metrics.

    Args:
        video_path: Path to video file

    Returns:
        Dictionary with analysis metrics
    """
    # Initialize components
    video = VideoProcessor(video_path)
    tracker = PoseTracker(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    # Process frames
    landmarks_sequence = []
    while True:
        frame = video.read_frame()
        if frame is None:
            break

        landmarks = tracker.process_frame(frame)
        landmarks_sequence.append(landmarks)

    # Clean up
    tracker.close()
    video.close()

    # Smooth landmarks
    smoothed = smooth_landmarks(landmarks_sequence, window_length=5)

    # Extract foot positions and visibilities using shared utility
    foot_positions, visibilities = extract_foot_positions_and_visibilities(smoothed)

    # Detect contact
    contact_states = detect_ground_contact(
        foot_positions,
        velocity_threshold=0.02,
        min_contact_frames=3,
        visibilities=visibilities,
    )

    # Calculate metrics
    metrics = calculate_drop_jump_metrics(contact_states, foot_positions, video.fps)

    return metrics.to_dict()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python programmatic_usage.py <video_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    results = analyze_video(video_path)

    print("Drop-Jump Analysis Results:")
    print(f"  Ground Contact Time: {results['ground_contact_time_ms']} ms")
    print(f"  Flight Time: {results['flight_time_ms']} ms")
    print(f"  Jump Height: {results['jump_height_m']} m")
