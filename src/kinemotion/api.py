"""Public API for programmatic use of kinemotion analysis.

This module provides a unified interface for both drop jump and CMJ video analysis.
The actual implementations have been moved to their respective submodules:
- Drop jump: kinemotion.dropjump.api
- CMJ: kinemotion.cmj.api

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
