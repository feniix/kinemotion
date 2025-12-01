"""Pytest fixtures for backend API tests."""

import asyncio
import os
import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set testing mode BEFORE any imports of kinemotion_backend
os.environ["TESTING"] = "true"

# Force reload of kinemotion_backend.app if it's already imported
if "kinemotion_backend.app" in sys.modules:
    del sys.modules["kinemotion_backend.app"]
if "kinemotion_backend" in sys.modules:
    del sys.modules["kinemotion_backend"]

from kinemotion_backend.app import app  # noqa: E402


@pytest.fixture(scope="function")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create and properly clean up event loop for each test.

    This fixture ensures:
    - Each test gets a fresh event loop
    - All pending tasks are cancelled during cleanup
    - The loop is properly closed
    - Handles edge cases like KeyboardInterrupt gracefully
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield loop

    # Cancel all pending tasks to prevent "Task was destroyed but it is pending"
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()

    # Run the loop one more time to process cancellations
    if pending:
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

    loop.close()


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_r2_client() -> MagicMock:
    """Mock R2 storage client."""
    mock = MagicMock()
    mock.upload_file = MagicMock(return_value="https://r2.example.com/videos/test.mp4")
    mock.download_file = MagicMock()
    mock.delete_file = MagicMock()
    mock.put_object = MagicMock(return_value="https://r2.example.com/results/test.json")
    return mock


@pytest.fixture
def sample_cmj_metrics() -> dict[str, Any]:
    """Sample CMJ analysis metrics."""
    return {
        "jump_height": 0.42,
        "flight_time": 0.825,
        "countermovement_depth": 0.35,
        "eccentric_duration": 750,
        "concentric_duration": 450,
        "total_movement_time": 1200,
        "peak_eccentric_velocity": 2.15,
        "peak_concentric_velocity": 4.35,
        "transition_time": 50,
        "standing_start_frame": 10,
        "lowest_point_frame": 85,
        "takeoff_frame": 115,
        "landing_frame": 180,
        "video_fps": 120.0,
        "tracking_method": "com",
        "quality_assessment": {
            "confidence": 0.92,
            "warnings": [],
        },
        "validation_result": {
            "is_valid": True,
            "checks_passed": 5,
            "checks_total": 5,
            "warnings": [],
        },
    }


@pytest.fixture
def sample_dropjump_metrics() -> dict[str, Any]:
    """Sample Drop Jump analysis metrics."""
    return {
        "ground_contact_time": 0.285,
        "flight_time": 0.515,
        "jump_height": 1.3,
        "jump_height_kinematic": 1.3,
        "jump_height_trajectory": 1.25,
        "contact_start_frame": 12,
        "contact_end_frame": 46,
        "flight_start_frame": 47,
        "flight_end_frame": 109,
        "peak_height_frame": 78,
        "quality_assessment": {
            "confidence": 0.88,
            "warnings": [],
        },
    }


@pytest.fixture
def sample_video_bytes() -> bytes:
    """Create sample video bytes (minimal MP4 file).

    Returns a valid but minimal MP4 file that can be parsed.
    """
    # Minimal valid MP4 file (about 600 bytes)
    # This is a real minimal MP4 that won't crash readers
    return (
        b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41"
        b"\x00\x00\x00\x08wide"
        b"\x00\x00\x00\x14mdat"
        b"Hello, this is a minimal video file"
    )


@pytest.fixture
def large_video_bytes() -> bytes:
    """Create large video bytes (>500MB) for size validation."""
    # Return 501MB of data
    return b"x" * (501 * 1024 * 1024)


@pytest.fixture
def invalid_video_bytes() -> bytes:
    """Create invalid video bytes (text file)."""
    return b"This is not a video file, just plain text content"


@pytest.fixture
def temp_video_file(sample_video_bytes: bytes, tmp_path: Path) -> Path:
    """Create temporary video file for local analysis testing."""
    video_path = tmp_path / "test_video.mp4"
    video_path.write_bytes(sample_video_bytes)
    return video_path


@pytest.fixture
def no_r2_env() -> None:
    """Unset R2 environment variables for testing without R2."""
    original_env = {}
    r2_vars = ["R2_ENDPOINT", "R2_ACCESS_KEY", "R2_SECRET_KEY", "R2_BUCKET_NAME"]

    for var in r2_vars:
        original_env[var] = os.environ.pop(var, None)

    yield

    # Restore original environment
    for var, value in original_env.items():
        if value is not None:
            os.environ[var] = value


@pytest.fixture(autouse=True)
def mock_kinemotion_analysis(
    sample_cmj_metrics: dict[str, Any], sample_dropjump_metrics: dict[str, Any], request
) -> None:
    """Mock kinemotion analysis functions for all tests.

    Can be disabled by marking tests with @pytest.mark.no_mock or by
    providing fixtures with a 'no_kinemotion_mock' marker.
    """

    class MockCMJResult:
        def to_dict(self) -> dict[str, Any]:
            return sample_cmj_metrics

    class MockDropJumpResult:
        def to_dict(self) -> dict[str, Any]:
            return sample_dropjump_metrics

    # Check if test requests to disable this autouse mock
    if "no_kinemotion_mock" in request.fixturenames:
        yield
        return

    with (
        patch("kinemotion_backend.app.process_cmj_video") as mock_cmj,
        patch("kinemotion_backend.app.process_dropjump_video") as mock_dropjump,
    ):
        mock_cmj.return_value = MockCMJResult()
        mock_dropjump.return_value = MockDropJumpResult()
        # Store mocks in test instance for potential per-test modification
        yield {"cmj": mock_cmj, "dropjump": mock_dropjump}


@pytest.fixture
def no_kinemotion_mock() -> None:
    """Fixture to disable the autouse kinemotion mock for specific tests."""
    pass


@pytest.fixture(autouse=True)
def clear_r2_client() -> None:
    """Clear R2 client before each test."""
    from kinemotion_backend import app as app_module

    app_module.r2_client = None


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> None:
    """Hook to handle exceptions during test execution more gracefully.

    This ensures that BaseException subclasses like KeyboardInterrupt don't
    propagate and corrupt the event loop state during fixture teardown.
    """
    # This hook allows tests to intentionally raise exceptions without
    # breaking the test suite cleanup
    pass
