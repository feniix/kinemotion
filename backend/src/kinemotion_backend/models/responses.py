from typing import Any

from pydantic import BaseModel, Field


class ValidationIssue(BaseModel):
    """Validation issue reported by the API."""

    metric: str = Field(..., description="Metric name with the issue")
    severity: str = Field(..., description="Severity level: ERROR, WARNING, or INFO")
    message: str = Field(..., description="Issue description")


class ValidationResults(BaseModel):
    """Validation results from analysis."""

    status: str = Field(..., description="Status: PASS, FAIL, WARNING, or PASS_WITH_WARNINGS")
    issues: list[ValidationIssue] = Field(
        default_factory=list, description="List of validation issues"
    )


class MetricsData(BaseModel):
    """Analysis metrics with optional metadata and validation."""

    data: dict[str, Any] | None = Field(None, description="Actual metric values")
    metadata: dict[str, Any] | None = Field(None, description="Metric metadata and descriptions")
    validation: ValidationResults | None = Field(
        None, description="Validation results for metrics"
    )


class AnalysisResponse(BaseModel):
    """Response structure for video analysis results."""

    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    metrics: MetricsData | None = Field(None, description="Analysis metrics")
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
