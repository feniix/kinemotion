"""Shared pytest fixtures for all test modules.

This module contains fixtures that are used across multiple test files,
reducing duplication and improving maintainability.
"""

from pathlib import Path

import cv2
import numpy as np
import pytest
from click.testing import CliRunner

from kinemotion.core.types import FloatArray


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide Click test runner with stderr separation.

    Used by CLI tests to invoke commands and capture output separately
    from stderr for better test assertions.
    """
    return CliRunner(mix_stderr=False)


@pytest.fixture(scope="session")
def minimal_video(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create minimal test video for CLI testing.

    Generates a 1-second video (30 frames at 30fps) with black frames.
    Suitable for testing CLI argument parsing and basic video handling.
    Created once per session to improve test speed.

    Args:
        tmp_path_factory: Pytest's session-scoped temporary directory fixture

    Returns:
        Path to the generated test video file
    """
    video_dir = tmp_path_factory.mktemp("video_data")
    video_path = video_dir / "test.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))

    # Create 30 frames (1 second)
    for _ in range(30):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        out.write(frame)

    out.release()
    return video_path


@pytest.fixture(scope="session")
def sample_video_path(tmp_path_factory: pytest.TempPathFactory) -> str:
    """Create a minimal synthetic video for API testing.

    Generates a 1-second video with a moving white circle pattern.
    The motion pattern allows for basic pose detection attempts,
    though detection may not succeed with synthetic data.
    Created once per session to improve test speed.

    Args:
        tmp_path_factory: Pytest's session-scoped temporary directory fixture

    Returns:
        String path to the generated test video file
    """
    video_dir = tmp_path_factory.mktemp("api_video_data")
    video_path = video_dir / "test_video.mp4"

    # Create a simple test video (30 frames at 30fps = 1 second)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))

    # Generate frames with a simple moving pattern
    for i in range(30):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some pattern to make pose detection possible (though it will likely fail)
        cv2.circle(frame, (320, 240 + i * 5), 50, (255, 255, 255), -1)
        out.write(frame)

    out.release()

    return str(video_path)


# Squat Jump test fixtures
@pytest.fixture
def sj_sample_positions() -> FloatArray:
    """Create sample SJ trajectory data.

    Returns positions showing:
    - Frames 0-30: Static squat hold (position = 0.6)
    - Frames 30-60: Concentric phase (rising to 0.4)
    - Frames 60-90: Flight phase (falling to 0.2)
    - Frames 90-100: Landing phase (back to 0.6)
    """
    import numpy as np

    return np.concatenate(
        [
            np.ones(30) * 0.6,  # Squat hold
            np.linspace(0.6, 0.4, 30),  # Concentric (rising)
            np.linspace(0.4, 0.2, 30),  # Flight (falling)
            np.linspace(0.2, 0.6, 10),  # Landing
        ]
    )


@pytest.fixture
def sj_sample_velocities() -> FloatArray:
    """Create sample SJ velocity data corresponding to positions."""
    import numpy as np

    positions = sj_sample_positions()
    # Simple derivative approximation
    velocities = np.zeros_like(positions)
    velocities[1:] = np.diff(positions)
    return velocities


@pytest.fixture
def sj_phase_frames() -> dict[str, float]:
    """Expected phase frame numbers for sample data."""
    return {
        "squat_hold_start": 0.0,
        "concentric_start": 30.0,
        "takeoff_frame": 60.0,
        "landing_frame": 90.0,
    }


@pytest.fixture
def test_mass_values() -> list[float | None]:
    """Test mass values for power/force calculations."""
    return [60.0, 75.0, 80.0, 100.0, None]
