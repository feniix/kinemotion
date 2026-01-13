"""Joint angle calculations for triple extension analysis."""

import math

import numpy as np


def _get_side_prefix(side: str) -> str:
    """Get the landmark key prefix for a given side.

    Args:
        side: Which side ("left" or "right")

    Returns:
        The prefix string for landmark keys
    """
    return "left_" if side == "left" else "right_"


def _is_landmark_visible(
    landmarks: dict[str, tuple[float, float, float]],
    key: str,
    threshold: float = 0.3,
) -> bool:
    """Check if a landmark meets the minimum visibility threshold.

    Args:
        landmarks: Pose landmarks dictionary
        key: Landmark key to check
        threshold: Minimum visibility threshold (default: 0.3)

    Returns:
        True if landmark exists and meets visibility threshold
    """
    return key in landmarks and landmarks[key][2] >= threshold


def _get_landmark_xy(
    landmarks: dict[str, tuple[float, float, float]],
    key: str,
) -> tuple[float, float] | None:
    """Extract x, y coordinates from a landmark.

    Args:
        landmarks: Pose landmarks dictionary
        key: Landmark key to extract

    Returns:
        Tuple of (x, y) coordinates, or None if key not found
    """
    if key not in landmarks:
        return None
    return (landmarks[key][0], landmarks[key][1])


def calculate_angle_3_points(
    point1: tuple[float, float],
    point2: tuple[float, float],
    point3: tuple[float, float],
) -> float:
    """
    Calculate angle at point2 formed by three points.

    Uses the law of cosines to find the angle at the middle point.

    Args:
        point1: First point (x, y) - e.g., foot
        point2: Middle point (x, y) - e.g., knee (vertex of angle)
        point3: Third point (x, y) - e.g., hip

    Returns:
        Angle in degrees (0-180)

    Example:
        >>> # Calculate knee angle
        >>> ankle = (0.5, 0.8)
        >>> knee = (0.5, 0.6)
        >>> hip = (0.5, 0.4)
        >>> angle = calculate_angle_3_points(ankle, knee, hip)
        >>> # angle ≈ 180 (straight leg)
    """
    # Convert points to numpy arrays
    p1 = np.array(point1)
    p2 = np.array(point2)
    p3 = np.array(point3)

    # Calculate vectors from point2 to point1 and point3
    v1 = p1 - p2
    v2 = p3 - p2

    # Calculate angle using dot product
    # cos(angle) = (v1 · v2) / (|v1| * |v2|)
    dot_product = np.dot(v1, v2)
    magnitude1 = np.linalg.norm(v1)
    magnitude2 = np.linalg.norm(v2)

    # Avoid division by zero
    if magnitude1 < 1e-9 or magnitude2 < 1e-9:
        return 0.0

    # Calculate angle in radians, then convert to degrees
    cos_angle = dot_product / (magnitude1 * magnitude2)

    # Clamp to [-1, 1] to avoid numerical errors with arccos
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    angle_rad = math.acos(cos_angle)
    angle_deg = math.degrees(angle_rad)

    return float(angle_deg)


def calculate_ankle_angle(
    landmarks: dict[str, tuple[float, float, float]], side: str = "right"
) -> float | None:
    """
    Calculate ankle angle (dorsiflexion/plantarflexion).

    Angle formed by: foot_index -> ankle -> knee (primary)
    Falls back to heel -> ankle -> knee if foot_index visibility < 0.5

    Measurements:
    - 90° = neutral (foot perpendicular to shin)
    - < 90° = dorsiflexion (toes up)
    - > 90° = plantarflexion (toes down)

    Technical note:
    - foot_index (toe tip) is used for accurate plantarflexion measurement
    - Heel is relatively static during push-off; toes (foot_index) actively plantarflex
    - Expected range during CMJ: 80° (standing) -> 130°+ (plantarflex at takeoff)

    Args:
        landmarks: Pose landmarks dictionary
        side: Which side to measure ("left" or "right")

    Returns:
        Ankle angle in degrees, or None if landmarks not available
    """
    prefix = _get_side_prefix(side)

    foot_index_key = f"{prefix}foot_index"
    heel_key = f"{prefix}heel"
    ankle_key = f"{prefix}ankle"
    knee_key = f"{prefix}knee"

    # Check ankle and knee visibility (required)
    if not _is_landmark_visible(landmarks, ankle_key):
        return None
    if not _is_landmark_visible(landmarks, knee_key):
        return None

    ankle = _get_landmark_xy(landmarks, ankle_key)
    knee = _get_landmark_xy(landmarks, knee_key)

    if ankle is None or knee is None:
        return None

    # Try foot_index first (primary: toe tip for plantarflexion accuracy)
    if _is_landmark_visible(landmarks, foot_index_key, threshold=0.5):
        foot_point = _get_landmark_xy(landmarks, foot_index_key)
        if foot_point is not None:
            return calculate_angle_3_points(foot_point, ankle, knee)

    # Fallback to heel if foot_index visibility is insufficient
    if _is_landmark_visible(landmarks, heel_key):
        foot_point = _get_landmark_xy(landmarks, heel_key)
        if foot_point is not None:
            return calculate_angle_3_points(foot_point, ankle, knee)

    # No valid foot landmark available
    return None


def calculate_knee_angle(
    landmarks: dict[str, tuple[float, float, float]], side: str = "right"
) -> float | None:
    """
    Calculate knee angle (flexion/extension).

    Angle formed by: ankle -> knee -> hip
    - 180° = full extension (straight leg)
    - 90° = 90° flexion (deep squat)
    - 0° = full flexion (not physiologically possible)

    Args:
        landmarks: Pose landmarks dictionary
        side: Which side to measure ("left" or "right")

    Returns:
        Knee angle in degrees, or None if landmarks not available
    """
    prefix = _get_side_prefix(side)

    ankle_key = f"{prefix}ankle"
    knee_key = f"{prefix}knee"
    hip_key = f"{prefix}hip"

    # Check visibility
    if not _is_landmark_visible(landmarks, ankle_key):
        # Fallback: use foot_index if ankle not visible
        foot_key = f"{prefix}foot_index"
        if _is_landmark_visible(landmarks, foot_key):
            ankle_key = foot_key
        else:
            return None

    if not _is_landmark_visible(landmarks, knee_key):
        return None
    if not _is_landmark_visible(landmarks, hip_key):
        return None

    ankle = _get_landmark_xy(landmarks, ankle_key)
    knee = _get_landmark_xy(landmarks, knee_key)
    hip = _get_landmark_xy(landmarks, hip_key)

    if ankle is None or knee is None or hip is None:
        return None

    return calculate_angle_3_points(ankle, knee, hip)


def calculate_hip_angle(
    landmarks: dict[str, tuple[float, float, float]], side: str = "right"
) -> float | None:
    """
    Calculate hip angle (flexion/extension).

    Angle formed by: knee -> hip -> shoulder
    - 180° = standing upright (trunk and thigh aligned)
    - 90° = 90° hip flexion (torso perpendicular to thigh)
    - < 90° = deep flexion (squat position)

    Args:
        landmarks: Pose landmarks dictionary
        side: Which side to measure ("left" or "right")

    Returns:
        Hip angle in degrees, or None if landmarks not available
    """
    prefix = _get_side_prefix(side)

    knee_key = f"{prefix}knee"
    hip_key = f"{prefix}hip"
    shoulder_key = f"{prefix}shoulder"

    # Check visibility
    if not _is_landmark_visible(landmarks, knee_key):
        return None
    if not _is_landmark_visible(landmarks, hip_key):
        return None
    if not _is_landmark_visible(landmarks, shoulder_key):
        return None

    knee = _get_landmark_xy(landmarks, knee_key)
    hip = _get_landmark_xy(landmarks, hip_key)
    shoulder = _get_landmark_xy(landmarks, shoulder_key)

    if knee is None or hip is None or shoulder is None:
        return None

    return calculate_angle_3_points(knee, hip, shoulder)


def calculate_trunk_tilt(
    landmarks: dict[str, tuple[float, float, float]], side: str = "right"
) -> float | None:
    """
    Calculate trunk tilt angle relative to vertical.

    Measures forward/backward lean of the torso.
    - 0° = perfectly vertical
    - Positive = leaning forward
    - Negative = leaning backward

    Args:
        landmarks: Pose landmarks dictionary
        side: Which side to measure ("left" or "right")

    Returns:
        Trunk tilt angle in degrees, or None if landmarks not available
    """
    prefix = _get_side_prefix(side)

    hip_key = f"{prefix}hip"
    shoulder_key = f"{prefix}shoulder"

    # Check visibility
    if not _is_landmark_visible(landmarks, hip_key):
        return None
    if not _is_landmark_visible(landmarks, shoulder_key):
        return None

    hip_xy = _get_landmark_xy(landmarks, hip_key)
    shoulder_xy = _get_landmark_xy(landmarks, shoulder_key)

    if hip_xy is None or shoulder_xy is None:
        return None

    hip = np.array([hip_xy[0], hip_xy[1]])
    shoulder = np.array([shoulder_xy[0], shoulder_xy[1]])

    # Vector from hip to shoulder
    trunk_vector = shoulder - hip

    # Vertical reference (in normalized coords, vertical is along y-axis)
    # Negative y direction is up in frame coordinates
    vertical = np.array([0, -1])

    # Calculate angle from vertical
    dot_product = np.dot(trunk_vector, vertical)
    magnitude_trunk = np.linalg.norm(trunk_vector)

    if magnitude_trunk < 1e-9:
        return None

    cos_angle = dot_product / magnitude_trunk
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    angle_rad = math.acos(cos_angle)
    angle_deg = math.degrees(angle_rad)

    # Determine if leaning forward or backward based on x-component
    if trunk_vector[0] > 0:  # Shoulder to the right of hip = leaning forward
        return float(angle_deg)
    else:
        return float(-angle_deg)


def calculate_triple_extension(
    landmarks: dict[str, tuple[float, float, float]], side: str = "right"
) -> dict[str, float | None] | None:
    """
    Calculate all three joint angles for triple extension analysis.

    Triple extension refers to simultaneous extension of ankle, knee, and hip joints
    during the propulsive phase of jumping. This is a key indicator of proper technique.

    NOTE: In side-view videos, ankle/knee may have low visibility from MediaPipe.
    Returns partial results with None for unavailable angles.

    Args:
        landmarks: Pose landmarks dictionary
        side: Which side to measure ("left" or "right")

    Returns:
        Dictionary with angle measurements:
        - ankle_angle: Ankle angle or None
        - knee_angle: Knee angle or None
        - hip_angle: Hip angle or None
        - trunk_tilt: Trunk lean angle or None
        Returns None if NO angles can be calculated

    Example:
        >>> angles = calculate_triple_extension(landmarks, side="right")
        >>> if angles and angles['knee_angle']:
        ...     print(f"Knee: {angles['knee_angle']:.0f}°")
    """
    ankle = calculate_ankle_angle(landmarks, side)
    knee = calculate_knee_angle(landmarks, side)
    hip = calculate_hip_angle(landmarks, side)
    trunk = calculate_trunk_tilt(landmarks, side)

    # Return results even if some are None (at least trunk should be available)
    if ankle is None and knee is None and hip is None and trunk is None:
        return None  # No angles available at all

    return {
        "ankle_angle": ankle,
        "knee_angle": knee,
        "hip_angle": hip,
        "trunk_tilt": trunk,
    }
