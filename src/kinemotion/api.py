"""Public API for programmatic use of kinemotion analysis.

This module provides a unified interface for drop jump, CMJ, and Squat Jump analysis.
The actual implementations have been moved to their respective submodules:
- Drop jump: kinemotion.drop_jump.api
- CMJ: kinemotion.countermovement_jump.api
- Squat Jump: kinemotion.squat_jump.api

"""

# CMJ API
from .countermovement_jump.api import (
    AnalysisOverrides as CMJAnalysisOverrides,
)
from .countermovement_jump.api import (
    CMJVideoConfig,
    CMJVideoResult,
    process_cmj_video,
    process_cmj_videos_bulk,
)
from .countermovement_jump.kinematics import CMJMetrics

# Drop jump API
from .drop_jump.api import (
    AnalysisOverrides,
    DropJumpVideoConfig,
    DropJumpVideoResult,
    process_dropjump_video,
    process_dropjump_videos_bulk,
)

# Squat Jump API
from .squat_jump.api import (
    AnalysisOverrides as SJAnalysisOverrides,
)
from .squat_jump.api import (
    SJVideoConfig,
    SJVideoResult,
    process_sj_video,
    process_sj_videos_bulk,
)
from .squat_jump.kinematics import SJMetrics

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
    # Squat Jump
    "SJAnalysisOverrides",
    "SJMetrics",
    "SJVideoConfig",
    "SJVideoResult",
    "process_sj_video",
    "process_sj_videos_bulk",
]
