"""Pose tracking using MediaPipe Tasks API.

The MediaPipe Solutions API was removed in version 0.10.31.
This module now uses the Tasks API (PoseLandmarker).

Key differences from Solution API:
- Tasks API uses index-based landmark access (0-32) instead of enums
- Running modes: IMAGE, VIDEO, LIVE_STREAM
- No smooth_landmarks option (built into VIDEO mode)
- Has min_pose_presence_confidence parameter (no Solution API equivalent)

Configuration strategies for matching Solution API behavior:
- "video": Standard VIDEO mode with temporal smoothing
- "video_low_presence": VIDEO mode with lower min_pose_presence_confidence (0.2)
- "video_very_low_presence": VIDEO mode with very low min_pose_presence_confidence (0.1)
- "image": IMAGE mode (no temporal smoothing, relies on our smoothing)
"""

from __future__ import annotations

from typing import Any

import cv2
import mediapipe as mp
import numpy as np

from .pose_landmarks import KINEMOTION_LANDMARKS, LANDMARK_INDICES
from .timing import NULL_TIMER, Timer

# Running modes
_RUNNING_MODES = {
    "image": mp.tasks.vision.RunningMode.IMAGE,  # type: ignore[attr-defined]
    "video": mp.tasks.vision.RunningMode.VIDEO,  # type: ignore[attr-defined]
}

# Strategy configurations
_STRATEGY_CONFIGS: dict[str, dict[str, float | str]] = {
    "video": {
        "min_pose_presence_confidence": 0.5,
        "running_mode": "video",
    },
    "video_low_presence": {
        "min_pose_presence_confidence": 0.2,
        "running_mode": "video",
    },
    "video_very_low_presence": {
        "min_pose_presence_confidence": 0.1,
        "running_mode": "video",
    },
    "image": {
        "min_pose_presence_confidence": 0.5,
        "running_mode": "image",
    },
}


class MediaPipePoseTracker:
    """Tracks human pose landmarks in video frames using MediaPipe Tasks API.

    Args:
        min_detection_confidence: Minimum confidence for pose detection (0.0-1.0)
        min_tracking_confidence: Minimum confidence for pose tracking (0.0-1.0)
        model_type: Model variant ("lite", "full", "heavy")
        strategy: Configuration strategy ("video", "video_low_presence", "image")
        timer: Optional Timer for measuring operations

    Note: The Solution API's smooth_landmarks parameter cannot be replicated
    exactly. VIDEO mode has built-in temporal smoothing that cannot be disabled.
    """

    def __init__(  # noqa: PLR0913
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_type: str = "lite",
        strategy: str = "video_low_presence",
        timer: Timer | None = None,
    ) -> None:
        """Initialize the pose tracker."""
        self.timer = timer or NULL_TIMER
        self.mp_pose = mp.tasks.vision  # type: ignore[attr-defined]
        self.model_type = model_type
        self.strategy = strategy

        # Get strategy configuration
        config = _STRATEGY_CONFIGS.get(strategy, _STRATEGY_CONFIGS["video_low_presence"])
        min_pose_presence = config["min_pose_presence_confidence"]
        running_mode_name = str(config["running_mode"])
        running_mode = _RUNNING_MODES[running_mode_name]

        # Get model path
        from .model_downloader import get_model_path

        model_path = str(get_model_path(model_type))

        # Create base options
        base_options = mp.tasks.BaseOptions(model_asset_path=model_path)  # type: ignore[attr-defined]

        # Create pose landmarker options
        options = mp.tasks.vision.PoseLandmarkerOptions(  # type: ignore[attr-defined]
            base_options=base_options,
            running_mode=running_mode,
            min_pose_detection_confidence=min_detection_confidence,
            min_pose_presence_confidence=min_pose_presence,
            min_tracking_confidence=min_tracking_confidence,
            output_segmentation_masks=False,
        )

        # Create the landmarker
        with self.timer.measure("model_load"):
            self.landmarker = self.mp_pose.PoseLandmarker.create_from_options(options)

        self.running_mode = running_mode

    def process_frame(
        self,
        frame: np.ndarray,
        timestamp_ms: int = 0,
    ) -> dict[str, tuple[float, float, float]] | None:
        """Process a single frame and extract pose landmarks.

        Args:
            frame: BGR image frame
            timestamp_ms: Frame timestamp in milliseconds (required for VIDEO mode)

        Returns:
            Dictionary mapping landmark names to (x, y, visibility) tuples,
            or None if no pose detected. Coordinates are normalized (0-1).
        """
        # Convert BGR to RGB
        with self.timer.measure("frame_conversion"):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        with self.timer.measure("image_creation"):
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)  # type: ignore[attr-defined]

        # Process the frame
        with self.timer.measure("mediapipe_inference"):
            if self.running_mode == mp.tasks.vision.RunningMode.VIDEO:  # type: ignore[attr-defined]
                results = self.landmarker.detect_for_video(mp_image, timestamp_ms)
            else:  # IMAGE mode
                results = self.landmarker.detect(mp_image)

        if not results.pose_landmarks:
            return None

        # Extract landmarks (first pose only)
        with self.timer.measure("landmark_extraction"):
            landmarks = _extract_landmarks_from_results(results.pose_landmarks[0])

        return landmarks

    def close(self) -> None:
        """Release resources.

        Note: Tasks API landmarker doesn't have explicit close method.
        Resources are released when the object is garbage collected.
        """
        pass


class PoseTrackerFactory:
    """Factory for creating pose trackers.

    Currently supports MediaPipe as the only backend.

    Usage:
        tracker = PoseTrackerFactory.create()
    """

    @classmethod
    def create(
        cls,
        backend: str = "mediapipe",
        **kwargs: Any,
    ) -> MediaPipePoseTracker:
        """Create a MediaPipe pose tracker.

        Args:
            backend: Backend selection (only 'mediapipe' supported)
            **kwargs: Arguments passed to MediaPipePoseTracker

        Returns:
            Configured MediaPipePoseTracker instance

        Raises:
            ValueError: If backend is not 'mediapipe'
        """
        # Normalize and validate backend
        normalized = backend.lower()
        if normalized not in ("mediapipe", "mp", "auto"):
            raise ValueError(f"Unknown backend: {backend}. Only 'mediapipe' is supported.")

        # Filter out any legacy kwargs that don't apply to MediaPipe
        legacy_keys = {"mode", "backend", "device", "pose_input_size"}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in legacy_keys}

        return MediaPipePoseTracker(**filtered_kwargs)


def _extract_landmarks_from_results(
    pose_landmarks: mp.tasks.vision.components.containers.NormalizedLandmark,  # type: ignore[valid-type]
) -> dict[str, tuple[float, float, float]]:
    """Extract kinemotion landmarks from pose landmarker result.

    Args:
        pose_landmarks: MediaPipe pose landmarks (list of 33 landmarks)

    Returns:
        Dictionary mapping landmark names to (x, y, visibility) tuples
    """
    landmarks: dict[str, tuple[float, float, float]] = {}

    for name in KINEMOTION_LANDMARKS:
        idx = LANDMARK_INDICES[name]
        if idx < len(pose_landmarks):
            lm = pose_landmarks[idx]
            # Tasks API uses presence in addition to visibility
            # Use visibility for consistency with Solution API
            visibility = getattr(lm, "visibility", 1.0)
            landmarks[name] = (lm.x, lm.y, visibility)

    return landmarks


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


def _compute_mean_landmark_position(
    landmark_keys: list[str],
    landmarks: dict[str, tuple[float, float, float]],
    vis_threshold: float,
) -> tuple[float, float, float] | None:
    """Compute mean position and visibility from multiple landmarks.

    Args:
        landmark_keys: List of landmark key names to average
        landmarks: Dictionary of landmark positions
        vis_threshold: Minimum visibility threshold

    Returns:
        (x, y, visibility) tuple if any landmarks are visible, else None
    """
    positions = [
        (x, y, vis)
        for key in landmark_keys
        if key in landmarks
        for x, y, vis in [landmarks[key]]
        if vis > vis_threshold
    ]
    if not positions:
        return None

    x = float(np.mean([p[0] for p in positions]))
    y = float(np.mean([p[1] for p in positions]))
    vis = float(np.mean([p[2] for p in positions]))
    return (x, y, vis)


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
    trunk_pos = _compute_mean_landmark_position(trunk_keys, landmarks, vis_threshold)

    if trunk_pos is not None:
        # Require at least 2 visible landmarks for valid trunk
        visible_count = sum(
            1 for key in trunk_keys if key in landmarks and landmarks[key][2] > vis_threshold
        )
        if visible_count >= 2:
            segments.append((trunk_pos[0], trunk_pos[1]))
            weights.append(0.50)
            visibilities.append(trunk_pos[2])


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
    foot_pos = _compute_mean_landmark_position(foot_keys, landmarks, vis_threshold)

    if foot_pos is not None:
        segments.append((foot_pos[0], foot_pos[1]))
        weights.append(0.015)
        visibilities.append(foot_pos[2])
