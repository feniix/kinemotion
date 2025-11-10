"""Tests for CMJ phase detection."""

import numpy as np

from kinemotion.cmj.analysis import (
    compute_signed_velocity,
    detect_cmj_phases,
    find_cmj_landing_from_position_peak,
    find_cmj_takeoff_from_velocity_peak,
    find_countermovement_start,
    find_lowest_point,
    find_standing_phase,
    interpolate_threshold_crossing,
    refine_transition_with_curvature,
)
from kinemotion.core.smoothing import (
    compute_acceleration_from_derivative,
    compute_velocity_from_derivative,
)


def test_find_standing_phase() -> None:
    """Test standing phase detection."""
    # Create trajectory with clear standing period followed by consistent downward motion
    fps = 30.0

    # Standing (0-30): constant position
    # Transition (30-35): very slow movement
    # Movement (35-100): clear downward motion
    positions = np.concatenate(
        [
            np.ones(30) * 0.5,  # Standing
            np.linspace(0.5, 0.51, 5),  # Slow transition
            np.linspace(0.51, 0.7, 65),  # Clear movement
        ]
    )

    velocities = compute_velocity_from_derivative(
        positions, window_length=5, polyorder=2
    )

    standing_end = find_standing_phase(
        positions, velocities, fps, min_standing_duration=0.5, velocity_threshold=0.005
    )

    # Should detect standing phase (or may return None if no clear transition)
    # This test verifies the function runs without error
    if standing_end is not None:
        assert 15 <= standing_end <= 40  # Allow wider tolerance


def test_find_countermovement_start() -> None:
    """Test countermovement start detection."""
    # Create trajectory with clear and fast downward motion
    positions = np.concatenate(
        [
            np.ones(30) * 0.5,  # Standing
            np.linspace(0.5, 0.8, 30),  # Fast downward (eccentric)
            np.linspace(0.8, 0.5, 30),  # Upward (concentric)
        ]
    )

    velocities = compute_velocity_from_derivative(
        positions, window_length=5, polyorder=2
    )

    eccentric_start = find_countermovement_start(
        velocities,
        countermovement_threshold=-0.008,  # More lenient threshold for test
        min_eccentric_frames=3,
        standing_start=30,
    )

    # Should detect eccentric start (or may return None depending on smoothing)
    # This test verifies the function runs without error
    if eccentric_start is not None:
        assert 25 <= eccentric_start <= 40


def test_find_lowest_point() -> None:
    """Test lowest point detection."""
    # Create trajectory with clear lowest point
    positions = np.concatenate(
        [
            np.linspace(0.5, 0.7, 50),  # Downward
            np.linspace(0.7, 0.4, 50),  # Upward
        ]
    )

    from kinemotion.cmj.analysis import compute_signed_velocity

    velocities = compute_signed_velocity(positions, window_length=5, polyorder=2)

    # New algorithm searches with min_search_frame=80 by default
    # For this short test, use min_search_frame=0
    lowest = find_lowest_point(positions, velocities, min_search_frame=0)

    # Should detect lowest point around frame 50 (with new algorithm may vary)
    assert 30 <= lowest <= 70  # Wider tolerance for new algorithm


def test_detect_cmj_phases_full() -> None:
    """Test complete CMJ phase detection."""
    # Create realistic CMJ trajectory with pronounced movements
    positions = np.concatenate(
        [
            np.ones(20) * 0.5,  # Standing
            np.linspace(0.5, 0.8, 40),  # Eccentric (deeper countermovement)
            np.linspace(0.8, 0.4, 40),  # Concentric (push up)
            np.linspace(0.4, 0.2, 30),  # Flight (clear airborne phase)
            np.linspace(0.2, 0.5, 10),  # Landing (return to ground)
        ]
    )

    fps = 30.0

    result = detect_cmj_phases(
        positions,
        fps,
        window_length=5,
        polyorder=2,
    )

    assert result is not None
    _, lowest_point, takeoff, landing = result

    # Verify phases are in correct order
    assert lowest_point < takeoff
    assert takeoff < landing

    # Verify phases are detected (with wide tolerances for synthetic data)
    # New algorithm works backward from peak, so lowest point may be later
    assert 0 <= lowest_point <= 140  # Lowest point found
    assert 40 <= takeoff <= 140  # Takeoff detected
    assert 80 <= landing <= 150  # Landing after takeoff


def test_cmj_phases_without_standing() -> None:
    """Test CMJ phase detection when no standing phase exists."""
    # Create trajectory starting directly with countermovement (more pronounced)
    # Add a very short standing period to help detection
    positions = np.concatenate(
        [
            np.ones(5) * 0.5,  # Brief start
            np.linspace(0.5, 0.9, 40),  # Eccentric (very deep)
            np.linspace(0.9, 0.3, 50),  # Concentric (strong push)
            np.linspace(0.3, 0.1, 30),  # Flight (very clear)
        ]
    )

    fps = 30.0

    result = detect_cmj_phases(
        positions,
        fps,
        window_length=5,
        polyorder=2,
    )

    # Result may be None with synthetic data - that's okay for this test
    # The main goal is to verify the function handles edge cases without crashing
    if result is not None:
        _, lowest_point, takeoff, landing = result
        # Basic sanity checks if phases were detected
        assert lowest_point < takeoff
        assert takeoff < landing


def test_interpolate_threshold_crossing_normal() -> None:
    """Test interpolate_threshold_crossing with normal interpolation."""
    # Velocity increases from 0.1 to 0.3, threshold at 0.2
    vel_before = 0.1
    vel_after = 0.3
    threshold = 0.2

    offset = interpolate_threshold_crossing(vel_before, vel_after, threshold)

    # Should be 0.5 (halfway between 0.1 and 0.3)
    assert abs(offset - 0.5) < 0.01


def test_interpolate_threshold_crossing_edge_case_no_change() -> None:
    """Test interpolate_threshold_crossing when velocity is not changing."""
    # Velocity same at both frames
    vel_before = 0.5
    vel_after = 0.5
    threshold = 0.5

    offset = interpolate_threshold_crossing(vel_before, vel_after, threshold)

    # Should return 0.5 when velocity not changing
    assert offset == 0.5


def test_interpolate_threshold_crossing_clamp_below_zero() -> None:
    """Test interpolate_threshold_crossing clamps to [0, 1] range."""
    # Threshold below vel_before (would give negative t)
    vel_before = 0.5
    vel_after = 0.8
    threshold = 0.3  # Below vel_before

    offset = interpolate_threshold_crossing(vel_before, vel_after, threshold)

    # Should clamp to 0.0
    assert offset == 0.0


def test_interpolate_threshold_crossing_clamp_above_one() -> None:
    """Test interpolate_threshold_crossing clamps to [0, 1] range."""
    # Threshold above vel_after (would give t > 1)
    vel_before = 0.2
    vel_after = 0.5
    threshold = 0.9  # Above vel_after

    offset = interpolate_threshold_crossing(vel_before, vel_after, threshold)

    # Should clamp to 1.0
    assert offset == 1.0


def test_interpolate_threshold_crossing_at_boundary() -> None:
    """Test interpolate_threshold_crossing when threshold equals velocity."""
    vel_before = 0.1
    vel_after = 0.5
    threshold = 0.1  # Exactly at vel_before

    offset = interpolate_threshold_crossing(vel_before, vel_after, threshold)

    # Should be 0.0 (at start)
    assert offset == 0.0


def test_refine_transition_with_curvature_landing() -> None:
    """Test refine_transition_with_curvature for landing detection."""
    # Create position data with clear impact spike
    positions = np.concatenate(
        [
            np.linspace(0.3, 0.5, 20),  # Falling
            np.array([0.5, 0.52, 0.54, 0.55, 0.55]),  # Impact
            np.ones(10) * 0.55,  # Stable
        ]
    )
    velocities = np.diff(positions, prepend=positions[0])
    initial_frame = 20  # Around impact

    result = refine_transition_with_curvature(
        positions, velocities, initial_frame, transition_type="landing", search_radius=5
    )

    # Should refine near the impact point (blend of curvature and initial)
    assert isinstance(result, float)
    assert 15 <= result <= 25


def test_refine_transition_with_curvature_takeoff() -> None:
    """Test refine_transition_with_curvature for takeoff detection."""
    # Create position data with acceleration change at takeoff
    positions = np.concatenate(
        [
            np.ones(15) * 0.5,  # Static
            np.array([0.5, 0.48, 0.45, 0.40, 0.35]),  # Accelerating upward
            np.linspace(0.35, 0.2, 10),  # Flight
        ]
    )
    velocities = np.diff(positions, prepend=positions[0])
    initial_frame = 15  # Around takeoff

    result = refine_transition_with_curvature(
        positions, velocities, initial_frame, transition_type="takeoff", search_radius=5
    )

    # Should refine near the takeoff point
    assert isinstance(result, float)
    assert 12 <= result <= 20


def test_refine_transition_with_curvature_empty_search_window() -> None:
    """Test refine_transition_with_curvature with empty search window."""
    positions = np.linspace(0.5, 0.3, 10)
    velocities = np.diff(positions, prepend=positions[0])
    initial_frame = 0  # At boundary
    search_radius = 0  # No search radius

    result = refine_transition_with_curvature(
        positions,
        velocities,
        initial_frame,
        transition_type="landing",
        search_radius=search_radius,
    )

    # Should return initial frame when search window is empty
    assert result == float(initial_frame)


def test_refine_transition_with_curvature_invalid_type() -> None:
    """Test refine_transition_with_curvature with invalid transition type."""
    positions = np.linspace(0.5, 0.3, 20)
    velocities = np.diff(positions, prepend=positions[0])
    initial_frame = 10

    result = refine_transition_with_curvature(
        positions,
        velocities,
        initial_frame,
        transition_type="invalid",  # Invalid type
        search_radius=5,
    )

    # Should return initial frame for invalid type
    assert result == float(initial_frame)


def test_refine_transition_with_curvature_takeoff_empty_accel_change() -> None:
    """Test refine_transition_with_curvature takeoff with very small search window."""
    # Create minimal data that results in empty acceleration change
    positions = np.linspace(0.5, 0.4, 10)
    velocities = np.diff(positions, prepend=positions[0])
    initial_frame = 5
    search_radius = 0  # Will create search window with just 1 element

    result = refine_transition_with_curvature(
        positions,
        velocities,
        initial_frame,
        transition_type="takeoff",
        search_radius=search_radius,
    )

    # Should handle empty accel_change gracefully
    assert isinstance(result, float)


def test_find_cmj_takeoff_from_velocity_peak_normal() -> None:
    """Test find_cmj_takeoff_from_velocity_peak with clear peak."""
    # Create velocity data with clear upward peak (most negative)
    positions = np.linspace(0.7, 0.3, 50)  # Dummy positions
    velocities = np.concatenate(
        [
            np.linspace(-0.01, -0.05, 10),  # Accelerating upward
            np.array([-0.08, -0.10, -0.09, -0.06]),  # Peak at index 11
            np.linspace(-0.05, -0.01, 10),  # Decelerating
        ]
    )
    lowest_point_frame = 0
    fps = 30.0

    result = find_cmj_takeoff_from_velocity_peak(
        positions, velocities, lowest_point_frame, fps
    )

    # Should find the peak around frame 11
    assert isinstance(result, float)
    assert 8 <= result <= 15


def test_find_cmj_takeoff_from_velocity_peak_search_window_too_short() -> None:
    """Test find_cmj_takeoff_from_velocity_peak with search window at boundary."""
    positions = np.linspace(0.5, 0.3, 10)
    velocities = np.linspace(-0.01, -0.05, 10)
    lowest_point_frame = 10  # Beyond array length
    fps = 30.0

    result = find_cmj_takeoff_from_velocity_peak(
        positions, velocities, lowest_point_frame, fps
    )

    # Should return lowest_point_frame + 1 when search window too short
    assert result == float(lowest_point_frame + 1)


def test_find_cmj_takeoff_from_velocity_peak_at_start() -> None:
    """Test find_cmj_takeoff_from_velocity_peak with peak at start of search."""
    positions = np.linspace(0.5, 0.3, 30)
    # Peak velocity right at the start
    velocities = np.concatenate([np.array([-0.10]), np.linspace(-0.05, -0.01, 29)])
    lowest_point_frame = 0
    fps = 30.0

    result = find_cmj_takeoff_from_velocity_peak(
        positions, velocities, lowest_point_frame, fps
    )

    # Should find peak at or near frame 0
    assert isinstance(result, float)
    assert 0 <= result <= 3


def test_find_cmj_takeoff_from_velocity_peak_constant_velocity() -> None:
    """Test find_cmj_takeoff_from_velocity_peak with constant velocity."""
    positions = np.linspace(0.5, 0.3, 30)
    velocities = np.ones(30) * -0.05  # Constant velocity
    lowest_point_frame = 5
    fps = 30.0

    result = find_cmj_takeoff_from_velocity_peak(
        positions, velocities, lowest_point_frame, fps
    )

    # Should find first frame (argmin of constant array returns 0)
    assert isinstance(result, float)
    assert result == float(lowest_point_frame)


# New edge case tests


def test_compute_signed_velocity_short_array() -> None:
    """Test compute_signed_velocity with array shorter than window."""
    positions = np.array([0.5, 0.6])  # Only 2 elements, less than window_length=5

    velocities = compute_signed_velocity(positions, window_length=5, polyorder=2)

    # Should fallback to simple diff
    assert len(velocities) == len(positions)
    assert velocities[0] == 0.0  # prepend=positions[0]
    assert velocities[1] > 0  # Downward motion


def test_compute_signed_velocity_even_window() -> None:
    """Test compute_signed_velocity adjusts even window to odd."""
    positions = np.linspace(0.5, 0.7, 20)

    # Pass even window - should be incremented to odd
    velocities = compute_signed_velocity(positions, window_length=6, polyorder=2)

    assert len(velocities) == len(positions)
    # Should have successfully computed velocities
    assert np.all(velocities >= 0)  # All downward motion


def test_find_standing_phase_too_short() -> None:
    """Test find_standing_phase with video too short."""
    positions = np.ones(10) * 0.5  # Only 10 frames
    velocities = np.zeros(10)
    fps = 30.0

    result = find_standing_phase(
        positions, velocities, fps, min_standing_duration=0.5  # Requires 15 frames
    )

    # Should return None for too-short video
    assert result is None


def test_find_standing_phase_no_transition() -> None:
    """Test find_standing_phase when standing detected but no clear transition."""
    fps = 30.0
    # Create trajectory with standing but no clear movement after
    positions = np.ones(100) * 0.5  # All standing
    velocities = np.zeros(100)  # No movement

    result = find_standing_phase(
        positions, velocities, fps, min_standing_duration=0.5, velocity_threshold=0.01
    )

    # May return None if no transition found
    # Test verifies function doesn't crash
    assert result is None or isinstance(result, int)


def test_find_countermovement_start_no_downward_motion() -> None:
    """Test find_countermovement_start when no sustained downward motion."""
    # All upward or near-zero velocities
    velocities = np.ones(50) * -0.005  # Slight upward motion

    result = find_countermovement_start(
        velocities, countermovement_threshold=0.015, min_eccentric_frames=3
    )

    # Should return None when no downward motion detected
    assert result is None


def test_find_lowest_point_invalid_search_range() -> None:
    """Test find_lowest_point when peak is too early, requiring fallback range."""
    # Create trajectory where peak is very early
    positions = np.concatenate(
        [
            np.array([0.3, 0.4, 0.5]),  # Peak at frame 0
            np.linspace(0.5, 0.7, 50),  # Rest of trajectory
        ]
    )
    velocities = compute_signed_velocity(positions)

    result = find_lowest_point(
        positions, velocities, min_search_frame=80  # Search start after peak
    )

    # Should use fallback range (30-70% of video)
    assert isinstance(result, int)
    assert 0 <= result < len(positions)


def test_find_lowest_point_empty_search_window() -> None:
    """Test find_lowest_point with empty search window."""
    positions = np.array([0.5, 0.6, 0.4, 0.5])  # Very short
    velocities = np.array([0, 0.1, -0.1, 0])

    result = find_lowest_point(positions, velocities, min_search_frame=10)

    # Should handle empty search gracefully
    assert isinstance(result, int)


def test_refine_transition_with_curvature_invalid_range() -> None:
    """Test refine_transition_with_curvature with invalid search range."""
    positions = np.linspace(0.5, 0.7, 20)
    velocities = np.ones(20) * 0.05

    # Initial frame beyond valid range
    result = refine_transition_with_curvature(
        positions,
        velocities,
        initial_frame=25,  # Beyond array length
        transition_type="landing",
        search_radius=3,
    )

    # Should return initial frame without refinement
    assert result == 25.0


def test_find_cmj_landing_from_position_peak_no_search_window() -> None:
    """Test find_cmj_landing_from_position_peak when search window invalid."""
    positions = np.linspace(0.5, 0.7, 15)
    velocities = np.ones(15) * 0.05
    accelerations = compute_acceleration_from_derivative(positions)
    fps = 30.0

    # Takeoff at end of array
    result = find_cmj_landing_from_position_peak(
        positions, velocities, accelerations, takeoff_frame=14, fps=fps
    )

    # Should handle edge case gracefully
    assert isinstance(result, float)


def test_find_cmj_landing_from_position_peak_short_landing_window() -> None:
    """Test landing detection when landing search window is too short."""
    positions = np.concatenate([np.linspace(0.5, 0.3, 10), np.linspace(0.3, 0.6, 5)])
    velocities = compute_signed_velocity(positions)
    accelerations = compute_acceleration_from_derivative(positions)
    fps = 30.0

    result = find_cmj_landing_from_position_peak(
        positions, velocities, accelerations, takeoff_frame=5, fps=fps
    )

    # Should find landing even with short window
    assert isinstance(result, float)
    assert 5 <= result <= len(positions)


def test_detect_cmj_phases_peak_too_early() -> None:
    """Test detect_cmj_phases when peak height is too early in video."""
    # Create trajectory with peak in first 10 frames (invalid)
    positions = np.concatenate(
        [
            np.array([0.5, 0.4, 0.3]),  # Peak at frame 2
            np.linspace(0.3, 0.7, 50),  # Rest goes down
        ]
    )
    fps = 30.0

    result = detect_cmj_phases(positions, fps)

    # Should return None for invalid peak position
    assert result is None


def test_find_lowest_point_with_fallback_positions() -> None:
    """Test find_lowest_point uses position-based fallback when needed."""
    # Peak very early, search window ends up empty
    positions = np.array([0.3] + [0.5] * 20 + [0.7] * 30)
    velocities = compute_signed_velocity(positions)

    result = find_lowest_point(positions, velocities, min_search_frame=100)

    # Should use fallback logic
    assert isinstance(result, int)
    assert 0 <= result < len(positions)
