"""Kinemotion: Video-based kinematic analysis for athletic performance.

Supports Counter Movement Jump (CMJ), Drop Jump, and Squat Jump (SJ) analysis
using MediaPipe pose estimation.
"""

from .api import (
    CMJVideoConfig,
    CMJVideoResult,
    DropJumpVideoConfig,
    DropJumpVideoResult,
    SJVideoConfig,
    SJVideoResult,
    process_cmj_video,
    process_cmj_videos_bulk,
    process_dropjump_video,
    process_dropjump_videos_bulk,
    process_sj_video,
    process_sj_videos_bulk,
)
from .countermovement_jump.kinematics import CMJMetrics
from .drop_jump.kinematics import DropJumpMetrics
from .squat_jump.kinematics import SJMetrics

# Get version from package metadata (set in pyproject.toml)
try:
    from importlib.metadata import version

    __version__ = version("kinemotion")
except Exception:
    # Fallback for development/editable installs
    __version__ = "0.0.0.dev0"

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
    # Squat Jump API
    "process_sj_video",
    "process_sj_videos_bulk",
    "SJVideoConfig",
    "SJVideoResult",
    "SJMetrics",
    "__version__",
]
