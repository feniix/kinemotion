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

        # Extract key landmarks for feet tracking
        landmarks = {}
        landmark_names = {
            self.mp_pose.PoseLandmark.LEFT_ANKLE: "left_ankle",
            self.mp_pose.PoseLandmark.RIGHT_ANKLE: "right_ankle",
            self.mp_pose.PoseLandmark.LEFT_HEEL: "left_heel",
            self.mp_pose.PoseLandmark.RIGHT_HEEL: "right_heel",
            self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX: "left_foot_index",
            self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX: "right_foot_index",
            self.mp_pose.PoseLandmark.LEFT_HIP: "left_hip",
            self.mp_pose.PoseLandmark.RIGHT_HIP: "right_hip",
        }

        for landmark_id, name in landmark_names.items():
            lm = results.pose_landmarks.landmark[landmark_id]
            landmarks[name] = (lm.x, lm.y, lm.visibility)

        return landmarks

    def close(self) -> None:
        """Release resources."""
        self.pose.close()
