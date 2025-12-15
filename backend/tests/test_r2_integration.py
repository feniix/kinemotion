"""R2 storage integration tests (mocked)."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from kinemotion_backend.models import R2StorageClient


def test_r2_client_initialization_with_credentials() -> None:
    """Test R2 client initialization with valid credentials."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
            "R2_BUCKET_NAME": "kinemotion",
        },
    ):
        client = R2StorageClient()

        assert client.endpoint == "https://r2.example.com"
        assert client.access_key == "test_key"
        assert client.secret_key == "test_secret"
        assert client.bucket_name == "kinemotion"
        assert client.public_base_url == ""
        assert client.presign_expiration_s == 604800  # 7 days default


def test_r2_client_initialization_with_public_url() -> None:
    """Test R2 client initialization with public base URL."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
            "R2_PUBLIC_BASE_URL": "https://kinemotion-public.example.com",
        },
    ):
        client = R2StorageClient()

        assert client.public_base_url == "https://kinemotion-public.example.com"


def test_r2_client_initialization_strips_trailing_slash_from_public_url() -> None:
    """Test that trailing slash is stripped from public base URL."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
            "R2_PUBLIC_BASE_URL": "https://kinemotion-public.example.com/",
        },
    ):
        client = R2StorageClient()

        assert client.public_base_url == "https://kinemotion-public.example.com"


def test_r2_client_initialization_custom_presign_expiration() -> None:
    """Test R2 client initialization with custom presigned expiration."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
            "R2_PRESIGN_EXPIRATION_S": "86400",  # 1 day
        },
    ):
        client = R2StorageClient()

        assert client.presign_expiration_s == 86400


def test_r2_client_initialization_invalid_presign_expiration() -> None:
    """Test R2 client falls back to default with invalid expiration."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
            "R2_PRESIGN_EXPIRATION_S": "not_a_number",
        },
    ):
        client = R2StorageClient()

        assert client.presign_expiration_s == 604800  # Falls back to 7 days


def test_r2_client_initialization_missing_endpoint() -> None:
    """Test R2 client initialization fails without endpoint."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
        clear=False,
    ):
        with pytest.raises(ValueError) as exc_info:
            R2StorageClient()

        assert "R2 credentials not configured" in str(exc_info.value)


def test_r2_client_initialization_missing_access_key() -> None:
    """Test R2 client initialization fails without access key."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "",
            "R2_SECRET_KEY": "test_secret",
        },
        clear=False,
    ):
        with pytest.raises(ValueError):
            R2StorageClient()


def test_r2_client_initialization_missing_secret_key() -> None:
    """Test R2 client initialization fails without secret key."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "",
        },
        clear=False,
    ):
        with pytest.raises(ValueError):
            R2StorageClient()


def test_r2_upload_file_success() -> None:
    """Test successful R2 file upload."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3
            mock_s3.generate_presigned_url.return_value = "https://r2.example.com/presigned-url"

            client = R2StorageClient()
            url = client.upload_file("/tmp/test.mp4", "videos/test.mp4")

            mock_s3.upload_file.assert_called_once_with(
                "/tmp/test.mp4", "test-bucket", "videos/test.mp4"
            )
            mock_s3.generate_presigned_url.assert_called_once_with(
                "get_object",
                Params={"Bucket": "test-bucket", "Key": "videos/test.mp4"},
                ExpiresIn=604800,  # 7 days default
            )
            assert url == "https://r2.example.com/presigned-url"


def test_get_object_url_with_public_base_url() -> None:
    """Test that get_object_url returns public URL when configured."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
            "R2_PUBLIC_BASE_URL": "https://kinemotion-public.example.com",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client"):
            client = R2StorageClient()
            url = client.get_object_url("videos/test.mp4")

            assert url == "https://kinemotion-public.example.com/videos/test.mp4"


def test_get_object_url_without_public_base_url() -> None:
    """Test that get_object_url falls back to presigned URL when no public base."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3
            mock_s3.generate_presigned_url.return_value = (
                "https://r2.example.com/presigned-url?expires=123"
            )

            client = R2StorageClient()
            url = client.get_object_url("videos/test.mp4")

            # Should call generate_presigned_url with default expiration
            mock_s3.generate_presigned_url.assert_called_once_with(
                "get_object",
                Params={"Bucket": "test-bucket", "Key": "videos/test.mp4"},
                ExpiresIn=604800,  # 7 days
            )
            assert url == "https://r2.example.com/presigned-url?expires=123"


def test_get_object_url_strips_leading_slash() -> None:
    """Test that get_object_url normalizes keys by stripping leading slash."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
            "R2_PUBLIC_BASE_URL": "https://kinemotion-public.example.com",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client"):
            client = R2StorageClient()
            url = client.get_object_url("/videos/test.mp4")  # Leading slash

            # Should strip leading slash
            assert url == "https://kinemotion-public.example.com/videos/test.mp4"


def test_get_object_url_with_custom_expiration() -> None:
    """Test that get_object_url respects custom presigned expiration."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
            "R2_PRESIGN_EXPIRATION_S": "3600",  # 1 hour
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3
            mock_s3.generate_presigned_url.return_value = "https://r2.example.com/presigned"

            client = R2StorageClient()
            url = client.get_object_url("videos/test.mp4")

            # Should use custom expiration
            mock_s3.generate_presigned_url.assert_called_once_with(
                "get_object",
                Params={"Bucket": "test-bucket", "Key": "videos/test.mp4"},
                ExpiresIn=3600,  # Custom expiration
            )
            assert url == "https://r2.example.com/presigned"


def test_r2_upload_file_returns_url() -> None:
    """Test that R2 upload returns proper URL."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3
            presigned_url = "https://r2.example.com/presigned-url"
            mock_s3.generate_presigned_url.return_value = presigned_url

            client = R2StorageClient()
            url = client.upload_file("/tmp/test.mp4", "videos/test.mp4")

            assert url == presigned_url


def test_r2_upload_file_error_handling() -> None:
    """Test R2 upload error handling."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_s3.upload_file.side_effect = Exception("Upload failed")
            mock_boto3.return_value = mock_s3

            client = R2StorageClient()

            with pytest.raises(IOError) as exc_info:
                client.upload_file("/tmp/test.mp4", "videos/test.mp4")

            assert "Failed to upload to R2" in str(exc_info.value)


def test_r2_download_file_success() -> None:
    """Test successful R2 file download."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3

            client = R2StorageClient()
            client.download_file("videos/test.mp4", "/tmp/test.mp4")

            mock_s3.download_file.assert_called_once_with(
                "test-bucket", "videos/test.mp4", "/tmp/test.mp4"
            )


def test_r2_download_file_error_handling() -> None:
    """Test R2 download error handling."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_s3.download_file.side_effect = Exception("Download failed")
            mock_boto3.return_value = mock_s3

            client = R2StorageClient()

            with pytest.raises(IOError) as exc_info:
                client.download_file("videos/test.mp4", "/tmp/test.mp4")

            assert "Failed to download from R2" in str(exc_info.value)


def test_r2_delete_file_success() -> None:
    """Test successful R2 file deletion."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3

            client = R2StorageClient()
            client.delete_file("videos/test.mp4")

            mock_s3.delete_object.assert_called_once_with(
                Bucket="test-bucket", Key="videos/test.mp4"
            )


def test_r2_delete_file_error_handling() -> None:
    """Test R2 deletion error handling."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_s3.delete_object.side_effect = Exception("Delete failed")
            mock_boto3.return_value = mock_s3

            client = R2StorageClient()

            with pytest.raises(IOError) as exc_info:
                client.delete_file("videos/test.mp4")

            assert "Failed to delete from R2" in str(exc_info.value)


def test_r2_put_object_success() -> None:
    """Test successful R2 put object (for results)."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3
            mock_s3.generate_presigned_url.return_value = "https://r2.example.com/presigned-url"

            client = R2StorageClient()
            url = client.put_object("results/test.json", b'{"status": "ok"}')

            mock_s3.put_object.assert_called_once()
            mock_s3.generate_presigned_url.assert_called_once_with(
                "get_object",
                Params={"Bucket": "test-bucket", "Key": "results/test.json"},
                ExpiresIn=604800,  # 7 days default
            )
            assert url == "https://r2.example.com/presigned-url"


def test_r2_put_object_error_handling() -> None:
    """Test R2 put object error handling."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_s3.put_object.side_effect = Exception("Put failed")
            mock_boto3.return_value = mock_s3

            client = R2StorageClient()

            with pytest.raises(IOError) as exc_info:
                client.put_object("results/test.json", b'{"status": "ok"}')

            assert "Failed to put object to R2" in str(exc_info.value)


@pytest.mark.skip(
    reason="Refactored architecture requires R2 credentials at service initialization, "
    "not runtime. Graceful degradation without R2 is no longer supported."
)
def test_r2_graceful_degradation_without_credentials(
    client: TestClient,
    sample_video_bytes: bytes,
    no_r2_env: None,
) -> None:
    """Test that endpoint works without R2 credentials configured.

    NOTE: This test is skipped because the refactored architecture requires
    R2 credentials at AnalysisService initialization time. The previous behavior
    of graceful degradation at request time is no longer supported.
    """
    files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
    response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

    # Should still work, just without R2
    assert response.status_code == 200


@pytest.mark.skip(
    reason="Refactored architecture handles R2 through StorageService "
    "in dependency injection. This test targets old monolithic app.py "
    "structure."
)
def test_endpoint_handles_r2_upload_failure_gracefully(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that endpoint handles R2 upload failures gracefully.

    NOTE: This test is skipped because the refactored architecture handles
    R2 through the StorageService which is initialized at request time.
    The old monolithic patching approach no longer works.
    """
    # Mock R2 to be configured but fail
    with patch("kinemotion_backend.app.r2_client") as mock_r2:
        mock_r2.upload_file.side_effect = OSError("R2 upload failed")

        files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
        response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

        # Should return 500 error for R2 failure
        assert response.status_code == 500
        data = response.json()
        assert "Failed to upload video to storage" in data.get("error", "")


@pytest.mark.skip(
    reason="Refactored architecture handles R2 through StorageService "
    "in dependency injection. This test targets old monolithic app.py "
    "structure."
)
def test_endpoint_handles_r2_results_upload_failure(
    client: TestClient,
    sample_video_bytes: bytes,
) -> None:
    """Test that results upload failure doesn't crash (graceful degradation).

    NOTE: This test is skipped because the refactored architecture handles
    R2 through the StorageService which is initialized at request time.
    The old monolithic patching approach no longer works.
    """
    # Mock R2 to fail on results upload but succeed on video upload
    with patch("kinemotion_backend.app.r2_client") as mock_r2:
        mock_r2.upload_file.return_value = "https://r2.example.com/video.mp4"
        mock_r2.put_object.side_effect = OSError("Results upload failed")

        files = {"file": ("test.mp4", BytesIO(sample_video_bytes), "video/mp4")}
        response = client.post("/api/analyze", files=files, data={"jump_type": "cmj"})

        # Should still succeed (results_url just won't be present)
        assert response.status_code == 200
        data = response.json()
        # results_url might not be present due to failure
        assert "metrics" in data


def test_r2_bucket_name_from_env() -> None:
    """Test that R2 bucket name is read from environment."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
            "R2_BUCKET_NAME": "custom-bucket",
        },
    ):
        client = R2StorageClient()
        assert client.bucket_name == "custom-bucket"


def test_r2_bucket_name_default() -> None:
    """Test that R2 bucket name defaults to 'kinemotion'."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
            "R2_BUCKET_NAME": "",
        },
        clear=False,
    ):
        client = R2StorageClient()
        assert client.bucket_name == "kinemotion"


def test_r2_client_initialization_region_auto() -> None:
    """Test that R2 client uses 'auto' region."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            R2StorageClient()

            # Verify boto3 was called with region_name="auto"
            call_kwargs = mock_boto3.call_args[1]
            assert call_kwargs.get("region_name") == "auto"


def test_multiple_r2_operations_sequential() -> None:
    """Test multiple R2 operations in sequence."""
    with patch.dict(
        "os.environ",
        {
            "R2_ENDPOINT": "https://r2.example.com",
            "R2_ACCESS_KEY": "test_key",
            "R2_SECRET_KEY": "test_secret",
        },
    ):
        with patch("kinemotion_backend.models.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3

            client = R2StorageClient()

            # Upload
            client.upload_file("/tmp/test.mp4", "videos/test.mp4")
            # Put object
            client.put_object("results/test.json", b'{"status": "ok"}')
            # Delete
            client.delete_file("videos/test.mp4")

            # Verify all operations were called
            assert mock_s3.upload_file.called
            assert mock_s3.put_object.called
            assert mock_s3.delete_object.called
