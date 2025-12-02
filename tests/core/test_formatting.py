"""Tests for numeric formatting utilities."""

from kinemotion.core.formatting import (
    PRECISION_DISTANCE_M,
    PRECISION_FRAME,
    PRECISION_NORMALIZED,
    PRECISION_TIME_MS,
    PRECISION_VELOCITY_M_S,
    format_float_metric,
    format_int_metric,
)


class TestFormatFloatMetric:
    """Test float metric formatting."""

    def test_basic_rounding(self) -> None:
        """Test basic rounding without scaling."""
        assert format_float_metric(1.23456, 1, 2) == 1.23
        assert format_float_metric(1.23456, 1, 3) == 1.235
        assert format_float_metric(1.23456, 1, 4) == 1.2346

    def test_scaling_with_rounding(self) -> None:
        """Test scaling (e.g., seconds to milliseconds) with rounding."""
        # Seconds to milliseconds
        assert format_float_metric(0.534123, 1000, 2) == 534.12
        assert format_float_metric(0.001, 1000, 2) == 1.0
        assert format_float_metric(1.999999, 1000, 2) == 2000.0

    def test_none_handling(self) -> None:
        """Test that None values pass through."""
        assert format_float_metric(None, 1, 2) is None
        assert format_float_metric(None, 1000, 3) is None

    def test_negative_values(self) -> None:
        """Test that negative values are preserved."""
        assert format_float_metric(-1.23456, 1, 2) == -1.23
        assert format_float_metric(-0.534, 1000, 2) == -534.0

    def test_zero_values(self) -> None:
        """Test zero handling."""
        assert format_float_metric(0.0, 1, 2) == 0.0
        assert format_float_metric(0.0, 1000, 2) == 0.0

    def test_precision_constants(self) -> None:
        """Test that precision constants are defined correctly."""
        assert PRECISION_TIME_MS == 2
        assert PRECISION_DISTANCE_M == 3
        assert PRECISION_VELOCITY_M_S == 4
        assert PRECISION_FRAME == 3
        assert PRECISION_NORMALIZED == 4


class TestFormatIntMetric:
    """Test integer metric formatting."""

    def test_float_to_int(self) -> None:
        """Test float to integer conversion."""
        assert format_int_metric(42.7) == 42
        assert format_int_metric(42.2) == 42
        assert format_int_metric(42.9) == 42

    def test_int_passthrough(self) -> None:
        """Test that integers pass through."""
        assert format_int_metric(42) == 42
        assert format_int_metric(0) == 0

    def test_none_handling(self) -> None:
        """Test that None values pass through."""
        assert format_int_metric(None) is None

    def test_negative_values(self) -> None:
        """Test negative value handling."""
        assert format_int_metric(-42.7) == -42


class TestPrecisionConsistency:
    """Test precision consistency across measurement types."""

    def test_time_precision(self) -> None:
        """Test time measurements use 2 decimal places."""
        # Time in milliseconds
        time_ms = format_float_metric(534.123456, 1, PRECISION_TIME_MS)
        assert time_ms == 534.12

        # Seconds to milliseconds
        time_s_to_ms = format_float_metric(0.534123456, 1000, PRECISION_TIME_MS)
        assert time_s_to_ms == 534.12

    def test_distance_precision(self) -> None:
        """Test distance measurements use 3 decimal places."""
        # Jump height in meters
        height = format_float_metric(0.35212345, 1, PRECISION_DISTANCE_M)
        assert height == 0.352

        # Countermovement depth
        depth = format_float_metric(0.04512345, 1, PRECISION_DISTANCE_M)
        assert depth == 0.045

    def test_velocity_precision(self) -> None:
        """Test velocity measurements use 4 decimal places."""
        # Velocity in m/s
        velocity = format_float_metric(2.63401234, 1, PRECISION_VELOCITY_M_S)
        assert velocity == 2.634

        # Negative velocity (downward)
        neg_velocity = format_float_metric(-1.23459999, 1, PRECISION_VELOCITY_M_S)
        assert neg_velocity == -1.2346

    def test_frame_precision(self) -> None:
        """Test frame numbers use 3 decimal places for sub-frame precision."""
        frame = format_float_metric(154.342567, 1, PRECISION_FRAME)
        assert frame == 154.343

    def test_normalized_precision(self) -> None:
        """Test normalized values use 4 decimal places."""
        normalized = format_float_metric(0.058234567, 1, PRECISION_NORMALIZED)
        assert normalized == 0.0582


class TestRealWorldExamples:
    """Test with real-world measurement examples."""

    def test_cmj_measurements(self) -> None:
        """Test CMJ measurement formatting."""
        # Jump height: 0.40502274976565683 → 0.405
        assert format_float_metric(0.40502274976565683, 1, 3) == 0.405

        # Flight time: 0.57471 seconds → 574.71 ms
        assert format_float_metric(0.57471, 1000, 2) == 574.71

        # Countermovement depth: 0.0024646043777466486 → 0.002
        assert format_float_metric(0.0024646043777466486, 1, 3) == 0.002

        # Peak velocity: 0.0028023441632588253 → 0.0028
        assert format_float_metric(0.0028023441632588253, 1, 4) == 0.0028

    def test_dropjump_measurements(self) -> None:
        """Test drop jump measurement formatting."""
        # Ground contact time: 0.35709 seconds → 357.09 ms
        assert format_float_metric(0.35709, 1000, 2) == 357.09

        # Jump height: 0.259123 → 0.259
        assert format_float_metric(0.259123, 1, 3) == 0.259

        # Trajectory normalized: 0.058234 → 0.0582
        assert format_float_metric(0.058234, 1, 4) == 0.0582

        # Precise frame: 32.034567 → 32.035
        assert format_float_metric(32.034567, 1, 3) == 32.035


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_small_values(self) -> None:
        """Test very small values near zero."""
        # Should not use scientific notation
        assert format_float_metric(0.0001, 1, 4) == 0.0001
        assert format_float_metric(0.00001, 1, 5) == 0.00001

    def test_very_large_values(self) -> None:
        """Test very large values."""
        assert format_float_metric(999999.123, 1, 2) == 999999.12
        assert format_float_metric(1000000.5, 1, 1) == 1000000.5

    def test_exact_values(self) -> None:
        """Test values that are exact after rounding."""
        assert format_float_metric(1.5, 1, 2) == 1.5
        assert format_float_metric(1.50, 1, 2) == 1.5
        assert format_float_metric(0.0, 1, 3) == 0.0

    def test_rounding_at_boundary(self) -> None:
        """Test rounding at .5 boundary (Python uses banker's rounding)."""
        # Banker's rounding: round to nearest even
        assert format_float_metric(2.5, 1, 0) == 2.0  # rounds to even (2)
        assert format_float_metric(3.5, 1, 0) == 4.0  # rounds to even (4)
        assert format_float_metric(1.25, 1, 1) == 1.2  # rounds to even (1.2)
        assert format_float_metric(1.35, 1, 1) == 1.4  # rounds to even (1.4)
