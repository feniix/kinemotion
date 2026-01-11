"""Central type definitions for the kinemotion package.

This module provides all type aliases used throughout the codebase to ensure
consistent typing and better IDE support.
"""

from typing import Any, TypeAlias

import numpy as np
from numpy.typing import NDArray

# NumPy array types for various use cases
FloatArray: TypeAlias = NDArray[np.floating[Any]]
Float64Array: TypeAlias = NDArray[np.float64]
IntArray: TypeAlias = NDArray[np.integer[Any]]
UInt8Array: TypeAlias = NDArray[np.uint8]
BoolArray: TypeAlias = NDArray[np.bool_]

# MediaPipe landmark types
# Using dict-based representation since MediaPipe lacks proper type stubs
LandmarkCoord: TypeAlias = tuple[float, float, float]  # (x, y, visibility)
LandmarkFrame: TypeAlias = dict[str, LandmarkCoord] | None
LandmarkSequence: TypeAlias = list[LandmarkFrame]

# Metrics dictionary type
# Uses Any because metrics can contain:
# - Simple values: float, int, str
# - Nested dicts: e.g. "triple_extension" contains angle data
# - Wrapper structures: e.g. {"data": {...actual metrics...}}
MetricsDict: TypeAlias = dict[str, Any]

# MediaPipe foot landmark names used for position and visibility tracking
FOOT_KEYS: tuple[str, ...] = (
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index",
)

# MediaPipe hip landmark names used for position tracking
HIP_KEYS: tuple[str, ...] = ("left_hip", "right_hip")

__all__ = [
    "FloatArray",
    "Float64Array",
    "IntArray",
    "UInt8Array",
    "BoolArray",
    "LandmarkCoord",
    "LandmarkFrame",
    "LandmarkSequence",
    "MetricsDict",
    "FOOT_KEYS",
    "HIP_KEYS",
]
