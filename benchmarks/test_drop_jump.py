"""Performance benchmarks for drop jump analysis.

Tests the vectorized implementations of:
- _assign_contact_states
- detect_ground_contact
"""

import numpy as np
import pytest

from kinemotion.drop_jump.analysis import (
    _assign_contact_states,
    detect_ground_contact,
)


@pytest.mark.benchmark
class TestAssignContactStates:
    """Benchmarks for _assign_contact_states."""

    def _generate_test_data(self, n_frames: int) -> tuple[np.ndarray, set[int]]:
        """Generate realistic test data for contact state assignment."""
        # Simulate visibility (some frames low visibility)
        visibilities = 0.5 + 0.5 * np.random.rand(n_frames)

        # Contact frames: middle third of video is on ground
        contact_start = n_frames // 3
        contact_end = 2 * n_frames // 3
        contact_frames = set(range(contact_start, contact_end))

        return visibilities, contact_frames

    def test_small_30_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with 30 frames."""
        visibilities, contact_frames = self._generate_test_data(30)
        result = benchmark(_assign_contact_states, 30, contact_frames, visibilities, 0.3)
        assert len(result) == 30

    def test_medium_90_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with 90 frames."""
        visibilities, contact_frames = self._generate_test_data(90)
        result = benchmark(_assign_contact_states, 90, contact_frames, visibilities, 0.3)
        assert len(result) == 90

    def test_large_300_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with 300 frames."""
        visibilities, contact_frames = self._generate_test_data(300)
        result = benchmark(_assign_contact_states, 300, contact_frames, visibilities, 0.3)
        assert len(result) == 300

    def test_no_visibility(self, benchmark: pytest.fixture) -> None:
        """Benchmark without visibility data (simpler path)."""
        _, contact_frames = self._generate_test_data(90)
        result = benchmark(_assign_contact_states, 90, contact_frames, None, 0.3)
        assert len(result) == 90

    def test_empty_contact_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with no contact frames (edge case)."""
        visibilities, _ = self._generate_test_data(90)
        result = benchmark(_assign_contact_states, 90, set(), visibilities, 0.3)
        assert len(result) == 90


@pytest.mark.benchmark
class TestDetectGroundContact:
    """Benchmarks for detect_ground_contact."""

    def _generate_foot_positions(self, n_frames: int) -> np.ndarray:
        """Generate realistic foot positions for drop jump."""
        # Simulate drop jump: on box → drop → ground contact → jump
        positions = np.ones(n_frames) * 0.7  # Start on box
        drop_frame = n_frames // 4
        landing_frame = n_frames // 2
        takeoff_frame = 3 * n_frames // 4

        # Drop phase
        positions[drop_frame:landing_frame] = np.linspace(0.7, 0.95, landing_frame - drop_frame)
        # Ground contact
        positions[landing_frame:takeoff_frame] = 0.95 + 0.02 * np.random.randn(
            takeoff_frame - landing_frame
        )
        # Flight phase
        positions[takeoff_frame:] = np.linspace(0.95, 0.7, n_frames - takeoff_frame)

        return positions

    def test_small_30_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with 30 frames."""
        foot_positions = self._generate_foot_positions(30)
        result = benchmark(detect_ground_contact, foot_positions)
        assert len(result) == 30

    def test_medium_90_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with 90 frames."""
        foot_positions = self._generate_foot_positions(90)
        result = benchmark(detect_ground_contact, foot_positions)
        assert len(result) == 90

    def test_large_300_frames(self, benchmark: pytest.fixture) -> None:
        """Benchmark with 300 frames."""
        foot_positions = self._generate_foot_positions(300)
        result = benchmark(detect_ground_contact, foot_positions)
        assert len(result) == 300
