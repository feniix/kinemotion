"""Test configuration and fixtures for kinemotion backend."""

import os
from typing import Any
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kinemotion_backend.app.main import create_application


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


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> None:
    """Set up test environment variables."""
    # Enable test mode to bypass referer validation
    os.environ["TESTING"] = "true"
    os.environ["R2_ENDPOINT"] = "https://test.r2.dev"
    os.environ["R2_ACCESS_KEY"] = "test-access-key"
    os.environ["R2_SECRET_KEY"] = "test-secret-key"
    os.environ["R2_BUCKET_NAME"] = "test-bucket"
    os.environ["SUPABASE_URL"] = "https://test.supabase.co"
    os.environ["SUPABASE_ANON_KEY"] = "test-anon-key"
    # Test password for /analyze endpoint authentication bypass
    os.environ["TEST_PASSWORD"] = "test-password-12345"
    os.environ["TEST_EMAIL"] = "test@example.com"

    yield

    # Clean up
    env_vars = [
        "TESTING",
        "R2_ENDPOINT",
        "R2_ACCESS_KEY",
        "R2_SECRET_KEY",
        "R2_BUCKET_NAME",
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "TEST_PASSWORD",
        "TEST_EMAIL",
    ]
    for key in env_vars:
        os.environ.pop(key, None)


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

    # Don't mock storage service when no_kinemotion_mock is requested
    if "no_kinemotion_mock" in request.fixturenames:
        # Only mock kinemotion processing, not storage
        cmj_patch = "kinemotion_backend.services.video_processor.process_cmj_video"
        dj_patch = "kinemotion_backend.services.video_processor.process_dropjump_video"
        with patch(cmj_patch) as mock_cmj, patch(dj_patch) as mock_dropjump:
            mock_cmj.return_value = MockCMJResult()
            mock_dropjump.return_value = MockDropJumpResult()
            # Store mocks in test instance for potential per-test modification
            yield {"cmj": mock_cmj, "dropjump": mock_dropjump}
    else:
        # Mock both kinemotion processing and storage service (normal case)
        cmj_patch = "kinemotion_backend.services.video_processor.process_cmj_video"
        dj_patch = "kinemotion_backend.services.video_processor.process_dropjump_video"
        upload_video_patch = (
            "kinemotion_backend.services.storage_service.StorageService.upload_video"
        )
        upload_results_patch = (
            "kinemotion_backend.services.storage_service.StorageService.upload_analysis_results"
        )
        with (
            patch(cmj_patch) as mock_cmj,
            patch(dj_patch) as mock_dropjump,
            patch(upload_video_patch) as mock_upload_video,
            patch(upload_results_patch) as mock_upload_results,
        ):
            mock_cmj.return_value = MockCMJResult()
            mock_dropjump.return_value = MockDropJumpResult()
            mock_upload_video.return_value = "https://test.r2.dev/videos/test.mp4"
            mock_upload_results.return_value = "https://test.r2.dev/results/test.json"
            # Store mocks for potential per-test modification
            yield {
                "cmj": mock_cmj,
                "dropjump": mock_dropjump,
                "upload_video": mock_upload_video,
                "upload_results": mock_upload_results,
            }


@pytest.fixture(scope="module")
def app() -> FastAPI:
    """FastAPI application fixture (module-scoped to avoid recreating for each test)."""
    return create_application()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Test client for the FastAPI application with test authentication."""
    test_client = TestClient(app)
    # Add test password header to all requests for authentication bypass
    test_client.headers["x-test-password"] = "test-password-12345"
    return test_client


@pytest.fixture
def sample_cmj_metrics() -> dict[str, Any]:
    """Sample CMJ metrics for testing with proper nested structure."""
    return {
        "data": {
            "jump_height_m": 0.45,
            "flight_time_s": 0.60,
            "countermovement_depth_m": 0.35,
            "triple_extension": True,
            "takeoff_angle_deg": 75.0,
            "landing_angle_deg": 65.0,
            "rsi_score": None,
        },
        "metadata": {
            "quality": "balanced",
            "tracking_method": "hip_hybrid",
        },
        "validation": {
            "status": "PASS",
            "issues": [],
        },
    }


@pytest.fixture
def sample_dropjump_metrics() -> dict[str, Any]:
    """Sample drop jump metrics for testing with proper nested structure."""
    return {
        "data": {
            "ground_contact_time_s": 0.25,
            "flight_time_s": 0.50,
            "reactive_strength_index": 2.0,
            "drop_height_m": 0.30,
            "jump_height_m": 0.31,
            "takeoff_angle_deg": 78.0,
            "landing_angle_deg": 62.0,
        },
        "metadata": {
            "quality": "balanced",
            "tracking_method": "hip_hybrid",
        },
        "validation": {
            "status": "PASS",
            "issues": [],
        },
    }


@pytest.fixture
def sample_analysis_session() -> dict[str, Any]:
    """Sample analysis session data for testing."""
    return {
        "jump_type": "cmj",
        "quality_preset": "balanced",
        "analysis_data": {
            "jump_height_m": 0.45,
            "flight_time_s": 0.60,
        },
        "processing_time_s": 2.5,
    }


@pytest.fixture
def sample_video_bytes() -> bytes:
    """Sample video bytes for testing.

    Returns minimal MP4 header bytes that simulate a video file upload.
    """
    # Minimal MP4 header that passes as a valid video file
    return b"\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mp42isom\x00\x00\x00\x00"


@pytest.fixture
def large_video_bytes() -> bytes:
    """Sample large video bytes for testing file size limits."""
    # Return bytes larger than the 500MB upload limit
    return b"x" * (501 * 1024 * 1024)


@pytest.fixture
def invalid_file_bytes() -> bytes:
    """Sample invalid file bytes for testing rejection of non-video files."""
    return b"This is not a video file, just plain text content."


@pytest.fixture
def invalid_video_bytes() -> bytes:
    """Sample invalid video bytes for testing file rejection."""
    return b"This is not a video file, just plain text content."


@pytest.fixture
def no_kinemotion_mock() -> None:
    """Fixture to disable kinemotion analysis mocking for tests."""
    # This fixture can be requested by tests to disable the autouse
    # mock_kinemotion_analysis
    pass
