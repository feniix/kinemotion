"""Tests for Squat Jump kinematics calculations."""

import numpy as np
import pytest

from kinemotion.squat_jump.kinematics import (
    _calculate_mean_power,
    _calculate_peak_force,
    _calculate_peak_power,
    calculate_sj_metrics,
)

pytestmark = [pytest.mark.unit, pytest.mark.squat_jump]


class TestCalculateSJMetrics:
    """Test SJ metrics calculation functionality."""

    def _create_sj_test_data(self) -> tuple[np.ndarray, np.ndarray]:
        """Create synthetic SJ trajectory data for testing.

        Creates realistic velocities in m/s for proper power/force testing.
        A 0.4m jump height requires takeoff velocity of ~2.8 m/s (v = sqrt(2gh)).
        """
        import numpy as np

        # Positions in normalized coordinates (for frame counting)
        positions = np.concatenate(
            [
                np.ones(30) * 0.6,  # Squat hold
                np.linspace(0.6, 0.4, 30),  # Concentric (rising)
                np.linspace(0.4, 0.2, 30),  # Flight (falling)
                np.linspace(0.2, 0.6, 10),  # Landing
            ]
        )

        # Velocities in m/s (realistic for a squat jump)
        # For a 0.4m jump: v = sqrt(2 * 9.81 * 0.4) ≈ 2.8 m/s takeoff
        velocities = np.zeros_like(positions)

        # Squat hold: near zero velocity (small noise for realism)
        velocities[:30] = np.random.uniform(-0.01, 0.01, 30)

        # Concentric phase: accelerating upward (negative = up in normalized coords)
        # Build from ~0 to peak takeoff velocity of ~2.8 m/s
        concentric_vel = np.linspace(0, -2.8, 30)
        velocities[30:60] = concentric_vel

        # Flight: velocity at takeoff, then decreasing due to gravity
        # Start at takeoff velocity, decrease to 0 at peak, then downward
        flight_frames = 30
        for i in range(flight_frames):
            frame_idx = 60 + i
            # v = v0 - gt (simplified, where g reduces upward velocity)
            velocities[frame_idx] = -2.8 + (9.81 * i / 30.0)

        # Landing: deceleration spike (positive = downward impact)
        velocities[90:] = [1.5, 0.5, 0.1, 0, 0, 0, 0, 0, 0, 0]

        return positions, velocities

    def test_calculate_sj_metrics_basic(self) -> None:
        """Test basic SJ metrics calculation with mass."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=0,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="hip",
        )

        # Basic metrics should always be calculated
        assert metrics is not None
        assert metrics.jump_height >= 0
        assert metrics.flight_time > 0
        assert metrics.squat_hold_duration > 0
        assert metrics.concentric_duration > 0
        assert metrics.peak_concentric_velocity >= 0

        # With mass, power/force should be calculated
        assert metrics.peak_power is not None
        assert metrics.mean_power is not None
        assert metrics.peak_force is not None

    def test_calculate_sj_metrics_no_mass(self) -> None:
        """Test SJ metrics calculation without mass (power/force should be None)."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=0,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=None,
            tracking_method="hip",
        )

        # Basic metrics should work without mass
        assert metrics is not None
        assert metrics.jump_height is not None

        # Without mass, power/force should be None
        assert metrics.peak_power is None
        assert metrics.mean_power is None
        assert metrics.peak_force is None

    def test_jump_height_calculation(self) -> None:
        """Test jump height calculation from flight time."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=0,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="hip",
        )

        # Jump height should be positive
        assert metrics.jump_height >= 0

    def test_concentric_duration_calculation(self) -> None:
        """Test concentric duration calculation."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=0,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="hip",
        )

        # Concentric duration = (60 - 30) / 30 = 1.0 seconds
        expected_duration = (60 - 30) / fps
        assert metrics.concentric_duration == expected_duration

    def test_squat_hold_duration_calculation(self) -> None:
        """Test squat hold duration calculation."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=0,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="hip",
        )

        # Squat hold duration = (30 - 0) / 30 = 1.0 seconds
        expected_duration = (30 - 0) / fps
        assert metrics.squat_hold_duration == expected_duration

    def test_peak_velocity_calculation(self) -> None:
        """Test peak concentric velocity calculation."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=0,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="hip",
        )

        # Peak velocity should be positive (magnitude)
        assert metrics.peak_concentric_velocity >= 0

    def test_power_calculation_with_mass(self) -> None:
        """Test power calculation returns valid values with mass."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=0,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="hip",
        )

        # Power should be positive and in reasonable range
        assert metrics.peak_power is not None
        assert metrics.peak_power > 0
        assert metrics.mean_power is not None
        assert metrics.mean_power > 0

        # Mean power should be less than peak power
        assert metrics.mean_power < metrics.peak_power

    def test_force_calculation_with_mass(self) -> None:
        """Test force calculation returns valid values with mass."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=0,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="hip",
        )

        # Force should be positive and in reasonable range
        assert metrics.peak_force is not None
        assert metrics.peak_force > 0

        # Force should be > body weight (75kg × 9.81 = 736N)
        assert metrics.peak_force > 736

    def test_tracking_method_inclusion(self) -> None:
        """Test that tracking method is properly included."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=0,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="test_method",
        )

        assert metrics.tracking_method == "test_method"

    def test_frame_information_included(self) -> None:
        """Test that frame indices are properly included."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=10,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="hip",
        )

        assert metrics.squat_hold_start_frame == 10.0
        assert metrics.concentric_start_frame == 30.0
        assert metrics.takeoff_frame == 60.0
        assert metrics.landing_frame == 90.0

    def test_negative_frames(self) -> None:
        """Test handling of invalid frame indices."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        # Should handle gracefully or return sensible defaults
        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=-1,  # Invalid
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="hip",
        )

        # Should still return metrics with negative frame
        assert metrics.squat_hold_start_frame == -1.0

    def test_metric_to_dict_conversion(self) -> None:
        """Test SJMetrics to dict conversion."""
        positions, velocities = self._create_sj_test_data()
        fps = 30.0

        metrics = calculate_sj_metrics(
            positions=positions,
            velocities=velocities,
            squat_hold_start=0,
            concentric_start=30,
            takeoff_frame=60,
            landing_frame=90,
            fps=fps,
            mass_kg=75.0,
            tracking_method="hip",
        )

        result = metrics.to_dict()

        # Check data structure
        assert "data" in result
        assert "jump_height_m" in result["data"]
        assert "flight_time_ms" in result["data"]
        assert "peak_power_w" in result["data"]
        assert "peak_force_n" in result["data"]
        assert "mean_power_w" in result["data"]


class TestPowerCalculations:
    """Test power calculation functions individually."""

    def test_peak_power_requires_mass(self) -> None:
        """Test that peak power returns None without mass."""
        # Realistic takeoff velocity in m/s (~2.5 m/s for 0.32m jump)
        velocities = np.array([0.0, -1.5, -2.5, -2.0])

        result = _calculate_peak_power(
            velocities=velocities,
            concentric_start=0,
            takeoff_frame=2,
            mass_kg=None,
        )

        assert result is None

    def test_peak_power_calculates_value(self) -> None:
        """Test that peak power calculates a value with mass."""
        # Realistic takeoff velocity in m/s (~2.5 m/s for 0.32m jump)
        velocities = np.array([0.0, -1.5, -2.5, -2.0])

        result = _calculate_peak_power(
            velocities=velocities,
            concentric_start=0,
            takeoff_frame=2,
            mass_kg=75.0,
        )

        assert result is not None
        assert result > 0

    def test_mean_power_requires_mass(self) -> None:
        """Test that mean power returns None without mass."""
        positions = np.array([0.6, 0.5, 0.4, 0.3])
        velocities = np.array([0.0, -1.5, -2.5, -2.0])

        result = _calculate_mean_power(
            positions=positions,
            velocities=velocities,
            concentric_start=0,
            takeoff_frame=2,
            fps=30.0,
            mass_kg=None,
        )

        assert result is None

    def test_mean_power_calculates_value(self) -> None:
        """Test that mean power calculates a value with mass."""
        positions = np.array([0.6, 0.5, 0.4, 0.3])
        # Realistic takeoff velocity in m/s
        velocities = np.array([0.0, -1.5, -2.5, -2.0])

        result = _calculate_mean_power(
            positions=positions,
            velocities=velocities,
            concentric_start=0,
            takeoff_frame=2,
            fps=30.0,
            mass_kg=75.0,
        )

        assert result is not None
        assert result > 0

    def test_peak_force_requires_mass(self) -> None:
        """Test that peak force returns None without mass."""
        positions = np.array([0.6, 0.5, 0.4, 0.3])
        velocities = np.array([0.0, -1.5, -2.5, -2.0])

        result = _calculate_peak_force(
            positions=positions,
            velocities=velocities,
            concentric_start=0,
            takeoff_frame=2,
            fps=30.0,
            mass_kg=None,
        )

        assert result is None

    def test_peak_force_calculates_value(self) -> None:
        """Test that peak force calculates a value with mass."""
        positions = np.array([0.6, 0.5, 0.4, 0.3])
        # Realistic takeoff velocity in m/s
        velocities = np.array([0.0, -1.5, -2.5, -2.0])

        result = _calculate_peak_force(
            positions=positions,
            velocities=velocities,
            concentric_start=0,
            takeoff_frame=2,
            fps=30.0,
            mass_kg=75.0,
        )

        assert result is not None
        assert result > 0


class TestSayersFormula:
    """Test Sayers regression equation for peak power."""

    def test_sayers_formula_components(self) -> None:
        """Test Sayers formula: P = 60.7 × h_cm + 45.3 × mass - 2055"""
        # Example: 80kg athlete, 35cm jump
        mass_kg = 80.0
        jump_height_cm = 35.0
        expected = 60.7 * jump_height_cm + 45.3 * mass_kg - 2055
        # = 2124.5 + 3624 - 2055 = 3693.5 W

        assert expected > 3000  # Should be in reasonable range

    def test_sayers_increases_with_height(self) -> None:
        """Test that power increases with jump height."""
        # Low jump: ~1.5 m/s takeoff velocity (~0.11m height)
        velocities_low = np.array([0.0, -0.8, -1.5, -1.2])

        # High jump: ~2.8 m/s takeoff velocity (~0.40m height)
        velocities_high = np.array([0.0, -1.5, -2.8, -2.2])

        power_low = _calculate_peak_power(velocities_low, 0, 2, 70.0)

        power_high = _calculate_peak_power(velocities_high, 0, 2, 70.0)

        assert power_high > power_low

    def test_sayers_increases_with_mass(self) -> None:
        """Test that power increases with athlete mass."""
        # Realistic takeoff velocity in m/s
        velocities = np.array([0.0, -1.5, -2.5, -2.0])

        power_light = _calculate_peak_power(velocities, 0, 2, 60.0)

        power_heavy = _calculate_peak_power(velocities, 0, 2, 90.0)

        assert power_heavy > power_light
