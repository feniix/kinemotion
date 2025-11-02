"""Pose tracking using MediaPipe Pose."""

import cv2
import mediapipe as mp
import numpy as np


class PoseTracker:
    """Tracks human pose landmarks in video frames using MediaPipe."""

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        """
        Initialize the pose tracker.

        Args:
            min_detection_confidence: Minimum confidence for pose detection
            min_tracking_confidence: Minimum confidence for pose tracking
        """
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=1,
        )

    def process_frame(
        self, frame: np.ndarray
    ) -> dict[str, tuple[float, float, float]] | None:
        """
        Process a single frame and extract pose landmarks.

        Args:
            frame: BGR image frame

        Returns:
            Dictionary mapping landmark names to (x, y, visibility) tuples,
            or None if no pose detected. Coordinates are normalized (0-1).
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = self.pose.process(rgb_frame)

        if not results.pose_landmarks:
            return None

        # Extract key landmarks for feet tracking and CoM estimation
        landmarks = {}
        landmark_names = {
            # Feet landmarks
            self.mp_pose.PoseLandmark.LEFT_ANKLE: "left_ankle",
            self.mp_pose.PoseLandmark.RIGHT_ANKLE: "right_ankle",
            self.mp_pose.PoseLandmark.LEFT_HEEL: "left_heel",
            self.mp_pose.PoseLandmark.RIGHT_HEEL: "right_heel",
            self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX: "left_foot_index",
            self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX: "right_foot_index",
            # Torso landmarks for CoM estimation
            self.mp_pose.PoseLandmark.LEFT_HIP: "left_hip",
            self.mp_pose.PoseLandmark.RIGHT_HIP: "right_hip",
            self.mp_pose.PoseLandmark.LEFT_SHOULDER: "left_shoulder",
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER: "right_shoulder",
            # Additional landmarks for better CoM estimation
            self.mp_pose.PoseLandmark.NOSE: "nose",
            self.mp_pose.PoseLandmark.LEFT_KNEE: "left_knee",
            self.mp_pose.PoseLandmark.RIGHT_KNEE: "right_knee",
        }

        for landmark_id, name in landmark_names.items():
            lm = results.pose_landmarks.landmark[landmark_id]
            landmarks[name] = (lm.x, lm.y, lm.visibility)

        return landmarks

    def close(self) -> None:
        """Release resources."""
        self.pose.close()


def compute_center_of_mass(
    landmarks: dict[str, tuple[float, float, float]],
    visibility_threshold: float = 0.5,
) -> tuple[float, float, float]:
    """
    Compute approximate center of mass (CoM) from body landmarks.

    Uses biomechanical segment weights based on Dempster's body segment parameters:
    - Head: 8% of body mass (represented by nose)
    - Trunk (shoulders to hips): 50% of body mass
    - Thighs: 2 × 10% = 20% of body mass
    - Legs (knees to ankles): 2 × 5% = 10% of body mass
    - Feet: 2 × 1.5% = 3% of body mass

    The CoM is estimated as a weighted average of these segments, with
    weights corresponding to their proportion of total body mass.

    Args:
        landmarks: Dictionary of landmark positions (x, y, visibility)
        visibility_threshold: Minimum visibility to include landmark in calculation

    Returns:
        (x, y, visibility) tuple for estimated CoM position
        visibility = average visibility of all segments used
    """
    # Define segment representatives and their weights (as fraction of body mass)
    # Each segment uses midpoint or average of its bounding landmarks
    segments = []
    segment_weights = []
    visibilities = []

    # Head segment: 8% (use nose as proxy)
    if "nose" in landmarks:
        x, y, vis = landmarks["nose"]
        if vis > visibility_threshold:
            segments.append((x, y))
            segment_weights.append(0.08)
            visibilities.append(vis)

    # Trunk segment: 50% (midpoint between shoulders and hips)
    trunk_landmarks = ["left_shoulder", "right_shoulder", "left_hip", "right_hip"]
    trunk_positions = [
        (x, y, vis)
        for key in trunk_landmarks
        if key in landmarks
        for x, y, vis in [landmarks[key]]
        if vis > visibility_threshold
    ]
    if len(trunk_positions) >= 2:
        trunk_x = float(np.mean([pos[0] for pos in trunk_positions]))
        trunk_y = float(np.mean([pos[1] for pos in trunk_positions]))
        trunk_vis = float(np.mean([pos[2] for pos in trunk_positions]))
        segments.append((trunk_x, trunk_y))
        segment_weights.append(0.50)
        visibilities.append(trunk_vis)

    # Thigh segment: 20% total (midpoint hip to knee for each leg)
    for side in ["left", "right"]:
        hip_key = f"{side}_hip"
        knee_key = f"{side}_knee"
        if hip_key in landmarks and knee_key in landmarks:
            hip_x, hip_y, hip_vis = landmarks[hip_key]
            knee_x, knee_y, knee_vis = landmarks[knee_key]
            if hip_vis > visibility_threshold and knee_vis > visibility_threshold:
                thigh_x = (hip_x + knee_x) / 2
                thigh_y = (hip_y + knee_y) / 2
                thigh_vis = (hip_vis + knee_vis) / 2
                segments.append((thigh_x, thigh_y))
                segment_weights.append(0.10)  # 10% per leg
                visibilities.append(thigh_vis)

    # Lower leg segment: 10% total (midpoint knee to ankle for each leg)
    for side in ["left", "right"]:
        knee_key = f"{side}_knee"
        ankle_key = f"{side}_ankle"
        if knee_key in landmarks and ankle_key in landmarks:
            knee_x, knee_y, knee_vis = landmarks[knee_key]
            ankle_x, ankle_y, ankle_vis = landmarks[ankle_key]
            if knee_vis > visibility_threshold and ankle_vis > visibility_threshold:
                leg_x = (knee_x + ankle_x) / 2
                leg_y = (knee_y + ankle_y) / 2
                leg_vis = (knee_vis + ankle_vis) / 2
                segments.append((leg_x, leg_y))
                segment_weights.append(0.05)  # 5% per leg
                visibilities.append(leg_vis)

    # Foot segment: 3% total (average of ankle, heel, foot_index)
    for side in ["left", "right"]:
        foot_keys = [f"{side}_ankle", f"{side}_heel", f"{side}_foot_index"]
        foot_positions = [
            (x, y, vis)
            for key in foot_keys
            if key in landmarks
            for x, y, vis in [landmarks[key]]
            if vis > visibility_threshold
        ]
        if foot_positions:
            foot_x = float(np.mean([pos[0] for pos in foot_positions]))
            foot_y = float(np.mean([pos[1] for pos in foot_positions]))
            foot_vis = float(np.mean([pos[2] for pos in foot_positions]))
            segments.append((foot_x, foot_y))
            segment_weights.append(0.015)  # 1.5% per foot
            visibilities.append(foot_vis)

    # If no segments found, fall back to hip average
    if not segments:
        if "left_hip" in landmarks and "right_hip" in landmarks:
            lh_x, lh_y, lh_vis = landmarks["left_hip"]
            rh_x, rh_y, rh_vis = landmarks["right_hip"]
            return (
                (lh_x + rh_x) / 2,
                (lh_y + rh_y) / 2,
                (lh_vis + rh_vis) / 2,
            )
        # Ultimate fallback: center of frame
        return (0.5, 0.5, 0.0)

    # Normalize weights to sum to 1.0
    total_weight = sum(segment_weights)
    normalized_weights = [w / total_weight for w in segment_weights]

    # Compute weighted average of segment positions
    com_x = float(
        sum(
            pos[0] * weight
            for pos, weight in zip(segments, normalized_weights, strict=True)
        )
    )
    com_y = float(
        sum(
            pos[1] * weight
            for pos, weight in zip(segments, normalized_weights, strict=True)
        )
    )
    com_visibility = float(np.mean(visibilities)) if visibilities else 0.0

    return (com_x, com_y, com_visibility)
