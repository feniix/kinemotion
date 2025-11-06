"""Kinemotion: Video-based kinematic analysis for athletic performance."""

from .api import (
    CMJVideoConfig,
    CMJVideoResult,
    DropJumpVideoConfig,
    DropJumpVideoResult,
    process_cmj_video,
    process_cmj_videos_bulk,
    process_dropjump_video,
    process_dropjump_videos_bulk,
)
from .cmj.kinematics import CMJMetrics
from .dropjump.kinematics import DropJumpMetrics

__version__ = "0.1.0"

__all__ = [
    # Drop jump API
    "process_dropjump_video",
    "process_dropjump_videos_bulk",
    "DropJumpVideoConfig",
    "DropJumpVideoResult",
    "DropJumpMetrics",
    # CMJ API
    "process_cmj_video",
    "process_cmj_videos_bulk",
    "CMJVideoConfig",
    "CMJVideoResult",
    "CMJMetrics",
]
