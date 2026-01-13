"""Base types and patterns for video analysis APIs.

This module defines shared infrastructure for jump-type-specific analysis modules.
Each jump type (CMJ, Drop Jump, etc.) has its own analysis algorithms, but they
share common patterns for:

1. Configuration (VideoConfig dataclass)
2. Results (VideoResult dataclass)
3. Parameter overrides (AnalysisOverrides dataclass)
4. Bulk processing utilities

To add a new jump type:
1. Create a new module: src/kinemotion/{jump_type}/
2. Implement analysis algorithms in {jump_type}/analysis.py
3. Use the patterns in this module for API structure
4. Import process_videos_bulk_generic from pipeline_utils for bulk processing
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..auto_tuning import QualityPreset
    from ..timing import Timer

__all__ = [
    "AnalysisOverrides",
    "VideoAnalysisConfig",
    "VideoAnalysisResult",
    "JumpAnalysisPipeline",
]


@dataclass
class AnalysisOverrides:
    """Optional overrides for analysis parameters.

    Allows fine-tuning of specific analysis parameters beyond quality presets.
    If None, values will be determined by the quality preset.

    Common overrides across all jump types:
    - smoothing_window: Number of frames for Savitzky-Golay smoothing
    - velocity_threshold: Threshold for phase detection
    - min_contact_frames: Minimum frames for ground contact
    - visibility_threshold: Minimum landmark visibility (0-1)
    """

    smoothing_window: int | None = None
    velocity_threshold: float | None = None
    min_contact_frames: int | None = None
    visibility_threshold: float | None = None


@dataclass
class VideoAnalysisConfig:
    """Base configuration for video analysis.

    Subclasses should add jump-type-specific fields (e.g., drop_start_frame
    for Drop Jump, or additional overrides for CMJ).
    """

    video_path: str
    quality: str = "balanced"
    output_video: str | None = None
    json_output: str | None = None
    overrides: AnalysisOverrides | None = None
    detection_confidence: float | None = None
    tracking_confidence: float | None = None
    verbose: bool = False
    timer: "Timer | None" = None


@dataclass
class VideoAnalysisResult:
    """Base result for video analysis.

    Subclasses should add jump-type-specific fields.
    """

    video_path: str
    success: bool
    metrics: object | None = None  # Will be CMJMetrics, DropJumpMetrics, etc.
    error: str | None = None
    processing_time: float = 0.0


class JumpAnalysisPipeline(ABC):
    """Abstract base class for jump analysis pipelines.

    Defines the common structure for processing jump videos. Each jump type
    implements the specific analysis logic while following this pattern.

    Example:
        class CMJPipeline(JumpAnalysisPipeline):
            def analyze(self) -> CMJMetrics:
                # CMJ-specific analysis (backward search algorithm)
                ...

        class DropJumpPipeline(JumpAnalysisPipeline):
            def analyze(self) -> DropJumpMetrics:
                # Drop jump-specific analysis (forward search algorithm)
                ...
    """

    def __init__(
        self,
        video_path: str,
        quality_preset: "QualityPreset",
        overrides: AnalysisOverrides | None,
        timer: "Timer",
    ) -> None:
        """Initialize the analysis pipeline."""
        self.video_path = video_path
        self.quality_preset = quality_preset
        self.overrides = overrides
        self.timer = timer

    @abstractmethod
    def analyze(self) -> object:
        """Run the jump-specific analysis algorithm.

        Returns:
            Metrics object with jump-type-specific results.
        """
        ...

    def validate_video_exists(self) -> None:
        """Validate that the input video file exists."""
        if not Path(self.video_path).exists():
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
