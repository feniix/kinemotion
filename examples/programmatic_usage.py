"""Example of using drop-jump analysis programmatically."""

import numpy as np
from dropjump.contact_detection import (
    compute_average_foot_position,
    detect_ground_contact,
)
from dropjump.kinematics import calculate_drop_jump_metrics
from dropjump.pose_tracker import PoseTracker
from dropjump.smoothing import smooth_landmarks
from dropjump.video_io import VideoProcessor


def analyze_video(video_path: str) -> dict:
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

    # Extract foot positions
    foot_positions = []
    visibilities = []

    for frame_landmarks in smoothed:
        if frame_landmarks:
            _, foot_y = compute_average_foot_position(frame_landmarks)
            foot_positions.append(foot_y)

            # Average foot visibility
            foot_vis = []
            for key in ["left_ankle", "right_ankle", "left_heel", "right_heel"]:
                if key in frame_landmarks:
                    foot_vis.append(frame_landmarks[key][2])
            visibilities.append(np.mean(foot_vis) if foot_vis else 0.0)
        else:
            foot_positions.append(foot_positions[-1] if foot_positions else 0.5)
            visibilities.append(0.0)

    foot_positions = np.array(foot_positions)
    visibilities = np.array(visibilities)

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
