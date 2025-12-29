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
    """Factory for creating pose trackers with automatic backend selection.

    Supports multiple backends with auto-detection:
    - RTMPose CUDA: NVIDIA GPU acceleration (fastest, 133 FPS)
    - RTMPose CoreML: Apple Silicon acceleration (42 FPS)
    - RTMPose CPU: Optimized CPU implementation (40-68 FPS)
    - MediaPipe: Fallback baseline (48 FPS)

    Usage:
        # Auto-detect best backend
        tracker = PoseTrackerFactory.create()

        # Force specific backend
        tracker = PoseTrackerFactory.create(backend='rtmpose-cuda')

        # Check available backends
        available = PoseTrackerFactory.get_available_backends()
    """

    # Backend class mappings
    _BACKENDS: dict[str, type] = {}

    @classmethod
    def create(
        cls,
        backend: str = "auto",
        mode: str = "lightweight",
        **kwargs: object,
    ) -> object:
        """Create a pose tracker with the specified backend.

        Args:
            backend: Backend selection:
                - 'auto': Auto-detect best available backend
                - 'mediapipe': MediaPipe Tasks API (baseline)
                - 'rtmpose-cpu': RTMPose optimized CPU
                - 'rtmpose-cuda': RTMPose with CUDA (NVIDIA GPU)
                - 'rtmpose-coreml': RTMPose with CoreML (Apple Silicon)
            mode: RTMPose performance mode ('lightweight', 'balanced', 'performance')
                Only used for RTMPose backends
            **kwargs: Additional arguments passed to tracker constructor

        Returns:
            Configured pose tracker instance

        Raises:
            ValueError: If backend is not available or recognized
        """
        # Auto-detect backend
        if backend == "auto":
            backend = cls._detect_best_backend()
            backend = cls._check_backend_available(backend)

        # Check environment variable override
        import os

        env_backend = os.environ.get("POSE_TRACKER_BACKEND")
        if env_backend:
            backend = cls._normalize_backend_name(env_backend)

        # Verify backend is available
        backend = cls._check_backend_available(backend)

        # Get tracker class
        tracker_class = cls._get_tracker_class(backend)

        # Create tracker with appropriate arguments
        return cls._create_tracker(tracker_class, backend, mode, kwargs)

    @classmethod
    def _detect_best_backend(cls) -> str:
        """Detect the best available backend.

        Priority order:
        1. CUDA (NVIDIA GPU) - fastest
        2. CoreML (Apple Silicon) - good performance
        3. RTMPose CPU - optimized CPU
        4. MediaPipe - baseline fallback

        Returns:
            Backend name string
        """
        # Check for CUDA (NVIDIA GPU)
        try:
            import torch

            if torch.cuda.is_available():
                return "rtmpose-cuda"
        except ImportError:
            pass

        # Check for CoreML (Apple Silicon)
        import sys

        if sys.platform == "darwin":
            return "rtmpose-coreml"

        # Check for RTMPose CPU
        try:
            from kinemotion.core.rtmpose_cpu import (
                OptimizedCPUTracker as _RTMPoseCPU,  # type: ignore
            )

            _ = _RTMPoseCPU  # Mark as intentionally used for availability check

            return "rtmpose-cpu"
        except ImportError:
            pass

        # Fallback to MediaPipe
        return "mediapipe"

    @classmethod
    def _check_backend_available(cls, backend: str) -> str:
        """Check if a backend is available and return a fallback if not.

        Args:
            backend: Requested backend name

        Returns:
            Available backend name (may be different from requested)

        Raises:
            ValueError: If no backend is available
        """
        normalized = cls._normalize_backend_name(backend)

        # Check if specific backend can be imported
        if normalized == "rtmpose-cuda":
            try:
                import torch  # noqa: F401

                if not torch.cuda.is_available():
                    # CUDA not available, fall back to CPU
                    return cls._check_backend_available("rtmpose-cpu")
                # CUDA is available, use rtmpose-cuda
                return normalized
            except ImportError:
                return cls._check_backend_available("rtmpose-cpu")

        if normalized == "rtmpose-coreml":
            import sys

            if sys.platform != "darwin":
                # Not macOS, fall back to CPU
                return cls._check_backend_available("rtmpose-cpu")

        if normalized == "rtmpose-cpu":
            try:
                from kinemotion.core.rtmpose_cpu import (
                    OptimizedCPUTracker as _RTMPoseCPU,
                )  # type: ignore

                _ = _RTMPoseCPU  # Mark as intentionally used for availability check

                return normalized
            except ImportError:
                # RTMPose not available, fall back to MediaPipe
                return "mediapipe"

        if normalized == "mediapipe":
            try:
                import mediapipe as _mp  # noqa: F401

                _ = _mp  # Mark as intentionally used for availability check
                return normalized
            except ImportError as err:
                raise ValueError(
                    "No pose tracking backend available. Please install mediapipe or rtmlib."
                ) from err

        raise ValueError(f"Unknown backend: {backend}")

    @classmethod
    def _normalize_backend_name(cls, backend: str) -> str:
        """Normalize backend name to canonical form.

        Args:
            backend: User-provided backend name

        Returns:
            Canonical backend name
        """
        # Normalize various aliases to canonical names
        aliases = {
            "mp": "mediapipe",
            "mediapipe": "mediapipe",
            "rtmpose": "rtmpose-cpu",
            "rtmpose-cpu": "rtmpose-cpu",
            "rtmpose_cpu": "rtmpose-cpu",
            "cpu": "rtmpose-cpu",
            "cuda": "rtmpose-cuda",
            "rtmpose-cuda": "rtmpose-cuda",
            "rtmpose_cuda": "rtmpose-cuda",
            "gpu": "rtmpose-cuda",
            "mps": "rtmpose-coreml",
            "coreml": "rtmpose-coreml",
            "rtmpose-coreml": "rtmpose-coreml",
            "rtmpose_coreml": "rtmpose-coreml",
        }
        return aliases.get(backend.lower(), backend)

    @classmethod
    def _get_tracker_class(cls, backend: str):
        """Get the tracker class for a backend.

        Args:
            backend: Canonical backend name

        Returns:
            Tracker class

        Raises:
            ValueError: If backend is not recognized
        """
        if backend == "mediapipe":
            return MediaPipePoseTracker

        if backend == "rtmpose-cpu":
            try:
                from kinemotion.core.rtmpose_cpu import OptimizedCPUTracker

                return OptimizedCPUTracker
            except ImportError as e:
                raise ValueError(f"RTMPose CPU backend requested but not available: {e}") from e

        if backend in ("rtmpose-cuda", "rtmpose-coreml"):
            try:
                from kinemotion.core.rtmpose_wrapper import RTMPoseWrapper

                return RTMPoseWrapper
            except ImportError as e:
                raise ValueError(
                    f"RTMPose wrapper backend requested but not available: {e}"
                ) from e

        raise ValueError(f"Unknown backend: {backend}")

    @classmethod
    def _create_tracker(
        cls,
        tracker_class: type,
        backend: str,
        mode: str,
        kwargs: dict[str, object],
    ) -> object:
        """Create a tracker instance with appropriate arguments.

        Args:
            tracker_class: Tracker class to instantiate
            backend: Backend name (for parameter mapping)
            mode: RTMPose mode (only used for RTMPose backends)
            kwargs: Additional arguments from user

        Returns:
            Tracker instance
        """
        # MediaPipe-specific arguments
        if backend == "mediapipe":
            # Remove RTMPose-specific arguments
            rttmpose_keys = {"mode", "backend", "device", "pose_input_size"}
            filtered_kwargs = {k: v for k, v in kwargs.items() if k not in rttmpose_keys}
            return tracker_class(**filtered_kwargs)

        # OptimizedCPUTracker (CPU-only, doesn't accept device parameter)
        if backend == "rtmpose-cpu":
            # Remove RTMPoseWrapper-specific and MediaPipe-specific arguments
            unsupported_keys = {
                "backend",
                "device",
                "min_detection_confidence",
                "min_tracking_confidence",
            }
            filtered_kwargs = {k: v for k, v in kwargs.items() if k not in unsupported_keys}
            filtered_kwargs.setdefault("mode", mode)
            return tracker_class(**filtered_kwargs)

        # RTMPoseWrapper (CUDA/CoreML, requires device parameter)
        # Remove MediaPipe-specific arguments
        mediapipe_keys = {"min_detection_confidence", "min_tracking_confidence"}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in mediapipe_keys}

        device = backend.split("-")[-1]  # Extract 'cuda', 'cpu', 'coreml'
        if device == "coreml":
            device = "mps"  # RTMLib uses 'mps' for Apple Silicon

        filtered_kwargs.setdefault("device", device)
        filtered_kwargs.setdefault("mode", mode)

        return tracker_class(**filtered_kwargs)

    @classmethod
    def get_available_backends(cls) -> list[str]:
        """Get list of available backends on current system.

        Returns:
            List of available backend names
        """
        available = []

        # Always have MediaPipe as fallback
        try:
            import mediapipe as _mp  # noqa: F401

            _ = _mp  # Mark as intentionally used for availability check
            available.append("mediapipe")
        except ImportError:
            pass

        # Check RTMPose CPU
        try:
            from kinemotion.core.rtmpose_cpu import (
                OptimizedCPUTracker as _RTMPoseCPU,
            )  # type: ignore

            _ = _RTMPoseCPU  # Mark as intentionally used for availability check

            available.append("rtmpose-cpu")
        except ImportError:
            pass

        # Check CUDA
        try:
            import torch

            if torch.cuda.is_available():
                from kinemotion.core.rtmpose_wrapper import (
                    RTMPoseWrapper as _RTMPoseWrapper,
                )  # type: ignore

                _ = _RTMPoseWrapper  # Mark as intentionally used for availability check

                available.append("rtmpose-cuda")
        except ImportError:
            pass

        # Check CoreML (Apple Silicon)
        import sys

        if sys.platform == "darwin":
            try:
                from kinemotion.core.rtmpose_wrapper import (
                    RTMPoseWrapper as _RTMPoseWrapperMPS,
                )  # type: ignore

                _ = _RTMPoseWrapperMPS  # Mark as intentionally used for availability check

                available.append("rtmpose-coreml")
            except ImportError:
                pass

        return available

    @classmethod
    def get_backend_info(cls, backend: str) -> dict[str, str]:
        """Get information about a backend.

        Args:
            backend: Backend name

        Returns:
            Dictionary with backend information
        """
        info = {
            "mediapipe": {
                "name": "MediaPipe",
                "description": "Baseline pose tracking using MediaPipe Tasks API",
                "performance": "~48 FPS",
                "accuracy": "Baseline (reference)",
                "requirements": "mediapipe package",
            },
            "rtmpose-cpu": {
                "name": "RTMPose CPU",
                "description": "Optimized CPU implementation with ONNX Runtime",
                "performance": "~40-68 FPS (134% of MediaPipe)",
                "accuracy": "9-12px mean difference (1-5% metric accuracy)",
                "requirements": "rtmlib package",
            },
            "rtmpose-cuda": {
                "name": "RTMPose CUDA",
                "description": "NVIDIA GPU acceleration with CUDA",
                "performance": "~133 FPS (271% of MediaPipe)",
                "accuracy": "9-12px mean difference (1-5% metric accuracy)",
                "requirements": "rtmlib + CUDA-capable GPU",
            },
            "rtmpose-coreml": {
                "name": "RTMPose CoreML",
                "description": "Apple Silicon acceleration with CoreML",
                "performance": "~42 FPS (94% of MediaPipe)",
                "accuracy": "9-12px mean difference (1-5% metric accuracy)",
                "requirements": "rtmlib + Apple Silicon",
            },
        }

        normalized = cls._normalize_backend_name(backend)
        return info.get(normalized, {})


def get_tracker_info(tracker: object) -> str:
    """Get detailed information about a pose tracker instance.

    Args:
        tracker: Pose tracker instance

    Returns:
        Formatted string with tracker details
    """
    tracker_class = type(tracker).__name__
    module = type(tracker).__module__

    info = f"{tracker_class} (from {module})"

    # Add backend-specific details
    if tracker_class == "MediaPipePoseTracker":
        info += " [MediaPipe Tasks API]"
    elif tracker_class == "OptimizedCPUTracker":
        # Check if ONNX Runtime has CUDA
        try:
            import onnxruntime as ort

            providers = ort.get_available_providers()
            if "CUDAExecutionProvider" in providers:
                # Check what providers the session is actually using
                det_session = getattr(tracker, "det_session", None)
                if det_session is not None:
                    active_providers = det_session.get_providers()
                    if "CUDAExecutionProvider" in active_providers:
                        info += " [ONNX Runtime: CUDA]"
                    else:
                        info += " [ONNX Runtime: CPU]"
                else:
                    info += " [ONNX Runtime]"
            else:
                info += " [ONNX Runtime: CPU]"
        except ImportError:
            info += " [ONNX Runtime]"
    elif tracker_class == "RTMPoseWrapper":
        device = getattr(tracker, "device", None)
        if device:
            if device == "cuda":
                try:
                    import torch

                    if torch.cuda.is_available():
                        device_name = torch.cuda.get_device_name(0)
                        info += f" [PyTorch CUDA: {device_name}]"
                    else:
                        info += " [PyTorch: CPU fallback]"
                except ImportError:
                    info += " [PyTorch CUDA]"
            elif device == "mps":
                info += " [PyTorch: Apple Silicon GPU]"
            else:
                info += f" [PyTorch: {device}]"
        else:
            info += " [PyTorch]"

    return info


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


# Legacy compatibility aliases for Solution API enum values
class _LegacyPoseLandmark:
    """Compatibility shim for Solution API enum values."""

    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    NOSE = 0
    LEFT_KNEE = 25
    RIGHT_KNEE = 26


PoseLandmark = _LegacyPoseLandmark


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
