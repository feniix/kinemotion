"""Kinemotion: Video-based kinematic analysis for athletic performance."""

from .api import VideoConfig, VideoResult, process_video, process_videos_bulk
from .dropjump.kinematics import DropJumpMetrics

__version__ = "0.1.0"

__all__ = [
    "process_video",
    "process_videos_bulk",
    "VideoConfig",
    "VideoResult",
    "DropJumpMetrics",
]
