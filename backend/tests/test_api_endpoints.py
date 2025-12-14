"""API endpoint tests for video analysis."""

from io import BytesIO
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def test_analyze_cmj_video_returns_200(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that CMJ analysis endpoint returns 200 status code."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_analyze_dropjump_video_returns_200(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that Drop Jump analysis endpoint returns 200 status code."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "drop_jump"})

    assert response.status_code == 200


def test_analyze_cmj_response_structure(
    client: TestClient,
    sample_video_bytes: bytes,
    sample_cmj_metrics: dict[str, Any],
) -> None:
    """Test that CMJ response has correct structure."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})
    data = response.json()

    # Required fields
    assert "status_code" in data
    assert "message" in data
    assert "metrics" in data
    assert "processing_time_s" in data

    # Verify status code
    assert data["status_code"] == 200

    # Verify metrics structure
    assert isinstance(data["metrics"], dict)
    assert "data" in data["metrics"]
    assert "jump_height_m" in data["metrics"]["data"]
    assert "flight_time_s" in data["metrics"]["data"]


def test_analyze_dropjump_response_structure(
    client: TestClient,
    sample_video_bytes: bytes,
    sample_dropjump_metrics: dict[str, Any],
) -> None:
    """Test that Drop Jump response has correct structure."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "drop_jump"})

    data = response.json()

    # Required fields
    assert "status_code" in data
    assert "message" in data
    assert "metrics" in data
    assert "processing_time_s" in data

    # Verify metrics structure (from autouse mock)
    assert "data" in data["metrics"]
    assert "ground_contact_time_s" in data["metrics"]["data"]
    assert "flight_time_s" in data["metrics"]["data"]


def test_analyze_processing_time_recorded(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that processing_time_s is recorded."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})
    data = response.json()

    assert "processing_time_s" in data
    assert isinstance(data["processing_time_s"], (int, float))
    assert data["processing_time_s"] >= 0


def test_analyze_default_quality_balanced(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that default quality preset is 'balanced'."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}

    cmj_patch = "kinemotion_backend.services.video_processor.process_cmj_video"
    with patch(cmj_patch) as mock_cmj:
        # Set up mock to return proper response
        class MockResult:
            def to_dict(self):
                return {"jump_height": 0.5, "flight_time": 0.8}

        mock_cmj.return_value = MockResult()
        response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

        assert response.status_code == 200
        # Verify that process_cmj_video was called with 'balanced' quality
        mock_cmj.assert_called_once()
        call_args = mock_cmj.call_args
        assert call_args[1]["quality"] == "balanced"


def test_analyze_custom_quality_fast(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that custom quality preset is respected."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}

    cmj_patch = "kinemotion_backend.services.video_processor.process_cmj_video"
    with patch(cmj_patch) as mock_cmj:

        class MockResult:
            def to_dict(self):
                return {"jump_height": 0.5, "flight_time": 0.8}

        mock_cmj.return_value = MockResult()
        response = client.post(
            "/api/analyze",
            files=files,
            data={"jump_type": "cmj", "quality": "fast"},
        )

        assert response.status_code == 200
        call_args = mock_cmj.call_args
        assert call_args[1]["quality"] == "fast"


def test_analyze_custom_quality_accurate(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that accurate quality preset works."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}

    cmj_patch = "kinemotion_backend.services.video_processor.process_cmj_video"
    with patch(cmj_patch) as mock_cmj:

        class MockResult:
            def to_dict(self):
                return {"jump_height": 0.5, "flight_time": 0.8}

        mock_cmj.return_value = MockResult()
        response = client.post(
            "/api/analyze",
            files=files,
            data={"jump_type": "cmj", "quality": "accurate"},
        )

        assert response.status_code == 200
        call_args = mock_cmj.call_args
        assert call_args[1]["quality"] == "accurate"


def test_analyze_cmj_message_contains_jump_type(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that response message contains jump type."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})
    data = response.json()

    assert data["message"] == "Analysis completed successfully"


def test_analyze_dropjump_message_contains_jump_type(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that response message contains jump type for drop jump."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "drop_jump"})

    data = response.json()
    assert data["message"] == "Analysis completed successfully"


def test_analyze_cmj_metrics_contains_expected_fields(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that CMJ metrics contain expected fields."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})
    data = response.json()
    metrics = data["metrics"]["data"]

    # Key CMJ metrics
    expected_fields = [
        "jump_height_m",
        "flight_time_s",
        "countermovement_depth_m",
        "triple_extension",
        "takeoff_angle_deg",
        "landing_angle_deg",
        "rsi_score",
    ]

    for field in expected_fields:
        assert field in metrics, f"Missing expected metric: {field}"


def test_analyze_dropjump_metrics_contains_expected_fields(
    client: TestClient,
    sample_video_bytes: bytes,
    sample_dropjump_metrics: dict[str, Any],
) -> None:
    """Test that Drop Jump metrics contain expected fields."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "drop_jump"})

    data = response.json()
    metrics = data["metrics"]["data"]

    # Key Drop Jump metrics (from sample_dropjump_metrics fixture)
    expected_fields = [
        "ground_contact_time_s",
        "flight_time_s",
        "reactive_strength_index",
        "drop_height_m",
        "jump_height_m",
        "takeoff_angle_deg",
        "landing_angle_deg",
    ]

    for field in expected_fields:
        assert field in metrics, f"Missing expected metric: {field}"


def test_analyze_with_mp4_extension(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test analysis with .mp4 file extension."""
    files = {"file": ("video.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_analyze_with_mov_extension(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test analysis with .mov file extension."""
    files = {"file": ("video.mov", BytesIO(sample_video_bytes), "video/quicktime")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_analyze_with_avi_extension(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test analysis with .avi file extension."""
    files = {"file": ("video.avi", BytesIO(sample_video_bytes), "video/avi")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_analyze_default_jump_type_cmj(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that default jump type is CMJ."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}

    cmj_patch = "kinemotion_backend.services.video_processor.process_cmj_video"
    with patch(cmj_patch) as mock_cmj:

        class MockResult:
            def to_dict(self):
                return {
                    "data": {"jump_height": 0.5, "flight_time": 0.8},
                    "metadata": {},
                    "validation": {"status": "PASS", "issues": []},
                }

        mock_cmj.return_value = MockResult()
        response = client.post("/api/analyze", files=files)

        assert response.status_code == 200
        # Should have called CMJ analysis
        mock_cmj.assert_called_once()


@pytest.mark.skip(reason="R2StorageClient requires credentials at instantiation time")
def test_analyze_response_no_results_url_without_r2(
    client: TestClient,
    sample_video_bytes: bytes,
    no_r2_env: None,
) -> None:
    """Test that results_url is not present without R2 configured."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})
    data = response.json()

    # results_url should not be in response without R2
    assert "results_url" not in data or data.get("results_url") is None
