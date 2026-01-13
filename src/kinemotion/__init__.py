"""Kinemotion: Video-based kinematic analysis for athletic performance.

Supports Counter Movement Jump (CMJ) and Drop Jump analysis using MediaPipe pose estimation.
"""

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
from .dj.kinematics import DropJumpMetrics

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
    "__version__",
]
