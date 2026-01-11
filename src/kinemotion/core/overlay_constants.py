"""Shared constants and type aliases for overlay renderers."""

from typing import Any

# Type aliases for overlay rendering
Color = tuple[int, int, int]
Landmark = tuple[float, float, float]
LandmarkDict = dict[str, Landmark]
CodecAttemptLog = list[dict[str, Any]]

# Visibility thresholds
VISIBILITY_THRESHOLD = 0.2
VISIBILITY_THRESHOLD_HIGH = 0.3
FOOT_VISIBILITY_THRESHOLD = 0.5

# Video encoding constants
MAX_VIDEO_DIMENSION = 720
CODECS_TO_TRY = ["avc1", "mp4v"]
FFMPEG_PRESET = "fast"
FFMPEG_CRF = "23"
FFMPEG_PIX_FMT = "yuv420p"

# Common colors (BGR format for OpenCV)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
CYAN = (255, 255, 0)
ORANGE = (0, 165, 255)

# Joint colors for triple extension
ANKLE_COLOR = (0, 255, 255)  # Cyan
KNEE_COLOR = (255, 100, 100)  # Light blue
HIP_COLOR = (100, 255, 100)  # Light green
TRUNK_COLOR = (100, 100, 255)  # Light red

# Angle thresholds
FULL_EXTENSION_ANGLE = 160
DEEP_FLEXION_ANGLE = 90

# Circle sizes
JOINT_CIRCLE_RADIUS = 6
JOINT_OUTLINE_RADIUS = 8
COM_CIRCLE_RADIUS = 15
COM_OUTLINE_RADIUS = 17
HIP_MARKER_RADIUS = 8
FOOT_CIRCLE_RADIUS = 10
FOOT_LANDMARK_RADIUS = 5
ANGLE_ARC_RADIUS = 25
NOSE_CIRCLE_RADIUS = 8
NOSE_OUTLINE_RADIUS = 10

# Box positioning
JOINT_ANGLES_BOX_X_OFFSET = 180
JOINT_ANGLES_BOX_HEIGHT = 150
METRICS_BOX_WIDTH = 320

# Phase label positioning
PHASE_LABEL_START_Y = 110
PHASE_LABEL_LINE_HEIGHT = 40
