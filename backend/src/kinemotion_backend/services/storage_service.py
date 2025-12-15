import tempfile
from pathlib import Path
from typing import Any

from ..models.storage import R2StorageClient


class StorageService:
    """Service for managing R2 storage operations."""

    def __init__(self) -> None:
        """Initialize storage service with R2 client."""
        self.client = R2StorageClient()

    async def upload_video(self, local_path: str, remote_key: str) -> str:
        """Upload video to R2 storage.

        Args:
            local_path: Local file path to upload
            remote_key: S3 object key in R2 bucket

        Returns:
            Public URL of uploaded file
        """
        return self.client.upload_file(local_path, remote_key)

    async def upload_analysis_results(self, results: dict[str, Any], remote_key: str) -> str:
        """Upload analysis results as JSON to R2 storage.

        Args:
            results: Analysis results data
            remote_key: S3 object key in R2 bucket

        Returns:
            Public URL of uploaded results
        """
        import json

        results_json = json.dumps(results, indent=2).encode("utf-8")
        return self.client.put_object(remote_key, results_json)

    async def generate_unique_key(self, filename: str, user_id: str | None = None) -> str:
        """Generate unique storage key for uploaded file.

        Args:
            filename: Original filename
            user_id: Optional user ID for organization

        Returns:
            Unique storage key
        """
        import uuid
        from datetime import datetime, timezone

        timestamp = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        file_id = str(uuid.uuid4())
        extension = Path(filename).suffix

        if user_id:
            return f"uploads/{user_id}/{timestamp}/{file_id}{extension}"
        else:
            return f"uploads/anonymous/{timestamp}/{file_id}{extension}"

    def get_temp_file_path(self, filename: str) -> str:
        """Get temporary file path for processing.

        Args:
            filename: Original filename

        Returns:
            Temporary file path
        """
        temp_dir = Path(tempfile.gettempdir()) / "kinemotion"
        temp_dir.mkdir(exist_ok=True)
        return str(temp_dir / filename)
