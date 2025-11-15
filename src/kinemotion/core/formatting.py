"""Formatting utilities for consistent numeric output across jump analysis types.

This module provides shared helpers for formatting numeric values with appropriate
precision based on measurement type and capabilities of video-based analysis.
"""

# Standard precision values for different measurement types
# These values are chosen based on:
# - Video analysis capabilities (30-240 fps)
# - Typical measurement uncertainty in video-based biomechanics
# - Balance between accuracy and readability

PRECISION_TIME_MS = 2  # Time in milliseconds: ±0.01ms (e.g., 534.12)
PRECISION_DISTANCE_M = 3  # Distance in meters: ±1mm (e.g., 0.352)
PRECISION_VELOCITY_M_S = 4  # Velocity in m/s: ±0.0001 m/s (e.g., 2.6340)
PRECISION_FRAME = 3  # Sub-frame interpolation precision (e.g., 154.342)
PRECISION_NORMALIZED = 4  # Normalized values 0-1 ratios (e.g., 0.0582)


def format_float_metric(
    value: float | None,
    multiplier: float = 1.0,
    decimals: int = 2,
) -> float | None:
    """Format a float metric value with optional scaling and rounding.

    This helper ensures consistent precision across all jump analysis outputs,
    preventing false precision in measurements while maintaining appropriate
    accuracy for the measurement type.

    Args:
        value: The value to format, or None
        multiplier: Factor to multiply value by (e.g., 1000 for seconds→milliseconds)
        decimals: Number of decimal places to round to

    Returns:
        Formatted value rounded to specified decimals, or None if input is None

    Examples:
        >>> format_float_metric(0.534123, 1000, 2)  # seconds to ms
        534.12
        >>> format_float_metric(0.3521234, 1, 3)  # meters
        0.352
        >>> format_float_metric(None, 1, 2)
        None
        >>> format_float_metric(-1.23456, 1, 4)  # negative values preserved
        -1.2346
    """
    if value is None:
        return None
    return round(value * multiplier, decimals)


def format_int_metric(value: float | int | None) -> int | None:
    """Format a value as an integer.

    Used for frame numbers and other integer-valued metrics.

    Args:
        value: The value to format, or None

    Returns:
        Value converted to int, or None if input is None

    Examples:
        >>> format_int_metric(42.7)
        42
        >>> format_int_metric(None)
        None
        >>> format_int_metric(154)
        154
    """
    if value is None:
        return None
    return int(value)
