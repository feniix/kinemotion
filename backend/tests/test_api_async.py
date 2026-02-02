"""Async endpoint tests using httpx AsyncClient.

These tests demonstrate proper async testing of FastAPI endpoints
using httpx AsyncClient instead of the synchronous TestClient.
"""

from io import BytesIO

import pytest

pytestmark = pytest.mark.asyncio


async def test_analyze_cmj_async(async_client, sample_video_bytes):
    """Test CMJ analysis endpoint using async client.

    Args:
        async_client: httpx AsyncClient fixture
        sample_video_bytes: Sample video data fixture
    """
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = await async_client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200
    data = response.json()
    assert "status_code" in data
    assert data["status_code"] == 200


async def test_health_check_async(async_client):
    """Test health check endpoint using async client.

    Args:
        async_client: httpx AsyncClient fixture
    """
    response = await async_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ("healthy", "ok")


async def test_platform_info_async(async_client):
    """Test platform info endpoint using async client.

    Args:
        async_client: httpx AsyncClient fixture
    """
    response = await async_client.get("/api/platform")

    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


async def test_analyze_dropjump_async(async_client, sample_video_bytes):
    """Test drop jump analysis using async client.

    Args:
        async_client: httpx AsyncClient fixture
        sample_video_bytes: Sample video data fixture
    """
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = await async_client.post(
        "/api/analyze", files=files, data={"jump_type": "drop_jump"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "data" in data["metrics"]


async def test_analyze_invalid_jump_type_async(async_client, sample_video_bytes):
    """Test validation of invalid jump type using async client.

    Args:
        async_client: httpx AsyncClient fixture
        sample_video_bytes: Sample video data fixture
    """
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = await async_client.post(
        "/api/analyze", files=files, data={"jump_type": "invalid_jump"}
    )

    # Should return validation error or handle gracefully
    assert response.status_code in (400, 422, 500)
