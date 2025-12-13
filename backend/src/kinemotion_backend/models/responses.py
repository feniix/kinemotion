from typing import Any

from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    """Response structure for video analysis results."""

    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    metrics: dict[str, Any] | None = Field(None, description="Analysis metrics")
    results_url: str | None = Field(None, description="URL to analysis results")
    debug_video_url: str | None = Field(None, description="URL to debug video")
    original_video_url: str | None = Field(None, description="URL to original video")
    error: str | None = Field(None, description="Error message if analysis failed")
    processing_time_s: float = Field(0.0, description="Processing time in seconds")

    model_config = {
        "json_encoders": {
            # Add any custom encoders if needed
        },
        "populate_by_name": True,
    }

    def to_dict(self) -> dict[str, Any]:
        """Convert response to JSON-serializable dictionary."""
        return self.model_dump(exclude_none=True)
