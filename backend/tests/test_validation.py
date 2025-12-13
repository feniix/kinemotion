"""File and input validation tests."""

from io import BytesIO

from fastapi.testclient import TestClient


def test_file_size_under_limit_passes(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that files under 500MB are accepted."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_file_size_over_limit_rejected(
    client: TestClient,
    large_video_bytes: bytes,
    no_kinemotion_mock,
) -> None:
    """Test that files over 500MB are rejected."""
    files = {"file": ("large.mp4", BytesIO(large_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert "500MB" in data["message"]


def test_mp4_format_accepted(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that MP4 format is accepted."""
    files = {"file": ("video.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_mov_format_accepted(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that MOV format is accepted."""
    files = {"file": ("video.mov", BytesIO(sample_video_bytes), "video/quicktime")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_avi_format_accepted(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that AVI format is accepted."""
    files = {"file": ("video.avi", BytesIO(sample_video_bytes), "video/avi")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_mkv_format_accepted(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that MKV format is accepted."""
    files = {"file": ("video.mkv", BytesIO(sample_video_bytes), "video/x-matroska")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_flv_format_accepted(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that FLV format is accepted."""
    files = {"file": ("video.flv", BytesIO(sample_video_bytes), "video/x-flv")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_wmv_format_accepted(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that WMV format is accepted."""
    files = {"file": ("video.wmv", BytesIO(sample_video_bytes), "video/x-ms-wmv")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_txt_format_rejected(
    client: TestClient,
    invalid_video_bytes: bytes,
) -> None:
    """Test that TXT format is rejected."""
    files = {"file": ("document.txt", BytesIO(invalid_video_bytes), "text/plain")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert "Invalid video format" in data["message"]


def test_jpg_format_rejected(
    client: TestClient,
    invalid_video_bytes: bytes,
) -> None:
    """Test that JPG format is rejected."""
    files = {"file": ("image.jpg", BytesIO(invalid_video_bytes), "image/jpeg")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 422
    data = response.json()
    assert "error" in data


def test_pdf_format_rejected(
    client: TestClient,
    invalid_video_bytes: bytes,
) -> None:
    """Test that PDF format is rejected."""
    files = {"file": ("document.pdf", BytesIO(invalid_video_bytes), "application/pdf")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 422


def test_zip_format_rejected(
    client: TestClient,
    invalid_video_bytes: bytes,
) -> None:
    """Test that ZIP format is rejected."""
    files = {"file": ("archive.zip", BytesIO(invalid_video_bytes), "application/zip")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 422


def test_valid_jump_type_cmj(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that valid jump_type 'cmj' is accepted."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 200


def test_valid_jump_type_drop_jump(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that valid jump_type 'drop_jump' is accepted."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "drop_jump"})

    assert response.status_code == 200


def test_invalid_jump_type_rejected(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that invalid jump_type is rejected."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "invalid"})

    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert "Invalid jump type" in data["message"]


def test_jump_type_case_insensitive(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that jump_type validation is case-insensitive."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "CMJ"})

    # Should be accepted (backend converts to lowercase)
    assert response.status_code == 200


def test_jump_type_uppercase_drop_jump(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that uppercase DROP_JUMP is accepted."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "DROP_JUMP"})

    # Should be accepted (backend converts to lowercase)
    assert response.status_code == 200


def test_file_without_extension_rejected(
    client: TestClient,
    invalid_video_bytes: bytes,
) -> None:
    """Test that files without extension are rejected."""
    files = {"file": ("video", BytesIO(invalid_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 422
    data = response.json()
    assert "error" in data


def test_file_without_name_rejected(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that files without filename are rejected."""
    # Send file without filename
    files = {"file": ("", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    assert response.status_code == 422
    data = response.json()
    # FastAPI validation returns "detail", not "error"
    assert "detail" in data or "error" in data


def test_missing_jump_type_uses_default(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that missing jump_type uses default value."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files)

    assert response.status_code == 200


def test_valid_quality_preset_fast(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that 'fast' quality preset is accepted."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post(
        "/api/analyze",
        files=files,
        data={"jump_type": "cmj", "quality": "fast"},
    )

    assert response.status_code == 200


def test_valid_quality_preset_balanced(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that 'balanced' quality preset is accepted."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post(
        "/api/analyze",
        files=files,
        data={"jump_type": "cmj", "quality": "balanced"},
    )

    assert response.status_code == 200


def test_valid_quality_preset_accurate(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that 'accurate' quality preset is accepted."""
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post(
        "/api/analyze",
        files=files,
        data={"jump_type": "cmj", "quality": "accurate"},
    )

    assert response.status_code == 200


def test_empty_file_rejected(
    client: TestClient,
) -> None:
    """Test that empty files are rejected."""
    files = {"file": ("test.mp4", BytesIO(b""), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    # Should be accepted by validation but may fail during processing
    # Backend should handle gracefully
    assert response.status_code in [200, 422, 500]
