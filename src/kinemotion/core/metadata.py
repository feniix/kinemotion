"""Metadata structures for analysis results."""

from dataclasses import dataclass
from datetime import datetime, timezone

from .quality import QualityAssessment


@dataclass
class VideoInfo:
    """Information about the source video.

    Attributes:
        source_path: Path to the source video file
        fps: Actual frames per second (measured from video)
        width: Video width in pixels
        height: Video height in pixels
        duration_s: Total video duration in seconds
        frame_count: Total number of frames
        codec: Video codec (e.g., "h264", "hevc") or None if unknown
    """

    source_path: str
    fps: float
    width: int
    height: int
    duration_s: float
    frame_count: int
    codec: str | None = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "source_path": self.source_path,
            "fps": round(self.fps, 2),
            "resolution": {"width": self.width, "height": self.height},
            "duration_s": round(self.duration_s, 2),
            "frame_count": self.frame_count,
            "codec": self.codec,
        }


@dataclass
class ProcessingInfo:
    """Information about processing context.

    Attributes:
        version: Kinemotion version string (e.g., "0.26.0")
        timestamp: ISO 8601 timestamp of when analysis was performed
        quality_preset: Quality preset used ("fast", "balanced", "accurate")
        processing_time_s: Time taken to process video in seconds
        timing_breakdown: Optional dict mapping stage names to duration in seconds
    """

    version: str
    timestamp: str
    quality_preset: str
    processing_time_s: float
    timing_breakdown: dict[str, float] | None = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        result: dict = {
            "version": self.version,
            "timestamp": self.timestamp,
            "quality_preset": self.quality_preset,
            "processing_time_s": round(self.processing_time_s, 3),
        }
        if self.timing_breakdown:
            result["timing_breakdown_ms"] = {
                stage: round(duration * 1000, 1)
                for stage, duration in self.timing_breakdown.items()
            }
        return result


@dataclass
class SmoothingConfig:
    """Smoothing algorithm configuration.

    Attributes:
        window_size: Savitzky-Golay window size
        polynomial_order: Polynomial degree for SG filter
        use_bilateral_filter: Whether bilateral temporal filtering was used
        use_outlier_rejection: Whether RANSAC/median outlier rejection was used
    """

    window_size: int
    polynomial_order: int
    use_bilateral_filter: bool
    use_outlier_rejection: bool

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "window_size": self.window_size,
            "polynomial_order": self.polynomial_order,
            "use_bilateral_filter": self.use_bilateral_filter,
            "use_outlier_rejection": self.use_outlier_rejection,
        }


@dataclass
class DetectionConfig:
    """Detection algorithm configuration.

    Attributes:
        velocity_threshold: Velocity threshold for contact/flight detection
        min_contact_frames: Minimum consecutive frames to confirm contact
        visibility_threshold: Minimum landmark visibility to trust
        use_curvature_refinement: Whether acceleration-based refinement was used
    """

    velocity_threshold: float
    min_contact_frames: int
    visibility_threshold: float
    use_curvature_refinement: bool

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "velocity_threshold": round(self.velocity_threshold, 4),
            "min_contact_frames": self.min_contact_frames,
            "visibility_threshold": round(self.visibility_threshold, 2),
            "use_curvature_refinement": self.use_curvature_refinement,
        }


@dataclass
class DropDetectionConfig:
    """Drop jump-specific detection configuration.

    Attributes:
        auto_detect_drop_start: Whether automatic drop start detection was used
        detected_drop_frame: Frame where drop was detected (None if manual)
        min_stationary_duration_s: Minimum standing time before drop
    """

    auto_detect_drop_start: bool
    detected_drop_frame: int | None
    min_stationary_duration_s: float

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "auto_detect_drop_start": self.auto_detect_drop_start,
            "detected_drop_frame": self.detected_drop_frame,
            "min_stationary_duration_s": round(self.min_stationary_duration_s, 2),
        }


@dataclass
class AlgorithmConfig:
    """Complete algorithm configuration for reproducibility.

    Attributes:
        detection_method: Algorithm used ("backward_search" for CMJ,
            "forward_search" for drop)
        tracking_method: Pose tracking method ("mediapipe_pose")
        model_complexity: MediaPipe model complexity (0, 1, or 2)
        smoothing: Smoothing configuration
        detection: Detection configuration
        drop_detection: Drop detection config (drop jump only, None for CMJ)
    """

    detection_method: str
    tracking_method: str
    model_complexity: int
    smoothing: SmoothingConfig
    detection: DetectionConfig
    drop_detection: DropDetectionConfig | None = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        result = {
            "detection_method": self.detection_method,
            "tracking_method": self.tracking_method,
            "model_complexity": self.model_complexity,
            "smoothing": self.smoothing.to_dict(),
            "detection": self.detection.to_dict(),
        }

        if self.drop_detection is not None:
            result["drop_detection"] = self.drop_detection.to_dict()

        return result


@dataclass
class ResultMetadata:
    """Complete metadata for analysis results.

    Attributes:
        quality: Quality assessment with confidence and warnings
        video: Source video information
        processing: Processing context and timing
        algorithm: Algorithm configuration used
    """

    quality: QualityAssessment
    video: VideoInfo
    processing: ProcessingInfo
    algorithm: AlgorithmConfig

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "quality": self.quality.to_dict(),
            "video": self.video.to_dict(),
            "processing": self.processing.to_dict(),
            "algorithm": self.algorithm.to_dict(),
        }


def create_timestamp() -> str:
    """Create ISO 8601 timestamp for current time in UTC."""
    return datetime.now(timezone.utc).isoformat()


def get_kinemotion_version() -> str:
    """Get current kinemotion version.

    Returns:
        Version string (e.g., "0.26.0")
    """
    try:
        from importlib.metadata import version

        return version("kinemotion")
    except Exception:
        return "unknown"
