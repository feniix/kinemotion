"""Pose tracking using MediaPipe Pose."""

import cv2
import mediapipe as mp
import numpy as np

from .timing import NULL_TIMER, Timer


class PoseTracker:
    """Tracks human pose landmarks in video frames using MediaPipe."""

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        timer: Timer | None = None,
    ) -> None:
        """
        Initialize the pose tracker.

        Args:
            min_detection_confidence: Minimum confidence for pose detection
            min_tracking_confidence: Minimum confidence for pose tracking
            timer: Optional Timer for measuring operations
        """
        self.timer = timer or NULL_TIMER
        self.mp_pose = mp.solutions.pose  # type: ignore[attr-defined]
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,  # Use tracking mode for better performance
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=1,
        )

    def process_frame(self, frame: np.ndarray) -> dict[str, tuple[float, float, float]] | None:
        """
        Process a single frame and extract pose landmarks.

        Args:
            frame: BGR image frame

        Returns:
            Dictionary mapping landmark names to (x, y, visibility) tuples,
            or None if no pose detected. Coordinates are normalized (0-1).
        """
        # Convert BGR to RGB
        with self.timer.measure("frame_conversion"):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        with self.timer.measure("mediapipe_inference"):
            results = self.pose.process(rgb_frame)

        if not results.pose_landmarks:
            return None

        # Extract key landmarks for feet tracking and CoM estimation
        with self.timer.measure("landmark_extraction"):
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


def _add_head_segment(
    segments: list,
    weights: list,
    visibilities: list,
    landmarks: dict[str, tuple[float, float, float]],
    vis_threshold: float,
) -> None:
    """Add head segment (8% body mass) if visible."""
    if "nose" in landmarks:
        x, y, vis = landmarks["nose"]
        if vis > vis_threshold:
            segments.append((x, y))
            weights.append(0.08)
            visibilities.append(vis)


def _add_trunk_segment(
    segments: list,
    weights: list,
    visibilities: list,
    landmarks: dict[str, tuple[float, float, float]],
    vis_threshold: float,
) -> None:
    """Add trunk segment (50% body mass) if visible."""
    trunk_keys = ["left_shoulder", "right_shoulder", "left_hip", "right_hip"]
    trunk_pos = [
        (x, y, vis)
        for key in trunk_keys
        if key in landmarks
        for x, y, vis in [landmarks[key]]
        if vis > vis_threshold
    ]
    if len(trunk_pos) >= 2:
        trunk_x = float(np.mean([p[0] for p in trunk_pos]))
        trunk_y = float(np.mean([p[1] for p in trunk_pos]))
        trunk_vis = float(np.mean([p[2] for p in trunk_pos]))
        segments.append((trunk_x, trunk_y))
        weights.append(0.50)
        visibilities.append(trunk_vis)


def _add_limb_segment(
    segments: list,
    weights: list,
    visibilities: list,
    landmarks: dict[str, tuple[float, float, float]],
    side: str,
    proximal_key: str,
    distal_key: str,
    segment_weight: float,
    vis_threshold: float,
) -> None:
    """Add a limb segment (thigh or lower leg) if both endpoints visible."""
    prox_full = f"{side}_{proximal_key}"
    dist_full = f"{side}_{distal_key}"

    if prox_full in landmarks and dist_full in landmarks:
        px, py, pvis = landmarks[prox_full]
        dx, dy, dvis = landmarks[dist_full]
        if pvis > vis_threshold and dvis > vis_threshold:
            seg_x = (px + dx) / 2
            seg_y = (py + dy) / 2
            seg_vis = (pvis + dvis) / 2
            segments.append((seg_x, seg_y))
            weights.append(segment_weight)
            visibilities.append(seg_vis)


def _add_foot_segment(
    segments: list,
    weights: list,
    visibilities: list,
    landmarks: dict[str, tuple[float, float, float]],
    side: str,
    vis_threshold: float,
) -> None:
    """Add foot segment (1.5% body mass per foot) if visible."""
    foot_keys = [f"{side}_ankle", f"{side}_heel", f"{side}_foot_index"]
    foot_pos = [
        (x, y, vis)
        for key in foot_keys
        if key in landmarks
        for x, y, vis in [landmarks[key]]
        if vis > vis_threshold
    ]
    if foot_pos:
        foot_x = float(np.mean([p[0] for p in foot_pos]))
        foot_y = float(np.mean([p[1] for p in foot_pos]))
        foot_vis = float(np.mean([p[2] for p in foot_pos]))
        segments.append((foot_x, foot_y))
        weights.append(0.015)
        visibilities.append(foot_vis)


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
    segments: list = []
    weights: list = []
    visibilities: list = []

    # Add body segments
    _add_head_segment(segments, weights, visibilities, landmarks, visibility_threshold)
    _add_trunk_segment(segments, weights, visibilities, landmarks, visibility_threshold)

    # Add bilateral limb segments
    for side in ["left", "right"]:
        _add_limb_segment(
            segments,
            weights,
            visibilities,
            landmarks,
            side,
            "hip",
            "knee",
            0.10,
            visibility_threshold,
        )
        _add_limb_segment(
            segments,
            weights,
            visibilities,
            landmarks,
            side,
            "knee",
            "ankle",
            0.05,
            visibility_threshold,
        )
        _add_foot_segment(segments, weights, visibilities, landmarks, side, visibility_threshold)

    # Fallback if no segments found
    if not segments:
        if "left_hip" in landmarks and "right_hip" in landmarks:
            lh_x, lh_y, lh_vis = landmarks["left_hip"]
            rh_x, rh_y, rh_vis = landmarks["right_hip"]
            return ((lh_x + rh_x) / 2, (lh_y + rh_y) / 2, (lh_vis + rh_vis) / 2)
        return (0.5, 0.5, 0.0)

    # Normalize weights and compute weighted average
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]

    com_x = float(sum(p[0] * w for p, w in zip(segments, normalized_weights, strict=True)))
    com_y = float(sum(p[1] * w for p, w in zip(segments, normalized_weights, strict=True)))
    com_visibility = float(np.mean(visibilities)) if visibilities else 0.0

    return (com_x, com_y, com_visibility)
