"""RTMPose-based pose tracker compatible with kinemotion's PoseTracker API.

This adapter enables RTMLib/RTMPose to be used as a drop-in replacement
for MediaPipe in kinemotion's pose tracking pipeline.
"""

from __future__ import annotations

import numpy as np
from rtmlib import BodyWithFeet

from kinemotion.core.timing import NULL_TIMER, Timer

# Halpe-26 to kinemotion landmark mapping
# Based on: https://github.com/Fang-Haoshu/Halpe-FullBody
HALPE_TO_KINEMOTION = {
    0: "nose",
    5: "left_shoulder",
    6: "right_shoulder",
    11: "left_hip",
    12: "right_hip",
    13: "left_knee",
    14: "right_knee",
    15: "left_ankle",
    16: "right_ankle",
    20: "left_foot_index",
    21: "right_foot_index",
    24: "left_heel",
    25: "right_heel",
}


class RTMPoseTracker:
    """RTMPose-based pose tracker matching MediaPipe PoseTracker interface.

    Uses RTMLib's BodyWithFeet (Halpe-26 format) which provides all 13
    kinemotion landmarks including feet.

    Attributes:
        timer: Optional Timer for measuring operations
        estimator: RTMLib BodyWithFeet estimator instance
        mode: RTMLib mode ('lightweight', 'balanced', 'performance')
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        timer: Timer | None = None,
        mode: str = "lightweight",
        backend: str = "onnxruntime",
        device: str = "cpu",
        pose_input_size: tuple[int, int] | None = None,
    ) -> None:
        """Initialize the RTMPose tracker.

        Args:
            min_detection_confidence: Minimum confidence for pose detection
                (maps to RTMLib's internal thresholding)
            min_tracking_confidence: Minimum confidence for pose tracking
                (used for visibility filtering)
            timer: Optional Timer for measuring operations
            mode: RTMLib performance mode:
                - 'lightweight': Fastest, RTMPose-s
                - 'balanced': Default mode
                - 'performance': Best accuracy, RTMPose-m
            backend: RTMLib backend ('onnxruntime', 'opencv')
            device: RTMLib device ('cpu', 'mps' for CoreML)
            pose_input_size: Custom input size as (height, width) tuple
        """
        self.timer = timer or NULL_TIMER
        self.mode = mode
        self.backend = backend
        self.device = device

        with self.timer.measure("rtmpose_initialization"):
            kwargs = {
                "mode": mode,
                "backend": backend,
                "device": device,
            }
            if pose_input_size is not None:
                kwargs["pose_input_size"] = pose_input_size
            self.estimator = BodyWithFeet(**kwargs)

    def process_frame(self, frame: np.ndarray) -> dict[str, tuple[float, float, float]] | None:
        """Process a single frame and extract pose landmarks.

        Args:
            frame: BGR image frame (OpenCV format)

        Returns:
            Dictionary mapping landmark names to (x, y, visibility) tuples,
            or None if no pose detected. Coordinates are normalized (0-1).

            Note: RTMLib returns pixel coordinates, so we normalize by image
            dimensions to match MediaPipe's output format.
        """
        if frame.size == 0:
            return None

        height, width = frame.shape[:2]

        # RTMLib expects RGB, but BodyWithFeet handles conversion internally
        with self.timer.measure("rtmpose_inference"):
            keypoints, scores = self.estimator(frame)

        if keypoints.shape[0] == 0:
            return None

        # Extract first person's keypoints
        with self.timer.measure("landmark_extraction"):
            landmarks = self._extract_landmarks(keypoints[0], scores[0], width, height)

        return landmarks

    def _extract_landmarks(
        self,
        keypoints: np.ndarray,
        scores: np.ndarray,
        img_width: int,
        img_height: int,
    ) -> dict[str, tuple[float, float, float]]:
        """Extract and convert RTMLib landmarks to MediaPipe format.

        Args:
            keypoints: (26, 2) array of pixel coordinates
            scores: (26,) array of confidence scores
            img_width: Image width for normalization
            img_height: Image height for normalization

        Returns:
            Dictionary mapping kinemotion landmark names to normalized
            (x, y, visibility) tuples.
        """
        landmarks = {}

        for halpe_idx, name in HALPE_TO_KINEMOTION.items():
            x_pixel, y_pixel = keypoints[halpe_idx]
            confidence = float(scores[halpe_idx])

            # Normalize to [0, 1] like MediaPipe
            x_norm = float(x_pixel / img_width)
            y_norm = float(y_pixel / img_height)

            # Clamp to valid range
            x_norm = max(0.0, min(1.0, x_norm))
            y_norm = max(0.0, min(1.0, y_norm))

            # Use confidence as visibility (MediaPipe compatibility)
            landmarks[name] = (x_norm, y_norm, confidence)

        return landmarks

    def close(self) -> None:
        """Release resources (no-op for RTMLib)."""
        pass


def create_rtmpose_tracker(
    mode: str = "lightweight",
    timer: Timer | None = None,
) -> RTMPoseTracker:
    """Factory function to create an RTMPoseTracker.

    Args:
        mode: Performance mode ('lightweight', 'balanced', 'performance')
        timer: Optional Timer for measuring operations

    Returns:
        Configured RTMPoseTracker instance
    """
    return RTMPoseTracker(mode=mode, timer=timer)
