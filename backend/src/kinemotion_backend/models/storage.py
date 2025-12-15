import os

import boto3
import structlog

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class R2StorageClient:
    """Cloudflare R2 storage client for video and results management."""

    def __init__(self) -> None:
        """Initialize R2 client with environment configuration."""
        self.endpoint = os.getenv("R2_ENDPOINT", "")
        self.access_key = os.getenv("R2_ACCESS_KEY", "")
        self.secret_key = os.getenv("R2_SECRET_KEY", "")
        self.bucket_name = os.getenv("R2_BUCKET_NAME") or "kinemotion"
        # Optional: if set, we will return stable public URLs instead of presigned URLs.
        # Example: https://<your-public-domain> (custom domain) or https://<bucket>.<account>.r2.dev
        self.public_base_url = (os.getenv("R2_PUBLIC_BASE_URL") or "").rstrip("/")
        # Fallback: presigned URL expiration seconds (default 7 days, S3 max)
        try:
            self.presign_expiration_s = int(os.getenv("R2_PRESIGN_EXPIRATION_S") or "604800")
        except ValueError:
            self.presign_expiration_s = 604800

        if not all([self.endpoint, self.access_key, self.secret_key]):
            raise ValueError(
                "R2 credentials not configured. Set R2_ENDPOINT, "
                "R2_ACCESS_KEY, and R2_SECRET_KEY environment variables."
            )

        # Initialize S3-compatible client for R2
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="auto",
        )

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for object.

        Args:
            key: Object key
            expiration: Expiration in seconds (default 1 hour)

        Returns:
            Presigned URL string

        Raises:
            OSError: If generation fails
        """
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expiration,
            )
        except Exception as e:
            raise OSError(f"Failed to generate presigned URL: {str(e)}") from e

    def get_object_url(self, key: str) -> str:
        """Return a long-lived shareable URL for an object key.

        Prefers a stable public URL if `R2_PUBLIC_BASE_URL` is configured.
        Otherwise, falls back to a presigned URL with `R2_PRESIGN_EXPIRATION_S`.
        """
        normalized_key = key.lstrip("/")
        if self.public_base_url:
            return f"{self.public_base_url}/{normalized_key}"
        return self.generate_presigned_url(normalized_key, expiration=self.presign_expiration_s)

    def upload_file(self, local_path: str, remote_key: str) -> str:
        """Upload file to R2 storage.

        Args:
            local_path: Local file path to upload
            remote_key: S3 object key in R2 bucket

        Returns:
            Presigned URL of uploaded file

        Raises:
            OSError: If upload fails
        """
        try:
            self.client.upload_file(local_path, self.bucket_name, remote_key)
            return self.get_object_url(remote_key)
        except Exception as e:
            raise OSError(f"Failed to upload to R2: {str(e)}") from e

    def download_file(self, remote_key: str, local_path: str) -> None:
        """Download file from R2 storage.

        Args:
            remote_key: S3 object key in R2 bucket
            local_path: Local path to save downloaded file

        Raises:
            OSError: If download fails
        """
        try:
            self.client.download_file(self.bucket_name, remote_key, local_path)
        except Exception as e:
            raise OSError(f"Failed to download from R2: {str(e)}") from e

    def delete_file(self, remote_key: str) -> None:
        """Delete file from R2 storage.

        Args:
            remote_key: S3 object key in R2 bucket

        Raises:
            OSError: If deletion fails
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=remote_key)
        except Exception as e:
            raise OSError(f"Failed to delete from R2: {str(e)}") from e

    def put_object(self, key: str, body: bytes) -> str:
        """Put object (bytes) to R2 storage.

        Args:
            key: S3 object key in R2 bucket
            body: Binary content to store

        Returns:
            Presigned URL of uploaded object

        Raises:
            OSError: If upload fails
        """
        try:
            self.client.put_object(Bucket=self.bucket_name, Key=key, Body=body)
            return self.get_object_url(key)
        except Exception as e:
            raise OSError(f"Failed to put object to R2: {str(e)}") from e
