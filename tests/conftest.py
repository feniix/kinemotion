"""Shared pytest fixtures for all test modules.

This module contains fixtures that are used across multiple test files,
reducing duplication and improving maintainability.
"""

from pathlib import Path

import cv2
import numpy as np
import pytest
from click.testing import CliRunner


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
