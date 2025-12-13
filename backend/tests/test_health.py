"""Health check endpoint tests."""

from datetime import datetime

from fastapi.testclient import TestClient


def test_health_check_returns_200(client: TestClient) -> None:
    """Test that /health endpoint returns 200 status code."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_structure(client: TestClient) -> None:
    """Test that /health response has correct structure."""
    response = client.get("/health")
    data = response.json()

    # Required fields
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "timestamp" in data
    assert "r2_configured" in data


def test_health_check_status_ok(client: TestClient) -> None:
    """Test that health status is 'healthy'."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "healthy"


def test_health_check_service_name(client: TestClient) -> None:
    """Test that service name is correct."""
    response = client.get("/health")
    data = response.json()
    assert data["service"] == "kinemotion-backend"


def test_health_check_version_present(client: TestClient) -> None:
    """Test that version is present."""
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0


def test_health_check_timestamp_is_iso_format(client: TestClient) -> None:
    """Test that timestamp is in ISO format."""
    response = client.get("/health")
    data = response.json()
    timestamp_str = data["timestamp"]

    # Should not raise ValueError if valid ISO format
    datetime.fromisoformat(timestamp_str)


def test_health_check_r2_configured_boolean(client: TestClient) -> None:
    """Test that r2_configured is a boolean."""
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["r2_configured"], bool)


def test_health_check_multiple_calls(client: TestClient) -> None:
    """Test that health endpoint can be called multiple times."""
    for _ in range(3):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
