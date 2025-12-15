"""Type stubs for MediaPipe Pose solution.

This stub file provides type hints for the MediaPipe Pose API.
Based on MediaPipe v0.10.9+ usage patterns in kinemotion.
"""

from enum import IntEnum
from typing import NamedTuple

import numpy as np

class PoseLandmark(IntEnum):
    """Enum of 33 pose landmarks used by MediaPipe Pose."""

    # Face
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10

    # Upper body
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22

    # Lower body
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32

class NormalizedLandmark:
    """A single pose landmark with normalized coordinates."""

    x: float  # Normalized to [0, 1] (0 = left, 1 = right)
    y: float  # Normalized to [0, 1] (0 = top, 1 = bottom)
    z: float  # Depth relative to hips (smaller = closer to camera)
    visibility: float  # Likelihood [0, 1] that landmark is visible

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        visibility: float = 0.0,
    ) -> None: ...

class NormalizedLandmarkList:
    """Collection of pose landmarks."""

    landmark: list[NormalizedLandmark]

    def __init__(self) -> None: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> NormalizedLandmark: ...

class PoseResults(NamedTuple):
    """Results from pose detection and tracking."""

    pose_landmarks: NormalizedLandmarkList | None
    pose_world_landmarks: NormalizedLandmarkList | None

class Pose:
    """MediaPipe Pose solution for detecting and tracking human pose.

    Usage:
        pose = Pose(min_detection_confidence=0.5)
        results = pose.process(image)
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                print(landmark.x, landmark.y, landmark.visibility)
        pose.close()
    """

    def __init__(
        self,
        static_image_mode: bool = False,
        model_complexity: int = 1,
        smooth_landmarks: bool = True,
        enable_segmentation: bool = False,
        smooth_segmentation: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        """Initialize Pose solution.

        Args:
            static_image_mode: If False, uses tracking for better performance
            model_complexity: 0, 1, or 2 (higher = more accurate but slower)
            smooth_landmarks: Whether to smooth landmarks across frames
            enable_segmentation: Whether to generate segmentation mask
            smooth_segmentation: Whether to smooth segmentation across frames
            min_detection_confidence: Minimum confidence [0.0, 1.0] for detection
            min_tracking_confidence: Minimum confidence [0.0, 1.0] for tracking
        """
        ...

    def process(self, image: np.ndarray) -> PoseResults:
        """Process an RGB image and return pose landmarks.

        Args:
            image: RGB image as numpy array (height, width, 3)

        Returns:
            PoseResults with pose_landmarks (or None if no pose detected)
        """
        ...

    def close(self) -> None:
        """Release resources held by the pose solution."""
        ...

    def __enter__(self) -> Pose:
        """Context manager entry."""
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Context manager exit - calls close()."""
        ...
