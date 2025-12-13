"""Public API for programmatic use of kinemotion analysis.

This module provides a unified interface for both drop jump and counter-movement
jump (CMJ) video analysis. Users can import analysis functions and configuration
classes directly from this module.

Supported jump analysis types:
- Drop jump (DJ): Ground contact time, reactive strength index (RSI)
- Counter-movement jump (CMJ): Jump height, flight time, countermovement depth

The actual implementations have been moved to their respective submodules:
- Drop jump: kinemotion.dropjump.api
- CMJ: kinemotion.cmj.api

Example:
    from kinemotion import process_dropjump_video, process_cmj_video

    # Analyze drop jump
    dj_result = process_dropjump_video("video.mp4", quality="balanced")

    # Analyze CMJ
    cmj_result = process_cmj_video("video.mp4", quality="balanced")
"""

# CMJ API
from .cmj.api import (
    AnalysisOverrides as CMJAnalysisOverrides,
)
from .cmj.api import (
    CMJVideoConfig,
    CMJVideoResult,
    process_cmj_video,
    process_cmj_videos_bulk,
)
from .cmj.kinematics import CMJMetrics

# Drop jump API
from .dropjump.api import (
    AnalysisOverrides,
    DropJumpVideoConfig,
    DropJumpVideoResult,
    process_dropjump_video,
    process_dropjump_videos_bulk,
)

__all__ = [
    # Drop jump
    "AnalysisOverrides",
    "DropJumpVideoConfig",
    "DropJumpVideoResult",
    "process_dropjump_video",
    "process_dropjump_videos_bulk",
    # CMJ
    "CMJAnalysisOverrides",
    "CMJMetrics",
    "CMJVideoConfig",
    "CMJVideoResult",
    "process_cmj_video",
    "process_cmj_videos_bulk",
]
