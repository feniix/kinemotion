"""Comprehensive tests for Drop Jump analysis and phase detection.

This test suite provides comprehensive coverage of Drop Jump phase detection,
similar to test_cmj_analysis.py for CMJ.
"""

import numpy as np

from kinemotion.dropjump.analysis import (
    ContactState,
    calculate_adaptive_threshold,
    detect_drop_start,
    detect_ground_contact,
    find_contact_phases,
    find_interpolated_phase_transitions,
    find_interpolated_phase_transitions_with_curvature,
    refine_transition_with_curvature,
)


class TestDropStartDetection:
    """Test drop start detection from stable baseline."""

    def test_drop_start_with_stable_baseline(self) -> None:
        """Test drop start detection with clear stable period."""
        fps = 30.0
        # Create trajectory: stable on box, then drop
        positions = np.concatenate(
            [
                np.ones(60) * 0.3,  # Stable on box (2 seconds)
                np.linspace(0.3, 0.8, 30),  # Drop
            ]
        )

        drop_frame = detect_drop_start(positions, fps, min_stationary_duration=1.0)

        # Should detect drop after stable period (allow wider tolerance)
        assert 50 <= drop_frame <= 65

    def test_drop_start_with_unstable_beginning(self) -> None:
        """Test drop start when athlete steps onto box at start."""
        fps = 30.0
        # Create trajectory: unstable stepping, stable, then drop
        positions = np.concatenate(
            [
                np.random.uniform(0.25, 0.35, 15),  # Unstable stepping
                np.ones(60) * 0.3,  # Stable on box
                np.linspace(0.3, 0.8, 30),  # Drop
            ]
        )

        drop_frame = detect_drop_start(positions, fps, min_stationary_duration=1.0)

        # Should detect drop after stable period, not during unstable start
        assert drop_frame > 15  # After unstable start
        assert drop_frame < 90  # Before end

    def test_drop_start_no_stable_period(self) -> None:
        """Test drop start when no stable period is found."""
        fps = 30.0
        # Create noisy trajectory without clear stable period
        rng = np.random.default_rng(42)
        positions = rng.uniform(0.3, 0.5, 50)

        drop_frame = detect_drop_start(positions, fps)

        # Should return 0 when no stable period found
        assert drop_frame == 0

    def test_drop_start_too_short_video(self) -> None:
        """Test drop start with video too short for analysis."""
        fps = 30.0
        positions = np.ones(20) * 0.3  # Only 20 frames

        drop_frame = detect_drop_start(positions, fps, min_stationary_duration=1.0, debug=True)

        # Should return 0 for too-short video
        assert drop_frame == 0


class TestGroundContactDetection:
    """Test ground contact detection from foot positions."""

    def test_contact_detection_simple_pattern(self) -> None:
        """Test basic ground contact detection with stationary feet."""
        # Create simple trajectory: on ground, jump, land
        positions = np.array([0.8, 0.8, 0.8, 0.7, 0.6, 0.5, 0.6, 0.7, 0.8, 0.8, 0.8])
        visibilities = np.ones(len(positions))

        states = detect_ground_contact(
            positions,
            velocity_threshold=0.05,
            min_contact_frames=2,
            visibilities=visibilities,
        )

        # First few frames should be on ground
        assert states[0] == ContactState.ON_GROUND
        assert states[1] == ContactState.ON_GROUND

        # Middle frames (during jump) should be in air
        assert ContactState.IN_AIR in states[3:8]

        # Last few frames should be on ground again
        assert states[-1] == ContactState.ON_GROUND

    def test_contact_detection_with_low_visibility(self) -> None:
        """Test that low visibility landmarks are ignored."""
        positions = np.array([0.8, 0.8, 0.8, 0.8, 0.8])
        # Middle frame low visibility
        visibilities = np.array([0.9, 0.9, 0.1, 0.9, 0.9])

        states = detect_ground_contact(
            positions,
            velocity_threshold=0.05,
            min_contact_frames=1,
            visibility_threshold=0.5,
            visibilities=visibilities,
        )

        # Middle frame should be unknown due to low visibility
        assert states[2] == ContactState.UNKNOWN

    def test_contact_detection_min_contact_frames(self) -> None:
        """Test minimum contact frames requirement."""
        # Create pattern with brief contact
        positions = np.array([0.8, 0.8, 0.7, 0.8, 0.8])
        visibilities = np.ones(len(positions))

        states = detect_ground_contact(
            positions,
            velocity_threshold=0.05,
            min_contact_frames=3,  # Require 3 consecutive frames
            visibilities=visibilities,
        )

        # Brief movement shouldn't register as flight with
        # min_contact_frames=3. Most frames should be on ground or in air
        # based on sustained motion
        assert len(states) == len(positions)


class TestContactPhaseIdentification:
    """Test phase identification from contact states."""

    def test_find_contact_phases_simple(self) -> None:
        """Test phase identification from contact states."""
        states = [
            ContactState.ON_GROUND,
            ContactState.ON_GROUND,
            ContactState.IN_AIR,
            ContactState.IN_AIR,
            ContactState.IN_AIR,
            ContactState.ON_GROUND,
            ContactState.ON_GROUND,
        ]

        phases = find_contact_phases(states)

        assert len(phases) == 3
        assert phases[0] == (0, 1, ContactState.ON_GROUND)
        assert phases[1] == (2, 4, ContactState.IN_AIR)
        assert phases[2] == (5, 6, ContactState.ON_GROUND)

    def test_find_contact_phases_with_unknown(self) -> None:
        """Test phase identification with unknown states."""
        states = [
            ContactState.ON_GROUND,
            ContactState.UNKNOWN,
            ContactState.IN_AIR,
            ContactState.IN_AIR,
            ContactState.ON_GROUND,
        ]

        phases = find_contact_phases(states)

        # Should have phases, possibly merging around unknown
        assert len(phases) >= 2


class TestInterpolatedPhaseTransitions:
    """Test sub-frame interpolation for phase transitions."""

    def test_interpolated_transitions_basic(self) -> None:
        """Test sub-frame interpolation of phase transitions."""
        # Create clear transitions
        positions = np.concatenate(
            [
                np.ones(10) * 0.8,  # On ground
                np.linspace(0.8, 0.5, 10),  # Falling
                np.linspace(0.5, 0.8, 10),  # Rising
                np.ones(10) * 0.8,  # On ground
            ]
        )

        contact_states = detect_ground_contact(
            positions, velocity_threshold=0.02, min_contact_frames=3
        )

        interpolated = find_interpolated_phase_transitions(
            positions, contact_states, velocity_threshold=0.02, smoothing_window=5
        )

        # Should have detected phases with fractional frame indices
        assert len(interpolated) > 0
        for start, end, _ in interpolated:
            assert isinstance(start, float)
            assert isinstance(end, float)
            assert start < end


class TestCurvatureRefinement:
    """Test curvature-based refinement of phase transitions."""

    def test_curvature_refinement_landing(self) -> None:
        """Test curvature refinement for landing detection."""
        # Create position data with clear impact spike
        positions = np.concatenate(
            [
                np.linspace(0.3, 0.5, 20),  # Falling
                np.array([0.5, 0.52, 0.54, 0.55, 0.55]),  # Impact
                np.ones(10) * 0.55,  # Stable
            ]
        )
        estimated_frame = 20.0  # Around impact

        refined = refine_transition_with_curvature(
            positions,
            estimated_frame,
            transition_type="landing",
            search_window=5,
        )

        # Should refine near the impact point
        assert isinstance(refined, float)
        assert 15 <= refined <= 25

    def test_curvature_refinement_takeoff(self) -> None:
        """Test curvature refinement for takeoff detection."""
        # Create position data with acceleration change at takeoff
        positions = np.concatenate(
            [
                np.ones(15) * 0.5,  # Static
                np.array([0.5, 0.48, 0.45, 0.40, 0.35]),  # Accelerating upward
                np.linspace(0.35, 0.2, 10),  # Flight
            ]
        )
        estimated_frame = 15.0  # Around takeoff

        refined = refine_transition_with_curvature(
            positions,
            estimated_frame,
            transition_type="takeoff",
            search_window=5,
        )

        # Should refine near the takeoff point
        assert isinstance(refined, float)
        assert 12 <= refined <= 20


class TestInterpolatedPhasesWithCurvature:
    """Test combined interpolation and curvature refinement."""

    def test_phases_with_curvature_enabled(self) -> None:
        """Test phase detection with curvature refinement enabled."""
        # Create realistic drop jump trajectory
        positions = np.concatenate(
            [
                np.ones(20) * 0.3,  # On box
                np.linspace(0.3, 0.7, 15),  # Drop
                np.ones(10) * 0.7,  # Contact
                np.linspace(0.7, 0.4, 15),  # Jump
                np.linspace(0.4, 0.7, 15),  # Landing
                np.ones(10) * 0.7,  # Stable
            ]
        )

        contact_states = detect_ground_contact(
            positions, velocity_threshold=0.02, min_contact_frames=3
        )

        refined_phases = find_interpolated_phase_transitions_with_curvature(
            positions,
            contact_states,
            velocity_threshold=0.02,
            smoothing_window=5,
            use_curvature=True,
        )

        # Should have detected phases with refinement
        assert len(refined_phases) > 0
        for start, end, _ in refined_phases:
            assert isinstance(start, float)
            assert isinstance(end, float)
            assert start < end

    def test_phases_without_curvature(self) -> None:
        """Test phase detection with curvature refinement disabled."""
        positions = np.concatenate(
            [
                np.ones(20) * 0.7,  # On ground
                np.linspace(0.7, 0.4, 15),  # Jump
                np.linspace(0.4, 0.7, 15),  # Landing
                np.ones(10) * 0.7,  # Stable
            ]
        )

        contact_states = detect_ground_contact(
            positions, velocity_threshold=0.02, min_contact_frames=3
        )

        phases_no_curvature = find_interpolated_phase_transitions_with_curvature(
            positions,
            contact_states,
            velocity_threshold=0.02,
            smoothing_window=5,
            use_curvature=False,
        )

        # Should still detect phases without curvature
        assert len(phases_no_curvature) > 0


class TestAdaptiveThreshold:
    """Test adaptive velocity threshold calculation."""

    def test_adaptive_threshold_with_low_noise(self) -> None:
        """Test adaptive threshold with low-noise baseline."""
        fps = 30.0
        baseline_frames = int(3 * fps)

        # Low noise baseline
        rng = np.random.default_rng(42)
        baseline_positions = 0.5 + rng.normal(0, 0.005, baseline_frames)
        movement_positions = np.linspace(0.5, 0.7, 60)
        positions = np.concatenate([baseline_positions, movement_positions])

        threshold = calculate_adaptive_threshold(positions, fps)

        # Should have minimum threshold with low noise
        assert 0.005 <= threshold <= 0.02

    def test_adaptive_threshold_with_high_noise(self) -> None:
        """Test adaptive threshold adapts to high-noise baseline."""
        fps = 30.0
        baseline_frames = int(3 * fps)

        # High noise baseline
        rng = np.random.default_rng(42)
        baseline_positions = 0.5 + rng.normal(0, 0.015, baseline_frames)
        movement_positions = np.linspace(0.5, 0.8, 60)
        positions = np.concatenate([baseline_positions, movement_positions])

        threshold = calculate_adaptive_threshold(positions, fps)

        # With higher noise, threshold should be proportionally higher
        assert 0.010 <= threshold <= 0.05


class TestPhaseOrdering:
    """Test that phases are detected in correct temporal order."""

    def test_phase_ordering_valid_drop_jump(self) -> None:
        """Test phase ordering for valid drop jump."""
        # Create realistic drop jump: box → drop → contact → flight → landing
        positions = np.concatenate(
            [
                np.ones(30) * 0.3,  # On box
                np.linspace(0.3, 0.7, 20),  # Drop
                np.ones(15) * 0.7,  # Ground contact
                np.linspace(0.7, 0.4, 20),  # Flight (jump up)
                np.linspace(0.4, 0.7, 20),  # Landing
                np.ones(10) * 0.7,  # Stable
            ]
        )

        contact_states = detect_ground_contact(
            positions, velocity_threshold=0.02, min_contact_frames=3
        )

        phases = find_contact_phases(contact_states)

        # Verify phases are in correct order
        assert len(phases) > 0

        # Check temporal ordering
        for i in range(len(phases) - 1):
            _, end_i, _ = phases[i]
            start_next, _, _ = phases[i + 1]
            assert end_i < start_next, "Phases should not overlap"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_short_video(self) -> None:
        """Test handling of very short video."""
        positions = np.array([0.5, 0.6, 0.7])
        visibilities = np.ones(len(positions))

        states = detect_ground_contact(
            positions,
            velocity_threshold=0.02,
            min_contact_frames=2,
            visibilities=visibilities,
        )

        # Should handle gracefully
        assert len(states) == len(positions)

    def test_constant_position(self) -> None:
        """Test handling of constant position (no movement)."""
        positions = np.ones(50) * 0.5
        visibilities = np.ones(len(positions))

        states = detect_ground_contact(
            positions,
            velocity_threshold=0.02,
            min_contact_frames=3,
            visibilities=visibilities,
        )

        # All frames should be on ground (stationary)
        assert all(s == ContactState.ON_GROUND for s in states)

    def test_all_low_visibility(self) -> None:
        """Test handling when all landmarks have low visibility."""
        positions = np.linspace(0.5, 0.7, 30)
        visibilities = np.ones(len(positions)) * 0.2  # All low visibility

        states = detect_ground_contact(
            positions,
            velocity_threshold=0.02,
            min_contact_frames=3,
            visibility_threshold=0.5,
            visibilities=visibilities,
        )

        # Most or all frames should be unknown
        unknown_count = sum(1 for s in states if s == ContactState.UNKNOWN)
        assert unknown_count > len(states) * 0.5


class TestRealisticDropJumpScenarios:
    """Test realistic drop jump scenarios with different athlete profiles."""

    def test_recreational_athlete_drop_jump(self) -> None:
        """Test drop jump detection for recreational athlete.

        Characteristics:
        - Moderate contact time (~400ms)
        - Moderate flight time (~650ms)
        - Moderate jump height (~50cm)
        """
        positions = np.concatenate(
            [
                np.ones(30) * 0.3,  # On box (1s)
                np.linspace(0.3, 0.7, 15),  # Drop (0.5s)
                np.ones(12) * 0.7,  # Contact (0.4s)
                np.linspace(0.7, 0.45, 20),  # Flight up (0.65s)
                np.linspace(0.45, 0.7, 15),  # Landing (0.5s)
                np.ones(10) * 0.7,  # Stable
            ]
        )

        contact_states = detect_ground_contact(
            positions, velocity_threshold=0.02, min_contact_frames=3
        )

        phases = find_contact_phases(contact_states)

        # Should detect multiple phases
        assert len(phases) >= 2

    def test_elite_athlete_drop_jump(self) -> None:
        """Test drop jump detection for elite athlete.

        Characteristics:
        - Short contact time (~250ms)
        - Long flight time (~850ms)
        - High jump height (~80cm)
        """
        positions = np.concatenate(
            [
                np.ones(30) * 0.3,  # On box
                np.linspace(0.3, 0.7, 12),  # Drop
                np.ones(8) * 0.7,  # Contact (0.25s - fast)
                np.linspace(0.7, 0.35, 26),  # Flight up (0.85s - long)
                np.linspace(0.35, 0.7, 15),  # Landing
                np.ones(10) * 0.7,  # Stable
            ]
        )

        contact_states = detect_ground_contact(
            positions, velocity_threshold=0.02, min_contact_frames=3
        )

        phases = find_contact_phases(contact_states)

        # Should detect phases despite fast contact
        assert len(phases) >= 2


class TestRobustness:
    """Test robustness to noise and measurement errors."""

    def test_noisy_trajectory(self) -> None:
        """Test handling of noisy position data."""
        rng = np.random.default_rng(42)

        # Create trajectory with noise
        clean_positions = np.concatenate(
            [
                np.ones(30) * 0.7,  # On ground
                np.linspace(0.7, 0.4, 20),  # Jump
                np.linspace(0.4, 0.7, 20),  # Landing
                np.ones(10) * 0.7,  # Stable
            ]
        )
        noisy_positions = clean_positions + rng.normal(0, 0.01, len(clean_positions))

        contact_states = detect_ground_contact(
            noisy_positions, velocity_threshold=0.03, min_contact_frames=3
        )

        phases = find_contact_phases(contact_states)

        # Should still detect phases despite noise
        assert len(phases) > 0

    def test_missing_frames(self) -> None:
        """Test handling of missing frames (low visibility)."""
        positions = np.concatenate(
            [
                np.ones(20) * 0.7,  # On ground
                np.linspace(0.7, 0.4, 15),  # Jump
                np.linspace(0.4, 0.7, 15),  # Landing
                np.ones(10) * 0.7,  # Stable
            ]
        )

        # Simulate missing frames with low visibility
        visibilities = np.ones(len(positions))
        visibilities[25:30] = 0.1  # Missing frames during jump

        contact_states = detect_ground_contact(
            positions,
            velocity_threshold=0.02,
            min_contact_frames=3,
            visibilities=visibilities,
        )

        # Should handle missing frames gracefully
        assert len(contact_states) == len(positions)
        # Missing frames should be marked as unknown
        assert contact_states[25] == ContactState.UNKNOWN
